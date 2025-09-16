#!/usr/bin/env python3
"""
Milestone Change Tracking System
Tracks changes to milestones and risks between presentation updates
"""

import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import hashlib

class MilestoneTracker:
    """Track milestone and risk changes for Safran presentations"""
    
    def __init__(self):
        self.tracking_dir = "/workspaces/control_tower/data/milestone_tracking"
        self.ensure_tracking_directory()
        
    def ensure_tracking_directory(self):
        """Ensure tracking directory exists"""
        os.makedirs(self.tracking_dir, exist_ok=True)
        
    def get_milestone_snapshot_path(self, project_phase: str) -> str:
        """Get file path for milestone snapshot"""
        return f"{self.tracking_dir}/milestones_{project_phase.lower().replace(' ', '_')}.json"
        
    def get_risk_snapshot_path(self) -> str:
        """Get file path for risk snapshot"""
        return f"{self.tracking_dir}/risks_snapshot.json"
        
    def create_milestone_hash(self, milestone: Dict) -> str:
        """Create unique hash for milestone"""
        key_data = f"{milestone.get('name', '')}{milestone.get('date', '')}{milestone.get('status', '')}"
        return hashlib.md5(key_data.encode()).hexdigest()[:12]
        
    def create_risk_hash(self, risk: Dict) -> str:
        """Create unique hash for risk"""
        key_data = f"{risk.get('risk', '')}{risk.get('impact', '')}{risk.get('status', '')}"
        return hashlib.md5(key_data.encode()).hexdigest()[:12]
        
    def save_milestone_snapshot(self, phase_name: str, milestones: List[Dict], project_data: List[Dict] = None):
        """Save current milestone state for comparison"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'phase_name': phase_name,
            'milestones': milestones,
            'project_data': project_data or [],
            'milestone_hashes': [self.create_milestone_hash(m) for m in milestones]
        }
        
        snapshot_path = self.get_milestone_snapshot_path(phase_name)
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
            
    def save_risk_snapshot(self, risks: List[Dict]):
        """Save current risk state for comparison"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'risks': risks,
            'risk_hashes': [self.create_risk_hash(r) for r in risks]
        }
        
        snapshot_path = self.get_risk_snapshot_path()
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
            
    def get_milestone_changes(self, phase_name: str, current_milestones: List[Dict]) -> Dict:
        """Compare current milestones with last snapshot and return changes"""
        snapshot_path = self.get_milestone_snapshot_path(phase_name)
        
        if not os.path.exists(snapshot_path):
            # First time - all milestones are new
            return {
                'new_milestones': current_milestones,
                'modified_milestones': [],
                'completed_milestones': [],
                'removed_milestones': [],
                'status_changes': [],
                'date_changes': [],
                'has_changes': True
            }
            
        try:
            with open(snapshot_path, 'r') as f:
                last_snapshot = json.load(f)
                
            last_milestones = last_snapshot.get('milestones', [])
            last_hashes = set(last_snapshot.get('milestone_hashes', []))
            current_hashes = set(self.create_milestone_hash(m) for m in current_milestones)
            
            # Create lookup dictionaries
            last_by_name = {m.get('name', ''): m for m in last_milestones}
            current_by_name = {m.get('name', ''): m for m in current_milestones}
            
            changes = {
                'new_milestones': [],
                'modified_milestones': [],
                'completed_milestones': [],
                'removed_milestones': [],
                'status_changes': [],
                'date_changes': [],
                'has_changes': False
            }
            
            # Find new milestones
            for milestone in current_milestones:
                milestone_hash = self.create_milestone_hash(milestone)
                if milestone_hash not in last_hashes:
                    milestone_name = milestone.get('name', '')
                    if milestone_name not in last_by_name:
                        changes['new_milestones'].append(milestone)
                    else:
                        # Modified milestone
                        changes['modified_milestones'].append({
                            'old': last_by_name[milestone_name],
                            'new': milestone,
                            'changes': self._get_milestone_field_changes(last_by_name[milestone_name], milestone)
                        })
                        
                        # Track specific change types
                        if (last_by_name[milestone_name].get('status') != milestone.get('status')):
                            changes['status_changes'].append({
                                'milestone': milestone_name,
                                'old_status': last_by_name[milestone_name].get('status'),
                                'new_status': milestone.get('status')
                            })
                            
                        if (last_by_name[milestone_name].get('date') != milestone.get('date')):
                            changes['date_changes'].append({
                                'milestone': milestone_name,
                                'old_date': last_by_name[milestone_name].get('date'),
                                'new_date': milestone.get('date')
                            })
                            
            # Find completed milestones (status changed to Complete)
            for milestone in current_milestones:
                milestone_name = milestone.get('name', '')
                if (milestone_name in last_by_name and 
                    last_by_name[milestone_name].get('status') != 'Complete' and
                    milestone.get('status') == 'Complete'):
                    changes['completed_milestones'].append(milestone)
                    
            # Find removed milestones
            for milestone in last_milestones:
                milestone_name = milestone.get('name', '')
                if milestone_name not in current_by_name:
                    changes['removed_milestones'].append(milestone)
                    
            # Determine if there are any changes
            changes['has_changes'] = (
                len(changes['new_milestones']) > 0 or
                len(changes['modified_milestones']) > 0 or
                len(changes['completed_milestones']) > 0 or
                len(changes['removed_milestones']) > 0
            )
            
            return changes
            
        except Exception as e:
            print(f"Error comparing milestone snapshots: {e}")
            return {
                'new_milestones': current_milestones,
                'modified_milestones': [],
                'completed_milestones': [],
                'removed_milestones': [],
                'status_changes': [],
                'date_changes': [],
                'has_changes': True
            }
            
    def get_risk_changes(self, current_risks: List[Dict]) -> Dict:
        """Compare current risks with last snapshot and return changes"""
        snapshot_path = self.get_risk_snapshot_path()
        
        if not os.path.exists(snapshot_path):
            # First time - all risks are new
            return {
                'new_risks': current_risks,
                'modified_risks': [],
                'resolved_risks': [],
                'removed_risks': [],
                'impact_changes': [],
                'has_changes': True
            }
            
        try:
            with open(snapshot_path, 'r') as f:
                last_snapshot = json.load(f)
                
            last_risks = last_snapshot.get('risks', [])
            last_hashes = set(last_snapshot.get('risk_hashes', []))
            current_hashes = set(self.create_risk_hash(r) for r in current_risks)
            
            # Create lookup dictionaries
            last_by_description = {r.get('risk', ''): r for r in last_risks}
            current_by_description = {r.get('risk', ''): r for r in current_risks}
            
            changes = {
                'new_risks': [],
                'modified_risks': [],
                'resolved_risks': [],
                'removed_risks': [],
                'impact_changes': [],
                'has_changes': False
            }
            
            # Find new risks
            for risk in current_risks:
                risk_hash = self.create_risk_hash(risk)
                if risk_hash not in last_hashes:
                    risk_description = risk.get('risk', '')
                    if risk_description not in last_by_description:
                        changes['new_risks'].append(risk)
                    else:
                        # Modified risk
                        changes['modified_risks'].append({
                            'old': last_by_description[risk_description],
                            'new': risk,
                            'changes': self._get_risk_field_changes(last_by_description[risk_description], risk)
                        })
                        
                        # Track impact changes
                        if (last_by_description[risk_description].get('impact') != risk.get('impact')):
                            changes['impact_changes'].append({
                                'risk': risk_description,
                                'old_impact': last_by_description[risk_description].get('impact'),
                                'new_impact': risk.get('impact')
                            })
                            
            # Find resolved risks (status changed to Resolved/Closed)
            for risk in current_risks:
                risk_description = risk.get('risk', '')
                if (risk_description in last_by_description and 
                    last_by_description[risk_description].get('status', '').lower() not in ['resolved', 'closed'] and
                    risk.get('status', '').lower() in ['resolved', 'closed']):
                    changes['resolved_risks'].append(risk)
                    
            # Find removed risks
            for risk in last_risks:
                risk_description = risk.get('risk', '')
                if risk_description not in current_by_description:
                    changes['removed_risks'].append(risk)
                    
            # Determine if there are any changes
            changes['has_changes'] = (
                len(changes['new_risks']) > 0 or
                len(changes['modified_risks']) > 0 or
                len(changes['resolved_risks']) > 0 or
                len(changes['removed_risks']) > 0
            )
            
            return changes
            
        except Exception as e:
            print(f"Error comparing risk snapshots: {e}")
            return {
                'new_risks': current_risks,
                'modified_risks': [],
                'resolved_risks': [],
                'removed_risks': [],
                'impact_changes': [],
                'has_changes': True
            }
            
    def _get_milestone_field_changes(self, old_milestone: Dict, new_milestone: Dict) -> List[str]:
        """Get list of changed fields in milestone"""
        changes = []
        fields_to_check = ['name', 'date', 'status', 'progress', 'owner']
        
        for field in fields_to_check:
            if old_milestone.get(field) != new_milestone.get(field):
                changes.append(f"{field}: {old_milestone.get(field)} → {new_milestone.get(field)}")
                
        return changes
        
    def _get_risk_field_changes(self, old_risk: Dict, new_risk: Dict) -> List[str]:
        """Get list of changed fields in risk"""
        changes = []
        fields_to_check = ['risk', 'impact', 'probability', 'mitigation', 'status', 'owner']
        
        for field in fields_to_check:
            if old_risk.get(field) != new_risk.get(field):
                changes.append(f"{field}: {old_risk.get(field)} → {new_risk.get(field)}")
                
        return changes
        
    def get_summary_for_presentation(self, phase_name: str, current_milestones: List[Dict], current_risks: List[Dict]) -> Dict:
        """Get summary of changes for presentation update"""
        milestone_changes = self.get_milestone_changes(phase_name, current_milestones)
        risk_changes = self.get_risk_changes(current_risks)
        
        return {
            'milestone_changes': milestone_changes,
            'risk_changes': risk_changes,
            'requires_update': milestone_changes['has_changes'] or risk_changes['has_changes'],
            'summary': {
                'new_milestones_count': len(milestone_changes['new_milestones']),
                'completed_milestones_count': len(milestone_changes['completed_milestones']),
                'modified_milestones_count': len(milestone_changes['modified_milestones']),
                'new_risks_count': len(risk_changes['new_risks']),
                'resolved_risks_count': len(risk_changes['resolved_risks']),
                'modified_risks_count': len(risk_changes['modified_risks'])
            }
        }
        
    def update_snapshots(self, phase_name: str, milestones: List[Dict], risks: List[Dict], project_data: List[Dict] = None):
        """Update both milestone and risk snapshots"""
        self.save_milestone_snapshot(phase_name, milestones, project_data)
        self.save_risk_snapshot(risks)


if __name__ == "__main__":
    # Test the tracking system
    tracker = MilestoneTracker()
    
    # Sample milestone data
    test_milestones = [
        {'name': 'Phase 1 Kickoff', 'date': '2025-08-01', 'status': 'Complete'},
        {'name': 'Data Architecture Setup', 'date': '2025-08-15', 'status': 'In Progress'},
        {'name': 'UI Framework', 'date': '2025-08-30', 'status': 'Planned'}
    ]
    
    # Sample risk data
    test_risks = [
        {'risk': 'Resource availability', 'impact': 'High', 'status': 'Open'},
        {'risk': 'Technical complexity', 'impact': 'Medium', 'status': 'Open'}
    ]
    
    # Get changes (will be empty first time)
    changes = tracker.get_summary_for_presentation("Phase 1", test_milestones, test_risks)
    print(f"Changes detected: {changes['requires_update']}")
    print(f"Summary: {changes['summary']}")
    
    # Save snapshot
    tracker.update_snapshots("Phase 1", test_milestones, test_risks)
    print("Snapshot saved successfully")
