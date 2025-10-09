"""
Integration Tests for AI Code Generator Orchestrator
Layer: LAYER-004-01-03-01

Tests for end-to-end TDD cycle orchestration.
"""
from pathlib import Path


class TestAICodeGeneratorOrchestratorIntegration:
    """Integration tests for AICodeGeneratorOrchestrator."""
    
    def test_execute_full_tdd_cycle(self):
        """
        AC-001: Execute complete RED -> GREEN -> REFACTOR cycle.
        
        Integration test that verifies the orchestrator can execute
        the complete TDD cycle from YAML requirements to final
        verification.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import (
            AICodeGeneratorOrchestrator
        )
        
        config = {
            'output_base_path': Path('output/test')
        }
        orchestrator = AICodeGeneratorOrchestrator(config)
        
        # Create minimal test requirements
        requirements = {
            'requirement_id': 'TEST-001',
            'acceptance_criteria': [
                {
                    'criterion_id': 'AC-001',
                    'criterion': 'Test orchestration'
                }
            ]
        }
        
        # Execute full cycle
        result = orchestrator.execute_full_cycle(requirements)
        
        assert result is not None
        assert result['status'] == 'COMPLETE'
        assert 'RED' in result['phases']
        assert 'GREEN' in result['phases']
        assert 'REFACTOR' in result['phases']
        assert result['phases']['RED']['tests_failed'] > 0
        assert result['phases']['GREEN']['tests_passed'] > 0
    
    def test_integration_with_test_generator(self):
        """
        AC-001: Integrate with LAYER-004-01-02-01 Test Code Generator.
        
        Test that the orchestrator can successfully call the
        test code generator and receive generated test files.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import (
            AICodeGeneratorOrchestrator
        )
        
        orchestrator = AICodeGeneratorOrchestrator({})
        
        requirements = {
            'acceptance_criteria': [
                {'criterion_id': 'AC-001', 'criterion': 'Test integration'}
            ]
        }
        
        # Call test generator integration
        test_files = orchestrator.call_test_generator(requirements)
        
        assert test_files is not None
        assert isinstance(test_files, list)
        assert len(test_files) > 0
    
    def test_integration_with_implementation_generator(self):
        """
        AC-001: Integrate with LAYER-004-01-02-02 Implementation Generator.
        
        Test that the orchestrator can successfully call the
        implementation code generator and receive generated code.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import (
            AICodeGeneratorOrchestrator
        )
        
        orchestrator = AICodeGeneratorOrchestrator({})
        
        requirements = {
            'acceptance_criteria': [
                {'criterion_id': 'AC-001', 'criterion': 'Test integration'}
            ]
        }
        test_results = {
            'failed_tests': ['test_example']
        }
        
        # Call implementation generator integration
        impl_files = orchestrator.call_implementation_generator(
            requirements,
            test_results
        )
        
        assert impl_files is not None
        assert isinstance(impl_files, list)
        assert len(impl_files) > 0
    
    def test_verification_report_generation(self):
        """
        AC-002: Generate complete verification reports.
        
        Integration test that verifies all required verification
        reports are generated with correct structure and content.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import (
            AICodeGeneratorOrchestrator
        )
        
        orchestrator = AICodeGeneratorOrchestrator({})
        
        cycle_results = {
            'RED': {
                'phase': 'RED',
                'tests_failed': 5,
                'tests_generated': ['test_1.py', 'test_2.py']
            },
            'GREEN': {
                'phase': 'GREEN',
                'tests_passed': 5,
                'coverage': 0.96,
                'implementation_generated': ['impl.py']
            },
            'REFACTOR': {
                'phase': 'REFACTOR',
                'tests_still_passing': True,
                'improvements': ['Added constants', 'Enhanced errors']
            }
        }
        
        requirements = {
            'requirement_id': 'TEST-001',
            'acceptance_criteria': [
                {'criterion_id': 'AC-001', 'criterion': 'Test'}
            ]
        }
        
        # Generate all verification reports
        reports = orchestrator.generate_all_reports(
            cycle_results,
            requirements
        )
        
        assert reports is not None
        assert 'test_pyramid_report' in reports
        assert 'requirements_verification' in reports
        assert 'traceability_matrix' in reports
        assert 'quality_gates_report' in reports
    
    def test_end_to_end_layer_execution(self):
        """
        AC-001, AC-002: Complete layer execution from YAML to reports.
        
        Full end-to-end integration test that starts with a YAML
        requirements file and produces all verification artifacts.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import (
            AICodeGeneratorOrchestrator
        )
        
        config = {
            'output_base_path': Path('output/e2e_test')
        }
        orchestrator = AICodeGeneratorOrchestrator(config)
        
        # Use real YAML requirements (minimal test version)
        yaml_path = Path('test_requirements.yaml')
        
        # Execute end-to-end
        result = orchestrator.execute_from_yaml(yaml_path)
        
        assert result is not None
        assert result['status'] == 'COMPLETE'
        assert 'verification_reports' in result
        assert 'artifacts_saved' in result
        assert result['artifacts_saved'] is True
