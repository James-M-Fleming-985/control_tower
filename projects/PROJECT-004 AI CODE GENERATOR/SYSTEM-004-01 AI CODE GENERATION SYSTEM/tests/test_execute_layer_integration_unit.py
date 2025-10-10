"""
Unit Tests for Execute Layer Integration
Layer: LAYER-004-01-03-03

AUTO-GENERATED from acceptance criteria.
Tests follow TDD RED phase - they should FAIL initially.

Acceptance Criteria Coverage:
- AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
- AC-002: Preserve backward compatibility for existing functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys


# Import will fail initially (RED phase)
try:
    from src.execute_layer_integration import ExecuteLayerIntegration
except ImportError:
    ExecuteLayerIntegration = None


class TestExecuteLayerIntegrationUnit:
    """Unit tests for ExecuteLayerIntegration component."""
    
    def test_add_ai_generate_flag(self):
        """
        Test that AI generate flag can be added to CLI parser.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: CLI parser accepts --ai-generate flag
        """
        # Arrange
        mock_parser = Mock()
        integration = ExecuteLayerIntegration()
        
        # Act
        integration.add_ai_generate_flag(mock_parser)
        
        # Assert
        mock_parser.add_argument.assert_called_with(
            '--ai-generate',
            action='store_true',
            help='Enable AI-powered code generation'
        )
    
    def test_inject_ai_code_generator(self):
        """
        Test that AI code generator can be injected into execute_layer workflow.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: AI generator is properly initialized and injected
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        mock_executor = Mock()
        
        # Act
        result = integration.inject_ai_code_generator(mock_executor, ai_enabled=True)
        
        # Assert
        assert result is not None
        assert hasattr(result, 'ai_generator')
        assert result.ai_generator is not None
    
    def test_preserve_existing_validation_logic(self):
        """
        Test that existing validation logic is preserved when AI is disabled.
        
        AC-002: Preserve backward compatibility for existing functionality
        Verifies: Original validation flow unchanged when ai_enabled=False
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        mock_executor = Mock()
        mock_executor.validate = Mock(return_value=True)
        
        # Act
        result = integration.inject_ai_code_generator(mock_executor, ai_enabled=False)
        
        # Assert
        assert result is mock_executor  # Should return same executor instance
        # When ai_enabled=False, should not add ai_generator attribute
    
    def test_fallback_to_manual_generation(self):
        """
        Test that system falls back to manual generation on AI failure.
        
        AC-002: Preserve backward compatibility for existing functionality
        Verifies: Graceful degradation when AI generation fails
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        mock_ai_generator = Mock()
        mock_ai_generator.generate_code.side_effect = Exception("AI failure")
        
        # Act
        result = integration.execute_with_fallback(
            ai_generator=mock_ai_generator,
            manual_generator=Mock(return_value="manual_code"),
            yaml_spec={"test": "data"}
        )
        
        # Assert
        assert result == "manual_code"
    
    def test_execute_requirements_cli_parser(self):
        """
        Test that CLI parser correctly processes execute_requirements arguments.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: CLI args parsed with ai-generate flag
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        test_args = ['--yaml-file', 'test.yaml', '--ai-generate']
        
        # Act
        parser = integration.create_cli_parser()
        args = parser.parse_args(test_args)
        
        # Assert
        assert args.yaml_file == 'test.yaml'
        assert args.ai_generate is True
    
    def test_yaml_file_path_validation(self):
        """
        Test that YAML file path is validated before processing.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: File existence validation
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Act & Assert - non-existent file
        with pytest.raises(FileNotFoundError):
            integration.validate_yaml_path('/nonexistent/file.yaml')
        
    def test_concurrent_flag_handling(self):
        """
        Test that concurrent execution flag is properly handled.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Concurrent flag passed to executor
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Act
        config = integration.build_execution_config(
            ai_enabled=True,
            concurrent=True,
            max_workers=5
        )
        
        # Assert
        assert config['ai_enabled'] is True
        assert config['concurrent'] is True
        assert config['max_workers'] == 5
    
    def test_ai_provider_selection(self):
        """
        Test that AI provider can be selected via configuration.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Provider selection mechanism
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Act
        config = integration.build_execution_config(
            ai_enabled=True,
            ai_provider='openai'
        )
        
        # Assert
        assert config['ai_provider'] == 'openai'
    
    def test_initialization_with_defaults(self):
        """
        Test that ExecuteLayerIntegration initializes with sensible defaults.
        
        AC-002: Preserve backward compatibility for existing functionality
        Verifies: Default behavior matches existing system
        """
        # Arrange & Act
        integration = ExecuteLayerIntegration()
        
        # Assert
        assert integration is not None
        assert hasattr(integration, 'default_ai_enabled')
        assert integration.default_ai_enabled is False  # Backward compatible default
    
    def test_preserve_execute_layer_interface(self):
        """
        Test that original execute_layer interface is preserved.
        
        AC-002: Preserve backward compatibility for existing functionality
        Verifies: Can call execute_layer without AI flags
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        mock_layer_executor = Mock()
        
        # Act
        result = integration.wrap_executor(mock_layer_executor)
        
        # Assert
        assert hasattr(result, 'execute_red_phase')
        assert hasattr(result, 'execute_green_phase')
        assert hasattr(result, 'execute_refactor_phase')
    
    def test_error_handling_with_invalid_config(self):
        """
        Test error handling when invalid configuration provided.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Proper error handling and validation
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Act & Assert
        with pytest.raises(ValueError):
            integration.build_execution_config(
                ai_enabled=True,
                max_workers=-1  # Invalid value
            )
    
    def test_generate_integration_metadata(self):
        """
        Test that integration metadata is properly generated.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Metadata tracking for integration
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Act
        metadata = integration.generate_metadata(
            layer_id='LAYER-004-01-03-03',
            ai_enabled=True
        )
        
        # Assert
        assert metadata['layer_id'] == 'LAYER-004-01-03-03'
        assert metadata['ai_enabled'] is True
        assert 'timestamp' in metadata
        assert 'integration_version' in metadata
    
    def test_execute_layer_with_verification_phase(self):
        """
        Test execution with verification phase.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Verification phase supported
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Create temp YAML file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('metadata:\n  requirement_id: TEST-001\n')
            yaml_path = f.name
        
        try:
            # Act - verification phase should fall back to manual mode
            # since we're not mocking orchestrator
            result = integration.execute_layer(
                yaml_file=yaml_path,
                ai_generate=False,
                phase='verification'
            )
            
            # Assert
            assert result is not None
            assert result['manual_mode'] is True
        finally:
            import os
            os.unlink(yaml_path)
    
    def test_execute_layer_invalid_yaml(self):
        """
        Test error handling with invalid YAML file.
        
        AC-001: Integrate with PROJECT-003 execute_layer.py infrastructure
        Verifies: Proper error handling for invalid inputs
        """
        # Arrange
        integration = ExecuteLayerIntegration()
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            integration.execute_layer(
                yaml_file='/nonexistent/invalid.yaml',
                ai_generate=True
            )
