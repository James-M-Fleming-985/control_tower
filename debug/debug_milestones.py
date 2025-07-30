#!/usr/bin/env python3
"""
Debug script to investigate milestone detection issues
"""

import sys
sys.path.append('/workspaces/control_tower')

from modules.ms_project.ms_project_integration import MSProjectIntegration
from datetime import datetime

def debug_milestones():
    # Load the project
    xml_path = '/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml'
    ms_project = MSProjectIntegration(xml_path)
    
    # The XML is automatically loaded in __init__, so just call read_project_file()
    success = ms_project.read_project_file()
    if not success:
        print("Failed to load project file")
        return
    
    print(f"Total tasks loaded: {len(ms_project.tasks)}")
    
    # Check milestones
    milestone_count = 0
    august_milestones = []
    
    for task in ms_project.tasks:
        if task['is_milestone']:
            milestone_count += 1
            finish_date = task['finish']
            print(f"Milestone: {task['name'][:50]}... | Finish: {finish_date}")
            
            # Check if it's August
            if finish_date and '2025-08' in finish_date:
                august_milestones.append(task)
                print(f"  *** AUGUST MILESTONE: {task['name']}")
    
    print(f"\nTotal milestones found: {milestone_count}")
    print(f"August milestones found: {len(august_milestones)}")
    
    # Test the actual milestone query method
    print("\n--- Testing get_milestones method ---")
    start_aug = datetime(2025, 8, 1)
    end_aug = datetime(2025, 8, 31, 23, 59, 59)
    
    august_from_method = ms_project.get_milestones(start_aug, end_aug)
    print(f"get_milestones() returned: {len(august_from_method)} milestones")
    
    for milestone in august_from_method:
        print(f"  {milestone['name']} - {milestone['date']}")

if __name__ == "__main__":
    debug_milestones()
