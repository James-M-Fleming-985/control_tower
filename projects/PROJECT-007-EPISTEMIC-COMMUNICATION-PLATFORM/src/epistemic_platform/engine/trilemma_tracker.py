"""Trilemma tracker — state machine for Agrippa's Trilemma navigation.

Tracks where a user is in the trilemma (regress / circularity / dogmatism),
records horn visits, and provides escape strategies from the actor's stance.
Serialises to/from the ConversationSession.trilemma_state JSON field.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from epistemic_platform.ontology.epistemological_stance import (
    EpistemologicalStance,
    StanceType,
    TrilemmaResponse,
    get_stance,
)


class TrilemmaState(str, Enum):
    """Possible states in the trilemma state machine."""

    EXPLORING = "exploring"
    APPROACHING_HORN = "approaching_horn"
    ON_HORN_REGRESS = "on_horn_regress"
    ON_HORN_DOGMATISM = "on_horn_dogmatism"
    ON_HORN_CIRCULARITY = "on_horn_circularity"
    ESCAPE_ATTEMPTED = "escape_attempted"
    RESOLVED = "resolved"


# Valid transitions: current_state → set of allowed next states
_TRANSITIONS: dict[TrilemmaState, set[TrilemmaState]] = {
    TrilemmaState.EXPLORING: {
        TrilemmaState.APPROACHING_HORN,
    },
    TrilemmaState.APPROACHING_HORN: {
        TrilemmaState.ON_HORN_REGRESS,
        TrilemmaState.ON_HORN_DOGMATISM,
        TrilemmaState.ON_HORN_CIRCULARITY,
        TrilemmaState.EXPLORING,  # false alarm
    },
    TrilemmaState.ON_HORN_REGRESS: {
        TrilemmaState.ESCAPE_ATTEMPTED,
        TrilemmaState.EXPLORING,  # topic change
    },
    TrilemmaState.ON_HORN_DOGMATISM: {
        TrilemmaState.ESCAPE_ATTEMPTED,
        TrilemmaState.EXPLORING,
    },
    TrilemmaState.ON_HORN_CIRCULARITY: {
        TrilemmaState.ESCAPE_ATTEMPTED,
        TrilemmaState.EXPLORING,
    },
    TrilemmaState.ESCAPE_ATTEMPTED: {
        TrilemmaState.RESOLVED,
        TrilemmaState.EXPLORING,  # escape failed, start over
        TrilemmaState.ON_HORN_REGRESS,  # fell into a different horn
        TrilemmaState.ON_HORN_DOGMATISM,
        TrilemmaState.ON_HORN_CIRCULARITY,
    },
    TrilemmaState.RESOLVED: {
        TrilemmaState.EXPLORING,  # new topic
    },
}

_HORN_STATES = {
    "regress": TrilemmaState.ON_HORN_REGRESS,
    "dogmatism": TrilemmaState.ON_HORN_DOGMATISM,
    "circularity": TrilemmaState.ON_HORN_CIRCULARITY,
}


@dataclass
class HornVisit:
    """Record of a single horn encounter."""

    horn: str
    turn_number: int
    escaped: bool = False
    escape_strategy: str = ""


class TrilemmaStateMachine:
    """Tracks a user's journey through Agrippa's Trilemma within a session."""

    def __init__(self) -> None:
        self._state = TrilemmaState.EXPLORING
        self._current_horn: str | None = None
        self._horn_visits: list[HornVisit] = []
        self._transition_log: list[dict[str, str]] = []

    @property
    def state(self) -> TrilemmaState:
        return self._state

    @property
    def current_horn(self) -> str | None:
        return self._current_horn

    @property
    def horn_visits(self) -> list[HornVisit]:
        return list(self._horn_visits)

    def transition(self, new_state: TrilemmaState, *, horn: str | None = None, turn: int = 0) -> bool:
        """Attempt a state transition. Returns True if valid, False if rejected."""
        if new_state not in _TRANSITIONS.get(self._state, set()):
            return False

        old_state = self._state
        self._state = new_state
        self._transition_log.append({
            "from": old_state.value,
            "to": new_state.value,
            "horn": horn or "",
            "turn": str(turn),
        })

        # Entering a horn
        if new_state in _HORN_STATES.values():
            horn_name = horn or next(
                (k for k, v in _HORN_STATES.items() if v == new_state), None
            )
            self._current_horn = horn_name
            self._horn_visits.append(HornVisit(horn=horn_name or "unknown", turn_number=turn))

        # Escape attempted
        elif new_state == TrilemmaState.ESCAPE_ATTEMPTED:
            if self._horn_visits:
                self._horn_visits[-1].escaped = True

        # Resolved or back to exploring
        elif new_state in (TrilemmaState.RESOLVED, TrilemmaState.EXPLORING):
            self._current_horn = None

        return True

    def detect_horn_and_transition(self, horn: str | None, confidence: float, turn: int) -> None:
        """Convenience: given a horn detection result, update the state machine."""
        if horn is None or confidence < 0.3:
            # No horn detected or low confidence — might return to exploring
            if self._state == TrilemmaState.APPROACHING_HORN:
                self.transition(TrilemmaState.EXPLORING, turn=turn)
            return

        if self._state == TrilemmaState.EXPLORING:
            self.transition(TrilemmaState.APPROACHING_HORN, horn=horn, turn=turn)
            # Immediately move to the horn if confidence is high
            if confidence >= 0.6:
                horn_state = _HORN_STATES.get(horn)
                if horn_state:
                    self.transition(horn_state, horn=horn, turn=turn)
        elif self._state == TrilemmaState.APPROACHING_HORN:
            horn_state = _HORN_STATES.get(horn)
            if horn_state:
                self.transition(horn_state, horn=horn, turn=turn)
        elif self._state == TrilemmaState.ESCAPE_ATTEMPTED:
            # Fell into another horn after attempting escape
            horn_state = _HORN_STATES.get(horn)
            if horn_state:
                self.transition(horn_state, horn=horn, turn=turn)

    def mark_escape_attempted(self, strategy: str, turn: int) -> None:
        """Mark that the user attempted an escape from the current horn."""
        if self._state in _HORN_STATES.values():
            self.transition(TrilemmaState.ESCAPE_ATTEMPTED, turn=turn)
            if self._horn_visits:
                self._horn_visits[-1].escape_strategy = strategy

    def mark_resolved(self, turn: int) -> None:
        """Mark the current trilemma encounter as resolved."""
        if self._state == TrilemmaState.ESCAPE_ATTEMPTED:
            self.transition(TrilemmaState.RESOLVED, turn=turn)

    # ── Serialisation ────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialise to JSON-safe dict for ConversationSession.trilemma_state."""
        return {
            "state": self._state.value,
            "current_horn": self._current_horn,
            "horn_visits": [
                {
                    "horn": v.horn,
                    "turn_number": v.turn_number,
                    "escaped": v.escaped,
                    "escape_strategy": v.escape_strategy,
                }
                for v in self._horn_visits
            ],
            "transition_log": self._transition_log,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrilemmaStateMachine:
        """Restore from a ConversationSession.trilemma_state dict."""
        sm = cls()
        state_str = data.get("state", "exploring")
        try:
            sm._state = TrilemmaState(state_str)
        except ValueError:
            sm._state = TrilemmaState.EXPLORING
        sm._current_horn = data.get("current_horn")
        sm._horn_visits = [
            HornVisit(
                horn=v.get("horn", "unknown"),
                turn_number=v.get("turn_number", 0),
                escaped=v.get("escaped", False),
                escape_strategy=v.get("escape_strategy", ""),
            )
            for v in data.get("horn_visits", [])
        ]
        sm._transition_log = data.get("transition_log", [])
        return sm


def get_escape_strategy(stance_type: StanceType | str, horn: str) -> TrilemmaResponse | None:
    """Look up the escape strategy for a given stance and horn.

    Parameters
    ----------
    stance_type : StanceType or str
        The epistemological stance to look up.
    horn : str
        One of "regress", "circularity", "dogmatism".

    Returns
    -------
    TrilemmaResponse or None if no matching strategy exists.
    """
    stance = get_stance(stance_type)
    for response in stance.trilemma_responses:
        if response.horn == horn:
            return response
    return None
