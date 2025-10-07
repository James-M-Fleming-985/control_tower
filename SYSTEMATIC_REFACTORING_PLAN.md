# 🔧 SYSTEMATIC REFACTORING PLAN
**PROJECT-003 TDD ENFORCER - Actor to Validator Conversion**

**Date:** October 7, 2025  
**Total Behaviors to Refactor:** 461  
**Approach:** Systematic, test-driven, batch-by-batch  

---

## 🎯 THE PLAN: SIMPLE AND DIRECT

You're right - we don't need complex categorization scripts. We have **461 specific line numbers** where actor behavior exists. We systematically refactor each one to validator behavior, testing at strategic checkpoints.

### Core Principle:
```
For each actor behavior:
1. Write test that enforces validator behavior (RED)
2. Refactor to pass test (GREEN)
3. Improve code quality (REFACTOR)
4. Move to next behavior
5. Run full test suite at checkpoints
```

---

## 📊 THE 461 BEHAVIORS - ORGANIZED BY TYPE

### Type 1: File Writing (142 instances)
**Pattern:** `open(..., 'w')` or `open(..., 'a')`

**Refactoring Strategy:**
```python
# BEFORE (ACTOR):
with open(test_file, 'w') as f:
    f.write(test_content)

# AFTER (VALIDATOR):
def validate_test_file(test_file_path: str) -> ValidationResult:
    """Receives path from PROJECT-002, validates content exists"""
    if not Path(test_file_path).exists():
        return ValidationResult(status="FAIL", reason="Test file not found")
    
    content = Path(test_file_path).read_text()
    # Validate content meets requirements
    return ValidationResult(status="PASS")
```

**Test Pattern:**
```python
def test_validator_does_not_create_files():
    """Validator must not create files - only validate existing ones"""
    validator = TDDWorkflowEnforcer()
    
    # Mock PROJECT-002 provides file path
    result = validator.validate_test_file("/path/to/test.py")
    
    # Validator should NOT have created this file
    assert not os.path.exists("/path/to/test.py")
    assert result.status == "FAIL"  # File doesn't exist
```

---

### Type 2: Directory Creation (58 instances)
**Pattern:** `.mkdir(parents=True, exist_ok=True)`

**Refactoring Strategy:**
```python
# BEFORE (ACTOR):
test_dir.mkdir(parents=True, exist_ok=True)

# AFTER (VALIDATOR):
def validate_directory_structure(test_dir: str) -> ValidationResult:
    """Receives directory path from PROJECT-002, validates structure"""
    test_dir = Path(test_dir)
    
    if not test_dir.exists():
        return ValidationResult(status="FAIL", reason="Test directory not found")
    
    if not test_dir.is_dir():
        return ValidationResult(status="FAIL", reason="Path is not a directory")
    
    return ValidationResult(status="PASS")
```

**Test Pattern:**
```python
def test_validator_does_not_create_directories():
    """Validator must not create directories"""
    validator = TDDWorkflowEnforcer()
    
    result = validator.validate_directory_structure("/path/to/tests")
    
    # Should NOT have created directory
    assert not os.path.exists("/path/to/tests")
    assert result.status == "FAIL"
```

---

### Type 3: Path Write Methods (10 instances)
**Pattern:** `.write_text(...)` or `.write_bytes(...)`

**Refactoring Strategy:**
```python
# BEFORE (ACTOR):
init_file.write_text(f'"""\\n{layer_name.title()} Layer\\n"""\\n')

# AFTER (VALIDATOR):
def validate_init_file(init_file_path: str, layer_name: str) -> ValidationResult:
    """Validates __init__.py exists with correct content"""
    init_file = Path(init_file_path)
    
    if not init_file.exists():
        return ValidationResult(status="FAIL", reason="__init__.py not found")
    
    content = init_file.read_text()
    expected_pattern = f'{layer_name.title()} Layer'
    
    if expected_pattern not in content:
        return ValidationResult(status="FAIL", reason="Missing layer documentation")
    
    return ValidationResult(status="PASS")
```

**Test Pattern:**
```python
def test_validator_does_not_write_files():
    """Validator must not write files using Path methods"""
    validator = TDDWorkflowEnforcer()
    
    result = validator.validate_init_file("/path/__init__.py", "business_logic")
    
    # Should NOT have written file
    assert not os.path.exists("/path/__init__.py")
    assert result.status == "FAIL"
```

---

### Type 4: Subprocess Execution (177 instances)

#### 4A: Test Execution (15-20 instances) - MUST REFACTOR
**Pattern:** `subprocess.run(['pytest', ...])`

**Refactoring Strategy:**
```python
# BEFORE (ACTOR):
result = subprocess.run(['pytest', test_file], capture_output=True)
if result.returncode == 0:
    return "PASS"

# AFTER (VALIDATOR):
def validate_test_results(test_results: TestExecutionResults) -> ValidationResult:
    """Receives test results from PROJECT-002, validates them"""
    if test_results.all_passed:
        return ValidationResult(status="PASS", tests_passed=test_results.passed_count)
    
    return ValidationResult(
        status="FAIL", 
        failed_tests=test_results.failures,
        reason=test_results.error_summary
    )
```

**Test Pattern:**
```python
def test_validator_receives_test_results_not_executes():
    """Validator must receive test results, not run tests"""
    validator = TDDWorkflowEnforcer()
    
    # Mock test results from PROJECT-002
    results = TestExecutionResults(
        all_passed=True,
        passed_count=5,
        failed_count=0
    )
    
    validation = validator.validate_test_results(results)
    
    # Should NOT have executed subprocess
    assert validation.status == "PASS"
    # Verify no pytest process was spawned (can check with mock/spy)
```

#### 4B: Git Read Operations (100+ instances) - KEEP AS-IS
**Pattern:** `subprocess.run(['git', 'status', ...])`

**Decision:** ✅ **KEEP** - These are validation operations (reading Git state)

```python
# OK TO KEEP:
result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True)
# This is READ-ONLY validation of Git state
```

#### 4C: Git Write Operations (40-50 instances) - MUST REFACTOR
**Pattern:** `subprocess.run(['git', 'commit', ...])`

**Refactoring Strategy:**
```python
# BEFORE (ACTOR):
subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True)

# AFTER (VALIDATOR):
def validate_git_checkpoint(commit_hash: str) -> ValidationResult:
    """Receives commit hash from PROJECT-002, validates checkpoint exists"""
    result = subprocess.run(
        ['git', 'cat-file', '-e', commit_hash],
        capture_output=True
    )
    
    if result.returncode == 0:
        return ValidationResult(status="PASS", commit_hash=commit_hash)
    
    return ValidationResult(status="FAIL", reason="Checkpoint not found")
```

**Test Pattern:**
```python
def test_validator_does_not_commit():
    """Validator must not create Git commits"""
    validator = TDDWorkflowEnforcer()
    
    # Get current commit
    current_commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True).stdout.strip()
    
    # Validator should validate existing commit, not create new one
    result = validator.validate_git_checkpoint(current_commit.decode())
    
    # Verify no new commit was created
    new_commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True).stdout.strip()
    assert current_commit == new_commit  # No new commit
```

---

### Type 5: File Object Writes (74 instances)
**Pattern:** `f.write(...)`

**Most Are Evidence Storage - Review Each:**
```python
# EVIDENCE (OK TO KEEP):
with open(evidence_file, 'w') as f:
    f.write(json.dumps(validation_results))

# ACTOR (MUST REFACTOR):
with open(test_file, 'w') as f:
    f.write(test_code)
```

**Quick Classification:**
- Writing `.json`, `.xml`, `.html`, `.md`, `.log` → ✅ LIKELY EVIDENCE (keep)
- Writing `.py` files → 🔴 ACTOR (refactor)
- Writing to paths containing `test/` or `src/` → 🔴 ACTOR (refactor)

---

## 📋 SYSTEMATIC EXECUTION PLAN

### Phase 1: High-Priority Actor Behaviors (3-4 days)

**Target:** 30-40 most critical behaviors

**Batch 1: Test File Generation (10 instances)**
Files:
- `legacy/utilities/tdd_workflow_engine.py` (lines 299, 533, 574, 596)
- `src/data_access/test_generation_data_access.py` (line 391)
- `src/business_logic/test_generation_verification_logic.py` (line 907)
- `legacy/utilities/tdd_workflow_enforcer.py` (lines 480, 504)

**Process:**
1. Day 1 Morning (4 hours):
   - Write RED tests for all 10 (tests that fail with current actor behavior)
   - Run tests → confirm all FAIL ✅
2. Day 1 Afternoon (4 hours):
   - Refactor first 5 behaviors to validator
   - Run tests → confirm these 5 PASS ✅
3. Day 2 Morning (4 hours):
   - Refactor remaining 5 behaviors to validator
   - Run tests → confirm all 10 PASS ✅
4. Day 2 Afternoon (2 hours):
   - REFACTOR phase: Improve code quality
   - **CHECKPOINT:** Run full test suite (66/66 + new 10)

**Batch 2: Test Directory Creation (8 instances)**
Files:
- `legacy/utilities/tdd_workflow_enforcer.py` (line 444)
- `legacy/utilities/tdd_workflow_engine.py` (line 199)
- `src/user_interface/tdd_workflow_interface.py` (lines 562, 569)

**Process:**
1. Day 3 Morning (3 hours):
   - Write RED tests for all 8
   - Refactor 4 behaviors
2. Day 3 Afternoon (3 hours):
   - Refactor remaining 4 behaviors
   - **CHECKPOINT:** Run full test suite

**Batch 3: Test Execution Subprocess (15 instances)**
Files:
- `legacy/utilities/tdd_workflow_enforcer.py` (lines 1062, 1135, 1400, 1540, 1696)
- `legacy/utilities/real_tdd_gates.py` (lines 46, 63, 112, 169, 186)
- `legacy/utilities/real_tdd_green_phase_engine.py` (lines 105, 130, 186, 206)

**Process:**
1. Day 4 (8 hours):
   - Write RED tests for all 15
   - Refactor all 15 to receive test results instead of executing
   - **CHECKPOINT:** Run full test suite

---

### Phase 2: Git Write Operations (2-3 days)

**Target:** 40-50 Git commit/tag/checkout operations

**Batch 4-6: Git Operations**
Files:
- `src/data_access/tdd_phase_repository.py` (25+ instances)
- `src/data_access/tdd_phase_repository_backup.py` (25+ instances)

**Process:**
1. Day 5-6 (16 hours):
   - Write RED tests for Git write operations
   - Refactor to validate checkpoints instead of creating them
   - Change signatures to receive commit_hash from PROJECT-002
   - **CHECKPOINT:** Run full test suite

2. Day 7 (8 hours):
   - REFACTOR phase for Git operations
   - Optimize validation logic
   - **CHECKPOINT:** Run full test suite

---

### Phase 3: Evidence File Operations - REVIEW ONLY (1-2 days)

**Target:** 150-200 file write operations for evidence

**Batch 7-10: Evidence Storage**
Files:
- `src/data_access/real_verification_evidence_storage.py`
- `src/data_access/real_test_result_storage.py`
- `src/data_access/real_test_metadata_persistence.py`
- All repository files

**Process:**
1. Day 8-9 (16 hours):
   - **REVIEW ONLY** - Don't refactor
   - Verify each is writing evidence files (`.json`, `.xml`, `.html`)
   - Verify NOT writing test/code files (`.py` in `test/` or `src/`)
   - Flag any accidental actor behaviors for refactoring
   - Document findings

**Expected Outcome:** Most are ✅ OK TO KEEP (evidence storage is validator behavior)

---

### Phase 4: Cleanup and Edge Cases (1 day)

**Target:** Remaining 20-30 edge cases

**Batch 11: Miscellaneous**
1. Day 10 (8 hours):
   - Handle any flagged behaviors from Phase 3
   - Refactor edge cases
   - Clean up any remaining actor behaviors
   - **FINAL CHECKPOINT:** Run full test suite

---

## ✅ STRATEGIC TESTING CHECKPOINTS

### After Each Batch:
```bash
# Run focused tests
pytest tests/ -v

# Verify specific refactored behavior
pytest tests/test_validator_behavior.py -v -k "test_no_file_creation"
```

### After Each Phase (4 major checkpoints):
```bash
# Full test suite
pytest tests/ -v --cov=src --cov-report=term-missing

# Verify no actor behaviors remain in refactored code
bash /tmp/comprehensive_actor_detection.sh | grep "REFACTORED_FILES"

# Existing tests still pass
pytest projects/PROJECT-003\ TDD\ ENFORCER/SYSTEM-003-02*/FEATURE-*/tests/ -v

# Current FEATURE-003-02-01 tests (66/66)
pytest projects/PROJECT-003\ TDD\ ENFORCER/SYSTEM-003-02*/FEATURE-003-02-01*/tests/ -v
```

### Final Validation (End of Day 10):
```bash
# 1. All new tests pass
pytest tests/test_validator_behavior.py -v

# 2. All existing tests still pass
pytest tests/ -v

# 3. FEATURE-003-02-01 tests still pass (66/66)
pytest projects/PROJECT-003\ TDD\ ENFORCER/SYSTEM-003-02*/FEATURE-003-02-01*/tests/ -v

# 4. Re-run detection to confirm zero actor behaviors in refactored code
bash /tmp/comprehensive_actor_detection.sh > FINAL_DETECTION_RESULTS.md

# 5. Verify count decreased from 461 to ~200 (kept evidence behaviors)
grep "TOTAL ACTOR BEHAVIORS" FINAL_DETECTION_RESULTS.md
```

---

## 📊 PROGRESS TRACKING

### Daily Progress Sheet:

```markdown
## Day 1: Test File Generation (Part 1)
- [ ] Write RED tests for 10 test file generation behaviors
- [ ] Refactor 5 behaviors to validator
- [ ] Tests: ___/10 passing
- Checkpoint: Full test suite ___/__ passing

## Day 2: Test File Generation (Part 2)
- [ ] Refactor remaining 5 behaviors
- [ ] REFACTOR phase: Code quality improvements
- [ ] Tests: 10/10 passing ✅
- Checkpoint: Full test suite ___/__ passing

## Day 3: Test Directory Creation
- [ ] Write RED tests for 8 directory creation behaviors
- [ ] Refactor all 8 behaviors
- [ ] Tests: 8/8 passing ✅
- Checkpoint: Full test suite ___/__ passing

## Day 4: Test Execution Subprocess
- [ ] Write RED tests for 15 test execution behaviors
- [ ] Refactor all 15 to receive results
- [ ] Tests: 15/15 passing ✅
- Checkpoint: Full test suite ___/__ passing

## Day 5-6: Git Write Operations
- [ ] Write RED tests for 40-50 Git operations
- [ ] Refactor all to validate instead of create
- [ ] Tests: __/__ passing
- Checkpoint: Full test suite ___/__ passing

## Day 7: Git Operations REFACTOR
- [ ] Code quality improvements
- [ ] Optimize validation logic
- Checkpoint: Full test suite ___/__ passing

## Day 8-9: Evidence Storage Review
- [ ] Review 150-200 evidence file operations
- [ ] Verify all are writing evidence (not test/code)
- [ ] Flag: ___ behaviors need refactoring
- [ ] Document findings

## Day 10: Cleanup and Final Validation
- [ ] Refactor flagged behaviors from Day 8-9
- [ ] Handle edge cases
- [ ] Final detection scan
- [ ] All tests passing: ___/___
- [ ] Actor behaviors remaining: ___ (target: ~200 evidence only)
```

---

## 🎯 SUCCESS CRITERIA

### At End of Day 10:

1. **All Critical Actor Behaviors Removed:**
   - ✅ Zero test file creation (`.py` in `test/`)
   - ✅ Zero code file creation (`.py` in `src/`)
   - ✅ Zero test execution (no `pytest` subprocess)
   - ✅ Zero directory creation for tests/code
   - ✅ Zero Git commits/tags/checkouts

2. **Evidence Storage Preserved:**
   - ✅ Evidence files still created (`.json`, `.xml`, `.html`, `.md`)
   - ✅ Validation reports still generated
   - ✅ Audit logs still maintained

3. **All Tests Passing:**
   - ✅ New validator tests: 40-50 tests passing
   - ✅ Existing tests: 66/66 FEATURE-003-02-01 tests
   - ✅ Full test suite: All passing

4. **Validator Interface Defined:**
   - ✅ `validate_test_files(file_paths: List[str])` method
   - ✅ `validate_test_results(results: TestExecutionResults)` method
   - ✅ `validate_git_checkpoint(commit_hash: str)` method
   - ✅ All methods receive data instead of creating it

5. **Detection Confirms Success:**
   - ✅ Re-run detection: ~200 behaviors remaining (all evidence storage)
   - ✅ Zero actor behaviors in refactored code
   - ✅ Clear separation: validator only

---

## 🚀 READY TO START?

### Tomorrow Morning (Day 1):

**Step 1: Create Test File (30 minutes)**
```bash
# Create new test file for validator behavior
touch tests/test_validator_no_actor_behavior.py
```

**Step 2: Write First RED Test (1 hour)**
```python
# tests/test_validator_no_actor_behavior.py

def test_stage_gate_3_does_not_create_test_files():
    """Stage Gate 3 must receive test file paths, not create files"""
    enforcer = TDDWorkflowEnforcer(project_root="/workspaces/control_tower")
    
    # Should receive test files from PROJECT-002
    test_files = ["/path/to/test_parser.py", "/path/to/test_generator.py"]
    
    result = enforcer.stage_gate_3_test_generation_verification(
        test_files=test_files  # Receive instead of generate
    )
    
    # Should NOT have created these files
    for test_file in test_files:
        assert not os.path.exists(test_file), f"Validator created file: {test_file}"
    
    # Should return validation failure (files don't exist)
    assert result.status == "FAIL"
    assert "not found" in result.reason.lower()
```

**Step 3: Run Test - Confirm RED (5 minutes)**
```bash
pytest tests/test_validator_no_actor_behavior.py::test_stage_gate_3_does_not_create_test_files -v
# Expected: FAIL (current code creates files)
```

**Step 4: Refactor to GREEN (2-3 hours)**
```python
# Refactor legacy/utilities/tdd_workflow_enforcer.py
# Change stage_gate_3 signature and implementation
```

**Step 5: Run Test - Confirm GREEN (5 minutes)**
```bash
pytest tests/test_validator_no_actor_behavior.py::test_stage_gate_3_does_not_create_test_files -v
# Expected: PASS (refactored code validates instead of creates)
```

**Step 6: Checkpoint (30 minutes)**
```bash
# Run full test suite to ensure nothing broke
pytest tests/ -v
pytest projects/PROJECT-003\ TDD\ ENFORCER/SYSTEM-003-02*/FEATURE-003-02-01*/tests/ -v
```

**Repeat for remaining 9 test file generation behaviors...**

---

## ⏱️ REALISTIC TIMELINE

### Total Time: 10 days (80 hours)

- **Day 1-2:** Test file generation (20 behaviors) - 16 hours
- **Day 3:** Test directory creation (8 behaviors) - 8 hours  
- **Day 4:** Test execution refactoring (15 behaviors) - 8 hours
- **Day 5-7:** Git write operations (40-50 behaviors) - 24 hours
- **Day 8-9:** Evidence storage review (200 behaviors) - 16 hours
- **Day 10:** Cleanup and validation (remaining + testing) - 8 hours

**Target Completion:** October 21, 2025 (2 weeks from now)

This aligns with the updated Phase 2 timeline: "10-12 days"

---

## 💡 KEY ADVANTAGES OF THIS APPROACH

1. ✅ **Simple**: Work through the list systematically
2. ✅ **Measurable**: Clear daily progress (behaviors refactored)
3. ✅ **Safe**: Test at every checkpoint
4. ✅ **TDD**: Write tests first, refactor to GREEN
5. ✅ **Focused**: One behavior at a time, batched logically
6. ✅ **Trackable**: Daily checklist shows exact progress
7. ✅ **Reversible**: Each commit is a checkpoint

---

**Let's start tomorrow with Batch 1: Test File Generation (10 behaviors)!**

Ready to begin? 🚀
