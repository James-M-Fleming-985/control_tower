"""
Critical Error Handling Tests for Business Logic Components
Strategic Coverage Improvement - Priority 2 Business Logic Error Handling
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from business_logic.tdd_cycle_enforcer import TDDCycleEnforcer
from business_logic.stage_gate_manager import StageGateManager
from business_logic.compliance_validator import ComplianceValidator


class TestTDDCycleEnforcerErrorHandling(unittest.TestCase):
    """Critical error handling tests for TDD Cycle Enforcer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.enforcer = TDDCycleEnforcer()
    
    def test_red_phase_enforcement_under_pressure(self):
        """Test RED phase enforcement when system is under stress"""
        # Simulate high load conditions
        with patch('threading.active_count', return_value=100):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 95  # High memory usage
                
                result = self.enforcer.enforce_red_phase()
                
                # System should still enforce RED phase rules under pressure
                self.assertIsNotNone(result)
                # Should handle resource constraints gracefully
                
    def test_green_phase_validation_edge_cases(self):
        """Test GREEN phase validation with edge case scenarios"""
        test_cases = [
            {"scenario": "empty_test_suite", "tests": []},
            {"scenario": "malformed_test_data", "tests": None},
            {"scenario": "corrupted_test_results", "tests": [{"corrupted": True}]}
        ]
        
        for case in test_cases:
            with self.subTest(scenario=case["scenario"]):
                try:
                    result = self.enforcer.validate_green_phase(case["tests"])
                    # Should handle edge cases without crashing
                    self.assertIsNotNone(result)
                except Exception as e:
                    # Should provide meaningful error information
                    self.assertIn("validation", str(e).lower())
    
    def test_refactor_phase_safety_checks(self):
        """Test REFACTOR phase safety mechanisms"""
        # Simulate dangerous refactor conditions
        with patch('os.path.exists', return_value=False):  # Missing backup
            with patch('git.Repo') as mock_repo:
                mock_repo.side_effect = Exception("Git repository corrupted")
                
                result = self.enforcer.validate_refactor_phase()
                
                # Should block dangerous refactors
                self.assertFalse(result.get('safe_to_proceed', True))
    
    def test_cycle_interruption_recovery(self):
        """Test recovery from TDD cycle interruptions"""
        # Simulate system interruption
        self.enforcer.current_phase = "GREEN"
        
        with patch('signal.signal') as mock_signal:
            # Simulate SIGINT (Ctrl+C)
            mock_signal.side_effect = KeyboardInterrupt()
            
            try:
                self.enforcer.handle_interruption()
            except KeyboardInterrupt:
                pass
            
            # Should save state before interruption
            self.assertIsNotNone(self.enforcer.get_recovery_state())


class TestStageGateManagerErrorHandling(unittest.TestCase):
    """Critical error handling tests for Stage Gate Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = StageGateManager()
    
    def test_stage_gate_bypass_prevention(self):
        """Test prevention of unauthorized stage gate bypasses"""
        # Attempt to bypass gate without meeting requirements
        bypass_attempts = [
            {"method": "force_override", "valid": False},
            {"method": "incomplete_tests", "valid": False},
            {"method": "missing_coverage", "valid": False}
        ]
        
        for attempt in bypass_attempts:
            with self.subTest(method=attempt["method"]):
                result = self.manager.attempt_bypass(attempt["method"])
                
                # All bypass attempts should be blocked
                self.assertFalse(result.get('allowed', True))
                self.assertIn('blocked', result.get('reason', '').lower())
    
    def test_invalid_phase_transition_blocking(self):
        """Test blocking of invalid phase transitions"""
        invalid_transitions = [
            ("RED", "REFACTOR"),    # Skip GREEN
            ("GREEN", "RED"),       # Backward transition
            ("REFACTOR", "GREEN"),  # Invalid backward
            ("UNKNOWN", "RED")      # Invalid source
        ]
        
        for from_phase, to_phase in invalid_transitions:
            with self.subTest(transition=f"{from_phase}->{to_phase}"):
                self.manager.current_phase = from_phase
                
                result = self.manager.transition_to(to_phase)
                
                # Invalid transitions should be blocked
                self.assertFalse(result.get('success', True))
    
    def test_stage_gate_state_corruption_recovery(self):
        """Test recovery from corrupted stage gate state"""
        # Corrupt the stage gate state
        self.manager.state = {"corrupted": True, "invalid_data": None}
        
        recovery_result = self.manager.recover_from_corruption()
        
        # Should restore valid state
        self.assertTrue(recovery_result.get('recovered', False))
        self.assertIsInstance(self.manager.state, dict)
        self.assertIn('phase', self.manager.state)
    
    def test_concurrent_stage_gate_access(self):
        """Test handling of concurrent stage gate access"""
        import threading
        import time
        
        results = []
        
        def concurrent_access(thread_id):
            try:
                result = self.manager.acquire_gate_lock(f"thread_{thread_id}")
                results.append(result)
                time.sleep(0.1)
                self.manager.release_gate_lock(f"thread_{thread_id}")
            except Exception as e:
                results.append({"error": str(e)})
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_access, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should handle concurrent access safely
        self.assertEqual(len(results), 5)
        # At least one should succeed
        successful = [r for r in results if r.get('success', False)]
        self.assertGreater(len(successful), 0)


class TestComplianceValidatorErrorHandling(unittest.TestCase):
    """Critical error handling tests for Compliance Validator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ComplianceValidator()
    
    def test_validation_under_corrupted_data(self):
        """Test compliance validation with corrupted input data"""
        corrupted_inputs = [
            None,
            {"malformed": "json"},
            {"tests": "not_a_list"},
            {"coverage": "invalid_percentage"}
        ]
        
        for corrupted_data in corrupted_inputs:
            with self.subTest(data=str(corrupted_data)):
                result = self.validator.validate_compliance(corrupted_data)
                
                # Should handle corruption gracefully
                self.assertIn('error', result)
                self.assertFalse(result.get('valid', True))
    
    def test_validation_timeout_handling(self):
        """Test handling of validation timeouts"""
        with patch('time.time') as mock_time:
            # Simulate timeout condition
            mock_time.side_effect = [0, 1000]  # Large time difference
            
            result = self.validator.validate_with_timeout(timeout=5)
            
            # Should handle timeout gracefully
            self.assertIn('timeout', result.get('error', '').lower())
    
    def test_external_dependency_failure(self):
        """Test behavior when external validation dependencies fail"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Network unavailable")
            
            result = self.validator.validate_external_compliance()
            
            # Should provide fallback validation
            self.assertIsNotNone(result)
            self.assertIn('fallback', result.get('mode', '').lower())


if __name__ == '__main__':
    unittest.main()