#!/usr/bin/env python3
"""
LAYER 2 INTEGRATION TESTS
Professional TDD Red-Green-Refactor

These tests MUST FAIL until Layer 2 is properly integrated 
into the business workflow (Layer 4 gap analysis).

The goal is to force proper Layer 2 integration through failing tests.
"""

import unittest
import pandas as pd
from layer_4_gap_analysis import Layer4_GapAnalysisGenerator
from layered_tdd_framework import Layer2_TextProcessor


class TestLayer2Integration(unittest.TestCase):
    """
    Integration tests to ensure Layer 2 text processing 
    is properly integrated into the business workflow.
    
    These tests SHOULD FAIL until integration is complete.
    """

    def setUp(self):
        """Set up test environment."""
        self.layer4 = Layer4_GapAnalysisGenerator()
        self.layer2 = Layer2_TextProcessor()

    def test_layer4_uses_layer2_preprocessing(self):
        """
        INTEGRATION TEST: Layer 4 must use Layer 2 preprocessing
        
        This test checks if Layer 4 gap analysis actually calls
        Layer 2 text processing for requirement preprocessing.
        
        EXPECTED TO FAIL until integration is implemented.
        """
        # Generate gap analysis
        results = self.layer4.generate_gap_analysis()
        
        # Check if results contain Layer 2 processed data
        self.assertIsInstance(results, pd.DataFrame)
        
        # Check for Layer 2 indicators in the data
        # Layer 2 should add categorization and processed text
        sample_result = results.iloc[0] if len(results) > 0 else None
        self.assertIsNotNone(sample_result, "Gap analysis should return results")
        
        # Check if Layer 2 text processing was applied
        # This SHOULD FAIL until Layer 4 calls Layer 2
        self.assertTrue(
            hasattr(sample_result, 'processed_text') or 'processed_text' in results.columns,
            "Layer 4 results should include Layer 2 processed text"
        )
        
        self.assertTrue(
            hasattr(sample_result, 'category') or 'category' in results.columns,
            "Layer 4 results should include Layer 2 categorization"
        )

    def test_layer2_preprocessing_improves_semantic_scores(self):
        """
        BUSINESS INTEGRATION TEST: Layer 2 preprocessing should improve semantic matching
        
        Business requirement: Text preprocessing should improve semantic match quality
        Current scores: 0.257 (poor)
        Expected scores: >0.6 (good)
        
        EXPECTED TO FAIL until Layer 2 is properly integrated.
        """
        # Get results with current (non-Layer 2) implementation
        results = self.layer4.generate_gap_analysis()
        
        # Check semantic scores
        if len(results) > 0 and 'semantic_score' in results.columns:
            avg_score = results['semantic_score'].mean()
            
            # This SHOULD FAIL - current scores are too low
            self.assertGreater(
                avg_score, 0.6,
                f"Average semantic score {avg_score:.3f} should be >0.6 with Layer 2 preprocessing"
            )
        else:
            # If no semantic scores, the integration is definitely missing
            self.fail("Layer 4 results should include semantic scores from Layer 2/3 integration")

    def test_layer2_categories_appear_in_business_output(self):
        """
        BUSINESS INTEGRATION TEST: Layer 2 categories should appear in business output
        
        Business users need to see requirement categories for decision-making.
        Layer 2 provides: documentation, process_control, quality_assurance, etc.
        
        EXPECTED TO FAIL until Layer 2 is integrated into Layer 4 output.
        """
        results = self.layer4.generate_gap_analysis()
        
        # Check if Layer 2 categories are in the business output
        self.assertIn('requirement_category', results.columns, 
                     "Business output should include Layer 2 requirement categories")
        
        # Check for actual categories from Layer 2
        categories = results['requirement_category'].unique() if 'requirement_category' in results.columns else []
        expected_categories = ['documentation', 'process_control', 'quality_assurance', 'equipment', 'training']
        
        found_categories = [cat for cat in expected_categories if cat in categories]
        self.assertGreater(len(found_categories), 0,
                          f"Should find Layer 2 categories {expected_categories}, found: {list(categories)}")

    def test_layer2_term_extraction_supports_semantic_matching(self):
        """
        TECHNICAL INTEGRATION TEST: Layer 2 term extraction should support Layer 3 semantic matching
        
        Layer 2 extracts and weights terms for better semantic matching.
        These terms should be used by Layer 3 for improved match scores.
        
        EXPECTED TO FAIL until proper Layer 2→3 integration.
        """
        # Test a specific requirement that should benefit from Layer 2 preprocessing
        test_requirement = "Calibration procedures for measuring equipment must be documented"
        
        # Process with Layer 2
        processed = self.layer2.preprocess_requirement(test_requirement)
        
        # Check that processed data has the expected structure
        self.assertIn('key_terms', processed)
        self.assertIn('category', processed)
        self.assertIn('weights', processed)
        
        # Generate gap analysis and check if these Layer 2 features are used
        results = self.layer4.generate_gap_analysis()
        
        # Look for evidence that Layer 2 term extraction was used
        # This should appear in semantic matching results
        calibration_results = results[results['Requirement'].str.contains('calibration', case=False, na=False)]
        
        if len(calibration_results) > 0:
            # Check if semantic scores are reasonable (indicating good term extraction)
            avg_calibration_score = calibration_results['semantic_score'].mean() if 'semantic_score' in calibration_results.columns else 0
            
            # This SHOULD FAIL with current implementation
            self.assertGreater(avg_calibration_score, 0.6,
                              f"Calibration semantic scores should be >0.6 with Layer 2 term extraction, got {avg_calibration_score:.3f}")


class TestLayer2BusinessWorkflowIntegration(unittest.TestCase):
    """
    Business workflow integration tests.
    
    These tests verify that Layer 2 is properly integrated into
    the end-to-end business workflow, not just working in isolation.
    """

    def test_business_output_includes_layer2_insights(self):
        """
        BUSINESS TEST: Final Excel output should include Layer 2 insights
        
        Business stakeholders need Layer 2 insights in their reports:
        - Requirement categories for prioritization
        - Text quality scores for validation
        - Processed text for review
        
        EXPECTED TO FAIL until Layer 2 is integrated into Excel export.
        """
        layer4 = Layer4_GapAnalysisGenerator()
        
        # Generate and export gap analysis
        results = layer4.generate_gap_analysis()
        
        # Export to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            export_path = tmp_file.name
            
        try:
            layer4.export_gap_analysis(results, export_path)
            
            # Read back the exported file
            exported_df = pd.read_excel(export_path)
            
            # Check for Layer 2 columns in business output
            layer2_columns = [
                'requirement_category',
                'text_quality_score', 
                'processed_terms',
                'layer2_preprocessing_applied'
            ]
            
            found_columns = [col for col in layer2_columns if col in exported_df.columns]
            
            # This SHOULD FAIL until Layer 2 is integrated
            self.assertGreater(len(found_columns), 0,
                              f"Business Excel export should include Layer 2 columns. "
                              f"Expected any of {layer2_columns}, "
                              f"Found columns: {list(exported_df.columns)}")
                              
        finally:
            # Clean up
            import os
            if os.path.exists(export_path):
                os.remove(export_path)


if __name__ == '__main__':
    print("🔴 LAYER 2 INTEGRATION TESTS - Expected to FAIL until integration complete")
    print("=" * 80)
    unittest.main(verbosity=2)
