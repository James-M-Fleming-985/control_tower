"""
Quality Models for Test Quality Scoring System
Contains all models for test quality assessment and enforcement
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class EnforcementAction(Enum):
    """Quality enforcement actions"""
    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK = "BLOCK"
    REJECT = "REJECT"


@dataclass
class QualityStandards:
    """Minimum quality standards for tests"""
    minimum_coverage: float
    minimum_assertion_count: int
    minimum_test_complexity: float
    maximum_test_duration: float
    required_documentation: bool
    minimum_acceptable_score: float = 80.0


@dataclass
class QualityScore:
    """Test quality scoring result"""
    overall_score: float
    meets_standards: bool
    violations: List[str]
    enforcement_action: str
    coverage_score: float = 0.0
    assertion_score: float = 0.0
    complexity_score: float = 0.0
    performance_score: float = 0.0
    documentation_score: float = 0.0


@dataclass
class BlockingCriteria:
    """Criteria for blocking low quality tests"""
    block_on_zero_assertions: bool
    block_on_low_coverage: bool
    block_on_missing_edge_cases: bool
    block_on_poor_naming: bool
    block_on_excessive_duration: bool


@dataclass
class TestQualityMetrics:
    """Comprehensive test quality metrics"""
    test_name: str
    assertion_count: int
    code_coverage: float
    edge_cases_covered: int
    execution_time: float
    naming_quality_score: float
    maintainability_score: float


@dataclass
class AssessmentResult:
    """Quality assessment result with blocking logic"""
    should_block: bool
    blocking_reasons: List[str]
    recommendation: str
    overall_quality_score: float = 0.0
    assessment_details: Optional[dict] = None