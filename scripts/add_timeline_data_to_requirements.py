#!/usr/bin/env python3
"""
Add timeline data to existing requirements files.

This script updates the 1,340 existing requirements files with timeline management fields:
- Duration (based on level and complexity)
- Due Date (realistic project timelines)
- Start Date (based on dependencies)
- Priority (based on project status and level)
- Effort Estimate (person-days based on scope)
- Dependencies (based on hierarchy)
- Progress (current completion status)
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

def get_timeline_estimates_by_level(level, project_type):
    """Get realistic timeline estimates based on requirement level and project type."""
    
    estimates = {
        "north_star": {
            "duration_days": 365,
            "effort_days": 250,
            "priority": "Critical"
        },
        "project": {
            "duration_days": 120,
            "effort_days": 80,
            "priority": "High"
        },
        "system": {
            "duration_days": 30,
            "effort_days": 20,
            "priority": "High"
        },
        "workpackage": {
            "duration_days": 30,
            "effort_days": 20,
            "priority": "High"
        },
        "feature": {
            "duration_days": 10,
            "effort_days": 7,
            "priority": "Medium"
        },
        "milestone": {
            "duration_days": 10,
            "effort_days": 7,
            "priority": "Medium"
        },
        "layer": {
            "duration_days": 3,
            "effort_days": 2,
            "priority": "Medium"
        },
        "task": {
            "duration_days": 3,
            "effort_days": 2,
            "priority": "Medium"
        }
    }
    
    return estimates.get(level, estimates["task"])

def determine_requirement_level(file_path):
    """Determine the requirement level from file path and content."""
    
    path_parts = file_path.parts
    
    # Check if it's a north star requirement
    if "requirements.md" in path_parts[-1] and len(path_parts) == 4:
        return "north_star"
    
    # Check by directory structure depth
    if len(path_parts) == 5:  # repo/project/requirements.md
        return "project"
    elif len(path_parts) == 6:  # repo/project/system/requirements.md
        return "system" if "systems" in str(file_path) else "workpackage"
    elif len(path_parts) == 7:  # repo/project/system/feature/requirements.md
        return "feature" if "features" in str(file_path) else "milestone"
    elif len(path_parts) == 8:  # repo/project/system/feature/layer/requirements.md
        return "layer" if "layers" in str(file_path) else "task"
    
    return "task"  # Default to task level

def get_project_type(file_path):
    """Determine if project is Application or Delivery type."""
    
    # Look for indicators in path
    path_str = str(file_path)
    
    if any(keyword in path_str.lower() for keyword in ["systems", "features", "layers"]):
        return "Application"
    elif any(keyword in path_str.lower() for keyword in ["workpackages", "milestones", "tasks"]):
        return "Delivery"
    
    # Check by project name patterns
    if any(project in path_str for project in ["financial_optimizer", "opti_royale", "Causal_affect"]):
        return "Application"
    elif any(project in path_str for project in ["home_improvements", "Safran SF Optimization"]):
        return "Delivery"
    
    return "Application"  # Default

def calculate_project_dates(level, base_date=None):
    """Calculate realistic start and due dates based on project level."""
    
    if base_date is None:
        base_date = datetime.now()
    
    level_offsets = {
        "north_star": {"start_offset": 0, "duration": 365},
        "project": {"start_offset": 7, "duration": 120},
        "system": {"start_offset": 14, "duration": 30},
        "workpackage": {"start_offset": 14, "duration": 30},
        "feature": {"start_offset": 21, "duration": 10},
        "milestone": {"start_offset": 21, "duration": 10},
        "layer": {"start_offset": 28, "duration": 3},
        "task": {"start_offset": 28, "duration": 3}
    }
    
    offset_info = level_offsets.get(level, level_offsets["task"])
    start_date = base_date + timedelta(days=offset_info["start_offset"])
    due_date = start_date + timedelta(days=offset_info["duration"])
    
    return start_date, due_date

def get_dependencies_by_level(level, file_path):
    """Generate realistic dependencies based on hierarchy level."""
    
    dependencies = []
    
    if level == "project":
        dependencies = ["NS-001"]  # Depends on North Star
    elif level == "system":
        dependencies = ["PROJ-APP-001"]  # Depends on Project
    elif level == "workpackage":
        dependencies = ["PROJ-DEL-001"]  # Depends on Project
    elif level == "feature":
        dependencies = ["SYS-APP-001"]  # Depends on System
    elif level == "milestone":
        dependencies = ["WP-DEL-001"]  # Depends on Workpackage
    elif level == "layer":
        dependencies = ["FEA-APP-001"]  # Depends on Feature
    elif level == "task":
        dependencies = ["MIL-DEL-001"]  # Depends on Milestone
    
    return dependencies

def estimate_progress(level, project_status):
    """Estimate current progress based on level and project maturity."""
    
    # Base progress by project maturity
    project_progress = {
        "financial_optimizer": 75,  # Mature project
        "opti_royale": 85,          # Very mature project
        "Causal_affect": 25,        # Early stage
        "home_improvements": 60,    # In progress
        "Safran SF Optimization": 90  # Near completion
    }
    
    # Adjust by level (higher levels tend to be more complete)
    level_adjustments = {
        "north_star": 0,
        "project": -5,
        "system": -10,
        "workpackage": -10,
        "feature": -15,
        "milestone": -15,
        "layer": -20,
        "task": -25
    }
    
    base_progress = 50  # Default
    for project, progress in project_progress.items():
        if project in str(project_status):
            base_progress = progress
            break
    
    adjustment = level_adjustments.get(level, -20)
    final_progress = max(0, min(100, base_progress + adjustment))
    
    return final_progress

def add_timeline_section(content, level, file_path):
    """Add timeline management section to requirements content."""
    
    estimates = get_timeline_estimates_by_level(level, get_project_type(file_path))
    start_date, due_date = calculate_project_dates(level)
    dependencies = get_dependencies_by_level(level, file_path)
    progress = estimate_progress(level, str(file_path))
    
    timeline_section = f"""
## ⏱️ TIMELINE MANAGEMENT

**Duration**: {estimates['duration_days']} days  
**Due Date**: {due_date.strftime('%Y-%m-%d')}  
**Start Date**: {start_date.strftime('%Y-%m-%d')}  
**Priority**: {estimates['priority']}  
**Effort Estimate**: {estimates['effort_days']} person-days  
**Dependencies**: {', '.join(dependencies) if dependencies else 'None'}  
**Progress**: {progress}% - {get_progress_description(progress)}
"""
    
    # Insert after header section but before main content
    lines = content.split('\n')
    
    # Find where to insert (after the header metadata)
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('**Status**:') or line.startswith('**Last Updated**:'):
            insert_index = i + 1
            break
    
    # Insert timeline section
    lines.insert(insert_index, timeline_section)
    
    return '\n'.join(lines)

def get_progress_description(progress):
    """Get descriptive status based on progress percentage."""
    
    if progress == 0:
        return "Not started"
    elif progress < 25:
        return "Initial planning"
    elif progress < 50:
        return "Early development"
    elif progress < 75:
        return "Active development"
    elif progress < 90:
        return "Near completion"
    elif progress < 100:
        return "Final testing"
    else:
        return "Complete"

def find_requirements_files():
    """Find all requirements files in cloned_repos."""
    
    cloned_repos_path = Path("/workspaces/control_tower/cloned_repos")
    requirements_files = []
    
    # Look for various requirements file patterns
    patterns = [
        "*_requirements.md",
        "requirements.md"
    ]
    
    for pattern in patterns:
        for req_file in cloned_repos_path.rglob(pattern):
            requirements_files.append(req_file)
    
    return requirements_files

def update_requirements_file(file_path):
    """Update a single requirements file with timeline data."""
    
    try:
        # Read current content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if timeline section already exists
        if "⏱️ TIMELINE MANAGEMENT" in content:
            print(f"⚠️  Timeline already exists in {file_path}")
            return False
        
        # Determine level and add timeline section
        level = determine_requirement_level(file_path)
        updated_content = add_timeline_section(content, level, file_path)
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Updated {file_path} (Level: {level})")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all requirements files with timeline data."""
    
    print("🔄 ADDING TIMELINE DATA TO REQUIREMENTS FILES")
    print("=" * 60)
    
    # Find all requirements files
    requirements_files = find_requirements_files()
    print(f"📋 Found {len(requirements_files)} requirements files")
    print()
    
    # Update each file
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for file_path in requirements_files:
        result = update_requirements_file(file_path)
        if result is True:
            updated_count += 1
        elif result is False:
            skipped_count += 1
        else:
            error_count += 1
    
    print()
    print("📊 TIMELINE UPDATE SUMMARY")
    print("=" * 30)
    print(f"✅ Updated: {updated_count} files")
    print(f"⚠️  Skipped: {skipped_count} files (already had timeline)")
    print(f"❌ Errors: {error_count} files")
    print(f"📋 Total: {len(requirements_files)} files")
    print()
    
    if updated_count > 0:
        print("🎯 NEXT STEPS:")
        print("1. Review timeline estimates for accuracy")
        print("2. Adjust dates based on actual project schedules") 
        print("3. Update dependencies based on real relationships")
        print("4. Run 'make what-next' to see timeline-driven priorities")
    
    return updated_count

if __name__ == "__main__":
    main()