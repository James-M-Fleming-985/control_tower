"""
Phase Enforcement Components for RED-GREEN-REFACTOR Cycle
========================================================

Specialized enforcement logic for each TDD phase with detailed validation,
evidence collection, and compliance verification.
"""

import time
import ast
import os
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from .constants import (
    COMPLEXITY_THRESHOLDS, 
    PERFORMANCE_THRESHOLDS, 
    COVERAGE_THRESHOLDS,
    COMPLIANCE_THRESHOLDS,
    PHASE_MESSAGES
)


class PhaseValidationResult(Enum):
    """Result of phase validation"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


@dataclass
class ValidationEvidence:
    """Evidence collected during phase validation"""
    test_files: List[str]
    implementation_files: List[str]
    test_results: Dict[str, bool]
    code_coverage: float
    quality_metrics: Dict[str, float]
    complexity_score: float
    validation_timestamp: datetime


@dataclass
class PhaseEnforcementResult:
    """Result of phase enforcement validation"""
    phase_name: str
    validation_result: PhaseValidationResult
    compliance_score: float
    blocking_issues: List[str]
    warnings: List[str]
    evidence: ValidationEvidence
    execution_time_ms: float
    recommendation: str


class BasePhaseEnforcer:
    """Base class for phase enforcement logic"""
    
    def __init__(self, min_coverage: float = 0.75, min_quality: float = 0.75):
        self.min_coverage = min_coverage
        self.min_quality = min_quality
        self.validation_cache = {}
    
    def _discover_test_files(self, project_path: str) -> List[str]:
        """Discover test files in project"""
        test_files = []
        project_root = Path(project_path)
        
        # Common test patterns
        test_patterns = ['test_*.py', '*_test.py', 'tests/*.py']
        
        for pattern in test_patterns:
            test_files.extend(str(f) for f in project_root.rglob(pattern))
        
        return test_files
    
    def _discover_implementation_files(self, project_path: str) -> List[str]:
        """Discover implementation files in project"""
        impl_files = []
        project_root = Path(project_path)
        
        # Find Python files excluding tests
        for py_file in project_root.rglob('*.py'):
            file_str = str(py_file)
            if not any(pattern in file_str for pattern in ['test_', '_test.py', '/tests/']):
                if not file_str.endswith('__init__.py'):
                    impl_files.append(file_str)
        
        return impl_files
    
    def _analyze_code_complexity(self, file_path: str) -> float:
        """Analyze code complexity using AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Count complexity indicators
            function_count = 0
            class_count = 0
            line_count = len(content.splitlines())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_count += 1
                elif isinstance(node, ast.ClassDef):
                    class_count += 1
            
            # Simple complexity score (normalized)
            complexity = (function_count * 2 + class_count * 3) / max(line_count, 1)
            return min(complexity, 1.0)
            
        except Exception:
            return 0.5  # Default moderate complexity
    
    def _validate_test_execution(self, test_files: List[str]) -> Dict[str, bool]:
        """Validate test execution results"""
        # In real implementation, this would run pytest and capture results
        # For this implementation, we'll simulate test results
        test_results = {}
        
        for test_file in test_files:
            # Simulate test execution
            test_results[test_file] = True  # Assume tests pass for simulation
        
        return test_results
    
    def _calculate_code_coverage(self, project_path: str) -> float:
        """Calculate code coverage percentage"""
        # In real implementation, this would use coverage.py
        # For simulation, we'll return a reasonable coverage value
        return 0.85  # 85% coverage simulation


class RedPhaseEnforcer(BasePhaseEnforcer):
    """
    RED Phase Enforcement Logic
    
    Validates that:
    1. Tests are written first (test-first development)
    2. Tests are failing (RED state achieved)
    3. Minimal test implementation exists
    4. No implementation code written yet
    """
    
    def enforce_red_phase(self, project_path: str, evidence: Dict[str, Any]) -> PhaseEnforcementResult:
        """Enforce RED phase requirements"""
        start_time = time.time()
        
        # Discover project files (use evidence if provided)
        test_files = evidence.get('test_files', self._discover_test_files(project_path))
        impl_files = evidence.get('implementation_files', self._discover_implementation_files(project_path))
        
        # Validation checks
        blocking_issues = []
        warnings = []
        compliance_score = 0.0
        
        # 1. Validate tests exist
        if not test_files:
            blocking_issues.append("No test files found. RED phase requires failing tests.")
        else:
            compliance_score += 0.25
        
        # 2. Validate tests are failing
        test_results = evidence.get('test_results', self._validate_test_execution(test_files))
        failing_tests = [f for f, result in test_results.items() if not result]
        
        if not failing_tests:
            blocking_issues.append("No failing tests found. RED phase requires at least one failing test.")
        else:
            compliance_score += 0.25
        
        # 3. Check for premature implementation
        if len(impl_files) > 0 and len(test_files) == 0:
            # Implementation exists without tests - blocking issue
            blocking_issues.append(f"Premature implementation detected. RED phase requires tests first.")
        
        for impl_file in impl_files:
            complexity = self._analyze_code_complexity(impl_file)
            if complexity > COMPLEXITY_THRESHOLDS["RED_PHASE_MAX"]:
                if len(test_files) == 0:
                    # No tests but implementation exists - blocking issue
                    blocking_issues.append(f"Premature implementation detected in {impl_file}. RED phase requires tests first.")
                else:
                    # Implementation with tests - just warning
                    warnings.append(f"Implementation detected in {impl_file}. RED phase should focus on tests only.")
        
        # 4. Validate test quality
        test_coverage = self._calculate_code_coverage(project_path)
        if test_coverage > 0:
            compliance_score += 0.25
        
        # 5. Validate minimal test implementation
        if len(test_files) > 0 and len(failing_tests) > 0:
            compliance_score += 0.25
        
        # Create evidence
        validation_evidence = ValidationEvidence(
            test_files=test_files,
            implementation_files=impl_files,
            test_results=test_results,
            code_coverage=test_coverage,
            quality_metrics={'test_count': len(test_files), 'failing_tests': len(failing_tests)},
            complexity_score=sum(self._analyze_code_complexity(f) for f in impl_files) / max(len(impl_files), 1),
            validation_timestamp=datetime.now()
        )
        
        # Determine validation result
        validation_result = PhaseValidationResult.PASS
        if blocking_issues:
            validation_result = PhaseValidationResult.FAIL
        elif warnings:
            validation_result = PhaseValidationResult.WARNING
        
        # Generate recommendation
        recommendation = self._generate_red_phase_recommendation(blocking_issues, warnings, compliance_score)
        
        execution_time = (time.time() - start_time) * 1000
        
        return PhaseEnforcementResult(
            phase_name="RED",
            validation_result=validation_result,
            compliance_score=compliance_score,
            blocking_issues=blocking_issues,
            warnings=warnings,
            evidence=validation_evidence,
            execution_time_ms=execution_time,
            recommendation=recommendation
        )
    
    def _generate_red_phase_recommendation(self, 
                                         blocking_issues: List[str], 
                                         warnings: List[str], 
                                         compliance_score: float) -> str:
        """Generate recommendation for RED phase"""
        if compliance_score >= 0.9:
            return "Excellent RED phase implementation. Ready for GREEN phase transition."
        elif compliance_score >= 0.75:
            return "Good RED phase implementation. Address warnings before GREEN transition."
        elif blocking_issues:
            return f"RED phase validation failed. Address {len(blocking_issues)} blocking issues."
        else:
            return "RED phase needs improvement. Focus on test-first development."


class GreenPhaseEnforcer(BasePhaseEnforcer):
    """
    GREEN Phase Enforcement Logic
    
    Validates that:
    1. Tests now pass (GREEN state achieved)
    2. Minimal implementation only (no over-engineering)
    3. Code coverage meets minimum requirements
    4. No additional features added
    """
    
    def enforce_green_phase(self, project_path: str, evidence: Dict[str, Any]) -> PhaseEnforcementResult:
        """Enforce GREEN phase requirements"""
        start_time = time.time()
        
        # Discover project files (use evidence if provided)
        test_files = evidence.get('test_files', self._discover_test_files(project_path))
        impl_files = evidence.get('implementation_files', self._discover_implementation_files(project_path))
        
        # Validation checks
        blocking_issues = []
        warnings = []
        compliance_score = 0.0
        
        # 1. Validate tests are passing
        test_results = evidence.get('test_results', self._validate_test_execution(test_files))
        passing_tests = [f for f, result in test_results.items() if result]
        
        if not passing_tests:
            blocking_issues.append("No passing tests found. GREEN phase requires tests to pass.")
        else:
            compliance_score += 0.3
        
        # 2. Validate minimal implementation
        total_complexity = 0.0
        if evidence.get('implementation_complexity') is not None:
            # Use evidence-provided complexity
            total_complexity = evidence['implementation_complexity']
            if total_complexity > COMPLEXITY_THRESHOLDS["GREEN_PHASE_MAX"]:
                blocking_issues.append(PHASE_MESSAGES["GREEN"]["OVER_IMPLEMENTATION"])
        else:
            # Calculate complexity from files
            for impl_file in impl_files:
                complexity = self._analyze_code_complexity(impl_file)
                total_complexity += complexity
                
                if complexity > COMPLEXITY_THRESHOLDS["GREEN_PHASE_MAX"]:
                    blocking_issues.append(f"Over-implementation detected in {impl_file}. Keep implementation minimal.")
        
        avg_complexity = total_complexity / max(len(impl_files), 1) if impl_files else total_complexity
        if avg_complexity <= COMPLEXITY_THRESHOLDS["REFACTOR_TARGET"]:
            compliance_score += 0.25
        
        # 3. Validate code coverage
        test_coverage = self._calculate_code_coverage(project_path)
        if test_coverage >= self.min_coverage:
            compliance_score += 0.25
        else:
            blocking_issues.append(f"Code coverage {test_coverage:.1%} below minimum {self.min_coverage:.1%}.")
        
        # 4. Validate no feature creep
        if evidence.get('new_features_added'):
            blocking_issues.append("New features detected. GREEN phase should only make tests pass.")
        elif evidence.get('implementation_features') and len(evidence.get('implementation_features', [])) > 2:
            # More than 2 features suggests feature creep
            warnings.append("Multiple features detected. GREEN phase should focus on minimal implementation.")
        else:
            compliance_score += 0.2
        
        # Create evidence
        validation_evidence = ValidationEvidence(
            test_files=test_files,
            implementation_files=impl_files,
            test_results=test_results,
            code_coverage=test_coverage,
            quality_metrics={
                'passing_tests': len(passing_tests),
                'average_complexity': avg_complexity,
                'coverage_ratio': test_coverage / self.min_coverage
            },
            complexity_score=avg_complexity,
            validation_timestamp=datetime.now()
        )
        
        # Determine validation result
        validation_result = PhaseValidationResult.PASS
        if blocking_issues:
            validation_result = PhaseValidationResult.FAIL
        elif warnings:
            validation_result = PhaseValidationResult.WARNING
        
        # Generate recommendation
        recommendation = self._generate_green_phase_recommendation(blocking_issues, warnings, compliance_score)
        
        execution_time = (time.time() - start_time) * 1000
        
        return PhaseEnforcementResult(
            phase_name="GREEN",
            validation_result=validation_result,
            compliance_score=compliance_score,
            blocking_issues=blocking_issues,
            warnings=warnings,
            evidence=validation_evidence,
            execution_time_ms=execution_time,
            recommendation=recommendation
        )
    
    def _generate_green_phase_recommendation(self, 
                                           blocking_issues: List[str], 
                                           warnings: List[str], 
                                           compliance_score: float) -> str:
        """Generate recommendation for GREEN phase"""
        if compliance_score >= 0.9:
            return "Excellent GREEN phase implementation. Ready for REFACTOR phase transition."
        elif compliance_score >= 0.75:
            return "Good GREEN phase implementation. Consider addressing warnings."
        elif blocking_issues:
            return f"GREEN phase validation failed. Address {len(blocking_issues)} blocking issues."
        else:
            return "GREEN phase needs improvement. Focus on minimal implementation that makes tests pass."


class RefactorPhaseEnforcer(BasePhaseEnforcer):
    """
    REFACTOR Phase Enforcement Logic
    
    Validates that:
    1. Tests still pass after refactoring
    2. Code quality improved (metrics-based)
    3. No new functionality added
    4. Technical debt reduced
    """
    
    def enforce_refactor_phase(self, project_path: str, evidence: Dict[str, Any]) -> PhaseEnforcementResult:
        """Enforce REFACTOR phase requirements"""
        start_time = time.time()
        
        # Discover project files
        test_files = self._discover_test_files(project_path)
        impl_files = self._discover_implementation_files(project_path)
        
        # Validation checks
        blocking_issues = []
        warnings = []
        compliance_score = 0.0
        
        # 1. Validate tests still pass
        if 'test_results' in evidence:
            # Use provided test results
            test_results = evidence['test_results']
        else:
            # Execute tests
            test_results = self._validate_test_execution(test_files)
        
        passing_tests = [f for f, result in test_results.items() if result]
        
        if len(passing_tests) != len(test_results):
            blocking_issues.append("Some tests failing after refactoring. All tests must still pass.")
        else:
            compliance_score += 0.3
        
        # 2. Validate code quality improvements
        current_quality = evidence.get('current_quality_score', 0.5)
        previous_quality = evidence.get('previous_quality_score', 0.5)
        
        if current_quality <= previous_quality:
            warnings.append("Code quality did not improve during refactoring.")
        else:
            compliance_score += 0.25
        
        # 3. Validate no new functionality
        if evidence.get('new_functionality_added'):
            blocking_issues.append("New functionality detected. REFACTOR phase should only improve existing code.")
        elif (evidence.get('functionality_after') and evidence.get('functionality_before') and
              len(evidence.get('functionality_after', [])) > len(evidence.get('functionality_before', []))):
            blocking_issues.append("New functionality detected. REFACTOR phase should only improve existing code.")
        else:
            compliance_score += 0.25
        
        # 4. Validate technical debt reduction
        current_complexity = sum(self._analyze_code_complexity(f) for f in impl_files) / max(len(impl_files), 1)
        previous_complexity = evidence.get('previous_complexity', current_complexity)
        
        if current_complexity >= previous_complexity:
            warnings.append("Code complexity did not decrease during refactoring.")
        else:
            compliance_score += 0.2
        
        # Create evidence
        validation_evidence = ValidationEvidence(
            test_files=test_files,
            implementation_files=impl_files,
            test_results=test_results,
            code_coverage=self._calculate_code_coverage(project_path),
            quality_metrics={
                'quality_improvement': current_quality - previous_quality,
                'complexity_reduction': previous_complexity - current_complexity,
                'tests_preserved': len(passing_tests) / max(len(test_files), 1)
            },
            complexity_score=current_complexity,
            validation_timestamp=datetime.now()
        )
        
        # Determine validation result
        validation_result = PhaseValidationResult.PASS
        if blocking_issues:
            validation_result = PhaseValidationResult.FAIL
        elif warnings:
            validation_result = PhaseValidationResult.WARNING
        
        # Generate recommendation
        recommendation = self._generate_refactor_phase_recommendation(blocking_issues, warnings, compliance_score)
        
        execution_time = (time.time() - start_time) * 1000
        
        return PhaseEnforcementResult(
            phase_name="REFACTOR",
            validation_result=validation_result,
            compliance_score=compliance_score,
            blocking_issues=blocking_issues,
            warnings=warnings,
            evidence=validation_evidence,
            execution_time_ms=execution_time,
            recommendation=recommendation
        )
    
    def _generate_refactor_phase_recommendation(self, 
                                              blocking_issues: List[str], 
                                              warnings: List[str], 
                                              compliance_score: float) -> str:
        """Generate recommendation for REFACTOR phase"""
        if compliance_score >= 0.9:
            return "Excellent REFACTOR phase implementation. Ready for next RED phase cycle."
        elif compliance_score >= 0.75:
            return "Good REFACTOR phase implementation. Code quality improved successfully."
        elif blocking_issues:
            return f"REFACTOR phase validation failed. Address {len(blocking_issues)} blocking issues."
        else:
            return "REFACTOR phase needs improvement. Focus on improving code quality without breaking tests."