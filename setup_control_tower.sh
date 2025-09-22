#!/bin/bash
# 🏗️ CONTROL TOWER SETUP SCRIPT
# Implements the robust architecture for multi-repository management

set -e  # Exit on any error

echo "🏗️ CONTROL TOWER ARCHITECTURE SETUP"
echo "=================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_STATE_DIR="workspace_state"
MANAGED_PROJECTS_DIR="managed_projects"
BACKUP_DIR="$WORKSPACE_STATE_DIR/backups"
SESSION_ID="$(date +%Y-%m-%d-%H%M%S)"

# Repository list (based on your GitHub repos)
REPOSITORIES=(
    "contract_projects"
    "investment_strategy"
    "business_ventures"
    "financial_security"
    "professional_excellence"
    "life_quality"
    "online_presence"
    "financial_optimizer"
    "Causal_affect"
    "home_improvements"
    "opti_royale"
)

echo -e "${BLUE}Session ID: $SESSION_ID${NC}"

# Function to log with timestamp
log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR: $1${NC}"
}

# Create directory structure
setup_directories() {
    log "Setting up directory structure..."
    
    mkdir -p "$WORKSPACE_STATE_DIR"
    mkdir -p "$MANAGED_PROJECTS_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$WORKSPACE_STATE_DIR/logs"
    mkdir -p "$WORKSPACE_STATE_DIR/manifests"
    
    log "Directory structure created"
}

# Initialize workspace state tracking
init_workspace_state() {
    log "Initializing workspace state tracking..."
    
    cat > "$WORKSPACE_STATE_DIR/workspace_state.json" << EOF
{
  "session_id": "$SESSION_ID",
  "created": "$(date -Iseconds)",
  "last_updated": "$(date -Iseconds)",
  "repositories": {},
  "health_status": "INITIALIZING",
  "backup_manifest": {
    "last_full_backup": null,
    "files_backed_up": 0,
    "backup_location": null
  }
}
EOF
    
    log "Workspace state initialized"
}

# Check GitHub connectivity
check_github_connectivity() {
    log "Checking GitHub connectivity..."
    
    if gh auth status > /dev/null 2>&1; then
        log "GitHub authentication verified"
    else
        error "GitHub authentication failed. Please run 'gh auth login'"
        exit 1
    fi
    
    # Test API access
    if gh api user > /dev/null 2>&1; then
        log "GitHub API access verified"
    else
        error "GitHub API access failed"
        exit 1
    fi
}

# Set up Git submodules for each repository
setup_submodules() {
    log "Setting up Git submodules..."
    
    cd "$MANAGED_PROJECTS_DIR"
    
    for repo in "${REPOSITORIES[@]}"; do
        log "Setting up submodule for $repo..."
        
        # Check if repository exists on GitHub
        if gh repo view "James-M-Fleming-985/$repo" > /dev/null 2>&1; then
            # Add as submodule if not already present
            if [ ! -d "$repo" ]; then
                git submodule add "https://github.com/James-M-Fleming-985/$repo.git" "$repo"
                log "Added submodule: $repo"
            else
                log "Submodule already exists: $repo"
            fi
        else
            warn "Repository not found on GitHub: $repo (will skip)"
        fi
    done
    
    cd ..
    
    # Initialize and update all submodules
    git submodule init
    git submodule update
    
    log "Submodules setup complete"
}

# Create workspace health check function
create_health_check() {
    log "Creating health check script..."
    
    cat > "$WORKSPACE_STATE_DIR/health_check.sh" << 'EOF'
#!/bin/bash
# Workspace Health Check Script

echo "🏥 WORKSPACE HEALTH CHECK"
echo "========================"

HEALTH_STATUS="HEALTHY"
ISSUES=()

# Check Git status for control_tower
echo "Checking control_tower repository..."
if git status --porcelain | grep -q .; then
    ISSUES+=("control_tower has uncommitted changes")
    HEALTH_STATUS="WARNING"
fi

# Check submodules
echo "Checking submodules..."
cd managed_projects 2>/dev/null || {
    ISSUES+=("managed_projects directory missing")
    HEALTH_STATUS="ERROR"
    echo "❌ CRITICAL: managed_projects directory not found"
    exit 1
}

for dir in */; do
    if [ -d "$dir" ]; then
        repo_name=${dir%/}
        echo "  Checking $repo_name..."
        
        cd "$dir"
        
        # Check if it's a Git repository
        if [ ! -d ".git" ]; then
            ISSUES+=("$repo_name is not a Git repository")
            HEALTH_STATUS="ERROR"
        else
            # Check for uncommitted changes
            if git status --porcelain | grep -q .; then
                ISSUES+=("$repo_name has uncommitted changes")
                HEALTH_STATUS="WARNING"
            fi
            
            # Check if remote is accessible
            if ! git fetch --dry-run > /dev/null 2>&1; then
                ISSUES+=("$repo_name cannot reach remote")
                HEALTH_STATUS="ERROR"
            fi
        fi
        
        cd ..
    fi
done

cd ..

# Report results
echo ""
echo "🎯 HEALTH STATUS: $HEALTH_STATUS"

if [ ${#ISSUES[@]} -eq 0 ]; then
    echo "✅ All checks passed"
else
    echo "⚠️  Issues found:"
    for issue in "${ISSUES[@]}"; do
        echo "   - $issue"
    done
fi

# Update workspace state
jq --arg status "$HEALTH_STATUS" --arg timestamp "$(date -Iseconds)" \
   '.health_status = $status | .last_health_check = $timestamp' \
   workspace_state/workspace_state.json > workspace_state/workspace_state.tmp && \
   mv workspace_state/workspace_state.tmp workspace_state/workspace_state.json

echo ""
echo "Health check complete. Status: $HEALTH_STATUS"
EOF

    chmod +x "$WORKSPACE_STATE_DIR/health_check.sh"
    log "Health check script created"
}

# Create enhanced Makefile
create_makefile() {
    log "Creating enhanced Makefile..."
    
    cat > "Makefile.control_tower" << 'EOF'
# 🏗️ CONTROL TOWER MAKEFILE
# Robust multi-repository management system

.PHONY: help health-check sync-all work-on save-work session-backup restore-state

# Default target
help:
	@echo "🏗️ CONTROL TOWER COMMANDS"
	@echo "========================"
	@echo ""
	@echo "🏥 HEALTH & STATUS:"
	@echo "  health-check     - Check workspace health"
	@echo "  status           - Show current workspace status"
	@echo ""
	@echo "🔄 REPOSITORY MANAGEMENT:"
	@echo "  sync-all         - Sync all repositories"
	@echo "  work-on PROJECT= - Set up to work on specific project"
	@echo "  save-work PROJECT= MESSAGE= - Save work with verification"
	@echo ""
	@echo "💾 BACKUP & RECOVERY:"
	@echo "  session-backup   - Create full session backup"
	@echo "  restore-state    - Restore from last backup"
	@echo ""
	@echo "🧹 MAINTENANCE:"
	@echo "  clean            - Clean temporary files"
	@echo "  setup            - Initial setup of control tower"

# Health check
health-check:
	@./workspace_state/health_check.sh

# Show current status
status:
	@echo "🎯 WORKSPACE STATUS"
	@echo "=================="
	@jq -r '"Session: " + .session_id' workspace_state/workspace_state.json
	@jq -r '"Health: " + .health_status' workspace_state/workspace_state.json
	@jq -r '"Last Updated: " + .last_updated' workspace_state/workspace_state.json
	@echo ""
	@echo "📊 REPOSITORY STATUS:"
	@cd managed_projects && for dir in */; do \
		if [ -d "$$dir" ]; then \
			repo=$${dir%/}; \
			echo -n "  $$repo: "; \
			cd "$$dir"; \
			if git status --porcelain | grep -q .; then \
				echo "📝 has changes"; \
			else \
				echo "✅ clean"; \
			fi; \
			cd ..; \
		fi; \
	done

# Sync all repositories
sync-all:
	@echo "🔄 SYNCING ALL REPOSITORIES"
	@echo "=========================="
	@cd managed_projects && \
	for dir in */; do \
		if [ -d "$$dir" ]; then \
			repo=$${dir%/}; \
			echo "Syncing $$repo..."; \
			cd "$$dir"; \
			git fetch origin; \
			git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "Pull failed for $$repo"; \
			cd ..; \
		fi; \
	done
	@echo "✅ Sync complete"

# Work on specific project
work-on:
	@if [ -z "$(PROJECT)" ]; then \
		echo "❌ Please specify PROJECT=<name>"; \
		exit 1; \
	fi
	@if [ ! -d "managed_projects/$(PROJECT)" ]; then \
		echo "❌ Project $(PROJECT) not found"; \
		exit 1; \
	fi
	@echo "🎯 SETTING UP WORK ON: $(PROJECT)"
	@echo "=============================="
	@cd managed_projects/$(PROJECT) && \
		git status && \
		echo "" && \
		echo "✅ Ready to work on $(PROJECT)" && \
		echo "📁 Location: managed_projects/$(PROJECT)" && \
		echo "🔧 Remember to use 'make save-work PROJECT=$(PROJECT) MESSAGE=\"your message\"' when done"

# Save work with verification
save-work:
	@if [ -z "$(PROJECT)" ]; then \
		echo "❌ Please specify PROJECT=<name>"; \
		exit 1; \
	fi
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Please specify MESSAGE=\"commit message\""; \
		exit 1; \
	fi
	@echo "💾 SAVING WORK: $(PROJECT)"
	@echo "======================"
	@cd managed_projects/$(PROJECT) && \
		echo "Current status:" && \
		git status && \
		echo "" && \
		echo "Adding all changes..." && \
		git add . && \
		echo "Committing with message: $(MESSAGE)" && \
		git commit -m "$(MESSAGE)" && \
		echo "Pushing to GitHub..." && \
		git push origin HEAD && \
		echo "✅ Work saved and pushed to GitHub" && \
		echo "🔗 Verify at: https://github.com/James-M-Fleming-985/$(PROJECT)"

# Create session backup
session-backup:
	@echo "💾 CREATING SESSION BACKUP"
	@echo "========================="
	@mkdir -p workspace_state/backups
	@SESSION_ID=$$(jq -r '.session_id' workspace_state/workspace_state.json); \
	BACKUP_FILE="workspace_state/backups/session_$${SESSION_ID}.tar.gz"; \
	echo "Creating backup: $$BACKUP_FILE"; \
	tar -czf "$$BACKUP_FILE" \
		--exclude='.git' \
		--exclude='workspace_state/backups' \
		--exclude='node_modules' \
		--exclude='__pycache__' \
		managed_projects/ workspace_state/ && \
	echo "✅ Backup created: $$BACKUP_FILE" && \
	ls -lh "$$BACKUP_FILE"

# Setup control tower
setup:
	@./setup_control_tower.sh

# Clean temporary files
clean:
	@echo "🧹 CLEANING WORKSPACE"
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"
EOF

    log "Enhanced Makefile created"
}

# Main setup execution
main() {
    echo -e "${BLUE}Starting Control Tower setup...${NC}"
    
    setup_directories
    init_workspace_state
    check_github_connectivity
    setup_submodules
    create_health_check
    create_makefile
    
    log "Creating evidence log for this setup..."
    cat > "$WORKSPACE_STATE_DIR/logs/setup_$SESSION_ID.log" << EOF
# CONTROL TOWER SETUP EVIDENCE LOG
Session: $SESSION_ID
Date: $(date)
User: $(whoami)
Location: $(pwd)

## Setup Actions Completed:
✅ Directory structure created
✅ Workspace state tracking initialized  
✅ GitHub connectivity verified
✅ Git submodules configured
✅ Health check script created
✅ Enhanced Makefile created

## Verification:
- Session ID: $SESSION_ID
- Workspace state file: $WORKSPACE_STATE_DIR/workspace_state.json
- Health check script: $WORKSPACE_STATE_DIR/health_check.sh
- Enhanced Makefile: Makefile.control_tower

## Next Steps:
1. Run 'make -f Makefile.control_tower health-check' to verify setup
2. Run 'make -f Makefile.control_tower sync-all' to sync repositories
3. Start working with 'make -f Makefile.control_tower work-on PROJECT=<name>'
EOF
    
    echo ""
    echo -e "${GREEN}🎉 CONTROL TOWER SETUP COMPLETE!${NC}"
    echo -e "${BLUE}Session ID: $SESSION_ID${NC}"
    echo ""
    echo "📋 Next steps:"
    echo "1. Run: make -f Makefile.control_tower health-check"
    echo "2. Run: make -f Makefile.control_tower sync-all"
    echo "3. Start working: make -f Makefile.control_tower work-on PROJECT=contract_projects"
    echo ""
    echo "📖 Full documentation: CONTROL_TOWER_ARCHITECTURE_BLUEPRINT.md"
}

# Run main function
main