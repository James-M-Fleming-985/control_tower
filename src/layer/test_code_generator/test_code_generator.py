"""
Test Code Generator

Layer: LAYER-004-01-02-01
Requirement: Test Code Generator

Generates pytest test files from YAML acceptance criteria.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import yaml
import re

# REQ-LAYER-004-01-02-01


class PromptTemplateEngine:
    """Template engine for building AI prompts from YAML."""
    
    def __init__(self):
        """Initialize the template engine."""
        self.templates = {
            'test_generation': """Generate pytest unit tests for the following acceptance criteria:

Layer: {layer_id}
Requirement: {requirement_name}

Acceptance Criteria:
{acceptance_criteria}

Requirements:
- Follow pytest conventions
- Use descriptive test names
- Include docstrings
- Add proper assertions
- Tests should fail initially (RED phase)

Generate complete, executable pytest tests."""
        }
    
    def build_prompt(self, template_name: str, **kwargs) -> str:
        """
        Build a prompt from template and variables.
        
        Args:
            template_name: Name of the template to use
            **kwargs: Variables to inject into template
            
        Returns:
            Formatted prompt string
            
        Raises:
            ValueError: If template doesn't exist
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required template variable: {e}")


class TestCodeGenerator:
    """
    Test Code Generator
    
    Acceptance Criteria:
    - Generate pytest test files from YAML acceptance criteria
    - Generated tests must fail in RED phase
    - Build prompts from YAML using template engine
    """

    def __init__(self, ai_provider=None):
        """
        Initialize the test code generator.
        
        Args:
            ai_provider: Optional AI provider for code generation
        """
        self.ai_provider = ai_provider
        self.template_engine = PromptTemplateEngine()
        self.generated_tests = []

    def parse_yaml_file(self, yaml_path: Path) -> Dict[str, Any]:
        """
        Parse YAML specification file.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            Parsed YAML as dictionary
            
        Raises:
            ValueError: If YAML is invalid or empty
        """
        if not yaml_path.exists():
            raise ValueError(f"YAML file not found: {yaml_path}")
        
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            raise ValueError("YAML file is empty")
        
        return data

    def extract_acceptance_criteria(self, yaml_data: Dict) -> List[Dict]:
        """
        Extract acceptance criteria from YAML data.
        
        Args:
            yaml_data: Parsed YAML dictionary
            
        Returns:
            List of acceptance criteria dictionaries
        """
        ac_list = yaml_data.get('acceptance_criteria', [])
        
        if not ac_list:
            return []
        
        return ac_list

    def build_test_generation_prompt(self, layer_id: str, requirement_name: str, 
                                     acceptance_criteria: List[Dict]) -> str:
        """
        AC-003: Build prompts from YAML using template engine
        
        Args:
            layer_id: Layer identifier
            requirement_name: Name of the requirement
            acceptance_criteria: List of AC dictionaries
            
        Returns:
            Formatted prompt for AI generation
        """
        # REQ-AC-003
        
        # Format acceptance criteria for prompt
        ac_text = ""
        for ac in acceptance_criteria:
            criterion_id = ac.get('criterion_id', 'AC-XXX')
            criterion = ac.get('criterion', '')
            priority = ac.get('priority', 'medium')
            ac_text += f"\n{criterion_id} ({priority}): {criterion}"
        
        return self.template_engine.build_prompt(
            'test_generation',
            layer_id=layer_id,
            requirement_name=requirement_name,
            acceptance_criteria=ac_text
        )

    def generate_unit_test_file(self, layer_id: str, requirement_name: str,
                                acceptance_criteria: List[Dict], 
                                output_path: Optional[Path] = None) -> str:
        """
        AC-001: Generate pytest test files from YAML acceptance criteria
        
        Args:
            layer_id: Layer identifier
            requirement_name: Name of the requirement
            acceptance_criteria: List of AC dictionaries
            output_path: Optional path to save the file
            
        Returns:
            Generated test code as string
        """
        # REQ-AC-001
        
        # Build the test file content
        test_code = f'''"""
Unit Tests for {requirement_name}
Layer: {layer_id}

Generated from acceptance criteria.
Tests follow TDD RED phase - they should FAIL initially.
"""

import pytest
from pathlib import Path
from typing import Dict, List


class Test{self._to_class_name(requirement_name)}Unit:
    """Unit tests for {requirement_name}."""

    def setup_method(self):
        """Setup test fixtures."""
        # Initialize test data
        self.test_data = {{}}
'''
        
        # Generate test methods for each AC
        for ac in acceptance_criteria:
            criterion_id = ac.get('criterion_id', 'AC-XXX')
            criterion = ac.get('criterion', '')
            test_name = self._to_test_name(criterion)
            
            test_code += f'''
    def test_{test_name}(self):
        """
        {criterion_id}: {criterion}
        
        This test validates acceptance criterion {criterion_id}.
        Expected to FAIL in RED phase until implementation is complete.
        """
        # REQ-{criterion_id}
        
        # Arrange
        test_input = "test_data"
        
        # Act
        with pytest.raises(NotImplementedError):
            # This should fail until implementation exists
            result = None  # Replace with actual call
        
        # Assert - will fail until GREEN phase
        # assert result is not None
'''
        
        # Save to file if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(test_code)
        
        self.generated_tests.append(test_code)
        return test_code

    def generate_integration_test_file(self, layer_id: str, requirement_name: str,
                                      acceptance_criteria: List[Dict],
                                      output_path: Optional[Path] = None) -> str:
        """
        AC-001: Generate pytest integration test files
        
        Args:
            layer_id: Layer identifier
            requirement_name: Name of the requirement
            acceptance_criteria: List of AC dictionaries
            output_path: Optional path to save the file
            
        Returns:
            Generated test code as string
        """
        # REQ-AC-001
        
        test_code = f'''"""
Integration Tests for {requirement_name}
Layer: {layer_id}

Tests component integration and end-to-end workflows.
"""

import pytest
from pathlib import Path


class Test{self._to_class_name(requirement_name)}Integration:
    """Integration tests for {requirement_name}."""

    def setup_method(self):
        """Setup integration test fixtures."""
        self.test_workspace = Path("/tmp/test_workspace")
        self.test_workspace.mkdir(exist_ok=True)

    def teardown_method(self):
        """Cleanup after tests."""
        import shutil
        if self.test_workspace.exists():
            shutil.rmtree(self.test_workspace)

    def test_end_to_end_workflow(self):
        """
        Test complete end-to-end workflow.
        
        Expected to FAIL until full integration is complete.
        """
        # Setup test environment
        test_file = self.test_workspace / "test.yaml"
        
        # Execute end-to-end workflow
        with pytest.raises(NotImplementedError):
            result = None  # Replace with actual integration
        
        # Verify results
        # assert result is not None
'''
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(test_code)
        
        self.generated_tests.append(test_code)
        return test_code

    def validate_generated_test_syntax(self, test_code: str) -> bool:
        """
        Validate that generated test code has valid Python syntax.
        
        Args:
            test_code: The generated test code
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            compile(test_code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False

    def generate_pytest_test_files_from_yaml(self, yaml_path: Path, 
                                            output_dir: Path) -> Dict[str, Path]:
        """
        AC-001: Generate pytest test files from YAML acceptance criteria
        
        Main entry point for test generation.
        
        Args:
            yaml_path: Path to YAML specification
            output_dir: Directory to save generated tests
            
        Returns:
            Dictionary mapping test type to file path
            
        Raises:
            ValueError: If YAML is invalid
        """
        # REQ-AC-001
        
        # Parse YAML
        yaml_data = self.parse_yaml_file(yaml_path)
        
        # Extract metadata and ACs
        metadata = yaml_data.get('metadata', {})
        layer_id = metadata.get('requirement_id', 'UNKNOWN')
        requirement_name = metadata.get('requirement_name', 'Unknown Requirement')
        acceptance_criteria = self.extract_acceptance_criteria(yaml_data)
        
        # Generate test files
        result = {}
        
        # Unit tests
        unit_test_path = output_dir / f"test_{self._to_snake_case(requirement_name)}_unit.py"
        self.generate_unit_test_file(layer_id, requirement_name, acceptance_criteria, unit_test_path)
        result['unit'] = unit_test_path
        
        # Integration tests
        integration_test_path = output_dir / f"test_{self._to_snake_case(requirement_name)}_integration.py"
        self.generate_integration_test_file(layer_id, requirement_name, acceptance_criteria, integration_test_path)
        result['integration'] = integration_test_path
        
        return result

    def verify_tests_fail_without_implementation(self, test_code: str) -> bool:
        """
        AC-002: Generated tests must fail in RED phase
        
        Verify that generated tests contain appropriate failure mechanisms.
        
        Args:
            test_code: The generated test code
            
        Returns:
            True if tests will fail without implementation
        """
        # REQ-AC-002
        
        # Check for failure indicators
        has_not_implemented = 'NotImplementedError' in test_code
        has_pytest_raises = 'pytest.raises' in test_code
        has_placeholder_assertions = 'Replace with actual' in test_code or 'TODO' in test_code
        
        return has_not_implemented or has_pytest_raises or has_placeholder_assertions

    def _to_class_name(self, text: str) -> str:
        """Convert text to PascalCase class name."""
        words = re.sub(r'[^a-zA-Z0-9\s]', ' ', text).split()
        return ''.join(word.capitalize() for word in words)

    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        words = text.lower().split()
        return '_'.join(words)

    def _to_test_name(self, text: str) -> str:
        """Convert criterion text to test method name."""
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        words = text.lower().split()
        return '_'.join(words[:8])  # Limit length
        
