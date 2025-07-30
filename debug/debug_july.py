#!/usr/bin/env python3
"""
Debug script to find all July milestones in the XML
"""

import sys
sys.path.append('/workspaces/control_tower')

from modules.ms_project.ms_project_integration import MSProjectIntegration
from datetime import datetime

def debug_july_milestones():
    # Load the project
    xml_path = '/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml'
    ms_project = MSProjectIntegration(xml_path)
    
    success = ms_project.read_project_file()
    if not success:
        print("Failed to load project file")
        return
    
    print(f"Total tasks loaded: {len(ms_project.tasks)}")
    
    # Find all July 2025 milestones
    july_milestones = []
    
    for task in ms_project.tasks:
        if task['is_milestone']:
            finish_date = task['finish']
            if finish_date and '2025-07' in finish_date:
                july_milestones.append(task)
                print(f"July Milestone: {task['name']}")
                print(f"  Finish: {finish_date}")
                print(f"  ID: {task['id']}")
                print(f"  Duration: {task['duration']}")
                print(f"  Percent Complete: {task['percent_complete']}")
                print()
    
    print(f"\nTotal July milestones found: {len(july_milestones)}")
    
    # Also check for any tasks that might be milestones but not flagged
    print("\n--- Checking for potential missed milestones ---")
    for task in ms_project.tasks:
        finish_date = task['finish']
        if finish_date and '2025-07' in finish_date:
            # Check if duration is zero or very small
            duration = task['duration']
            if not task['is_milestone'] and duration and ('PT0H0M0S' in duration or '0 days' in duration):
                print(f"Potential missed milestone: {task['name']}")
                print(f"  Finish: {finish_date}")
                print(f"  Duration: {duration}")
                print(f"  Milestone flag: {task['is_milestone']}")
                print()

if __name__ == "__main__":
    debug_july_milestones()
