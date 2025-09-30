#!/usr/bin/env python3
"""
Test Suite for TDD Progress Formatter - Phase 2C UI Layer

Comprehensive testing for TR-UI-003: TDD Progress & Feedback Display
Tests the TDD Progress Formatter's ability to provide real-time visual feedback
for TDD workflow execution.
"""

import pytest
import io
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime
from contextlib import redirect_stdout

# Add src to path for imports
# Import (using root src - not PROJECT-003 specific)
sys.path.append('/workspaces/control_tower/src')

from ui.tdd_progress_formatter import (
    TDDProgressFormatter, ProgressState, ProgressUpdate,
    ColorScheme
)
from business_logic.tdd_workflow_engine import (
    TDDPhase, WorkflowResult, TestingPyramidLevel, TestExecutionResult,
    ValidationResult, TraceabilityReport, ComplianceReport
)


class TestTDDProgressFormatter:
    """Test suite for TDD Progress Formatter"""
    
    @pytest.fixture
    def formatter(self):
        """Create TDD progress formatter for testing"""
        return TDDProgressFormatter()
    
    @pytest.fixture
    def mock_tdd_result(self):
        """Create mock TDD result for testing"""
        return WorkflowResult(
            success=True,
            message="TDD cycle completed successfully",
            tests_generated=True,
            red_phase_completed=True,
            green_phase_completed=True,
            refactor_phase_completed=True,
            implementation_completed=True,
            final_test_status=TestExecutionResult(
                level=TestingPyramidLevel.UNIT,
                success=True,
                execution_time=2.5,
                all_passing=True,
                total_tests=12,
                tests_passed=12,
                tests_failed=0
            )
        )
    
    @pytest.fixture
    def mock_validation_result(self):
        """Create mock validation result for testing"""
        return ValidationResult(
            total_requirements=5,
            validated_requirements=5,
            issues=[],
            compliance_percentage=100.0
        )
    
    @pytest.fixture
    def mock_traceability_report(self):
        """Create mock traceability report for testing"""
        return TraceabilityReport(
            total_requirements=5,
            traced_requirements=5,
            coverage_percentage=100.0,
            orphaned_tests=[],
            untested_requirements=[]
        )

    def test_formatter_initialization(self):
        """Test TDD progress formatter initialization"""
        formatter = TDDProgressFormatter()
        
        assert formatter is not None
        assert isinstance(formatter, TDDProgressFormatter)
        assert formatter.colors is not None
        assert formatter._current_progress == []
        assert formatter._start_time is None

    def test_start_workflow_display(self, formatter):
        """Test workflow display initialization"""
        # Capture output
        output = io.StringIO()
        
        with redirect_stdout(output):
            formatter.start_workflow_display("TEST-001", "Test Feature Implementation")
        
        captured = output.getvalue()
        
        # Verify header content
        assert "🏗️ Starting TDD workflow for: Test Feature Implementation" in captured
        assert "=" in captured  # Header separator
        assert formatter._start_time is not None
        assert formatter._current_progress == []

    def test_progress_update_initialization(self, formatter):
        """Test initialization progress update display"""
        update = ProgressUpdate(
            state=ProgressState.INITIALIZING,
            message="Creating safety checkpoint...",
            success=True
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "✅" in captured  # Success icon
        assert "Creating safety checkpoint..." in captured
        assert len(formatter._current_progress) == 1

    def test_progress_update_requirements_parsing(self, formatter):
        """Test requirements parsing progress display"""
        update = ProgressUpdate(
            state=ProgressState.PARSING_REQUIREMENTS,
            message="Parsing Business Logic Layer requirements...",
            details={
                'acceptance_criteria_count': 4,
                'project_type': 'APPLICATION'
            }
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "🔍" in captured  # Parsing icon
        assert "Parsing Business Logic Layer requirements..." in captured
        assert "4 acceptance criteria found (APPLICATION)" in captured

    def test_progress_update_test_generation(self, formatter):
        """Test test generation progress display"""
        update = ProgressUpdate(
            state=ProgressState.GENERATING_TESTS,
            message="Creating failing tests...",
            success=True,
            details={
                'passing_tests': 0,
                'total_tests': 4
            }
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "📝" in captured  # Test generation icon
        assert "Creating failing tests..." in captured
        assert "✅ Failing tests created (0/4 passing)" in captured

    def test_progress_update_red_phase(self, formatter):
        """Test RED phase progress display"""
        update = ProgressUpdate(
            state=ProgressState.RED_PHASE,
            phase=TDDPhase.RED,
            message="Running RED phase...",
            success=True,
            details={
                'duration_seconds': 1.2,
                'test_results': {
                    'passing': 0,
                    'total': 4
                }
            }
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "🔴" in captured  # RED phase icon
        assert "RED Phase" in captured
        assert "Running RED phase..." in captured
        assert "✅" in captured  # Success icon
        assert "Tests: 0/4 passing (1.2s)" in captured

    def test_progress_update_green_phase(self, formatter):
        """Test GREEN phase progress display"""
        update = ProgressUpdate(
            state=ProgressState.GREEN_PHASE,
            phase=TDDPhase.GREEN,
            message="Running GREEN phase...",
            success=True,
            details={
                'duration_seconds': 2.1,
                'test_results': {
                    'passing': 4,
                    'total': 4
                }
            }
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "🟢" in captured  # GREEN phase icon
        assert "GREEN Phase" in captured
        assert "Running GREEN phase..." in captured
        assert "✅" in captured  # Success icon
        assert "Tests: 4/4 passing (2.1s)" in captured

    def test_progress_update_refactor_phase(self, formatter):
        """Test REFACTOR phase progress display"""
        update = ProgressUpdate(
            state=ProgressState.REFACTOR_PHASE,
            phase=TDDPhase.REFACTOR,
            message="Running REFACTOR phase...",
            success=True,
            details={
                'duration_seconds': 0.8,
                'test_results': {
                    'passing': 4,
                    'total': 4
                }
            }
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "🔵" in captured  # REFACTOR phase icon
        assert "REFACTOR Phase" in captured
        assert "Running REFACTOR phase..." in captured
        assert "✅" in captured  # Success icon
        assert "Tests: 4/4 passing (0.8s)" in captured

    def test_progress_update_testing_pyramid(self, formatter):
        """Test testing pyramid progress display"""
        update = ProgressUpdate(
            state=ProgressState.TESTING_PYRAMID,
            message="Running testing pyramid...",
            details={
                'pyramid_results': {
                    'unit': {
                        'executed': True,
                        'passing': 45,
                        'total': 45,
                        'duration': 2.1
                    },
                    'integration': {
                        'executed': True,
                        'passing': 12,
                        'total': 12,
                        'duration': 1.5
                    },
                    'e2e': {
                        'executed': False,
                        'skip_reason': 'UI layer not available'
                    },
                    'system': {
                        'executed': False,
                        'skip_reason': 'System incomplete'
                    }
                }
            }
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "🧪" in captured  # Testing pyramid icon
        assert "Running testing pyramid..." in captured
        assert "Unit tests... ✅ 45/45 PASS (2.1s)" in captured
        assert "Integration tests... ✅ 12/12 PASS (1.5s)" in captured
        assert "E2e tests... ⏭️ SKIPPED (UI layer not available)" in captured
        assert "System tests... ⏭️ SKIPPED (System incomplete)" in captured

    def test_progress_update_validation(self, formatter):
        """Test validation progress display"""
        update = ProgressUpdate(
            state=ProgressState.VALIDATION,
            message="Validating requirements...",
            success=True,
            details={
                'functional_passed': 4,
                'functional_total': 4,
                'business_passed': 5,
                'business_total': 5,
                'acceptance_passed': 6,
                'acceptance_total': 6,
                'compliance_score': 100.0
            }
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "🎯" in captured  # Validation icon
        assert "Validation: 4/4 functional, 5/5 business, 6/6 acceptance criteria PASS" in captured
        assert "✅" in captured  # Success icon
        assert "Overall Compliance: 100.0%" in captured

    def test_progress_update_completion_success(self, formatter):
        """Test successful completion display"""
        formatter._start_time = datetime.now()
        
        update = ProgressUpdate(
            state=ProgressState.COMPLETION,
            message="Feature completed successfully",
            success=True
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "🚀 Feature completed successfully!" in captured
        assert "Pushed to git" in captured
        assert "🎯 Continue with next feature or run 'make what-next'" in captured

    def test_progress_update_completion_failure(self, formatter):
        """Test failed completion display"""
        update = ProgressUpdate(
            state=ProgressState.COMPLETION,
            message="Test generation failed",
            success=False,
            details={
                'recovery_suggestions': [
                    "Check requirements file format",
                    "Verify acceptance criteria are testable"
                ]
            }
        )
        
        output = io.StringIO()
        with redirect_stdout(output):
            formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "❌ Workflow failed: Test generation failed" in captured
        assert "💡 Recovery suggestions:" in captured
        assert "Check requirements file format" in captured
        assert "Verify acceptance criteria are testable" in captured

    def test_display_tdd_result_success(self, formatter, mock_tdd_result):
        """Test TDD result display for successful workflow"""
        output = io.StringIO()
        
        with redirect_stdout(output):
            formatter.display_tdd_result(mock_tdd_result)
        
        captured = output.getvalue()
        
        assert "📊 TDD Workflow Summary" in captured
        assert "Status: ✅ SUCCESS" in captured
        assert "Tests Generated: ✅" in captured
        assert "RED Phase: ✅" in captured
        assert "GREEN Phase: ✅" in captured
        assert "REFACTOR Phase: ✅" in captured
        assert "Implementation: ✅" in captured
        assert "Final Tests: ALL PASSING" in captured

    def test_display_tdd_result_failure(self, formatter):
        """Test TDD result display for failed workflow"""
        failed_result = WorkflowResult(
            success=False,
            message="RED phase failed",
            tests_generated=True,
            red_phase_completed=False,
            green_phase_completed=False,
            refactor_phase_completed=False,
            implementation_completed=False,
            final_test_status=TestExecutionResult(
                level=TestingPyramidLevel.UNIT,
                success=False,
                execution_time=1.2,
                all_passing=False,
                total_tests=4,
                tests_passed=0,
                tests_failed=4
            )
        )
        
        output = io.StringIO()
        
        with redirect_stdout(output):
            formatter.display_tdd_result(failed_result)
        
        captured = output.getvalue()
        
        assert "📊 TDD Workflow Summary" in captured
        assert "Status: ❌ FAILED" in captured
        assert "Tests Generated: ✅" in captured
        assert "RED Phase: ❌" in captured
        assert "GREEN Phase: ❌" in captured
        assert "REFACTOR Phase: ❌" in captured
        assert "Implementation: ❌" in captured
        assert "Final Tests: FAILURES" in captured

    def test_display_validation_result(self, formatter, mock_validation_result):
        """Test validation result display"""
        output = io.StringIO()
        
        with redirect_stdout(output):
            formatter.display_validation_result(mock_validation_result)
        
        captured = output.getvalue()
        
        assert "🔍 Requirements Validation" in captured
        assert "Total Requirements: 5" in captured
        assert "Validated Requirements: 5" in captured
        assert "Compliance: 100.0%" in captured

    def test_display_validation_result_with_failures(self, formatter):
        """Test validation result display with failures"""
        validation_with_failures = ValidationResult(
            total_requirements=5,
            validated_requirements=3,
            issues=[
                "Acceptance criteria AC-001 not implemented",
                "Business rule BR-002 validation failed"
            ],
            compliance_percentage=60.0
        )
        
        output = io.StringIO()
        
        with redirect_stdout(output):
            formatter.display_validation_result(validation_with_failures)
        
        captured = output.getvalue()
        
        assert "🔍 Requirements Validation" in captured
        assert "Total Requirements: 5" in captured
        assert "Validated Requirements: 3" in captured
        assert "Compliance: 60.0%" in captured
        assert "Issues Found:" in captured
        assert "Acceptance criteria AC-001 not implemented" in captured
        assert "Business rule BR-002 validation failed" in captured

    def test_display_traceability_report(self, formatter, mock_traceability_report):
        """Test traceability report display"""
        output = io.StringIO()
        
        with redirect_stdout(output):
            formatter.display_traceability_report(mock_traceability_report)
        
        captured = output.getvalue()
        
        assert "📋 Traceability Report" in captured
        assert "Total Requirements: 5" in captured
        assert "Traced Requirements: 5" in captured
        assert "Coverage: 100.0%" in captured

    def test_display_traceability_report_with_issues(self, formatter):
        """Test traceability report display with orphaned tests and untested requirements"""
        traceability_with_issues = TraceabilityReport(
            total_requirements=5,
            traced_requirements=4,
            coverage_percentage=80.0,
            orphaned_tests=[
                "test_obsolete_feature.py"
            ],
            untested_requirements=[
                "REQ-005: Performance optimization"
            ]
        )
        
        output = io.StringIO()
        
        with redirect_stdout(output):
            formatter.display_traceability_report(traceability_with_issues)
        
        captured = output.getvalue()
        
        assert "📋 Traceability Report" in captured
        assert "Total Requirements: 5" in captured
        assert "Traced Requirements: 4" in captured
        assert "Coverage: 80.0%" in captured
        assert "Orphaned Tests:" in captured
        assert "test_obsolete_feature.py" in captured
        assert "Untested Requirements:" in captured
        assert "REQ-005: Performance optimization" in captured

    @patch('builtins.input', return_value='1')
    def test_prompt_next_action(self, mock_input, formatter):
        """Test next action prompting"""
        output = io.StringIO()
        
        with redirect_stdout(output):
            choice = formatter.prompt_next_action()
        
        captured = output.getvalue()
        
        assert choice == '1'
        assert "What would you like to do next?" in captured
        assert "1. Continue with next priority (make what-next)" in captured
        assert "2. Start another work item (make work TASK=<id>)" in captured
        assert "3. Review completed work" in captured
        assert "4. Exit" in captured

    @patch('builtins.input', side_effect=['invalid', '5', '2'])
    def test_prompt_next_action_invalid_input(self, mock_input, formatter):
        """Test next action prompting with invalid input"""
        output = io.StringIO()
        
        with redirect_stdout(output):
            choice = formatter.prompt_next_action()
        
        captured = output.getvalue()
        
        assert choice == '2'
        assert "Please enter 1, 2, 3, or 4" in captured

    @patch('builtins.input', side_effect=KeyboardInterrupt())
    def test_prompt_next_action_keyboard_interrupt(self, mock_input, formatter):
        """Test next action prompting with keyboard interrupt"""
        output = io.StringIO()
        
        with redirect_stdout(output):
            choice = formatter.prompt_next_action()
        
        captured = output.getvalue()
        
        assert choice == '4'
        assert "Workflow interrupted by user" in captured

    def test_display_workflow_header(self, formatter):
        """Test workflow header display"""
        output = io.StringIO()
        
        with redirect_stdout(output):
            formatter.display_workflow_header(
                work_item_id="FEATURE-001-05-02",
                title="Automated Rebalancing Execution",
                hierarchy_level="Feature"
            )
        
        captured = output.getvalue()
        
        assert "🏗️ TDD WORKFLOW EXECUTION" in captured
        assert "Work Item: FEATURE-001-05-02" in captured
        assert "Title: Automated Rebalancing Execution" in captured
        assert "Level: Feature" in captured
        assert "Started:" in captured

    def test_color_scheme_integration(self):
        """Test color scheme integration with parent class"""
        custom_colors = ColorScheme()
        custom_colors.GREEN = "\033[92m"  # Bright green
        
        formatter = TDDProgressFormatter(custom_colors)
        
        assert formatter.colors.GREEN == "\033[92m"
        assert formatter.colors == custom_colors

    def test_progress_state_enum_coverage(self):
        """Test all progress states are handled"""
        all_states = list(ProgressState)
        
        # Verify all states we expect are present
        expected_states = [
            ProgressState.INITIALIZING,
            ProgressState.PARSING_REQUIREMENTS,
            ProgressState.GENERATING_TESTS,
            ProgressState.RED_PHASE,
            ProgressState.GREEN_PHASE,
            ProgressState.REFACTOR_PHASE,
            ProgressState.TESTING_PYRAMID,
            ProgressState.VALIDATION,
            ProgressState.COMPLETION
        ]
        
        for state in expected_states:
            assert state in all_states

    def test_progress_update_timestamp_auto_generation(self):
        """Test progress update automatically generates timestamp"""
        update = ProgressUpdate(
            state=ProgressState.INITIALIZING,
            message="Test message"
        )
        
        assert update.timestamp is not None
        assert isinstance(update.timestamp, datetime)

    def test_integration_with_parent_formatter(self, formatter):
        """Test integration with parent TerminalFormatter functionality"""
        # TDD Progress Formatter should inherit all parent functionality
        assert hasattr(formatter, 'format_work_items')
        assert hasattr(formatter, 'colors')
        
        # Test that parent functionality still works
        assert formatter.colors.RED == "\033[31m"
        assert formatter.colors.GREEN == "\033[32m"
        assert formatter.colors.RESET == "\033[0m"


# Additional end-to-end UI integration tests
class TestTDDProgressFormatterIntegration:
    """Integration tests for TDD Progress Formatter with business logic"""
    
    def test_complete_workflow_display_simulation(self):
        """Test complete workflow display from start to finish"""
        formatter = TDDProgressFormatter()
        
        # Capture all output
        output = io.StringIO()
        
        with redirect_stdout(output):
            # Start workflow
            formatter.start_workflow_display(
                "FEATURE-001-05-02", 
                "Automated Rebalancing Execution"
            )
            
            # Simulate complete workflow progression
            workflow_updates = [
                ProgressUpdate(ProgressState.INITIALIZING, message="Creating safety checkpoint...", success=True),
                ProgressUpdate(ProgressState.PARSING_REQUIREMENTS, message="Parsing requirements...", details={'acceptance_criteria_count': 5, 'project_type': 'APPLICATION'}),
                ProgressUpdate(ProgressState.GENERATING_TESTS, message="Creating failing tests...", success=True, details={'passing_tests': 0, 'total_tests': 5}),
                ProgressUpdate(ProgressState.RED_PHASE, phase=TDDPhase.RED, message="Running RED phase...", success=True, details={'duration_seconds': 1.2, 'test_results': {'passing': 0, 'total': 5}}),
                ProgressUpdate(ProgressState.GREEN_PHASE, phase=TDDPhase.GREEN, message="Running GREEN phase...", success=True, details={'duration_seconds': 2.8, 'test_results': {'passing': 5, 'total': 5}}),
                ProgressUpdate(ProgressState.REFACTOR_PHASE, phase=TDDPhase.REFACTOR, message="Running REFACTOR phase...", success=True, details={'duration_seconds': 1.1, 'test_results': {'passing': 5, 'total': 5}}),
                ProgressUpdate(ProgressState.TESTING_PYRAMID, message="Running testing pyramid...", details={
                    'pyramid_results': {
                        'unit': {'executed': True, 'passing': 15, 'total': 15, 'duration': 1.2},
                        'integration': {'executed': True, 'passing': 8, 'total': 8, 'duration': 2.1},
                        'e2e': {'executed': False, 'skip_reason': 'UI layer not available'},
                        'system': {'executed': False, 'skip_reason': 'System incomplete'}
                    }
                }),
                ProgressUpdate(ProgressState.VALIDATION, message="Validating requirements...", success=True, details={
                    'functional_passed': 5, 'functional_total': 5,
                    'business_passed': 3, 'business_total': 3,
                    'acceptance_passed': 5, 'acceptance_total': 5,
                    'compliance_score': 100.0
                }),
                ProgressUpdate(ProgressState.COMPLETION, message="Feature completed successfully", success=True)
            ]
            
            for update in workflow_updates:
                formatter.update_progress(update)
        
        captured = output.getvalue()
        
        # Verify complete workflow is represented
        assert "🏗️ Starting TDD workflow for: Automated Rebalancing Execution" in captured
        assert "Creating safety checkpoint..." in captured
        assert "5 acceptance criteria found (APPLICATION)" in captured
        assert "✅ Failing tests created (0/5 passing)" in captured
        assert "🔴 RED Phase" in captured
        assert "🟢 GREEN Phase" in captured
        assert "🔵 REFACTOR Phase" in captured
        assert "Unit tests... ✅ 15/15 PASS" in captured
        assert "Integration tests... ✅ 8/8 PASS" in captured
        assert "E2e tests... ⏭️ SKIPPED" in captured
        assert "Validation: 5/5 functional, 3/3 business, 5/5 acceptance criteria PASS" in captured
        assert "Overall Compliance: 100.0%" in captured
        assert "🚀 Feature completed successfully!" in captured
        assert "🎯 Continue with next feature" in captured

    def test_error_scenario_display(self):
        """Test error scenario display throughout workflow"""
        formatter = TDDProgressFormatter()
        output = io.StringIO()
        
        with redirect_stdout(output):
            # Simulate workflow that fails at GREEN phase
            error_updates = [
                ProgressUpdate(ProgressState.INITIALIZING, message="Creating safety checkpoint...", success=True),
                ProgressUpdate(ProgressState.PARSING_REQUIREMENTS, message="Parsing requirements...", success=True),
                ProgressUpdate(ProgressState.GENERATING_TESTS, message="Creating failing tests...", success=True),
                ProgressUpdate(ProgressState.RED_PHASE, message="Running RED phase...", success=True),
                ProgressUpdate(ProgressState.GREEN_PHASE, message="Implementation generation failed", success=False),
                ProgressUpdate(ProgressState.COMPLETION, message="Implementation generation failed", success=False, details={
                    'recovery_suggestions': [
                        "Review acceptance criteria clarity",
                        "Check for missing dependencies"
                    ]
                })
            ]
            
            for update in error_updates:
                formatter.update_progress(update)
        
        captured = output.getvalue()
        
        assert "🟢 GREEN Phase: Implementation generation failed ❌" in captured
        assert "❌ Workflow failed: Implementation generation failed" in captured
        assert "💡 Recovery suggestions:" in captured
        assert "Review acceptance criteria clarity" in captured
        assert "Check for missing dependencies" in captured


if __name__ == "__main__":
    pytest.main([__file__, "-v"])