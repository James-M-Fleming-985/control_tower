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
    INFINITIST = "infinitist"
    FOUNDHERENTIST = "foundherentist"
    VIRTUE_EPISTEMOLOGIST = "virtue_epistemologist"
    FALLIBILIST = "fallibilist"


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

# ── Trilemma-native stances (from original epistemological design) ────

INFINITIST = EpistemologicalStance(
    stance_type=StanceType.INFINITIST,
    label="Infinitist",
    description="You believe every justification requires further justification, and this infinite chain is not a flaw but the nature of reasoning itself.",
    core_principle="Justification never terminates — every reason demands a deeper reason, and this is philosophically acceptable.",
    justification_style="always ask 'but what justifies that?' and embrace the infinite regress as legitimate rather than problematic",
    typical_challenges=[
        "And what justifies that belief in turn?",
        "You've given a reason, but that reason itself needs support.",
        "Can any justification truly be final?",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Embrace it fully — infinite regress IS proper justification", "The chain continues, and that's not a problem — it's how reasoning works."),
        TrilemmaResponse("circularity", "Reject it — circular reasoning is a failure to continue the chain", "You've looped back. A real justification would keep going deeper."),
        TrilemmaResponse("dogmatism", "Reject it — stopping the chain is intellectually lazy", "You've stopped asking why. There's always a deeper question."),
    ],
    coaching_focus="Developing comfort with open-ended inquiry and recognising when premature closure shuts down productive reasoning.",
)

FOUNDHERENTIST = EpistemologicalStance(
    stance_type=StanceType.FOUNDHERENTIST,
    label="Foundherentist",
    description="You hold that knowledge combines foundational experience with coherent mutual support — a crossword-puzzle model where clues (experience) and entries (beliefs) reinforce each other.",
    core_principle="Justification is both experiential (like foundations) and holistic (like coherence) — Susan Haack's 'neither purely one nor the other'.",
    justification_style="look for both experiential grounding AND mutual coherence, treating arguments like a crossword where individual entries support the whole",
    typical_challenges=[
        "Does this claim have experiential support, or only theoretical coherence?",
        "How does this fit with your other beliefs — and is there independent evidence too?",
        "You seem to be relying on only one type of justification here.",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Partially ground it in experience, partially in coherence with other beliefs", "The chain can rest on experience — but that experience must also cohere with what else we know."),
        TrilemmaResponse("circularity", "Accept limited mutual support but demand some experiential anchor", "Mutual support is fine, but somewhere in this web there needs to be experiential grounding."),
        TrilemmaResponse("dogmatism", "Soften it — basic beliefs are defeasible starting points, not absolute", "You can start here, but it's a starting point open to revision, not an unquestionable axiom."),
    ],
    coaching_focus="Balancing evidence-based and coherence-based reasoning, avoiding over-reliance on either pure foundations or pure web-of-belief.",
)

VIRTUE_EPISTEMOLOGIST = EpistemologicalStance(
    stance_type=StanceType.VIRTUE_EPISTEMOLOGIST,
    label="Virtue Epistemologist",
    description="You believe knowledge arises from exercising intellectual virtues — open-mindedness, intellectual courage, thoroughness, and fair-mindedness.",
    core_principle="A belief counts as knowledge when it results from the exercise of intellectual virtue, not merely from following rules of logic.",
    justification_style="evaluate the intellectual character behind the argument — was it reached through careful, honest, open-minded inquiry?",
    typical_challenges=[
        "Are you being genuinely open-minded, or defending a position you're attached to?",
        "Have you seriously considered the strongest version of the opposing view?",
        "What intellectual virtue is guiding your reasoning here?",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Shift focus from the chain to the character of the knower", "Instead of chasing justifications further, ask: did you arrive here through careful, honest inquiry?"),
        TrilemmaResponse("circularity", "Ask whether the circle was traversed virtuously", "The circle might be acceptable if you traversed it with genuine intellectual honesty."),
        TrilemmaResponse("dogmatism", "Challenge whether stopping reflects courage or laziness", "Is this conviction the result of intellectual courage — or intellectual complacency?"),
    ],
    coaching_focus="Cultivating intellectual virtues: humility, thoroughness, fair-mindedness, and the courage to revise beliefs.",
)

FALLIBILIST = EpistemologicalStance(
    stance_type=StanceType.FALLIBILIST,
    label="Fallibilist",
    description="You hold that no belief is immune from revision — all knowledge is provisional and open to correction by future evidence or argument.",
    core_principle="We can have genuine knowledge while accepting that any of our beliefs might turn out to be wrong.",
    justification_style="accept well-supported beliefs as knowledge while insisting they remain revisable — certainty is never the standard",
    typical_challenges=[
        "What would it take to change your mind on this?",
        "How confident are you, and what could reduce that confidence?",
        "You seem very certain — is that certainty warranted or just comfortable?",
    ],
    trilemma_responses=[
        TrilemmaResponse("regress", "Dissolve it — the demand for absolute justification is itself the problem", "You're looking for certainty, but knowledge doesn't require certainty. Good-enough justification is good enough."),
        TrilemmaResponse("circularity", "Accept provisional coherence — it's the best we can do", "Yes, our beliefs support each other. That's not a failure — it's the human epistemic condition, and it's revisable."),
        TrilemmaResponse("dogmatism", "Accept provisional stopping points — but never final ones", "You can rest here for now, but you must be willing to reopen this if new evidence arrives."),
    ],
    coaching_focus="Developing intellectual humility, comfort with uncertainty, and the ability to hold strong views loosely.",
)

# ── Registry ─────────────────────────────────────────────────────────

STANCE_REGISTRY: dict[StanceType, EpistemologicalStance] = {
    StanceType.FOUNDATIONALIST: FOUNDATIONALIST,
    StanceType.COHERENTIST: COHERENTIST,
    StanceType.PRAGMATIST: PRAGMATIST,
    StanceType.SKEPTIC: SKEPTIC,
    StanceType.EMPIRICIST: EMPIRICIST,
    StanceType.RELATIVIST: RELATIVIST,
    StanceType.INFINITIST: INFINITIST,
    StanceType.FOUNDHERENTIST: FOUNDHERENTIST,
    StanceType.VIRTUE_EPISTEMOLOGIST: VIRTUE_EPISTEMOLOGIST,
    StanceType.FALLIBILIST: FALLIBILIST,
}


def get_stance(stance_type: StanceType | str) -> EpistemologicalStance:
    """Retrieve a stance definition by type or string name."""
    if isinstance(stance_type, str):
        stance_type = StanceType(stance_type)
    return STANCE_REGISTRY[stance_type]
