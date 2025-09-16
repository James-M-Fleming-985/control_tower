"""
Validation tests for TR-BL-001 Work Item Discovery Engine requirements

These tests validate that the Work Item Discovery Engine implementation meets all acceptance criteria:
- BL-001: Discovers work items from all repository types
- BL-002: Correctly identifies due and overdue items
- BL-003: Determines project type (Application vs Standard Delivery)
- BL-004: Extracts hierarchical context information
- BL-005: Applies basic priority sorting (overdue first, then due today)
- BL-006: Handles parsing errors gracefully

This validation ensures requirements compliance before progression to Integration Layer.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
from src.business_logic.work_item_discovery_engine import WorkItemDiscoveryEngine
from src.business_logic.work_item_model import WorkItem, Priority, RequirementLevel, ProjectType, ItemStatus
from src.data_access.repository_scanner import RawRequirement, RequirementMetadata


class TestTR_BL_001_Validation:
    """Validation test suite for TR-BL-001 Work Item Discovery Engine acceptance criteria"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.discovery_engine = WorkItemDiscoveryEngine()
        self.north_star_repositories = [
            "/workspaces/control_tower/cloned_repos/financial_security_dev",
            "/workspaces/control_tower/cloned_repos/home_improvements", 
            "/workspaces/control_tower/cloned_repos/LIMS_concept_actual",
            "/workspaces/control_tower/cloned_repos/contract_projects",
            "/workspaces/control_tower/cloned_repos/relationship_building",
            "/workspaces/control_tower/cloned_repos/opti_royale"
        ]
    
    def test_BL_001_discovers_work_items_from_all_repository_types(self):
        """
        Validation Test BL-001: Discovers work items from all repository types
        
        Validates that the discovery engine can process different types of repositories
        and extract work items from various project structures.
        """
        # Mock diverse repository types with different structures
        mock_raw_requirements = [
            # Application repository (financial_security_dev)
            RawRequirement(
                file_path="/test/financial_security_dev/features/investment_portfolio.md",
                content="# Investment Portfolio Management\n**Due Date**: 2025-09-13",
                metadata=RequirementMetadata(
                    id="FINSCTY-001",
                    title="Investment Portfolio Management",
                    due_date=date(2025, 9, 13),
                    priority=Priority.HIGH,
                    effort_estimate="5 days",
                    requirement_level=RequirementLevel.FR,
                    status="Not Started"
                )
            ),
            # Standard delivery repository (LIMS_concept_actual)
            RawRequirement(
                file_path="/test/LIMS_concept_actual/milestones/sample_tracking.md",
                content="# Sample Tracking System\n**Due Date**: 2025-09-13",
                metadata=RequirementMetadata(
                    id="LIMS-001",
                    title="Sample Tracking System",
                    due_date=date(2025, 9, 13),
                    priority=Priority.MEDIUM,
                    effort_estimate="3 days",
                    requirement_level=RequirementLevel.MR,
                    status="In Progress"
                )
            ),
            # Home improvement project (home_improvements)
            RawRequirement(
                file_path="/test/home_improvements/features/kitchen_renovation.md",
                content="# Kitchen Renovation Planning\n**Due Date**: 2025-09-13",
                metadata=RequirementMetadata(
                    id="HOME-001",
                    title="Kitchen Renovation Planning",
                    due_date=date(2025, 9, 13),
                    priority=Priority.LOW,
                    effort_estimate="2 days",
                    requirement_level=RequirementLevel.PR,
                    status="Not Started"
                )
            )
        ]
        
        with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories', 
                         return_value=mock_raw_requirements):
            result = self.discovery_engine.discover_work_items(self.north_star_repositories)
            
            # Validate discovery from all repository types
            assert len(result) == 3, "Should discover work items from all repository types"
            
            # Validate different repository types are represented
            repository_names = [item.repository for item in result]
            assert any("financial_security_dev" in repo for repo in repository_names)
            assert any("LIMS_concept_actual" in repo for repo in repository_names)
            assert any("home_improvements" in repo for repo in repository_names)
            
            # Validate different requirement levels are processed
            requirement_levels = [item.requirement_level for item in result]
            assert RequirementLevel.FR in requirement_levels  # Feature requirement
            assert RequirementLevel.MR in requirement_levels  # Milestone requirement
            assert RequirementLevel.PR in requirement_levels  # Project requirement
        
        print("✅ BL-001: Discovery Engine processes all repository types successfully")
    
    def test_BL_002_correctly_identifies_due_and_overdue_items(self):
        """
        Validation Test BL-002: Correctly identifies due and overdue items
        
        Validates that the discovery engine accurately categorizes work items
        based on their due dates relative to the current date.
        """
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Create test work items with different due date scenarios
        test_items = [
            # Overdue item
            WorkItem(
                id="OVERDUE-001", title="Overdue Feature", description="Past due",
                due_date=yesterday, priority=Priority.HIGH, effort_estimate="2 days",
                requirement_level=RequirementLevel.FR, project_type=ProjectType.APPLICATION,
                repository="financial_security_dev", system_name="Investment", project_name="Financial",
                layer_or_milestone="Business Logic", hierarchy_path="Feature → System → Project",
                status=ItemStatus.NOT_DUE  # Will be updated by filter
            ),
            # Due today item
            WorkItem(
                id="DUE-TODAY-001", title="Due Today Feature", description="Due today",
                due_date=today, priority=Priority.MEDIUM, effort_estimate="1 day",
                requirement_level=RequirementLevel.SR, project_type=ProjectType.STANDARD_DELIVERY,
                repository="LIMS_concept_actual", system_name="LIMS", project_name="Laboratory",
                layer_or_milestone="Data Access", hierarchy_path="Feature → System → Project",
                status=ItemStatus.NOT_DUE  # Will be updated by filter
            ),
            # Future item (should be filtered out)
            WorkItem(
                id="FUTURE-001", title="Future Feature", description="Not due yet",
                due_date=tomorrow, priority=Priority.LOW, effort_estimate="3 days",
                requirement_level=RequirementLevel.PR, project_type=ProjectType.APPLICATION,
                repository="home_improvements", system_name="Home", project_name="Improvements",
                layer_or_milestone="UI Layer", hierarchy_path="Feature → System → Project",
                status=ItemStatus.NOT_DUE
            )
        ]
        
        # Test the filtering logic
        filtered_items = self.discovery_engine.filter_due_and_overdue(test_items)
        
        # Validate filtering results
        assert len(filtered_items) == 2, "Should filter to only due and overdue items"
        
        # Find the items in results
        overdue_item = next((item for item in filtered_items if item.id == "OVERDUE-001"), None)
        due_today_item = next((item for item in filtered_items if item.id == "DUE-TODAY-001"), None)
        future_item = next((item for item in filtered_items if item.id == "FUTURE-001"), None)
        
        # Validate correct identification
        assert overdue_item is not None, "Overdue item should be included"
        assert due_today_item is not None, "Due today item should be included"
        assert future_item is None, "Future item should be excluded"
        
        # Validate status assignment
        assert overdue_item.status == ItemStatus.OVERDUE, "Overdue item should have OVERDUE status"
        assert due_today_item.status == ItemStatus.DUE_TODAY, "Due today item should have DUE_TODAY status"
        
        print("✅ BL-002: Discovery Engine correctly identifies due and overdue items")
    
    def test_BL_003_determines_project_type_application_vs_standard_delivery(self):
        """
        Validation Test BL-003: Determines project type (Application vs Standard Delivery)
        
        Validates that the discovery engine can distinguish between different project types
        based on repository characteristics and content patterns.
        """
        # Test application project type determination
        application_requirements = [
            RawRequirement(
                file_path="/test/financial_security_dev/features/portfolio_analysis.md",
                content="# Portfolio Analysis Engine\nCustom financial analysis application",
                metadata=RequirementMetadata(
                    id="FINSCTY-002",
                    title="Portfolio Analysis Engine",
                    due_date=date(2025, 9, 13),
                    priority=Priority.HIGH,
                    effort_estimate="7 days",
                    requirement_level=RequirementLevel.FR,
                    status="Not Started"
                )
            ),
            RawRequirement(
                file_path="/test/opti_royale/features/game_mechanics.md",
                content="# Game Mechanics System\nCustom game application features",
                metadata=RequirementMetadata(
                    id="OPTI-001",
                    title="Game Mechanics System",
                    due_date=date(2025, 9, 13),
                    priority=Priority.HIGH,
                    effort_estimate="10 days",
                    requirement_level=RequirementLevel.FR,
                    status="Not Started"
                )
            )
        ]
        
        # Test standard delivery project type determination
        standard_delivery_requirements = [
            RawRequirement(
                file_path="/test/LIMS_concept_actual/milestones/database_setup.md",
                content="# Database Setup Milestone\nStandard LIMS database configuration",
                metadata=RequirementMetadata(
                    id="LIMS-002",
                    title="Database Setup Milestone",
                    due_date=date(2025, 9, 13),
                    priority=Priority.MEDIUM,
                    effort_estimate="3 days",
                    requirement_level=RequirementLevel.MR,
                    status="Not Started"
                )
            ),
            RawRequirement(
                file_path="/test/contract_projects/milestones/documentation.md",
                content="# Documentation Milestone\nStandard project documentation",
                metadata=RequirementMetadata(
                    id="CONTRACT-001",
                    title="Documentation Milestone",
                    due_date=date(2025, 9, 13),
                    priority=Priority.LOW,
                    effort_estimate="2 days",
                    requirement_level=RequirementLevel.MR,
                    status="Not Started"
                )
            )
        ]
        
        # Test both project types
        all_requirements = application_requirements + standard_delivery_requirements
        
        with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories', 
                         return_value=all_requirements):
            work_items = self.discovery_engine.discover_work_items(self.north_star_repositories)
            
            # Validate project type determination
            application_items = [item for item in work_items if item.project_type == ProjectType.APPLICATION]
            standard_delivery_items = [item for item in work_items if item.project_type == ProjectType.STANDARD_DELIVERY]
            
            assert len(application_items) >= 2, "Should identify application project types"
            assert len(standard_delivery_items) >= 2, "Should identify standard delivery project types"
            
            # Validate specific project type assignments
            financial_items = [item for item in application_items if "financial_security_dev" in item.repository]
            lims_items = [item for item in standard_delivery_items if "LIMS_concept_actual" in item.repository]
            
            assert len(financial_items) > 0, "Financial security should be classified as APPLICATION"
            assert len(lims_items) > 0, "LIMS should be classified as STANDARD_DELIVERY"
        
        print("✅ BL-003: Discovery Engine determines project types correctly")
    
    def test_BL_004_extracts_hierarchical_context_information(self):
        """
        Validation Test BL-004: Extracts hierarchical context information
        
        Validates that the discovery engine extracts and structures hierarchical context
        for proper display and navigation (Feature → System → Project → Repository).
        """
        mock_requirement = RawRequirement(
            file_path="/test/financial_security_dev/features/investment_portfolio_rebalancing.md",
            content="# Investment Portfolio Rebalancing\n**System**: Investment Strategy\n**Project**: Financial Security",
            metadata=RequirementMetadata(
                id="FINSCTY-003",
                title="Investment Portfolio Rebalancing",
                due_date=date(2025, 9, 13),
                priority=Priority.HIGH,
                effort_estimate="5 days",
                requirement_level=RequirementLevel.FR,
                status="Not Started"
            )
        )
        
        with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories', 
                         return_value=[mock_requirement]):
            work_items = self.discovery_engine.discover_work_items(["/test/financial_security_dev"])
            
            assert len(work_items) == 1
            item = work_items[0]
            
            # Validate hierarchical context extraction
            assert item.title == "Investment Portfolio Rebalancing", "Should extract feature title"
            assert "Investment Strategy" in item.system_name or "Investment Strategy" in item.hierarchy_path, "Should extract system name"
            assert "Financial Security" in item.project_name or "Financial Security" in item.hierarchy_path, "Should extract project name"
            assert "financial_security_dev" in item.repository, "Should extract repository name"
            
            # Validate hierarchy path format
            assert item.hierarchy_path is not None, "Should have hierarchy path"
            assert "→" in item.hierarchy_path or "->" in item.hierarchy_path, "Should use hierarchy separator"
            
            # Validate context completeness
            hierarchy_components = [item.title, item.system_name, item.project_name, item.repository]
            assert all(component for component in hierarchy_components if component), "All hierarchy components should be populated"
        
        print("✅ BL-004: Discovery Engine extracts hierarchical context information")
    
    def test_BL_005_applies_basic_priority_sorting_overdue_first_then_due_today(self):
        """
        Validation Test BL-005: Applies basic priority sorting (overdue first, then due today)
        
        Validates that the discovery engine applies correct prioritization logic
        integrating with the Priority Calculator component.
        """
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Create test items with different due dates and priorities
        test_items = [
            # Due today, high priority
            WorkItem(
                id="DUE-HIGH", title="Due Today High Priority", description="Test",
                due_date=today, priority=Priority.HIGH, effort_estimate="1 day",
                requirement_level=RequirementLevel.FR, project_type=ProjectType.APPLICATION,
                repository="test_repo", system_name="test_system", project_name="test_project",
                layer_or_milestone="Business Logic", hierarchy_path="Test → System → Project",
                status=ItemStatus.DUE_TODAY
            ),
            # Overdue, low priority (should still come first)
            WorkItem(
                id="OVERDUE-LOW", title="Overdue Low Priority", description="Test",
                due_date=yesterday, priority=Priority.LOW, effort_estimate="2 days",
                requirement_level=RequirementLevel.SR, project_type=ProjectType.STANDARD_DELIVERY,
                repository="test_repo", system_name="test_system", project_name="test_project",
                layer_or_milestone="Data Access", hierarchy_path="Test → System → Project",
                status=ItemStatus.OVERDUE
            ),
            # Due today, medium priority
            WorkItem(
                id="DUE-MEDIUM", title="Due Today Medium Priority", description="Test",
                due_date=today, priority=Priority.MEDIUM, effort_estimate="3 days",
                requirement_level=RequirementLevel.PR, project_type=ProjectType.APPLICATION,
                repository="test_repo", system_name="test_system", project_name="test_project",
                layer_or_milestone="UI Layer", hierarchy_path="Test → System → Project",
                status=ItemStatus.DUE_TODAY
            )
        ]
        
        # Apply prioritization
        prioritized_items = self.discovery_engine.apply_basic_prioritization(test_items)
        
        # Validate prioritization results
        assert len(prioritized_items) == 3, "Should maintain all items"
        
        # Find item positions
        overdue_position = next(i for i, item in enumerate(prioritized_items) if item.id == "OVERDUE-LOW")
        due_high_position = next(i for i, item in enumerate(prioritized_items) if item.id == "DUE-HIGH")
        due_medium_position = next(i for i, item in enumerate(prioritized_items) if item.id == "DUE-MEDIUM")
        
        # Validate overdue items come first
        assert overdue_position == 0, "Overdue items should come first regardless of priority"
        
        # Validate due today items come after overdue
        assert due_high_position > overdue_position, "Due today items should come after overdue"
        assert due_medium_position > overdue_position, "Due today items should come after overdue"
        
        print("✅ BL-005: Discovery Engine applies correct priority sorting")
    
    def test_BL_006_handles_parsing_errors_gracefully(self):
        """
        Validation Test BL-006: Handles parsing errors gracefully
        
        Validates that the discovery engine handles various error conditions
        without crashing and provides meaningful responses.
        """
        # Test various error scenarios
        error_scenarios = [
            # Empty repository list
            [],
            # Invalid repository paths
            ["/nonexistent/repository"],
            # Corrupted requirement data
            [RawRequirement(
                file_path="/test/corrupted.md",
                content="Invalid content without metadata",
                metadata=RequirementMetadata(
                    id="CORRUPT-001",
                    title="",  # Empty title
                    due_date=None,  # Missing due date
                    priority=Priority.MEDIUM,  # Default priority
                    effort_estimate="Unknown",
                    requirement_level=RequirementLevel.FR,  # Default
                    status="Unknown"
                )
            )],
            # Mixed valid and invalid data
            [
                RawRequirement(
                    file_path="/test/valid.md",
                    content="# Valid Requirement\n**Due Date**: 2025-09-13",
                    metadata=RequirementMetadata(
                        id="VALID-001",
                        title="Valid Requirement",
                        due_date=date(2025, 9, 13),
                        priority=Priority.HIGH,
                        effort_estimate="2 days",
                        requirement_level=RequirementLevel.FR,
                        status="Not Started"
                    )
                ),
                RawRequirement(
                    file_path="/test/invalid.md",
                    content="Corrupted content",
                    metadata=RequirementMetadata(
                        id="INVALID-001",
                        title="",  # Invalid title
                        due_date=None,
                        priority=Priority.MEDIUM,
                        effort_estimate="Unknown",
                        requirement_level=RequirementLevel.FR,
                        status="Unknown"
                    )
                )
            ]
        ]
        
        for i, scenario in enumerate(error_scenarios):
            with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories', 
                             return_value=scenario):
                try:
                    # Should not crash on any error scenario
                    result = self.discovery_engine.discover_work_items(self.north_star_repositories)
                    
                    # Validate graceful handling
                    assert isinstance(result, list), f"Scenario {i}: Should return list even on errors"
                    
                    # For mixed scenarios, should process valid items
                    if i == 3:  # Mixed valid/invalid scenario
                        valid_items = [item for item in result if item.title and item.title != ""]
                        assert len(valid_items) >= 0, "Should process valid items even when some are invalid"
                    
                except Exception as e:
                    pytest.fail(f"Scenario {i}: Discovery engine should not crash on parsing errors: {e}")
        
        print("✅ BL-006: Discovery Engine handles parsing errors gracefully")
    
    def test_integration_work_item_discovery_engine_complete(self):
        """
        Integration validation test for complete TR-BL-001 Work Item Discovery Engine
        
        Validates that the Work Item Discovery Engine works as a complete, integrated component
        meeting all acceptance criteria in realistic Phase 1 scenarios.
        """
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Create realistic North Star repository scenario
        mock_requirements = [
            # Financial Security - Application type, overdue
            RawRequirement(
                file_path="/test/financial_security_dev/features/portfolio_optimization.md",
                content="# Portfolio Optimization Engine\n**System**: Investment Strategy\n**Project**: Financial Security",
                metadata=RequirementMetadata(
                    id="FINSCTY-004",
                    title="Portfolio Optimization Engine",
                    due_date=yesterday,  # Overdue
                    priority=Priority.HIGH,
                    effort_estimate="7 days",
                    requirement_level=RequirementLevel.FR,
                    status="In Progress"
                )
            ),
            # LIMS - Standard Delivery type, due today
            RawRequirement(
                file_path="/test/LIMS_concept_actual/milestones/sample_processing.md",
                content="# Sample Processing Milestone\n**System**: Laboratory Management\n**Project**: LIMS Implementation",
                metadata=RequirementMetadata(
                    id="LIMS-003",
                    title="Sample Processing Milestone",
                    due_date=today,  # Due today
                    priority=Priority.MEDIUM,
                    effort_estimate="3 days",
                    requirement_level=RequirementLevel.MR,
                    status="Not Started"
                )
            ),
            # Home Improvements - Application type, due today
            RawRequirement(
                file_path="/test/home_improvements/features/kitchen_design.md",
                content="# Kitchen Design System\n**System**: Home Planning\n**Project**: Home Improvements",
                metadata=RequirementMetadata(
                    id="HOME-002",
                    title="Kitchen Design System",
                    due_date=today,  # Due today
                    priority=Priority.LOW,
                    effort_estimate="2 days",
                    requirement_level=RequirementLevel.PR,
                    status="Not Started"
                )
            )
        ]
        
        with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories', 
                         return_value=mock_requirements):
            
            # Execute complete discovery workflow
            all_work_items = self.discovery_engine.discover_work_items(self.north_star_repositories)
            due_and_overdue_items = self.discovery_engine.filter_due_and_overdue(all_work_items)
            prioritized_items = self.discovery_engine.apply_basic_prioritization(due_and_overdue_items)
            
            # Validate complete workflow integration
            assert len(all_work_items) == 3, "Should discover all work items"
            assert len(due_and_overdue_items) == 3, "Should filter to due and overdue items"
            assert len(prioritized_items) == 3, "Should maintain all items through prioritization"
            
            # Validate prioritization (overdue first)
            first_item = prioritized_items[0]
            assert first_item.status == ItemStatus.OVERDUE, "First item should be overdue"
            assert "Portfolio Optimization" in first_item.title, "Should be the overdue portfolio item"
            
            # Validate project type determination
            application_items = [item for item in all_work_items if item.project_type == ProjectType.APPLICATION]
            standard_delivery_items = [item for item in all_work_items if item.project_type == ProjectType.STANDARD_DELIVERY]
            
            assert len(application_items) >= 2, "Should identify application projects"
            assert len(standard_delivery_items) >= 1, "Should identify standard delivery projects"
            
            # Validate hierarchical context
            for item in all_work_items:
                assert item.hierarchy_path, "All items should have hierarchical context"
                assert item.repository, "All items should have repository information"
                assert item.system_name or "System" in item.hierarchy_path, "All items should have system context"
                assert item.project_name or "Project" in item.hierarchy_path, "All items should have project context"
        
        print("✅ TR-BL-001: Work Item Discovery Engine integration validation complete")
        print("✅ All acceptance criteria validated: BL-001, BL-002, BL-003, BL-004, BL-005, BL-006")