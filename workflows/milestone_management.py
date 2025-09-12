#!/usr/bin/env python3
"""
Control Tower Milestone Management
Main entry point for milestone management across all repositories

This provides a simple interface to the comprehensive milestone management system
that works across all Control Tower repositories.
"""

import os
import sys

# Add Control Tower to path
sys.path.append("/workspaces/control_tower")

from modules.milestone_management.automation.workflow_manager import WorkflowManager

def main():
    """Simple main interface"""
    
    print("🚀 CONTROL TOWER MILESTONE MANAGEMENT")
    print("="*60)
    print("Universal milestone change detection and reporting")
    print("Works across all repositories with MS Project XML files")
    print("="*60)
    
    manager = WorkflowManager()
    
    print("\nWhat would you like to do?")
    print("1. 👁️  Start automated monitoring (watches all XML files)")
    print("2. 🔍 Run manual scan (detect changes now)")
    print("3. 📊 Generate PowerPoint reports")
    print("4. 📋 System status")
    print("5. 🛠️  Install dependencies")
    print("6. ❌ Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                print("\n👁️ Starting automated monitoring...")
                manager.start_automated_monitoring()
                
            elif choice == '2':
                print("\n🔍 Running manual scan...")
                changes = manager.run_manual_scan()
                
                if any(changes.values()):
                    total_changes = sum(len(c) for c in changes.values())
                    print(f"\n✅ Scan complete! Found {total_changes} changes")
                else:
                    print("\n✅ Scan complete! No changes detected")
                
            elif choice == '3':
                print("\n📊 Generating PowerPoint reports...")
                # Generate reports through workflow manager
                manager._generate_reports_for_changes({})
                print("✅ Reports generated!")
                
            elif choice == '4':
                print("\n📋 System Status:")
                status = manager.get_system_status()
                print(f"   Repositories: {status['monitoring']['monitored_repositories']}")
                print(f"   XML files: {status['monitoring']['monitored_files']}")
                print(f"   Total changes recorded: {status['changes']['total_changes']}")
                print(f"   Monitoring active: {'Yes' if status['monitoring']['active'] else 'No'}")
                
            elif choice == '5':
                print("\n🛠️ Installing dependencies...")
                if manager.install_dependencies():
                    print("✅ Dependencies installed! Restart to use automated monitoring.")
                else:
                    print("❌ Failed to install some dependencies")
                
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
