#!/usr/bin/env python3
"""
Real-time File Organization Monitor
===================================

Watches for file creation/modification and enforces organization rules.
Runs as a background service to catch violations immediately.
"""

import os
import sys
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

# Add the scripts directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))
from repo_file_guard import RepoFileGuard

class FileOrganizationHandler(FileSystemEventHandler):
    """Handles file system events and enforces organization rules"""
    
    def __init__(self, repo_root="/workspaces/control_tower"):
        self.repo_root = Path(repo_root)
        self.guard = RepoFileGuard(repo_root)
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the file monitor"""
        log_dir = self.repo_root / "protection_logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "file_organization_monitor.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        filename = file_path.name
        
        # Skip temporary and hidden files
        if filename.startswith('.') or filename.endswith('.tmp'):
            return
            
        # Skip files in .git directory
        if '.git' in file_path.parts:
            return
            
        self.check_file_organization(file_path)
        
    def on_modified(self, event):
        """Handle file modification events"""
        # Only check new files, not modifications to existing files
        pass
        
    def check_file_organization(self, file_path: Path):
        """Check if file placement violates organization rules"""
        try:
            # Read file content for analysis
            content = ""
            try:
                if file_path.suffix in ['.py', '.md', '.json', '.yaml', '.yml']:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')[:1000]  # First 1KB
            except Exception:
                pass  # Continue without content analysis
                
            # Change to file directory for guard check
            original_cwd = Path.cwd()
            try:
                os.chdir(file_path.parent)
                check_result = self.guard.check_file_placement(file_path.name, content)
                
                if check_result["warning_level"] in ["critical", "high"]:
                    self.handle_violation(file_path, check_result)
                elif check_result["warning_level"] == "medium":
                    self.handle_warning(file_path, check_result)
                else:
                    self.logger.info(f"✅ File placement OK: {file_path}")
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"Error checking file {file_path}: {e}")
            
    def handle_violation(self, file_path: Path, check_result: dict):
        """Handle critical file placement violations"""
        self.logger.error(f"🚨 CRITICAL VIOLATION: {file_path}")
        self.logger.error(f"Issue: {check_result['message']}")
        self.logger.error(f"Required location: {check_result['suggested_location']}")
        
        # Create notification file
        violation_file = self.repo_root / "protection_logs" / "URGENT_FILE_VIOLATION.txt"
        with open(violation_file, "w") as f:
            f.write(f"URGENT: File Placement Violation Detected\n")
            f.write(f"=========================================\n")
            f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"File: {file_path}\n")
            f.write(f"Issue: {check_result['message']}\n")
            f.write(f"Required location: {check_result['suggested_location']}\n")
            f.write(f"Fix command: mkdir -p {check_result['suggested_location']} && mv {file_path} {check_result['suggested_location']}\n")
            
        # Try to auto-fix if it's a clear PROJECT-003 violation
        if check_result["is_project_003"] and check_result["suggested_location"]:
            self.attempt_auto_fix(file_path, check_result)
            
    def handle_warning(self, file_path: Path, check_result: dict):
        """Handle medium-level warnings"""
        self.logger.warning(f"⚠️  File placement warning: {file_path}")
        self.logger.warning(f"Suggestion: {check_result['suggested_location']}")
        
    def attempt_auto_fix(self, file_path: Path, check_result: dict):
        """Attempt to automatically fix obvious violations"""
        try:
            suggested_dir = self.repo_root / check_result['suggested_location']
            suggested_dir.mkdir(parents=True, exist_ok=True)
            
            new_path = suggested_dir / file_path.name
            file_path.rename(new_path)
            
            self.logger.info(f"🔧 Auto-fixed: moved {file_path} to {new_path}")
            
            # Update the violation file with fix status
            violation_file = self.repo_root / "protection_logs" / "URGENT_FILE_VIOLATION.txt"
            with open(violation_file, "a") as f:
                f.write(f"STATUS: AUTO-FIXED - File moved to {new_path}\n")
                
        except Exception as e:
            self.logger.error(f"Failed to auto-fix {file_path}: {e}")

def main():
    """Main function to start the file organization monitor"""
    repo_root = "/workspaces/control_tower"
    
    print("🛡️  Starting File Organization Monitor")
    print("=====================================")
    print(f"Monitoring: {repo_root}")
    print("Press Ctrl+C to stop")
    print()
    
    handler = FileOrganizationHandler(repo_root)
    observer = Observer()
    observer.schedule(handler, repo_root, recursive=True)
    
    try:
        observer.start()
        handler.logger.info("📁 File Organization Monitor started")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping File Organization Monitor...")
        handler.logger.info("📁 File Organization Monitor stopped")
        observer.stop()
        
    observer.join()

if __name__ == "__main__":
    main()