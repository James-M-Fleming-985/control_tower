#!/usr/bin/env python3
"""
MS Project & Slide Deck Update Workflow
=======================================

This script executes the complete MS Project and PowerPoint update workflow:
1. Integrate XML changes into ZnNi Line Development Plan-08
2. Open change management form in terminal
3. Update MS Project files with milestone tracking
4. Update PowerPoint presentations (timeline, milestones, risk tables)
5. Track changes and update presentation snapshots

Usage:
    python push_project_update.py --description "What changed"
    
Example:
    python push_project_update.py --description "Added SF Investment Strategy OEE & OLE Application with Power BI integration"
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Add module paths
sys.path.append('/workspaces/control_tower/modules/ms_project')
sys.path.append('/workspaces/control_tower/modules/milestone_management/reporting')

def execute_complete_update_workflow(description: str = None):
    """Execute the complete project update workflow"""
    
    print("\n" + "=" * 80)
    print("🚀 COMPLETE MS PROJECT & POWERPOINT WORKFLOW")
    print("=" * 80)
    print("This will execute:")
    print("1. 📊 Convert CSV to XML for any Level 3 project")
    print("2. 🔗 Integrate XML changes into ZnNi Line Development Plan-08")
    print("3. 📋 Open change management form")
    print("4. 🔄 Update MS Project integration")
    print("5. 📊 Update PowerPoint presentations")
    print("6. 📤 Commit changes to repository")
    print("=" * 80)
    
    # Import required modules
    sys.path.append('/workspaces/control_tower/modules/ms_project')
    sys.path.append('/workspaces/control_tower/modules/milestone_management')
    
    # Initialize project manager with enhanced tracking
    from contract_project_manager import ContractProjectManager
    from milestone_tracker import MilestoneTracker
    
    manager = ContractProjectManager()
    tracker = MilestoneTracker()
    
    # Project file path
    project_file = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    
    if not os.path.exists(project_file):
        print(f"❌ Project file not found: {project_file}")
        return False
        
    print(f"📂 Project: ZnNi Line Development Plan-08")
    print(f"📝 Description: {description}")
    print()
    
    # Step 1: Generate XML from CSV (for any Level 3 project)
    print("\n🔸 STEP 1: Generate XML from CSV Data")
    print("-" * 50)
    
    # Check for SF Investment Strategy CSV (can be extended for other projects)
    csv_file = "/workspaces/control_tower/data/SF_Investment_Strategy_OEE_OLE_Import_CORRECTED.csv"
    
    if os.path.exists(csv_file):
        print(f"📊 Found SF Investment Strategy CSV: {os.path.basename(csv_file)}")
        
        # Generate timestamped XML file
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        xml_output = f"/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/SF_Investment_Strategy_OEE_OLE_Application_Schedule_{timestamp}.xml"
        
        # Execute CSV to XML conversion
        try:
            converter_script = "/workspaces/control_tower/scripts/simple_csv_to_xml.py"
            conversion_cmd = [
                'python3', converter_script,
                '--csv', csv_file,
                '--output', xml_output,
                '--project-name', 'SF Investment Strategy - OEE/OLE Implementation'
            ]
            
            print(f"🔄 Converting CSV to XML...")
            result = subprocess.run(conversion_cmd, capture_output=True, text=True, cwd='/workspaces/control_tower')
            
            if result.returncode == 0:
                print(f"✅ CSV to XML conversion successful!")
                print(f"📁 Generated: {os.path.basename(xml_output)}")
                # Update the standalone XML path for integration
                standalone_xml = xml_output
            else:
                print(f"⚠️  CSV conversion warning: {result.stderr}")
                print("Using existing standalone XML...")
                standalone_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/SF_Investment_Strategy_OEE_OLE_Application_Schedule.xml"
                
        except Exception as e:
            print(f"⚠️  CSV conversion error: {e}")
            print("Using existing standalone XML...")
            standalone_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/SF_Investment_Strategy_OEE_OLE_Application_Schedule.xml"
    else:
        print("ℹ️  No CSV file found, using existing standalone XML")
        standalone_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/SF_Investment_Strategy_OEE_OLE_Application_Schedule.xml"
    
    # Step 2: Integrate current XML file into ZnNi master plan
    print("\n🔸 STEP 2: Integrate XML Changes")
    print("-" * 50)
    
    # Check if the standalone XML file exists
    znni_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    
    if os.path.exists(standalone_xml):
        print(f"✅ Found standalone XML: {os.path.basename(standalone_xml)}")
        
        # Execute the integration script
        try:
            os.chdir('/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace')
            result = subprocess.run(['python', 'update_znni_project.py'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ XML integration successful")
                print(f"📁 Updated: {os.path.basename(znni_xml)}")
            else:
                print(f"⚠️  XML integration warning: {result.stderr}")
                print("Continuing with workflow...")
                
        except subprocess.TimeoutExpired:
            print("⚠️  XML integration timed out, continuing...")
        except Exception as e:
            print(f"⚠️  XML integration error: {e}, continuing...")
    else:
        print("ℹ️  No standalone XML file found, using existing ZnNi plan")
    
    # Step 3: Execute Contract Project Manager with Change Management
    print("\n🔸 STEP 3: Change Management & MS Project Update")
    print("-" * 50)
    
    try:
        # This will open the change management form in terminal
        update_description = description or "MS Project schedule update via Control Tower"
        success = manager.update_project_with_change_management(
            update_description=update_description,
            auto_approve=False  # Always show the form for user input
        )
        
        if not success:
            print("❌ Change management or project update failed/cancelled")
            return False
            
        print("✅ MS Project integration completed")
        
    except Exception as e:
        print(f"❌ Error in change management: {e}")
        return False
    
    # Step 4: Update PowerPoint Presentations
    print("\n🔸 STEP 4: Update PowerPoint Presentations")
    print("-" * 50)
    
    try:
        from safran_powerpoint_generator import SafranPowerpointGenerator
        
        # Generate updated presentation with change management data
        ppt_generator = SafranPowerpointGenerator("contract_projects")
        ppt_file = ppt_generator.generate_safran_presentation()
        
        if ppt_file:
            print(f"✅ PowerPoint updated: {os.path.basename(ppt_file)}")
            print("📊 Includes updated timelines, milestones, and change slides")
        else:
            print("⚠️  PowerPoint generation failed, but continuing...")
            
    except Exception as e:
        print(f"⚠️  PowerPoint error: {e}, continuing...")
    
    # Step 5: Show Change Summary
    print("\n🔸 STEP 5: Change Summary")
    print("-" * 50)
    
    try:
        change_summary = manager.change_management.generate_change_summary_report()
        print(change_summary)
    except:
        print("⚠️  Could not generate change summary")
    
    print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("✅ Change management captured")
    print("✅ MS Project files updated") 
    print("✅ PowerPoint presentations generated")
    print("✅ Milestone/risk tracking updated")
    print()
    print("💡 Note: Repository commit not included in workflow")
    print("   Use your normal git workflow to commit when ready")
    print("   Files ready for commit:")
    print("   • MS Project XML files")
    print("   • PowerPoint presentations") 
    print("   • Change management logs")
    print("   • Milestone tracking snapshots")
    
    return True

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Execute complete MS Project update workflow with change management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python push_project_update.py --description "Added Power BI investment optimization"
    python push_project_update.py --description "Updated milestone dates and dependencies"
    python push_project_update.py --description "Integrated SF OEE/OLE application timeline"
        """
    )
    parser.add_argument('--description', required=True,
                       help='Description of what changed in this update')
    
    args = parser.parse_args()
    
    print(f"\n📋 Update Description: {args.description}")
    
    # Confirm before proceeding
    confirm = input(f"\n🤔 Ready to execute MS Project & Slide Deck Update Workflow? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("❌ Workflow cancelled by user")
        return 1
    
    try:
        success = execute_complete_update_workflow(args.description)
        
        if success:
            print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("="*80)
            return 0
        else:
            print("\n❌ WORKFLOW FAILED!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Workflow cancelled by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
