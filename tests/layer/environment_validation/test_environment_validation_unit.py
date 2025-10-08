"""
Unit Tests for Environment Validation
Layer: LAYER-003-03-02-01

Tests validate Python environment meets TDD workflow requirements.
"""

import sys
from src.layer.environment_validation import EnvironmentValidation

# REQ-LAYER-003-03-02-01


class TestEnvironmentValidationUnit:
    """Unit tests for EnvironmentValidation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.validator = EnvironmentValidation()

    def test_validate_python_version_3_8(self):
        """
        AC-001: Validate Python version >= 3.8

        This test validates acceptance criterion AC-001.
        Verifies that Python version detection works correctly.
        """
        # REQ-AC-001

        # Act
        result = self.validator.validate_python_version_3_8()

        # Assert
        assert isinstance(result, bool), "Should return boolean"
        # Python 3.8+ is required for this codebase
        expected_msg = (
            f"Python version should be >= 3.8, "
            f"got {sys.version_info}"
        )
        assert result is True, expected_msg
        assert 'python_version' in self.validator.validation_results

    def test_detect_virtual_environment_activation(self):
        """
        AC-002: Detect virtual environment activation

        This test validates acceptance criterion AC-002.
        Verifies that virtual environment detection works.
        """
        # REQ-AC-002

        # Act
        result = self.validator.detect_virtual_environment_activation()

        # Assert
        assert isinstance(result, bool), "Should return boolean"
        # Result should be True (we're in a dev container/venv)
        # or False (running in system Python)
        assert 'virtual_environment' in self.validator.validation_results

    def test_validate_required_environment_variables(self):
        """
        AC-003: Validate required environment variables

        This test validates acceptance criterion AC-003.
        Verifies that environment variable validation works.
        """
        # REQ-AC-003

        # Act
        result = self.validator.validate_required_environment_variables()

        # Assert
        assert isinstance(result, bool), "Should return boolean"
        assert 'environment_variables' in self.validator.validation_results
        # HOME and USER should typically be set
        assert result is True, "Required env vars should be present"

    def test_get_validation_report(self):
        """Test comprehensive validation report generation."""
        # Arrange - run all validations first
        self.validator.validate_python_version_3_8()
        self.validator.detect_virtual_environment_activation()
        self.validator.validate_required_environment_variables()

        # Act
        report = self.validator.get_validation_report()

        # Assert
        assert isinstance(report, dict)
        assert 'python_version' in report
        assert 'virtual_environment' in report
        assert 'environment_variables' in report
        assert 'timestamp' in report

    def test_validate_all(self):
        """Test complete validation workflow."""
        # Act
        all_valid, report = self.validator.validate_all()

        # Assert
        assert isinstance(all_valid, bool)
        assert isinstance(report, dict)
        # Report should contain all validation sections
        assert 'python_version' in report
        assert 'virtual_environment' in report
        assert 'environment_variables' in report

        
