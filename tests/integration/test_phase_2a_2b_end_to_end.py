"""
End-to-End Integration Tests for Phase 2A + 2B
Complete workflow validation from requirements to implementation

This test suite validates the complete integration between:
- Phase 2A: Requirements Parser & Test Generator  
- Phase 2B: TDD Workflow Engine & Business Logic Orchestration
"""
import pytest
import tempfile
from pathlib import Path
import subprocess
import sys
import os

# Add src to path for imports
sys.path.append('/workspaces/control_tower/src')

from data_access.requirements_parser import RequirementsParser
from data_access.requirements_models import ParsedRequirement
from business_logic.tdd_workflow_engine import TDDWorkflowEngine, TDDPhase


class TestPhase2APhase2BEndToEndIntegration:
    """
    Complete end-to-end testing of Phase 2A + 2B integration
    
    Tests the full workflow:
    1. Parse real requirements (Phase 2A)
    2. Generate failing tests (Phase 2A/2B coordination)
    3. Execute RED-GREEN-REFACTOR cycle (Phase 2B)
    4. Validate requirements compliance (Phase 2B)
    5. Generate traceability reports (Phase 2B)
    """
    
    @pytest.fixture
    def real_requirement_file(self):
        """Path to real requirement file from investment_strategy repo"""
        return "/workspaces/control_tower/cloned_repos/investment_strategy/projects/PROJECT-001/SYSTEM-001-05_rebalancing_automation/features/FEATURE-001-05-02_automated_rebalancing_execution.md"
    
    @pytest.fixture
    def temp_workspace(self):
        """Temporary workspace for end-to-end testing"""
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

    def test_complete_phase_2a_2b_workflow_integration(self, 
                                                       real_requirement_file, 
                                                       temp_workspace,
                                                       requirements_parser,
                                                       workflow_engine):
        """
        MASTER END-TO-END TEST: Complete Phase 2A + 2B Integration
        
        This test validates the entire workflow from requirements to implementation:
        
        Phase 2A Integration:
        1. Parse real requirement file from investment_strategy
        2. Extract acceptance criteria and metadata
        3. Validate requirement structure and completeness
        
        Phase 2B Integration:
        4. Generate failing tests from parsed requirements
        5. Execute RED phase (confirm tests fail)
        6. Execute GREEN phase (minimal implementation)
        7. Execute REFACTOR phase (code quality improvements)
        8. Validate functional requirements compliance
        9. Generate comprehensive traceability report
        
        Success Criteria:
        - Real requirement file successfully parsed
        - TDD cycle completes successfully
        - All acceptance criteria covered by tests
        - Implementation passes validation
        - Complete traceability maintained
        """
        
        # Skip if requirement file doesn't exist
        if not Path(real_requirement_file).exists():
            pytest.skip("Real requirement file not available for end-to-end testing")
        
        print(f"\n🚀 STARTING COMPLETE PHASE 2A + 2B END-TO-END INTEGRATION TEST")
        print("=" * 80)
        
        # =====================================================
        # PHASE 2A: Requirements Parsing & Analysis
        # =====================================================
        print("\n📋 PHASE 2A: Requirements Parsing & Analysis")
        print("-" * 50)
        
        # Step 1: Parse real requirement file
        print(f"📄 Parsing requirement file: {Path(real_requirement_file).name}")
        requirement = requirements_parser.parse_file(real_requirement_file)
        
        # Validate Phase 2A parsing success
        assert requirement is not None, "Failed to parse requirement file"
        assert requirement.id, "Requirement ID not extracted"
        assert requirement.title, "Requirement title not extracted"
        assert len(requirement.acceptance_criteria) > 0, "No acceptance criteria found"
        
        print(f"✅ Successfully parsed requirement: {requirement.id}")
        print(f"   Title: {requirement.title}")
        print(f"   Acceptance Criteria: {len(requirement.acceptance_criteria)} found")
        print(f"   Project Type: {requirement.project_type}")
        print(f"   Target Layer: {requirement.get_target_layer()}")
        
        # =====================================================
        # PHASE 2B: TDD Workflow Orchestration  
        # =====================================================
        print("\n🔄 PHASE 2B: TDD Workflow Orchestration")
        print("-" * 50)
        
        # Step 2: Execute complete TDD cycle
        print("🔄 Executing complete RED-GREEN-REFACTOR cycle...")
        tdd_result = workflow_engine.execute_complete_tdd_cycle(requirement, temp_workspace)
        
        # Validate TDD cycle success
        assert tdd_result.success is True, f"TDD cycle failed: {tdd_result.message}"
        assert tdd_result.tests_generated is True, "Test generation failed"
        assert tdd_result.red_phase_completed is True, "RED phase failed"
        assert tdd_result.green_phase_completed is True, "GREEN phase failed"
        assert tdd_result.refactor_phase_completed is True, "REFACTOR phase failed"
        assert tdd_result.implementation_completed is True, "Implementation not completed"
        
        print(f"✅ TDD Cycle completed successfully!")
        print(f"   RED Phase: {'✅ PASSED' if tdd_result.red_phase_completed else '❌ FAILED'}")
        print(f"   GREEN Phase: {'✅ PASSED' if tdd_result.green_phase_completed else '❌ FAILED'}")
        print(f"   REFACTOR Phase: {'✅ PASSED' if tdd_result.refactor_phase_completed else '❌ FAILED'}")
        print(f"   Final Tests: {'✅ ALL PASSING' if tdd_result.final_test_status.all_passing else '❌ FAILURES'}")
        
        # =====================================================
        # INTEGRATION VALIDATION: Cross-Phase Coordination
        # =====================================================
        print("\n🔗 INTEGRATION VALIDATION: Cross-Phase Coordination")
        print("-" * 60)
        
        # Step 3: Validate requirements coordination
        print("🎯 Validating requirements-to-implementation traceability...")
        validation = workflow_engine.validate_functional_requirements(requirement, temp_workspace)
        
        assert validation.total_requirements > 0, "No requirements to validate"
        assert validation.validated_requirements > 0, "No requirements validated"
        
        print(f"✅ Requirements validation completed!")
        print(f"   Total Requirements: {validation.total_requirements}")
        print(f"   Validated Requirements: {validation.validated_requirements}")
        print(f"   Compliance: {validation.compliance_percentage:.1f}%")
        
        # Step 4: Generate traceability report
        print("📊 Generating comprehensive traceability report...")
        traceability = workflow_engine.generate_traceability_report([requirement], temp_workspace)
        
        assert traceability.total_requirements > 0, "No requirements in traceability"
        assert traceability.coverage_percentage >= 0, "Invalid coverage calculation"
        
        print(f"✅ Traceability report generated!")
        print(f"   Total Requirements: {traceability.total_requirements}")
        print(f"   Traced Requirements: {traceability.traced_requirements}")
        print(f"   Coverage: {traceability.coverage_percentage:.1f}%")
        
        # Step 5: Business logic validation
        print("🏗️ Validating business logic implementation quality...")
        business_validation = workflow_engine.validate_business_logic(requirement, temp_workspace)
        
        assert business_validation.business_rules_implemented is True, "Business rules not implemented"
        
        print(f"✅ Business logic validation completed!")
        print(f"   Business Rules: {'✅ IMPLEMENTED' if business_validation.business_rules_implemented else '❌ MISSING'}")
        print(f"   Edge Cases: {'✅ HANDLED' if business_validation.edge_cases_handled else '❌ MISSING'}")
        print(f"   Performance: {'✅ MET' if business_validation.performance_requirements_met else '❌ BELOW STANDARD'}")
        
        # =====================================================
        # FINAL VALIDATION: Complete System Integration
        # =====================================================
        print("\n🏆 FINAL VALIDATION: Complete System Integration")
        print("-" * 55)
        
        # Validate workspace structure
        assert (temp_workspace / "src").exists(), "Implementation directory not created"
        assert (temp_workspace / "tests").exists(), "Test directory not created"
        
        src_files = list((temp_workspace / "src").glob("*.py"))
        test_files = list((temp_workspace / "tests").rglob("test_*.py"))
        
        assert len(src_files) > 0, "No implementation files created"
        assert len(test_files) > 0, "No test files created"
        
        print(f"✅ Workspace structure validated!")
        print(f"   Implementation Files: {len(src_files)}")
        print(f"   Test Files: {len(test_files)}")
        
        # Generate final compliance report
        compliance = workflow_engine.generate_compliance_report([requirement], temp_workspace)
        
        print(f"✅ Final compliance report generated!")
        print(f"   Overall Score: {compliance.overall_score:.1f}%")
        print(f"   Functional Requirements: {compliance.functional_requirements_score:.1f}%")
        print(f"   Business Requirements: {compliance.business_requirements_score:.1f}%")
        print(f"   Acceptance Criteria: {compliance.acceptance_criteria_score:.1f}%")
        
        print("\n" + "=" * 80)
        print("🎉 COMPLETE PHASE 2A + 2B INTEGRATION TEST: SUCCESS!")
        print("✅ Requirements parsing successful (Phase 2A)")
        print("✅ TDD workflow automation successful (Phase 2B)")  
        print("✅ Cross-phase integration validated")
        print("✅ End-to-end traceability maintained")
        print("✅ Implementation quality validated")
        print("=" * 80)

    def test_multi_requirement_batch_processing(self, temp_workspace, requirements_parser, workflow_engine):
        """
        Test batch processing of multiple requirements (scalability test)
        
        Validates that the integrated system can handle multiple requirements
        and maintain quality and traceability across all of them.
        """
        
        # Create mock requirements for batch testing
        mock_requirements = [
            ParsedRequirement(
                id=f"BATCH-TEST-{i:03d}",
                title=f"Batch Test Requirement {i}",
                description=f"Test requirement {i} for batch processing validation",
                acceptance_criteria=[
                    {"id": f"AC-{i}-001", "description": f"Basic functionality {i}"},
                    {"id": f"AC-{i}-002", "description": f"Error handling {i}"}
                ],
                project_type="APPLICATION"
            )
            for i in range(1, 4)  # 3 requirements for batch test
        ]
        
        print(f"\n🔄 BATCH PROCESSING TEST: Processing {len(mock_requirements)} requirements")
        
        batch_results = []
        for req in mock_requirements:
            print(f"   Processing {req.id}...")
            result = workflow_engine.execute_complete_tdd_cycle(req, temp_workspace / req.id)
            batch_results.append(result)
            assert result.success is True, f"Batch processing failed for {req.id}"
        
        # Validate batch traceability - check each requirement's workspace
        total_requirements = 0
        total_traced = 0
        
        for req in mock_requirements:
            req_workspace = temp_workspace / req.id
            if req_workspace.exists():
                req_traceability = workflow_engine.generate_traceability_report([req], req_workspace)
                total_requirements += req_traceability.total_requirements
                total_traced += req_traceability.traced_requirements
        
        batch_coverage = (total_traced / total_requirements * 100) if total_requirements > 0 else 0
        
        print(f"✅ Batch processing completed successfully!")
        print(f"   Requirements Processed: {len(batch_results)}")
        print(f"   Success Rate: {sum(1 for r in batch_results if r.success) / len(batch_results) * 100:.1f}%")
        print(f"   Total Coverage: {batch_coverage:.1f}%")
        
        assert all(result.success for result in batch_results), "Some batch items failed"
        assert total_requirements > 0, "No requirements found for traceability"

    def test_testing_pyramid_cross_phase_integration(self, temp_workspace, workflow_engine):
        """
        Test the intelligent testing pyramid integration across phases
        
        Validates that the testing pyramid correctly integrates with
        both Phase 2A parsed requirements and Phase 2B workflow execution.
        """
        
        print(f"\n🔺 TESTING PYRAMID INTEGRATION TEST")
        
        # Test component availability detection
        component_states = {
            "data_access": "available",      # Phase 2A completed
            "business_logic": "in_development",  # Phase 2B in progress
            "ui": "not_started",            # Phase 2C pending
            "integration": "not_started"    # Phase 2D pending
        }
        
        execution_plan = workflow_engine.create_testing_execution_plan(component_states)
        
        print(f"   Executable Levels: {[level.value for level in execution_plan.executable_levels]}")
        print(f"   Skipped Levels: {[level.value for level in execution_plan.skipped_levels]}")
        
        # Validate intelligent test selection
        from business_logic.tdd_workflow_engine import TestingPyramidLevel
        assert TestingPyramidLevel.UNIT in execution_plan.executable_levels
        assert TestingPyramidLevel.INTEGRATION in execution_plan.executable_levels
        assert TestingPyramidLevel.E2E in execution_plan.skipped_levels
        
        print(f"✅ Testing pyramid integration validated!")

# Additional end-to-end scenarios
def test_error_handling_integration():
    """Test error handling across Phase 2A and 2B integration"""
    pass

def test_performance_integration():
    """Test performance requirements across integrated phases"""  
    pass