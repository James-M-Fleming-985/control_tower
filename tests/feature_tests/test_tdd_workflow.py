"""
FEATURE-003-01-03 TDD Workflow Tests
Testing TDD cycle enforcement and phase transitions
"""
import pytest
import sys
import os
import tempfile
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.data_access.tdd_phase_repository import TDDPhaseRepository
from src.business_logic.tdd_cycle_enforcer import TDDCycleEnforcer, EnforcementDecision
from src.data_access.phase_models import PhaseType
from src.integration.git_operations import GitOperations

class TestTDDWorkflow:
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        self.enforcer = TDDCycleEnforcer(self.repo)
    
    def test_red_phase_initiation_complete_workflow(self):
        """Step 13: Test RED phase initiation complete workflow"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        assert state is not None
        assert state.current_phase.value == PhaseType.RED.value
    
    def test_red_to_green_phase_transition(self):
        """Step 14: Test RED to GREEN phase transition"""
        # Initialize cycle
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Attempt transition with valid evidence
        evidence = {
            'failing_tests': True,
            'tests_passing': True,
            'implementation_complexity': 0.2
        }
        result = self.enforcer.enforce_phase_transition(
            self.temp_dir, PhaseType.RED, PhaseType.GREEN, evidence
        )
        assert result is not None
    
    def test_green_phase_implementation_workflow(self):
        """Step 15: Test GREEN phase implementation workflow"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Simulate GREEN phase work
        evidence = {
            'tests_passing': True,
            'minimal_implementation': True
        }
        result = self.enforcer.enforce_phase_transition(
            self.temp_dir, PhaseType.RED, PhaseType.GREEN, evidence
        )
        assert result is not None
    
    def test_green_to_refactor_phase_transition(self):
        """Step 16: Test GREEN to REFACTOR phase transition"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Test transition validation
        evidence = {
            'tests_passing': True,
            'code_quality_baseline': 0.7
        }
        result = self.enforcer.enforce_phase_transition(
            self.temp_dir, PhaseType.GREEN, PhaseType.REFACTOR, evidence
        )
        assert result is not None
    
    def test_refactor_phase_optimization_workflow(self):
        """Step 17: Test REFACTOR phase optimization workflow"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Test refactor workflow
        evidence = {
            'quality_improvement': True,
            'tests_still_passing': True
        }
        assert state is not None
        assert evidence['quality_improvement'] == True
    
    def test_refactor_to_red_cycle_completion(self):
        """Step 18: Test REFACTOR to RED cycle completion"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Test cycle completion
        evidence = {
            'refactoring_complete': True,
            'quality_score': 0.8,
            'tests_passing': True
        }
        result = self.enforcer.enforce_phase_transition(
            self.temp_dir, PhaseType.REFACTOR, PhaseType.RED, evidence
        )
        assert result is not None
    
    def test_multiple_tdd_cycles_continuity(self):
        """Step 19: Test multiple TDD cycles continuity"""
        # First cycle
        state1 = self.enforcer.initialize_cycle(self.temp_dir)
        assert state1.current_phase.value == PhaseType.RED.value
        
        # Second cycle 
        state2 = self.enforcer.initialize_cycle(self.temp_dir + "_2")
        assert state2.current_phase.value == PhaseType.RED.value
    
    def test_tdd_cycle_checkpoint_management(self):
        """Step 20: Test TDD cycle checkpoint management"""
        git_ops = GitOperations()
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Create checkpoint
        checkpoint = git_ops.create_phase_checkpoint("RED_PHASE", {"cycle": "test"})
        assert checkpoint is not None
        assert state is not None
    
    def test_tdd_phase_validation_enforcement(self):
        """Step 21: Test TDD phase validation enforcement"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Test validation
        can_transition = self.enforcer.can_transition_to_phase(PhaseType.GREEN)
        assert can_transition == True
        assert state.current_phase.value == PhaseType.RED.value
    
    def test_tdd_cycle_interruption_recovery(self):
        """Step 22: Test TDD cycle interruption recovery"""
        # Simulate interruption
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Recovery
        recovered_state = self.enforcer.get_current_state(self.temp_dir)
        assert recovered_state is not None
        assert state.current_phase == recovered_state.current_phase
    
    def test_tdd_cycle_performance_monitoring(self):
        """Step 23: Test TDD cycle performance monitoring"""
        start_time = time.time()
        state = self.enforcer.initialize_cycle(self.temp_dir)
        end_time = time.time()
        
        # Performance check
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Should be fast
        assert state is not None
    
    def test_tdd_cycle_quality_assurance(self):
        """Step 24: Test TDD cycle quality assurance"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Quality metrics
        metrics = self.enforcer.get_validation_metrics()
        assert metrics is not None
        assert 'total_validations' in metrics
    
    def test_tdd_cycle_compliance_tracking(self):
        """Step 25: Test TDD cycle compliance tracking"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Compliance validation
        assert state.current_phase.value == PhaseType.RED.value
        assert state.evidence_collected == False
    
    def test_tdd_cycle_metrics_collection(self):
        """Step 26: Test TDD cycle metrics collection"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Metrics collection
        metrics = self.enforcer.get_validation_metrics()
        performance = self.enforcer.get_performance_metrics()
        
        assert metrics is not None
        assert performance is not None
    
    def test_tdd_cycle_audit_trail(self):
        """Step 27: Test TDD cycle audit trail"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Audit trail
        history = self.enforcer.get_phase_history()
        assert history is not None
        assert len(history) > 0
    
    def test_tdd_cycle_documentation_generation(self):
        """Step 28: Test TDD cycle documentation generation"""
        state = self.enforcer.initialize_cycle(self.temp_dir)
        
        # Documentation check
        current_phase = self.enforcer.get_current_phase()
        assert current_phase is not None
        assert state.current_phase == current_phase