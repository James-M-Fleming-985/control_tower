#!/bin/bash

# Control Tower - Auto Sync Script
# This script automatically pulls the latest changes from all your repositories
# Run this when you start your Codespace to ensure you have the latest documentation

echo "🏗️  Control Tower - Syncing all repositories..."

REPOS_DIR="cloned_repos"

# Create repos directory if it doesn't exist
mkdir -p $REPOS_DIR

# Parse repositories from repos.json
REPOS=($(python3 -c "
import json
with open('repos.json', 'r') as f:
    data = json.load(f)
    for repo in data['repositories']:
        print(repo['name'])
"))

for repo in "${REPOS[@]}"; do
    echo "📥 Syncing $repo..."
    
    if [ -d "$REPOS_DIR/$repo" ]; then
        # Repository exists, pull latest changes
        cd "$REPOS_DIR/$repo"
        git pull origin main
        cd ../..
        echo "✅ $repo updated"
    else
        # Repository doesn't exist, clone it
        echo "🔄 Cloning $repo for the first time..."
        git clone "https://github.com/James-M-Fleming-985/$repo.git" "$REPOS_DIR/$repo"
        echo "✅ $repo cloned"
    fi
done

echo "🎉 All repositories synced! Your documentation is now up to date."
echo ""
echo "📁 Your repos are available in:"
for repo in "${REPOS[@]}"; do
    echo "   - cloned_repos/$repo/"
done
