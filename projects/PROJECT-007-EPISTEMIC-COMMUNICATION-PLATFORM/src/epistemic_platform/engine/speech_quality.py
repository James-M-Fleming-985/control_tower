"""Speech quality analyser — counts fillers, measures cadence, detects repetition.

Provides a ``SpeechQualityReport`` that gets injected into the coach
debrief system prompt so the coach can give concrete feedback on verbal
habits such as filler words, run-on responses, and uneven cadence.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field


# Filler / hedge patterns — case-insensitive, word-boundary-aware
_FILLER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("um", re.compile(r"\bum+\b", re.IGNORECASE)),
    ("uh", re.compile(r"\buh+\b", re.IGNORECASE)),
    ("you know", re.compile(r"\byou know\b", re.IGNORECASE)),
    ("like", re.compile(r"\blike\b", re.IGNORECASE)),
    ("sort of", re.compile(r"\bsort of\b", re.IGNORECASE)),
    ("kind of", re.compile(r"\bkind of\b", re.IGNORECASE)),
    ("I mean", re.compile(r"\bI mean\b", re.IGNORECASE)),
    ("basically", re.compile(r"\bbasically\b", re.IGNORECASE)),
    ("literally", re.compile(r"\bliterally\b", re.IGNORECASE)),
    ("right?", re.compile(r"\bright\s*\?", re.IGNORECASE)),
    ("yeah?", re.compile(r"\byeah\s*\?", re.IGNORECASE)),
    ("actually", re.compile(r"\bactually\b", re.IGNORECASE)),
    ("so", re.compile(r"(?:^|(?<=\.\s))\bso\b", re.IGNORECASE | re.MULTILINE)),
]

# "like" as filler vs legitimate use — exclude common non-filler uses
_LIKE_LEGIT = re.compile(
    r"\b(?:looks? like|feels? like|sounds? like|seems? like|would like|"
    r"I(?:'d)? like|something like|nothing like|just like|much like)\b",
    re.IGNORECASE,
)


@dataclass
class SpeechQualityReport:
    """Structured speech quality analysis for injection into coaching prompt."""

    total_user_turns: int = 0
    total_words: int = 0
    avg_words_per_turn: float = 0.0
    min_words_in_turn: int = 0
    max_words_in_turn: int = 0
    cadence_std_dev: float = 0.0  # standard deviation of words-per-turn

    filler_counts: dict[str, int] = field(default_factory=dict)
    total_fillers: int = 0
    filler_rate_per_100_words: float = 0.0

    repeated_phrases: list[tuple[str, int]] = field(default_factory=list)

    def to_prompt_section(self) -> str:
        """Format as a section for the coach debrief system prompt."""
        if self.total_user_turns == 0:
            return ""

        lines = [
            "## Communication Quality Analysis",
            f"- Total user turns: {self.total_user_turns}",
            f"- Total words spoken: {self.total_words}",
            f"- Average words per turn: {self.avg_words_per_turn:.0f}"
            f" (range: {self.min_words_in_turn}–{self.max_words_in_turn})",
            f"- Cadence variability (std dev): {self.cadence_std_dev:.1f} words",
        ]

        if self.total_fillers > 0:
            lines.append("")
            lines.append(
                f"### Filler Words ({self.total_fillers} total, "
                f"{self.filler_rate_per_100_words:.1f} per 100 words)"
            )
            # Sort by count descending
            for filler, count in sorted(
                self.filler_counts.items(), key=lambda x: -x[1]
            ):
                lines.append(f"- \"{filler}\": {count} times")
        else:
            lines.append("")
            lines.append("### Filler Words: None detected — excellent verbal clarity")

        if self.cadence_std_dev > 20:
            lines.append("")
            lines.append(
                "### Cadence Note: High variability in response length — "
                "some turns were very short while others were very long. "
                "This can make it harder for listeners to follow."
            )

        if self.repeated_phrases:
            lines.append("")
            lines.append("### Repeated Phrases")
            for phrase, count in self.repeated_phrases[:5]:
                lines.append(f"- \"{phrase}\": used {count} times")

        return "\n".join(lines)


def _count_filler_like(text: str) -> int:
    """Count 'like' as filler, excluding legitimate uses."""
    total = len(re.findall(r"\blike\b", text, re.IGNORECASE))
    legit = len(_LIKE_LEGIT.findall(text))
    return max(0, total - legit)


def _extract_ngrams(words: list[str], n: int) -> list[str]:
    """Extract n-grams from a word list."""
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def analyse_speech_quality(messages: list[dict]) -> SpeechQualityReport:
    """Analyse speech quality from a conversation transcript.

    Parameters
    ----------
    messages:
        List of message dicts with ``role`` and ``content`` keys.

    Returns
    -------
    SpeechQualityReport with filler counts, cadence stats, and repeated phrases.
    """
    user_texts: list[str] = []
    for m in messages:
        if m.get("role") == "user":
            content = m.get("content", "").strip()
            if content:
                user_texts.append(content)

    if not user_texts:
        return SpeechQualityReport()

    # Word counts per turn
    word_counts = [len(t.split()) for t in user_texts]
    total_words = sum(word_counts)
    avg_words = total_words / len(word_counts) if word_counts else 0

    # Standard deviation
    if len(word_counts) >= 2:
        mean = avg_words
        variance = sum((w - mean) ** 2 for w in word_counts) / len(word_counts)
        std_dev = variance ** 0.5
    else:
        std_dev = 0.0

    # Filler word counting
    all_user_text = " ".join(user_texts)
    filler_counts: dict[str, int] = {}

    for label, pattern in _FILLER_PATTERNS:
        if label == "like":
            count = _count_filler_like(all_user_text)
        else:
            count = len(pattern.findall(all_user_text))
        if count > 0:
            filler_counts[label] = count

    total_fillers = sum(filler_counts.values())
    filler_rate = (total_fillers / total_words * 100) if total_words > 0 else 0

    # Repeated phrase detection (3-grams and 4-grams)
    all_words = all_user_text.lower().split()
    phrase_counter: Counter[str] = Counter()
    for n in (3, 4):
        ngrams = _extract_ngrams(all_words, n)
        phrase_counter.update(ngrams)

    # Only keep phrases repeated 3+ times
    repeated = [
        (phrase, count)
        for phrase, count in phrase_counter.most_common(20)
        if count >= 3
    ]

    return SpeechQualityReport(
        total_user_turns=len(user_texts),
        total_words=total_words,
        avg_words_per_turn=avg_words,
        min_words_in_turn=min(word_counts) if word_counts else 0,
        max_words_in_turn=max(word_counts) if word_counts else 0,
        cadence_std_dev=std_dev,
        filler_counts=filler_counts,
        total_fillers=total_fillers,
        filler_rate_per_100_words=filler_rate,
        repeated_phrases=repeated,
    )
