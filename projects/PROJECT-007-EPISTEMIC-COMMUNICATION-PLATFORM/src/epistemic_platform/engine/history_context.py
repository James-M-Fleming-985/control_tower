"""History context — builds compact cross-session context for actor prompts.

Compiles a user's recent session history into structured data that can be
injected into the system prompt so actors can:
1. Reference progress and proficiency across prior conversations.
2. Mention insights from conversations with *other* actors (cross-actor
   awareness — as if the faculty of actors discuss the user between sessions).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionSummary:
    """Compact summary of a single completed session."""

    actor_name: str
    actor_stance: str
    turn_count: int
    date: str  # human-readable, e.g. "22 Mar 2026"
    highlights: list[str] = field(default_factory=list)
    stances_detected: list[str] = field(default_factory=list)
    horns_visited: list[str] = field(default_factory=list)
    is_same_actor: bool = False


@dataclass
class UserHistoryContext:
    """Everything an actor needs to know about the user's history."""

    proficiency: dict[str, float] = field(default_factory=dict)
    total_sessions: int = 0
    session_summaries: list[SessionSummary] = field(default_factory=list)

    @property
    def has_history(self) -> bool:
        return self.total_sessions > 0


def build_history_context(
    *,
    sessions: list[Any],
    current_actor_id: int,
    proficiency: dict[str, Any] | None = None,
) -> UserHistoryContext:
    """Build a UserHistoryContext from recent completed sessions.

    Parameters
    ----------
    sessions : list[ConversationSession]
        Recent completed sessions (newest first), with actor relationship loaded.
    current_actor_id : int
        The actor_id of the *current* conversation, so we can distinguish
        "your prior chats" vs "colleague chats".
    proficiency : dict | None
        User's proficiency data from preferences, e.g.
        {"awareness": {"value": 0.45}, "quality": {"value": 0.72}, ...}
    """
    ctx = UserHistoryContext()

    # Parse proficiency
    if proficiency:
        for axis in ("awareness", "quality", "flexibility", "composure"):
            entry = proficiency.get(axis)
            if isinstance(entry, dict):
                ctx.proficiency[axis] = round(entry.get("value", 0) * 100)
            elif isinstance(entry, (int, float)):
                ctx.proficiency[axis] = round(float(entry) * 100)

    ctx.total_sessions = len(sessions)

    for s in sessions:
        actor_name = s.actor.name if s.actor else f"Actor #{s.actor_id}"
        actor_stance = (
            s.actor.epistemological_stance if s.actor else "unknown"
        )

        # Human-readable date
        date_str = ""
        if s.started_at:
            date_str = s.started_at.strftime("%-d %b %Y")

        # Extract highlights from coaching annotations
        highlights: list[str] = []
        for ann in (s.coaching_annotations or [])[-3:]:
            if isinstance(ann, dict):
                text = ann.get("what_happened") or ann.get("summary", "")
                if text and len(text) > 10:
                    highlights.append(text[:150])

        # Stances detected from trilemma_state
        ts = s.trilemma_state or {}
        stances = ts.get("stance_history", [])
        # stance_history entries may be dicts or strings
        stance_labels: list[str] = []
        for entry in stances[-5:]:
            if isinstance(entry, dict):
                label = entry.get("stance", "")
            else:
                label = str(entry)
            if label and label not in stance_labels:
                stance_labels.append(label)

        horns = ts.get("horn_visits", [])
        horn_labels: list[str] = []
        for h in horns:
            label = h.get("horn", str(h)) if isinstance(h, dict) else str(h)
            if label and label not in horn_labels:
                horn_labels.append(label)

        ctx.session_summaries.append(SessionSummary(
            actor_name=actor_name,
            actor_stance=actor_stance,
            turn_count=s.turn_count,
            date=date_str,
            highlights=highlights,
            stances_detected=stance_labels,
            horns_visited=horn_labels,
            is_same_actor=(s.actor_id == current_actor_id),
        ))

    return ctx
