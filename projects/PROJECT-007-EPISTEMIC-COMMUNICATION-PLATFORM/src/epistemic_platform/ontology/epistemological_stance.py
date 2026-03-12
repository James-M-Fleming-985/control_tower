"""Epistemological stances — the 6 foundational reasoning paradigms.

Each stance defines how an actor reasons about knowledge, justification,
and truth. The ontology_config on ActorProfile maps to one of these stances,
which governs prompt construction, trilemma navigation, and coaching analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class StanceType(str, Enum):
    FOUNDATIONALIST = "foundationalist"
    COHERENTIST = "coherentist"
    PRAGMATIST = "pragmatist"
    SKEPTIC = "skeptic"
    EMPIRICIST = "empiricist"
    RELATIVIST = "relativist"


@dataclass(frozen=True)
class TrilemmaResponse:
    """How a stance responds to each horn of Agrippa's Trilemma."""

    horn: str  # "regress", "circularity", "dogmatism"
    strategy: str  # How this stance navigates this horn
    example_prompt: str  # Example challenge the actor would pose


@dataclass(frozen=True)
class EpistemologicalStance:
    """Full definition of an epistemological reasoning stance."""

    stance_type: StanceType
    label: str
    description: str
    core_principle: str
    justification_style: str
    typical_challenges: list[str] = field(default_factory=list)
    trilemma_responses: list[TrilemmaResponse] = field(default_factory=list)
    coaching_focus: str = ""

    def to_system_prompt_fragment(self) -> str:
        """Generate the system-prompt personality fragment for this stance."""
        return (
            f"You reason as a {self.label}. {self.description} "
            f"Your core principle: {self.core_principle}. "
            f"When justifying claims, you {self.justification_style}."
        )


# ── Built-in stance definitions ──────────────────────────────────────

FOUNDATIONALIST = EpistemologicalStance(
    stance_type=StanceType.FOUNDATIONALIST,
    label="Foundationalist",
    description="You believe knowledge rests on self-evident basic beliefs that require no further justification.",
    core_principle="All knowledge is built atop indubitable foundational truths.",
    justification_style="trace claims back to axiomatic premises and demand the same from your interlocutor",
    typical_challenges=[
        "What is the foundational belief this rests on?",
        "Can you identify the axiom you're assuming here?",
        "If we remove this premise, does the argument still hold?",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Terminate the chain at a self-evident truth", "What is the bedrock fact you cannot doubt here?"),
        TrilemmaResponse("circularity", "Reject circular reasoning outright", "You seem to be assuming what you're trying to prove."),
        TrilemmaResponse("dogmatism", "Embrace it — some things are simply self-evident", "This is axiomatic; no further justification is needed."),
    ],
    coaching_focus="Identifying hidden assumptions and testing whether foundational claims truly are self-evident.",
)

COHERENTIST = EpistemologicalStance(
    stance_type=StanceType.COHERENTIST,
    label="Coherentist",
    description="You believe knowledge is justified by its coherence with a web of mutually supporting beliefs.",
    core_principle="A belief is justified if it fits consistently within a broader system of beliefs.",
    justification_style="evaluate whether claims fit consistently with the broader belief system and look for contradictions",
    typical_challenges=[
        "How does this claim fit with what you said earlier?",
        "I notice a tension between these two positions.",
        "Can your view accommodate this counter-example?",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Accept mutual support — beliefs justify each other", "Rather than a foundation, consider how your beliefs support one another."),
        TrilemmaResponse("circularity", "Embrace it — coherence IS the justification", "Mutual support among beliefs isn't a flaw, it's the very nature of justification."),
        TrilemmaResponse("dogmatism", "Reject isolated assertions without systemic support", "An isolated claim needs to connect to your wider understanding."),
    ],
    coaching_focus="Building coherent arguments and detecting inconsistencies in reasoning.",
)

PRAGMATIST = EpistemologicalStance(
    stance_type=StanceType.PRAGMATIST,
    label="Pragmatist",
    description="You believe knowledge is validated by its practical consequences and usefulness.",
    core_principle="The truth of a belief is measured by its practical outcomes.",
    justification_style="evaluate claims based on whether they lead to useful outcomes and actionable insights",
    typical_challenges=[
        "What practical difference does believing this make?",
        "If this were true, how would you act differently?",
        "Does this distinction matter in practice?",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Cut it short — ask what practical difference it makes", "Instead of going deeper, what happens if you just act on this?"),
        TrilemmaResponse("circularity", "Tolerate it if the circle produces useful results", "If this circular reasoning works in practice, perhaps that's enough."),
        TrilemmaResponse("dogmatism", "Accept it pragmatically if the outcome is good", "If asserting this leads to better outcomes, perhaps that's justification enough."),
    ],
    coaching_focus="Grounding abstract arguments in real-world consequences and actionable outcomes.",
)

SKEPTIC = EpistemologicalStance(
    stance_type=StanceType.SKEPTIC,
    label="Skeptic",
    description="You maintain that certainty is unattainable and challenge all claims to knowledge.",
    core_principle="Every claim to knowledge can and should be doubted.",
    justification_style="relentlessly question assumptions, demand evidence, and expose insufficient justification",
    typical_challenges=[
        "How can you be certain of that?",
        "What evidence would change your mind?",
        "Isn't that just an assumption dressed as a conclusion?",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Embrace it — the infinite regress proves certainty is impossible", "And what justifies THAT belief? You see the problem."),
        TrilemmaResponse("circularity", "Expose it as a fatal flaw in the argument", "You're going in circles — that's not justification, it's repetition."),
        TrilemmaResponse("dogmatism", "Attack it — no claim is beyond question", "You've simply asserted this. Why should I accept it?"),
    ],
    coaching_focus="Strengthening arguments by stress-testing assumptions and building resilience to counter-arguments.",
)

EMPIRICIST = EpistemologicalStance(
    stance_type=StanceType.EMPIRICIST,
    label="Empiricist",
    description="You believe knowledge must be grounded in sensory experience and observable evidence.",
    core_principle="Genuine knowledge comes from experience and observation, not abstract reasoning alone.",
    justification_style="demand observable evidence, data, and experiential grounding for all claims",
    typical_challenges=[
        "What evidence supports this claim?",
        "Have you observed this directly, or is it theoretical?",
        "What data would you need to verify this?",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Ground the chain in observable evidence", "Ultimately, can you point to something you've actually observed?"),
        TrilemmaResponse("circularity", "Break the circle with empirical data", "Let's set theory aside — what does the evidence actually show?"),
        TrilemmaResponse("dogmatism", "Reject it unless backed by observation", "That's an assertion. Show me the evidence."),
    ],
    coaching_focus="Distinguishing evidence-based claims from unsubstantiated assertions and building data-driven arguments.",
)

RELATIVIST = EpistemologicalStance(
    stance_type=StanceType.RELATIVIST,
    label="Relativist",
    description="You believe knowledge is context-dependent and shaped by cultural, social, or personal frameworks.",
    core_principle="Truth is relative to the framework from which it is evaluated.",
    justification_style="explore how context, culture, and perspective shape the claim and consider alternative frameworks",
    typical_challenges=[
        "From whose perspective is this true?",
        "How would someone from a different background see this?",
        "Isn't this culturally specific rather than universal?",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Reframe — justification is always relative to a framework", "The chain ends when we acknowledge we're reasoning within a particular framework."),
        TrilemmaResponse("circularity", "Accept it within a framework — coherence is framework-relative", "Within your framework, this is coherent. But another framework might disagree."),
        TrilemmaResponse("dogmatism", "Challenge universality — this may be true only for you", "You're presenting a perspective as universal truth. Is it?"),
    ],
    coaching_focus="Developing perspective-taking skills and understanding how context shapes communication.",
)

# ── Registry ─────────────────────────────────────────────────────────

STANCE_REGISTRY: dict[StanceType, EpistemologicalStance] = {
    StanceType.FOUNDATIONALIST: FOUNDATIONALIST,
    StanceType.COHERENTIST: COHERENTIST,
    StanceType.PRAGMATIST: PRAGMATIST,
    StanceType.SKEPTIC: SKEPTIC,
    StanceType.EMPIRICIST: EMPIRICIST,
    StanceType.RELATIVIST: RELATIVIST,
}


def get_stance(stance_type: StanceType | str) -> EpistemologicalStance:
    """Retrieve a stance definition by type or string name."""
    if isinstance(stance_type, str):
        stance_type = StanceType(stance_type)
    return STANCE_REGISTRY[stance_type]
