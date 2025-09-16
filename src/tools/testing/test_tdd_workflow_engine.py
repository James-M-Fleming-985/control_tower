"""
Test Suite for TR-BL-003: Automated TDD Workflow Engine
Phase 2B Business Logic Layer - TDD Automation Orchestrator

Following TDD methodology (RED-GREEN-REFACTOR):
1. RED: Create failing tests for TDD workflow automation
2. GREEN: Implement minimal TDD orchestrator to make tests pass
3. REFACTOR: Optimize and enhance the implementation

Test Coverage:
- Requirements Analysis & Test Generation coordination
- RED-GREEN-REFACTOR cycle automation
- Intelligent Testing Pyramid management
- Requirements Validation Engine
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

# Import Phase 2A components (already implemented)
import sys
sys.path.append('/workspaces/control_tower/src')
from data_access.requirements_parser import RequirementsParser
from data_access.requirements_models import ParsedRequirement, AcceptanceCriterion, ProjectType, RequirementType

# Phase 2B components to be implemented
try:
    from business_logic.tdd_workflow_engine import (
        TDDWorkflowEngine,
        TDDPhase,
        WorkflowResult,
        TestingPyramidLevel,
        ValidationResult
    )
except ImportError:
    # Will be implemented in GREEN phase
    TDDWorkflowEngine = None
    TDDPhase = None
    WorkflowResult = None
    TestingPyramidLevel = None
    ValidationResult = None


class TestTDDWorkflowEngine:
    """Test suite for TDD Automation Orchestrator component"""
    
    @pytest.fixture
    def sample_requirement(self):
        """Sample requirement from Phase 2A testing"""
        return ParsedRequirement(
            id="FEA-APP-001-05-02",
            title="Automated Rebalancing Execution",
            description="Implement automated portfolio rebalancing logic",
            project_type=ProjectType.APPLICATION,
            acceptance_criteria=[
                {
                    "id": "AC-001",
                    "description": "System executes rebalancing when threshold exceeded",
                    "details": "Given portfolio drift > 5%, When rebalancing triggered, Then portfolio balanced within tolerance"
                },
                {
                    "id": "AC-002", 
                    "description": "Rebalancing respects risk constraints",
                    "details": "Given risk limits defined, When rebalancing executes, Then no position exceeds risk limits"
                }
            ],
            priority="P0",
            layer_implementation="Business Logic Layer"
        )
    
    @pytest.fixture
    def workflow_engine(self):
        """TDD Workflow Engine instance for testing"""
        if TDDWorkflowEngine is None:
            pytest.skip("TDDWorkflowEngine not implemented yet - RED phase")
        return TDDWorkflowEngine()
    
    @pytest.fixture
    def temp_workspace(self):
        """Temporary workspace for test generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "tests").mkdir()
            (workspace / "src").mkdir()
            yield workspace

    # =====================================================
    # FR-BL-003-001: Requirements Analysis & Test Generation Coordination
    # =====================================================
    
    def test_parse_requirements_and_generate_failing_tests(self, workflow_engine, sample_requirement, temp_workspace):
        """
        Test that workflow engine coordinates with Phase 2A to generate failing tests
        
        Given: A requirement with acceptance criteria
        When: TDD workflow engine processes the requirement
        Then: Failing tests are generated automatically
        And: Tests follow pytest conventions
        And: All tests fail initially (RED phase ready)
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Act
        result = workflow_engine.generate_failing_tests(sample_requirement, temp_workspace)
        
        # Assert
        assert result.success is True
        assert len(result.generated_test_files) > 0
        assert all(Path(f).exists() for f in result.generated_test_files)
        
        # Verify tests are initially failing
        test_results = workflow_engine.run_tests(result.generated_test_files)
        assert test_results.all_tests_failing is True
        assert test_results.total_tests > 0
    
    def test_identify_project_type_and_layer_requirements(self, workflow_engine, sample_requirement):
        """
        Test automatic identification of project type and layer focus
        
        Given: Requirements with different project types (Application vs Standard Delivery)
        When: Workflow engine analyzes requirements
        Then: Correct project type is identified
        And: Appropriate layer requirements are extracted
        And: Test generation strategy matches project type
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Act
        analysis = workflow_engine.analyze_requirements(sample_requirement)
        
        # Assert
        assert analysis.project_type == ProjectType.APPLICATION
        assert analysis.target_layer == "Business Logic"
        assert analysis.test_strategy == "layer_focused"
        assert len(analysis.testable_criteria) == 2
    
    def test_validate_requirements_are_testable(self, workflow_engine, temp_workspace):
        """
        Test validation that requirements are testable before proceeding
        
        Given: Requirements with various completeness levels
        When: Workflow engine validates testability
        Then: Complete requirements are marked as testable
        And: Incomplete requirements are flagged
        And: Missing acceptance criteria are identified
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Incomplete requirement (missing acceptance criteria)
        incomplete_req = ParsedRequirement(
            id="INCOMPLETE-001",
            title="Incomplete Feature",
            description="Missing acceptance criteria",
            project_type=ProjectType.APPLICATION,
            acceptance_criteria=[],  # Empty criteria
            priority="P0",
            layer_implementation="Business Logic Layer"
        )
        
        # Act
        validation = workflow_engine.validate_requirements_testability([incomplete_req])
        
        # Assert
        assert validation.total_requirements == 1
        assert validation.testable_requirements == 0
        assert validation.untestable_requirements == 1
        assert "missing acceptance criteria" in validation.issues[0].lower()

    # =====================================================
    # FR-BL-003-002: RED-GREEN-REFACTOR Automation
    # =====================================================
    
    def test_execute_red_phase_with_failing_tests(self, workflow_engine, sample_requirement, temp_workspace):
        """
        Test RED phase execution with proper failure confirmation
        
        Given: Generated failing tests from acceptance criteria
        When: RED phase is executed
        Then: All tests fail as expected
        And: Failure reasons are clearly reported
        And: No implementation exists yet
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Arrange
        workflow_engine.generate_failing_tests(sample_requirement, temp_workspace)
        
        # Act
        red_result = workflow_engine.execute_red_phase(temp_workspace)
        
        # Assert
        assert red_result.phase == TDDPhase.RED
        assert red_result.success is True
        assert red_result.all_tests_failing is True
        assert red_result.tests_run > 0
        assert len(red_result.failure_details) > 0
    
    def test_execute_green_phase_with_minimal_implementation(self, workflow_engine, sample_requirement, temp_workspace):
        """
        Test GREEN phase with guided minimal implementation
        
        Given: Failing tests from RED phase
        When: GREEN phase is executed
        Then: Minimal implementation makes tests pass
        And: No over-engineering occurs
        And: Implementation is focused on making tests pass
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Arrange
        workflow_engine.generate_failing_tests(sample_requirement, temp_workspace)
        workflow_engine.execute_red_phase(temp_workspace)
        
        # Act
        green_result = workflow_engine.execute_green_phase(temp_workspace, sample_requirement)
        
        # Assert
        assert green_result.phase == TDDPhase.GREEN
        assert green_result.success is True
        assert green_result.all_tests_passing is True
        assert green_result.implementation_files_created > 0
    
    def test_execute_refactor_phase_with_improvements(self, workflow_engine, sample_requirement, temp_workspace):
        """
        Test REFACTOR phase with code quality improvements
        
        Given: Passing tests from GREEN phase
        When: REFACTOR phase is executed
        Then: Code quality improvements are applied
        And: All tests continue to pass
        And: No behavior changes occur
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Arrange
        workflow_engine.generate_failing_tests(sample_requirement, temp_workspace)
        workflow_engine.execute_red_phase(temp_workspace)
        workflow_engine.execute_green_phase(temp_workspace, sample_requirement)
        
        # Act
        refactor_result = workflow_engine.execute_refactor_phase(temp_workspace)
        
        # Assert
        assert refactor_result.phase == TDDPhase.REFACTOR
        assert refactor_result.success is True
        assert refactor_result.all_tests_passing is True
        assert refactor_result.quality_improvements > 0
    
    def test_complete_red_green_refactor_cycle(self, workflow_engine, sample_requirement, temp_workspace):
        """
        Test complete TDD cycle execution
        
        Given: A requirement with acceptance criteria
        When: Complete RED-GREEN-REFACTOR cycle is executed
        Then: All phases complete successfully
        And: Final implementation passes all tests
        And: Progress is tracked throughout cycle
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Act
        cycle_result = workflow_engine.execute_complete_tdd_cycle(sample_requirement, temp_workspace)
        
        # Assert
        assert cycle_result.success is True
        assert cycle_result.red_phase_completed is True
        assert cycle_result.green_phase_completed is True
        assert cycle_result.refactor_phase_completed is True
        assert cycle_result.final_test_status.all_passing is True

    # =====================================================
    # FR-BL-003-003: Intelligent Testing Pyramid
    # =====================================================
    
    def test_execute_unit_tests_for_business_logic(self, workflow_engine, temp_workspace):
        """
        Test unit testing execution for feature-specific business logic
        
        Given: Generated unit tests for business logic
        When: Unit test layer is executed
        Then: Business logic is validated in isolation
        And: No external dependencies are required
        And: Fast execution (< 1 second per test)
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Act
        unit_result = workflow_engine.execute_testing_pyramid_level(
            TestingPyramidLevel.UNIT, 
            temp_workspace
        )
        
        # Assert
        assert unit_result.level == TestingPyramidLevel.UNIT
        assert unit_result.success is True
        assert unit_result.execution_time < 1.0  # Fast execution
        assert unit_result.external_dependencies_required is False
    
    def test_execute_integration_tests_with_previous_layers_only(self, workflow_engine, temp_workspace):
        """
        Test integration testing with dependency awareness
        
        Given: Available previous layers (Data Access from Phase 2A)
        When: Integration test layer is executed
        Then: Tests run with PREVIOUS layers only
        And: Future dependencies are mocked or skipped
        And: Layer integration is validated
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Mock available layers
        available_layers = ["data_access"]  # Phase 2A completed
        
        # Act
        integration_result = workflow_engine.execute_testing_pyramid_level(
            TestingPyramidLevel.INTEGRATION,
            temp_workspace,
            available_layers=available_layers
        )
        
        # Assert
        assert integration_result.level == TestingPyramidLevel.INTEGRATION
        assert integration_result.success is True
        assert "data_access" in integration_result.tested_integrations
        assert integration_result.mocked_future_dependencies is True
    
    def test_skip_e2e_tests_when_layers_incomplete(self, workflow_engine, temp_workspace):
        """
        Test E2E test skipping when all layers not available
        
        Given: Incomplete layer implementation (UI, Integration layers pending)
        When: E2E test layer is executed
        Then: E2E tests are skipped with clear reasoning
        And: Available tests are executed
        And: Pending dependencies are reported
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Act
        e2e_result = workflow_engine.execute_testing_pyramid_level(
            TestingPyramidLevel.E2E,
            temp_workspace
        )
        
        # Assert
        assert e2e_result.level == TestingPyramidLevel.E2E
        assert e2e_result.tests_skipped > 0
        assert "UI layer not available" in e2e_result.skip_reasons
        assert "Integration layer not available" in e2e_result.skip_reasons
    
    def test_dynamic_test_selection_based_on_available_components(self, workflow_engine, temp_workspace):
        """
        Test intelligent test selection based on component availability
        
        Given: Various component availability states
        When: Testing pyramid determines executable tests
        Then: Only appropriate tests are selected
        And: Dependency requirements are validated
        And: Clear execution plan is provided
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Mock component states
        component_states = {
            "data_access": "available",
            "business_logic": "in_development", 
            "ui": "not_started",
            "integration": "not_started"
        }
        
        # Act
        execution_plan = workflow_engine.create_testing_execution_plan(component_states)
        
        # Assert
        assert TestingPyramidLevel.UNIT in execution_plan.executable_levels
        assert TestingPyramidLevel.INTEGRATION in execution_plan.executable_levels
        assert TestingPyramidLevel.E2E in execution_plan.skipped_levels
        assert len(execution_plan.execution_order) > 0

    # =====================================================
    # FR-BL-003-004: Requirements Validation Engine
    # =====================================================
    
    def test_validate_functional_requirements_against_implementation(self, workflow_engine, sample_requirement, temp_workspace):
        """
        Test validation of functional requirements against implementation
        
        Given: Implemented feature with test coverage
        When: Functional requirements validation is executed
        Then: Original acceptance criteria are validated
        And: Implementation compliance is verified
        And: Missing functionality is identified
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Arrange - simulate implemented feature
        workflow_engine.execute_complete_tdd_cycle(sample_requirement, temp_workspace)
        
        # Act
        validation = workflow_engine.validate_functional_requirements(
            sample_requirement, temp_workspace
        )
        
        # Assert
        assert validation.total_requirements == len(sample_requirement.acceptance_criteria)
        assert validation.validated_requirements > 0
        assert validation.compliance_percentage >= 100
        assert len(validation.missing_functionality) == 0
    
    def test_validate_business_logic_implementation(self, workflow_engine, sample_requirement, temp_workspace):
        """
        Test business logic implementation validation
        
        Given: Business logic layer implementation
        When: Business validation is executed
        Then: Business rules are correctly implemented
        And: Edge cases are handled appropriately
        And: Performance requirements are met
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Act
        business_validation = workflow_engine.validate_business_logic(
            sample_requirement, temp_workspace
        )
        
        # Assert
        assert business_validation.business_rules_implemented is True
        assert business_validation.edge_cases_handled is True
        assert business_validation.performance_requirements_met is True
        assert len(business_validation.violations) == 0
    
    def test_generate_requirements_traceability_report(self, workflow_engine, sample_requirement, temp_workspace):
        """
        Test comprehensive traceability reporting
        
        Given: Complete implementation with tests
        When: Traceability report is generated
        Then: All requirements are traced to tests
        And: All tests are traced to requirements
        And: Coverage gaps are identified
        And: Compliance summary is provided
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Arrange
        workflow_engine.execute_complete_tdd_cycle(sample_requirement, temp_workspace)
        
        # Act
        traceability = workflow_engine.generate_traceability_report(
            [sample_requirement], temp_workspace
        )
        
        # Assert
        assert traceability.total_requirements > 0
        assert traceability.traced_requirements == traceability.total_requirements
        assert traceability.coverage_percentage == 100
        assert len(traceability.orphaned_tests) == 0
        assert len(traceability.untested_requirements) == 0
    
    def test_provide_detailed_compliance_reporting(self, workflow_engine, sample_requirement, temp_workspace):
        """
        Test detailed compliance reporting with pass/fail breakdown
        
        Given: Multiple requirements with various compliance states
        When: Compliance report is generated
        Then: Detailed pass/fail breakdown is provided
        And: Actionable guidance for failures is included
        And: Overall compliance score is calculated
        And: Next steps are recommended
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Act
        compliance_report = workflow_engine.generate_compliance_report(
            [sample_requirement], temp_workspace
        )
        
        # Assert
        assert compliance_report.functional_requirements_score >= 0
        assert compliance_report.business_requirements_score >= 0
        assert compliance_report.acceptance_criteria_score >= 0
        assert len(compliance_report.actionable_guidance) > 0
        assert compliance_report.overall_score >= 0
        assert len(compliance_report.next_steps) > 0


class TestTDDWorkflowIntegration:
    """Integration tests for TDD Workflow Engine with Phase 2A components"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Temporary workspace for integration testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "tests").mkdir()
            (workspace / "src").mkdir()
            yield workspace
    
    def test_integration_with_requirements_parser(self, temp_workspace):
        """
        Test integration with Phase 2A Requirements Parser
        
        Given: Real requirement file from repository
        When: TDD workflow engine processes the file
        Then: Requirements are parsed using Phase 2A parser
        And: Test generation coordinates seamlessly
        And: End-to-end workflow completes successfully
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Use real requirements file
        parser = RequirementsParser()
        sample_file = "/workspaces/control_tower/cloned_repos/investment_strategy/projects/PROJECT-001/SYSTEM-001-05_rebalancing_automation/features/FEATURE-001-05-02_automated_rebalancing_execution.md"
        
        if not Path(sample_file).exists():
            pytest.skip("Sample requirement file not available")
        
        # Act
        requirement = parser.parse_file(sample_file)
        workflow_engine = TDDWorkflowEngine()
        result = workflow_engine.execute_complete_tdd_cycle(requirement, temp_workspace)
        
        # Assert
        assert result.success is True
        assert result.tests_generated is True
        assert result.implementation_completed is True
        assert result.red_phase_completed is True
        assert result.green_phase_completed is True
        assert result.refactor_phase_completed is True
    
    def test_workflow_engine_performance_requirements(self):
        """
        Test that workflow engine meets performance requirements
        
        Given: Performance requirements from specification
        When: Workflow operations are executed
        Then: Response times are within specified limits
        And: Resource usage is efficient
        And: Concurrent operations are supported
        """
        if TDDWorkflowEngine is None:
            pytest.skip("Implementation pending - RED phase")
            
        # Performance requirements validation will be implemented
        # in GREEN phase along with the main component
        pass


@pytest.fixture
def complex_requirement_set():
    """Complex requirement set for comprehensive testing"""
    return [
        ParsedRequirement(
            id="FEA-APP-001-BL",
            title="Business Logic Layer Feature",
            description="Complex business logic implementation",
            project_type=ProjectType.APPLICATION,
            acceptance_criteria=[
                {"id": "AC-BL-001", "description": "Business rule validation"},
                {"id": "AC-BL-002", "description": "Data transformation logic"},
                {"id": "AC-BL-003", "description": "Integration point handling"}
            ],
            priority="P0",
            layer_implementation="Business Logic Layer"
        ),
        ParsedRequirement(
            id="MIL-DEL-002-SD",
            title="Standard Delivery Milestone",
            description="Standard delivery task completion",
            project_type=ProjectType.STANDARD_DELIVERY,
            acceptance_criteria=[
                {"id": "AC-SD-001", "description": "Deliverable completion"},
                {"id": "AC-SD-002", "description": "Quality validation"}
            ],
            priority="P1",
            layer_implementation="Task Layer"
        )
    ]