```python
import pytest
import sys
import os
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import List, Dict, Any
import tempfile
import shutil


class ViolationType:
    MOCK_USAGE = "mock_usage"
    PLACEHOLDER_TEST = "placeholder_test"
    COVERAGE_VIOLATION = "coverage_violation"
    TEAM_SIZE_MISMATCH = "team_size_mismatch"


class ViolationSeverity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Violation:
    def __init__(self, violation_type: str, severity: str, message: str, location: str = None):
        self.violation_type = violation_type
        self.severity = severity
        self.message = message
        self.location = location


class ViolationDetector:
    def __init__(self, threshold: float = 80.0):
        self.threshold = threshold
        self.violations: List[Violation] = []
    
    def detect_mock_usage(self, test_code: str, allows_mock: bool = False) -> List[Violation]:
        violations = []
        if not allows_mock:
            mock_keywords = ['Mock(', 'MagicMock(', 'patch(', '@patch', 'mock.']
            for keyword in mock_keywords:
                if keyword in test_code:
                    violations.append(Violation(
                        ViolationType.MOCK_USAGE,
                        ViolationSeverity.HIGH,
                        f"Mock usage detected: {keyword}",
                        "test_code"
                    ))
        return violations
    
    def detect_placeholder_tests(self, test_code: str) -> List[Violation]:
        violations = []
        placeholder_patterns = ['assert True', 'pass']
        for pattern in placeholder_patterns:
            if pattern in test_code:
                violations.append(Violation(
                    ViolationType.PLACEHOLDER_TEST,
                    ViolationSeverity.MEDIUM,
                    f"Placeholder test detected: {pattern}",
                    "test_code"
                ))
        return violations
    
    def detect_coverage_violations(self, coverage: float) -> List[Violation]:
        violations = []
        if coverage < self.threshold:
            violations.append(Violation(
                ViolationType.COVERAGE_VIOLATION,
                ViolationSeverity.CRITICAL,
                f"Coverage {coverage}% is below threshold {self.threshold}%",
                "coverage_report"
            ))
        return violations
    
    def detect_team_size_violations(self, actual_size: int, expected_size: int) -> List[Violation]:
        violations = []
        if actual_size != expected_size:
            violations.append(Violation(
                ViolationType.TEAM_SIZE_MISMATCH,
                ViolationSeverity.LOW,
                f"Team size {actual_size} does not match expected size {expected_size}",
                "team_config"
            ))
        return violations
    
    def categorize_violations(self, violations: List[Violation]) -> Dict[str, List[Violation]]:
        categorized = {}
        for violation in violations:
            key = f"{violation.violation_type}_{violation.severity}"
            if key not in categorized:
                categorized[key] = []
            categorized[key].append(violation)
        return categorized


class TestDetectMockUsageInTests:
    """AC-001: Detect mock usage in tests (unless requirement allows)"""
    
    def test_detect_mock_when_not_allowed(self):
        """Test that mock usage is detected when not allowed"""
        detector = ViolationDetector()
        test_code = """
        def test_something():
            mock_obj = Mock()
            assert mock_obj is not None
        """
        violations = detector.detect_mock_usage(test_code, allows_mock=False)
        assert False, "Should detect Mock usage"
    
    def test_detect_magicmock_when_not_allowed(self):
        """Test that MagicMock usage is detected when not allowed"""
        detector = ViolationDetector()
        test_code = """
        def test_something():
            magic = MagicMock()
            assert magic is not None
        """
        violations = detector.detect_mock_usage(test_code, allows_mock=False)
        assert False, "Should detect MagicMock usage"
    
    def test_detect_patch_decorator_when_not_allowed(self):
        """Test that @patch decorator is detected when not allowed"""
        detector = ViolationDetector()
        test_code = """
        @patch('module.function')
        def test_something(mock_func):
            pass
        """
        violations = detector.detect_mock_usage(test_code, allows_mock=False)
        assert False, "Should detect @patch decorator"
    
    def test_detect_patch_context_manager_when_not_allowed(self):
        """Test that patch() context manager is detected when not allowed"""
        detector = ViolationDetector()
        test_code = """
        def test_something():
            with patch('module.function'):
                pass
        """
        violations = detector.detect_mock_usage(test_code, allows_mock=False)
        assert False, "Should detect patch() context manager"
    
    def test_allow_mock_when_requirement_permits(self):
        """Test that mock usage is allowed when requirement permits"""
        detector = ViolationDetector()
        test_code = """
        def test_something():
            mock_obj = Mock()
            assert mock_obj is not None
        """
        violations = detector.detect_mock_usage(test_code, allows_mock=True)
        assert False, "Should allow mock when permits"
    
    def test_no_violation_when_no_mock_used(self):
        """Test that no violation is reported when no mock is used"""
        detector = ViolationDetector()
        test_code = """
        def test_something():
            result = 1 + 1
            assert result == 2
        """
        violations = detector.detect_mock_usage(test_code, allows_mock=False)
        assert False, "Should not detect mock when none used"


class TestDetectPlaceholderTests:
    """AC-002: Detect placeholder tests (assert True, pass)"""
    
    def test_detect_assert_true_placeholder(self):
        """Test that 'assert True' placeholder is detected"""
        detector = ViolationDetector()
        test_code = """
        def test_placeholder():
            assert True
        """
        violations = detector.detect_placeholder_tests(test_code)
        assert False, "Should detect 'assert True' placeholder"
    
    def test_detect_pass_placeholder(self):
        """Test that 'pass' placeholder is detected"""
        detector = ViolationDetector()
        test_code = """
        def test_placeholder():
            pass
        """
        violations = detector.detect_placeholder_tests(test_code)
        assert False, "Should detect 'pass' placeholder"
    
    def test_detect_multiple_placeholders(self):
        """Test that multiple placeholders are detected"""
        detector = ViolationDetector()
        test_code = """
        def test_placeholder1():
            assert True
        
        def test_placeholder2():
            pass
        """
        violations = detector.detect_placeholder_tests(test_code)
        assert False, "Should detect multiple placeholders"
    
    def test_no_violation_for_real_test(self):
        """Test that real tests are not flagged as placeholders"""
        detector = ViolationDetector()
        test_code = """
        def test_real():
            result = calculate(2, 3)
            assert result == 5
        """
        violations = detector.detect_placeholder_tests(test_code)
        assert False, "Should not detect real test as placeholder"


class TestDetectCoverageBelowThreshold:
    """AC-003: Detect coverage below threshold violations"""
    
    def test_detect_coverage_below_80_percent(self):
        """Test that coverage below 80% is detected"""
        detector = ViolationDetector(threshold=80.0)
        violations = detector.detect_coverage_violations(75.0)
        assert False, "Should detect coverage below 80%"
    
    def test_detect_coverage_below_custom_threshold(self):
        """Test that coverage below custom threshold is detected"""
        detector = ViolationDetector(threshold=90.0)
        violations = detector.detect_coverage_violations(85.0)
        assert False, "Should detect coverage below custom threshold"
    
    def test_no_violation_when_coverage_meets_threshold(self):
        """Test that no violation when coverage meets threshold"""
        detector = ViolationDetector(threshold=80.0)
        violations = detector.detect_coverage_violations(80.0)
        assert False, "Should not detect violation when coverage meets threshold"
    
    def test_no_violation_when_coverage_exceeds_threshold(self):
        """Test that no violation when coverage exceeds threshold"""
        detector = ViolationDetector(threshold=80.0)
        violations = detector.detect_coverage_violations(95.0)
        assert False, "Should not detect violation when coverage exceeds threshold"
    
    def test_detect_zero_coverage(self):
        """Test that zero coverage is detected"""
        detector = ViolationDetector(threshold=80.0)
        violations = detector.detect_coverage_violations(0.0)
        assert False, "Should detect zero coverage"


class TestDetectTeamSizeMismatch:
    """AC-004: Detect team size mismatch violations"""
    
    def test_detect_team_size_smaller_than_expected(self):
        """Test that team size smaller than expected is detected"""
        detector = ViolationDetector()
        violations = detector.detect_team_size_violations(actual_size=3, expected_size=5)
        assert False, "Should detect team size smaller than expected"
    
    def test_detect_team_size_larger_than_expected(self):
        """Test that team size larger than expected is detected"""
        detector = ViolationDetector()
        violations = detector.detect_team_size_violations(actual_size=7, expected_size=5)
        assert False, "Should detect team size larger than expected"
    
    def test_no_violation_when_team_size_matches(self):
        """Test that no violation when team size matches"""
        detector = ViolationDetector()
        violations = detector.detect_team_size_violations(actual_size=5, expected_size=5)
        assert False, "Should not detect violation when team size matches"
    
    def test_detect_zero_team_size(self):
        """Test that zero team size is detected"""
        detector = ViolationDetector()
        violations = detector.detect_team_size_violations(actual_size=0, expected_size=5)
        assert False, "Should detect zero team size"


class TestCategorizeViolations:
    """AC-005: Categorize violations by type and severity"""
    
    def test_categorize_single_violation(self):
        """Test categorization of a single violation"""
        detector = ViolationDetector()
        violations = [
            Violation(ViolationType.MOCK_USAGE, ViolationSeverity.HIGH, "Mock found")
        ]
        categorized = detector.categorize_violations(violations)
        assert False, "Should categorize single violation"
    
    def test_categorize_multiple_violations_same_type(self):
        """Test categorization of multiple violations of same type"""
        detector = ViolationDetector()
        violations = [
            Violation(ViolationType.MOCK_USAGE, ViolationSeverity.HIGH, "Mock 1"),
            Violation(ViolationType.MOCK_USAGE, ViolationSeverity.HIGH, "Mock 2")
        ]
        categorized = detector.categorize_violations(violations)
        assert False, "Should categorize multiple violations of same type"
    
    def test_categorize_multiple_violations_different_types(self):
        """Test categorization of multiple violations of different types"""
        detector = ViolationDetector()
        violations = [
            Violation(ViolationType.MOCK_USAGE, ViolationSeverity.HIGH, "Mock"),
            Violation(ViolationType.PLACEHOLDER_TEST, ViolationSeverity.MEDIUM, "Placeholder")
        ]
        categorized = detector.categorize_violations(violations)
        assert False, "Should categorize multiple violations of different types"
    
    def test_categorize_violations_by_severity(self):
        """Test categorization of violations by severity"""
        detector = ViolationDetector()
        violations = [
            Violation(ViolationType.MOCK_USAGE, ViolationSeverity.HIGH, "Mock high"),
            Violation(ViolationType.MOCK_USAGE, ViolationSeverity.LOW, "Mock low")
        ]
        categorized = detector.categorize_violations(violations)
        assert False, "Should categorize violations by severity"
    
    def test_categorize_empty_violations_list(self):
        """Test categorization of empty violations list"""
        detector = ViolationDetector()
        violations = []
        categorized = detector.categorize_violations(violations)
        assert False, "Should handle empty violations list"
    
    def test_categorize_all_violation_types(self):
        """Test categorization of all violation types"""
        detector = ViolationDetector()
        violations = [
            Violation(ViolationType.MOCK_USAGE, ViolationSeverity.HIGH, "Mock"),
            Violation(ViolationType.PLACEHOLDER_TEST, ViolationSeverity.MEDIUM, "Placeholder"),
            Violation(ViolationType.COVERAGE_VIOLATION, ViolationSeverity.CRITICAL, "Coverage"),
            Violation(ViolationType.TEAM_SIZE_MISMATCH, ViolationSeverity.LOW, "Team size")
        ]
        categorized = detector.categorize_violations(violations)
        assert False, "Should categorize all violation types"


@pytest.mark.integration
class TestIntegrationMockAndPlaceholderDetection:
    """Integration test for detecting both mock usage and placeholders"""
    
    def test_detect_both_mock_and_placeholder_in_same_file(self):
        """Test detection of both mock usage and placeholder in same file"""
        detector = ViolationDetector()
        test_code = """
        def test_with_mock():
            mock_obj = Mock()
            assert True
        """
        mock_violations = detector.detect_mock_usage(test_code, allows_mock=False)
        placeholder_violations = detector.detect_placeholder_tests(test_code)
        assert False, "Should detect both mock and placeholder violations"
    
    def test_categorize_mixed_violations(self):
        """Test categorization of mixed violation types"""
        detector = ViolationDetector()
        test_code = """
        def test_with_mock():
            mock_obj = Mock()
            pass
        """
        all_violations = []
        all_violations.extend(detector.detect_mock_usage(test_code, allows_mock=False))
        all_violations.extend(detector.detect_placeholder_tests(test_code))
        categorized = detector.categorize_violations(all_violations)
        assert False, "Should categorize mixed violations"


@pytest.mark.integration
class TestIntegrationCoverageAndTeamSizeDetection:
    """Integration test for detecting coverage and team size violations"""
    
    def test_detect_both_coverage_and_team_size_violations(self):
        """Test detection of both coverage and team size violations"""
        detector = ViolationDetector(threshold=80.0)
        coverage_violations = detector.detect_coverage_violations(70.0)
        team_violations = detector.detect_team_