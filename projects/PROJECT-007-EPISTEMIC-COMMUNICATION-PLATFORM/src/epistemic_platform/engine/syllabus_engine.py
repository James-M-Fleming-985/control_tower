"""Syllabus engine — assessment-driven, competency-based learning progression.

Generates a personalised syllabus per level based on assessment results.
Each level prescribes scenarios from the appropriate difficulty tier,
requiring completion with ALL 6 actors at a minimum grade threshold.

Level model (like a university year):
  L1 Explorer       — 2 beginner scenarios  × 6 actors, min C
  L2 Practitioner   — 3 scenarios (beginner+intermediate) × 6 actors, min C+
  L3 Communicator   — 3 intermediate scenarios × 6 actors, min B
  L4 Advanced       — 2 advanced scenarios × 6 actors, min B+
  L5 Expert         — 1 expert scenario  × 6 actors, min A
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ── Grade helpers ────────────────────────────────────────────────────

GRADE_ORDER = {"S": 6, "A": 5, "B+": 4, "B": 3, "C+": 2, "C": 1, "D": 0}

# Minimum grade required per level
LEVEL_MIN_GRADE: dict[int, str] = {
    1: "C",
    2: "C+",
    3: "B",
    4: "B+",
    5: "A",
}

# Score thresholds for sub-grades (B+ and C+ don't exist in scoring_rubric
# so we map from final_score directly)
GRADE_SCORE_THRESHOLDS: dict[str, float] = {
    "S": 95.0,
    "A": 80.0,
    "B+": 72.0,
    "B": 65.0,
    "C+": 57.0,
    "C": 50.0,
    "D": 0.0,
}


def grade_from_score(score: float) -> str:
    """Convert a final score to a grade including sub-grades (B+, C+)."""
    for grade, threshold in GRADE_SCORE_THRESHOLDS.items():
        if score >= threshold:
            return grade
    return "D"


def grade_meets_minimum(grade: str, min_grade: str) -> bool:
    """Check if a grade meets or exceeds the minimum."""
    return GRADE_ORDER.get(grade, 0) >= GRADE_ORDER.get(min_grade, 0)


# ── Level → scenario difficulty mapping ──────────────────────────────

LEVEL_DIFFICULTY_MAP: dict[int, list[str]] = {
    1: ["beginner"],
    2: ["beginner", "intermediate"],
    3: ["intermediate"],
    4: ["advanced"],
    5: ["expert"],
}

LEVEL_SCENARIO_COUNT: dict[int, int] = {
    1: 2,
    2: 3,
    3: 3,
    4: 2,
    5: 1,
}

# ── Stance → scenario category affinity ──────────────────────────────
# Used to personalise which scenarios are prioritised based on assessment

STANCE_CATEGORY_AFFINITY: dict[str, list[str]] = {
    "foundationalist": ["ethics", "epistemology", "political_philosophy"],
    "coherentist": ["ethics", "science", "communication"],
    "pragmatist": ["ethics", "science", "communication"],
    "empiricist": ["science", "epistemology", "philosophy"],
    "skeptic": ["philosophy", "political_philosophy", "epistemology"],
    "relativist": ["ethics", "political_philosophy", "communication"],
    "fallibilist": ["science", "philosophy", "epistemology"],
    "infinitist": ["philosophy", "epistemology"],
    "foundherentist": ["philosophy", "science"],
    "virtue_epistemologist": ["ethics", "communication", "philosophy"],
}


class SyllabusEngine:
    """Generates and manages competency-based syllabi."""

    def generate(
        self,
        assessment_result: dict[str, Any],
        current_level: int,
        all_scenarios: list[dict[str, Any]],
        all_actor_ids: list[int],
    ) -> dict[str, Any]:
        """Generate a syllabus for the given level.

        Parameters
        ----------
        assessment_result : dict
            Latest assessment result with primary_stance, secondary_stance, etc.
        current_level : int
            The level to generate the syllabus for (1–5).
        all_scenarios : list[dict]
            All active scenario definitions (each must have id, title, difficulty, category).
        all_actor_ids : list[int]
            All active actor IDs.

        Returns
        -------
        Syllabus dict ready to store on user.syllabus.
        """
        level = max(1, min(5, current_level))
        allowed_difficulties = LEVEL_DIFFICULTY_MAP[level]
        scenario_count = LEVEL_SCENARIO_COUNT[level]
        min_grade = LEVEL_MIN_GRADE[level]

        # Filter scenarios by difficulty
        eligible = [
            s for s in all_scenarios
            if s.get("difficulty") in allowed_difficulties and s.get("is_active", True)
        ]

        # Rank by assessment affinity (weak stances → prioritise scenarios in those categories)
        primary = assessment_result.get("primary_stance", "")
        secondary = assessment_result.get("secondary_stance", "")

        # Weak categories = categories NOT aligned with user's strong stances
        strong_categories = set()
        if primary:
            strong_categories.update(STANCE_CATEGORY_AFFINITY.get(primary, []))
        if secondary:
            strong_categories.update(STANCE_CATEGORY_AFFINITY.get(secondary, []))

        # Sort: scenarios in weak categories first, then strong
        def sort_key(s: dict) -> tuple:
            cat = s.get("category", "")
            is_weak = 0 if cat not in strong_categories else 1
            return (is_weak, cat, s.get("title", ""))

        eligible.sort(key=sort_key)

        # Select scenarios (cap at available count)
        selected = eligible[:scenario_count]

        # Build items — each scenario requires ALL actors
        items = []
        for scenario in selected:
            actors_dict: dict[str, dict] = {}
            for actor_id in all_actor_ids:
                actors_dict[str(actor_id)] = {}  # empty = not completed
            items.append({
                "scenario_id": scenario["id"],
                "scenario_title": scenario.get("title", ""),
                "scenario_difficulty": scenario.get("difficulty", ""),
                "min_grade": min_grade,
                "actors": actors_dict,
            })

        return {
            "current_level": level,
            "min_grade": min_grade,
            "items": items,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "assessment_ref": {
                "primary_stance": primary,
                "secondary_stance": secondary,
            },
        }

    def record_completion(
        self,
        syllabus: dict[str, Any],
        scenario_id: int,
        actor_id: int,
        grade: str,
        final_score: float,
        session_id: int,
    ) -> tuple[dict[str, Any], bool]:
        """Record a scenario+actor completion in the syllabus.

        Returns
        -------
        (updated_syllabus, is_new_completion) — is_new_completion=True if this
        was a new passing completion (not a re-attempt of already passed).
        """
        items = syllabus.get("items", [])
        min_grade = syllabus.get("min_grade", "C")

        for item in items:
            if item["scenario_id"] != scenario_id:
                continue
            actor_key = str(actor_id)
            if actor_key not in item.get("actors", {}):
                continue

            passes = grade_meets_minimum(grade, min_grade)
            existing = item["actors"].get(actor_key, {})
            already_passed = existing and grade_meets_minimum(
                existing.get("grade", "D"), min_grade
            )

            # Always record the attempt (overwrite with better score)
            if not existing or final_score > existing.get("score", 0):
                item["actors"][actor_key] = {
                    "grade": grade,
                    "score": round(final_score, 1),
                    "session_id": session_id,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }

            return syllabus, passes and not already_passed

        return syllabus, False

    def check_level_complete(self, syllabus: dict[str, Any]) -> bool:
        """Check if ALL syllabus items are completed with ALL actors at min grade."""
        items = syllabus.get("items", [])
        min_grade = syllabus.get("min_grade", "C")

        if not items:
            return False

        for item in items:
            actors = item.get("actors", {})
            if not actors:
                return False
            for actor_key, completion in actors.items():
                if not completion:
                    return False
                if not grade_meets_minimum(completion.get("grade", "D"), min_grade):
                    return False

        return True

    def get_progress(self, syllabus: dict[str, Any]) -> dict[str, Any]:
        """Compute completion progress for the current syllabus."""
        items = syllabus.get("items", [])
        min_grade = syllabus.get("min_grade", "C")

        total_cells = 0
        completed_cells = 0
        scenario_progress = []

        for item in items:
            actors = item.get("actors", {})
            scenario_total = len(actors)
            scenario_done = 0
            for completion in actors.values():
                if completion and grade_meets_minimum(
                    completion.get("grade", "D"), min_grade
                ):
                    scenario_done += 1
            total_cells += scenario_total
            completed_cells += scenario_done
            scenario_progress.append({
                "scenario_id": item["scenario_id"],
                "scenario_title": item.get("scenario_title", ""),
                "completed": scenario_done,
                "total": scenario_total,
            })

        return {
            "current_level": syllabus.get("current_level", 1),
            "min_grade": min_grade,
            "total_completions": total_cells,
            "completed_completions": completed_cells,
            "percentage": round(
                (completed_cells / total_cells * 100) if total_cells > 0 else 0, 1
            ),
            "level_complete": self.check_level_complete(syllabus),
            "scenarios": scenario_progress,
            "items": items,  # Full items with actor completion details
        }

    @staticmethod
    def should_reassess(
        assessment_history: list[dict],
        total_sessions: int,
    ) -> bool:
        """Check if the user should be prompted for reassessment.

        Triggers when:
        - No assessment exists yet
        - 15+ sessions since last assessment
        - 30+ days since last assessment
        """
        if not assessment_history:
            return True

        latest = assessment_history[-1]
        completed_at = latest.get("completed_at", "")

        # Session-count trigger: approximate from total_sessions
        # (We don't track sessions-since-assessment, so use a heuristic)
        sessions_at_assessment = latest.get("session_count", 0)
        if total_sessions - sessions_at_assessment >= 15:
            return True

        # Time-based trigger
        if completed_at:
            try:
                from datetime import datetime, timezone
                ts = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                days_since = (datetime.now(timezone.utc) - ts).days
                if days_since >= 30:
                    return True
            except (ValueError, TypeError):
                pass

        return False
