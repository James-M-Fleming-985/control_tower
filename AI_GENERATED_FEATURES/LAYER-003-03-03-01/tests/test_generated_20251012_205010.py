```python
import pytest
import unittest.mock
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Violation:
    type: str
    severity: str
    message: str
    location: str


class MockDetector:
    def detect_mock_usage(self, test_content: str, allows_mock: bool = False) -> List[Violation]:
        if not allows_mock and ('unittest.mock' in test_content or 'from unittest.mock import' in test_content or '@mock' in test_content or 'Mock()' in test_content):
            return [Violation(
                type='mock_usage',
                severity='error',
                message='Mock usage detected in test without explicit permission',
                location='test_file.py'
            )]
        return []


class PlaceholderDetector:
    def detect_placeholder_tests(self, test_content: str) -> List[Violation]:
        violations = []
        if 'assert True' in test_content:
            violations.append(Violation(
                type='placeholder_test',
                severity='error',
                message='Placeholder test detected: assert True',
                location='test_file.py'
            ))
        if 'pass' in test_content and 'def test_' in test_content:
            violations.append(Violation(
                type='placeholder_test',
                severity='error',
                message='Placeholder test detected: empty test with pass',
                location='test_file.py'
            ))
        return violations


class CoverageValidator:
    def validate_coverage(self, coverage_data: Dict[str, Any], threshold: float) -> List[Violation]:
        violations = []
        if coverage_data.get('total', 100) < threshold:
            violations.append(Violation(
                type='coverage_threshold',
                severity='error',
                message=f"Coverage {coverage_data.get('total')}% below threshold {threshold}%",
                location='coverage_report'
            ))
        return violations


class TeamSizeValidator:
    def validate_team_size(self, actual_team_size: int, expected_team_size: int) -> List[Violation]:
        violations = []
        if actual_team_size != expected_team_size:
            violations.append(Violation(
                type='team_size_mismatch',
                severity='warning',
                message=f"Team size mismatch: expected {expected_team_size}, got {actual_team_size}",
                location='team_config'
            ))
        return violations


class ViolationCategorizer:
    def categorize_violations(self, violations: List[Violation]) -> Dict[str, Dict[str, List[Violation]]]:
        categorized = {}
        for violation in violations:
            if violation.type not in categorized:
                categorized[violation.type] = {'error': [], 'warning': [], 'info': []}
            categorized[violation.type][violation.severity].append(violation)
        return categorized


class TestAC001DetectMockUsage:
    """Test AC-001: Detect mock usage in tests (unless requirement allows)"""

    def test_detects_mock_when_not_allowed(self):
        """Should detect mock usage when mocks are not allowed"""
        detector = MockDetector()
        test_content = "from unittest.mock import Mock\ndef test_something():\n    mock_obj = Mock()"
        violations = detector.detect_mock_usage(test_content, allows_mock=False)
        assert False, "Expected to detect mock usage violation"

    def test_allows_mock_when_permitted(self):
        """Should allow mock usage when explicitly permitted"""
        detector = MockDetector()
        test_content = "from unittest.mock import Mock\ndef test_something():\n    mock_obj = Mock()"
        violations = detector.detect_mock_usage(test_content, allows_mock=True)
        assert False, "Expected no violations when mocks are allowed"

    def test_detects_unittest_mock_import(self):
        """Should detect unittest.mock import"""
        detector = MockDetector()
        test_content = "import unittest.mock\ndef test_something():\n    pass"
        violations = detector.detect_mock_usage(test_content, allows_mock=False)
        assert False, "Expected to detect unittest.mock import"

    def test_detects_mock_decorator(self):
        """Should detect @mock decorator usage"""
        detector = MockDetector()
        test_content = "@mock.patch('module.function')\ndef test_something():\n    pass"
        violations = detector.detect_mock_usage(test_content, allows_mock=False)
        assert False, "Expected to detect @mock decorator"

    def test_no_violation_without_mock(self):
        """Should not detect violations when no mocks are used"""
        detector = MockDetector()
        test_content = "def test_something():\n    assert 1 + 1 == 2"
        violations = detector.detect_mock_usage(test_content, allows_mock=False)
        assert False, "Expected no violations for clean test"


class TestAC002DetectPlaceholderTests:
    """Test AC-002: Detect placeholder tests (assert True, pass)"""

    def test_detects_assert_true_placeholder(self):
        """Should detect assert True as placeholder"""
        detector = PlaceholderDetector()
        test_content = "def test_something():\n    assert True"
        violations = detector.detect_placeholder_tests(test_content)
        assert False, "Expected to detect assert True placeholder"

    def test_detects_pass_placeholder(self):
        """Should detect pass statement in test"""
        detector = PlaceholderDetector()
        test_content = "def test_something():\n    pass"
        violations = detector.detect_placeholder_tests(test_content)
        assert False, "Expected to detect pass placeholder"

    def test_multiple_placeholders_detected(self):
        """Should detect multiple placeholder patterns"""
        detector = PlaceholderDetector()
        test_content = "def test_one():\n    assert True\ndef test_two():\n    pass"
        violations = detector.detect_placeholder_tests(test_content)
        assert False, "Expected to detect multiple placeholders"

    def test_no_placeholder_in_real_test(self):
        """Should not flag real tests as placeholders"""
        detector = PlaceholderDetector()
        test_content = "def test_something():\n    result = 1 + 1\n    assert result == 2"
        violations = detector.detect_placeholder_tests(test_content)
        assert False, "Expected no violations for real test"

    def test_violation_contains_correct_type(self):
        """Should create violations with correct type"""
        detector = PlaceholderDetector()
        test_content = "def test_something():\n    assert True"
        violations = detector.detect_placeholder_tests(test_content)
        assert False, "Expected violation type to be 'placeholder_test'"


class TestAC003DetectCoverageBelowThreshold:
    """Test AC-003: Detect coverage below threshold violations"""

    def test_detects_coverage_below_threshold(self):
        """Should detect when coverage is below threshold"""
        validator = CoverageValidator()
        coverage_data = {'total': 75.0}
        violations = validator.validate_coverage(coverage_data, threshold=80.0)
        assert False, "Expected to detect coverage below threshold"

    def test_no_violation_when_coverage_meets_threshold(self):
        """Should not violate when coverage meets threshold"""
        validator = CoverageValidator()
        coverage_data = {'total': 85.0}
        violations = validator.validate_coverage(coverage_data, threshold=80.0)
        assert False, "Expected no violations when coverage meets threshold"

    def test_no_violation_when_coverage_exceeds_threshold(self):
        """Should not violate when coverage exceeds threshold"""
        validator = CoverageValidator()
        coverage_data = {'total': 95.0}
        violations = validator.validate_coverage(coverage_data, threshold=80.0)
        assert False, "Expected no violations when coverage exceeds threshold"

    def test_detects_zero_coverage(self):
        """Should detect zero coverage as violation"""
        validator = CoverageValidator()
        coverage_data = {'total': 0.0}
        violations = validator.validate_coverage(coverage_data, threshold=80.0)
        assert False, "Expected to detect zero coverage violation"

    def test_violation_message_includes_values(self):
        """Should include actual and threshold values in message"""
        validator = CoverageValidator()
        coverage_data = {'total': 60.0}
        violations = validator.validate_coverage(coverage_data, threshold=80.0)
        assert False, "Expected violation message to contain coverage values"


class TestAC004DetectTeamSizeMismatch:
    """Test AC-004: Detect team size mismatch violations"""

    def test_detects_team_size_too_small(self):
        """Should detect when team size is smaller than expected"""
        validator = TeamSizeValidator()
        violations = validator.validate_team_size(actual_team_size=3, expected_team_size=5)
        assert False, "Expected to detect team size too small"

    def test_detects_team_size_too_large(self):
        """Should detect when team size is larger than expected"""
        validator = TeamSizeValidator()
        violations = validator.validate_team_size(actual_team_size=7, expected_team_size=5)
        assert False, "Expected to detect team size too large"

    def test_no_violation_when_team_size_matches(self):
        """Should not violate when team size matches"""
        validator = TeamSizeValidator()
        violations = validator.validate_team_size(actual_team_size=5, expected_team_size=5)
        assert False, "Expected no violations when team size matches"

    def test_violation_severity_is_warning(self):
        """Should create warning severity for team size mismatch"""
        validator = TeamSizeValidator()
        violations = validator.validate_team_size(actual_team_size=3, expected_team_size=5)
        assert False, "Expected violation severity to be warning"

    def test_violation_includes_actual_and_expected(self):
        """Should include both actual and expected values in violation"""
        validator = TeamSizeValidator()
        violations = validator.validate_team_size(actual_team_size=3, expected_team_size=5)
        assert False, "Expected violation to contain actual and expected values"


class TestAC005CategorizeViolationsByTypeAndSeverity:
    """Test AC-005: Categorize violations by type and severity"""

    def test_categorizes_violations_by_type(self):
        """Should categorize violations by their type"""
        categorizer = ViolationCategorizer()
        violations = [
            Violation('mock_usage', 'error', 'msg1', 'loc1'),
            Violation('placeholder_test', 'error', 'msg2', 'loc2')
        ]
        result = categorizer.categorize_violations(violations)
        assert False, "Expected violations categorized by type"

    def test_categorizes_violations_by_severity(self):
        """Should categorize violations by severity within type"""
        categorizer = ViolationCategorizer()
        violations = [
            Violation('mock_usage', 'error', 'msg1', 'loc1'),
            Violation('mock_usage', 'warning', 'msg2', 'loc2')
        ]
        result = categorizer.categorize_violations(violations)
        assert False, "Expected violations categorized by severity"

    def test_handles_multiple_violation_types(self):
        """Should handle multiple different violation types"""
        categorizer = ViolationCategorizer()
        violations = [
            Violation('mock_usage', 'error', 'msg1', 'loc1'),
            Violation('placeholder_test', 'error', 'msg2', 'loc2'),
            Violation('coverage_threshold', 'error', 'msg3', 'loc3'),
            Violation('team_size_mismatch', 'warning', 'msg4', 'loc4')
        ]
        result = categorizer.categorize_violations(violations)
        assert False, "Expected all violation types categorized"

    def test_handles_empty_violations_list(self):
        """Should handle empty violations list"""
        categorizer = ViolationCategorizer()
        violations = []
        result = categorizer.categorize_violations(violations)
        assert False, "Expected empty categorization for no violations"

    def test_maintains_violation_objects(self):
        """Should maintain original violation objects in categorization"""
        categorizer = ViolationCategorizer()
        violation = Violation('mock_usage', 'error', 'test message', 'test.py')
        violations = [violation]
        result = categorizer.categorize_violations(violations)
        assert False, "Expected original violation objects preserved"


@pytest.mark.integration
class TestMockDetectionIntegration:
    """Integration test for mock detection across multiple components"""

    def test_mock_detection_with_categorization(self):
        """Should detect mocks and categorize violations"""
        detector = MockDetector()
        categorizer = ViolationCategorizer()
        test_content = "from unittest.mock import Mock\ndef test_something():\n    mock_obj = Mock()"
        violations = detector.detect_mock_usage(test_content, allows_mock=False)
        categorized = categorizer.categorize_violations(violations)
        assert False, "Expected mock violations to be detected and categorized"

    def test_multiple_detectors_with_categorization(self):
        """Should combine violations from multiple detectors"""
        mock_detector = MockDetector()
        placeholder_detector = PlaceholderDetector()
        categorizer = ViolationCategorizer()
        test_content = "from unittest.mock import Mock\ndef test_something():\n    assert True"
        mock_violations = mock_detector.detect_mock_usage(test_content, allows_mock=False)
        placeholder_violations = placeholder_detector.detect_placeholder_tests(test_content)
        all_violations = mock_violations + placeholder_violations
        categorized = categorizer.categorize_violations(all_violations)
        assert False, "Expected combined violations from multiple detectors"

    def test_detection_and_validation_pipeline(self):
        """Should run complete detection and validation pipeline"""
        mock_detector = MockDetector()
        placeholder_detector = PlaceholderDetector()
        coverage_validator = CoverageValidator()
        categorizer = ViolationCategorizer()
        test_content = "from unittest.mock import Mock"
        coverage_data = {'total': 50.0}
        violations = []
        violations.extend(mock_detector.detect_mock_usage(test_content, allows_mock=False))
        violations.extend(placeholder_detector.detect_placeholder_tests(test_content))
        violations.extend(coverage_validator.validate_coverage(coverage_data, threshold=80.0))
        categorized = categorizer.categorize_violations(violations)
        assert False, "Expected complete pipeline to process all violations"


@pytest.mark.integration
class TestCoverageAndTeamValidationIntegration:
    """Integration test for coverage and team size validation"""

    def test_combined_coverage_and_team_validation(self):
        """Should validate both coverage and team size together"""
        coverage_validator = CoverageValidator()
        team_validator = TeamSizeValidator()
        categorizer = ViolationCategorizer()
        coverage_data = {'total': 65.0}
        violations = []
        violations.extend(coverage_validator.validate_coverage(coverage_data, threshold=80.0))
        violations.extend(team_validator.validate_team_size(actual_team_size=3, expected_team_size=5))
        categorized = categorizer.categorize_violations(violations)
        assert False, "Expected combined coverage and team