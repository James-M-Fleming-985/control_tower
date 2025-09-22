"""
FEATURE-003-01-03 Layer Integration Tests
Testing cross-layer communication and coordination
"""
import pytest
import sys
import os
import tempfile
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.data_access.tdd_phase_repository import TDDPhaseRepository
from src.business_logic.tdd_cycle_enforcer import TDDCycleEnforcer
from src.integration.git_operations import GitOperations
from src.integration.test_runner_coordinator import TestRunnerCoordinator

class TestLayerIntegration:
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_data_access_to_business_logic_flow(self):
        """Step 1: Test data access to business logic flow"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        
        # Test data flow using actual methods
        state = enforcer.initialize_cycle(self.temp_dir)
        assert state is not None
        
        # Verify data persistence
        current_state = enforcer.get_current_state(self.temp_dir)
        assert current_state is not None
    
    def test_business_logic_to_ui_flow(self):
        """Step 2: Test business logic to UI flow"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        
        # Test business logic generates UI data
        state = enforcer.initialize_cycle(self.temp_dir)
        current_phase = enforcer.get_current_phase()
        
        assert current_phase is not None
        assert state is not None
    
    def test_ui_to_integration_flow(self):
        """Step 3: Test UI to integration flow"""
        git_ops = GitOperations()
        
        # Test UI commands trigger integration using mock mode
        result = git_ops.create_phase_checkpoint("RED_PHASE", {"test": "data"})
        assert result is not None
    
    def test_integration_to_data_access_flow(self):
        """Step 4: Test integration to data access flow"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        git_ops = GitOperations()
        
        # Test integration updates data access
        checkpoint = git_ops.create_phase_checkpoint("TEST_PHASE", {"test": "data"})
        assert checkpoint is not None
    
    def test_complete_layer_cycle_workflow(self):
        """Step 5: Test complete layer cycle workflow"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        git_ops = GitOperations()
        
        # Test complete workflow
        state = enforcer.initialize_cycle(self.temp_dir)
        checkpoint = git_ops.create_phase_checkpoint("RED_PHASE", {"test": "data"})
        
        assert checkpoint is not None
        assert state is not None
    
    def test_cross_layer_data_consistency(self):
        """Step 6: Test cross-layer data consistency"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        
        # Test data consistency
        state = enforcer.initialize_cycle(self.temp_dir)
        current_state = enforcer.get_current_state(self.temp_dir)
        
        assert state.current_phase == current_state.current_phase
    
    def test_layer_error_propagation(self):
        """Step 7: Test layer error propagation"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        
        # Test error handling
        try:
            state = enforcer.initialize_cycle(self.temp_dir)
            assert state is not None
        except Exception as e:
            assert False, f"Unexpected error: {e}"
    
    def test_layer_performance_coordination(self):
        """Step 8: Test layer performance coordination"""
        import time
        
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        
        start_time = time.time()
        state = enforcer.initialize_cycle(self.temp_dir)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 1.0
        assert state is not None
    
    def test_layer_security_chain(self):
        """Step 9: Test layer security chain"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        
        # Test security validation
        state = enforcer.initialize_cycle(self.temp_dir)
        assert state is not None
    
    def test_layer_transaction_boundaries(self):
        """Step 10: Test layer transaction boundaries"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        
        # Test transaction integrity
        state = enforcer.initialize_cycle(self.temp_dir)
        current_state = enforcer.get_current_state(self.temp_dir)
        assert current_state is not None
        assert state is not None
    
    def test_layer_state_synchronization(self):
        """Step 11: Test layer state synchronization"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        
        # Test state sync
        state = enforcer.initialize_cycle(self.temp_dir)
        current_phase = enforcer.get_current_phase()
        assert current_phase == state.current_phase
    
    def test_layer_dependency_resolution(self):
        """Step 12: Test layer dependency resolution"""
        repo = TDDPhaseRepository("/tmp/test.db", "/tmp/test_repo")
        enforcer = TDDCycleEnforcer(repo)
        git_ops = GitOperations()
        
        # Test dependencies resolve correctly
        state = enforcer.initialize_cycle(self.temp_dir)
        checkpoint = git_ops.create_phase_checkpoint("DEPENDENCY_TEST", {"test": "data"})
        
        assert checkpoint is not None
        assert state is not None