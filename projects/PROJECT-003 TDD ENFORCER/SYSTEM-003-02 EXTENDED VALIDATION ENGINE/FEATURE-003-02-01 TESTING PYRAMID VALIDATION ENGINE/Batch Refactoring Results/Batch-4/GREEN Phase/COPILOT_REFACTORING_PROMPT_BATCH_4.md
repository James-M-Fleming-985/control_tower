# GitHub Copilot Refactoring Request - Batch 4

**Batch:** Git Write Operations - Part 1  
**Date:** 2025-10-08  
**Total Behaviors:** 15  
**Automation Type:** GitHub Copilot Assisted Refactoring

---

## 🎯 REFACTORING OBJECTIVE

Please refactor all 15 behaviors listed below from ACTOR (file creation) to VALIDATOR (file validation).

**Current Problem:** These methods CREATE files (actor behavior - belongs in PROJECT-002)  
**Target Solution:** Change to VALIDATE files (validator behavior - belongs in PROJECT-003)

---

## 📋 REFACTORING PATTERN

BEFORE (ACTOR):
  commit_hash = repo.git.commit('-m', message)  # Creates commit

AFTER (VALIDATOR):
  def validate_phase_commit(commit_hash: str, expected_phase: str) -> ValidationResult:
      if not self.git_ops.commit_exists(commit_hash):
          return ValidationResult(status="FAIL", reason="Commit not found")
      # Validate commit message, files, etc.
      return ValidationResult(status="PASS")


---

## 🔨 BEHAVIORS TO REFACTOR

Please refactor the following files. For each one:
1. Open the file
2. Navigate to the exact line number  
3. Change ACTOR code → VALIDATOR code
4. Update method signature to accept file path parameter
5. Return ValidationResult instead of creating files
6. Ensure no file.write_text(), Path.mkdir(), or file creation remains


### Behavior 1: src/data_access/tdd_phase_repository.py:123

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 123  
**Current Code:** `self.repo.git.commit('-m', f'Phase {phase} checkpoint')`  
**Target Code:** `validate_phase_checkpoint(commit_hash: str, phase: str)`  
**Description:** Creates phase checkpoint commit - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 123
3. Find: `self.repo.git.commit('-m', f'Phase {phase} checkpoint')`
4. Change to pattern: `validate_phase_checkpoint(commit_hash: str, phase: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 2: src/data_access/tdd_phase_repository.py:234

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 234  
**Current Code:** `self.repo.git.commit('-a', '-m', 'RED phase complete')`  
**Target Code:** `validate_red_phase_commit(commit_hash: str)`  
**Description:** Creates RED phase commit - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 234
3. Find: `self.repo.git.commit('-a', '-m', 'RED phase complete')`
4. Change to pattern: `validate_red_phase_commit(commit_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 3: src/data_access/tdd_phase_repository.py:345

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 345  
**Current Code:** `self.repo.git.commit('-a', '-m', 'GREEN phase complete')`  
**Target Code:** `validate_green_phase_commit(commit_hash: str)`  
**Description:** Creates GREEN phase commit - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 345
3. Find: `self.repo.git.commit('-a', '-m', 'GREEN phase complete')`
4. Change to pattern: `validate_green_phase_commit(commit_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 4: src/data_access/tdd_phase_repository.py:456

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 456  
**Current Code:** `self.repo.git.commit('-a', '-m', 'REFACTOR phase complete')`  
**Target Code:** `validate_refactor_phase_commit(commit_hash: str)`  
**Description:** Creates REFACTOR phase commit - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 456
3. Find: `self.repo.git.commit('-a', '-m', 'REFACTOR phase complete')`
4. Change to pattern: `validate_refactor_phase_commit(commit_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 5: src/data_access/tdd_phase_repository.py:567

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 567  
**Current Code:** `self.repo.git.tag(tag_name)`  
**Target Code:** `validate_phase_tag(tag_name: str, commit_hash: str)`  
**Description:** Creates phase tag - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 567
3. Find: `self.repo.git.tag(tag_name)`
4. Change to pattern: `validate_phase_tag(tag_name: str, commit_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 6: src/data_access/tdd_phase_repository.py:678

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 678  
**Current Code:** `self.repo.git.checkout(checkpoint_hash)`  
**Target Code:** `validate_phase_checkout(current_hash: str, expected_hash: str)`  
**Description:** Checks out phase checkpoint - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 678
3. Find: `self.repo.git.checkout(checkpoint_hash)`
4. Change to pattern: `validate_phase_checkout(current_hash: str, expected_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 7: src/data_access/tdd_phase_repository.py:789

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 789  
**Current Code:** `self.repo.git.checkout('-b', branch_name)`  
**Target Code:** `validate_feature_branch(branch_name: str)`  
**Description:** Creates feature branch - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 789
3. Find: `self.repo.git.checkout('-b', branch_name)`
4. Change to pattern: `validate_feature_branch(branch_name: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 8: src/data_access/tdd_phase_repository.py:890

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 890  
**Current Code:** `self.repo.git.merge(source_branch)`  
**Target Code:** `validate_phase_merge(merge_commit_hash: str)`  
**Description:** Merges phase work - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 890
3. Find: `self.repo.git.merge(source_branch)`
4. Change to pattern: `validate_phase_merge(merge_commit_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 9: src/data_access/tdd_phase_repository.py:901

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 901  
**Current Code:** `self.repo.git.commit('-m', 'Implementation checkpoint')`  
**Target Code:** `validate_implementation_checkpoint(commit_hash: str)`  
**Description:** Creates implementation checkpoint - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 901
3. Find: `self.repo.git.commit('-m', 'Implementation checkpoint')`
4. Change to pattern: `validate_implementation_checkpoint(commit_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 10: src/data_access/tdd_phase_repository.py:1012

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 1012  
**Current Code:** `self.repo.git.commit('-m', 'Test baseline')`  
**Target Code:** `validate_test_baseline(commit_hash: str)`  
**Description:** Creates test baseline commit - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 1012
3. Find: `self.repo.git.commit('-m', 'Test baseline')`
4. Change to pattern: `validate_test_baseline(commit_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 11: src/data_access/tdd_phase_repository.py:1123

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 1123  
**Current Code:** `self.repo.git.commit('-m', f'Layer {layer} checkpoint')`  
**Target Code:** `validate_layer_checkpoint(commit_hash: str, layer: str)`  
**Description:** Creates layer checkpoint - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 1123
3. Find: `self.repo.git.commit('-m', f'Layer {layer} checkpoint')`
4. Change to pattern: `validate_layer_checkpoint(commit_hash: str, layer: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 12: src/data_access/tdd_phase_repository.py:1234

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 1234  
**Current Code:** `self.repo.git.tag(f'feature-{feature_id}-complete')`  
**Target Code:** `validate_feature_tag(tag_name: str, commit_hash: str)`  
**Description:** Creates feature complete tag - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 1234
3. Find: `self.repo.git.tag(f'feature-{feature_id}-complete')`
4. Change to pattern: `validate_feature_tag(tag_name: str, commit_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 13: src/data_access/tdd_phase_repository.py:1345

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 1345  
**Current Code:** `self.repo.git.reset('--hard', checkpoint_hash)`  
**Target Code:** `validate_checkpoint_revert(current_hash: str, checkpoint_hash: str)`  
**Description:** Reverts to checkpoint - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 1345
3. Find: `self.repo.git.reset('--hard', checkpoint_hash)`
4. Change to pattern: `validate_checkpoint_revert(current_hash: str, checkpoint_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 14: src/data_access/tdd_phase_repository.py:1456

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 1456  
**Current Code:** `self.repo.git.branch(f'backup-{timestamp}')`  
**Target Code:** `validate_backup_branch(branch_name: str)`  
**Description:** Creates backup branch - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 1456
3. Find: `self.repo.git.branch(f'backup-{timestamp}')`
4. Change to pattern: `validate_backup_branch(branch_name: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 15: src/data_access/tdd_phase_repository.py:1567

**File:** `src/data_access/tdd_phase_repository.py`  
**Line:** 1567  
**Current Code:** `self.repo.git.commit('-m', 'Phase evidence')`  
**Target Code:** `validate_evidence_commit(commit_hash: str)`  
**Description:** Commits phase evidence - should validate instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/data_access/tdd_phase_repository.py`
2. Go to line 1567
3. Find: `self.repo.git.commit('-m', 'Phase evidence')`
4. Change to pattern: `validate_evidence_commit(commit_hash: str)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


---

## ✅ ACCEPTANCE CRITERIA

After refactoring all 15 behaviors:

1. **No file creation code remains** - no `.write_text()`, `.mkdir()`, `open(..., 'w')`
2. **Methods accept file paths** - all refactored methods take `file_path: str` parameter
3. **Methods return ValidationResult** - all return structured validation results
4. **Tests pass** - run `pytest tests/test_batch_4_refactoring.py -v`
5. **Existing tests pass** - run full test suite to ensure no breakage

---

## 🚀 EXECUTION STEPS

1. **Read this entire prompt carefully**
2. **Review the refactoring pattern above**
3. **For each behavior listed:**
   - Open the file
   - Navigate to line number
   - Apply the refactoring pattern
   - Verify no file creation code remains
4. **After all refactorings:**
   - Run: `pytest tests/test_batch_4_refactoring.py -v`
   - Run: Full test suite
   - Report results

---

## 📁 FILES TO MODIFY

- `src/data_access/tdd_phase_repository.py` (line 123)
- `src/data_access/tdd_phase_repository.py` (line 234)
- `src/data_access/tdd_phase_repository.py` (line 345)
- `src/data_access/tdd_phase_repository.py` (line 456)
- `src/data_access/tdd_phase_repository.py` (line 567)
- `src/data_access/tdd_phase_repository.py` (line 678)
- `src/data_access/tdd_phase_repository.py` (line 789)
- `src/data_access/tdd_phase_repository.py` (line 890)
- `src/data_access/tdd_phase_repository.py` (line 901)
- `src/data_access/tdd_phase_repository.py` (line 1012)
- `src/data_access/tdd_phase_repository.py` (line 1123)
- `src/data_access/tdd_phase_repository.py` (line 1234)
- `src/data_access/tdd_phase_repository.py` (line 1345)
- `src/data_access/tdd_phase_repository.py` (line 1456)
- `src/data_access/tdd_phase_repository.py` (line 1567)

---

## 🔍 VERIFICATION

After completing the refactoring, please:

1. List all files you modified
2. Show the before/after code for each behavior
3. Run the test suite and share results  
4. Confirm zero file creation code remains in refactored methods

---

**READY TO REFACTOR? Please proceed with Batch 4.**
