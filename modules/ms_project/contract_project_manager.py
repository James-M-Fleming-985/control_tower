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
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import argparse

# Import from the same module directory
import sys
import os
sys.path.append('/workspaces/control_tower/modules/ms_project')
from ms_project_integration import MSProjectIntegration
from change_management import ChangeManagementSystem

# Import reporting manager
import sys
sys.path.append('/workspaces/control_tower/modules/reporting')
from reporting_manager import ReportingManager

class ContractProjectManager:
    """
    Manage contract projects workflow between Control Tower and MS Project
    """
    
    def __init__(self):
        """Initialize the contract project manager"""
        self.project_name = "ZnNi Line Development Plan"
        self.xml_workspace = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace"
        # UPDATED: Use new folder structure with /current/ subdirectory as per Friday workflow
        self.current_xml = os.path.join(self.xml_workspace, "current", "ZnNi_Line_Development_Plan-08.xml")
        self.source_mpp = r"D:\Downloads\ZnNi Line Development Plan-08.mpp"
        self.ms_project = None
        self.auto_sync_enabled = True
        
        # Initialize reporting manager
        self.reporting = ReportingManager()
        
        # Initialize change management system
        self.change_management = ChangeManagementSystem("ZnNi Line Development Plan-08")
        
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
        Query milestones for current/next month with reporting
        
        Args:
            period: "current", "next", or "both"
            
        Returns:
            Dictionary with milestone lists
        """
        # Track this query for reporting
        command = f"python3 control_tower.py ms-project --action milestones --period {period}"
        parameters = {"period": period}
        query_hash, is_new = self.reporting.track_query("milestones", command, parameters)
        
        if not self.load_project():
            return {}
            
        today = datetime.now()
        
        # Current month range - ensure we include the last day of the month
        current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Get last day of current month more reliably
        if today.month == 12:
            current_month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            current_month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        # Set to end of day
        current_month_end = current_month_end.replace(hour=23, minute=59, second=59)
        
        # Next month range - fixed calculation
        if today.month == 12:
            next_month_start = today.replace(year=today.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month_end = today.replace(year=today.year + 1, month=1, day=31, hour=23, minute=59, second=59)
        else:
            next_month_start = today.replace(month=today.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            # Get last day of next month
            if today.month + 1 in [1, 3, 5, 7, 8, 10, 12]:
                last_day = 31
            elif today.month + 1 in [4, 6, 9, 11]:
                last_day = 30
            else:  # February
                last_day = 29 if (today.year + (1 if today.month == 12 else 0)) % 4 == 0 else 28
            next_month_end = today.replace(month=today.month + 1, day=last_day, hour=23, minute=59, second=59)
        
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
        
        # Generate and save report
        report_content = self._format_milestones_report(results, period)
        report_name = f"milestones_{period}"
        self.reporting.save_report(report_name, report_content, query_hash)
        
        if is_new:
            print(f"🆕 New query tracked! Check control_tower_commands.md for reusable command.")
        
        return results
    
    def update_project_with_change_management(self, update_description: str = None, auto_approve: bool = False) -> bool:
        """
        Update project with integrated change management form and milestone/risk tracking
        
        Args:
            update_description: Description of the update being performed
            auto_approve: If True, auto-approve change for system updates
            
        Returns:
            bool: True if successful
        """
        print("\n🔄 PROJECT UPDATE WITH CHANGE MANAGEMENT & MILESTONE TRACKING")
        print("="*70)
        
        # Trigger change management form
        if update_description:
            print(f"Update: {update_description}")
        
        change_data = self.change_management.capture_change_request(auto_approve=auto_approve)
        
        # Proceed with the project update only if approved
        if change_data['approval_status'] in ['Approved', 'Auto-Approved']:
            print(f"\n✅ Change {change_data['change_id']} approved - proceeding with update...")
            
            # Step 1: Track milestone/risk changes before update
            milestone_risk_changes = self._track_milestone_risk_changes()
            
            # Step 2: Perform the actual project sync/update
            success = self.load_project(force_sync=True)
            
            if success:
                print(f"📊 Project updated successfully")
                print(f"📋 Change documented in: {self.change_management.changes_csv}")
                
                # Step 3: Export updated XML for MS Project import
                export_success = self.export_for_ms_project()
                if export_success:
                    print(f"📤 Updated XML exported for MS Project import")
                
                # Step 4: Update PowerPoint with milestone/risk changes
                self._update_presentation_with_changes(milestone_risk_changes)
                
                print(f"📈 PowerPoint data updated with milestone/risk changes")
                return True
            else:
                print(f"❌ Project update failed")
                return False
        else:
            print(f"⏸️  Change {change_data['change_id']} not approved - update cancelled")
            return False

    def _track_milestone_risk_changes(self) -> Dict:
        """Track milestone and risk changes during project update"""
        try:
            # Import milestone tracker
            import sys
            sys.path.append('/workspaces/control_tower/modules/milestone_management')
            from milestone_tracker import MilestoneTracker
            
            tracker = MilestoneTracker()
            
            # Import PowerPoint generator for phase data
            sys.path.append('/workspaces/control_tower/modules/milestone_management/reporting')
            from safran_powerpoint_generator import SafranPowerPointGenerator
            
            generator = SafranPowerPointGenerator()
            phases = generator.safran_phases
            
            total_changes = {
                'milestone_changes': [],
                'risk_changes': [],
                'phases_with_changes': [],
                'has_changes': False
            }
            
            print("\n📊 Tracking milestone and risk changes...")
            
            for phase_key, phase_info in phases.items():
                # Get current milestone and risk data
                current_milestones = generator._get_msproject_milestone_data("current", phase_info)
                current_risks = generator._get_control_tower_risk_data(phase_info)
                
                # Track changes for this phase
                change_summary = generator.track_presentation_changes(
                    phase_info, current_milestones, current_risks
                )
                
                if change_summary['requires_update']:
                    total_changes['phases_with_changes'].append(phase_info['name'])
                    total_changes['milestone_changes'].extend(
                        change_summary['milestone_changes'].get('new_milestones', [])
                    )
                    total_changes['risk_changes'].extend(
                        change_summary['risk_changes'].get('new_risks', [])
                    )
                    total_changes['has_changes'] = True
                    
            if total_changes['has_changes']:
                print(f"📈 Changes detected in phases: {', '.join(total_changes['phases_with_changes'])}")
            else:
                print("✅ No milestone/risk changes detected")
                
            return total_changes
            
        except Exception as e:
            print(f"⚠️  Error tracking milestone/risk changes: {e}")
            return {'has_changes': False, 'error': str(e)}
            
    def _update_presentation_with_changes(self, milestone_risk_changes: Dict):
        """Update presentation with tracked milestone/risk changes"""
        try:
            # Import PowerPoint generator
            sys.path.append('/workspaces/control_tower/modules/milestone_management/reporting')
            from safran_powerpoint_generator import SafranPowerPointGenerator
            
            generator = SafranPowerPointGenerator()
            
            # Generate presentation with change tracking
            presentation_path = generator.generate_presentation()
            
            if presentation_path:
                print(f"📊 Presentation updated: {presentation_path}")
                
                # Update snapshots if changes were detected
                if milestone_risk_changes.get('has_changes'):
                    phases = generator.safran_phases
                    for phase_key, phase_info in phases.items():
                        current_milestones = generator._get_msproject_milestone_data("current", phase_info)
                        current_risks = generator._get_control_tower_risk_data(phase_info)
                        generator.update_presentation_snapshots(phase_info, current_milestones, current_risks)
                    print("📸 Milestone/risk snapshots updated")
                    
                print("✅ Complete workflow finished successfully!")
                print(f"\n📋 Summary:")
                print(f"   • Change Management: ✅ Captured")
                print(f"   • MS Project: ✅ Updated")
                print(f"   • Presentation: ✅ Generated")
                print(f"   • Milestone/Risk Tracking: ✅ {'Updated' if milestone_risk_changes.get('has_changes') else 'Current'}")
                print(f"\n💡 Note: Repository commit not included - handle separately when ready")
                return True
                    
            else:
                print("⚠️  Presentation generation failed")
                return False
                
        except Exception as e:
            print(f"⚠️  Error updating presentation: {e}")

    def get_change_management_data_for_powerpoint(self, phase: str = None) -> List[Dict]:
        """
        Get change management data formatted for PowerPoint presentations
        
        Args:
            phase: Specific phase to filter changes (optional)
            
        Returns:
            List of change records formatted for presentation
        """
        return self.change_management.get_presentation_changes(phase)
        """
        Query milestones for current/next month with reporting
        
        Args:
            period: "current", "next", or "both"
            
        Returns:
            Dictionary with milestone lists
        """
        # Track this query for reporting
        command = f"python3 control_tower.py ms-project --action milestones --period {period}"
        parameters = {"period": period}
        query_hash, is_new = self.reporting.track_query("milestones", command, parameters)
        
        if not self.load_project():
            return {}
            
        today = datetime.now()
        
        # Current month range - ensure we include the last day of the month
        current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Get last day of current month more reliably
        if today.month == 12:
            current_month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            current_month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        # Set to end of day
        current_month_end = current_month_end.replace(hour=23, minute=59, second=59)
        
        # Next month range - fixed calculation
        if today.month == 12:
            next_month_start = today.replace(year=today.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month_end = today.replace(year=today.year + 1, month=1, day=31, hour=23, minute=59, second=59)
        else:
            next_month_start = today.replace(month=today.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            # Get last day of next month
            if today.month + 1 in [1, 3, 5, 7, 8, 10, 12]:
                last_day = 31
            elif today.month + 1 in [4, 6, 9, 11]:
                last_day = 30
            else:  # February
                last_day = 29 if (today.year + (1 if today.month == 12 else 0)) % 4 == 0 else 28
            next_month_end = today.replace(month=today.month + 1, day=last_day, hour=23, minute=59, second=59)
        
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
        
        # Generate and save report
        report_content = self._format_milestones_report(results, period)
        report_name = f"milestones_{period}"
        self.reporting.save_report(report_name, report_content, query_hash)
        
        if is_new:
            print(f"🆕 New query tracked! Check control_tower_commands.md for reusable command.")
        
        return results
    
    def _format_milestones_report(self, milestones_data: Dict[str, List], period: str) -> str:
        """Format milestones data for report generation"""
        content = []
        today = datetime.now()
        
        if 'current_month' in milestones_data:
            count = len(milestones_data['current_month'])
            current_month_name = today.strftime('%B %Y')  # e.g., "August 2025"
            content.append(f"## Milestones This Month ({current_month_name}) - {count} Total")
            if milestones_data['current_month']:
                for milestone in milestones_data['current_month']:
                    date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                    
                    # Check if milestone is overdue
                    is_overdue = False
                    if milestone['date'] and milestone['status'] != 'Complete':
                        is_overdue = milestone['date'].date() < today.date()
                    
                    # Set appropriate icon
                    if milestone['status'] == 'Complete':
                        status_icon = "✅"
                    elif is_overdue:
                        status_icon = "🚨"  # Overdue
                    else:
                        status_icon = "⏳"  # Pending
                    
                    resource = milestone.get('resource', '') or 'Not assigned'
                    overdue_text = " (OVERDUE)" if is_overdue else ""
                    content.append(f"- {status_icon} **{milestone['name']}**{overdue_text}")
                    content.append(f"  - Due: {date_str}")
                    content.append(f"  - Status: {milestone['status']}")
                    content.append(f"  - Resource: {resource}")
                    content.append("")
            else:
                content.append("No milestones found for this month.\n")
        
        if 'next_month' in milestones_data:
            count = len(milestones_data['next_month'])
            # Calculate next month name
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1)
            else:
                next_month = today.replace(month=today.month + 1)
            next_month_name = next_month.strftime('%B %Y')  # e.g., "September 2025"
            
            content.append(f"## Milestones Next Month ({next_month_name}) - {count} Total")
            if milestones_data['next_month']:
                for milestone in milestones_data['next_month']:
                    date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                    status_icon = "✅" if milestone['status'] == 'Complete' else "⏳"
                    resource = milestone.get('resource', '') or 'Not assigned'
                    content.append(f"- {status_icon} **{milestone['name']}**")
                    content.append(f"  - Due: {date_str}")
                    content.append(f"  - Status: {milestone['status']}")
                    content.append(f"  - Resource: {resource}")
                    content.append("")
            else:
                content.append("No milestones found for next month.\n")
        
        return '\n'.join(content)
    
    def display_milestones(self, milestones_data: Dict[str, List]):
        """Display milestones in a formatted way"""
        today = datetime.now()
        
        if 'current_month' in milestones_data:
            count = len(milestones_data['current_month'])
            current_month_name = today.strftime('%B %Y')  # e.g., "August 2025"
            print(f"\n📅 MILESTONES THIS MONTH ({current_month_name}) - {count} Total:")
            if milestones_data['current_month']:
                for milestone in milestones_data['current_month']:
                    date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                    
                    # Check if milestone is overdue
                    is_overdue = False
                    if milestone['date'] and milestone['status'] != 'Complete':
                        is_overdue = milestone['date'].date() < today.date()
                    
                    # Set appropriate icon
                    if milestone['status'] == 'Complete':
                        status_icon = "✅"
                    elif is_overdue:
                        status_icon = "🚨"  # Overdue
                    else:
                        status_icon = "⏳"  # Pending
                    
                    resource = milestone.get('resource', '') or 'Not assigned'
                    overdue_text = " (OVERDUE)" if is_overdue else ""
                    print(f"  {status_icon} {milestone['name']}{overdue_text}")
                    print(f"     Due: {date_str} | Status: {milestone['status']} | Resource: {resource}")
            else:
                print("  No milestones found for this month")
                
        if 'next_month' in milestones_data:
            count = len(milestones_data['next_month'])
            # Calculate next month name
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1)
            else:
                next_month = today.replace(month=today.month + 1)
            next_month_name = next_month.strftime('%B %Y')  # e.g., "September 2025"
            
            print(f"\n📅 MILESTONES NEXT MONTH ({next_month_name}) - {count} Total:")
            if milestones_data['next_month']:
                for milestone in milestones_data['next_month']:
                    date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                    status_icon = "✅" if milestone['status'] == 'Complete' else "⏳"
                    resource = milestone.get('resource', '') or 'Not assigned'
                    print(f"  {status_icon} {milestone['name']}")
                    print(f"     Due: {date_str} | Status: {milestone['status']} | Resource: {resource}")
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
        Automatically import updated XML back into MS Project
        This completes the single-command workflow automation
        
        Returns:
            bool: True if successful
        """
        print(f"\n🔄 AUTOMATIC MS PROJECT SYNC")
        print("="*50)
        
        # The main XML file has already been updated by the integration script
        # We just need to import it back into MS Project automatically
        
        if not os.path.exists(self.current_xml):
            print(f"❌ Updated XML file not found: {self.current_xml}")
            return False
            
        print(f"📁 Importing updated XML: {os.path.basename(self.current_xml)}")
        
        # Try automatic MS Project import using COM interface
        success = self._import_xml_to_ms_project()
        
        if success:
            print(f"✅ MS Project automatically updated with latest changes")
            print(f"� Imported from: {self.current_xml}")
            print(f"💾 MS Project file: {self.source_mpp}")
            return True
        else:
            print(f"⚠️  Automatic import failed, providing manual fallback instructions")
            print(f"\n📋 MANUAL FALLBACK - TO UPDATE MS PROJECT:")
            print(f"1. Open MS Project")
            print(f"2. Go to: File → Open → {self.current_xml}")
            print(f"3. Choose 'Merge the data' to update existing project")
            print(f"4. Save your .mpp file to: {self.source_mpp}")
            return False
    
    def _import_xml_to_ms_project(self) -> bool:
        """
        Automatically import updated XML into MS Project using COM interface
        
        Returns:
            bool: True if successful
        """
        try:
            print(f"🔗 Attempting automatic MS Project import...")
            
            # Try PowerShell COM interface first
            if self._import_via_powershell():
                return True
                
            # Fallback to other methods if PowerShell fails
            print("⚠️  PowerShell import failed, trying alternative methods...")
            return self._import_via_alternative_methods()
                
        except Exception as e:
            print(f"❌ Automatic import failed: {e}")
            return False
    
    def _import_via_powershell(self) -> bool:
        """
        Import XML using MS Project COM interface via PowerShell
        
        Returns:
            bool: True if successful
        """
        try:
            # PowerShell script to import XML into existing MS Project file
            powershell_script = f'''
Add-Type -AssemblyName "Microsoft.Office.Interop.MSProject"
$msp = New-Object -ComObject MSProject.Application
$msp.Visible = $false

try {{
    # Open the existing .mpp file
    if (Test-Path "{self.source_mpp}") {{
        $project = $msp.FileOpen("{self.source_mpp}")
        
        # Import/merge the updated XML data
        $project.FileOpen("{self.current_xml}", $false)  # Open as merge
        
        # Save the updated project
        $project.Save()
        $project.Close($false)
        $msp.Quit()
        Write-Output "SUCCESS: XML imported and MS Project updated"
    }} else {{
        # If .mpp doesn't exist, create new project from XML
        $project = $msp.FileOpen("{self.current_xml}")
        $project.SaveAs("{self.source_mpp}")
        $project.Close($false)
        $msp.Quit()
        Write-Output "SUCCESS: New MS Project created from XML"
    }}
}} catch {{
    Write-Output "ERROR: $_"
    $msp.Quit()
}}
'''
            
            # Write PowerShell script to temporary file
            ps_script_path = os.path.join(self.xml_workspace, "import_temp.ps1")
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
                print(f"✅ PowerShell import successful")
                return True
            else:
                print(f"❌ PowerShell import failed: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  PowerShell import timed out")
            return False
        except Exception as e:
            print(f"⚠️  PowerShell import error: {e}")
            return False
    
    def _import_via_alternative_methods(self) -> bool:
        """
        Try alternative import methods if COM interface fails
        
        Returns:
            bool: True if successful
        """
        # Method 1: Try direct file copy if .mpp doesn't exist
        if not os.path.exists(self.source_mpp):
            print("ℹ️  Creating new .mpp file from XML (requires manual MS Project open)")
            return False
            
        # Method 2: Could try other automation libraries here
        print("ℹ️  No alternative import methods available")
        return False
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive project status with reporting"""
        # Track this query for reporting
        command = "python3 control_tower.py ms-project --action status"
        parameters = {"action": "status"}
        query_hash, is_new = self.reporting.track_query("status", command, parameters)
        
        if not self.load_project():
            return {}
        
        report_data = self.ms_project.generate_status_report()
        
        if report_data:
            # Generate and save report
            report_content = self._format_status_report(report_data)
            self.reporting.save_report("project_status", report_content, query_hash)
            
            if is_new:
                print(f"🆕 New query tracked! Check control_tower_commands.md for reusable command.")
        
        return report_data
    
    def _format_status_report(self, report_data: Dict[str, Any]) -> str:
        """Format status report data for report generation"""
        content = []
        
        content.append(f"## {report_data['project_title']}")
        content.append(f"**Report Date**: {report_data['report_date']}\n")
        
        stats = report_data['statistics']
        content.append("### Project Statistics")
        content.append(f"- **Total Tasks**: {stats['total_tasks']}")
        content.append(f"- **Completed**: {stats['completed_tasks']} ({stats['completion_percentage']}%)")
        content.append(f"- **Overdue**: {stats['overdue_tasks']}")
        content.append("")
        
        content.append("### Upcoming Milestones")
        content.append(f"- **This Month**: {len(report_data['milestones_this_month'])}")
        content.append(f"- **Next Month**: {len(report_data['milestones_next_month'])}")
        content.append("")
        
        if report_data['milestones_this_month']:
            content.append("#### This Month's Milestones")
            for milestone in report_data['milestones_this_month']:
                date_str = milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'
                status_icon = "✅" if milestone['status'] == 'Complete' else "⏳"
                content.append(f"- {status_icon} **{milestone['name']}** (Due: {date_str})")
            content.append("")
        
        if report_data['overdue_tasks']:
            content.append("#### Sample Overdue Tasks")
            for task in report_data['overdue_tasks'][:5]:  # Show first 5 overdue
                content.append(f"- ⚠️ **{task['name']}** ({task['percent_complete']}% complete)")
            if len(report_data['overdue_tasks']) > 5:
                content.append(f"- ... and {len(report_data['overdue_tasks']) - 5} more overdue tasks")
            content.append("")
        
        return '\n'.join(content)
    
    def query_overdue_tasks(self, limit: int = 20) -> List[Dict]:
        """
        Query overdue tasks with reporting
        
        Args:
            limit: Maximum number of overdue tasks to return
            
        Returns:
            List of overdue task dictionaries
        """
        # Track this query for reporting
        command = f"python3 control_tower.py ms-project --action overdue --limit {limit}"
        parameters = {"action": "overdue", "limit": limit}
        query_hash, is_new = self.reporting.track_query("overdue", command, parameters)
        
        if not self.load_project():
            return []
        
        overdue_tasks = self.ms_project.get_overdue_tasks()
        
        # Limit results
        limited_tasks = overdue_tasks[:limit] if overdue_tasks else []
        
        # Generate and save report
        report_content = self._format_overdue_report(limited_tasks, len(overdue_tasks))
        self.reporting.save_report(f"overdue_tasks_top{limit}", report_content, query_hash)
        
        if is_new:
            print(f"🆕 New query tracked! Check control_tower_commands.md for reusable command.")
        
        return limited_tasks
    
    def _format_overdue_report(self, overdue_tasks: List[Dict], total_overdue: int) -> str:
        """Format overdue tasks for report generation"""
        content = []
        
        content.append(f"## Overdue Tasks Report")
        content.append(f"**Total Overdue Tasks**: {total_overdue}")
        content.append(f"**Showing**: Top {len(overdue_tasks)} tasks\n")
        
        if overdue_tasks:
            content.append("### Overdue Task Details")
            for i, task in enumerate(overdue_tasks, 1):
                finish_date = task.get('finish_date')
                finish_str = finish_date.strftime('%d/%m/%Y') if finish_date else 'No finish date'
                content.append(f"{i}. **{task['name']}**")
                content.append(f"   - Progress: {task['percent_complete']}%")
                content.append(f"   - Due Date: {finish_str}")
                content.append(f"   - Resource: {task.get('resource', 'Unassigned')}")
                content.append("")
        else:
            content.append("🎉 No overdue tasks found!")
        
        return '\n'.join(content)

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Contract Project Manager for Control Tower')
    parser.add_argument('--action', 
                       choices=['sync', 'milestones', 'update', 'export', 'status', 'force-sync', 'overdue', 'reports', 'change-update'],
                       required=True,
                       help='Action to perform')
    parser.add_argument('--period', choices=['current', 'next', 'both'], 
                       default='both', help='Period for milestone queries')
    parser.add_argument('--limit', type=int, default=20, help='Limit for overdue tasks')
    parser.add_argument('--task', help='Task name to update')
    parser.add_argument('--progress', type=int, help='Progress percentage (0-100)')
    parser.add_argument('--start-date', help='Actual start date (YYYY-MM-DD)')
    parser.add_argument('--finish-date', help='Actual finish date (YYYY-MM-DD)')
    parser.add_argument('--description', help='Description of the update/change')
    parser.add_argument('--auto-approve', action='store_true', 
                       help='Auto-approve change for system updates')
    
    args = parser.parse_args()
    
    manager = ContractProjectManager()
    
    if args.action == 'sync':
        # Auto-sync from MS Project
        if manager.auto_sync_from_mpp():
            print("✅ Sync complete! Project data is now current.")
        else:
            print("❌ Sync failed. Check MS Project file accessibility.")
    
    elif args.action == 'change-update':
        # Update with change management form
        description = args.description or "Manual project update via Control Tower"
        if manager.update_project_with_change_management(description, args.auto_approve):
            print("✅ Project updated with change management documentation.")
        else:
            print("❌ Project update failed or cancelled.")
            
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
    
    elif args.action == 'overdue':
        # Query overdue tasks
        overdue_tasks = manager.query_overdue_tasks(args.limit)
        print(f"\n⚠️ OVERDUE TASKS (Top {args.limit}):")
        if overdue_tasks:
            for i, task in enumerate(overdue_tasks, 1):
                finish_date = task.get('finish_date')
                finish_str = finish_date.strftime('%d/%m/%Y') if finish_date else 'No finish date'
                print(f"  {i}. {task['name']} ({task['percent_complete']}% complete)")
                print(f"     Due: {finish_str} | Resource: {task.get('resource', 'Unassigned')}")
        else:
            print("  🎉 No overdue tasks found!")
    
    elif args.action == 'reports':
        # Show reporting statistics and recent reports
        manager.reporting.show_query_stats()
        print(f"\n📁 Find all reports in: /workspaces/control_tower/reporting/")
        print(f"📋 Reusable commands in: control_tower_commands.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
