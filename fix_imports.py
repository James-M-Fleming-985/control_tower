#!/usr/bin/env python3
"""
Fix Import Paths Script
=======================

Updates all test files to use the correct project-specific src directory
instead of the root-level src directory.
"""

import os
from pathlib import Path

# Define the base test directory
test_base_dir = Path("/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/DATA ACCESS LAYER/tests")

# Old import pattern to replace
old_import_pattern = """import sys
sys.path.append('/workspaces/control_tower/src')"""

# New import pattern
new_import_pattern = """import sys
from pathlib import Path
project_src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(project_src_path))"""

def update_imports_in_file(file_path):
    """Update imports in a single test file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the import pattern
        if old_import_pattern in content:
            updated_content = content.replace(old_import_pattern, new_import_pattern)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"⏭️  Skipped: {file_path} (no matching pattern)")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all test files"""
    updated_count = 0
    total_files = 0
    
    # Find all Python test files
    for root, dirs, files in os.walk(test_base_dir):
        for file in files:
            if file.endswith('.py') and file.startswith('test_'):
                file_path = Path(root) / file
                total_files += 1
                
                if update_imports_in_file(file_path):
                    updated_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   Total test files: {total_files}")
    print(f"   Updated files: {updated_count}")
    print(f"   Skipped files: {total_files - updated_count}")

if __name__ == "__main__":
    main()