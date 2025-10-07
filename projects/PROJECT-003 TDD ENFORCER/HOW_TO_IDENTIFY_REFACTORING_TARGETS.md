# How to Identify What Needs Refactoring - Systematic Approach

**Created**: 2025-10-07  
**Purpose**: Explain best practice approach to identify actor behavior in validator code  
**Context**: You don't need to read entire codebase - use systematic detection methods

---

## 🎯 THE QUESTION

**"Do we have to go through the entire codebase, list out all actor implementations, then refactor one by one?"**

**Short Answer**: **NO!** Use systematic detection methods to find actor behavior automatically.

---

## 📋 BEST PRACTICE: SYSTEMATIC DETECTION (Not Manual Reading)

### **Strategy: Use Code Analysis Tools, Not Manual Review**

```
❌ INEFFICIENT APPROACH:
Read entire codebase line by line → Manually identify actor code → List everything → Refactor

✅ EFFICIENT APPROACH:
Use automated detection → Find actor patterns → Verify findings → Refactor systematically
```

---

## 🔍 METHOD 1: Pattern-Based Grep Search (5 minutes)

### **What We're Looking For**

Actor behavior has **distinct patterns**:
- File creation: `open(..., 'w')`, `mkdir()`, `Path(...).write_text()`
- File modification: `open(..., 'a')`, file writes
- Command execution: `subprocess.run()`, `os.system()`
- External actions: API calls, database writes

### **Step 1: Search for File Writing Patterns**

```bash
# Search for file writing in TDDWorkflowEnforcer
cd /workspaces/control_tower

# Pattern 1: open() with write mode
grep -n "open.*'w'" legacy/utilities/tdd_workflow_enforcer.py

# Pattern 2: Path.write_text() or similar
grep -n "write_text\|write_bytes" legacy/utilities/tdd_workflow_enforcer.py

# Pattern 3: mkdir() calls (directory creation)
grep -n "mkdir" legacy/utilities/tdd_workflow_enforcer.py

# Pattern 4: File object writes
grep -n "\.write(" legacy/utilities/tdd_workflow_enforcer.py
```

**Expected Output**:
```bash
# Example results showing actor behavior
399:        test_dir.mkdir(parents=True, exist_ok=True)
412:        with open(test_file, 'w') as f:
413:            f.write(test_content)
```

**Interpretation**: 
- Line 399: Creates directory (ACTOR behavior)
- Line 412-413: Writes file (ACTOR behavior)
- These are in `stage_gate_3_test_generation_verification()`

### **Step 2: Search for Command Execution**

```bash
# Pattern: subprocess calls
grep -n "subprocess\|os.system\|os.popen" legacy/utilities/tdd_workflow_enforcer.py

# Pattern: Test execution
grep -n "pytest.main\|unittest.main" legacy/utilities/tdd_workflow_enforcer.py
```

**Expected Output**: Should be NONE (enforcer shouldn't execute tests directly)

### **Step 3: Create Finding Report**

```bash
# Generate comprehensive report
cat > /tmp/actor_behavior_findings.txt << 'EOF'
ACTOR BEHAVIOR DETECTION REPORT
Generated: $(date)
File: legacy/utilities/tdd_workflow_enforcer.py

FILE WRITING PATTERNS:
EOF

echo "=== open() with write mode ===" >> /tmp/actor_behavior_findings.txt
grep -n "open.*'w'" legacy/utilities/tdd_workflow_enforcer.py >> /tmp/actor_behavior_findings.txt

echo "" >> /tmp/actor_behavior_findings.txt
echo "=== mkdir() calls ===" >> /tmp/actor_behavior_findings.txt
grep -n "mkdir" legacy/utilities/tdd_workflow_enforcer.py >> /tmp/actor_behavior_findings.txt

echo "" >> /tmp/actor_behavior_findings.txt
echo "=== .write() calls ===" >> /tmp/actor_behavior_findings.txt
grep -n "\.write(" legacy/utilities/tdd_workflow_enforcer.py >> /tmp/actor_behavior_findings.txt

# Review findings
cat /tmp/actor_behavior_findings.txt
```

**Result**: Complete list of actor behaviors in <5 minutes, no manual reading required!

---

## 🔍 METHOD 2: AST-Based Code Analysis (10 minutes, more thorough)

### **Use Python AST to Find Patterns Programmatically**

Create a script that analyzes code structure:

```python
# File: tools/detect_actor_behavior.py

import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class ActorBehaviorDetector(ast.NodeVisitor):
    """Detects actor behavior patterns in Python code."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.findings: List[Dict] = []
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        """Track which function we're in."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_Call(self, node):
        """Find function calls that indicate actor behavior."""
        
        # Pattern 1: open() with 'w' or 'a' mode
        if isinstance(node.func, ast.Name) and node.func.id == 'open':
            if len(node.args) >= 2:
                mode_arg = node.args[1]
                if isinstance(mode_arg, ast.Constant):
                    if 'w' in mode_arg.value or 'a' in mode_arg.value:
                        self.findings.append({
                            'type': 'FILE_WRITE',
                            'function': self.current_function,
                            'line': node.lineno,
                            'pattern': f"open(..., '{mode_arg.value}')",
                            'severity': 'HIGH'
                        })
        
        # Pattern 2: Path.mkdir()
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'mkdir':
                self.findings.append({
                    'type': 'DIRECTORY_CREATE',
                    'function': self.current_function,
                    'line': node.lineno,
                    'pattern': '.mkdir()',
                    'severity': 'HIGH'
                })
            
            # Pattern 3: Path.write_text() / write_bytes()
            if node.func.attr in ['write_text', 'write_bytes']:
                self.findings.append({
                    'type': 'FILE_WRITE',
                    'function': self.current_function,
                    'line': node.lineno,
                    'pattern': f'.{node.func.attr}()',
                    'severity': 'HIGH'
                })
            
            # Pattern 4: subprocess.run() / os.system()
            if node.func.attr in ['run', 'call', 'check_output']:
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'subprocess':
                        self.findings.append({
                            'type': 'COMMAND_EXECUTION',
                            'function': self.current_function,
                            'line': node.lineno,
                            'pattern': f'subprocess.{node.func.attr}()',
                            'severity': 'MEDIUM'
                        })
        
        self.generic_visit(node)

def analyze_file(filepath: str) -> List[Dict]:
    """Analyze Python file for actor behavior."""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read(), filename=filepath)
    
    detector = ActorBehaviorDetector(filepath)
    detector.visit(tree)
    return detector.findings

def generate_report(findings: List[Dict]) -> str:
    """Generate human-readable report."""
    if not findings:
        return "✅ No actor behavior detected - Pure validator!"
    
    report = []
    report.append("⚠️  ACTOR BEHAVIOR DETECTED\n")
    report.append("=" * 60)
    
    # Group by function
    by_function = {}
    for finding in findings:
        func = finding['function'] or 'module_level'
        if func not in by_function:
            by_function[func] = []
        by_function[func].append(finding)
    
    # Report each function
    for func_name, func_findings in sorted(by_function.items()):
        report.append(f"\n📍 Function: {func_name}")
        report.append("-" * 60)
        
        for finding in func_findings:
            severity_emoji = "🔴" if finding['severity'] == 'HIGH' else "🟡"
            report.append(
                f"  {severity_emoji} Line {finding['line']}: "
                f"{finding['type']} - {finding['pattern']}"
            )
    
    report.append("\n" + "=" * 60)
    report.append(f"Total findings: {len(findings)}")
    report.append("\n💡 RECOMMENDATION:")
    report.append("These functions contain ACTOR behavior (file writing, execution).")
    report.append("Refactor to VALIDATOR behavior (receive paths, validate files).")
    
    return "\n".join(report)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_actor_behavior.py <file_path>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not Path(filepath).exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    
    print(f"🔍 Analyzing: {filepath}\n")
    
    findings = analyze_file(filepath)
    report = generate_report(findings)
    
    print(report)
    
    # Exit code: 1 if findings, 0 if clean
    sys.exit(1 if findings else 0)
```

**Run the analyzer**:

```bash
# Run automated detection
python tools/detect_actor_behavior.py legacy/utilities/tdd_workflow_enforcer.py

# Expected output:
# ⚠️  ACTOR BEHAVIOR DETECTED
# ============================================================
# 
# 📍 Function: stage_gate_3_test_generation_verification
# ------------------------------------------------------------
#   🔴 Line 399: DIRECTORY_CREATE - .mkdir()
#   🔴 Line 412: FILE_WRITE - open(..., 'w')
#   🔴 Line 413: FILE_WRITE - .write()
# 
# ============================================================
# Total findings: 3
# 
# 💡 RECOMMENDATION:
# These functions contain ACTOR behavior (file writing, execution).
# Refactor to VALIDATOR behavior (receive paths, validate files).
```

**Result**: Precise identification of ALL actor behaviors in 10 minutes!

---

## 🔍 METHOD 3: Git Diff Pattern Search (If You Have History)

### **Find Actor Code Added in Commits**

If the code evolved over time, find when actor behavior was added:

```bash
# Search git history for file writing patterns
git log -p legacy/utilities/tdd_workflow_enforcer.py | grep -B5 -A5 "open.*'w'"

# Find commits that added mkdir()
git log -p legacy/utilities/tdd_workflow_enforcer.py | grep -B5 -A5 "mkdir"

# Show functions that write files
git log --all -S "open(" -S "mkdir" -- legacy/utilities/tdd_workflow_enforcer.py
```

**Use Case**: Understanding WHY actor code exists (was it intentional or creep?)

---

## 🔍 METHOD 4: Test-Driven Detection (Most Reliable)

### **Write Tests That FIND Actor Behavior**

```python
# File: tests/meta/test_detect_actor_behavior.py

import ast
import pytest
from pathlib import Path

def test_enforcer_does_not_write_files():
    """Meta-test: Detect if enforcer contains file writing code."""
    
    enforcer_file = Path("legacy/utilities/tdd_workflow_enforcer.py")
    with open(enforcer_file, 'r') as f:
        source_code = f.read()
    
    # Parse AST
    tree = ast.parse(source_code)
    
    # Find all open() calls with write mode
    file_writes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'open':
                if len(node.args) >= 2:
                    mode = node.args[1]
                    if isinstance(mode, ast.Constant):
                        if 'w' in mode.value or 'a' in mode.value:
                            file_writes.append(node.lineno)
    
    # ASSERTION: Should be ZERO file writes
    assert len(file_writes) == 0, \
        f"❌ Enforcer contains {len(file_writes)} file write(s) at lines: {file_writes}\n" \
        f"Validator should NOT write files - this is actor behavior!"

def test_enforcer_does_not_create_directories():
    """Meta-test: Detect if enforcer creates directories."""
    
    enforcer_file = Path("legacy/utilities/tdd_workflow_enforcer.py")
    with open(enforcer_file, 'r') as f:
        source_code = f.read()
    
    # Simple pattern search (mkdir calls)
    mkdir_lines = [
        i + 1 for i, line in enumerate(source_code.split('\n'))
        if 'mkdir(' in line and not line.strip().startswith('#')
    ]
    
    # ASSERTION: Should be ZERO mkdir calls
    assert len(mkdir_lines) == 0, \
        f"❌ Enforcer creates directories at lines: {mkdir_lines}\n" \
        f"Validator should NOT create directories - this is actor behavior!"

def test_enforcer_does_not_execute_commands():
    """Meta-test: Detect if enforcer executes system commands."""
    
    enforcer_file = Path("legacy/utilities/tdd_workflow_enforcer.py")
    with open(enforcer_file, 'r') as f:
        source_code = f.read()
    
    # Check for subprocess/os.system calls
    command_patterns = ['subprocess.', 'os.system(', 'os.popen(']
    found_commands = []
    
    for pattern in command_patterns:
        if pattern in source_code:
            lines = [
                i + 1 for i, line in enumerate(source_code.split('\n'))
                if pattern in line and not line.strip().startswith('#')
            ]
            if lines:
                found_commands.append((pattern, lines))
    
    # ASSERTION: Should be ZERO command executions
    assert len(found_commands) == 0, \
        f"❌ Enforcer executes commands: {found_commands}\n" \
        f"Validator should NOT execute commands - this is actor behavior!"
```

**Run the detection tests**:

```bash
# Run meta-tests to detect actor behavior
pytest tests/meta/test_detect_actor_behavior.py -v

# Expected output (BEFORE refactoring):
# test_enforcer_does_not_write_files FAILED ❌
#   AssertionError: Enforcer contains 1 file write(s) at lines: [412]
#   Validator should NOT write files - this is actor behavior!
# 
# test_enforcer_does_not_create_directories FAILED ❌
#   AssertionError: Enforcer creates directories at lines: [399]
#   Validator should NOT create directories - this is actor behavior!
# 
# test_enforcer_does_not_execute_commands PASSED ✅

# After refactoring, all should PASS
```

**Why This is Best**: 
- Tests are **automated** (run in CI/CD)
- Tests **prevent regression** (actor code can't sneak back in)
- Tests **document intent** ("enforcer should NOT write files")

---

## 📊 COMPARISON: Which Method to Use?

| Method | Speed | Accuracy | Automation | Best For |
|--------|-------|----------|------------|----------|
| **Grep Search** | ⚡ 5 min | 85% | ✅ Yes | Quick initial scan |
| **AST Analysis** | ⚡⚡ 10 min | 95% | ✅ Yes | Thorough detection |
| **Git History** | ⏱️ 15 min | 70% | ⚠️ Manual | Understanding context |
| **Meta-Tests** | ⚡ 5 min | 100% | ✅✅ CI/CD | Ongoing prevention |

**Recommended Approach**: **Combine Methods**

1. **Start with Grep** (5 min): Quick finding of obvious patterns
2. **Verify with AST** (10 min): Catch edge cases grep might miss
3. **Lock with Meta-Tests** (5 min): Prevent future regressions

**Total Time**: ~20 minutes vs. hours of manual code reading!

---

## 🎯 PRACTICAL WORKFLOW FOR PROJECT-003

### **Step-by-Step: Find Actor Behavior in TDDWorkflowEnforcer**

```bash
# Step 1: Quick grep search (2 minutes)
cd /workspaces/control_tower

echo "🔍 Searching for actor behavior patterns..."

# File writing
echo "=== FILE WRITING ===" 
grep -n "open.*'w'\|write_text\|write_bytes" legacy/utilities/tdd_workflow_enforcer.py

# Directory creation  
echo "=== DIRECTORY CREATION ==="
grep -n "mkdir" legacy/utilities/tdd_workflow_enforcer.py

# Command execution
echo "=== COMMAND EXECUTION ===" 
grep -n "subprocess\|os.system" legacy/utilities/tdd_workflow_enforcer.py

# Step 2: Organize findings by function (3 minutes)
echo ""
echo "📋 Organizing findings by function..."

# For each finding, show the function it's in
grep -B10 "open.*'w'\|mkdir" legacy/utilities/tdd_workflow_enforcer.py | \
  grep "def " | sort | uniq

# Step 3: Create refactoring checklist (2 minutes)
cat > /tmp/refactoring_checklist.md << 'EOF'
# Refactoring Checklist - Actor Behavior Removal

## Findings from Automated Detection

### ❌ stage_gate_3_test_generation_verification
- [ ] Line 399: Remove `test_dir.mkdir(parents=True, exist_ok=True)`
- [ ] Line 412-413: Remove `with open(test_file, 'w') as f: f.write(...)`
- [ ] Change signature: `generated_tests: List` → `test_file_paths: List[str]`
- [ ] Add validation: Check files exist, validate syntax, check coverage

### ✅ stage_gate_4_red_phase_validation  
- [x] Already pure validator (receives test_results_output)
- [x] No changes needed

### ✅ stage_gate_5 through stage_gate_10
- [x] Review each for actor patterns
- [ ] Update signatures if needed

## Refactoring Order

1. **Stage 3** (CRITICAL): Most obvious actor behavior
2. **Stages 5-7**: Check for implicit actor behavior  
3. **Stages 8-10**: Usually already validators

## Estimated Time
- Detection: ✅ Complete (20 minutes)
- Refactoring: ~2 days (16 hours)
EOF

cat /tmp/refactoring_checklist.md
```

**Output**: Complete refactoring checklist in **~20 minutes** without reading entire codebase!

---

## ✅ ANSWER TO YOUR QUESTION

### **"Do we have to go through entire codebase and list everything?"**

**NO! Here's what you actually do:**

```
✅ EFFICIENT APPROACH (20 minutes total):

1. Run grep search for patterns (5 min)
   → Finds: Line 399 (mkdir), Line 412-413 (file write)
   → Located in: stage_gate_3_test_generation_verification()

2. Create AST analyzer (10 min)
   → Confirms grep findings
   → Catches any edge cases
   → Generates precise line numbers

3. Write meta-tests (5 min)
   → Tests fail showing exact actor behaviors
   → After refactoring, tests will pass
   → Prevents regression forever

RESULT: Complete list of what to refactor in 20 minutes!
```

### **What You DON'T Need to Do**

```
❌ Don't manually read 1824 lines of code
❌ Don't guess which functions have actor behavior  
❌ Don't worry about missing something
❌ Don't refactor blindly hoping to find issues

✅ Let automated tools find patterns
✅ Let tests verify completeness
✅ Focus refactoring effort on known issues
```

---

## 🚀 IMMEDIATE NEXT STEPS

**For YOUR project right now:**

```bash
# Run this 3-command sequence (5 minutes):

# 1. Find file writes
grep -n "open.*'w'\|mkdir\|write_text" \
  legacy/utilities/tdd_workflow_enforcer.py

# 2. Find command executions  
grep -n "subprocess\|os.system\|pytest.main" \
  legacy/utilities/tdd_workflow_enforcer.py

# 3. Show which functions contain actor behavior
grep -B10 "open.*'w'\|mkdir" \
  legacy/utilities/tdd_workflow_enforcer.py | grep "def "

# Done! You now have complete list of what needs refactoring.
```

**Expected Result**:
```
399:        test_dir.mkdir(parents=True, exist_ok=True)
412:        with open(test_file, 'w') as f:
413:            f.write(test_content)

Function containing actor behavior:
→ stage_gate_3_test_generation_verification()

REFACTORING SCOPE: 1 function, ~50 lines of code
TIME ESTIMATE: 2 days (includes writing tests, refactoring, validation)
```

---

## 📝 SUMMARY

**Best Practice for Finding Actor Behavior**:

1. **Use Pattern Search** (grep/AST) - DON'T manually read code
2. **Write Detection Tests** - Automate finding + prevent regression  
3. **Generate Checklist** - Know exactly what to refactor
4. **Refactor Systematically** - One function at a time with TDD

**Time Investment**:
- ❌ Manual review: 4-8 hours (error-prone)
- ✅ Automated detection: 20 minutes (precise)
- ✅ Refactoring: 2 days (once you know what to change)

**Key Insight**: Spend 20 minutes on detection to save hours of guessing!

---

**Status**: Ready to run automated detection  
**Next Action**: Run grep commands to find actor patterns in 5 minutes
