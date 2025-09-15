"""
Data models for Repository Scanner - TR-DA-001

Defines the data structures used by the Repository Scanner to represent
raw requirements and extracted metadata.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

# For legacy compatibility - import RequirementLevel and Priority 
try:
    from src.business_logic.work_item_model import RequirementLevel, Priority
except ImportError:
    # Define basic enums if business logic not available
    from enum import Enum
    
    class RequirementLevel(Enum):
        COMPONENT = 1
        MODULE = 2
        SERVICE = 3
        SYSTEM = 4
        LAYER = 5
        FR = 6  # Functional Requirement
        BR = 7  # Business Requirement
        AC = 8  # Acceptance Criteria
        PR = 9  # Performance Requirement
        QR = 10  # Quality Requirement
    
    class Priority(Enum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3
        CRITICAL = 4


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