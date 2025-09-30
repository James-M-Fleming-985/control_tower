#!/usr/bin/env python3
"""
Repository File Organization Checker
===================================

Validates file placement and prevents accidental saves to repo root.
Provides automatic suggestions for proper file organization.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

class RepoFileGuard:
    """Guards against improper file placement in repository"""
    
    def __init__(self, repo_root: str = "/workspaces/control_tower"):
        self.repo_root = Path(repo_root)
        self.current_dir = Path.cwd()
        
        # Protected directories where PROJECT-003 code should NOT be added
        self.protected_dirs = {
            "root_src": self.repo_root / "src",
            "root_tests": self.repo_root / "tests"
        }
        
        # Define proper locations for different file types
        self.file_location_map = {
            # Documentation
            ".md": {
                "project_003": "projects/PROJECT-003 TDD ENFORCER/docs/",
                "general": "docs/",
                "requirements": "requirements/"
            },
            # Python files  
            ".py": {
                "test": "tests/",
                "project_003": "projects/PROJECT-003 TDD ENFORCER/src/",
                "general": "src/",
                "script": "scripts/",
                "tool": "tools/"
            },
            # Configuration
            ".json": "config/",
            ".ini": "config/", 
            ".toml": "config/",
            ".yaml": "config/",
            ".yml": "config/",
            
            # Scripts
            ".sh": "scripts/",
            ".bash": "scripts/",
            
            # Data
            ".csv": "data/",
            ".db": "data/",
            ".sqlite": "data/",
            
            # Reports
            ".html": "reports/",
            ".txt": "reports/",
            
            # Archives  
            ".tar.gz": "backups/",
            ".zip": "backups/",
            ".backup": "backups/"
        }
    
    def is_in_repo_root(self) -> bool:
        """Check if current directory is repository root"""
        return self.current_dir == self.repo_root
    
    def is_in_protected_dir(self) -> str:
        """Check if current directory is a protected directory for PROJECT-003"""
        for dir_name, dir_path in self.protected_dirs.items():
            if self.current_dir == dir_path or dir_path in self.current_dir.parents:
                return dir_name
        return ""
    
    def is_project_003_content(self, filename: str, content: str = "") -> bool:
        """Detect if file appears to be PROJECT-003 related content"""
        name_lower = filename.lower()
        content_lower = content.lower()
        
        # Filename indicators
        project_indicators = [
            "project-003", "project_003", "tdd_enforcer", "tdd-enforcer",
            "mobile_command", "context_engine", "audit_trail", 
            "tdd_cycle", "phase_enforcement", "stage_gate"
        ]
        
        # Check filename
        if any(indicator in name_lower for indicator in project_indicators):
            return True
            
        # Check content for PROJECT-003 specific imports/references
        if content:
            content_indicators = [
                "project-003", "tdd enforcer", "mobile_command_history_repository",
                "context_engine_repository", "tdd_cycle_enforcer", 
                "system-003-", "feature-003-", "layer-003-"
            ]
            if any(indicator in content_lower for indicator in content_indicators):
                return True
                
        return False
    
    def suggest_location(self, filename: str) -> str:
        """Suggest proper location for a file based on its type and content"""
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        name = file_path.name.lower()
        
        # Check for PROJECT-003 specific files
        if any(keyword in name for keyword in ["project-003", "tdd", "enforcer"]):
            if extension == ".md":
                return "projects/PROJECT-003 TDD ENFORCER/docs/"
            elif extension == ".py":
                if name.startswith("test_"):
                    return "projects/PROJECT-003 TDD ENFORCER/tests/"
                else:
                    return "projects/PROJECT-003 TDD ENFORCER/src/"
        
        # Check for test files
        if name.startswith("test_") and extension == ".py":
            return "tests/"
        
        # Check extension-based mapping
        if extension in self.file_location_map:
            location = self.file_location_map[extension]
            if isinstance(location, dict):
                # Default to general location
                return location.get("general", "")
            return location
        
        return "appropriate_subdirectory/"
    
    def check_file_placement(self, filename: str, content: str = "") -> Dict[str, any]:
        """Check if file placement is appropriate"""
        result = {
            "is_root_save": self.is_in_repo_root(),
            "is_protected_save": "",
            "is_project_003": self.is_project_003_content(filename, content),
            "filename": filename,
            "current_location": str(self.current_dir),
            "suggested_location": "",
            "warning_level": "none",
            "message": ""
        }
        
        # Check for protected directory violations
        protected_dir = self.is_in_protected_dir()
        if protected_dir:
            result["is_protected_save"] = protected_dir
            
            # CRITICAL: PROJECT-003 content should NEVER go in root src/tests
            if result["is_project_003"]:
                result["warning_level"] = "critical"
                if protected_dir == "root_src":
                    result["suggested_location"] = "projects/PROJECT-003 TDD ENFORCER/src/"
                    result["message"] = f"🚨 CRITICAL: PROJECT-003 code detected in root src! Must use: {result['suggested_location']}"
                elif protected_dir == "root_tests":
                    result["suggested_location"] = "projects/PROJECT-003 TDD ENFORCER/tests/"
                    result["message"] = f"🚨 CRITICAL: PROJECT-003 test detected in root tests! Must use: {result['suggested_location']}"
            else:
                result["warning_level"] = "medium"
                result["message"] = f"⚠️  Adding to {protected_dir.replace('_', ' ')} - ensure this is not PROJECT-003 related"
        
        # Standard root save check
        elif result["is_root_save"]:
            result["suggested_location"] = self.suggest_location(filename)
            result["warning_level"] = "high"
            result["message"] = f"⚠️  Attempting to save '{filename}' to repository root! Consider: {result['suggested_location']}"
        
        return result
    
    def warn_if_root_save(self, filename: str, content: str = "") -> bool:
        """Warn user if attempting inappropriate file placement"""
        check_result = self.check_file_placement(filename, content)
        
        # Handle different warning levels
        if check_result["warning_level"] == "critical":
            print(f"\n🚨🚨 CRITICAL VIOLATION 🚨🚨")
            print(f"📁 File: {filename}")
            print(f"📍 Current location: {check_result['current_location']}")
            print(f"� Issue: {check_result['message']}")
            print(f"💡 Required location: {check_result['suggested_location']}")
            print(f"🔧 Command: mkdir -p {check_result['suggested_location']} && mv {filename} {check_result['suggested_location']}")
            print("⛔ This violates PROJECT-003 architecture - MUST be fixed!")
            print()
            return False
            
        elif check_result["warning_level"] in ["high", "medium"]:
            print(f"\n🚨 FILE PLACEMENT WARNING 🚨")
            print(f"📁 File: {filename}")
            print(f"📍 Current location: {check_result['current_location']}")
            print(f"💡 Suggested location: {check_result['suggested_location']}")
            print(f"🔧 Command: mkdir -p {check_result['suggested_location']} && mv {filename} {check_result['suggested_location']}")
            if check_result["message"]:
                print(f"ℹ️  {check_result['message']}")
            print()
            return False
        
        return True
    
    def get_root_cleanup_suggestions(self) -> List[Dict[str, str]]:
        """Analyze current root files and suggest cleanup"""
        suggestions = []
        
        if not self.is_in_repo_root():
            return suggestions
            
        # Get all files in root
        root_files = [f for f in self.repo_root.iterdir() if f.is_file()]
        
        for file_path in root_files:
            if file_path.name.startswith('.'):
                continue  # Skip hidden files
                
            suggested_location = self.suggest_location(file_path.name)
            if suggested_location != "appropriate_subdirectory/":
                suggestions.append({
                    "filename": file_path.name,
                    "current": str(file_path),
                    "suggested": suggested_location,
                    "command": f"mkdir -p {suggested_location} && mv {file_path.name} {suggested_location}"
                })
        
        return suggestions

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python repo_file_guard.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    guard = RepoFileGuard()
    
    # Check file placement
    is_safe = guard.warn_if_root_save(filename)
    
    if not is_safe:
        print("❌ Consider relocating file to suggested location")
        sys.exit(1)
    else:
        print("✅ File placement looks good")
        sys.exit(0)

if __name__ == "__main__":
    main()