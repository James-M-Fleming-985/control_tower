#!/usr/bin/env python3
"""
Validation Tests for TR-BL-002 Priority Calculator

Maps directly to acceptance criteria from Phase 1 Layer Requirements
Validates business logic layer meets all specified requirements
"""

import pytest
from datetime import date, timedelta
from src.business_logic.priority_calculator import BasicPriorityCalculator, PriorityCategory
from src.business_logic.work_item_model import WorkItem, ItemStatus, ProjectType, Priority, RequirementLevel


class TestTRBL002Validation:
    """Validation tests mapping to TR-BL-002 acceptance criteria"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = BasicPriorityCalculator()
        self.today = date.today()
        
        # Standard test items
        self.overdue_item = WorkItem(
            id="task1",
            title="Overdue Task",
            description="Test overdue task",
            status=ItemStatus.OVERDUE,
            due_date=self.today - timedelta(days=2),
            project_type=ProjectType.APPLICATION,
            priority=Priority.HIGH,
            effort_estimate="2 days",
            requirement_level=RequirementLevel.TR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path"
        )
        
        self.due_today_item = WorkItem(
            id="task2", 
            title="Due Today Task",
            description="Test due today task",
            status=ItemStatus.DUE_TODAY,
            due_date=self.today,
            project_type=ProjectType.APPLICATION,
            priority=Priority.MEDIUM,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.FR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path"
        )
        
        self.future_item = WorkItem(
            id="task3",
            title="Future Task", 
            description="Test future task",
            status=ItemStatus.UPCOMING,
            due_date=self.today + timedelta(days=5),
            project_type=ProjectType.STANDARD_DELIVERY,
            priority=Priority.LOW,
            effort_estimate="3 days",
            requirement_level=RequirementLevel.MR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Milestone",
            hierarchy_path="Test/Path"
        )
        
        self.no_date_item = WorkItem(
            id="task4",
            title="No Date Task",
            description="Test no date task",
            status=ItemStatus.UPCOMING,
            due_date=None,
            project_type=ProjectType.APPLICATION,
            priority=Priority.LOW,
            effort_estimate="1 week",
            requirement_level=RequirementLevel.TR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path"
        )
    
    def test_bl_001_accurate_priority_calculation(self):
        """
        BL-001: Priority calculator accurately calculates priority scores
        Validates: Overdue items (100+), Due today (50-99), Others (lower)
        """
        # Test overdue items get highest scores (100+)
        overdue_score = self.calculator.calculate_priority_score(self.overdue_item)
        assert overdue_score >= 100, f"Overdue item should have score 100+, got {overdue_score}"
        
        # Test due today items get high scores (50-99)
        due_today_score = self.calculator.calculate_priority_score(self.due_today_item)
        assert 50 <= due_today_score <= 99, f"Due today item should have score 50-99, got {due_today_score}"
        
        # Test future items get lower scores
        future_score = self.calculator.calculate_priority_score(self.future_item)
        assert future_score < 50, f"Future item should have score <50, got {future_score}"
        
        # Test no date items get lowest scores
        no_date_score = self.calculator.calculate_priority_score(self.no_date_item)
        assert no_date_score < 25, f"No date item should have low score, got {no_date_score}"
        
        # Validate priority ordering
        assert overdue_score > due_today_score > future_score > no_date_score
    
    def test_bl_002_overdue_prioritization(self):
        """
        BL-002: Priority calculator correctly identifies and prioritizes overdue items
        Validates: Overdue items ranked highest with correct overdue calculation
        """
        # Create items with different overdue amounts
        one_day_overdue = WorkItem(
            id="over1", title="1 Day Overdue",
            description="One day overdue task",
            status=ItemStatus.OVERDUE,
            due_date=self.today - timedelta(days=1),
            project_type=ProjectType.APPLICATION,
            priority=Priority.HIGH,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.TR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path"
        )
        
        five_days_overdue = WorkItem(
            id="over5", title="5 Days Overdue", 
            description="Five days overdue task",
            status=ItemStatus.OVERDUE,
            due_date=self.today - timedelta(days=5),
            project_type=ProjectType.APPLICATION,
            priority=Priority.HIGH,
            effort_estimate="2 days",
            requirement_level=RequirementLevel.TR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path"
        )
        
        # Test overdue detection
        assert self.calculator.is_overdue(one_day_overdue), "Should detect 1 day overdue"
        assert self.calculator.is_overdue(five_days_overdue), "Should detect 5 days overdue"
        assert not self.calculator.is_overdue(self.due_today_item), "Due today should not be overdue"
        assert not self.calculator.is_overdue(self.future_item), "Future should not be overdue"
        
        # Test more overdue = higher priority
        score_1_day = self.calculator.calculate_priority_score(one_day_overdue)
        score_5_days = self.calculator.calculate_priority_score(five_days_overdue)
        assert score_5_days > score_1_day, "5 days overdue should have higher priority than 1 day"
        
        # Test sorting puts most overdue first
        items = [one_day_overdue, self.due_today_item, five_days_overdue, self.future_item]
        sorted_items = self.calculator.sort_by_priority(items)
        assert sorted_items[0] == five_days_overdue, "Most overdue should be first"
        assert sorted_items[1] == one_day_overdue, "Less overdue should be second"
    
    def test_bl_003_discovery_order_preservation(self):
        """
        BL-003: Priority calculator maintains discovery order within same priority categories
        Validates: Original order preserved within each priority tier
        """
        # Create multiple items of same priority category
        future_1 = WorkItem(
            id="fut1", title="Future 1",
            description="Future task 1",
            status=ItemStatus.UPCOMING,
            due_date=self.today + timedelta(days=3),
            project_type=ProjectType.APPLICATION,
            priority=Priority.MEDIUM,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.FR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path/1"
        )
        
        future_2 = WorkItem(
            id="fut2", title="Future 2", 
            description="Future task 2",
            status=ItemStatus.UPCOMING,
            due_date=self.today + timedelta(days=4),
            project_type=ProjectType.APPLICATION,
            priority=Priority.MEDIUM,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.FR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path/2"
        )
        
        future_3 = WorkItem(
            id="fut3", title="Future 3",
            description="Future task 3",
            status=ItemStatus.UPCOMING, 
            due_date=self.today + timedelta(days=2),
            project_type=ProjectType.APPLICATION,
            priority=Priority.MEDIUM,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.FR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path/3"
        )
        
        # Test that discovery order is maintained within same category
        items = [future_1, future_2, future_3]
        sorted_items = self.calculator.sort_by_priority(items)
        
        # All should remain in original order since they're same category
        expected_order = [future_1, future_2, future_3]
        assert sorted_items == expected_order, "Discovery order should be maintained within category"
    
    def test_bl_004_missing_date_handling(self):
        """
        BL-004: Priority calculator gracefully handles items with missing due dates
        Validates: No crashes, appropriate low priority assignment
        """
        # Test single item with no date
        score = self.calculator.calculate_priority_score(self.no_date_item)
        assert isinstance(score, int), "Should return integer score for no date item"
        assert score > 0, "Should assign positive score even with no date"
        
        # Test sorting with mix of dated and undated items
        items = [self.no_date_item, self.overdue_item, self.due_today_item]
        sorted_items = self.calculator.sort_by_priority(items)
        
        # No date items should be last
        assert sorted_items[-1] == self.no_date_item, "No date item should be last priority"
        
        # Test list of only no-date items
        no_date_1 = WorkItem(id="nd1", title="No Date 1", description="No date task 1",
                           status=ItemStatus.UPCOMING, due_date=None, project_type=ProjectType.APPLICATION,
                           priority=Priority.LOW, effort_estimate="1 day", requirement_level=RequirementLevel.TR,
                           repository="test_repo", system_name="Test System", project_name="Test Project",
                           layer_or_milestone="Test Layer", hierarchy_path="Test/Path/1")
        no_date_2 = WorkItem(id="nd2", title="No Date 2", description="No date task 2",
                           status=ItemStatus.UPCOMING, due_date=None, project_type=ProjectType.APPLICATION,
                           priority=Priority.LOW, effort_estimate="1 day", requirement_level=RequirementLevel.TR,
                           repository="test_repo", system_name="Test System", project_name="Test Project",
                           layer_or_milestone="Test Layer", hierarchy_path="Test/Path/2")
        
        no_date_items = [no_date_1, no_date_2]
        sorted_no_dates = self.calculator.sort_by_priority(no_date_items)
        assert len(sorted_no_dates) == 2, "Should handle all no-date items"
        assert sorted_no_dates == no_date_items, "Should maintain order for no-date items"
    
    def test_bl_005_algorithm_consistency(self):
        """
        BL-005: Priority calculation algorithm is deterministic and consistent
        Validates: Same input always produces same output
        """
        # Test multiple calls return same result
        item = self.overdue_item
        score1 = self.calculator.calculate_priority_score(item)
        score2 = self.calculator.calculate_priority_score(item)
        score3 = self.calculator.calculate_priority_score(item)
        
        assert score1 == score2 == score3, "Priority calculation should be deterministic"
        
        # Test sorting is stable
        items = [self.future_item, self.overdue_item, self.due_today_item, self.no_date_item]
        sorted1 = self.calculator.sort_by_priority(items.copy())
        sorted2 = self.calculator.sort_by_priority(items.copy())
        sorted3 = self.calculator.sort_by_priority(items.copy())
        
        assert sorted1 == sorted2 == sorted3, "Sorting should be deterministic"
    
    def test_bl_006_edge_case_robustness(self):
        """
        BL-006: Priority calculator handles edge cases without errors
        Validates: Empty lists, single items, extreme dates
        """
        # Test empty list
        empty_sorted = self.calculator.sort_by_priority([])
        assert empty_sorted == [], "Should handle empty list gracefully"
        
        # Test single item
        single_sorted = self.calculator.sort_by_priority([self.overdue_item])
        assert single_sorted == [self.overdue_item], "Should handle single item"
        
        # Test extreme overdue date
        very_old_item = WorkItem(
            id="ancient", title="Ancient Task",
            description="Very old task",
            status=ItemStatus.OVERDUE,
            due_date=date(2020, 1, 1),  # Very old
            project_type=ProjectType.APPLICATION,
            priority=Priority.HIGH,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.TR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path"
        )
        
        score = self.calculator.calculate_priority_score(very_old_item)
        assert score > 1000, "Very overdue items should have very high scores"
        
        # Test far future date
        far_future_item = WorkItem(
            id="future", title="Far Future Task",
            description="Far future task",
            status=ItemStatus.UPCOMING,
            due_date=date(2030, 12, 31),  # Far future
            project_type=ProjectType.APPLICATION,
            priority=Priority.LOW,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.TR,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Path"
        )
        
        future_score = self.calculator.calculate_priority_score(far_future_item)
        assert isinstance(future_score, int), "Should handle far future dates"
        assert future_score < 100, "Far future should have low priority"
    
    def test_bl_007_priority_explanation_feature(self):
        """
        BL-007: Priority calculator provides explanations for priority decisions
        Validates: Human-readable rationale for each priority assignment
        """
        # Test explanation functionality exists and works
        explanation = self.calculator.get_priority_explanation(self.overdue_item)
        assert isinstance(explanation, str), "Should return string explanation"
        assert len(explanation) > 0, "Explanation should not be empty"
        assert "overdue" in explanation.lower(), "Should mention overdue in explanation"
        
        # Test different explanations for different categories
        due_today_explanation = self.calculator.get_priority_explanation(self.due_today_item)
        future_explanation = self.calculator.get_priority_explanation(self.future_item)
        no_date_explanation = self.calculator.get_priority_explanation(self.no_date_item)
        
        # Each should be different and relevant
        explanations = [explanation, due_today_explanation, future_explanation, no_date_explanation]
        assert len(set(explanations)) == 4, "Each category should have unique explanation"
        
        assert "today" in due_today_explanation.lower(), "Due today explanation should mention today"
        assert "no" in no_date_explanation.lower(), "No date explanation should mention missing date"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])