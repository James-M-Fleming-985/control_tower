"""
Critical Stage Gate Enforcement Safety Tests
FEATURE-003-01-03 Risk Mitigation - Priority 2

These tests focus on preventing stage gate bypass and ensuring 
TDD workflow integrity under error conditions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import threading
import time

from src.business_logic.stage_gate_manager import StageGateManager
from src.business_logic.tdd_cycle_enforcer import TDDCycleEnforcer


class TestStageGateEnforcementSafety:
    """Critical safety tests for stage gate enforcement"""
    
    def setup_method(self):
        """Setup test environment"""
        self.stage_manager = StageGateManager()
        self.test_context = {
            "feature_id": "FEATURE-003-01-03",
            "current_phase": "RED",
            "user_id": "test_user"
        }
    
    def test_stage_gate_bypass_prevention(self):
        """Test prevention of unauthorized stage gate bypass attempts"""
        # Simulate attempt to bypass stage gate validation
        with patch.object(self.stage_manager, '_validate_phase_requirements') as mock_validate:
            mock_validate.return_value = {"valid": False, "missing": ["tests", "coverage"]}
            
            # Attempt to force phase transition without meeting requirements
            result = self.stage_manager.force_phase_transition(
                from_phase="RED",
                to_phase="GREEN",
                bypass_validation=True,  # Malicious attempt
                context=self.test_context
            )
            
            # Should block bypass attempt
            assert result.success is False
            assert result.bypass_blocked is True
            assert "unauthorized bypass attempt" in result.error_message.lower()
            assert result.security_violation_logged is True
    
    def test_invalid_phase_transition_blocking(self):
        """Test blocking of logically invalid phase transitions"""
        # Test invalid transitions
        invalid_transitions = [
            ("RED", "REFACTOR"),      # Skip GREEN phase
            ("GREEN", "RED"),         # Backwards transition  
            ("REFACTOR", "GREEN"),    # Invalid backwards
            ("UNKNOWN", "RED"),       # Invalid starting phase
        ]
        
        for from_phase, to_phase in invalid_transitions:
            result = self.stage_manager.attempt_phase_transition(
                from_phase=from_phase,
                to_phase=to_phase,
                context=self.test_context
            )
            
            assert result.success is False
            assert result.invalid_transition is True
            assert f"{from_phase} -> {to_phase}" in result.blocked_transition
    
    def test_stage_gate_state_corruption_recovery(self):
        """Test recovery from corrupted stage gate state"""
        # Simulate corrupted internal state
        self.stage_manager._internal_state = {
            "current_phase": "INVALID_PHASE",
            "last_transition": None,
            "corruption_detected": True
        }
        
        # System should detect and recover from corruption
        result = self.stage_manager.validate_and_recover_state(self.test_context)
        
        assert result.corruption_detected is True
        assert result.recovery_successful is True
        assert result.state_restored_to == "RED"  # Safe default state
        assert result.corruption_logged is True
    
    def test_concurrent_stage_gate_access_protection(self):
        """Test protection against race conditions in concurrent access"""
        results = []
        
        def concurrent_transition_attempt(thread_id):
            """Simulate concurrent stage gate access"""
            result = self.stage_manager.thread_safe_phase_transition(
                from_phase="RED",
                to_phase="GREEN", 
                context={**self.test_context, "thread_id": thread_id}
            )
            results.append(result)
        
        # Launch multiple concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=concurrent_transition_attempt,
                args=(f"thread_{i}",)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Only one transition should succeed, others should be blocked
        successful_transitions = [r for r in results if r.success]
        blocked_transitions = [r for r in results if not r.success]
        
        assert len(successful_transitions) == 1
        assert len(blocked_transitions) == 4
        assert all("concurrent access blocked" in r.error_message for r in blocked_transitions)
    
    def test_stage_gate_timeout_protection(self):
        """Test protection against hanging stage gate validations"""
        # Simulate validation that takes too long
        with patch.object(self.stage_manager, '_perform_comprehensive_validation') as mock_validate:
            # Mock a validation that hangs
            mock_validate.side_effect = lambda: time.sleep(100)  # Simulate hang
            
            # Should timeout and fail safely
            result = self.stage_manager.validate_with_timeout(
                phase="GREEN",
                context=self.test_context,
                timeout_seconds=5
            )
            
            assert result.success is False
            assert result.timed_out is True
            assert result.validation_incomplete is True
            assert "validation timeout" in result.error_message.lower()
    
    def test_stage_gate_rollback_on_validation_failure(self):
        """Test rollback when stage gate validation fails mid-process"""
        # Mock partial validation failure
        with patch.object(self.stage_manager, '_validate_tests') as mock_test_validation:
            with patch.object(self.stage_manager, '_validate_coverage') as mock_coverage_validation:
                # Tests pass, but coverage fails
                mock_test_validation.return_value = {"valid": True}
                mock_coverage_validation.side_effect = Exception("Coverage calculation failed")
                
                initial_state = self.stage_manager.get_current_state()
                
                result = self.stage_manager.comprehensive_validation(
                    phase="GREEN",
                    context=self.test_context
                )
                
                # Should rollback to initial state
                final_state = self.stage_manager.get_current_state()
                
                assert result.success is False
                assert result.rollback_completed is True
                assert final_state == initial_state
    
    def test_malicious_context_injection_protection(self):
        """Test protection against malicious context data injection"""
        # Simulate malicious context injection
        malicious_context = {
            "feature_id": "'; DROP TABLE stages; --",  # SQL injection attempt
            "current_phase": "<script>alert('xss')</script>",  # XSS attempt
            "user_id": "../../../etc/passwd",  # Path traversal attempt
            "bypass_all_validations": True,  # Authorization bypass attempt
        }
        
        result = self.stage_manager.secure_phase_transition(
            from_phase="RED",
            to_phase="GREEN",
            context=malicious_context
        )
        
        # Should sanitize and block malicious inputs
        assert result.success is False
        assert result.malicious_input_detected is True
        assert result.security_violation_logged is True
        assert "input sanitization failed" in result.error_message.lower()


class TestTDDCycleEnforcementSafety:
    """Critical safety tests for TDD cycle enforcement"""
    
    def setup_method(self):
        """Setup test environment"""
        self.tdd_enforcer = TDDCycleEnforcer()
    
    def test_red_phase_enforcement_under_pressure(self):
        """Test RED phase enforcement when under time pressure"""
        # Simulate high-pressure scenario (tight deadline)
        pressure_context = {
            "deadline_minutes": 5,  # Very tight deadline
            "skip_tests_requested": True,  # User wants to skip
            "management_override": True,  # Pressure from above
        }
        
        result = self.tdd_enforcer.enforce_red_phase_requirements(
            context=pressure_context
        )
        
        # Should maintain TDD integrity despite pressure
        assert result.requirements_enforced is True
        assert result.bypass_denied is True
        assert "tdd integrity maintained" in result.status_message.lower()
    
    def test_green_phase_validation_edge_cases(self):
        """Test GREEN phase validation handles edge cases properly"""
        edge_cases = [
            {"tests": [], "coverage": 0},  # No tests at all
            {"tests": ["fake_test"], "coverage": None},  # Invalid coverage
            {"tests": None, "coverage": 100},  # Missing test data
            {"tests": ["test1"] * 1000, "coverage": 50},  # Too many tests, low coverage
        ]
        
        for case in edge_cases:
            result = self.tdd_enforcer.validate_green_phase_requirements(
                test_data=case
            )
            
            # Should handle all edge cases gracefully
            assert result.validation_completed is True
            assert isinstance(result.valid, bool)  # Should never be None/undefined
            assert result.error_handling_successful is True
    
    def test_refactor_phase_safety_checks(self):
        """Test REFACTOR phase safety checks prevent code breakage"""
        # Simulate refactoring that might break functionality
        with patch.object(self.tdd_enforcer, '_run_regression_tests') as mock_regression:
            # Simulate regression test failure
            mock_regression.return_value = {
                "passed": False,
                "failures": ["test_critical_feature", "test_user_workflow"],
                "new_failures": 2
            }
            
            result = self.tdd_enforcer.validate_refactor_safety(
                proposed_changes=["modify_core_logic", "update_interface"]
            )
            
            # Should block unsafe refactoring
            assert result.refactor_approved is False
            assert result.regression_detected is True
            assert result.safety_check_passed is False
            assert "regression failures detected" in result.blocking_reason.lower()
    
    def test_cycle_interruption_recovery(self):
        """Test recovery from interrupted TDD cycles"""
        # Simulate interrupted cycle (system crash, power loss, etc.)
        interrupted_state = {
            "phase": "GREEN",
            "partial_implementation": True,
            "tests_passing": False,
            "last_checkpoint": "2025-09-20T10:30:00Z",
            "interruption_detected": True
        }
        
        result = self.tdd_enforcer.recover_from_interruption(
            last_known_state=interrupted_state
        )
        
        # Should recover to safe state
        assert result.recovery_successful is True
        assert result.safe_state_restored is True
        assert result.recovered_to_phase == "RED"  # Safe restart point
        assert result.partial_work_preserved is True
    
    def test_tdd_enforcement_under_system_load(self):
        """Test TDD enforcement maintains integrity under high system load"""
        # Simulate high system load conditions
        with patch('psutil.cpu_percent') as mock_cpu:
            with patch('psutil.virtual_memory') as mock_memory:
                mock_cpu.return_value = 95  # Very high CPU usage
                mock_memory.return_value = Mock(percent=90)  # High memory usage
                
                result = self.tdd_enforcer.enforce_tdd_under_load(
                    phase="GREEN",
                    load_threshold=80
                )
                
                # Should adapt to load but maintain standards
                assert result.enforcement_maintained is True
                assert result.performance_adapted is True
                assert result.standards_compromised is False
    
    def test_external_tool_failure_handling(self):
        """Test handling when external TDD tools fail"""
        # Simulate external tool failures
        tool_failures = [
            {"tool": "pytest", "error": "ImportError: module not found"},
            {"tool": "coverage", "error": "Permission denied"},
            {"tool": "git", "error": "Repository not found"},
        ]
        
        for failure in tool_failures:
            result = self.tdd_enforcer.handle_external_tool_failure(
                tool=failure["tool"],
                error=failure["error"]
            )
            
            # Should provide graceful degradation
            assert result.fallback_activated is True
            assert result.enforcement_continued is True
            assert failure["tool"] in result.failed_tools
            assert result.alternative_validation_used is True