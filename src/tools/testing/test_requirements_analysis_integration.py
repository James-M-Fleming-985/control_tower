#!/usr/bin/env python3
"""
Integration Tests for Requirements Analysis Engine - TR-DA-003

Tests for integration between parser and generator with real requirement files
Following TDD methodology - RED phase tests that will initially fail
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from data_access.requirements_parser import RequirementsParser
from data_access.test_generator import TestGenerator
# from data_access.requirements_analysis_engine import RequirementsAnalysisEngine


class TestRequirementsAnalysisEngineIntegration:
    """Integration tests for complete requirements analysis workflow"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        # self.analysis_engine = RequirementsAnalysisEngine()
        self.parser = RequirementsParser()
        self.test_generator = TestGenerator()
        self.real_feature_file = Path("/workspaces/control_tower/cloned_repos/investment_strategy/projects/PROJECT-001/SYSTEM-001-05_rebalancing_automation/features/FEATURE-001-05-02_automated_rebalancing_execution.md")
    
    # RED PHASE INTEGRATION TESTS - These will fail initially
    
    def test_parse_real_feature_file_from_investment_strategy(self):
        """Test parsing the actual overdue feature file from investment_strategy repository"""
        # This will fail until we implement the complete integration
        result = self.analysis_engine.parse_requirement_file(self.real_feature_file)
        
        # Validate parsing of real file
        assert result.requirement_id == "FEATURE-001-05-02"
        assert result.requirement_type == "Feature Requirement"
        assert result.level == 4
        assert result.parent_system == "SYSTEM-001-05 (Rebalancing Automation)"
        assert result.repository == "Investment Strategy"
        assert result.target_layer == "Integration Layer"
        assert result.project_type == "Application"
        
        # Should have extracted acceptance criteria
        assert len(result.acceptance_criteria) >= 5
        assert any(ac["id"] == "AC-003" for ac in result.acceptance_criteria)
        assert any("trading platform APIs" in ac["description"] for ac in result.acceptance_criteria)
    
    def test_generate_tests_from_real_feature_requirements(self):
        """Test generating tests from the actual overdue feature file"""
        # Parse real requirement
        parsed_requirement = self.analysis_engine.parse_requirement_file(self.real_feature_file)
        
        # Generate tests from real requirement
        generated_tests = self.analysis_engine.generate_tests_from_requirement(parsed_requirement)
        
        assert len(generated_tests) >= 5  # Should generate tests for all acceptance criteria
        
        # Validate specific test generation for AC-003 (trading platform APIs)
        api_test = next((test for test in generated_tests if "trading_platform_apis" in test.test_name), None)
        assert api_test is not None
        assert api_test.test_type == "unit"
        assert "trading" in api_test.test_code.lower()
        assert "api" in api_test.test_code.lower()
    
    def test_create_complete_test_file_for_real_feature(self):
        """Test creating a complete pytest file for the real overdue feature"""
        # Complete workflow: parse → generate → create file
        test_file = self.analysis_engine.create_test_file_for_requirement(self.real_feature_file)
        
        assert test_file.filename == "test_feature_001_05_02_automated_rebalancing_execution.py"
        assert "class TestAutomatedRebalancingExecution:" in test_file.content
        
        # Should include all acceptance criteria as test methods
        assert "test_calculates_optimal_buy_sell_orders_for_rebalancing" in test_file.content
        assert "test_implements_cost_optimization_algorithms" in test_file.content  
        assert "test_integrates_with_trading_platform_apis" in test_file.content
        assert "test_implements_comprehensive_safety_validations" in test_file.content
        assert "test_provides_real_time_execution_monitoring" in test_file.content
        
        # Should include appropriate fixtures for Integration Layer
        assert "@pytest.fixture" in test_file.content
        assert "mock_trading_platform" in test_file.content
    
    def test_integration_with_phase_1_repository_scanner(self):
        """Test integration with existing Phase 1 repository scanner"""
        # Import Phase 1 repository scanner
        from data_access.repository_scanner import RepositoryScanner
        
        scanner = RepositoryScanner()
        
        # Get requirements from Phase 1 scanner
        repo_paths = ["/workspaces/control_tower/cloned_repos/investment_strategy"]
        requirements = scanner.scan_repositories(repo_paths)
        
        # Find our overdue feature in the scanner results
        overdue_feature = next(
            (req for req in requirements if req.id == "FEATURE-001-05-02"), 
            None
        )
        assert overdue_feature is not None
        
        # Use analysis engine to parse the detailed requirements
        detailed_requirement = self.analysis_engine.parse_requirement_file(
            Path(overdue_feature.file_path)
        )
        
        assert detailed_requirement.requirement_id == overdue_feature.id
        assert detailed_requirement.due_date == overdue_feature.due_date.strftime("%Y-%m-%d")
    
    def test_batch_processing_multiple_requirement_files(self):
        """Test processing multiple requirement files in batch"""
        # Get all feature files from investment_strategy
        feature_dir = Path("/workspaces/control_tower/cloned_repos/investment_strategy")
        feature_files = list(feature_dir.rglob("FEATURE-*.md"))
        
        # Process all feature files
        results = self.analysis_engine.batch_process_requirements(feature_files)
        
        assert len(results) >= 1  # At least our overdue feature
        
        # Validate each result
        for result in results:
            assert hasattr(result, 'requirement_id')
            assert hasattr(result, 'generated_tests')
            assert len(result.generated_tests) > 0
    
    def test_concurrent_processing_performance(self):
        """Test concurrent processing of multiple files for performance"""
        import time
        
        # Get multiple feature files (use existing ones or create test files)
        feature_files = list(Path("/workspaces/control_tower/cloned_repos").rglob("FEATURE-*.md"))
        
        if len(feature_files) < 3:
            # Skip if not enough files for meaningful test
            pytest.skip("Not enough feature files for concurrent processing test")
        
        # Process sequentially
        start_time = time.time()
        sequential_results = []
        for file_path in feature_files[:3]:
            result = self.analysis_engine.parse_requirement_file(file_path)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Process concurrently  
        start_time = time.time()
        concurrent_results = self.analysis_engine.batch_process_requirements_concurrent(feature_files[:3])
        concurrent_time = time.time() - start_time
        
        # Concurrent should be faster (or at least not significantly slower)
        assert len(concurrent_results) == len(sequential_results)
        # Allow some tolerance for overhead
        assert concurrent_time <= sequential_time * 1.5


class TestFileSystemIntegration:
    """Integration tests for file system operations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analysis_engine = RequirementsAnalysisEngine()
        self.test_output_dir = Path("/tmp/control_tower_test_output")
        self.test_output_dir.mkdir(exist_ok=True)
    
    def test_write_generated_tests_to_file_system(self):
        """Test writing generated test files to file system"""
        real_feature_file = Path("/workspaces/control_tower/cloned_repos/investment_strategy/projects/PROJECT-001/SYSTEM-001-05_rebalancing_automation/features/FEATURE-001-05-02_automated_rebalancing_execution.md")
        
        # Generate test file
        test_file = self.analysis_engine.create_test_file_for_requirement(real_feature_file)
        
        # Write to file system
        output_path = self.test_output_dir / test_file.filename
        written_path = self.analysis_engine.write_test_file(test_file, self.test_output_dir)
        
        assert written_path.exists()
        assert written_path.name == test_file.filename
        
        # Validate file content
        content = written_path.read_text()
        assert "class TestAutomatedRebalancingExecution:" in content
        assert "import pytest" in content
    
    def test_create_test_directory_structure(self):
        """Test creating proper directory structure for generated tests"""
        # Should create structure like: tests/integration/feature_001_05_02/
        test_structure = self.analysis_engine.create_test_directory_structure(
            "FEATURE-001-05-02",
            self.test_output_dir
        )
        
        assert test_structure.base_dir.exists()
        assert test_structure.unit_tests_dir.exists()
        assert test_structure.integration_tests_dir.exists()
        
        expected_base = self.test_output_dir / "tests" / "feature_001_05_02"
        assert test_structure.base_dir == expected_base
    
    def teardown_method(self):
        """Clean up test files"""
        import shutil
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)


class TestTraceabilityIntegration:
    """Integration tests for requirements traceability"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analysis_engine = RequirementsAnalysisEngine()
    
    def test_generate_traceability_matrix_for_real_feature(self):
        """Test generating traceability matrix for real feature file"""
        real_feature_file = Path("/workspaces/control_tower/cloned_repos/investment_strategy/projects/PROJECT-001/SYSTEM-001-05_rebalancing_automation/features/FEATURE-001-05-02_automated_rebalancing_execution.md")
        
        # Generate complete traceability
        traceability = self.analysis_engine.generate_traceability_matrix(real_feature_file)
        
        assert len(traceability.requirement_to_test_mapping) >= 5
        
        # Validate specific mappings
        ac_003_mapping = traceability.requirement_to_test_mapping.get("AC-003")
        assert ac_003_mapping is not None
        assert "test_integrates_with_trading_platform_apis" in ac_003_mapping.test_names
        
        # Should track coverage
        assert traceability.coverage_percentage >= 100.0  # All ACs should have tests
    
    def test_identify_missing_test_coverage(self):
        """Test identification of acceptance criteria without test coverage"""
        # Create requirement with some criteria missing from generated tests
        partial_requirement_file = self.analysis_engine.create_test_requirement_file(
            requirement_id="TEST-001",
            acceptance_criteria=[
                {"id": "AC-001", "description": "Implemented feature", "completed": True},
                {"id": "AC-002", "description": "Missing test coverage", "completed": False}
            ]
        )
        
        # Generate limited tests (simulate partial generation)
        coverage_analysis = self.analysis_engine.analyze_test_coverage(partial_requirement_file)
        
        # Should identify missing coverage
        assert len(coverage_analysis.missing_coverage) > 0
        assert any("AC-002" in missing.requirement_id for missing in coverage_analysis.missing_coverage)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])