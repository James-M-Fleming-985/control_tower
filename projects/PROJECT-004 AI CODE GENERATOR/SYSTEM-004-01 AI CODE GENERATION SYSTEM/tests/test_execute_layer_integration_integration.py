"""
Integration Tests for Execute Layer Integration
Layer: LAYER-004-01-03-03

AUTO-GENERATED from acceptance criteria.
Tests follow TDD RED phase - they should FAIL initially.

Integration Test Coverage:
- AC-001: End-to-end integration with execute_layer.py
- AC-002: Backward compatibility validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import tempfile
import yaml


# Import will fail initially (RED phase)
try:
    from src.execute_layer_integration import ExecuteLayerIntegration
    from src.layer.orchestrator.ai_code_generator_orchestrator import AICodeGeneratorOrchestrator
except ImportError:
    ExecuteLayerIntegration = None
    AICodeGeneratorOrchestrator = None


class TestExecuteLayerIntegrationIntegration:
    """Integration tests for ExecuteLayerIntegration component."""
    
    @pytest.fixture
    def sample_layer_yaml(self, tmp_path):
        """Create a sample layer YAML file for testing."""
        yaml_content = {
            'metadata': {
                'requirement_id': 'LAYER-TEST-001',
                'requirement_name': 'Test Layer',
                'requirement_type': 'Layer'
            },
            'acceptance_criteria': [
                {
                    'criterion_id': 'AC-001',
                    'criterion': 'Test criterion',
                    'verification_method': 'unit_tests'
                }
            ]
        }
        
        yaml_file = tmp_path / "test_layer.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)
        
        return yaml_file
    
    def test_execute_layer_with_ai_generate_flag(self, sample_layer_yaml):
        """
        Test end-to-end execution with --ai-generate flag.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Complete workflow with AI generation enabled
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        mock_orchestrator = Mock(spec=AICodeGeneratorOrchestrator)
        mock_orchestrator.execute_full_cycle.return_value = {
            'status': 'success',
            'tests_passed': 10,
            'coverage': 0.95
        }
        
        # Act
        with patch.object(integration, '_create_orchestrator', return_value=mock_orchestrator):
            result = integration.execute_layer(
                yaml_file=str(sample_layer_yaml),
                ai_generate=True,
                phase='full-cycle'
            )
        
        # Assert
        assert result['status'] == 'success'
        assert result['ai_enabled'] is True
        mock_orchestrator.execute_full_cycle.assert_called_once()
    
    def test_execute_requirements_script_integration(self, tmp_path, sample_layer_yaml):
        """
        Test integration with execute_requirements.py script.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Can be called from execute_requirements.py
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Simulate CLI arguments from execute_requirements.py
        args = Mock()
        args.yaml_file = str(sample_layer_yaml)
        args.ai_generate = True
        args.phase = 'red'
        args.concurrent = False
        
        # Act
        result = integration.execute_from_cli_args(args)
        
        # Assert
        assert result is not None
        assert 'phase' in result
        # Phase may be normalized to uppercase by orchestrator
        assert result['phase'].lower() == 'red'
    
    def test_backward_compatibility_without_ai_flag(self, sample_layer_yaml):
        """
        Test that system works without --ai-generate flag (backward compatible).
        
        AC-002: Preserve backward compatibility for existing functionality
        Verifies: Original execute_layer behavior maintained
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Act - execute without AI flag
        result = integration.execute_layer(
            yaml_file=str(sample_layer_yaml),
            ai_generate=False,
            phase='red'
        )
        
        # Assert
        assert result is not None
        assert result.get('ai_enabled', False) is False
        assert 'fallback_mode' in result or 'manual_mode' in result
    
    def test_integration_with_existing_execute_layer(self, sample_layer_yaml):
        """
        Test integration with PROJECT-003's existing execute_layer.py.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Can wrap existing LayerExecutor class
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Create mock LayerExecutor (from PROJECT-003)
        mock_layer_executor = Mock()
        mock_layer_executor.layer_id = 'LAYER-TEST-001'
        mock_layer_executor.execute_red_phase = Mock(return_value={'status': 'tests_failed'})
        
        # Act
        wrapped_executor = integration.wrap_executor(mock_layer_executor)
        result = wrapped_executor.execute_red_phase()
        
        # Assert
        assert result['status'] == 'tests_failed'
        mock_layer_executor.execute_red_phase.assert_called_once()
    
    def test_ai_orchestrator_lifecycle_integration(self, sample_layer_yaml):
        """
        Test complete AI orchestrator lifecycle integration.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: RED -> GREEN -> REFACTOR phases with AI orchestrator
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Mock orchestrator with phase execution
        mock_orchestrator = Mock(spec=AICodeGeneratorOrchestrator)
        mock_orchestrator.execute_red_phase.return_value = {'tests': 'failing'}
        mock_orchestrator.execute_green_phase.return_value = {'tests': 'passing'}
        mock_orchestrator.execute_refactor_phase.return_value = {'tests': 'optimized'}
        
        # Act
        with patch.object(integration, '_create_orchestrator', return_value=mock_orchestrator):
            red_result = integration.execute_layer(
                yaml_file=str(sample_layer_yaml),
                ai_generate=True,
                phase='red'
            )
            
            green_result = integration.execute_layer(
                yaml_file=str(sample_layer_yaml),
                ai_generate=True,
                phase='green'
            )
            
            refactor_result = integration.execute_layer(
                yaml_file=str(sample_layer_yaml),
                ai_generate=True,
                phase='refactor'
            )
        
        # Assert
        assert mock_orchestrator.execute_red_phase.call_count >= 1
        assert mock_orchestrator.execute_green_phase.call_count >= 1
        assert mock_orchestrator.execute_refactor_phase.call_count >= 1
    
    def test_concurrent_execution_integration(self, sample_layer_yaml):
        """
        Test integration with concurrent layer executor.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Concurrent execution flag properly propagates
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        mock_orchestrator = Mock()
        mock_orchestrator.execute_full_cycle.return_value = {
            'status': 'success'
        }
        
        # Act
        with patch.object(integration, '_create_orchestrator', return_value=mock_orchestrator):
            result = integration.execute_layer(
                yaml_file=str(sample_layer_yaml),
                ai_generate=True,
                concurrent=True,
                max_concurrent=3
            )
        
        # Assert
        assert result.get('concurrent_enabled') is True
        # Concurrent configuration was passed during creation
        assert result.get('max_concurrent') == 3
