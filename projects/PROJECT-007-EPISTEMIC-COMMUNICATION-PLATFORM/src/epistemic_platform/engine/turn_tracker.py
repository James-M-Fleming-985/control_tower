"""Turn tracker — triggers coaching analysis at configurable intervals.

Monitors turn count and triggers an async Opus coaching analysis
every N user turns (configurable via settings.coaching_trigger_interval).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from epistemic_platform.config import get_settings
from epistemic_platform.engine.prompt_compositor import build_coaching_prompt
from epistemic_platform.llm.protocol import CoachingLLM, LLMMessage
from epistemic_platform.ontology.actor_ontology import ActorOntology

logger = logging.getLogger(__name__)


@dataclass
class CoachingAnnotation:
    """Structured coaching feedback from Opus."""

    summary: str = ""
    strengths: list[str] | None = None
    improvements: list[str] | None = None
    gricean_scores: dict[str, int] | None = None
    trilemma_awareness: int = 0
    epistemological_insight: str = ""
    turn_number: int = 0
    # M2 additions
    what_happened: str = ""
    why_it_matters: str = ""
    what_to_try: str = ""
    detected_stance: str = ""
    trilemma_horn: str = ""

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "strengths": self.strengths or [],
            "improvements": self.improvements or [],
            "gricean_scores": self.gricean_scores or {},
            "trilemma_awareness": self.trilemma_awareness,
            "epistemological_insight": self.epistemological_insight,
            "turn_number": self.turn_number,
            "what_happened": self.what_happened,
            "why_it_matters": self.why_it_matters,
            "what_to_try": self.what_to_try,
            "detected_stance": self.detected_stance,
            "trilemma_horn": self.trilemma_horn,
        }


class TurnTracker:
    """Tracks user turns and triggers coaching at configurable intervals."""

    def __init__(
        self,
        coaching_llm: CoachingLLM,
        ontology: ActorOntology,
        interval: int | None = None,
    ):
        self._coaching_llm = coaching_llm
        self._ontology = ontology
        self._interval = interval or get_settings().coaching_trigger_interval
        self._user_turn_count = 0

    @property
    def user_turn_count(self) -> int:
        return self._user_turn_count

    def record_user_turn(self) -> bool:
        """Record a user turn. Returns True if coaching should be triggered."""
        self._user_turn_count += 1
        return self._user_turn_count > 0 and self._user_turn_count % self._interval == 0

    async def run_coaching_analysis(
        self,
        messages: list[dict],
        *,
        trilemma_state: dict | None = None,
        detected_stance: str = "",
        stance_confidence: float = 0.0,
    ) -> CoachingAnnotation:
        """Run Opus coaching analysis on the conversation so far.

        Parameters
        ----------
        messages : list[dict]
            The full conversation messages (role + content dicts).
        trilemma_state : dict | None
            Current trilemma state machine snapshot.
        detected_stance : str
            The user's detected epistemological stance.
        stance_confidence : float
            Confidence of the stance detection.

        Returns
        -------
        CoachingAnnotation with structured feedback.
        """
        system_prompt = build_coaching_prompt(
            self._ontology,
            trilemma_state=trilemma_state,
            detected_stance=detected_stance,
            stance_confidence=stance_confidence,
        )

        transcript = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages
        )

        llm_messages = [
            LLMMessage(
                role="user",
                content=f"Analyse this conversation:\n\n{transcript}",
            )
        ]

        response = await self._coaching_llm.analyse(
            messages=llm_messages,
            system_prompt=system_prompt,
        )

        return self._parse_coaching_response(response.content)

    def _parse_coaching_response(self, content: str) -> CoachingAnnotation:
        """Parse Opus JSON response into a CoachingAnnotation."""
        try:
            data = json.loads(content)
            return CoachingAnnotation(
                summary=data.get("summary", ""),
                strengths=data.get("strengths", []),
                improvements=data.get("improvements", []),
                gricean_scores=data.get("gricean_scores", {}),
                trilemma_awareness=data.get("trilemma_awareness", 0),
                epistemological_insight=data.get("epistemological_insight", ""),
                turn_number=self._user_turn_count,
                what_happened=data.get("what_happened", ""),
                why_it_matters=data.get("why_it_matters", ""),
                what_to_try=data.get("what_to_try", ""),
                detected_stance=data.get("detected_stance", ""),
                trilemma_horn=data.get("trilemma_horn", ""),
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse coaching response: %s", e)
            return CoachingAnnotation(
                summary=content[:200],
                turn_number=self._user_turn_count,
            )
