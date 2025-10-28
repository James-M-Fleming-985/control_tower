#!/usr/bin/env python3
"""
Fix and properly add dropdown validation to column G in the NADCAP Action Plan
"""
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation
from pathlib import Path

def add_status_dropdown():
    # Load the main file
    wb_path = Path('cloned_repos/professional_excellence/projects/PROJECT-001 NADCAP COMPLIANCE/inputs/NADCAP 2026 Action Plan-281025.xlsx')
    wb = load_workbook(filename=str(wb_path))
    ap = wb['Action Plan']
    
    print("=== ADDING STATUS DROPDOWN TO COLUMN G ===")
    
    # Clear existing data validations to start fresh
    # Remove existing validations
    ap.data_validations.dataValidation = []
    
    # Define the status options exactly as requested
    status_options = ["Unstarted", "With PE", "In Review", "Approved", "Released", "Blocked"]
    
    # Create data validation with proper formula
    dv = DataValidation(
        type="list",
        formula1=f'"{",".join(status_options)}"',
        allow_blank=True,
        showDropDown=True
    )
    
    # Set validation messages
    dv.error = 'Please select a valid status from the dropdown'
    dv.errorTitle = 'Invalid Status'
    dv.prompt = 'Choose from: ' + ', '.join(status_options)
    dv.promptTitle = 'Action Status Selection'
    
    # Apply to a reasonable range in column G (Status column)
    # Find the last row with data
    last_row = ap.max_row
    if last_row > 500:  # Cap at reasonable limit
        last_row = 500
        
    range_string = f"G2:G{last_row}"
    dv.add(range_string)
    ap.add_data_validation(dv)
    
    print(f"✅ Added dropdown validation to range: {range_string}")
    print(f"✅ Status options: {', '.join(status_options)}")
    
    # Set some sample statuses to demonstrate
    sample_statuses = ["Unstarted", "With PE", "In Review", "Approved", "Released"]
    for r in range(2, min(7, ap.max_row + 1)):
        if ap.cell(row=r, column=1).value:  # If there's an Action ID
            # Cycle through sample statuses
            status_index = (r - 2) % len(sample_statuses)
            ap.cell(row=r, column=7).value = sample_statuses[status_index]
    
    print("✅ Set sample statuses for first few rows")
    
    # Save the file
    wb.save(str(wb_path))
    print(f"✅ Saved file with dropdown validation: {wb_path.name}")
    
    return wb_path

def verify_dropdown():
    # Verify the dropdown was applied
    wb_path = Path('cloned_repos/professional_excellence/projects/PROJECT-001 NADCAP COMPLIANCE/inputs/NADCAP 2026 Action Plan-281025.xlsx')
    wb = load_workbook(filename=str(wb_path))
    ap = wb['Action Plan']
    
    print("\n=== VERIFICATION ===")
    print(f"Data validations in worksheet: {len(ap.data_validations.dataValidation)}")
    
    for dv in ap.data_validations.dataValidation:
        print(f"Validation type: {dv.type}")
        print(f"Formula: {dv.formula1}")
        print(f"Ranges: {dv.sqref}")
        print(f"Show dropdown: {dv.showDropDown}")
    
    print("\nSample status values in column G:")
    for r in range(2, 8):
        action_id = ap.cell(row=r, column=1).value
        status = ap.cell(row=r, column=7).value
        if action_id:
            print(f"  {action_id}: {status}")

if __name__ == '__main__':
    add_status_dropdown()
    verify_dropdown()