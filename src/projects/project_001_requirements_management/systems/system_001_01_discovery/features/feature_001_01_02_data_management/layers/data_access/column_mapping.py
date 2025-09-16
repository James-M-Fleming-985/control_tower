#!/usr/bin/env python3
"""
Control Tower Column Mapping Configuration
Handles the empty Constraint Date/Type columns that cause apparent column shifts
"""

# ACTUAL CSV Column Layout (what's in the files)
# Note: Constraint Date (col 2) and Constraint Type (col 3) are consistently empty
ACTUAL_COLUMNS = [
    '% Complete',           # 0  - Percentage complete
    'Constraint Date',      # 1  - EMPTY (causes confusion)
    'Constraint Type',      # 2  - EMPTY (causes confusion) 
    'Is Milestone',         # 3  - Yes/No milestone flag
    'Milestone',            # 4  - Task scheduling mode (Auto/Manual)
    'Task Mode',            # 5  - ACTUAL TASK NAME (project/task description)
    'Task Name',            # 6  - ACTUAL DURATION (days/hours)
    'Duration',             # 7  - ACTUAL START DATE
    'Start',                # 8  - ACTUAL FINISH DATE
    'Finish',               # 9  - Predecessor info
    'Predecessors',         # 10 - Work hours/effort
    'Work',                 # 11 - ACTUAL RESOURCE NAMES (who's assigned)
    'Resource Names',       # 12 - Baseline start date
    'Baseline Start',       # 13 - Baseline finish date
    'Baseline Finish',      # 14 - Actual start date
    'Actual Start',         # 15 - Actual finish date
    'Actual Finish',        # 16 - Physical completion percentage
    'Physical % Complete',  # 17 - Custom number field 1
    'Number1',              # 18 - Custom number field 2
    'Number2'               # 19 - Custom number field 3
]

# LOGICAL Data Mapping (what the data actually represents)
# Use these indices for accessing the correct data
class TaskColumns:
    """Column indices for accessing task data correctly"""
    
    # Basic task info
    PERCENT_COMPLETE = 0      # '% Complete' - "25%", "100%"
    IS_MILESTONE = 3          # 'Is Milestone' - "Yes", "No" 
    SCHEDULING_MODE = 4       # 'Milestone' - "Auto Scheduled", "Manually Scheduled"
    
    # Core task data (shifted due to empty constraint columns)
    TASK_NAME = 5             # 'Task Mode' - Contains actual project/task names
    DURATION = 6              # 'Task Name' - Contains actual duration ("60 days", "120 days")
    START_DATE = 7            # 'Duration' - Contains actual start dates
    FINISH_DATE = 8           # 'Start' - Contains actual finish dates
    
    # Relationships and effort
    PREDECESSORS = 9          # 'Finish' - Task dependencies 
    WORK_HOURS = 10           # 'Predecessors' - Work effort
    RESOURCE_NAMES = 11       # 'Work' - Who's assigned to task
    
    # Baseline planning
    BASELINE_START = 12       # 'Resource Names' - Original planned start
    BASELINE_FINISH = 13      # 'Baseline Start' - Original planned finish
    
    # Actual execution
    ACTUAL_START = 14         # 'Baseline Finish' - When work actually started
    ACTUAL_FINISH = 15        # 'Actual Start' - When work actually finished
    
    # Additional metrics
    PHYSICAL_COMPLETE = 16    # 'Actual Finish' - Physical completion %
    NUMBER1 = 17              # 'Physical % Complete' - Custom field
    NUMBER2 = 18              # 'Number1' - Custom field

def get_task_name(row):
    """Extract the actual task name from the row"""
    return row[TaskColumns.TASK_NAME] if len(row) > TaskColumns.TASK_NAME else ""

def get_duration(row):
    """Extract the actual duration from the row"""
    return row[TaskColumns.DURATION] if len(row) > TaskColumns.DURATION else ""

def get_start_date(row):
    """Extract the actual start date from the row"""
    return row[TaskColumns.START_DATE] if len(row) > TaskColumns.START_DATE else ""

def get_finish_date(row):
    """Extract the actual finish date from the row"""
    return row[TaskColumns.FINISH_DATE] if len(row) > TaskColumns.FINISH_DATE else ""

def get_resource_names(row):
    """Extract the actual resource names from the row"""
    return row[TaskColumns.RESOURCE_NAMES] if len(row) > TaskColumns.RESOURCE_NAMES else ""

def get_percent_complete(row):
    """Extract the completion percentage from the row"""
    return row[TaskColumns.PERCENT_COMPLETE] if len(row) > TaskColumns.PERCENT_COMPLETE else ""

def is_milestone(row):
    """Check if the task is a milestone"""
    if len(row) <= TaskColumns.IS_MILESTONE:
        return False
    
    milestone_flag = row[TaskColumns.IS_MILESTONE].strip().lower()
    duration = get_duration(row).strip().lower()
    
    # Check both milestone flag and zero duration
    return (milestone_flag == 'yes' or 
            duration in ['0 days', '0 hrs', '0 hours', '0'])

def get_project_name_from_path(file_path):
    """Extract project name from file path"""
    import os
    path_parts = file_path.split('/')
    
    # Handle different project structures
    if 'contract_projects' in path_parts:
        # For contract projects: use the last folder name
        return path_parts[-2] if len(path_parts) > 1 else 'Unknown Project'
    else:
        # For other projects: use the project folder name
        for i, part in enumerate(path_parts):
            if part == 'projects' and i + 1 < len(path_parts):
                return path_parts[i + 2] if i + 2 < len(path_parts) else path_parts[i + 1]
        return path_parts[-2] if len(path_parts) > 1 else 'Unknown Project'

# Export the mapping for use in other modules
__all__ = ['TaskColumns', 'get_task_name', 'get_duration', 'get_start_date', 
           'get_finish_date', 'get_resource_names', 'get_percent_complete', 
           'is_milestone', 'get_project_name_from_path', 'ACTUAL_COLUMNS']
