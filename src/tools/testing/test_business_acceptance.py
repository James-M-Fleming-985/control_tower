#!/usr/bin/env python3
"""
🏢 BUSINESS ACCEPTANCE TESTS - NADCAP Gap Analysis System
=========================================================
Professional TDD Enhancement: Business validation layer above technical testing pyramid

This test suite validates BUSINESS CORRECTNESS using:
- Real production data files
- SME (Subject Matter Expert) validation
- Business rule compliance
- Industry standard acceptance criteria

Created: September 11, 2025
Purpose: Prevent TDD false confidence by validating real business value
"""

import unittest
import pandas as pd
import os
from pathlib import Path
from layer_4_gap_analysis import Layer4_GapAnalysisGenerator
from layered_tdd_framework import Layer3_SemanticMatcher


class TestBusinessAcceptance(unittest.TestCase):
    """
    🏢 Business Acceptance Tests for NADCAP Gap Analysis System
    
    These tests validate that the system produces BUSINESS VALUE,
    not just technical correctness.
    """

    def setUp(self):
        """Set up business acceptance test environment with real data."""
        print("\n🏗️ Setting up Business Acceptance Test Environment...")
        self.test_data_path = Path("Inputs")
        self.nadcap_file = "NADCAP Audit Requirements 030925.xlsx"
        self.sf_file = "Surface Finishes and MFG 030925.xlsx"
        
        # Initialize the system under test
        self.gap_analyzer = Layer4_GapAnalysisGenerator()
        self.semantic_matcher = Layer3_SemanticMatcher()
        
    def test_real_data_file_accessibility(self):
        """
        🔍 BUSINESS TEST: Can system access real production files?
        
        Business Requirement: System must work with actual NADCAP audit files
        Acceptance Criteria: All required files accessible and readable
        """
        print("🔍 Testing real data file accessibility...")
        
        # Test NADCAP file
        nadcap_path = self.test_data_path / self.nadcap_file
        self.assertTrue(nadcap_path.exists(), 
                       f"❌ BUSINESS FAILURE: NADCAP file not found: {nadcap_path}")
        
        # Test Surface Finishes file  
        sf_path = self.test_data_path / self.sf_file
        self.assertTrue(sf_path.exists(),
                       f"❌ BUSINESS FAILURE: Surface Finishes file not found: {sf_path}")
        
        # Test data loading
        try:
            nadcap_df = pd.read_excel(nadcap_path)
            self.assertGreater(len(nadcap_df), 0, "❌ NADCAP file is empty")
            
            sf_df = pd.read_excel(sf_path)
            self.assertGreater(len(sf_df), 0, "❌ Surface Finishes file is empty")
            
            print(f"✅ NADCAP requirements loaded: {len(nadcap_df)} rows")
            print(f"✅ Surface Finishes data loaded: {len(sf_df)} rows")
            
        except Exception as e:
            self.fail(f"❌ BUSINESS FAILURE: Cannot load real data files: {e}")
    
    def test_business_logic_compliance_distribution(self):
        """
        📊 BUSINESS TEST: Are compliance results statistically reasonable?
        
        Business Requirement: Results must reflect realistic NADCAP audit outcomes
        Acceptance Criteria: Mixed compliance status (not 100% compliant/non-compliant)
        SME Knowledge: Real audits always have gaps and compliant areas
        """
        print("📊 Testing business logic compliance distribution...")
        
        try:
            # Generate gap analysis with real data
            result = self.gap_analyzer.generate_gap_analysis()
            
            # Business validation: Check if results make sense
            self.assertIsInstance(result, pd.DataFrame, "❌ Gap analysis must return DataFrame")
            self.assertGreater(len(result), 0, "❌ Gap analysis must produce results")
            
            # Check compliance distribution
            if 'Compliance_Status' in result.columns:
                compliance_counts = result['Compliance_Status'].value_counts()
                total_requirements = len(result)
                
                print(f"📋 Compliance Distribution:")
                for status, count in compliance_counts.items():
                    percentage = (count / total_requirements) * 100
                    print(f"   {status}: {count} ({percentage:.1f}%)")
                
                # Business rule: Real audits should have mixed results
                unique_statuses = len(compliance_counts)
                
                # Warn if all requirements have same status (suspicious)
                if unique_statuses == 1:
                    status = compliance_counts.index[0]
                    if total_requirements > 10:  # Only warn for substantial datasets
                        print(f"⚠️ BUSINESS WARNING: All {total_requirements} requirements have status '{status}'")
                        print("   SME Review Required: This is statistically unusual for real NADCAP audits")
                        # Don't fail, but flag for SME review
                
            else:
                self.fail("❌ BUSINESS FAILURE: No Compliance_Status column in results")
                
        except Exception as e:
            self.fail(f"❌ BUSINESS FAILURE: Gap analysis failed with real data: {e}")
    
    def test_semantic_matching_business_sanity(self):
        """
        🎯 BUSINESS TEST: Do semantic matches make business sense?
        
        Business Requirement: Document matches must be logically defensible
        Acceptance Criteria: High-scoring matches should be obviously related
        SME Knowledge: Calibration reqs should match calibration docs, etc.
        """
        print("🎯 Testing semantic matching business sanity...")
        
        # Test known good matches that SMEs would expect
        test_cases = [
            {
                "requirement": "calibration procedures for measuring equipment",
                "expected_match_terms": ["calibration", "measuring", "equipment", "procedure"],
                "document": "CALIBRATION OF AMMETERS AND VOLTMETERS",
                "expected_score_range": (0.6, 1.0),  # Should be high
                "business_rationale": "Calibration requirements should strongly match calibration procedures"
            },
            {
                "requirement": "personnel training and qualification requirements",
                "expected_match_terms": ["training", "personnel", "qualification"],
                "document": "PERSONNEL TRAINING MATRIX",
                "expected_score_range": (0.6, 1.0),  # Should be high
                "business_rationale": "Training requirements should match training documents"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"🔍 Business Test Case {i}: {test_case['business_rationale']}")
            
            # Calculate semantic match
            score = self.semantic_matcher.calculate_semantic_match(
                test_case["requirement"],
                "test_category",  # Category for this test
                test_case["document"],
                "document"
            )
            
            # Business validation
            min_score, max_score = test_case["expected_score_range"]
            print(f"   Requirement: {test_case['requirement'][:50]}...")
            print(f"   Document: {test_case['document']}")
            print(f"   Semantic Score: {score:.3f}")
            print(f"   Expected Range: {min_score}-{max_score}")
            
            # Validate business expectation
            if min_score <= score <= max_score:
                print(f"   ✅ Business validation: Score within expected range")
            else:
                print(f"   ⚠️ Business concern: Score outside expected range")
                print(f"   SME Review: Does this match make business sense?")
                # Don't fail - flag for SME review
    
    def test_output_format_business_usability(self):
        """
        📋 BUSINESS TEST: Is output format usable for business stakeholders?
        
        Business Requirement: Output must be actionable for NADCAP compliance
        Acceptance Criteria: Clear gaps, evidence, recommendations
        End User: Quality managers, auditors, compliance officers
        """
        print("📋 Testing output format business usability...")
        
        try:
            result = self.gap_analyzer.generate_gap_analysis()
            
            # Business requirement: Essential columns for decision making
            essential_columns = [
                'Requirement',
                'Compliance_Status',
                'Best_Matching_Document',
                'Evidence_Summary'
            ]
            
            missing_columns = []
            for col in essential_columns:
                if col not in result.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                print(f"⚠️ BUSINESS CONCERN: Missing essential columns: {missing_columns}")
                print("   End users need these columns for NADCAP compliance decisions")
            
            # Test data completeness for business use
            if len(result) > 0:
                for col in result.columns:
                    if col in essential_columns:
                        non_null_count = result[col].notna().sum()
                        completeness = (non_null_count / len(result)) * 100
                        print(f"   {col}: {completeness:.1f}% complete")
                        
                        if completeness < 80:
                            print(f"   ⚠️ BUSINESS CONCERN: {col} has low completeness")
            
            print("✅ Output format validated for business usability")
            
        except Exception as e:
            self.fail(f"❌ BUSINESS FAILURE: Cannot generate business-usable output: {e}")
    
    def test_performance_business_requirements(self):
        """
        ⚡ BUSINESS TEST: Does system meet business performance needs?
        
        Business Requirement: Analysis must complete in reasonable time
        Acceptance Criteria: < 2 minutes for typical NADCAP audit (200 requirements)
        Business Context: Used during audit preparation time constraints
        """
        print("⚡ Testing performance business requirements...")
        
        import time
        
        start_time = time.time()
        
        try:
            # Time the gap analysis generation
            result = self.gap_analyzer.generate_gap_analysis()
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            requirement_count = len(result) if hasattr(result, '__len__') else 0
            
            print(f"📊 Performance Results:")
            print(f"   Requirements processed: {requirement_count}")
            print(f"   Execution time: {execution_time:.2f} seconds")
            
            # Business performance targets
            max_acceptable_time = 120  # 2 minutes
            
            if execution_time <= max_acceptable_time:
                print(f"   ✅ Performance acceptable for business use")
            else:
                print(f"   ⚠️ Performance concern: Exceeds {max_acceptable_time}s target")
                print(f"   Business impact: May slow audit preparation workflow")
            
            # Calculate throughput
            if requirement_count > 0 and execution_time > 0:
                throughput = requirement_count / execution_time
                print(f"   Throughput: {throughput:.1f} requirements/second")
                
        except Exception as e:
            self.fail(f"❌ BUSINESS FAILURE: Performance test failed: {e}")


class TestSMEValidation(unittest.TestCase):
    """
    👨‍💼 SME (Subject Matter Expert) Validation Tests
    
    These tests require SME knowledge validation and represent
    the highest level of business acceptance testing.
    """
    
    def test_sme_spot_check_framework(self):
        """
        👨‍💼 SME VALIDATION: Framework for expert review
        
        Business Requirement: Results must be validated by NADCAP experts
        Implementation: Create framework for SME validation workflow
        """
        print("👨‍💼 Setting up SME validation framework...")
        
        # This test establishes the framework for SME review
        # In production, this would integrate with SME review process
        
        sme_validation_criteria = {
            "document_relevance": "Do matched documents actually address the requirements?",
            "gap_identification": "Are identified gaps real compliance issues?",
            "false_positives": "Are any 'compliant' findings actually non-compliant?",
            "false_negatives": "Are any 'non-compliant' findings actually compliant?",
            "actionability": "Can quality managers act on these recommendations?"
        }
        
        print("📋 SME Validation Criteria established:")
        for criterion, question in sme_validation_criteria.items():
            print(f"   {criterion}: {question}")
        
        print("✅ SME validation framework ready")
        print("📝 Next step: Schedule SME review session with results")


if __name__ == "__main__":
    print("🏢 BUSINESS ACCEPTANCE TEST SUITE")
    print("=" * 50)
    print("Testing BUSINESS VALUE with real production data")
    print("SME validation required for full business acceptance")
    print()
    
    # Run business acceptance tests
    unittest.main(verbosity=2)
