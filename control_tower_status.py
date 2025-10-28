#!/usr/bin/env python3
"""
Control Tower Status Dashboard
Shows the status of all managed repositories and projects
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"Error: {e}", 1

def get_git_status(path):
    """Get git status for a repository"""
    output, code = run_command("git status --porcelain", cwd=path)
    if code == 0:
        return len(output.split('\n')) if output else 0
    return "Not a git repo"

def main():
    print("🏗️  CONTROL TOWER STATUS DASHBOARD")
    print("=" * 50)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Workspace: {os.getcwd()}")
    print()
    
    # Main repository status
    print("🎯 MAIN CONTROL TOWER REPOSITORY")
    changes = get_git_status(".")
    if isinstance(changes, int):
        print(f"   📊 Uncommitted changes: {changes}")
    else:
        print(f"   ⚠️  Status: {changes}")
    
    # Check for managed repositories
    repos_dir = Path("repos")
    if repos_dir.exists():
        print("\n🔗 MANAGED REPOSITORIES")
        for repo_path in repos_dir.iterdir():
            if repo_path.is_dir() and (repo_path / ".git").exists():
                changes = get_git_status(repo_path)
                print(f"   📦 {repo_path.name}: {changes} changes")
    
    # Check TDD test status
    if Path("test_evidence_storage.py").exists():
        print("\n🧪 TDD TEST STATUS")
        output, code = run_command("python3 -m pytest test_evidence_storage.py --tb=no -q")
        if code == 0:
            print("   ✅ All tests passing")
        else:
            print("   🔴 Tests failing (as expected for TDD)")
    
    # Check project structure
    print("\n📋 PROJECT STRUCTURE")
    key_dirs = ["projects", "src", "tests", "Prompts"]
    for dir_name in key_dirs:
        if Path(dir_name).exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ (missing)")
    
    print("\n" + "=" * 50)
    print("Use './manage_repos.sh help' for repository management commands")

if __name__ == "__main__":
    main()
