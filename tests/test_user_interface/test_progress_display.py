#!/usr/bin/env python3
"""
Tests for Progress Display Component

Tests F1 requirement: Real-time verification progress display
Part of LAYER-003-01-02-003: User Interface Layer Testing
Created: 2025-09-18
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from user_interface.progress_display import RealTimeProgressDisplay, VerificationProgressTracker


class TestRealTimeProgressDisplay(unittest.TestCase):
    """Test real-time progress display functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.progress_display = RealTimeProgressDisplay()
    
    def test_f1_progress_display_initialization(self):
        """Test F1: Progress display properly initializes"""
        self.assertIsNotNone(self.progress_display)
        self.assertFalse(self.progress_display.is_active)
        self.assertEqual(self.progress_display.state.current_step, 0)
        self.assertEqual(self.progress_display.state.total_steps, 100)
    
    def test_f1_start_progress_tracking(self):
        """Test F1: Starting progress tracking"""
        result = self.progress_display.start_progress(
            total_steps=100,
            initial_message="Starting test verification"
        )
        
        self.assertEqual(result['status'], 'started')
        self.assertTrue(self.progress_display.is_active)
        self.assertEqual(self.progress_display.state.total_steps, 100)
        self.assertEqual(self.progress_display.state.current_step, 0)
        self.assertIn('start_time', result)
    
    def test_f1_update_progress_with_stage_info(self):
        """Test F1: Updating progress with stage information"""
        self.progress_display.start_progress(total_steps=10)
        
        result = self.progress_display.update_progress(
            step=5,
            stage="TESTING",
            message="Running integration tests"
        )
        
        self.assertEqual(result['status'], 'updated')
        self.assertEqual(result['percentage'], 50.0)
        self.assertEqual(result['step'], 5)
        self.assertEqual(result['stage'], "TESTING")
        self.assertIn('response_time_ms', result)
        self.assertTrue(result['meets_requirement'])  # <50ms requirement
    
    def test_f1_stop_progress_tracking(self):
        """Test F1: Stopping progress tracking and getting metrics"""
        self.progress_display.start_progress(total_steps=5)
        
        # Make some progress updates
        for i in range(5):
            self.progress_display.update_progress(i, f"STAGE_{i}", f"Step {i}")
            time.sleep(0.01)  # Small delay to test timing
        
        final_metrics = self.progress_display.stop_progress()
        
        self.assertFalse(self.progress_display.is_active)
        self.assertIn('total_time', final_metrics)
        self.assertIn('avg_response_time_ms', final_metrics)
        self.assertIn('total_updates', final_metrics)
        self.assertIn('performance_requirements_met', final_metrics)
        
        # Verify performance requirements
        perf_req = final_metrics['performance_requirements_met']
        self.assertTrue(perf_req['response_time_ok'])
        self.assertIsInstance(perf_req['throughput_ok'], bool)
    
    def test_f1_observer_pattern_callbacks(self):
        """Test F1: Observer pattern for real-time updates"""
        callback_events = []
        
        def test_callback(state):
            callback_events.append(state.copy())
        
        display = RealTimeProgressDisplay(update_callback=test_callback)
        display.start_progress(total_steps=3)
        
        # Trigger updates and wait for callbacks
        display.update_progress(1, "RED", "Writing failing test")
        time.sleep(0.1)  # Wait for update loop
        display.update_progress(2, "GREEN", "Making test pass")
        time.sleep(0.1)  # Wait for update loop
        display.update_progress(3, "REFACTOR", "Improving code")
        time.sleep(0.1)  # Wait for update loop
        
        display.stop_progress()
        time.sleep(0.1)  # Final wait
        
        # Verify callbacks were triggered
        self.assertGreaterEqual(len(callback_events), 3, f"Expected at least 3 callbacks, got {len(callback_events)}")
        
        # Verify callback structure
        for event in callback_events:
            self.assertIn('stage', event)
            self.assertIn('percentage', event)
            self.assertIn('message', event)
    
    def test_f1_real_time_performance_tracking(self):
        """Test F1: Real-time performance meets requirements"""
        self.progress_display.start_progress(total_steps=20)
        
        response_times = []
        
        for i in range(20):
            start_time = time.time()
            result = self.progress_display.update_progress(
                step=i,
                stage=f"STAGE_{i%3}",
                message=f"Performance test update {i}"
            )
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            response_times.append(response_time_ms)
            
            # Each update should meet requirement
            self.assertTrue(result['meets_requirement'])
            self.assertLess(result['response_time_ms'], 50.0)
        
        final_metrics = self.progress_display.stop_progress()
        
        # Verify overall performance
        avg_response = sum(response_times) / len(response_times)
        self.assertLess(avg_response, 50.0, "Average response time should be <50ms")
        
        self.assertTrue(final_metrics['performance_requirements_met']['response_time_ok'])


class TestVerificationProgressTracker(unittest.TestCase):
    """Test verification progress tracker functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.tracker = VerificationProgressTracker()
    
    def test_f1_tracker_initialization(self):
        """Test tracker initializes properly"""
        self.assertIsNotNone(self.tracker)
        self.assertEqual(self.tracker.current_stage_index, 0)
        self.assertEqual(len(self.tracker.verification_stages), 7)
        self.assertIsNotNone(self.tracker.progress_display)
    
    def test_f1_start_verification_session(self):
        """Test starting verification session"""
        total_test_files = 5
        
        result = self.tracker.start_verification(total_test_files)
        
        self.assertEqual(result['status'], 'started')
        self.assertEqual(result['total_steps'], 35)  # 7 stages * 5 files
        self.assertIn('start_time', result)
    
    def test_f1_track_verification_progress(self):
        """Test tracking individual verification progress"""
        self.tracker.start_verification(3)
        
        # Track progress on RUNNING_TESTS stage
        result = self.tracker.update_stage(
            stage_name="RUNNING_TESTS",
            files_processed=2,
            message="Running tests for file 2"
        )
        
        self.assertEqual(result['status'], 'updated')
        self.assertEqual(result['stage'], "RUNNING_TESTS")
        self.assertIn('response_time_ms', result)
    
    def test_f1_complete_verification(self):
        """Test completing verification"""
        self.tracker.start_verification(2)
        
        # Complete verification
        result = self.tracker.complete_verification()
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('total_time', result)
        self.assertIn('performance_requirements_met', result)
    
    def test_f1_get_overall_progress(self):
        """Test getting overall verification progress"""
        self.tracker.start_verification(4)
        
        # Make some progress
        self.tracker.update_stage("RUNNING_TESTS", 2, "Running tests")
        self.tracker.update_stage("VALIDATING_COVERAGE", 1, "Validating coverage")
        
        metrics = self.tracker.get_performance_metrics()
        
        self.assertIn('avg_response_time_ms', metrics)
        self.assertIn('total_updates', metrics)
        self.assertIn('requirements_compliance', metrics)
        
        compliance = metrics['requirements_compliance']
        self.assertIn('F1_real_time_display', compliance)
        self.assertIn('Q1_response_time_under_50ms', compliance)
    
    def test_f1_tracker_performance_requirements(self):
        """Test tracker meets performance requirements"""
        # Measure session start time
        start_time = time.time()
        self.tracker.start_verification(10)
        session_time = (time.time() - start_time) * 1000
        
        self.assertLess(session_time, 50.0, "Session start should be <50ms")
        
        # Measure update performance
        update_times = []
        for i in range(5):
            start_time = time.time()
            self.tracker.update_stage(
                "RUNNING_TESTS",
                i,
                f"Performance test update {i}"
            )
            update_time = (time.time() - start_time) * 1000
            update_times.append(update_time)
        
        avg_update_time = sum(update_times) / len(update_times)
        self.assertLess(avg_update_time, 50.0, "Average update time should be <50ms")


if __name__ == '__main__':
    unittest.main()