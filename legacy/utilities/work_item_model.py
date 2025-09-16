#!/usr/bin/env python3
"""
Work Item Model - Data structures for work item representation

Based on TR-BL-001 specifications from Phase 1 Layer Requirements
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class ItemStatus(Enum):
    """Status of work items based on due dates"""
    DUE_TODAY = "due_today"
    OVERDUE = "overdue"
    UPCOMING = "upcoming"
    NOT_DUE = "not_due"  # For items that are not due yet


class ProjectType(Enum):
    """Type of project for hierarchical display"""
    APPLICATION = "application"
    STANDARD_DELIVERY = "standard_delivery"


class RequirementLevel(Enum):
    """Requirement level in the hierarchy"""
    NSR = "NSR"  # North Star Requirement
    PR = "PR"    # Project Requirement
    SR = "SR"    # System Requirement
    FR = "FR"    # Feature Requirement
    TR = "TR"    # Technical Requirement
    MR = "MR"    # Milestone Requirement


class Priority(Enum):
    """Priority levels for work items"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class WorkItem:
    """
    Work item model based on TR-BL-001 specifications
    
    Represents a single work item discovered from repositories
    with all necessary metadata for prioritization and display.
    """
    id: str
    title: str
    description: str
    due_date: Optional[date]  # Allow None for missing due dates
    priority: Priority
    effort_estimate: str
    requirement_level: RequirementLevel
    project_type: ProjectType
    repository: str
    system_name: str
    project_name: str
    layer_or_milestone: str
    hierarchy_path: str
    status: ItemStatus
    
    def is_overdue(self) -> bool:
        """Check if work item is overdue"""
        return self.status == ItemStatus.OVERDUE
    
    def is_due_today(self) -> bool:
        """Check if work item is due today"""
        return self.status == ItemStatus.DUE_TODAY
    
    def days_overdue(self) -> int:
        """Calculate how many days overdue (negative for future dates)"""
        if self.due_date is None:
            return 0  # No due date, not overdue
        today = date.today()
        delta = today - self.due_date
        return delta.days
    
    def get_hierarchical_display(self) -> str:
        """Get the appropriate hierarchical display based on project type"""
        if self.project_type == ProjectType.APPLICATION:
            return f"Feature Name: {self.hierarchy_path}"
        else:
            return f"Milestone Name: {self.hierarchy_path}"
    
    def get_work_specification(self) -> str:
        """Get the layer or milestone work specification"""
        if self.project_type == ProjectType.APPLICATION:
            return f"Layer to work on: {self.layer_or_milestone}"
        else:
            return f"Milestone to work on: {self.layer_or_milestone}"