"""Stance detector — classifies the user's epistemological tendency.

Uses the conversation LLM (Sonnet) to analyse the user's justification
patterns and classify which of the 10 epistemological stances they
most closely exhibit.  Runs every N turns (configurable) to limit cost.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from epistemic_platform.llm.protocol import EpistemicActorLLM, LLMMessage
from epistemic_platform.ontology.epistemological_stance import StanceType

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent / "prompts"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    trim_blocks=True,
    lstrip_blocks=True,
)


@dataclass
class StanceDetectionResult:
    """Result of stance classification on user messages."""

    stance: StanceType | None
    confidence: float  # 0.0 – 1.0
    evidence: list[str] = field(default_factory=list)
    secondary_stance: StanceType | None = None
    reasoning: str = ""


@dataclass
class StanceSnapshot:
    """A single observation in the stance history."""

    turn_number: int
    stance: StanceType
    confidence: float


class StanceHistory:
    """Tracks stance detections over the life of a conversation."""

    def __init__(self) -> None:
        self._snapshots: list[StanceSnapshot] = []

    @property
    def snapshots(self) -> list[StanceSnapshot]:
        return list(self._snapshots)

    @property
    def latest(self) -> StanceSnapshot | None:
        return self._snapshots[-1] if self._snapshots else None

    def record(self, turn_number: int, result: StanceDetectionResult) -> bool:
        """Record a detection result. Returns True if the stance shifted."""
        if result.stance is None:
            return False

        shifted = False
        if self._snapshots and self._snapshots[-1].stance != result.stance:
            shifted = True

        self._snapshots.append(StanceSnapshot(
            turn_number=turn_number,
            stance=result.stance,
            confidence=result.confidence,
        ))
        return shifted

    def to_list(self) -> list[dict]:
        return [
            {"turn_number": s.turn_number, "stance": s.stance.value, "confidence": s.confidence}
            for s in self._snapshots
        ]

    @classmethod
    def from_list(cls, data: list[dict]) -> StanceHistory:
        history = cls()
        for item in data:
            try:
                history._snapshots.append(StanceSnapshot(
                    turn_number=item["turn_number"],
                    stance=StanceType(item["stance"]),
                    confidence=item.get("confidence", 0.0),
                ))
            except (KeyError, ValueError):
                continue
        return history


class StanceDetector:
    """Detects the user's epistemological stance from conversation messages."""

    def __init__(self, llm: EpistemicActorLLM) -> None:
        self._llm = llm

    async def detect(self, messages: list[dict]) -> StanceDetectionResult:
        """Classify the user's epistemological stance from their messages.

        Parameters
        ----------
        messages : list[dict]
            Full conversation messages (role + content dicts).

        Returns
        -------
        StanceDetectionResult with primary stance, confidence, and evidence.
        """
        user_messages = [m for m in messages if m.get("role") == "user"]
        if len(user_messages) < 2:
            return StanceDetectionResult(stance=None, confidence=0.0, reasoning="Too few messages")

        tpl = _env.get_template("stance_detection.j2")
        system_prompt = tpl.render()

        # Build transcript of the last ~10 exchanges for analysis
        recent = messages[-20:]
        transcript = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )

        try:
            response = await self._llm.generate(
                messages=[LLMMessage(role="user", content=f"Conversation:\n\n{transcript}")],
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=512,
            )

            data = json.loads(response.content)
            primary = self._parse_stance(data.get("primary_stance"))
            secondary = self._parse_stance(data.get("secondary_stance"))

            return StanceDetectionResult(
                stance=primary,
                confidence=float(data.get("confidence", 0.0)),
                evidence=data.get("evidence", []),
                secondary_stance=secondary,
                reasoning=data.get("reasoning", ""),
            )
        except Exception as e:
            logger.warning("Stance detection failed: %s", e)
            return StanceDetectionResult(
                stance=None,
                confidence=0.0,
                reasoning=f"Detection error: {e}",
            )

    @staticmethod
    def _parse_stance(value: str | None) -> StanceType | None:
        if not value or value == "null":
            return None
        try:
            return StanceType(value)
        except ValueError:
            return None
