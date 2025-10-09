"""
Unit Tests for Test Code Generator
Layer: LAYER-004-01-02-01

Tests for test code generation functionality.
"""

import pytest
from pathlib import Path
from typing import Dict, List
import tempfile
import shutil

from src.layer.test_code_generator import TestCodeGenerator, PromptTemplateEngine

# REQ-LAYER-004-01-02-01


class TestPromptTemplateEngineUnit:
    """Unit tests for PromptTemplateEngine."""

    def setup_method(self):
        """Setup test fixtures."""
        self.engine = PromptTemplateEngine()

    def test_prompt_template_engine_initialization(self):
        """Test that template engine initializes with templates."""
        assert self.engine is not None
        assert hasattr(self.engine, 'templates')
        assert 'test_generation' in self.engine.templates

    def test_build_prompt_with_valid_template(self):
        """
        AC-003: Build prompts from YAML using template engine
        
        Test building a prompt with valid template and variables.
        """
        # REQ-AC-003
        
        # Arrange
        layer_id = "LAYER-TEST-001"
        requirement_name = "Test Requirement"
        acceptance_criteria = "\nAC-001: Test criterion"
        
        # Act
        prompt = self.engine.build_prompt(
            'test_generation',
            layer_id=layer_id,
            requirement_name=requirement_name,
            acceptance_criteria=acceptance_criteria
        )
        
        # Assert
        assert prompt is not None
        assert layer_id in prompt
        assert requirement_name in prompt
        assert "AC-001" in prompt
        assert "pytest" in prompt

    def test_build_prompt_invalid_template(self):
        """Test that building with invalid template raises error."""
        with pytest.raises(ValueError, match="Template .* not found"):
            self.engine.build_prompt('nonexistent_template')

    def test_build_prompt_missing_variable(self):
        """Test that missing template variable raises error."""
        with pytest.raises(ValueError, match="Missing required template variable"):
            self.engine.build_prompt('test_generation', layer_id="TEST")


class TestTestCodeGeneratorUnit:
    """Unit tests for TestCodeGenerator."""

    def setup_method(self):
        """Setup test fixtures."""
        self.generator = TestCodeGenerator()
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create sample YAML data
        self.sample_yaml_path = self.test_dir / "test_layer.yaml"
        yaml_content = """
metadata:
  requirement_id: LAYER-TEST-001
  requirement_name: Test Layer
  requirement_type: Layer

acceptance_criteria:
  - criterion_id: AC-001
    criterion: "First test criterion"
    priority: critical
  - criterion_id: AC-002
    criterion: "Second test criterion"
    priority: high
"""
        with open(self.sample_yaml_path, 'w') as f:
            f.write(yaml_content)

    def teardown_method(self):
        """Cleanup test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_parse_yaml_file(self):
        """Test parsing YAML file."""
        # Act
        result = self.generator.parse_yaml_file(self.sample_yaml_path)
        
        # Assert
        assert result is not None
        assert 'metadata' in result
        assert 'acceptance_criteria' in result

    def test_parse_yaml_file_not_found(self):
        """Test error when YAML file doesn't exist."""
        with pytest.raises(ValueError, match="YAML file not found"):
            self.generator.parse_yaml_file(Path("/nonexistent/file.yaml"))

    def test_parse_yaml_empty_file(self):
        """Test error when YAML file is empty."""
        empty_file = self.test_dir / "empty.yaml"
        empty_file.write_text("")
        
        with pytest.raises(ValueError, match="YAML file is empty"):
            self.generator.parse_yaml_file(empty_file)

    def test_extract_acceptance_criteria(self):
        """Test extracting acceptance criteria from YAML data."""
        # Arrange
        yaml_data = self.generator.parse_yaml_file(self.sample_yaml_path)
        
        # Act
        ac_list = self.generator.extract_acceptance_criteria(yaml_data)
        
        # Assert
        assert isinstance(ac_list, list)
        assert len(ac_list) == 2
        assert ac_list[0]['criterion_id'] == 'AC-001'
        assert ac_list[1]['criterion_id'] == 'AC-002'

    def test_extract_acceptance_criteria_empty(self):
        """Test extracting ACs when none exist."""
        result = self.generator.extract_acceptance_criteria({})
        assert result == []

    def test_build_test_generation_prompt(self):
        """
        AC-003: Build prompts from YAML using template engine
        
        Test building test generation prompt from YAML data.
        """
        # REQ-AC-003
        
        # Arrange
        layer_id = "LAYER-TEST-001"
        requirement_name = "Test Requirement"
        acceptance_criteria = [
            {'criterion_id': 'AC-001', 'criterion': 'Test AC 1', 'priority': 'critical'},
            {'criterion_id': 'AC-002', 'criterion': 'Test AC 2', 'priority': 'high'}
        ]
        
        # Act
        prompt = self.generator.build_test_generation_prompt(
            layer_id, requirement_name, acceptance_criteria
        )
        
        # Assert
        assert prompt is not None
        assert layer_id in prompt
        assert requirement_name in prompt
        assert 'AC-001' in prompt
        assert 'AC-002' in prompt
        assert 'critical' in prompt

    def test_generate_unit_test_file(self):
        """
        AC-001: Generate pytest test files from YAML acceptance criteria
        
        Test generating unit test file.
        """
        # REQ-AC-001
        
        # Arrange
        layer_id = "LAYER-TEST-001"
        requirement_name = "Test Layer"
        acceptance_criteria = [
            {'criterion_id': 'AC-001', 'criterion': 'Test criterion', 'priority': 'critical'}
        ]
        output_path = self.test_dir / "test_generated_unit.py"
        
        # Act
        result = self.generator.generate_unit_test_file(
            layer_id, requirement_name, acceptance_criteria, output_path
        )
        
        # Assert
        assert result is not None
        assert output_path.exists()
        assert 'import pytest' in result
        assert 'class Test' in result
        assert 'def test_' in result

    def test_generate_integration_test_file(self):
        """
        AC-001: Generate pytest integration test files
        
        Test generating integration test file.
        """
        # REQ-AC-001
        
        # Arrange
        layer_id = "LAYER-TEST-001"
        requirement_name = "Test Layer"
        acceptance_criteria = [
            {'criterion_id': 'AC-001', 'criterion': 'Test criterion', 'priority': 'critical'}
        ]
        output_path = self.test_dir / "test_generated_integration.py"
        
        # Act
        result = self.generator.generate_integration_test_file(
            layer_id, requirement_name, acceptance_criteria, output_path
        )
        
        # Assert
        assert result is not None
        assert output_path.exists()
        assert 'import pytest' in result
        assert 'Integration' in result

    def test_validate_generated_test_syntax(self):
        """Test validation of generated test syntax."""
        # Valid Python code
        valid_code = "import pytest\n\nclass TestExample:\n    def test_one(self):\n        assert True"
        assert self.generator.validate_generated_test_syntax(valid_code) is True
        
        # Invalid Python code
        invalid_code = "import pytest\n\nclass TestExample:\n    def test_one(\n        assert True"
        assert self.generator.validate_generated_test_syntax(invalid_code) is False

    def test_generate_pytest_test_files_from_yaml(self):
        """
        AC-001: Generate pytest test files from YAML acceptance criteria
        
        Test complete test file generation from YAML.
        """
        # REQ-AC-001
        
        # Arrange
        output_dir = self.test_dir / "generated_tests"
        output_dir.mkdir()
        
        # Act
        result = self.generator.generate_pytest_test_files_from_yaml(
            self.sample_yaml_path, output_dir
        )
        
        # Assert
        assert result is not None
        assert 'unit' in result
        assert 'integration' in result
        assert result['unit'].exists()
        assert result['integration'].exists()

    def test_verify_tests_fail_without_implementation(self):
        """
        AC-002: Generated tests must fail in RED phase
        
        Test that generated tests will fail without implementation.
        """
        # REQ-AC-002
        
        # Arrange
        test_code_with_not_implemented = "raise NotImplementedError('Test')"
        test_code_with_pytest_raises = "with pytest.raises(NotImplementedError): pass"
        test_code_with_placeholders = "result = None  # Replace with actual call"
        valid_passing_code = "assert True"
        
        # Act & Assert
        assert self.generator.verify_tests_fail_without_implementation(test_code_with_not_implemented) is True
        assert self.generator.verify_tests_fail_without_implementation(test_code_with_pytest_raises) is True
        assert self.generator.verify_tests_fail_without_implementation(test_code_with_placeholders) is True
        assert self.generator.verify_tests_fail_without_implementation(valid_passing_code) is False

    def test_to_class_name(self):
        """Test conversion to PascalCase class name."""
        assert self.generator._to_class_name("test layer name") == "TestLayerName"
        assert self.generator._to_class_name("test-layer-name") == "TestLayerName"
        assert self.generator._to_class_name("Test_Layer_Name") == "TestLayerName"

    def test_to_snake_case(self):
        """Test conversion to snake_case."""
        assert self.generator._to_snake_case("Test Layer Name") == "test_layer_name"
        assert self.generator._to_snake_case("TestLayerName") == "testlayername"

    def test_to_test_name(self):
        """Test conversion to test method name."""
        result = self.generator._to_test_name("Generate pytest test files from YAML")
        assert result.startswith("generate")
        assert "_" in result
        assert " " not in result

        
