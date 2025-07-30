#!/usr/bin/env python3
"""
Contract Project Manager for Control Tower
Manages ZnNi Line Development Plan project workflow

This script handles:
- Querying milestones from MS Project XML
- Updating task progress
- Exporting updated XML for MS Project import
- Generating PowerPoint reports
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import argparse

# Add the control tower to path to import our MS Project integration
sys.path.append('/workspaces/control_tower')
from ms_project_integration import MSProjectIntegration

class ContractProjectManager:
    """
    Manage contract projects workflow between Control Tower and MS Project
    """
    
    def __init__(self):
        """Initialize the contract project manager"""
        self.project_name = "ZnNi Line Development Plan"
        self.xml_workspace = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace"
        self.current_xml = os.path.join(self.xml_workspace, "ZnNi Line Development Plan-08.xml")
        self.source_mpp = r"D:\Downloads\ZnNi Line Development Plan-08.mpp"
        self.ms_project = None
        self.auto_sync_enabled = True
        
    def auto_sync_from_mpp(self) -> bool:
        """
        Automatically sync XML from MS Project .mpp file
        Uses MS Project COM interface or command line export
        
        Returns:
            bool: True if successful
        """
        try:
            # Create workspace if it doesn't exist
            os.makedirs(self.xml_workspace, exist_ok=True)
            
            # Check if source .mpp file exists
            if not os.path.exists(self.source_mpp):
                print(f"⚠️  Running in containerized environment - direct .mpp access not available")
                print(f"Expected path: {self.source_mpp}")
                return self._request_manual_export()
            
            print(f"🔄 Auto-syncing from MS Project file...")
            print(f"Source: {self.source_mpp}")
            
            # Try to export XML using PowerShell and MS Project COM
            success = self._export_via_com_interface()
            
            if success:
                print(f"✅ Auto-sync successful! XML updated: {self.current_xml}")
                return True
            else:
                print("⚠️  COM interface failed, trying alternative methods...")
                return self._export_via_alternative_methods()
                
        except Exception as e:
            print(f"❌ Auto-sync failed: {e}")
            return False
    
    def _export_via_com_interface(self) -> bool:
        """
        Export XML using MS Project COM interface via PowerShell
        
        Returns:
            bool: True if successful
        """
        try:
            # PowerShell script to export MS Project to XML
            powershell_script = f'''
Add-Type -AssemblyName "Microsoft.Office.Interop.MSProject"
$msp = New-Object -ComObject MSProject.Application
$msp.Visible = $false

try {{
    $project = $msp.FileOpen("{self.source_mpp}")
    $project.SaveAs("{self.current_xml}", 9)  # 9 = XML format
    $project.Close($false)
    $msp.Quit()
    Write-Output "SUCCESS"
}} catch {{
    Write-Output "ERROR: $_"
    $msp.Quit()
}}
'''
            
            # Write PowerShell script to temporary file
            ps_script_path = os.path.join(self.xml_workspace, "export_temp.ps1")
            with open(ps_script_path, 'w') as f:
                f.write(powershell_script)
            
            # Execute PowerShell script
            result = subprocess.run([
                "powershell.exe", "-ExecutionPolicy", "Bypass", 
                "-File", ps_script_path
            ], capture_output=True, text=True, timeout=60)
            
            # Clean up temporary script
            os.remove(ps_script_path)
            
            if "SUCCESS" in result.stdout:
                return True
            else:
                print(f"PowerShell export failed: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  PowerShell export timed out")
            return False
        except Exception as e:
            print(f"⚠️  PowerShell export error: {e}")
            return False
    
    def _export_via_alternative_methods(self) -> bool:
        """
        Try alternative export methods
        
        Returns:
            bool: True if successful
        """
        # Method 1: Try MPXJ (if available)
        if self._try_mpxj_export():
            return True
            
        # Method 2: Check for existing XML with recent timestamp
        if self._check_existing_xml():
            return True
            
        # Method 3: Manual export instructions
        return self._request_manual_export()
    
    def _try_mpxj_export(self) -> bool:
        """Try using MPXJ library for export"""
        try:
            # This would require MPXJ installation
            # For now, we'll skip this and move to next method
            print("⚠️  MPXJ not available, trying next method...")
            return False
        except Exception:
            return False
    
    def _check_existing_xml(self) -> bool:
        """Check if existing XML is recent enough"""
        try:
            if os.path.exists(self.current_xml):
                xml_mtime = os.path.getmtime(self.current_xml)
                mpp_mtime = os.path.getmtime(self.source_mpp)
                
                # If XML is newer than MPP, we're good
                if xml_mtime >= mpp_mtime:
                    print(f"✅ Existing XML is up to date (newer than .mpp file)")
                    return True
                else:
                    print(f"⚠️  XML is outdated (MPP modified more recently)")
                    return False
            return False
        except Exception:
            return False
    
    def _request_manual_export(self) -> bool:
        """Request manual export as fallback"""
        print(f"\n📋 ONE-TIME SETUP REQUIRED:")
        print(f"We're running in a containerized environment, so direct .mpp access isn't available.")
        print(f"Please do a one-time XML export:")
        print(f"")
        print(f"1. Open: {self.source_mpp}")
        print(f"2. File → Export → Save as XML Format (.xml)")
        print(f"3. Save as: {self.current_xml}")
        print(f"")
        print(f"✨ After this one-time setup:")
        print(f"   • All automation will work perfectly")
        print(f"   • Milestone queries will be instant")
        print(f"   • Progress updates will be seamless")
        print(f"   • PowerPoint automation will work")
        print(f"")
        print(f"💡 TIP: You only need to re-export when you make major changes to your .mpp file")
        
        # Check if user completed manual export
        if os.path.exists(self.current_xml):
            print(f"✅ XML file found! Automation is now fully enabled.")
            return True
        else:
            print(f"⏳ Waiting for XML export to enable automation...")
            return False
    
    def load_project(self, force_sync: bool = False) -> bool:
        """
        Load the current project XML (with auto-sync)
        
        Args:
            force_sync: Force sync from .mpp even if XML exists
            
        Returns:
            bool: True if successful
        """
        # Auto-sync from .mpp file if enabled
        if self.auto_sync_enabled or force_sync:
            if not self.auto_sync_from_mpp():
                print("⚠️  Auto-sync failed, trying to use existing XML...")
        
        if not os.path.exists(self.current_xml):
            print(f"❌ Project XML not found: {self.current_xml}")
            print("Auto-sync failed and no existing XML available")
            return False
            
        self.ms_project = MSProjectIntegration(self.current_xml)
        if not self.ms_project.read_project_file():
            print("❌ Failed to read project XML file")
            return False
            
        print(f"✅ Loaded project: {self.ms_project.project_data.get('title', 'Unknown')}")
        
        # Show sync status
        if os.path.exists(self.source_mpp):
            xml_mtime = os.path.getmtime(self.current_xml)
            mpp_mtime = os.path.getmtime(self.source_mpp)
            if xml_mtime >= mpp_mtime:
                print(f"📅 Data is current (XML sync: {datetime.fromtimestamp(xml_mtime).strftime('%Y-%m-%d %H:%M')})")
            else:
                print(f"⚠️  Data may be outdated (MPP modified: {datetime.fromtimestamp(mpp_mtime).strftime('%Y-%m-%d %H:%M')})")
        
        return True
    
    def query_milestones(self, period: str = "both") -> Dict[str, List]:
        """
        Query milestones for current/next month
        
        Args:
            period: "current", "next", or "both"
            
        Returns:
            Dictionary with milestone lists
        """
        if not self.load_project():
            return {}
            
        today = datetime.now()
        
        # Current month range
        current_month_start = today.replace(day=1)
        current_month_end = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        # Next month range  
        next_month_start = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        next_month_end = (today.replace(day=28) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        results = {}
        
        if period in ["current", "both"]:
            current_milestones = self.ms_project.get_milestones(
                start_date=current_month_start,
                end_date=current_month_end
            )
            results['current_month'] = current_milestones
            
        if period in ["next", "both"]:
            next_milestones = self.ms_project.get_milestones(
                start_date=next_month_start, 
                end_date=next_month_end
            )
            results['next_month'] = next_milestones
            
        return results
    
    def display_milestones(self, milestones_data: Dict[str, List]):
        """Display milestones in a formatted way"""
        
        if 'current_month' in milestones_data:
            print(f"\n📅 MILESTONES THIS MONTH (July 2025):")
            if milestones_data['current_month']:
                for milestone in milestones_data['current_month']:
                    date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                    status_icon = "✅" if milestone['status'] == 'Complete' else "⏳"
                    print(f"  {status_icon} {milestone['name']}")
                    print(f"     Due: {date_str} | Status: {milestone['status']} | Resource: {milestone['resource']}")
            else:
                print("  No milestones found for this month")
                
        if 'next_month' in milestones_data:
            print(f"\n📅 MILESTONES NEXT MONTH (August 2025):")
            if milestones_data['next_month']:
                for milestone in milestones_data['next_month']:
                    date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                    status_icon = "✅" if milestone['status'] == 'Complete' else "⏳"
                    print(f"  {status_icon} {milestone['name']}")
                    print(f"     Due: {date_str} | Status: {milestone['status']} | Resource: {milestone['resource']}")
            else:
                print("  No milestones found for next month")
    
    def update_task_progress(self, task_name: str, progress: int, 
                           actual_start: Optional[str] = None,
                           actual_finish: Optional[str] = None) -> bool:
        """
        Update task progress in the XML (ready for export back to MS Project)
        
        Args:
            task_name: Name of the task to update
            progress: Completion percentage (0-100)
            actual_start: Actual start date (YYYY-MM-DD format)
            actual_finish: Actual finish date (YYYY-MM-DD format)
            
        Returns:
            bool: True if successful
        """
        if not self.load_project():
            return False
            
        # Find task by name
        task_found = False
        for task in self.ms_project.tasks:
            if task_name.lower() in task['name'].lower():
                task_id = task['id']
                
                # Parse dates if provided
                start_date = None
                finish_date = None
                
                if actual_start:
                    try:
                        start_date = datetime.strptime(actual_start, '%Y-%m-%d')
                    except ValueError:
                        print(f"⚠️  Invalid start date format: {actual_start}. Use YYYY-MM-DD")
                        
                if actual_finish:
                    try:
                        finish_date = datetime.strptime(actual_finish, '%Y-%m-%d')
                    except ValueError:
                        print(f"⚠️  Invalid finish date format: {actual_finish}. Use YYYY-MM-DD")
                
                # Update the task
                if self.ms_project.update_task_progress(task_id, progress, start_date, finish_date):
                    print(f"✅ Updated task '{task['name']}' to {progress}% complete")
                    task_found = True
                    break
                    
        if not task_found:
            print(f"❌ Task not found: {task_name}")
            return False
            
        return True
    
    def export_for_ms_project(self) -> bool:
        """
        Export updated XML for import back into MS Project
        
        Returns:
            bool: True if successful
        """
        if not self.load_project():
            return False
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = os.path.join(self.xml_workspace, f"updated_project_{timestamp}.xml")
        
        if self.ms_project.export_updated_xml(export_path):
            print(f"\n📤 EXPORT COMPLETE:")
            print(f"Updated XML saved to: {export_path}")
            print(f"\n📋 TO UPDATE MS PROJECT:")
            print(f"1. Open MS Project")
            print(f"2. Go to: File → Open → {export_path}")
            print(f"3. Choose 'Merge the data' to update existing project")
            print(f"4. Save your .mpp file")
            return True
        else:
            return False
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive project status"""
        if not self.load_project():
            return {}
            
        return self.ms_project.generate_status_report()

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Contract Project Manager for Control Tower')
    parser.add_argument('--action', 
                       choices=['sync', 'milestones', 'update', 'export', 'status', 'force-sync'],
                       required=True,
                       help='Action to perform')
    parser.add_argument('--period', choices=['current', 'next', 'both'], 
                       default='both', help='Period for milestone queries')
    parser.add_argument('--task', help='Task name to update')
    parser.add_argument('--progress', type=int, help='Progress percentage (0-100)')
    parser.add_argument('--start-date', help='Actual start date (YYYY-MM-DD)')
    parser.add_argument('--finish-date', help='Actual finish date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    manager = ContractProjectManager()
    
    if args.action == 'sync':
        # Auto-sync from MS Project
        if manager.auto_sync_from_mpp():
            print("✅ Sync complete! Project data is now current.")
        else:
            print("❌ Sync failed. Check MS Project file accessibility.")
            
    elif args.action == 'force-sync':
        # Force sync even if XML exists
        if manager.load_project(force_sync=True):
            print("✅ Force sync complete!")
        else:
            print("❌ Force sync failed.")
        
    elif args.action == 'milestones':
        # Query and display milestones (auto-sync first)
        milestones = manager.query_milestones(args.period)
        manager.display_milestones(milestones)
        
    elif args.action == 'update':
        # Update task progress
        if not args.task or args.progress is None:
            print("❌ Task name and progress are required for updates")
            print("Example: --action update --task 'Design Review' --progress 75")
            return 1
            
        manager.update_task_progress(args.task, args.progress, args.start_date, args.finish_date)
        
    elif args.action == 'export':
        # Export updated XML
        manager.export_for_ms_project()
        
    elif args.action == 'status':
        # Generate status report
        report = manager.generate_status_report()
        if report:
            print(f"\n📊 {report['project_title']} - STATUS REPORT")
            print(f"Report Date: {report['report_date']}")
            print(f"\n📈 STATISTICS:")
            stats = report['statistics']
            print(f"  • Total Tasks: {stats['total_tasks']}")
            print(f"  • Completed: {stats['completed_tasks']} ({stats['completion_percentage']}%)")
            print(f"  • Overdue: {stats['overdue_tasks']}")
            print(f"\n📅 UPCOMING:")
            print(f"  • Milestones This Month: {len(report['milestones_this_month'])}")
            print(f"  • Milestones Next Month: {len(report['milestones_next_month'])}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
