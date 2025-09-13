#!/usr/bin/env python3
"""
End-to-End Integration Test - Complete Layer Integration

Tests the complete workflow across all implemented layers:
- UI Layer: Terminal Formatter 
- Business Logic Layer: Priority Calculator
- Complete WorkItem data flow and display

This validates that all layers work together as a cohesive system.
"""

import pytest
from datetime import date, timedelta
from src.ui.terminal_formatter import TerminalFormatter, ColorScheme
from src.business_logic.priority_calculator import BasicPriorityCalculator
from src.business_logic.work_item_model import (
    WorkItem, ItemStatus, ProjectType, Priority, RequirementLevel
)


class TestEndToEndLayerIntegration:
    """End-to-end tests across all implemented layers"""
    
    def setup_method(self):
        """Set up complete test scenario"""
        self.formatter = TerminalFormatter()
        self.calculator = BasicPriorityCalculator()
        self.today = date.today()
        
        # Create realistic work items representing a typical development scenario
        self.work_items = self._create_realistic_work_scenario()
    
    def _create_realistic_work_scenario(self):
        """Create realistic work items representing mixed project states"""
        return [
            # Overdue critical security issue
            WorkItem(
                id="SEC-001",
                title="Fix Authentication Bypass Vulnerability",
                description="Critical security vulnerability allowing authentication bypass",
                status=ItemStatus.OVERDUE,
                priority=Priority.CRITICAL,
                due_date=self.today - timedelta(days=5),
                project_type=ProjectType.APPLICATION,
                effort_estimate="1 day",
                requirement_level=RequirementLevel.TR,
                repository="control_tower",
                system_name="Authentication System",
                project_name="Security Critical Fixes",
                layer_or_milestone="Business Logic Layer",
                hierarchy_path="Security/Authentication/CriticalFix"
            ),
            
            # Due today deployment
            WorkItem(
                id="DEP-001", 
                title="Deploy Q3 Security Updates",
                description="Deploy all security updates for Q3 release",
                status=ItemStatus.DUE_TODAY,
                priority=Priority.HIGH,
                due_date=self.today,
                project_type=ProjectType.STANDARD_DELIVERY,
                effort_estimate="4 hours",
                requirement_level=RequirementLevel.MR,
                repository="control_tower",
                system_name="Deployment Pipeline",
                project_name="Q3 Release",
                layer_or_milestone="Q3 Security Milestone",
                hierarchy_path="Release/Q3/Security/Deploy"
            ),
            
            # Overdue but less critical
            WorkItem(
                id="DOC-001",
                title="Update API Documentation", 
                description="Update documentation for new authentication endpoints",
                status=ItemStatus.OVERDUE,
                priority=Priority.MEDIUM,
                due_date=self.today - timedelta(days=2),
                project_type=ProjectType.STANDARD_DELIVERY,
                effort_estimate="2 days",
                requirement_level=RequirementLevel.FR,
                repository="control_tower",
                system_name="Documentation System",
                project_name="API Documentation Updates",
                layer_or_milestone="Documentation Milestone",
                hierarchy_path="Documentation/API/Authentication"
            ),
            
            # Future feature work
            WorkItem(
                id="FEAT-001",
                title="Implement Multi-Factor Authentication",
                description="Add MFA support to enhance security",
                status=ItemStatus.UPCOMING,
                priority=Priority.HIGH,
                due_date=self.today + timedelta(days=7),
                project_type=ProjectType.APPLICATION,
                effort_estimate="1 week",
                requirement_level=RequirementLevel.FR,
                repository="control_tower",
                system_name="Authentication System",
                project_name="Enhanced Security Features",
                layer_or_milestone="Business Logic Layer",
                hierarchy_path="Security/Authentication/MFA"
            ),
            
            # Refactoring work without due date
            WorkItem(
                id="REF-001",
                title="Refactor Legacy Authentication Code",
                description="Clean up and modernize authentication codebase",
                status=ItemStatus.UPCOMING,
                priority=Priority.LOW,
                due_date=None,
                project_type=ProjectType.APPLICATION,
                effort_estimate="2 weeks",
                requirement_level=RequirementLevel.TR,
                repository="control_tower",
                system_name="Authentication System", 
                project_name="Code Quality Improvements",
                layer_or_milestone="Business Logic Layer",
                hierarchy_path="Refactoring/Authentication/Legacy"
            ),
            
            # Another due today item
            WorkItem(
                id="TEST-001",
                title="Complete Security Testing",
                description="Finish penetration testing for authentication system",
                status=ItemStatus.DUE_TODAY,
                priority=Priority.HIGH,
                due_date=self.today,
                project_type=ProjectType.STANDARD_DELIVERY,
                effort_estimate="6 hours",
                requirement_level=RequirementLevel.MR,
                repository="control_tower",
                system_name="Testing System",
                project_name="Security Validation",
                layer_or_milestone="Security Testing Milestone",
                hierarchy_path="Testing/Security/Penetration"
            )
        ]
    
    def test_complete_what_next_workflow(self):
        """
        Test the complete 'make what-next' workflow end-to-end
        
        This simulates the exact user experience:
        1. Unsorted work items from discovery
        2. Priority calculation and sorting
        3. Terminal formatting and display
        4. User sees prioritized, color-coded output
        """
        print("\n" + "="*80)
        print("TESTING COMPLETE 'make what-next' WORKFLOW")
        print("="*80)
        
        # STEP 1: Start with unsorted work items (as they would come from discovery)
        unsorted_items = self.work_items.copy()
        print(f"\n📋 Starting with {len(unsorted_items)} unsorted work items:")
        for i, item in enumerate(unsorted_items, 1):
            print(f"  {i}. {item.title} ({item.status.value}, {item.priority.value})")
        
        # STEP 2: Calculate priorities and sort
        print(f"\n🧮 Calculating priorities with BasicPriorityCalculator...")
        sorted_items = self.calculator.sort_by_priority(unsorted_items)
        
        # Verify sorting worked correctly
        assert len(sorted_items) == len(unsorted_items), "Should preserve all items"
        
        print(f"✅ Priority calculation complete. Results:")
        for i, item in enumerate(sorted_items, 1):
            score = self.calculator.calculate_priority_score(item)
            explanation = self.calculator.get_priority_explanation(item)
            print(f"  {i}. {item.title}")
            print(f"     Priority Score: {score}")
            print(f"     Rationale: {explanation}")
        
        # STEP 3: Format for terminal display
        print(f"\n🎨 Formatting for terminal display with TerminalFormatter...")
        formatted_output = self.formatter.format_work_items(sorted_items)
        
        # Verify output exists and contains all items
        assert isinstance(formatted_output, str), "Should return string output"
        assert len(formatted_output) > 0, "Should not be empty"
        
        for item in sorted_items:
            assert item.title in formatted_output, f"Output should contain '{item.title}'"
        
        print(f"✅ Terminal formatting complete.")
        print(f"\n📺 FINAL 'make what-next' OUTPUT:")
        print("-" * 80)
        print(formatted_output)
        print("-" * 80)
        
        # STEP 4: Validate priority ordering in output
        self._validate_priority_ordering_in_output(sorted_items, formatted_output)
        
        # STEP 5: Validate visual formatting quality
        self._validate_visual_formatting_quality(formatted_output)
        
        print(f"\n✅ End-to-end workflow test PASSED!")
        print(f"   - All {len(sorted_items)} items properly prioritized")
        print(f"   - Priority ordering maintained in display")
        print(f"   - Visual formatting applied correctly")
        print("="*80)
    
    def test_priority_score_accuracy_end_to_end(self):
        """
        Test that priority scores accurately reflect business rules across layers
        """
        # Get the critical overdue item (should have highest score)
        critical_overdue = next(item for item in self.work_items if item.id == "SEC-001")
        
        # Get due today items (should have high but lower scores)
        due_today_items = [item for item in self.work_items if item.status == ItemStatus.DUE_TODAY]
        
        # Get future item (should have medium score)
        future_item = next(item for item in self.work_items if item.id == "FEAT-001")
        
        # Get no-date item (should have lowest score)
        no_date_item = next(item for item in self.work_items if item.due_date is None)
        
        # Calculate scores
        critical_score = self.calculator.calculate_priority_score(critical_overdue)
        due_today_scores = [self.calculator.calculate_priority_score(item) for item in due_today_items]
        future_score = self.calculator.calculate_priority_score(future_item)
        no_date_score = self.calculator.calculate_priority_score(no_date_item)
        
        # Validate score ordering matches business rules
        assert critical_score >= 100, f"Critical overdue should be 100+, got {critical_score}"
        assert all(50 <= score <= 99 for score in due_today_scores), "Due today should be 50-99"
        assert future_score < 50, f"Future should be <50, got {future_score}"
        assert no_date_score < 25, f"No date should be <25, got {no_date_score}"
        
        # Validate relative ordering
        assert critical_score > max(due_today_scores), "Critical overdue > due today"
        assert min(due_today_scores) > future_score, "Due today > future"
        assert future_score > no_date_score, "Future > no date"
        
        print(f"\n📊 PRIORITY SCORE VALIDATION:")
        print(f"   Critical Overdue: {critical_score} (5 days overdue)")
        print(f"   Due Today Items: {due_today_scores} (due today)")
        print(f"   Future Item: {future_score} (due in 7 days)")
        print(f"   No Date Item: {no_date_score} (no due date)")
        print(f"   ✅ All priority scores follow business rules correctly")
    
    def test_project_type_differentiation_end_to_end(self):
        """
        Test that project types are differentiated correctly across layers
        """
        # Separate items by project type
        app_items = [item for item in self.work_items if item.project_type == ProjectType.APPLICATION]
        std_items = [item for item in self.work_items if item.project_type == ProjectType.STANDARD_DELIVERY]
        
        assert len(app_items) > 0, "Should have application items"
        assert len(std_items) > 0, "Should have standard delivery items"
        
        # Sort each group
        sorted_app_items = self.calculator.sort_by_priority(app_items)
        sorted_std_items = self.calculator.sort_by_priority(std_items)
        
        # Format each group
        app_output = self.formatter.format_work_items(sorted_app_items)
        std_output = self.formatter.format_work_items(sorted_std_items)
        
        # Verify both formats work
        assert isinstance(app_output, str) and len(app_output) > 0, "App items should format"
        assert isinstance(std_output, str) and len(std_output) > 0, "Std items should format"
        
        # Verify project type specific elements appear
        for item in sorted_app_items:
            assert item.title in app_output, f"App output should contain {item.title}"
            # Application items should show "Feature Name" and "Layer to work on"
            hierarchical_display = item.get_hierarchical_display()
            work_spec = item.get_work_specification()
            assert "Feature Name:" in hierarchical_display, "App items should show Feature Name"
            assert "Layer to work on:" in work_spec, "App items should show Layer to work on"
        
        for item in sorted_std_items:
            assert item.title in std_output, f"Std output should contain {item.title}"
            # Standard delivery items should show "Milestone Name" and "Milestone to work on"
            hierarchical_display = item.get_hierarchical_display()
            work_spec = item.get_work_specification()
            assert "Milestone Name:" in hierarchical_display, "Std items should show Milestone Name"
            assert "Milestone to work on:" in work_spec, "Std items should show Milestone to work on"
        
        print(f"\n🏗️ PROJECT TYPE DIFFERENTIATION TEST:")
        print(f"   Application Items: {len(app_items)} (show Feature Name/Layer)")
        print(f"   Standard Delivery Items: {len(std_items)} (show Milestone Name/Milestone)")
        print(f"   ✅ Project types differentiated correctly across all layers")
    
    def _validate_priority_ordering_in_output(self, sorted_items, formatted_output):
        """Validate that priority ordering is maintained in terminal output"""
        lines = formatted_output.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Find lines containing task titles and their positions
        title_positions = {}
        for i, line in enumerate(non_empty_lines):
            for item in sorted_items:
                if item.title in line:
                    title_positions[item.id] = i
        
        # Verify that higher priority items appear earlier in the output
        for i in range(len(sorted_items) - 1):
            current_item = sorted_items[i]
            next_item = sorted_items[i + 1]
            
            if current_item.id in title_positions and next_item.id in title_positions:
                current_pos = title_positions[current_item.id]
                next_pos = title_positions[next_item.id]
                assert current_pos < next_pos, \
                    f"Higher priority item '{current_item.title}' should appear before '{next_item.title}'"
    
    def _validate_visual_formatting_quality(self, formatted_output):
        """Validate the quality of visual formatting"""
        # Check for color codes (indicating proper formatting)
        color_codes = ['\033[', '\x1b[']
        has_colors = any(code in formatted_output for code in color_codes)
        assert has_colors, "Output should contain color formatting"
        
        # Check for emoji status indicators
        status_emojis = ['⏰', '🎯']  # Actual emojis used by TerminalFormatter
        has_status_emojis = any(emoji in formatted_output for emoji in status_emojis)
        assert has_status_emojis, "Output should contain status emoji indicators"
        
        # Check for structural elements
        assert len(formatted_output.split('\n')) > 1, "Output should be multi-line"
        
        # Verify readability - should have reasonable line lengths and structure
        lines = formatted_output.split('\n')
        content_lines = [line for line in lines if line.strip()]
        assert len(content_lines) > 0, "Should have content lines"


if __name__ == "__main__":
    # Run with output capture disabled to see the formatted output
    pytest.main([__file__, "-v", "-s"])