# Quick Reference: Using Generated Copilot Refactoring Prompts

## 📂 All Generated Prompts

```bash
# List all prompts
find "projects/PROJECT-003 TDD ENFORCER" -name "COPILOT_REFACTORING_PROMPT*.md" | sort

# Result: 11 prompts ready to use
```

## 🚀 How to Execute a Batch Refactoring

### Step 1: Read the Prompt

```bash
# Example for Batch 1
cat "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results/Batch-1/GREEN Phase/COPILOT_REFACTORING_PROMPT_BATCH_1.md"
```

### Step 2: Give to Copilot

Simply say to Copilot:
```
"Please refactor Batch 1 according to:
projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results/Batch-1/GREEN Phase/COPILOT_REFACTORING_PROMPT_BATCH_1.md"
```

### Step 3: Review Changes

Copilot will:
- Open each file mentioned in the prompt
- Navigate to the specific line number
- Refactor ACTOR code to VALIDATOR code
- Return `ValidationResult` instead of creating files
- Preserve existing functionality

### Step 4: Run Tests

```bash
# Run tests for the batch you just refactored
pytest tests/test_batch_1_refactoring.py -v

# Expected: All tests should pass (no longer SKIPPED)
```

### Step 5: Verify No Regressions

```bash
# Run full test suite
pytest tests/ -v

# Verify: No existing tests broke
```

## 📊 Batch Priority Order

Execute in this order for best results:

| Priority | Batch | Behaviors | Why Execute This Order |
|----------|-------|-----------|------------------------|
| 1 | Batch 1 | 10 | Test file generation - foundational |
| 2 | Batch 2 | 8 | Directory creation - supports test generation |
| 3 | Batch 3 | 15 | Test execution - verifies refactorings work |
| 4 | Batch 4 | 15 | Git operations - most complex |
| 5 | Batch 5 | 1 | Git operations continued |
| 6 | Batch 6 | 1 | Git operations completed |
| 7 | Batch 7 | 1 | Evidence review - determine if ACTOR or EVIDENCE |
| 8 | Batch 8 | 1 | Evidence review continued |
| 9 | Batch 9 | 1 | Evidence review continued |
| 10 | Batch 10 | 1 | Evidence review completed |
| 11 | Batch 11 | 0 | Cleanup and final validation |

## 🎯 What Each Prompt Contains

Each `COPILOT_REFACTORING_PROMPT_BATCH_N.md` includes:

1. **Objective:** What this batch refactors
2. **Pattern:** BEFORE/AFTER code examples
3. **Behaviors:** Complete list with:
   - File path
   - Line number
   - Current code (ACTOR)
   - Target code (VALIDATOR)
   - Description
4. **Step-by-Step Instructions:** How to refactor
5. **Acceptance Criteria:** How to verify success
6. **Verification Steps:** Testing approach

## ⚡ Quick Commands

```bash
# View Batch 1 prompt
less "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results/Batch-1/GREEN Phase/COPILOT_REFACTORING_PROMPT_BATCH_1.md"

# View Batch 1 spec
less "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results/Batch-1/RED Phase/"*_batch_1_spec.yaml

# Run Batch 1 tests
pytest tests/test_batch_1_refactoring.py -v

# Run ALL batch tests
pytest tests/test_batch_*_refactoring.py -v
```

## 📝 Tracking Progress

Create a checklist:

- [ ] Batch 1: Test File Generation (10 behaviors)
  - [x] Behavior 1: test_file.write_text → validate_test_file_for_criterion
  - [x] Behavior 2: impl_file.write_text → validate_implementation_file
  - [x] Behavior 3: test_file.write_text → validate_test_update
  - [ ] Behavior 4: py_file.write_text → validate_python_file
  - [ ] Behavior 5: demo_test.write_text → validate_demo_test
  - [ ] Behavior 6: demo_test.write_text → validate_generated_test
  - [ ] Behavior 7: f.write → validate_parser_file
  - [ ] Behavior 8: f.write → validate_generator_file
  - [ ] Behavior 9: REVIEW (baseline file)
  - [ ] Behavior 10: REVIEW (results file)

- [ ] Batch 2: Test Directory Creation (8 behaviors)
- [ ] Batch 3: Test Execution Subprocess (15 behaviors)
- [ ] Batch 4: Git Write Operations Part 1 (15 behaviors)
- [ ] Batch 5: Git Write Operations Part 2 (1 behavior)
- [ ] Batch 6: Git Write Operations Part 3 (1 behavior)
- [ ] Batch 7: Evidence Review Part 1 (1 behavior)
- [ ] Batch 8: Evidence Review Part 2 (1 behavior)
- [ ] Batch 9: Evidence Review Part 3 (1 behavior)
- [ ] Batch 10: Evidence Review Part 4 (1 behavior)
- [ ] Batch 11: Cleanup & Validation (0 behaviors)

## 🎓 Tips for Success

1. **One Batch at a Time:** Complete each batch before moving to next
2. **Run Tests Frequently:** After each behavior refactoring
3. **Commit After Each Batch:** Git commits provide rollback points
4. **Review Edge Cases:** Some behaviors may need custom handling
5. **Ask Copilot for Help:** If stuck, reference the prompt again

## 🚨 Common Issues

### Issue: Tests Still SKIPPED
**Cause:** Refactoring not complete or tests not updated  
**Fix:** Remove `@pytest.mark.skip` decorator after refactoring behavior

### Issue: ValidationResult Not Found
**Cause:** Import missing  
**Fix:** Add `from validation_result import ValidationResult` to file

### Issue: Tests Failing
**Cause:** Refactoring broke existing functionality  
**Fix:** Review behavior, ensure validation logic correct, check return types

## ✅ When Complete

After all 11 batches refactored:

```bash
# Run detection scan
python tools/comprehensive_actor_detection.py

# Expected: 0 ACTOR behaviors, ~200 EVIDENCE behaviors

# Run full test suite
pytest tests/ -v --cov

# Expected: All tests pass, good coverage
```

---

**Generated:** October 8, 2025  
**Purpose:** Quick reference for executing Copilot-driven refactoring  
**Status:** Ready to use anytime
