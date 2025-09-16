#!/usr/bin/env python3
"""
Control Tower Phase 1 - Enhanced Make What Next

This is the enhanced version of the Control Tower "make what-next" command with
beautiful purple and green terminal output using the proper terminal formatter.

Usage:
    python make_what_next.py [options]
    make what-next [options]

Options:
    --repository=<name>     Filter to specific repository
    --repositories=<list>   Comma-separated list of repositories
    --json                  Output in JSON format
    --debug                 Enable debug mode
    --all                   Show all work items (not just due/overdue)

Author: Control Tower Development Team
Created: 2025-09-16
Status: Enhanced with proper terminal formatting
"""

import sys
import os
import json
import argparse
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Color scheme for beautiful terminal output
class ColorScheme:
    """Color scheme configuration for terminal output"""
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_PURPLE = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


class ItemStatus(Enum):
    """Work item status enumeration"""
    OVERDUE = "overdue"
    DUE_TODAY = "due_today"
    UPCOMING = "upcoming"


class RequirementLevel(Enum):
    """Requirement level enumeration"""
    FEATURE = "FR"
    LAYER = "LR"
    SYSTEM = "SY"
    PROJECT = "PR"


class Priority(Enum):
    """Priority enumeration"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    CRITICAL = "Critical"


class Priority(Enum):
    """Priority enumeration"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    CRITICAL = "Critical"


@dataclass
class WorkItem:
    """Work item model for terminal display"""
    id: str
    title: str
    requirement_level: RequirementLevel
    status: ItemStatus
    priority: Priority
    effort_estimate: str
    due_date: date
    progress: int
    file_path: str
    hierarchy_path: str
    
    def get_hierarchical_display(self) -> str:
        """Get the hierarchical context display"""
        return f"Feature Name: {self.title} → {self.hierarchy_path}"
    
    def get_work_specification(self) -> str:
        """Get the work specification (what layer to work on)"""
        if self.requirement_level == RequirementLevel.FEATURE:
            return f"Feature to implement: {self.title}"
        elif self.requirement_level == RequirementLevel.LAYER:
            return f"Layer to work on: {self.title}"
        else:
            return f"Work item: {self.title}"


class SimpleTerminalFormatter:
class WorkItem:
    """Work item model for terminal display"""
    id: str
    title: str
    requirement_level: RequirementLevel
    status: ItemStatus
    priority: Priority
    effort_estimate: str
    due_date: date
    progress: int
    file_path: str
    hierarchy_path: str
    
    def get_hierarchical_display(self) -> str:
        """Get the hierarchical context display"""
        return f"Feature Name: {self.title} → {self.hierarchy_path}"
    
    def get_work_specification(self) -> str:
        """Get the work specification (what layer to work on)"""
        if self.requirement_level == RequirementLevel.FEATURE:
            return f"Feature to implement: {self.title}"
        elif self.requirement_level == RequirementLevel.LAYER:
            return f"Layer to work on: {self.title}"
        else:
            return f"Work item: {self.title}"


class SimpleTerminalFormatter:
    """
    Simple terminal formatter with beautiful purple and green output
    """
    
    def __init__(self):
        self.colors = ColorScheme()
    
    def format_header(self, total_items: int, overdue_count: int) -> str:
        """Format header with statistics"""
        if total_items == 0:
            return f"{self.colors.BLUE}📊 No work items found{self.colors.RESET}"
        
        overdue_text = f"{self.colors.RED}{overdue_count} overdue{self.colors.RESET}" if overdue_count > 0 else "none overdue"
        return f"{self.colors.BLUE}📊 Found {total_items} work items ({overdue_text}){self.colors.RESET}"
    
    def format_work_items(self, work_items: List[WorkItem]) -> str:
        """Format multiple work items for display"""
        if not work_items:
            return f"{self.colors.GREEN}✅ No work items due today or overdue. Great job staying on top of your work!{self.colors.RESET}"
        
        formatted_items = []
        for item in work_items:
            formatted_items.append(self.format_work_item(item))
        
        return "\n\n".join(formatted_items)
    
    def format_work_item(self, item: WorkItem) -> str:
        """Format a single work item with beautiful colors"""
        # Build status line with emoji and color
        status_line = self._build_status_line(item)
        
        # Build hierarchical context line (bright green)
        hierarchy_line = f"   {self.colors.BRIGHT_GREEN}Feature Name: {item.title} → {item.hierarchy_path}{self.colors.RESET}"
        
        # Build work specification line (purple)
        work_spec = item.get_work_specification()
        work_spec_line = f"   {self.colors.PURPLE}{work_spec}{self.colors.RESET}"
        
        # Build metadata line (cyan)
        priority_value = item.priority.value
        metadata_line = f"   {self.colors.CYAN}Priority: {self.colors.RESET}{priority_value} {self.colors.DIM}|{self.colors.RESET} {self.colors.CYAN}Effort: {self.colors.RESET}{item.effort_estimate} {self.colors.DIM}|{self.colors.RESET} {self.colors.CYAN}Due: {self.colors.RESET}{item.due_date}"
        
        # Build action line (bright purple)
        action_line = f"   {self.colors.BRIGHT_PURPLE}Next: {self.colors.RESET}{self.colors.BOLD}make work TASK={item.id}{self.colors.RESET}"
        
        return "\n".join([
            status_line,
            hierarchy_line,
            work_spec_line,
            metadata_line,
            action_line
        ])
    
    def _build_status_line(self, item: WorkItem) -> str:
        """Build the main status line with emoji and color coding"""
        req_level = item.requirement_level.value
        
        if item.status == ItemStatus.OVERDUE:
            days_overdue = (date.today() - item.due_date).days
            status_text = f"⏰ OVERDUE: {item.id} ({item.title}) [{req_level}] ({days_overdue} days overdue)"
            return f"{self.colors.RED}{status_text}{self.colors.RESET}"
        elif item.status == ItemStatus.DUE_TODAY:
            status_text = f"🎯 DUE TODAY: {item.id} ({item.title}) [{req_level}]"
            return f"{self.colors.YELLOW}{status_text}{self.colors.RESET}"
        elif item.status == ItemStatus.UPCOMING:
            days_until_due = (item.due_date - date.today()).days
            if days_until_due > 0:
                status_text = f"📋 UPCOMING: {item.id} ({item.title}) [{req_level}] (due in {days_until_due} days)"
            else:
                status_text = f"📋 UPCOMING: {item.id} ({item.title}) [{req_level}]"
            return f"{self.colors.GREEN}{status_text}{self.colors.RESET}"
        else:
            status_text = f"📋 {item.id} ({item.title}) [{req_level}]"
            return f"{self.colors.WHITE}{status_text}{self.colors.RESET}"


def discover_requirements() -> List[Dict[str, Any]]:
    """
    Discover all requirements documents in the hierarchical structure
    
    Returns:
        List of requirement document information
    """
    requirements = []
    
    # Search in the projects directory
    projects_dir = Path("/workspaces/control_tower/projects")
    if projects_dir.exists():
        for req_file in projects_dir.rglob("*.md"):
            if req_file.stem.startswith(("FEATURE-", "LAYER-", "SYSTEM-", "PROJECT-")):
                try:
                    content = req_file.read_text()
                    req_info = parse_requirement_metadata(content, req_file)
                    if req_info:
                        requirements.append(req_info)
                except Exception as e:
                    if "--debug" in sys.argv:
                        print(f"Debug: Error reading {req_file}: {e}")
    
    return requirements


def parse_requirement_metadata(content: str, file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse requirement document metadata
    
    Args:
        content: File content
        file_path: Path to the file
        
    Returns:
        Requirement metadata or None if parsing fails
    """
    try:
        lines = content.split('\n')
        metadata = {'file_path': str(file_path)}
        
        # Extract title from first heading
        for line in lines[:10]:
            if line.startswith('# '):
                metadata['title'] = line[2:].strip()
                break
        
        # Parse key metadata fields
        for line in lines[:50]:
            if line.startswith('**Due Date**:'):
                date_str = line.split(':', 1)[1].strip()
                try:
                    metadata['due_date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    metadata['due_date'] = date.today()
            elif line.startswith('**Priority**:'):
                priority_str = line.split(':', 1)[1].strip()
                metadata['priority'] = priority_str
            elif line.startswith('**Progress**:'):
                progress_str = line.split(':', 1)[1].strip()
                if '%' in progress_str:
                    metadata['progress'] = int(progress_str.replace('%', '').strip())
                else:
                    metadata['progress'] = 0
            elif line.startswith('**Effort Estimate**:'):
                metadata['effort_estimate'] = line.split(':', 1)[1].strip()
        
        # Set defaults
        metadata.setdefault('title', file_path.stem)
        metadata.setdefault('due_date', date.today())
        metadata.setdefault('priority', 'Medium')
        metadata.setdefault('progress', 0)
        metadata.setdefault('effort_estimate', 'Unknown')
        
        # Determine requirement level and hierarchy
        filename = file_path.stem
        if filename.startswith('FEATURE-'):
            metadata['requirement_level'] = RequirementLevel.FEATURE
            metadata['hierarchy_path'] = get_feature_hierarchy(file_path)
        elif filename.startswith('LAYER-'):
            metadata['requirement_level'] = RequirementLevel.LAYER
            metadata['hierarchy_path'] = get_layer_hierarchy(file_path)
        elif filename.startswith('SYSTEM-'):
            metadata['requirement_level'] = RequirementLevel.SYSTEM
            metadata['hierarchy_path'] = get_system_hierarchy(file_path)
        elif filename.startswith('PROJECT-'):
            metadata['requirement_level'] = RequirementLevel.PROJECT
            metadata['hierarchy_path'] = get_project_hierarchy(file_path)
        else:
            return None
        
        return metadata
        
    except Exception as e:
        if "--debug" in sys.argv:
            print(f"Debug: Error parsing {file_path}: {e}")
        return None


def get_feature_hierarchy(file_path: Path) -> str:
    """Get hierarchy path for a feature"""
    parts = file_path.parts
    # Extract system and project from path
    project_name = "Unknown Project"
    system_name = "Unknown System"
    
    for part in parts:
        if part.startswith("PROJECT-"):
            project_name = part
        elif part.startswith("SYSTEM-"):
            system_name = part
    
    return f"{system_name} → {project_name} → Control Tower"


def get_layer_hierarchy(file_path: Path) -> str:
    """Get hierarchy path for a layer"""
    parts = file_path.parts
    feature_name = "Unknown Feature"
    
    for part in parts:
        if part.startswith("FEATURE-"):
            feature_name = part
    
    return f"{feature_name} → TDD Workflow Automation → Control Tower"


def get_system_hierarchy(file_path: Path) -> str:
    """Get hierarchy path for a system"""
    parts = file_path.parts
    project_name = "Unknown Project"
    
    for part in parts:
        if part.startswith("PROJECT-"):
            project_name = part
    
    return f"{project_name} → Control Tower"


def get_project_hierarchy(file_path: Path) -> str:
    """Get hierarchy path for a project"""
    return "Control Tower"


def determine_status(due_date: date, progress: int) -> ItemStatus:
    """
    Determine work item status based on due date and progress
    
    Args:
        due_date: Item due date
        progress: Progress percentage
        
    Returns:
        Item status
    """
    today = date.today()
    
    if progress >= 100:
        return ItemStatus.UPCOMING  # Completed items show as upcoming/green
    elif due_date < today:
        return ItemStatus.OVERDUE
    elif due_date == today:
        return ItemStatus.DUE_TODAY
    else:
        return ItemStatus.UPCOMING


def create_work_items(requirements: List[Dict[str, Any]], show_all: bool = False) -> List[WorkItem]:
    """
    Create work item objects from requirements
    
    Args:
        requirements: List of requirement metadata
        show_all: Whether to show all items or just due/overdue
        
    Returns:
        List of work items
    """
    work_items = []
    
    for req in requirements:
        try:
            # Create work item
            priority_str = req.get('priority', 'Medium')
            priority = Priority.MEDIUM  # Default
            for p in Priority:
                if p.value.lower() == priority_str.lower():
                    priority = p
                    break
            
            status = determine_status(req['due_date'], req['progress'])
            
            # Filter items unless show_all is True
            if not show_all and status == ItemStatus.UPCOMING and req['progress'] >= 100:
                continue
            
            work_item = WorkItem(
                id=Path(req['file_path']).stem,
                title=req['title'],
                requirement_level=req['requirement_level'],
                status=status,
                priority=priority,
                effort_estimate=req['effort_estimate'],
                due_date=req['due_date'],
                progress=req['progress'],
                file_path=req['file_path'],
                hierarchy_path=req['hierarchy_path']
            )
            
            work_items.append(work_item)
            
        except Exception as e:
            if "--debug" in sys.argv:
                print(f"Debug: Error creating work item from {req}: {e}")
    
    # Sort by due date, then by priority
    priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
    work_items.sort(key=lambda x: (x.due_date, priority_order.get(x.priority, 2)))
    
    return work_items


def main():
    """Main entry point for make what-next command"""
    parser = argparse.ArgumentParser(description="Control Tower Work Discovery")
    parser.add_argument("--repository", help="Filter to specific repository")
    parser.add_argument("--repositories", help="Comma-separated list of repositories")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--all", action="store_true", help="Show all work items")
    
    args = parser.parse_args()
    
    try:
        # Discover requirements
        requirements = discover_requirements()
        
        if args.debug:
            print(f"Debug: Found {len(requirements)} requirements documents")
        
        # Create work items
        work_items = create_work_items(requirements, args.all)
        
        if args.json:
            # JSON output for automation
            json_output = {
                "total_items": len(work_items),
                "overdue_count": len([item for item in work_items if item.status == ItemStatus.OVERDUE]),
                "work_items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "status": item.status.value,
                        "priority": item.priority.value,
                        "due_date": item.due_date.isoformat(),
                        "progress": item.progress,
                        "effort_estimate": item.effort_estimate
                    }
                    for item in work_items
                ]
            }
            print(json.dumps(json_output, indent=2))
        else:
            # Beautiful terminal output
            formatter = SimpleTerminalFormatter()
            overdue_count = len([item for item in work_items if item.status == ItemStatus.OVERDUE])
            
            # Print header with Control Tower branding
            print(f"{formatter.colors.BRIGHT_CYAN}🏗️  Control Tower - Work Discovery Engine{formatter.colors.RESET}")
            print("=" * 50)
            print()
            
            # Print statistics header
            print(formatter.format_header(len(work_items), overdue_count))
            print()
            
            # Print work items
            if work_items:
                formatted_output = formatter.format_work_items(work_items)
                print(formatted_output)
            else:
                print(f"{formatter.colors.GREEN}✅ No work items due today or overdue. Great job staying on top of your work!{formatter.colors.RESET}")
            
            print()
            print(f"{formatter.colors.DIM}💡 Use 'make work TASK=<id>' to start working on any item{formatter.colors.RESET}")
    
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()