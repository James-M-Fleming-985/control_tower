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
        text="You're arguing with a friend about a topic you care about. What feels like the strongest way to back up your point?",
        options=[
            {"key": "a", "text": "Point to a basic truth that everyone should accept", "stance_signal": "foundationalist"},
            {"key": "b", "text": "Show how it fits with everything else you believe", "stance_signal": "coherentist"},
            {"key": "c", "text": "Explain that it actually works well in practice", "stance_signal": "pragmatist"},
            {"key": "d", "text": "Pull up real data or examples from the world", "stance_signal": "empiricist"},
        ],
    ),
    AssessmentQuestion(
        id="q2",
        text="Someone says: 'That's just obviously true.' What's your gut reaction?",
        options=[
            {"key": "a", "text": "I agree — some things just ARE obvious", "stance_signal": "foundationalist"},
            {"key": "b", "text": "Nothing is obvious — I'd push back on that", "stance_signal": "skeptic"},
            {"key": "c", "text": "Obvious to who? That depends on where you're coming from", "stance_signal": "relativist"},
            {"key": "d", "text": "Maybe, but I'd stay open to changing my mind later", "stance_signal": "fallibilist"},
        ],
    ),
    AssessmentQuestion(
        id="q3",
        text="You realise two things you believe actually contradict each other. What do you do first?",
        options=[
            {"key": "a", "text": "Check which one is better supported by my own experience", "stance_signal": "foundherentist"},
            {"key": "b", "text": "Drop whichever one fits less well with my other beliefs", "stance_signal": "coherentist"},
            {"key": "c", "text": "Keep digging — maybe neither is fully right yet", "stance_signal": "infinitist"},
            {"key": "d", "text": "See which one is more useful in real life", "stance_signal": "pragmatist"},
        ],
    ),
    AssessmentQuestion(
        id="q4",
        text="What kind of debate partner makes you think the hardest?",
        options=[
            {"key": "a", "text": "Someone who keeps asking 'but why?' over and over", "stance_signal": "infinitist"},
            {"key": "b", "text": "Someone who says 'show me the evidence'", "stance_signal": "empiricist"},
            {"key": "c", "text": "Someone who helps me see my blind spots honestly", "stance_signal": "virtue_epistemologist"},
            {"key": "d", "text": "Someone who's comfortable saying 'you could be wrong'", "stance_signal": "fallibilist"},
        ],
    ),
    AssessmentQuestion(
        id="q5",
        text="When do you feel like you really KNOW something?",
        options=[
            {"key": "a", "text": "When I've seen the proof or evidence myself", "stance_signal": "empiricist"},
            {"key": "b", "text": "Honestly? I'm not sure we ever fully know anything", "stance_signal": "skeptic"},
            {"key": "c", "text": "When I reached the answer by thinking carefully and honestly", "stance_signal": "virtue_epistemologist"},
            {"key": "d", "text": "When it actually works — results speak for themselves", "stance_signal": "pragmatist"},
        ],
    ),
    AssessmentQuestion(
        id="q6",
        text="A friend says: 'What's right in one culture might be wrong in another.' You think...",
        options=[
            {"key": "a", "text": "That's fair — truth really does depend on context", "stance_signal": "relativist"},
            {"key": "b", "text": "Some things are right or wrong no matter what culture you're in", "stance_signal": "foundationalist"},
            {"key": "c", "text": "I'd want to check — do cultures actually disagree that much?", "stance_signal": "empiricist"},
            {"key": "d", "text": "Both sides probably have a point — I'd need to think more", "stance_signal": "fallibilist"},
        ],
    ),
]

# ── Stance explanations (plain-English for results page) ────────────

STANCE_EXPLANATIONS: dict[str, dict[str, str]] = {
    "foundationalist": {
        "name": "Foundationalist",
        "short": "You believe some truths are self-evident and everything else builds on them.",
        "description": "Foundationalists think knowledge rests on basic, undeniable truths — like building a house on solid rock. You're drawn to clear starting points and firm principles.",
    },
    "coherentist": {
        "name": "Coherentist",
        "short": "You judge ideas by how well they fit together as a whole.",
        "description": "Coherentists care about consistency. For you, a belief is trustworthy when it fits seamlessly with everything else you know — like pieces of a jigsaw puzzle.",
    },
    "pragmatist": {
        "name": "Pragmatist",
        "short": "You trust what works — practical results matter most to you.",
        "description": "Pragmatists judge ideas by their real-world usefulness. If a belief leads to good outcomes, it's worth holding onto. You prefer action over abstract debate.",
    },
    "skeptic": {
        "name": "Skeptic",
        "short": "You question everything and resist accepting claims too easily.",
        "description": "Skeptics believe certainty is hard to come by. You naturally challenge assumptions and push others to justify their claims before you accept them.",
    },
    "empiricist": {
        "name": "Empiricist",
        "short": "You trust evidence — what you can see, measure, or test.",
        "description": "Empiricists ground their beliefs in observable facts and data. You want proof before commitment, and your go-to question is 'what's the evidence?'",
    },
    "relativist": {
        "name": "Relativist",
        "short": "You believe truth depends on perspective, culture, or context.",
        "description": "Relativists recognise that what counts as 'true' can vary across people and cultures. You're comfortable with multiple valid viewpoints coexisting.",
    },
    "infinitist": {
        "name": "Infinitist",
        "short": "You believe there's always another 'why' — justification never fully ends.",
        "description": "Infinitists think every answer raises new questions. You enjoy digging deeper and resist the idea that any explanation is truly final.",
    },
    "foundherentist": {
        "name": "Foundherentist",
        "short": "You blend experience with consistency — the best of both worlds.",
        "description": "Foundherentists combine direct experience with a coherent web of beliefs. You want your ideas to be both grounded in reality and internally consistent.",
    },
    "virtue_epistemologist": {
        "name": "Virtue Epistemologist",
        "short": "You value intellectual honesty, open-mindedness, and careful reasoning.",
        "description": "Virtue epistemologists focus on the character of the thinker. For you, good knowledge comes from good intellectual habits — curiosity, humility, and rigour.",
    },
    "fallibilist": {
        "name": "Fallibilist",
        "short": "You hold beliefs firmly but stay open to being wrong.",
        "description": "Fallibilists accept that any belief could turn out to be mistaken. You commit to your best current understanding while remaining genuinely open to revision.",
    },
}


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
    answer_deductions: list[dict[str, str]] = field(default_factory=list)

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
            "answer_deductions": self.answer_deductions,
            "stance_explanations": STANCE_EXPLANATIONS,
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
        answer_deductions: list[dict[str, str]] = []
        for q in CALIBRATION_QUESTIONS:
            selected_key = answers.get(q.id)
            if not selected_key:
                continue
            for opt in q.options:
                if opt["key"] == selected_key:
                    signal = opt["stance_signal"]
                    stance_counts[signal] = stance_counts.get(signal, 0) + 1
                    info = STANCE_EXPLANATIONS.get(signal, {})
                    answer_deductions.append({
                        "question": q.text,
                        "your_answer": opt["text"],
                        "stance_signal": signal,
                        "stance_name": info.get("name", signal.replace("_", " ").title()),
                    })

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

        primary_key = primary.value if primary else "unknown"
        primary_info = STANCE_EXPLANATIONS.get(primary_key, {})
        primary_name = primary_info.get("name", primary_key.replace("_", " ").title())
        secondary_key = secondary.value if secondary else None
        secondary_info = STANCE_EXPLANATIONS.get(secondary_key, {}) if secondary_key else {}
        secondary_name = secondary_info.get("name", (secondary_key or "none").replace("_", " ").title())

        explanation = (
            f"{primary_info.get('description', '')} "
            f"Your secondary tendency is {secondary_name}: "
            f"{secondary_info.get('short', '')}"
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
            answer_deductions=answer_deductions,
        )

    @staticmethod
    def _parse_stance(value: str | None) -> StanceType | None:
        if not value or value == "null":
            return None
        try:
            return StanceType(value)
        except ValueError:
            return None
