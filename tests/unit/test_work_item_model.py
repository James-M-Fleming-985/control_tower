#!/usr/bin/env python3
"""
Unit Tests for WorkItem Model - TR-BL-001

Tests the WorkItem model implementation that's used across all layers
for representing work items with proper metadata and status tracking.
"""

import pytest
from datetime import date, timedelta
from src.business_logic.work_item_model import (
    WorkItem, ItemStatus, ProjectType, Priority, RequirementLevel
)


class TestWorkItemModel:
    """Unit tests for WorkItem model implementation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
    
    def test_work_item_creation_with_all_fields(self):
        """Test that WorkItem can be created with all required fields"""
        item = WorkItem(
            id="TEST-001",
            title="Test Feature",
            description="Test description",
            due_date=self.today,
            priority=Priority.HIGH,
            effort_estimate="3 days",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Data Access Layer",
            hierarchy_path="Feature → System → Project → Repository",
            status=ItemStatus.DUE_TODAY
        )
        
        assert item.id == "TEST-001"
        assert item.title == "Test Feature"
        assert item.description == "Test description"
        assert item.due_date == self.today
        assert item.priority == Priority.HIGH
        assert item.effort_estimate == "3 days"
        assert item.requirement_level == RequirementLevel.FR
        assert item.project_type == ProjectType.APPLICATION
        assert item.repository == "test_repo"
        assert item.system_name == "Test System"
        assert item.project_name == "Test Project"
        assert item.layer_or_milestone == "Data Access Layer"
        assert item.hierarchy_path == "Feature → System → Project → Repository"
        assert item.status == ItemStatus.DUE_TODAY
    
    def test_work_item_overdue_detection(self):
        """Test overdue detection functionality"""
        overdue_item = WorkItem(
            id="OVERDUE-001",
            title="Overdue Task",
            description="Overdue description",
            due_date=self.yesterday,
            priority=Priority.HIGH,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="UI Layer",
            hierarchy_path="Feature → System → Project → Repository",
            status=ItemStatus.OVERDUE
        )
        
        assert overdue_item.is_overdue() == True
        assert overdue_item.is_due_today() == False
        assert overdue_item.days_overdue() == 1  # 1 day overdue
    
    def test_work_item_due_today_detection(self):
        """Test due today detection functionality"""
        due_today_item = WorkItem(
            id="TODAY-001",
            title="Due Today Task",
            description="Due today description",
            due_date=self.today,
            priority=Priority.MEDIUM,
            effort_estimate="2 days",
            requirement_level=RequirementLevel.SR,
            project_type=ProjectType.STANDARD_DELIVERY,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Milestone 1",
            hierarchy_path="Task → Milestone → Project → Repository",
            status=ItemStatus.DUE_TODAY
        )
        
        assert due_today_item.is_due_today() == True
        assert due_today_item.is_overdue() == False
        assert due_today_item.days_overdue() == 0  # Due today, not overdue
    
    def test_work_item_with_no_due_date(self):
        """Test work item with missing due date"""
        no_date_item = WorkItem(
            id="NODATE-001",
            title="No Date Task",
            description="No date description",
            due_date=None,  # No due date
            priority=Priority.LOW,
            effort_estimate="Unknown",
            requirement_level=RequirementLevel.TR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Integration Layer",
            hierarchy_path="Feature → System → Project → Repository",
            status=ItemStatus.UPCOMING
        )
        
        assert no_date_item.due_date is None
        assert no_date_item.is_overdue() == False
        assert no_date_item.is_due_today() == False
        assert no_date_item.days_overdue() == 0  # No due date, so 0
    
    def test_work_item_hierarchical_display_application(self):
        """Test hierarchical display for application projects"""
        app_item = WorkItem(
            id="APP-001",
            title="Application Feature",
            description="Application description",
            due_date=self.today,
            priority=Priority.HIGH,
            effort_estimate="5 days",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="app_repo",
            system_name="User Management",
            project_name="Core Platform",
            layer_or_milestone="Business Logic Layer",
            hierarchy_path="User Authentication → User Management → Core Platform → app_repo",
            status=ItemStatus.DUE_TODAY
        )
        
        display = app_item.get_hierarchical_display()
        assert "Feature Name:" in display
        assert "User Authentication → User Management → Core Platform → app_repo" in display
    
    def test_work_item_hierarchical_display_standard_delivery(self):
        """Test hierarchical display for standard delivery projects"""
        delivery_item = WorkItem(
            id="DEL-001",
            title="Delivery Milestone",
            description="Delivery description",
            due_date=self.today,
            priority=Priority.MEDIUM,
            effort_estimate="10 days",
            requirement_level=RequirementLevel.MR,
            project_type=ProjectType.STANDARD_DELIVERY,
            repository="delivery_repo",
            system_name="Database Migration",
            project_name="Platform Upgrade",
            layer_or_milestone="Migration Phase 1",
            hierarchy_path="Data Migration → Database Migration → Platform Upgrade → delivery_repo",
            status=ItemStatus.DUE_TODAY
        )
        
        display = delivery_item.get_hierarchical_display()
        assert "Milestone Name:" in display
        assert "Data Migration → Database Migration → Platform Upgrade → delivery_repo" in display
    
    def test_work_item_work_specification_application(self):
        """Test work specification for application projects"""
        app_item = WorkItem(
            id="APP-WORK-001",
            title="App Work",
            description="App work description",
            due_date=self.today,
            priority=Priority.HIGH,
            effort_estimate="3 days",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="app_repo",
            system_name="System",
            project_name="Project",
            layer_or_milestone="UI Layer",
            hierarchy_path="Path",
            status=ItemStatus.DUE_TODAY
        )
        
        work_spec = app_item.get_work_specification()
        assert "Layer to work on: UI Layer" == work_spec
    
    def test_work_item_work_specification_standard_delivery(self):
        """Test work specification for standard delivery projects"""
        delivery_item = WorkItem(
            id="DEL-WORK-001",
            title="Delivery Work",
            description="Delivery work description",
            due_date=self.today,
            priority=Priority.MEDIUM,
            effort_estimate="7 days",
            requirement_level=RequirementLevel.MR,
            project_type=ProjectType.STANDARD_DELIVERY,
            repository="delivery_repo",
            system_name="System",
            project_name="Project",
            layer_or_milestone="Phase 2 Milestone",
            hierarchy_path="Path",
            status=ItemStatus.DUE_TODAY
        )
        
        work_spec = delivery_item.get_work_specification()
        assert "Milestone to work on: Phase 2 Milestone" == work_spec
    
    def test_requirement_level_enum_values(self):
        """Test that all requirement levels are properly defined"""
        assert RequirementLevel.NSR.value == "NSR"
        assert RequirementLevel.PR.value == "PR"
        assert RequirementLevel.SR.value == "SR"
        assert RequirementLevel.FR.value == "FR"
        assert RequirementLevel.TR.value == "TR"
        assert RequirementLevel.MR.value == "MR"
    
    def test_priority_enum_values(self):
        """Test that all priority levels are properly defined"""
        assert Priority.CRITICAL.value == "Critical"
        assert Priority.HIGH.value == "High"
        assert Priority.MEDIUM.value == "Medium"
        assert Priority.LOW.value == "Low"
    
    def test_project_type_enum_values(self):
        """Test that all project types are properly defined"""
        assert ProjectType.APPLICATION.value == "application"
        assert ProjectType.STANDARD_DELIVERY.value == "standard_delivery"
    
    def test_item_status_enum_values(self):
        """Test that all item statuses are properly defined"""
        assert ItemStatus.DUE_TODAY.value == "due_today"
        assert ItemStatus.OVERDUE.value == "overdue"
        assert ItemStatus.UPCOMING.value == "upcoming"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])