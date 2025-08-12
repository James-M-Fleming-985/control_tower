#!/usr/bin/env python3
"""
Enhanced Auto-Sync for Control Tower
====================================

Automatically fetches the latest XML from Windows MS Project machine
before running milestone reports, eliminating manual export steps.

Usage:
    python enhanced_sync.py --auto-fetch-and-report current
    python enhanced_sync.py --fetch-only
    python enhanced_sync.py --report-only current
"""

import argparse
import subprocess
import os
import sys
import configparser
import shutil
from datetime import datetime
from pathlib import Path

class EnhancedSync:
    def __init__(self):
        """Initialize the enhanced sync system"""
        self.config = self._load_config()
        self.local_xml_path = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
        
    def _load_config(self):
        """Load Windows machine configuration"""
        config_path = "/workspaces/control_tower/config/windows_target.conf"
        
        if not os.path.exists(config_path):
            print(f"❌ Configuration file not found: {config_path}")
            return None
        
        config = configparser.ConfigParser()
        config.read(config_path)
        return config
    
    def fetch_latest_xml(self) -> bool:
        """
        Fetch the latest XML from Windows machine using network share
        
        Returns:
            bool: True if successful
        """
        if not self.config:
            print("❌ No configuration available")
            return False
            
        try:
            # Get Windows share path
            windows_share = self.config['network']['windows_share_path']
            source_xml = f"{windows_share}/ms_project/ZnNi Line Development Plan-08.xml"
            
            print(f"🔄 Fetching latest XML from Windows machine...")
            print(f"Source: {source_xml}")
            print(f"Target: {self.local_xml_path}")
            
            # Create backup of current XML
            if os.path.exists(self.local_xml_path):
                backup_path = f"{self.local_xml_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(self.local_xml_path, backup_path)
                print(f"✅ Backup created: {backup_path}")
            
            # Copy from Windows share
            if os.path.exists(source_xml):
                shutil.copy2(source_xml, self.local_xml_path)
                print(f"✅ XML fetched successfully!")
                
                # Show file info
                stat = os.stat(self.local_xml_path)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                print(f"📅 XML timestamp: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            else:
                print(f"❌ Source XML not found at: {source_xml}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to fetch XML: {e}")
            return False
    
    def run_milestone_report(self, period: str) -> bool:
        """
        Run milestone report using current XML
        
        Args:
            period: "current", "next", or "both"
            
        Returns:
            bool: True if successful
        """
        try:
            print(f"📊 Running milestone report for {period} period...")
            
            # Run the milestone command
            result = subprocess.run([
                "python3", "control_tower.py", "ms-project", 
                "--action", "milestones", "--period", period
            ], cwd="/workspaces/control_tower", capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Milestone report completed successfully!")
                print(result.stdout)
                return True
            else:
                print(f"❌ Milestone report failed:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error running milestone report: {e}")
            return False
    
    def auto_fetch_and_report(self, period: str) -> bool:
        """
        Complete workflow: fetch latest XML and run report
        
        Args:
            period: "current", "next", or "both"
            
        Returns:
            bool: True if successful
        """
        print("🚀 ENHANCED AUTO-SYNC & REPORT")
        print("="*50)
        
        # Step 1: Fetch latest XML
        if not self.fetch_latest_xml():
            print("❌ Failed to fetch latest XML - using existing XML")
            # Continue with existing XML rather than failing completely
        
        # Step 2: Run milestone report
        return self.run_milestone_report(period)
    
    def check_sync_status(self):
        """Check the current sync status"""
        print("📋 SYNC STATUS CHECK")
        print("="*30)
        
        if os.path.exists(self.local_xml_path):
            stat = os.stat(self.local_xml_path)
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            age_hours = (datetime.now() - mod_time).total_seconds() / 3600
            
            print(f"📁 Local XML: EXISTS")
            print(f"📅 Last Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏰ Age: {age_hours:.1f} hours")
            
            if age_hours > 24:
                print(f"⚠️  XML is more than 24 hours old - consider fetching latest")
            else:
                print(f"✅ XML is relatively recent")
        else:
            print(f"❌ Local XML not found: {self.local_xml_path}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Enhanced Auto-Sync for Control Tower')
    parser.add_argument('--auto-fetch-and-report', 
                       choices=['current', 'next', 'both'],
                       help='Fetch latest XML and run milestone report')
    parser.add_argument('--fetch-only', action='store_true',
                       help='Only fetch latest XML (no report)')
    parser.add_argument('--report-only',
                       choices=['current', 'next', 'both'],
                       help='Only run milestone report (no fetch)')
    parser.add_argument('--status', action='store_true',
                       help='Check current sync status')
    
    args = parser.parse_args()
    
    if not any([args.auto_fetch_and_report, args.fetch_only, args.report_only, args.status]):
        parser.print_help()
        return 1
    
    sync = EnhancedSync()
    
    if args.status:
        sync.check_sync_status()
        return 0
    
    if args.fetch_only:
        success = sync.fetch_latest_xml()
        return 0 if success else 1
    
    if args.report_only:
        success = sync.run_milestone_report(args.report_only)
        return 0 if success else 1
    
    if args.auto_fetch_and_report:
        success = sync.auto_fetch_and_report(args.auto_fetch_and_report)
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
