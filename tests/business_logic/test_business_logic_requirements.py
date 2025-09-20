"""
Business Logic Layer Requirements Test Suite
===========================================

Comprehensive failing tests for LAY-003-01-03-002 Business Logic Layer
covering all functional, performance, and compliance requirements.
"""

import pytest
import time
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Dict, List, Any

# Import business logic components (these will fail initially)
from src.business_logic.tdd_cycle_enforcer import (
    TDDCycleEnforcer,
    EnforcementDecision,
    EnforcementReason,
    EnforcementResult,
    CycleState
)
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
    StageGateStatus,
    TransitionType
)


class TestBusinessLogicLayerRequirements:
    """Test suite for Business Logic Layer requirements compliance"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = self.temp_dir
        
        # Create mock test files
        self.test_files_dir = Path(self.temp_dir) / "tests"
        self.test_files_dir.mkdir(exist_ok=True)
        
        # Create mock implementation files
        self.src_dir = Path(self.temp_dir) / "src"
        self.src_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)


class TestREDPhaseEnforcementRequirements:
    """
    F1: RED Phase Enforcement Requirements
    Tests for REAL test-first development validation
    """
    
    def setup_method(self):
        self.enforcer = RedPhaseEnforcer()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_f1_1_red_phase_validates_tests_exist(self):
        """
        REQUIREMENT F1.1: RED phase must validate that tests exist
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with no test files
        project_path = self.temp_dir
        evidence = {}
        
        # ACT & ASSERT: Should validate and find issues
        result = self.enforcer.enforce_red_phase(project_path, evidence)
        assert result.validation_result == PhaseValidationResult.FAIL
        assert any("No test files found" in issue for issue in result.blocking_issues)
    
    def test_f1_2_red_phase_validates_tests_are_failing(self):
        """
        REQUIREMENT F1.2: RED phase must validate tests are failing
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with passing tests (invalid for RED phase)
        project_path = self.temp_dir
        evidence = {"test_results": {"test_example.py": True}}  # Passing test
        
        # ACT & ASSERT: Should validate and find issues
        result = self.enforcer.enforce_red_phase(project_path, evidence)
        assert result.validation_result == PhaseValidationResult.FAIL
        assert any("No failing tests found" in issue for issue in result.blocking_issues)
    
    def test_f1_3_red_phase_blocks_premature_implementation(self):
        """
        REQUIREMENT F1.3: RED phase must block premature implementation
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with complex implementation code
        project_path = self.temp_dir
        evidence = {"implementation_complexity": 0.8}  # High complexity
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_red_phase(project_path, evidence)

        
        assert "Implementation detected" in str(result.warnings)

    def test_f1_4_red_phase_enforces_test_first_development(self):
        """
        REQUIREMENT F1.4: RED phase must enforce test-first development
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with tests written after implementation
        project_path = self.temp_dir
        evidence = {"test_first_violation": True}
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_red_phase(project_path, evidence)

        
        assert result.compliance_score < 0.5

    def test_f1_5_red_phase_validates_minimal_test_implementation(self):
        """
        REQUIREMENT F1.5: RED phase must validate minimal test implementation
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with over-complex test setup
        project_path = self.temp_dir
        evidence = {"test_complexity": 0.9}
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_red_phase(project_path, evidence)

        
        assert result.compliance_score >= 0.75


class TestGREENPhaseEnforcementRequirements:
    """
    F2: GREEN Phase Enforcement Requirements  
    Tests for REAL minimal implementation validation
    """
    
    def setup_method(self):
        self.enforcer = GreenPhaseEnforcer()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_f2_1_green_phase_validates_tests_pass(self):
        """
        REQUIREMENT F2.1: GREEN phase must validate tests now pass
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with failing tests (invalid for GREEN phase)
        project_path = self.temp_dir
        evidence = {"test_results": {"test_example.py": False}}  # Failing test
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_green_phase(project_path, evidence)

        
        assert result.validation_result == PhaseValidationResult.FAIL

        
        assert any("No passing tests found" in issue for issue in result.blocking_issues)
    
    def test_f2_2_green_phase_validates_minimal_implementation(self):
        """
        REQUIREMENT F2.2: GREEN phase must validate minimal implementation only
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with over-engineered implementation
        project_path = self.temp_dir
        evidence = {"implementation_complexity": 0.8}  # Too complex
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_green_phase(project_path, evidence)

        
        assert "Over-implementation detected" in result.blocking_issues

        
        def test_f2_3_green_phase_validates_code_coverage(self):
        """
        REQUIREMENT F2.3: GREEN phase must validate adequate code coverage
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with insufficient code coverage
        project_path = self.temp_dir
        evidence = {"code_coverage": 0.60}  # Below 75% threshold
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_green_phase(project_path, evidence)

        
        assert "Code coverage" in str(result.blocking_issues)

        
        def test_f2_4_green_phase_prevents_feature_creep(self):
        """
        REQUIREMENT F2.4: GREEN phase must prevent feature creep
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with new features added
        project_path = self.temp_dir
        evidence = {"new_features_added": True}
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_green_phase(project_path, evidence)

        
        assert "New features detected" in result.blocking_issues

        
        class TestREFACTORPhaseEnforcementRequirements:
    """
    F3: REFACTOR Phase Enforcement Requirements
    Tests for REAL quality improvement validation
    """
    
    def setup_method(self):
        self.enforcer = RefactorPhaseEnforcer()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_f3_1_refactor_phase_validates_tests_still_pass(self):
        """
        REQUIREMENT F3.1: REFACTOR phase must validate tests still pass
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with broken tests after refactoring
        project_path = self.temp_dir
        evidence = {"test_results": {"test_example.py": False}}  # Broken test
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_refactor_phase(project_path, evidence)

        
        assert "Some tests failing after refactoring" in result.blocking_issues

        
        def test_f3_2_refactor_phase_validates_quality_improvement(self):
        """
        REQUIREMENT F3.2: REFACTOR phase must validate quality improved
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with no quality improvement
        project_path = self.temp_dir
        evidence = {
            "current_quality_score": 0.65,
            "previous_quality_score": 0.70  # Quality decreased
        }
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_refactor_phase(project_path, evidence)

        
        assert "Code quality did not improve" in result.warnings

        
        def test_f3_3_refactor_phase_prevents_new_functionality(self):
        """
        REQUIREMENT F3.3: REFACTOR phase must prevent new functionality
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with new functionality added
        project_path = self.temp_dir
        evidence = {"new_functionality_added": True}
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_refactor_phase(project_path, evidence)

        
        assert "New functionality detected" in result.blocking_issues

        
        def test_f3_4_refactor_phase_validates_technical_debt_reduction(self):
        """
        REQUIREMENT F3.4: REFACTOR phase must validate technical debt reduction
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with increased complexity
        project_path = self.temp_dir
        evidence = {
            "previous_complexity": 0.5,
            "current_complexity": 0.6  # Complexity increased
        }
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.enforcer.enforce_refactor_phase(project_path, evidence)

        
        assert "Code complexity did not decrease" in result.warnings

        
        class TestStageGateManagementRequirements:
    """
    F4: Stage Gate Management Requirements
    Tests for REAL transition blocking and compliance validation
    """
    
    def setup_method(self):
        self.stage_gate_manager = StageGateManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_f4_1_stage_gate_validates_transition_readiness(self):
        """
        REQUIREMENT F4.1: Stage gate must validate transition readiness
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Invalid transition request
        current_phase = "RED"
        target_phase = "GREEN"
        project_path = self.temp_dir
        evidence = {"compliance_score": 0.50}  # Below threshold
        
        # ACT & ASSERT: Should validate and find issues

        
        decision = self.stage_gate_manager.evaluate_stage_gate(

        
        current_phase, target_phase, project_path, evidence

        
        )
            assert decision.status == StageGateStatus.CLOSED
    
    def test_f4_2_stage_gate_blocks_invalid_transitions(self):
        """
        REQUIREMENT F4.2: Stage gate must block invalid transitions
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Transition with blocking issues
        current_phase = "GREEN"
        target_phase = "REFACTOR"
        project_path = self.temp_dir
        evidence = {"blocking_issues": ["Tests not passing", "Coverage too low"]}
        
        # ACT & ASSERT: Should validate and find issues

        
        decision = self.stage_gate_manager.evaluate_stage_gate(

        
        current_phase, target_phase, project_path, evidence

        
        )
            assert decision.status == StageGateStatus.CLOSED
            assert len(decision.evidence.blocking_criteria) > 0
    
    def test_f4_3_stage_gate_collects_compliance_evidence(self):
        """
        REQUIREMENT F4.3: Stage gate must collect compliance evidence
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Valid transition with evidence
        current_phase = "REFACTOR"
        target_phase = "RED"
        project_path = self.temp_dir
        evidence = {"quality_improvement": 0.15, "technical_debt_reduced": True}
        
        # ACT & ASSERT: Should validate and find issues

        
        decision = self.stage_gate_manager.evaluate_stage_gate(

        
        current_phase, target_phase, project_path, evidence

        
        )
            assert decision.evidence.compliance_evidence is not None
            assert "quality_improvement" in decision.evidence.compliance_evidence
    
    def test_f4_4_stage_gate_enforces_approval_criteria(self):
        """
        REQUIREMENT F4.4: Stage gate must enforce approval criteria
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Transition missing required approval criteria
        current_phase = "RED"
        target_phase = "GREEN"
        project_path = self.temp_dir
        evidence = {"tests_exist": False, "tests_failing": False}
        
        # ACT & ASSERT: Should validate and find issues

        
        decision = self.stage_gate_manager.evaluate_stage_gate(

        
        current_phase, target_phase, project_path, evidence

        
        )
            assert len(decision.evidence.approval_criteria_met) < len(decision.evidence.blocking_criteria)


class TestTDDCycleEnforcerRequirements:
    """
    F5: TDD Cycle Enforcer Core Requirements
    Tests for REAL cycle management and state validation
    """
    
    def setup_method(self):
        from unittest.mock import Mock
        self.cycle_enforcer = TDDCycleEnforcer(
            repository=Mock(),
            git_manager=Mock(),
            feature_id="FEATURE-003-01-03",
            layer_id="LAY-003-01-03-002"
        )
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_f5_1_tdd_cycle_enforcer_manages_phase_state(self):
        """
        REQUIREMENT F5.1: TDD Cycle Enforcer must manage phase state
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Initial cycle state
        project_path = self.temp_dir
        
        # ACT & ASSERT: Should validate and find issues

        
        current_state = self.cycle_enforcer.get_current_state(project_path)

        
        assert isinstance(current_state, CycleState)

        
        assert current_state.current_phase in ["RED", "GREEN", "REFACTOR"]
    
    def test_f5_2_tdd_cycle_enforcer_validates_phase_transitions(self):
        """
        REQUIREMENT F5.2: TDD Cycle Enforcer must validate phase transitions
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Invalid phase transition
        project_path = self.temp_dir
        target_phase = "GREEN"
        evidence = {"compliance_score": 0.40}  # Below threshold
        
        # ACT & ASSERT: Should validate and find issues

        
        result = self.cycle_enforcer.request_phase_transition(

        
        project_path, target_phase, evidence

        
        )
            assert result.decision == EnforcementDecision.BLOCK
    
    def test_f5_3_tdd_cycle_enforcer_tracks_cycle_metrics(self):
        """
        REQUIREMENT F5.3: TDD Cycle Enforcer must track cycle metrics
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Cycle with multiple phases
        project_path = self.temp_dir
        
        # ACT & ASSERT: Should validate and find issues

        
        metrics = self.cycle_enforcer.get_cycle_metrics(project_path)

        
        assert "cycle_count" in metrics

        
        assert "average_cycle_time" in metrics
            assert "compliance_score" in metrics
    
    def test_f5_4_tdd_cycle_enforcer_integrates_with_data_access(self):
        """
        REQUIREMENT F5.4: TDD Cycle Enforcer must integrate with data access layer
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Mock data access layer
        project_path = self.temp_dir
        
        # ACT & ASSERT: Should validate and find issues

        
        # Should use data access layer for persistence

        
        self.cycle_enforcer.save_cycle_state(project_path)

        
        loaded_state = self.cycle_enforcer.load_cycle_state(project_path)
            assert loaded_state is not None


class TestPerformanceRequirements:
    """
    NF1: Performance Requirements
    Tests for REAL performance targets and resource constraints
    """
    
    def setup_method(self):
        self.red_enforcer = RedPhaseEnforcer()
        self.green_enforcer = GreenPhaseEnforcer()
        self.refactor_enforcer = RefactorPhaseEnforcer()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_nf1_1_red_phase_response_time_under_3_seconds(self):
        """
        REQUIREMENT NF1.1: RED phase validation must complete in < 3 seconds
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Large project for performance testing
        project_path = self.temp_dir
        evidence = {"large_codebase": True}
        
        # ACT & ASSERT: Should validate and find issues

        
        start_time = time.time()

        
        result = self.red_enforcer.enforce_red_phase(project_path, evidence)

        
        execution_time = time.time() - start_time
            
            assert execution_time < 3.0
            assert result.execution_time_ms < 3000
    
    def test_nf1_2_green_phase_response_time_under_5_seconds(self):
        """
        REQUIREMENT NF1.2: GREEN phase validation must complete in < 5 seconds
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Large project for performance testing
        project_path = self.temp_dir
        evidence = {"large_codebase": True}
        
        # ACT & ASSERT: Should validate and find issues

        
        start_time = time.time()

        
        result = self.green_enforcer.enforce_green_phase(project_path, evidence)

        
        execution_time = time.time() - start_time
            
            assert execution_time < 5.0
            assert result.execution_time_ms < 5000
    
    def test_nf1_3_refactor_phase_response_time_under_8_seconds(self):
        """
        REQUIREMENT NF1.3: REFACTOR phase validation must complete in < 8 seconds
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Large project for performance testing
        project_path = self.temp_dir
        evidence = {"large_codebase": True}
        
        # ACT & ASSERT: Should validate and find issues

        
        start_time = time.time()

        
        result = self.refactor_enforcer.enforce_refactor_phase(project_path, evidence)

        
        execution_time = time.time() - start_time
            
            assert execution_time < 8.0
            assert result.execution_time_ms < 8000
    
    def test_nf1_4_throughput_20_validations_per_minute(self):
        """
        REQUIREMENT NF1.4: System must handle 20+ phase validations per minute
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Multiple validation requests
        project_path = self.temp_dir
        evidence = {}
        validation_count = 20
        
        # ACT & ASSERT: Should validate and find issues

        
        start_time = time.time()

        
        for i in range(validation_count):

        
        if i % 3 == 0:
                    self.red_enforcer.enforce_red_phase(project_path, evidence)
                elif i % 3 == 1:
                    self.green_enforcer.enforce_green_phase(project_path, evidence)
                else:
                    self.refactor_enforcer.enforce_refactor_phase(project_path, evidence)
            
            execution_time = time.time() - start_time
            validations_per_minute = (validation_count / execution_time) * 60
            
            assert validations_per_minute >= 20


class TestComplianceRequirements:
    """
    NF2: Compliance Requirements
    Tests for REAL TDD methodology compliance and enforcement accuracy
    """
    
    def setup_method(self):
        self.stage_gate_manager = StageGateManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_nf2_1_enforcement_decision_accuracy_100_percent(self):
        """
        REQUIREMENT NF2.1: Enforcement decisions must be 100% accurate
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Known valid and invalid scenarios
        test_scenarios = [
            ("RED", "GREEN", {"tests_failing": True, "compliance_score": 0.8}, StageGateStatus.OPEN),
            ("RED", "GREEN", {"tests_failing": False, "compliance_score": 0.8}, StageGateStatus.CLOSED),
            ("GREEN", "REFACTOR", {"tests_passing": True, "coverage": 0.8}, StageGateStatus.OPEN),
            ("GREEN", "REFACTOR", {"tests_passing": False, "coverage": 0.8}, StageGateStatus.CLOSED),
        ]
        
        # ACT & ASSERT: Should validate and find issues

        
        for current_phase, target_phase, evidence, expected_status in test_scenarios:

        
        decision = self.stage_gate_manager.evaluate_stage_gate(

        
        current_phase, target_phase, self.temp_dir, evidence
                )
                assert decision.status == expected_status, f"Incorrect decision for {current_phase} -> {target_phase}"
    
    def test_nf2_2_compliance_evidence_completeness(self):
        """
        REQUIREMENT NF2.2: Compliance evidence must be complete and verifiable
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Transition requiring evidence
        current_phase = "REFACTOR"
        target_phase = "RED"
        evidence = {"quality_improvement": 0.15}
        
        # ACT & ASSERT: Should validate and find issues

        
        decision = self.stage_gate_manager.evaluate_stage_gate(

        
        current_phase, target_phase, self.temp_dir, evidence

        
        )
            
            # Verify evidence completeness
            assert decision.evidence.phase_enforcement_result is not None
            assert decision.evidence.compliance_evidence is not None
            assert decision.evidence.quality_metrics is not None
            assert decision.evidence.performance_metrics is not None
            assert decision.evidence.risk_assessment is not None
    
    def test_nf2_3_tdd_methodology_enforcement(self):
        """
        REQUIREMENT NF2.3: Must enforce authentic TDD methodology
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Non-TDD workflow attempt
        current_phase = "RED"
        target_phase = "REFACTOR"  # Skipping GREEN phase
        evidence = {"skip_green_phase": True}
        
        # ACT & ASSERT: Should validate and find issues

        
        decision = self.stage_gate_manager.evaluate_stage_gate(

        
        current_phase, target_phase, self.temp_dir, evidence

        
        )
            
            # Should block invalid TDD sequence
            assert decision.status == StageGateStatus.CLOSED
            assert "Invalid TDD sequence" in str(decision.evidence.blocking_criteria)


class TestIntegrationRequirements:
    """
    NF3: Integration Requirements
    Tests for REAL data access layer coordination and external service integration
    """
    
    def setup_method(self):
        from unittest.mock import Mock
        self.cycle_enforcer = TDDCycleEnforcer(
            repository=Mock(),
            git_manager=Mock(),
            feature_id="FEATURE-003-01-03",
            layer_id="LAY-003-01-03-002"
        )
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_nf3_1_data_access_layer_coordination(self):
        """
        REQUIREMENT NF3.1: Must coordinate with data access layer for state persistence
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Cycle state changes requiring persistence
        project_path = self.temp_dir
        
        # ACT & ASSERT: Should validate and find issues

        
        # Should persist state via data access layer

        
        initial_state = self.cycle_enforcer.get_current_state(project_path)

        
        # Modify state
            self.cycle_enforcer.update_phase("GREEN", project_path)
            
            # Should persist changes
            updated_state = self.cycle_enforcer.get_current_state(project_path)
            assert updated_state.current_phase == "GREEN"
    
    def test_nf3_2_test_framework_integration(self):
        """
        REQUIREMENT NF3.2: Must integrate with test frameworks for real test execution
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with actual test files
        project_path = self.temp_dir
        
        # ACT & ASSERT: Should validate and find issues

        
        # Should execute real tests and get actual results

        
        test_results = self.cycle_enforcer.execute_tests(project_path)

        
        assert isinstance(test_results, dict)
            assert all(isinstance(result, bool) for result in test_results.values())
    
    def test_nf3_3_git_integration_for_code_analysis(self):
        """
        REQUIREMENT NF3.3: Must integrate with git for code change analysis
        EXPECTED: Should fail initially - no implementation
        """
        # ARRANGE: Project with git history
        project_path = self.temp_dir
        
        # ACT & ASSERT: Should validate and find issues

        
        # Should analyze git changes for phase validation

        
        changes = self.cycle_enforcer.analyze_git_changes(project_path)

        
        assert "files_changed" in changes
            assert "lines_added" in changes
            assert "lines_removed" in changes


if __name__ == "__main__":
    # Run the test suite to verify all tests fail initially
    pytest.main([__file__, "-v", "--tb=short"])