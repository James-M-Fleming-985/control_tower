#!/usr/bin/env python3
"""
Stage Gate Visualization Component for TDD Workflow Interface

Implements requirement F2: Stage gate status visualization with RED/GREEN/REFACTOR indicators
Part of LAYER-003-01-02-003: User Interface Layer

Created: 2025-09-18
"""

import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime


class TDDStage(Enum):
    """TDD workflow stages"""
    RED = "RED"
    GREEN = "GREEN" 
    REFACTOR = "REFACTOR"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


@dataclass
class StageState:
    """Stage gate state information"""
    current_stage: TDDStage = TDDStage.RED
    stage_start_time: float = 0.0
    stage_duration: float = 0.0
    tests_failing: int = 0
    tests_passing: int = 0
    stage_message: str = ""
    stage_complete: bool = False
    
    @property
    def stage_elapsed(self) -> float:
        """Calculate elapsed time in current stage"""
        if self.stage_start_time == 0.0:
            return 0.0
        return time.time() - self.stage_start_time


class StageGateVisualizer:
    """
    Stage gate visualization component with RED/GREEN/REFACTOR indicators
    Implements requirement F2: Stage gate status visualization
    """
    
    def __init__(self, use_colors: bool = True):
        """Initialize stage gate visualizer"""
        self.use_colors = use_colors
        self.stage_history: List[StageState] = []
        self.current_state = StageState()
        
        # Visual indicators for each stage
        self.stage_colors = {
            TDDStage.RED: '\033[91m',      # Red
            TDDStage.GREEN: '\033[92m',    # Green
            TDDStage.REFACTOR: '\033[94m', # Blue
            TDDStage.COMPLETE: '\033[95m', # Magenta
            TDDStage.ERROR: '\033[93m'     # Yellow
        }
        self.reset_color = '\033[0m'
        
        # ASCII art indicators
        self.stage_indicators = {
            TDDStage.RED: "🔴",
            TDDStage.GREEN: "🟢", 
            TDDStage.REFACTOR: "🔵",
            TDDStage.COMPLETE: "✅",
            TDDStage.ERROR: "⚠️"
        }
    
    def start_stage(self, stage: TDDStage, message: str = "") -> Dict[str, Any]:
        """Start a new TDD stage"""
        # Save previous stage to history
        if self.current_state.stage_start_time > 0:
            self.current_state.stage_duration = time.time() - self.current_state.stage_start_time
            self.current_state.stage_complete = True
            self.stage_history.append(self.current_state)
        
        # Start new stage
        self.current_state = StageState(
            current_stage=stage,
            stage_start_time=time.time(),
            stage_message=message
        )
        
        return {
            'status': 'stage_started',
            'stage': stage.value,
            'message': message,
            'start_time': self.current_state.stage_start_time
        }
    
    def update_stage_status(self, tests_failing: int, tests_passing: int, message: str = "") -> Dict[str, Any]:
        """Update current stage status"""
        self.current_state.tests_failing = tests_failing
        self.current_state.tests_passing = tests_passing
        if message:
            self.current_state.stage_message = message
        
        # Auto-transition logic based on test results
        stage_transition = self._check_stage_transition(tests_failing, tests_passing)
        
        return {
            'status': 'updated',
            'stage': self.current_state.current_stage.value,
            'tests_failing': tests_failing,
            'tests_passing': tests_passing,
            'stage_elapsed': self.current_state.stage_elapsed,
            'auto_transition': stage_transition
        }
    
    def display_current_stage(self) -> str:
        """Generate visual display of current stage"""
        stage = self.current_state.current_stage
        indicator = self.stage_indicators.get(stage, "●")
        color = self.stage_colors.get(stage, "") if self.use_colors else ""
        reset = self.reset_color if self.use_colors else ""
        
        # Create stage display
        stage_display = f"{color}{indicator} {stage.value}{reset}"
        
        # Add test status
        if self.current_state.tests_failing > 0 or self.current_state.tests_passing > 0:
            test_status = f" | ❌ {self.current_state.tests_failing} ✅ {self.current_state.tests_passing}"
            stage_display += test_status
        
        # Add elapsed time
        elapsed = self.current_state.stage_elapsed
        if elapsed > 0:
            stage_display += f" | ⏱️ {elapsed:.1f}s"
        
        # Add message
        if self.current_state.stage_message:
            stage_display += f" | {self.current_state.stage_message}"
        
        return stage_display
    
    def display_stage_timeline(self) -> str:
        """Generate visual timeline of all stages"""
        timeline = "TDD Stage Timeline:\n"
        
        # Show completed stages
        for i, stage_state in enumerate(self.stage_history):
            indicator = self.stage_indicators.get(stage_state.current_stage, "●")
            duration = stage_state.stage_duration
            timeline += f"  {i+1}. {indicator} {stage_state.current_stage.value} "
            timeline += f"({duration:.1f}s) - {stage_state.stage_message}\n"
        
        # Show current stage
        if self.current_state.stage_start_time > 0:
            current_display = self.display_current_stage()
            timeline += f"  {len(self.stage_history)+1}. {current_display} (ACTIVE)\n"
        
        return timeline
    
    def get_stage_metrics(self) -> Dict[str, Any]:
        """Get comprehensive stage metrics"""
        total_time = sum(stage.stage_duration for stage in self.stage_history)
        if self.current_state.stage_start_time > 0:
            total_time += self.current_state.stage_elapsed
        
        stage_counts = {}
        for stage in TDDStage:
            stage_counts[stage.value] = sum(1 for s in self.stage_history if s.current_stage == stage)
        
        return {
            'total_stages_completed': len(self.stage_history),
            'total_time_seconds': total_time,
            'current_stage': self.current_state.current_stage.value,
            'current_stage_elapsed': self.current_state.stage_elapsed,
            'stage_distribution': stage_counts,
            'red_green_ratio': self._calculate_red_green_ratio(),
            'tdd_compliance': self._assess_tdd_compliance()
        }
    
    def _check_stage_transition(self, tests_failing: int, tests_passing: int) -> Optional[str]:
        """Check if stage should transition based on test results"""
        current = self.current_state.current_stage
        
        if current == TDDStage.RED and tests_failing == 0 and tests_passing > 0:
            return "RED_TO_GREEN"
        elif current == TDDStage.GREEN and tests_passing > 0:
            return "GREEN_TO_REFACTOR"
        elif current == TDDStage.REFACTOR and tests_passing > 0:
            return "REFACTOR_COMPLETE"
        
        return None
    
    def _calculate_red_green_ratio(self) -> float:
        """Calculate RED to GREEN stage time ratio"""
        red_time = sum(s.stage_duration for s in self.stage_history if s.current_stage == TDDStage.RED)
        green_time = sum(s.stage_duration for s in self.stage_history if s.current_stage == TDDStage.GREEN)
        
        if green_time == 0:
            return float('inf') if red_time > 0 else 0.0
        return red_time / green_time
    
    def _assess_tdd_compliance(self) -> Dict[str, Any]:
        """Assess TDD workflow compliance"""
        stages_present = set(s.current_stage for s in self.stage_history)
        
        has_red = TDDStage.RED in stages_present
        has_green = TDDStage.GREEN in stages_present
        has_refactor = TDDStage.REFACTOR in stages_present
        
        proper_sequence = self._check_proper_sequence()
        
        return {
            'has_red_phase': has_red,
            'has_green_phase': has_green,
            'has_refactor_phase': has_refactor,
            'proper_sequence': proper_sequence,
            'tdd_complete': has_red and has_green and has_refactor and proper_sequence,
            'compliance_score': self._calculate_compliance_score()
        }
    
    def _check_proper_sequence(self) -> bool:
        """Check if stages follow proper RED -> GREEN -> REFACTOR sequence"""
        if len(self.stage_history) < 2:
            return True
        
        for i in range(len(self.stage_history) - 1):
            current = self.stage_history[i].current_stage
            next_stage = self.stage_history[i + 1].current_stage
            
            # Valid transitions
            valid_transitions = {
                TDDStage.RED: [TDDStage.GREEN, TDDStage.RED],
                TDDStage.GREEN: [TDDStage.REFACTOR, TDDStage.RED],
                TDDStage.REFACTOR: [TDDStage.RED, TDDStage.COMPLETE]
            }
            
            if next_stage not in valid_transitions.get(current, []):
                return False
        
        return True
    
    def _calculate_compliance_score(self) -> float:
        """Calculate overall TDD compliance score (0-100)"""
        score = 0.0
        
        # Stage presence (40 points)
        stages_present = set(s.current_stage for s in self.stage_history)
        if TDDStage.RED in stages_present:
            score += 15.0
        if TDDStage.GREEN in stages_present:
            score += 15.0  
        if TDDStage.REFACTOR in stages_present:
            score += 10.0
        
        # Proper sequence (30 points)
        if self._check_proper_sequence():
            score += 30.0
        
        # Time balance (30 points)
        red_green_ratio = self._calculate_red_green_ratio()
        if 0.5 <= red_green_ratio <= 2.0:  # Balanced RED/GREEN time
            score += 30.0
        elif red_green_ratio != float('inf'):
            score += max(0, 30.0 - abs(red_green_ratio - 1.0) * 10)
        
        return min(100.0, score)


class TDDWorkflowVisualizer:
    """
    High-level TDD workflow visualizer combining progress and stage displays
    Implements requirements F1 + F2: Complete visual workflow feedback
    """
    
    def __init__(self):
        """Initialize complete TDD workflow visualizer"""
        self.stage_visualizer = StageGateVisualizer()
        self.workflow_start_time = 0.0
        self.workflow_active = False
    
    def start_workflow(self, initial_stage: TDDStage = TDDStage.RED) -> Dict[str, Any]:
        """Start TDD workflow visualization"""
        self.workflow_start_time = time.time()
        self.workflow_active = True
        
        return self.stage_visualizer.start_stage(initial_stage, "Starting TDD workflow...")
    
    def update_workflow(self, stage: TDDStage, tests_failing: int, tests_passing: int, message: str = "") -> Dict[str, Any]:
        """Update workflow with new stage and test results"""
        if not self.workflow_active:
            return {'status': 'error', 'message': 'Workflow not started'}
        
        # Update or transition stage if needed
        if stage != self.stage_visualizer.current_state.current_stage:
            self.stage_visualizer.start_stage(stage, message)
        
        return self.stage_visualizer.update_stage_status(tests_failing, tests_passing, message)
    
    def display_workflow_status(self) -> str:
        """Generate complete workflow status display"""
        if not self.workflow_active:
            return "TDD Workflow: Inactive"
        
        # Header with total workflow time
        total_time = time.time() - self.workflow_start_time
        header = f"🔄 TDD Workflow Active ({total_time:.1f}s total)\n"
        header += "=" * 50 + "\n"
        
        # Current stage display
        current_stage = self.stage_visualizer.display_current_stage()
        header += f"Current: {current_stage}\n\n"
        
        # Stage timeline
        timeline = self.stage_visualizer.display_stage_timeline()
        
        return header + timeline
    
    def complete_workflow(self) -> Dict[str, Any]:
        """Complete workflow and return comprehensive metrics"""
        self.workflow_active = False
        total_time = time.time() - self.workflow_start_time
        
        metrics = self.stage_visualizer.get_stage_metrics()
        metrics['total_workflow_time'] = total_time
        metrics['workflow_complete'] = True
        
        return metrics