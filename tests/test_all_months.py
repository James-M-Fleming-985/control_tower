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

def test_all_months():
    """Test milestone detection for all months in 2025"""
    
    print("=== COMPREHENSIVE MILESTONE COUNT TEST ===")
    print("Testing milestone detection for all months in 2025...")
    
    # Initialize the integration module
    xml_path = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    ms_project = MSProjectIntegration(xml_path)
    
    if not ms_project.read_project_file():
        print("Failed to load project")
        return
    
    # Get all milestones once
    all_milestones = ms_project.get_milestones()
    print(f"Total milestones in project: {len(all_milestones)}")
    print()
    
    # Test each month in 2025
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    total_found = 0
    
    for month_num in range(1, 13):
        month_name = months[month_num - 1]
        start_date, end_date = get_month_date_range(2025, month_num)
        
        # Get milestones using our integration
        month_milestones = ms_project.get_milestones(start_date, end_date)
        milestone_count = len(month_milestones)
        total_found += milestone_count
        
        print(f"📅 {month_name} 2025: {milestone_count} milestones")
        print(f"   Range: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if milestone_count > 0:
            print("   Milestones:")
            for milestone in sorted(month_milestones, key=lambda x: x['date'] or datetime.min):
                date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                print(f"     • {milestone['name']} - {date_str}")
        print()
    
    print(f"=== SUMMARY ===")
    print(f"Total milestones found across all months: {total_found}")
    print(f"Total milestones in project: {len(all_milestones)}")
    
    # Check for any milestones that might be outside 2025
    milestones_2025 = [m for m in all_milestones if m['date'] and m['date'].year == 2025]
    milestones_other_years = [m for m in all_milestones if m['date'] and m['date'].year != 2025]
    
    print(f"Milestones in 2025: {len(milestones_2025)}")
    print(f"Milestones in other years: {len(milestones_other_years)}")
    
    if milestones_other_years:
        print("\nMilestones in other years:")
        for milestone in milestones_other_years[:10]:  # Show first 10
            date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
            print(f"  • {milestone['name']} - {date_str}")
        if len(milestones_other_years) > 10:
            print(f"  ... and {len(milestones_other_years) - 10} more")
    
    # Verification
    if total_found == len(milestones_2025):
        print("\n✅ SUCCESS: All 2025 milestones accounted for!")
    else:
        print(f"\n❌ MISMATCH: Found {total_found} in monthly queries but {len(milestones_2025)} total in 2025")
        
        # Find missing milestones
        found_names = set()
        for month_num in range(1, 13):
            start_date, end_date = get_month_date_range(2025, month_num)
            month_milestones = ms_project.get_milestones(start_date, end_date)
            for m in month_milestones:
                found_names.add(m['name'])
        
        all_2025_names = {m['name'] for m in milestones_2025}
        missing = all_2025_names - found_names
        
        if missing:
            print(f"\nMissing milestones:")
            for name in missing:
                milestone = next(m for m in milestones_2025 if m['name'] == name)
                date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                print(f"  • {name} - {date_str}")

def test_specific_months():
    """Test the specific months we know have issues"""
    
    print("\n=== SPECIFIC MONTH VALIDATION ===")
    
    # Initialize the integration module
    xml_path = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    ms_project = MSProjectIntegration(xml_path)
    
    if not ms_project.read_project_file():
        print("Failed to load project")
        return
    
    # Test July 2025 (should be 7 milestones)
    july_start, july_end = get_month_date_range(2025, 7)
    july_milestones = ms_project.get_milestones(july_start, july_end)
    print(f"July 2025: {len(july_milestones)} milestones (expected: 7)")
    
    # Test August 2025 (should be 12 milestones)
    august_start, august_end = get_month_date_range(2025, 8)
    august_milestones = ms_project.get_milestones(august_start, august_end)
    print(f"August 2025: {len(august_milestones)} milestones (expected: 12)")
    
    # Test edge cases
    print("\n=== EDGE CASE TESTS ===")
    
    # February 2025 (non-leap year)
    feb_start, feb_end = get_month_date_range(2025, 2)
    feb_milestones = ms_project.get_milestones(feb_start, feb_end)
    print(f"February 2025: {len(feb_milestones)} milestones")
    print(f"   Range: {feb_start.strftime('%Y-%m-%d')} to {feb_end.strftime('%Y-%m-%d')} (28 days)")
    
    # December 2025 (year transition)
    dec_start, dec_end = get_month_date_range(2025, 12)
    dec_milestones = ms_project.get_milestones(dec_start, dec_end)
    print(f"December 2025: {len(dec_milestones)} milestones")
    print(f"   Range: {dec_start.strftime('%Y-%m-%d')} to {dec_end.strftime('%Y-%m-%d')} (31 days)")

if __name__ == "__main__":
    test_specific_months()
    print()
    test_all_months()
