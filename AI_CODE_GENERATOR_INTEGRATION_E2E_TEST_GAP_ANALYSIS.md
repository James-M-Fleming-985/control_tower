# AI Code Generator - Integration & E2E Test Gap Analysis

**Date**: October 12, 2025  
**Issue**: AI Code Generator not creating explicit integration and E2E tests from YAML scenarios  
**Severity**: **CRITICAL** - This is a core requirement for the AI Code Generator

---

## Executive Summary

The AI Code Generator is **NOT** reading or processing the `integration_test_scenarios` and `e2e_test_scenarios` sections from feature YAML files. It only processes `acceptance_criteria`, which results in minimal test coverage that doesn't match the explicit test scenarios defined in the requirements.

---

## Root Cause Analysis

### 1. **YAML Loading - Partial Implementation**

**File**: `ai_code_generator_orchestrator.py` - Line 103  
**Method**: `load_yaml_requirements()`

```python
def load_yaml_requirements(self, yaml_path: Path) -> Dict[str, Any]:
    """Load requirements from YAML specification file."""
    with open(yaml_path, 'r') as f:
        requirements = yaml.safe_load(f)
    
    if 'acceptance_criteria' not in requirements:
        requirements['acceptance_criteria'] = []
    
    return requirements  # ⚠️ Returns full dict but doesn't validate scenario sections
```

**Issue**: While the method loads the entire YAML, it only validates `acceptance_criteria` exists. It doesn't check for or validate `integration_test_scenarios` or `e2e_test_scenarios`.

---

### 2. **Test Generation Prompt - Missing Scenarios**

**File**: `ai_code_generator_orchestrator.py` - Line 626  
**Method**: `_build_test_generation_prompt()`

```python
def _build_test_generation_prompt(
    self,
    requirements: Dict[str, Any],
    acceptance_criteria: List[Dict[str, Any]]  # ⚠️ Only accepts AC list
) -> str:
    """Build prompt for AI to generate test code."""
    prompt = f"""Generate pytest test code for the following requirements:

Layer: {requirements.get('layer_id', 'UNKNOWN')}
Feature: {requirements.get('feature_name', 'UNKNOWN')}

Acceptance Criteria:
"""
    for i, ac in enumerate(acceptance_criteria, 1):
        criterion = ac.get('criterion', ac.get('description', 'No description'))
        prompt += f"\n{i}. {criterion}"
    
    prompt += """

Generate a complete Python test file with:
- Import statements (pytest, unittest.mock, etc.)
- Test class for each acceptance criterion  # ⚠️ Only AC classes
- At least 2 test methods per criterion
- Tests should initially FAIL (RED phase requirement)
...
"""
    return prompt
```

**Issue**: The prompt builder:
1. Only accepts `acceptance_criteria` as a parameter
2. Only includes AC in the prompt to the AI
3. Has NO mention of integration or E2E test scenarios
4. Does NOT read `integration_test_scenarios` or `e2e_test_scenarios` from requirements dict

---

### 3. **RED Phase Execution - Limited Scope**

**File**: `ai_code_generator_orchestrator.py` - Line 133  
**Method**: `execute_red_phase()`

```python
def execute_red_phase(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Execute RED phase: Generate tests that should fail."""
    self.current_phase = 'RED'
    
    # Build prompt for test generation
    ac_list = requirements.get('acceptance_criteria', [])  # ⚠️ Only gets AC
    prompt = self._build_test_generation_prompt(requirements, ac_list)
    
    # Call AI provider to generate test code
    test_code = self.ai_provider.generate_code(prompt)
    ...
```

**Issue**: RED phase only extracts `acceptance_criteria` from requirements and passes it to the prompt builder. Integration and E2E scenarios are completely ignored.

---

## Impact Assessment

### Current Behavior

For `FEATURE-003-03-02_prerequisites_validation.yaml`:

**YAML Contains**:
- 5 Acceptance Criteria (unit test level)
- 4 Integration Test Scenarios (explicitly defined with test classes)
- 4 E2E Test Scenarios (explicitly defined with test classes)

**AI Generator Produces**:
- ✅ 5 Unit tests (from AC)
- ❌ 1 Generic integration test (not from scenarios)
- ❌ 0 E2E tests (scenarios completely ignored)

**Test Pyramid Report Shows**:
```yaml
actual_ratio: '83:16:0'  # Unit:Integration:E2E
# Should be closer to: '50:33:16' based on YAML scenarios
```

### Expected Behavior

The AI Code Generator should:
1. Read `integration_test_scenarios` from YAML
2. Generate a test class for EACH scenario (4 classes)
3. Generate test methods for EACH test in the scenario
4. Read `e2e_test_scenarios` from YAML  
5. Generate a test class for EACH E2E scenario (4 classes)
6. Generate test methods for EACH test in the scenario

**Expected Output**:
- 5 Unit test classes (from AC)
- 4 Integration test classes (from scenarios)
- 4 E2E test classes (from scenarios)
- Total: 13 test classes with proper categorization

---

## Fix Requirements

### Phase 1: Update YAML Loader (LOW RISK)

**File**: `ai_code_generator_orchestrator.py`  
**Method**: `load_yaml_requirements()`

```python
def load_yaml_requirements(self, yaml_path: Path) -> Dict[str, Any]:
    """Load requirements from YAML specification file."""
    with open(yaml_path, 'r') as f:
        requirements = yaml.safe_load(f)
    
    # Validate and initialize all test sections
    if 'acceptance_criteria' not in requirements:
        requirements['acceptance_criteria'] = []
    
    # NEW: Validate scenario sections
    if 'integration_test_scenarios' not in requirements:
        requirements['integration_test_scenarios'] = []
    
    if 'e2e_test_scenarios' not in requirements:
        requirements['e2e_test_scenarios'] = []
    
    return requirements
```

---

### Phase 2: Update Prompt Builder (MEDIUM RISK)

**File**: `ai_code_generator_orchestrator.py`  
**Method**: `_build_test_generation_prompt()`

```python
def _build_test_generation_prompt(
    self,
    requirements: Dict[str, Any],
    acceptance_criteria: List[Dict[str, Any]],
    integration_scenarios: List[Dict[str, Any]] = None,  # NEW
    e2e_scenarios: List[Dict[str, Any]] = None  # NEW
) -> str:
    """Build prompt for AI to generate test code."""
    
    integration_scenarios = integration_scenarios or []
    e2e_scenarios = e2e_scenarios or []
    
    prompt = f"""Generate pytest test code for the following requirements:

Layer: {requirements.get('layer_id', 'UNKNOWN')}
Feature: {requirements.get('feature_name', 'UNKNOWN')}

Acceptance Criteria (UNIT TESTS):
"""
    for i, ac in enumerate(acceptance_criteria, 1):
        criterion = ac.get('criterion', ac.get('description', 'No description'))
        prompt += f"\n{i}. {criterion}"
    
    # NEW: Add integration test scenarios
    if integration_scenarios:
        prompt += "\n\nINTEGRATION TEST SCENARIOS:\n"
        for i, scenario in enumerate(integration_scenarios, 1):
            prompt += f"\n{i}. Scenario: {scenario.get('scenario', 'UNKNOWN')}"
            prompt += f"\n   Description: {scenario.get('description', '')}"
            prompt += f"\n   Test Class: {scenario.get('test_class', 'TestIntegration')}"
            prompt += f"\n   Tests to implement:"
            for test in scenario.get('tests', []):
                prompt += f"\n      - {test}"
            if 'layers_integrated' in scenario:
                prompt += f"\n   Layers Integrated: {', '.join(scenario['layers_integrated'])}"
    
    # NEW: Add E2E test scenarios
    if e2e_scenarios:
        prompt += "\n\nEND-TO-END TEST SCENARIOS:\n"
        for i, scenario in enumerate(e2e_scenarios, 1):
            prompt += f"\n{i}. Scenario: {scenario.get('scenario', 'UNKNOWN')}"
            prompt += f"\n   Description: {scenario.get('description', '')}"
            prompt += f"\n   Test Class: {scenario.get('test_class', 'TestE2E')}"
            prompt += f"\n   Tests to implement:"
            for test in scenario.get('tests', []):
                prompt += f"\n      - {test}"
    
    prompt += """

Generate a complete Python test file with:
- Import statements (pytest, unittest.mock, etc.)
- Test class for EACH acceptance criterion (UNIT tests)
- Test class for EACH integration test scenario (INTEGRATION tests)
- Test class for EACH E2E test scenario (E2E tests)
- Each test class MUST have the exact name specified in the YAML
- Each test MUST be implemented as specified in the scenario
- Tests should initially FAIL (RED phase requirement)
- Use pytest.raises() for expected failures
- Include docstrings
- Mark integration tests with @pytest.mark.integration
- Mark E2E tests with @pytest.mark.e2e

CRITICAL: You MUST create ALL test classes and test methods specified above.
Do not skip any scenarios. Each scenario becomes its own test class.

Output only valid Python code, no explanations.
"""
    return prompt
```

---

### Phase 3: Update RED Phase Caller (LOW RISK)

**File**: `ai_code_generator_orchestrator.py`  
**Method**: `execute_red_phase()`

```python
def execute_red_phase(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Execute RED phase: Generate tests that should fail."""
    self.current_phase = 'RED'
    
    # Extract ALL test definitions from requirements
    ac_list = requirements.get('acceptance_criteria', [])
    integration_scenarios = requirements.get('integration_test_scenarios', [])  # NEW
    e2e_scenarios = requirements.get('e2e_test_scenarios', [])  # NEW
    
    # Build comprehensive prompt
    prompt = self._build_test_generation_prompt(
        requirements, 
        ac_list,
        integration_scenarios,  # NEW
        e2e_scenarios  # NEW
    )
    
    # Call AI provider to generate test code
    test_code = self.ai_provider.generate_code(prompt)
    ...
```

---

### Phase 4: Update Test Categorization (MEDIUM RISK)

The test pyramid report builder needs to detect test classes by their names:

**File**: `ai_code_generator_orchestrator.py`  
**Method**: `_categorize_test_class()` (around line 820)

Current logic already checks for patterns, but we need to ensure it matches our YAML test_class names:

```python
# Current patterns (should already work):
if any(pattern in class_name_lower for pattern in ['integration', 'integ']):
    return 'integration'
elif any(pattern in class_name_lower for pattern in ['e2e', 'endtoend', 'end2end', 'e2etest']):
    return 'e2e'
```

This should work IF the test classes are actually generated with names like:
- `TestIntegrationPrerequisitesChain`
- `TestE2ECompletePrerequisitesCheck`

---

## Testing Plan

### 1. Unit Test the Fix

Create unit tests for the new prompt builder:

```python
def test_prompt_includes_integration_scenarios():
    """Test that integration scenarios are included in prompt."""
    requirements = {
        'layer_id': 'TEST-001',
        'integration_test_scenarios': [
            {
                'scenario': 'INT-001',
                'description': 'Test integration',
                'test_class': 'TestMyIntegration',
                'tests': ['Test something', 'Test another thing']
            }
        ]
    }
    
    prompt = orchestrator._build_test_generation_prompt(
        requirements, 
        [],
        requirements['integration_test_scenarios'],
        []
    )
    
    assert 'INTEGRATION TEST SCENARIOS' in prompt
    assert 'TestMyIntegration' in prompt
    assert 'Test something' in prompt
```

### 2. Integration Test with Real YAML

Use FEATURE-003-03-02 YAML to validate:

```bash
python run_layer_generation.py \
  "projects/PROJECT-003.../FEATURE-003-03-02_prerequisites_validation.yaml"
```

Expected test file should contain:
- 5 unit test classes (from AC)
- 4 integration test classes (TestCompletePrerequisitesChain, etc.)
- 4 E2E test classes (TestE2ECompletePrerequisitesCheck, etc.)

### 3. Validate Test Pyramid Report

After regeneration, check pyramid report:

```yaml
expected_ratio: '38:31:30'  # 5 unit : 4 integration : 4 E2E
# Or similar distribution based on actual test counts
```

---

## Implementation Priority

1. **IMMEDIATE** (Today):
   - Phase 1: Update YAML loader validation
   - Phase 2: Update prompt builder to include scenarios
   - Phase 3: Update RED phase caller

2. **VALIDATION** (Today):
   - Re-run FEATURE-003-03-02 generation
   - Verify test pyramid report
   - Validate all scenario test classes are created

3. **ROLLOUT** (Next):
   - Apply same pattern to FEATURE-003-03-03, 04, 05
   - Update AI Code Generator documentation
   - Add acceptance criteria validation for this fix

---

## Success Criteria

✅ YAML loader validates all test scenario sections  
✅ Prompt builder includes integration scenarios in prompt  
✅ Prompt builder includes E2E scenarios in prompt  
✅ RED phase passes all scenarios to prompt builder  
✅ Generated test file contains ALL scenario test classes  
✅ Test pyramid report shows proper distribution  
✅ All 13 test classes generated (5 unit + 4 integration + 4 E2E)  

---

## Risk Assessment

**Risk Level**: MEDIUM

**Risks**:
1. AI might not follow complex prompts correctly
2. Generated test class names might not match YAML exactly
3. Prompt might become too long for token limits

**Mitigation**:
1. Use clear, structured prompt format
2. Explicitly specify test class names in prompt
3. Test with small YAML first, then scale up
4. Consider splitting into separate prompts if needed

---

## Next Steps

1. Implement the fix in `ai_code_generator_orchestrator.py`
2. Run unit tests to verify prompt builder changes
3. Re-run FEATURE-003-03-02 generation
4. Review generated test file and pyramid report
5. If successful, apply to remaining features
6. Update AI Code Generator requirements to include this validation

---

**Prepared by**: GitHub Copilot  
**Review Status**: Pending Implementation  
**Estimated Fix Time**: 2-3 hours
