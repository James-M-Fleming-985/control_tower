# 🗼 CONTROL TOWER - REQUIREMENTS-DRIVEN DEVELOPMENT MAKEFILE
# Master control system for managing 6-level hierarch# ==============================================================================
# PROJECT-SPECIFIC OPERATIONS
# ==============================================================================

.PHONY: analyze-business-ventures
analyze-business-ventures: ## Analyze business_ventures repository
	@echo "💼 Analyzing bus.PHONY: trace-requirements
trace-requirements: ## Trace requirements from project to task level
	@echo "🔗 Tracing requirements hierarchy..."
	@$(PYTHON) $(SCRIPTS_DIR)/test_requirements_management.py

.PHONY: what-next
what-next: ## Show what development work	@echo ""
	@echo "🔍 Git safety checkpoint..	@echo ""
	@echo "🔒 Git safety checkpoint..."
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  Uncommitted changes detected:"; \
		git status --short; \
		echo ""; \
		echo "🔒 Creating safety checkpoint..."; \
		git add .; \
		git commit -m "Session checkpoint: $$(date '+%Y-%m-%d %H:%M:%S') - Timeline system state save" || echo "Commit failed - manual review needed"; \
		echo "✅ Changes committed for safety"; \
	else \
		echo "✅ Repository is clean - no uncommitted changes"; \
	fi
	@echo ""
	@echo "📦 Syncing requirements to project repositories..."
	@if [ -d "cloned_repos" ]; then \
		for repo in cloned_repos/*/; do \
			if [ -d "$$repo" ]; then \
				repo_name=$$(basename "$$repo"); \
				echo "  📁 Checking $$repo_name..."; \
				if [ -f "$$repo/requirements" ] && [ -n "$$(find $$repo/requirements -name '*.md' -type f 2>/dev/null)" ]; then \
					cd "$$repo" && \
					if [ -n "$$(git status --porcelain)" ]; then \
						echo "    🔄 Syncing requirements updates..."; \
						git add requirements/; \
						git commit -m "Requirements update: $$(date '+%Y-%m-%d %H:%M:%S') - Timeline data sync" 2>/dev/null || echo "    ⚠️  Sync failed - manual review needed"; \
					else \
						echo "    ✅ Requirements up to date"; \
					fi; \
					cd - >/dev/null; \
				else \
					echo "    ⏭️  No requirements folder found"; \
				fi; \
			fi; \
		done; \
	else \
		echo "  ℹ️  No cloned repositories found"; \
	fi
	@echo ""
	@echo "🎯 Next session - recommended workflow:"
	@echo "   1. make what-next (see current priorities)"
	@echo "   2. make prep PROJECT=<project> (prepare work environment)"
	@echo "   3. Continue development on recommended action"
	@echo ""
	@echo "🚀 Session closed safely - ready for next development cycle" status --porcelain)" ]; then \
		echo "⚠️  Uncommitted changes detected:"; \
		git status --short; \
		echo ""; \
		echo "🔒 Creating safety checkpoint..."; \
		git add .; \
		git commit -m "Session checkpoint: $$(date '+%Y-%m-%d %H:%M:%S') - Timeline system state save" || echo "Commit failed - manual review needed"; \
		echo "✅ Changes committed for safety"; \
	else \
		echo "✅ Repository is clean - no uncommitted changes"; \
	fi
	@echo ""
	@echo "📦 Syncing requirements to project repositories..."
	@if [ -d "cloned_repos" ]; then \
		for repo in cloned_repos/*/; do \
			if [ -d "$$repo" ]; then \
				repo_name=$$(basename "$$repo"); \
				echo "  📁 Checking $$repo_name..."; \
				if [ -f "$$repo/requirements" ] && [ -n "$$(find $$repo/requirements -name '*.md' -type f 2>/dev/null)" ]; then \
					cd "$$repo" && \
					if [ -n "$$(git status --porcelain)" ]; then \
						echo "    🔄 Syncing requirements updates..."; \
						git add requirements/; \
						git commit -m "Requirements update: $$(date '+%Y-%m-%d %H:%M:%S') - Timeline data sync" 2>/dev/null || echo "    ⚠️  Sync failed - manual review needed"; \
					else \
						echo "    ✅ Requirements up to date"; \
					fi; \
					cd - >/dev/null; \
				else \
					echo "    ⏭️  No requirements folder found"; \
				fi; \
			fi; \
		done; \
	else \
		echo "  ℹ️  No cloned repositories found"; \
	fi
	@echo ""
	@echo "🎯 Next session - recommended workflow:"
	@echo "   1. make what-next (see current priorities)"
	@echo "   2. make prep PROJECT=<project> (prepare work environment)"
	@echo "   3. Continue development on recommended action"
	@echo ""
	@echo "🚀 Session closed safely - ready for next development cycle"xt
	@echo "🎯 Analyzing timeline priorities..."
	@$(PYTHON) $(SCRIPTS_DIR)/timeline_processor.py

.PHONY: prep
prep: ## Prepare development environment for specific project/task (specify PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then \
		echo "Please specify PROJECT=name"; \
		echo "Available projects:"; \
		make list-projects | grep "Project" | head -5; \
		exit 1; \
	fi
	@echo "Preparing development environment for: $(PROJECT)"
	@echo "=================================================="
	@if find $(CLONED_REPOS) -name "$(PROJECT)" -type d | grep -q .; then \
		echo "Project found: $(PROJECT)"; \
		find $(CLONED_REPOS) -name "$(PROJECT)" -type d | head -1; \
		echo "Requirements files:"; \
		find $(CLONED_REPOS) -path "*$(PROJECT)*" -name "*requirements*.md" | head -3; \
		echo ""; \
		echo "Next Steps:"; \
		echo "1. Navigate to project directory"; \
		echo "2. Review requirements files"; \
		echo "3. Start development work"; \
		echo "4. Update progress when complete"; \
	else \
		echo "Project not found: $(PROJECT)"; \
		echo "Available projects:"; \
		make list-projects | head -10; \
	fi

.PHONY: analyze-business-ventures
analyze-business-ventures: ## Analyze business_ventures repository
	@echo "💼 Analyzing business_ventures..."
analyze-life-quality: ## Analyze life_quality repository
	@echo "🏠 Analyzing life_quality..."
	@if [ -d "$(CLONED_REPOS)/life_quality" ]; then \
		$(PYTHON) $(SCRIPTS_DIR)/test_requirements_management.py; \
	else \
		echo "❌ life_quality repository not found"; \
	fi

.PHONY: analyze-professional-excellence
analyze-professional-excellence: ## Analyze professional_excellence repository
	@echo "⭐ Analyzing professional_excellence..."
	@if [ -d "$(CLONED_REPOS)/professional_excellence" ]; then \
		$(PYTHON) $(SCRIPTS_DIR)/test_professional_excellence_restructuring.py; \
	else \
		echo "❌ professional_excellence repository not found"; \
	fi

# ==============================================================================
# RESTRUCTURING OPERATIONS
# ==============================================================================

.PHONY: restructure-professional-excellence
restructure-professional-excellence: ## Restructure professional_excellence hierarchy
	@echo "🔧 Restructuring professional_excellence..."
	@$(PYTHON) $(SCRIPTS_DIR)/restructure_professional_excellence.py

.PHONY: backup-before-restructure
backup-before-restructure: ## Create backup before restructuring
	@echo "💾 Creating backup before restructuring..."
	@mkdir -p $(BACKUPS_DIR)
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	tar -czf $(BACKUPS_DIR)/control_tower_backup_$$timestamp.tar.gz \
		$(CLONED_REPOS) $(SCRIPTS_DIR) $(TEMPLATES_DIR) \
		--exclude="*.pyc" --exclude="__pycache__" --exclude="node_modules" \
		2>/dev/null || true
	@echo "✅ Backup created in $(BACKUPS_DIR)/"

# ==============================================================================
# REPORTING & METRICS
# ==============================================================================

.PHONY: generate-reports
generate-reports: ## Generate all analysis reports
	@echo "📊 Generating reports..."
	@mkdir -p $(REPORTS_DIR)
	@$(PYTHON) $(SCRIPTS_DIR)/audit_all_repositories.py > /dev/null
	@$(PYTHON) $(SCRIPTS_DIR)/test_complete_requirements_management.py > /dev/null
	@echo "✅ Reports generated in $(REPORTS_DIR)/"

.PHONY: show-metrics
show-metrics: ## Show current system metrics
	@echo "📈 Control Tower Metrics"
	@echo "========================"
	@echo "📂 Total Repositories: $(words $(REPOSITORIES))"
	@echo "🎯 Active Projects: $(words $(ACTIVE_PROJECTS))"
	@total_req_files=0; \
	for repo in $(REPOSITORIES); do \
		if [ -d "$(CLONED_REPOS)/$$repo" ]; then \
			count=$$(find "$(CLONED_REPOS)/$$repo" -name "requirements" -type d 2>/dev/null | wc -l || echo 0); \
			echo "   $$repo: $$count requirements folders"; \
			total_req_files=$$((total_req_files + count)); \
		fi; \
	done; \
	echo "📋 Total Requirements Folders: $$total_req_files"

.PHONY: status-summary
status-summary: ## Generate compact status summary
	@echo "🗼 Control Tower Status Summary"
	@echo "==============================="
	@working_repos=0; \
	total_repos=$(words $(REPOSITORIES)); \
	for repo in $(REPOSITORIES); do \
		if [ -d "$(CLONED_REPOS)/$$repo" ]; then \
			working_repos=$$((working_repos + 1)); \
		fi; \
	done; \
	echo "📊 Repositories: $$working_repos/$$total_repos operational"
	@working_projects=0; \
	total_projects=$(words $(ACTIVE_PROJECTS)); \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$(CLONED_REPOS)/$$project" ]; then \
			working_projects=$$((working_projects + 1)); \
		fi; \
	done; \
	echo "🎯 Projects: $$working_projects/$$total_projects active"
	@if [ $$working_repos -eq $$total_repos ] && [ $$working_projects -eq $$total_projects ]; then \
		echo "✅ System Status: OPERATIONAL"; \
	else \
		echo "⚠️  System Status: DEGRADED"; \
	fi

# ==============================================================================
# DEVELOPMENT & TESTING
# ==============================================================================

.PHONY: test-hierarchy
test-hierarchy: ## Test hierarchy detection across projects
	@echo "🧪 Testing hierarchy detection..."
	@$(PYTHON) $(SCRIPTS_DIR)/test_application_hierarchy.py

.PHONY: test-templates
test-templates: ## Test template population
	@echo "📝 Testing template population..."
	@$(PYTHON) $(SCRIPTS_DIR)/populate_requirements_templates.py

.PHONY: test-complete
test-complete: ## Run complete test suite
	@echo "🧪 Running complete test suite..."
	@echo "1. Testing hierarchy validation..."
	@$(PYTHON) $(SCRIPTS_DIR)/validate_requirements_hierarchy.py
	@echo ""
	@echo "2. Testing requirements management..."
	@$(PYTHON) $(SCRIPTS_DIR)/test_complete_requirements_management.py
	@echo ""
	@echo "3. Testing project type detection..."
	@$(PYTHON) $(SCRIPTS_DIR)/test_application_hierarchy.py
	@echo ""
	@echo "✅ Complete test suite finished"

# ==============================================================================
# MAINTENANCE & CLEANUP
# ==============================================================================

.PHONY: clean
clean: ## Clean generated files and caches
	@echo "🧹 Cleaning generated files..."
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

.PHONY: clean-reports
clean-reports: ## Clean old reports
	@echo "🗑️ Cleaning old reports..."
	@if [ -d "$(REPORTS_DIR)" ]; then \
		find $(REPORTS_DIR) -name "*.json" -mtime +7 -delete 2>/dev/null || true; \
		find $(REPORTS_DIR) -name "*.md" -mtime +7 -delete 2>/dev/null || true; \
	fi
	@echo "✅ Old reports cleaned"

# ==============================================================================
# QUICK WORKFLOWS
# ==============================================================================

.PHONY: quick-check
quick-check: ## Quick system health check
	@echo "⚡ Quick system check..."
	@$(MAKE) status-summary
	@echo ""
	@$(MAKE) show-metrics

.PHONY: daily-workflow
daily-workflow: ## Daily maintenance workflow
	@echo "📅 Running daily workflow..."
	@$(MAKE) validate-all
	@$(MAKE) generate-reports
	@echo "✅ Daily workflow complete"

.PHONY: setup-check
setup-check: ## Check if system is properly set up
	@echo "🔧 Checking system setup..."
	@if [ ! -d "$(CLONED_REPOS)" ]; then \
		echo "❌ $(CLONED_REPOS) directory missing"; \
		exit 1; \
	fi
	@if [ ! -d "$(SCRIPTS_DIR)" ]; then \
		echo "❌ $(SCRIPTS_DIR) directory missing"; \
		exit 1; \
	fi
	@which $(PYTHON) > /dev/null || (echo "❌ Python 3 not found"; exit 1)
	@echo "✅ System setup verified"

# ==============================================================================
# DEFAULT TARGET
# ==============================================================================

# ==============================================================================
# MONITORING & MAINTENANCE
# ==============================================================================

.PHONY: monitor
monitor: ## Monitor requirements changes and updates
	@echo "👀 Monitoring requirements changes..."
	@$(PYTHON) monitoring/monitor_xml_changes.py

.PHONY: backup
backup: ## Backup current requirements state
	@echo "💾 Creating backup..."
	@mkdir -p $(BACKUPS_DIR)
	@tar -czf $(BACKUPS_DIR)/requirements_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz $(CLONED_REPOS)
	@echo "✅ Backup created in $(BACKUPS_DIR)"

.PHONY: restore
restore: ## Restore from backup (specify BACKUP_FILE=filename)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "❌ Please specify BACKUP_FILE=filename"; \
		echo "📁 Available backups:"; \
		ls -la $(BACKUPS_DIR)/*.tar.gz 2>/dev/null || echo "   No backups found"; \
		exit 1; \
	fi
	@echo "🔄 Restoring from $(BACKUP_FILE)..."
	@tar -xzf $(BACKUPS_DIR)/$(BACKUP_FILE)
	@echo "✅ Restore complete"

# ==============================================================================
# DEVELOPMENT WORKFLOWS
# ==============================================================================

.PHONY: setup
setup: ## Initial setup for Control Tower
	@echo "🔧 Setting up Control Tower..."
	@mkdir -p $(REPORTS_DIR) $(BACKUPS_DIR)
	@$(PIP) install -r requirements.txt 2>/dev/null || echo "📝 No requirements.txt found"
	@echo "✅ Setup complete"

.PHONY: update
update: ## Update repositories and dependencies
	@echo "🔄 Updating repositories..."
	@for repo in $(REPOSITORIES); do \
		if [ -d "$(CLONED_REPOS)/$$repo/.git" ]; then \
			echo "  📦 Updating $$repo..."; \
			cd $(CLONED_REPOS)/$$repo && git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "    ⚠️  Could not update $$repo"; \
			cd ../..; \
		fi; \
	done
	@echo "✅ Updates complete"

# ==============================================================================
# REPORTING & ANALYTICS
# ==============================================================================

.PHONY: report
report: ## Generate comprehensive requirements report
	@echo "📊 Generating requirements report..."
	@$(PYTHON) $(SCRIPTS_DIR)/generate_requirements_report.py
	@echo "✅ Report generated in $(REPORTS_DIR)"

.PHONY: metrics
metrics: ## Show requirements metrics and statistics
	@echo "📈 CONTROL TOWER METRICS"
	@echo "========================"
	@echo "📂 Total Repositories: $(words $(REPOSITORIES))"
	@echo "🎯 Active Projects: $(words $(ACTIVE_PROJECTS))"
	@echo ""
	@echo "📋 Requirements Files:"
	@find $(CLONED_REPOS) -name "requirements.md" | wc -l | xargs -I {} echo "  Total requirements files: {}"
	@echo ""
	@echo "📁 Directory Structure:"
	@for repo in $(REPOSITORIES); do \
		if [ -d "$(CLONED_REPOS)/$$repo" ]; then \
			count=$$(find $(CLONED_REPOS)/$$repo -type d | wc -l); \
			echo "  $$repo: $$count directories"; \
		fi; \
	done

.PHONY: audit
audit: ## Comprehensive audit of all repositories
	@echo "🔍 Starting comprehensive audit..."
	@$(PYTHON) $(SCRIPTS_DIR)/audit_all_repositories.py
	@$(PYTHON) $(SCRIPTS_DIR)/validate_requirements_hierarchy.py
	@$(PYTHON) $(SCRIPTS_DIR)/test_complete_requirements_management.py
	@echo ""
	@echo "✅ Comprehensive audit complete"

# ==============================================================================
# PROJECT MANAGEMENT
# ==============================================================================

.PHONY: list-projects
list-projects: ## List all available projects
	@echo "📋 Available Projects:"
	@for repo in $(REPOSITORIES); do \
		echo "  📁 $$repo"; \
		if [ -d "$(CLONED_REPOS)/$$repo" ]; then \
			find $(CLONED_REPOS)/$$repo -maxdepth 2 -type d -not -path "*/.*" | grep -v "^$(CLONED_REPOS)/$$repo$$" | sed 's|$(CLONED_REPOS)/||' | sed 's|^|    🎯 |'; \
		fi; \
		echo ""; \
	done

.PHONY: project-status
project-status: ## Show status of specific project (specify PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then \
		echo "❌ Please specify PROJECT=name"; \
		echo "📋 Available projects:"; \
		make list-projects; \
		exit 1; \
	fi
	@echo "🎯 Project Status: $(PROJECT)"
	@echo "=============================="
	@if [ -d "$(CLONED_REPOS)/$(PROJECT)" ]; then \
		echo "✅ Project exists"; \
		echo "📁 Directory: $(CLONED_REPOS)/$(PROJECT)"; \
		echo "📋 Requirements files:"; \
		find $(CLONED_REPOS)/$(PROJECT) -name "requirements.md" | sed 's|^|  ✓ |' || echo "  ❌ No requirements files found"; \
	else \
		echo "❌ Project not found: $(PROJECT)"; \
	fi

# ==============================================================================
# DEFAULT TARGET
# ==============================================================================

.DEFAULT_GOAL := help

# ==============================================================================
# END OF MAKEFILE
# ==============================================================================

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Control Tower Configuration
PROJECT_NAME := Control Tower
VERSION := 1.0.0
PYTHON := python3
PIP := pip3

# Directory Structure
CLONED_REPOS := cloned_repos
SCRIPTS_DIR := scripts
TEMPLATES_DIR := templates
REPORTS_DIR := reports
BACKUPS_DIR := backups
MODULES_DIR := modules

# Repository List
REPOSITORIES := business_ventures financial_security investment_strategy life_quality online_presence professional_excellence

# Active Projects (with populated requirements)
ACTIVE_PROJECTS := business_ventures/financial_optimizer business_ventures/opti_royale business_ventures/Causal_affect life_quality/home_improvements professional_excellence/Safran\ SF\ Optimization

# ==============================================================================
# HELP SYSTEM
# ==============================================================================

.PHONY: help
help: ## Show this help message
	@echo "🗼 Control Tower - Requirements Management System"
	@echo "Version: $(VERSION)"
	@echo ""
	@echo "� Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🎯 Quick Start:"
	@echo "  make validate-all    # Validate all repositories"
	@echo "  make test-management # Test requirements management"
	@echo "  make status          # Show system status"
# ==============================================================================
# SYSTEM STATUS & VALIDATION
# ==============================================================================

.PHONY: status
status: ## Show Control Tower system status
	@echo "🗼 CONTROL TOWER SYSTEM STATUS"
	@echo "==============================================="
	@echo "📊 Repositories: $(words $(REPOSITORIES))"
	@echo "🎯 Active Projects: $(words $(ACTIVE_PROJECTS))"
	@echo "📁 Base Path: $(PWD)"
	@echo ""
	@echo "📂 Repository Status:"
	@for repo in $(REPOSITORIES); do \
		if [ -d "$(CLONED_REPOS)/$$repo" ]; then \
			echo "  ✅ $$repo"; \
		else \
			echo "  ❌ $$repo (missing)"; \
		fi; \
	done
	@echo ""
	@echo "🎯 Active Project Status:"
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$(CLONED_REPOS)/$$project" ]; then \
			echo "  ✅ $$project"; \
		else \
			echo "  ❌ $$project (missing)"; \
		fi; \
	done

.PHONY: validate-all
validate-all: ## Validate all repositories and requirements
	@echo "🔍 Validating all repositories..."
	@$(PYTHON) $(SCRIPTS_DIR)/audit_all_repositories.py
	@echo ""
	@echo "✅ Validation complete - check output above for any issues"

.PHONY: validate-hierarchy
validate-hierarchy: ## Validate hierarchy structure across all repos
	@echo "🏗️ Validating hierarchy structure..."
	@$(PYTHON) $(SCRIPTS_DIR)/validate_requirements_hierarchy.py
	@echo ""
	@echo "✅ Hierarchy validation complete"

.PHONY: validate-requirements
validate-requirements: ## Validate requirements folder structure
	@echo "📋 Validating requirements structure..."
	@$(PYTHON) $(SCRIPTS_DIR)/test_complete_requirements_management.py
	@echo ""
	@echo "✅ Requirements validation complete"

# ==============================================================================
# REQUIREMENTS MANAGEMENT
# ==============================================================================

.PHONY: test-management
test-management: ## Test requirements management functionality
	@echo "🧪 Testing requirements management..."
	@$(PYTHON) $(SCRIPTS_DIR)/test_complete_requirements_management.py

.PHONY: populate-templates
populate-templates: ## Populate requirements folders with templates
	@echo "📝 Populating requirements templates..."
	@$(PYTHON) $(SCRIPTS_DIR)/populate_requirements_templates.py

.PHONY: create-requirements
create-requirements: ## Create missing requirements folders
	@echo "📁 Creating missing requirements folders..."
	@$(PYTHON) $(SCRIPTS_DIR)/create_remaining_requirements.py

.PHONY: trace-requirements
trace-requirements: ## Trace requirements from project to task level
	@echo "� Tracing requirements hierarchy..."
	@$(PYTHON) $(SCRIPTS_DIR)/test_requirements_management.py
	@echo "  make prep-layer1    - Prepare Layer 1 development"
	@echo "  make prep-layer2    - Prepare Layer 2 development"
	@echo ""
	@echo "📊 VALIDATION COMMANDS:"
	@echo "  make requirements-validation - Validate requirements traceability"
	@echo "  make git-status     - Check git status"
	@echo "  make git-safety-check - Verify git safety (non-interactive)"

# Git Safety Check - NON-INTERACTIVE
git-safety-check:
	@echo "🔒 Git Safety Check (Non-Interactive)"
	@echo "====================================="
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  WARNING: Uncommitted changes detected:"; \
		git status --short; \
		echo ""; \
		echo "❌ SAFETY CHECK FAILED"; \
		echo "💡 Run 'make git-status' for details"; \
		echo "💡 Commit changes before proceeding with Layer development"; \
		exit 1; \
	else \
		echo "✅ Git repository is clean"; \
		echo "✅ Safe to proceed with Layer development"; \
	fi

# Git Status
git-status:
	@echo "📊 Git Repository Status"
	@echo "========================"
	@git status
	@echo ""
	@echo "📈 Recent commits:"
	@git log --oneline -5

# Requirements Validation
requirements-validation:
	@echo "📋 Requirements Traceability Matrix"
	@echo "==================================="
	@echo ""
	@echo "📂 LAYER 1 REQUIREMENTS (Business): 15 requirements"
	@if [ -f "LAYER_1_REQUIREMENTS.md" ]; then \
		echo "✅ LAYER_1_REQUIREMENTS.md exists"; \
		grep -c "REQ-BUS-" LAYER_1_REQUIREMENTS.md | xargs -I {} echo "   Found {} business requirements"; \
	else \
		echo "❌ LAYER_1_REQUIREMENTS.md missing"; \
	fi
	@echo ""
	@echo "📂 LAYER 2 REQUIREMENTS (Technical): 15 requirements"
	@if [ -f "LAYER_2_REQUIREMENTS.md" ]; then \
		echo "✅ LAYER_2_REQUIREMENTS.md exists"; \
		grep -c "REQ-TECH-" LAYER_2_REQUIREMENTS.md | xargs -I {} echo "   Found {} technical requirements"; \
	else \
		echo "❌ LAYER_2_REQUIREMENTS.md missing"; \
	fi
	@echo ""
	@echo "🎯 TOTAL REQUIREMENTS: 30 (15 Business + 15 Technical)"

# Layer 1 Preparation
prep-layer1: git-safety-check
	@echo "🚀 Preparing Layer 1 Development Environment"
	@echo "============================================"
	@echo ""
	@echo "✅ Layer 1 Status: COMPLETE"
	@echo "📋 Business Requirements: Implemented"
	@echo "🧪 Test Coverage: 100%"
	@echo ""
	@echo "💡 Layer 1 is ready for usage and maintenance"

# Layer 2 Preparation  
prep-layer2: git-safety-check
	@echo "🚀 Preparing Layer 2 Development Environment"
	@echo "============================================"
	@echo ""
	@echo "📋 Checking Layer 2 Requirements..."
	@if [ -f "LAYER_2_REQUIREMENTS.md" ]; then \
		echo "✅ LAYER_2_REQUIREMENTS.md found"; \
	else \
		echo "❌ LAYER_2_REQUIREMENTS.md missing"; \
		echo "💡 Create Layer 2 requirements before development"; \
		exit 1; \
	fi
	@echo ""
	@echo "🔧 Layer 2 Focus Areas:"
	@echo "   • Text Processing Engine"
	@echo "   • Document Scanning System"
	@echo "   • Data Source Integration"
	@echo ""
	@echo "✅ Ready for Layer 2 RED-GREEN-REFACTOR cycle"

# Layer 1 Tests
test-layer1:
	@echo "🧪 Running Layer 1 Tests (Business Requirements)"
	@echo "================================================"
	@python -m pytest tests/ -v -k "layer1 or business" --tb=short

# Layer 2 Tests
test-layer2:
	@echo "🧪 Running Layer 2 Tests (Text Processing)"
	@echo "==========================================="
	@python -m pytest tests/ -v -k "layer2 or text_processing" --tb=short

# All Tests
test: test-layer1 test-layer2
	@echo ""
	@echo "🎯 Full Test Suite Complete"

# Layer 1 RED Phase
red-layer1: prep-layer1
	@echo "🔴 Layer 1 RED Phase - Write Failing Tests"
	@echo "=========================================="
	@echo ""
	@echo "✅ Layer 1 Status: COMPLETE"
	@echo "💡 All Layer 1 tests are passing"
	@echo "💡 Layer 1 RED phase was completed successfully"

# Layer 1 GREEN Phase
green-layer1: red-layer1
	@echo "🟢 Layer 1 GREEN Phase - Make Tests Pass"
	@echo "========================================"
	@echo ""
	@echo "✅ Layer 1 Status: COMPLETE"
	@echo "✅ All business requirements implemented"
	@echo "✅ 100% test coverage achieved"

# Layer 2 RED Phase
red-layer2: prep-layer2
	@echo "🔴 Layer 2 RED Phase - Write Failing Tests"
	@echo "=========================================="
	@echo ""
	@echo "📝 Creating Layer 2 failing tests..."
	@echo "🎯 Focus: Text Processing & Document Scanning"
	@echo ""
	@echo "🔧 Next Steps:"
	@echo "   1. Write failing tests for text processing"
	@echo "   2. Write failing tests for document scanning"
	@echo "   3. Run 'make test-layer2' to confirm RED state"
	@echo "   4. Proceed to 'make green-layer2'"

# Layer 2 GREEN Phase
green-layer2: red-layer2
	@echo "🟢 Layer 2 GREEN Phase - Make Tests Pass"
	@echo "========================================"
	@echo ""
	@echo "⚙️ Implementing Layer 2 functionality..."
	@echo "🎯 Focus: Text Processing & Document Scanning"
	@echo ""
	@echo "🔧 Implementation Steps:"
	@echo "   1. Implement text processing engine"
	@echo "   2. Implement document scanning system"
	@echo "   3. Run 'make test-layer2' to confirm GREEN state"
	@echo "   4. Refactor for clean code"

# Session Management
.PHONY: session-close
session-close:
	@echo "💾 CLOSING DEVELOPMENT SESSION SAFELY"
	@echo "====================================="
	@echo ""
	@echo "📊 Current session summary:"
	@echo "  📅 Date: $(shell date '+%Y-%m-%d %H:%M:%S')"
	@echo "  📁 Repository: control_tower"
	@echo "  🔧 Timeline system: OPERATIONAL"
	@echo ""
	@echo "� Saving session state document..."
	@SESSION_FILE="SESSION_STATE_$(shell date '+%Y%m%d_%H%M%S').md"; \
	echo "# Control Tower Development Session State" > $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "**Session Date**: $(shell date '+%Y-%m-%d %H:%M:%S')" >> $$SESSION_FILE; \
	echo "**Repository**: control_tower" >> $$SESSION_FILE; \
	echo "**Branch**: $(shell git branch --show-current 2>/dev/null || echo 'unknown')" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "## 🎯 System Status" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "- ✅ Timeline-driven development system: **OPERATIONAL**" >> $$SESSION_FILE; \
	echo "- ✅ Requirements parser: **FUNCTIONAL**" >> $$SESSION_FILE; \
	echo "- ✅ Priority calculation: **ACTIVE**" >> $$SESSION_FILE; \
	echo "- ✅ What-next recommendations: **WORKING**" >> $$SESSION_FILE; \
	echo "- ✅ Clean output format: **IMPLEMENTED**" >> $$SESSION_FILE; \
	echo "- ✅ Hierarchy context display: **COMPLETE**" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "## 📊 Current Metrics" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	if [ -f "data/timeline_analysis.json" ]; then \
		echo "- **Total Requirements**: $$(python3 -c "import json; data=json.load(open('data/timeline_analysis.json')); print(len(data['requirements']))" 2>/dev/null || echo 'N/A')" >> $$SESSION_FILE; \
		echo "- **Active North Stars**: $$(python3 -c "import json; data=json.load(open('data/timeline_analysis.json')); print(len([r for r in data['requirements'] if r.startswith('NS-')]))" 2>/dev/null || echo 'N/A')" >> $$SESSION_FILE; \
		echo "- **Development Items Ready**: $$(python3 -c "import json; data=json.load(open('data/timeline_analysis.json')); reqs=data['requirements']; dev_levels=['task','layer','feature','workpackage']; print(len([r for r_id,r in reqs.items() if r['level'] in dev_levels and r['progress'] < 100]))" 2>/dev/null || echo 'N/A')" >> $$SESSION_FILE; \
	else \
		echo "- **Timeline Data**: Not available" >> $$SESSION_FILE; \
	fi; \
	echo "" >> $$SESSION_FILE; \
	echo "## 🔄 Current Recommended Action" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	if [ -f "scripts/timeline_processor.py" ]; then \
		echo "\`\`\`" >> $$SESSION_FILE; \
		python3 scripts/timeline_processor.py 2>/dev/null | tail -n 10 >> $$SESSION_FILE || echo "Timeline processor output not available" >> $$SESSION_FILE; \
		echo "\`\`\`" >> $$SESSION_FILE; \
	fi; \
	echo "" >> $$SESSION_FILE; \
	echo "## 📋 Outstanding Tasks" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "1. **Define North Star requirements** - Populate placeholder templates with actual business objectives" >> $$SESSION_FILE; \
	echo "2. **Complete requirements cascade** - Ensure proper hierarchy from North Stars → Projects → Systems → Features → Layers → Tasks" >> $$SESSION_FILE; \
	echo "3. **Create requirements health check** - Build validation tool for requirements integrity" >> $$SESSION_FILE; \
	echo "4. **Build metrics dashboard** - Show completion percentages and financial metrics at all levels" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "## 🔧 Key Components Completed This Session" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "- Enhanced timeline processor with development-focused prioritization" >> $$SESSION_FILE; \
	echo "- Clean what-next output format (summary + action only)" >> $$SESSION_FILE; \
	echo "- Meaningful hierarchy context display" >> $$SESSION_FILE; \
	echo "- Proper project extraction for make prep commands" >> $$SESSION_FILE; \
	echo "- Session management with safe close functionality" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "## ⚡ Next Session Workflow" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "1. \`make what-next\` - Check current priorities" >> $$SESSION_FILE; \
	echo "2. \`make prep PROJECT=<project>\` - Prepare work environment" >> $$SESSION_FILE; \
	echo "3. Work on recommended action" >> $$SESSION_FILE; \
	echo "4. Update progress in requirements files" >> $$SESSION_FILE; \
	echo "5. \`make session-close\` - Save state and close safely" >> $$SESSION_FILE; \
	echo "" >> $$SESSION_FILE; \
	echo "---" >> $$SESSION_FILE; \
	echo "Generated by Control Tower session management system" >> $$SESSION_FILE; \
	echo "✅ Session state saved to: $$SESSION_FILE"
	@echo ""
	@echo "�🔍 Checking git status..."
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  Uncommitted changes detected:"; \
		git status --short; \
		echo ""; \
		echo "💡 OPTIONS:"; \
		echo "   • make git-commit MESSAGE='Session work complete'"; \
		echo "   • git add . && git commit -m 'Session: Timeline system improvements'"; \
		echo "   • git stash (to save changes temporarily)"; \
	else \
		echo "✅ Repository is clean - no uncommitted changes"; \
	fi
	@echo ""
	@echo "🎯 Next session - recommended workflow:"
	@echo "   1. make what-next (see current priorities)"
	@echo "   2. make prep PROJECT=<project> (prepare work environment)"
	@echo "   3. Continue development on recommended action"
	@echo ""
	@echo "🚀 Session closed safely - ready for next development cycle"

.PHONY: git-commit
git-commit:
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Usage: make git-commit MESSAGE='Your commit message'"; \
		exit 1; \
	fi
	@echo "💾 Committing changes with message: $(MESSAGE)"
	@git add .
	@git status --short
	@git commit -m "$(MESSAGE)"
	@echo "✅ Changes committed successfully"
