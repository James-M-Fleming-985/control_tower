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
