"""
TDD Models and Enums for Business Logic Layer
Contains all models for TDD compliance checking and enforcement
"""
from enum import Enum
from typing import List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


class TDDViolation(Enum):
    """Types of TDD violations"""
    IMPLEMENTATION_BEFORE_TESTS = "implementation_before_tests"
    SKIPPED_TESTS = "skipped_tests"
    LOW_COVERAGE = "low_coverage"
    INVALID_TRANSITION = "invalid_transition"
    TESTS_NOT_FAILING = "tests_not_failing"


class ComplianceLevel(Enum):
    """TDD compliance levels"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"


class TDDPhase(Enum):
    """TDD cycle phases"""
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"


class CycleStep(Enum):
    """TDD cycle steps"""
    WRITE_TEST = "write_test"
    RUN_TEST = "run_test"
    WRITE_CODE = "write_code"
    REFACTOR_CODE = "refactor_code"


@dataclass
class TestResult:
    """Individual test result"""
    name: str
    status: str
    execution_time: float = 0.0
    skip_reason: Optional[str] = None


@dataclass
class VerificationResult:
    """Verification result containing test data"""
    test_results: List[TestResult]
    coverage_percentage: float
    implementation_quality_score: float
    tdd_cycle_compliance: bool


@dataclass
class Violation:
    """TDD violation record"""
    violation_type: TDDViolation
    description: str
    severity: str = "HIGH"
    timestamp: Optional[datetime] = None


@dataclass
class ComplianceResult:
    """TDD compliance assessment result"""
    compliance_level: ComplianceLevel
    violations: List[Violation]
    should_allow_progression: bool
    assessment_score: float = 0.0


@dataclass
class ValidationResult:
    """Verification result validation"""
    is_valid: bool
    rejection_reasons: Optional[List[str]]
    allows_progression: bool
    validation_score: float = 0.0


@dataclass
class TransitionAttempt:
    """TDD phase transition attempt result"""
    transition_allowed: bool
    violation_reasons: List[str]
    current_phase: TDDPhase
    target_phase: TDDPhase