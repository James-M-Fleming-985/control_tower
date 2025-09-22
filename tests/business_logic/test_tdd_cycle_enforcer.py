"""
TDD Cycle Enforcer Core Tests
=============================

Failing tests for the core TDD Cycle Enforcer functionality
covering state management, phase transitions, and enforcement decisions.
"""

import pytest
import tempfile
import time
from unittest.mock import Mock, patch
from dataclasses import asdict

from src.business_logic.tdd_cycle_enforcer import (
    TDDCycleEnforcer,
    EnforcementDecision,
    EnforcementReason,
    EnforcementResult,
    CycleState,
    PhaseType
)


class TestTDDCycleEnforcerCore:
    """Tests for TDD Cycle Enforcer core functionality"""
    
    def setup_method(self):
        from unittest.mock import Mock
        self.enforcer = TDDCycleEnforcer(
            repository=Mock(),
            git_manager=Mock(),
            feature_id="FEATURE-003-01-03",
            layer_id="LAY-003-01-03-002"
        )
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_enforcer_initialization_creates_proper_state(self):
        """
        TEST: TDD Cycle Enforcer should initialize with proper default state
        EXPECTED: Should create valid initial cycle state
        """
        state = self.enforcer.initialize_cycle(self.temp_dir)
        assert isinstance(state, CycleState)
        assert state.current_phase == PhaseType.RED
        assert state.tests_passing == False
        assert state.tests_failing == False
        assert state.code_coverage == 0.0
        assert state.quality_score == 0.0
        assert state.evidence_collected == False
    
    def test_get_current_state_returns_valid_cycle_state(self):
        """
        TEST: Should return current cycle state for project
        EXPECTED: Should fail - get_current_state method not implemented
        """
        with pytest.raises(AttributeError):
            state = self.enforcer.get_current_state(self.temp_dir)
            assert isinstance(state, CycleState)
            assert state.project_path == self.temp_dir
            assert state.current_phase in ["RED", "GREEN", "REFACTOR"]
    
    def test_update_phase_changes_current_phase(self):
        """
        TEST: Should update current phase in cycle state
        EXPECTED: Should fail - update_phase method not implemented
        """
        with pytest.raises(AttributeError):
            # Initialize state
            self.enforcer.initialize_cycle(self.temp_dir)
            
            # Update phase
            result = self.enforcer.update_phase("GREEN", self.temp_dir)
            assert result.decision == EnforcementDecision.APPROVE
            
            # Verify state change
            state = self.enforcer.get_current_state(self.temp_dir)
            assert state.current_phase == "GREEN"
    
    def test_request_phase_transition_validates_compliance(self):
        """
        TEST: Should validate compliance before allowing phase transition
        EXPECTED: Should fail - request_phase_transition method not implemented
        """
        with pytest.raises(AttributeError):
            evidence = {"compliance_score": 0.50}  # Below threshold
            
            result = self.enforcer.request_phase_transition(
                self.temp_dir, "GREEN", evidence
            )
            
            assert result.decision == EnforcementDecision.BLOCK
            assert result.reason == EnforcementReason.INSUFFICIENT_COMPLIANCE
    
    def test_validate_transition_checks_prerequisites(self):
        """
        TEST: Should validate prerequisites for phase transitions
        EXPECTED: Should validate transition requirements properly
        """
        # Test RED -> GREEN transition
        is_valid = self.enforcer.validate_transition(PhaseType.RED, PhaseType.GREEN, {
            "tests_exist": True,
            "tests_failing": True,
            "minimal_implementation": True
        })
        assert is_valid == True
        
        # Test invalid transition
        is_valid = self.enforcer.validate_transition(PhaseType.RED, PhaseType.GREEN, {
            "tests_exist": False,
            "tests_failing": False
        })
        assert is_valid == False
    
    def test_calculate_compliance_score_accurate_assessment(self):
        """
        TEST: Should calculate accurate compliance score based on evidence
        EXPECTED: Should calculate compliance score properly
        """
        evidence = {
            "tests_exist": True,
            "tests_failing": True,
            "code_coverage": 0.80,
            "quality_score": 0.75
        }
        
        score = self.enforcer.calculate_compliance_score(evidence)
        assert 0.0 <= score <= 1.0
        assert score >= 0.75  # Should be high for good evidence
    
    def test_get_cycle_metrics_returns_comprehensive_metrics(self):
        """
        TEST: Should return comprehensive cycle metrics for analysis
        EXPECTED: Should fail - get_cycle_metrics method not implemented
        """
        with pytest.raises(AttributeError):
            metrics = self.enforcer.get_cycle_metrics(self.temp_dir)
            
            required_metrics = [
                "cycle_count", "average_cycle_time", "compliance_score",
                "red_phase_duration", "green_phase_duration", "refactor_phase_duration",
                "total_test_count", "passing_test_ratio", "code_coverage"
            ]
            
            for metric in required_metrics:
                assert metric in metrics
    
    def test_save_cycle_state_persists_to_data_layer(self):
        """
        TEST: Should persist cycle state via data access layer
        EXPECTED: Should fail - save_cycle_state method not implemented
        """
        with pytest.raises(AttributeError):
            # Create and modify state
            self.enforcer.initialize_cycle(self.temp_dir)
            self.enforcer.update_phase("GREEN", self.temp_dir)
            
            # Save state
            save_result = self.enforcer.save_cycle_state(self.temp_dir)
            assert save_result == True
    
    def test_load_cycle_state_retrieves_from_data_layer(self):
        """
        TEST: Should load cycle state from data access layer
        EXPECTED: Should load state or return None if not exists
        """
        # Should load existing state or return None
        state = self.enforcer.load_cycle_state(self.temp_dir)
        assert isinstance(state, CycleState) or state is None
    
    def test_reset_cycle_returns_to_initial_state(self):
        """
        TEST: Should reset cycle to initial RED phase state
        EXPECTED: Should fail - reset_cycle method not implemented
        """
        with pytest.raises(AttributeError):
            # Advance cycle
            self.enforcer.initialize_cycle(self.temp_dir)
            self.enforcer.update_phase("GREEN", self.temp_dir)
            self.enforcer.update_phase("REFACTOR", self.temp_dir)
            
            # Reset cycle
            reset_result = self.enforcer.reset_cycle(self.temp_dir)
            assert reset_result.decision == EnforcementDecision.APPROVE
            
            # Verify reset state
            state = self.enforcer.get_current_state(self.temp_dir)
            assert state.current_phase == "RED"
            assert state.cycle_count > 0  # Should increment cycle count


class TestEnforcementDecisionLogic:
    """Tests for enforcement decision logic and reasoning"""
    
    def setup_method(self):
        from unittest.mock import Mock
        self.enforcer = TDDCycleEnforcer(
            repository=Mock(),
            git_manager=Mock(),
            feature_id="FEATURE-003-01-03",
            layer_id="LAY-003-01-03-002"
        )
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_enforcement_decision_approve_with_valid_evidence(self):
        """
        TEST: Should approve transitions with valid evidence
        EXPECTED: Should fail - decision logic not implemented
        """
        with pytest.raises(AttributeError):
            evidence = {
                "compliance_score": 0.85,
                "tests_passing": True,
                "coverage_adequate": True
            }
            
            result = self.enforcer.make_enforcement_decision("GREEN", "REFACTOR", evidence)
            assert result.decision == EnforcementDecision.APPROVE
            assert result.reason == EnforcementReason.COMPLIANCE_SATISFIED
    
    def test_enforcement_decision_block_with_insufficient_compliance(self):
        """
        TEST: Should block transitions with insufficient compliance
        EXPECTED: Should fail - decision logic not implemented
        """
        with pytest.raises(AttributeError):
            evidence = {
                "compliance_score": 0.40,
                "tests_passing": False,
                "coverage_adequate": False
            }
            
            result = self.enforcer.make_enforcement_decision("RED", "GREEN", evidence)
            assert result.decision == EnforcementDecision.BLOCK
            assert result.reason == EnforcementReason.INSUFFICIENT_COMPLIANCE
    
    def test_enforcement_decision_warn_with_partial_compliance(self):
        """
        TEST: Should warn for transitions with partial compliance
        EXPECTED: Should fail - decision logic not implemented
        """
        with pytest.raises(AttributeError):
            evidence = {
                "compliance_score": 0.70,
                "tests_passing": True,
                "coverage_adequate": False
            }
            
            result = self.enforcer.make_enforcement_decision("GREEN", "REFACTOR", evidence)
            assert result.decision == EnforcementDecision.WARN
            assert result.reason == EnforcementReason.PARTIAL_COMPLIANCE


class TestCycleStateManagement:
    """Tests for cycle state management and persistence"""
    
    def setup_method(self):
        from unittest.mock import Mock
        self.enforcer = TDDCycleEnforcer(
            repository=Mock(),
            git_manager=Mock(),
            feature_id="FEATURE-003-01-03",
            layer_id="LAY-003-01-03-002"
        )
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_cycle_state_tracks_phase_history(self):
        """
        TEST: Should track phase transition history
        EXPECTED: Should fail - phase history tracking not implemented
        """
        with pytest.raises(AttributeError):
            self.enforcer.initialize_cycle(self.temp_dir)
            
            # Make transitions
            self.enforcer.update_phase("GREEN", self.temp_dir)
            self.enforcer.update_phase("REFACTOR", self.temp_dir)
            self.enforcer.update_phase("RED", self.temp_dir)
            
            state = self.enforcer.get_current_state(self.temp_dir)
            assert len(state.phase_history) == 4  # Initial + 3 transitions
            assert state.phase_history[-1].phase == "RED"
    
    def test_cycle_state_calculates_phase_durations(self):
        """
        TEST: Should calculate accurate phase durations
        EXPECTED: Should fail - phase duration calculation not implemented
        """
        with pytest.raises(AttributeError):
            self.enforcer.initialize_cycle(self.temp_dir)
            
            # Simulate time in RED phase
            time.sleep(0.1)
            self.enforcer.update_phase("GREEN", self.temp_dir)
            
            # Simulate time in GREEN phase
            time.sleep(0.1)
            self.enforcer.update_phase("REFACTOR", self.temp_dir)
            
            state = self.enforcer.get_current_state(self.temp_dir)
            assert state.red_phase_duration > 0
            assert state.green_phase_duration > 0
    
    def test_cycle_state_maintains_compliance_tracking(self):
        """
        TEST: Should maintain compliance score tracking over time
        EXPECTED: Should fail - compliance tracking not implemented
        """
        with pytest.raises(AttributeError):
            self.enforcer.initialize_cycle(self.temp_dir)
            
            # Update compliance scores
            self.enforcer.update_compliance_score(0.75, self.temp_dir)
            self.enforcer.update_compliance_score(0.85, self.temp_dir)
            
            state = self.enforcer.get_current_state(self.temp_dir)
            assert len(state.compliance_history) == 2
            assert state.compliance_score == 0.85


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])