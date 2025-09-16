#!/usr/bin/env python3
"""
LAYER 4 TDD TEST SUITE
Professional Test-Driven Development for Gap Analysis Generator

Tests comprehensive gap analysis functionality including:
- NADCAP requirements loading and parsing
- SF document discovery and categorization
- Layer 3 semantic matcher integration
- Evidence scoring and compliance calculation
- Excel export with professional formatting
- End-to-end gap analysis workflow

Following Red-Green-Refactor TDD methodology
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from layer_4_gap_analysis import Layer4_GapAnalysisGenerator
except ImportError:
    print(
        "❌ Cannot import Layer4_GapAnalysisGenerator - run from NADCAP Analysis directory"
    )
    sys.exit(1)


class TestLayer4_DataLoading(unittest.TestCase):
    """Test data loading and initialization functionality."""

    def setUp(self):
        """Set up test environment."""
        self.generator = Layer4_GapAnalysisGenerator()
        self.test_data_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def test_initialization(self):
        """Test Layer 4 generator initialization."""
        generator = Layer4_GapAnalysisGenerator()

        # Check basic initialization
        self.assertIsNotNone(generator.base_dir)
        self.assertIsNotNone(generator.inputs_dir)
        self.assertIsNotNone(generator.outputs_dir)

        # Check file paths are set
        self.assertTrue(
            generator.nadcap_file.endswith(
                "NADCAP Audit Requirements 030925.xlsx")
        )
        self.assertTrue(generator.pd_forms_dir.endswith("sf_pd_forms"))
        self.assertTrue(generator.manps_dir.endswith("sf_manps"))

        print("✅ test_initialization: PASSED")

    def test_semantic_matcher_integration(self):
        """Test Layer 3 semantic matcher integration."""
        generator = Layer4_GapAnalysisGenerator()

        # Should attempt to load Layer 3 semantic matcher
        if generator.semantic_matcher is not None:
            # Layer 3 available - test integration
            self.assertTrue(
                hasattr(generator.semantic_matcher, "calculate_semantic_match")
            )
            print("✅ Layer 3 semantic matcher integrated successfully")
        else:
            # Layer 3 not available - fallback should work
            print("⚠️  Layer 3 not available, using fallback scoring")

        print("✅ test_semantic_matcher_integration: PASSED")

    @patch("pandas.read_excel")
    @patch("pandas.ExcelFile")
    def test_nadcap_requirements_loading(
            self, mock_excel_file, mock_read_excel):
        """Test NADCAP requirements file loading."""
        # Mock Excel file structure
        mock_excel_file.return_value.sheet_names = ["Requirements", "Appendix"]
        mock_df = pd.DataFrame(
            {
                "Requirement": ["Test requirement 1", "Test requirement 2"],
                "Section": ["3.1", "3.2"],
                "Category": ["Documentation", "Training"],
            }
        )
        mock_read_excel.return_value = mock_df

        generator = Layer4_GapAnalysisGenerator()
        result = generator.load_nadcap_requirements()

        # Check loading results
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn("Requirement", result.columns)

        print("✅ test_nadcap_requirements_loading: PASSED")

    def test_requirements_compliance_coverage(self):
        """
        PROFESSIONAL TDD: Test that ALL original requirements are met.
        This test should have been written FIRST to prevent scope gaps.

        Original Requirements:
        1. Three document sources: SF PD Forms + SF MANPs + Surface Finishes Column I
        2. NADCAP context: Columns C (Title) + E (Title.1) + G (Content) + H (Guidance)
        3. 41 Column I procedures must be accessible
        4. Enhanced context must combine all NADCAP columns
        """
        generator = Layer4_GapAnalysisGenerator()

        # Test 1: All three document sources must be supported
        with patch.object(
            generator, "_load_surface_finishes_column_i"
        ) as mock_column_i:
            mock_column_i.return_value = [
                "proc1",
                "proc2",
                "proc3",
            ]  # Mock 3 procedures

            sf_docs = generator.load_sf_documents()

            # CRITICAL: Must have all three document categories
            self.assertIn(
                "pd_forms", sf_docs, "Missing SF PD Forms - Requirement violation!"
            )
            self.assertIn(
                "manps",
                sf_docs,
                "Missing SF MANPs - Requirement violation!")
            self.assertIn(
                "column_i_procedures",
                sf_docs,
                "Missing Column I procedures - Requirement violation!",
            )

            # Verify Column I procedures are loaded
            self.assertEqual(
                len(sf_docs["column_i_procedures"]),
                3,
                "Column I procedures not loaded properly",
            )

        # Test 2: NADCAP enhanced context must combine all required columns
        with patch("pandas.read_excel") as mock_excel, patch(
            "pandas.ExcelFile"
        ) as mock_excel_file, patch("os.path.exists") as mock_exists:

            # Mock file exists
            mock_exists.return_value = True

            # Mock ExcelFile and sheet names
            mock_excel_file_instance = Mock()
            mock_excel_file_instance.sheet_names = ["Sheet1"]
            mock_excel_file.return_value = mock_excel_file_instance

            # Mock NADCAP data with all required columns
            mock_df = pd.DataFrame(
                {
                    "A": ["A1", "A2"],
                    "B": ["B1", "B2"],
                    "C": ["Title 1", "Title 2"],  # Column C: Title
                    "D": ["D1", "D2"],
                    "E": ["Subtitle 1", "Subtitle 2"],  # Column E: Title.1
                    "F": ["F1", "F2"],
                    "G": ["Content 1", "Content 2"],  # Column G: Content
                    "H": ["Guidance 1", "Guidance 2"],  # Column H: Guidance
                    "I": ["I1", "I2"],
                    "J": ["J1", "J2"],
                }
            )

            mock_excel.return_value = mock_df
            generator.nadcap_file = "mock_file.xlsx"

            result = generator.load_nadcap_requirements()

            # CRITICAL: Enhanced context must exist and combine all columns
            self.assertIsNotNone(result, "NADCAP requirements loading failed")
            self.assertIn(
                "enhanced_context",
                result.columns,
                "Enhanced context missing - Requirement violation!",
            )

            # Verify enhanced context contains all required column data
            enhanced_text = str(result["enhanced_context"].iloc[0])
            self.assertIn(
                "Title: Title 1",
                enhanced_text,
                "Column C (Title) not in enhanced context",
            )
            self.assertIn(
                "Subtitle: Subtitle 1",
                enhanced_text,
                "Column E (Title.1) not in enhanced context",
            )
            self.assertIn(
                "Content: Content 1",
                enhanced_text,
                "Column G (Content) not in enhanced context",
            )
            self.assertIn(
                "Guidance: Guidance 1",
                enhanced_text,
                "Column H (Guidance) not in enhanced context",
            )

        print(
            "✅ test_requirements_compliance_coverage: PASSED - All original requirements verified"
        )

    def test_sf_documents_loading(self):
        """Test Surface Finishes documents loading including Column I procedures."""
        # Create test document structure
        test_pd_dir = os.path.join(self.test_data_dir, "sf_pd_forms")
        test_manp_dir = os.path.join(self.test_data_dir, "sf_manps")

        os.makedirs(test_pd_dir, exist_ok=True)
        os.makedirs(test_manp_dir, exist_ok=True)

        # Create test files
        test_files = [
            (test_pd_dir, "PD_Test_Form.pdf"),
            (test_pd_dir, "PD_Quality_Check.xlsx"),
            (test_manp_dir, "MANP_Procedure_01.doc"),
            (test_manp_dir, "MANP_Training_Guide.pdf"),
        ]

        for directory, filename in test_files:
            filepath = os.path.join(directory, filename)
            with open(filepath, "w") as f:
                f.write("test content")

        # Mock Surface Finishes Column I loading
        with patch.object(
            Layer4_GapAnalysisGenerator, "_load_surface_finishes_column_i"
        ) as mock_column_i:
            mock_column_i.return_value = [
                "Procedure 1: Test coating procedure",
                "Procedure 2: Quality control check",
                "Procedure 3: Final inspection protocol",
            ]

            # Test loading with mocked directories
            generator = Layer4_GapAnalysisGenerator()
            generator.pd_forms_dir = test_pd_dir
            generator.manps_dir = test_manp_dir

            result = generator.load_sf_documents()

            # Check results - updated for Column I
            self.assertIn("pd_forms", result)
            self.assertIn("manps", result)
            self.assertIn("column_i_procedures", result)
            self.assertEqual(len(result["pd_forms"]), 2)
            self.assertEqual(len(result["manps"]), 2)
            self.assertEqual(len(result["column_i_procedures"]), 3)
            self.assertEqual(result["total_count"], 7)  # 2 + 2 + 3

        print("✅ test_sf_documents_loading: PASSED (with Column I)")


class TestLayer4_EvidenceScoring(unittest.TestCase):
    """Test evidence scoring and compliance calculation."""

    def setUp(self):
        """Set up test environment."""
        self.generator = Layer4_GapAnalysisGenerator()

    def test_evidence_scoring_with_layer3(self):
        """Test evidence scoring with Layer 3 semantic matcher."""
        if self.generator.semantic_matcher is None:
            self.skipTest("Layer 3 semantic matcher not available")

        # Test with known good matches
        test_cases = [
            {
                "requirement": "calibration equipment accuracy verification",
                "document": "calibration procedure manual",
                "expected_range": (0.15, 0.4),  # Realistic Layer 3 scoring
            },
            {
                "requirement": "personnel training qualification",
                "document": "stress relief procedure",
                # Should be poor match (anti-pattern)
                "expected_range": (0.0, 0.2),
            },
        ]

        for case in test_cases:
            score = self.generator.calculate_evidence_score(
                case["requirement"], case["document"]
            )

            min_score, max_score = case["expected_range"]
            self.assertGreaterEqual(score, min_score)
            self.assertLessEqual(score, max_score)
            self.assertIsInstance(score, float)

        print("✅ test_evidence_scoring_with_layer3: PASSED")

    def test_fallback_evidence_scoring(self):
        """Test fallback evidence scoring without Layer 3."""
        # Test fallback scoring directly
        test_cases = [
            {
                "requirement": "calibration equipment",
                "document": "calibration procedure",
                "expected_min": 0.2,  # Should have some overlap
            },
            {
                "requirement": "quality control",
                "document": "unrelated document",
                "expected_max": 0.1,  # Should have minimal overlap
            },
        ]

        for case in test_cases:
            score = self.generator._fallback_evidence_scoring(
                case["requirement"], case["document"]
            )

            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

            if "expected_min" in case:
                self.assertGreaterEqual(score, case["expected_min"])
            if "expected_max" in case:
                self.assertLessEqual(score, case["expected_max"])

        print("✅ test_fallback_evidence_scoring: PASSED")

    def test_compliance_status_calculation(self):
        """Test compliance status and recommendation calculation."""
        test_cases = [
            {
                "primary": {"score": 0.9, "document": "PD_Test_Form"},
                "secondary": {"score": 0.8, "document": "MANP_Test_Proc"},
                "expected_status": "Compliant",
            },
            {
                "primary": {"score": 0.7, "document": "PD_Partial_Match"},
                "secondary": None,
                "expected_status": "Partially Compliant",
            },
            {
                "primary": {"score": 0.2, "document": "PD_Poor_Match"},
                "secondary": None,
                "expected_status": "Non-Compliant",
            },
            {"primary": None, "secondary": None,
                "expected_status": "Non-Compliant"},
        ]

        for case in test_cases:
            result = self.generator._calculate_compliance_status(
                case["primary"], case["secondary"]
            )

            self.assertIn("status", result)
            self.assertIn("match_percentage", result)
            self.assertIn("recommendation", result)

            self.assertEqual(result["status"], case["expected_status"])
            self.assertIsInstance(result["match_percentage"], float)
            self.assertIsInstance(result["recommendation"], str)

        print("✅ test_compliance_status_calculation: PASSED")


class TestLayer4_GapAnalysisGeneration(unittest.TestCase):
    """Test complete gap analysis generation workflow."""

    def setUp(self):
        """Set up test environment."""
        self.generator = Layer4_GapAnalysisGenerator()
        self.test_data_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    @patch.object(Layer4_GapAnalysisGenerator, "load_nadcap_requirements")
    @patch.object(Layer4_GapAnalysisGenerator, "load_sf_documents")
    def test_gap_analysis_structure(self, mock_sf_docs, mock_nadcap):
        """Test gap analysis generates proper structure."""
        # Mock data sources
        mock_nadcap.return_value = pd.DataFrame(
            {
                "Requirement": ["Test requirement 1", "Test requirement 2"],
                "Section": ["3.1", "3.2"],
            }
        )

        mock_sf_docs.return_value = {
            "pd_forms": ["test_form.pdf"],
            "manps": ["test_manp.doc"],
            "total_count": 2,
        }

        # Generate gap analysis
        result = self.generator.generate_gap_analysis()

        # Check structure
        self.assertIsInstance(result, pd.DataFrame)

        # Check industry best practice columns added
        expected_columns = [
            "Primary_Evidence_Document",
            "Primary_Evidence_Title",
            "Primary_Evidence_Score",
            "Secondary_Evidence_Document",
            "Secondary_Evidence_Title",
            "Secondary_Evidence_Score",
            "Compliance_Status",
            "Match_Percentage",
            "Recommendation_Action",
            "Analysis_Date",
        ]

        for column in expected_columns:
            self.assertIn(column, result.columns)

        print("✅ test_gap_analysis_structure: PASSED")

    def test_evidence_matching_logic(self):
        """Test evidence matching finds appropriate documents."""
        # Mock SF documents
        sf_docs = {
            "pd_forms": [
                "PD_Calibration_Form.pdf",
                "PD_Quality_Control.xlsx",
                "PD_Training_Record.doc",
            ],
            "manps": ["MANP_Calibration_Procedure.pdf", "MANP_Safety_Guidelines.doc"],
        }

        # Test primary evidence finding
        test_requirement = "calibration equipment accuracy verification procedures"

        primary = self.generator._find_best_evidence(test_requirement, sf_docs)

        self.assertIsNotNone(primary)
        self.assertIn("document", primary)
        self.assertIn("title", primary)
        self.assertIn("score", primary)
        self.assertIsInstance(primary["score"], float)

        # Test secondary evidence finding
        secondary = self.generator._find_secondary_evidence(
            test_requirement, sf_docs, primary
        )

        if secondary:  # May be None if no good secondary match
            self.assertIn("document", secondary)
            self.assertIn("title", secondary)
            self.assertIn("score", secondary)
            self.assertNotEqual(secondary["document"], primary["document"])

        print("✅ test_evidence_matching_logic: PASSED")


class TestLayer4_ExportFunctionality(unittest.TestCase):
    """Test Excel export and formatting functionality."""

    def setUp(self):
        """Set up test environment."""
        self.generator = Layer4_GapAnalysisGenerator()
        self.test_output_dir = tempfile.mkdtemp()
        self.generator.outputs_dir = self.test_output_dir

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

    def test_export_gap_analysis(self):
        """Test gap analysis Excel export functionality."""
        # Create mock gap analysis results
        self.generator.gap_analysis_results = pd.DataFrame(
            {
                "Requirement": ["Test requirement"],
                "Primary_Evidence_Document": ["PD_Test_Form.pdf"],
                "Primary_Evidence_Score": [0.85],
                "Compliance_Status": ["Compliant"],
                "Match_Percentage": [85.0],
                "Recommendation_Action": ["Continue monitoring"],
            }
        )

        # Test export
        output_file = self.generator.export_gap_analysis("test_export.xlsx")

        # Check file was created
        self.assertTrue(os.path.exists(output_file))
        self.assertTrue(output_file.endswith("test_export.xlsx"))

        # Verify Excel file can be read
        df_check = pd.read_excel(output_file)
        self.assertEqual(len(df_check), 1)
        self.assertIn("Requirement", df_check.columns)

        print("✅ test_export_gap_analysis: PASSED")

    def test_export_without_results(self):
        """Test export behavior when no results exist."""
        # Clear any existing results
        self.generator.gap_analysis_results = None

        # Should raise exception
        with self.assertRaises(Exception) as context:
            self.generator.export_gap_analysis()

        self.assertIn("No gap analysis results", str(context.exception))

        print("✅ test_export_without_results: PASSED")


class TestLayer4_PropertyBasedInvariants(unittest.TestCase):
    """Test property-based invariants and edge cases."""

    def setUp(self):
        """Set up test environment."""
        self.generator = Layer4_GapAnalysisGenerator()

    def test_evidence_scores_within_range(self):
        """Property: All evidence scores must be between 0.0 and 1.0."""
        test_cases = [
            ("calibration equipment", "calibration procedure"),
            ("quality control", "training manual"),
            ("", "empty requirement"),
            ("test requirement", ""),
            ("very long requirement text with many words", "short doc"),
        ]

        for requirement, document in test_cases:
            score = self.generator.calculate_evidence_score(
                requirement, document)

            self.assertGreaterEqual(
                score,
                0.0,
                f"Score {score} below 0.0 for '{requirement}' vs '{document}'",
            )
            self.assertLessEqual(
                score,
                1.0,
                f"Score {score} above 1.0 for '{requirement}' vs '{document}'",
            )
            self.assertIsInstance(score, float)

        print("✅ test_evidence_scores_within_range: PASSED")

    def test_compliance_status_consistency(self):
        """Property: Compliance status must be consistent with scores."""
        test_cases = [
            {"primary": {"score": 0.95}, "secondary": {
                "score": 0.90}},  # High scores
            {"primary": {"score": 0.5}, "secondary": None},  # Medium scores
            {"primary": {"score": 0.1}, "secondary": None},  # Low scores
            {"primary": None, "secondary": None},  # No evidence
        ]

        for case in test_cases:
            result = self.generator._calculate_compliance_status(
                case["primary"], case["secondary"]
            )

            # Check status is valid
            valid_statuses = [
                "Compliant",
                "Partially Compliant",
                "Non-Compliant"]
            self.assertIn(result["status"], valid_statuses)

            # Check match percentage consistency
            if case["primary"] is None:
                self.assertEqual(result["match_percentage"], 0.0)
            else:
                self.assertGreater(result["match_percentage"], 0.0)

            # Check recommendation exists
            self.assertTrue(
                len(result["recommendation"]) > 10
            )  # Non-trivial recommendation

        print("✅ test_compliance_status_consistency: PASSED")

    def test_gap_analysis_completeness(self):
        """Property: Gap analysis must process all input requirements."""
        # Mock input data
        test_requirements = pd.DataFrame(
            {
                "Requirement": [f"Test requirement {i}" for i in range(5)],
                "Section": [f"3.{i}" for i in range(5)],
            }
        )

        # Mock the data loading
        with patch.object(
            self.generator, "load_nadcap_requirements", return_value=test_requirements
        ), patch.object(
            self.generator,
            "load_sf_documents",
            return_value={"pd_forms": [], "manps": []},
        ):

            result = self.generator.generate_gap_analysis()

            # Check all requirements processed
            self.assertEqual(len(result), len(test_requirements))

            # Check all have compliance data
            for idx, row in result.iterrows():
                self.assertIn(
                    row["Compliance_Status"],
                    ["Compliant", "Partially Compliant", "Non-Compliant"],
                )
                self.assertIsInstance(row["Match_Percentage"], (float, int))
                self.assertIsInstance(row["Recommendation_Action"], str)

        print("✅ test_gap_analysis_completeness: PASSED")


def run_layer4_tdd_test_suite():
    """Run the complete Layer 4 TDD test suite."""
    print("🧪 LAYER 4 TDD TEST SUITE")
    print("=" * 50)

    # Create test suite
    test_classes = [
        TestLayer4_DataLoading,
        TestLayer4_EvidenceScoring,
        TestLayer4_GapAnalysisGeneration,
        TestLayer4_ExportFunctionality,
        TestLayer4_PropertyBasedInvariants,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_class in test_classes:
        print(f"\n🔍 Running {test_class.__name__}...")

        # Create test suite for this class
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)

        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=0, stream=open(os.devnull, "w"))
        result = runner.run(suite)

        # Track results
        total_tests += result.testsRun
        passed_tests += result.testsRun - \
            len(result.failures) - len(result.errors)
        failed_tests += len(result.failures) + len(result.errors)

        # Report class results
        if result.failures or result.errors:
            print(
                f"❌ {
                    test_class.__name__}: {
                    len(
                        result.failures +
                        result.errors)} failures"
            )
            for failure in result.failures + result.errors:
                print(f"   • {failure[0]}: {failure[1].split(chr(10))[0]}")
        else:
            print(f"✅ {test_class.__name__}: All tests passed")

    # Final summary
    print("\n" + "=" * 50)
    print(
        f"📊 LAYER 4 TDD RESULTS: {passed_tests}/{total_tests} tests passing ({
            passed_tests / total_tests * 100:.1f}%)"
    )
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")

    if failed_tests == 0:
        print("🎉 ALL LAYER 4 TDD TESTS PASSING - Ready for implementation!")
    else:
        print("🔧 Layer 4 TDD cycle needs refactoring to achieve 100% success")

    print("=" * 50)

    return passed_tests, total_tests, failed_tests


if __name__ == "__main__":
    run_layer4_tdd_test_suite()
