"""Completion detector — determines when a conversation session is naturally complete.

Criteria for session completion:
1. Minimum turns reached (configurable, default 6)
2. At least one coaching round has occurred
3. One of: trilemma resolved, horn escaped, or turn limit reached

Returns a CompletionSignal consumed by the WebSocket routers to trigger
the session ending flow → achievement engine → optional coach debrief.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CompletionSignal:
    """Signal indicating a session is ready to complete."""

    should_complete: bool = False
    reason: str = ""
    can_debrief: bool = False  # True if coach debrief is available

    def to_dict(self) -> dict[str, Any]:
        return {
            "should_complete": self.should_complete,
            "reason": self.reason,
            "can_debrief": self.can_debrief,
        }


# Default thresholds
_MIN_TURNS = 6
_MAX_TURNS = 30
_MIN_COACHING = 1


class CompletionDetector:
    """Evaluates whether a session has reached natural completion."""

    def __init__(
        self,
        min_turns: int = _MIN_TURNS,
        max_turns: int = _MAX_TURNS,
        min_coaching: int = _MIN_COACHING,
    ) -> None:
        self._min_turns = min_turns
        self._max_turns = max_turns
        self._min_coaching = min_coaching

    def check(
        self,
        turn_count: int,
        coaching_count: int,
        trilemma_state: dict,
        subscription_tier: str = "free",
    ) -> CompletionSignal:
        """Check if the session should be completed.

        Parameters
        ----------
        turn_count : int
            Number of user turns so far.
        coaching_count : int
            Number of coaching annotations so far.
        trilemma_state : dict
            Current trilemma_state from the session.
        subscription_tier : str
            User's subscription tier ("free" or "premium").
        """
        state = trilemma_state.get("state", "exploring")
        can_debrief = subscription_tier == "premium"

        # Hard limit: always end at max turns
        if turn_count >= self._max_turns:
            return CompletionSignal(
                should_complete=True,
                reason="Maximum turn limit reached",
                can_debrief=can_debrief,
            )

        # Not enough turns yet
        if turn_count < self._min_turns:
            return CompletionSignal(should_complete=False)

        # Need at least one coaching round
        if coaching_count < self._min_coaching:
            return CompletionSignal(should_complete=False)

        # Check for natural completion signals
        if state == "resolved":
            return CompletionSignal(
                should_complete=True,
                reason="Trilemma resolved — excellent navigation",
                can_debrief=can_debrief,
            )

        # Check if an escape was attempted
        if state == "escape_attempted":
            return CompletionSignal(
                should_complete=True,
                reason="Escape attempted — session objectives met",
                can_debrief=can_debrief,
            )

        # Check horn visits with escapes
        horn_visits = trilemma_state.get("horn_visits", [])
        escaped = sum(1 for v in horn_visits if v.get("escaped"))
        if escaped > 0 and turn_count >= self._min_turns + 2:
            return CompletionSignal(
                should_complete=True,
                reason="Horn escaped — ready for debrief",
                can_debrief=can_debrief,
            )

        # Extended engagement without resolution — suggest completion at 2x min
        if turn_count >= self._min_turns * 2:
            return CompletionSignal(
                should_complete=True,
                reason="Extended engagement — session ready to wrap up",
                can_debrief=can_debrief,
            )

        return CompletionSignal(should_complete=False)
