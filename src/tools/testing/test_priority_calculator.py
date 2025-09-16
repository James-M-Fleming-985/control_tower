#!/usr/bin/env python3
"""
TDD RED PHASE: Priority Calculator Tests

Testing TR-BL-002: Priority Calculator (Basic)
Acceptance Criteria: BL-007 through BL-010
"""

import pytest
from datetime import date, timedelta
from typing import List

# These imports will FAIL initially - that's the RED phase
from src.business_logic.priority_calculator import BasicPriorityCalculator
from src.business_logic.work_item_model import WorkItem, ItemStatus, ProjectType, RequirementLevel, Priority


class TestBasicPriorityCalculator:
    """Unit tests for BasicPriorityCalculator - RED PHASE (should fail initially)"""

    def setup_method(self):
        """Setup test fixtures"""
        self.calculator = BasicPriorityCalculator()
        today = date.today()
        
        # Sample work items for testing
        self.overdue_item_1 = WorkItem(
            id="OVERDUE-001",
            title="Critical Overdue Task",
            description="Very overdue task",
            due_date=today - timedelta(days=3),  # 3 days overdue
            priority=Priority.CRITICAL,
            effort_estimate="2 days",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test → Test → Test → test_repo",
            status=ItemStatus.OVERDUE
        )
        
        self.overdue_item_2 = WorkItem(
            id="OVERDUE-002",
            title="Another Overdue Task",
            description="Another overdue task",
            due_date=today - timedelta(days=2),  # 2 days overdue
            priority=Priority.HIGH,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test → Test → Test → test_repo",
            status=ItemStatus.OVERDUE
        )
        
        self.due_today_item_1 = WorkItem(
            id="DUE-TODAY-001",
            title="Due Today Task 1",
            description="Task due today",
            due_date=today,  # Today
            priority=Priority.HIGH,
            effort_estimate="3 days",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test → Test → Test → test_repo",
            status=ItemStatus.DUE_TODAY
        )
        
        self.due_today_item_2 = WorkItem(
            id="DUE-TODAY-002",
            title="Due Today Task 2",
            description="Another task due today",
            due_date=today,  # Today
            priority=Priority.MEDIUM,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test → Test → Test → test_repo",
            status=ItemStatus.DUE_TODAY
        )

    def test_calculate_priority_score_overdue_items(self):
        """RED: Test priority score calculation for overdue items - BL-007"""
        score1 = self.calculator.calculate_priority_score(self.overdue_item_1)
        score2 = self.calculator.calculate_priority_score(self.overdue_item_2)
        
        # Overdue items should have priority score 100+
        assert score1 >= 100
        assert score2 >= 100

    def test_calculate_priority_score_due_today_items(self):
        """RED: Test priority score calculation for due today items - BL-008"""
        score1 = self.calculator.calculate_priority_score(self.due_today_item_1)
        score2 = self.calculator.calculate_priority_score(self.due_today_item_2)
        
        # Due today items should have priority score 50-99
        assert 50 <= score1 < 100
        assert 50 <= score2 < 100

    def test_sort_by_priority_overdue_first(self):
        """RED: Test that overdue items always appear first - BL-007"""
        mixed_items = [
            self.due_today_item_1,
            self.overdue_item_1,
            self.due_today_item_2,
            self.overdue_item_2
        ]
        
        sorted_items = self.calculator.sort_by_priority(mixed_items)
        
        # First two items should be overdue
        assert sorted_items[0].status == ItemStatus.OVERDUE
        assert sorted_items[1].status == ItemStatus.OVERDUE
        
        # Last two items should be due today
        assert sorted_items[2].status == ItemStatus.DUE_TODAY
        assert sorted_items[3].status == ItemStatus.DUE_TODAY

    def test_sort_by_priority_maintains_discovery_order(self):
        """RED: Test that discovery order is maintained within priority groups - BL-009"""
        # Test overdue items maintain order
        overdue_items = [self.overdue_item_1, self.overdue_item_2]
        sorted_overdue = self.calculator.sort_by_priority(overdue_items)
        
        assert sorted_overdue[0].id == "OVERDUE-001"  # First discovered
        assert sorted_overdue[1].id == "OVERDUE-002"  # Second discovered
        
        # Test due today items maintain order
        due_today_items = [self.due_today_item_1, self.due_today_item_2]
        sorted_due_today = self.calculator.sort_by_priority(due_today_items)
        
        assert sorted_due_today[0].id == "DUE-TODAY-001"  # First discovered
        assert sorted_due_today[1].id == "DUE-TODAY-002"  # Second discovered

    def test_is_overdue_method(self):
        """RED: Test is_overdue method accuracy"""
        assert self.calculator.is_overdue(self.overdue_item_1) == True
        assert self.calculator.is_overdue(self.due_today_item_1) == False

    def test_is_due_today_method(self):
        """RED: Test is_due_today method accuracy"""
        assert self.calculator.is_due_today(self.due_today_item_1) == True
        assert self.calculator.is_due_today(self.overdue_item_1) == False

    def test_handle_missing_due_dates_gracefully(self):
        """RED: Test graceful handling of missing due dates - BL-010"""
        # Create item with None due date
        item_no_date = WorkItem(
            id="NO-DATE-001",
            title="No Due Date Task",
            description="Task without due date",
            due_date=None,  # Missing due date
            priority=Priority.MEDIUM,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test → Test → Test → test_repo",
            status=ItemStatus.UPCOMING  # Default status
        )
        
        # Should not crash when calculating priority
        score = self.calculator.calculate_priority_score(item_no_date)
        assert isinstance(score, int)
        assert score >= 0  # Should return valid score
        
        # Should handle gracefully in sorting
        items_with_missing = [self.due_today_item_1, item_no_date, self.overdue_item_1]
        sorted_items = self.calculator.sort_by_priority(items_with_missing)
        assert len(sorted_items) == 3  # Should not lose items

    def test_empty_list_handling(self):
        """RED: Test handling of empty work item lists"""
        empty_list = []
        result = self.calculator.sort_by_priority(empty_list)
        
        assert result == []
        assert isinstance(result, list)

    def test_single_item_handling(self):
        """RED: Test handling of single work item"""
        single_item = [self.due_today_item_1]
        result = self.calculator.sort_by_priority(single_item)
        
        assert len(result) == 1
        assert result[0].id == "DUE-TODAY-001"

    def test_priority_score_consistency(self):
        """RED: Test that priority scores are consistent for same item"""
        score1 = self.calculator.calculate_priority_score(self.overdue_item_1)
        score2 = self.calculator.calculate_priority_score(self.overdue_item_1)
        
        assert score1 == score2  # Should be deterministic

    def test_complex_sorting_scenario(self):
        """RED: Test complex scenario with mixed items"""
        complex_items = [
            self.due_today_item_2,    # Due today (medium priority)
            self.overdue_item_1,      # Overdue (critical priority)  
            self.due_today_item_1,    # Due today (high priority)
            self.overdue_item_2,      # Overdue (high priority)
        ]
        
        sorted_items = self.calculator.sort_by_priority(complex_items)
        
        # Should maintain overdue first, then due today
        assert sorted_items[0].status == ItemStatus.OVERDUE
        assert sorted_items[1].status == ItemStatus.OVERDUE
        assert sorted_items[2].status == ItemStatus.DUE_TODAY
        assert sorted_items[3].status == ItemStatus.DUE_TODAY
        
        # Within overdue group, should maintain discovery order
        overdue_ids = [item.id for item in sorted_items[:2]]
        assert overdue_ids == ["OVERDUE-001", "OVERDUE-002"]  # Discovery order
        
        # Within due today group, should maintain discovery order
        due_today_ids = [item.id for item in sorted_items[2:]]
        assert due_today_ids == ["DUE-TODAY-002", "DUE-TODAY-001"]  # Discovery order

if __name__ == "__main__":
    pytest.main([__file__, "-v"])