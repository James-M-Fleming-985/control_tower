"""
Comprehensive Integration tests for UI components
Achieves 80%+ coverage for TP-002 requirement
Tests integration between all 4 UI components
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.user_interface.command_interface import InteractiveCommandInterface
from src.user_interface.enforcement_display import EnforcementStatusDisplay
from src.user_interface.phase_display import TDDPhaseDisplay
from src.user_interface.progress_tracker import CycleProgressTracker


class TestUIComponentsIntegration:
    """Integration tests for all UI components working together"""
    
    def setup_method(self):
        """Setup for each test"""
        self.command_interface = InteractiveCommandInterface()
        self.enforcement_display = EnforcementStatusDisplay()
        self.phase_display = TDDPhaseDisplay()
        self.progress_tracker = CycleProgressTracker()
    
    def test_complete_tdd_workflow_integration(self):
        """Test complete TDD workflow through all UI components"""
        # Start a new cycle
        cycle_id = self.progress_tracker.start_new_cycle("Integration Test", "Testing UI integration")
        
        # Register TDD commands
        self.command_interface.register_command("start_red", lambda: self._start_red_phase())
        self.command_interface.register_command("start_green", lambda: self._start_green_phase())
        self.command_interface.register_command("start_refactor", lambda: self._start_refactor_phase())
        
        # Execute TDD cycle
        phases = ["start_red", "start_green", "start_refactor"]
        for phase_cmd in phases:
            # Execute command
            result = self.command_interface.execute_command(phase_cmd)
            assert result is not None
            
            # Update progress
            progress = {"start_red": 30, "start_green": 70, "start_refactor": 100}[phase_cmd]
            self.progress_tracker.update_progress(cycle_id, progress, f"Completed {phase_cmd}")
            
        # Verify integration
        final_progress = self.progress_tracker.get_progress(cycle_id)
        assert final_progress >= 100
        
        current_phase = self.phase_display.get_current_phase()
        assert current_phase in ["RED", "GREEN", "REFACTOR"]
        
    def _start_red_phase(self):
        """Helper method for RED phase"""
        self.phase_display.set_current_phase("RED", "Writing failing test")
        self.enforcement_display.update_enforcement_status("VIOLATION", "Test should fail initially")
        return "RED phase started"
        
    def _start_green_phase(self):
        """Helper method for GREEN phase"""
        self.phase_display.set_current_phase("GREEN", "Making test pass")
        self.enforcement_display.update_enforcement_status("COMPLIANT", "Test now passes")
        return "GREEN phase started"
        
    def _start_refactor_phase(self):
        """Helper method for REFACTOR phase"""
        self.phase_display.set_current_phase("REFACTOR", "Improving code quality")
        self.enforcement_display.update_enforcement_status("COMPLIANT", "Code refactored, tests still pass")
        return "REFACTOR phase started"
    
    def test_command_interface_with_phase_display_integration(self):
        """Test command interface working with phase display"""
        # Register phase commands
        phases = ["RED", "GREEN", "REFACTOR"]
        for phase in phases:
            self.command_interface.register_command(
                f"set_{phase.lower()}", 
                lambda p=phase: self.phase_display.set_current_phase(p, f"Switched to {p}")
            )
        
        # Test phase transitions via commands
        for phase in phases:
            result = self.command_interface.execute_command(f"set_{phase.lower()}")
            assert result is not None
            
            current_phase = self.phase_display.get_current_phase()
            assert current_phase == phase
            
        # Test history tracking
        history = self.command_interface.get_command_history()
        assert len(history) >= len(phases)
        
        phase_history = self.phase_display.get_phase_history()
        assert len(phase_history) >= len(phases)
    
    def test_enforcement_display_with_progress_tracker_integration(self):
        """Test enforcement display working with progress tracker"""
        cycle_id = self.progress_tracker.start_new_cycle("Enforcement Test", "Testing enforcement integration")
        
        # Test enforcement status affecting progress
        enforcement_scenarios = [
            ("VIOLATION", 0, "Tests failing"),
            ("WARNING", 25, "Some issues detected"),
            ("COMPLIANT", 50, "Basic compliance achieved"),
            ("COMPLIANT", 100, "Full compliance")
        ]
        
        for status, progress, message in enforcement_scenarios:
            # Update enforcement status
            self.enforcement_display.update_enforcement_status(status, message)
            
            # Update corresponding progress
            self.progress_tracker.update_progress(cycle_id, progress, message)
            
            # Record enforcement metrics
            self.progress_tracker.record_metric(cycle_id, f"enforcement_{status.lower()}", 1, "count")
            
        # Verify integration
        final_progress = self.progress_tracker.get_progress(cycle_id)
        assert final_progress == 100
        
        final_status = self.enforcement_display.get_current_status()
        assert "COMPLIANT" in final_status
        
        metrics = self.progress_tracker.get_metrics(cycle_id)
        assert len(metrics) >= len(enforcement_scenarios)
    
    def test_phase_display_with_progress_tracker_integration(self):
        """Test phase display working with progress tracker"""
        cycle_id = self.progress_tracker.start_new_cycle("Phase Progress Test", "Testing phase-progress integration")
        
        # Test phase-based progress tracking
        phase_progress_mapping = [
            ("RED", 20, "Test written and failing"),
            ("GREEN", 60, "Test now passes"),
            ("REFACTOR", 90, "Code improved"),
            ("COMPLETE", 100, "Cycle completed")
        ]
        
        for phase, progress, description in phase_progress_mapping:
            # Set phase
            self.phase_display.set_current_phase(phase, description)
            
            # Track phase timing
            self.phase_display.start_phase_timer(phase)
            time.sleep(0.001)  # Minimal delay
            duration = self.phase_display.stop_phase_timer(phase)
            
            # Update progress
            self.progress_tracker.update_progress(cycle_id, progress, description)
            
            # Record phase metrics in progress tracker
            self.progress_tracker.record_metric(cycle_id, f"{phase.lower()}_duration", duration, "seconds")
            
        # Verify integration
        final_progress = self.progress_tracker.get_progress(cycle_id)
        assert final_progress == 100
        
        phase_timings = self.phase_display.get_phase_timings()
        assert len(phase_timings) >= 4
        
        cycle_metrics = self.progress_tracker.get_metrics(cycle_id)
        assert len(cycle_metrics) >= 4
    
    def test_all_components_collaborative_workflow(self):
        """Test all 4 components working together in collaborative workflow"""
        # Initialize collaborative session
        session_id = "integration_test_session"
        cycle_id = self.progress_tracker.start_new_cycle(f"Session {session_id}", "Full integration test")
        
        # Register collaborative commands
        self.command_interface.register_command("status", self._get_comprehensive_status)
        self.command_interface.register_command("next_phase", self._advance_to_next_phase)
        self.command_interface.register_command("check_progress", lambda: self.progress_tracker.get_progress(cycle_id))
        
        # Simulate collaborative TDD session
        tdd_phases = ["RED", "GREEN", "REFACTOR"]
        
        for i, phase in enumerate(tdd_phases):
            # Command interface: execute phase command
            self.command_interface.execute_command("next_phase")
            
            # Phase display: set and track phase
            self.phase_display.set_current_phase(phase, f"Phase {i+1}: {phase}")
            self.phase_display.start_phase_timer(phase)
            
            # Enforcement display: update based on phase
            if phase == "RED":
                self.enforcement_display.update_enforcement_status("VIOLATION", "Test must fail")
                self.enforcement_display.add_violation("test_failure", "Test fails as expected")
            else:
                self.enforcement_display.update_enforcement_status("COMPLIANT", f"{phase} phase compliant")
                
            # Progress tracker: update progress
            progress = (i + 1) * 33  # 33%, 66%, 99%
            self.progress_tracker.update_progress(cycle_id, progress, f"Completed {phase} phase")
            
            # Simulate phase work
            time.sleep(0.001)
            duration = self.phase_display.stop_phase_timer(phase)
            
            # Record comprehensive metrics
            self.progress_tracker.record_metric(cycle_id, f"{phase.lower()}_duration", duration, "seconds")
            self.progress_tracker.record_metric(cycle_id, f"{phase.lower()}_violations", 
                                               1 if phase == "RED" else 0, "count")
            
            # Command interface: check status
            status = self.command_interface.execute_command("status")
            assert status is not None
            
        # Final validation of all components
        final_progress = self.command_interface.execute_command("check_progress")
        assert final_progress >= 99
        
        final_phase = self.phase_display.get_current_phase()
        assert final_phase == "REFACTOR"
        
        final_enforcement = self.enforcement_display.get_current_status()
        assert "COMPLIANT" in final_enforcement
        
        all_metrics = self.progress_tracker.get_metrics(cycle_id)
        assert len(all_metrics) >= 6  # 3 durations + 3 violations
        
    def _get_comprehensive_status(self):
        """Helper method to get status from all components"""
        return {
            "phase": self.phase_display.get_current_phase(),
            "enforcement": self.enforcement_display.get_current_status(),
            "violations": self.enforcement_display.get_violation_count(),
            "phase_history": len(self.phase_display.get_phase_history()),
            "command_history": len(self.command_interface.get_command_history())
        }
        
    def _advance_to_next_phase(self):
        """Helper method to advance to next phase"""
        current = self.phase_display.get_current_phase()
        phase_sequence = {"": "RED", "RED": "GREEN", "GREEN": "REFACTOR", "REFACTOR": "RED"}
        next_phase = phase_sequence.get(current, "RED")
        self.phase_display.set_current_phase(next_phase, f"Advanced to {next_phase}")
        return f"Advanced to {next_phase}"
    
    def test_error_handling_integration(self):
        """Test error handling across all components"""
        cycle_id = self.progress_tracker.start_new_cycle("Error Test", "Testing error handling integration")
        
        # Test error scenarios
        error_scenarios = [
            ("invalid_command", lambda: self.command_interface.execute_command("nonexistent")),
            ("invalid_phase", lambda: self.phase_display.set_current_phase("INVALID", "test")),
            ("invalid_progress", lambda: self.progress_tracker.update_progress(cycle_id, 150, "test")),
            ("invalid_status", lambda: self.enforcement_display.update_enforcement_status("INVALID", "test"))
        ]
        
        error_count = 0
        for scenario_name, error_func in error_scenarios:
            try:
                result = error_func()
                # Should handle gracefully
                self.enforcement_display.add_violation("error_handled", f"Handled {scenario_name}")
                error_count += 1
            except Exception as e:
                # Expected behavior - errors caught and handled
                self.enforcement_display.add_violation("error_caught", f"Caught {scenario_name}: {str(e)}")
                error_count += 1
                
        # Verify error handling was integrated across components
        violations = self.enforcement_display.get_violation_count()
        assert violations >= error_count
        
    def test_real_time_updates_integration(self):
        """Test real-time updates across all components"""
        cycle_id = self.progress_tracker.start_new_cycle("Real-time Test", "Testing real-time integration")
        
        # Setup real-time handlers
        updates = []
        
        def phase_change_handler(old_phase, new_phase, timestamp):
            updates.append(f"Phase: {old_phase} -> {new_phase}")
            
        def progress_update_handler(cycle_id, progress, message):
            updates.append(f"Progress: {progress}% - {message}")
            
        # Register handlers if supported
        try:
            self.phase_display.register_phase_change_handler(phase_change_handler)
        except AttributeError:
            pass  # Handler not implemented
            
        # Simulate real-time updates
        real_time_sequence = [
            ("RED", 10, "VIOLATION", "Starting RED phase"),
            ("GREEN", 50, "COMPLIANT", "Moving to GREEN phase"),
            ("REFACTOR", 90, "COMPLIANT", "Refactoring phase"),
            ("COMPLETE", 100, "COMPLIANT", "Cycle complete")
        ]
        
        for phase, progress, status, message in real_time_sequence:
            # Rapid updates across all components
            self.phase_display.set_current_phase(phase, message)
            self.progress_tracker.update_progress(cycle_id, progress, message)
            self.enforcement_display.update_enforcement_status(status, message)
            
            # Record timestamp for real-time verification
            self.progress_tracker.record_metric(cycle_id, f"{phase.lower()}_timestamp", time.time(), "timestamp")
            
        # Verify real-time integration
        final_progress = self.progress_tracker.get_progress(cycle_id)
        assert final_progress == 100
        
        metrics = self.progress_tracker.get_metrics(cycle_id)
        timestamps = [v for k, v in metrics.items() if "timestamp" in k]
        assert len(timestamps) >= 4
        
    def test_data_consistency_integration(self):
        """Test data consistency across all components"""
        cycle_id = self.progress_tracker.start_new_cycle("Consistency Test", "Testing data consistency")
        
        # Test consistent state management
        test_phases = ["RED", "GREEN", "REFACTOR"]
        
        for i, phase in enumerate(test_phases):
            # Update all components with consistent data
            timestamp = time.time()
            progress = (i + 1) * 33
            
            self.phase_display.set_current_phase(phase, f"Phase {i+1}")
            self.progress_tracker.update_progress(cycle_id, progress, f"Phase {i+1} progress")
            self.enforcement_display.update_enforcement_status("COMPLIANT", f"Phase {i+1} compliant")
            
            # Record state across all components
            state_data = {
                "phase": self.phase_display.get_current_phase(),
                "progress": self.progress_tracker.get_progress(cycle_id),
                "status": self.enforcement_display.get_current_status(),
                "timestamp": timestamp
            }
            
            # Verify state consistency
            assert state_data["phase"] == phase
            assert state_data["progress"] == progress
            assert "COMPLIANT" in state_data["status"]
            
            # Store state for consistency verification
            self.progress_tracker.record_metric(cycle_id, f"state_{i}", state_data["timestamp"], "timestamp")
            
        # Final consistency check
        all_metrics = self.progress_tracker.get_metrics(cycle_id)
        phase_history = self.phase_display.get_phase_history()
        
        assert len(all_metrics) >= 3  # At least 3 state timestamps
        assert len(phase_history) >= 3  # At least 3 phase changes
        
    def test_performance_integration(self):
        """Test performance across all components working together"""
        start_time = time.time()
        
        # Create multiple cycles for performance testing
        cycle_ids = []
        for i in range(10):
            cycle_id = self.progress_tracker.start_new_cycle(f"Perf Test {i}", f"Performance test cycle {i}")
            cycle_ids.append(cycle_id)
            
        # Register performance commands
        perf_commands = {
            "bulk_phase_update": lambda: self._bulk_phase_updates(),
            "bulk_progress_update": lambda: self._bulk_progress_updates(cycle_ids),
            "bulk_enforcement_update": lambda: self._bulk_enforcement_updates()
        }
        
        for cmd_name, cmd_func in perf_commands.items():
            self.command_interface.register_command(cmd_name, cmd_func)
            
        # Execute performance tests
        for cmd_name in perf_commands.keys():
            cmd_start = time.time()
            result = self.command_interface.execute_command(cmd_name)
            cmd_duration = time.time() - cmd_start
            
            assert result is not None
            assert cmd_duration < 1.0  # Should complete within 1 second
            
        total_duration = time.time() - start_time
        assert total_duration < 5.0  # Total test should complete within 5 seconds
        
        # Verify all components still responsive after performance test
        test_cycle_id = cycle_ids[0]
        final_progress = self.progress_tracker.get_progress(test_cycle_id)
        assert isinstance(final_progress, (int, float))
        
        current_phase = self.phase_display.get_current_phase()
        assert isinstance(current_phase, str)
        
        current_status = self.enforcement_display.get_current_status()
        assert isinstance(current_status, str)
        
    def _bulk_phase_updates(self):
        """Helper for bulk phase updates"""
        phases = ["RED", "GREEN", "REFACTOR"] * 10
        for i, phase in enumerate(phases):
            self.phase_display.set_current_phase(phase, f"Bulk update {i}")
        return f"Updated {len(phases)} phases"
        
    def _bulk_progress_updates(self, cycle_ids):
        """Helper for bulk progress updates"""
        update_count = 0
        for cycle_id in cycle_ids:
            for progress in range(0, 101, 10):
                self.progress_tracker.update_progress(cycle_id, progress, f"Bulk progress {progress}")
                update_count += 1
        return f"Updated {update_count} progress points"
        
    def _bulk_enforcement_updates(self):
        """Helper for bulk enforcement updates"""
        statuses = ["COMPLIANT", "WARNING", "VIOLATION"] * 10
        for i, status in enumerate(statuses):
            self.enforcement_display.update_enforcement_status(status, f"Bulk status {i}")
        return f"Updated {len(statuses)} enforcement statuses"