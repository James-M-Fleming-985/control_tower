#!/usr/bin/env python3
"""
TDD Progress Formatter - UI Layer Implementation for Phase 2C

Extends existing TerminalFormatter with TDD workflow progress display capabilities.
Implements TR-UI-003: TDD Progress & Feedback Display requirements.

This component provides real-time visual feedback for:
- TDD cycle phases (RED-GREEN-REFACTOR)
- Testing pyramid execution  
- Requirements validation
- Workflow completion and next steps
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Import existing UI foundation from Phase 1
from src.ui.terminal_formatter import TerminalFormatter, ColorScheme

# Import Phase 2B business logic models  
from src.business_logic.tdd_workflow_engine import (
    TDDPhase, WorkflowResult, TestingPyramidLevel, TestExecutionResult,
    ValidationResult, TraceabilityReport, ComplianceReport
)


class ProgressState(Enum):
    """TDD workflow progress states for display"""
    INITIALIZING = "initializing"
    PARSING_REQUIREMENTS = "parsing_requirements" 
    GENERATING_TESTS = "generating_tests"
    RED_PHASE = "red_phase"
    GREEN_PHASE = "green_phase"
    REFACTOR_PHASE = "refactor_phase"
    TESTING_PYRAMID = "testing_pyramid"
    VALIDATION = "validation"
    COMPLETION = "completion"


@dataclass
class ProgressUpdate:
    """Individual progress update for TDD workflow"""
    state: ProgressState
    phase: Optional[TDDPhase] = None
    message: str = ""
    success: bool = True
    details: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.details is None:
            self.details = {}


class TDDProgressFormatter(TerminalFormatter):
    """
    TDD Progress Formatter - Extends TerminalFormatter for workflow feedback
    
    Provides real-time visual feedback for TDD workflow execution including:
    - TDD cycle phase progress with visual indicators
    - Testing pyramid execution with detailed metrics
    - Requirements validation with compliance reporting
    - Workflow completion with next-step guidance
    
    Extends Phase 1 TerminalFormatter to maintain consistent visual design.
    """
    
    def __init__(self, color_scheme: Optional[ColorScheme] = None):
        """Initialize TDD progress formatter"""
        super().__init__(color_scheme)
        self._current_progress: List[ProgressUpdate] = []
        self._start_time = None
        
    def start_workflow_display(self, work_item_id: str, title: str) -> None:
        """
        Start TDD workflow display with header
        
        Args:
            work_item_id: Work item identifier
            title: Work item title/description
        """
        self._start_time = datetime.now()
        self._current_progress = []
        
        header = f"{self.colors.BRIGHT_CYAN}🏗️ Starting TDD workflow for: {title}{self.colors.RESET}"
        print(header)
        print("=" * min(len(title) + 30, 80))
    
    def update_progress(self, update: ProgressUpdate) -> None:
        """
        Update and display current progress
        
        Args:
            update: Progress update to display
        """
        self._current_progress.append(update)
        self._display_progress_update(update)
    
    def _display_progress_update(self, update: ProgressUpdate) -> None:
        """Display individual progress update with appropriate formatting"""
        
        # State-specific formatting
        if update.state == ProgressState.INITIALIZING:
            self._display_initialization(update)
        elif update.state == ProgressState.PARSING_REQUIREMENTS:
            self._display_requirements_parsing(update)
        elif update.state == ProgressState.GENERATING_TESTS:
            self._display_test_generation(update)
        elif update.state in [ProgressState.RED_PHASE, ProgressState.GREEN_PHASE, ProgressState.REFACTOR_PHASE]:
            self._display_tdd_phase(update)
        elif update.state == ProgressState.TESTING_PYRAMID:
            self._display_testing_pyramid(update)
        elif update.state == ProgressState.VALIDATION:
            self._display_validation(update)
        elif update.state == ProgressState.COMPLETION:
            self._display_completion(update)
    
    def _display_initialization(self, update: ProgressUpdate) -> None:
        """Display workflow initialization progress"""
        if update.success:
            icon = f"{self.colors.GREEN}✅{self.colors.RESET}"
        else:
            icon = f"{self.colors.RED}❌{self.colors.RESET}"
        
        print(f"{icon} {update.message}")
    
    def _display_requirements_parsing(self, update: ProgressUpdate) -> None:
        """Display requirements parsing progress"""
        icon = f"{self.colors.BLUE}🔍{self.colors.RESET}"
        print(f"{icon} {update.message}")
        
        if update.details:
            num_criteria = update.details.get('acceptance_criteria_count', 0)
            project_type = update.details.get('project_type', 'Unknown')
            print(f"   └── {num_criteria} acceptance criteria found ({project_type})")
    
    def _display_test_generation(self, update: ProgressUpdate) -> None:
        """Display test generation progress"""
        icon = f"{self.colors.YELLOW}📝{self.colors.RESET}"
        
        if update.success:
            passing_tests = update.details.get('passing_tests', 0)
            total_tests = update.details.get('total_tests', 0)
            status = f"{self.colors.GREEN}✅ Failing tests created ({passing_tests}/{total_tests} passing){self.colors.RESET}"
        else:
            status = f"{self.colors.RED}❌ Test generation failed{self.colors.RESET}"
        
        print(f"{icon} {update.message} {status}")
    
    def _display_tdd_phase(self, update: ProgressUpdate) -> None:
        """Display TDD phase progress (RED/GREEN/REFACTOR)"""
        
        # Phase-specific colors and icons
        phase_config = {
            ProgressState.RED_PHASE: {
                'color': self.colors.RED,
                'icon': '🔴',
                'name': 'RED'
            },
            ProgressState.GREEN_PHASE: {
                'color': self.colors.GREEN, 
                'icon': '🟢',
                'name': 'GREEN'
            },
            ProgressState.REFACTOR_PHASE: {
                'color': self.colors.BLUE,
                'icon': '🔵', 
                'name': 'REFACTOR'
            }
        }
        
        config = phase_config[update.state]
        status_icon = f"{self.colors.GREEN}✅{self.colors.RESET}" if update.success else f"{self.colors.RED}❌{self.colors.RESET}"
        
        print(f"{config['icon']} {config['color']}{config['name']} Phase{self.colors.RESET}: {update.message} {status_icon}")
        
        # Show details if available
        if update.details:
            duration = update.details.get('duration_seconds', 0)
            test_results = update.details.get('test_results', {})
            if test_results:
                passing = test_results.get('passing', 0)
                total = test_results.get('total', 0)
                print(f"   └── Tests: {passing}/{total} passing ({duration:.1f}s)")
    
    def _display_testing_pyramid(self, update: ProgressUpdate) -> None:
        """Display testing pyramid execution progress"""
        icon = f"{self.colors.PURPLE}🧪{self.colors.RESET}"
        print(f"{icon} Running testing pyramid...")
        
        if update.details:
            pyramid_results = update.details.get('pyramid_results', {})
            
            for level_name, result in pyramid_results.items():
                if result.get('executed', False):
                    passing = result.get('passing', 0)
                    total = result.get('total', 0)
                    duration = result.get('duration', 0)
                    status = f"{self.colors.GREEN}✅ {passing}/{total} PASS{self.colors.RESET}"
                    print(f"   ├── {level_name.title()} tests... {status} ({duration:.1f}s)")
                else:
                    reason = result.get('skip_reason', 'Not available')
                    status = f"{self.colors.YELLOW}⏭️ SKIPPED{self.colors.RESET}"
                    print(f"   ├── {level_name.title()} tests... {status} ({reason})")
    
    def _display_validation(self, update: ProgressUpdate) -> None:
        """Display requirements validation progress"""
        icon = f"{self.colors.CYAN}🎯{self.colors.RESET}"
        
        if update.success:
            details = update.details or {}
            functional = details.get('functional_passed', 0)
            functional_total = details.get('functional_total', 0)
            business = details.get('business_passed', 0)
            business_total = details.get('business_total', 0)
            acceptance = details.get('acceptance_passed', 0)
            acceptance_total = details.get('acceptance_total', 0)
            
            validation_text = f"Validation: {functional}/{functional_total} functional, {business}/{business_total} business, {acceptance}/{acceptance_total} acceptance criteria PASS"
            status = f"{self.colors.GREEN}✅{self.colors.RESET}"
        else:
            validation_text = "Validation failed"
            status = f"{self.colors.RED}❌{self.colors.RESET}"
        
        print(f"{icon} {validation_text} {status}")
        
        # Show compliance score if available
        if update.details and 'compliance_score' in update.details:
            score = update.details['compliance_score']
            score_color = self.colors.GREEN if score >= 90 else self.colors.YELLOW if score >= 70 else self.colors.RED
            print(f"   └── Overall Compliance: {score_color}{score:.1f}%{self.colors.RESET}")
    
    def _display_completion(self, update: ProgressUpdate) -> None:
        """Display workflow completion with next steps"""
        if update.success:
            # Calculate total duration
            total_duration = ""
            if self._start_time:
                duration = datetime.now() - self._start_time
                total_duration = f" ({duration.total_seconds():.1f}s)"
            
            timestamp = update.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n{self.colors.BRIGHT_GREEN}🚀 Feature completed successfully!{self.colors.RESET} Pushed to git [{timestamp}]{total_duration}")
            print(f"{self.colors.BRIGHT_CYAN}🎯 Continue with next feature or run 'make what-next' for other priorities?{self.colors.RESET}")
        else:
            print(f"\n{self.colors.RED}❌ Workflow failed: {update.message}{self.colors.RESET}")
            if update.details and 'recovery_suggestions' in update.details:
                print(f"{self.colors.YELLOW}💡 Recovery suggestions:{self.colors.RESET}")
                for suggestion in update.details['recovery_suggestions']:
                    print(f"   • {suggestion}")
    
    def display_tdd_result(self, result: WorkflowResult) -> None:
        """
        Display comprehensive TDD result summary
        
        Args:
            result: Complete TDD workflow result
        """
        print(f"\n{self.colors.BOLD}📊 TDD Workflow Summary{self.colors.RESET}")
        print("=" * 40)
        
        # Overall success
        overall_status = f"{self.colors.GREEN}✅ SUCCESS{self.colors.RESET}" if result.success else f"{self.colors.RED}❌ FAILED{self.colors.RESET}"
        print(f"Status: {overall_status}")
        
        # Phase completion
        phases = [
            ("Tests Generated", result.tests_generated),
            ("RED Phase", result.red_phase_completed),
            ("GREEN Phase", result.green_phase_completed), 
            ("REFACTOR Phase", result.refactor_phase_completed),
            ("Implementation", result.implementation_completed)
        ]
        
        for phase_name, completed in phases:
            status = f"{self.colors.GREEN}✅{self.colors.RESET}" if completed else f"{self.colors.RED}❌{self.colors.RESET}"
            print(f"  {phase_name}: {status}")
        
        # Final test status
        if result.final_test_status:
            test_status = "ALL PASSING" if result.final_test_status.all_passing else "FAILURES"
            test_color = self.colors.GREEN if result.final_test_status.all_passing else self.colors.RED
            print(f"  Final Tests: {test_color}{test_status}{self.colors.RESET}")
    
    def display_validation_result(self, validation: ValidationResult) -> None:
        """
        Display requirements validation results
        
        Args:
            validation: Validation result to display
        """
        print(f"\n{self.colors.BOLD}🔍 Requirements Validation{self.colors.RESET}")
        print("-" * 30)
        
        compliance = (validation.validated_requirements / validation.total_requirements * 100) if validation.total_requirements > 0 else 0
        
        print(f"Total Requirements: {validation.total_requirements}")
        print(f"Validated Requirements: {validation.validated_requirements}")
        
        compliance_color = self.colors.GREEN if compliance >= 90 else self.colors.YELLOW if compliance >= 70 else self.colors.RED
        print(f"Compliance: {compliance_color}{compliance:.1f}%{self.colors.RESET}")
        
        if validation.issues:
            print(f"\n{self.colors.RED}Issues Found:{self.colors.RESET}")
            for issue in validation.issues:
                print(f"  • {issue}")
    
    def display_traceability_report(self, traceability: TraceabilityReport) -> None:
        """
        Display requirements traceability report
        
        Args:
            traceability: Traceability report to display
        """
        print(f"\n{self.colors.BOLD}📋 Traceability Report{self.colors.RESET}")
        print("-" * 25)
        
        print(f"Total Requirements: {traceability.total_requirements}")
        print(f"Traced Requirements: {traceability.traced_requirements}")
        
        coverage_color = self.colors.GREEN if traceability.coverage_percentage >= 90 else self.colors.YELLOW if traceability.coverage_percentage >= 70 else self.colors.RED
        print(f"Coverage: {coverage_color}{traceability.coverage_percentage:.1f}%{self.colors.RESET}")
        
        if traceability.orphaned_tests:
            print(f"\n{self.colors.YELLOW}Orphaned Tests:{self.colors.RESET}")
            for test in traceability.orphaned_tests:
                print(f"  • {test}")
        
        if traceability.untested_requirements:
            print(f"\n{self.colors.RED}Untested Requirements:{self.colors.RESET}")
            for req in traceability.untested_requirements:
                print(f"  • {req}")
    
    def prompt_next_action(self) -> str:
        """
        Prompt user for next action after workflow completion
        
        Returns:
            User's chosen action
        """
        print(f"\n{self.colors.BOLD}What would you like to do next?{self.colors.RESET}")
        print("1. Continue with next priority (make what-next)")
        print("2. Start another work item (make work TASK=<id>)")  
        print("3. Review completed work")
        print("4. Exit")
        
        while True:
            try:
                choice = input(f"\n{self.colors.CYAN}Choose an option (1-4): {self.colors.RESET}").strip()
                if choice in ['1', '2', '3', '4']:
                    return choice
                else:
                    print(f"{self.colors.RED}Please enter 1, 2, 3, or 4{self.colors.RESET}")
            except KeyboardInterrupt:
                print(f"\n{self.colors.YELLOW}Workflow interrupted by user{self.colors.RESET}")
                return "4"
    
    def clear_screen(self) -> None:
        """Clear terminal screen for clean display"""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_workflow_header(self, work_item_id: str, title: str, hierarchy_level: str) -> None:
        """
        Display enhanced workflow header with context
        
        Args:
            work_item_id: Work item identifier  
            title: Work item title
            hierarchy_level: Hierarchy level (Feature, System, Project, etc.)
        """
        print(f"\n{self.colors.BRIGHT_PURPLE}{'=' * 80}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_CYAN}🏗️ TDD WORKFLOW EXECUTION{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_PURPLE}{'=' * 80}{self.colors.RESET}")
        print(f"\n{self.colors.BOLD}Work Item:{self.colors.RESET} {work_item_id}")
        print(f"{self.colors.BOLD}Title:{self.colors.RESET} {title}")
        print(f"{self.colors.BOLD}Level:{self.colors.RESET} {hierarchy_level}")
        print(f"{self.colors.BOLD}Started:{self.colors.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()