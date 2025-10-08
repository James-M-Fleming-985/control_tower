# 📊 Batch Refactoring: Configuration & Structure Explained

**Date:** October 8, 2025  
**Questions Answered:**
1. How many batches are there?
2. How does the script know what to put in the YAML spec?

---

## 🔢 ANSWER 1: How Many Batches Are There?

### Total: **11 Batches**

Breaking down **461 actor behaviors** into manageable chunks:

| Batch | Name | Behaviors | Days | Status |
|-------|------|-----------|------|--------|
| **1** | Test File Generation | 10 | 1-2 | ✅ Configured |
| **2** | Test Directory Creation | 8 | 3 | ⏳ Need to configure |
| **3** | Test Execution Subprocess | 15 | 4 | ⏳ Need to configure |
| **4** | Git Operations Part 1 | ~15 | 5 | ⏳ Need to configure |
| **5** | Git Operations Part 2 | ~15 | 5-6 | ⏳ Need to configure |
| **6** | Git Operations Part 3 | ~15 | 6-7 | ⏳ Need to configure |
| **7** | Evidence Storage Review 1 | ~40 | 8 | ⏳ Need to configure |
| **8** | Evidence Storage Review 2 | ~40 | 8 | ⏳ Need to configure |
| **9** | Evidence Storage Review 3 | ~40 | 9 | ⏳ Need to configure |
| **10** | Evidence Storage Review 4 | ~40 | 9 | ⏳ Need to configure |
| **11** | Cleanup & Edge Cases | ~20 | 10 | ⏳ Need to configure |

**Total:** ~460 behaviors across 11 batches

---

## 🎯 ANSWER 2: How Does the Script Know What to Put in YAML?

### The Configuration System

The script uses **hard-coded batch configurations** stored in the `_load_batch_configurations()` method:

```python
def _load_batch_configurations(self) -> Dict[int, BatchConfig]:
    """Load all batch configurations"""
    return {
        1: BatchConfig(
            batch_number=1,
            batch_name="Test File Generation",
            behaviors=[
                BatchBehavior(
                    file_path="legacy/utilities/tdd_workflow_engine.py",
                    line_number=299,
                    current_behavior="test_file.write_text(test_content)",
                    target_behavior="validate_test_file(test_file_path)",
                    description="Creates test file - should validate instead"
                ),
                # ... 9 more behaviors
            ],
            target_days="Days 1-2",
            estimated_hours=8.0
        ),
        # Batches 2-11 would go here...
    }
```

---

## 📋 Batch 1 Configuration (Example)

### Complete Batch 1 Setup

**Currently Configured** (in the automation tool):

```python
BatchConfig(
    batch_number=1,
    batch_name="Test File Generation",
    behaviors=[
        # Behavior 1
        BatchBehavior(
            file_path="legacy/utilities/tdd_workflow_engine.py",
            line_number=299,
            current_behavior="test_file.write_text(test_content)",
            target_behavior="validate_test_file(test_file_path)",
            description="Creates test file - should validate instead"
        ),
        
        # Behavior 2
        BatchBehavior(
            file_path="legacy/utilities/tdd_workflow_engine.py",
            line_number=533,
            current_behavior="impl_file.write_text(impl_content)",
            target_behavior="validate_impl_file(impl_file_path)",
            description="Creates implementation file - should validate instead"
        ),
        
        # Behaviors 3-10 (similar structure)
        # ...
    ],
    target_days="Days 1-2",
    estimated_hours=8.0
)
```

### How This Becomes YAML

When you run:
```bash
python tools/batch_refactoring_automation.py --batch 1 --phase RED
```

The tool's `_generate_yaml_spec()` method converts the configuration to YAML:

```python
def _generate_yaml_spec(self, config: BatchConfig, output_file: Path):
    yaml_content = f"""---
metadata:
  batch_name: {config.batch_name}
  behaviors_count: {len(config.behaviors)}

behaviors:
"""
    for i, behavior in enumerate(config.behaviors, 1):
        yaml_content += f"""
  behavior_{i:03d}:
    file: {behavior.file_path}
    line: {behavior.line_number}
    current_behavior: {behavior.current_behavior}
    target_behavior: {behavior.target_behavior}
    description: {behavior.description}
"""
    
    with open(output_file, 'w') as f:
        f.write(yaml_content)
```

**Result:** Creates a YAML file like:

```yaml
---
metadata:
  batch_name: Test File Generation
  behaviors_count: 10

behaviors:
  behavior_001:
    file: legacy/utilities/tdd_workflow_engine.py
    line: 299
    current_behavior: test_file.write_text(test_content)
    target_behavior: validate_test_file(test_file_path)
    description: Creates test file - should validate instead
  
  behavior_002:
    file: legacy/utilities/tdd_workflow_engine.py
    line: 533
    current_behavior: impl_file.write_text(impl_content)
    target_behavior: validate_impl_file(impl_file_path)
    description: Creates implementation file - should validate instead
  
  # ... behaviors 3-10
```

---

## 🔍 Where Did These Behaviors Come From?

### Source: Comprehensive Detection Scan

The 461 behaviors were identified by the comprehensive detection script:

```bash
# Original detection scan (October 7, 2025)
bash /tmp/comprehensive_actor_detection.sh > COMPREHENSIVE_ACTOR_DETECTION_RESULTS_20251007.md
```

**Results:**
- Scanned 579 Python files
- Found 461 actor behaviors
- Categorized by type:
  * 142 file write operations
  * 58 directory creation
  * 10 path write methods
  * 177 subprocess executions
  * 74 file object writes

### Manual Categorization into Batches

I took those 461 behaviors and organized them into 11 batches based on:

1. **Similarity** - Group similar behaviors together
2. **Complexity** - Easier batches first (file writes) before harder ones (Git ops)
3. **Size** - Keep batches to 8-15 behaviors for manageability
4. **Dependencies** - Refactor test file creation before test execution

---

## 🛠️ How to Add More Batches

### Step 1: Find the Behaviors

Look in the detection results:
```bash
cat COMPREHENSIVE_ACTOR_DETECTION_RESULTS_20251007.md | grep "Type 2: Directory"
```

### Step 2: Add to Configuration

Edit `tools/batch_refactoring_automation.py`:

```python
def _load_batch_configurations(self):
    return {
        1: BatchConfig(...),  # Already configured
        
        2: BatchConfig(       # ADD BATCH 2
            batch_number=2,
            batch_name="Test Directory Creation",
            behaviors=[
                BatchBehavior(
                    file_path="legacy/utilities/tdd_workflow_enforcer.py",
                    line_number=444,
                    current_behavior="test_dir.mkdir(parents=True)",
                    target_behavior="validate_test_directory(test_dir)",
                    description="Creates test directory"
                ),
                BatchBehavior(
                    file_path="legacy/utilities/tdd_workflow_engine.py",
                    line_number=199,
                    current_behavior="workspace.mkdir(parents=True)",
                    target_behavior="validate_workspace_structure(workspace)",
                    description="Creates workspace directory"
                ),
                # ... 6 more behaviors
            ],
            target_days="Day 3",
            estimated_hours=4.0
        ),
        
        # Batches 3-11...
    }
```

### Step 3: Run the Batch

```bash
python tools/batch_refactoring_automation.py --batch 2 --phase RED
```

The tool automatically generates the YAML from your configuration!

---

## 📊 Current Status

### ✅ Configured (Ready to Run)

**Batch 1 Only:**
- 10 behaviors fully configured
- YAML generation tested
- Test file generation logic implemented
- Documentation complete

### ⏳ Need Configuration (Batches 2-11)

**What's Missing:**
Each batch needs a `BatchConfig` entry with:
1. `batch_number` (2-11)
2. `batch_name` (descriptive name)
3. `behaviors` (list of BatchBehavior objects)
4. `target_days` (when to execute)
5. `estimated_hours` (time estimate)

**Where to Find Behaviors:**
1. Read `SYSTEMATIC_REFACTORING_PLAN.md` (lines 260-350)
2. Read `COMPREHENSIVE_ACTOR_DETECTION_RESULTS_20251007.md`
3. Search for specific file patterns:
   ```bash
   grep "Type 2: Directory" COMPREHENSIVE_ACTOR_DETECTION_RESULTS_20251007.md
   grep "Type 4A: Test Execution" COMPREHENSIVE_ACTOR_DETECTION_RESULTS_20251007.md
   ```

---

## 🎯 Configuration Template

### For Quick Copy-Paste

```python
# Add to _load_batch_configurations() in batch_refactoring_automation.py

BatchConfig(
    batch_number=X,
    batch_name="DESCRIPTIVE_NAME",
    behaviors=[
        BatchBehavior(
            file_path="path/to/file.py",
            line_number=123,
            current_behavior="original_code_pattern",
            target_behavior="new_validator_pattern",
            description="What this behavior does - why it needs refactoring",
            review_needed=False  # True if needs manual review
        ),
        # ... more behaviors
    ],
    target_days="Day X",
    estimated_hours=Y.0
),
```

---

## 🔄 Complete Flow

```
1. Detection Scan
   ↓
   461 behaviors found across 579 files
   ↓
2. Manual Organization
   ↓
   Grouped into 11 batches by type/complexity
   ↓
3. Hard-Code Configuration
   ↓
   BatchConfig objects in _load_batch_configurations()
   ↓
4. Run Automation Tool
   ↓
   Tool reads configuration for specified batch
   ↓
5. Generate YAML
   ↓
   _generate_yaml_spec() converts config to YAML
   ↓
6. Create Tests
   ↓
   _generate_test_file() creates Python tests
   ↓
7. Execute & Save
   ↓
   Runs tests, saves all outputs to correct locations
```

---

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `SYSTEMATIC_REFACTORING_PLAN.md` | Overall plan, 11 batches defined |
| `COMPREHENSIVE_ACTOR_DETECTION_RESULTS_20251007.md` | All 461 behaviors with line numbers |
| `tools/batch_refactoring_automation.py` | Main automation tool with configurations |
| `tools/batch_refactoring_automation.py:122` | `_load_batch_configurations()` method |

---

## ✅ Summary

### How Many Batches?
**11 batches** covering 461 actor behaviors

### How Does Script Know YAML Content?
**Hard-coded configurations** in `_load_batch_configurations()` method:
- You manually configure each batch with:
  * File path
  * Line number
  * Current behavior
  * Target behavior
  * Description
- Script converts configuration to YAML automatically

### What's Configured?
- **Batch 1:** ✅ Fully configured (10 behaviors)
- **Batches 2-11:** ⏳ Need to be added to configuration

### Next Steps
1. Review `SYSTEMATIC_REFACTORING_PLAN.md` for batch breakdowns
2. Add Batch 2 configuration to the tool
3. Run Batch 1 to test the automation
4. Gradually add remaining batches 3-11

---

**Last Updated:** October 8, 2025  
**Status:** Batch 1 ready, Batches 2-11 awaiting configuration ✅
