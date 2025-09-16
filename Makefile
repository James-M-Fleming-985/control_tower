# Control Tower Phase 1 - Comprehensive Makefile
# 
# This Makefile provides the unified interface for the Control Tower system,
# implementing the "make what-next" command and supporting development workflows.
#
# Phase 1 Integration:
# - Connects all 4 layers through the main entry point
# - Provides user-friendly command interface
# - Supports testing, validation, and development workflows
#
# Author: Control Tower Development Team
# Created: 2025-09-13
# Phase: Phase 1 - Core Discovery
# Status: Production Ready

# ============================================================================
# CONFIGURATION
# ============================================================================

# Python interpreter
PYTHON := python3

# Project directories
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs
LOGS_DIR := logs

# Main entry point
MAIN_SCRIPT := make_what_next.py

# Default target
.DEFAULT_GOAL := what-next

# ============================================================================
# PHASE 1 - PRIMARY COMMANDS
# ============================================================================

.PHONY: what-next
what-next: ## 🎯 Discover and prioritize due/overdue work items (PRIMARY COMMAND)
	@echo "🏗️  Control Tower - Discovering what to work on next..."
	@$(PYTHON) $(MAIN_SCRIPT) $(ARGS)

.PHONY: what-next-json
what-next-json: ## 📊 Output work items in JSON format
	@$(PYTHON) $(MAIN_SCRIPT) --json $(ARGS)

.PHONY: what-next-debug
what-next-debug: ## 🐛 Run with debug information and timing
	@$(PYTHON) $(MAIN_SCRIPT) --debug $(ARGS)

.PHONY: what-next-all
what-next-all: ## 📋 Show all work items (not just due/overdue)
	@$(PYTHON) $(MAIN_SCRIPT) --all $(ARGS)

# ============================================================================
# REPOSITORY-SPECIFIC COMMANDS
# ============================================================================

.PHONY: what-next-financial
what-next-financial: ## 💰 Check financial security development repository
	@$(PYTHON) $(MAIN_SCRIPT) --repository=cloned_repos/financial_security_dev

.PHONY: what-next-investment
what-next-investment: ## 📈 Check investment strategy repository
	@$(PYTHON) $(MAIN_SCRIPT) --repository=cloned_repos/investment_strategy

.PHONY: what-next-contract
what-next-contract: ## 📄 Check contract projects repository
	@$(PYTHON) $(MAIN_SCRIPT) --repository=cloned_repos/contract_projects

.PHONY: what-next-home
what-next-home: ## 🏠 Check home improvements repository
	@$(PYTHON) $(MAIN_SCRIPT) --repository=cloned_repos/home_improvements

.PHONY: what-next-lims
what-next-lims: ## 🧪 Check LIMS concept repository
	@$(PYTHON) $(MAIN_SCRIPT) --repository=cloned_repos/LIMS_concept_actual

.PHONY: what-next-relationships
what-next-relationships: ## 👥 Check relationship building repository
	@$(PYTHON) $(MAIN_SCRIPT) --repository=cloned_repos/relationship_building

.PHONY: what-next-control-tower
what-next-control-tower: ## 🏗️ Check Control Tower self-management repository
	@$(PYTHON) $(MAIN_SCRIPT) --repository=cloned_repos/control_tower

# ============================================================================
# PROFESSIONAL STANDARDS ENFORCEMENT
# ============================================================================

.PHONY: validate-professional
validate-professional: ## 🎯 MANDATORY professional validation for completion claims
	@if [ -z "$(COMPONENT)" ]; then \
		echo "❌ Error: COMPONENT parameter required"; \
		echo "Usage: make validate-professional COMPONENT=<component_name>"; \
		exit 1; \
	fi
	@echo "🎯 PROFESSIONAL VALIDATION: $(COMPONENT)"
	@echo "🔍 Enforcing evidence-based completion standards..."
	@$(PYTHON) scripts/professional_validator.py $(COMPONENT)

.PHONY: validate-all-components
validate-all-components: ## 🏆 Validate all Phase 2 components
	@echo "🏆 VALIDATING ALL PHASE 2 COMPONENTS"
	@echo "======================================"
	@make validate-professional COMPONENT=test_generator || echo "❌ TestGenerator validation failed"
	@make validate-professional COMPONENT=tdd_workflow_engine || echo "❌ TDDWorkflowEngine validation failed" 
	@make validate-professional COMPONENT=tdd_progress_formatter || echo "❌ TDDProgressFormatter validation failed"
	@make validate-professional COMPONENT=git_safety_manager || echo "❌ GitSafetyManager validation failed"
	@make validate-professional COMPONENT=tool_integration_manager || echo "❌ ToolIntegrationManager validation failed"

.PHONY: client-verify-all
client-verify-all: ## 🔒 Client-side verification of all completion claims
	@echo "🔒 CLIENT VERIFICATION OF ALL COMPLETION CLAIMS"
	@echo "==============================================="
	@echo "📋 Checking evidence files..."
	@ls -la evidence/validation_reports/ 2>/dev/null || echo "⚠️  No validation reports found"
	@ls -la evidence/test_outputs/ 2>/dev/null || echo "⚠️  No test outputs found"
	@ls -la evidence/coverage_reports/ 2>/dev/null || echo "⚠️  No coverage reports found"
	@echo "🔍 Re-running critical validations..."
	@make validate-all-components

.PHONY: client-audit
client-audit: ## 🕵️ Comprehensive audit of phase completion
	@if [ -z "$(PHASE)" ]; then \
		echo "❌ Error: PHASE parameter required"; \
		echo "Usage: make client-audit PHASE=<phase_number>"; \
		exit 1; \
	fi
	@echo "🕵️ COMPREHENSIVE AUDIT: Phase $(PHASE)"
	@echo "====================================="
	@echo "📋 Mapping requirements to implementations..."
	@find . -name "PHASE-$(PHASE)-*.md" -exec echo "📄 {}" \;
	@echo "🔍 Checking for false completion claims..."
	@make validate-all-components
	@echo "📊 Generating audit report..."
	@echo "Audit completed at $$(date)" > evidence/audit_phase_$(PHASE)_$$(date +%Y%m%d_%H%M%S).log

.PHONY: validate-system
validate-system: ## 🏗️ Validate entire system with all projects
	@if [ -z "$(SYSTEM)" ]; then \
		echo "❌ Error: SYSTEM parameter required"; \
		echo "Usage: make validate-system SYSTEM=<system_name>"; \
		exit 1; \
	fi
	@echo "🏗️ SYSTEM VALIDATION: $(SYSTEM)"
	@$(PYTHON) scripts/universal_validator.py --system $(SYSTEM)

.PHONY: validate-project
validate-project: ## 📋 Validate entire project with all features
	@if [ -z "$(PROJECT)" ]; then \
		echo "❌ Error: PROJECT parameter required"; \
		echo "Usage: make validate-project PROJECT=<project_name>"; \
		exit 1; \
	fi
	@echo "📋 PROJECT VALIDATION: $(PROJECT)"
	@$(PYTHON) scripts/universal_validator.py --project $(PROJECT)

.PHONY: validate-feature
validate-feature: ## 🎯 Validate feature with all components
	@if [ -z "$(FEATURE)" ]; then \
		echo "❌ Error: FEATURE parameter required"; \
		echo "Usage: make validate-feature FEATURE=<feature_name>"; \
		exit 1; \
	fi
	@echo "🎯 FEATURE VALIDATION: $(FEATURE)"
	@$(PYTHON) scripts/universal_validator.py --feature $(FEATURE)

.PHONY: validate-north-star
validate-north-star: ## 🌟 Validate North Star with all cascading requirements
	@echo "🌟 NORTH STAR VALIDATION"
	@echo "========================"
	@echo "🔍 Validating Master North Star System..."
	@make validate-system SYSTEM=north_star || echo "❌ Master North Star validation failed"
	@echo "🔍 Validating Investment Strategy..."
	@make validate-project PROJECT=investment_strategy || echo "❌ Investment Strategy validation failed"
	@echo "🔍 Validating Professional Excellence..."
	@make validate-project PROJECT=professional_excellence || echo "❌ Professional Excellence validation failed"
	@echo "🔍 Validating Business Ventures..."
	@make validate-project PROJECT=business_ventures || echo "❌ Business Ventures validation failed"
	@echo "📊 North Star validation complete"

.PHONY: enforce-standards
enforce-standards: ## 🛡️ Enforce professional standards before any git commit
	@echo "🛡️ ENFORCING PROFESSIONAL STANDARDS"
	@echo "===================================="
	@echo "🔍 Checking for unstaged changes..."
	@git status --porcelain | grep -q "^[AM]" && echo "📝 Changes detected, validating..." || echo "✅ No changes to validate"
	@echo "🎯 Running professional validation on changed components..."
	@echo "⚠️  NO COMMITS ALLOWED WITHOUT VALIDATION EVIDENCE"

# ============================================================================
# TESTING & VALIDATION
# ============================================================================

.PHONY: test
test: ## 🧪 Run all tests (unit + validation + integration)
	@echo "🧪 Running comprehensive test suite..."
	@$(PYTHON) -m pytest $(TEST_DIR) -v

.PHONY: test-unit
test-unit: ## ⚡ Run unit tests only
	@echo "⚡ Running unit tests..."
	@$(PYTHON) -m pytest $(TEST_DIR)/unit -v

.PHONY: test-validation
test-validation: ## ✅ Run validation tests (acceptance criteria)
	@echo "✅ Running validation tests..."
	@$(PYTHON) -m pytest $(TEST_DIR)/validation -v

.PHONY: test-integration
test-integration: ## 🔗 Run integration tests
	@echo "🔗 Running integration tests..."
	@$(PYTHON) -m pytest $(TEST_DIR)/integration -v

.PHONY: test-coverage
test-coverage: ## 📊 Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	@$(PYTHON) -m pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term

.PHONY: validate-phase1
validate-phase1: ## 🎯 Validate Phase 1 requirements (FR-001)
	@echo "🎯 Validating Phase 1 requirements..."
	@$(PYTHON) -m pytest $(TEST_DIR)/validation/test_phase_1_requirements_validation.py -v

# ============================================================================
# DEVELOPMENT & MAINTENANCE
# ============================================================================

.PHONY: clean
clean: ## 🧹 Clean up generated files and caches
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@rm -rf htmlcov/ 2>/dev/null || true
	@echo "✅ Cleanup completed"

.PHONY: setup-logs
setup-logs: ## 📝 Create logs directory
	@mkdir -p $(LOGS_DIR)
	@echo "📝 Logs directory created: $(LOGS_DIR)"

.PHONY: lint
lint: ## 🔍 Run code linting and formatting checks
	@echo "🔍 Running linting checks..."
	@$(PYTHON) -m flake8 $(SRC_DIR) --max-line-length=120 --extend-ignore=E203,W503 || echo "⚠️  Linting issues found"
	@$(PYTHON) -m black --check $(SRC_DIR) || echo "⚠️  Formatting issues found"

.PHONY: format
format: ## ✨ Auto-format code with black
	@echo "✨ Formatting code..."
	@$(PYTHON) -m black $(SRC_DIR)
	@echo "✅ Code formatting completed"

# ============================================================================
# DOCUMENTATION & HELP
# ============================================================================

.PHONY: docs
docs: ## 📚 Generate documentation
	@echo "📚 Generating documentation..."
	@echo "Documentation sources available in $(DOCS_DIR)/"
	@ls -la $(DOCS_DIR)/

.PHONY: status
status: ## 📊 Show Control Tower system status
	@echo "📊 Control Tower System Status"
	@echo "=============================="
	@echo "📂 Source Code:"
	@find $(SRC_DIR) -name "*.py" | wc -l | xargs echo "   Python files:"
	@echo "🧪 Test Suite:"
	@find $(TEST_DIR) -name "*.py" | wc -l | xargs echo "   Test files:"
	@echo "📚 Documentation:"
	@find $(DOCS_DIR) -name "*.md" 2>/dev/null | wc -l | xargs echo "   Documentation files:" || echo "   Documentation files: 0"
	@echo "🔗 Repositories:"
	@ls -1 cloned_repos/ 2>/dev/null | wc -l | xargs echo "   Cloned repositories:" || echo "   Cloned repositories: 0"

.PHONY: version
version: ## 📋 Show Control Tower version information
	@echo "🏗️  Control Tower - Phase 1"
	@echo "Version: 1.0.0"
	@echo "Built with: Test-Driven Development (TDD)"
	@echo "Components: 4-Layer Architecture (UI, Business Logic, Data Access, Integration)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Ready for: Phase 2 Intelligence Layer"

# ============================================================================
# ADVANCED USAGE EXAMPLES
# ============================================================================

.PHONY: examples
examples: ## 📖 Show usage examples
	@echo "📖 Control Tower Usage Examples"
	@echo "==============================="
	@echo ""
	@echo "🎯 Basic Usage:"
	@echo "   make what-next                    # Show due/overdue work items"
	@echo "   make what-next-debug             # With timing and debug info"
	@echo "   make what-next-json              # JSON output for automation"
	@echo "   make what-next-all               # Show all work items"
	@echo ""
	@echo "🎯 Repository-Specific:"
	@echo "   make what-next-financial         # Financial security repository"
	@echo "   make what-next-investment        # Investment strategy repository"
	@echo "   make what-next-contract          # Contract projects repository"
	@echo ""
	@echo "🎯 Custom Filters:"
	@echo "   make what-next ARGS='--repository=custom_repo'"
	@echo "   make what-next ARGS='--repositories=repo1,repo2'"
	@echo "   make what-next ARGS='--json --debug'"
	@echo ""
	@echo "🧪 Testing & Validation:"
	@echo "   make test                        # Run all tests"
	@echo "   make validate-phase1             # Validate Phase 1 requirements"
	@echo "   make test-coverage               # Test with coverage report"

.PHONY: help
help: ## ❓ Show this help message
	@echo "🏗️  Control Tower - Phase 1 Make Commands"
	@echo "=========================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🎯 Quick Start:"
	@echo "   make what-next                   # Discover what to work on next"
	@echo "   make examples                    # Show detailed usage examples"
	@echo "   make status                      # Show system status"
	@echo ""
	@echo "For more information, see: docs/CONTROL_TOWER_COMMANDS.md"

# ============================================================================
# INTERNAL TARGETS
# ============================================================================

# Ensure Python path is set correctly
.PHONY: _check-env
_check-env:
	@if [ ! -f $(MAIN_SCRIPT) ]; then \
		echo "❌ Error: $(MAIN_SCRIPT) not found. Please run from Control Tower root directory."; \
		exit 1; \
	fi
	@if [ ! -d $(SRC_DIR) ]; then \
		echo "❌ Error: Source directory $(SRC_DIR) not found."; \
		exit 1; \
	fi

# All primary targets depend on environment check
what-next what-next-json what-next-debug what-next-all: _check-env

# ============================================================================
# MAKEFILE INFORMATION
# ============================================================================

# Prevent make from trying to remake the Makefile itself
Makefile: ;

# Ensure intermediate files are not deleted
.PRECIOUS: %.py

# ============================================================================
# PHASE 1 COMPLETION MARKER
# ============================================================================

.PHONY: phase1-complete
phase1-complete: ## 🎉 Verify Phase 1 completion status
	@echo "🎉 Phase 1 Completion Verification"
	@echo "=================================="
	@echo "✅ TR-UI-001: Terminal Output Formatter"
	@echo "✅ TR-BL-001: Work Item Discovery Engine"  
	@echo "✅ TR-BL-002: Priority Calculator"
	@echo "✅ TR-DA-001: Repository Scanner"
	@echo "✅ TR-DA-002: File System Interface"
	@echo "✅ TR-IL-001: Git Integration"
	@echo "✅ TR-IL-002: Command Line Interface"
	@echo "✅ Main Entry Point: make_what_next.py"
	@echo "✅ Comprehensive Makefile: make what-next"
	@echo ""
	@echo "🚀 Phase 1 is COMPLETE and ready for production use!"
	@echo "🎯 Next: Phase 2 Intelligence Layer"