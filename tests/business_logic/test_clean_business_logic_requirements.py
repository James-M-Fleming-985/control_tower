"""
Business Logic Requirements Tests - Clean Implementation
======================================================

Failing tests for LAYER-003-01-03-002 Business Logic Layer requirements
covering REAL TDD phase enforcement and compliance validation.

Based on: LAYER-003-01-03-002_business_logic_requirements.md
"""

import pytest
import tempfile
import time
from unittest.mock import Mock, patch
from pathlib import Path

from src.business_logic.tdd_cycle_enforcer import TDDCycleEnforcer, PhaseType, EnforcementDecision
from src.business_logic.phase_enforcement import (
    RedPhaseEnforcer, 
    GreenPhaseEnforcer, 
    RefactorPhaseEnforcer,
    PhaseEnforcementResult,
    PhaseValidationResult
)
from src.business_logic.stage_gate_manager import (
    StageGateManager,
    StageGateDecision,
    StageGateStatus
)


class TestREDPhaseEnforcement:
    """
    REQUIREMENT: REAL RED phase enforcement with test failure validation
    """
    
    def setup_method(self):
        self.repository = Mock()
        self.git_manager = Mock()
        self.enforcer = RedPhaseEnforcer(min_coverage=0.75, min_quality=0.75)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_red_phase_requires_failing_tests(self):
        """
        RED phase must validate that tests exist AND are failing
        EXPECTED: Should fail when no tests exist or all tests pass
        """
        # Test with no tests
        result = self.enforcer.enforce_red_phase(self.temp_dir, {})
        assert result.validation_result == PhaseValidationResult.FAIL
        assert any("failing test" in issue.lower() for issue in result.blocking_issues)
        
        # Test with passing tests (invalid for RED phase)
        evidence = {
            "test_files": ["test_example.py"],
            "test_results": {"test_example.py": True}  # Passing test
        }
        result = self.enforcer.enforce_red_phase(self.temp_dir, evidence)
        assert result.validation_result == PhaseValidationResult.FAIL
        assert any("failing" in issue.lower() for issue in result.blocking_issues)
    
    def test_red_phase_blocks_premature_implementation(self):
        """
        RED phase must block when implementation exists before tests
        EXPECTED: Should warn or block if implementation code detected
        """
        evidence = {
            "test_files": [],
            "implementation_files": ["src/example.py"],  # Implementation without tests
            "implementation_size": 100  # Lines of implementation code
        }
        result = self.enforcer.enforce_red_phase(self.temp_dir, evidence)
        assert result.validation_result in [PhaseValidationResult.FAIL, PhaseValidationResult.WARNING]
        assert any("implementation" in issue.lower() for issue in result.blocking_issues + result.warnings)
    
    def test_red_phase_response_time_under_3_seconds(self):
        """
        PERFORMANCE REQUIREMENT: RED validation < 3 seconds
        """
        start_time = time.time()
        result = self.enforcer.enforce_red_phase(self.temp_dir, {"test_files": ["test1.py"]})
        end_time = time.time()
        
        assert (end_time - start_time) < 3.0, f"RED phase took {end_time - start_time:.2f} seconds, expected < 3.0"


class TestGREENPhaseEnforcement:
    """
    REQUIREMENT: REAL GREEN phase enforcement with minimal implementation validation
    """
    
    def setup_method(self):
        self.repository = Mock()
        self.git_manager = Mock()
        self.enforcer = GreenPhaseEnforcer(min_coverage=0.75, min_quality=0.75)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_green_phase_requires_passing_tests(self):
        """
        GREEN phase must validate that tests are now passing
        EXPECTED: Should fail when tests are still failing
        """
        evidence = {
            "test_files": ["test_example.py"],
            "test_results": {"test_example.py": False}  # Still failing
        }
        result = self.enforcer.enforce_green_phase(self.temp_dir, evidence)
        assert result.validation_result == PhaseValidationResult.FAIL
        assert any("passing" in issue.lower() for issue in result.blocking_issues)
    
    def test_green_phase_validates_minimal_implementation(self):
        """
        GREEN phase must ensure implementation is minimal (just enough to pass tests)
        EXPECTED: Should warn about over-implementation
        """
        evidence = {
            "test_files": ["test_example.py"],
            "test_results": {"test_example.py": True},
            "implementation_complexity": 10.0,  # High complexity = over-implementation
            "implementation_size": 500  # Large implementation
        }
        result = self.enforcer.enforce_green_phase(self.temp_dir, evidence)
        assert result.validation_result in [PhaseValidationResult.WARNING, PhaseValidationResult.FAIL]
        assert any("minimal" in issue.lower() or "over" in issue.lower() 
                  for issue in result.blocking_issues + result.warnings)
    
    def test_green_phase_prevents_feature_creep(self):
        """
        GREEN phase must prevent adding features beyond what tests require
        EXPECTED: Should detect and block feature creep
        """
        evidence = {
            "test_files": ["test_basic.py"],
            "test_results": {"test_basic.py": True},
            "implementation_features": ["basic_function", "extra_feature", "bonus_method"]  # Extra features
        }
        result = self.enforcer.enforce_green_phase(self.temp_dir, evidence)
        assert result.validation_result in [PhaseValidationResult.WARNING, PhaseValidationResult.FAIL]
        assert any("feature" in issue.lower() for issue in result.blocking_issues + result.warnings)
    
    def test_green_phase_response_time_under_5_seconds(self):
        """
        PERFORMANCE REQUIREMENT: GREEN validation < 5 seconds
        """
        start_time = time.time()
        result = self.enforcer.enforce_green_phase(self.temp_dir, {"test_files": ["test1.py"]})
        end_time = time.time()
        
        assert (end_time - start_time) < 5.0, f"GREEN phase took {end_time - start_time:.2f} seconds, expected < 5.0"


class TestREFACTORPhaseEnforcement:
    """
    REQUIREMENT: REAL REFACTOR phase enforcement with quality improvement validation
    """
    
    def setup_method(self):
        self.repository = Mock()
        self.git_manager = Mock()
        self.enforcer = RefactorPhaseEnforcer(min_coverage=0.75, min_quality=0.75)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_refactor_phase_validates_tests_still_pass(self):
        """
        REFACTOR phase must ensure all tests still pass after refactoring
        EXPECTED: Should fail if any tests are broken
        """
        evidence = {
            "test_files": ["test1.py", "test2.py"],
            "test_results": {"test1.py": True, "test2.py": False}  # One test broken
        }
        result = self.enforcer.enforce_refactor_phase(self.temp_dir, evidence)
        assert result.validation_result == PhaseValidationResult.FAIL
        assert any("test" in issue.lower() and "fail" in issue.lower() 
                  for issue in result.blocking_issues)
    
    def test_refactor_phase_validates_quality_improvement(self):
        """
        REFACTOR phase must validate that code quality has improved
        EXPECTED: Should fail if quality metrics haven't improved
        """
        evidence = {
            "test_files": ["test1.py"],
            "test_results": {"test1.py": True},
            "quality_before": {"complexity": 8.0, "maintainability": 5.0},
            "quality_after": {"complexity": 8.5, "maintainability": 4.5}  # Quality got worse
        }
        result = self.enforcer.enforce_refactor_phase(self.temp_dir, evidence)
        assert result.validation_result in [PhaseValidationResult.FAIL, PhaseValidationResult.WARNING]
        assert any("quality" in issue.lower() or "improve" in issue.lower() 
                  for issue in result.blocking_issues + result.warnings)
    
    def test_refactor_phase_prevents_new_functionality(self):
        """
        REFACTOR phase must not add new functionality
        EXPECTED: Should block if new features are detected
        """
        evidence = {
            "test_files": ["test1.py"],
            "test_results": {"test1.py": True},
            "functionality_before": ["func1", "func2"],
            "functionality_after": ["func1", "func2", "func3"]  # New functionality added
        }
        result = self.enforcer.enforce_refactor_phase(self.temp_dir, evidence)
        assert result.validation_result == PhaseValidationResult.FAIL
        assert any("new" in issue.lower() and "function" in issue.lower() 
                  for issue in result.blocking_issues)
    
    def test_refactor_phase_response_time_under_8_seconds(self):
        """
        PERFORMANCE REQUIREMENT: REFACTOR validation < 8 seconds
        """
        start_time = time.time()
        result = self.enforcer.enforce_refactor_phase(self.temp_dir, {"test_files": ["test1.py"]})
        end_time = time.time()
        
        assert (end_time - start_time) < 8.0, f"REFACTOR phase took {end_time - start_time:.2f} seconds, expected < 8.0"


class TestPhaseTransitionBlocking:
    """
    REQUIREMENT: REAL phase transition blocking with compliance evidence requirement
    """
    
    def setup_method(self):
        self.repository = Mock()
        self.git_manager = Mock()
        self.stage_gate = StageGateManager(compliance_threshold=0.8, risk_tolerance="MEDIUM")
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_red_to_green_transition_requires_failing_tests(self):
        """
        RED->GREEN transition must be blocked without failing tests
        EXPECTED: Stage gate should block transition
        """
        evidence = {
            "current_phase": PhaseType.RED,
            "target_phase": PhaseType.GREEN,
            "test_files": [],  # No tests
            "test_results": {}
        }
        decision = self.stage_gate.evaluate_stage_gate(self.temp_dir, evidence)
        assert decision.status == StageGateStatus.CLOSED
        assert len(decision.evidence.blocking_criteria) > 0
    
    def test_green_to_refactor_transition_requires_passing_tests(self):
        """
        GREEN->REFACTOR transition must be blocked without passing tests
        EXPECTED: Stage gate should block transition
        """
        evidence = {
            "current_phase": PhaseType.GREEN,
            "target_phase": PhaseType.REFACTOR,
            "test_files": ["test1.py"],
            "test_results": {"test1.py": False}  # Tests still failing
        }
        decision = self.stage_gate.evaluate_stage_gate(self.temp_dir, evidence)
        assert decision.status == StageGateStatus.CLOSED
        assert len(decision.evidence.blocking_criteria) > 0
    
    def test_successful_transition_with_compliance_evidence(self):
        """
        Transition should succeed when all compliance evidence is satisfied
        EXPECTED: Stage gate should allow transition
        """
        evidence = {
            "current_phase": PhaseType.RED,
            "target_phase": PhaseType.GREEN,
            "test_files": ["test1.py"],
            "test_results": {"test1.py": False},  # Failing test (good for RED phase)
            "implementation_files": ["src/impl.py"],
            "compliance_score": 0.95
        }
        decision = self.stage_gate.evaluate_stage_gate(self.temp_dir, evidence)
        assert decision.status in [StageGateStatus.OPEN, StageGateStatus.WARNING]


class TestThroughputPerformance:
    """
    PERFORMANCE REQUIREMENT: 20+ phase validations per minute
    """
    
    def setup_method(self):
        self.repository = Mock()
        self.git_manager = Mock()
        self.cycle_enforcer = TDDCycleEnforcer(self.repository, self.git_manager)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_throughput_20_validations_per_minute(self):
        """
        System must handle 20+ phase validations per minute
        EXPECTED: Should complete 20 validations in under 60 seconds
        """
        start_time = time.time()
        
        # Perform 20 validation operations
        for i in range(20):
            state = self.cycle_enforcer.get_current_state(self.temp_dir)
            self.cycle_enforcer.update_phase(PhaseType.RED, self.temp_dir)
            
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 60.0, f"20 validations took {duration:.2f} seconds, expected < 60.0"
        throughput = 20 / (duration / 60)  # validations per minute
        assert throughput >= 20.0, f"Throughput was {throughput:.2f}/min, expected >= 20.0/min"


class TestComplianceValidation:
    """
    Overall compliance and enforcement decision accuracy
    """
    
    def setup_method(self):
        self.repository = Mock()
        self.git_manager = Mock()
        self.cycle_enforcer = TDDCycleEnforcer(self.repository, self.git_manager)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_enforcement_decision_accuracy(self):
        """
        Enforcement decisions must be 100% accurate based on evidence
        EXPECTED: Correct decision for valid/invalid scenarios
        """
        # Valid RED phase scenario
        valid_evidence = {
            "test_files": ["test1.py"],
            "test_results": {"test1.py": False},  # Failing test (correct for RED)
            "implementation_files": []
        }
        result = self.cycle_enforcer.make_enforcement_decision(PhaseType.RED, valid_evidence)
        assert result.decision in [EnforcementDecision.APPROVE, EnforcementDecision.WARN]  # Should approve valid RED phase
        
        # Invalid RED phase scenario
        invalid_evidence = {
            "test_files": [],  # No tests (invalid for RED)
            "test_results": {},
            "implementation_files": ["src/impl.py"]  # Implementation without tests
        }
        result = self.cycle_enforcer.make_enforcement_decision(PhaseType.RED, invalid_evidence)
        assert result.decision == EnforcementDecision.BLOCK  # Should block invalid RED phase
    
    def test_evidence_requirement_completeness(self):
        """
        All phase transitions must collect complete evidence
        EXPECTED: Evidence should include all required fields
        """
        evidence = self.cycle_enforcer.collect_compliance_evidence(self.temp_dir, PhaseType.RED)
        
        # Evidence should include key fields for compliance validation
        required_fields = ["test_files", "test_results", "implementation_files", "compliance_score"]
        for field in required_fields:
            assert field in evidence, f"Missing required evidence field: {field}"