# 🚀 AI Feature Builder - Quick Start Guide

**Build complete features with a single command!**

---

## ⚡ Quick Start

```bash
# Set your API key
export OPENAI_API_KEY="your-key-here"

# Build a feature (example: Workflow State Management)
python build_feature.py "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-03 WORKFLOW ORCHESTRATION SYSTEM/FEATURE-003-03-01 Workflow Orchestration Engine/FEATURE-003-03-01_workflow_orchestration_engine.yaml"
```

**That's it!** The AI will:
1. ✅ Read the feature specification
2. ✅ Build each layer sequentially
3. ✅ Generate code via AI (tests → implementation → refactor)
4. ✅ Run all tests
5. ✅ Generate verification reports
6. ✅ Save everything to `AI_GENERATED_FEATURES/`

---

## 📋 Command Format

```bash
python build_feature.py [OPTIONS] <feature-yaml-path>
```

### Required Arguments

- **`<feature-yaml-path>`** - Path to feature YAML specification

### Optional Arguments

- **`--provider {openai|anthropic}`** - AI provider (default: openai)
- **`--verbose`** - Show detailed output and stack traces
- **`--help`** - Show help message

---

## 🎯 Examples

### Example 1: Build Workflow Orchestration Engine

```bash
export OPENAI_API_KEY="sk-..."

python build_feature.py \
  "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-03 WORKFLOW ORCHESTRATION SYSTEM/FEATURE-003-03-01 Workflow Orchestration Engine/FEATURE-003-03-01_workflow_orchestration_engine.yaml"
```

**What happens:**
- Builds LAYER-003-03-01-01: Workflow State Management
- Builds LAYER-003-03-01-02: Stage Sequencing Engine  
- Builds LAYER-003-03-01-03: Actor-Enforcer Communication
- Each layer gets full TDD cycle (RED → GREEN → REFACTOR)
- Complete verification reports generated

### Example 2: Use Anthropic Claude

```bash
export ANTHROPIC_API_KEY="sk-ant-..."

python build_feature.py \
  --provider anthropic \
  "projects/PROJECT-003 TDD ENFORCER/.../FEATURE-003-03-01_workflow_orchestration_engine.yaml"
```

### Example 3: Verbose Output

```bash
python build_feature.py \
  --verbose \
  "path/to/feature.yaml"
```

### Example 4: Build AI Provider Foundation

```bash
python build_feature.py \
  "projects/PROJECT-004 AI CODE GENERATOR/SYSTEM-004-01 AI CODE GENERATION SYSTEM/FEATURE-004-01-01 AI Provider Foundation/FEATURE-004-01-01_ai_provider_foundation.yaml"
```

---

## 📊 Output Structure

All generated code goes to:
```
AI_GENERATED_FEATURES/
├── LAYER-003-03-01-01/          ← Layer 1: Workflow State Management
│   ├── src/
│   │   └── orchestration/state/
│   │       └── workflow_state_manager.py
│   ├── tests/
│   │   └── layer/workflow_state/
│   │       ├── test_workflow_state_manager_unit.py
│   │       └── test_workflow_state_manager_integration.py
│   ├── Requirements Verification/
│   │   ├── requirements_verification_complete.yaml
│   │   ├── test_pyramid_report.yaml
│   │   ├── quality_gates_report.yaml
│   │   └── execution_evidence.json
│   └── Testing Outputs/
│       ├── red_phase_log_*.txt
│       ├── green_phase_log_*.txt
│       └── refactor_phase_log_*.txt
│
├── LAYER-003-03-01-02/          ← Layer 2: Stage Sequencing Engine
│   └── (same structure)
│
└── LAYER-003-03-01-03/          ← Layer 3: Actor-Enforcer Communication
    └── (same structure)
```

---

## ✅ What Gets Generated Per Layer

### Implementation Files
- Complete Python modules with classes/functions
- Type hints on all methods
- Comprehensive docstrings
- Error handling
- Input validation

### Test Files
- Unit tests (majority)
- Integration tests
- Edge case tests
- Error condition tests
- Test pyramid ratio ≥ 2:1

### Verification Reports
1. **requirements_verification_complete.yaml**
   - All acceptance criteria verified
   - Complete evidence chains
   - Traceability matrix

2. **test_pyramid_report.yaml**
   - Test distribution metrics
   - Coverage statistics
   - Pyramid ratio validation

3. **quality_gates_report.yaml**
   - RED phase verification
   - GREEN phase verification
   - REFACTOR phase verification

4. **execution_evidence.json**
   - Execution metadata
   - Timestamps
   - Test results

### TDD Phase Logs
- RED phase log (tests failed before implementation)
- GREEN phase log (tests passed after implementation)
- REFACTOR phase log (tests still pass after refactoring)

---

## 🎯 Feature Requirements

Your feature YAML must include:

```yaml
metadata:
  requirement_id: FEATURE-XXX-XX-XX
  requirement_name: "Feature Name"
  # ... other metadata

# List of layers to build
layers:
  - layer_id: LAYER-XXX-XX-XX-01
    name: "Layer 1 Name"
    requirement_file: LAYER-XXX-XX-XX-01_layer_name.yaml
    status: not_started
  
  - layer_id: LAYER-XXX-XX-XX-02
    name: "Layer 2 Name"
    requirement_file: LAYER-XXX-XX-XX-02_layer_name.yaml
    status: not_started
```

Each layer YAML must include:

```yaml
metadata:
  requirement_id: LAYER-XXX-XX-XX-XX
  requirement_name: "Layer Name"
  # ... other metadata

acceptance_criteria:
  - criterion: "AC-001: Description"
    # ... details
  - criterion: "AC-002: Description"
    # ... details
```

---

## 🕐 Estimated Duration

**Per Layer:**
- Simple layer (1-2 ACs): 5-10 minutes
- Medium layer (3-4 ACs): 10-20 minutes
- Complex layer (5+ ACs): 20-30 minutes

**Complete Feature:**
- 3 layers × 15 minutes average = **~45 minutes**

Actual time depends on:
- Complexity of acceptance criteria
- Number of methods to implement
- AI provider response time
- Your internet connection speed

---

## 🐛 Troubleshooting

### Issue: "Feature specification not found"

**Fix:** Use the full path to the YAML file
```bash
# Use absolute path
python build_feature.py "/workspaces/control_tower/projects/..."

# Or relative path from workspace root
python build_feature.py "projects/PROJECT-003/..."
```

### Issue: "OPENAI_API_KEY not set"

**Fix:** Export your API key
```bash
export OPENAI_API_KEY="sk-..."
echo $OPENAI_API_KEY  # Verify it's set
```

### Issue: "Layer spec not found"

**Fix:** Ensure the layer YAML files exist in the feature directory
```bash
# Check layer files exist
ls -la "projects/PROJECT-003/.../FEATURE-003-03-01 Workflow Orchestration Engine/"
```

### Issue: "Layer failed"

**What to do:**
1. Check the error message
2. Review the layer's output directory
3. Check TDD phase logs for details
4. Run with `--verbose` for stack traces
5. Decide whether to continue or stop

The script will ask: `Continue with next layer? (y/n)`

### Issue: "Tests failed"

**Possible causes:**
- AI misunderstood requirements
- Complex acceptance criteria
- Edge cases not handled

**Solutions:**
- Review generated code
- Check test logs
- Manually fix and re-run tests
- Try building layer again

---

## 📞 Available Features

### PROJECT-003: TDD ENFORCER

```bash
# FEATURE-003-03-01: Workflow Orchestration Engine (3 layers)
python build_feature.py "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-03 WORKFLOW ORCHESTRATION SYSTEM/FEATURE-003-03-01 Workflow Orchestration Engine/FEATURE-003-03-01_workflow_orchestration_engine.yaml"
```

### PROJECT-004: AI CODE GENERATOR

```bash
# FEATURE-004-01-01: AI Provider Foundation (2 layers)
python build_feature.py "projects/PROJECT-004 AI CODE GENERATOR/SYSTEM-004-01 AI CODE GENERATION SYSTEM/FEATURE-004-01-01 AI Provider Foundation/FEATURE-004-01-01_ai_provider_foundation.yaml"
```

---

## 🎉 Success Criteria

The build is **SUCCESSFUL** when:

✅ All layers completed without errors  
✅ All tests passing (100% pass rate)  
✅ Test pyramid ratios ≥ 2:1  
✅ Code coverage ≥ 90%  
✅ All quality gates PASSED  
✅ Verification reports generated  
✅ No syntax errors  

---

## 🚀 Quick Reference

**Simplest command:**
```bash
export OPENAI_API_KEY="sk-..."
python build_feature.py "path/to/feature.yaml"
```

**Check output:**
```bash
ls -la AI_GENERATED_FEATURES/
```

**Review layer code:**
```bash
cat AI_GENERATED_FEATURES/LAYER-XXX-XX-XX-XX/src/.../*.py
```

**Check verification:**
```bash
cat AI_GENERATED_FEATURES/LAYER-XXX-XX-XX-XX/Requirements\ Verification/requirements_verification_complete.yaml
```

---

## 💡 Pro Tips

1. **Start small** - Build one layer first to verify everything works
2. **Use verbose mode** - Helps debug issues: `--verbose`
3. **Check API limits** - AI providers have rate limits and costs
4. **Review generated code** - AI is good but not perfect
5. **Keep API keys secure** - Never commit them to git
6. **Monitor progress** - Each layer takes 10-20 minutes
7. **Save costs** - Use cheaper models for simple features

---

## 📚 Next Steps

After successful build:

1. **Review Generated Code**
   ```bash
   cd AI_GENERATED_FEATURES/LAYER-XXX-XX-XX-XX
   cat src/**/*.py
   ```

2. **Run Tests Manually**
   ```bash
   pytest tests/ -v
   ```

3. **Check Coverage**
   ```bash
   pytest tests/ --cov=src --cov-report=html
   ```

4. **Integrate into Project**
   - Move code to appropriate project location
   - Update imports
   - Add to version control
   - Deploy!

---

**Ready to build features with AI? Let's go! 🚀**

```bash
export OPENAI_API_KEY="your-key"
python build_feature.py "path/to/your/feature.yaml"
```
