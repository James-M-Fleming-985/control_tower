#!/usr/bin/env python3
"""
Control Tower Change Management System
=====================================

Interactive change management form system that captures project changes,
documents them for audit trail, and integrates with PowerPoint scope change slides.

Features:
- Terminal-based change request form
- Automatic documentation to CSV/JSON
- Integration with presentation generation
- Approval workflow tracking
- Impact assessment capture
"""

import os
import sys
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ChangeManagementSystem:
    def __init__(self, project_name: str = "ZnNi Line Development Plan-08"):
        self.project_name = project_name
        self.change_log_dir = Path("/workspaces/control_tower/data/change_management")
        self.change_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Change management file paths
        self.changes_csv = self.change_log_dir / f"{project_name.replace(' ', '_')}_changes.csv"
        self.changes_json = self.change_log_dir / f"{project_name.replace(' ', '_')}_changes.json"
        self.presentation_data = self.change_log_dir / f"{project_name.replace(' ', '_')}_presentation_changes.json"
        
        # Initialize CSV if it doesn't exist
        self._initialize_change_log()
    
    def _initialize_change_log(self):
        """Initialize change log CSV with headers if it doesn't exist"""
        if not self.changes_csv.exists():
            headers = [
                'change_id', 'timestamp', 'project_phase', 'change_type', 'requester_name', 
                'requester_role', 'change_description', 'business_justification', 
                'impact_scope', 'impact_timeline', 'impact_budget', 'impact_resources',
                'risk_assessment', 'mitigation_plan', 'approval_status', 'approver_name',
                'implementation_date', 'actual_impact', 'lessons_learned'
            ]
            
            with open(self.changes_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            print(f"✅ Initialized change log: {self.changes_csv}")
    
    def capture_change_request(self, auto_approve: bool = False) -> Dict:
        """
        Interactive terminal form to capture change request details
        
        Args:
            auto_approve: If True, automatically approve for system updates
            
        Returns:
            Dict containing the captured change request
        """
        print("\n" + "="*80)
        print("🔄 CONTROL TOWER CHANGE MANAGEMENT SYSTEM")
        print("="*80)
        print(f"Project: {self.project_name}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Generate unique change ID
        change_id = f"CHG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        change_data = {
            'change_id': change_id,
            'timestamp': datetime.now().isoformat(),
            'project_name': self.project_name
        }
        
        if auto_approve:
            # Pre-fill for automated system changes
            change_data.update({
                'project_phase': 'SF Investment Strategy OEE & OLE Application',
                'change_type': 'Schedule Update',
                'requester_name': 'Control Tower System',
                'requester_role': 'Automated Project Management',
                'change_description': 'XML project schedule integration and MS Project sync',
                'business_justification': 'Automated synchronization of project data between XML and MS Project for reporting accuracy',
                'impact_scope': 'Project schedule and milestone tracking',
                'impact_timeline': 'Immediate - sync operation',
                'impact_budget': 'No budget impact',
                'impact_resources': 'No additional resources required',
                'risk_assessment': 'Low - automated process with existing validation',
                'mitigation_plan': 'Automated backup and rollback capability',
                'approval_status': 'Auto-Approved',
                'approver_name': 'James Fleming (Project Manager)',
                'implementation_date': datetime.now().strftime('%Y-%m-%d'),
                'actual_impact': 'TBD',
                'lessons_learned': 'TBD'
            })
        else:
            # Interactive form for manual changes
            print("\n📋 CHANGE REQUEST DETAILS")
            print("-" * 40)
            
            change_data['project_phase'] = input("1. Project Phase (e.g., Phase 1, Phase 2): ").strip()
            
            print("\nChange Type Options:")
            print("  • Scope Change")
            print("  • Schedule Change") 
            print("  • Resource Change")
            print("  • Budget Change")
            print("  • Technical Change")
            print("  • Risk Mitigation")
            change_data['change_type'] = input("2. Change Type: ").strip()
            
            change_data['requester_name'] = input("3. Your Name: ").strip()
            change_data['requester_role'] = input("4. Your Role: ").strip()
            
            print("\n📝 CHANGE DESCRIPTION")
            print("-" * 40)
            change_data['change_description'] = input("5. Detailed Description of Change: ").strip()
            change_data['business_justification'] = input("6. Business Justification: ").strip()
            
            print("\n📊 IMPACT ASSESSMENT")
            print("-" * 40)
            change_data['impact_scope'] = input("7. Scope Impact: ").strip()
            change_data['impact_timeline'] = input("8. Timeline Impact: ").strip()
            change_data['impact_budget'] = input("9. Budget Impact: ").strip()
            change_data['impact_resources'] = input("10. Resource Impact: ").strip()
            
            print("\n⚠️ RISK ASSESSMENT")
            print("-" * 40)
            change_data['risk_assessment'] = input("11. Risk Assessment: ").strip()
            change_data['mitigation_plan'] = input("12. Risk Mitigation Plan: ").strip()
            
            print("\n✅ APPROVAL")
            print("-" * 40)
            print("Approval Status Options:")
            print("  • Pending")
            print("  • Approved")
            print("  • Rejected")
            print("  • Conditional")
            change_data['approval_status'] = input("13. Approval Status: ").strip()
            change_data['approver_name'] = input("14. Approver Name: ").strip()
            change_data['implementation_date'] = input("15. Implementation Date (YYYY-MM-DD): ").strip()
            
            # Optional fields
            change_data['actual_impact'] = "TBD"
            change_data['lessons_learned'] = "TBD"
        
        # Save the change request
        self._save_change_request(change_data)
        
        print("\n" + "="*80)
        print(f"✅ Change Request {change_id} Captured Successfully")
        print("="*80)
        print(f"📁 Saved to: {self.changes_csv}")
        print(f"📊 PowerPoint data: {self.presentation_data}")
        print("="*80)
        
        return change_data
    
    def _save_change_request(self, change_data: Dict):
        """Save change request to CSV and JSON files"""
        
        # Save to CSV
        with open(self.changes_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=change_data.keys())
            writer.writerow(change_data)
        
        # Save to JSON for easy programmatic access
        json_data = []
        if self.changes_json.exists():
            with open(self.changes_json, 'r', encoding='utf-8') as f:
                try:
                    json_data = json.load(f)
                except:
                    json_data = []
        
        json_data.append(change_data)
        
        with open(self.changes_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # Update presentation data for PowerPoint integration
        self._update_presentation_data(change_data)
    
    def _update_presentation_data(self, change_data: Dict):
        """Update presentation-specific change data for PowerPoint integration"""
        
        # Load existing presentation data
        presentation_changes = []
        if self.presentation_data.exists():
            with open(self.presentation_data, 'r', encoding='utf-8') as f:
                try:
                    presentation_changes = json.load(f)
                except:
                    presentation_changes = []
        
        # Create presentation-friendly entry
        presentation_entry = {
            'change_id': change_data['change_id'],
            'date': change_data['timestamp'][:10],  # Just the date
            'phase': change_data['project_phase'],
            'type': change_data['change_type'],
            'description': change_data['change_description'][:100] + "..." if len(change_data['change_description']) > 100 else change_data['change_description'],
            'impact': f"Scope: {change_data['impact_scope'][:50]}{'...' if len(change_data['impact_scope']) > 50 else ''}",
            'status': change_data['approval_status'],
            'approver': change_data['approver_name']
        }
        
        presentation_changes.append(presentation_entry)
        
        # Keep only last 20 changes for presentation
        presentation_changes = presentation_changes[-20:]
        
        with open(self.presentation_data, 'w', encoding='utf-8') as f:
            json.dump(presentation_changes, f, indent=2, ensure_ascii=False)
    
    def get_changes_for_phase(self, phase: str) -> List[Dict]:
        """Get all changes for a specific project phase"""
        if not self.changes_json.exists():
            return []
        
        with open(self.changes_json, 'r', encoding='utf-8') as f:
            try:
                all_changes = json.load(f)
                return [change for change in all_changes if change.get('project_phase', '').lower() == phase.lower()]
            except:
                return []
    
    def get_recent_changes(self, days: int = 30) -> List[Dict]:
        """Get changes from the last N days"""
        if not self.changes_json.exists():
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with open(self.changes_json, 'r', encoding='utf-8') as f:
            try:
                all_changes = json.load(f)
                recent_changes = []
                
                for change in all_changes:
                    try:
                        change_date = datetime.fromisoformat(change['timestamp'])
                        if change_date >= cutoff_date:
                            recent_changes.append(change)
                    except:
                        continue
                
                return recent_changes
            except:
                return []
    
    def generate_change_summary_report(self) -> str:
        """Generate a summary report of all changes"""
        if not self.changes_json.exists():
            return "No changes recorded."
        
        with open(self.changes_json, 'r', encoding='utf-8') as f:
            try:
                all_changes = json.load(f)
            except:
                return "Error reading change data."
        
        if not all_changes:
            return "No changes recorded."
        
        report = f"\n📊 CHANGE MANAGEMENT SUMMARY - {self.project_name}\n"
        report += "=" * 60 + "\n"
        report += f"Total Changes: {len(all_changes)}\n"
        report += f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Group by status
        status_counts = {}
        for change in all_changes:
            status = change.get('approval_status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        report += "📈 Changes by Status:\n"
        for status, count in status_counts.items():
            report += f"  • {status}: {count}\n"
        
        # Group by type
        type_counts = {}
        for change in all_changes:
            change_type = change.get('change_type', 'Unknown')
            type_counts[change_type] = type_counts.get(change_type, 0) + 1
        
        report += "\n📋 Changes by Type:\n"
        for change_type, count in type_counts.items():
            report += f"  • {change_type}: {count}\n"
        
        # Recent changes
        report += "\n🕒 Recent Changes (Last 5):\n"
        recent_changes = sorted(all_changes, key=lambda x: x['timestamp'], reverse=True)[:5]
        
        for change in recent_changes:
            report += f"  • {change['change_id']} - {change['change_type']} - {change['approval_status']}\n"
            report += f"    {change['change_description'][:80]}{'...' if len(change['change_description']) > 80 else ''}\n"
        
        report += "\n" + "=" * 60 + "\n"
        
        return report
    
    def get_presentation_changes(self, phase: Optional[str] = None) -> List[Dict]:
        """Get changes formatted for PowerPoint presentation"""
        if not self.presentation_data.exists():
            return []
        
        with open(self.presentation_data, 'r', encoding='utf-8') as f:
            try:
                presentation_changes = json.load(f)
                
                if phase:
                    return [change for change in presentation_changes 
                           if change.get('phase', '').lower() == phase.lower()]
                
                return presentation_changes
            except:
                return []

def main():
    """Command line interface for change management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Control Tower Change Management System')
    parser.add_argument('action', choices=['request', 'report', 'phase', 'recent'], 
                       help='Action to perform')
    parser.add_argument('--project', default='ZnNi Line Development Plan-08',
                       help='Project name')
    parser.add_argument('--phase', help='Project phase for filtering')
    parser.add_argument('--days', type=int, default=30, help='Days for recent changes')
    parser.add_argument('--auto-approve', action='store_true',
                       help='Auto-approve change for system updates')
    
    args = parser.parse_args()
    
    cms = ChangeManagementSystem(args.project)
    
    if args.action == 'request':
        change_data = cms.capture_change_request(auto_approve=args.auto_approve)
        return change_data['change_id']
        
    elif args.action == 'report':
        report = cms.generate_change_summary_report()
        print(report)
        
    elif args.action == 'phase':
        if not args.phase:
            print("❌ --phase required for phase action")
            return 1
        
        changes = cms.get_changes_for_phase(args.phase)
        if changes:
            print(f"\n📋 Changes for Phase: {args.phase}")
            print("-" * 40)
            for change in changes:
                print(f"• {change['change_id']} - {change['change_type']} - {change['approval_status']}")
                print(f"  {change['change_description'][:80]}{'...' if len(change['change_description']) > 80 else ''}")
        else:
            print(f"No changes found for phase: {args.phase}")
            
    elif args.action == 'recent':
        from datetime import timedelta
        changes = cms.get_recent_changes(args.days)
        if changes:
            print(f"\n🕒 Recent Changes (Last {args.days} days)")
            print("-" * 40)
            for change in changes:
                print(f"• {change['change_id']} - {change['change_type']} - {change['approval_status']}")
                print(f"  {change['change_description'][:80]}{'...' if len(change['change_description']) > 80 else ''}")
        else:
            print(f"No changes in the last {args.days} days")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
