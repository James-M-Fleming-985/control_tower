"""
Data models for Repository Scanner - TR-DA-001

Defines the data structures used by the Repository Scanner to represent
raw requirements and extracted metadata.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from src.business_logic.work_item_model import RequirementLevel, Priority


@dataclass
class RequirementMetadata:
    """
    Metadata extracted from requirement files
    
    Contains structured information parsed from markdown files including
    due dates, priorities, requirement levels, and other essential data.
    """
    id: str
    title: str
    due_date: Optional[date] = None
    priority: Priority = Priority.MEDIUM
    requirement_level: RequirementLevel = RequirementLevel.FR
    status: str = "Not Started"
    effort_estimate: str = "Unknown"
    description: str = ""


@dataclass 
class RawRequirement:
    """
    Raw requirement data from file system scanning
    
    Represents a discovered requirement file with its content and extracted metadata.
    This is the output of the Repository Scanner before conversion to WorkItem objects.
    """
    file_path: str
    content: str
    metadata: RequirementMetadata