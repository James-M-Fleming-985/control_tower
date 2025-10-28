#!/usr/bin/env python3
"""
Test script to verify that Action Plan formulas update when Gap Analysis changes.
This simulates what would happen in Excel when you edit primary evidence and recalculate.
"""
from openpyxl import load_workbook
from pathlib import Path

def test_formula_linkage():
    # Load the workbook with formulas
    wb_path = Path('cloned_repos/professional_excellence/projects/PROJECT-001 NADCAP COMPLIANCE/inputs/NADCAP 2026 Action Plan-281025.fixed_descriptions.xlsx')
    
    wb = load_workbook(filename=str(wb_path), data_only=False)
    ap = wb['Action Plan']
    ga = wb['Gap Analysis']
    
    print("=== TESTING FORMULA LINKAGE ===")
    print()
    
    # Find a test row - let's use the first few rows
    test_clause = ap.cell(row=2, column=3).value  # Get clause from Action Plan
    print(f"Test clause: {test_clause}")
    
    # Find the corresponding row in Gap Analysis
    ga_test_row = None
    for r in range(2, ga.max_row + 1):
        if ga.cell(row=r, column=6).value == test_clause:  # Column F is clause
            ga_test_row = r
            break
    
    if ga_test_row:
        print(f"Found matching Gap Analysis row: {ga_test_row}")
        
        # Get original values
        original_ref = ga.cell(row=ga_test_row, column=10).value  # Primary Evidence Doc Ref
        original_title = ga.cell(row=ga_test_row, column=11).value  # Primary Evidence Title
        
        print(f"Original Primary Evidence Doc Ref: {original_ref}")
        print(f"Original Primary Evidence Title: {original_title}")
        
        # Show the Action Plan formula (not evaluated)
        ap_formula = ap.cell(row=2, column=2).value
        print(f"Action Plan Formula: {ap_formula}")
        
        # Now simulate a change and show what would happen
        print()
        print("=== SIMULATING CHANGE ===")
        test_ref = "TEST-REF-001"
        test_title = "TEST DOCUMENT TITLE FOR DEMONSTRATION"
        
        ga.cell(row=ga_test_row, column=10).value = test_ref
        ga.cell(row=ga_test_row, column=11).value = test_title
        
        print(f"Changed Primary Evidence Doc Ref to: {test_ref}")
        print(f"Changed Primary Evidence Title to: {test_title}")
        
        # Save a test copy
        test_path = wb_path.parent / (wb_path.stem + '.test' + wb_path.suffix)
        wb.save(str(test_path))
        
        print(f"Saved test workbook to: {test_path}")
        print()
        print("=== VERIFICATION ===")
        print("When you open this test workbook in Excel:")
        print("1. The Action Plan row 2 Action Description should now contain:")
        print(f"   'Review document {test_ref} {test_title} to ensure it adequately satisfies the requirements of NADCAP clause {test_clause}'")
        print("2. Any future changes to Primary Evidence Doc Ref or Title in Gap Analysis will automatically update the Action Plan")
        
        # Restore original values and save the fixed version
        ga.cell(row=ga_test_row, column=10).value = original_ref
        ga.cell(row=ga_test_row, column=11).value = original_title
        wb.save(str(wb_path))
        
        print()
        print("Original values restored in the fixed_descriptions workbook.")
        
    else:
        print(f"Could not find Gap Analysis row for clause {test_clause}")

if __name__ == '__main__':
    test_formula_linkage()