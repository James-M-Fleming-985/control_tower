#!/bin/bash
# EMERGENCY PROTECTION SYSTEM
# Prevents data loss by auto-committing and syncing work every few minutes

echo "🛡️  EMERGENCY PROTECTION SYSTEM ACTIVATED"
echo "This will auto-commit and sync your work every 5 minutes to prevent data loss"

# Function to auto-commit all changes
auto_commit() {
    timestamp=$(date '+%Y%m%d_%H%M%S')
    cd /workspaces/control_tower
    
    # Add all changes
    git add -A
    
    # Check if there are changes to commit
    if ! git diff --cached --quiet; then
        git commit -m "AUTO-COMMIT: Emergency protection backup - $timestamp"
        echo "✅ Auto-committed changes at $timestamp"
        
        # Try to push to remote
        if git push origin main 2>/dev/null; then
            echo "✅ Successfully pushed to GitHub"
        else
            echo "⚠️  Could not push to GitHub - but local commit saved"
        fi
    else
        echo "ℹ️  No changes to commit at $timestamp"
    fi
}

# Function to backup to multiple locations
emergency_backup() {
    timestamp=$(date '+%Y%m%d_%H%M%S')
    backup_dir="/tmp/emergency_backup_$timestamp"
    
    mkdir -p "$backup_dir"
    cp -r /workspaces/control_tower/* "$backup_dir"/ 2>/dev/null
    echo "✅ Emergency backup created at $backup_dir"
    
    # Compress the backup
    tar -czf "/tmp/emergency_backup_$timestamp.tar.gz" -C "$backup_dir" .
    echo "✅ Compressed backup created at /tmp/emergency_backup_$timestamp.tar.gz"
}

# Initial backup
emergency_backup

# Auto-commit loop every 5 minutes
while true; do
    sleep 300  # 5 minutes
    auto_commit
    
    # Full backup every 30 minutes
    if [ $(($(date +%M) % 30)) -eq 0 ]; then
        emergency_backup
    fi
done