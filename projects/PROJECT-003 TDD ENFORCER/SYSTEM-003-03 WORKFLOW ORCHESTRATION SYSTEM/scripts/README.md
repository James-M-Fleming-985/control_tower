# SYSTEM-003-03 Implementation Scripts

This directory contains companion scripts that make SYSTEM-003-03 requirements executable through automated testing, verification, and validation.

## 📋 Scripts Overview

### 1. `execute_layer.py` - ⭐ Layer Requirement Executor (PRIMARY)
**Purpose**: Make layer requirements executable through complete TDD cycle (RED→GREEN→REFACTOR).

**Usage**:
```bash
# Execute full TDD cycle for a layer
python scripts/execute_layer.py --layer LAYER-003-03-01-01 --phase full-cycle

# Execute RED phase (generate tests, expect failures)
python scripts/execute_layer.py --layer LAYER-003-03-01-01 --phase red

# Execute GREEN phase (implement requirements, pass tests)
python scripts/execute_layer.py --layer LAYER-003-03-01-01 --phase green

# Execute REFACTOR phase (improve code, keep tests green)
python scripts/execute_layer.py --layer LAYER-003-03-01-01 --phase refactor
```

**What it does**:
- ✅ Generates test files from acceptance criteria (auto-generated unit & integration tests)
- ✅ Creates implementation stubs with TODO markers
- ✅ Executes RED phase (tests must FAIL)
- ✅ Executes GREEN phase (implement & make tests PASS)
- ✅ Executes REFACTOR phase (verify tests still pass)
- ✅ Saves all evidence to `Testing Outputs/` folder
- ✅ Updates `Requirements Verification/requirements_verification_template.yaml`
- ✅ Saves execution evidence to `Requirements Verification/execution_evidence.json`

**Output Files**:
- `Testing Outputs/red_phase_results_YYYYMMDD_HHMMSS.xml`
- `Testing Outputs/red_phase_log_YYYYMMDD_HHMMSS.txt`
- `Testing Outputs/green_phase_results_YYYYMMDD_HHMMSS.xml`
- `Testing Outputs/green_phase_log_YYYYMMDD_HHMMSS.txt`
- `Testing Outputs/coverage_YYYYMMDD_HHMMSS.json`
- `Requirements Verification/execution_evidence.json`

**Exit Codes**:
- `0`: Phase completed successfully
- `1`: Phase failed or incomplete

---

### 2. `execute_all_layers.py` - Batch Layer Executor
**Purpose**: Execute all layers in dependency order with full TDD cycle.

**Usage**:
```bash
# Execute all layers sequentially
python scripts/execute_all_layers.py

# Execute all layers in parallel (where dependencies allow)
python scripts/execute_all_layers.py --parallel --max-workers 4

# Execute only layers for a specific feature
python scripts/execute_all_layers.py --feature FEATURE-003-03-02

# Execute specific phase for all layers
python scripts/execute_all_layers.py --phase red
```

**What it does**:
- ✅ Executes all 12 layers in dependency order (FEATURE-002 → 001 → 004 → 003)
- ✅ Supports parallel execution within same priority group
- ✅ Generates batch execution report
- ✅ Saves batch execution evidence JSON
- ✅ Aggregates results from all layers

**Execution Order**:
1. **Priority 1**: FEATURE-003-03-02 layers (Prerequisites - foundation)
2. **Priority 2**: FEATURE-003-03-01 layers (Orchestration - core)
3. **Priority 3**: FEATURE-003-03-04 layers (Monitoring - observability)
4. **Priority 4**: FEATURE-003-03-03 layers (Failure Handling - integration)

**Exit Codes**:
- `0`: All layers completed successfully
- `1`: One or more layers failed

---

### 3. `run_layer_tests.py` - Layer-Level Test Runner
**Purpose**: Execute tests for a specific layer and validate against acceptance criteria.

**Usage**:
```bash
# Run all tests for a layer
python scripts/run_layer_tests.py --layer LAYER-003-03-01-01

# Run specific TDD phase
python scripts/run_layer_tests.py --layer LAYER-003-03-01-01 --phase red
python scripts/run_layer_tests.py --layer LAYER-003-03-01-01 --phase green

# Update verification YAML with results
python scripts/run_layer_tests.py --layer LAYER-003-03-01-01 --update-verification
```

**What it does**:
- ✅ Runs unit tests (90% coverage threshold)
- ✅ Runs integration tests (80% coverage threshold)
- ✅ Validates acceptance criteria implementation
- ✅ Generates test reports
- ✅ Updates `requirements_verification_template.yaml` with results
- ✅ Saves test outputs to `Testing Outputs/` folder

**Exit Codes**:
- `0`: All tests passed, acceptance criteria met
- `1`: Tests failed or acceptance criteria not met

---

### 4. `verify_feature.py` - Feature-Level Verification
**Purpose**: Verify a complete feature by testing all its layers and integration.

**Usage**:
```bash
# Verify entire feature (all layers + integration + e2e)
python scripts/verify_feature.py --feature FEATURE-003-03-01

# Verify feature with verbose output
python scripts/verify_feature.py --feature FEATURE-003-03-01 --verbose

# Update feature YAML with results
python scripts/verify_feature.py --feature FEATURE-003-03-01 --update-yaml

# Skip layer tests (only run feature-level tests)
python scripts/verify_feature.py --feature FEATURE-003-03-01 --skip-layers
```

**What it does**:
- ✅ Runs all layer tests using `run_layer_tests.py`
- ✅ Runs feature-level integration tests (85% coverage)
- ✅ Runs feature-level E2E tests (70% coverage)
- ✅ Validates feature acceptance criteria
- ✅ Aggregates results from all layers
- ✅ Generates comprehensive feature report

**Exit Codes**:
- `0`: All layers and feature tests passed
- `1`: One or more tests failed

---

### 5. `run_system_verification.py` - System-Level Orchestration
**Purpose**: Execute complete system verification across all features.

**Usage**:
```bash
# Verify entire system
python scripts/run_system_verification.py

# Verify with verbose output
python scripts/run_system_verification.py --verbose

# Verify single feature only
python scripts/run_system_verification.py --feature FEATURE-003-03-01

# Skip system-level tests
python scripts/run_system_verification.py --skip-e2e --skip-performance
```

**What it does**:
- ✅ Verifies all features in dependency order (2→1→4→3)
- ✅ Runs system-level E2E tests (80% coverage)
- ✅ Runs performance tests (15min workflow, 30s validation, 2min stage)
- ✅ Aggregates all feature and layer results
- ✅ Generates system verification report

**Verification Order** (dependency-based):
1. **FEATURE-003-03-02**: Prerequisites Validation (foundation)
2. **FEATURE-003-03-01**: Workflow Orchestration (core)
3. **FEATURE-003-03-04**: Progress Monitoring (observability)
4. **FEATURE-003-03-03**: Failure Handling (integration)

**Exit Codes**:
- `0`: Complete system verification passed
- `1`: One or more verifications failed

---

### 6. `validate_traceability.py` - Requirements Traceability Validator
**Purpose**: Validate requirements traceability across code and YAMLs.

**Usage**:
```bash
# Validate entire system traceability
python scripts/validate_traceability.py

# Validate specific layer
python scripts/validate_traceability.py --layer LAYER-003-03-01-01

# Validate specific feature
python scripts/validate_traceability.py --feature FEATURE-003-03-01
```

**What it does**:
- ✅ Scans codebase for `# REQ-XXX` comments (auto-discovery)
- ✅ Loads manually registered requirements from YAMLs
- ✅ Compares auto-discovered vs manual registrations
- ✅ Detects orphaned code (no requirement comments)
- ✅ Validates acceptance criteria have tests and implementations
- ✅ Generates traceability compliance report

**Quality Gates**:
- Auto-discovered must match manually registered (90% compliance)
- No orphaned code allowed (0 files >10 LOC without comments)
- All acceptance criteria must have tests (80% coverage)

**Exit Codes**:
- `0`: Traceability validation passed
- `1`: Traceability issues detected

---

## 🎯 Testing Strategy: Layer-Level vs Feature-Level

### ✅ **RECOMMENDED: Layer-Level Testing**

**Why Layer-Level is More Efficient:**

1. **Granular Feedback** - Fast, focused tests on specific functionality
2. **Better Isolation** - Single responsibility testing
3. **Progressive Integration** - Build confidence incrementally
4. **Requirement Traceability** - Direct mapping to acceptance criteria
5. **Faster CI/CD** - Parallel layer testing possible

### Testing Hierarchy:

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER Level (PRIMARY VERIFICATION)                          │
│ ├─ Unit Tests: 90% coverage                                 │
│ ├─ Integration Tests: 80% coverage                          │
│ ├─ Acceptance Criteria: All validated                       │
│ └─ Test Reports: In Testing Outputs/                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FEATURE Level (COMPOSITION VERIFICATION)                    │
│ ├─ All Layer Tests: Must pass                               │
│ ├─ Integration Tests: 85% coverage                          │
│ ├─ E2E Tests: 70% coverage                                  │
│ └─ Multi-layer workflows validated                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM Level (FULL WORKFLOW VERIFICATION)                   │
│ ├─ All Feature Tests: Must pass                             │
│ ├─ System E2E: 80% coverage                                 │
│ ├─ Performance: <15min workflow                             │
│ └─ Actor-Enforcer subprocess integration                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Examples

### Example 1: Execute Layer Requirements (Most Common - TDD Cycle)
```bash
# Execute full TDD cycle for a single layer
python scripts/execute_layer.py \
  --layer LAYER-003-03-02-01 \
  --phase full-cycle

# This will:
# 1. Generate test files from acceptance criteria
# 2. Create implementation stubs
# 3. Run RED phase (tests fail)
# 4. Prompt for implementation
# 5. Run GREEN phase (tests pass)
# 6. Run REFACTOR phase (verify still passing)
# 7. Save all evidence to Testing Outputs/
# 8. Update Requirements Verification/

# View evidence
cat "FEATURE-003-03-02 Prerequisites Validation/LAYER-003-03-02-01 Environment Validation/Requirements Verification/execution_evidence.json"
```

### Example 2: Execute All Layers (Batch Processing)
```bash
# Execute all 12 layers in dependency order
python scripts/execute_all_layers.py

# Execute in parallel for faster processing
python scripts/execute_all_layers.py --parallel

# Execute only one feature's layers
python scripts/execute_all_layers.py --feature FEATURE-003-03-02

# Check batch execution report
cat batch_execution_report_*.txt
```

### Example 3: Use Makefile (Recommended)
```bash
# Execute single layer
make execute-layer LAYER=LAYER-003-03-02-01 PHASE=full-cycle

# Quick TDD phase shortcuts
make red LAYER=LAYER-003-03-02-01
make green LAYER=LAYER-003-03-02-01
make refactor LAYER=LAYER-003-03-02-01

# Execute entire feature
make execute-feature FEATURE=FEATURE-003-03-02

# Execute all layers
make execute-all

# Execute in parallel
make execute-all-parallel

# Prerequisites feature shortcuts
make prereq-env        # Execute LAYER-003-03-02-01
make prereq-tools      # Execute LAYER-003-03-02-02
make prereq-structure  # Execute LAYER-003-03-02-03
make prereq-all        # Execute all prerequisites layers
```

### Example 4: Test Single Layer (Manual Testing)
```bash
# Run complete layer verification
python scripts/run_layer_tests.py \
  --layer LAYER-003-03-02-01 \
  --update-verification \
  --verbose

# View results
cat "FEATURE-003-03-02 Prerequisites Validation/LAYER-003-03-02-01 Environment Validation/Testing Outputs/test_report_*.txt"
```

### Example 5: Verify Complete Feature
```bash
# Run complete layer verification
python scripts/run_layer_tests.py \
  --layer LAYER-003-03-02-01 \
  --update-verification \
  --verbose

# View results
cat "FEATURE-003-03-02 Prerequisites Validation/LAYER-003-03-02-01 Environment Validation/Testing Outputs/test_report_*.txt"
```

### Example 2: Verify Complete Feature
```bash
# Verify feature (runs all layers + integration)
python scripts/verify_feature.py \
  --feature FEATURE-003-03-02 \
  --update-yaml \
  --verbose

# Check feature report
cat "FEATURE-003-03-02 Prerequisites Validation/feature_verification_report_*.txt"
```

### Example 3: Full System Verification
```bash
# Complete system verification (all features, all layers)
python scripts/run_system_verification.py --verbose

# Check system report
cat system_verification_report_*.txt
```

### Example 4: Validate Traceability
```bash
# Check requirements traceability
python scripts/validate_traceability.py

# Check specific layer traceability
python scripts/validate_traceability.py --layer LAYER-003-03-01-01
```

---

## 📊 Output Files

### Layer Level:
```
LAYER-XXX/
├── Testing Outputs/
│   ├── test_report_YYYYMMDD_HHMMSS.txt
│   ├── unit_test_results_YYYYMMDD_HHMMSS.xml
│   ├── integration_test_results_YYYYMMDD_HHMMSS.xml
│   └── coverage_report.html
└── Requirements Verification/
    └── requirements_verification_template.yaml  (updated)
```

### Feature Level:
```
FEATURE-XXX/
├── feature_verification_report_YYYYMMDD_HHMMSS.txt
├── integration_test_results_YYYYMMDD_HHMMSS.xml
└── e2e_test_results_YYYYMMDD_HHMMSS.xml
```

### System Level:
```
SYSTEM-003-03/
├── system_verification_report_YYYYMMDD_HHMMSS.txt
├── system_e2e_results_YYYYMMDD_HHMMSS.xml
├── performance_results_YYYYMMDD_HHMMSS.xml
└── traceability_report_YYYYMMDD_HHMMSS.txt
```

---

## 🔧 Dependencies

All scripts require:
- Python 3.8+
- pytest
- pytest-cov
- pyyaml

Install with:
```bash
pip install pytest pytest-cov pyyaml
```

---

## 📝 Integration with Make

These scripts integrate with the Makefile workflow:

```makefile
# Run layer tests
make test-layer LAYER=LAYER-003-03-01-01

# Verify feature
make verify-feature FEATURE=FEATURE-003-03-01

# System verification
make verify-system

# Traceability validation
make validate-traceability
```

---

## 🎯 Best Practices

1. **Start with Layer Tests** - Get fast feedback on specific functionality
2. **Run Feature Verification** - Before committing, verify feature integration
3. **System Verification in CI/CD** - Run complete verification in pipeline
4. **Traceability Weekly** - Check traceability compliance regularly
5. **Update Verification YAMLs** - Always use `--update-verification` flag

---

## 📚 Additional Resources

- **SYSTEM-003-03_workflow_orchestration_system.yaml** - Complete requirements specification
- **Testing Outputs README** - Test artifact guidelines
- **Requirements Verification README** - Verification process documentation

---

**Created**: October 8, 2025  
**Last Updated**: October 8, 2025  
**Version**: 1.0.0
