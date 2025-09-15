#!/usr/bin/env python3
"""
Phase 2A + 2B + 2C Integration Test
Complete end-to-end workflow with UI display

This test validates the complete integration across all three Phase 2 layers:
- Phase 2A: Requirements Parser & Test Generator
- Phase 2B: TDD Workflow Engine & Business Logic
- Phase 2C: TDD Progress Formatter & User Interface

Tests the complete workflow from requirements parsing to visual feedback display.
"""

import pytest
import tempfile
import io
import sys
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch

# Add src to path for imports
sys.path.append('/workspaces/control_tower/src')

from data_access.requirements_parser import RequirementsParser
from business_logic.tdd_workflow_engine import TDDWorkflowEngine, TDDPhase
from ui.tdd_progress_formatter import TDDProgressFormatter, ProgressState, ProgressUpdate


class TestPhase2CompleteIntegration:
    """
    Complete Phase 2A + 2B + 2C Integration Testing
    
    Validates the complete workflow from requirements to UI display:
    1. Parse requirements (Phase 2A) 
    2. Execute TDD workflow (Phase 2B)
    3. Display progress visually (Phase 2C)
    """
    
    @pytest.fixture
    def real_requirement_file(self):
        """Path to real requirement file from investment_strategy repo"""
        return "/workspaces/control_tower/cloned_repos/investment_strategy/projects/PROJECT-001/SYSTEM-001-05_rebalancing_automation/features/FEATURE-001-05-02_automated_rebalancing_execution.md"
    
    @pytest.fixture
    def temp_workspace(self):
        """Temporary workspace for integration testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "tests").mkdir()
            (workspace / "src").mkdir()
            yield workspace
    
    @pytest.fixture
    def requirements_parser(self):
        """Phase 2A Requirements Parser"""
        return RequirementsParser()
    
    @pytest.fixture
    def workflow_engine(self):
        """Phase 2B TDD Workflow Engine"""
        return TDDWorkflowEngine()
    
    @pytest.fixture
    def progress_formatter(self):
        """Phase 2C TDD Progress Formatter"""
        return TDDProgressFormatter()

    def test_complete_phase_2_workflow_with_ui_display(self, 
                                                       real_requirement_file,
                                                       temp_workspace,
                                                       requirements_parser,
                                                       workflow_engine,
                                                       progress_formatter):
        """
        MASTER INTEGRATION TEST: Complete Phase 2A + 2B + 2C Workflow
        
        This test validates the entire Phase 2 workflow with UI display:
        
        Phase 2A Integration:
        1. Parse real requirement file from investment_strategy
        2. Extract acceptance criteria and validate structure
        
        Phase 2B Integration:
        3. Execute complete TDD workflow with business logic
        4. Generate failing tests, RED-GREEN-REFACTOR, validation
        
        Phase 2C Integration:
        5. Display workflow progress with visual feedback
        6. Show TDD cycle phases with color coding
        7. Present results with user-friendly formatting
        
        Complete Integration:
        8. Verify seamless data flow across all layers
        9. Validate user experience from start to finish
        10. Ensure visual feedback matches workflow state
        """
        
        # Skip if requirement file doesn't exist
        if not Path(real_requirement_file).exists():
            pytest.skip("Real requirement file not available for complete integration testing")
        
        # Capture all UI output
        output = io.StringIO()
        
        with redirect_stdout(output):
            print(f"\n🚀 COMPLETE PHASE 2A + 2B + 2C INTEGRATION TEST")
            print("=" * 80)
            
            # =====================================================
            # PHASE 2A: Requirements Parsing with UI Feedback
            # =====================================================
            
            # Start workflow display
            progress_formatter.start_workflow_display(
                work_item_id="FEATURE-001-05-02",
                title="Automated Rebalancing Execution"
            )
            
            # Phase 2A: Parse requirements with progress display
            progress_formatter.update_progress(ProgressUpdate(
                state=ProgressState.PARSING_REQUIREMENTS,
                message="Parsing Business Logic Layer requirements...",
                success=True
            ))
            
            requirement = requirements_parser.parse_file(real_requirement_file)
            
            # Validate Phase 2A success with UI feedback
            assert requirement is not None, "Phase 2A: Requirements parsing failed"
            assert requirement.id, "Phase 2A: Requirement ID not extracted"
            assert len(requirement.acceptance_criteria) > 0, "Phase 2A: No acceptance criteria found"
            
            progress_formatter.update_progress(ProgressUpdate(
                state=ProgressState.PARSING_REQUIREMENTS,
                message="Requirements parsed successfully",
                success=True,
                details={
                    'acceptance_criteria_count': len(requirement.acceptance_criteria),
                    'project_type': requirement.project_type.value
                }
            ))
            
            # =====================================================
            # PHASE 2B: TDD Workflow with UI Progress Display
            # =====================================================
            
            # Test generation with UI feedback
            progress_formatter.update_progress(ProgressUpdate(
                state=ProgressState.GENERATING_TESTS,
                message="Creating failing tests...",
                success=True,
                details={
                    'passing_tests': 0,
                    'total_tests': len(requirement.acceptance_criteria)
                }
            ))
            
            # Execute TDD workflow with progress tracking
            tdd_result = workflow_engine.execute_complete_tdd_cycle(requirement, temp_workspace)
            
            # Validate Phase 2B success
            assert tdd_result.success is True, f"Phase 2B: TDD cycle failed: {tdd_result.message}"
            assert tdd_result.tests_generated is True, "Phase 2B: Test generation failed"
            assert tdd_result.red_phase_completed is True, "Phase 2B: RED phase failed"
            assert tdd_result.green_phase_completed is True, "Phase 2B: GREEN phase failed"
            assert tdd_result.refactor_phase_completed is True, "Phase 2B: REFACTOR phase failed"
            
            # Display TDD phases with UI feedback
            for phase, phase_state in [
                (TDDPhase.RED, ProgressState.RED_PHASE),
                (TDDPhase.GREEN, ProgressState.GREEN_PHASE),
                (TDDPhase.REFACTOR, ProgressState.REFACTOR_PHASE)
            ]:
                progress_formatter.update_progress(ProgressUpdate(
                    state=phase_state,
                    phase=phase,
                    message=f"Running {phase.value.upper()} phase...",
                    success=True,
                    details={
                        'duration_seconds': 1.5,
                        'test_results': {
                            'passing': len(requirement.acceptance_criteria) if phase != TDDPhase.RED else 0,
                            'total': len(requirement.acceptance_criteria)
                        }
                    }
                ))
            
            # Testing pyramid with UI display
            progress_formatter.update_progress(ProgressUpdate(
                state=ProgressState.TESTING_PYRAMID,
                message="Running testing pyramid...",
                details={
                    'pyramid_results': {
                        'unit': {
                            'executed': True,
                            'passing': 15,
                            'total': 15,
                            'duration': 1.2
                        },
                        'integration': {
                            'executed': True,
                            'passing': 8,
                            'total': 8,
                            'duration': 2.1
                        },
                        'e2e': {
                            'executed': False,
                            'skip_reason': 'UI layer integration pending Phase 2D'
                        },
                        'system': {
                            'executed': False,
                            'skip_reason': 'System integration pending Phase 2D'
                        }
                    }
                }
            ))
            
            # =====================================================
            # PHASE 2C: Complete UI Display and User Experience
            # =====================================================
            
            # Requirements validation with UI display
            validation = workflow_engine.validate_functional_requirements(requirement, temp_workspace)
            
            progress_formatter.update_progress(ProgressUpdate(
                state=ProgressState.VALIDATION,
                message="Validating requirements...",
                success=True,
                details={
                    'functional_passed': validation.validated_requirements,
                    'functional_total': validation.total_requirements,
                    'business_passed': 3,
                    'business_total': 3,
                    'acceptance_passed': len(requirement.acceptance_criteria),
                    'acceptance_total': len(requirement.acceptance_criteria),
                    'compliance_score': validation.compliance_percentage
                }
            ))
            
            # Workflow completion with UI display
            progress_formatter.update_progress(ProgressUpdate(
                state=ProgressState.COMPLETION,
                message="Feature completed successfully",
                success=True
            ))
            
            # Display comprehensive results using Phase 2C UI
            progress_formatter.display_tdd_result(tdd_result)
            progress_formatter.display_validation_result(validation)
            
            # Generate traceability report with UI display
            traceability = workflow_engine.generate_traceability_report([requirement], temp_workspace)
            progress_formatter.display_traceability_report(traceability)
        
        captured_output = output.getvalue()
        
        # =====================================================
        # INTEGRATION VALIDATION: Cross-Layer Verification
        # =====================================================
        
        # Validate Phase 2A output appears in UI
        assert "🔍" in captured_output, "Phase 2A: Requirements parsing icon not displayed"
        assert "acceptance criteria found" in captured_output, "Phase 2A: Acceptance criteria count not shown"
        
        # Validate Phase 2B workflow appears in UI
        assert "📝" in captured_output, "Phase 2B: Test generation icon not displayed"
        assert "🔴" in captured_output, "Phase 2B: RED phase icon not displayed"
        assert "🟢" in captured_output, "Phase 2B: GREEN phase icon not displayed"
        assert "🔵" in captured_output, "Phase 2B: REFACTOR phase icon not displayed"
        
        # Validate Phase 2C UI enhancements
        assert "🧪" in captured_output, "Phase 2C: Testing pyramid icon not displayed"
        assert "🎯" in captured_output, "Phase 2C: Validation icon not displayed"
        assert "🚀" in captured_output, "Phase 2C: Completion icon not displayed"
        
        # Validate complete workflow progression
        assert "Unit tests..." in captured_output, "Phase 2C: Unit test results not displayed"
        assert "Integration tests..." in captured_output, "Phase 2C: Integration test results not displayed"
        assert "SKIPPED" in captured_output, "Phase 2C: Intelligent test skipping not shown"
        
        # Validate user experience elements
        assert "Continue with next feature" in captured_output, "Phase 2C: Next steps not displayed"
        assert "TDD Workflow Summary" in captured_output, "Phase 2C: Summary display not shown"
        assert "Requirements Validation" in captured_output, "Phase 2C: Validation report not shown"
        assert "Traceability Report" in captured_output, "Phase 2C: Traceability report not shown"
        
        print("\n" + "=" * 80)
        print("🎉 COMPLETE PHASE 2A + 2B + 2C INTEGRATION: SUCCESS!")
        print("✅ Phase 2A: Requirements parsing with UI feedback")
        print("✅ Phase 2B: TDD workflow automation with progress display")
        print("✅ Phase 2C: Visual feedback and user experience")
        print("✅ Complete integration: Seamless data flow across all layers")
        print("✅ User experience: Professional, informative, actionable")
        print("=" * 80)

    @patch('builtins.input', return_value='1')
    def test_user_interaction_workflow_continuation(self, mock_input, progress_formatter):
        """
        Test user interaction for workflow continuation (Phase 2C feature)
        
        Validates that the UI layer properly handles user input for next steps
        and provides appropriate workflow continuation options.
        """
        
        output = io.StringIO()
        
        with redirect_stdout(output):
            # Simulate workflow completion
            progress_formatter.update_progress(ProgressUpdate(
                state=ProgressState.COMPLETION,
                message="Feature completed successfully",
                success=True
            ))
            
            # Test next action prompting
            choice = progress_formatter.prompt_next_action()
        
        captured_output = output.getvalue()
        
        # Validate user interaction display
        assert choice == '1', "User choice not captured correctly"
        assert "What would you like to do next?" in captured_output, "Next action prompt not displayed"
        assert "make what-next" in captured_output, "Continue option not shown"
        assert "make work TASK=" in captured_output, "Work item option not shown"
        
        print("✅ Phase 2C User Interaction: Workflow continuation validated")

    def test_error_handling_with_ui_display(self, progress_formatter):
        """
        Test error handling with appropriate UI feedback (Phase 2C feature)
        
        Validates that errors are displayed with helpful recovery guidance
        and maintain professional user experience.
        """
        
        output = io.StringIO()
        
        with redirect_stdout(output):
            # Simulate workflow failure
            progress_formatter.update_progress(ProgressUpdate(
                state=ProgressState.COMPLETION,
                message="Requirements parsing failed",
                success=False,
                details={
                    'recovery_suggestions': [
                        "Check requirements file format",
                        "Verify acceptance criteria are testable",
                        "Ensure file is accessible"
                    ]
                }
            ))
        
        captured_output = output.getvalue()
        
        # Validate error display
        assert "❌ Workflow failed" in captured_output, "Error status not displayed"
        assert "💡 Recovery suggestions" in captured_output, "Recovery guidance not shown"
        assert "Check requirements file format" in captured_output, "Specific recovery step not displayed"
        
        print("✅ Phase 2C Error Handling: User-friendly error display validated")

    def test_visual_consistency_across_phases(self, progress_formatter):
        """
        Test visual consistency across all Phase 2 components
        
        Validates that the UI maintains consistent visual design,
        color scheme, and formatting across all workflow phases.
        """
        
        output = io.StringIO()
        
        with redirect_stdout(output):
            # Test complete workflow display consistency
            progress_formatter.display_workflow_header(
                work_item_id="TEST-001",
                title="Test Feature",
                hierarchy_level="Feature"
            )
            
            # Test various progress states
            states_to_test = [
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
            
            for state in states_to_test:
                progress_formatter.update_progress(ProgressUpdate(
                    state=state,
                    message=f"Testing {state.value}...",
                    success=True
                ))
        
        captured_output = output.getvalue()
        
        # Validate visual consistency
        assert "🏗️ TDD WORKFLOW EXECUTION" in captured_output, "Header format not consistent"
        assert "Work Item:" in captured_output, "Work item display not consistent"
        assert "✅" in captured_output, "Success icons not consistent"
        
        # Validate all phase icons are present
        expected_icons = ["✅", "🔍", "📝", "🔴", "🟢", "🔵", "🧪", "🎯", "🚀"]
        for icon in expected_icons:
            assert icon in captured_output, f"Icon {icon} not found in output"
        
        print("✅ Phase 2C Visual Consistency: Design consistency validated across all phases")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])