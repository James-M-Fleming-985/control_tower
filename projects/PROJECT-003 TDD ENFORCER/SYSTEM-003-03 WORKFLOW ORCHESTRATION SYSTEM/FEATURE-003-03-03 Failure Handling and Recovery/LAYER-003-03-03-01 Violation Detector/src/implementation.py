```python
import ast
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ViolationType(Enum):
    MOCK_USAGE = "mock_usage"
    PLACEHOLDER_TEST = "placeholder_test"
    COVERAGE_BELOW_THRESHOLD = "coverage_below_threshold"
    TEAM_SIZE_MISMATCH = "team_size_mismatch"


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Violation:
    type: ViolationType
    severity: Severity
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)


class ViolationDetector:
    def __init__(self):
        self.violations: List[Violation] = []
        
    def detect_mock_usage(self, code: str, file_path: str = None, allow_mocks: bool = False) -> List[Violation]:
        """Detect mock usage in test code."""
        violations = []
        
        if allow_mocks:
            return violations
            
        mock_patterns = [
            r'\bMock\(',
            r'\bMagicMock\(',
            r'\bpatch\(',
            r'@patch',
            r'\bmock\.',
            r'from\s+unittest\.mock\s+import',
            r'from\s+mock\s+import',
            r'import\s+mock',
            r'unittest\.mock',
        ]
        
        lines = code.split('\n')
        for line_num, line in enumerate(lines, start=1):
            for pattern in mock_patterns:
                if re.search(pattern, line):
                    violation = Violation(
                        type=ViolationType.MOCK_USAGE,
                        severity=Severity.HIGH,
                        message=f"Mock usage detected: {line.strip()}",
                        file_path=file_path,
                        line_number=line_num,
                        details={"line": line.strip()}
                    )
                    violations.append(violation)
                    break
                    
        return violations
    
    def detect_placeholder_tests(self, code: str, file_path: str = None) -> List[Violation]:
        """Detect placeholder tests (assert True, pass)."""
        violations = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return violations
            
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                is_placeholder = self._is_placeholder_test(node)
                if is_placeholder:
                    violation = Violation(
                        type=ViolationType.PLACEHOLDER_TEST,
                        severity=Severity.MEDIUM,
                        message=f"Placeholder test detected: {node.name}",
                        file_path=file_path,
                        line_number=node.lineno,
                        details={"test_name": node.name}
                    )
                    violations.append(violation)
                    
        return violations
    
    def _is_placeholder_test(self, node: ast.FunctionDef) -> bool:
        """Check if a test function is a placeholder."""
        if not node.body:
            return True
            
        for stmt in node.body:
            if isinstance(stmt, ast.Pass):
                return True
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if isinstance(stmt.value.value, str):
                    continue
                    
            elif isinstance(stmt, ast.Assert):
                if isinstance(stmt.test, ast.Constant):
                    if stmt.test.value is True:
                        return True
                elif isinstance(stmt.test, ast.NameConstant):
                    if stmt.test.value is True:
                        return True
                        
        has_real_assertion = False
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assert):
                if not self._is_trivial_assert(stmt):
                    has_real_assertion = True
                    break
            elif isinstance(stmt, ast.Call):
                if hasattr(stmt.func, 'attr') and 'assert' in stmt.func.attr.lower():
                    has_real_assertion = True
                    break
                    
        return not has_real_assertion
    
    def _is_trivial_assert(self, node: ast.Assert) -> bool:
        """Check if an assertion is trivial (assert True)."""
        if isinstance(node.test, ast.Constant):
            return node.test.value is True
        elif isinstance(node.test, ast.NameConstant):
            return node.test.value is True
        return False
    
    def detect_coverage_violations(self, coverage_data: Dict[str, Any], 
                                   threshold: float = 80.0,
                                   file_path: str = None) -> List[Violation]:
        """Detect coverage below threshold violations."""
        violations = []
        
        coverage_percentage = coverage_data.get('coverage', 0)
        
        if coverage_percentage < threshold:
            severity = self._get_coverage_severity(coverage_percentage, threshold)
            violation = Violation(
                type=ViolationType.COVERAGE_BELOW_THRESHOLD,
                severity=severity,
                message=f"Coverage {coverage_percentage}% is below threshold {threshold}%",
                file_path=file_path,
                details={
                    "coverage": coverage_percentage,
                    "threshold": threshold,
                    "gap": threshold - coverage_percentage
                }
            )
            violations.append(violation)
            
        return violations
    
    def _get_coverage_severity(self, coverage: float, threshold: float) -> Severity:
        """Determine severity based on coverage gap."""
        gap = threshold - coverage
        if gap >= 30:
            return Severity.CRITICAL
        elif gap >= 20:
            return Severity.HIGH
        elif gap >= 10:
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    def detect_team_size_violations(self, actual_size: int, 
                                   expected_size: int,
                                   file_path: str = None) -> List[Violation]:
        """Detect team size mismatch violations."""
        violations = []
        
        if actual_size != expected_size:
            severity = self._get_team_size_severity(actual_size, expected_size)
            violation = Violation(
                type=ViolationType.TEAM_SIZE_MISMATCH,
                severity=severity,
                message=f"Team size {actual_size} does not match expected {expected_size}",
                file_path=file_path,
                details={
                    "actual_size": actual_size,
                    "expected_size": expected_size,
                    "difference": abs(actual_size - expected_size)
                }
            )
            violations.append(violation)
            
        return violations
    
    def _get_team_size_severity(self, actual: int, expected: int) -> Severity:
        """Determine severity based on team size difference."""
        diff = abs(actual - expected)
        if diff >= 5:
            return Severity.CRITICAL
        elif diff >= 3:
            return Severity.HIGH
        elif diff >= 2:
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    def categorize_violations(self, violations: List[Violation]) -> Dict[str, List[Violation]]:
        """Categorize violations by type and severity."""
        categorized = {
            "by_type": {},
            "by_severity": {}
        }
        
        for violation in violations:
            violation_type = violation.type.value
            severity = violation.severity.value
            
            if violation_type not in categorized["by_type"]:
                categorized["by_type"][violation_type] = []
            categorized["by_type"][violation_type].append(violation)
            
            if severity not in categorized["by_severity"]:
                categorized["by_severity"][severity] = []
            categorized["by_severity"][severity].append(violation)
            
        return categorized
    
    def detect_all_violations(self, 
                             code: str = None,
                             file_path: str = None,
                             allow_mocks: bool = False,
                             coverage_data: Dict[str, Any] = None,
                             coverage_threshold: float = 80.0,
                             team_size_actual: int = None,
                             team_size_expected: int = None) -> List[Violation]:
        """Detect all types of violations."""
        all_violations = []
        
        if code:
            mock_violations = self.detect_mock_usage(code, file_path, allow_mocks)
            all_violations.extend(mock_violations)
            
            placeholder_violations = self.detect_placeholder_tests(code, file_path)
            all_violations.extend(placeholder_violations)
        
        if coverage_data:
            coverage_violations = self.detect_coverage_violations(
                coverage_data, coverage_threshold, file_path
            )
            all_violations.extend(coverage_violations)
        
        if team_size_actual is not None and team_size_expected is not None:
            team_violations = self.detect_team_size_violations(
                team_size_actual, team_size_expected, file_path
            )
            all_violations.extend(team_violations)
        
        self.violations = all_violations
        return all_violations
    
    def get_violations_by_type(self, violation_type: ViolationType) -> List[Violation]:
        """Get violations filtered by type."""
        return [v for v in self.violations if v.type == violation_type]
    
    def get_violations_by_severity(self, severity: Severity) -> List[Violation]:
        """Get violations filtered by severity."""
        return [v for v in self.violations if v.severity == severity]
    
    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of all violations."""
        summary = {
            "total": len(self.violations),
            "by_type": {},
            "by_severity": {}
        }
        
        for violation in self.violations:
            violation_type = violation.type.value
            severity = violation.severity.value
            
            summary["by_type"][violation_type] = summary["by_type"].get(violation_type, 0) + 1
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
        return summary
```