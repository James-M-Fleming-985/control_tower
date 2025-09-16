"""
Test-Driven Development Framework for NADCAP Document Matching
============================================================

This module contains tests to ensure logical document matching for NADCAP requirements.
The current algorithm matches documents like "STRESS RELIEF" to "drawing/sketch" questions,
which is illogical. This TDD framework will fix that.

Current Issue Example:
- Question: "Is there a drawing/sketch defining the location of each process line?"
- Wrong Match: "O_INST-GLO-000191: STRESS RELIEF AND DE-EMBRITTLEMENT" (Score: 0.149)
- Problem: Stress relief procedures have nothing to do with drawings/sketches

Goal: Maintain 100% document utilization while ensuring logical semantic matching.
"""

import re
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


class DocumentMatchingLogic:
    """
    Enhanced document matching logic that goes beyond TF-IDF similarity
    to include semantic understanding and logical constraints.
    """

    def __init__(self):
        # Define semantic categories for NADCAP requirements
        self.requirement_categories = {
            "documentation": [
                "drawing",
                "sketch",
                "diagram",
                "plan",
                "layout",
                "blueprint",
                "documentation",
                "document",
                "record",
                "certificate",
                "report",
            ],
            "procedures": [
                "procedure",
                "process",
                "method",
                "instruction",
                "step",
                "protocol",
                "technique",
                "operation",
            ],
            "calibration": [
                "calibration",
                "calibrate",
                "accuracy",
                "measurement",
                "meter",
                "gauge",
                "instrument",
                "equipment",
                "verification",
            ],
            "training": [
                "training",
                "certification",
                "qualification",
                "competency",
                "education",
                "skill",
                "knowledge",
            ],
            "quality": [
                "quality",
                "inspection",
                "testing",
                "control",
                "assurance",
                "audit",
                "review",
                "verification",
            ],
            "safety": [
                "safety",
                "hazard",
                "risk",
                "protection",
                "ppe",
                "emergency",
                "incident",
                "accident",
            ],
            "environmental": [
                "environmental",
                "waste",
                "disposal",
                "emission",
                "pollution",
                "air",
                "water",
                "chemical",
            ],
        }

        # Define document type patterns
        self.document_patterns = {
            "procedures": ["procedure", "process", "instruction", "method"],
            "calibration": ["calibration", "calibrate", "meter", "gauge"],
            "drawings": ["drawing", "sketch", "diagram", "layout", "plan"],
            "training": ["training", "certification", "qualification"],
            "quality": ["quality", "inspection", "testing", "control"],
            "safety": ["safety", "hazard", "protection", "emergency"],
            "environmental": ["environmental", "waste", "disposal"],
        }

    def categorize_requirement(self, requirement_text: str) -> List[str]:
        """Categorize a NADCAP requirement based on semantic content."""
        requirement_lower = requirement_text.lower()
        categories = []

        for category, keywords in self.requirement_categories.items():
            if any(keyword in requirement_lower for keyword in keywords):
                categories.append(category)

        return categories if categories else ["general"]

    def categorize_document(self, document_title: str) -> List[str]:
        """Categorize a document based on its title and content indicators."""
        doc_lower = document_title.lower()
        categories = []

        for category, patterns in self.document_patterns.items():
            if any(pattern in doc_lower for pattern in patterns):
                categories.append(category)

        return categories if categories else ["general"]

    def calculate_semantic_compatibility(
        self, req_categories: List[str], doc_categories: List[str]
    ) -> float:
        """Calculate semantic compatibility between requirement and document categories."""
        if not req_categories or not doc_categories:
            return 0.1  # Low compatibility for uncategorized items

        # Perfect match
        if any(cat in doc_categories for cat in req_categories):
            return 1.0

        # Compatible categories (manually defined logical relationships)
        compatible_pairs = {
            "documentation": ["drawings", "quality", "procedures"],
            "procedures": ["quality", "safety", "environmental"],
            "calibration": ["quality", "procedures"],
            "training": ["quality", "safety", "procedures"],
            "quality": ["procedures", "calibration", "training"],
            "safety": ["procedures", "environmental", "training"],
            "environmental": ["procedures", "safety", "quality"],
        }

        for req_cat in req_categories:
            if req_cat in compatible_pairs:
                if any(
                    doc_cat in compatible_pairs[req_cat] for doc_cat in doc_categories
                ):
                    return 0.7  # High compatibility

        return 0.3  # Low compatibility

    def enhanced_document_matching(
        self, requirements_df: pd.DataFrame, documents_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Enhanced document matching that combines TF-IDF with semantic logic.
        """
        results = []

        for _, req_row in requirements_df.iterrows():
            requirement_text = req_row["Requirement"]
            req_categories = self.categorize_requirement(requirement_text)

            best_matches = []

            for _, doc_row in documents_df.iterrows():
                doc_title = doc_row["Document_Title"]
                doc_categories = self.categorize_document(doc_title)

                # Calculate semantic compatibility
                semantic_score = self.calculate_semantic_compatibility(
                    req_categories, doc_categories
                )

                # Combine with existing TF-IDF score (if available)
                tfidf_score = doc_row.get(
                    "TF_IDF_Score", 0.5
                )  # Default if not available

                # Weighted combination: 70% semantic, 30% TF-IDF
                combined_score = (0.7 * semantic_score) + (0.3 * tfidf_score)

                best_matches.append(
                    {
                        "Document": doc_title,
                        "Semantic_Score": semantic_score,
                        "TFIDF_Score": tfidf_score,
                        "Combined_Score": combined_score,
                        "Req_Categories": req_categories,
                        "Doc_Categories": doc_categories,
                    }
                )

            # Sort by combined score and take the best match
            best_matches.sort(key=lambda x: x["Combined_Score"], reverse=True)
            best_match = best_matches[0] if best_matches else None

            results.append(
                {
                    "Requirement": requirement_text,
                    "Primary_Evidence": (
                        best_match["Document"] if best_match else "No Match"
                    ),
                    "Combined_Score": best_match["Combined_Score"] if best_match else 0,
                    "Semantic_Score": best_match["Semantic_Score"] if best_match else 0,
                    "Match_Logic": f"Req: {req_categories} -> Doc: {best_match['Doc_Categories'] if best_match else []}",
                }
            )

        return pd.DataFrame(results)


class TestDocumentMatching:
    """Test cases to ensure logical document matching."""

    def setup_method(self):
        """Set up test data and matching logic."""
        self.matcher = DocumentMatchingLogic()

        # Sample NADCAP requirements (based on real examples)
        self.test_requirements = pd.DataFrame(
            [
                {
                    "Requirement": "Is there a drawing/sketch defining the location of each process line for which Nadcap Accreditation is sought?",
                    "Expected_Category": ["documentation"],
                },
                {
                    "Requirement": "Did the Auditee upload a copy of the documents listed in 2.3.3, to eAuditNet at least 30 days prior to the audit?",
                    "Expected_Category": ["documentation", "quality"],
                },
                {
                    "Requirement": "Are all personnel operating the plating line trained and certified?",
                    "Expected_Category": ["training"],
                },
                {
                    "Requirement": "Are ammeters and voltmeters calibrated according to procedure?",
                    "Expected_Category": ["calibration"],
                },
            ]
        )

        # Sample documents (based on real inventory)
        self.test_documents = pd.DataFrame(
            [
                {
                    "Document_Title": "O_INST-GLO-000191: STRESS RELIEF AND DE-EMBRITTLEMENT OF PART BATCHES OF COMPONENTS TAKEN FROM THE PLATING LINES",
                    "Expected_Category": ["procedures", "safety"],
                },
                {
                    "Document_Title": "O_INST-GLO-000170: Calibration of Ammeters and Voltmeters",
                    "Expected_Category": ["calibration"],
                },
                {
                    "Document_Title": "DRAWING-PLT-001: Plating Line Layout and Process Flow",
                    "Expected_Category": ["drawings", "documentation"],
                },
                {
                    "Document_Title": "TRAIN-CERT-001: Personnel Training and Certification Program",
                    "Expected_Category": ["training"],
                },
            ]
        )

    def test_requirement_categorization(self):
        """Test that requirements are correctly categorized."""
        # Test drawing/sketch requirement
        req_text = (
            "Is there a drawing/sketch defining the location of each process line?"
        )
        categories = self.matcher.categorize_requirement(req_text)
        assert (
            "documentation" in categories
        ), f"Drawing requirement should be categorized as documentation, got: {categories}"

        # Test training requirement
        req_text = "Are all personnel operating the plating line trained and certified?"
        categories = self.matcher.categorize_requirement(req_text)
        assert (
            "training" in categories
        ), f"Training requirement should be categorized as training, got: {categories}"

        # Test calibration requirement
        req_text = "Are ammeters and voltmeters calibrated according to procedure?"
        categories = self.matcher.categorize_requirement(req_text)
        assert (
            "calibration" in categories
        ), f"Calibration requirement should be categorized as calibration, got: {categories}"

    def test_document_categorization(self):
        """Test that documents are correctly categorized."""
        # Test stress relief document
        doc_title = "STRESS RELIEF AND DE-EMBRITTLEMENT OF PART BATCHES"
        categories = self.matcher.categorize_document(doc_title)
        assert (
            "procedures" in categories or "safety" in categories
        ), f"Stress relief should be procedure/safety, got: {categories}"

        # Test calibration document
        doc_title = "Calibration of Ammeters and Voltmeters"
        categories = self.matcher.categorize_document(doc_title)
        assert (
            "calibration" in categories
        ), f"Calibration document should be categorized as calibration, got: {categories}"

        # Test drawing document
        doc_title = "Plating Line Layout and Process Flow"
        categories = self.matcher.categorize_document(doc_title)
        assert (
            "drawings" in categories or "documentation" in categories
        ), f"Layout should be drawing/documentation, got: {categories}"

    def test_semantic_compatibility(self):
        """Test semantic compatibility scoring."""
        # High compatibility: documentation requirement with drawing document
        req_cats = ["documentation"]
        doc_cats = ["drawings"]
        score = self.matcher.calculate_semantic_compatibility(
            req_cats, doc_cats)
        assert (
            score >= 0.7
        ), f"Documentation-Drawing compatibility should be high, got: {score}"

        # Low compatibility: documentation requirement with stress relief
        # procedure
        req_cats = ["documentation"]
        doc_cats = ["procedures", "safety"]
        score = self.matcher.calculate_semantic_compatibility(
            req_cats, doc_cats)
        assert (
            score <= 0.7
        ), f"Documentation-Procedure compatibility should be lower, got: {score}"

        # Perfect match: calibration requirement with calibration document
        req_cats = ["calibration"]
        doc_cats = ["calibration"]
        score = self.matcher.calculate_semantic_compatibility(
            req_cats, doc_cats)
        assert score == 1.0, f"Perfect category match should score 1.0, got: {score}"

    def test_illogical_matching_prevention(self):
        """Test that illogical matches are prevented."""
        # This should NOT match stress relief to drawing requirement
        drawing_req = (
            "Is there a drawing/sketch defining the location of each process line?"
        )
        stress_doc = "STRESS RELIEF AND DE-EMBRITTLEMENT OF PART BATCHES"

        req_cats = self.matcher.categorize_requirement(drawing_req)
        doc_cats = self.matcher.categorize_document(stress_doc)
        compatibility = self.matcher.calculate_semantic_compatibility(
            req_cats, doc_cats
        )

        assert (
            compatibility < 0.5
        ), f"Stress relief should not match drawing requirement well, got: {compatibility}"

    def test_logical_matching_promotion(self):
        """Test that logical matches are promoted."""
        # This SHOULD match calibration requirement to calibration document
        cal_req = "Are ammeters and voltmeters calibrated according to procedure?"
        cal_doc = "Calibration of Ammeters and Voltmeters"

        req_cats = self.matcher.categorize_requirement(cal_req)
        doc_cats = self.matcher.categorize_document(cal_doc)
        compatibility = self.matcher.calculate_semantic_compatibility(
            req_cats, doc_cats
        )

        assert (
            compatibility >= 0.9
        ), f"Calibration requirement should match calibration document well, got: {compatibility}"


def run_tests():
    """Run all tests and report results."""
    test_class = TestDocumentMatching()
    test_class.setup_method()

    tests = [
        ("Requirement Categorization", test_class.test_requirement_categorization),
        ("Document Categorization", test_class.test_document_categorization),
        ("Semantic Compatibility", test_class.test_semantic_compatibility),
        (
            "Illogical Matching Prevention",
            test_class.test_illogical_matching_prevention,
        ),
        ("Logical Matching Promotion", test_class.test_logical_matching_promotion),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            test_func()
            results.append(f"✅ {test_name}: PASSED")
        except AssertionError as e:
            results.append(f"❌ {test_name}: FAILED - {str(e)}")
        except Exception as e:
            results.append(f"🔥 {test_name}: ERROR - {str(e)}")

    return results


if __name__ == "__main__":
    print("NADCAP Document Matching TDD Framework")
    print("=" * 50)
    results = run_tests()
    for result in results:
        print(result)
