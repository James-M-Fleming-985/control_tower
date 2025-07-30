#!/usr/bin/env python3
"""
Automated Sync Scheduler for Contract Projects
Periodically syncs MS Project files to keep XML data current

This runs in the background and automatically:
- Syncs MS Project files to XML every hour
- Updates contract project data
- Logs sync status
"""

import os
import sys
import time
import schedule
from datetime import datetime
import logging

# Import from the same module directory
from .contract_project_manager import ContractProjectManager

class AutoSyncScheduler:
    """
    Automated sync scheduler for contract projects
    """
    
    def __init__(self):
        """Initialize the scheduler"""
        self.manager = ContractProjectManager()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for sync operations"""
        log_dir = "/workspaces/control_tower/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'auto_sync.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def sync_project_data(self):
        """Perform scheduled sync of project data"""
        try:
            self.logger.info("🔄 Starting scheduled sync...")
            
            if self.manager.auto_sync_from_mpp():
                self.logger.info("✅ Scheduled sync successful")
                
                # Verify data quality
                if self.manager.load_project():
                    task_count = len(self.manager.ms_project.tasks)
                    milestone_count = len([t for t in self.manager.ms_project.tasks if t['is_milestone']])
                    self.logger.info(f"📊 Project loaded: {task_count} tasks, {milestone_count} milestones")
                else:
                    self.logger.warning("⚠️  Sync completed but data verification failed")
            else:
                self.logger.warning("❌ Scheduled sync failed")
                
        except Exception as e:
            self.logger.error(f"❌ Sync error: {e}")
    
    def check_project_health(self):
        """Check project data health and currency"""
        try:
            self.logger.info("🔍 Checking project health...")
            
            xml_path = self.manager.current_xml
            mpp_path = self.manager.source_mpp
            
            if os.path.exists(xml_path) and os.path.exists(mpp_path):
                xml_mtime = os.path.getmtime(xml_path)
                mpp_mtime = os.path.getmtime(mpp_path)
                
                age_hours = (time.time() - xml_mtime) / 3600
                
                if xml_mtime >= mpp_mtime:
                    self.logger.info(f"✅ Project data is current (age: {age_hours:.1f} hours)")
                else:
                    self.logger.warning(f"⚠️  Project data is outdated (MPP newer than XML)")
                    # Trigger immediate sync
                    self.sync_project_data()
            else:
                self.logger.warning(f"⚠️  Missing files - XML: {os.path.exists(xml_path)}, MPP: {os.path.exists(mpp_path)}")
                
        except Exception as e:
            self.logger.error(f"❌ Health check error: {e}")
    
    def start_scheduler(self, sync_interval_hours: int = 1):
        """
        Start the automated sync scheduler
        
        Args:
            sync_interval_hours: Hours between sync attempts
        """
        self.logger.info(f"🚀 Starting auto-sync scheduler (every {sync_interval_hours} hour(s))")
        
        # Schedule sync every N hours
        schedule.every(sync_interval_hours).hours.do(self.sync_project_data)
        
        # Schedule health check every 30 minutes
        schedule.every(30).minutes.do(self.check_project_health)
        
        # Initial sync
        self.sync_project_data()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Scheduler error: {e}")

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-Sync Scheduler for Contract Projects')
    parser.add_argument('--interval', type=int, default=1, 
                       help='Sync interval in hours (default: 1)')
    parser.add_argument('--once', action='store_true',
                       help='Run sync once and exit (no scheduling)')
    parser.add_argument('--health-check', action='store_true',
                       help='Run health check and exit')
    
    args = parser.parse_args()
    
    scheduler = AutoSyncScheduler()
    
    if args.once:
        # Run sync once and exit
        scheduler.sync_project_data()
    elif args.health_check:
        # Run health check and exit
        scheduler.check_project_health()
    else:
        # Start continuous scheduler
        scheduler.start_scheduler(args.interval)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
