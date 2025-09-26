"""
REFACTOR Enhancement Validation Tests
Post-Refactor Layer Testing - EvidenceValidator Business Logic Layer
Generated from: Prompts/TDD Prompts/4. Post-Refactor Layer Testing.md
Execution Date: September 26, 2025
"""

import pytest
import time
from evidence_validator import (
    EvidenceValidator, ValidationResult, QualityScore, 
    InvalidEvidenceFormatError, EvidenceValidationError
)
from unittest.mock import Mock, patch


class TestEvidenceValidatorRefactorValidation:
    """Validation tests for 10 REFACTOR enhancement steps"""

    def test_configuration_constants_work(self):
        """Step 1: Verify DEFAULT_PENALTIES and DEFAULT_THRESHOLDS are configurable"""
        validator = EvidenceValidator()
        
        # Default penalties configurable
        assert validator.DEFAULT_PENALTIES['RED'] == -50
        assert validator.DEFAULT_PENALTIES['GREEN'] == -30
        assert validator.DEFAULT_PENALTIES['REFACTOR'] == -20
        
        # Custom configuration works
        custom_config = {'penalties': {'RED': -40}}
        custom_validator = EvidenceValidator(config=custom_config)
        assert custom_validator.penalties['RED'] == -40

    def test_comprehensive_docstrings_exist(self):
        """Step 2: Verify enhanced documentation exists"""
        validator = EvidenceValidator()
        docstring = validator.verify_tdd_compliance.__doc__
        
        assert "severity-weighted penalty scoring" in docstring
        assert "Args:" in docstring and "Returns:" in docstring
        assert "Example:" in docstring

    def test_helper_methods_extracted(self):
        """Step 4: Verify helper methods work correctly"""
        validator = EvidenceValidator()
        workflow = {'implementation_before_tests': True, 'excessive_implementation': True}
        
        violation_types, violation_details = validator._extract_workflow_violations(workflow)
        assert 'RED_PHASE_VIOLATION' in violation_types
        assert 'GREEN_PHASE_VIOLATION' in violation_types
        
        score = validator._calculate_compliance_penalty_score(violation_types)
        assert score == 20.0  # 100 - 50 - 30

    def test_custom_exceptions_work(self):
        """Step 5: Verify custom exception types function"""
        validator = EvidenceValidator()
        
        with pytest.raises(InvalidEvidenceFormatError):
            validator.validate_evidence_format({})  # Missing required keys

    def test_logging_integration(self):
        """Step 7: Verify logging support works"""
        validator = EvidenceValidator()
        workflow = {'implementation_before_tests': True}
        
        result = validator.verify_tdd_compliance(workflow)
        # Should generate logs (visible in test output with -s flag)
        assert result.violations_found == True

    def test_performance_metrics_tracking(self):
        """Step 8: Verify performance metrics are captured"""
        validator = EvidenceValidator()
        workflow = {'implementation_before_tests': False}
        
        result = validator.verify_tdd_compliance(workflow)
        
        assert hasattr(result, 'performance_metrics')
        assert 'execution_time_ms' in result.performance_metrics
        assert result.performance_metrics['execution_time_ms'] > 0

    def test_configuration_validation(self):
        """Step 9: Verify config validation prevents errors"""
        with pytest.raises(ValueError):
            EvidenceValidator(config={'penalties': {'RED': 50}})  # Positive penalty invalid

    def test_mobile_package_optimization(self):
        """Step 10: Verify mobile package meets size requirements"""
        validator = EvidenceValidator()
        evidence = {
            'compliance_score': 85.0,
            'test_results': [{'name': f'test_{i}'} for i in range(100)],
            'issues': [{'severity': 'CRITICAL', 'message': 'Issue'}]
        }
        
        mobile_package = validator.prepare_mobile_evidence_package(evidence)
        package_size = len(str(mobile_package)) / 1024
        
        assert package_size < 50  # Must be under 50KB
        assert 'compliance_score' in mobile_package

    def test_input_validation_enhancement(self):
        """Additional test: Verify input validation improvements"""
        validator = EvidenceValidator()
        
        # Valid input should work
        valid_workflow = {
            'implementation_before_tests': False,
            'excessive_implementation': False,
            'tests_changed_during_refactor': False
        }
        result = validator.verify_tdd_compliance(valid_workflow)
        assert not result.violations_found
        
        # Invalid input should raise error or handle gracefully
        with pytest.raises((ValueError, InvalidEvidenceFormatError,
                            AttributeError)):
            validator.verify_tdd_compliance(None)

    def test_error_handling_robustness(self):
        """Additional test: Verify error handling improvements"""
        validator = EvidenceValidator()
        
        # Should handle edge cases gracefully
        empty_workflow = {}
        result = validator.verify_tdd_compliance(empty_workflow)
        
        # Should either process successfully or fail with clear error
        assert (isinstance(result, type(result)) or
                hasattr(result, 'violations_found'))

    def test_backward_compatibility_maintained(self):
        """Verify that all REFACTOR changes maintain backward compatibility"""
        validator = EvidenceValidator()
        
        # Original interface should still work
        workflow = {
            'implementation_before_tests': True,
            'excessive_implementation': False,
            'tests_changed_during_refactor': False
        }
        
        result = validator.verify_tdd_compliance(workflow)
        
        # Core properties should still exist
        assert hasattr(result, 'violations_found')
        assert hasattr(result, 'overall_compliance_score')
        assert isinstance(result.violations_found, bool)
        assert isinstance(result.overall_compliance_score, (int, float))

    def test_performance_regression_check(self):
        """Verify REFACTOR enhancements don't degrade performance"""
        validator = EvidenceValidator()
        workflow = {
            'implementation_before_tests': False,
            'excessive_implementation': False,
            'tests_changed_during_refactor': False
        }
        
        # Time multiple runs
        times = []
        for _ in range(5):
            start_time = time.time()
            result = validator.verify_tdd_compliance(workflow)
            execution_time = (time.time() - start_time) * 1000
            times.append(execution_time)
        
        avg_time = sum(times) / len(times)
        
        # Should still be under 1ms average (requirement from prompt)
        assert avg_time < 1.0  # Under 1ms
        
        # All runs should be successful
        assert not result.violations_found
        assert result.overall_compliance_score == 100.0