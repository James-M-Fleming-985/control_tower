#!/usr/bin/env python3
"""
Terminal Formatter - UI Layer Implementation

REFACTOR PHASE: Polished implementation with better structure and error handling
Based on TR-UI-001 specifications from Phase 1 Layer Requirements
"""

from typing import List, Optional
from dataclasses import dataclass
from datetime import date
from src.business_logic.work_item_model import WorkItem, ItemStatus


@dataclass
class ColorScheme:
    """Color scheme configuration for terminal output"""
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class TerminalFormatter:
    """
    Terminal output formatter for work items
    
    Provides clean, formatted terminal output with color coding
    and hierarchical context display. Follows clean architecture
    principles with separation of concerns.
    """
    
    def __init__(self, color_scheme: Optional[ColorScheme] = None):
        """Initialize formatter with optional color scheme"""
        self.colors = color_scheme or ColorScheme()
    
    def format_work_items(self, work_items: List[WorkItem]) -> str:
        """
        Format multiple work items for terminal display
        
        Args:
            work_items: List of work items to format
            
        Returns:
            Formatted string ready for terminal output
        """
        if not work_items:
            return self._format_empty_message()
        
        formatted_items = []
        for item in work_items:
            try:
                formatted_items.append(self.format_work_item(item))
            except Exception as e:
                # Graceful degradation for problematic items
                formatted_items.append(f"Error formatting item {getattr(item, 'id', 'unknown')}: {str(e)}")
        
        return "\n\n".join(formatted_items)
    
    def format_header(self, total_items: int, overdue_count: int) -> str:
        """
        Format header with statistics
        
        Args:
            total_items: Total number of work items
            overdue_count: Number of overdue items
            
        Returns:
            Formatted header string
        """
        if total_items == 0:
            return f"{self.colors.BLUE}📊 No work items found{self.colors.RESET}"
        
        overdue_text = f"{self.colors.RED}{overdue_count} overdue{self.colors.RESET}" if overdue_count > 0 else "none overdue"
        return f"{self.colors.BLUE}📊 Found {total_items} work items ({overdue_text}){self.colors.RESET}"
    
    def format_work_item(self, item: WorkItem) -> str:
        """
        Format a single work item for display
        
        Args:
            item: Work item to format
            
        Returns:
            Formatted work item string
        """
        if not item:
            return "Error: Invalid work item"
        
        try:
            # Build status line with appropriate emoji and formatting
            status_line = self._build_status_line(item)
            
            # Build hierarchical context line
            hierarchy_line = self._build_hierarchy_line(item)
            
            # Build work specification line
            work_spec_line = self._build_work_specification_line(item)
            
            # Build metadata line
            metadata_line = self._build_metadata_line(item)
            
            # Build action line
            action_line = self._build_action_line(item)
            
            return "\n".join([
                status_line,
                hierarchy_line,
                work_spec_line,
                metadata_line,
                action_line
            ])
            
        except Exception as e:
            return f"Error formatting work item {item.id}: {str(e)}"
    
    def apply_color_coding(self, text: str, status: ItemStatus) -> str:
        """
        Apply ANSI color codes based on item status
        
        Args:
            text: Text to colorize
            status: Item status determining color
            
        Returns:
            Colorized text with ANSI codes
        """
        color_map = {
            ItemStatus.OVERDUE: self.colors.RED,
            ItemStatus.DUE_TODAY: self.colors.YELLOW,
            ItemStatus.UPCOMING: self.colors.GREEN
        }
        
        color = color_map.get(status, self.colors.WHITE)
        return f"{color}{text}{self.colors.RESET}"
    
    def _build_status_line(self, item: WorkItem) -> str:
        """Build the main status line with emoji and color coding"""
        if item.status == ItemStatus.OVERDUE:
            days_overdue = (date.today() - item.due_date).days if item.due_date else 0
            req_level = item.requirement_level.value if hasattr(item.requirement_level, 'value') else item.requirement_level
            status_text = f"⏰ OVERDUE: {item.id} ({item.title}) [{req_level}] ({days_overdue} days overdue)"
        elif item.status == ItemStatus.DUE_TODAY:
            req_level = item.requirement_level.value if hasattr(item.requirement_level, 'value') else item.requirement_level
            status_text = f"🎯 DUE TODAY: {item.id} ({item.title}) [{req_level}]"
        
        return self.apply_color_coding(status_text, item.status)
    
    def _build_hierarchy_line(self, item: WorkItem) -> str:
        """Build the hierarchical context line"""
        hierarchy_display = item.get_hierarchical_display()
        return f"   {hierarchy_display}"
    
    def _build_work_specification_line(self, item: WorkItem) -> str:
        """Build the work specification line (layer or milestone)"""
        work_spec = item.get_work_specification()
        return f"   {work_spec}"
    
    def _build_metadata_line(self, item: WorkItem) -> str:
        """Build the metadata line with priority, effort, and due date"""
        priority_value = item.priority.value if hasattr(item.priority, 'value') else item.priority
        return f"   Priority: {priority_value} | Effort: {item.effort_estimate} | Due: {item.due_date}"
    
    def _build_action_line(self, item: WorkItem) -> str:
        """Build the direct action command line"""
        return f"   Next: make work TASK={item.id}"
    
    def _format_empty_message(self) -> str:
        """Format message for when no work items are found"""
        return f"{self.colors.GREEN}✅ No work items due today or overdue. Great job staying on top of your work!{self.colors.RESET}"