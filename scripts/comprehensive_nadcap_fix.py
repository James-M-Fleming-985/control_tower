#!/usr/bin/env python3
"""
Comprehensive fix for NADCAP Action Plan Excel workbook:
1. Fix Team Summary formulas to reference correct columns
2. Update due dates based on project start date (tomorrow)
3. Fix Status Summary formulas to use column G instead of E
4. Add data validation dropdown for Status column G
"""
from openpyxl import load_workbook
from datetime import datetime, timedelta
from pathlib import Path

try:
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:
    print("DataValidation not available - skipping dropdown creation")
    DataValidation = None

def main():
    # Load the workbook
    wb_path = Path('cloned_repos/professional_excellence/projects/PROJECT-001 NADCAP COMPLIANCE/inputs/NADCAP 2026 Action Plan-281025.fixed_descriptions.xlsx')
    wb = load_workbook(filename=str(wb_path), data_only=False)
    
    print("=== COMPREHENSIVE NADCAP WORKBOOK FIX ===")
    
    # 1. Fix Team Summary formulas
    print("\n1. Fixing Team Summary formulas...")
    fix_team_summary_formulas(wb)
    
    # 2. Update due dates
    print("2. Updating due dates based on project start tomorrow...")
    update_due_dates(wb)
    
    # 3. Fix Status Summary formulas
    print("3. Fixing Status Summary formulas to use column G...")
    fix_status_summary_formulas(wb)
    
    # 4. Add status dropdown validation
    print("4. Adding status dropdown validation to column G...")
    add_status_dropdown(wb)
    
    # Save the updated workbook
    output_path = wb_path.parent / (wb_path.stem + '.comprehensive_fix' + wb_path.suffix)
    wb.save(str(output_path))
    
    print(f"\n✅ All fixes applied successfully!")
    print(f"📁 Saved to: {output_path}")
    
    return output_path

def fix_team_summary_formulas(wb):
    """Fix Team Summary sheet formulas to reference correct columns and status."""
    ts = wb['Team Summary']
    
    # The Team Summary currently references:
    # - Column D for owners (correct - Documentation Reference seems wrong)
    # - Column E for status (should be G)
    # Let's fix to reference column E for Owner and G for Status
    
    team_members = ["Josh Kenny", "Matthew White", "Dean Wilkins", "Mike Warriner"]
    
    for i, member in enumerate(team_members, start=4):  # Starting from row 4
        # Fix owner column reference (should be E, not D)
        ts.cell(row=i, column=2).value = f"=COUNTIF('Action Plan'!E:E,\"{member}\")"
        
        # Fix priority counts (using correct owner column E)
        ts.cell(row=i, column=3).value = f"=COUNTIFS('Action Plan'!E:E,\"{member}\",'Action Plan'!H:H,\"High\")"
        ts.cell(row=i, column=4).value = f"=COUNTIFS('Action Plan'!E:E,\"{member}\",'Action Plan'!H:H,\"Medium\")"
        ts.cell(row=i, column=5).value = f"=COUNTIFS('Action Plan'!E:E,\"{member}\",'Action Plan'!H:H,\"Low\")"
        
        # Fix status percentage (using column G for status)
        ts.cell(row=i, column=6).value = f"=IF(B{i}>0,COUNTIFS('Action Plan'!E:E,\"{member}\",'Action Plan'!G:G,\"Approved\")/B{i}*100,0)"
    
    print("   ✓ Team Summary formulas updated")

def update_due_dates(wb):
    """Update due dates in Action Plan based on project starting tomorrow."""
    ap = wb['Action Plan']
    
    # Project starts tomorrow (Oct 29, 2025)
    project_start = datetime(2025, 10, 29)
    
    # Update due dates in column F
    row_count = 0
    for r in range(2, ap.max_row + 1):
        if ap.cell(row=r, column=1).value:  # If there's an Action ID
            # Stagger due dates: 2-4 weeks from project start
            weeks_offset = 2 + ((r - 2) % 3)  # 2, 3, 4, 2, 3, 4, etc.
            due_date = project_start + timedelta(weeks=weeks_offset)
            
            ap.cell(row=r, column=6).value = due_date.strftime('%Y-%m-%d')
            row_count += 1
    
    print(f"   ✓ Updated {row_count} due dates starting from {project_start.strftime('%Y-%m-%d')}")

def fix_status_summary_formulas(wb):
    """Fix Status Summary sheet to reference column G instead of E."""
    ss = wb['Status Summary']
    
    status_options = ["Unstarted", "With PE", "In Review", "Approved", "Released", "Blocked"]
    
    for i, status in enumerate(status_options, start=4):  # Starting from row 4
        # Count formula (column B) - change from E:E to G:G
        ss.cell(row=i, column=2).value = f"=COUNTIF('Action Plan'!G:G,\"{status}\")"
        
        # Percentage formula (column C) - change from E:E to G:G
        ss.cell(row=i, column=3).value = f"=IF(COUNT('Action Plan'!G:G)>0,B{i}/COUNT('Action Plan'!G:G)*100,0)"
    
    print("   ✓ Status Summary formulas updated to use column G")

def add_status_dropdown(wb):
    """Add data validation dropdown for status options in column G."""
    ap = wb['Action Plan']
    
    # Define the status options
    status_options = ["Unstarted", "With PE", "In Review", "Approved", "Released", "Blocked"]
    status_list = ",".join(status_options)
    
    # Create data validation
    dv = DataValidation(type="list", formula1=f'"{status_list}"', showDropDown=True)
    dv.error = 'Please select a valid status'
    dv.errorTitle = 'Invalid Status'
    dv.prompt = 'Please select a status from the dropdown'
    dv.promptTitle = 'Action Status'
    
    # Apply to the entire Status column G (assuming max 500 rows)
    range_string = f"G2:G{min(ap.max_row + 50, 500)}"
    dv.add(range_string)
    ap.add_data_validation(dv)
    
    # Set default status for existing rows
    row_count = 0
    for r in range(2, ap.max_row + 1):
        if ap.cell(row=r, column=1).value:  # If there's an Action ID
            current_status = ap.cell(row=r, column=7).value
            if not current_status or current_status not in status_options:
                ap.cell(row=r, column=7).value = "Unstarted"
                row_count += 1
    
    print(f"   ✓ Added status dropdown validation to column G")
    print(f"   ✓ Set default status 'Unstarted' for {row_count} rows")

if __name__ == '__main__':
    main()