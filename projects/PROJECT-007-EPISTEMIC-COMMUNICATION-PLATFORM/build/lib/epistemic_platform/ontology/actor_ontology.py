"""ActorOntology — composite ontology for a conversation actor.

Combines an EpistemologicalStance + CommunicationRegister + Gricean evaluation
into a complete actor personality definition. This is the primary interface
used by the LLM adapter to build system prompts.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from epistemic_platform.ontology.communication_register import (
    CommunicationRegister,
    RegisterLevel,
    get_register,
)
from epistemic_platform.ontology.epistemological_stance import (
    EpistemologicalStance,
    StanceType,
    get_stance,
)
from epistemic_platform.ontology.gricean_maxims import build_coaching_evaluation_prompt


@dataclass
class ActorOntology:
    """Complete ontology for a conversation actor.

    This is built from the actor's database config and used to generate
    system prompts for both the conversation LLM and the coaching LLM.
    """

    stance: EpistemologicalStance
    register: CommunicationRegister
    actor_name: str = ""
    custom_instructions: str = ""
    difficulty_modifier: float = 1.0  # 0.5 (gentle) → 2.0 (relentless)
    topics: list[str] = field(default_factory=list)

    def build_conversation_system_prompt(self) -> str:
        """Build the full system prompt for the conversation LLM (Sonnet)."""
        parts = [
            f"You are {self.actor_name}, an AI conversation partner.",
            "",
            "## Epistemological Stance",
            self.stance.to_system_prompt_fragment(),
            "",
            "## Communication Style",
            self.register.to_system_prompt_fragment(),
            "",
            "## Behavioural Rules",
            f"- Challenge intensity: {self.difficulty_modifier:.1f}x (1.0 = balanced, 2.0 = relentless)",
            "- Stay in character at all times",
            "- Never break the fourth wall or reveal you are an AI training tool",
            "- Use your trilemma responses naturally when the conversation reaches justification limits",
            "- End each response with metadata in JSON on the last line: "
            '{"tone": "...", "mood": "...", "energy": "...", "urgency": 0.0-1.0, "connotation": 0.0-1.0}',
        ]

        if self.custom_instructions:
            parts.extend(["", "## Additional Instructions", self.custom_instructions])

        if self.topics:
            parts.extend(["", "## Preferred Topics", ", ".join(self.topics)])

        return "\n".join(parts)

    def build_coaching_system_prompt(self) -> str:
        """Build the system prompt for the coaching LLM (Opus)."""
        return "\n".join([
            "You are an expert communication coach analysing a conversation.",
            f"The user is speaking with a {self.stance.label} ({self.stance.stance_type.value}) "
            f"who communicates in a {self.register.label.lower()} register.",
            "",
            "## Your Task",
            "Analyse the user's most recent turns and provide actionable coaching feedback.",
            f"Focus area: {self.stance.coaching_focus}",
            "",
            "## Evaluation Framework",
            build_coaching_evaluation_prompt(),
            "",
            "## Output Format",
            "Provide a JSON response with:",
            '- "summary": one-sentence overall assessment',
            '- "strengths": list of things the user did well',
            '- "improvements": list of specific, actionable suggestions',
            '- "gricean_scores": {"quantity": 0-10, "quality": 0-10, "relation": 0-10, "manner": 0-10}',
            '- "trilemma_awareness": how well the user navigated justification challenges (0-10)',
        ])

    @classmethod
    def from_config(cls, actor_name: str, config: dict) -> ActorOntology:
        """Build an ActorOntology from the ontology_config JSON stored in the DB."""
        stance = get_stance(config.get("stance", "foundationalist"))
        register = get_register(config.get("register", "consultative"))
        return cls(
            stance=stance,
            register=register,
            actor_name=actor_name,
            custom_instructions=config.get("custom_instructions", ""),
            difficulty_modifier=float(config.get("difficulty_modifier", 1.0)),
            topics=config.get("topics", []),
        )
