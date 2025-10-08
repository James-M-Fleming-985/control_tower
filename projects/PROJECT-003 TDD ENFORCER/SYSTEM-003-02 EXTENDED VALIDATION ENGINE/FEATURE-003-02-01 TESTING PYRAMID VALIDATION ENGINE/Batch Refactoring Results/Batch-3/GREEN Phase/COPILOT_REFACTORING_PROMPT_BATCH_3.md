# GitHub Copilot Refactoring Request - Batch 3

**Batch:** Test Execution Subprocess Calls  
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
  result = subprocess.run(["pytest", test_file], capture_output=True)  # Runs tests

AFTER (VALIDATOR):
  def validate_test_execution(test_execution_result: TestExecutionResult) -> ValidationResult:
      if test_execution_result.tests_run == 0:
          return ValidationResult(status="FAIL", reason="No tests executed")
      if test_execution_result.tests_failed > 0:
          return ValidationResult(status="FAIL", reason="Tests failed")
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


### Behavior 1: legacy/utilities/tdd_workflow_enforcer.py:234

**File:** `legacy/utilities/tdd_workflow_enforcer.py`  
**Line:** 234  
**Current Code:** `subprocess.run(['pytest', test_path], capture_output=True)`  
**Target Code:** `validate_red_phase_execution(test_result: TestExecutionResult)`  
**Description:** Executes RED phase tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/tdd_workflow_enforcer.py`
2. Go to line 234
3. Find: `subprocess.run(['pytest', test_path], capture_output=True)`
4. Change to pattern: `validate_red_phase_execution(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 2: legacy/utilities/tdd_workflow_enforcer.py:567

**File:** `legacy/utilities/tdd_workflow_enforcer.py`  
**Line:** 567  
**Current Code:** `subprocess.run(['pytest', '-v', test_file])`  
**Target Code:** `validate_green_phase_execution(test_result: TestExecutionResult)`  
**Description:** Executes GREEN phase tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/tdd_workflow_enforcer.py`
2. Go to line 567
3. Find: `subprocess.run(['pytest', '-v', test_file])`
4. Change to pattern: `validate_green_phase_execution(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 3: legacy/utilities/real_tdd_gates.py:123

**File:** `legacy/utilities/real_tdd_gates.py`  
**Line:** 123  
**Current Code:** `subprocess.run(['pytest', '--tb=short'])`  
**Target Code:** `validate_stage_gate_results(test_result: TestExecutionResult)`  
**Description:** Executes stage gate tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/real_tdd_gates.py`
2. Go to line 123
3. Find: `subprocess.run(['pytest', '--tb=short'])`
4. Change to pattern: `validate_stage_gate_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 4: legacy/utilities/real_tdd_green_phase_engine.py:456

**File:** `legacy/utilities/real_tdd_green_phase_engine.py`  
**Line:** 456  
**Current Code:** `result = subprocess.run(['pytest', impl_test])`  
**Target Code:** `validate_implementation_test_results(test_result: TestExecutionResult)`  
**Description:** Executes implementation tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/real_tdd_green_phase_engine.py`
2. Go to line 456
3. Find: `result = subprocess.run(['pytest', impl_test])`
4. Change to pattern: `validate_implementation_test_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 5: legacy/utilities/tdd_workflow_engine.py:789

**File:** `legacy/utilities/tdd_workflow_engine.py`  
**Line:** 789  
**Current Code:** `subprocess.run(['pytest'] + test_files)`  
**Target Code:** `validate_test_results(test_result: TestExecutionResult)`  
**Description:** Executes multiple test files - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/tdd_workflow_engine.py`
2. Go to line 789
3. Find: `subprocess.run(['pytest'] + test_files)`
4. Change to pattern: `validate_test_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 6: src/business_logic/tdd_cycle_enforcer.py:234

**File:** `src/business_logic/tdd_cycle_enforcer.py`  
**Line:** 234  
**Current Code:** `subprocess.run(['python', '-m', 'pytest', test_dir])`  
**Target Code:** `validate_test_execution_results(test_result: TestExecutionResult)`  
**Description:** Executes test directory - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/business_logic/tdd_cycle_enforcer.py`
2. Go to line 234
3. Find: `subprocess.run(['python', '-m', 'pytest', test_dir])`
4. Change to pattern: `validate_test_execution_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 7: legacy/utilities/tdd_workflow_enforcer.py:890

**File:** `legacy/utilities/tdd_workflow_enforcer.py`  
**Line:** 890  
**Current Code:** `subprocess.run(pytest_cmd, shell=True)`  
**Target Code:** `validate_pytest_results(test_result: TestExecutionResult)`  
**Description:** Executes pytest command - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/tdd_workflow_enforcer.py`
2. Go to line 890
3. Find: `subprocess.run(pytest_cmd, shell=True)`
4. Change to pattern: `validate_pytest_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 8: legacy/utilities/real_tdd_gates.py:345

**File:** `legacy/utilities/real_tdd_gates.py`  
**Line:** 345  
**Current Code:** `os.system('pytest tests/unit')`  
**Target Code:** `validate_unit_test_results(test_result: TestExecutionResult)`  
**Description:** Executes unit tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/real_tdd_gates.py`
2. Go to line 345
3. Find: `os.system('pytest tests/unit')`
4. Change to pattern: `validate_unit_test_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 9: legacy/utilities/real_tdd_gates.py:456

**File:** `legacy/utilities/real_tdd_gates.py`  
**Line:** 456  
**Current Code:** `os.system('pytest tests/integration')`  
**Target Code:** `validate_integration_test_results(test_result: TestExecutionResult)`  
**Description:** Executes integration tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/real_tdd_gates.py`
2. Go to line 456
3. Find: `os.system('pytest tests/integration')`
4. Change to pattern: `validate_integration_test_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 10: legacy/utilities/real_tdd_green_phase_engine.py:678

**File:** `legacy/utilities/real_tdd_green_phase_engine.py`  
**Line:** 678  
**Current Code:** `subprocess.run(['pytest', '--cov'])`  
**Target Code:** `validate_coverage_results(test_result: TestExecutionResult)`  
**Description:** Executes coverage tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/real_tdd_green_phase_engine.py`
2. Go to line 678
3. Find: `subprocess.run(['pytest', '--cov'])`
4. Change to pattern: `validate_coverage_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 11: src/business_logic/test_generation_verification_logic.py:456

**File:** `src/business_logic/test_generation_verification_logic.py`  
**Line:** 456  
**Current Code:** `subprocess.run(['pytest', generated_test])`  
**Target Code:** `validate_generated_test_results(test_result: TestExecutionResult)`  
**Description:** Executes generated tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/business_logic/test_generation_verification_logic.py`
2. Go to line 456
3. Find: `subprocess.run(['pytest', generated_test])`
4. Change to pattern: `validate_generated_test_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 12: legacy/utilities/tdd_workflow_enforcer.py:1234

**File:** `legacy/utilities/tdd_workflow_enforcer.py`  
**Line:** 1234  
**Current Code:** `subprocess.Popen(['pytest', '-x', test_suite])`  
**Target Code:** `validate_test_suite_results(test_result: TestExecutionResult)`  
**Description:** Executes test suite - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/tdd_workflow_enforcer.py`
2. Go to line 1234
3. Find: `subprocess.Popen(['pytest', '-x', test_suite])`
4. Change to pattern: `validate_test_suite_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 13: legacy/utilities/real_tdd_gates.py:567

**File:** `legacy/utilities/real_tdd_gates.py`  
**Line:** 567  
**Current Code:** `subprocess.run(['pytest', '--cov-report=term'])`  
**Target Code:** `validate_coverage_report(test_result: TestExecutionResult)`  
**Description:** Generates coverage report - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/real_tdd_gates.py`
2. Go to line 567
3. Find: `subprocess.run(['pytest', '--cov-report=term'])`
4. Change to pattern: `validate_coverage_report(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 14: legacy/utilities/tdd_workflow_engine.py:456

**File:** `legacy/utilities/tdd_workflow_engine.py`  
**Line:** 456  
**Current Code:** `subprocess.run(['pytest', '--tb=long', workspace])`  
**Target Code:** `validate_refactor_test_results(test_result: TestExecutionResult)`  
**Description:** Executes REFACTOR phase tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `legacy/utilities/tdd_workflow_engine.py`
2. Go to line 456
3. Find: `subprocess.run(['pytest', '--tb=long', workspace])`
4. Change to pattern: `validate_refactor_test_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


### Behavior 15: src/business_logic/tdd_cycle_enforcer.py:789

**File:** `src/business_logic/tdd_cycle_enforcer.py`  
**Line:** 789  
**Current Code:** `subprocess.run(['pytest', '-m', 'checkpoint'])`  
**Target Code:** `validate_checkpoint_test_results(test_result: TestExecutionResult)`  
**Description:** Executes checkpoint tests - should validate results instead  

**REFACTOR THIS FILE NOW:**
1. Open `src/business_logic/tdd_cycle_enforcer.py`
2. Go to line 789
3. Find: `subprocess.run(['pytest', '-m', 'checkpoint'])`
4. Change to pattern: `validate_checkpoint_test_results(test_result: TestExecutionResult)`
5. Update method signature to accept `file_path: str` parameter
6. Return `ValidationResult` object
7. Remove all file creation/writing code


---

## ✅ ACCEPTANCE CRITERIA

After refactoring all 15 behaviors:

1. **No file creation code remains** - no `.write_text()`, `.mkdir()`, `open(..., 'w')`
2. **Methods accept file paths** - all refactored methods take `file_path: str` parameter
3. **Methods return ValidationResult** - all return structured validation results
4. **Tests pass** - run `pytest tests/test_batch_3_refactoring.py -v`
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
   - Run: `pytest tests/test_batch_3_refactoring.py -v`
   - Run: Full test suite
   - Report results

---

## 📁 FILES TO MODIFY

- `legacy/utilities/tdd_workflow_enforcer.py` (line 234)
- `legacy/utilities/tdd_workflow_enforcer.py` (line 567)
- `legacy/utilities/real_tdd_gates.py` (line 123)
- `legacy/utilities/real_tdd_green_phase_engine.py` (line 456)
- `legacy/utilities/tdd_workflow_engine.py` (line 789)
- `src/business_logic/tdd_cycle_enforcer.py` (line 234)
- `legacy/utilities/tdd_workflow_enforcer.py` (line 890)
- `legacy/utilities/real_tdd_gates.py` (line 345)
- `legacy/utilities/real_tdd_gates.py` (line 456)
- `legacy/utilities/real_tdd_green_phase_engine.py` (line 678)
- `src/business_logic/test_generation_verification_logic.py` (line 456)
- `legacy/utilities/tdd_workflow_enforcer.py` (line 1234)
- `legacy/utilities/real_tdd_gates.py` (line 567)
- `legacy/utilities/tdd_workflow_engine.py` (line 456)
- `src/business_logic/tdd_cycle_enforcer.py` (line 789)

---

## 🔍 VERIFICATION

After completing the refactoring, please:

1. List all files you modified
2. Show the before/after code for each behavior
3. Run the test suite and share results  
4. Confirm zero file creation code remains in refactored methods

---

**READY TO REFACTOR? Please proceed with Batch 3.**
