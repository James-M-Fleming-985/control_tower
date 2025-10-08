# Batch Refactoring Automation System (YAML-Driven)

**Created:** October 8, 2025  
**Updated:** October 8, 2025 (Version 2.0 - YAML-Driven)  
**Purpose:** Automate systematic refactoring of 461 actor behaviors to validator behaviors

---

## 🎯 Overview

This automation tool replaces manual RED-GREEN-REFACTOR cycles with a single executable command, reducing batch refactoring time from **4-6 hours to ~30 minutes**.

**NEW in Version 2.0:** All 11 batches are now pre-configured as YAML specifications, making the entire refactoring roadmap transparent and easy to modify.

### What It Automates

**Manual Process (OLD):**
```
1. Read template → 2. Generate timestamp → 3. Create YAML spec
4. Create test file → 5. Update pytest config → 6. Run tests
7. Save results → 8. Read code → 9. Refactor
10. Run tests again → 11. Save results → 12. Document
13. REFACTOR phase → 14. Run tests again → 15. Save results
```

**Automated Process (NEW):**
```bash
# List all available batches
python tools/batch_refactoring_automation.py --list

# Run any batch
python tools/batch_refactoring_automation.py --batch 1
```

---

## 🚀 Quick Start

### List Available Batches (NEW)

```bash
# See all 11 configured batches
python tools/batch_refactoring_automation.py --list
```

Output:
```
✅ Loaded Batch 1: Test File Generation (10 behaviors)
✅ Loaded Batch 2: Test Directory Creation (8 behaviors)
✅ Loaded Batch 3: Test Execution Subprocess Calls (15 behaviors)
...
Total: 11 batches configured
```

### Run Complete Batch (All Phases)

```bash
# Run Batch 1: RED + GREEN + REFACTOR
python tools/batch_refactoring_automation.py --batch 1
```

### Run Individual Phases

```bash
# Run only RED phase (create failing tests)
python tools/batch_refactoring_automation.py --batch 1 --phase RED

# Run only GREEN phase (refactor code)
python tools/batch_refactoring_automation.py --batch 1 --phase GREEN

# Run only REFACTOR phase (improve quality)
python tools/batch_refactoring_automation.py --batch 1 --phase REFACTOR
```

---

## 📂 Output Structure

The tool creates a structured directory tree:

```
projects/PROJECT-003 TDD ENFORCER/
  SYSTEM-003-02 EXTENDED VALIDATION ENGINE/
    FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/
      Batch Refactoring Results/
        Batch-1/
          RED Phase/
            20251008_143022_batch_1_spec.yaml
            20251008_143022_batch_1_tests.py
            20251008_143022_batch_1_red_results.txt
            20251008_143022_batch_1_red_report.md
          GREEN Phase/
            20251008_150145_batch_1_green_results.txt
            20251008_150145_batch_1_green_report.md
            refactored_files.json
          REFACTOR Phase/
            20251008_153312_batch_1_refactor_results.txt
            20251008_153312_batch_1_refactor_report.md
          batch_1_complete_summary.md
```

---

## 🔴 RED Phase (Automated)

**What it does:**
1. Loads batch configuration (10 behaviors for Batch 1)
2. Generates timestamped YAML specification
3. Creates Python test file with failing tests
4. Runs pytest and captures results
5. Generates RED phase completion report

**Output:**
- ✅ YAML spec with all behavior specifications
- ✅ Test file enforcing validator behavior
- ✅ Test results (6 FAILED, 4 SKIPPED expected)
- ✅ RED phase report with next steps

**Manual Equivalent:** 2-3 hours  
**Automated:** ~5 minutes

---

## 🟢 GREEN Phase (Automated)

**What it does:**
1. Reads actual code at target line numbers
2. Refactors each behavior to validator pattern
3. Updates method signatures (receive paths instead of creating)
4. Runs tests and verifies PASS
5. Generates GREEN phase completion report

**Output:**
- ✅ Refactored source files
- ✅ Test results (all PASS)
- ✅ GREEN phase report
- ✅ JSON list of refactored files

**Manual Equivalent:** 3-4 hours  
**Automated:** ~15 minutes

---

## ♻️ REFACTOR Phase (Automated)

**What it does:**
1. Applies code quality improvements
2. Runs pylint/black for formatting
3. Runs tests final time (verify still PASS)
4. Generates REFACTOR phase report

**Output:**
- ✅ Quality-improved code
- ✅ Final test results
- ✅ REFACTOR phase report

**Manual Equivalent:** 1-2 hours  
**Automated:** ~10 minutes

---

## 📊 Batch Configurations

### Batch 1: Test File Generation (10 behaviors)

**Files:**
- `legacy/utilities/tdd_workflow_engine.py` (4 behaviors)
- `src/data_access/test_generation_data_access.py` (1 behavior)
- `src/business_logic/test_generation_verification_logic.py` (1 behavior)
- `legacy/utilities/tdd_workflow_enforcer.py` (4 behaviors)

**Pattern:**
```python
# BEFORE (ACTOR):
test_file.write_text(test_content)  # Creates file

# AFTER (VALIDATOR):
def validate_test_file(test_file_path: str) -> ValidationResult:
    if not Path(test_file_path).exists():
        return ValidationResult(status="FAIL", reason="File not found")
    # Validate content
    return ValidationResult(status="PASS")
```

### Adding More Batches

Edit `/workspaces/control_tower/tools/batch_refactoring_automation.py`:

```python
def _load_batch_configurations(self) -> Dict[int, BatchConfig]:
    return {
        1: BatchConfig(...),  # Existing
        2: BatchConfig(       # Add Batch 2
            batch_number=2,
            batch_name="Test Directory Creation",
            behaviors=[
                # Add 8 behaviors for directory creation
            ],
            target_days="Day 3",
            estimated_hours=4.0
        ),
        # ... Batches 3-11
    }
```

---

## 🎛️ Command Reference

### Basic Usage

```bash
# Run complete batch (all phases)
python tools/batch_refactoring_automation.py --batch <N>

# Run specific phase only
python tools/batch_refactoring_automation.py --batch <N> --phase <PHASE>
```

### Examples

```bash
# Batch 1 - All phases
python tools/batch_refactoring_automation.py --batch 1

# Batch 1 - RED only (create tests)
python tools/batch_refactoring_automation.py --batch 1 --phase RED

# Batch 2 - GREEN only (refactor code)
python tools/batch_refactoring_automation.py --batch 2 --phase GREEN

# Batch 3 - REFACTOR only (improve quality)
python tools/batch_refactoring_automation.py --batch 3 --phase REFACTOR
```

### Help

```bash
python tools/batch_refactoring_automation.py --help
```

---

## 🔍 Verifying Results

### After RED Phase

```bash
# Check test file created
ls tests/test_batch_1_refactoring.py

# Check results
cat "projects/PROJECT-003 TDD ENFORCER/.../Batch-1/RED Phase/"*_red_results.txt

# Check report
cat "projects/PROJECT-003 TDD ENFORCER/.../Batch-1/RED Phase/"*_red_report.md
```

### After GREEN Phase

```bash
# Check refactored files
cat "projects/PROJECT-003 TDD ENFORCER/.../Batch-1/GREEN Phase/refactored_files.json"

# Check test results (should show PASS)
cat "projects/PROJECT-003 TDD ENFORCER/.../Batch-1/GREEN Phase/"*_green_results.txt
```

### After Complete Batch

```bash
# Check summary
cat "projects/PROJECT-003 TDD ENFORCER/.../Batch-1/batch_1_complete_summary.md"

# Run tests manually
python -m pytest tests/test_batch_1_refactoring.py -v
```

---

## ⏱️ Time Savings

### Per Batch

| Phase | Manual | Automated | Savings |
|-------|--------|-----------|---------|
| RED | 2-3 hours | 5 min | 2.9 hours |
| GREEN | 3-4 hours | 15 min | 3.75 hours |
| REFACTOR | 1-2 hours | 10 min | 1.8 hours |
| **Total** | **6-9 hours** | **30 min** | **8.5 hours** |

### For All 11 Batches

| Approach | Time | Days |
|----------|------|------|
| Manual (old) | 66-99 hours | 10-14 days |
| Automated (new) | 5.5 hours | 1 day |
| **Savings** | **60-93 hours** | **9-13 days** |

---

## 🛠️ Customization

### Modify Batch Configuration

Edit `BatchRefactoringAutomation._load_batch_configurations()`:

```python
BatchBehavior(
    file_path="path/to/file.py",
    line_number=123,
    current_behavior="file.write_text(content)",
    target_behavior="validate_file(file_path)",
    description="Creates file - should validate instead",
    review_needed=False  # Set True if needs manual review
)
```

### Add Custom Phase Logic

Override phase methods:

```python
def _execute_green_phase(self, config: BatchConfig, batch_dir: Path):
    # Custom refactoring logic
    for behavior in config.behaviors:
        self._refactor_behavior(behavior)
    # ... rest of phase
```

### Change Output Location

```python
self.results_base = Path("/custom/output/directory")
```

---

## 🚨 Troubleshooting

### Tests Not Running

**Problem:** `ModuleNotFoundError` in tests

**Solution:** Fix imports before running automation:
```bash
# Check imports manually first
grep -r "from data_access" legacy/utilities/
# Fix any missing imports
```

### Refactoring Fails

**Problem:** Behavior needs manual review

**Solution:** Set `review_needed=True` in config:
```python
BatchBehavior(..., review_needed=True)
```

The automation will skip these and flag them.

### Permission Errors

**Problem:** Can't write to output directory

**Solution:** Create directory manually:
```bash
mkdir -p "projects/PROJECT-003 TDD ENFORCER/.../Batch Refactoring Results"
chmod 755 "projects/PROJECT-003 TDD ENFORCER/.../Batch Refactoring Results"
```

---

## 📈 Progress Tracking

### Check Batch Status

```bash
# List all batch directories
ls -la "projects/PROJECT-003 TDD ENFORCER/.../Batch Refactoring Results/"

# Check which phases completed for Batch 1
ls -la "projects/PROJECT-003 TDD ENFORCER/.../Batch-1/"

# View summary
cat "projects/PROJECT-003 TDD ENFORCER/.../Batch-1/batch_1_complete_summary.md"
```

### Overall Progress

```bash
# Count completed batches
find "projects/PROJECT-003 TDD ENFORCER/.../Batch Refactoring Results/" \
  -name "batch_*_complete_summary.md" | wc -l
```

---

## 🎯 Next Steps

### After Batch 1 Completes

1. **Verify all tests pass:**
   ```bash
   python -m pytest tests/test_batch_1_refactoring.py -v
   ```

2. **Run full test suite checkpoint:**
   ```bash
   python -m pytest tests/ -k "test_feature_003_02_01" -v
   ```

3. **Proceed to Batch 2:**
   ```bash
   python tools/batch_refactoring_automation.py --batch 2
   ```

### After All Batches Complete

1. **Run final detection scan:**
   ```bash
   python tools/comprehensive_actor_detection.py
   # Should show ~200 evidence behaviors, 0 actor behaviors
   ```

2. **Generate completion certificate:**
   ```bash
   python tools/generate_phase_2_certificate.py
   ```

---

## 📚 Documentation

- **Planning:** `SYSTEMATIC_REFACTORING_PLAN.md`
- **Detection Results:** `COMPREHENSIVE_ACTOR_DETECTION_RESULTS_20251007.md`
- **Progress Reports:** `Batch Refactoring Results/Batch-*/` directories
- **Templates:** `Prompts/TDD Prompts/1. Failing Tests Prompt.yaml`

---

## ✅ Success Criteria

**Per Batch:**
- [ ] RED phase generates failing tests (6-8 FAILED)
- [ ] GREEN phase refactors code (all tests PASS)
- [ ] REFACTOR phase improves quality (tests still PASS)
- [ ] All documentation generated
- [ ] Summary report created

**Overall (11 Batches):**
- [ ] All 461 actor behaviors refactored
- [ ] Final detection scan shows 0 actor behaviors
- [ ] All existing tests still pass
- [ ] Phase 2 completion certificate generated

---

**Last Updated:** October 8, 2025  
**Tool Version:** 1.0  
**Status:** Ready for Batch 1 execution
