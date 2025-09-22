#!/usr/bin/env python3
"""
Tests for Stage Gate Visualization Component

Tests F2 requirement: Stage gate status visualization with RED/GREEN/REFACTOR indicators
Part of LAYER-003-01-02-003: User Interface Layer Testing  
Created: 2025-09-18
"""

import unittest
import time
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from user_interface.stage_gate_visualization import (
    StageGateVisualizer, 
    TDDWorkflowVisualizer, 
    TDDStage
)


class TestStageGateVisualizer(unittest.TestCase):
    """Test stage gate visualization functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.visualizer = StageGateVisualizer()
    
    def test_f2_visualizer_initialization(self):
        """Test F2: Stage gate visualizer initializes properly"""
        self.assertIsNotNone(self.visualizer)
        self.assertEqual(self.visualizer.current_state.current_stage, TDDStage.RED)
        self.assertEqual(self.visualizer.current_state.tests_failing, 0)
        self.assertEqual(self.visualizer.current_state.tests_passing, 0)
        self.assertEqual(len(self.visualizer.stage_history), 0)
    
    def test_f2_start_red_stage(self):
        """Test F2: Starting RED stage visualization"""
        result = self.visualizer.start_stage(
            TDDStage.RED,
            "Writing failing test for user authentication"
        )
        
        self.assertEqual(result['status'], 'stage_started')
        self.assertEqual(self.visualizer.current_state.current_stage, TDDStage.RED)
        self.assertEqual(result['stage'], 'RED')
        self.assertIn('start_time', result)
        self.assertIn('message', result)
        
        # Verify stage appears in history when next stage starts
        self.visualizer.start_stage(TDDStage.GREEN, "Next stage")
        self.assertEqual(len(self.visualizer.stage_history), 1)
        self.assertEqual(self.visualizer.stage_history[0].current_stage, TDDStage.RED)
    
    def test_f2_start_green_stage(self):
        """Test F2: Starting GREEN stage visualization"""
        result = self.visualizer.start_stage(
            TDDStage.GREEN,
            "Making authentication test pass"
        )
        
        self.assertEqual(result['status'], 'stage_started')
        self.assertEqual(self.visualizer.current_state.current_stage, TDDStage.GREEN)
        self.assertEqual(result['stage'], 'GREEN')
    
    def test_f2_start_refactor_stage(self):
        """Test F2: Starting REFACTOR stage visualization"""
        result = self.visualizer.start_stage(
            TDDStage.REFACTOR,
            "Improving authentication code structure"
        )
        
        self.assertEqual(result['status'], 'stage_started')
        self.assertEqual(self.visualizer.current_state.current_stage, TDDStage.REFACTOR)
        self.assertEqual(result['stage'], 'REFACTOR')
    
    def test_f2_update_stage_status(self):
        """Test F2: Updating stage status with test counts"""
        self.visualizer.start_stage(TDDStage.RED, "Writing tests")
        
        result = self.visualizer.update_stage_status(
            tests_failing=3,
            tests_passing=7,
            message="3 new tests failing as expected"
        )
        
        self.assertEqual(result['status'], 'updated')
        self.assertEqual(self.visualizer.current_state.tests_failing, 3)
        self.assertEqual(self.visualizer.current_state.tests_passing, 7)
        self.assertEqual(result['tests_failing'], 3)
        self.assertEqual(result['tests_passing'], 7)
        self.assertIn('stage_elapsed', result)
    
    def test_f2_display_current_stage_red(self):
        """Test F2: Display current RED stage with visual indicators"""
        self.visualizer.start_stage(TDDStage.RED, "Writing failing tests")
        self.visualizer.update_stage_status(2, 5, "2 tests failing")
        
        display = self.visualizer.display_current_stage()
        
        self.assertIsInstance(display, str)
        self.assertIn('RED', display)
        self.assertIn('🔴', display)  # Red circle emoji
        self.assertIn('2', display)  # Failing count
        self.assertIn('5', display)  # Passing count
        self.assertIn('2 tests failing', display)  # Should contain message
    
    def test_f2_display_current_stage_green(self):
        """Test F2: Display current GREEN stage with visual indicators"""
        self.visualizer.start_stage(TDDStage.GREEN, "Making tests pass")
        self.visualizer.update_stage_status(0, 8, "All tests now passing")
        
        display = self.visualizer.display_current_stage()
        
        self.assertIsInstance(display, str)
        self.assertIn('GREEN', display)
        self.assertIn('🟢', display)  # Green circle emoji
        self.assertIn('0', display)  # No failing tests
        self.assertIn('8', display)  # All passing
        self.assertIn('All tests now passing', display)
    
    def test_f2_display_current_stage_refactor(self):
        """Test F2: Display current REFACTOR stage with visual indicators"""
        self.visualizer.start_stage(TDDStage.REFACTOR, "Improving code quality")
        self.visualizer.update_stage_status(0, 10, "Refactoring complete")
        
        display = self.visualizer.display_current_stage()
        
        self.assertIsInstance(display, str)
        self.assertIn('REFACTOR', display)
        self.assertIn('🔵', display)  # Blue circle emoji
        self.assertIn('0', display)  # No failing tests
        self.assertIn('10', display)  # All passing
        self.assertIn('Refactoring complete', display)
    
    def test_f2_display_stage_timeline(self):
        """Test F2: Display stage timeline with progression"""
        # Go through complete TDD cycle, ensuring history is built
        self.visualizer.start_stage(TDDStage.RED, "Write failing test")
        time.sleep(0.1)
        self.visualizer.start_stage(TDDStage.GREEN, "Make test pass")  # This moves RED to history
        time.sleep(0.1)
        self.visualizer.start_stage(TDDStage.REFACTOR, "Improve code")  # This moves GREEN to history
        
        timeline = self.visualizer.display_stage_timeline()
        
        self.assertIsInstance(timeline, str)
        self.assertIn('Timeline', timeline)
        self.assertIn('RED', timeline)
        self.assertIn('GREEN', timeline)
        self.assertIn('REFACTOR', timeline)
        
        # Should show stage progression (2 completed stages + 1 active)
        self.assertEqual(len(self.visualizer.stage_history), 2)
    
    def test_f2_calculate_stage_compliance_score(self):
        """Test F2: Calculate TDD compliance score"""
        # Complete proper TDD cycle
        self.visualizer.start_stage(TDDStage.RED, "Write test")
        self.visualizer.update_stage_status(1, 0, "Test failing")
        time.sleep(0.1)
        
        self.visualizer.start_stage(TDDStage.GREEN, "Make pass")
        self.visualizer.update_stage_status(0, 1, "Test passing")
        time.sleep(0.1)
        
        self.visualizer.start_stage(TDDStage.REFACTOR, "Improve")
        self.visualizer.update_stage_status(0, 1, "Refactored")
        
        metrics = self.visualizer.get_stage_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('tdd_compliance', metrics)
        
        compliance = metrics['tdd_compliance']
        self.assertIn('compliance_score', compliance)
        self.assertIn('has_red_phase', compliance)
        self.assertIn('has_green_phase', compliance)
        self.assertIn('has_refactor_phase', compliance)
        
        # Should have good compliance for proper cycle
        self.assertTrue(compliance['has_red_phase'])
        self.assertTrue(compliance['has_green_phase'])


class TestTDDWorkflowVisualizer(unittest.TestCase):
    """Test TDD workflow visualization functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.workflow_visualizer = TDDWorkflowVisualizer()
    
    def test_f2_workflow_initialization(self):
        """Test F2: Workflow visualizer initializes properly"""
        self.assertIsNotNone(self.workflow_visualizer)
        self.assertEqual(self.workflow_visualizer.stage_visualizer.current_state.current_stage, TDDStage.RED)
        self.assertEqual(self.workflow_visualizer.workflow_start_time, 0.0)
        self.assertFalse(self.workflow_visualizer.workflow_active)
    
    def test_f2_start_workflow(self):
        """Test F2: Starting TDD workflow"""
        result = self.workflow_visualizer.start_workflow(TDDStage.RED)
        
        self.assertEqual(result['status'], 'stage_started')
        self.assertTrue(self.workflow_visualizer.workflow_active)
        self.assertEqual(self.workflow_visualizer.stage_visualizer.current_state.current_stage, TDDStage.RED)
        self.assertGreater(self.workflow_visualizer.workflow_start_time, 0)
        self.assertIn('start_time', result)
    
    def test_f2_update_workflow_progress(self):
        """Test F2: Updating workflow progress"""
        self.workflow_visualizer.start_workflow(TDDStage.RED)
        
        result = self.workflow_visualizer.update_workflow(
            stage=TDDStage.RED,
            tests_failing=2,
            tests_passing=3,
            message="Added 2 failing tests"
        )
        
        self.assertEqual(result['status'], 'updated')
        self.assertEqual(result['stage'], 'RED')
        self.assertEqual(result['tests_failing'], 2)
        self.assertEqual(result['tests_passing'], 3)
        self.assertIn('stage_elapsed', result)
    
    def test_f2_complete_workflow_cycle(self):
        """Test F2: Complete TDD workflow cycle"""
        # Start workflow
        self.workflow_visualizer.start_workflow(TDDStage.RED)
        
        # RED phase
        self.workflow_visualizer.update_workflow(TDDStage.RED, 1, 0, "Test failing")
        
        # GREEN phase
        self.workflow_visualizer.update_workflow(TDDStage.GREEN, 0, 1, "Test passing")
        
        # REFACTOR phase
        result = self.workflow_visualizer.update_workflow(
            TDDStage.REFACTOR, 0, 1, "Code improved"
        )
        
        self.assertEqual(result['status'], 'updated')
        self.assertEqual(result['stage'], 'REFACTOR')
        
        # Check workflow history tracks all phases
        self.assertGreaterEqual(len(self.workflow_visualizer.stage_visualizer.stage_history), 2)
    
    def test_f2_display_workflow_status(self):
        """Test F2: Display complete workflow status"""
        self.workflow_visualizer.start_workflow(TDDStage.GREEN)
        self.workflow_visualizer.update_workflow(TDDStage.GREEN, 0, 5, "All tests passing")
        
        status = self.workflow_visualizer.display_workflow_status()
        
        self.assertIsInstance(status, str)
        self.assertIn('TDD Workflow Active', status)
        self.assertIn('GREEN', status)
        self.assertIn('🟢', status)
        self.assertIn('5', status)  # Test count
        self.assertIn('All tests passing', status)
    
    def test_f2_workflow_timeline_display(self):
        """Test F2: Workflow timeline display"""
        # Create workflow with multiple updates
        self.workflow_visualizer.start_workflow(TDDStage.RED)
        
        for i in range(3):
            self.workflow_visualizer.update_workflow(
                TDDStage.RED, 
                1, 
                i, 
                f"Update {i}"
            )
            time.sleep(0.05)
        
        timeline = self.workflow_visualizer.stage_visualizer.display_stage_timeline()
        
        self.assertIsInstance(timeline, str)
        self.assertIn('Timeline', timeline)
        self.assertIn('RED', timeline)
        
        # Should show current stage
        self.assertGreater(self.workflow_visualizer.stage_visualizer.current_state.stage_start_time, 0)
    
    def test_f2_stop_workflow(self):
        """Test F2: Stopping workflow and getting summary"""
        self.workflow_visualizer.start_workflow(TDDStage.RED)
        
        # Add some workflow activity
        self.workflow_visualizer.update_workflow(TDDStage.RED, 2, 1, "Tests failing")
        self.workflow_visualizer.update_workflow(TDDStage.GREEN, 0, 3, "Tests passing")
        
        # Complete workflow
        summary = self.workflow_visualizer.complete_workflow()
        
        self.assertFalse(self.workflow_visualizer.workflow_active)
        self.assertIsInstance(summary, dict)
        self.assertIn('total_workflow_time', summary)
        self.assertIn('total_stages_completed', summary)
        self.assertIn('current_stage', summary)
        self.assertIn('workflow_complete', summary)
        
        # Verify final state
        self.assertEqual(summary['current_stage'], 'GREEN')
        self.assertTrue(summary['workflow_complete'])


class TestTDDStageEnum(unittest.TestCase):
    """Test TDD stage enumeration"""
    
    def test_f2_stage_enum_values(self):
        """Test F2: TDD stage enum has correct values"""
        self.assertEqual(TDDStage.RED.value, "RED")
        self.assertEqual(TDDStage.GREEN.value, "GREEN")
        self.assertEqual(TDDStage.REFACTOR.value, "REFACTOR")
        self.assertEqual(TDDStage.COMPLETE.value, "COMPLETE")
        self.assertEqual(TDDStage.ERROR.value, "ERROR")
    
    def test_f2_stage_enum_colors(self):
        """Test F2: Stage enum provides visual indicators"""
        # These should be accessible as stage properties
        self.assertTrue(hasattr(TDDStage, 'RED'))
        self.assertTrue(hasattr(TDDStage, 'GREEN'))
        self.assertTrue(hasattr(TDDStage, 'REFACTOR'))


if __name__ == '__main__':
    unittest.main()