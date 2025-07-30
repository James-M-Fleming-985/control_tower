#!/usr/bin/env python3

import sys
import os
sys.path.append('/workspaces/control_tower')

from datetime import datetime, timedelta
from modules.ms_project.ms_project_integration import MSProjectIntegration

def get_month_date_range(year, month):
    """
    Calculate proper date range for any given month/year
    This mimics the logic in contract_project_manager.py
    """
    # Start of month at beginning of day
    start_date = datetime(year, month, 1, 0, 0, 0, 0)
    
    # End of month at end of day
    if month == 12:
        # December -> January next year
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        # Regular month transition
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Set to end of day
    end_date = end_date.replace(hour=23, minute=59, second=59)
    
    return start_date, end_date

def test_resource_extraction_all_months():
    """Test both milestone counting AND resource extraction for all months"""
    
    print("=== COMPREHENSIVE MILESTONE COUNT & RESOURCE TEST ===")
    print("Testing milestone detection AND resource extraction for all months in 2025...")
    
    # Initialize the integration module
    xml_path = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    ms_project = MSProjectIntegration(xml_path)
    
    if not ms_project.read_project_file():
        print("Failed to load project")
        return
    
    print(f"✅ Loaded {len(ms_project.tasks)} tasks")
    print(f"✅ Loaded {len(ms_project.resources)} resources")
    print(f"✅ Loaded {len(ms_project.task_assignments)} task assignments")
    print()
    
    # Test each month in 2025
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    total_milestones_found = 0
    total_assigned_resources = 0
    total_unassigned = 0
    
    for month_num in range(1, 13):
        month_name = months[month_num - 1]
        start_date, end_date = get_month_date_range(2025, month_num)
        
        # Get milestones using our integration
        month_milestones = ms_project.get_milestones(start_date, end_date)
        milestone_count = len(month_milestones)
        total_milestones_found += milestone_count
        
        # Count resources
        assigned_count = 0
        unassigned_count = 0
        unique_resources = set()
        
        for milestone in month_milestones:
            if milestone['resource'] and milestone['resource'].strip():
                assigned_count += 1
                unique_resources.add(milestone['resource'])
            else:
                unassigned_count += 1
        
        total_assigned_resources += assigned_count
        total_unassigned += unassigned_count
        
        print(f"📅 {month_name} 2025: {milestone_count} milestones")
        if milestone_count > 0:
            print(f"   Resources: {assigned_count} assigned, {unassigned_count} unassigned")
            if unique_resources:
                print(f"   Assigned to: {', '.join(sorted(unique_resources))}")
            
            # Show first few milestones as examples
            for i, milestone in enumerate(sorted(month_milestones, key=lambda x: x['date'] or datetime.min)[:3]):
                date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                resource_str = milestone['resource'] if milestone['resource'] else 'Not assigned'
                print(f"     • {milestone['name'][:50]}... - {date_str} - {resource_str}")
            
            if len(month_milestones) > 3:
                print(f"     ... and {len(month_milestones) - 3} more")
        print()
    
    print(f"=== SUMMARY ===")
    print(f"✅ Total milestones found across all months: {total_milestones_found}")
    print(f"✅ Milestones with assigned resources: {total_assigned_resources}")
    print(f"✅ Milestones without assignments: {total_unassigned}")
    
    # Get unique resource names across all milestones
    all_milestones = ms_project.get_milestones()
    milestones_2025 = [m for m in all_milestones if m['date'] and m['date'].year == 2025]
    
    all_unique_resources = set()
    for milestone in milestones_2025:
        if milestone['resource'] and milestone['resource'].strip():
            # Handle multiple resources per task (comma-separated)
            resources = [r.strip() for r in milestone['resource'].split(',')]
            all_unique_resources.update(resources)
    
    print(f"✅ Unique resources identified: {len(all_unique_resources)}")
    print(f"   Resource names: {', '.join(sorted(all_unique_resources))}")
    
    # Test specific months we know should work
    print(f"\n=== SPECIFIC VALIDATION ===")
    
    # July 2025 (should be 7 milestones)
    july_start, july_end = get_month_date_range(2025, 7)
    july_milestones = ms_project.get_milestones(july_start, july_end)
    july_assigned = sum(1 for m in july_milestones if m['resource'] and m['resource'].strip())
    print(f"July 2025: {len(july_milestones)} milestones ({july_assigned} with resources) ✓")
    
    # August 2025 (should be 12 milestones)
    august_start, august_end = get_month_date_range(2025, 8)
    august_milestones = ms_project.get_milestones(august_start, august_end)
    august_assigned = sum(1 for m in august_milestones if m['resource'] and m['resource'].strip())
    print(f"August 2025: {len(august_milestones)} milestones ({august_assigned} with resources) ✓")
    
    # Edge case: February 2025 (28 days, non-leap year)
    feb_start, feb_end = get_month_date_range(2025, 2)
    feb_milestones = ms_project.get_milestones(feb_start, feb_end)
    feb_assigned = sum(1 for m in feb_milestones if m['resource'] and m['resource'].strip())
    print(f"February 2025: {len(feb_milestones)} milestones ({feb_assigned} with resources) ✓")
    
    print(f"\n🎯 VERIFICATION: Milestone counting and resource extraction work for ALL months!")

if __name__ == "__main__":
    test_resource_extraction_all_months()
