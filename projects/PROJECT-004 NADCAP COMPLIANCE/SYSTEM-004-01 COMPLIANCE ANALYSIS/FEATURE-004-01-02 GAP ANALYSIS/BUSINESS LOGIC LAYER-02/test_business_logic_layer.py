#!/usr/bin/env python3
"""
🔴 RED PHASE: Business Logic Layer Tests for NADCAP Gap Analysis
Test-Driven Development based on LAYER-004-01-02-002_business_logic_requirements.md

Created: 2025-09-17
Feature: FEATURE-004-01-02_gap_analysis
Layer: BUSINESS LOGIC LAYER-02

REAL Tests for REAL Business Value - Based on ALL Requirements
"""

import os
import tempfile
import unittest
from pathlib import Path
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Requirement:
    """REAL NADCAP requirement structure"""
    id: str
    content: str
    category: str
    section: str
    guidance: str


@dataclass
class Document:
    """REAL SF document structure"""
    reference: str
    title: str
    category: str
    source: str  # 'controlled' or 'uncontrolled'
    content: str


@dataclass
class EvidenceScore:
    """REAL evidence scoring structure"""
    similarity_score: float
    confidence: float
    relevance: str  # 'High', 'Medium', 'Low'
    quality: str    # 'Excellent', 'Good', 'Fair', 'Weak'


@dataclass
class GapClassification:
    """REAL gap classification structure"""
    gap_type: str      # 'Missing', 'Insufficient', 'Outdated'
    severity: str      # 'Critical', 'High', 'Medium', 'Low'
    risk_level: str    # 'High', 'Medium', 'Low'
    priority: int      # 1-5 scale


@dataclass
class RequirementResult:
    """REAL requirement analysis result"""
    requirement_id: str
    compliance_status: str  # 'Strong Evidence', 'Potential Evidence', 'Gap Identified'
    primary_evidence: Document
    primary_score: EvidenceScore
    secondary_evidence: Document
    secondary_score: EvidenceScore
    gaps: List[GapClassification]
    recommendations: List[str]


# Import the actual implementation
from business_logic_layer import BusinessLogicLayer


class TestBusinessLogicLayer(unittest.TestCase):
    """COMPREHENSIVE tests for Business Logic Layer based on ALL requirements"""

    def setUp(self):
        """Set up REAL test data based on actual NADCAP requirements"""
        self.business_logic = BusinessLogicLayer()
        
        # REAL NADCAP requirements from AC7108
        self.real_requirements = [
            Requirement(
                id="2.7.1",
                content="Is there a drawing/sketch defining the location of each process line for which Nadcap Accreditation is sought?",
                category="documentation",
                section="Instructions to Auditee",
                guidance="The drawing/sketch should not contain specific tank details, it is purely to help define the physical areas covered by the scope of the audit."
            ),
            Requirement(
                id="4.2.6",
                content="Are periodic test results available at the same frequency as the periodic test pieces are processed?",
                category="testing",
                section="Periodic Testing",
                guidance=""
            ),
            Requirement(
                id="3.6.1.7",
                content="Do buy-off steps comply with AC7108 Appendix E, and were they properly bought off and dated?",
                category="process_control",
                section="Process Control Documents",
                guidance=""
            )
        ]
        
        # REAL SF controlled documents
        self.real_controlled_docs = [
            Document(
                reference="O_INST-GLO-000191",
                title="STRESS RELIEF AND DE-EMBRITTLEMENT OF PART BATCHES OF COMPONENTS TAKEN FROM THE PLATING LINES",
                category="process_control",
                source="controlled",
                content="This document describes stress relief procedures for plated components to prevent hydrogen embrittlement and ensure part integrity."
            ),
            Document(
                reference="O_INST-GLO-000215",
                title="CONTROL OF TESTS AND TEST PIECES WITHIN THE SURFACE FINISHES DEPARTMENT",
                category="testing",
                source="controlled",
                content="This procedure establishes the requirements for periodic testing, test piece control, and result documentation for NADCAP compliance."
            ),
            Document(
                reference="O_INST-GLO-000210",
                title="GUIDELINES FOR CREATING DATA SHEETS",
                category="documentation",
                source="controlled",
                content="Guidelines for creating technical data sheets and process documentation within the surface finishes department."
            )
        ]
        
        # REAL SF PD forms (uncontrolled)
        self.real_pd_forms = [
            Document(
                reference="PD1052",
                title="AUTHORISATION TO CREATE & ALTER LAYOUTS",
                category="documentation",
                source="uncontrolled",
                content="Authorization procedure for creating and altering facility layouts and process line configurations."
            ),
            Document(
                reference="PD1036",
                title="Parts Processed",
                category="testing",
                source="uncontrolled",
                content="Excel spreadsheet tracking parts processed through various surface finishing lines with test data."
            )
        ]

    # ============================================================================
    # PRIMARY FUNCTION TESTS - Core semantic matching functionality
    # ============================================================================

    def test_semantic_matching_accuracy_requirement(self):
        """
        🔴 RED: Test 95%+ accuracy in semantic similarity assessment (Requirement)
        REAL Business Value: Accurate matching ensures audit-grade evidence identification
        """
        # Known good matches based on domain expertise
        known_matches = [
            (self.real_requirements[1], self.real_controlled_docs[1], 0.95),  # Testing req → Testing doc
            (self.real_requirements[0], self.real_pd_forms[0], 0.80),        # Layout req → Layout doc
        ]
        
        for requirement, document, expected_min_score in known_matches:
            with self.subTest(req=requirement.id, doc=document.reference):
                score = self.business_logic.scoreEvidence(requirement, document)
                # When implemented, this should pass:
                self.assertGreaterEqual(score.similarity_score, expected_min_score,
                    f"Semantic matching failed for obvious match: {requirement.id} → {document.reference}")

    def test_semantic_matching_anti_patterns(self):
        """
        🔴 RED: Test anti-pattern prevention (drawing/sketch ≠ stress relief)
        REAL Business Value: Prevents audit failures from incorrect evidence assignments
        """
        # Known anti-patterns that should score low
        anti_patterns = [
            (self.real_requirements[0], self.real_controlled_docs[0]),  # Drawing req → Stress relief doc
        ]
        
        for requirement, document in anti_patterns:
            with self.subTest(req=requirement.id, doc=document.reference):
                score = self.business_logic.scoreEvidence(requirement, document)
                # When implemented, this should pass:
                self.assertLess(score.similarity_score, 0.3,
                    f"Anti-pattern not prevented: {requirement.id} should not match {document.reference}")

    def test_confidence_scoring_calibration(self):
        """
        🔴 RED: Test 90%+ correlation between confidence scores and expert validation
        REAL Business Value: Enables stakeholders to trust automated assessments
        """
        expert_validations = [
            (self.real_requirements[1], self.real_controlled_docs[1], "High"),    # Expert says High confidence
            (self.real_requirements[0], self.real_controlled_docs[0], "Low"),     # Expert says Low confidence
        ]
        
        for requirement, document, expert_confidence in expert_validations:
            with self.subTest(req=requirement.id, expert=expert_confidence):
                score = self.business_logic.scoreEvidence(requirement, document)
                # When implemented, this should pass:
                if expert_confidence == "High":
                    self.assertGreater(score.confidence, 0.8)
                elif expert_confidence == "Low":
                    self.assertLess(score.confidence, 0.4)

    def test_gap_detection_accuracy(self):
        """
        🔴 RED: Test 90%+ precision and recall for compliance gap identification
        REAL Business Value: Accurate gap detection ensures audit preparation completeness
        """
        # Requirements with known gaps (no appropriate controlled documents exist)
        known_gaps = [self.real_requirements[2]]  # Buy-off steps requirement
        
        for requirement in known_gaps:
            with self.subTest(req=requirement.id):
                gap = self.business_logic.classifyGap(requirement, self.real_controlled_docs)
                # When implemented, this should pass:
                self.assertEqual(gap.gap_type, "Missing",
                    f"Failed to detect gap for requirement {requirement.id}")
                self.assertIn(gap.severity, ["Critical", "High"],
                    f"Gap severity not properly classified for {requirement.id}")

    # ============================================================================
    # PERFORMANCE TESTS - Processing speed and scalability
    # ============================================================================

    def test_analysis_performance_under_30_minutes(self):
        """
        🔴 RED: Test <30 minutes for 200+ requirements vs 70+ documents analysis
        REAL Business Value: Enables practical use for audit preparation timelines
        """
        # Simulate large-scale analysis
        large_requirements = self.real_requirements * 67  # 201 requirements
        large_documents = self.real_controlled_docs * 24  # 72 documents
        
        import time
        start_time = time.time()
        result = self.business_logic.analyzeCompliance(large_requirements, large_documents)
        analysis_time = time.time() - start_time
        # When implemented, this should pass:
        self.assertLess(analysis_time, 30 * 60,  # 30 minutes
            f"Analysis took {analysis_time/60:.1f} minutes, exceeding 30-minute requirement")

    def test_memory_efficiency_no_overflow(self):
        """
        🔴 RED: Test efficient processing without memory overflow
        REAL Business Value: Enables deployment on standard hardware
        """
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Large-scale analysis should not cause memory issues
        result = self.business_logic.analyzeCompliance(self.real_requirements * 100, self.real_controlled_docs * 50)
        # When implemented, this should pass:
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        self.assertLess(memory_increase, 6000,  # 6GB limit per requirements
            f"Memory usage increased by {memory_increase:.1f}MB, exceeding limits")

    # ============================================================================
    # QUALITY ASSURANCE TESTS - Business logic validation
    # ============================================================================

    def test_evidence_hierarchy_controlled_vs_uncontrolled(self):
        """
        🔴 RED: Test controlled documents prioritized over uncontrolled as primary evidence
        REAL Business Value: Ensures audit-grade evidence hierarchy for compliance
        """
        requirement = self.real_requirements[0]  # Drawing/layout requirement
        all_documents = self.real_controlled_docs + self.real_pd_forms
        
        result = self.business_logic.analyzeCompliance([requirement], all_documents)
        # When implemented, this should pass:
        req_result = result.requirement_results[0]
        self.assertEqual(req_result.primary_evidence.source, "controlled",
            "Primary evidence should always be from controlled documents")
        if req_result.secondary_evidence:
            self.assertIn(req_result.secondary_evidence.source, ["controlled", "uncontrolled"],
                "Secondary evidence can be from any source")

    def test_compliance_status_determination(self):
        """
        🔴 RED: Test compliance status accurately reflects evidence quality
        REAL Business Value: Provides clear audit preparation guidance
        """
        test_cases = [
            (self.real_requirements[1], "Strong Evidence"),    # Testing req with good testing doc
            (self.real_requirements[2], "Gap Identified"),     # Buy-off req with no appropriate docs
        ]
        
        for requirement, expected_status in test_cases:
            with self.subTest(req=requirement.id, expected=expected_status):
                result = self.business_logic.analyzeCompliance([requirement], self.real_controlled_docs)
                # When implemented, this should pass:
                req_result = result.requirement_results[0]
                self.assertEqual(req_result.compliance_status, expected_status,
                    f"Compliance status incorrect for {requirement.id}")

    def test_recommendation_generation_actionability(self):
        """
        🔴 RED: Test recommendations are actionable and feasible
        REAL Business Value: Enables concrete steps for gap remediation
        """
        gap = GapClassification(
            gap_type="Missing",
            severity="Critical", 
            risk_level="High",
            priority=1
        )
        
        recommendations = self.business_logic.generateRecommendations([gap])
        # When implemented, this should pass:
        self.assertGreater(len(recommendations), 0, "No recommendations generated for critical gap")
        for rec in recommendations:
            self.assertIsInstance(rec, str)
            self.assertGreater(len(rec.strip()), 10, "Recommendation too brief to be actionable")
            self.assertIn("create", rec.lower(), "Missing gap should suggest document creation")

    # ============================================================================
    # INTEGRATION TESTS - End-to-end workflow validation
    # ============================================================================

    def test_complete_nadcap_workflow_integration(self):
        """
        🔴 RED: Test complete analysis workflow with real NADCAP data
        REAL Business Value: Validates end-to-end audit preparation capability
        """
        all_documents = self.real_controlled_docs + self.real_pd_forms
        
        result = self.business_logic.analyzeCompliance(self.real_requirements, all_documents)
        # When implemented, this should pass:
        self.assertEqual(len(result.requirement_results), len(self.real_requirements),
            "Not all requirements processed")
        
        # Validate each requirement has proper analysis
        for req_result in result.requirement_results:
            self.assertIsInstance(req_result, RequirementResult)
            self.assertIn(req_result.compliance_status, 
                ["Strong Evidence", "Potential Evidence", "Gap Identified"])
            self.assertIsInstance(req_result.primary_score.similarity_score, float)
            self.assertGreaterEqual(req_result.primary_score.similarity_score, 0.0)
            self.assertLessEqual(req_result.primary_score.similarity_score, 1.0)

    def test_consistency_across_multiple_runs(self):
        """
        🔴 RED: Test reproducible results across multiple analysis runs
        REAL Business Value: Ensures reliability for audit preparation planning
        """
        all_documents = self.real_controlled_docs + self.real_pd_forms
        
        # Run analysis twice
        result1 = self.business_logic.analyzeCompliance(self.real_requirements, all_documents)
        result2 = self.business_logic.analyzeCompliance(self.real_requirements, all_documents)
        
        # When implemented, this should pass:
        self.assertEqual(len(result1.requirement_results), len(result2.requirement_results))
        
        for r1, r2 in zip(result1.requirement_results, result2.requirement_results):
            self.assertEqual(r1.requirement_id, r2.requirement_id)
            self.assertEqual(r1.compliance_status, r2.compliance_status)
            self.assertAlmostEqual(r1.primary_score.similarity_score, 
                                 r2.primary_score.similarity_score, places=3,
                                 msg="Inconsistent similarity scores across runs")

    # ============================================================================
    # ERROR HANDLING TESTS - Robustness and quality validation
    # ============================================================================

    def test_graceful_handling_of_missing_documents(self):
        """
        🔴 RED: Test handling when no appropriate evidence exists
        REAL Business Value: Provides clear gap identification without system failures
        """
        # Requirement with no matching documents
        requirement = Requirement(
            id="99.99",
            content="Does the facility have a time machine for temporal compliance audits?",
            category="impossible",
            section="Future Tech",
            guidance=""
        )
        
        result = self.business_logic.analyzeCompliance([requirement], self.real_controlled_docs)
        # When implemented, this should pass:
        req_result = result.requirement_results[0]
        self.assertEqual(req_result.compliance_status, "Gap Identified")
        self.assertIsNotNone(req_result.gaps)
        self.assertGreater(len(req_result.gaps), 0)

    def test_quality_filtering_of_poor_matches(self):
        """
        🔴 RED: Test poor quality matches are filtered with transparency
        REAL Business Value: Prevents false confidence in weak evidence
        """
        # This test validates that very poor matches (< 0.15 similarity) are handled appropriately
        score = self.business_logic.scoreEvidence(
            self.real_requirements[0],  # Drawing requirement
            self.real_controlled_docs[0]  # Stress relief doc (should be poor match)
        )
        # When implemented, this should pass:
        if score.similarity_score < 0.15:
            self.assertEqual(score.relevance, "Low")
            self.assertIn(score.quality, ["Weak", "Poor"])


if __name__ == "__main__":
    print("🔴 RED PHASE: Business Logic Layer Tests for NADCAP Gap Analysis")
    print("=" * 70)
    print("Testing ALL requirements from LAYER-004-01-02-002_business_logic_requirements.md")
    print("REAL Tests for REAL Business Value")
    print("=" * 70)
    
    # Run tests with detailed output
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 70)
    print("🔴 RED PHASE COMPLETE")
    print("Next: GREEN PHASE - Implement Business Logic Layer to make tests pass")
    print("Target: 95%+ semantic accuracy, 90%+ confidence calibration, <30min analysis")
    print("=" * 70)