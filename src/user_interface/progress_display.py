#!/usr/bin/env python3
"""
Real-time Progress Display Component for TDD Workflow Interface

Implements requirement F1: Real-time verification progress display with <50ms updates
Part of LAYER-003-01-02-003: User Interface Layer

Created: 2025-09-18
"""

import time
import threading
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from datetime import datetime


@dataclass
class ProgressState:
    """Progress display state information"""
    current_step: int = 0
    total_steps: int = 100
    stage: str = "INITIALIZING"
    message: str = "Starting..."
    start_time: float = 0.0
    last_update: float = 0.0
    
    @property
    def percentage(self) -> float:
        """Calculate completion percentage"""
        if self.total_steps == 0:
            return 0.0
        return min(100.0, (self.current_step / self.total_steps) * 100.0)
    
    @property
    def elapsed_time(self) -> float:
        """Calculate elapsed time since start"""
        if self.start_time == 0.0:
            return 0.0
        return time.time() - self.start_time


class RealTimeProgressDisplay:
    """
    Real-time progress display component with <50ms update capability
    Implements requirement F1: Real-time verification progress display
    """
    
    def __init__(self, update_callback: Optional[Callable] = None):
        """Initialize progress display with optional update callback"""
        self.state = ProgressState()
        self.is_active = False
        self.update_thread = None
        self.update_callback = update_callback or self._default_update_callback
        self.update_interval = 0.01  # 10ms for <50ms response requirement
        self.lock = threading.Lock()
        
        # Performance tracking
        self.update_count = 0
        self.last_performance_check = time.time()
        self.response_times = []
    
    def start_progress(self, total_steps: int, initial_message: str = "Starting...") -> Dict[str, Any]:
        """Start progress tracking"""
        with self.lock:
            self.state = ProgressState(
                total_steps=total_steps,
                message=initial_message,
                start_time=time.time(),
                last_update=time.time()
            )
            self.is_active = True
            self.update_count = 0
            self.response_times.clear()
        
        # Start update thread for real-time display
        if self.update_thread is None or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
        
        return {
            'status': 'started',
            'total_steps': total_steps,
            'start_time': self.state.start_time
        }
    
    def update_progress(self, step: int, stage: str, message: str) -> Dict[str, Any]:
        """
        Update progress with performance tracking
        Must complete within <50ms to meet requirement Q1
        """
        update_start = time.time()
        
        with self.lock:
            if not self.is_active:
                return {'status': 'error', 'message': 'Progress not started'}
            
            self.state.current_step = step
            self.state.stage = stage
            self.state.message = message
            self.state.last_update = time.time()
            self.update_count += 1
        
        # Track response time for performance requirement
        response_time = (time.time() - update_start) * 1000  # Convert to milliseconds
        self.response_times.append(response_time)
        
        # Keep only recent response times for performance monitoring
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
        
        return {
            'status': 'updated',
            'step': step,
            'percentage': self.state.percentage,
            'stage': stage,
            'response_time_ms': response_time,
            'meets_requirement': response_time < 50.0  # Q1: <50ms requirement
        }
    
    def stop_progress(self) -> Dict[str, Any]:
        """Stop progress tracking and return performance metrics"""
        with self.lock:
            self.is_active = False
            end_time = time.time()
            total_time = end_time - self.state.start_time if self.state.start_time > 0 else 0
        
        # Calculate performance metrics
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        max_response_time = max(self.response_times) if self.response_times else 0
        updates_per_second = self.update_count / total_time if total_time > 0 else 0
        
        return {
            'status': 'completed',
            'total_time': total_time,
            'total_updates': self.update_count,
            'avg_response_time_ms': avg_response_time,
            'max_response_time_ms': max_response_time,
            'updates_per_second': updates_per_second,
            'performance_requirements_met': {
                'response_time_ok': avg_response_time < 50.0,  # Q1: <50ms
                'throughput_ok': updates_per_second >= 100.0   # Q2: >100/sec
            }
        }
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current progress state"""
        with self.lock:
            return {
                'step': self.state.current_step,
                'total_steps': self.state.total_steps,
                'percentage': self.state.percentage,
                'stage': self.state.stage,
                'message': self.state.message,
                'elapsed_time': self.state.elapsed_time,
                'is_active': self.is_active
            }
    
    def _update_loop(self):
        """Internal update loop for real-time display"""
        while True:
            if not self.is_active:
                break
            
            # Trigger display update
            try:
                current_state = self.get_current_state()
                self.update_callback(current_state)
            except Exception:
                # Don't let display errors break the progress tracking
                pass
            
            time.sleep(self.update_interval)  # 10ms sleep for <50ms updates
    
    def _default_update_callback(self, state: Dict[str, Any]):
        """Default update callback - prints to console"""
        if state['is_active']:
            progress_bar = self._generate_progress_bar(state['percentage'])
            print(f"\r{state['stage']} [{progress_bar}] {state['percentage']:.1f}% - {state['message']}", end='', flush=True)
    
    def _generate_progress_bar(self, percentage: float, width: int = 30) -> str:
        """Generate ASCII progress bar"""
        filled = int(width * percentage / 100)
        return '█' * filled + '░' * (width - filled)


class VerificationProgressTracker:
    """
    High-level progress tracker for TDD verification workflows
    Integrates with RealTimeProgressDisplay for user feedback
    """
    
    def __init__(self):
        """Initialize verification progress tracker"""
        self.progress_display = RealTimeProgressDisplay()
        self.verification_stages = [
            "INITIALIZING",
            "DISCOVERING_TESTS", 
            "RUNNING_TESTS",
            "COLLECTING_RESULTS",
            "VALIDATING_COVERAGE",
            "GENERATING_EVIDENCE",
            "COMPLETING"
        ]
        self.current_stage_index = 0
    
    def start_verification(self, total_test_files: int) -> Dict[str, Any]:
        """Start verification progress tracking"""
        total_steps = len(self.verification_stages) * total_test_files
        return self.progress_display.start_progress(
            total_steps=total_steps,
            initial_message="Initializing TDD verification..."
        )
    
    def update_stage(self, stage_name: str, files_processed: int, message: str) -> Dict[str, Any]:
        """Update verification stage progress"""
        if stage_name in self.verification_stages:
            self.current_stage_index = self.verification_stages.index(stage_name)
        
        step = self.current_stage_index * files_processed + files_processed
        return self.progress_display.update_progress(step, stage_name, message)
    
    def complete_verification(self) -> Dict[str, Any]:
        """Complete verification and return metrics"""
        return self.progress_display.stop_progress()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for requirements validation"""
        state = self.progress_display.get_current_state()
        response_times = self.progress_display.response_times
        
        return {
            'avg_response_time_ms': sum(response_times) / len(response_times) if response_times else 0,
            'max_response_time_ms': max(response_times) if response_times else 0,
            'min_response_time_ms': min(response_times) if response_times else 0,
            'total_updates': self.progress_display.update_count,
            'requirements_compliance': {
                'F1_real_time_display': state['is_active'],
                'Q1_response_time_under_50ms': all(rt < 50.0 for rt in response_times[-10:]),
                'Q2_throughput_over_100_per_sec': state['elapsed_time'] > 0 and (self.progress_display.update_count / state['elapsed_time']) >= 100
            }
        }