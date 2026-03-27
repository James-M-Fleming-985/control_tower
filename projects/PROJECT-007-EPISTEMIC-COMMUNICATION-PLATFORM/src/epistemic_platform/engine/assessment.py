"""Pre-conversation assessment — calibrates user's epistemological profile.

Presents a set of calibration questions and uses the coaching LLM (Opus) to
classify the user's epistemological tendencies, communication style, and
recommend suitable actors and scenarios.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from epistemic_platform.llm.protocol import CoachingLLM, LLMMessage
from epistemic_platform.ontology.epistemological_stance import StanceType

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent / "prompts"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    trim_blocks=True,
    lstrip_blocks=True,
)


# ── Calibration questions ───────────────────────────────────────────

@dataclass
class AssessmentQuestion:
    """A single calibration question with multiple-choice options."""

    id: str
    text: str
    options: list[dict[str, str]]  # [{"key": "a", "text": "...", "stance_signal": "foundationalist"}, ...]

    def to_dict(self) -> dict:
        return {"id": self.id, "text": self.text, "options": self.options}


CALIBRATION_QUESTIONS: list[AssessmentQuestion] = [
    AssessmentQuestion(
        id="q1",
        text="When you make an important claim in a discussion, what do you consider the best form of support?",
        options=[
            {"key": "a", "text": "A self-evident principle that needs no further justification", "stance_signal": "foundationalist"},
            {"key": "b", "text": "Showing how it fits consistently with everything else I believe", "stance_signal": "coherentist"},
            {"key": "c", "text": "Demonstrating that acting on this belief leads to good outcomes", "stance_signal": "pragmatist"},
            {"key": "d", "text": "Concrete data or observations from the real world", "stance_signal": "empiricist"},
        ],
    ),
    AssessmentQuestion(
        id="q2",
        text="Someone tells you: 'This is just obviously true.' How do you respond?",
        options=[
            {"key": "a", "text": "I agree — some things really are self-evident", "stance_signal": "foundationalist"},
            {"key": "b", "text": "I challenge them — nothing is beyond questioning", "stance_signal": "skeptic"},
            {"key": "c", "text": "I ask: obvious to whom? It depends on your perspective", "stance_signal": "relativist"},
            {"key": "d", "text": "I accept it tentatively but stay open to revision", "stance_signal": "fallibilist"},
        ],
    ),
    AssessmentQuestion(
        id="q3",
        text="You discover two of your beliefs contradict each other. What do you do?",
        options=[
            {"key": "a", "text": "Investigate which one has better experiential grounding", "stance_signal": "foundherentist"},
            {"key": "b", "text": "Revise the one that creates less overall coherence", "stance_signal": "coherentist"},
            {"key": "c", "text": "Keep questioning both — consistency might be less important than thoroughness", "stance_signal": "infinitist"},
            {"key": "d", "text": "Ask which belief, if true, would lead to better practical outcomes", "stance_signal": "pragmatist"},
        ],
    ),
    AssessmentQuestion(
        id="q4",
        text="What kind of conversation partner challenges you the most productively?",
        options=[
            {"key": "a", "text": "Someone who relentlessly asks 'why?' at every step", "stance_signal": "infinitist"},
            {"key": "b", "text": "Someone who demands concrete evidence for everything", "stance_signal": "empiricist"},
            {"key": "c", "text": "Someone who shows me how my reasoning could be more honest and careful", "stance_signal": "virtue_epistemologist"},
            {"key": "d", "text": "Someone who keeps pointing out I might be wrong", "stance_signal": "fallibilist"},
        ],
    ),
    AssessmentQuestion(
        id="q5",
        text="When can you say you truly 'know' something?",
        options=[
            {"key": "a", "text": "When it's been verified through observation or experiment", "stance_signal": "empiricist"},
            {"key": "b", "text": "You can never truly know — certainty is an illusion", "stance_signal": "skeptic"},
            {"key": "c", "text": "When you've arrived at it through honest, careful intellectual inquiry", "stance_signal": "virtue_epistemologist"},
            {"key": "d", "text": "When it works — practical success validates knowledge", "stance_signal": "pragmatist"},
        ],
    ),
    AssessmentQuestion(
        id="q6",
        text="A friend says morality differs across cultures. You think...",
        options=[
            {"key": "a", "text": "They're right — truth depends on framework and context", "stance_signal": "relativist"},
            {"key": "b", "text": "Maybe, but some moral truths are foundational across all cultures", "stance_signal": "foundationalist"},
            {"key": "c", "text": "We should look at the evidence — do moral systems actually differ in practice?", "stance_signal": "empiricist"},
            {"key": "d", "text": "Both views might be partly right — I'd need to think more before committing", "stance_signal": "fallibilist"},
        ],
    ),
]


@dataclass
class AssessmentResult:
    """Result of evaluating assessment answers."""

    primary_stance: StanceType | None = None
    secondary_stance: StanceType | None = None
    confidence: float = 0.0
    communication_style: str = ""
    recommended_actors: list[str] = field(default_factory=list)
    recommended_scenarios: list[str] = field(default_factory=list)
    reasoning: str = ""
    explanation: str = ""
    stance_scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "primary_stance": self.primary_stance.value if self.primary_stance else None,
            "secondary_stance": self.secondary_stance.value if self.secondary_stance else None,
            "confidence": self.confidence,
            "communication_style": self.communication_style,
            "recommended_actors": self.recommended_actors,
            "recommended_scenarios": self.recommended_scenarios,
            "reasoning": self.reasoning,
            "explanation": self.explanation,
            "stance_scores": self.stance_scores,
        }


class AssessmentEngine:
    """Evaluates user assessment answers to determine epistemological profile."""

    def __init__(self, coaching_llm: CoachingLLM) -> None:
        self._llm = coaching_llm

    @staticmethod
    def get_questions() -> list[dict]:
        """Return the calibration questions with options."""
        return [q.to_dict() for q in CALIBRATION_QUESTIONS]

    async def evaluate(self, answers: dict[str, str]) -> AssessmentResult:
        """Evaluate assessment answers and return a profile.

        Parameters
        ----------
        answers : dict[str, str]
            Mapping of question ID to selected option key, e.g. {"q1": "a", "q2": "c"}.

        Returns
        -------
        AssessmentResult with stance classification and recommendations.
        """
        # Build question + answer context for the LLM
        questions_with_answers = []
        for q in CALIBRATION_QUESTIONS:
            selected_key = answers.get(q.id)
            if selected_key:
                selected_text = next(
                    (opt["text"] for opt in q.options if opt["key"] == selected_key),
                    f"(invalid option: {selected_key})",
                )
            else:
                selected_text = "(not answered)"
            questions_with_answers.append({"text": q.text, "answer": selected_text})

        tpl = _env.get_template("assessment_analysis.j2")
        system_prompt = tpl.render(questions=questions_with_answers)

        try:
            response = await self._llm.analyse(
                messages=[LLMMessage(role="user", content="Please evaluate my assessment answers.")],
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1024,
            )

            data = json.loads(response.content)
            return AssessmentResult(
                primary_stance=self._parse_stance(data.get("primary_stance")),
                secondary_stance=self._parse_stance(data.get("secondary_stance")),
                confidence=float(data.get("confidence", 0.0)),
                communication_style=data.get("communication_style", ""),
                recommended_actors=data.get("recommended_actors", []),
                recommended_scenarios=data.get("recommended_scenarios", []),
                reasoning=data.get("reasoning", ""),
                explanation=data.get("explanation", ""),
                stance_scores=data.get("stance_scores", {}),
            )
        except Exception as e:
            logger.warning("Assessment evaluation failed: %s", e)
            # Fall back to simple counting
            return self._heuristic_evaluation(answers)

    def _heuristic_evaluation(self, answers: dict[str, str]) -> AssessmentResult:
        """Simple counting fallback if LLM fails."""
        stance_counts: dict[str, int] = {}
        for q in CALIBRATION_QUESTIONS:
            selected_key = answers.get(q.id)
            if not selected_key:
                continue
            for opt in q.options:
                if opt["key"] == selected_key:
                    signal = opt["stance_signal"]
                    stance_counts[signal] = stance_counts.get(signal, 0) + 1

        if not stance_counts:
            return AssessmentResult()

        sorted_stances = sorted(stance_counts.items(), key=lambda x: x[1], reverse=True)
        primary = self._parse_stance(sorted_stances[0][0])
        secondary = self._parse_stance(sorted_stances[1][0]) if len(sorted_stances) > 1 else None

        # Build stance_scores as proportions
        total = sum(stance_counts.values())
        stance_scores = {k: round(v / total, 2) for k, v in stance_counts.items()}

        # Stance → actor affinity for recommendations
        _STANCE_ACTOR_MAP = {
            "foundationalist": "Professor Axelrod",
            "coherentist": "Dr Weaver",
            "pragmatist": "Max Results",
            "skeptic": "Zara Doubt",
            "empiricist": "Dr Data",
            "relativist": "Sage Perspective",
        }
        _STANCE_SCENARIO_MAP = {
            "foundationalist": "Should We Trust Expert Consensus?",
            "coherentist": "The Trolley Problem Revisited",
            "pragmatist": "The Ethics of AI Art",
            "skeptic": "Free Will vs Determinism",
            "empiricist": "What Counts as Scientific Evidence?",
            "relativist": "Can We Know Other Minds?",
        }

        # Recommend actors/scenarios for weak stances (not primary/secondary)
        strong = {sorted_stances[0][0]}
        if len(sorted_stances) > 1:
            strong.add(sorted_stances[1][0])
        rec_actors = [v for k, v in _STANCE_ACTOR_MAP.items() if k not in strong]
        rec_scenarios = [v for k, v in _STANCE_SCENARIO_MAP.items() if k not in strong]

        primary_name = primary.value if primary else "unknown"
        secondary_name = secondary.value if secondary else "none"
        explanation = (
            f"Your responses indicate a primarily {primary_name} approach to knowledge, "
            f"with {secondary_name} as a secondary tendency. "
            f"Consider exploring perspectives that challenge your dominant stance."
        )

        return AssessmentResult(
            primary_stance=primary,
            secondary_stance=secondary,
            confidence=sorted_stances[0][1] / len(CALIBRATION_QUESTIONS),
            reasoning="Heuristic classification from answer option mapping",
            recommended_actors=rec_actors,
            recommended_scenarios=rec_scenarios,
            explanation=explanation,
            stance_scores=stance_scores,
        )

    @staticmethod
    def _parse_stance(value: str | None) -> StanceType | None:
        if not value or value == "null":
            return None
        try:
            return StanceType(value)
        except ValueError:
            return None
