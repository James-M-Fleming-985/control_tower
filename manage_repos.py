#!/usr/bin/env python3
"""
Control Tower Repository Management System
Scalable solution for managing multiple repositories from control_tower
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import argparse
from datetime import datetime

class RepoManager:
    def __init__(self, base_path: str = "/workspaces/control_tower/cloned_repos"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.config_file = Path("/workspaces/control_tower/repo_config.json")
        self.load_config()
    
    def load_config(self):
        """Load repository configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "repositories": {
                    "business_ventures": {
                        "owner": "James-M-Fleming-985",
                        "type": "workspace_link",
                        "source_path": "/workspaces/business_ventures",
                        "description": "Business projects and ventures",
                        "active": True
                    }
                },
                "settings": {
                    "auto_sync": True,
                    "backup_before_sync": True,
                    "default_branch": "main"
                },
                "last_updated": datetime.now().isoformat()
            }
            self.save_config()
    
    def save_config(self):
        """Save repository configuration"""
        self.config["last_updated"] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_repo(self, name: str, owner: str, repo_type: str = "clone", description: str = ""):
        """Add a new repository to management"""
        self.config["repositories"][name] = {
            "owner": owner,
            "type": repo_type,
            "description": description,
            "active": True,
            "added": datetime.now().isoformat()
        }
        self.save_config()
        print(f"✅ Added repository: {name}")
        
        if repo_type == "clone":
            self.clone_repo(name)
    
    def clone_repo(self, name: str) -> bool:
        """Clone a repository"""
        if name not in self.config["repositories"]:
            print(f"❌ Repository {name} not in configuration")
            return False
        
        repo_config = self.config["repositories"][name]
        owner = repo_config["owner"]
        repo_path = self.base_path / name
        
        if repo_path.exists():
            print(f"⚠️  Repository {name} already exists at {repo_path}")
            return False
        
        try:
            cmd = f"gh repo clone {owner}/{name} {repo_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Cloned {owner}/{name} to {repo_path}")
                return True
            else:
                print(f"❌ Failed to clone {name}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error cloning {name}: {str(e)}")
            return False
    
    def sync_repo(self, name: str) -> bool:
        """Sync a repository (pull latest changes)"""
        repo_path = self.base_path / name
        
        if not repo_path.exists():
            print(f"❌ Repository {name} not found at {repo_path}")
            return False
        
        try:
            # Save current directory
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Get current branch
            branch_result = subprocess.run(
                "git branch --show-current", 
                shell=True, capture_output=True, text=True
            )
            current_branch = branch_result.stdout.strip()
            
            # Pull latest changes
            result = subprocess.run(
                f"git pull origin {current_branch}", 
                shell=True, capture_output=True, text=True
            )
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                print(f"✅ Synced {name} ({current_branch})")
                return True
            else:
                print(f"⚠️  Sync issues for {name}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error syncing {name}: {str(e)}")
            return False
    
    def sync_all(self):
        """Sync all active repositories"""
        print("🔄 Syncing all repositories...")
        
        for name, config in self.config["repositories"].items():
            if config.get("active", True) and config.get("type") != "workspace_link":
                self.sync_repo(name)
    
    def status(self):
        """Show status of all repositories"""
        print("\n📊 REPOSITORY STATUS")
        print("=" * 50)
        
        for name, config in self.config["repositories"].items():
            repo_path = self.base_path / name
            status = "✅ Available" if repo_path.exists() else "❌ Missing"
            repo_type = config.get("type", "clone")
            description = config.get("description", "No description")
            
            print(f"\n🔷 {name}")
            print(f"   Status: {status}")
            print(f"   Type: {repo_type}")
            print(f"   Path: {repo_path}")
            print(f"   Description: {description}")
            
            if repo_path.exists() and repo_type != "workspace_link":
                try:
                    original_dir = os.getcwd()
                    os.chdir(repo_path)
                    
                    # Get git status
                    branch_result = subprocess.run(
                        "git branch --show-current", 
                        shell=True, capture_output=True, text=True
                    )
                    branch = branch_result.stdout.strip()
                    
                    status_result = subprocess.run(
                        "git status --porcelain", 
                        shell=True, capture_output=True, text=True
                    )
                    changes = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
                    
                    os.chdir(original_dir)
                    
                    print(f"   Branch: {branch}")
                    print(f"   Uncommitted changes: {changes}")
                    
                except Exception as e:
                    print(f"   Git status: Error ({str(e)})")
        
        print(f"\n📁 Base path: {self.base_path}")
        print(f"⚙️  Config: {self.config_file}")
    
    def setup_workspace_links(self):
        """Set up symbolic links for workspace repositories"""
        for name, config in self.config["repositories"].items():
            if config.get("type") == "workspace_link":
                source_path = Path(config.get("source_path", ""))
                target_path = self.base_path / name
                
                if source_path.exists() and not target_path.exists():
                    try:
                        target_path.symlink_to(source_path)
                        print(f"✅ Created workspace link: {name} -> {source_path}")
                    except Exception as e:
                        print(f"❌ Failed to create link for {name}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Control Tower Repository Manager")
    parser.add_argument("command", choices=["status", "sync", "sync-all", "add", "setup-links"])
    parser.add_argument("--name", help="Repository name")
    parser.add_argument("--owner", help="Repository owner")
    parser.add_argument("--type", choices=["clone", "workspace_link"], default="clone", help="Repository type")
    parser.add_argument("--description", help="Repository description")
    
    args = parser.parse_args()
    
    manager = RepoManager()
    
    if args.command == "status":
        manager.status()
    elif args.command == "sync":
        if not args.name:
            print("❌ --name is required for sync command")
            return
        manager.sync_repo(args.name)
    elif args.command == "sync-all":
        manager.sync_all()
    elif args.command == "add":
        if not args.name or not args.owner:
            print("❌ --name and --owner are required for add command")
            return
        manager.add_repo(args.name, args.owner, args.type, args.description or "")
    elif args.command == "setup-links":
        manager.setup_workspace_links()


if __name__ == "__main__":
    main()