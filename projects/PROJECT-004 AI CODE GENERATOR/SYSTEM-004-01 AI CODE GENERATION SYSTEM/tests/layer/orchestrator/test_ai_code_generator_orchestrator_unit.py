"""
Unit Tests for AI Code Generator Orchestrator
Layer: LAYER-004-01-03-01

Tests for orchestrating the complete TDD cycle.
"""
import pytest
from pathlib import Path
from typing import Dict, Any, List


class TestAICodeGeneratorOrchestratorUnit:
    """Unit tests for AICodeGeneratorOrchestrator."""
    
    def test_orchestrator_initialization(self):
        """
        AC-001: Initialize orchestrator with configuration.
        
        Test that the orchestrator can be created with proper configuration
        including paths for test generator, implementation generator, and
        output directories.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        config = {
            'test_generator_path': Path('src/layer/test_code_generator'),
            'impl_generator_path': Path('src/layer/implementation_code_generator'),
            'output_base_path': Path('output')
        }
        
        orchestrator = AICodeGeneratorOrchestrator(config)
        
        assert orchestrator is not None
        assert orchestrator.config == config
        assert orchestrator.current_phase is None
        assert orchestrator.phase_results == {}
    
    def test_load_yaml_requirements(self):
        """
        AC-001: Load YAML requirements specification.
        
        Test that the orchestrator can load a YAML file containing
        layer requirements and extract acceptance criteria.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        orchestrator = AICodeGeneratorOrchestrator({})
        yaml_path = Path('test_spec.yaml')
        
        # Should load YAML and extract requirements
        requirements = orchestrator.load_yaml_requirements(yaml_path)
        
        assert requirements is not None
        assert 'acceptance_criteria' in requirements
        assert isinstance(requirements['acceptance_criteria'], list)
    
    def test_execute_red_phase(self):
        """
        AC-001: Execute RED phase - generate tests that fail.
        
        Test that the orchestrator can execute the RED phase which
        involves generating tests from requirements and verifying they fail.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        orchestrator = AICodeGeneratorOrchestrator({})
        requirements = {
            'acceptance_criteria': [
                {'criterion_id': 'AC-001', 'criterion': 'Test criterion'}
            ]
        }
        
        result = orchestrator.execute_red_phase(requirements)
        
        assert result['phase'] == 'RED'
        assert result['status'] in ['PASS', 'FAIL']
        assert 'tests_generated' in result
        assert 'tests_failed' in result
        assert result['tests_failed'] > 0  # Tests should fail in RED phase
    
    def test_execute_green_phase(self):
        """
        AC-001: Execute GREEN phase - implement code to pass tests.
        
        Test that the orchestrator can execute the GREEN phase which
        involves generating implementation code to pass the failing tests.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        orchestrator = AICodeGeneratorOrchestrator({})
        red_results = {
            'tests_generated': ['test_file.py'],
            'tests_failed': 5
        }
        requirements = {
            'acceptance_criteria': [
                {'criterion_id': 'AC-001', 'criterion': 'Test criterion'}
            ]
        }
        
        result = orchestrator.execute_green_phase(requirements, red_results)
        
        assert result['phase'] == 'GREEN'
        assert result['status'] in ['PASS', 'FAIL']
        assert 'implementation_generated' in result
        assert 'tests_passed' in result
    
    def test_execute_refactor_phase(self):
        """
        AC-001: Execute REFACTOR phase - improve code quality.
        
        Test that the orchestrator can execute the REFACTOR phase which
        involves improving code quality while maintaining test passage.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        orchestrator = AICodeGeneratorOrchestrator({})
        green_results = {
            'tests_passed': 5,
            'coverage': 0.96
        }
        
        result = orchestrator.execute_refactor_phase(green_results)
        
        assert result['phase'] == 'REFACTOR'
        assert result['status'] in ['PASS', 'FAIL']
        assert 'refactoring_applied' in result
        assert 'tests_still_passing' in result
    
    def test_execute_verification_phase(self):
        """
        AC-002: Execute verification phase - generate reports.
        
        Test that the orchestrator can execute the verification phase
        which generates comprehensive verification reports.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        orchestrator = AICodeGeneratorOrchestrator({})
        all_results = {
            'RED': {'tests_failed': 5},
            'GREEN': {'tests_passed': 5},
            'REFACTOR': {'tests_still_passing': True}
        }
        
        result = orchestrator.execute_verification_phase(all_results)
        
        assert result['phase'] == 'VERIFICATION'
        assert result['status'] in ['PASS', 'FAIL']
        assert 'verification_reports' in result
        assert 'traceability_complete' in result
    
    def test_validate_phase_transitions(self):
        """
        AC-001: Validate that phases execute in correct order.
        
        Test that the orchestrator enforces RED -> GREEN -> REFACTOR
        phase transitions and prevents invalid transitions.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        orchestrator = AICodeGeneratorOrchestrator({})
        
        # Should allow RED as first phase
        assert orchestrator.validate_phase_transition(None, 'RED') == True
        
        # Should allow GREEN after RED
        assert orchestrator.validate_phase_transition('RED', 'GREEN') == True
        
        # Should allow REFACTOR after GREEN
        assert orchestrator.validate_phase_transition('GREEN', 'REFACTOR') == True
        
        # Should NOT allow GREEN before RED
        assert orchestrator.validate_phase_transition(None, 'GREEN') == False
        
        # Should NOT allow REFACTOR before GREEN
        assert orchestrator.validate_phase_transition('RED', 'REFACTOR') == False
    
    def test_collect_evidence_per_phase(self):
        """
        AC-002: Collect evidence artifacts for each phase.
        
        Test that the orchestrator collects and stores evidence
        (test results, logs, coverage) for each phase.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        orchestrator = AICodeGeneratorOrchestrator({})
        phase_result = {
            'phase': 'GREEN',
            'tests_passed': 5,
            'coverage': 0.96
        }
        
        evidence = orchestrator.collect_evidence(phase_result)
        
        assert evidence is not None
        assert 'phase' in evidence
        assert 'timestamp' in evidence
        assert 'artifacts' in evidence
        assert isinstance(evidence['artifacts'], list)
    
    def test_generate_verification_reports(self):
        """
        AC-002: Generate comprehensive verification reports.
        
        Test that the orchestrator can generate all required
        verification reports including test pyramid, requirements
        verification, and traceability matrix.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        orchestrator = AICodeGeneratorOrchestrator({})
        all_results = {
            'RED': {'tests_failed': 5},
            'GREEN': {'tests_passed': 5, 'coverage': 0.96},
            'REFACTOR': {'tests_still_passing': True}
        }
        requirements = {
            'acceptance_criteria': [
                {'criterion_id': 'AC-001', 'criterion': 'Test criterion'}
            ]
        }
        
        reports = orchestrator.generate_verification_reports(all_results, requirements)
        
        assert reports is not None
        assert 'test_pyramid_report' in reports
        assert 'requirements_verification' in reports
        assert 'traceability_matrix' in reports
    
    def test_handle_phase_failures(self):
        """
        AC-001: Handle failures in any phase gracefully.
        
        Test that the orchestrator can detect and report failures
        in any phase and prevent continuation to next phase.
        """
        from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
        
        orchestrator = AICodeGeneratorOrchestrator({})
        
        # Simulate RED phase failure (tests didn't fail)
        red_result_invalid = {
            'phase': 'RED',
            'tests_failed': 0  # Invalid - tests should fail in RED
        }
        
        is_valid = orchestrator.validate_phase_result('RED', red_result_invalid)
        
        assert is_valid == False
        
        # Simulate GREEN phase failure (tests didn't pass)
        green_result_invalid = {
            'phase': 'GREEN',
            'tests_passed': 0  # Invalid - tests should pass in GREEN
        }
        
        is_valid = orchestrator.validate_phase_result('GREEN', green_result_invalid)
        
        assert is_valid == False
