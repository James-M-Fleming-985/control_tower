# Makefile for SYSTEM-003-03 Workflow Orchestration System
# Makes layer requirements executable through simple make commands

.PHONY: help test-layer verify-feature verify-system execute-layer execute-all validate-traceability clean

# Default target
help:
	@echo "SYSTEM-003-03 Workflow Orchestration System"
	@echo "============================================"
	@echo ""
	@echo "Layer Execution (TDD Cycle):"
	@echo "  make execute-layer LAYER=LAYER-003-03-01-01 PHASE=red"
	@echo "  make execute-layer LAYER=LAYER-003-03-01-01 PHASE=green"
	@echo "  make execute-layer LAYER=LAYER-003-03-01-01 PHASE=refactor"
	@echo "  make execute-layer LAYER=LAYER-003-03-01-01 PHASE=full-cycle"
	@echo ""
	@echo "Batch Execution:"
	@echo "  make execute-all                    # All layers sequentially"
	@echo "  make execute-all-parallel           # All layers in parallel"
	@echo "  make execute-feature FEATURE=FEATURE-003-03-02"
	@echo ""
	@echo "Testing & Verification:"
	@echo "  make test-layer LAYER=LAYER-003-03-01-01"
	@echo "  make verify-feature FEATURE=FEATURE-003-03-01"
	@echo "  make verify-system                  # Complete system verification"
	@echo ""
	@echo "Quality & Traceability:"
	@echo "  make validate-traceability"
	@echo "  make validate-traceability-layer LAYER=LAYER-003-03-01-01"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                          # Remove test outputs"
	@echo "  make clean-all                      # Remove all generated files"
	@echo ""

# Layer execution targets
execute-layer:
ifndef LAYER
	@echo "Error: LAYER not specified"
	@echo "Usage: make execute-layer LAYER=LAYER-003-03-01-01 PHASE=red"
	@exit 1
endif
ifndef PHASE
	$(eval PHASE := full-cycle)
endif
	@echo "Executing $(LAYER) in $(PHASE) phase..."
	python3 scripts/execute_layer.py --layer $(LAYER) --phase $(PHASE)

execute-all:
	@echo "Executing all layers sequentially..."
	python3 scripts/execute_all_layers.py

execute-all-parallel:
	@echo "Executing all layers in parallel..."
	python3 scripts/execute_all_layers.py --parallel

execute-feature:
ifndef FEATURE
	@echo "Error: FEATURE not specified"
	@echo "Usage: make execute-feature FEATURE=FEATURE-003-03-02"
	@exit 1
endif
	@echo "Executing all layers for $(FEATURE)..."
	python3 scripts/execute_all_layers.py --feature $(FEATURE)

# Testing targets
test-layer:
ifndef LAYER
	@echo "Error: LAYER not specified"
	@echo "Usage: make test-layer LAYER=LAYER-003-03-01-01"
	@exit 1
endif
	@echo "Running tests for $(LAYER)..."
	python3 scripts/run_layer_tests.py --layer $(LAYER) --update-verification

verify-feature:
ifndef FEATURE
	@echo "Error: FEATURE not specified"
	@echo "Usage: make verify-feature FEATURE=FEATURE-003-03-01"
	@exit 1
endif
	@echo "Verifying $(FEATURE)..."
	python3 scripts/verify_feature.py --feature $(FEATURE) --update-yaml

verify-system:
	@echo "Running complete system verification..."
	python3 scripts/run_system_verification.py

# Traceability targets
validate-traceability:
	@echo "Validating requirements traceability..."
	python3 scripts/validate_traceability.py

validate-traceability-layer:
ifndef LAYER
	@echo "Error: LAYER not specified"
	@echo "Usage: make validate-traceability-layer LAYER=LAYER-003-03-01-01"
	@exit 1
endif
	@echo "Validating traceability for $(LAYER)..."
	python3 scripts/validate_traceability.py --layer $(LAYER)

# Quick execution targets for common workflows
red:
ifndef LAYER
	@echo "Error: LAYER not specified"
	@echo "Usage: make red LAYER=LAYER-003-03-01-01"
	@exit 1
endif
	@echo "RED Phase: $(LAYER)"
	python3 scripts/execute_layer.py --layer $(LAYER) --phase red

green:
ifndef LAYER
	@echo "Error: LAYER not specified"
	@echo "Usage: make green LAYER=LAYER-003-03-01-01"
	@exit 1
endif
	@echo "GREEN Phase: $(LAYER)"
	python3 scripts/execute_layer.py --layer $(LAYER) --phase green

refactor:
ifndef LAYER
	@echo "Error: LAYER not specified"
	@echo "Usage: make refactor LAYER=LAYER-003-03-01-01"
	@exit 1
endif
	@echo "REFACTOR Phase: $(LAYER)"
	python3 scripts/execute_layer.py --layer $(LAYER) --phase refactor

# Cleanup targets
clean:
	@echo "Cleaning test outputs..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "coverage.xml" -delete
	find . -name ".coverage" -delete
	@echo "Cleanup complete"

clean-all: clean
	@echo "Removing all generated files..."
	@echo "⚠️  This will delete all test outputs and verification evidence!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	find . -path "*/Testing Outputs/*" -type f -delete
	find . -name "*_results_*.xml" -delete
	find . -name "*_log_*.txt" -delete
	find . -name "execution_evidence.json" -delete
	find . -name "batch_execution_*.json" -delete
	find . -name "batch_execution_*.txt" -delete
	@echo "All generated files removed"

# Development shortcuts
dev-setup:
	@echo "Setting up development environment..."
	pip install -q pytest pytest-cov pyyaml
	@echo "Dependencies installed"

dev-test:
	@echo "Running all layer tests..."
	pytest tests/layer/ -v --tb=short

# Layer-specific shortcuts for FEATURE-003-03-02 (Prerequisites - highest priority)
prereq-env:
	@make execute-layer LAYER=LAYER-003-03-02-01 PHASE=full-cycle

prereq-tools:
	@make execute-layer LAYER=LAYER-003-03-02-02 PHASE=full-cycle

prereq-structure:
	@make execute-layer LAYER=LAYER-003-03-02-03 PHASE=full-cycle

prereq-all:
	@make execute-feature FEATURE=FEATURE-003-03-02

# Layer-specific shortcuts for FEATURE-003-03-01 (Orchestration)
orch-state:
	@make execute-layer LAYER=LAYER-003-03-01-01 PHASE=full-cycle

orch-sequencing:
	@make execute-layer LAYER=LAYER-003-03-01-02 PHASE=full-cycle

orch-communication:
	@make execute-layer LAYER=LAYER-003-03-01-03 PHASE=full-cycle

orch-all:
	@make execute-feature FEATURE=FEATURE-003-03-01

# Report generation
reports:
	@echo "Generating comprehensive reports..."
	@make validate-traceability > traceability_report.txt
	@make verify-system > system_verification_report.txt
	@echo "Reports generated:"
	@echo "  - traceability_report.txt"
	@echo "  - system_verification_report.txt"

# CI/CD targets
ci-test: dev-setup
	@echo "Running CI test suite..."
	@make execute-all
	@make verify-system
	@make validate-traceability

# Show layer status
status:
	@echo "Layer Execution Status"
	@echo "======================"
	@find . -name "execution_evidence.json" -exec echo "Found evidence in:" \; -print

# List all layers
list-layers:
	@echo "All Layers (in execution order):"
	@find . -name "LAYER-*.yaml" -not -path "*/Requirements Verification/*" | \
		grep -o 'LAYER-[0-9-]*' | sort -u

# List all features
list-features:
	@echo "All Features:"
	@find . -maxdepth 1 -type d -name "FEATURE-*" | \
		sed 's|.*/||' | sort
