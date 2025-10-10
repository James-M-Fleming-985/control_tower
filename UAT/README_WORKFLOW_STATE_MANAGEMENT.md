# 🧪 UAT: Build Real Production Feature
## Testing AI Code Generator on Workflow State Management

**Date:** 2025-10-10  
**Feature:** LAYER-003-03-01-01 Workflow State Management  
**Project:** PROJECT-003 TDD ENFORCER  

---

## 🎯 What We're Building

The AI Code Generator will build a **REAL production feature** - the Workflow State Management layer from the TDD Enforcer system. This is not a toy example, but actual production code that will be used to track the 10-stage TDD workflow.

### Feature Overview: Workflow State Management

**Purpose:** Manages workflow execution state, stage tracking, and persistence for the TDD Enforcer's 10-stage orchestration system.

**Real-World Usage:**
- Tracks which TDD stages have completed (1-10)
- Maintains current execution state
- Provides recovery through state persistence
- Validates workflow progressions
- Enables resumption after failures

**Key Components:**
1. **`WorkflowStateManager`** class - Core state management
2. **State Tracking** - Current stage, completion status, failures
3. **Persistence** - Save/load workflow state to JSON
4. **Validation** - Prevent invalid stage transitions

---

## 📋 The Challenge: 4 Acceptance Criteria

### AC-001: Initialize workflow state with all stages
- Initialize with 10 TDD stages
- Track status (pending, in_progress, completed, failed)
- Validate workflow ID and stages list

### AC-002: Track current stage and completion status
- Get current stage
- Advance to next stage
- Mark stages completed/failed
- Get workflow status summary

### AC-003: Persist state for recovery capability
- Save state to JSON file
- Load state from JSON file
- Handle corrupted files gracefully
- Enable workflow recovery

### AC-004: Validate state transitions
- Prevent skipping stages
- Ensure sequential progression
- Detect workflow completion
- Validate transitions

---

## 🚀 Quick Start - Run UAT

### Step 1: Set Your API Key
```bash
# Use OpenAI (GPT-4)
export OPENAI_API_KEY="your-openai-api-key"

# OR use Anthropic (Claude)
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Step 2: Run the UAT
```bash
cd /workspaces/control_tower/UAT

# Default (uses Workflow State Management spec)
python run_uat.py --verbose

# Or explicitly specify the spec file
python run_uat.py --spec LAYER-UAT-002_workflow_state_management.yaml --verbose

# Use Anthropic instead of OpenAI
python run_uat.py --provider anthropic --verbose
```

### Step 3: Watch the AI Build Real Code!

The UAT will:
1. ✅ Parse the YAML requirements (4 acceptance criteria)
2. ✅ Generate comprehensive unit & integration tests via AI
3. ✅ Generate the WorkflowStateManager implementation via AI
4. ✅ Execute complete TDD cycle (RED → GREEN → REFACTOR)
5. ✅ Run all tests and verify they pass
6. ✅ Generate verification reports (test pyramid, requirements verification, quality gates)
7. ✅ Provide UAT report with PASS/FAIL

---

## ✅ Expected Output Structure

```
UAT/output/
├── src/
│   └── orchestration/
│       └── state/
│           ├── __init__.py
│           └── workflow_state_manager.py    ← AI-generated implementation
│
├── tests/
│   └── layer/
│       └── workflow_state/
│           ├── test_workflow_state_manager_unit.py        ← AI-generated unit tests
│           └── test_workflow_state_manager_integration.py ← AI-generated integration tests
│
├── Requirements Verification/
│   ├── requirements_verification_complete.yaml  ← Complete AC verification
│   ├── test_pyramid_report.yaml                ← Test distribution & ratios
│   ├── quality_gates_report.yaml               ← RED/GREEN/REFACTOR validation
│   └── execution_evidence.json                 ← Audit trail
│
└── Testing Outputs/
    ├── red_phase_log_*.txt      ← Tests failed before implementation
    ├── green_phase_log_*.txt    ← Tests passed after implementation
    └── refactor_phase_log_*.txt ← Tests still pass after refactoring
```

---

## 🎯 Success Criteria

### Critical Requirements
- ✅ All 4 acceptance criteria implemented
- ✅ `WorkflowStateManager` class created
- ✅ All methods implemented with type hints
- ✅ All unit tests pass (100%)
- ✅ All integration tests pass (100%)
- ✅ Test pyramid ratio ≥ 2:1
- ✅ Test coverage ≥ 90%
- ✅ All quality gates PASSED

### Quality Requirements
- ✅ Type hints on all public methods
- ✅ Docstrings on all public methods
- ✅ No PEP 8 violations
- ✅ Comprehensive error handling
- ✅ Clear error messages

### Excellence Requirements
- ✅ Edge cases thoroughly tested
- ✅ State recovery robustly tested
- ✅ Validation logic comprehensive
- ✅ Performance requirements met

---

## 🔍 What the AI Must Generate

### 1. Implementation: `workflow_state_manager.py`

**Class:** `WorkflowStateManager`

**Methods:**
```python
__init__(workflow_id: str, stages: List[str])
get_current_stage() -> str
advance_to_next_stage() -> bool
mark_stage_completed(stage_name: str) -> None
mark_stage_failed(stage_name: str, error: str) -> None
get_workflow_status() -> Dict[str, Any]
save_state(file_path: str) -> None
load_state(file_path: str) -> WorkflowStateManager  # classmethod
can_advance() -> bool
validate_transition(from_stage: str, to_stage: str) -> bool
is_workflow_complete() -> bool
```

**Features:**
- Track 10 TDD stages
- State persistence (JSON)
- Validation logic
- Error handling
- Type hints
- Docstrings

### 2. Tests: Comprehensive Coverage

**Unit Tests (~12 tests):**
- Initialization with valid/invalid inputs
- Stage tracking and advancement
- Completion/failure marking
- Status queries
- Validation logic
- Edge cases

**Integration Tests (~6 tests):**
- State persistence (save/load)
- State recovery scenarios
- Corrupted file handling
- End-to-end workflows

---

## 📊 Verification Reports

The AI must generate 4 verification reports:

### 1. Test Pyramid Report
- Unit test count: ~12
- Integration test count: ~6
- Ratio: 2:1 (meets requirement)
- Coverage: ≥90%

### 2. Requirements Verification
- AC-001: VERIFIED ✅
- AC-002: VERIFIED ✅
- AC-003: VERIFIED ✅
- AC-004: VERIFIED ✅
- Complete evidence chains
- Full traceability matrix

### 3. Quality Gates Report
- RED phase: PASSED ✅ (tests failed before implementation)
- GREEN phase: PASSED ✅ (tests passed after implementation)
- REFACTOR phase: PASSED ✅ (tests still pass after refactoring)

### 4. Execution Evidence
- Timestamps
- Test results
- Coverage data
- Traceability links

---

## 🧪 Manual Testing After UAT

After the automated UAT completes, you can manually test the generated code:

### Test the Implementation
```python
cd output
python

>>> from src.orchestration.state.workflow_state_manager import WorkflowStateManager

# Test initialization
>>> stages = [
...     "stage_gate_1_requirement_parsing",
...     "stage_gate_2_test_specification",
...     "stage_gate_3_test_generation",
...     "stage_gate_4_test_validation",
...     "stage_gate_5_red_phase",
...     "stage_gate_6_implementation",
...     "stage_gate_7_green_phase",
...     "stage_gate_8_refactoring",
...     "stage_gate_9_documentation",
...     "stage_gate_10_verification"
... ]
>>> manager = WorkflowStateManager("wf-001", stages)

# Test tracking
>>> manager.get_current_stage()
'stage_gate_1_requirement_parsing'

>>> manager.mark_stage_completed('stage_gate_1_requirement_parsing')
>>> manager.advance_to_next_stage()
True

>>> manager.get_current_stage()
'stage_gate_2_test_specification'

# Test status
>>> status = manager.get_workflow_status()
>>> status['completed_count']
1
>>> status['current_stage']
'stage_gate_2_test_specification'

# Test persistence
>>> manager.save_state('/tmp/test_state.json')
>>> restored = WorkflowStateManager.load_state('/tmp/test_state.json')
>>> restored.get_workflow_status() == manager.get_workflow_status()
True
```

---

## 🎉 Why This is Significant

This UAT demonstrates the AI Code Generator can:

1. **Parse Complex Requirements** - 4 ACs with multiple methods, edge cases, error conditions
2. **Generate Production Code** - Not a toy example, but real TDD Enforcer infrastructure
3. **Follow TDD Strictly** - Generate tests first, then implementation, then refactor
4. **Create Comprehensive Tests** - Unit + integration, edge cases, error conditions
5. **Validate Quality** - Test pyramid, coverage, quality gates, verification reports
6. **Handle Complexity** - State management, persistence, validation logic
7. **Produce Maintainable Code** - Type hints, docstrings, PEP 8, error handling

**This proves the system works end-to-end on real production features!**

---

## 🐛 Troubleshooting

### Issue: "API Key not set"
```bash
export OPENAI_API_KEY="sk-..."
echo $OPENAI_API_KEY  # Verify it's set
```

### Issue: "Module not found"
```bash
pip install openai anthropic pytest pytest-cov pyyaml pytest-json-report
```

### Issue: "Tests failed"
- Review generated implementation in `output/src/`
- Check test logs in `output/Testing Outputs/`
- Verify AI understood requirements correctly
- Try running again (AI may produce different results)

### Issue: "Wrong feature being built"
The default is now Workflow State Management. To use a different spec:
```bash
python run_uat.py --spec LAYER-UAT-001_string_utilities.yaml
```

---

## 📞 Available UAT Specifications

1. **`LAYER-UAT-001_string_utilities.yaml`** - Simple string manipulation (demo)
2. **`LAYER-UAT-002_workflow_state_management.yaml`** - Real TDD Enforcer feature (default)

---

## 🚀 Next Steps After UAT Passes

1. **Review Generated Code** - Ensure it meets your quality standards
2. **Integrate into Project** - Move generated code to actual project structure
3. **Build More Features** - Use AI Generator for other layers/features
4. **Customize Specifications** - Create your own YAML requirement files
5. **Production Deployment** - The code is production-ready if UAT passes!

---

**Ready to build real production code with AI?** 🚀

```bash
cd /workspaces/control_tower/UAT
export OPENAI_API_KEY="your-key"
python run_uat.py --verbose
```

Watch the AI Code Generator build the Workflow State Management layer from scratch!

---

**Generated:** 2025-10-10  
**Status:** ✅ READY TO RUN  
**Feature:** Real Production Code (TDD Enforcer)
