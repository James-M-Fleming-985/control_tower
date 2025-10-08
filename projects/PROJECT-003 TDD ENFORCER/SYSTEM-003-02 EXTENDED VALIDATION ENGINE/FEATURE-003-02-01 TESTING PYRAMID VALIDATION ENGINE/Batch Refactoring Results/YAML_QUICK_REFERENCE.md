# YAML-Driven Batch Refactoring - Quick Reference

**Version:** 2.0  
**Date:** October 8, 2025

---

## 📋 Quick Commands

### List All Batches
```bash
python tools/batch_refactoring_automation.py --list
```

### Run Complete Batch
```bash
python tools/batch_refactoring_automation.py --batch 1
```

### Run Specific Phase
```bash
python tools/batch_refactoring_automation.py --batch 1 --phase RED
python tools/batch_refactoring_automation.py --batch 1 --phase GREEN
python tools/batch_refactoring_automation.py --batch 1 --phase REFACTOR
```

---

## 📁 File Locations

### YAML Specs (Planning)
```
projects/PROJECT-003 TDD ENFORCER/
  SYSTEM-003-02 EXTENDED VALIDATION ENGINE/
    FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/
      Batch Refactoring Results/
        Batch Specs/
          ├── Batch-1-spec.yaml
          ├── Batch-2-spec.yaml
          ├── ...
          └── Batch-11-spec.yaml
```

### Automation Tool (Execution)
```
tools/
  ├── batch_refactoring_automation.py  ← Main tool
  ├── BATCH_REFACTORING_AUTOMATION_README.md
  ├── YAML_DRIVEN_AUTOMATION_UPDATE.md
  └── BATCH_REFACTORING_QUICK_REFERENCE.md
```

### Output (Results)
```
Batch Refactoring Results/
  Batch-{N}/
    ├── RED Phase/
    │   ├── {timestamp}_batch_{N}_spec.yaml
    │   ├── {timestamp}_batch_{N}_tests.py
    │   ├── {timestamp}_batch_{N}_red_results.txt
    │   └── {timestamp}_batch_{N}_red_report.md
    ├── GREEN Phase/
    │   ├── {timestamp}_batch_{N}_green_results.txt
    │   ├── {timestamp}_batch_{N}_green_report.md
    │   └── refactored_files.json
    └── REFACTOR Phase/
        ├── {timestamp}_batch_{N}_refactor_results.txt
        ├── {timestamp}_batch_{N}_refactor_report.md
        └── batch_{N}_complete_summary.md
```

---

## 🔄 Workflow

### 1. Review Available Batches
```bash
python tools/batch_refactoring_automation.py --list
```

### 2. Execute Batch
```bash
# Option A: Run all phases
python tools/batch_refactoring_automation.py --batch 1

# Option B: Run phases individually
python tools/batch_refactoring_automation.py --batch 1 --phase RED
python tools/batch_refactoring_automation.py --batch 1 --phase GREEN
python tools/batch_refactoring_automation.py --batch 1 --phase REFACTOR
```

### 3. Review Results
```bash
# Check output directory
ls "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results/Batch-1/"

# Read batch summary
cat "projects/.../Batch-1/batch_1_complete_summary.md"
```

### 4. Proceed to Next Batch
```bash
python tools/batch_refactoring_automation.py --batch 2
```

---

## 📊 All 11 Batches

| # | Name | Behaviors | Days | Hours | Status |
|---|------|-----------|------|-------|--------|
| 1 | Test File Generation | 10 | 1-2 | 8.0 | ✅ Ready |
| 2 | Test Directory Creation | 8 | 3 | 4.0 | ✅ Ready |
| 3 | Test Execution | 15 | 4 | 6.0 | ✅ Ready |
| 4 | Git Operations Part 1 | 15 | 5 | 6.0 | ✅ Ready |
| 5 | Git Operations Part 2 | 15 | 6 | 6.0 | ⚠️ Placeholder |
| 6 | Git Operations Part 3 | 15 | 7 | 6.0 | ⚠️ Placeholder |
| 7 | Evidence Review Part 1 | 50 | 8am | 3.0 | ⚠️ Placeholder |
| 8 | Evidence Review Part 2 | 50 | 8pm | 3.0 | ⚠️ Placeholder |
| 9 | Evidence Review Part 3 | 50 | 9am | 3.0 | ⚠️ Placeholder |
| 10 | Evidence Review Part 4 | 50 | 9pm | 3.0 | ⚠️ Placeholder |
| 11 | Cleanup & Validation | Var | 10 | 8.0 | ✅ Ready |

**Total:** ~461 behaviors across 11 batches

---

## 🎯 Expected Outputs

### RED Phase
- ✅ YAML spec with behavior definitions
- ✅ Test file with failing tests
- ✅ Test results showing FAILURES/SKIPS
- ✅ RED phase report

### GREEN Phase
- ✅ Refactored source files
- ✅ Test results showing PASSES
- ✅ List of refactored files (JSON)
- ✅ GREEN phase report

### REFACTOR Phase
- ✅ Quality-improved code
- ✅ Test results showing PASSES (still)
- ✅ REFACTOR phase report
- ✅ Complete batch summary

---

## 🔧 Modifying Batches

### To Edit a Batch Specification
1. Open the YAML file:
   ```bash
   code "projects/.../Batch Specs/Batch-1-spec.yaml"
   ```

2. Edit behaviors, patterns, or success criteria

3. Save file

4. Run batch (tool automatically loads updated YAML):
   ```bash
   python tools/batch_refactoring_automation.py --batch 1
   ```

### To Add a New Batch
1. Create new YAML file:
   ```bash
   cp "Batch-1-spec.yaml" "Batch-12-spec.yaml"
   ```

2. Update metadata and behaviors

3. Save file

4. Tool automatically detects it:
   ```bash
   python tools/batch_refactoring_automation.py --list
   ```

---

## ✅ Success Indicators

### Batch Successfully Completed When:
- ✅ RED phase: Tests created and FAIL
- ✅ GREEN phase: Code refactored and tests PASS
- ✅ REFACTOR phase: Quality improved and tests still PASS
- ✅ Complete summary generated
- ✅ All files saved to output directory

### Phase 2 Complete When:
- ✅ All 11 batches executed
- ✅ Final detection scan shows 0 actor behaviors
- ✅ ~200 evidence behaviors remain (validation evidence)
- ✅ All tests passing
- ✅ Completion certificate generated

---

## 🚨 Troubleshooting

### YAML Not Loading?
```bash
# Check if spec file exists
ls "projects/.../Batch Specs/"

# Verify YAML syntax
python -c "import yaml; print(yaml.safe_load(open('Batch-1-spec.yaml')))"
```

### Tool Not Found?
```bash
# Run from workspace root
cd /workspaces/control_tower
python tools/batch_refactoring_automation.py --list
```

### Tests Failing?
```bash
# Check test output in RED phase results
cat "Batch Refactoring Results/Batch-1/RED Phase/*_red_results.txt"

# Review RED phase report
cat "Batch Refactoring Results/Batch-1/RED Phase/*_red_report.md"
```

---

**Quick Start:** Run `python tools/batch_refactoring_automation.py --list` to see all available batches and begin execution.
