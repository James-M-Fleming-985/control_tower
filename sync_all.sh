#!/bin/bash
# 🔄 CONTROL TOWER: Sync All Repositories
# Pulls latest from all GitHub repositories into cloned_repos/

set -e  # Exit on any error

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="/workspaces/control_tower/sync_status/sync_all_$TIMESTAMP.log"
BACKUP_DIR="/workspaces/control_tower/backups/pre_sync"

echo "🏗️  CONTROL TOWER SYNC OPERATION STARTING" | tee $LOG_FILE
echo "Timestamp: $TIMESTAMP" | tee -a $LOG_FILE
echo "=========================================" | tee -a $LOG_FILE

# Create necessary directories
mkdir -p /workspaces/control_tower/sync_status
mkdir -p /workspaces/control_tower/backups/pre_sync
mkdir -p /workspaces/control_tower/cloned_repos

cd /workspaces/control_tower/cloned_repos

# Repository mapping based on your GitHub account
REPOSITORIES=(
    "professional_excellence"
    "business_ventures" 
    "investment_strategy"
    "financial_security"
    "life_quality"
    "online_presence"
    "financial_optimizer"
    "Causal_affect"
    "home_improvements"
    "opti_royale"
    "contract_projects"
)

# Function to sync a single repository
sync_repository() {
    local repo_name=$1
    echo "📥 Syncing $repo_name..." | tee -a $LOG_FILE
    
    if [ -d "$repo_name" ]; then
        echo "   Repository exists, pulling latest..." | tee -a $LOG_FILE
        cd "$repo_name"
        
        # Check for uncommitted changes
        if ! git diff-index --quiet HEAD --; then
            echo "   ⚠️  WARNING: Uncommitted changes detected in $repo_name" | tee -a $LOG_FILE
            echo "   Creating backup before pull..." | tee -a $LOG_FILE
            cp -r "../$repo_name" "$BACKUP_DIR/${repo_name}_backup_$TIMESTAMP"
        fi
        
        # Pull latest
        if git pull origin main; then
            echo "   ✅ Successfully synced $repo_name" | tee -a $LOG_FILE
        else
            echo "   ❌ Failed to sync $repo_name" | tee -a $LOG_FILE
            return 1
        fi
        cd ..
    else
        echo "   Repository doesn't exist, cloning..." | tee -a $LOG_FILE
        if gh repo clone "James-M-Fleming-985/$repo_name"; then
            echo "   ✅ Successfully cloned $repo_name" | tee -a $LOG_FILE
        else
            echo "   ❌ Failed to clone $repo_name" | tee -a $LOG_FILE
            return 1
        fi
    fi
}

# Sync all repositories
FAILED_REPOS=()
for repo in "${REPOSITORIES[@]}"; do
    if ! sync_repository "$repo"; then
        FAILED_REPOS+=("$repo")
    fi
done

# Summary
echo "=========================================" | tee -a $LOG_FILE
echo "🏁 SYNC OPERATION COMPLETE" | tee -a $LOG_FILE
echo "Timestamp: $(date '+%Y%m%d_%H%M%S')" | tee -a $LOG_FILE

if [ ${#FAILED_REPOS[@]} -eq 0 ]; then
    echo "✅ All repositories synced successfully" | tee -a $LOG_FILE
else
    echo "❌ Failed repositories: ${FAILED_REPOS[*]}" | tee -a $LOG_FILE
    echo "Check individual repository access and authentication" | tee -a $LOG_FILE
fi

# Update last sync status
echo "$TIMESTAMP" > /workspaces/control_tower/sync_status/last_sync.timestamp
echo "Log: $LOG_FILE" >> /workspaces/control_tower/sync_status/last_sync.timestamp

echo "📊 Run './status_dashboard.sh' to see current status"