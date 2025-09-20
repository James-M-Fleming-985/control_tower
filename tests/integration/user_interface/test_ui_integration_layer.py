"""
Integration tests for UI components with Integration Layer
Tests interaction between UI and integration components
"""

import pytest
from unittest.mock import Mock, patch
from src.user_interface.phase_display import TDDPhaseDisplay
from src.user_interface.enforcement_display import EnforcementStatusDisplay
from src.user_interface.progress_tracker import CycleProgressTracker
from src.user_interface.command_interface import InteractiveCommandInterface
from src.integration.git_operations import GitOperations
from src.integration.test_runner_coordinator import TestRunnerCoordinator


class TestUIIntegrationLayer:
    """Integration tests between UI and Integration Layer components"""
    
    def setup_method(self):
        """Setup for each test"""
        self.git_ops = GitOperations()
        self.test_coordinator = TestRunnerCoordinator()
        self.phase_display = TDDPhaseDisplay()
        self.enforcement_display = EnforcementStatusDisplay()
        
    def test_phase_display_with_git_operations(self):
        """Test phase display integration with git operations"""
        # Simulate git checkpoint creation
        result = self.git_ops.create_phase_checkpoint("RED", "Test RED phase checkpoint")
        
        # Display should update to show git operation result
        self.phase_display.show_red_phase()
        self.phase_display.display_test_results({"git_result": result})
        
        assert self.phase_display.current_phase == "RED"
        assert "git_result" in self.phase_display.last_results
        
    def test_enforcement_display_with_test_coordination(self):
        """Test enforcement display integration with test coordination"""
        # Simulate test execution
        test_result = self.test_coordinator.execute_red_phase_validation()
        
        # Enforcement display should show test results
        self.enforcement_display.show_enforcement_active()
        self.enforcement_display.update_metrics({"test_result": test_result})
        
        assert self.enforcement_display.enforcement_active is True
        assert "test_result" in self.enforcement_display.current_metrics
        
    def test_progress_tracker_with_integration_operations(self):
        """Test progress tracker with multiple integration operations"""
        # Start tracking integration operations
        self.progress_tracker = CycleProgressTracker()
        self.progress_tracker.start_cycle()
        
        # Simulate git and test operations
        self.git_ops.create_phase_checkpoint("GREEN")
        self.test_coordinator.capture_test_results()
        
        # Progress should advance
        self.progress_tracker.update_progress(50)
        self.progress_tracker.log_milestone("git_checkpoint_created")
        
        assert self.progress_tracker.current_progress == 50
        assert "git_checkpoint_created" in self.progress_tracker.milestones
        
    def test_command_interface_integration_workflow(self):
        """Test command interface with full integration workflow"""
        self.command_interface = InteractiveCommandInterface()
        
        # Register integration commands
        self.command_interface.register_command("git_checkpoint", 
                                               lambda: self.git_ops.create_phase_checkpoint("TEST"))
        self.command_interface.register_command("run_tests", 
                                               lambda: self.test_coordinator.execute_red_phase_validation())
        
        # Execute integration workflow
        git_result = self.command_interface.execute_command("git_checkpoint")
        test_result = self.command_interface.execute_command("run_tests")
        
        assert "success" in str(git_result)
        assert "success" in str(test_result)
        assert len(self.command_interface.get_command_history()) == 2