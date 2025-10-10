# 🧪 User Acceptance Testing (UAT) Guide
## SYSTEM-004-01 AI Code Generation System

---

## 🚀 Quick Start - Run UAT in 3 Steps

### Step 1: Set Your API Key
```bash
# Option A: Use OpenAI (GPT-4)
export OPENAI_API_KEY="your-openai-api-key-here"

# Option B: Use Anthropic (Claude)
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

### Step 2: Run the UAT Script
```bash
cd /workspaces/control_tower/UAT

# Default (uses OpenAI)
python run_uat.py

# Or use Anthropic
python run_uat.py --provider anthropic

# Verbose mode (see detailed output)
python run_uat.py --verbose
```

### Step 3: Review Results
The UAT script will:
- ✅ Generate Python code from YAML requirements using AI
- ✅ Execute complete TDD cycle (RED → GREEN → REFACTOR)
- ✅ Run all generated tests
- ✅ Verify all artifacts are created
- ✅ Generate comprehensive UAT report

**Expected Output Structure:**
```
UAT/output/
├── src/layer/string_utilities/
│   ├── __init__.py
│   └── string_utilities.py          ← AI-generated implementation
├── tests/layer/string_utilities/
│   ├── test_string_utilities_unit.py       ← AI-generated unit tests
│   └── test_string_utilities_integration.py ← AI-generated integration tests
├── Requirements Verification/
│   ├── requirements_verification_complete.yaml
│   ├── test_pyramid_report.yaml
│   ├── quality_gates_report.yaml
│   └── execution_evidence.json
└── Testing Outputs/
    ├── red_phase_log_*.txt
    ├── green_phase_log_*.txt
    └── refactor_phase_log_*.txt
```

---

## 📋 What Gets Tested?

The UAT executes the AI Code Generator on a **real feature specification** to generate:

**Feature: String Utilities (3 functions)**
1. `capitalize_words(text: str) -> str` - Capitalize first letter of each word
2. `reverse_words(text: str) -> str` - Reverse word order
3. `count_vowels(text: str) -> int` - Count vowels (case-insensitive)

The system will:
1. **Parse** the YAML requirement file
2. **Generate tests** via AI (RED phase - tests should fail)
3. **Generate implementation** via AI (GREEN phase - tests should pass)
4. **Refactor code** via AI (REFACTOR phase - improve quality)
5. **Verify** all quality gates and generate reports

---

## ✅ Success Criteria

UAT PASSES if:
- ✅ All 3 functions are implemented correctly
- ✅ All generated tests pass (100% pass rate)
- ✅ Code is syntactically valid Python
- ✅ Test coverage ≥ 90%
- ✅ Test pyramid ratio ≥ 2:1 (unit:integration)
- ✅ All TDD phases executed (RED → GREEN → REFACTOR)
- ✅ All required artifacts generated
- ✅ Verification reports created

---

## 🔍 Manual Verification

After the automated UAT completes, manually verify the quality:

### 1. Check Generated Code
```bash
# View the AI-generated implementation
cat output/src/layer/string_utilities/string_utilities.py
```

**Look for:**
- Clean, readable code
- Proper docstrings
- Type hints
- Error handling
- No obvious bugs

### 2. Test the Functions Manually
```python
cd output
python

>>> from src.layer.string_utilities.string_utilities import *

# Test capitalize_words
>>> capitalize_words("hello world")
'Hello World'  # Should match

# Test reverse_words
>>> reverse_words("one two three")
'three two one'  # Should match

# Test count_vowels
>>> count_vowels("Hello World!")
3  # Should match
```

### 3. Review Test Files
```bash
# View generated tests
cat output/tests/layer/string_utilities/test_string_utilities_unit.py
cat output/tests/layer/string_utilities/test_string_utilities_integration.py
```

**Look for:**
- Comprehensive test coverage
- Tests for all examples from YAML
- Edge case tests
- Error condition tests
- Proper test structure

### 4. Check Verification Reports
```bash
# View comprehensive verification
cat output/Requirements\ Verification/requirements_verification_complete.yaml

# View test pyramid
cat output/Requirements\ Verification/test_pyramid_report.yaml

# View quality gates
cat output/Requirements\ Verification/quality_gates_report.yaml
```

### 5. Review TDD Cycle Logs
```bash
# RED phase (tests should have failed)
cat output/Testing\ Outputs/red_phase_log_*.txt

# GREEN phase (tests should pass)
cat output/Testing\ Outputs/green_phase_log_*.txt

# REFACTOR phase (tests still pass, code improved)
cat output/Testing\ Outputs/refactor_phase_log_*.txt
```

---

## 📊 UAT Report

After execution, find the complete UAT report:
```bash
ls -la uat_report_*.json
cat uat_report_*.json
```

The report contains:
- Execution summary (duration, AI provider used)
- Artifact counts (implementation, tests, reports, logs)
- Test results (total, passed, failed, coverage)
- Quality gate results
- Overall pass/fail status

---

## 🎯 Expected Results

**UAT should complete in:** 5-10 minutes (including AI generation time)

**Final message should be:**
```
🎉 UAT PASSED! System is ready for production deployment.
```

If you see this, the **SYSTEM-004-01 AI Code Generation System** has successfully:
- Used AI to generate working code from requirements
- Followed complete TDD methodology
- Produced production-quality code
- Generated all required verification artifacts
- Passed all quality gates

**System Status: CERTIFIED FOR PRODUCTION** ✅

---

## 🐛 Troubleshooting

### Issue: "API Key not set"
```bash
# Make sure you exported the key
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify it's set
echo $OPENAI_API_KEY
```

### Issue: "Module not found"
```bash
# Install required packages
pip install openai anthropic pytest pytest-cov pyyaml pytest-json-report
```

### Issue: "Tests failed"
- Review the generated implementation in `output/src/`
- Check test logs in `output/Testing Outputs/`
- Verify the AI understood the requirements correctly
- Try running again (AI may produce different results)

### Issue: "Execution timeout"
- AI generation can take time (especially for complex features)
- Default timeout is 10 minutes
- If it times out, the feature might be too complex

---

## 📞 Support

For detailed execution plan and checklist, see:
- `UAT_EXECUTION_PLAN.md` - Complete UAT methodology
- `LAYER-UAT-001_string_utilities.yaml` - Test requirements specification

For questions about the AI Code Generation System, see:
- `projects/PROJECT-004 AI CODE GENERATOR/SYSTEM-004-01 AI CODE GENERATION SYSTEM/`
- System verification: `SYSTEM-004-01_requirements_verification_*.yaml`

---

## 🎉 Next Steps After UAT Passes

1. **Review the generated code quality** - Ensure it meets your standards
2. **Test with your own features** - Create custom YAML requirements
3. **Deploy to production** - The system is certified and ready
4. **Monitor AI costs** - Track API usage for OpenAI/Anthropic
5. **Iterate and improve** - Use feedback to enhance the system

**Congratulations! You've successfully validated the AI Code Generation System!** 🚀
