"""
Integration Tests for Implementation Code Generator
Layer: LAYER-004-01-02-02

Tests integration with other layers and real YAML files.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from src.layer.implementation_code_generator import (
    ImplementationCodeGenerator,
    CodeValidator
)

# REQ-LAYER-004-01-02-02

pytestmark = pytest.mark.integration


class TestImplementationCodeGeneratorIntegration:
    """Integration tests for ImplementationCodeGenerator."""

    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ImplementationCodeGenerator()
        
        # Create a realistic YAML specification
        self.full_yaml = {
            'metadata': {
                'requirement_id': 'LAYER-004-01-02-03',
                'requirement_name': 'Integration Code Generator',
                'layer_number': '003',
                'system_id': 'SYSTEM-004-01',
                'project_id': 'PROJECT-004'
            },
            'acceptance_criteria': [
                {
                    'criterion_id': 'AC-001',
                    'criterion': 'Generate integration tests from YAML',
                    'validation_method': 'Automated test execution'
                },
                {
                    'criterion_id': 'AC-002',
                    'criterion': 'Validate test coverage requirements',
                    'validation_method': 'Coverage analysis'
                },
                {
                    'criterion_id': 'AC-003',
                    'criterion': 'Create pytest fixtures automatically',
                    'validation_method': 'Fixture inspection'
                }
            ],
            'traceability': {
                'requirement_to_test_mapping': {
                    'AC-001': ['test_generate_integration_tests'],
                    'AC-002': ['test_validate_coverage'],
                    'AC-003': ['test_create_fixtures']
                }
            }
        }

    def test_generate_from_real_yaml_file(self):
        """Test generating implementation from real YAML file."""
        # REQ-AC-001, REQ-AC-003
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write YAML to file
            yaml_path = Path(tmpdir) / "layer_spec.yaml"
            with open(yaml_path, 'w') as f:
                yaml.dump(self.full_yaml, f)
            
            output_dir = Path(tmpdir) / "generated"
            output_dir.mkdir()
            
            # Generate implementation
            impl_file = self.generator.generate_implementation_from_yaml(
                yaml_path,
                output_dir
            )
            
            assert impl_file.exists()
            assert impl_file.name == 'integration_code_generator.py'
            
            # Verify content
            with open(impl_file, 'r') as f:
                content = f.read()
            
            assert 'class IntegrationCodeGenerator:' in content
            assert 'AC-001' in content
            assert 'AC-002' in content
            assert 'AC-003' in content

    def test_generated_code_is_syntactically_valid(self):
        """Test that generated code has valid Python syntax."""
        # REQ-AC-002
        
        ac_list = self.full_yaml['acceptance_criteria']
        mapping = self.full_yaml['traceability']['requirement_to_test_mapping']
        
        code = self.generator.generate_implementation_class(
            'LAYER-TEST-001',
            'Test Generator',
            ac_list,
            mapping
        )
        
        validator = CodeValidator()
        assert validator.validate_syntax(code) is True

    def test_generated_code_has_required_quality(self):
        """Test that generated code meets quality standards."""
        # REQ-AC-002
        
        ac_list = self.full_yaml['acceptance_criteria']
        mapping = self.full_yaml['traceability']['requirement_to_test_mapping']
        
        code = self.generator.generate_implementation_class(
            'LAYER-TEST-001',
            'Test Generator',
            ac_list,
            mapping
        )
        
        validator = CodeValidator()
        quality = validator.validate_quality(code)
        
        assert quality['has_docstrings'] is True
        assert quality['has_type_hints'] is True
        assert quality['has_classes'] is True
        assert quality['has_methods'] is True
        assert quality['syntax_valid'] is True

    def test_multiple_yaml_files_generation(self):
        """Test generating implementations for multiple YAML files."""
        # REQ-AC-001, REQ-AC-003
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()
            
            # Create multiple YAML files
            for i in range(3):
                yaml_data = {
                    'metadata': {
                        'requirement_id': f'LAYER-TEST-{i:03d}',
                        'requirement_name': f'Test Requirement {i}'
                    },
                    'acceptance_criteria': [
                        {
                            'criterion_id': 'AC-001',
                            'criterion': f'Criterion for requirement {i}'
                        }
                    ],
                    'traceability': {
                        'requirement_to_test_mapping': {}
                    }
                }
                
                yaml_path = tmpdir_path / f"layer_{i}.yaml"
                with open(yaml_path, 'w') as f:
                    yaml.dump(yaml_data, f)
                
                # Generate implementation
                impl_file = self.generator.generate_implementation_from_yaml(
                    yaml_path,
                    output_dir
                )
                
                assert impl_file.exists()
            
            # Verify all files generated
            generated_files = list(output_dir.glob("*.py"))
            assert len(generated_files) == 3

    def test_traceability_mapping_affects_generation(self):
        """Test that traceability mapping is used in generation."""
        # REQ-AC-003
        
        yaml_with_mapping = self.full_yaml.copy()
        mapping = self.generator.extract_traceability_mapping(yaml_with_mapping)
        
        assert 'AC-001' in mapping
        assert 'AC-002' in mapping
        assert 'AC-003' in mapping

    def test_end_to_end_workflow(self):
        """Test complete workflow from YAML to validated implementation."""
        # REQ-AC-001, REQ-AC-002, REQ-AC-003
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: Create YAML
            yaml_path = Path(tmpdir) / "spec.yaml"
            with open(yaml_path, 'w') as f:
                yaml.dump(self.full_yaml, f)
            
            # Step 2: Parse YAML
            parsed = self.generator.parse_yaml_file(yaml_path)
            assert parsed is not None
            
            # Step 3: Extract components
            ac_list = self.generator.extract_acceptance_criteria(parsed)
            mapping = self.generator.extract_traceability_mapping(parsed)
            
            assert len(ac_list) == 3
            assert len(mapping) == 3
            
            # Step 4: Generate implementation
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir()
            
            impl_file = self.generator.generate_implementation_from_yaml(
                yaml_path,
                output_dir
            )
            
            # Step 5: Verify output
            assert impl_file.exists()
            
            with open(impl_file, 'r') as f:
                code = f.read()
            
            # Step 6: Validate quality
            validator = CodeValidator()
            assert validator.validate_syntax(code) is True
            
            quality = validator.validate_quality(code)
            assert quality['overall_score'] > 0.8

    def test_generated_implementation_has_all_methods(self):
        """Test that all ACs result in methods."""
        # REQ-AC-001, REQ-AC-003
        
        ac_list = self.full_yaml['acceptance_criteria']
        mapping = self.full_yaml['traceability']['requirement_to_test_mapping']
        
        code = self.generator.generate_implementation_class(
            'LAYER-TEST-001',
            'Complete Generator',
            ac_list,
            mapping
        )
        
        # Check that each AC has a corresponding method
        for ac in ac_list:
            assert ac['criterion_id'] in code
