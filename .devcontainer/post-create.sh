#!/bin/bash

# Control Tower Multi-Repo Setup Script
# This script configures the control tower for managing multiple repositories

echo "🏗️  Setting up Control Tower Multi-Repo Management Hub..."

# Set up Git configuration for multi-repo work
echo "📋 Configuring Git for multi-repo management..."

# Set up global Git config if not already set
if ! git config --global user.name >/dev/null 2>&1; then
    echo "⚠️  Git user.name not configured. Please run:"
    echo "   git config --global user.name 'Your Name'"
fi

if ! git config --global user.email >/dev/null 2>&1; then
    echo "⚠️  Git user.email not configured. Please run:"
    echo "   git config --global user.email 'your.email@example.com'"
fi

# Configure Git for better multi-repo workflow
git config --global push.default simple
git config --global pull.rebase true
git config --global core.editor "code --wait"
git config --global init.defaultBranch main

# Set up GitHub CLI authentication check
echo "🔐 Checking GitHub CLI authentication..."
if ! gh auth status >/dev/null 2>&1; then
    echo "⚠️  GitHub CLI not authenticated. Run: gh auth login --web"
else
    echo "✅ GitHub CLI authenticated"
fi

# Create necessary directories for multi-repo management
echo "📁 Creating control tower directory structure..."
mkdir -p /workspaces/control_tower/{repos,temp_clones,sync_status,deployment_targets}

# Set up Python environment
echo "🐍 Setting up Python environment..."
pip install --upgrade pip
pip install -e . 2>/dev/null || echo "No setup.py found, skipping editable install"

# Install required packages based on pyproject.toml
if [ -f "/workspaces/control_tower/pyproject.toml" ]; then
    echo "📦 Installing packages from pyproject.toml..."
    pip install pytest pytest-cov pytest-mock pytest-html pathlib dataclasses
    pip install black flake8 pylint
    pip install requests pyyaml click
else
    echo "⚠️  No pyproject.toml found, installing common packages..."
    pip install pytest pytest-cov pytest-mock pytest-html
    pip install black flake8 pylint
    pip install requests pyyaml click pathlib dataclasses
fi

# Set up workspace environment variables
echo "🔧 Setting up environment variables..."
echo "export CONTROL_TOWER_MODE=true" >> ~/.bashrc
echo "export MULTI_REPO_WORKSPACE=/workspaces/control_tower" >> ~/.bashrc
echo "export PYTHONPATH=/workspaces/control_tower/src:/workspaces/control_tower:\$PYTHONPATH" >> ~/.bashrc

# Create helpful aliases for multi-repo management
echo "⚡ Setting up helpful aliases..."
cat >> ~/.bashrc << 'EOF'

# Control Tower Multi-Repo Aliases
alias ct-status='echo "=== Control Tower Status ===" && pwd && git status --short'
alias ct-repos='ls -la repos/ 2>/dev/null || echo "No repos directory found"'
alias ct-sync='echo "Syncing all repositories..." && find repos -name ".git" -type d | while read gitdir; do echo "Syncing $(dirname $gitdir)"; (cd $(dirname $gitdir) && git fetch --all); done'
alias ct-test='pytest test_evidence_storage.py -v'
alias ct-test-all='find . -name "test_*.py" -exec pytest {} -v \;'
alias ct-clean='find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; find . -name "*.pyc" -delete 2>/dev/null'

# TDD Workflow aliases
alias tdd-red='echo "🔴 RED: Running failing tests..." && ct-test'
alias tdd-green='echo "🟢 GREEN: Implementing minimal code..." && code evidence_storage.py'
alias tdd-refactor='echo "🔵 REFACTOR: Improving code quality..." && black . && flake8 .'

EOF

# Create a multi-repo management script
echo "📜 Creating multi-repo management utilities..."
cat > /workspaces/control_tower/manage_repos.sh << 'EOF'
#!/bin/bash

# Multi-Repository Management Script for Control Tower

ACTION=${1:-help}

case $ACTION in
    "clone")
        REPO_URL=$2
        if [ -z "$REPO_URL" ]; then
            echo "Usage: ./manage_repos.sh clone <repo_url>"
            exit 1
        fi
        REPO_NAME=$(basename "$REPO_URL" .git)
        echo "Cloning $REPO_NAME into control tower workspace..."
        mkdir -p repos
        cd repos && git clone "$REPO_URL"
        ;;
    
    "status")
        echo "=== Control Tower Repository Status ==="
        echo "Main repo: $(pwd)"
        git status --short
        echo ""
        if [ -d "repos" ]; then
            echo "=== Managed Repositories ==="
            find repos -name ".git" -type d | while read gitdir; do
                repo_path=$(dirname "$gitdir")
                echo "Repository: $repo_path"
                (cd "$repo_path" && git status --short --branch)
                echo ""
            done
        fi
        ;;
    
    "sync")
        echo "=== Syncing All Repositories ==="
        git fetch --all
        if [ -d "repos" ]; then
            find repos -name ".git" -type d | while read gitdir; do
                repo_path=$(dirname "$gitdir")
                echo "Syncing: $repo_path"
                (cd "$repo_path" && git fetch --all)
            done
        fi
        ;;
    
    "push-to")
        TARGET_REPO=$2
        if [ -z "$TARGET_REPO" ]; then
            echo "Usage: ./manage_repos.sh push-to <target_repo_name>"
            echo "Available repos:"
            ls repos/ 2>/dev/null || echo "No repos found"
            exit 1
        fi
        echo "Pushing changes to $TARGET_REPO..."
        if [ -d "repos/$TARGET_REPO" ]; then
            # Copy relevant files to target repo
            echo "Implement your file copying logic here"
            # Then push from target repo
            (cd "repos/$TARGET_REPO" && git add . && git commit -m "Update from control tower" && git push)
        else
            echo "Repository $TARGET_REPO not found in repos/"
        fi
        ;;
    
    "help"|*)
        echo "Control Tower Multi-Repo Management"
        echo "Usage: ./manage_repos.sh <action> [arguments]"
        echo ""
        echo "Actions:"
        echo "  clone <repo_url>     - Clone a repository into the control tower"
        echo "  status               - Show status of all repositories"
        echo "  sync                 - Fetch latest changes from all remotes"
        echo "  push-to <repo>       - Push changes to a specific target repository"
        echo "  help                 - Show this help message"
        ;;
esac
EOF

chmod +x /workspaces/control_tower/manage_repos.sh

# Create a control tower status dashboard
echo "📊 Creating status dashboard..."
cat > /workspaces/control_tower/control_tower_status.py << 'EOF'
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
EOF

chmod +x /workspaces/control_tower/control_tower_status.py

echo ""
echo "✅ Control Tower Multi-Repo Management Hub setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Reload your shell: source ~/.bashrc"
echo "   2. Authenticate with GitHub: gh auth login --web"
echo "   3. Configure Git if needed:"
echo "      git config --global user.name 'Your Name'"
echo "      git config --global user.email 'your.email@example.com'"
echo "   4. Use './manage_repos.sh help' for repository management"
echo "   5. Run 'python3 control_tower_status.py' for status dashboard"
echo ""
echo "🚀 Control Tower is ready for multi-repository development!"