"""Prompt compositor — builds system prompts from Jinja2 templates + ontology data.

Assembles the full system prompt for both conversation (Sonnet) and coaching (Opus)
by rendering Jinja2 templates with actor ontology, scenario, and maxim data.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from epistemic_platform.engine.history_context import UserHistoryContext
from epistemic_platform.ontology.actor_ontology import ActorOntology
from epistemic_platform.ontology.gricean_maxims import ALL_MAXIMS

_TEMPLATE_DIR = Path(__file__).parent / "prompts"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    trim_blocks=True,
    lstrip_blocks=True,
)


def build_conversation_prompt(
    ontology: ActorOntology,
    *,
    scenario: dict | None = None,
    mode: str = "text",
    history: UserHistoryContext | None = None,
) -> str:
    """Render the full conversation system prompt for the actor LLM (Sonnet).

    Parameters
    ----------
    ontology : ActorOntology
        The actor's complete ontology (stance + register + config).
    scenario : dict | None
        Optional scenario dict with keys: title, description, objectives,
        evaluation_criteria, difficulty, category.
    mode : str
        Conversation mode ('text' or 'voice'). Affects response style.
    history : UserHistoryContext | None
        Optional cross-session context: user proficiency + prior session
        summaries (own + colleague actors).
    """
    tpl = _env.get_template("system_base.j2")
    return tpl.render(
        actor_name=ontology.actor_name,
        actor_description=ontology.custom_instructions or f"A {ontology.stance.label} communicator.",
        stance_fragment=ontology.stance.to_system_prompt_fragment(),
        register_fragment=ontology.register.to_system_prompt_fragment(),
        difficulty_modifier=f"{ontology.difficulty_modifier:.1f}",
        trilemma_responses=ontology.stance.trilemma_responses,
        custom_instructions=ontology.custom_instructions,
        topics=ontology.topics,
        scenario_title=scenario.get("title") if scenario else None,
        scenario_description=scenario.get("description", "") if scenario else "",
        scenario_objectives=scenario.get("objectives", []) if scenario else [],
        mode=mode,
        history=history,
    )


def build_coaching_prompt(
    ontology: ActorOntology,
    *,
    trilemma_state: dict | None = None,
    detected_stance: str = "",
    stance_confidence: float = 0.0,
) -> str:
    """Render the coaching analysis system prompt for the coaching LLM (Opus)."""
    tpl = _env.get_template("coaching_analysis.j2")
    return tpl.render(
        actor_name=ontology.actor_name,
        stance=ontology.stance,
        register=ontology.register,
        trilemma_responses=ontology.stance.trilemma_responses,
        maxims=ALL_MAXIMS,
        trilemma_state=trilemma_state,
        detected_stance=detected_stance,
        stance_confidence=f"{stance_confidence:.1f}",
    )
