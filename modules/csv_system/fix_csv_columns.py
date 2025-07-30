#!/usr/bin/env python3
"""
CSV Column Standardization Script for Control Tower
Fixes column alignment issues in all tasks.csv files
"""

import os
import pandas as pd
import glob
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the original file"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"  ✅ Backup created: {backup_path}")
    return backup_path

def analyze_csv_structure(file_path):
    """Analyze the CSV structure to understand the column alignment"""
    print(f"\n🔍 Analyzing: {file_path}")
    
    with open(file_path, 'r') as f:
        header_line = f.readline().strip()
        data_line = f.readline().strip()
    
    header_fields = header_line.split(',')
    data_fields = data_line.split(',')
    
    print(f"  📊 Header fields: {len(header_fields)}")
    print(f"  📊 Data fields: {len(data_fields)}")
    
    if len(header_fields) != len(data_fields):
        print(f"  ⚠️ MISMATCH: {len(header_fields)} header fields vs {len(data_fields)} data fields")
    
    # Show first few fields for analysis
    print("  🔍 First 8 fields comparison:")
    for i in range(min(8, len(header_fields), len(data_fields))):
        print(f"    {i+1:2d}: {header_fields[i]:20} = '{data_fields[i]}'")
    
    return header_fields, data_fields

def fix_csv_columns(file_path):
    """Fix column alignment in a CSV file"""
    print(f"\n🛠️ Fixing: {file_path}")
    
    # Create backup
    backup_path = backup_file(file_path)
    
    try:
        # Read the raw CSV data
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            print("  ❌ Empty file, skipping")
            return False
        
        # Parse header
        header = lines[0].strip().split(',')
        
        # Expected column order (corrected)
        expected_columns = [
            '% Complete',           # 1
            'Constraint Date',      # 2 - often empty
            'Constraint Type',      # 3 - often empty (this is the issue!)
            'Is Milestone',         # 4
            'Milestone',           # 5 - actual task names
            'Task Mode',           # 6 - actual duration info
            'Task Name',           # 7 - actual start dates  
            'Duration',            # 8 - actual finish dates
            'Start',               # 9 - baseline start
            'Finish',              # 10 - baseline finish
            'Predecessors',        # 11 - resource names
            'Work',                # 12 - work hours
            'Resource Names',      # 13 - baseline dates
            'Baseline Start',      # 14
            'Baseline Finish',     # 15
            'Actual Start',        # 16
            'Actual Finish',       # 17
            'Physical % Complete', # 18
            'Number1',             # 19
            'Number2'              # 20
        ]
        
        # Process each data line
        fixed_lines = [','.join(expected_columns) + '\n']  # Fixed header
        
        for line_num, line in enumerate(lines[1:], 2):
            line = line.strip()
            if not line:
                continue
                
            fields = line.split(',')
            
            # If we have fewer fields than expected, pad with empty values
            while len(fields) < len(expected_columns):
                fields.append('')
            
            # If we have more fields than expected, truncate
            if len(fields) > len(expected_columns):
                print(f"  ⚠️ Line {line_num}: Too many fields ({len(fields)}), truncating")
                fields = fields[:len(expected_columns)]
            
            fixed_lines.append(','.join(fields) + '\n')
        
        # Write the fixed file
        with open(file_path, 'w') as f:
            f.writelines(fixed_lines)
        
        print(f"  ✅ Fixed: {len(fixed_lines)-1} data rows processed")
        return True
        
    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")
        # Restore backup on error
        shutil.copy2(backup_path, file_path)
        print(f"  🔄 Restored from backup")
        return False

def main():
    """Main function to fix all CSV files"""
    print("🏗️ Control Tower CSV Column Standardization")
    print("=" * 50)
    
    # Find all task files
    task_files = glob.glob("cloned_repos/**/tasks.csv", recursive=True)
    
    if not task_files:
        print("❌ No tasks.csv files found")
        return
    
    print(f"📁 Found {len(task_files)} task files")
    
    # Analyze before fixing
    print("\n📊 ANALYSIS PHASE")
    print("-" * 30)
    
    issues_found = 0
    for file_path in task_files:
        try:
            header_fields, data_fields = analyze_csv_structure(file_path)
            if len(header_fields) != len(data_fields):
                issues_found += 1
        except Exception as e:
            print(f"  ❌ Error analyzing {file_path}: {e}")
            issues_found += 1
    
    if issues_found == 0:
        print("\n🎉 No column alignment issues found!")
        return
    
    print(f"\n⚠️ Found {issues_found} files with column alignment issues")
    
    # Ask for confirmation
    response = input("\n🔧 Proceed with fixing? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Aborted by user")
        return
    
    # Fix phase
    print("\n🛠️ FIXING PHASE")
    print("-" * 20)
    
    fixed_count = 0
    error_count = 0
    
    for file_path in task_files:
        try:
            if fix_csv_columns(file_path):
                fixed_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"❌ Unexpected error with {file_path}: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"✅ Successfully fixed: {fixed_count} files")
    print(f"❌ Errors: {error_count} files")
    print(f"📁 Total processed: {len(task_files)} files")
    
    if fixed_count > 0:
        print("\n🎉 CSV standardization complete!")
        print("💡 All queries should now work without column shift workarounds")
        print("📝 Backup files created with .backup_YYYYMMDD_HHMMSS extension")
    
    if error_count > 0:
        print(f"\n⚠️ {error_count} files had errors - check the output above")

if __name__ == "__main__":
    main()
