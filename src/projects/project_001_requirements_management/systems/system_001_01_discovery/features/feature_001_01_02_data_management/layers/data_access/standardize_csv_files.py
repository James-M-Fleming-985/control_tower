#!/usr/bin/env python3
"""
CSV Standardization Script for Control Tower
Fixes column alignment issues and ensures data integrity
"""

import os
import pandas as pd
import glob
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the original file"""
    backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"  Backed up: {backup_path}")
    return backup_path

def standardize_csv_file(file_path):
    """Standardize a single CSV file"""
    print(f"\nProcessing: {file_path}")
    
    try:
        # Create backup
        backup_file(file_path)
        
        # Read the file line by line to handle inconsistent columns
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            print("  ❌ Empty file, skipping")
            return False
        
        # Parse header
        header = lines[0].strip()
        expected_columns = [
            '% Complete', 'Constraint Date', 'Constraint Type', 'Is Milestone', 
            'Milestone', 'Task Mode', 'Task Name', 'Duration', 'Start', 'Finish', 
            'Predecessors', 'Work', 'Resource Names', 'Baseline Start', 
            'Baseline Finish', 'Actual Start', 'Actual Finish', 
            'Physical % Complete', 'Number1', 'Number2'
        ]
        
        print(f"  Header columns: {len(header.split(','))}")
        
        # Process data lines
        standardized_lines = [header + '\n']
        fixed_count = 0
        
        for i, line in enumerate(lines[1:], 1):
            line = line.strip()
            if not line:
                continue
                
            fields = line.split(',')
            print(f"  Row {i}: {len(fields)} fields", end='')
            
            # If missing fields, add empty constraint date field
            if len(fields) == 19:  # Missing Constraint Date
                # Insert empty constraint date at position 1
                fields.insert(1, '')
                fixed_count += 1
                print(" → Fixed (added empty Constraint Date)")
            elif len(fields) == 20:
                print(" → OK")
            else:
                print(f" → Warning: Unexpected field count ({len(fields)})")
            
            # Ensure exactly 20 fields
            while len(fields) < 20:
                fields.append('')
            
            # Truncate if too many fields
            fields = fields[:20]
            
            standardized_lines.append(','.join(fields) + '\n')
        
        # Write standardized file
        with open(file_path, 'w') as f:
            f.writelines(standardized_lines)
        
        print(f"  ✅ Standardized: {fixed_count} rows fixed")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def validate_csv_file(file_path):
    """Validate that a CSV file has consistent structure"""
    try:
        df = pd.read_csv(file_path)
        expected_columns = [
            '% Complete', 'Constraint Date', 'Constraint Type', 'Is Milestone', 
            'Milestone', 'Task Mode', 'Task Name', 'Duration', 'Start', 'Finish', 
            'Predecessors', 'Work', 'Resource Names', 'Baseline Start', 
            'Baseline Finish', 'Actual Start', 'Actual Finish', 
            'Physical % Complete', 'Number1', 'Number2'
        ]
        
        if list(df.columns) == expected_columns:
            print(f"  ✅ Valid: {len(df)} rows, {len(df.columns)} columns")
            return True
        else:
            print(f"  ❌ Invalid: Column mismatch")
            print(f"      Expected: {len(expected_columns)} columns")
            print(f"      Found: {len(df.columns)} columns")
            return False
            
    except Exception as e:
        print(f"  ❌ Validation error: {e}")
        return False

def main():
    """Main standardization process"""
    print("🏗️ Control Tower CSV Standardization")
    print("=" * 50)
    
    # Find all CSV files
    csv_files = glob.glob("cloned_repos/**/tasks.csv", recursive=True)
    
    if not csv_files:
        print("No tasks.csv files found in cloned_repos/")
        return
    
    print(f"Found {len(csv_files)} CSV files to standardize")
    
    # Process each file
    success_count = 0
    for csv_file in csv_files:
        if standardize_csv_file(csv_file):
            success_count += 1
    
    print(f"\n" + "=" * 50)
    print(f"📊 STANDARDIZATION COMPLETE")
    print(f"✅ Successfully processed: {success_count}/{len(csv_files)} files")
    
    # Validate all files
    print(f"\n🔍 VALIDATION PHASE")
    print("-" * 30)
    valid_count = 0
    for csv_file in csv_files:
        print(f"\nValidating: {csv_file}")
        if validate_csv_file(csv_file):
            valid_count += 1
    
    print(f"\n" + "=" * 50)
    print(f"📋 VALIDATION RESULTS")
    print(f"✅ Valid files: {valid_count}/{len(csv_files)}")
    
    if valid_count == len(csv_files):
        print("🎉 All CSV files are now standardized!")
        print("\nNext steps:")
        print("1. Remove column shift workarounds from query code")
        print("2. Update load_all_tasks() to use standard CSV reading")
        print("3. Test all queries with standardized data")
    else:
        print("⚠️ Some files still need attention")

if __name__ == "__main__":
    main()
