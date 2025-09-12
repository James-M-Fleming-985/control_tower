#!/usr/bin/env python3
"""
Automated Sync Scheduler for Contract Projects
Periodically syncs MS Project files to keep XML data current

This runs in the background and automatically:
- Syncs MS Project files to XML every hour
- Updates contract project data
- Logs sync status
- Uses remote execution for Linux/Codespaces environments
"""

import os
import sys
import time
import schedule
from datetime import datetime
import logging
import configparser
import subprocess
import platform

# Import from the same module directory
from .contract_project_manager import ContractProjectManager

class AutoSyncScheduler:
    """
    Automated sync scheduler for contract projects
    Enhanced with remote execution for Linux/Codespaces environments
    """
    
    def __init__(self):
        """Initialize the scheduler"""
        self.manager = ContractProjectManager()
        self.setup_logging()
        self.windows_config = self.load_windows_target_config()
        self.is_containerized = self.detect_containerized_environment()
        
    def detect_containerized_environment(self):
        """Detect if running in containerized environment (Linux/Codespaces)"""
        # Check if we're in a Linux environment without direct Windows access
        if platform.system() != "Windows":
            return True
        # Check if the expected Windows path exists
        return not os.path.exists(r"D:\Downloads\ZnNi Line Development Plan-08.mpp")
    
    def load_windows_target_config(self):
        """Load Windows machine target configuration for remote sync"""
        config_path = "/workspaces/control_tower/config/windows_target.conf"
        
        if not os.path.exists(config_path):
            return None
        
        config = configparser.ConfigParser()
        try:
            config.read(config_path)
            return {
                'host': config['windows_machine']['host'],
                'username': config.get('windows_machine', 'username', fallback=None),
                'xml_workspace': config['windows_machine']['xml_workspace'],
                'main_project_file': config['ms_project']['main_project_file'],
                'ssh_key': config.get('network', 'ssh_key', fallback='~/.ssh/id_rsa'),
                'use_admin_shares': config.getboolean('network', 'use_admin_shares', fallback=False),
                'codespaces_xml_workspace': config['codespaces']['xml_workspace']
            }
        except Exception as e:
            self.logger.warning(f"⚠️  Could not load Windows config: {e}")
            return None
        
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
        """Perform scheduled sync of project data with multiple fallback methods"""
        try:
            self.logger.info("🔄 Starting scheduled sync...")
            
            if self.is_containerized:
                # Try multiple sync methods for containerized environments
                self.logger.info("🐧 Containerized environment detected - using file-based sync methods")
                success = self.containerized_sync_project_data()
            else:
                # Use local sync for Windows environments
                self.logger.info("🔧 Using local sync (Windows environment)")
                success = self.manager.auto_sync_from_mpp()
            
            if success:
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
    
    def containerized_sync_project_data(self):
        """Perform sync in containerized environment using multiple methods"""
        
        # Method 1: Check for newer files in ms_project_data folder
        success = self.sync_from_ms_project_data()
        if success:
            self.logger.info("✅ Sync successful via ms_project_data folder")
            return True
        
        # Method 2: Try remote execution if configured
        if self.windows_config:
            self.logger.info("📡 Attempting remote execution sync...")
            success = self.remote_sync_project_data()
            if success:
                self.logger.info("✅ Remote sync successful")
                return True
            else:
                self.logger.warning("⚠️  Remote sync failed")
        
        # Method 3: Use existing XML (no sync needed)
        self.logger.info("📄 Using existing XML file (no newer source found)")
        return True  # Not a failure - just no sync needed
    
    def sync_from_ms_project_data(self):
        """Check ms_project_data folder for newer XML files and sync them"""
        try:
            ms_project_data_dir = "/workspaces/control_tower/cloned_repos/contract_projects/ms_project_data"
            current_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/current/ZnNi Line Development Plan-08.xml"
            snapshots_dir = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/snapshots"
            
            # Ensure current and snapshots directories exist
            os.makedirs(os.path.dirname(current_xml), exist_ok=True)
            os.makedirs(snapshots_dir, exist_ok=True)
            
            if not os.path.exists(ms_project_data_dir):
                return False
            
            # Find XML files in ms_project_data
            xml_files = [f for f in os.listdir(ms_project_data_dir) if f.endswith('.xml')]
            
            if not xml_files:
                return False
            
            # Find the newest XML file
            newest_file = None
            newest_time = 0
            
            for xml_file in xml_files:
                file_path = os.path.join(ms_project_data_dir, xml_file)
                file_time = os.path.getmtime(file_path)
                if file_time > newest_time:
                    newest_time = file_time
                    newest_file = file_path
            
            # Check if the newest file is newer than current XML
            if os.path.exists(current_xml):
                current_xml_time = os.path.getmtime(current_xml)
                if newest_time <= current_xml_time:
                    self.logger.info("📄 Current XML is up to date")
                    return True
            
            # Copy the newer file to XML workspace
            import shutil
            
            # Create Friday snapshot if current XML exists
            if os.path.exists(current_xml):
                friday_date = datetime.now().strftime('%Y%m%d')
                snapshot_path = os.path.join(snapshots_dir, f"friday_{friday_date}_ZnNi_Line_Development_Plan-08.xml")
                shutil.copy2(current_xml, snapshot_path)
                self.logger.info(f"� Friday snapshot created: friday_{friday_date}_ZnNi_Line_Development_Plan-08.xml")
            
            shutil.copy2(newest_file, current_xml)
            self.logger.info(f"✅ XML updated from: {os.path.basename(newest_file)}")
            self.logger.info(f"📅 Source file date: {datetime.fromtimestamp(newest_time).strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ms_project_data sync error: {e}")
            return False
    
    def remote_sync_project_data(self):
        """Perform remote sync using Windows target configuration"""
        try:
            if not self.windows_config:
                self.logger.warning("⚠️  No Windows configuration available for remote sync")
                return False
            
            local_xml = os.path.join(self.windows_config['codespaces_xml_workspace'], 
                                   "ZnNi Line Development Plan-08.xml")
            
            self.logger.info(f"🔄 Remote sync: {self.windows_config['host']}")
            
            # Use the remote execution framework to sync XML
            # This will copy XML to Windows, launch MS Project, export updated XML, and copy back
            from . import remote_execution_utils
            
            success = remote_execution_utils.execute_remote_sync(
                self.windows_config, 
                local_xml, 
                "Automated background sync"
            )
            
            if success:
                self.logger.info("✅ Remote sync completed successfully")
                return True
            else:
                self.logger.warning("⚠️  Remote sync failed, using existing XML")
                return False
                
        except ImportError:
            # Fallback to manual request if remote execution not available
            self.logger.warning("⚠️  Remote execution not available, requesting manual sync")
            return False
        except Exception as e:
            self.logger.error(f"❌ Remote sync error: {e}")
            return False
    
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
