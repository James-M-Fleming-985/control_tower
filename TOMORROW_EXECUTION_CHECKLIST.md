# Tomorrow's Execution Checklist - October 16, 2025

**Goal**: Fix YAML architecture violations + Implement multi-phase generation for 100% compliance

**Estimated Time**: 3.5 hours

---

## ✅ Pre-Flight Checklist

- [ ] Review `/workspaces/control_tower/YAML_COMPLIANCE_AUDIT.md` (current state: 60% compliant)
- [ ] Review `/workspaces/control_tower/YAML_REFACTOR_AND_MULTI_PHASE_IMPLEMENTATION_PLAN.md` (full plan)
- [ ] Backup current YAML files
- [ ] Backup current `build_system.py`

---

## 📋 Part 1: YAML Refactor (45 minutes)

### Task 1.1: Fix SYSTEM-CA-006.yaml (20 min)

**File**: `/workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/SYSTEM-CA-006.yaml`

**Changes Required** (lines 76-84):

- [ ] ❌ REMOVE: `- "services/        # Business logic..."`
- [ ] ❌ REMOVE: `- "models/          # Pydantic models..."`
- [ ] ✅ KEEP: `- "api/             # API route handlers"`
- [ ] ✅ UPDATE: `- "db/"` to only include `connection.py` and `base.py`
- [ ] ✅ ADD: `- "middleware/"` section (error_handler.py, logging.py, cors.py)
- [ ] ✅ ADD: `- "schemas/"` section (health.py, error.py for shared DTOs)
- [ ] ✅ ADD: `features:` section with all 6 features' directory structure

**After editing**:

- [ ] Validate YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('SYSTEM-CA-006.yaml'))"`

### Task 1.2: Add `code_generation.phases` Section (15 min)

**File**: Same SYSTEM-CA-006.yaml

**Location**: After `code_generation.folder_structure`

- [ ] Add complete `phases:` section with 10 phases
- [ ] Each phase defines: name, max_tokens (8192), files, dependencies, acceptance_criteria
- [ ] Validate YAML syntax again

### Task 1.3: Update All 6 Feature YAMLs (10 min)

**Files**:

1. [ ] `FEATURE-CA-006-01_analytics_integration.yaml`
2. [ ] `FEATURE-CA-006-02_engagement_tracking.yaml`
3. [ ] `FEATURE-CA-006-03_revenue_tracking.yaml`
4. [ ] `FEATURE-CA-006-04_prioritization_engine.yaml`
5. [ ] `FEATURE-CA-006-05_automated_iteration.yaml`
6. [ ] `FEATURE-CA-006-06_dashboard_visualization.yaml`

**For Each Feature**:

- [ ] Add `directory_structure:` section showing services/, models/, db/, tests/
- [ ] Add `models/` to `code_structure:` with specific model files
- [ ] Add `db/` to `code_structure:` with schema.py and repositories.py
- [ ] Add `tests/` to `code_structure:` with test files

**Validation**:

- [ ] Run compliance check: Should show **100% compliance**

```bash
cd /workspaces/business_ventures/Causal_affect
python3 << 'EOF'
import yaml
from pathlib import Path
import json

system_yaml = Path("SYSTEM-CA-006_feedback_iteration/SYSTEM-CA-006.yaml")
with open(system_yaml) as f:
    system_spec = yaml.safe_load(f)

backend_structure = system_spec['code_generation']['folder_structure']['source_backend']
backend_str = json.dumps(backend_structure, indent=2)

violations = []
if '"services"' in backend_str or 'app/services' in backend_str:
    violations.append("FAIL: Still has app/services/")
if '"models"' in backend_str or 'app/models' in backend_str:
    violations.append("FAIL: Still has app/models/")

if violations:
    print("❌ COMPLIANCE CHECK FAILED:")
    for v in violations:
        print(f"  {v}")
else:
    print("✅ 100% COMPLIANCE - Ready for implementation!")
EOF
```

---

## 📋 Part 2: Update build_system.py (30 minutes)

### Task 2.1: Backup Current Version

- [ ] `cp /workspaces/control_tower/build_system.py /workspaces/control_tower/build_system.py.backup`

### Task 2.2: Implement Multi-Phase Architecture

**File**: `/workspaces/control_tower/build_system.py`

**New Methods to Add**:

- [ ] `_load_feature_yamls()` - Load all feature YAML files into dict
- [ ] `_build_phase_prompt(phase)` - Build AI prompt for specific phase
- [ ] `_generate_phase(phase)` - Execute single phase generation
- [ ] `_dependencies_met(phase, results)` - Check if dependencies satisfied
- [ ] `_validate_acceptance_criteria(phase, result)` - Validate phase output
- [ ] `_extract_feature_requirements(feature_yaml)` - Extract requirements from feature YAML
- [ ] `_format_file_list(files)` - Format files for prompt
- [ ] `_format_acceptance_criteria(criteria)` - Format criteria for prompt

**Update Existing Methods**:

- [ ] `__init__()` - Add phase loading, feature YAML loading
- [ ] `generate_system_integration()` - Iterate through phases instead of single call

**Test**:

- [ ] `python3 build_system.py --help` (should work)
- [ ] Check for syntax errors

---

## 📋 Part 3: Execute Phased Generation (75 minutes)

### Task 3.1: Test Phase 1 Only (10 min)

```bash
cd /workspaces/control_tower
python3 build_system.py \
  --system-yaml /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/SYSTEM-CA-006.yaml \
  --phase phase_01_system_infrastructure \
  --verbose
```

**Validation**:

- [ ] 12 files created in `src/feedback_iteration/backend/app/`
- [ ] `app/main.py` exists with FastAPI app
- [ ] `app/config.py` exists with Pydantic Settings
- [ ] `app/db/connection.py` exists
- [ ] No syntax errors: `python3 -m py_compile app/*.py`

### Task 3.2: Execute All 10 Phases (60-75 min)

```bash
cd /workspaces/control_tower
python3 build_system.py \
  --system-yaml /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/SYSTEM-CA-006.yaml \
  --all-phases \
  --verbose
```

**Expected Console Output**:

```
🚀 Starting Multi-Phase System Integration Generation
Total Phases: 10
Estimated Time: 60 minutes

🔨 Phase 1: System Infrastructure (3 min)
  ✅ Generated 12 files
  ✅ Acceptance criteria met
  ✅ Phase 1 complete

🔨 Phase 2: API Routers (5 min)
  ✅ Generated 6 files
  ✅ Acceptance criteria met
  ✅ Phase 2 complete

🔨 Phase 3: FEATURE-01 Analytics (8 min)
  ✅ Generated 9 files
  ✅ Acceptance criteria met
  ✅ Phase 3 complete

... (continue for all 10 phases)

🎉 SYSTEM INTEGRATION COMPLETE
Total Time: 73 minutes
Files Generated: 42
Lines of Code: 2,847
Compliance: 100%
```

**Monitor For**:

- [ ] Each phase completes successfully
- [ ] No truncation errors
- [ ] No JSON parse errors
- [ ] File count increasing

---

## 📋 Part 4: Validation (15 minutes)

### Task 4.1: Directory Structure Check

```bash
cd /workspaces/business_ventures/Causal_affect/src/feedback_iteration/backend
tree -L 4
```

**Expected Structure**:

- [ ] `app/` directory exists
- [ ] `app/api/` with 5 router files
- [ ] `app/db/connection.py` and `app/db/base.py`
- [ ] `app/middleware/` with 3 files
- [ ] `features/` directory exists
- [ ] 6 feature directories (FEATURE-CA-006-01 through 06)
- [ ] Each feature has `services/`, `models/`, `db/`, `tests/`

### Task 4.2: Syntax Validation

```bash
# Check all Python files compile
find . -name "*.py" -exec python3 -m py_compile {} \;
echo "✅ All files have valid Python syntax"

# Count files and lines
echo "Files created: $(find . -name '*.py' | wc -l)"
echo "Lines of code: $(find . -name '*.py' -exec wc -l {} + | tail -1)"
```

**Expected**:

- [ ] No syntax errors
- [ ] 40+ Python files
- [ ] 2,500+ lines of code

### Task 4.3: Import Validation

```bash
cd /workspaces/business_ventures/Causal_affect/src/feedback_iteration/backend

python3 << 'EOF'
try:
    from app.main import app
    print("✅ Main app imports successfully")
    
    from app.config import Settings
    print("✅ Config imports successfully")
    
    from app.db.connection import get_session
    print("✅ Database connection imports successfully")
    
    print("\n✅ All critical imports work!")
except Exception as e:
    print(f"❌ Import error: {e}")
EOF
```

- [ ] All imports work

### Task 4.4: Run Tests

```bash
cd /workspaces/business_ventures/Causal_affect/src/feedback_iteration/backend

# Install test dependencies if needed
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v --tb=short

# Check coverage
pytest tests/ --cov=app --cov=features --cov-report=term-missing
```

**Expected**:

- [ ] All tests pass
- [ ] Coverage > 80%
- [ ] No critical failures

### Task 4.5: Start Server

```bash
cd /workspaces/business_ventures/Causal_affect/src/feedback_iteration/backend

# Set up .env file
cp .env.example .env
# Edit .env with actual values

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Validation**:

- [ ] Server starts without errors
- [ ] Visit http://localhost:8000/health → Returns 200 OK
- [ ] Visit http://localhost:8000/docs → OpenAPI docs load
- [ ] Check all 6 feature endpoints appear in docs

---

## 📊 Success Metrics Checklist

| Metric | Before | Target | Actual | Status |
|--------|--------|--------|--------|--------|
| YAML Compliance | 60% | 100% | ___% | ☐ |
| Files Generated | 9 | 40+ | ___ | ☐ |
| Lines of Code | 464 | 2,500+ | ___ | ☐ |
| Features Complete | 0% | 100% | ___% | ☐ |
| Unit Tests | 0 | 20+ | ___ | ☐ |
| Test Coverage | 0% | 80%+ | ___% | ☐ |
| Manual Work Needed | 75% | 0% | ___% | ☐ |
| Server Starts | ❌ | ✅ | ☐ | ☐ |
| API Docs Generated | ❌ | ✅ | ☐ | ☐ |

---

## 🚨 Troubleshooting Guide

### Issue: YAML Syntax Error

**Symptom**: `yaml.scanner.ScannerError`

**Fix**:

```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('SYSTEM-CA-006.yaml'))"
# Check indentation, colons, quotes
```

### Issue: Phase Truncation (Response > 8K tokens)

**Symptom**: `⚠️ Response appears truncated`

**Fix**: Split phase into 2 sub-phases

```yaml
phase_04a_feature_02_engagement_services:
  max_tokens: 8192
  files:
    - services/*.py  # Only services

phase_04b_feature_02_engagement_models_db:
  max_tokens: 8192
  dependencies: ["phase_04a_feature_02_engagement_services"]
  files:
    - models/*.py
    - db/*.py
```

### Issue: Dependency Not Met

**Symptom**: `⏸️ Skipping ... - dependencies not met`

**Fix**: Check previous phase succeeded

```bash
# Re-run failed phase
python3 build_system.py --phase phase_XX --verbose
```

### Issue: Import Errors After Generation

**Symptom**: `ModuleNotFoundError` when importing

**Fix**: Check `__init__.py` files created

```bash
# Add missing __init__.py
touch features/FEATURE-XX/__init__.py
touch features/FEATURE-XX/services/__init__.py
```

### Issue: Tests Failing

**Symptom**: Pytest failures

**Fix**: Check test fixtures in conftest.py

```python
# tests/conftest.py should have:
import pytest
from app.main import app
from app.db.connection import get_session

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)
```

---

## 📝 Notes & Observations

**Space for tomorrow's notes**:

- Phase execution times (actual vs estimated):
- Issues encountered:
- Solutions applied:
- Final metrics:

---

## ✅ Final Sign-Off

- [ ] YAML Compliance: 100%
- [ ] All 10 phases executed successfully
- [ ] 40+ files generated
- [ ] 2,500+ lines of code
- [ ] All tests passing
- [ ] Server starts successfully
- [ ] API documentation accessible
- [ ] Zero manual code completion required

**Date Completed**: ______________

**Total Time**: ______________

**Status**: ☐ SUCCESS ☐ PARTIAL ☐ NEEDS REWORK

---

**🚀 Ready to execute tomorrow! Let's achieve true automation!**
