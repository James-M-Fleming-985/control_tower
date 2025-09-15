#!/usr/bin/env python3
"""
🎯 CLEAN OUTPUT FORMATTER
Provides clean, concise, noise-free terminal output following user journey

This module handles all terminal output formatting to ensure:
- Clean visual hierarchy with consistent formatting
- Color coding for status (green=good, yellow=warning, red=error)
- User journey-focused messaging
- Noise elimination and aggregation
"""

import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class OutputLevel(Enum):
    """Output verbosity levels"""
    QUIET = 0      # Only critical information
    NORMAL = 1     # Standard user journey information
    VERBOSE = 2    # Detailed information
    DEBUG = 3      # Full debug information

class StatusType(Enum):
    """Status types with associated colors"""
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    INFO = "ℹ️"
    PROGRESS = "🔄"
    DUE = "🎯"
    OVERDUE = "⏰"
    UPCOMING = "📅"
    WORK = "🔧"
    COMPLETE = "🎉"

class CleanOutput:
    """Clean terminal output formatter following user journey"""
    
    def __init__(self, level: OutputLevel = OutputLevel.NORMAL):
        self.level = level
        self.colors = {
            "green": "\033[92m",
            "yellow": "\033[93m", 
            "red": "\033[91m",
            "blue": "\033[94m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "bold": "\033[1m",
            "reset": "\033[0m"
        }
    
    def header(self, title: str, subtitle: str = None):
        """Print a clean section header"""
        if self.level == OutputLevel.QUIET:
            return
            
        print(f"\n{self.colors['bold']}{title}{self.colors['reset']}")
        if subtitle:
            print(f"{self.colors['cyan']}{subtitle}{self.colors['reset']}")
        print("=" * 50)
    
    def status(self, status_type: StatusType, message: str, details: str = None):
        """Print a status message with appropriate icon and color"""
        if self.level == OutputLevel.QUIET and status_type not in [StatusType.ERROR, StatusType.DUE, StatusType.OVERDUE]:
            return
        
        # Color mapping
        color_map = {
            StatusType.SUCCESS: "green",
            StatusType.WARNING: "yellow", 
            StatusType.ERROR: "red",
            StatusType.INFO: "blue",
            StatusType.PROGRESS: "cyan",
            StatusType.DUE: "yellow",
            StatusType.OVERDUE: "red",
            StatusType.UPCOMING: "blue",
            StatusType.WORK: "cyan",
            StatusType.COMPLETE: "green"
        }
        
        color = color_map.get(status_type, "white")
        colored_message = f"{self.colors[color]}{message}{self.colors['reset']}"
        
        print(f"{status_type.value} {colored_message}")
        
        if details and self.level.value >= OutputLevel.VERBOSE.value:
            print(f"   {details}")
    
    def work_item(self, item_id: str, title: str, due_date: str, priority: str, status: str):
        """Format a work item for display"""
        if self.level == OutputLevel.QUIET:
            return
            
        # Determine status type based on due date
        status_type = self._get_due_status(due_date)
        
        # Format the work item
        priority_color = {
            "Critical": "red",
            "High": "yellow", 
            "Medium": "blue",
            "Low": "white"
        }.get(priority, "white")
        
        priority_text = f"{self.colors[priority_color]}[{priority}]{self.colors['reset']}"
        title_text = f"{self.colors['bold']}{title}{self.colors['reset']}"
        
        print(f"{status_type.value} {priority_text} {item_id}: {title_text}")
        print(f"   Due: {due_date} | Status: {status}")
    
    def next_action(self, command: str, description: str = None):
        """Show the next action to take"""
        if self.level == OutputLevel.QUIET:
            return
            
        print(f"\n{self.colors['bold']}Next:{self.colors['reset']} {self.colors['cyan']}{command}{self.colors['reset']}")
        if description:
            print(f"   {description}")
    
    def progress_update(self, current: int, total: int, item: str = None):
        """Show progress update"""
        if self.level == OutputLevel.QUIET:
            return
            
        percentage = (current / total * 100) if total > 0 else 0
        bar_length = 20
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        progress_text = f"[{bar}] {percentage:.0f}% ({current}/{total})"
        if item:
            progress_text += f" - {item}"
            
        print(f"{StatusType.PROGRESS.value} {progress_text}")
    
    def section_break(self):
        """Add a visual section break"""
        if self.level != OutputLevel.QUIET:
            print()
    
    def summary(self, items: List[Dict[str, Any]]):
        """Print a clean summary of items"""
        if not items or self.level == OutputLevel.QUIET:
            return
            
        print(f"\n{self.colors['bold']}Summary:{self.colors['reset']}")
        
        # Group by status
        by_status = {}
        for item in items:
            status = item.get('status', 'Unknown')
            if status not in by_status:
                by_status[status] = 0
            by_status[status] += 1
        
        for status, count in by_status.items():
            print(f"  {status}: {count}")
    
    def error(self, message: str, details: str = None, exit_code: int = None):
        """Print error message and optionally exit"""
        print(f"{StatusType.ERROR.value} {self.colors['red']}{message}{self.colors['reset']}", file=sys.stderr)
        
        if details and self.level.value >= OutputLevel.NORMAL.value:
            print(f"   {details}", file=sys.stderr)
        
        if exit_code is not None:
            sys.exit(exit_code)
    
    def debug(self, message: str, data: Any = None):
        """Print debug information (only in debug mode)"""
        if self.level.value >= OutputLevel.DEBUG.value:
            print(f"DEBUG: {message}")
            if data:
                print(f"       {data}")
    
    def _get_due_status(self, due_date_str: str) -> StatusType:
        """Determine status type based on due date"""
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            today = datetime.now()
            days_diff = (due_date - today).days
            
            if days_diff < 0:
                return StatusType.OVERDUE
            elif days_diff == 0:
                return StatusType.DUE
            elif days_diff <= 7:
                return StatusType.UPCOMING
            else:
                return StatusType.INFO
        except (ValueError, TypeError):
            return StatusType.INFO
    
    def user_journey_message(self, journey_step: str, message: str):
        """Print user journey specific messages"""
        journey_icons = {
            "discovery": "🔍",
            "work_setup": "🛠️",
            "development": "💻", 
            "testing": "🧪",
            "validation": "✅",
            "deployment": "🚀",
            "completion": "🎉"
        }
        
        icon = journey_icons.get(journey_step, "ℹ️")
        print(f"{icon} {message}")

# Global output instance
output = CleanOutput()

def set_output_level(level: OutputLevel):
    """Set global output level"""
    global output
    output.level = level

def get_clean_output() -> CleanOutput:
    """Get the global clean output instance"""
    return output