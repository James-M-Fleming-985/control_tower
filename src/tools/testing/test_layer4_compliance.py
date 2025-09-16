#!/usr/bin/env python3
"""
🔴 RED PHASE: Layer 4 Compliance Scoring Tests
Test-Driven Development for NADCAP compliance scoring and risk assessment.
"""

import unittest

from layered_tdd_framework import Layer4_ComplianceScorer


class TestLayer4ComplianceScorer(unittest.TestCase):
    """Test Layer 4 compliance scoring functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.scorer = Layer4_ComplianceScorer()

    def test_calculate_compliance_score_high_performance(self):
        """🔴 RED: Test compliance scoring for high-performance matches"""
        # Mock high-quality requirement matches (from Layer 3)
        requirement_matches = [
            ("Calibration procedures documented", 0.89, "calibration"),
            ("Quality control processes verified", 0.85, "quality"),
            ("Training records maintained", 0.78, "training"),
            ("Documentation standards followed", 0.82, "documentation"),
        ]

        result = self.scorer.calculate_compliance_score(requirement_matches)

        # Expected: High compliance score, low risk
        self.assertIn("overall_score", result)
        self.assertIn("risk_level", result)
        self.assertIn("category_breakdown", result)
        self.assertGreater(
            result["overall_score"],
            0.80)  # Should be high compliance
        self.assertEqual(result["risk_level"], "low")

    def test_calculate_compliance_score_critical_gaps(self):
        """🔴 RED: Test compliance scoring with critical gaps"""
        # Mock poor matches indicating compliance issues
        requirement_matches = [
            ("Calibration procedures documented",
             0.25, "calibration"),  # CRITICAL gap
            ("Quality control processes verified", 0.30, "quality"),  # High risk
            ("Training records maintained", 0.45, "training"),  # Medium risk
            ("Safety procedures documented", 0.15, "safety"),  # CRITICAL gap
        ]

        result = self.scorer.calculate_compliance_score(requirement_matches)

        # Expected: Low compliance score, critical risk
        self.assertLess(
            result["overall_score"],
            0.40)  # Should be low compliance
        self.assertEqual(result["risk_level"], "critical")
        self.assertIn("critical_gaps", result)
        self.assertGreater(len(result["critical_gaps"]), 0)

    def test_assess_audit_risk_patterns(self):
        """🔴 RED: Test audit risk assessment based on matching patterns"""
        # Mock requirement matches with concerning patterns
        requirement_matches = [
            ("Calibration equipment verified", 0.35, "calibration"),
            (
                "Calibration procedures followed",
                0.28,
                "calibration",
            ),  # Multiple cal issues
            ("Quality inspection performed", 0.75, "quality"),
            ("Training completed", 0.80, "training"),
        ]

        risk_assessment = self.scorer.assess_audit_risk(requirement_matches)

        # Expected: Pattern-based risk identification
        self.assertIn("risk_level", risk_assessment)
        self.assertIn("risk_factors", risk_assessment)
        self.assertIn("recommendations", risk_assessment)

        # Should flag calibration as high-risk category
        self.assertIn("calibration", str(risk_assessment["risk_factors"]))

    def test_generate_compliance_recommendations(self):
        """🔴 RED: Test generation of actionable compliance recommendations"""
        # Mock mixed compliance scenario
        requirement_matches = [
            (
                "Calibration procedures documented",
                0.45,
                "calibration",
            ),  # Needs improvement
            ("Quality control verified", 0.85, "quality"),  # Good
            ("Training records missing", 0.20, "training"),  # Critical
        ]

        recommendations = self.scorer.generate_compliance_recommendations(
            requirement_matches
        )

        # Expected: Targeted recommendations for each category
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

        # Should include specific actions for problematic areas
        rec_text = " ".join([rec["action"] for rec in recommendations])
        self.assertIn("calibration", rec_text.lower())
        self.assertIn("training", rec_text.lower())

    def test_identify_critical_gaps(self):
        """🔴 RED: Test identification of critical compliance gaps"""
        # Mock scenario with critical gaps
        requirement_matches = [
            ("Critical safety procedure", 0.15, "safety"),  # CRITICAL
            ("Calibration verification", 0.25, "calibration"),  # CRITICAL
            ("Quality documentation", 0.78, "quality"),  # OK
            ("Training completion", 0.82, "training"),  # OK
        ]

        critical_gaps = self.scorer.identify_critical_gaps(requirement_matches)

        # Expected: Clear identification of critical issues
        self.assertIsInstance(critical_gaps, list)
        self.assertEqual(len(critical_gaps), 2)  # Should find 2 critical gaps

        # Should include gap details
        for gap in critical_gaps:
            self.assertIn("requirement", gap)
            self.assertIn("score", gap)
            self.assertIn("category", gap)
            self.assertIn("severity", gap)
            # All should be critical threshold
            self.assertLess(gap["score"], 0.30)


if __name__ == "__main__":
    print("🔴 RUNNING LAYER 4 COMPLIANCE TESTS (RED PHASE)")
    print("=" * 60)

    unittest.main(verbosity=2)
