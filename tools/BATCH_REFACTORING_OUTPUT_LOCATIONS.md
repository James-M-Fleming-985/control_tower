# 📂 Batch Refactoring Automation - Output File Locations

**Updated:** October 8, 2025  
**Purpose:** Clearly specify where all automation outputs are saved

---

## 🎯 Overview

The batch refactoring automation tool saves outputs to a structured directory tree. This document shows exactly where each file is created during execution.

---

## 📁 Base Directory Structure

```
/workspaces/control_tower/
└── projects/
    └── PROJECT-003 TDD ENFORCER/
        └── SYSTEM-003-02 EXTENDED VALIDATION ENGINE/
            └── FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/
                └── Batch Refactoring Results/    ← BASE DIRECTORY
                    ├── Batch-1/
                    ├── Batch-2/
                    ├── ...
                    └── Batch-11/
```

**Base Path:**
```
projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results/
```

---

## 🔴 RED Phase Outputs

### Directory
```
Batch Refactoring Results/
  └── Batch-1/
      └── RED Phase/    ← ALL RED PHASE FILES HERE
```

### Files Created

#### 1. YAML Specification
**Filename Pattern:** `{timestamp}_batch_{N}_spec.yaml`  
**Example:** `20251008_143022_batch_1_spec.yaml`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/RED Phase/20251008_143022_batch_1_spec.yaml
```
**Content:**
- Metadata (batch number, name, date)
- All 10 behavior specifications
- Current vs target behavior
- Test code examples

#### 2. Test File (Copy)
**Filename Pattern:** `{timestamp}_batch_{N}_tests.py`  
**Example:** `20251008_143022_batch_1_tests.py`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/RED Phase/20251008_143022_batch_1_tests.py
```
**Content:** Copy of generated test file for archival

**Original Test File Location:**
```
/workspaces/control_tower/tests/test_batch_1_refactoring.py    ← ACTUAL TEST FILE
```

#### 3. Test Results
**Filename Pattern:** `{timestamp}_batch_{N}_red_results.txt`  
**Example:** `20251008_143022_batch_1_red_results.txt`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/RED Phase/20251008_143022_batch_1_red_results.txt
```
**Content:**
- Complete pytest output
- Test names and results (PASSED/FAILED/SKIPPED)
- Error messages and stack traces
- Coverage report

#### 4. RED Phase Report
**Filename Pattern:** `{timestamp}_batch_{N}_red_report.md`  
**Example:** `20251008_143022_batch_1_red_report.md`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/RED Phase/20251008_143022_batch_1_red_report.md
```
**Content:**
- Phase completion summary
- Test results breakdown
- Behaviors targeted list
- Next steps for GREEN phase
- Files created references

---

## 🟢 GREEN Phase Outputs

### Directory
```
Batch Refactoring Results/
  └── Batch-1/
      └── GREEN Phase/    ← ALL GREEN PHASE FILES HERE
```

### Files Created

#### 1. Refactored Files List
**Filename:** `refactored_files.json`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/GREEN Phase/refactored_files.json
```
**Content:**
```json
[
  {
    "file": "legacy/utilities/tdd_workflow_engine.py",
    "line": 299,
    "behavior": "test_file.write_text()",
    "refactored_to": "validate_test_file()",
    "timestamp": "2025-10-08T15:01:45"
  },
  ...
]
```

#### 2. Test Results (After Refactoring)
**Filename Pattern:** `{timestamp}_batch_{N}_green_results.txt`  
**Example:** `20251008_150145_batch_1_green_results.txt`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/GREEN Phase/20251008_150145_batch_1_green_results.txt
```
**Content:**
- Complete pytest output (should show PASSED tests)
- Verification that refactoring worked
- Coverage report

#### 3. GREEN Phase Report
**Filename Pattern:** `{timestamp}_batch_{N}_green_report.md`  
**Example:** `20251008_150145_batch_1_green_report.md`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/GREEN Phase/20251008_150145_batch_1_green_report.md
```
**Content:**
- Phase completion summary
- Test results (PASSED count)
- Refactored behaviors list
- Success criteria verification
- Next steps for REFACTOR phase

---

## ♻️ REFACTOR Phase Outputs

### Directory
```
Batch Refactoring Results/
  └── Batch-1/
      └── REFACTOR Phase/    ← ALL REFACTOR PHASE FILES HERE
```

### Files Created

#### 1. Final Test Results
**Filename Pattern:** `{timestamp}_batch_{N}_refactor_results.txt`  
**Example:** `20251008_153312_batch_1_refactor_results.txt`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/REFACTOR Phase/20251008_153312_batch_1_refactor_results.txt
```
**Content:**
- Final pytest output (verify tests still PASS)
- Coverage report
- Quality metrics

#### 2. REFACTOR Phase Report
**Filename Pattern:** `{timestamp}_batch_{N}_refactor_report.md`  
**Example:** `20251008_153312_batch_1_refactor_report.md`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/REFACTOR Phase/20251008_153312_batch_1_refactor_report.md
```
**Content:**
- Phase completion summary
- Final test results
- Code quality improvements applied
- Batch completion confirmation

---

## 📊 Batch Summary

### Directory
```
Batch Refactoring Results/
  └── Batch-1/
      └── batch_1_complete_summary.md    ← BATCH ROOT LEVEL
```

### File Created

**Filename Pattern:** `batch_{N}_complete_summary.md`  
**Example:** `batch_1_complete_summary.md`  
**Full Path:**
```
projects/.../Batch Refactoring Results/Batch-1/batch_1_complete_summary.md
```
**Content:**
- Complete batch overview
- All phase results consolidated
- File locations for all outputs
- Success confirmation

---

## 🎯 Complete Directory Tree (Example for Batch 1)

```
projects/PROJECT-003 TDD ENFORCER/
  SYSTEM-003-02 EXTENDED VALIDATION ENGINE/
    FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/
      Batch Refactoring Results/
        Batch-1/
          │
          ├── RED Phase/
          │   ├── 20251008_143022_batch_1_spec.yaml
          │   ├── 20251008_143022_batch_1_tests.py
          │   ├── 20251008_143022_batch_1_red_results.txt
          │   └── 20251008_143022_batch_1_red_report.md
          │
          ├── GREEN Phase/
          │   ├── refactored_files.json
          │   ├── 20251008_150145_batch_1_green_results.txt
          │   └── 20251008_150145_batch_1_green_report.md
          │
          ├── REFACTOR Phase/
          │   ├── 20251008_153312_batch_1_refactor_results.txt
          │   └── 20251008_153312_batch_1_refactor_report.md
          │
          └── batch_1_complete_summary.md
```

---

## 📝 Console Output Example

When you run the automation, it will print file locations:

```bash
$ python tools/batch_refactoring_automation.py --batch 1

================================================================================
🚀 BATCH 1 REFACTORING AUTOMATION
================================================================================
Batch Name: Test File Generation
Behaviors: 10
Target: Days 1-2
Estimated: 8.0 hours
================================================================================

🔴 RED PHASE - Generating Failing Tests
================================================================================

📂 Output Directory:
   projects/.../Batch-1/RED Phase

✅ Generated YAML spec:
   📄 projects/.../Batch-1/RED Phase/20251008_143022_batch_1_spec.yaml

✅ Generated test file:
   📄 /workspaces/control_tower/tests/test_batch_1_refactoring.py

✅ Executed tests: 6 FAILED, 4 SKIPPED
   📄 Results saved to: projects/.../Batch-1/RED Phase/20251008_143022_batch_1_red_results.txt

✅ Generated RED report:
   📄 projects/.../Batch-1/RED Phase/20251008_143022_batch_1_red_report.md

🟢 GREEN PHASE - Refactoring to Validator Behavior
================================================================================

📂 Output Directory:
   projects/.../Batch-1/GREEN Phase

📝 Refactoring: legacy/utilities/tdd_workflow_engine.py:299
...

✅ Refactored files list saved:
   📄 projects/.../Batch-1/GREEN Phase/refactored_files.json

✅ Tests after refactoring: 10 PASSED
   📄 Results saved to: projects/.../Batch-1/GREEN Phase/20251008_150145_batch_1_green_results.txt

✅ Generated GREEN report:
   📄 projects/.../Batch-1/GREEN Phase/20251008_150145_batch_1_green_report.md

♻️  REFACTOR PHASE - Improving Code Quality
================================================================================

📂 Output Directory:
   projects/.../Batch-1/REFACTOR Phase

♻️  Applying code quality improvements...

✅ Final tests: 10 PASSED
   📄 Results saved to: projects/.../Batch-1/REFACTOR Phase/20251008_153312_batch_1_refactor_results.txt

✅ Generated REFACTOR report:
   📄 projects/.../Batch-1/REFACTOR Phase/20251008_153312_batch_1_refactor_report.md

📊 Generated batch summary:
   📄 projects/.../Batch-1/batch_1_complete_summary.md

================================================================================
✅ BATCH 1 AUTOMATION COMPLETE
================================================================================

📂 All outputs saved to:
   projects/.../Batch-1

📋 Phase directories:
   📁 projects/.../Batch-1/RED Phase
   📁 projects/.../Batch-1/GREEN Phase
   📁 projects/.../Batch-1/REFACTOR Phase
```

---

## 🔍 How to Find Your Files

### After Running Batch 1

```bash
# Navigate to batch directory
cd "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results/Batch-1"

# List all files
find . -type f

# Output:
./RED Phase/20251008_143022_batch_1_spec.yaml
./RED Phase/20251008_143022_batch_1_tests.py
./RED Phase/20251008_143022_batch_1_red_results.txt
./RED Phase/20251008_143022_batch_1_red_report.md
./GREEN Phase/refactored_files.json
./GREEN Phase/20251008_150145_batch_1_green_results.txt
./GREEN Phase/20251008_150145_batch_1_green_report.md
./REFACTOR Phase/20251008_153312_batch_1_refactor_results.txt
./REFACTOR Phase/20251008_153312_batch_1_refactor_report.md
./batch_1_complete_summary.md
```

### Read Specific Files

```bash
# Read RED phase report
cat "RED Phase/"*_red_report.md

# Read GREEN phase report
cat "GREEN Phase/"*_green_report.md

# Read final summary
cat batch_1_complete_summary.md

# Read test results
cat "RED Phase/"*_red_results.txt
cat "GREEN Phase/"*_green_results.txt
cat "REFACTOR Phase/"*_refactor_results.txt
```

---

## ✅ File Location Summary Table

| File Type | Location | Filename Pattern |
|-----------|----------|------------------|
| **YAML Spec** | `Batch-{N}/RED Phase/` | `{timestamp}_batch_{N}_spec.yaml` |
| **Test File (copy)** | `Batch-{N}/RED Phase/` | `{timestamp}_batch_{N}_tests.py` |
| **Test File (actual)** | `/tests/` | `test_batch_{N}_refactoring.py` |
| **RED Results** | `Batch-{N}/RED Phase/` | `{timestamp}_batch_{N}_red_results.txt` |
| **RED Report** | `Batch-{N}/RED Phase/` | `{timestamp}_batch_{N}_red_report.md` |
| **Refactored Files** | `Batch-{N}/GREEN Phase/` | `refactored_files.json` |
| **GREEN Results** | `Batch-{N}/GREEN Phase/` | `{timestamp}_batch_{N}_green_results.txt` |
| **GREEN Report** | `Batch-{N}/GREEN Phase/` | `{timestamp}_batch_{N}_green_report.md` |
| **REFACTOR Results** | `Batch-{N}/REFACTOR Phase/` | `{timestamp}_batch_{N}_refactor_results.txt` |
| **REFACTOR Report** | `Batch-{N}/REFACTOR Phase/` | `{timestamp}_batch_{N}_refactor_report.md` |
| **Batch Summary** | `Batch-{N}/` | `batch_{N}_complete_summary.md` |

---

## 🎯 Quick Reference

### Where is my YAML specification?
```
Batch Refactoring Results/Batch-{N}/RED Phase/{timestamp}_batch_{N}_spec.yaml
```

### Where are my test results?
```
RED:      Batch-{N}/RED Phase/{timestamp}_batch_{N}_red_results.txt
GREEN:    Batch-{N}/GREEN Phase/{timestamp}_batch_{N}_green_results.txt
REFACTOR: Batch-{N}/REFACTOR Phase/{timestamp}_batch_{N}_refactor_results.txt
```

### Where is my final summary?
```
Batch Refactoring Results/Batch-{N}/batch_{N}_complete_summary.md
```

### Where is the actual test file that pytest runs?
```
/workspaces/control_tower/tests/test_batch_{N}_refactoring.py
```

---

**Last Updated:** October 8, 2025  
**Tool Version:** 1.0  
**All output locations clearly specified** ✅
