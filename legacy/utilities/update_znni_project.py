#!/usr/bin/env python3
"""
Dynamic Project Update for ZnNi Line Development Plan-08.xml
This script can update any Level 4 project by finding it dynamically in the XML
"""

import argparse
import os
import shutil
import re
from datetime import datetime
from pathlib import Path

def create_backup(file_path):
    """Create a backup of the original file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def find_project_boundaries(xml_content, project_name):
    """
    Dynamically find the start and end boundaries for a Level 4 project in the XML
    
    Args:
        xml_content: Full XML content as string
        project_name: Name of the Level 4 project to find
    
    Returns:
        tuple: (start_line, end_line, project_uid) or (None, None, None) if not found
    """
    lines = xml_content.split('\n')
    
    # Look for the project task by name
    project_start = None
    project_uid = None
    
    print(f"🔍 Searching for project: '{project_name}'")
    
    for i, line in enumerate(lines):
        # Look for task with matching name
        if f'<Name>{project_name}</Name>' in line:
            print(f"✅ Found project name at line {i+1}")
            # Found the project name, now find its UID
            # Look backwards for the <Task> opening tag
            for j in range(i, max(0, i-20), -1):
                if '<Task>' in lines[j]:
                    # Found task start, now find UID
                    for k in range(j, min(len(lines), j+20)):
                        uid_match = re.search(r'<UID>(\d+)</UID>', lines[k])
                        if uid_match:
                            project_uid = uid_match.group(1)
                            project_start = j
                            print(f"✅ Found project '{project_name}' with UID {project_uid} at line {project_start+1}")
                            break
                    break
            break
    
    if not project_start or not project_uid:
        print(f"❌ Could not find project '{project_name}' in XML")
        return None, None, None
    
    # Now find the end of this project's scope
    # We need to find the matching </Task> for this project
    project_end = None
    task_depth = 0
    
    for i in range(project_start, len(lines)):
        line = lines[i]
        
        if '<Task>' in line:
            task_depth += 1
        elif '</Task>' in line:
            task_depth -= 1
            if task_depth == 0:
                project_end = i
                print(f"✅ Found project end boundary at line {project_end+1}")
                break
    
    if project_end is None:
        print(f"❌ Could not find end boundary for project '{project_name}'")
        return None, None, None
    
    return project_start, project_end, project_uid

def find_standalone_file_for_project(project_name):
    """
    Find the standalone XML file for a given project
    
    Args:
        project_name: Name of the Level 4 project
    
    Returns:
        str: Path to standalone file or None if not found
    """
    print(f"🔍 Looking for standalone file for project: '{project_name}'")
    
    # Convert project name to expected filename pattern
    # Example: "SF Investment Strategy OEE & OLE Application" -> "SF_Investment_Strategy_OEE_OLE_Application_Schedule.xml"
    
    # Remove special characters and convert to filename format
    filename_base = re.sub(r'[&\s]+', '_', project_name)
    filename_base = re.sub(r'_+', '_', filename_base)  # Remove multiple underscores
    filename_base = filename_base.strip('_')  # Remove leading/trailing underscores
    
    potential_files = [
        f"{filename_base}_Schedule.xml",
        f"{filename_base}.xml",
        f"{project_name.replace(' ', '_')}_Schedule.xml",
        f"{project_name.replace(' ', '_')}.xml"
    ]
    
    print(f"🔍 Searching for files: {potential_files}")
    
    for filename in potential_files:
        filepath = os.path.join('.', filename)
        if os.path.exists(filepath):
            print(f"✅ Found standalone file: {filepath}")
            return filepath
    
    # Also check if there's only one standalone file and use that
    xml_files = [f for f in os.listdir('.') if f.endswith('.xml') and f != 'ZnNi Line Development Plan-08.xml']
    if len(xml_files) == 1:
        print(f"✅ Found single standalone file: {xml_files[0]}")
        return xml_files[0]
    
    print(f"❌ Could not find standalone file for project '{project_name}'")
    print(f"   Available XML files: {xml_files}")
    return None

def extract_project_section_from_standalone(standalone_file):
    """Extract the project section from the standalone XML file"""
    print(f"📖 Reading standalone file: {standalone_file}")
    
    with open(standalone_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the Tasks section
    tasks_start = content.find('<Tasks>')
    tasks_end = content.find('</Tasks>')
    
    if tasks_start == -1 or tasks_end == -1:
        print("❌ Could not find <Tasks> section in standalone file")
        return None
    
    tasks_content = content[tasks_start + len('<Tasks>'):tasks_end].strip()
    print(f"✅ Extracted {len(tasks_content)} characters from standalone file")
    
    return tasks_content

def update_project_in_main_xml(main_xml_file, project_name, standalone_file):
    """Update the specified project in the main XML file with data from standalone file"""
    
    print(f"\n🚀 Starting update process...")
    print(f"📁 Main XML: {main_xml_file}")
    print(f"📁 Standalone: {standalone_file}")
    print(f"🎯 Project: {project_name}")
    
    # Create backup
    backup_path = create_backup(main_xml_file)
    
    # Read main XML file
    with open(main_xml_file, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Find project boundaries
    start_line, end_line, project_uid = find_project_boundaries(main_content, project_name)
    
    if start_line is None:
        print(f"❌ Could not find project '{project_name}' in main XML file")
        return False
    
    # Extract new project data from standalone file
    new_project_data = extract_project_section_from_standalone(standalone_file)
    
    if not new_project_data:
        print("❌ Could not extract project data from standalone file")
        return False
    
    # Split main content into lines for easier manipulation
    main_lines = main_content.split('\n')
    
    # Replace the project section
    print(f"🔄 Replacing lines {start_line+1} to {end_line+1} with new project data...")
    
    # Convert new project data back to lines
    new_project_lines = new_project_data.split('\n')
    
    # Build the updated content
    updated_lines = (
        main_lines[:start_line] +  # Content before project
        new_project_lines +        # New project data
        main_lines[end_line+1:]    # Content after project
    )
    
    # Write the updated content back
    updated_content = '\n'.join(updated_lines)
    
    with open(main_xml_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ Successfully updated '{project_name}' in {main_xml_file}")
    print(f"📊 Replaced {end_line - start_line + 1} lines with {len(new_project_lines)} lines")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Update ZnNi Project XML with standalone project data')
    parser.add_argument('--project', required=True,
                       help='Name of the Level 4 project to update')
    parser.add_argument('--file', required=False,
                       help='Specific standalone XML file to use (overrides auto-detection)')
    
    args = parser.parse_args()
    project_name = args.project
    
    print(f"\n🎯 DYNAMIC PROJECT UPDATE")
    print(f"🎯 Target Project: {project_name}")
    if args.file:
        print(f"📄 Specified File: {args.file}")
    print("="*60)
    
    # File paths
    main_xml_file = "ZnNi Line Development Plan-08.xml"
    
    # Verify main XML file exists
    if not os.path.exists(main_xml_file):
        print(f"❌ Main XML file not found: {main_xml_file}")
        return 1
    
    # Use specified file or find the appropriate standalone file
    if args.file:
        standalone_file = args.file
        print(f"🎯 Using specified standalone file: {standalone_file}")
    else:
        standalone_file = find_standalone_file_for_project(project_name)
        if not standalone_file:
            print(f"❌ Cannot proceed without standalone file for '{project_name}'")
            return 1
    
    # Verify standalone file exists
    if not os.path.exists(standalone_file):
        print(f"❌ Standalone file not found: {standalone_file}")
        return 1
    
    # Perform the update
    success = update_project_in_main_xml(main_xml_file, project_name, standalone_file)
    
    if success:
        print(f"\n🎉 PROJECT UPDATE COMPLETED SUCCESSFULLY!")
        print(f"✅ Project '{project_name}' has been updated in {main_xml_file}")
        return 0
    else:
        print(f"\n❌ PROJECT UPDATE FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())
