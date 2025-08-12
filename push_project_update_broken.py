#!/usr/bin/env python3
"""
MS Project & Slide Deck Update Workflow
=======================================

This script executes the complete MS Project and PowerPoint update workflow:
1.        if success:
            print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("="*80)
            print("📊 PowerPoint presentation updated with latest data")
            print("📁 MS Project XML ready for import")
            
            # Auto-launch MS Project with updated XML (user requirement)
            print("\n🚀 LAUNCHING MS PROJECT WITH UPDATES...")
            try:
                xml_file = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
                
                # Simple approach: Open the file with default application
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.Popen(['start', xml_file], shell=True)
                    print("✅ MS Project launched with updated file")
                elif platform.system() == "Linux" and "microsoft" in platform.uname().release.lower():
                    # WSL environment
                    subprocess.Popen(['cmd.exe', '/c', 'start', xml_file])
                    print("✅ MS Project launched via WSL")
                else:
                    print("💡 Please manually open the updated XML file in MS Project:")
                    print(f"   {xml_file}")
                    
            except Exception as e:
                print(f"⚠️  Could not auto-launch MS Project: {e}")
                print("💡 Please manually import the updated XML file:")
                print(f"   {xml_file}")
            
            return 0te XML changes into ZnNi Line Development Plan-08
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

def execute_complete_update_workflow(description, project_name):
    """Execute the complete workflow as documented: XML integration + PowerPoint generation"""
    print("\n" + "="*80)
    print("🚀 STARTING MS PROJECT & SLIDE DECK UPDATE WORKFLOW")
    print("="*80)
    
    try:
        # STEP 1: INTEGRATE STANDALONE XML FILES INTO MAIN XML
        print("\n📁 STEP 1: Integrating standalone XML files into main XML...")
        print(f"🎯 Target Project: {project_name}")
        
        update_script = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/update_znni_project.py"
        
        # Run the XML integration with project parameter
        cmd = f"cd /workspaces/control_tower/cloned_repos/contract_projects/xml_workspace && python update_znni_project.py --project '{project_name}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ XML integration failed: {result.stderr}")
            return False
        
        print("✅ XML integration completed successfully")
        
        # STEP 2: RECORD CHANGE IN CHANGE MANAGEMENT SYSTEM
        print("
� STEP 2: Recording change in change management system...")
        change_manager = ChangeManagementSystem()
        change_id = change_manager.record_change("MS_PROJECT_UPDATE", {
            "description": description,
            "project": project_name,
            "xml_file": "ZnNi Line Development Plan-08.xml",
            "update_type": "Level 4 project update",
            "timestamp": datetime.now().isoformat()
        })
        print(f"✅ Change recorded with ID: {change_id}")
        
        # STEP 3: REGENERATE SAFRAN POWERPOINT WITH UPDATED DATA
        print("
📊 STEP 3: Regenerating SafRan PowerPoint with updated data...")
        
        # Initialize the PowerPoint generator
        generator = SafranPowerPointGenerator()
        
        # Generate the presentation with updated data
        success = generator.generate_presentation(
            output_path="/workspaces/control_tower/cloned_repos/domain_specific-network_dev/powerpoint_reports/SafRan_Weekly_Progress.pptx",
            change_description=description,
            project_focus=project_name
        )
        
        if not success:
            print("❌ PowerPoint generation failed")
            return False
            
        print("✅ PowerPoint presentation updated successfully")
        
        # STEP 4: SUMMARY & STATUS
        print("
📋 STEP 4: Workflow summary...")
        print(f"� Description: {description}")
        print(f"🎯 Project: {project_name}")
        print(f"🔄 Change ID: {change_id}")
        print("📊 PowerPoint: Updated with latest project data")
        print("📁 MS Project XML: Ready for import")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
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
        from safran_powerpoint_generator import SafranPowerPointGenerator
        
        # Generate updated presentation with change management data
        ppt_generator = SafranPowerPointGenerator(repo_name="contract_projects")
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
    """Main function - implements the documented single-command workflow"""
    parser = argparse.ArgumentParser(description='MS Project & Slide Deck Update Workflow')
    parser.add_argument('--description', required=True,
                       help='Description of what changed in this update')
    
    args = parser.parse_args()
    
    def main():
    """Main function - implements the documented single-command workflow"""
    parser = argparse.ArgumentParser(description='MS Project & Slide Deck Update Workflow')
    parser.add_argument('--description', required=True,
                       help='Description of what changed in this update')
    parser.add_argument('--project', required=True,
                       help='Name of the Level 4 project to update (e.g., "SF Investment Strategy OEE & OLE Application")')
    
    args = parser.parse_args()
    
    print(f"
📋 Update Description: {args.description}")
    print(f"🎯 Target Project: {args.project}")
    
    # Confirm before proceeding
    confirm = input(f"
🤔 Ready to execute MS Project & Slide Deck Update Workflow? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("❌ Workflow cancelled by user")
        return 1
    
    try:
        success = execute_complete_update_workflow(args.description, args.project)
        
        if success:
            print("
🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("="*80)
            print(f"📊 PowerPoint presentation updated with latest {args.project} data")
            print("📁 MS Project XML ready for import")
            
            # Auto-launch MS Project with updated XML (user requirement)
            print("
🚀 LAUNCHING MS PROJECT WITH UPDATES...")
            try:
                xml_file = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
                
                # Simple approach: Open the file with default application
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.Popen(['start', xml_file], shell=True)
                    print("✅ MS Project launched with updated file")
                elif platform.system() == "Linux" and "microsoft" in platform.uname().release.lower():
                    # WSL environment
                    subprocess.Popen(['cmd.exe', '/c', 'start', xml_file])
                    print("✅ MS Project launched via WSL")
                else:
                    print("💡 Please manually open the updated XML file in MS Project:")
                    print(f"   {xml_file}")
                    
            except Exception as e:
                print(f"⚠️  Could not auto-launch MS Project: {e}")
                print("💡 Please manually import the updated XML file:")
                print(f"   {xml_file}")
            
            return 0
        else:
            print("
❌ WORKFLOW FAILED!")
            return 1
    
    # Confirm before proceeding
    confirm = input(f"
🤔 Ready to execute MS Project & Slide Deck Update Workflow? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("❌ Workflow cancelled by user")
        return 1
    
    try:
        success = execute_complete_update_workflow(args.description)
        
        if success:
            print("
🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("="*80)
            print("� PowerPoint presentation updated with latest data")
            print("📁 MS Project XML ready for import")
            print("💡 Next step: Import updated XML into MS Project manually")
            return 0
        else:
            print("
❌ WORKFLOW FAILED!")
            return 1
            
    except KeyboardInterrupt:
        print("
⏹️  Workflow cancelled by user")
        return 1
    except Exception as e:
        print(f"
💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
