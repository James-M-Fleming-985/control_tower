#!/usr/bin/env python3
"""
Temporary make what-next fix for discovering TDD workflow automation feature

This is a simple workaround to test if the TDD feature can be discovered
while the full make what-next command has import issues from the code reorganization.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re

def scan_for_requirements():
    """Scan for requirements documents in the projects directory"""
    projects_dir = Path("/workspaces/control_tower/projects")
    requirements_files = []
    
    if not projects_dir.exists():
        print("❌ Projects directory not found")
        return []
    
    # Look for requirements documents
    for md_file in projects_dir.rglob("*.md"):
        if any(keyword in md_file.name.lower() for keyword in ["requirement", "feature", "project", "system"]):
            requirements_files.append(md_file)
    
    return requirements_files

def parse_timeline_from_file(file_path):
    """Extract timeline information from a requirements document"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for timeline information
        start_date_match = re.search(r'Start Date.*?(\d{4}-\d{2}-\d{2})', content)
        due_date_match = re.search(r'Due Date.*?(\d{4}-\d{2}-\d{2})', content)
        progress_match = re.search(r'Progress.*?(\d+)%', content)
        
        return {
            'start_date': start_date_match.group(1) if start_date_match else None,
            'due_date': due_date_match.group(1) if due_date_match else None,
            'progress': int(progress_match.group(1)) if progress_match else 0,
            'content': content[:500]  # First 500 chars for context
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    print("🔍 Control Tower Work Discovery (Temporary Fix)")
    print("=" * 50)
    
    # Find requirements files
    requirements_files = scan_for_requirements()
    
    if not requirements_files:
        print("❌ No requirements documents found")
        return
    
    print(f"📁 Found {len(requirements_files)} requirements documents")
    print()
    
    # Focus on TDD workflow automation
    tdd_features = []
    today = datetime.now().date()
    
    for req_file in requirements_files:
        if "tdd" in req_file.name.lower() or "workflow" in req_file.name.lower():
            timeline = parse_timeline_from_file(req_file)
            
            if timeline.get('due_date'):
                try:
                    due_date = datetime.strptime(timeline['due_date'], '%Y-%m-%d').date()
                    days_until_due = (due_date - today).days
                    
                    tdd_features.append({
                        'file': req_file,
                        'timeline': timeline,
                        'days_until_due': days_until_due
                    })
                except:
                    pass
    
    # Sort by urgency (due date)
    tdd_features.sort(key=lambda x: x['days_until_due'])
    
    if tdd_features:
        print("🎯 TDD WORKFLOW AUTOMATION FEATURES FOUND:")
        print("-" * 40)
        
        for feature in tdd_features:
            file_path = feature['file']
            timeline = feature['timeline']
            days = feature['days_until_due']
            
            # Determine urgency
            if days < 0:
                urgency = "🔴 OVERDUE"
            elif days <= 3:
                urgency = "🟡 DUE SOON"
            else:
                urgency = "🟢 ON TRACK"
            
            print(f"{urgency}")
            print(f"📋 File: {file_path.name}")
            print(f"📅 Due: {timeline['due_date']} ({days} days)")
            print(f"📊 Progress: {timeline['progress']}%")
            print(f"📁 Location: {file_path.parent.name}")
            print()
    else:
        print("❌ No TDD workflow automation features found with timeline information")
        
        # Show all requirements files for debugging
        print("\n🔍 All requirements files found:")
        for req_file in requirements_files[:10]:  # Show first 10
            print(f"  📄 {req_file.relative_to(Path('/workspaces/control_tower'))}")

if __name__ == "__main__":
    main()