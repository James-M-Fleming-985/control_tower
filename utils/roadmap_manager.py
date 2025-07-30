#!/usr/bin/env python3
"""
Control Tower Development Workflow Manager
Helps track features, issues, and development progress
"""

import os
import json
import datetime
from datetime import datetime, timedelta
import argparse

def load_roadmap_data():
    """Load roadmap tracking data"""
    roadmap_file = "development_tracking.json"
    
    if os.path.exists(roadmap_file):
        with open(roadmap_file, 'r') as f:
            return json.load(f)
    else:
        # Initialize default structure
        return {
            "current_version": "0.3",
            "features": {},
            "issues": {},
            "sprints": {},
            "metrics": {
                "features_completed": 0,
                "bugs_fixed": 0,
                "development_hours": 0
            }
        }

def save_roadmap_data(data):
    """Save roadmap tracking data"""
    with open("development_tracking.json", 'w') as f:
        json.dump(data, f, indent=2, default=str)

def add_feature(name, description, priority="Medium", estimated_hours=8):
    """Add a new feature to track"""
    data = load_roadmap_data()
    
    feature_id = f"FEAT-{len(data['features']) + 1:03d}"
    
    data['features'][feature_id] = {
        "name": name,
        "description": description,
        "priority": priority,
        "estimated_hours": estimated_hours,
        "status": "Planned",
        "created_date": datetime.now(),
        "assigned_to": "James Fleming",
        "completed_date": None,
        "actual_hours": 0,
        "notes": []
    }
    
    save_roadmap_data(data)
    print(f"✅ Added feature {feature_id}: {name}")
    return feature_id

def add_issue(title, description, priority="Medium", issue_type="Bug"):
    """Add a new issue to track"""
    data = load_roadmap_data()
    
    issue_id = f"CTRL-{len(data['issues']) + 1:03d}"
    
    data['issues'][issue_id] = {
        "title": title,
        "description": description,
        "priority": priority,
        "type": issue_type,  # Bug, Enhancement, Task
        "status": "Open",
        "created_date": datetime.now(),
        "assigned_to": "James Fleming",
        "resolved_date": None,
        "resolution": None,
        "time_spent": 0,
        "notes": []
    }
    
    save_roadmap_data(data)
    print(f"🐛 Added issue {issue_id}: {title}")
    return issue_id

def update_feature_status(feature_id, status, notes=None, hours_spent=0):
    """Update feature status"""
    data = load_roadmap_data()
    
    if feature_id not in data['features']:
        print(f"❌ Feature {feature_id} not found")
        return
    
    feature = data['features'][feature_id]
    old_status = feature['status']
    feature['status'] = status
    feature['actual_hours'] += hours_spent
    
    if notes:
        feature['notes'].append({
            "date": datetime.now(),
            "note": notes
        })
    
    if status == "Completed" and old_status != "Completed":
        feature['completed_date'] = datetime.now()
        data['metrics']['features_completed'] += 1
    
    data['metrics']['development_hours'] += hours_spent
    
    save_roadmap_data(data)
    print(f"✅ Updated {feature_id} status: {old_status} → {status}")
    
    if hours_spent > 0:
        print(f"⏱️ Added {hours_spent} hours (Total: {feature['actual_hours']}h)")

def resolve_issue(issue_id, resolution, hours_spent=0):
    """Resolve an issue"""
    data = load_roadmap_data()
    
    if issue_id not in data['issues']:
        print(f"❌ Issue {issue_id} not found")
        return
    
    issue = data['issues'][issue_id]
    issue['status'] = "Resolved"
    issue['resolution'] = resolution
    issue['resolved_date'] = datetime.now()
    issue['time_spent'] = hours_spent
    
    data['metrics']['bugs_fixed'] += 1
    data['metrics']['development_hours'] += hours_spent
    
    save_roadmap_data(data)
    print(f"✅ Resolved {issue_id}: {resolution}")

def show_status():
    """Show current development status"""
    data = load_roadmap_data()
    
    print("🏗️ CONTROL TOWER DEVELOPMENT STATUS")
    print("=" * 50)
    print(f"Current Version: {data['current_version']}")
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Metrics
    metrics = data['metrics']
    print(f"\n📊 METRICS")
    print(f"Features Completed: {metrics['features_completed']}")
    print(f"Bugs Fixed: {metrics['bugs_fixed']}")
    print(f"Development Hours: {metrics['development_hours']}")
    
    # Active Features
    print(f"\n🚀 ACTIVE FEATURES")
    active_features = {k: v for k, v in data['features'].items() 
                      if v['status'] in ['In Progress', 'Testing']}
    
    if active_features:
        for feat_id, feature in active_features.items():
            status_emoji = "🔄" if feature['status'] == "In Progress" else "🧪"
            print(f"{status_emoji} {feat_id}: {feature['name']}")
            print(f"   Priority: {feature['priority']} | Hours: {feature['actual_hours']}/{feature['estimated_hours']}")
    else:
        print("No active features")
    
    # Open Issues
    print(f"\n🐛 OPEN ISSUES")
    open_issues = {k: v for k, v in data['issues'].items() 
                  if v['status'] == 'Open'}
    
    if open_issues:
        for issue_id, issue in open_issues.items():
            priority_emoji = "🔴" if issue['priority'] == "High" else "🟡" if issue['priority'] == "Medium" else "🟢"
            print(f"{priority_emoji} {issue_id}: {issue['title']}")
            print(f"   Type: {issue['type']} | Priority: {issue['priority']}")
    else:
        print("No open issues")
    
    # Completed Recently
    print(f"\n✅ RECENTLY COMPLETED")
    recent_features = []
    week_ago = datetime.now() - timedelta(days=7)
    
    for feat_id, feature in data['features'].items():
        if (feature['status'] == 'Completed' and 
            feature.get('completed_date') and 
            datetime.fromisoformat(str(feature['completed_date'])) > week_ago):
            recent_features.append((feat_id, feature))
    
    if recent_features:
        for feat_id, feature in recent_features[-5:]:  # Last 5
            print(f"✅ {feat_id}: {feature['name']}")
    else:
        print("No features completed this week")

def generate_sprint_report():
    """Generate sprint progress report"""
    data = load_roadmap_data()
    
    # Calculate sprint metrics
    sprint_start = datetime.now() - timedelta(days=14)  # 2-week sprint
    
    sprint_features = []
    sprint_issues = []
    
    for feat_id, feature in data['features'].items():
        created = datetime.fromisoformat(str(feature['created_date']))
        if created > sprint_start or feature['status'] in ['In Progress', 'Testing']:
            sprint_features.append((feat_id, feature))
    
    for issue_id, issue in data['issues'].items():
        created = datetime.fromisoformat(str(issue['created_date']))
        if created > sprint_start or issue['status'] == 'Open':
            sprint_issues.append((issue_id, issue))
    
    # Generate report
    report = f"# 🏃‍♂️ SPRINT REPORT\n"
    report += f"**Period**: {sprint_start.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    report += f"## 📊 Sprint Metrics\n"
    report += f"- Features in sprint: {len(sprint_features)}\n"
    report += f"- Issues addressed: {len(sprint_issues)}\n"
    report += f"- Development hours this sprint: {sum(f[1]['actual_hours'] for f in sprint_features)}\n\n"
    
    report += f"## 🚀 Sprint Features\n"
    for feat_id, feature in sprint_features:
        status_emoji = {"Planned": "📋", "In Progress": "🔄", "Testing": "🧪", "Completed": "✅"}
        emoji = status_emoji.get(feature['status'], "❓")
        report += f"- {emoji} **{feat_id}**: {feature['name']} ({feature['status']})\n"
    
    report += f"\n## 🐛 Sprint Issues\n"
    for issue_id, issue in sprint_issues:
        status_emoji = {"Open": "🔓", "In Progress": "🔄", "Resolved": "✅"}
        emoji = status_emoji.get(issue['status'], "❓")
        report += f"- {emoji} **{issue_id}**: {issue['title']} ({issue['status']})\n"
    
    # Save report
    report_file = f"todos/{datetime.now().strftime('%Y%m%d')}_sprint_report.md"
    os.makedirs('todos', exist_ok=True)
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Sprint report saved: {report_file}")

def main():
    parser = argparse.ArgumentParser(description='Control Tower Development Workflow Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add feature
    add_feat_parser = subparsers.add_parser('add-feature', help='Add a new feature')
    add_feat_parser.add_argument('name', help='Feature name')
    add_feat_parser.add_argument('description', help='Feature description')
    add_feat_parser.add_argument('--priority', choices=['Low', 'Medium', 'High'], default='Medium')
    add_feat_parser.add_argument('--hours', type=int, default=8, help='Estimated hours')
    
    # Add issue
    add_issue_parser = subparsers.add_parser('add-issue', help='Add a new issue')
    add_issue_parser.add_argument('title', help='Issue title')
    add_issue_parser.add_argument('description', help='Issue description')
    add_issue_parser.add_argument('--priority', choices=['Low', 'Medium', 'High'], default='Medium')
    add_issue_parser.add_argument('--type', choices=['Bug', 'Enhancement', 'Task'], default='Bug')
    
    # Update feature
    update_parser = subparsers.add_parser('update-feature', help='Update feature status')
    update_parser.add_argument('feature_id', help='Feature ID (e.g., FEAT-001)')
    update_parser.add_argument('status', choices=['Planned', 'In Progress', 'Testing', 'Completed'])
    update_parser.add_argument('--notes', help='Update notes')
    update_parser.add_argument('--hours', type=int, default=0, help='Hours spent')
    
    # Resolve issue
    resolve_parser = subparsers.add_parser('resolve-issue', help='Resolve an issue')
    resolve_parser.add_argument('issue_id', help='Issue ID (e.g., CTRL-001)')
    resolve_parser.add_argument('resolution', help='Resolution description')
    resolve_parser.add_argument('--hours', type=int, default=0, help='Hours spent')
    
    # Status
    subparsers.add_parser('status', help='Show development status')
    
    # Sprint report
    subparsers.add_parser('sprint', help='Generate sprint report')
    
    args = parser.parse_args()
    
    if args.command == 'add-feature':
        add_feature(args.name, args.description, args.priority, args.hours)
    elif args.command == 'add-issue':
        add_issue(args.title, args.description, args.priority, args.type)
    elif args.command == 'update-feature':
        update_feature_status(args.feature_id, args.status, args.notes, args.hours)
    elif args.command == 'resolve-issue':
        resolve_issue(args.issue_id, args.resolution, args.hours)
    elif args.command == 'status':
        show_status()
    elif args.command == 'sprint':
        generate_sprint_report()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
