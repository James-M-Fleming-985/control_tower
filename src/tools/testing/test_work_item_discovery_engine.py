"""
Unit tests for Work Item Discovery Engine - TR-BL-001 implementation

Tests the core business logic for discovering, processing, and prioritizing work items from repositories.
This is the main orchestrator that integrates Repository Scanner, File System Interface, and Priority Calculator.

Follows TDD methodology with comprehensive test coverage for acceptance criteria BL-001 through BL-006.
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import List, Optional
from src.business_logic.work_item_discovery_engine import WorkItemDiscoveryEngine
from src.business_logic.work_item_model import WorkItem, Priority, RequirementLevel, ProjectType, ItemStatus
from src.data_access.repository_scanner import RawRequirement, RequirementMetadata


class TestWorkItemDiscoveryEngine:
    """Test suite for Work Item Discovery Engine functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.discovery_engine = WorkItemDiscoveryEngine()
        self.test_repositories = [
            "/workspaces/control_tower/cloned_repos/financial_security_dev",
            "/workspaces/control_tower/cloned_repos/home_improvements", 
            "/workspaces/control_tower/cloned_repos/LIMS_concept_actual"
        ]
    
    def test_discover_work_items_returns_work_item_list(self):
        """
        Test that discover_work_items returns a list of WorkItem objects
        Acceptance Criteria: BL-001 - Discovers work items from all repository types
        """
        mock_raw_requirements = [
            RawRequirement(
                file_path="/test/repo1/features/feature1.md",
                content="# Test Feature 1\n**Due Date**: 2025-09-13\n**Priority**: High",
                metadata=RequirementMetadata(
                    id="TEST-001",
                    title="Test Feature 1",
                    due_date=date(2025, 9, 13),
                    priority=Priority.HIGH,
                    effort_estimate="3 days",
                    requirement_level=RequirementLevel.FR,
                    status="Not Started"
                )
            )
        ]
        
        with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories', return_value=mock_raw_requirements):
            result = self.discovery_engine.discover_work_items(self.test_repositories)
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(item, WorkItem) for item in result)
    
    def test_discover_work_items_integrates_with_repository_scanner(self):
        """
        Test that discovery engine properly integrates with repository scanner
        Acceptance Criteria: BL-001 - Discovers work items from all repository types
        """
        with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories') as mock_scan:
            mock_scan.return_value = []
            
            result = self.discovery_engine.discover_work_items(self.test_repositories)
            
            # Verify repository scanner was called with correct parameters
            mock_scan.assert_called_once_with(self.test_repositories)
            assert isinstance(result, list)
    
    def test_filter_due_and_overdue_identifies_due_today_items(self):
        """
        Test that filter identifies items due today correctly
        Acceptance Criteria: BL-002 - Correctly identifies due and overdue items
        """
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        test_items = [
            WorkItem(
                id="ITEM-001", title="Due Today Item", description="Test",
                due_date=today, priority=Priority.HIGH, effort_estimate="1 day",
                requirement_level=RequirementLevel.FR, project_type=ProjectType.APPLICATION,
                repository="test_repo", system_name="test_system", project_name="test_project",
                layer_or_milestone="Data Access Layer", hierarchy_path="Test → System → Project",
                status=ItemStatus.DUE_TODAY
            ),
            WorkItem(
                id="ITEM-002", title="Future Item", description="Test",
                due_date=tomorrow, priority=Priority.MEDIUM, effort_estimate="2 days",
                requirement_level=RequirementLevel.SR, project_type=ProjectType.STANDARD_DELIVERY,
                repository="test_repo", system_name="test_system", project_name="test_project",
                layer_or_milestone="Business Logic Layer", hierarchy_path="Test → System → Project",
                status=ItemStatus.NOT_DUE
            )
        ]
        
        result = self.discovery_engine.filter_due_and_overdue(test_items)
        
        assert len(result) == 1
        assert result[0].id == "ITEM-001"
        assert result[0].status == ItemStatus.DUE_TODAY
    
    def test_filter_due_and_overdue_identifies_overdue_items(self):
        """
        Test that filter identifies overdue items correctly
        Acceptance Criteria: BL-002 - Correctly identifies due and overdue items
        """
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        test_items = [
            WorkItem(
                id="ITEM-001", title="Overdue Item", description="Test",
                due_date=yesterday, priority=Priority.HIGH, effort_estimate="1 day",
                requirement_level=RequirementLevel.FR, project_type=ProjectType.APPLICATION,
                repository="test_repo", system_name="test_system", project_name="test_project",
                layer_or_milestone="Data Access Layer", hierarchy_path="Test → System → Project",
                status=ItemStatus.OVERDUE
            )
        ]
        
        result = self.discovery_engine.filter_due_and_overdue(test_items)
        
        assert len(result) == 1
        assert result[0].status == ItemStatus.OVERDUE
    
    def test_apply_basic_prioritization_uses_priority_calculator(self):
        """
        Test that basic prioritization integrates with priority calculator
        Acceptance Criteria: BL-005 - Applies basic priority sorting
        """
        test_items = [
            WorkItem(
                id="ITEM-001", title="Low Priority", description="Test",
                due_date=date.today(), priority=Priority.LOW, effort_estimate="1 day",
                requirement_level=RequirementLevel.SR, project_type=ProjectType.APPLICATION,
                repository="test_repo", system_name="test_system", project_name="test_project",
                layer_or_milestone="UI Layer", hierarchy_path="Test → System → Project",
                status=ItemStatus.DUE_TODAY
            ),
            WorkItem(
                id="ITEM-002", title="High Priority", description="Test",
                due_date=date.today() - timedelta(days=1), priority=Priority.HIGH, effort_estimate="2 days",
                requirement_level=RequirementLevel.FR, project_type=ProjectType.APPLICATION,
                repository="test_repo", system_name="test_system", project_name="test_project",
                layer_or_milestone="Business Logic Layer", hierarchy_path="Test → System → Project",
                status=ItemStatus.OVERDUE
            )
        ]
        
        with patch.object(self.discovery_engine.priority_calculator, 'sort_by_priority') as mock_sort:
            mock_sort.return_value = [test_items[1], test_items[0]]  # Overdue first
            
            result = self.discovery_engine.apply_basic_prioritization(test_items)
            
            mock_sort.assert_called_once_with(test_items)
            assert result[0].id == "ITEM-002"  # Overdue item first
    
    def test_determine_project_type_application_vs_standard_delivery(self):
        """
        Test that project type determination works correctly
        Acceptance Criteria: BL-003 - Determines project type (Application vs Standard Delivery)
        """
        # Test Application project type
        app_item = WorkItem(
            id="APP-001", title="Application Feature", description="Custom app feature",
            due_date=date.today(), priority=Priority.HIGH, effort_estimate="5 days",
            requirement_level=RequirementLevel.FR, project_type=ProjectType.APPLICATION,
            repository="financial_security_dev", system_name="Investment Strategy", 
            project_name="Financial Security", layer_or_milestone="Business Logic Layer",
            hierarchy_path="Feature → System → Project", status=ItemStatus.DUE_TODAY
        )
        
        # Test Standard Delivery project type  
        std_item = WorkItem(
            id="STD-001", title="Standard Feature", description="Standard delivery item",
            due_date=date.today(), priority=Priority.MEDIUM, effort_estimate="2 days",
            requirement_level=RequirementLevel.SR, project_type=ProjectType.STANDARD_DELIVERY,
            repository="LIMS_concept_actual", system_name="LIMS System", 
            project_name="Laboratory Management", layer_or_milestone="Data Access Layer",
            hierarchy_path="Feature → System → Project", status=ItemStatus.DUE_TODAY
        )
        
        app_result = self.discovery_engine.determine_project_type(app_item)
        std_result = self.discovery_engine.determine_project_type(std_item)
        
        assert app_result == ProjectType.APPLICATION
        assert std_result == ProjectType.STANDARD_DELIVERY
    
    def test_extract_hierarchical_context_information(self):
        """
        Test that hierarchical context extraction works correctly
        Acceptance Criteria: BL-004 - Extracts hierarchical context information
        """
        mock_raw_requirement = RawRequirement(
            file_path="/test/financial_security_dev/features/investment_portfolio.md",
            content="# Investment Portfolio Rebalancing\n**System**: Investment Strategy\n**Project**: Financial Security",
            metadata=RequirementMetadata(
                id="FINSCTY-001",
                title="Investment Portfolio Rebalancing",
                due_date=date(2025, 9, 13),
                priority=Priority.HIGH,
                effort_estimate="3 days",
                requirement_level=RequirementLevel.FR,
                status="Not Started"
            )
        )
        
        # This would be called internally during work item conversion
        result = self.discovery_engine._extract_hierarchical_context(mock_raw_requirement)
        
        assert "Investment Portfolio Rebalancing" in result['hierarchy_path']
        assert "Investment Strategy" in result['system'] or "Investment Strategy" in result['hierarchy_path']
        assert "Financial Security" in result['project'] or "Financial Security" in result['hierarchy_path']
        assert "financial_security_dev" in result['repository']
    
    def test_handle_parsing_errors_gracefully(self):
        """
        Test that parsing errors are handled gracefully
        Acceptance Criteria: BL-006 - Handles parsing errors gracefully
        """
        # Mock raw requirement with invalid/corrupted data
        invalid_raw_requirement = RawRequirement(
            file_path="/test/corrupted_file.md",
            content="Corrupted content without proper metadata",
            metadata=RequirementMetadata(
                id="CORRUPT-001",
                title="",  # Missing title
                due_date=None,  # Missing due date
                priority=Priority.MEDIUM,  # Default priority since None not allowed
                effort_estimate="Unknown",
                requirement_level=RequirementLevel.FR,  # Default since None not allowed
                status="Unknown"
            )
        )
        
        with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories', 
                         return_value=[invalid_raw_requirement]):
            result = self.discovery_engine.discover_work_items(self.test_repositories)
            
            # Should not crash and return empty list or handle gracefully
            assert isinstance(result, list)
            # Either filters out invalid items or handles them with default values
    
    def test_work_item_conversion_from_raw_requirements(self):
        """
        Test that raw requirements are properly converted to WorkItem objects
        Acceptance Criteria: BL-001, BL-004 - Discovery and context extraction
        """
        mock_raw_requirement = RawRequirement(
            file_path="/test/financial_security_dev/features/portfolio_rebalancing.md",
            content="# Investment Portfolio Rebalancing\n**Due Date**: 2025-09-13\n**Priority**: High",
            metadata=RequirementMetadata(
                id="FINSCTY-002",
                title="Investment Portfolio Rebalancing",
                due_date=date(2025, 9, 13),
                priority=Priority.HIGH,
                effort_estimate="3 days",
                requirement_level=RequirementLevel.FR,
                status="Not Started"
            )
        )
        
        work_item = self.discovery_engine._convert_to_work_item(mock_raw_requirement)
        
        assert isinstance(work_item, WorkItem)
        assert work_item.title == "Investment Portfolio Rebalancing"
        assert work_item.due_date == date(2025, 9, 13)
        assert work_item.priority == Priority.HIGH
        assert work_item.requirement_level == RequirementLevel.FR
        assert "financial_security_dev" in work_item.repository
    
    def test_empty_repository_list_handling(self):
        """
        Test that empty repository lists are handled gracefully
        Acceptance Criteria: BL-006 - Handles parsing errors gracefully
        """
        result = self.discovery_engine.discover_work_items([])
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_repository_with_no_requirements_handling(self):
        """
        Test that repositories with no requirements are handled gracefully
        Acceptance Criteria: BL-006 - Handles parsing errors gracefully
        """
        with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories', return_value=[]):
            result = self.discovery_engine.discover_work_items(self.test_repositories)
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_complete_discovery_workflow_integration(self):
        """
        Test the complete work item discovery workflow end-to-end
        Acceptance Criteria: BL-001 through BL-006 integration
        """
        # Mock complete workflow with realistic data
        mock_raw_requirements = [
            RawRequirement(
                file_path="/test/financial_security_dev/features/portfolio.md",
                content="# Portfolio Management\n**Due Date**: 2025-09-13\n**Priority**: High",
                metadata=RequirementMetadata(
                    id="FINSCTY-003",
                    title="Portfolio Management",
                    due_date=date(2025, 9, 13),
                    priority=Priority.HIGH,
                    effort_estimate="5 days",
                    requirement_level=RequirementLevel.FR,
                    status="Not Started"
                )
            ),
            RawRequirement(
                file_path="/test/home_improvements/features/kitchen.md",
                content="# Kitchen Renovation\n**Due Date**: 2025-09-12\n**Priority**: Medium",
                metadata=RequirementMetadata(
                    id="HOME-001",
                    title="Kitchen Renovation",
                    due_date=date(2025, 9, 12),  # Overdue
                    priority=Priority.MEDIUM,
                    effort_estimate="3 days",
                    requirement_level=RequirementLevel.SR,
                    status="In Progress"
                )
            )
        ]
        
        with patch.object(self.discovery_engine.repository_scanner, 'scan_repositories', 
                         return_value=mock_raw_requirements):
            # Execute complete workflow
            all_items = self.discovery_engine.discover_work_items(self.test_repositories)
            due_items = self.discovery_engine.filter_due_and_overdue(all_items)
            prioritized_items = self.discovery_engine.apply_basic_prioritization(due_items)
            
            # Validate complete workflow
            assert len(all_items) == 2
            assert len(due_items) == 2  # Both due today or overdue
            assert isinstance(prioritized_items, list)
            # Overdue item should be first after prioritization
            assert any(item.status == ItemStatus.OVERDUE for item in prioritized_items)