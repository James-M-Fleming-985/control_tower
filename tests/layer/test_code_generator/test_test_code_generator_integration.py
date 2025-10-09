"""
Integration Tests for Test Code Generator
Layer: LAYER-004-01-02-01

Tests component integration and end-to-end workflows.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import subprocess

from src.layer.test_code_generator import TestCodeGenerator

# REQ-LAYER-004-01-02-01

pytestmark = pytest.mark.integration


class TestTestCodeGeneratorIntegration:
    """Integration tests for Test Code Generator."""

    def setup_method(self):
        """Setup integration test fixtures."""
        self.test_workspace = Path(tempfile.mkdtemp())
        self.generator = TestCodeGenerator()
        
        # Create a real layer YAML file for testing
        self.layer_yaml = self.test_workspace / "test_layer.yaml"
        yaml_content = """
metadata:
  requirement_id: LAYER-TEST-INT-001
  requirement_name: Integration Test Layer
  requirement_type: Layer

acceptance_criteria:
  - criterion_id: AC-001
    criterion: "Process data correctly"
    priority: critical
  - criterion_id: AC-002
    criterion: "Handle errors gracefully"
    priority: high
"""
        self.layer_yaml.write_text(yaml_content)

    def teardown_method(self):
        """Cleanup after tests."""
        if self.test_workspace.exists():
            shutil.rmtree(self.test_workspace)

    def test_generate_tests_from_real_yaml(self):
        """
        AC-001: Test end-to-end generation from real YAML file.
        """
        # Arrange
        output_dir = self.test_workspace / "generated_tests"
        output_dir.mkdir()
        
        # Act
        result = self.generator.generate_pytest_test_files_from_yaml(
            self.layer_yaml, output_dir
        )
        
        # Assert
        assert result is not None
        assert 'unit' in result
        assert result['unit'].exists()

    def test_generated_tests_fail_without_implementation(self):
        """
        AC-002: Verify generated tests actually fail when run.
        """
        # Arrange
        output_dir = self.test_workspace / "generated_tests"
        output_dir.mkdir()
        
        # Generate tests
        result = self.generator.generate_pytest_test_files_from_yaml(
            self.layer_yaml, output_dir
        )
        
        # Act - verify tests will fail
        unit_content = result['unit'].read_text()
        will_fail = self.generator.verify_tests_fail_without_implementation(
            unit_content
        )
        
        # Assert
        assert will_fail is True

    def test_save_generated_test_files(self):
        """Test saving generated test files to disk."""
        # Arrange
        output_dir = self.test_workspace / "output"
        output_dir.mkdir()
        
        # Act
        result = self.generator.generate_pytest_test_files_from_yaml(
            self.layer_yaml, output_dir
        )
        
        # Assert
        assert result['unit'].exists()
        assert result['unit'].stat().st_size > 0

    def test_multi_file_test_generation(self):
        """Test generating multiple test files in one run."""
        # Arrange
        output_dir = self.test_workspace / "multi_output"
        output_dir.mkdir()
        
        # Act
        result = self.generator.generate_pytest_test_files_from_yaml(
            self.layer_yaml, output_dir
        )
        
        # Assert
        assert len(result) >= 2
        assert result['unit'].exists()
        assert result['integration'].exists()

    def test_end_to_end_test_generation(self):
        """Complete end-to-end test generation workflow."""
        # Arrange
        output_dir = self.test_workspace / "e2e_output"
        output_dir.mkdir()
        
        # Act - full workflow
        result = self.generator.generate_pytest_test_files_from_yaml(
            self.layer_yaml, output_dir
        )
        
        unit_content = result['unit'].read_text()
        unit_valid = self.generator.validate_generated_test_syntax(unit_content)
        unit_will_fail = self.generator.verify_tests_fail_without_implementation(
            unit_content
        )
        
        # Assert
        assert unit_valid is True
        assert unit_will_fail is True

    def test_generated_tests_contain_proper_structure(self):
        """Verify generated tests have proper pytest structure."""
        # Arrange
        output_dir = self.test_workspace / "structure_test"
        output_dir.mkdir()
        
        # Act
        result = self.generator.generate_pytest_test_files_from_yaml(
            self.layer_yaml, output_dir
        )
        
        # Assert - check structure
        unit_content = result['unit'].read_text()
        assert 'import pytest' in unit_content
        assert 'class Test' in unit_content
        assert 'def test_' in unit_content

    def test_standalone_integration(self):
        """Test layer functions independently."""
        # This layer can work standalone
        generator = TestCodeGenerator()
        assert generator is not None
        assert generator.template_engine is not None

        
