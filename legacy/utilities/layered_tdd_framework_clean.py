"""
Clean Working NADCAP TDD Framework - Audit Compliance Ready
===========================================================

This is a clean, working version of the framework specifically
designed for audit compliance with professional TDD testing.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class RequirementData:
    """Structured representation of a NADCAP requirement."""

    id: str
    text: str
    section: str
    category: Optional[str] = None
    priority: Optional[str] = None


@dataclass
class DocumentData:
    """Structured representation of a controlled document."""

    id: str
    title: str
    type: str
    content_summary: Optional[str] = None
    category: Optional[str] = None


class Layer3_SemanticMatcher:
    """Enhanced semantic matcher for NADCAP compliance with audit-grade accuracy."""

    def __init__(self):
        # Enhanced compatibility matrix for audit compliance
        self.compatibility_matrix = {
            "documentation": {
                "documentation": 1.0,
                "procedures": 0.7,
                "calibration": 0.6,
                "quality": 0.6,
                "training": 0.4,
                "safety": 0.5,
                "environmental": 0.4,
            },
            "calibration": {
                "calibration": 1.0,
                "procedures": 0.8,
                "documentation": 0.6,
                "quality": 0.8,
                "training": 0.5,
                "safety": 0.4,
                "environmental": 0.3,
            },
            "quality": {
                "quality": 1.0,
                "training": 0.8,
                "procedures": 0.8,
                "calibration": 0.8,
                "documentation": 0.6,
                "safety": 0.6,
                "environmental": 0.5,
            },
            "training": {
                "training": 1.0,
                "quality": 0.8,
                "procedures": 0.7,
                "documentation": 0.5,
                "calibration": 0.5,
                "safety": 0.6,
                "environmental": 0.4,
            },
            "safety": {
                "safety": 1.0,
                "procedures": 0.8,
                "environmental": 0.7,
                "training": 0.6,
                "quality": 0.6,
                "documentation": 0.5,
                "calibration": 0.4,
            },
            "procedures": {
                "procedures": 1.0,
                "quality": 0.8,
                "calibration": 0.8,
                "safety": 0.8,
                "documentation": 0.7,
                "training": 0.7,
                "environmental": 0.6,
            },
            "environmental": {
                "environmental": 1.0,
                "safety": 0.7,
                "procedures": 0.6,
                "quality": 0.5,
                "training": 0.4,
                "documentation": 0.4,
                "calibration": 0.3,
            },
        }

        # Anti-pattern detection for audit compliance
        self.anti_patterns = [
            (
                ["drawing", "sketch", "diagram", "layout"],
                ["stress", "relief", "embrittlement"],
            ),
            (["financial", "billing", "cost"], [
             "technical", "process", "equipment"]),
            (["environmental", "waste"], ["training", "qualification"]),
            (["calibration", "measurement"], ["administrative", "billing"]),
        ]

        # Domain-specific term mappings
        self.domain_mappings = {
            "calibration": [
                "calibrat",
                "ammeter",
                "voltmeter",
                "equipment",
                "measuring",
                "accuracy",
                "instrument",
                "gauge",
                "meter",
                "measurement",
            ],
            "documentation": [
                "drawing",
                "sketch",
                "diagram",
                "layout",
                "plan",
                "document",
                "specification",
                "blueprint",
                "schematic",
                "chart",
            ],
            "quality": [
                "quality",
                "inspection",
                "testing",
                "control",
                "assurance",
                "verification",
                "audit",
                "review",
                "check",
                "validate",
            ],
            "training": [
                "training",
                "qualification",
                "certification",
                "education",
                "personnel",
                "competence",
                "skill",
                "learn",
                "course",
            ],
            "safety": [
                "safety",
                "hazard",
                "risk",
                "protection",
                "ppe",
                "emergency",
                "accident",
                "injury",
                "secure",
                "safe",
            ],
            "procedures": [
                "process",
                "procedure",
                "method",
                "operation",
                "workflow",
                "standard",
                "protocol",
                "step",
                "instruction",
            ],
            "environmental": [
                "environmental",
                "waste",
                "emission",
                "disposal",
                "treatment",
                "pollution",
                "discharge",
                "containment",
            ],
        }

    def calculate_semantic_compatibility(
            self, req_cat: str, doc_cat: str) -> float:
        """Calculate semantic compatibility between requirement and document categories."""
        req_cat = req_cat.lower()
        doc_cat = doc_cat.lower()

        if (
            req_cat in self.compatibility_matrix
            and doc_cat in self.compatibility_matrix[req_cat]
        ):
            return self.compatibility_matrix[req_cat][doc_cat]

        # Default compatibility for unknown categories
        return 0.3

    def calculate_contextual_cosine_similarity(
            self, text1: str, text2: str) -> float:
        """Calculate enhanced cosine similarity with domain awareness."""
        try:
            # Tokenize and clean texts
            words1 = [w.lower() for w in text1.split() if len(w) > 2]
            words2 = [w.lower() for w in text2.split() if len(w) > 2]

            if not words1 or not words2:
                return 0.0

            # Create word sets for overlap calculation
            set1 = set(words1)
            set2 = set(words2)

            # Calculate direct overlap
            overlap = len(set1.intersection(set2))
            union = len(set1.union(set2))

            if union == 0:
                return 0.0

            # Basic Jaccard similarity
            jaccard = overlap / union

            # Enhance with semantic relationships
            semantic_score = 0.0

            # Identify domains for each text
            text1_domains = []
            text2_domains = []

            for domain, terms in self.domain_mappings.items():
                if any(term in text1.lower() for term in terms):
                    text1_domains.append(domain)
                if any(term in text2.lower() for term in terms):
                    text2_domains.append(domain)

            # Domain compatibility scoring
            if text1_domains and text2_domains:
                domain_overlap = len(
                    set(text1_domains).intersection(set(text2_domains))
                )

                # Logical cross-domain connections
                logical_cross_domains = [
                    ("quality", "training"),
                    ("calibration", "quality"),
                    ("procedures", "quality"),
                    ("training", "quality"),
                    ("documentation", "procedures"),
                    ("safety", "procedures"),
                    ("environmental", "safety"),
                ]

                cross_domain_bonus = False
                for d1, d2 in logical_cross_domains:
                    if (d1 in text1_domains and d2 in text2_domains) or (
                        d2 in text1_domains and d1 in text2_domains
                    ):
                        cross_domain_bonus = True
                        break

                if domain_overlap == 0:
                    if cross_domain_bonus:
                        # Logical cross-domain connection
                        jaccard *= 0.85
                        semantic_score += 0.1
                    else:
                        # Different domains - apply penalty
                        jaccard *= 0.7
                elif domain_overlap > 0:
                    # Same domain - boost score
                    semantic_score += 0.15

            # Exact term matching bonus
            exact_matches = 0
            for word1 in set1:
                if word1 in set2 and len(word1) > 3:
                    exact_matches += 1

            if exact_matches > 0:
                semantic_score += min(0.2, exact_matches * 0.1)

            # Content length considerations
            content_length = len(text1) + len(text2)
            if content_length > 300:
                semantic_score += 0.05

            return min(1.0, jaccard + semantic_score)

        except Exception as e:
            print(f"⚠️  Similarity calculation error: {e}")
            return 0.0

    def check_anti_patterns(
            self, req_terms: List[str], doc_terms: List[str]) -> bool:
        """Check for anti-patterns that should block matching."""
        req_lower = [t.lower() for t in req_terms]
        doc_lower = [t.lower() for t in doc_terms]

        for req_indicators, doc_indicators in self.anti_patterns:
            req_match = any(
                indicator in " ".join(req_lower) for indicator in req_indicators
            )
            doc_match = any(
                indicator in " ".join(doc_lower) for indicator in doc_indicators
            )

            if req_match and doc_match:
                return True

        return False

    def calculate_semantic_match(
        self, req_text: str, req_cat: str, doc_title: str, doc_cat: str
    ) -> float:
        """Calculate overall semantic match score with audit compliance focus."""
        try:
            # Check for anti-patterns first
            req_terms = req_text.split()
            doc_terms = doc_title.split()

            if self.check_anti_patterns(req_terms, doc_terms):
                return min(
                    0.1, self.calculate_semantic_compatibility(
                        req_cat, doc_cat) * 0.1
                )

            # Calculate individual components
            compatibility = self.calculate_semantic_compatibility(
                req_cat, doc_cat)
            text_similarity = self.calculate_contextual_cosine_similarity(
                req_text, doc_title
            )

            # Weighted combination (60% compatibility, 40% text similarity)
            final_score = min(1.0, (compatibility * 0.6) +
                              (text_similarity * 0.4))

            return final_score

        except Exception as e:
            print(f"⚠️  Semantic match calculation error: {e}")
            return 0.0


# Compatibility functions for existing test structure
def get_enhanced_nadcap_matcher():
    """Get the enhanced NADCAP matcher for testing."""
    return Layer3_SemanticMatcher()


if __name__ == "__main__":
    print("🧪 NADCAP Clean Framework Loaded Successfully")
    matcher = Layer3_SemanticMatcher()

    # Quick validation test
    score = matcher.calculate_semantic_match(
        "Calibration procedures for measuring equipment",
        "calibration",
        "CALIBRATION OF AMMETERS AND VOLTMETERS",
        "calibration",
    )
    print(f"✅ Test score: {score:.3f}")

    # Anti-pattern test
    anti_score = matcher.calculate_semantic_match(
        "Drawing/sketch defining location",
        "documentation",
        "STRESS RELIEF PROCEDURE",
        "safety",
    )
    print(f"🚫 Anti-pattern score: {anti_score:.3f}")
