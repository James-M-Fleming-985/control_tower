# SYSTEM-003-03 Scripts - Quick Reference Card

## 🚀 Most Common Commands

### ⭐ Execute Layer (Full TDD Cycle - NEW!)
```bash
make execute-layer LAYER=LAYER-003-03-02-01 PHASE=full-cycle
```
**Time**: Varies (manual implementation required)  
**Use When**: Implementing new layer from requirements, auto-generates tests and stubs  
**Output**: Auto-saves evidence to Testing Outputs/ and Requirements Verification/

---

### Execute All Layers (Batch - NEW!)
```bash
make execute-all                    # Sequential execution
make execute-all-parallel           # Parallel (faster)
```
**Time**: Varies  
**Use When**: Executing complete system implementation

---

### Test a Single Layer (Fastest - Use This Daily)
```bash
python scripts/run_layer_tests.py --layer LAYER-003-03-01-01 --update-verification
# OR
make test-layer LAYER=LAYER-003-03-01-01
```
**Time**: ~10-30 seconds  
**Use When**: Testing existing layer implementation

---

### Verify a Complete Feature (Before PR)
```bash
python scripts/verify_feature.py --feature FEATURE-003-03-01 --verbose
# OR
make verify-feature FEATURE=FEATURE-003-03-01
```
**Time**: ~2-5 minutes  
**Use When**: Ready to submit pull request, verify feature integration

---

### Full System Verification (Before Merge)
```bash
python scripts/run_system_verification.py
# OR
make verify-system
```
**Time**: ~10-15 minutes  
**Use When**: Before merging to main, complete system validation

---

### Check Requirements Traceability (Weekly)
```bash
python scripts/validate_traceability.py
# OR
make validate-traceability
```
**Time**: ~1-2 minutes  
**Use When**: Weekly compliance check, before releases

---

## 📊 All Scripts at a Glance

| Script | Purpose | Time | Exit 0 = Success |
|--------|---------|------|-----------------|
| **`execute_layer.py`** ⭐ | **Make layer executable (TDD)** | **Varies** | **Tests pass, coverage ≥90%** |
| **`execute_all_layers.py`** | **Batch execute all layers** | **Varies** | **All layers pass** |
| `run_layer_tests.py` | Test single layer | 10-30s | All tests pass, AC ≥50% |
| `verify_feature.py` | Verify complete feature | 2-5min | All layers + integration pass |
| `run_system_verification.py` | Complete system check | 10-15min | All features + e2e pass |
| `validate_traceability.py` | Check req traceability | 1-2min | ≥90% compliance, 0 orphans |

---

## 🎯 Testing Strategy Summary

**✅ RECOMMENDED: Layer-Level Testing**

```
Daily:    run_layer_tests.py      (10s feedback)
         ↓
PR:      verify_feature.py        (2min verification)  
         ↓
Merge:   run_system_verification.py (15min full check)
         ↓
Weekly:  validate_traceability.py  (compliance audit)
```

**Why Layer-Level?**
- 3x faster than feature-level
- Precise failure location
- Better isolation
- Parallel CI/CD execution

---

## 📁 Key Directories

```
SYSTEM-003-03/
├── scripts/               ← All 4 executable scripts here
├── FEATURE-XXX/
│   ├── LAYER-XXX/
│   │   ├── Testing Outputs/        ← Test reports saved here
│   │   └── Requirements Verification/  ← Updated by --update-verification
```

---

## 🔧 Common Options

```bash
--verbose, -v              # Detailed output
--update-verification      # Update requirements_verification_template.yaml
--update-yaml             # Update feature YAML status
--phase red|green|refactor # Specific TDD phase
--layer LAYER-003-03-01-01 # Specific layer
--feature FEATURE-003-03-01 # Specific feature
--skip-layers             # Skip layer tests in feature verification
--skip-e2e                # Skip system E2E tests
--skip-performance        # Skip performance tests
```

---

## 📊 Coverage Thresholds

| Level | Unit | Integration | E2E |
|-------|------|-------------|-----|
| Layer | 90% | 80% | - |
| Feature | 90% | 85% | 70% |
| System | 95% | 90% | 80% |

---

## ✅ Quality Gates (Always Enforced)

- ✅ No mocks (unless requirement allows)
- ✅ Real assertions (no `assert True`)
- ✅ Team size appropriate patterns
- ✅ Requirements traceability (# REQ-XXX)

---

## 🔍 Quick Troubleshooting

**Tests failing?**
```bash
# Run with verbose output
python scripts/run_layer_tests.py --layer LAYER-XXX --verbose
```

**Coverage too low?**
```bash
# Check which files need tests
cat Testing\ Outputs/coverage_report.html
```

**Orphaned code detected?**
```bash
# Add # REQ-XXX comments to implementation files
python scripts/validate_traceability.py
```

**Feature verification failing?**
```bash
# Test each layer individually first
python scripts/run_layer_tests.py --layer LAYER-003-03-01-01
python scripts/run_layer_tests.py --layer LAYER-003-03-01-02
python scripts/run_layer_tests.py --layer LAYER-003-03-01-03
```

---

## 📚 Full Documentation

- **scripts/README.md** - Complete usage guide
- **COMPANION_SCRIPTS_SUMMARY.md** - Implementation summary
- **Testing Outputs/README.md** - Test artifacts guide
- **Requirements Verification/README.md** - Verification process

---

**Quick Help**: `python scripts/<script>.py --help`

---

**Created**: October 8, 2025
