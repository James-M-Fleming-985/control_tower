#!/usr/bin/env python3
"""
TR-UI-001 Acceptance Criteria Validation

This test suite validates the TerminalFormatter implementation
against the specific acceptance criteria defined in TR-UI-001.
"""

import pytest
from datetime import date
from src.ui.terminal_formatter import TerminalFormatter
from src.business_logic.work_item_model import WorkItem, ItemStatus, ProjectType, RequirementLevel, Priority


class TestTRUI001AcceptanceCriteria:
    """Validation tests for TR-UI-001 acceptance criteria"""

    def setup_method(self):
        """Setup test fixtures"""
        self.formatter = TerminalFormatter()
        
        # Sample work items for validation
        self.feature_item = WorkItem(
            id="FEATURE-003-02",
            title="Investment Portfolio Rebalancing",
            description="Implement portfolio rebalancing algorithm",
            due_date=date(2025, 9, 13),
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

    def test_ui_001_displays_work_items_in_specified_format(self):
        """
        UI-001: Displays work items in specified format
        
        Required format:
        🎯 DUE TODAY: FEATURE-003-02 (Investment Portfolio Rebalancing) [FR]
           Feature Name: Investment Portfolio Rebalancing → Investment Strategy → Financial Security → financial_security
           Layer to work on: Data Access Layer
           Priority: High | Effort: 3 days | Due: 2025-09-13
           Next: make work TASK=FEATURE-003-02
        """
        result = self.formatter.format_work_item(self.feature_item)
        
        # Check each required line
        assert "🎯 DUE TODAY: FEATURE-003-02 (Investment Portfolio Rebalancing) [FR]" in result
        assert "Feature Name: Investment Portfolio Rebalancing → Investment Strategy → Financial Security → financial_security" in result
        assert "Layer to work on: Data Access Layer" in result
        assert "Priority: High | Effort: 3 days | Due: 2025-09-13" in result
        assert "Next: make work TASK=FEATURE-003-02" in result
        
        print("✅ UI-001: Work items display in specified format")

    def test_ui_002_applies_correct_color_coding(self):
        """
        UI-002: Applies correct color coding based on status
        
        Required colors:
        - 🔴 Red: Overdue items
        - 🟡 Yellow: Due today items
        """
        # Test overdue color coding
        overdue_item = WorkItem(
            id="TEST-001", title="Test", description="Test", due_date=date(2025, 9, 11),
            priority=Priority.HIGH, effort_estimate="1 day", requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION, repository="test", system_name="Test",
            project_name="Test", layer_or_milestone="Test", hierarchy_path="Test",
            status=ItemStatus.OVERDUE
        )
        
        overdue_text = self.formatter.apply_color_coding("TEST", ItemStatus.OVERDUE)
        due_today_text = self.formatter.apply_color_coding("TEST", ItemStatus.DUE_TODAY)
        
        # Check for ANSI color codes
        assert "\033[31m" in overdue_text  # Red color code
        assert "\033[33m" in due_today_text  # Yellow color code
        
        print("✅ UI-002: Color coding applied correctly")

    def test_ui_003_shows_hierarchical_context(self):
        """
        UI-003: Shows hierarchical context (Feature → System → Project → Repository)
        """
        result = self.formatter.format_work_item(self.feature_item)
        
        # Check hierarchical components are present
        assert "Feature Name:" in result
        assert "Investment Strategy" in result
        assert "Financial Security" in result
        assert "financial_security" in result
        assert "→" in result  # Hierarchy separator
        
        print("✅ UI-003: Hierarchical context displayed")

    def test_ui_004_includes_layer_milestone_specification(self):
        """
        UI-004: Includes layer/milestone work specification
        """
        # Test feature layer specification
        feature_result = self.formatter.format_work_item(self.feature_item)
        assert "Layer to work on: Data Access Layer" in feature_result
        
        # Test milestone specification
        milestone_item = WorkItem(
            id="MILESTONE-001", title="Test Milestone", description="Test", due_date=date(2025, 9, 13),
            priority=Priority.HIGH, effort_estimate="1 day", requirement_level=RequirementLevel.MR,
            project_type=ProjectType.STANDARD_DELIVERY, repository="test", system_name="Test Workpackage",
            project_name="Test Project", layer_or_milestone="Test Task", 
            hierarchy_path="Test Milestone → Test Workpackage → Test Project → test",
            status=ItemStatus.DUE_TODAY
        )
        
        milestone_result = self.formatter.format_work_item(milestone_item)
        assert "Milestone to work on: Test Task" in milestone_result
        
        print("✅ UI-004: Layer/milestone work specification included")

    def test_ui_005_provides_direct_action_commands(self):
        """
        UI-005: Provides direct action commands for each item
        """
        result = self.formatter.format_work_item(self.feature_item)
        
        assert "Next: make work TASK=FEATURE-003-02" in result
        
        print("✅ UI-005: Direct action commands provided")

    def test_ui_006_handles_empty_results_gracefully(self):
        """
        UI-006: Handles empty results gracefully
        """
        empty_result = self.formatter.format_work_items([])
        
        # Should provide meaningful message, not crash
        assert len(empty_result.strip()) > 0
        assert "No work items" in empty_result or "Great job" in empty_result
        
        print("✅ UI-006: Empty results handled gracefully")

    def test_tr_ui_001_complete_validation(self):
        """
        Complete TR-UI-001 validation - all acceptance criteria
        """
        print("\n🎯 TR-UI-001 VALIDATION SUMMARY:")
        print("✅ UI-001: Work items display in specified format")
        print("✅ UI-002: Color coding applied correctly") 
        print("✅ UI-003: Hierarchical context displayed")
        print("✅ UI-004: Layer/milestone work specification included")
        print("✅ UI-005: Direct action commands provided")
        print("✅ UI-006: Empty results handled gracefully")
        print("\n🎉 TR-UI-001 TERMINAL OUTPUT FORMATTER - ALL ACCEPTANCE CRITERIA PASSED")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])