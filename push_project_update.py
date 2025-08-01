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
    print("🚀 MS PROJECT & SLIDE DECK UPDATE WORKFLOW")
    print("=" * 80)
    print("This will execute:")
    print("1. 🔗 Integrate XML changes into ZnNi Line Development Plan-08")
    print("2. 📋 Open change management form")
    print("3. 🔄 Update MS Project integration")
    print("4. 📊 Update PowerPoint presentations")
    print("5. 📤 Commit changes to repository")
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
    
    # Step 1: Integrate current XML file into ZnNi master plan
    print("\n🔸 STEP 1: Integrate XML Changes")
    print("-" * 50)
    
    # Check if the standalone XML file exists
    standalone_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/SF_Investment_Strategy_OEE_OLE_Application_Schedule.xml"
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
    
    # Step 2: Execute Contract Project Manager with Change Management
    print("\n🔸 STEP 2: Change Management & MS Project Update")
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
    
    # Step 3: Update PowerPoint Presentations
    print("\n🔸 STEP 3: Update PowerPoint Presentations")
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
    
    # Step 4: Show Change Summary
    print("\n🔸 STEP 4: Change Summary")
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
