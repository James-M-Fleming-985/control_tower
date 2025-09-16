#!/usr/bin/env python3
"""
Universal Milestone Change Detector for Control Tower
Detects milestone changes across all repositories with MS Project XML files

This detector:
1. Scans all repositories for MS Project XML files
2. Compares current milestones with previous snapshots
3. Prompts for business context when changes detected
4. Stores change records for cross-project reporting
5. Supports repository-specific project phases
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pickle
from pathlib import Path

# Add Control Tower modules to path
sys.path.append("/workspaces/control_tower")
from modules.ms_project.ms_project_integration import MSProjectIntegration
from .repository_scanner import RepositoryScanner

class MilestoneChangeDetector:
    """
    Detects and manages milestone changes across all repositories
    """
    
    def __init__(self, data_path: str = "/workspaces/control_tower/data/milestone_management"):
        """
        Initialize the change detector
        
        Args:
            data_path: Base path for storing change detection data
        """
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.scanner = RepositoryScanner()
        
        # Repository-specific project phases (can be extended per project)
        self.default_phases = {
            "planning": ["Planning", "Initiation", "Requirements", "Design"],
            "implementation": ["Development", "Construction", "Installation", "Configuration"],
            "testing": ["Testing", "Validation", "Verification", "Commissioning"],
            "deployment": ["Deployment", "Go-Live", "Launch", "Production"],
            "optimization": ["Optimization", "Enhancement", "Continuous Improvement"]
        }
    
    def scan_all_repositories_for_changes(self) -> Dict[str, List[Dict]]:
        """
        Scan all repositories for milestone changes
        
        Returns:
            Dictionary mapping repository names to lists of changes
        """
        print("🔍 SCANNING ALL REPOSITORIES FOR MILESTONE CHANGES")
        print("="*60)
        
        all_changes = {}
        repositories = self.scanner.scan_all_repositories()
        
        for repo_name, repo_info in repositories.items():
            print(f"\n📂 Checking repository: {repo_name}")
            repo_changes = []
            
            for xml_file in repo_info['xml_files']:
                print(f"   📄 Analyzing: {Path(xml_file).name}")
                changes = self.detect_changes_in_file(xml_file, repo_name)
                repo_changes.extend(changes)
            
            if repo_changes:
                all_changes[repo_name] = repo_changes
                print(f"   ✅ Found {len(repo_changes)} changes in {repo_name}")
            else:
                print(f"   ✅ No changes detected in {repo_name}")
        
        total_changes = sum(len(changes) for changes in all_changes.values())
        print(f"\n📊 TOTAL CHANGES DETECTED: {total_changes}")
        
        return all_changes
    
    def detect_changes_in_file(self, xml_file_path: str, repository_name: str) -> List[Dict]:
        """
        Detect changes in a specific XML file
        
        Args:
            xml_file_path: Path to the XML file
            repository_name: Name of the repository
            
        Returns:
            List of detected changes
        """
        try:
            # Create unique identifiers for this file
            file_name = Path(xml_file_path).stem
            snapshot_file = self.data_path / f"{repository_name}_{file_name}_snapshot.pkl"
            change_log_file = self.data_path / f"{repository_name}_{file_name}_changes.json"
            
            # Load MS Project data
            ms_project = MSProjectIntegration(xml_file_path)
            if not ms_project.read_project_file():
                print(f"❌ Failed to read XML file: {xml_file_path}")
                return []
            
            # Extract current milestones
            current_milestones = self._extract_milestones(ms_project)
            
            # Load previous snapshot
            previous_milestones = self._load_snapshot(snapshot_file)
            
            # Detect changes
            changes = []
            if previous_milestones is not None:
                changes = self._compare_milestones(previous_milestones, current_milestones, repository_name, file_name)
            else:
                print(f"   📝 Creating baseline snapshot for {file_name}")
            
            # Save current snapshot
            self._save_snapshot(current_milestones, snapshot_file)
            
            # Process changes with user input if any detected
            if changes:
                changes = self._process_changes_with_user_input(changes, repository_name, file_name)
                self._save_changes_to_log(changes, change_log_file)
            
            return changes
            
        except Exception as e:
            print(f"❌ Error detecting changes in {xml_file_path}: {e}")
            return []
    
    def _extract_milestones(self, ms_project: MSProjectIntegration) -> Dict[str, Dict]:
        """Extract milestone data from MS Project"""
        milestones = {}
        
        for task in ms_project.tasks:
            if task.get('is_milestone', False):
                milestone_uid = task['uid']
                milestones[milestone_uid] = {
                    'uid': milestone_uid,
                    'name': task['name'],
                    'finish_date': task.get('finish'),
                    'start_date': task.get('start'),
                    'resource_names': task.get('resource_names', 'Not assigned'),
                    'percent_complete': task.get('percent_complete', 0),
                    'notes': task.get('notes', ''),
                    'extracted_at': datetime.now().isoformat()
                }
        
        return milestones
    
    def _load_snapshot(self, snapshot_file: Path) -> Optional[Dict]:
        """Load previous milestone snapshot"""
        try:
            if snapshot_file.exists():
                with open(snapshot_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"⚠️ Error loading snapshot: {e}")
        return None
    
    def _save_snapshot(self, milestones: Dict, snapshot_file: Path) -> None:
        """Save current milestone snapshot"""
        try:
            with open(snapshot_file, 'wb') as f:
                pickle.dump(milestones, f)
        except Exception as e:
            print(f"❌ Error saving snapshot: {e}")
    
    def _compare_milestones(self, previous: Dict, current: Dict, repo_name: str, file_name: str) -> List[Dict]:
        """Compare milestone snapshots and detect changes"""
        changes = []
        
        # Check for new milestones
        for uid, milestone in current.items():
            if uid not in previous:
                changes.append({
                    'type': 'milestone_added',
                    'repository': repo_name,
                    'file_name': file_name,
                    'milestone_uid': uid,
                    'milestone_name': milestone['name'],
                    'new_data': milestone,
                    'detected_at': datetime.now().isoformat()
                })
        
        # Check for removed milestones
        for uid, milestone in previous.items():
            if uid not in current:
                changes.append({
                    'type': 'milestone_removed',
                    'repository': repo_name,
                    'file_name': file_name,
                    'milestone_uid': uid,
                    'milestone_name': milestone['name'],
                    'old_data': milestone,
                    'detected_at': datetime.now().isoformat()
                })
        
        # Check for modified milestones
        for uid in set(previous.keys()) & set(current.keys()):
            old_milestone = previous[uid]
            new_milestone = current[uid]
            
            # Check specific fields for changes
            fields_to_check = ['name', 'finish_date', 'start_date', 'resource_names', 'percent_complete']
            
            for field in fields_to_check:
                if old_milestone.get(field) != new_milestone.get(field):
                    changes.append({
                        'type': f'{field}_changed',
                        'repository': repo_name,
                        'file_name': file_name,
                        'milestone_uid': uid,
                        'milestone_name': new_milestone['name'],
                        'field_changed': field,
                        'old_value': old_milestone.get(field),
                        'new_value': new_milestone.get(field),
                        'detected_at': datetime.now().isoformat()
                    })
        
        return changes
    
    def _process_changes_with_user_input(self, changes: List[Dict], repo_name: str, file_name: str) -> List[Dict]:
        """Process changes and collect business context from user"""
        
        print(f"\n🔔 CHANGES DETECTED in {repo_name}/{file_name}")
        print("="*50)
        
        for i, change in enumerate(changes, 1):
            print(f"\n📋 CHANGE {i}/{len(changes)}:")
            print(f"   Type: {change['type'].replace('_', ' ').title()}")
            print(f"   Milestone: {change['milestone_name']}")
            
            if 'old_value' in change and 'new_value' in change:
                print(f"   Field: {change['field_changed']}")
                print(f"   Old: {change['old_value']}")
                print(f"   New: {change['new_value']}")
            
            # Collect business context
            try:
                reason = input("\n💬 Why did this change occur? (business reason): ").strip()
                contingency = input("🔧 Any contingency or mitigation needed?: ").strip()
                phase = self._categorize_milestone_phase(change['milestone_name'])
                
                # Add business context to change record
                change.update({
                    'business_reason': reason or "No reason provided",
                    'contingency_plan': contingency or "No contingency specified",
                    'project_phase': phase,
                    'processed_by': 'user_input',
                    'processed_at': datetime.now().isoformat()
                })
                
            except KeyboardInterrupt:
                print("\n⏹️ User cancelled input - saving changes without additional context")
                change.update({
                    'business_reason': "Change detection interrupted",
                    'contingency_plan': "Review required",
                    'project_phase': 'unknown',
                    'processed_by': 'system',
                    'processed_at': datetime.now().isoformat()
                })
        
        return changes
    
    def _categorize_milestone_phase(self, milestone_name: str) -> str:
        """Categorize milestone into project phase based on name"""
        milestone_lower = milestone_name.lower()
        
        for phase, keywords in self.default_phases.items():
            for keyword in keywords:
                if keyword.lower() in milestone_lower:
                    return phase
        
        return 'general'
    
    def _save_changes_to_log(self, changes: List[Dict], log_file: Path) -> None:
        """Save changes to JSON log file"""
        try:
            # Load existing log
            existing_changes = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    existing_changes = json.load(f)
            
            # Add new changes
            existing_changes.extend(changes)
            
            # Save updated log
            with open(log_file, 'w') as f:
                json.dump(existing_changes, f, indent=2)
                
            print(f"✅ Saved {len(changes)} changes to {log_file}")
            
        except Exception as e:
            print(f"❌ Error saving changes: {e}")
    
    def get_all_changes_summary(self) -> Dict[str, Any]:
        """Get summary of all changes across all repositories"""
        summary = {
            'total_repositories': 0,
            'total_files': 0,
            'total_changes': 0,
            'changes_by_repository': {},
            'changes_by_type': {},
            'recent_changes': [],
            'generated_at': datetime.now().isoformat()
        }
        
        # Scan all change log files
        for log_file in self.data_path.glob("*_changes.json"):
            try:
                with open(log_file, 'r') as f:
                    changes = json.load(f)
                
                if changes:
                    repo_name = changes[0]['repository']
                    summary['changes_by_repository'][repo_name] = len(changes)
                    summary['total_changes'] += len(changes)
                    
                    # Count by type
                    for change in changes:
                        change_type = change['type']
                        summary['changes_by_type'][change_type] = summary['changes_by_type'].get(change_type, 0) + 1
                    
                    # Add recent changes (last 10)
                    recent = sorted(changes, key=lambda x: x['detected_at'], reverse=True)[:10]
                    summary['recent_changes'].extend(recent)
            
            except Exception as e:
                print(f"⚠️ Error reading {log_file}: {e}")
        
        # Sort recent changes
        summary['recent_changes'] = sorted(
            summary['recent_changes'], 
            key=lambda x: x['detected_at'], 
            reverse=True
        )[:20]  # Keep top 20 most recent
        
        summary['total_repositories'] = len(summary['changes_by_repository'])
        
        return summary

def main():
    """Main function for command line usage"""
    print("🚀 CONTROL TOWER MILESTONE CHANGE DETECTOR")
    print("="*60)
    
    detector = MilestoneChangeDetector()
    
    # Scan all repositories
    all_changes = detector.scan_all_repositories_for_changes()
    
    if all_changes:
        print(f"\n📊 CHANGE SUMMARY:")
        for repo_name, changes in all_changes.items():
            print(f"   📂 {repo_name}: {len(changes)} changes")
        
        print(f"\n📋 DETAILED SUMMARY:")
        summary = detector.get_all_changes_summary()
        print(f"   Total changes: {summary['total_changes']}")
        print(f"   Repositories affected: {summary['total_repositories']}")
        
        if summary['changes_by_type']:
            print(f"   Change types:")
            for change_type, count in summary['changes_by_type'].items():
                print(f"      • {change_type.replace('_', ' ').title()}: {count}")
    else:
        print("\n✅ No changes detected across all repositories")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   • Use PowerPoint generator for cross-project reporting")
    print(f"   • Set up automated workflows for each repository")
    print(f"   • Review change logs for business context")

if __name__ == "__main__":
    main()
