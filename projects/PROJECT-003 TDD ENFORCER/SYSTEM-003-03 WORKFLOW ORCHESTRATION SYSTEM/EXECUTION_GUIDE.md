# SYSTEM-003-03 Complete Usage Guide

## 🎯 Making Requirements Executable

This guide shows how to make SYSTEM-003-03 layer requirements executable through automated TDD cycles, with all evidence automatically saved to the proper folders.

---

## 📁 Evidence Storage Structure

All execution evidence is automatically saved to standardized folders:

```
LAYER-XXX/
├── Testing Outputs/              ← Test execution evidence
│   ├── red_phase_results_*.xml
│   ├── red_phase_log_*.txt
│   ├── green_phase_results_*.xml
│   ├── green_phase_log_*.txt
│   ├── green_phase_coverage_*.json
│   ├── refactor_phase_results_*.xml
│   └── refactor_phase_log_*.txt
│
└── Requirements Verification/    ← Verification evidence
    ├── requirements_verification_template.yaml  (updated)
    └── execution_evidence.json  (complete audit trail)
```

---

## 🔄 Complete TDD Workflow

### Step 1: Execute RED Phase (Tests Must FAIL)

```bash
# Using execute_layer.py
python scripts/execute_layer.py \
  --layer LAYER-003-03-02-01 \
  --phase red

# Or using Makefile
make red LAYER=LAYER-003-03-02-01
```

**What happens**:
1. ✅ Generates test files from acceptance criteria in layer YAML
2. ✅ Creates unit tests (e.g., `tests/layer/environment_validation/test_environment_validation_unit.py`)
3. ✅ Creates integration tests (e.g., `tests/layer/environment_validation/test_environment_validation_integration.py`)
4. ✅ Runs tests (they MUST fail - this proves TDD is being followed)
5. ✅ Saves `red_phase_results_*.xml` to `Testing Outputs/`
6. ✅ Saves `red_phase_log_*.txt` to `Testing Outputs/`
7. ✅ Updates `execution_evidence.json` in `Requirements Verification/`

**Expected Output**:
```
RED PHASE: Running Tests (Expected to FAIL)
======================================================================
✅ RED PHASE PASSED: Tests are failing as expected
   Log saved to: Testing Outputs/red_phase_log_20251008_143000.txt
```

**Evidence Files Created**:
- `LAYER-XXX/Testing Outputs/red_phase_results_20251008_143000.xml`
- `LAYER-XXX/Testing Outputs/red_phase_log_20251008_143000.txt`
- `LAYER-XXX/Requirements Verification/execution_evidence.json` (updated)

---

### Step 2: Execute GREEN Phase (Implement & Pass Tests)

```bash
# Using execute_layer.py
python scripts/execute_layer.py \
  --layer LAYER-003-03-02-01 \
  --phase green

# Or using Makefile
make green LAYER=LAYER-003-03-02-01
```

**What happens**:
1. ✅ Generates implementation stubs (e.g., `src/layer/environment_validation/environment_validation.py`)
2. ✅ Creates `__init__.py` with proper imports
3. ✅ Prompts developer to implement TODOs
4. ✅ Runs tests with coverage (90% threshold for unit tests)
5. ✅ Saves `green_phase_results_*.xml` to `Testing Outputs/`
6. ✅ Saves `green_phase_log_*.txt` to `Testing Outputs/`
7. ✅ Saves `coverage_*.json` to `Testing Outputs/`
8. ✅ Updates `execution_evidence.json`

**Developer Action Required**:
```
⚠️  Implementation stubs generated.
   Please implement the TODOs in:
   - src/layer/environment_validation/environment_validation.py
   
   After implementation, run tests again...
```

**After implementing the TODOs, rerun GREEN phase**:
```bash
make green LAYER=LAYER-003-03-02-01
```

**Expected Output** (after implementation):
```
GREEN PHASE: Implementing Requirements
======================================================================
✅ GREEN PHASE PASSED: All tests passing
   Coverage: 92.5% (required: 90.0%)
   Results saved to: Testing Outputs/green_phase_results_20251008_144500.xml
```

**Evidence Files Created**:
- `LAYER-XXX/Testing Outputs/green_phase_results_20251008_144500.xml`
- `LAYER-XXX/Testing Outputs/green_phase_log_20251008_144500.txt`
- `LAYER-XXX/Testing Outputs/coverage_20251008_144500.json`
- `LAYER-XXX/Testing Outputs/htmlcov/` (HTML coverage report)
- `LAYER-XXX/Requirements Verification/execution_evidence.json` (updated)

---

### Step 3: Execute REFACTOR Phase (Improve Code)

```bash
# Using execute_layer.py
python scripts/execute_layer.py \
  --layer LAYER-003-03-02-01 \
  --phase refactor

# Or using Makefile
make refactor LAYER=LAYER-003-03-02-01
```

**What happens**:
1. ✅ Reruns all tests to verify refactoring didn't break anything
2. ✅ Verifies coverage is maintained
3. ✅ Saves `refactor_phase_results_*.xml` to `Testing Outputs/`
4. ✅ Saves `refactor_phase_log_*.txt` to `Testing Outputs/`
5. ✅ Updates `execution_evidence.json`

**Expected Output**:
```
REFACTOR PHASE: Verify Tests Still Pass
======================================================================
✅ REFACTOR PHASE PASSED: Tests still passing after refactoring
```

**Evidence Files Created**:
- `LAYER-XXX/Testing Outputs/refactor_phase_results_20251008_145500.xml`
- `LAYER-XXX/Testing Outputs/refactor_phase_log_20251008_145500.txt`
- `LAYER-XXX/Requirements Verification/execution_evidence.json` (updated)

---

### Step 4: Execute Full Cycle (All Phases)

```bash
# Execute complete RED → GREEN → REFACTOR cycle
python scripts/execute_layer.py \
  --layer LAYER-003-03-02-01 \
  --phase full-cycle

# Or using Makefile
make execute-layer LAYER=LAYER-003-03-02-01 PHASE=full-cycle
```

**What happens**:
1. ✅ Runs RED phase automatically
2. ✅ Runs GREEN phase automatically (pauses for implementation if needed)
3. ✅ Runs REFACTOR phase automatically
4. ✅ Saves all evidence to respective folders
5. ✅ Updates Requirements Verification YAML
6. ✅ Generates complete execution audit trail

**Expected Output**:
```
FULL TDD CYCLE COMPLETE
======================================================================
✅ RED Phase: Tests failed as expected
✅ GREEN Phase: All tests passing (Coverage: 92.5%)
✅ REFACTOR Phase: Tests still passing
======================================================================
```

---

## 📊 Viewing Execution Evidence

### 1. View Execution Evidence JSON
```bash
# Complete audit trail of all execution phases
cat "FEATURE-003-03-02 Prerequisites Validation/LAYER-003-03-02-01 Environment Validation/Requirements Verification/execution_evidence.json"
```

**Example Evidence**:
```json
[
  {
    "phase": "test_generation",
    "timestamp": "2025-10-08T14:30:00",
    "description": "Generated 2 test files with 4 acceptance criteria"
  },
  {
    "phase": "red_phase",
    "timestamp": "2025-10-08T14:30:15",
    "description": "Tests failed as expected",
    "data": {
      "junit_file": ".../red_phase_results_20251008_143000.xml",
      "log_file": ".../red_phase_log_20251008_143000.txt",
      "tests_failed": true,
      "returncode": 1
    }
  },
  {
    "phase": "green_phase",
    "timestamp": "2025-10-08T14:45:00",
    "description": "Tests passed, Coverage: 92.5%",
    "data": {
      "junit_file": ".../green_phase_results_20251008_144500.xml",
      "coverage": 92.5,
      "required_coverage": 90.0
    }
  }
]
```

### 2. View Test Logs
```bash
# RED phase log
cat "LAYER-XXX/Testing Outputs/red_phase_log_*.txt"

# GREEN phase log
cat "LAYER-XXX/Testing Outputs/green_phase_log_*.txt"

# REFACTOR phase log
cat "LAYER-XXX/Testing Outputs/refactor_phase_log_*.txt"
```

### 3. View Coverage Report
```bash
# Open HTML coverage report in browser
open "LAYER-XXX/Testing Outputs/htmlcov/index.html"

# Or view JSON coverage data
cat "LAYER-XXX/Testing Outputs/coverage_*.json"
```

### 4. View Requirements Verification
```bash
# Updated verification YAML
cat "LAYER-XXX/Requirements Verification/requirements_verification_template.yaml"
```

---

## 🔄 Batch Execution Workflows

### Execute All Layers Sequentially

```bash
# Execute all 12 layers in dependency order
python scripts/execute_all_layers.py

# Or using Makefile
make execute-all
```

**Execution Order** (dependency-based):
1. LAYER-003-03-02-01, LAYER-003-03-02-02, LAYER-003-03-02-03 (Prerequisites)
2. LAYER-003-03-01-01, LAYER-003-03-01-02, LAYER-003-03-01-03 (Orchestration)
3. LAYER-003-03-04-01, LAYER-003-03-04-02, LAYER-003-03-04-03 (Monitoring)
4. LAYER-003-03-03-01, LAYER-003-03-03-02, LAYER-003-03-03-03 (Failure Handling)

**Evidence Generated**:
- `batch_execution_evidence_*.json` (system root)
- `batch_execution_report_*.txt` (system root)
- Individual layer evidence in each `Testing Outputs/` and `Requirements Verification/`

---

### Execute All Layers in Parallel

```bash
# Execute with 4 parallel workers
python scripts/execute_all_layers.py --parallel --max-workers 4

# Or using Makefile
make execute-all-parallel
```

**How Parallel Execution Works**:
- Layers with same priority (same feature) execute in parallel
- Ensures dependencies are respected
- Faster overall execution

---

### Execute Feature Layers

```bash
# Execute all layers for Prerequisites feature
python scripts/execute_all_layers.py --feature FEATURE-003-03-02

# Or using Makefile shortcuts
make prereq-all        # All prerequisites layers
make prereq-env        # Just environment validation
make prereq-tools      # Just tool availability
make prereq-structure  # Just project structure

# Orchestration feature
make orch-all          # All orchestration layers
make orch-state        # Just state management
make orch-sequencing   # Just sequencing
make orch-communication # Just actor-enforcer comm
```

---

## 📋 Verification Workflows

### Verify Single Layer

```bash
# Run verification for completed layer
python scripts/run_layer_tests.py \
  --layer LAYER-003-03-02-01 \
  --update-verification

# Or using Makefile
make test-layer LAYER=LAYER-003-03-02-01
```

**Evidence Generated**:
- `LAYER-XXX/Testing Outputs/test_report_*.txt`
- `LAYER-XXX/Testing Outputs/unit_test_results_*.xml`
- `LAYER-XXX/Testing Outputs/integration_test_results_*.xml`
- `LAYER-XXX/Requirements Verification/requirements_verification_template.yaml` (updated)

---

### Verify Complete Feature

```bash
# Verify all layers + feature integration
python scripts/verify_feature.py \
  --feature FEATURE-003-03-02 \
  --update-yaml

# Or using Makefile
make verify-feature FEATURE=FEATURE-003-03-02
```

**Evidence Generated**:
- `FEATURE-XXX/feature_verification_report_*.txt`
- `FEATURE-XXX/integration_test_results_*.xml`
- `FEATURE-XXX/e2e_test_results_*.xml`
- Updated feature YAML with progress

---

### Verify Complete System

```bash
# Complete system verification
python scripts/run_system_verification.py

# Or using Makefile
make verify-system
```

**Evidence Generated**:
- `system_verification_report_*.txt` (system root)
- `system_e2e_results_*.xml` (system root)
- `performance_results_*.xml` (system root)

---

## 🔍 Traceability Validation

### Validate Complete Traceability

```bash
# Scan codebase and validate traceability
python scripts/validate_traceability.py

# Or using Makefile
make validate-traceability
```

**What it checks**:
- ✅ Auto-discovered `# REQ-XXX` comments in code
- ✅ Manually registered requirements in YAMLs
- ✅ Orphaned code (no requirement comments)
- ✅ Missing tests for acceptance criteria
- ✅ Missing implementations

**Evidence Generated**:
- `traceability_report_*.txt` (system root)

---

### Validate Layer Traceability

```bash
# Check specific layer
python scripts/validate_traceability.py \
  --layer LAYER-003-03-02-01

# Or using Makefile
make validate-traceability-layer LAYER=LAYER-003-03-02-01
```

---

## 🎯 Common Workflows

### Workflow 1: Start New Layer Implementation

```bash
# 1. Execute RED phase (generate tests & stubs)
make red LAYER=LAYER-003-03-02-01

# 2. Implement TODOs in generated files
#    - Edit src/layer/*/implementation.py
#    - Replace NotImplementedError with actual code

# 3. Execute GREEN phase (make tests pass)
make green LAYER=LAYER-003-03-02-01

# 4. Refactor if needed
make refactor LAYER=LAYER-003-03-02-01

# 5. Verify complete layer
make test-layer LAYER=LAYER-003-03-02-01
```

---

### Workflow 2: Implement Complete Feature

```bash
# Execute all feature layers automatically
make execute-feature FEATURE=FEATURE-003-03-02

# Verify feature integration
make verify-feature FEATURE=FEATURE-003-03-02

# Check evidence
ls -R "FEATURE-003-03-02 Prerequisites Validation/"
```

---

### Workflow 3: Complete System Implementation

```bash
# 1. Execute all layers in dependency order
make execute-all

# 2. Verify complete system
make verify-system

# 3. Validate traceability
make validate-traceability

# 4. Generate comprehensive reports
make reports
```

---

## 📂 Evidence Inspection Commands

```bash
# List all execution evidence
find . -name "execution_evidence.json" -exec echo "Found:" \; -print

# List all test results
find . -name "*_results_*.xml"

# List all test logs
find . -name "*_log_*.txt"

# List all coverage reports
find . -name "coverage_*.json"

# Count total evidence files
find . -path "*/Testing Outputs/*" -type f | wc -l
```

---

## 🧹 Cleanup Commands

```bash
# Clean test artifacts only
make clean

# Clean ALL generated files (WARNING: removes evidence)
make clean-all

# List what would be cleaned
find . -path "*/Testing Outputs/*" -type f
```

---

## 📊 Reporting

### Generate All Reports

```bash
# Generate comprehensive reports
make reports

# This creates:
# - traceability_report.txt
# - system_verification_report.txt
```

### View Layer Status

```bash
# Show execution status for all layers
make status

# List all layers
make list-layers

# List all features
make list-features
```

---

## 🚀 CI/CD Integration

```bash
# Complete CI test suite
make ci-test

# This runs:
# 1. Install dependencies
# 2. Execute all layers
# 3. Verify system
# 4. Validate traceability
```

---

## ✅ Success Criteria

After executing a layer, you should see:

### Testing Outputs Folder:
```
Testing Outputs/
├── red_phase_results_*.xml       ✅
├── red_phase_log_*.txt           ✅
├── green_phase_results_*.xml     ✅
├── green_phase_log_*.txt         ✅
├── coverage_*.json               ✅
├── htmlcov/                      ✅
├── refactor_phase_results_*.xml  ✅
└── refactor_phase_log_*.txt      ✅
```

### Requirements Verification Folder:
```
Requirements Verification/
├── requirements_verification_template.yaml  ✅ (updated)
└── execution_evidence.json                  ✅ (complete audit trail)
```

---

**Last Updated**: October 8, 2025
