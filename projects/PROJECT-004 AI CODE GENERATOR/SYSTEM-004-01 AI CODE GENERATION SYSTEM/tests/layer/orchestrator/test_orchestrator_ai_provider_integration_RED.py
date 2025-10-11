"""
AI Code Generator Orchestrator - RED PHASE Integration Tests
==============================================================

These tests verify ACTUAL BEHAVIOR, not just interfaces.
They will FAIL until GREEN phase implementation is complete.

Anti-Pattern Protection: These tests verify:
1. AI provider methods are actually called
2. Files are actually created on disk  
3. Pytest is actually executed
4. Verification reports actually exist

Expected Status: ALL TESTS FAIL (RED PHASE)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import tempfile
import yaml
import sys

# Add project src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Add control_tower root to path for AI provider abstraction
control_tower_root = project_root.parent.parent.parent
if str(control_tower_root) not in sys.path:
    sys.path.insert(0, str(control_tower_root))

# Import from project-local src (not control_tower src)
from layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator


class TestOrchestratorAIProviderIntegration:
    """
    REQ-ORCH-INT-001: Initialize AI Provider from Config
    
    These tests verify the orchestrator actually initializes and uses AI providers,
    not just stores config values.
    """

    def test_orchestrator_initializes_ai_provider_from_config(self):
        """
        RED: Orchestrator should initialize AI provider from config['provider']
        
        Expected Failure: AssertionError - AIProviderFactory.create_provider() not called
        """
        config = {
            'output_base_path': '/tmp/test_output',
            'provider': 'anthropic'
        }
        
        with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory') as mock_factory:
            mock_provider = Mock()
            mock_factory.create_provider.return_value = mock_provider
            
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            
            # VERIFY: Factory method was called with correct provider type
            mock_factory.create_provider.assert_called_once_with('anthropic')

    def test_orchestrator_validates_provider_configuration(self):
        """
        RED: Orchestrator should validate AI provider configuration
        
        Expected Failure: AssertionError - provider.validate_configuration() not called
        """
        config = {
            'output_base_path': '/tmp/test_output',
            'provider': 'anthropic'
        }
        
        with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory') as mock_factory:
            mock_provider = Mock()
            mock_provider.validate_configuration.return_value = True
            mock_factory.create_provider.return_value = mock_provider
            
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            
            # VERIFY: Validation was called
            mock_provider.validate_configuration.assert_called_once()

    def test_orchestrator_fails_with_invalid_provider_type(self):
        """
        RED: Should raise ValueError for unsupported provider types
        
        Expected Failure: No validation - accepts any provider value
        """
        config = {
            'output_base_path': '/tmp/test_output',
            'provider': 'invalid_provider'
        }
        
        # VERIFY: Should raise error for invalid provider
        with pytest.raises(ValueError, match="Unsupported provider type"):
            orchestrator = AICodeGeneratorOrchestrator(config=config)


class TestOrchestratorRedPhaseAI:
    """
    REQ-ORCH-INT-002: Generate Tests Using AI Provider
    
    These tests verify RED phase actually calls AI to generate test code,
    not just returns mock file names.
    """

    def test_red_phase_calls_ai_provider_for_test_generation(self):
        """
        RED: RED phase should call provider.generate_code() with test prompt
        
        Expected Failure: AssertionError - generate_code() never called
        """
        config = {
            'output_base_path': '/tmp/test_output',
            'provider': 'anthropic'
        }
        
        requirements = {
            'acceptance_criteria': [
                {
                    'criterion_id': 'AC-001',
                    'criterion': 'Test criterion',
                    'priority': 'high'
                }
            ]
        }
        
        with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory') as mock_factory:
            mock_provider = Mock()
            mock_provider.generate_code.return_value = "def test_example(): pass"
            mock_provider.validate_configuration.return_value = True
            mock_factory.create_provider.return_value = mock_provider
            
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            result = orchestrator.execute_red_phase(requirements)
            
            # VERIFY: AI provider was called
            assert mock_provider.generate_code.called, "AI provider should be called for test generation"
            
            # VERIFY: Prompt contains requirements
            call_args = mock_provider.generate_code.call_args
            assert call_args is not None, "generate_code should have been called with arguments"
            assert 'Test criterion' in call_args[0][0], "Prompt should contain acceptance criteria"

    def test_red_phase_writes_generated_tests_to_files(self):
        """
        RED: Should write AI-generated test code to actual files on disk
        
        Expected Failure: AssertionError - no files created
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_base_path': tmpdir,
                'provider': 'anthropic'
            }
            
            requirements = {
                'acceptance_criteria': [
                    {'criterion_id': 'AC-001', 'criterion': 'Test'}
                ]
            }
            
            with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory') as mock_factory:
                mock_provider = Mock()
                mock_provider.generate_code.return_value = "def test_example():\n    assert True"
                mock_provider.validate_configuration.return_value = True
                mock_factory.create_provider.return_value = mock_provider
                
                orchestrator = AICodeGeneratorOrchestrator(config=config)
                result = orchestrator.execute_red_phase(requirements)
                
                # VERIFY: Files actually created on disk
                test_files = list(Path(tmpdir).glob('**/test_*.py'))
                assert len(test_files) > 0, "Should create actual test files"
                
                # VERIFY: File contains generated code
                if test_files:
                    content = test_files[0].read_text()
                    assert 'def test_example' in content, "File should contain generated test"

    def test_red_phase_executes_generated_tests_with_pytest(self):
        """
        RED: Should execute pytest on generated tests
        
        Expected Failure: AssertionError - pytest not executed
        """
        config = {
            'output_base_path': '/tmp/test_output',
            'provider': 'anthropic'
        }
        
        requirements = {
            'acceptance_criteria': [
                {'criterion_id': 'AC-001', 'criterion': 'Test'}
            ]
        }
        
        with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory') as mock_factory, \
             patch('subprocess.run') as mock_run:
            
            mock_provider = Mock()
            mock_provider.generate_code.return_value = "def test_example(): assert False"
            mock_provider.validate_configuration.return_value = True
            mock_factory.create_provider.return_value = mock_provider
            
            # Mock pytest execution (tests should fail in RED phase)
            mock_run.return_value = Mock(returncode=1, stdout=b'1 failed')
            
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            result = orchestrator.execute_red_phase(requirements)
            
            # VERIFY: pytest was executed
            assert mock_run.called, "Should execute pytest on generated tests"
            
            # VERIFY: pytest command was used
            pytest_calls = [c for c in mock_run.call_args_list if 'pytest' in str(c)]
            assert len(pytest_calls) > 0, "Should call pytest"
            
            # VERIFY: Result reports failed tests
            assert result.get('tests_failed', 0) > 0, "RED phase should report failed tests"


class TestOrchestratorGreenPhaseAI:
    """
    REQ-ORCH-INT-003: Generate Implementation Using AI Provider
    
    These tests verify GREEN phase actually calls AI to generate implementation,
    not just returns mock success.
    """

    def test_green_phase_calls_ai_provider_for_implementation(self):
        """
        RED: GREEN phase should call provider.generate_code() with implementation prompt
        
        Expected Failure: AssertionError - generate_code() never called for implementation
        """
        config = {
            'output_base_path': '/tmp/test_output',
            'provider': 'anthropic'
        }
        
        requirements = {
            'acceptance_criteria': [
                {'criterion_id': 'AC-001', 'criterion': 'Implement feature X'}
            ]
        }
        
        red_results = {
            'tests_generated': ['test_feature_x.py'],
            'tests_failed': 3
        }
        
        with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory') as mock_factory:
            mock_provider = Mock()
            mock_provider.generate_code.return_value = "class FeatureX:\n    pass"
            mock_provider.validate_configuration.return_value = True
            mock_factory.create_provider.return_value = mock_provider
            
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            result = orchestrator.execute_green_phase(requirements, red_results)
            
            # VERIFY: AI provider was called
            assert mock_provider.generate_code.called, "Should call AI for implementation"
            
            # VERIFY: Prompt includes requirements
            call_args = mock_provider.generate_code.call_args
            assert call_args is not None, "generate_code should have been called"
            prompt = call_args[0][0]
            assert 'Implement feature X' in prompt, "Prompt should include requirements"

    def test_green_phase_writes_implementation_to_src_files(self):
        """
        RED: Should write AI-generated implementation to src/ directory
        
        Expected Failure: AssertionError - no source files created
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_base_path': tmpdir,
                'provider': 'anthropic'
            }
            
            requirements = {
                'acceptance_criteria': [
                    {'criterion_id': 'AC-001', 'criterion': 'Feature'}
                ],
                'layer_id': 'LAYER-TEST-01'
            }
            
            red_results = {'tests_failed': 3}
            
            with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory') as mock_factory:
                mock_provider = Mock()
                mock_provider.generate_code.return_value = "class Feature:\n    def method(self): pass"
                mock_provider.validate_configuration.return_value = True
                mock_factory.create_provider.return_value = mock_provider
                
                orchestrator = AICodeGeneratorOrchestrator(config=config)
                result = orchestrator.execute_green_phase(requirements, red_results)
                
                # VERIFY: Source files created on disk
                src_files = list(Path(tmpdir).glob('**/src/**/*.py'))
                assert len(src_files) > 0, "Should create source files in src/ directory"
                
                # VERIFY: File contains generated implementation
                if src_files:
                    content = src_files[0].read_text()
                    assert 'class Feature' in content, "File should contain generated implementation"

    def test_green_phase_reruns_tests_and_verifies_passing(self):
        """
        RED: Should rerun tests after implementation and verify they pass
        
        Expected Failure: AssertionError - tests not re-executed
        """
        config = {
            'output_base_path': '/tmp/test_output',
            'provider': 'anthropic'
        }
        
        requirements = {'acceptance_criteria': [{'criterion': 'Test'}]}
        red_results = {'tests_failed': 3, 'tests_generated': ['test_file.py']}
        
        with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory') as mock_factory, \
             patch('subprocess.run') as mock_run:
            
            mock_provider = Mock()
            mock_provider.generate_code.return_value = "implementation"
            mock_provider.validate_configuration.return_value = True
            mock_factory.create_provider.return_value = mock_provider
            
            # Mock pytest execution - tests now pass
            mock_run.return_value = Mock(returncode=0, stdout=b'3 passed')
            
            orchestrator = AICodeGeneratorOrchestrator(config=config)
            result = orchestrator.execute_green_phase(requirements, red_results)
            
            # VERIFY: pytest was executed after implementation
            assert mock_run.called, "Should run pytest after implementation"
            
            # VERIFY: Tests are reported as passing
            assert result.get('tests_passed', 0) > 0, "Should report passing tests"
            assert result.get('tests_passed') == red_results['tests_failed'], \
                "All previously failing tests should now pass"


class TestOrchestratorVerificationPhase:
    """
    REQ-ORCH-INT-004: Generate Verification Reports
    
    These tests verify verification reports are actually created with real evidence,
    not just returned as stub data.
    """

    def test_generate_all_reports_creates_yaml_files(self):
        """
        RED: Should create actual YAML verification report files on disk
        
        Expected Failure: AssertionError - no YAML files created
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_base_path': tmpdir,
                'provider': 'anthropic'
            }
            
            phases = {
                'RED': {'tests_failed': 3},
                'GREEN': {'tests_passed': 3},
                'REFACTOR': {'improvements': ['refactor 1']}
            }
            
            requirements = {'acceptance_criteria': [{'criterion': 'Test'}]}
            
            with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory'):
                orchestrator = AICodeGeneratorOrchestrator(config=config)
                reports = orchestrator.generate_all_reports(phases, requirements)
                
                # VERIFY: Directory created
                report_dir = Path(tmpdir) / "Requirements Verification"
                assert report_dir.exists(), "Should create Requirements Verification directory"
                
                # VERIFY: YAML files created
                yaml_files = list(report_dir.glob('*.yaml'))
                assert len(yaml_files) > 0, "Should create verification YAML files"
                
                # VERIFY: Expected reports exist
                expected_reports = [
                    'requirements_verification',
                    'test_pyramid_report',
                    'traceability_matrix',
                    'quality_gates_report'
                ]
                
                for report_name in expected_reports:
                    matching_files = [f for f in yaml_files if report_name in f.name]
                    assert len(matching_files) > 0, f"Should create {report_name}.yaml"

    def test_verification_reports_contain_actual_evidence(self):
        """
        RED: Reports should contain real test execution data, not stub values
        
        Expected Failure: AssertionError - reports contain stub data
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'output_base_path': tmpdir,
                'provider': 'anthropic'
            }
            
            phases = {
                'RED': {
                    'tests_failed': 5,
                    'tests_generated': ['test_file_1.py', 'test_file_2.py']
                },
                'GREEN': {
                    'tests_passed': 5,
                    'coverage': 0.96,
                    'implementation_generated': ['src/feature.py']
                }
            }
            
            requirements = {
                'layer_id': 'LAYER-TEST-01',
                'acceptance_criteria': [
                    {'criterion_id': 'AC-001', 'criterion': 'Feature X'}
                ]
            }
            
            with patch('layer.orchestrator.ai_code_generator_orchestrator.AIProviderFactory'):
                orchestrator = AICodeGeneratorOrchestrator(config=config)
                reports = orchestrator.generate_all_reports(phases, requirements)
                
                # VERIFY: Report file exists
                report_dir = Path(tmpdir) / "Requirements Verification"
                report_files = list(report_dir.glob('requirements_verification*.yaml'))
                assert len(report_files) > 0, "Should create requirements_verification YAML"
                
                report_file = report_files[0]
                
                # VERIFY: File contains actual data
                with open(report_file) as f:
                    report_data = yaml.safe_load(f)
                
                assert report_data is not None, "Report should contain YAML data"
                assert report_data.get('layer_metadata', {}).get('requirement_id') == 'LAYER-TEST-01'
                assert report_data.get('test_verification', {}).get('total_tests') == 5
                assert 'AC-001' in str(report_data.get('acceptance_criteria_verification', {}))
