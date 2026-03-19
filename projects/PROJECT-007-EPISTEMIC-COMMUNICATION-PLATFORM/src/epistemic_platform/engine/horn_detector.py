"""Horn detector — identifies which horn of Agrippa's Trilemma a user is on.

Uses lightweight keyword heuristics first, with an optional LLM fallback
when the heuristics are uncertain. This keeps API costs low while maintaining
accuracy for ambiguous cases.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from epistemic_platform.config import get_settings
from epistemic_platform.llm.protocol import EpistemicActorLLM, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


@dataclass
class HornDetectionResult:
    """Result of horn detection on a user turn."""

    horn: str | None  # "regress", "circularity", "dogmatism", or None
    confidence: float  # 0.0 – 1.0
    evidence: str  # Brief explanation of why this horn was detected


# ── Keyword / pattern heuristics ────────────────────────────────────

_REGRESS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bbut\s+why\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+justifies\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+supports\b", re.IGNORECASE),
    re.compile(r"\bhow\s+do\s+you\s+know\b", re.IGNORECASE),
    re.compile(r"\bwhat('s|\s+is)\s+the\s+(basis|ground|foundation)\b", re.IGNORECASE),
    re.compile(r"\bwhy\s+should\s+I\s+(believe|accept|trust)\b", re.IGNORECASE),
    re.compile(r"\band\s+what\s+justifies\s+that\b", re.IGNORECASE),
    re.compile(r"\bkeep\s+asking\s+why\b", re.IGNORECASE),
    re.compile(r"\binfinite\s+(chain|regress)\b", re.IGNORECASE),
]

_DOGMATISM_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bit('s|\s+is)\s+just\s+(true|obvious|clear)\b", re.IGNORECASE),
    re.compile(r"\bthat('s|\s+is)\s+(self-evident|obvious|axiomatic)\b", re.IGNORECASE),
    re.compile(r"\beveryone\s+knows\b", re.IGNORECASE),
    re.compile(r"\byou\s+just\s+have\s+to\s+(accept|believe)\b", re.IGNORECASE),
    re.compile(r"\bno\s+further\s+(justification|explanation)\b", re.IGNORECASE),
    re.compile(r"\bi\s+don('t|\s+not)\s+need\s+to\s+(explain|justify|prove)\b", re.IGNORECASE),
    re.compile(r"\bthat('s|\s+is)\s+just\s+how\s+it\s+is\b", re.IGNORECASE),
    re.compile(r"\bit('s|\s+is)\s+common\s+sense\b", re.IGNORECASE),
]

_CIRCULARITY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bbecause\s+I\s+said\s+so\b", re.IGNORECASE),
    re.compile(r"\bthat('s|\s+is)\s+why\s+it('s|\s+is)\s+true\b", re.IGNORECASE),
    re.compile(r"\byou('re|\s+are)\s+going\s+in\s+circles\b", re.IGNORECASE),
    re.compile(r"\bcircular\b", re.IGNORECASE),
    re.compile(r"\bbegging\s+the\s+question\b", re.IGNORECASE),
    re.compile(r"\bassuming\s+what\s+(you('re|\s+are)\s+trying\s+to\s+prove|needs\s+to\s+be\s+proven)\b", re.IGNORECASE),
]


def _score_patterns(text: str, patterns: list[re.Pattern[str]]) -> int:
    """Count how many patterns match in the text."""
    return sum(1 for p in patterns if p.search(text))


def detect_horn_heuristic(user_text: str) -> HornDetectionResult:
    """Detect trilemma horn using keyword heuristics only.

    Returns a result with confidence based on how many patterns matched.
    """
    scores = {
        "regress": _score_patterns(user_text, _REGRESS_PATTERNS),
        "dogmatism": _score_patterns(user_text, _DOGMATISM_PATTERNS),
        "circularity": _score_patterns(user_text, _CIRCULARITY_PATTERNS),
    }

    best_horn = max(scores, key=scores.get)  # type: ignore[arg-type]
    best_score = scores[best_horn]

    if best_score == 0:
        return HornDetectionResult(horn=None, confidence=0.0, evidence="No horn patterns detected")

    # Confidence: 1 match = 0.4, 2 = 0.6, 3+ = 0.8
    confidence = min(0.4 + (best_score - 1) * 0.2, 0.8)

    return HornDetectionResult(
        horn=best_horn,
        confidence=confidence,
        evidence=f"Matched {best_score} {best_horn} pattern(s) in user text",
    )


# ── LLM-based classification (fallback) ────────────────────────────

_HORN_CLASSIFICATION_PROMPT = """You are analysing a conversation turn for signs of Agrippa's Trilemma.

The three horns are:
- **regress**: The user keeps demanding justification for justifications (infinite chain of "why?")
- **dogmatism**: The user asserts something as self-evident without justification ("it's just true")
- **circularity**: The user's reasoning loops back to an earlier premise (A because B, B because A)

Analyse ONLY the user's most recent message in context.

Respond with ONLY valid JSON:
{"horn": "regress" | "dogmatism" | "circularity" | null, "confidence": 0.0-1.0, "evidence": "brief reason"}"""


async def detect_horn_llm(
    recent_messages: list[dict],
    llm: EpistemicActorLLM,
) -> HornDetectionResult:
    """Use the conversation LLM to classify which horn the user is on."""
    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in recent_messages[-6:]
    )

    try:
        response: LLMResponse = await llm.generate(
            messages=[LLMMessage(role="user", content=f"Conversation:\n\n{transcript}")],
            system_prompt=_HORN_CLASSIFICATION_PROMPT,
            temperature=0.1,
            max_tokens=256,
        )

        import json
        data = json.loads(response.content)
        horn = data.get("horn")
        if horn not in ("regress", "dogmatism", "circularity", None):
            horn = None
        return HornDetectionResult(
            horn=horn,
            confidence=float(data.get("confidence", 0.0)),
            evidence=data.get("evidence", "LLM classification"),
        )
    except Exception as e:
        logger.warning("LLM horn detection failed: %s", e)
        return HornDetectionResult(horn=None, confidence=0.0, evidence=f"LLM error: {e}")


class HornDetector:
    """Detects which horn of Agrippa's Trilemma a user is on.

    Uses keyword heuristics first. If the result is ambiguous (low confidence)
    and LLM fallback is enabled, calls the conversation LLM for classification.
    """

    def __init__(
        self,
        llm: EpistemicActorLLM | None = None,
        *,
        llm_fallback: bool = True,
        llm_confidence_threshold: float = 0.4,
    ) -> None:
        self._llm = llm
        self._llm_fallback = llm_fallback and llm is not None
        self._threshold = llm_confidence_threshold

    async def detect(self, messages: list[dict]) -> HornDetectionResult:
        """Detect the trilemma horn from the most recent user message.

        Parameters
        ----------
        messages : list[dict]
            Full conversation messages (role + content dicts).

        Returns
        -------
        HornDetectionResult with horn, confidence, and evidence.
        """
        # Find most recent user message
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return HornDetectionResult(horn=None, confidence=0.0, evidence="No user messages")

        latest = user_messages[-1]["content"]

        # Try heuristics first
        result = detect_horn_heuristic(latest)

        # If heuristics are uncertain and LLM fallback is available, use it
        if result.confidence < self._threshold and self._llm_fallback and self._llm:
            result = await detect_horn_llm(messages, self._llm)

        return result
