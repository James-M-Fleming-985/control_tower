#!/usr/bin/env python3
"""
Control Tower Milestone Management CLI
Universal command-line interface for milestone management across all repositories

Usage:
    python -m modules.milestone_management.cli scan       # Scan all repositories
    python -m modules.milestone_management.cli detect     # Detect changes
    python -m modules.milestone_management.cli report     # Generate reports
    python -m modules.milestone_management.cli monitor    # Start monitoring
    python -m modules.milestone_management.cli status     # System status
"""

import sys
import argparse
from pathlib import Path

# Add Control Tower to path
sys.path.append("/workspaces/control_tower")

from modules.milestone_management import (
    RepositoryScanner, 
    MilestoneChangeDetector,
    PowerPointGenerator,
    WorkflowManager
)

def scan_repositories():
    """Scan all repositories for XML files"""
    print("🔍 SCANNING ALL REPOSITORIES")
    print("="*40)
    
    scanner = RepositoryScanner()
    repositories = scanner.scan_all_repositories()
    
    if repositories:
        print(f"✅ Found XML files in {len(repositories)} repositories:")
        for repo_name, repo_info in repositories.items():
            print(f"   📂 {repo_name}: {len(repo_info['xml_files'])} XML files")
    else:
        print("❌ No XML files found in any repository")

def detect_changes():
    """Detect milestone changes across all repositories"""
    print("🔍 DETECTING MILESTONE CHANGES")
    print("="*40)
    
    detector = MilestoneChangeDetector()
    all_changes = detector.scan_all_repositories_for_changes()
    
    if all_changes:
        total_changes = sum(len(changes) for changes in all_changes.values())
        print(f"✅ Detected {total_changes} changes across {len(all_changes)} repositories")
        
        for repo_name, changes in all_changes.items():
            print(f"\n📂 {repo_name}:")
            for change in changes[:3]:  # Show first 3
                print(f"   • {change['type'].replace('_', ' ').title()}: {change['milestone_name'][:50]}...")
            if len(changes) > 3:
                print(f"   ... and {len(changes) - 3} more changes")
    else:
        print("✅ No changes detected across all repositories")

def generate_reports():
    """Generate PowerPoint reports"""
    print("📊 GENERATING POWERPOINT REPORTS")
    print("="*40)
    
    generator = PowerPointGenerator()
    
    # Generate cross-project report
    cross_project_path = generator.generate_cross_project_report()
    if cross_project_path:
        print(f"✅ Cross-project report: {cross_project_path}")
    
    # Optionally generate repository-specific reports
    scanner = RepositoryScanner()
    repositories = scanner.scan_all_repositories()
    
    for repo_name in repositories.keys():
        repo_path = generator.generate_repository_report(repo_name)
        if repo_path:
            print(f"✅ {repo_name} report: {repo_path}")

def start_monitoring():
    """Start automated monitoring"""
    print("👁️ STARTING AUTOMATED MONITORING")
    print("="*40)
    
    manager = WorkflowManager()
    manager.start_automated_monitoring()

def show_status():
    """Show system status"""
    print("📊 SYSTEM STATUS")
    print("="*40)
    
    manager = WorkflowManager()
    status = manager.get_system_status()
    
    print(f"Repositories: {status['monitoring']['monitored_repositories']}")
    print(f"XML files: {status['monitoring']['monitored_files']}")
    print(f"Monitoring: {'Active' if status['monitoring']['active'] else 'Inactive'}")
    print(f"Total changes: {status['changes']['total_changes']}")
    
    if status['changes']['changes_by_type']:
        print("\nChange types:")
        for change_type, count in status['changes']['changes_by_type'].items():
            print(f"  • {change_type.replace('_', ' ').title()}: {count}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Control Tower Milestone Management',
        epilog='Examples:\n'
               '  %(prog)s scan     # Scan all repositories\n'
               '  %(prog)s detect   # Detect changes\n'
               '  %(prog)s report   # Generate reports\n'
               '  %(prog)s monitor  # Start monitoring\n'
               '  %(prog)s status   # Show status',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command',
        choices=['scan', 'detect', 'report', 'monitor', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--repository',
        help='Target specific repository (for applicable commands)'
    )
    
    args = parser.parse_args()
    
    print("🚀 CONTROL TOWER MILESTONE MANAGEMENT")
    print("="*50)
    
    try:
        if args.command == 'scan':
            scan_repositories()
        elif args.command == 'detect':
            detect_changes()
        elif args.command == 'report':
            generate_reports()
        elif args.command == 'monitor':
            start_monitoring()
        elif args.command == 'status':
            show_status()
    
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
