#!/usr/bin/env python3
"""
Guided Project Workflow with Manual MS Project Import
====================================================

This script manages the complete project workflow including the manual 
MS Project import step. It provides clear guidance and checkpoints to
ensure each step is completed correctly.

Usage:
    python guided_project_workflow.py --project "SF Investment Strategy" --description "Update description"
    python guided_project_workflow.py --project "Financial Optimizer" --description "Added new features"
    
Process:
    1. Generate XML from CSV automatically
    2. Guide user through manual MS Project import
    3. Wait for confirmation that import is complete
    4. Continue with PowerPoint generation and change management
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"🔸 {title}")
    print("=" * 80)

def print_step(step_num, title):
    """Print a formatted step header"""
    print(f"\n📋 STEP {step_num}: {title}")
    print("-" * 60)

def wait_for_user_confirmation(message):
    """Wait for user to confirm they've completed a manual step"""
    print(f"\n⏸️  {message}")
    print("   Press ENTER when ready to continue, or 'q' to quit...")
    
    while True:
        user_input = input("   ").strip().lower()
        if user_input == 'q':
            print("🚫 Workflow cancelled by user")
            return False
        elif user_input == '':
            return True
        else:
            print("   Please press ENTER to continue or 'q' to quit...")

def generate_xml_from_csv(project_name, description):
    """Generate XML file from CSV data"""
    print_step(1, "Generate XML from CSV Data")
    
    # Use the existing auto_launch_msproject.py to generate XML
    try:
        cmd = [
            'python3', 'auto_launch_msproject.py',
            '--project', project_name
        ]
        
        if description:
            cmd.extend(['--description', description])
        
        print(f"🔄 Generating XML for project: {project_name}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='/workspaces/control_tower')
        
        if result.returncode == 0:
            print("✅ XML generation successful!")
            
            # Parse output to find generated XML file path
            xml_file_path = None
            for line in result.stdout.split('\n'):
                if 'Generated XML ready for manual import:' in line:
                    xml_filename = line.split(':')[-1].strip()
                    xml_file_path = f"/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/{xml_filename}"
                    break
                elif 'Output:' in line and '.xml' in line:
                    xml_file_path = line.split('Output:')[-1].strip()
                    break
            
            if xml_file_path and os.path.exists(xml_file_path):
                print(f"📁 XML File: {xml_file_path}")
                return xml_file_path
            else:
                # Fallback: look for recent XML files
                xml_workspace = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace"
                if os.path.exists(xml_workspace):
                    xml_files = [f for f in os.listdir(xml_workspace) if f.endswith('.xml') and project_name.replace(' ', '_') in f]
                    if xml_files:
                        # Get most recent
                        xml_files.sort(key=lambda x: os.path.getmtime(os.path.join(xml_workspace, x)), reverse=True)
                        xml_file_path = os.path.join(xml_workspace, xml_files[0])
                        print(f"📁 Found XML File: {xml_file_path}")
                        return xml_file_path
                
                print("⚠️  XML file generated but path not found in output")
                return None
                
        else:
            print(f"❌ XML generation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating XML: {e}")
        return None

def guide_manual_import(xml_file_path):
    """Guide user through manual MS Project import"""
    print_step(2, "Manual MS Project Import")
    
    print("📁 XML File Ready for Import:")
    print(f"   {xml_file_path}")
    
    print("\n🔸 MANUAL IMPORT INSTRUCTIONS:")
    print("   1. Open Microsoft Project")
    print("   2. Go to File → Open")
    print("   3. Browse to and select the XML file:")
    print(f"      {xml_file_path}")
    print("   4. 🚨 IMPORTANT: Choose 'New Project' (not merge/append)")
    print("   5. Follow the Import Wizard")
    print("   6. Review imported tasks (should show all tasks with correct dates)")
    print("   7. Save your project as a .mpp file")
    
    print("\n💡 TIPS:")
    print("   • Make sure you choose 'New Project' to avoid appending")
    print("   • Verify dates match your project documentation")
    print("   • Check that hierarchical structure is preserved")
    print("   • Save the .mpp file in a location you can remember")
    
    return wait_for_user_confirmation("Have you successfully imported the XML file and saved your MS Project file?")

def execute_powerpoint_workflow(description, project_name):
    """Execute the PowerPoint and change management workflow"""
    print_step(3, "PowerPoint Generation & Change Management")
    
    try:
        # Import and execute the existing workflow
        sys.path.append('/workspaces/control_tower')
        from push_project_update import execute_complete_update_workflow
        
        print(f"🔄 Executing PowerPoint and change management workflow...")
        print(f"📝 Description: {description}")
        
        # Execute the workflow (skipping XML generation since we did it manually)
        success = execute_complete_update_workflow(description)
        
        if success:
            print("✅ PowerPoint and change management workflow completed!")
            return True
        else:
            print("❌ PowerPoint workflow failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in PowerPoint workflow: {e}")
        return False

def main():
    """Main guided workflow function"""
    parser = argparse.ArgumentParser(description='Guided project workflow with manual MS Project import')
    parser.add_argument('--project', required=True,
                       help='Project name (e.g., "SF Investment Strategy")')
    parser.add_argument('--description', required=True,
                       help='Description of what changed in this update')
    
    args = parser.parse_args()
    
    print_header("GUIDED PROJECT WORKFLOW WITH MANUAL IMPORT")
    print("🎯 This workflow will guide you through:")
    print("   1. ✅ Automated XML generation from CSV data")
    print("   2. 👤 Manual MS Project import (with guidance)")
    print("   3. ✅ Automated PowerPoint generation & change management")
    print()
    print(f"📊 Project: {args.project}")
    print(f"📝 Description: {args.description}")
    
    # Step 1: Generate XML automatically
    xml_file_path = generate_xml_from_csv(args.project, args.description)
    if not xml_file_path:
        print("❌ XML generation failed. Cannot continue.")
        return 1
    
    # Step 2: Guide user through manual import
    import_completed = guide_manual_import(xml_file_path)
    if not import_completed:
        print("🚫 Manual import was not completed. Workflow cancelled.")
        return 1
    
    # Step 3: Execute PowerPoint workflow
    powerpoint_success = execute_powerpoint_workflow(args.description, args.project)
    if not powerpoint_success:
        print("❌ PowerPoint workflow failed")
        return 1
    
    # Final success message
    print_header("WORKFLOW COMPLETED SUCCESSFULLY!")
    print("✅ XML generated and imported into MS Project")
    print("✅ PowerPoint presentations updated")
    print("✅ Change management captured")
    print("✅ Milestone tracking updated")
    print()
    print("🎉 Your project has been successfully updated across all systems!")
    print()
    print("💡 NEXT STEPS:")
    print("   • Review your updated MS Project file")
    print("   • Check the generated PowerPoint presentations")
    print("   • Share milestone updates with stakeholders")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
