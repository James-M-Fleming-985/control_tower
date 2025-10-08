"""
Integration Tests for Environment Validation
Layer: LAYER-003-03-02-01

Tests integration with other layers and dependencies.
"""

import pytest
from src.layer.environment_validation import EnvironmentValidation

# REQ-LAYER-003-03-02-01

pytestmark = pytest.mark.integration


class TestEnvironmentValidationIntegration:
    """Integration tests for EnvironmentValidation."""

    def test_standalone_integration(self):
        """Test layer functions independently.
        
        This layer has no external dependencies, so integration
        test validates complete workflow execution.
        """
        # REQ-LAYER-003-03-02-01
        validator = EnvironmentValidation()
        
        # Execute complete validation workflow
        all_valid, report = validator.validate_all()
        
        # Verify report structure
        assert isinstance(report, dict), "Report should be a dictionary"
        assert 'python_version' in report, "Report should include Python version"
        assert 'virtual_environment' in report, "Report should include venv status"
        assert 'environment_variables' in report, "Report should include env vars"
        assert 'timestamp' in report, "Report should include timestamp"
        
        # Verify all validation methods were called
        assert 'python_version' in validator.validation_results
        assert 'virtual_environment' in validator.validation_results
        assert 'environment_variables' in validator.validation_results
        
        # Verify Python version check (should pass in Python 3.8+)
        assert report['python_version']['valid'] is True

        
