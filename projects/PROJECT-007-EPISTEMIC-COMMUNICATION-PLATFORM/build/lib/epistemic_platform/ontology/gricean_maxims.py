"""Gricean maxims — conversational cooperation evaluation.

Based on Paul Grice's Cooperative Principle, these maxims provide the
coaching engine with a framework for evaluating user communication quality.
The coaching LLM (Opus) evaluates each user turn against these maxims.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MaximType(str, Enum):
    QUANTITY = "quantity"
    QUALITY = "quality"
    RELATION = "relation"
    MANNER = "manner"


@dataclass(frozen=True)
class GriceanMaxim:
    """Definition of a Gricean conversational maxim."""

    maxim_type: MaximType
    label: str
    principle: str
    sub_maxims: list[str] = field(default_factory=list)
    evaluation_questions: list[str] = field(default_factory=list)

    def to_coaching_prompt_fragment(self) -> str:
        sub = "; ".join(self.sub_maxims) if self.sub_maxims else ""
        return f"Maxim of {self.label}: {self.principle}. Sub-maxims: {sub}"


# ── Built-in maxim definitions ───────────────────────────────────────

QUANTITY = GriceanMaxim(
    maxim_type=MaximType.QUANTITY,
    label="Quantity",
    principle="Make your contribution as informative as required, but not more informative than required.",
    sub_maxims=[
        "Provide enough information for the current purpose",
        "Do not provide more information than needed",
    ],
    evaluation_questions=[
        "Did the user provide sufficient detail to support their claim?",
        "Did the user give too much irrelevant information?",
    ],
)

QUALITY = GriceanMaxim(
    maxim_type=MaximType.QUALITY,
    label="Quality",
    principle="Try to make your contribution one that is true.",
    sub_maxims=[
        "Do not say what you believe to be false",
        "Do not say that for which you lack adequate evidence",
    ],
    evaluation_questions=[
        "Did the user assert something without evidence?",
        "Did the user acknowledge uncertainty where appropriate?",
    ],
)

RELATION = GriceanMaxim(
    maxim_type=MaximType.RELATION,
    label="Relation",
    principle="Be relevant.",
    sub_maxims=[
        "Make your contribution relevant to the current exchange",
    ],
    evaluation_questions=[
        "Did the user stay on topic?",
        "Did tangents serve the argument or distract from it?",
    ],
)

MANNER = GriceanMaxim(
    maxim_type=MaximType.MANNER,
    label="Manner",
    principle="Be perspicuous — avoid obscurity, ambiguity, prolixity, and disorder.",
    sub_maxims=[
        "Avoid obscurity of expression",
        "Avoid ambiguity",
        "Be brief (avoid unnecessary prolixity)",
        "Be orderly",
    ],
    evaluation_questions=[
        "Was the user's response clear and well-structured?",
        "Could the user's point be stated more concisely?",
        "Were logical connections made explicit?",
    ],
)

ALL_MAXIMS: list[GriceanMaxim] = [QUANTITY, QUALITY, RELATION, MANNER]

MAXIM_REGISTRY: dict[MaximType, GriceanMaxim] = {m.maxim_type: m for m in ALL_MAXIMS}


def get_maxim(maxim_type: MaximType | str) -> GriceanMaxim:
    if isinstance(maxim_type, str):
        maxim_type = MaximType(maxim_type)
    return MAXIM_REGISTRY[maxim_type]


def build_coaching_evaluation_prompt() -> str:
    """Build the full Gricean evaluation section for the coaching prompt."""
    sections = [m.to_coaching_prompt_fragment() for m in ALL_MAXIMS]
    return (
        "Evaluate the user's communication against the Gricean Maxims:\n"
        + "\n".join(f"- {s}" for s in sections)
    )
