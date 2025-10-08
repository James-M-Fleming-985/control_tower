# Requirements Verification and Compliance Analysis Prompt

## OBJECTIVE
Execute comprehensive requirements verification using our automated validation tools to ensure **User Interface Layer** achieves minimum 80% implementation coverage with REAL requirement testing (not placeholder failures).

## MANDATORY EXECUTION ORDER

### Phase 1: Automated Requirements Validation

```bash
# Step 1.1: Validate complete User Interface Layer implementation (FEATURE-003-01-03)
python tools/validate_requirements.py --feature 003-01-03 --layer user_interface

# Step 1.2: Validate specific UI requirement components
python tools/validate_requirements.py --requirement FR-001  # Real-Time TDD Phase Display
python tools/validate_requirements.py --requirement FR-002  # TDD Enforcement Status Visualization
python tools/validate_requirements.py --requirement FR-003  # TDD Cycle Progress Tracking Display
python tools/validate_requirements.py --requirement FR-004  # Interactive User Command Interface

# Step 1.3: Parse UI requirements from source documents for cross-reference
python tools/exhaustive_requirements_parser.py LAYER-003-01-03-003_REQUIREMENTS_ANALYSIS.md
```

### Phase 2: Test Validation and Enhancement

```bash
# Step 2.1: Inspect ALL failing test files for UI requirement specificity
find tests/failing_tests/ -name "*ui*" -name "*.py" -exec grep -l "pytest.fail" {} \;

# Step 2.2: Identify generic placeholder tests that need rewriting
grep -r "pytest.fail.*not yet implemented" tests/failing_tests/

# Step 2.3: Verify tests contain actual UI requirement assertions
grep -r "assert.*<.*ms" tests/failing_tests/  # UI Response timing
grep -r "assert.*error_rate.*<" tests/failing_tests/  # UI Error rates  
grep -r "coverage.*%" tests/failing_tests/  # UI Coverage measurements
```

### Phase 3: Test Execution and Coverage Analysis

```bash
# Step 3.1: Run failing tests to confirm they fail for RIGHT REASONS
pytest tests/failing_tests/ -v --tb=short

# Step 3.2: Generate User Interface Layer coverage report
pytest --cov=src/user_interface tests/failing_tests/ --cov-report=term-missing --cov-report=html:htmlcov

# Step 3.3: Run comprehensive test suite for compatibility
pytest tests/ -v --tb=short -x
```

### Phase 4: Implementation Coverage Validation

```bash
# Step 4.1: Cross-reference requirements against UI implementation
python tools/validate_requirements.py --feature 003-01-03 --layer user_interface | grep "OVERALL VALIDATION SUMMARY" -A 15

# Step 4.2: Check individual UI requirement implementation status
python tools/validate_requirements.py --requirement FR-001
python tools/validate_requirements.py --requirement FR-002  
python tools/validate_requirements.py --requirement FR-003
python tools/validate_requirements.py --requirement FR-004

# Step 4.3: Identify gaps and missing UI implementations
python tools/validate_requirements.py --feature 003-01-03 --layer user_interface | grep "IMPLEMENTATION PRIORITIES" -A 10
```

## COMPLETION CRITERIA VALIDATION

Execute these verification commands to confirm completion:

### ✅ Requirements Implementation Coverage Verification
```bash
# Verify User Interface Layer achieves minimum 80% implementation coverage
python tools/validate_requirements.py --feature 003-01-03 --layer user_interface | grep "Actual (Validation):" | grep -o "[0-9.]*%"

# Expected: 80.0% or higher
# Current status should show: "✅ GRADE B ACHIEVED" or better
```

### ✅ Individual Requirements Status Verification  
```bash
# Verify all core UI requirements are implemented
echo "🔍 Checking individual requirement implementation status..."

for req in FR-001 FR-002 FR-003 FR-004; do
    echo "Checking $req..."
    python tools/validate_requirements.py --requirement $req | grep "status\|coverage"
done

# Expected: All requirements show IMPLEMENTED status with 80%+ coverage
```

### ✅ Test Coverage Verification
```bash
# Verify functional UI implementation with test coverage
pytest --cov=src/user_interface tests/failing_tests/ --cov-report=term | grep "TOTAL"

# Expected: TOTAL coverage >= 75%
```

### ✅ Test Compatibility Verification
```bash
# Verify 100% test compatibility maintained
pytest tests/ --tb=no -q | grep "passed"

# Expected: "20/20 tests passing" or equivalent with 0 failures
```

### ✅ UI Component Implementation Verification
```bash
# Verify UI components contain all required methods
python -c "
from src.user_interface.phase_display import TDDPhaseDisplay
from src.user_interface.enforcement_display import EnforcementStatusDisplay
from src.user_interface.progress_tracker import CycleProgressTracker
from src.user_interface.command_interface import InteractiveCommandInterface

components = {
    'TDDPhaseDisplay': TDDPhaseDisplay(),
    'EnforcementStatusDisplay': EnforcementStatusDisplay(),
    'CycleProgressTracker': CycleProgressTracker(),
    'InteractiveCommandInterface': InteractiveCommandInterface()
}

for name, component in components.items():
    methods = [m for m in dir(component) if not m.startswith('_')]
    print(f'{name}: {len(methods)} methods')
    
print('✅ All UI components loaded successfully')
"

# Expected: All components load without ImportError
```

## REWRITE REQUIREMENTS FOR GENERIC TESTS

For any tests containing generic `pytest.fail()`, rewrite with UI requirement-specific logic:

### Performance Requirements (PF-001, PF-002, PF-003)
Replace generic failures with:
```python
import time
import psutil
import pytest

def test_ui_performance_requirement_timing():
    """Test actual UI response time measurement"""
    from src.user_interface.phase_display import TDDPhaseDisplay
    
    display = TDDPhaseDisplay()
    start_time = time.perf_counter()
    
    # Execute actual UI operation
    result = display.display_current_phase("RED")
    
    end_time = time.perf_counter()
    response_time_ms = (end_time - start_time) * 1000
    
    # Assert actual requirement: < 100ms for UI
    assert response_time_ms < 100, f"UI response time {response_time_ms:.2f}ms exceeds 100ms requirement"
```

### Reliability Requirements (RL-001, RL-002)
Replace generic failures with:
```python
def test_ui_error_rate_requirement():
    """Test actual UI error rate measurement"""
    from src.user_interface.phase_display import TDDPhaseDisplay
    
    display = TDDPhaseDisplay()
    total_operations = 1000
    errors = 0
    
    for i in range(total_operations):
        try:
            display.display_current_phase("RED" if i % 3 == 0 else "GREEN" if i % 3 == 1 else "REFACTOR")
        except Exception:
            errors += 1
    
    error_rate = errors / total_operations
    # Assert actual requirement: < 0.01% error rate for UI
    assert error_rate < 0.0001, f"UI error rate {error_rate:.4f} exceeds 0.01% requirement"
```

### Test Coverage Requirements (TP-001, TP-002)
Replace generic failures with:
```python
import subprocess
import re

def test_ui_coverage_requirement():
    """Test actual UI coverage measurement"""
    # Run coverage measurement for UI layer
    result = subprocess.run([
        'pytest', '--cov=src/user_interface', 'tests/', '--cov-report=term'
    ], capture_output=True, text=True)
    
    # Parse coverage percentage
    coverage_match = re.search(r'TOTAL.*?(\d+)%', result.stdout)
    coverage_pct = int(coverage_match.group(1)) if coverage_match else 0
    
    # Assert actual requirement: 95% minimum coverage for UI
    assert coverage_pct >= 95, f"UI Coverage {coverage_pct}% below 95% requirement"
```

## BLOCKING VALIDATION RULES

### 🚫 STOP CONDITIONS - Do NOT proceed if:

1. **UI Requirements validation fails:**
   ```bash
   python tools/validate_requirements.py --feature 003-01-03 --layer user_interface | grep -q "ERROR\|MISSING"
   # If ERROR or significant MISSING found, FIX UI implementation before continuing
   ```

2. **Implementation coverage below 80%:**
   ```bash
   coverage=$(python tools/validate_requirements.py --feature 003-01-03 --layer user_interface | grep "Actual (Validation):" | grep -o "[0-9.]*" | head -1)
   if (( $(echo "$coverage < 80" | bc -l) )); then echo "BLOCKING: UI Coverage ${coverage}% below 80% minimum"; exit 1; fi
   ```

3. **Core UI components missing:**
   ```bash
   python tools/validate_requirements.py --requirement FR-001 | grep -q "MISSING\|ERROR"
   # If FR-001 (core phase display) missing, IMPLEMENT before continuing
   ```

4. **Test compatibility broken:**
   ```bash
   pytest tests/ --tb=no -q | grep -q "FAILED"
   # If any test failures, FIX compatibility issues before continuing
   ```

5. **Generic placeholder tests remain:**
   ```bash
   grep -r "pytest.fail.*not yet implemented" tests/failing_tests/ | wc -l
   # If count > 0, REWRITE with UI requirement-specific logic before continuing
   ```

## SUCCESS VALIDATION COMMANDS

Execute these commands to confirm successful completion:

```bash
# Final validation suite using our validate_requirements.py tool
echo "🔍 Validating Requirements Verification Completion..."

# Check 1: Overall feature implementation coverage
echo "📊 Running comprehensive feature validation..."
python tools/validate_requirements.py --feature 003-01-03

# Check 2: Individual requirement validation
echo "� Validating individual requirements..."
for req in FR-001 FR-002 FR-003 FR-004; do
    echo "  Checking $req..."
    python tools/validate_requirements.py --requirement $req
done

# Check 3: Test execution status
echo "🧪 Running test suite..."
failed_tests=$(pytest tests/failing_tests/ --tb=no -q | grep -o '\d\+ failed' | head -1 | grep -o '\d\+')
echo "Failing Tests: ${failed_tests:-0}"
[ "${failed_tests:-0}" -gt 0 ] && echo "✅ Tests failing for requirement reasons" || echo "❌ No failing tests found"

# Check 4: Test compatibility
echo "✅ Checking test compatibility..."
passing_tests=$(pytest tests/ --tb=no -q | grep -o '\d\+ passed' | head -1 | grep -o '\d\+')
echo "Passing Tests: ${passing_tests:-0}"
[ "${passing_tests:-0}" -ge 20 ] && echo "✅ Test compatibility maintained" || echo "❌ Test compatibility broken"

# Check 5: Implementation completeness
echo "🏗️ Checking method implementation completeness..."
python -c "
from src.data_access.tdd_phase_repository import TDDPhaseRepository
repo = TDDPhaseRepository('/tmp/test.db', '/tmp/test_repo')
required_methods = ['create_phase_state_record', 'get_phase_state', 'update_phase_state', 'list_phase_transitions', 'create_checkpoint', 'restore_checkpoint', 'list_checkpoints', 'store_test_evidence', 'get_test_evidence', 'validate_test_evidence', 'collect_evidence', 'validate_evidence']
missing = [m for m in required_methods if not hasattr(repo, m)]
completeness = ((len(required_methods) - len(missing)) / len(required_methods)) * 100
print(f'Method Implementation: {completeness:.1f}%')
print(f'Missing methods: {missing}')
"

echo "🎯 Requirements Verification Analysis Complete!"
```

## DELIVERABLES

Upon successful completion, generate these artifacts:

1. **Requirements Validation Report** - Output from `python tools/validate_requirements.py --feature 003-01-03`
2. **Individual Requirement Status** - Output from individual `--requirement` validations
3. **htmlcov/index.html** - Detailed coverage report from pytest coverage analysis
4. **Test Execution Results** - Output from `pytest tests/failing_tests/ -v`
5. **Implementation Completeness Report** - Method-by-method validation results
6. **Grade Assessment** - B-grade achievement confirmation with next action recommendations

## POST-VERIFICATION ACTIONS

After successful verification:

1. **Archive validation results:** Save all command outputs for audit trail
2. **Update implementation status:** Mark User Interface Layer as verified at 80%+ coverage
3. **Document gaps:** Record any remaining partial implementations for future enhancement
4. **Notify stakeholders:** Share validation report with UI implementation coverage metrics
5. **Prepare for next phase:** Begin Integration Phase Testing (Steps 13-15) preparation
6. **Schedule maintenance:** Plan incremental validation schedule for ongoing compliance

## TOOL USAGE REFERENCE

Our `validate_requirements.py` tool supports these key operations:

```bash
# Validate entire feature (recommended)
python tools/validate_requirements.py --feature 003-01-03

# Validate specific requirements individually  
python tools/validate_requirements.py --requirement FR-001  # Phase State Tracking
python tools/validate_requirements.py --requirement FR-002  # Git Checkpoint Creation
python tools/validate_requirements.py --requirement FR-003  # Test Execution Storage
python tools/validate_requirements.py --requirement FR-004  # Evidence Collection

# Cross-reference with source requirements documents
python tools/exhaustive_requirements_parser.py LAYER-003-01-03-003_REQUIREMENTS_ANALYSIS.md
```

The validator provides:
- ✅ **Implementation Status**: IMPLEMENTED/PARTIAL/MISSING for each UI requirement
- 📊 **Coverage Metrics**: Percentage completion with component-level details  
- 🎯 **Grade Assessment**: B-grade achievement status with recommendations
- 🔧 **Gap Analysis**: Specific missing methods and UI implementation priorities
- 📝 **Next Actions**: Clear guidance on what UI components to implement next

---

**⚠️ CRITICAL:** This verification process must achieve 80%+ implementation coverage using our `validate_requirements.py` tool before proceeding to Integration Layer. The tool will show "✅ GRADE B ACHIEVED" when minimum UI requirements are met.