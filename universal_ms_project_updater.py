#!/usr/bin/env python3
"""
Universal Level 4 Project Updater - Codespaces to Windows
=========================================================

Machine-agnostic remote MS Project launcher that can update ANY Level 4 project
within the main ZnNi Line Development Plan-08.xml file.

This script:
1. Finds standalone XML for any Level 4 project
2. Integrates it into the main ZnNi project XML
3. Copies the updated ZnNi project to target Windows machine
4. Launches MS Project with the complete updated project

Usage from ANY Codespaces session:
    python universal_ms_project_updater.py --project "Any Level 4 Project Name" --description "Updates"
    
Examples:
    python universal_ms_project_updater.py --project "SF Investment Strategy OEE & OLE Application" --description "Updated data integration tasks"
    python universal_ms_project_updater.py --project "Manufacturing Optimization Phase 1" --description "Added new milestones"
"""

import argparse
import subprocess
import os
import sys
import configparser
from pathlib import Path

def load_windows_target_config():
    """Load Windows machine target configuration"""
    config_path = "/workspaces/control_tower/config/windows_target.conf"
    
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        print("💡 Run: python setup_windows_target.py")
        return None
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    try:
        return {
            'host': config['windows_machine']['host'],
            'username': config.get('windows_machine', 'username', fallback=None),
            'xml_workspace': config['windows_machine']['xml_workspace'],
            'ms_project_workspace': config['windows_machine']['ms_project_workspace'],
            'ssh_key': config.get('network', 'ssh_key', fallback='~/.ssh/id_rsa'),
            'use_admin_shares': config.getboolean('network', 'use_admin_shares', fallback=False),
            'main_project_location': config['ms_project']['main_project_file'],
            'codespaces_xml_workspace': config['codespaces']['xml_workspace']
        }
    except KeyError as e:
        print(f"❌ Missing configuration key: {e}")
        return None

def find_standalone_xml_for_project(project_name, xml_workspace):
    """Find standalone XML file for any Level 4 project"""
    print(f"🔍 Looking for standalone XML for project: '{project_name}'")
    
    # Generate potential filename patterns
    filename_patterns = [
        # Standard patterns
        f"{project_name.replace(' ', '_')}_Schedule.xml",
        f"{project_name.replace(' ', '_')}.xml",
        # Handle special characters
        f"{project_name.replace(' & ', '_').replace(' ', '_')}_Schedule.xml",
        f"{project_name.replace(' & ', '_').replace(' ', '_')}.xml",
        # Common variations
        f"{project_name.replace(' ', '_').replace('&', 'and')}_Schedule.xml",
        f"{project_name.replace(' ', '_').replace('&', 'and')}.xml"
    ]
    
    print(f"🔍 Searching for: {filename_patterns[:3]}...")  # Show first 3 patterns
    
    # Check each pattern
    for pattern in filename_patterns:
        filepath = os.path.join(xml_workspace, pattern)
        if os.path.exists(filepath):
            print(f"✅ Found standalone XML: {pattern}")
            return filepath
    
    # If not found, list available files for reference
    available_files = [f for f in os.listdir(xml_workspace) if f.endswith('.xml') and 'ZnNi' not in f]
    print(f"❌ No standalone XML found for project: '{project_name}'")
    print(f"📁 Available standalone files: {available_files}")
    
    return None

def integrate_project_into_znni(standalone_xml, project_name, xml_workspace, description):
    """Integrate any Level 4 project into main ZnNi XML using dynamic update script"""
    print(f"\n🔄 INTEGRATING LEVEL 4 PROJECT INTO ZNNI...")
    print("=" * 60)
    
    main_znni_xml = os.path.join(xml_workspace, "ZnNi Line Development Plan-08.xml")
    
    if not os.path.exists(main_znni_xml):
        print(f"❌ Main ZnNi project file not found: {main_znni_xml}")
        return None
    
    print(f"✅ Standalone XML: {os.path.basename(standalone_xml)}")
    print(f"✅ Main ZnNi project: {os.path.basename(main_znni_xml)}")
    print(f"🎯 Level 4 Project: {project_name}")
    print(f"📝 Description: {description}")
    
    # Run the dynamic integration script
    print("🔄 Running dynamic project integration...")
    
    try:
        # Change to XML workspace directory
        original_cwd = os.getcwd()
        os.chdir(xml_workspace)
        
        # Run our dynamic update script with project parameter
        cmd = f'python update_znni_project.py --project "{project_name}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("✅ Integration completed successfully")
            print("📊 Level 4 project integrated into main ZnNi project")
            return main_znni_xml
        else:
            print(f"❌ Integration failed: {result.stderr}")
            print(f"💡 Output: {result.stdout}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Integration timed out")
        os.chdir(original_cwd)
        return None
    except Exception as e:
        print(f"❌ Integration error: {e}")
        os.chdir(original_cwd)
        return None

def copy_znni_to_windows(znni_xml_file, config):
    """Copy the updated ZnNi project file to Windows machine"""
    print(f"\n📁 COPYING UPDATED ZNNI PROJECT TO WINDOWS...")
    print("=" * 60)
    
    try:
        windows_host = config['host']
        windows_project_path = config['main_project_location']
        
        if config['use_admin_shares']:
            # Use Windows Admin Shares
            print("🔄 Using Windows Admin Shares method...")
            unc_path = windows_project_path.replace('C:', f'//{windows_host}/c$').replace('\\', '/')
            copy_command = f"cp {znni_xml_file} {unc_path}"
        else:
            # Use SCP method
            print("🔄 Using SCP method...")
            if config['username']:
                scp_target = f"{config['username']}@{windows_host}:{windows_project_path}"
            else:
                scp_target = f"{windows_host}:{windows_project_path}"
            
            copy_command = f"scp -i {config['ssh_key']} {znni_xml_file} {scp_target}"
        
        print(f"🔄 Executing: {copy_command}")
        result = subprocess.run(copy_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Updated ZnNi project copied to Windows machine")
            print(f"📍 Location: {windows_project_path}")
            return windows_project_path
        else:
            print(f"❌ Copy failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        return None

def launch_znni_project_on_windows(config, windows_xml_path, project_name, description):
    """Launch MS Project with the updated ZnNi project on Windows machine"""
    print(f"\n🚀 LAUNCHING ZNNI PROJECT ON WINDOWS...")
    print("=" * 60)
    
    windows_host = config['host']
    
    # PowerShell command to launch MS Project with the full ZnNi project
    powershell_command = f'''
    $msProjectPath = Get-ChildItem "C:\\Program Files*\\Microsoft Office*\\Office*\\WINPROJ.EXE" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($msProjectPath) {{
        Write-Host "Found MS Project: $($msProjectPath.FullName)"
        Write-Host "Opening ZnNi Project: {windows_xml_path}"
        Write-Host "Updated Level 4 Project: {project_name}"
        Write-Host "Description: {description}"
        Start-Process -FilePath $msProjectPath.FullName -ArgumentList '"{windows_xml_path}"'
        Write-Host "ZnNi Line Development Plan opened with {project_name} updates!"
    }} else {{
        Write-Host "MS Project not found on this machine"
        exit 1
    }}
    '''
    
    try:
        # Build SSH command
        if config['username']:
            ssh_target = f"{config['username']}@{windows_host}"
        else:
            ssh_target = windows_host
            
        ssh_command = f'ssh -i {config["ssh_key"]} {ssh_target} "powershell -Command \\"{powershell_command}\\""'
        
        print(f"🔄 Executing remote command on {windows_host}")
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ZnNi Line Development Plan launched with Level 4 updates!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Remote execution failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error executing remote command: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update any Level 4 project in ZnNi Line Development Plan on Windows from Codespaces')
    parser.add_argument('--project', required=True,
                       help='Name of the Level 4 project to update (e.g., "SF Investment Strategy OEE & OLE Application")')
    parser.add_argument('--description', required=True,
                       help='Description of the updates made to the project')
    
    args = parser.parse_args()
    
    print("🌐 UNIVERSAL LEVEL 4 PROJECT UPDATER")
    print("=" * 80)
    print("🎯 ANY Codespaces → Windows ZnNi Project → Level 4 Integration")
    print(f"📊 Level 4 Project: {args.project}")
    print(f"📝 Update Description: {args.description}")
    print()
    
    # Step 1: Load target Windows machine configuration
    config = load_windows_target_config()
    if not config:
        return 1
    
    print(f"📍 Target Windows: {config['host']}")
    print(f"📁 ZnNi Project: {config['main_project_location']}")
    print()
    
    # Step 2: Find standalone XML for the requested Level 4 project
    xml_workspace = config['codespaces_xml_workspace']
    standalone_xml = find_standalone_xml_for_project(args.project, xml_workspace)
    if not standalone_xml:
        return 1
    
    # Step 3: Integrate the Level 4 project into main ZnNi XML
    updated_znni_xml = integrate_project_into_znni(standalone_xml, args.project, xml_workspace, args.description)
    if not updated_znni_xml:
        return 1
    
    # Step 4: Copy updated ZnNi project to Windows machine
    windows_xml_path = copy_znni_to_windows(updated_znni_xml, config)
    if not windows_xml_path:
        return 1
    
    # Step 5: Launch MS Project with the updated ZnNi project on Windows
    success = launch_znni_project_on_windows(config, windows_xml_path, args.project, args.description)
    
    if success:
        print("\n🎉 LEVEL 4 PROJECT UPDATE COMPLETED!")
        print("=" * 80)
        print(f"✅ ZnNi Line Development Plan opened on {config['host']}")
        print(f"📊 Level 4 Project '{args.project}' integrated and updated")
        print("🔄 Full project context maintained")
        print()
        print("💡 Universal command - works for ANY Level 4 project!")
        return 0
    else:
        print("\n❌ WORKFLOW FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
