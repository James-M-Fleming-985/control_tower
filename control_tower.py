#!/usr/bin/env python3
"""
Control Tower Main Entry Point
Unified command interface for all Control Tower functionality
"""

import sys
import argparse
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def main():
    """Main entry point with unified command interface"""
    parser = argparse.ArgumentParser(description='Control Tower - Project Management Hub')
    subparsers = parser.add_subparsers(dest='system', help='Available systems')
    
    # MS Project System
    ms_parser = subparsers.add_parser('ms-project', help='MS Project integration commands')
    ms_parser.add_argument('--action', 
                          choices=['sync', 'milestones', 'update', 'export', 'status', 'force-sync', 'overdue', 'reports'],
                          required=True,
                          help='Action to perform')
    ms_parser.add_argument('--period', choices=['current', 'next', 'both'], 
                          default='both', help='Period for milestone queries')
    ms_parser.add_argument('--limit', type=int, default=20, help='Limit for overdue tasks')
    ms_parser.add_argument('--task', help='Task name to update')
    ms_parser.add_argument('--progress', type=int, help='Progress percentage (0-100)')
    ms_parser.add_argument('--start-date', help='Actual start date (YYYY-MM-DD)')
    ms_parser.add_argument('--finish-date', help='Actual finish date (YYYY-MM-DD)')
    
    # CSV System
    csv_parser = subparsers.add_parser('csv', help='CSV system commands')
    csv_parser.add_argument('action', 
                           choices=['today', 'week', 'overdue', 'milestones', 'status', 'tasks'],
                           help='Query to run')
    csv_parser.add_argument('--person', help='Person name for task filtering')
    csv_parser.add_argument('--project', help='Project filter')
    csv_parser.add_argument('--days', type=int, default=30, help='Days ahead for milestones')
    
    # Utilities
    util_parser = subparsers.add_parser('util', help='Utility commands')
    util_parser.add_argument('action',
                            choices=['help', 'demo', 'organize', 'roadmap'],
                            help='Utility to run')
    
    args = parser.parse_args()
    
    if not args.system:
        parser.print_help()
        return 1
    
    # Route to appropriate system
    if args.system == 'ms-project':
        return run_ms_project_commands(args)
    elif args.system == 'csv':
        return run_csv_commands(args)
    elif args.system == 'util':
        return run_utility_commands(args)
    
    return 0

def run_ms_project_commands(args):
    """Run MS Project system commands"""
    try:
        from modules.ms_project.contract_project_manager import ContractProjectManager
        
        manager = ContractProjectManager()
        
        if args.action == 'sync':
            if manager.auto_sync_from_mpp():
                print("✅ Sync complete! Project data is now current.")
                return 0
            else:
                print("❌ Sync failed. Check MS Project file accessibility.")
                return 1
                
        elif args.action == 'force-sync':
            if manager.load_project(force_sync=True):
                print("✅ Force sync complete!")
                return 0
            else:
                print("❌ Force sync failed.")
                return 1
            
        elif args.action == 'milestones':
            milestones = manager.query_milestones(args.period)
            manager.display_milestones(milestones)
            return 0
            
        elif args.action == 'update':
            if not args.task or args.progress is None:
                print("❌ Task name and progress are required for updates")
                print("Example: --action update --task 'Design Review' --progress 75")
                return 1
                
            if manager.update_task_progress(args.task, args.progress, args.start_date, args.finish_date):
                return 0
            else:
                return 1
                
        elif args.action == 'export':
            if manager.export_for_ms_project():
                return 0
            else:
                return 1
                
        elif args.action == 'status':
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
            else:
                return 1
        
        elif args.action == 'overdue':
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
            return 0
        
        elif args.action == 'reports':
            manager.reporting.show_query_stats()
            print(f"\n📁 Find all reports in: /workspaces/control_tower/reporting/")
            print(f"📋 Reusable commands in: control_tower_commands.md")
            return 0
                
    except ImportError as e:
        print(f"❌ MS Project module not available: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error running MS Project command: {e}")
        return 1

def run_csv_commands(args):
    """Run CSV system commands"""
    try:
        # Import CSV system functions
        sys.path.append('modules/csv_system')
        from modules.csv_system.quick_query import (
            whats_due_today, whats_due_this_week, show_overdue, 
            show_milestones, show_my_tasks, show_project_status
        )
        
        if args.action == 'today':
            whats_due_today()
        elif args.action == 'week':
            whats_due_this_week()
        elif args.action == 'overdue':
            show_overdue()
        elif args.action == 'milestones':
            show_milestones(args.days)
        elif args.action == 'tasks' and args.person:
            show_my_tasks(args.person)
        elif args.action == 'status':
            show_project_status(args.project or "")
        else:
            print("❌ Invalid CSV command or missing required arguments")
            return 1
            
        return 0
        
    except ImportError as e:
        print(f"❌ CSV system module not available: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error running CSV command: {e}")
        return 1

def run_utility_commands(args):
    """Run utility commands"""
    if args.action == 'help':
        os.system('bash scripts/control_tower_help.sh')
        return 0
    elif args.action == 'demo':
        os.system('bash scripts/demo.sh')
        return 0
    elif args.action == 'organize':
        print("📁 Control Tower is already organized!")
        print("Structure:")
        print("  📂 modules/ms_project/ - MS Project integration")
        print("  📂 modules/csv_system/ - Legacy CSV system")
        print("  📂 scripts/ - Helper scripts")
        print("  📂 docs/ - Documentation")
        print("  📂 utils/ - Utilities")
        return 0
    elif args.action == 'roadmap':
        try:
            from utils.roadmap_manager import main as roadmap_main
            return roadmap_main()
        except ImportError:
            print("❌ Roadmap manager not available")
            return 1
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
