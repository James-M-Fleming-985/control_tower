# 📋 Batch Refactoring Automation - Quick Reference Card

**Version:** 1.1 (with explicit output locations)  
**Date:** October 8, 2025

---

## ⚡ Quick Start

```bash
# Run complete batch (all phases)
python tools/batch_refactoring_automation.py --batch 1

# Run specific phase only
python tools/batch_refactoring_automation.py --batch 1 --phase RED
python tools/batch_refactoring_automation.py --batch 1 --phase GREEN
python tools/batch_refactoring_automation.py --batch 1 --phase REFACTOR
```

---

## 📂 Where Files Are Saved

### Base Directory
```
projects/PROJECT-003 TDD ENFORCER/
  SYSTEM-003-02 EXTENDED VALIDATION ENGINE/
    FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/
      Batch Refactoring Results/Batch-{N}/
```

### RED Phase Files
```
Batch-{N}/RED Phase/
  ├── {timestamp}_batch_{N}_spec.yaml         (YAML specification)
  ├── {timestamp}_batch_{N}_tests.py          (Test file copy)
  ├── {timestamp}_batch_{N}_red_results.txt   (pytest output)
  └── {timestamp}_batch_{N}_red_report.md     (Phase report)
```

### GREEN Phase Files
```
Batch-{N}/GREEN Phase/
  ├── refactored_files.json                    (Files changed)
  ├── {timestamp}_batch_{N}_green_results.txt  (pytest output)
  └── {timestamp}_batch_{N}_green_report.md    (Phase report)
```

### REFACTOR Phase Files
```
Batch-{N}/REFACTOR Phase/
  ├── {timestamp}_batch_{N}_refactor_results.txt  (Final pytest)
  └── {timestamp}_batch_{N}_refactor_report.md    (Phase report)
```

### Summary
```
Batch-{N}/batch_{N}_complete_summary.md  (Complete overview)
```

---

## 🎯 What Each Phase Does

| Phase | Duration | Actions | Output |
|-------|----------|---------|--------|
| **RED** | 5 min | Generate tests, run pytest (expect FAIL) | YAML spec, test file, results, report |
| **GREEN** | 15 min | Refactor code, run pytest (expect PASS) | Refactored files list, results, report |
| **REFACTOR** | 10 min | Improve quality, run pytest (verify PASS) | Final results, report |

---

## 📊 Console Output Format

```
🔴 RED PHASE
📂 Output Directory: .../Batch-1/RED Phase
✅ Generated YAML spec:
   📄 .../RED Phase/{timestamp}_batch_1_spec.yaml
✅ Generated test file:
   📄 /workspaces/control_tower/tests/test_batch_1_refactoring.py
✅ Executed tests: 6 FAILED, 4 SKIPPED
   📄 Results saved to: .../RED Phase/{timestamp}_batch_1_red_results.txt
✅ Generated RED report:
   📄 .../RED Phase/{timestamp}_batch_1_red_report.md

🟢 GREEN PHASE
📂 Output Directory: .../Batch-1/GREEN Phase
📝 Refactoring: {file}:{line}
✅ Refactored files list saved:
   📄 .../GREEN Phase/refactored_files.json
✅ Tests after refactoring: 10 PASSED
   📄 Results saved to: .../GREEN Phase/{timestamp}_batch_1_green_results.txt
✅ Generated GREEN report:
   📄 .../GREEN Phase/{timestamp}_batch_1_green_report.md

♻️ REFACTOR PHASE
📂 Output Directory: .../Batch-1/REFACTOR Phase
✅ Final tests: 10 PASSED
   📄 Results saved to: .../REFACTOR Phase/{timestamp}_batch_1_refactor_results.txt
✅ Generated REFACTOR report:
   📄 .../REFACTOR Phase/{timestamp}_batch_1_refactor_report.md

📊 Generated batch summary:
   📄 .../Batch-1/batch_1_complete_summary.md

📂 All outputs saved to: .../Batch-1
```

---

## 🔍 How to Find Files

### Navigate to Batch Directory
```bash
cd "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results/Batch-1"
```

### List All Files
```bash
find . -type f
```

### Read Specific Files
```bash
# RED phase
cat "RED Phase/"*_red_report.md
cat "RED Phase/"*_red_results.txt

# GREEN phase
cat "GREEN Phase/"*_green_report.md
cat "GREEN Phase/"*_green_results.txt

# REFACTOR phase
cat "REFACTOR Phase/"*_refactor_report.md
cat "REFACTOR Phase/"*_refactor_results.txt

# Summary
cat batch_1_complete_summary.md
```

---

## ⏱️ Time Savings

| Metric | Manual | Automated | Savings |
|--------|--------|-----------|---------|
| Per batch | 12.5 hrs | 0.5 hrs | 12 hrs (96%) |
| All 11 batches | 88 hrs | 5.5 hrs | 82.5 hrs (93%) |
| Calendar time | 14 days | 1 day | 13 days |

---

## ✅ Success Indicators

### RED Phase Success
- ✅ Tests created (10 total)
- ✅ Tests FAIL or SKIP (expected)
- ✅ YAML spec generated
- ✅ RED report created

### GREEN Phase Success
- ✅ Code refactored
- ✅ Tests PASS (10 total)
- ✅ Refactored files list created
- ✅ GREEN report created

### REFACTOR Phase Success
- ✅ Quality improved
- ✅ Tests still PASS
- ✅ REFACTOR report created

### Batch Complete
- ✅ All phases completed
- ✅ Summary generated
- ✅ All files in correct locations

---

## 🎨 Icon Reference

| Icon | Meaning |
|------|---------|
| 📂 | Output directory |
| 📄 | Individual file path |
| 📁 | Folder in directory tree |
| 📊 | Batch summary |
| ✅ | Action completed successfully |
| 🔴 | RED phase (failing tests) |
| 🟢 | GREEN phase (refactoring) |
| ♻️ | REFACTOR phase (quality) |
| 📝 | Refactoring in progress |
| ⚠️ | Warning/review needed |

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `batch_refactoring_automation.py` | Main automation tool |
| `BATCH_REFACTORING_AUTOMATION_README.md` | Complete user guide |
| `BATCH_REFACTORING_OUTPUT_LOCATIONS.md` | File location reference |
| `BATCH_REFACTORING_AUTOMATION_DECISION.md` | Manual vs automated analysis |
| `AUTOMATION_TOOL_UPDATE_SUMMARY.md` | Recent updates |
| This file | Quick reference card |

---

## 🚀 Next Steps

1. **Run Batch 1:**
   ```bash
   python tools/batch_refactoring_automation.py --batch 1
   ```

2. **Review Results:**
   ```bash
   cat "projects/.../Batch-1/batch_1_complete_summary.md"
   ```

3. **Verify Tests:**
   ```bash
   python -m pytest tests/test_batch_1_refactoring.py -v
   ```

4. **Configure Next Batch:**
   - Edit `batch_refactoring_automation.py`
   - Add Batch 2 configuration (8 behaviors)

5. **Run All Batches:**
   ```bash
   for i in {1..11}; do
     python tools/batch_refactoring_automation.py --batch $i
   done
   ```

---

**Last Updated:** October 8, 2025  
**Status:** Production Ready ✅  
**All output locations clearly specified** ✅
