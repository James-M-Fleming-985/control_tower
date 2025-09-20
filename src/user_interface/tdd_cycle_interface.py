#!/usr/bin/env python3
"""
LAYER-003-01-03-003: User Interface Layer - TDD Cycle Interface
FEATURE-003-01-03: RED GREEN REFACTOR CYCLE ENFORCER

Provides user interface for TDD cycle management with real-time progress display
and phase transition visualization.

B-Grade Requirements:
- 85%+ test coverage
- Real-time progress display under concurrent operations
- Phase transition visualization validation
- Accessibility compliance (WCAG 2.1 AA standards)
"""

import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class TDDCycleInterface:
    """
    User interface for TDD cycle management providing real-time
    progress display and phase transition visualization.
    """
    
    def __init__(self):
        self.display_enabled = True
        self.progress_history: List[Dict[str, Any]] = []
        self.current_display_state = {
            "phase": None,
            "progress": 0,
            "status": "idle"
        }
        
    def display_tdd_phase(self, phase: str, feature_name: str, progress: float = 0.0) -> bool:
        """
        Display current TDD phase with progress indication.
        
        Args:
            phase: Current TDD phase (RED, GREEN, REFACTOR)
            feature_name: Name of feature being developed
            progress: Progress percentage (0.0 to 1.0)
            
        Returns:
            bool: Display success status
        """
        try:
            if not self.display_enabled:
                return True
                
            # Update display state
            self.current_display_state = {
                "phase": phase,
                "feature_name": feature_name,
                "progress": progress,
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
            
            # Create phase-specific display
            phase_display = self._create_phase_display(phase, feature_name, progress)
            
            # Output to console (in real implementation, would use proper UI framework)
            if self.display_enabled:
                print(phase_display)
                
            # Record in history
            self.progress_history.append(self.current_display_state.copy())
            
            logger.info(f"Displayed TDD phase: {phase} for {feature_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to display TDD phase {phase}: {e}")
            return False
    
    def show_phase_transition(self, from_phase: str, to_phase: str, feature_name: str) -> bool:
        """
        Show transition between TDD phases with validation.
        
        Args:
            from_phase: Previous phase
            to_phase: Target phase
            feature_name: Feature being developed
            
        Returns:
            bool: Transition display success
        """
        try:
            # Validate transition
            if not self._validate_phase_transition(from_phase, to_phase):
                logger.error(f"Invalid phase transition: {from_phase} → {to_phase}")
                return False
            
            # Create transition display
            transition_display = self._create_transition_display(from_phase, to_phase, feature_name)
            
            if self.display_enabled:
                print(transition_display)
                
            # Update current state
            self.current_display_state["phase"] = to_phase
            self.current_display_state["status"] = "transitioning"
            
            logger.info(f"Showed phase transition: {from_phase} → {to_phase}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to show phase transition: {e}")
            return False
    
    def display_progress_bar(self, current: int, total: int, operation: str) -> bool:
        """
        Display progress bar for current operation.
        
        Args:
            current: Current progress count
            total: Total operations
            operation: Description of operation
            
        Returns:
            bool: Display success status
        """
        try:
            if total <= 0:
                return False
                
            progress_percent = (current / total) * 100
            bar_length = 40
            filled_length = int(bar_length * current // total)
            
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            progress_display = f"\r{operation}: |{bar}| {progress_percent:.1f}% ({current}/{total})"
            
            if self.display_enabled:
                print(progress_display, end='', flush=True)
                
            # Update progress in current state
            self.current_display_state["progress"] = progress_percent / 100
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to display progress bar: {e}")
            return False
    
    def show_test_results(self, results: Dict[str, Any]) -> bool:
        """
        Display test execution results with formatting.
        
        Args:
            results: Test results dictionary
            
        Returns:
            bool: Display success status
        """
        try:
            # Format test results
            results_display = self._format_test_results(results)
            
            if self.display_enabled:
                print(results_display)
                
            logger.info("Displayed test results")
            return True
            
        except Exception as e:
            logger.error(f"Failed to display test results: {e}")
            return False
    
    def show_coverage_report(self, coverage_data: Dict[str, float]) -> bool:
        """
        Display coverage report with layer-specific breakdown.
        
        Args:
            coverage_data: Coverage percentages by layer
            
        Returns:
            bool: Display success status
        """
        try:
            coverage_display = self._format_coverage_report(coverage_data)
            
            if self.display_enabled:
                print(coverage_display)
                
            logger.info("Displayed coverage report")
            return True
            
        except Exception as e:
            logger.error(f"Failed to display coverage report: {e}")
            return False
    
    def get_current_display_state(self) -> Dict[str, Any]:
        """Get current display state"""
        return self.current_display_state.copy()
    
    def get_progress_history(self) -> List[Dict[str, Any]]:
        """Get progress display history"""
        return self.progress_history.copy()
    
    def enable_display(self) -> None:
        """Enable display output"""
        self.display_enabled = True
        
    def disable_display(self) -> None:
        """Disable display output (for testing)"""
        self.display_enabled = False
    
    def _create_phase_display(self, phase: str, feature_name: str, progress: float) -> str:
        """Create formatted phase display"""
        phase_colors = {
            "RED": "🔴",
            "GREEN": "🟢", 
            "REFACTOR": "🔵"
        }
        
        phase_icon = phase_colors.get(phase, "⚪")
        progress_bar = self._create_mini_progress_bar(progress)
        
        return f"""
{'='*60}
{phase_icon} TDD PHASE: {phase}
Feature: {feature_name}
Progress: {progress_bar} {progress*100:.1f}%
Time: {datetime.now().strftime('%H:%M:%S')}
{'='*60}
"""
    
    def _create_transition_display(self, from_phase: str, to_phase: str, feature_name: str) -> str:
        """Create formatted transition display"""
        return f"""
🔄 PHASE TRANSITION
{from_phase} ➜ {to_phase}
Feature: {feature_name}
Time: {datetime.now().strftime('%H:%M:%S')}
"""
    
    def _create_mini_progress_bar(self, progress: float) -> str:
        """Create mini progress bar"""
        bar_length = 20
        filled = int(bar_length * progress)
        return '█' * filled + '░' * (bar_length - filled)
    
    def _validate_phase_transition(self, from_phase: str, to_phase: str) -> bool:
        """Validate if phase transition is allowed"""
        valid_transitions = {
            "RED": ["GREEN"],
            "GREEN": ["REFACTOR"],
            "REFACTOR": ["COMPLETE", "RED"],  # Can start new cycle
            "COMPLETE": ["RED"]
        }
        
        return to_phase in valid_transitions.get(from_phase, [])
    
    def _format_test_results(self, results: Dict[str, Any]) -> str:
        """Format test results for display"""
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        total = passed + failed
        
        return f"""
📊 TEST RESULTS
Passed: {passed}
Failed: {failed}
Total: {total}
Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%
"""
    
    def _format_coverage_report(self, coverage_data: Dict[str, float]) -> str:
        """Format coverage report for display"""
        report = "\n📈 COVERAGE REPORT\n"
        report += "-" * 30 + "\n"
        
        for layer, percentage in coverage_data.items():
            status = "✅" if percentage >= 85 else "❌"
            report += f"{status} {layer}: {percentage:.1f}%\n"
            
        return report

if __name__ == "__main__":
    # Basic functionality test
    ui = TDDCycleInterface()
    ui.display_tdd_phase("RED", "test_feature", 0.3)
    ui.show_phase_transition("RED", "GREEN", "test_feature")
    ui.display_progress_bar(30, 100, "Running tests")
    print("\nCurrent state:", ui.get_current_display_state())