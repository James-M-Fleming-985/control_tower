#!/usr/bin/env python3
"""
NADCAP Model Validation Dataset
===============================

Property-based testing with known inputs and expected outputs using actual NADCAP content.
This validates model performance with realistic content sizes and context-relevant scenarios.

Based on analysis:
- Requirements: 156 chars avg, 22 words avg (range: 39-374 chars)
- Documents: 42 chars avg, 6 words avg (range: 13-93 chars)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd

from layered_tdd_framework import Layer3_SemanticMatcher


@dataclass
class TestCase:
    """Represents a single test case with known input and expected output"""

    requirement_text: str
    requirement_category: str
    document_title: str
    document_category: str
    expected_score_range: Tuple[float, float]  # (min, max)
    expected_outcome: str  # 'MATCH', 'NO_MATCH', 'ANTI_PATTERN'
    test_type: str  # 'PERFECT_MATCH', 'GOOD_MATCH', 'POOR_MATCH', 'ANTI_PATTERN'
    context: str  # Description of why this expectation is set


class NADCAPModelValidationDataset:
    """Comprehensive validation dataset based on actual NADCAP content patterns"""

    def __init__(self):
        self.matcher = Layer3_SemanticMatcher()
        self.test_cases = self._create_comprehensive_dataset()

    def _create_comprehensive_dataset(self) -> List[TestCase]:
        """Create comprehensive test dataset with known inputs/outputs"""

        test_cases = []

        # =====================================================================
        # CATEGORY 1: PERFECT MATCHES (Expected: 0.7-1.0)
        # =====================================================================

        # Calibration perfect matches
        test_cases.extend(
            [
                TestCase(
                    requirement_text="Are calibration procedures for measuring equipment documented and followed consistently?",
                    requirement_category="calibration",
                    document_title="CALIBRATION OF AMMETERS AND VOLTMETERS",
                    document_category="calibration",
                    expected_score_range=(0.7, 1.0),
                    expected_outcome="MATCH",
                    test_type="PERFECT_MATCH",
                    context="Same domain, overlapping key terms (calibration, equipment, measuring)",
                ),
                TestCase(
                    requirement_text="Is there evidence that calibration equipment accuracy is verified before use?",
                    requirement_category="calibration",
                    document_title="Calibration Records for Measuring Instruments",
                    document_category="calibration",
                    expected_score_range=(0.7, 1.0),
                    expected_outcome="MATCH",
                    test_type="PERFECT_MATCH",
                    context="Direct semantic match - calibration equipment verification",
                ),
            ]
        )

        # Documentation perfect matches
        test_cases.extend(
            [
                TestCase(
                    requirement_text="Is there a drawing/sketch defining the location of each process line for which NADCAP Accreditation is sought?",
                    requirement_category="documentation",
                    document_title="Process Line Layout Drawings and Specifications",
                    document_category="documentation",
                    expected_score_range=(0.7, 1.0),
                    expected_outcome="MATCH",
                    test_type="PERFECT_MATCH",
                    context="Exact requirement match - drawings defining process line locations",
                ),
                TestCase(
                    requirement_text="Does the Specification List provided by the Auditee contain all applicable main processing specifications?",
                    requirement_category="documentation",
                    document_title="GUIDELINES FOR CREATING DATA SHEETS",
                    document_category="documentation",
                    expected_score_range=(0.6, 0.9),
                    expected_outcome="MATCH",
                    test_type="GOOD_MATCH",
                    context="Related documentation - specifications and data sheets",
                ),
            ]
        )

        # Quality control perfect matches
        test_cases.extend(
            [
                TestCase(
                    requirement_text="Are inspection and test personnel trained in procedures and techniques for deciding what sampling plan to use?",
                    requirement_category="quality",
                    document_title="Quality Control Training Manual for Inspection Personnel",
                    document_category="training",
                    expected_score_range=(0.7, 1.0),
                    expected_outcome="MATCH",
                    test_type="PERFECT_MATCH",
                    context="Quality training match - inspection personnel training procedures",
                ),
            ]
        )

        # =====================================================================
        # CATEGORY 2: GOOD MATCHES (Expected: 0.5-0.7)
        # =====================================================================

        test_cases.extend(
            [
                TestCase(
                    requirement_text="Has the Auditee identified what chemical process scope data shall be collected and analyzed?",
                    requirement_category="process_specific",
                    document_title="SURFACE FINISHES STANDARD FOR GRIT BLASTING",
                    document_category="procedures",
                    expected_score_range=(0.5, 0.7),
                    expected_outcome="MATCH",
                    test_type="GOOD_MATCH",
                    context="Related domains - chemical process and surface finishing procedures",
                ),
                TestCase(
                    requirement_text="Is there evidence that the identified data is collected on a defined frequency and analyzed on a periodic basis?",
                    requirement_category="quality",
                    document_title="Surface Finishes Weekly Physical Check for Compressed Air Contamination",
                    document_category="quality",
                    expected_score_range=(0.5, 0.7),
                    expected_outcome="MATCH",
                    test_type="GOOD_MATCH",
                    context="Data collection frequency matches weekly check procedures",
                ),
            ]
        )

        # =====================================================================
        # CATEGORY 3: POOR MATCHES (Expected: 0.2-0.5)
        # =====================================================================

        test_cases.extend(
            [
                TestCase(
                    requirement_text="Are waste disposal procedures documented and environmentally compliant?",
                    requirement_category="environmental",
                    document_title="CALIBRATION OF AMMETERS AND VOLTMETERS",
                    document_category="calibration",
                    expected_score_range=(0.2, 0.5),
                    expected_outcome="NO_MATCH",
                    test_type="POOR_MATCH",
                    context="Different domains - environmental vs calibration, no semantic overlap",
                ),
                TestCase(
                    requirement_text="If used, are Auditee developed sampling plans available for review and approved by the customer?",
                    requirement_category="quality",
                    document_title="Employee Training Records and Certification Status",
                    document_category="training",
                    expected_score_range=(0.2, 0.5),
                    expected_outcome="NO_MATCH",
                    test_type="POOR_MATCH",
                    context="Different focus - sampling plans vs training records",
                ),
            ]
        )

        # =====================================================================
        # CATEGORY 4: ANTI-PATTERNS (Expected: 0.0-0.3)
        # =====================================================================

        test_cases.extend(
            [
                TestCase(
                    requirement_text="Is there a drawing/sketch defining the location of each process line for which NADCAP Accreditation is sought?",
                    requirement_category="documentation",
                    document_title="STRESS RELIEF AND DE-EMBRITTLEMENT OF PART BATCHES",
                    document_category="safety",
                    expected_score_range=(0.0, 0.3),
                    expected_outcome="ANTI_PATTERN",
                    test_type="ANTI_PATTERN",
                    context="CRITICAL: Drawing requirements should never match stress relief procedures",
                ),
                TestCase(
                    requirement_text="Are personnel safety procedures documented and followed for chemical handling?",
                    requirement_category="safety",
                    document_title="Financial Audit Procedures and Documentation",
                    document_category="general",
                    expected_score_range=(0.0, 0.3),
                    expected_outcome="ANTI_PATTERN",
                    test_type="ANTI_PATTERN",
                    context="Completely unrelated domains - safety vs financial",
                ),
                TestCase(
                    requirement_text="Does the waste management system comply with environmental regulations?",
                    requirement_category="environmental",
                    document_title="CALIBRATION OF AMMETERS AND VOLTMETERS",
                    document_category="calibration",
                    expected_score_range=(0.0, 0.3),
                    expected_outcome="ANTI_PATTERN",
                    test_type="ANTI_PATTERN",
                    context="Environmental waste vs calibration equipment - no logical connection",
                ),
            ]
        )

        # =====================================================================
        # CATEGORY 5: REALISTIC CONTENT SIZE VARIATIONS
        # =====================================================================

        # Short requirements (like real data minimum: 39 chars)
        test_cases.extend(
            [
                TestCase(
                    requirement_text="Are calibration records maintained?",  # 35 chars
                    requirement_category="calibration",
                    document_title="CALIBRATION RECORDS DATABASE",  # 29 chars
                    document_category="calibration",
                    expected_score_range=(0.7, 1.0),
                    expected_outcome="MATCH",
                    test_type="PERFECT_MATCH",
                    context="Short content test - minimal but exact match",
                ),
            ]
        )

        # Long requirements (like real data maximum: 374 chars)
        test_cases.extend(
            [
                TestCase(
                    requirement_text="When the Customer specification states a specific standard, procedure, or method for heat treatment operations, has the Auditee documented evidence that the specified standard, procedure, or method is being followed completely and accurately, including all specified parameters, timing requirements, temperature controls, and verification steps as required by the customer specification and applicable industry standards?",  # ~370 chars
                    requirement_category="process_specific",
                    document_title="Heat Treatment Standard Operating Procedures Manual",  # ~52 chars
                    document_category="procedures",
                    expected_score_range=(0.7, 1.0),
                    expected_outcome="MATCH",
                    test_type="PERFECT_MATCH",
                    context="Long content test - comprehensive requirement with detailed procedure match",
                ),
            ]
        )

        # =====================================================================
        # CATEGORY 6: EDGE CASES WITH REALISTIC CONTENT
        # =====================================================================

        test_cases.extend(
            [
                TestCase(
                    requirement_text="Are measurement instruments calibrated according to documented procedures and maintained in traceable condition?",
                    requirement_category="calibration",
                    document_title="CONTROL OF TESTS AND TEST PIECES WITHIN THE SURFACE FINISHES DEPARTMENT",
                    document_category="quality",
                    expected_score_range=(0.5, 0.8),
                    expected_outcome="MATCH",
                    test_type="GOOD_MATCH",
                    context="Cross-domain match - calibration requirements for quality control testing",
                ),
                TestCase(
                    requirement_text="If the data has shown an opportunity for improvement in the Chemical Process area is the process improvement in progress?",
                    requirement_category="quality",
                    document_title="Abrasive Blasting Qualification Testing",
                    document_category="process_specific",
                    expected_score_range=(0.4, 0.7),
                    expected_outcome="MATCH",
                    test_type="GOOD_MATCH",
                    context="Process improvement data analysis vs specific process testing",
                ),
            ]
        )

        return test_cases

    def run_validation(self) -> Dict:
        """Run complete model validation and return performance metrics"""

        print("🧪 NADCAP MODEL VALIDATION WITH REALISTIC CONTENT")
        print("=" * 70)
        print(f"📊 Dataset: {len(self.test_cases)} test cases")
        print(f"   Content sizes: Req 35-370 chars, Docs 13-93 chars")
        print(
            f"   Categories: {len(set(tc.test_type for tc in self.test_cases))} test types"
        )
        print("=" * 70)

        results = {
            "total_tests": len(self.test_cases),
            "passed": 0,
            "failed": 0,
            "by_category": {},
            "score_accuracy": [],
            "failed_cases": [],
        }

        for i, test_case in enumerate(self.test_cases):
            print(f"\n🔍 Test {i + 1}: {test_case.test_type}")
            print(f"   Requirement: {test_case.requirement_text[:80]}...")
            print(f"   Document: {test_case.document_title}")
            print(
                f"   Expected: {
                    test_case.expected_outcome} ({
                    test_case.expected_score_range[0]:.1f}-{
                    test_case.expected_score_range[1]:.1f})"
            )

            # Calculate actual score
            actual_score = self.matcher.calculate_semantic_match(
                test_case.requirement_text,
                test_case.requirement_category,
                test_case.document_title,
                test_case.document_category,
            )

            print(f"   Actual: {actual_score:.3f}")

            # Check if score is within expected range
            min_expected, max_expected = test_case.expected_score_range
            within_range = min_expected <= actual_score <= max_expected

            if within_range:
                print(f"   ✅ PASS - Score within expected range")
                results["passed"] += 1
            else:
                print(
                    f"   ❌ FAIL - Score outside range ({min_expected:.1f}-{max_expected:.1f})"
                )
                results["failed"] += 1
                results["failed_cases"].append(
                    {
                        "test_case": test_case,
                        "actual_score": actual_score,
                        "deviation": min(
                            abs(actual_score - min_expected),
                            abs(actual_score - max_expected),
                        ),
                    }
                )

            # Track by category
            category = test_case.test_type
            if category not in results["by_category"]:
                results["by_category"][category] = {
                    "passed": 0,
                    "failed": 0,
                    "total": 0,
                }

            results["by_category"][category]["total"] += 1
            if within_range:
                results["by_category"][category]["passed"] += 1
            else:
                results["by_category"][category]["failed"] += 1

            # Track score accuracy
            target_center = (min_expected + max_expected) / 2
            accuracy = (
                1.0 - abs(actual_score - target_center) / target_center
                if target_center > 0
                else 0
            )
            results["score_accuracy"].append(accuracy)

        return results

    def print_summary(self, results: Dict):
        """Print comprehensive validation summary"""

        print("\n" + "=" * 70)
        print("📊 MODEL VALIDATION SUMMARY")
        print("=" * 70)

        total = results["total_tests"]
        passed = results["passed"]
        success_rate = (passed / total) * 100

        print(f"🎯 Overall Performance:")
        print(f"   Tests passed: {passed}/{total} ({success_rate:.1f}%)")
        print(
            f"   Average score accuracy: {
                sum(
                    results['score_accuracy']) / len(
                    results['score_accuracy']) * 100:.1f}%"
        )

        print(f"\n📈 Performance by Category:")
        for category, stats in results["by_category"].items():
            cat_success = (stats["passed"] / stats["total"]) * 100
            print(
                f"   {category}: {
                    stats['passed']}/{
                    stats['total']} ({
                    cat_success:.1f}%)"
            )

        if results["failed_cases"]:
            print(f"\n⚠️  Failed Cases Requiring Tuning:")
            for i, failure in enumerate(
                    results["failed_cases"][:5]):  # Show top 5
                tc = failure["test_case"]
                print(
                    f"   {
                        i +
                        1}. {
                        tc.test_type}: Expected {
                        tc.expected_score_range}, Got {
                        failure['actual_score']:.3f}"
                )
                print(f"      Context: {tc.context}")

        print(f"\n🔧 Model Tuning Recommendations:")
        if success_rate < 85:
            print(
                f"   ❌ Model needs significant tuning (success rate: {
                    success_rate:.1f}%)"
            )
        elif success_rate < 95:
            print(
                f"   ⚠️  Model needs minor tuning (success rate: {
                    success_rate:.1f}%)"
            )
        else:
            print(
                f"   ✅ Model performing well (success rate: {
                    success_rate:.1f}%)"
            )

        return success_rate >= 90  # Return True if model passes validation


def run_nadcap_model_validation():
    """Main function to run NADCAP model validation"""
    dataset = NADCAPModelValidationDataset()
    results = dataset.run_validation()
    model_validated = dataset.print_summary(results)

    if model_validated:
        print(f"\n🎉 MODEL VALIDATION PASSED - Ready for production!")
    else:
        print(f"\n🔧 MODEL VALIDATION FAILED - Tuning required before deployment")

    return model_validated


if __name__ == "__main__":
    run_nadcap_model_validation()
