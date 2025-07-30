#!/usr/bin/env python3

import sys
import os
sys.path.append('/workspaces/control_tower')

from datetime import datetime
from modules.ms_project.ms_project_integration import MSProjectIntegration

def debug_august_milestones():
    """Debug August milestone detection using the actual integration module"""
    
    print("Debugging August milestones using MSProjectIntegration...")
    
    # Initialize the integration module
    xml_path = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    ms_project = MSProjectIntegration(xml_path)
    
    if not ms_project.read_project_file():
        print("Failed to load project")
        return
    
    # Calculate August 2025 date range (matching the logic in contract_project_manager.py)
    today = datetime(2025, 7, 30)  # Current date
    
    # Next month range - August (with proper time handling)
    next_month_start = today.replace(month=today.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    # August has 31 days
    next_month_end = today.replace(month=today.month + 1, day=31, hour=23, minute=59, second=59)
    
    print(f"August range: {next_month_start.strftime('%Y-%m-%d %H:%M:%S')} to {next_month_end.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Let's also check the first milestone's actual date/time
    all_milestones = ms_project.get_milestones()
    aug_1_milestones = [m for m in all_milestones if m['date'] and m['date'].month == 8 and m['date'].day == 1 and m['date'].year == 2025]
    
    if aug_1_milestones:
        print(f"\nMilestones on August 1st:")
        for milestone in aug_1_milestones:
            print(f"  - {milestone['name']} - {milestone['date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Is date >= start? {milestone['date'] >= next_month_start}")
            print(f"    Is date <= end? {milestone['date'] <= next_month_end}")
    
    # Get August milestones using the actual method
    august_milestones = ms_project.get_milestones(next_month_start, next_month_end)
    
    print(f"\nTotal August milestones found: {len(august_milestones)}")
    
    if august_milestones:
        print("\nAugust milestones:")
        for milestone in august_milestones:
            date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
            resource_str = milestone['resource'] if milestone['resource'] else 'No resource assigned'
            print(f"  - {milestone['name']}")
            print(f"    Due: {date_str}")
            print(f"    Resource: '{resource_str}'")
            print(f"    Status: {milestone['status']}")
            print()
    
    # Also check all milestones to see total count
    all_milestones = ms_project.get_milestones()
    print(f"\nTotal milestones in project: {len(all_milestones)}")
    
    # Let's also see if there are any milestones on August 31st specifically
    august_31 = datetime(2025, 8, 31, 23, 59, 59)
    august_31_milestones = [m for m in all_milestones if m['date'] and m['date'].month == 8 and m['date'].day == 31 and m['date'].year == 2025]
    
    if august_31_milestones:
        print(f"\nMilestones specifically on August 31st:")
        for milestone in august_31_milestones:
            print(f"  - {milestone['name']} - {milestone['date'].strftime('%d/%m/%Y')}")
    else:
        print("\nNo milestones found on August 31st")

if __name__ == "__main__":
    debug_august_milestones()
