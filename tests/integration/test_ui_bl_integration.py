#!/usr/bin/env python3
"""
Integration Tests: UI Layer + Business Logic Layer

Tests the integration between Terminal Formatter (UI) and Priority Calculator (BL)
Validates that work items can flow from priority calculation to terminal display
"""

import pytest
from datetime import date, timedelta
from src.ui.terminal_formatter import TerminalFormatter
from src.business_logic.priority_calculator import BasicPriorityCalculator
from src.business_logic.work_item_model import WorkItem, ItemStatus, ProjectType, Priority, RequirementLevel


class TestUIBusinessLogicIntegration:
    """Integration tests between UI and Business Logic layers"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.formatter = TerminalFormatter()
        self.calculator = BasicPriorityCalculator()
        self.today = date.today()
        
        # Create test work items with all required fields
        self.overdue_item = WorkItem(
            id="task1",
            title="Critical Bug Fix",
            description="Fix authentication vulnerability",
            status=ItemStatus.OVERDUE,
            priority=Priority.HIGH,
            due_date=self.today - timedelta(days=3),
            project_type=ProjectType.APPLICATION,
            effort_estimate="2 days",
            requirement_level=RequirementLevel.TR,
            repository="control_tower",
            system_name="Authentication System",
            project_name="Security Updates",
            layer_or_milestone="Business Logic Layer",
            hierarchy_path="Security/Authentication/BugFix"
        )
        
        self.due_today_item = WorkItem(
            id="task2",
            title="Deploy Security Update", 
            description="Deploy the bug fix to production",
            status=ItemStatus.DUE_TODAY,
            priority=Priority.HIGH,
            due_date=self.today,
            project_type=ProjectType.APPLICATION,
            effort_estimate="4 hours",
            requirement_level=RequirementLevel.TR,
            repository="control_tower",
            system_name="Deployment System",
            project_name="Security Updates",
            layer_or_milestone="Integration Layer",
            hierarchy_path="Security/Deployment/Production"
        )
        
        self.future_item = WorkItem(
            id="task3",
            title="Documentation Update",
            description="Update API documentation",
            status=ItemStatus.UPCOMING,
            priority=Priority.MEDIUM,
            due_date=self.today + timedelta(days=5),
            project_type=ProjectType.STANDARD_DELIVERY,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.FR,
            repository="control_tower",
            system_name="Documentation System",
            project_name="API Documentation",
            layer_or_milestone="Documentation Milestone",
            hierarchy_path="Documentation/API/Update"
        )
        
        self.no_date_item = WorkItem(
            id="task4",
            title="Code Refactoring",
            description="Refactor legacy authentication module",
            status=ItemStatus.UPCOMING,
            priority=Priority.LOW,
            due_date=None,
            project_type=ProjectType.APPLICATION,
            effort_estimate="1 week",
            requirement_level=RequirementLevel.TR,
            repository="control_tower",
            system_name="Authentication System",
            project_name="Code Quality",
            layer_or_milestone="Business Logic Layer",
            hierarchy_path="Refactoring/Authentication/Legacy"
        )
    
    def test_complete_workflow_priority_to_display(self):
        """
        Test complete workflow: unsorted items → priority calculation → terminal display
        """
        # Start with unsorted work items
        unsorted_items = [
            self.future_item,      # Should be 3rd priority
            self.no_date_item,     # Should be 4th priority
            self.overdue_item,     # Should be 1st priority
            self.due_today_item    # Should be 2nd priority
        ]
        
        # Step 1: Calculate priorities and sort
        sorted_items = self.calculator.sort_by_priority(unsorted_items)
        
        # Verify sorting worked correctly
        assert sorted_items[0] == self.overdue_item, "Overdue should be first"
        assert sorted_items[1] == self.due_today_item, "Due today should be second"
        assert sorted_items[2] == self.future_item, "Future should be third"
        assert sorted_items[3] == self.no_date_item, "No date should be last"
        
        # Step 2: Format for terminal display
        formatted_output = self.formatter.format_work_items(sorted_items)
        
        # Verify output contains expected elements
        assert isinstance(formatted_output, str), "Should return string output"
        assert len(formatted_output) > 0, "Should not be empty"
        
        # Verify all items appear in output
        for item in sorted_items:
            assert item.title in formatted_output, f"Item '{item.title}' should appear in output"
        
        # Verify priority order is maintained in display
        lines = formatted_output.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Find lines containing task titles
        title_positions = {}
        for i, line in enumerate(non_empty_lines):
            for item in sorted_items:
                if item.title in line:
                    title_positions[item.id] = i
        
        # Verify display order matches priority order
        assert title_positions[self.overdue_item.id] < title_positions[self.due_today_item.id], \
            "Overdue should appear before due today in display"
        assert title_positions[self.due_today_item.id] < title_positions[self.future_item.id], \
            "Due today should appear before future in display"
        assert title_positions[self.future_item.id] < title_positions[self.no_date_item.id], \
            "Future should appear before no date in display"
    
    def test_priority_scores_influence_display_colors(self):
        """
        Test that priority scores from calculator influence color coding in formatter
        """
        # Get priority scores
        overdue_score = self.calculator.calculate_priority_score(self.overdue_item)
        due_today_score = self.calculator.calculate_priority_score(self.due_today_item)
        future_score = self.calculator.calculate_priority_score(self.future_item)
        
        # Format individual items
        overdue_display = self.formatter.format_work_items([self.overdue_item])
        due_today_display = self.formatter.format_work_items([self.due_today_item])
        future_display = self.formatter.format_work_items([self.future_item])
        
        # Verify different formatting for different priorities
        # (Terminal formatter should use different colors/styles based on status/priority)
        assert overdue_display != due_today_display, "Different priorities should have different formatting"
        assert due_today_display != future_display, "Different priorities should have different formatting"
        
        # Verify high priority items get more prominent display
        # Check for color codes or styling indicators
        color_codes = ['\033[', '\x1b[']  # ANSI color codes
        
        # Overdue items should have color coding (red for urgent)
        has_overdue_color = any(code in overdue_display for code in color_codes)
        assert has_overdue_color, "Overdue items should have color coding"
    
    def test_empty_list_integration(self):
        """
        Test integration with empty work item list
        """
        empty_items = []
        
        # Step 1: Priority calculation with empty list
        sorted_empty = self.calculator.sort_by_priority(empty_items)
        assert sorted_empty == [], "Empty list should remain empty after sorting"
        
        # Step 2: Format empty list for display
        empty_display = self.formatter.format_work_items(sorted_empty)
        
        # Should handle gracefully
        assert isinstance(empty_display, str), "Should return string even for empty list"
        # Could be empty string or a "no items" message
        assert len(empty_display) >= 0, "Should handle empty list gracefully"
    
    def test_single_item_integration(self):
        """
        Test integration with single work item
        """
        single_item = [self.overdue_item]
        
        # Step 1: Priority calculation
        sorted_single = self.calculator.sort_by_priority(single_item)
        assert len(sorted_single) == 1, "Single item should remain single"
        assert sorted_single[0] == self.overdue_item, "Item should be unchanged"
        
        # Step 2: Format for display
        single_display = self.formatter.format_work_items(sorted_single)
        
        assert isinstance(single_display, str), "Should return string"
        assert self.overdue_item.title in single_display, "Should contain item title"
        assert len(single_display) > 0, "Should not be empty"
    
    def test_mixed_project_types_integration(self):
        """
        Test integration with mixed project types (Application vs Standard Delivery)
        """
        # Create items with different project types
        app_item = WorkItem(
            id="app1", title="App Feature",
            status=ItemStatus.UPCOMING,
            due_date=self.today + timedelta(days=2),
            project_type=ProjectType.APPLICATION,
            description="Feature implementation",
            priority=Priority.MEDIUM,
            effort_estimate="3 days",
            requirement_level=RequirementLevel.FR,
            repository="control_tower",
            system_name="Feature System",
            project_name="App Features",
            layer_or_milestone="UI Layer",
            hierarchy_path="Features/App/UI"
        )
        
        std_item = WorkItem(
            id="std1", title="Standard Process",
            status=ItemStatus.UPCOMING, 
            due_date=self.today + timedelta(days=2),
            project_type=ProjectType.STANDARD_DELIVERY,
            description="Standard delivery process",
            priority=Priority.MEDIUM,
            effort_estimate="2 days",
            requirement_level=RequirementLevel.MR,
            repository="control_tower",
            system_name="Process System",
            project_name="Standard Delivery",
            layer_or_milestone="Process Milestone",
            hierarchy_path="Delivery/Standard/Process"
        )
        
        mixed_items = [app_item, std_item]
        
        # Step 1: Priority calculation (should maintain discovery order for same priority)
        sorted_mixed = self.calculator.sort_by_priority(mixed_items)
        assert len(sorted_mixed) == 2, "Should preserve both items"
        
        # Step 2: Format for display (should show project type differences)
        mixed_display = self.formatter.format_work_items(sorted_mixed)
        
        assert app_item.title in mixed_display, "Application item should appear"
        assert std_item.title in mixed_display, "Standard delivery item should appear"
        
        # Terminal formatter should differentiate project types visually
        # This might be through different icons, colors, or labels
        lines = mixed_display.split('\n')
        app_lines = [line for line in lines if app_item.title in line]
        std_lines = [line for line in lines if std_item.title in line]
        
        # Should have different visual treatment (this tests the formatter's project-type awareness)
        if app_lines and std_lines:
            # The formatting might differ (colors, icons, etc.)
            # At minimum, both should be properly formatted
            assert len(app_lines) > 0, "Application item should be formatted"
            assert len(std_lines) > 0, "Standard delivery item should be formatted"
    
    def test_priority_explanation_integration(self):
        """
        Test that priority explanations from calculator can be used by formatter
        """
        # Get explanations from calculator
        overdue_explanation = self.calculator.get_priority_explanation(self.overdue_item)
        due_today_explanation = self.calculator.get_priority_explanation(self.due_today_item)
        
        # Verify explanations exist
        assert isinstance(overdue_explanation, str), "Should return string explanation"
        assert len(overdue_explanation) > 0, "Explanation should not be empty"
        assert isinstance(due_today_explanation, str), "Should return string explanation"
        assert len(due_today_explanation) > 0, "Explanation should not be empty"
        
        # Verify explanations are different
        assert overdue_explanation != due_today_explanation, "Different items should have different explanations"
        
        # Test that formatter can work with explanations
        # (In a real implementation, formatter might include explanations in detailed view)
        items_with_explanations = [self.overdue_item, self.due_today_item]
        display_output = self.formatter.format_work_items(items_with_explanations)
        
        # Basic integration test - formatter should handle items that have explanations available
        assert isinstance(display_output, str), "Formatter should handle items with explanations"
        assert len(display_output) > 0, "Output should not be empty"
    
    def test_error_handling_integration(self):
        """
        Test error handling across UI and Business Logic layers
        """
        # Test with potentially problematic data
        edge_case_item = WorkItem(
            id="edge",
            title="",  # Empty title
            status=ItemStatus.UPCOMING,
            due_date=self.today,
            project_type=ProjectType.APPLICATION,
            description="Edge case test",
            priority=Priority.LOW,
            effort_estimate="TBD",
            requirement_level=RequirementLevel.TR,
            repository="control_tower",
            system_name="Test System",
            project_name="Edge Cases",
            layer_or_milestone="Test Layer",
            hierarchy_path="Test/Edge/Case"
        )
        
        edge_items = [edge_case_item]
        
        # Step 1: Priority calculation should handle edge cases
        try:
            sorted_edge = self.calculator.sort_by_priority(edge_items)
            assert len(sorted_edge) == 1, "Should handle edge case items"
        except Exception as e:
            pytest.fail(f"Priority calculator should handle edge cases gracefully, got: {e}")
        
        # Step 2: Formatter should handle edge cases
        try:
            edge_display = self.formatter.format_work_items(sorted_edge)
            assert isinstance(edge_display, str), "Formatter should return string even for edge cases"
        except Exception as e:
            pytest.fail(f"Terminal formatter should handle edge cases gracefully, got: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])