#!/usr/bin/env python3
"""
Auto-Launch MS Project with Standalone XML (Option 1)
=====================================================

CHOSEN APPROACH: Direct standalone XML import into MS Project

This script implements Option 1 from CONTROL_TOWER_WORKFLOWS.md:
1. Locates standalone XML files (no integration with main XML)
2. Launches MS Project with standalone file directly
3. Handles cross-platform compatibility
4. Skips complex XML parsing and integration

Usage:
    python auto_launch_msproject.py                                    # Auto-detect available project
    python auto_launch_msproject.py --project "SF Investment"          # Specific project
    python auto_launch_msproject.py --description "What changed"       # With update description
    python auto_launch_msproject.py --list-projects                    # List all Level 4 projects
    
Decision: August 5, 2025 - Option 1 chosen for simplicity and reliability
"""

import os
import sys
import subprocess
import platform
import argparse
from datetime import datetime
from pathlib import Path

def find_matching_csv_file(project_name):
    """Find CSV file that matches the project name"""
    data_dir = "/workspaces/control_tower/data"
    
    if not os.path.exists(data_dir):
        return None
    
    # Look for CSV files that contain project name keywords
    project_keywords = project_name.lower().split()
    
    for file in os.listdir(data_dir):
        if file.endswith('.csv'):
            file_lower = file.lower()
            # Check if file contains any of the project keywords
            if any(keyword in file_lower for keyword in project_keywords):
                csv_path = os.path.join(data_dir, file)
                print(f"📋 Found matching CSV: {file}")
                return csv_path
    
    return None

def generate_xml_from_csv(csv_file, project_name, description=None):
    """Generate XML from any CSV file for any project"""
    print(f"\n📊 GENERATING {project_name.upper()} XML FROM CSV...")
    print("-" * 50)
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return None
    
    # Generate timestamped XML file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_project_name = project_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    xml_file = f"/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/{safe_project_name}_Schedule_{timestamp}.xml"
    
    print(f"📋 CSV Source: {csv_file}")
    print(f"🎯 XML Output: {xml_file}")
    
    if description:
        print(f"📝 Update: {description}")
    
    # Execute CSV to XML conversion
    try:
        converter_script = "/workspaces/control_tower/scripts/simple_csv_to_xml_fixed.py"
        conversion_cmd = [
            'python3', converter_script,
            '--csv', csv_file,
            '--output', xml_file,
            '--project-name', project_name
        ]
        
        print(f"🔄 Converting CSV to MS Project XML...")
        result = subprocess.run(conversion_cmd, capture_output=True, text=True, cwd='/workspaces/control_tower')
        
        if result.returncode == 0:
            print(f"✅ CSV to XML conversion successful!")
            # Show converter output
            for line in result.stdout.strip().split('\n'):
                if line.strip() and not line.startswith('📋') and not line.startswith('�'):
                    print(f"  {line}")
            
            # Verify file was created and has content
            if os.path.exists(xml_file):
                file_size = os.path.getsize(xml_file)
                if file_size > 1000:  # Basic sanity check
                    print(f"✅ Generated XML ready for manual import: {os.path.basename(xml_file)}")
                    print(f"📊 File size: {file_size} bytes")
                    return xml_file
                else:
                    print(f"❌ Generated XML too small ({file_size} bytes) - likely corrupted")
                    return None
            else:
                print(f"❌ XML file was not created at expected location: {xml_file}")
                return None
        else:
            print(f"❌ CSV conversion failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error during CSV conversion: {e}")
        return None

def find_available_standalone_projects():
    """Find all available standalone Level 4 project XML files"""
    xml_workspace = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace"
    
    if not os.path.exists(xml_workspace):
        return []
    
    # Look for standalone project XML files (excluding main ZnNi file and backups)
    standalone_files = []
    for file in os.listdir(xml_workspace):
        if (file.endswith('.xml') and 
            not file.startswith('ZnNi Line Development Plan') and
            not 'backup' in file.lower() and
            not file.startswith('TEST_')):
            standalone_files.append(file)
    
    return standalone_files

def integrate_latest_updates(project_name=None, description=None):
    """Prepare the latest standalone XML for direct MS Project import (Option 1)"""
    print("\n🔄 PREPARING STANDALONE XML FOR DIRECT IMPORT...")
    print("=" * 50)
    
    xml_workspace = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace"
    
    # FLEXIBLE CSV HANDLING: Try to find matching CSV file for any project
    if project_name:
        csv_file = find_matching_csv_file(project_name)
        if csv_file:
            print(f"🎯 {project_name} detected - generating from CSV data")
            return generate_xml_from_csv(csv_file, project_name, description)
    
    # FALLBACK: SF Investment Strategy (backward compatibility)
    if project_name and ("sf investment" in project_name.lower() or "investment strategy" in project_name.lower()):
        print("🎯 SF Investment Strategy detected - generating from CSV data (legacy)")
        return generate_sf_investment_xml_from_csv(description)
    
    # Find available standalone projects
    available_projects = find_available_standalone_projects()
    
    if not available_projects:
        print("❌ No standalone Level 4 project XML files found")
        print(f"📁 Checked directory: {xml_workspace}")
        print("💡 Create a standalone XML file for your Level 4 project first")
        return None
    
    # If specific project requested, use it
    if project_name:
        # Look for exact match or partial match
        matching_files = [f for f in available_projects if project_name.lower() in f.lower()]
        if matching_files:
            selected_file = matching_files[0]
        else:
            print(f"❌ Project '{project_name}' not found in available standalone files")
            print(f"📋 Available projects: {', '.join(available_projects)}")
            return None
    else:
        # Auto-select or let user choose
        if len(available_projects) == 1:
            selected_file = available_projects[0]
            print(f"🎯 Auto-selected only available project: {selected_file}")
        else:
            print(f"📋 Available Level 4 projects:")
            for i, file in enumerate(available_projects, 1):
                project_title = file.replace('_', ' ').replace('.xml', '')
                print(f"   {i}. {project_title}")
            
            # For now, default to first available (can be enhanced with user input)
            selected_file = available_projects[0]
            print(f"🎯 Using first available: {selected_file}")
    
    standalone_xml = os.path.join(xml_workspace, selected_file)
    
    if os.path.exists(standalone_xml):
        project_title = selected_file.replace('_', ' ').replace('.xml', '')
        print(f"✅ Found Level 4 project: {project_title}")
        print("📋 Option 1: Using standalone XML file for direct MS Project import")
        
        if description:
            print(f"📝 Update: {description}")
        
        # No integration needed - standalone file is ready for direct import
        print("✅ Standalone XML ready for direct MS Project import")
        return standalone_xml
    else:
        print(f"❌ Standalone XML file not accessible: {standalone_xml}")
        return None

def generate_sf_investment_xml_from_csv(description=None):
    """Generate SF Investment Strategy XML from CSV data"""
    print("\n📊 GENERATING SF INVESTMENT XML FROM CSV...")
    print("-" * 50)
    
    # CSV source file
    csv_file = "/workspaces/control_tower/data/SF_Investment_Strategy_OEE_OLE_Import_CORRECTED.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return None
    
    # Generate timestamped XML file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    xml_file = f"/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/SF_Investment_Strategy_OEE_OLE_Application_Schedule_{timestamp}.xml"
    
    print(f"📋 CSV Source: {csv_file}")
    print(f"🎯 XML Output: {xml_file}")
    
    if description:
        print(f"📝 Update: {description}")
    
    # Execute CSV to XML conversion
    try:
        converter_script = "/workspaces/control_tower/scripts/simple_csv_to_xml_fixed.py"
        conversion_cmd = [
            'python3', converter_script,
            '--csv', csv_file,
            '--output', xml_file,
            '--project-name', 'SF Investment Strategy - OEE/OLE Implementation'
        ]
        
        print(f"🔄 Converting CSV to MS Project XML...")
        result = subprocess.run(conversion_cmd, capture_output=True, text=True, cwd='/workspaces/control_tower')
        
        if result.returncode == 0:
            print(f"✅ CSV to XML conversion successful!")
            # Show converter output
            for line in result.stdout.strip().split('\n'):
                if line.strip() and not line.startswith('📋') and not line.startswith('�'):
                    print(f"  {line}")
            
            # Verify file was created and has content
            if os.path.exists(xml_file):
                file_size = os.path.getsize(xml_file)
                if file_size > 1000:  # Basic sanity check
                    print(f"✅ Generated XML ready for manual import: {os.path.basename(xml_file)}")
                    print(f"📊 File size: {file_size} bytes")
                    return xml_file
                else:
                    print(f"❌ Generated XML too small ({file_size} bytes) - likely corrupted")
                    return None
            else:
                print(f"❌ XML file was not created at expected location: {xml_file}")
                return None
        else:
            print(f"❌ CSV conversion failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error during CSV conversion: {e}")
        return None

def detect_ms_project_path():
    """Detect MS Project installation path"""
    common_paths = [
        # MS Project 2021/2019/2016
        r"C:\Program Files\Microsoft Office\root\Office16\WINPROJ.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINPROJ.EXE",
        
        # MS Project 2013
        r"C:\Program Files\Microsoft Office\Office15\WINPROJ.EXE",
        r"C:\Program Files (x86)\Microsoft Office\Office15\WINPROJ.EXE",
        
        # MS Project 2010
        r"C:\Program Files\Microsoft Office\Office14\WINPROJ.EXE",
        r"C:\Program Files (x86)\Microsoft Office\Office14\WINPROJ.EXE",
        
        # MS Project standalone
        r"C:\Program Files\Microsoft Project\WINPROJ.EXE",
        r"C:\Program Files (x86)\Microsoft Project\WINPROJ.EXE",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def convert_wsl_path_to_windows(wsl_path):
    """Convert WSL path to Windows path for MS Project"""
    if platform.system() == "Linux" and "microsoft" in platform.uname().release.lower():
        # We're in WSL - convert path
        # /workspaces/control_tower/... -> /mnt/c/... or similar
        try:
            result = subprocess.run(['wslpath', '-w', wsl_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
    
    return wsl_path

def launch_ms_project(xml_file_path):
    """Provide instructions for manual MS Project import"""
    print(f"\n� MANUAL MS PROJECT IMPORT INSTRUCTIONS")
    print("=" * 50)
    
    # Convert path for Windows if needed
    windows_path = convert_wsl_path_to_windows(xml_file_path)
    
    print(f"📁 XML File Location: {xml_file_path}")
    if windows_path != xml_file_path:
        print(f"🪟 Windows Path: {windows_path}")
    
    print(f"\n� MANUAL IMPORT STEPS:")
    print(f"   1. Open Microsoft Project")
    print(f"   2. Go to File → Open")
    print(f"   3. Browse to and select the XML file:")
    if windows_path != xml_file_path:
        print(f"      {windows_path}")
    else:
        print(f"      {xml_file_path}")
    print(f"   4. Choose import options in the Import Wizard")
    print(f"   5. Review imported tasks (should show all 38 tasks)")
    print(f"   6. Save your MS Project file")
    
    # Try to open file location for convenience
    if platform.system() == "Windows":
        try:
            # Open the containing folder
            folder_path = os.path.dirname(windows_path)
            subprocess.Popen(['explorer', folder_path])
            print(f"\n💡 Opened folder in Windows Explorer: {folder_path}")
            return True
        except Exception as e:
            print(f"\n⚠️  Could not open folder: {e}")
            return False
    
    elif platform.system() == "Linux" and "microsoft" in platform.uname().release.lower():
        # WSL - try to open Windows folder
        try:
            folder_path = os.path.dirname(windows_path)
            subprocess.Popen(['cmd.exe', '/c', 'explorer', folder_path])
            print(f"\n💡 Opened folder via WSL: {folder_path}")
            return True
        except Exception as e:
            print(f"\n⚠️  Could not open folder via WSL: {e}")
            return False
    
    else:
        print(f"\n💡 Navigate to the file location manually in your file manager")
        return True

def create_desktop_shortcut():
    """Create a desktop shortcut for easy access"""
    if platform.system() == "Windows":
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "Launch ZnNi Project.bat")
            
            script_path = os.path.abspath(__file__)
            
            with open(shortcut_path, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{os.path.dirname(script_path)}"\n')
                f.write(f'python "{script_path}"\n')
                f.write(f'pause\n')
            
            print(f"🔗 Desktop shortcut created: {shortcut_path}")
            return True
        except Exception as e:
            print(f"⚠️  Could not create shortcut: {e}")
            return False
    
    return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Auto-launch MS Project with latest updates for any Level 4 project')
    parser.add_argument('--project', 
                       help='Name or partial name of the Level 4 project to launch')
    parser.add_argument('--description', 
                       help='Description of what changed in this update')
    parser.add_argument('--create-shortcut', action='store_true',
                       help='Create desktop shortcut for easy access')
    parser.add_argument('--list-projects', action='store_true',
                       help='List all available Level 4 projects')
    
    args = parser.parse_args()
    
    if args.list_projects:
        print("📋 AVAILABLE LEVEL 4 PROJECTS")
        print("=" * 50)
        available_projects = find_available_standalone_projects()
        if available_projects:
            for i, file in enumerate(available_projects, 1):
                project_title = file.replace('_', ' ').replace('.xml', '')
                print(f"   {i}. {project_title}")
                print(f"      File: {file}")
        else:
            print("❌ No standalone Level 4 project files found")
            print("💡 Create standalone XML files for your Level 4 projects first")
        return 0
    
    print("🚀 MS PROJECT AUTO-LAUNCHER (OPTION 1)")
    print("=" * 60)
    print("🎯 This will automatically:")
    print("   1. Locate any Level 4 project standalone XML")
    print("   2. Launch MS Project with standalone file directly")
    print("   3. Handle cross-platform compatibility")
    print("   4. Skip main XML integration (Option 1 approach)")
    print()
    
    if args.create_shortcut:
        create_desktop_shortcut()
        return
    
    # Step 1: Prepare standalone XML for direct import
    standalone_xml_path = integrate_latest_updates(args.project, args.description)
    if not standalone_xml_path:
        print("❌ No Level 4 project XML file available for direct import")
        print("💡 Use --list-projects to see available projects")
        print("💡 Use --project 'ProjectName' to specify a specific project")
        return 1
    
    # Step 2: Launch MS Project with standalone XML directly
    success = launch_ms_project(standalone_xml_path)
    
    if success:
        project_name = os.path.basename(standalone_xml_path).replace('_', ' ').replace('.xml', '')
        print("\n🎉 SUCCESS!")
        print("=" * 50)
        print("✅ XML file ready for manual MS Project import")
        print(f"📊 Level 4 project: {project_name}")
        print("🔄 Manual import workflow prepared")
        print()
        print("💡 TIP: Use this command again to regenerate fresh XML:")
        if args.project:
            print(f"   python {os.path.abspath(__file__)} --project '{args.project}' --description 'Updated tasks'")
        else:
            print(f"   python {os.path.abspath(__file__)} --description 'Updated tasks'")
    else:
        project_name = os.path.basename(standalone_xml_path).replace('_', ' ').replace('.xml', '')
        print("\n⚠️  MANUAL STEPS REQUIRED")
        print("=" * 50)
        print(f"📁 Your Level 4 project XML file is ready at:")
        print(f"   {standalone_xml_path}")
        print(f"📊 Project: {project_name}")
        print("🖱️  Please import this file manually into MS Project")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
