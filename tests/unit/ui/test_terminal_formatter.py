#!/usr/bin/env python3
"""
TDD RED PHASE: Terminal Formatter Tests

Testing TR-UI-001: Terminal Output Formatter
Acceptance Criteria: UI-001 through UI-006
"""

import pytest
from datetime import date
from enum import Enum
from dataclasses import dataclass
from typing import List

# These imports will FAIL initially - that's the RED phase
from src.ui.terminal_formatter import TerminalFormatter
from src.business_logic.work_item_model import WorkItem, ItemStatus, ProjectType, RequirementLevel, Priority


class TestTerminalFormatter:
    """Unit tests for TerminalFormatter - RED PHASE (should fail initially)"""

    def setup_method(self):
        """Setup test fixtures"""
        self.formatter = TerminalFormatter()
        
        # Sample work items for testing
        self.feature_item = WorkItem(
            id="FEATURE-003-02",
            title="Investment Portfolio Rebalancing",
            description="Implement portfolio rebalancing algorithm",
            due_date=date(2025, 9, 13),  # Today
            priority=Priority.HIGH,
            effort_estimate="3 days",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="financial_security",
            system_name="Investment Strategy",
            project_name="Financial Security",
            layer_or_milestone="Data Access Layer",
            hierarchy_path="Investment Portfolio Rebalancing → Investment Strategy → Financial Security → financial_security",
            status=ItemStatus.DUE_TODAY
        )
        
        self.milestone_item = WorkItem(
            id="MILESTONE-004",
            title="Project Review Completion",
            description="Complete project documentation review",
            due_date=date(2025, 9, 11),  # Overdue
            priority=Priority.CRITICAL,
            effort_estimate="1 day",
            requirement_level=RequirementLevel.MR,
            project_type=ProjectType.STANDARD_DELIVERY,
            repository="professional_excellence",
            system_name="Professional Development Workpackage",
            project_name="Professional Excellence",
            layer_or_milestone="Documentation Review Task",
            hierarchy_path="Project Review Completion → Professional Development Workpackage → Professional Excellence → professional_excellence",
            status=ItemStatus.OVERDUE
        )

    def test_format_work_items_with_multiple_items(self):
        """RED: Test formatting multiple work items - UI-001"""
        work_items = [self.feature_item, self.milestone_item]
        
        result = self.formatter.format_work_items(work_items)
        
        # Should contain both items
        assert "FEATURE-003-02" in result
        assert "MILESTONE-004" in result
        assert "Investment Portfolio Rebalancing" in result
        assert "Project Review Completion" in result

    def test_format_work_item_due_today(self):
        """RED: Test formatting due today item - UI-001, UI-002"""
        result = self.formatter.format_work_item(self.feature_item)
        
        expected_lines = [
            "🎯 DUE TODAY: FEATURE-003-02 (Investment Portfolio Rebalancing) [FR]",
            "   Feature Name: Investment Portfolio Rebalancing → Investment Strategy → Financial Security → financial_security",
            "   Layer to work on: Data Access Layer",
            "   Priority: High | Effort: 3 days | Due: 2025-09-13",
            "   Next: make work TASK=FEATURE-003-02"
        ]
        
        for line in expected_lines:
            assert line in result

    def test_format_work_item_overdue(self):
        """RED: Test formatting overdue item - UI-001, UI-002"""
        result = self.formatter.format_work_item(self.milestone_item)
        
        expected_lines = [
            "⏰ OVERDUE: MILESTONE-004 (Project Review Completion) [MR] (2 days overdue)",
            "   Milestone Name: Project Review Completion → Professional Development Workpackage → Professional Excellence → professional_excellence",
            "   Milestone to work on: Documentation Review Task",
            "   Priority: Critical | Effort: 1 day | Due: 2025-09-11",
            "   Next: make work TASK=MILESTONE-004"
        ]
        
        for line in expected_lines:
            assert line in result

    def test_format_header_with_statistics(self):
        """RED: Test header formatting with statistics"""
        result = self.formatter.format_header(total_items=5, overdue_count=2)
        
        assert "5" in result  # Total items
        assert "2" in result  # Overdue count
        assert "overdue" in result.lower()

    def test_apply_color_coding_overdue(self):
        """RED: Test color coding for overdue items - UI-002"""
        text = "OVERDUE ITEM"
        result = self.formatter.apply_color_coding(text, ItemStatus.OVERDUE)
        
        # Should contain ANSI red color codes
        assert "\033[31m" in result or "\033[91m" in result  # Red color codes

    def test_apply_color_coding_due_today(self):
        """RED: Test color coding for due today items - UI-002"""
        text = "DUE TODAY ITEM"
        result = self.formatter.apply_color_coding(text, ItemStatus.DUE_TODAY)
        
        # Should contain ANSI yellow color codes
        assert "\033[33m" in result or "\033[93m" in result  # Yellow color codes

    def test_hierarchical_context_application_project(self):
        """RED: Test hierarchical context for application projects - UI-003"""
        result = self.formatter.format_work_item(self.feature_item)
        
        # Should show: Feature Name: → System → Project → Repository
        assert "Feature Name:" in result
        assert "Investment Strategy" in result
        assert "Financial Security" in result
        assert "financial_security" in result

    def test_hierarchical_context_standard_delivery(self):
        """RED: Test hierarchical context for standard delivery - UI-003"""
        result = self.formatter.format_work_item(self.milestone_item)
        
        # Should show: Milestone Name: → Workpackage → Project → Repository
        assert "Milestone Name:" in result
        assert "Professional Development Workpackage" in result
        assert "Professional Excellence" in result
        assert "professional_excellence" in result

    def test_layer_milestone_specification(self):
        """RED: Test layer/milestone work specification - UI-004"""
        feature_result = self.formatter.format_work_item(self.feature_item)
        milestone_result = self.formatter.format_work_item(self.milestone_item)
        
        # Feature should show layer
        assert "Layer to work on: Data Access Layer" in feature_result
        
        # Milestone should show milestone task
        assert "Milestone to work on: Documentation Review Task" in milestone_result

    def test_direct_action_commands(self):
        """RED: Test direct action command generation - UI-005"""
        result = self.formatter.format_work_item(self.feature_item)
        
        assert "Next: make work TASK=FEATURE-003-02" in result

    def test_empty_results_handling(self):
        """RED: Test graceful handling of empty results - UI-006"""
        empty_list = []
        result = self.formatter.format_work_items(empty_list)
        
        assert "No work items" in result or "Nothing due" in result
        assert len(result.strip()) > 0  # Should return meaningful message

    def test_format_work_items_maintains_order(self):
        """RED: Test that work items maintain priority order"""
        work_items = [self.milestone_item, self.feature_item]  # Overdue first
        result = self.formatter.format_work_items(work_items)
        
        # Overdue item should appear before due today item
        overdue_pos = result.find("MILESTONE-004")
        due_today_pos = result.find("FEATURE-003-02")
        assert overdue_pos < due_today_pos

if __name__ == "__main__":
    pytest.main([__file__, "-v"])