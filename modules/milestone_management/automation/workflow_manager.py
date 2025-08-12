#!/usr/bin/env python3
"""
Universal Workflow Manager for Control Tower
Manages automated milestone change detection and reporting workflows across all repositories

This manager:
1. Discovers and monitors all repository XML files
2. Provides automated file watching across repositories
3. Coordinates change detection and reporting workflows
4. Manages scheduling and automation
5. Provides central control for all milestone management
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# File monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Add Control Tower modules to path
sys.path.append("/workspaces/control_tower")
from ..core.repository_scanner import RepositoryScanner
from ..core.milestone_detector import MilestoneChangeDetector
from ..reporting.safran_powerpoint_generator import SafranPowerPointGenerator

class UniversalXMLHandler(FileSystemEventHandler):
    """Handles XML file changes across all repositories"""
    
    def __init__(self, workflow_manager):
        self.workflow_manager = workflow_manager
        self.last_processed = {}
        self.processing_lock = threading.Lock()
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's an XML file we're monitoring
        if file_path.suffix.lower() == '.xml' and self._is_monitored_file(str(file_path)):
            current_time = time.time()
            
            # Prevent duplicate processing
            if current_time - self.last_processed.get(str(file_path), 0) < 2:
                return
            
            with self.processing_lock:
                self.last_processed[str(file_path)] = current_time
                self._process_xml_change(file_path)
    
    def _is_monitored_file(self, file_path: str) -> bool:
        """Check if file is one of our monitored XML files"""
        return file_path in self.workflow_manager.monitored_files
    
    def _process_xml_change(self, file_path: Path):
        """Process XML file change"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n🔔 [{timestamp}] XML CHANGE DETECTED!")
        print("="*60)
        print(f"📁 File: {file_path.name}")
        print(f"📂 Repository: {self.workflow_manager.get_repository_for_file(str(file_path))}")
        print(f"⏰ Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("🚀 Starting automated workflow...")
        print("="*60)
        
        try:
            # Run workflow for this specific file
            success = self.workflow_manager.run_workflow_for_file(str(file_path))
            
            if success:
                print(f"\n✅ Automated workflow completed for {file_path.name}")
            else:
                print(f"\n❌ Workflow encountered issues for {file_path.name}")
                
        except Exception as e:
            print(f"\n❌ Error in automated workflow: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n👁️ Resuming monitoring...")

class WorkflowManager:
    """
    Central workflow manager for milestone management across all repositories
    """
    
    def __init__(self, base_path: str = "/workspaces/control_tower"):
        """
        Initialize the workflow manager
        
        Args:
            base_path: Base Control Tower path
        """
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data" / "milestone_management"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.scanner = RepositoryScanner(str(self.base_path))
        self.detector = MilestoneChangeDetector(str(self.data_path))
        self.generator = SafranPowerPointGenerator(str(self.base_path / "reports" / "milestone_presentations"))
        
        # File monitoring
        self.monitored_files = set()
        self.file_to_repository = {}
        self.observers = []
        self.handler = None
        
        # Update monitored files
        self._update_monitored_files()
    
    def _update_monitored_files(self):
        """Update the list of files being monitored"""
        repositories = self.scanner.scan_all_repositories()
        
        self.monitored_files.clear()
        self.file_to_repository.clear()
        
        for repo_name, repo_info in repositories.items():
            for xml_file in repo_info['xml_files']:
                self.monitored_files.add(xml_file)
                self.file_to_repository[xml_file] = repo_name
        
        print(f"📋 Monitoring {len(self.monitored_files)} XML files across {len(repositories)} repositories")
    
    def get_repository_for_file(self, file_path: str) -> str:
        """Get repository name for a file path"""
        return self.file_to_repository.get(file_path, "Unknown")
    
    def start_automated_monitoring(self):
        """Start automated monitoring of all XML files"""
        
        if not WATCHDOG_AVAILABLE:
            print("❌ File watching requires 'watchdog' package")
            print("💡 Install with: pip install watchdog")
            return False
        
        print("🚀 CONTROL TOWER UNIVERSAL MILESTONE MONITORING")
        print("="*70)
        print(f"⏰ Started: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Update monitored files
        self._update_monitored_files()
        
        if not self.monitored_files:
            print("❌ No XML files found to monitor")
            return False
        
        # Get all unique directories to watch
        directories_to_watch = set()
        for file_path in self.monitored_files:
            directories_to_watch.add(str(Path(file_path).parent))
        
        print(f"👁️ Watching {len(directories_to_watch)} directories:")
        for directory in sorted(directories_to_watch):
            print(f"   📂 {directory}")
        
        print(f"📄 Monitoring {len(self.monitored_files)} XML files")
        print("="*70)
        
        # Create handler
        self.handler = UniversalXMLHandler(self)
        
        # Create observers for each directory
        self.observers = []
        for directory in directories_to_watch:
            try:
                observer = Observer()
                observer.schedule(self.handler, directory, recursive=False)
                observer.start()
                self.observers.append(observer)
            except Exception as e:
                print(f"⚠️ Could not watch {directory}: {e}")
        
        if not self.observers:
            print("❌ Failed to start any file observers")
            return False
        
        print("✅ Automated monitoring started successfully!")
        print("💡 The system will detect changes across all repositories")
        print("💡 Press Ctrl+C to stop monitoring")
        print("\n👁️ Monitoring for changes...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping automated monitoring...")
            self.stop_monitoring()
            print("✅ Monitoring stopped")
        
        return True
    
    def stop_monitoring(self):
        """Stop all file monitoring"""
        for observer in self.observers:
            observer.stop()
            observer.join()
        self.observers.clear()
    
    def run_manual_scan(self) -> Dict[str, List[Dict]]:
        """Run manual scan across all repositories"""
        print("🔍 MANUAL MILESTONE CHANGE SCAN")
        print("="*50)
        
        # Detect changes across all repositories
        all_changes = self.detector.scan_all_repositories_for_changes()
        
        # Generate reports if changes found
        if any(changes for changes in all_changes.values()):
            print("\n📊 Generating updated PowerPoint presentations...")
            self._generate_reports_for_changes(all_changes)
        else:
            print("\n📊 Generating baseline PowerPoint presentation...")
            self.generator.generate_cross_project_report()
        
        return all_changes
    
    def run_workflow_for_file(self, file_path: str) -> bool:
        """Run workflow for a specific XML file"""
        try:
            repo_name = self.get_repository_for_file(file_path)
            
            # Detect changes in this specific file
            changes = self.detector.detect_changes_in_file(file_path, repo_name)
            
            # Generate updated reports
            if changes:
                # Generate repository-specific report
                self.generator.generate_repository_report(repo_name)
                # Generate updated cross-project report
                self.generator.generate_cross_project_report()
            
            return True
            
        except Exception as e:
            print(f"❌ Error in workflow for {file_path}: {e}")
            return False
    
    def _generate_reports_for_changes(self, all_changes: Dict[str, List[Dict]]):
        """Generate PowerPoint reports for detected changes"""
        
        # Generate cross-project report
        cross_project_path = self.generator.generate_cross_project_report()
        if cross_project_path:
            print(f"✅ Cross-project report: {cross_project_path}")
        
        # Generate repository-specific reports for affected repositories
        for repo_name in all_changes.keys():
            repo_path = self.generator.generate_repository_report(repo_name)
            if repo_path:
                print(f"✅ {repo_name} report: {repo_path}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        repositories = self.scanner.scan_all_repositories()
        change_summary = self.detector.get_all_changes_summary()
        
        status = {
            'monitoring': {
                'active': len(self.observers) > 0,
                'monitored_files': len(self.monitored_files),
                'monitored_repositories': len(repositories),
                'observers_running': len(self.observers)
            },
            'repositories': repositories,
            'changes': change_summary,
            'last_updated': datetime.now().isoformat()
        }
        
        return status
    
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        try:
            import subprocess
            
            packages = ['watchdog', 'python-pptx']
            for package in packages:
                print(f"📦 Installing {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            
            print("✅ All dependencies installed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

def main():
    """Main function for command line usage"""
    
    print("🚀 CONTROL TOWER WORKFLOW MANAGER")
    print("="*50)
    
    manager = WorkflowManager()
    
    # Check if watchdog is available
    if not WATCHDOG_AVAILABLE:
        print("⚠️ Watchdog package not available for automated monitoring")
        response = input("Install dependencies? (y/n): ").strip().lower()
        
        if response == 'y':
            if manager.install_dependencies():
                print("🔄 Please restart to use automated monitoring")
                return
        else:
            print("💡 Running manual scan instead...")
            manager.run_manual_scan()
            return
    
    # Show menu
    while True:
        print("\nChoose an option:")
        print("1. Start automated monitoring")
        print("2. Run manual scan")
        print("3. System status")
        print("4. Exit")
        
        try:
            choice = input("\nSelect (1-4): ").strip()
            
            if choice == '1':
                manager.start_automated_monitoring()
            elif choice == '2':
                manager.run_manual_scan()
            elif choice == '3':
                status = manager.get_system_status()
                print(f"\n📊 SYSTEM STATUS:")
                print(f"   Monitoring: {'Active' if status['monitoring']['active'] else 'Inactive'}")
                print(f"   Repositories: {status['monitoring']['monitored_repositories']}")
                print(f"   XML files: {status['monitoring']['monitored_files']}")
                print(f"   Total changes: {status['changes']['total_changes']}")
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
