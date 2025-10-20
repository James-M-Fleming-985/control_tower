# Layer Requirements Template - Quick Start

## Copy Template to Your Layer

```bash
# Navigate to your layer directory
cd "/path/to/LAYER-XXX-YYY-ZZZ_LayerName/"

# Copy template
cp /workspaces/control_tower/templates/LAYER_REQUIREMENTS_TEMPLATE.yaml \
   ./REQ-XXX-YYY-ZZZ.yaml

# Open in editor
code ./REQ-XXX-YYY-ZZZ.yaml
```

## Minimum Required Edits

### 1. Metadata (Lines 19-32)
```yaml
metadata:
  requirement_id: "REQ-003-001-001"              # ← Update
  requirement_title: "YAML File Reader"          # ← Update
  layer: "LAYER-001_YAML_XML_Reader"             # ← Update
  feature: "FEATURE-003-001_Data_Reader_Parser"  # ← Update
  owner: "Your Name"                             # ← Update
  target_date: "2025-10-31"                      # ← Update
```

### 2. Requirement Description (Lines 39-52)
```yaml
requirement:
  title: "YAML File Reader"  # ← Update
  
  description: |
    [REPLACE: Explain what this layer does in 2-3 sentences]
  
  rationale: |
    [REPLACE: Explain why this layer exists and its value]
```

### 3. Specification - Classes (Lines 66-74)
```yaml
specification:
  classes:
    - name: "YAMLReader"  # ← Your class name
      purpose: "Read and parse YAML files"  # ← What it does
      methods:
        - name: "read_file"  # ← Your method
          signature: "read_file(path: Path) -> Dict[str, Any]"  # ← Full signature
          purpose: "Read YAML file and return as dictionary"  # ← What it does
```

### 4. Acceptance Criteria (Lines 98-107)
```yaml
acceptance_criteria:
  - criterion: "Reads valid YAML files without errors"  # ← Update
    test: "pytest tests/unit/test_yaml_reader.py::test_read_valid_yaml"  # ← Update
  
  - criterion: "[Add second criterion]"  # ← Add
    test: "[Add test command]"  # ← Add
```

### 5. TDD Steps (Lines 112-150)
```yaml
week_1_task:
  title: "Build YAML Reader (TDD Approach)"  # ← Update
  
  steps:
    - step: 1
      action: "Write failing unit tests (RED phase)"
      file: "tests/unit/test_yaml_reader.py"  # ← Update filename
      tests:
        - "test_read_valid_yaml"  # ← Add your test names
        - "test_handle_utf16_encoding"
        - "test_raise_error_invalid_yaml"
      duration: "20 min"
```

## Search & Replace Shortcuts

Use your editor's find/replace to update all placeholders:

| Find | Replace With | Example |
|------|-------------|---------|
| `[REQ-XXX-YYY-ZZZ]` | Your requirement ID | `REQ-003-001-001` |
| `[LAYER-XXX_YYY_LayerName]` | Your layer ID | `LAYER-001_YAML_XML_Reader` |
| `[FEATURE-XXX-YYY_FeatureName]` | Your feature ID | `FEATURE-003-001_Data_Reader_Parser` |
| `[module_name]` | Your module name | `yaml_reader` |
| `[ClassName]` | Your class name | `YAMLReader` |
| `[Your Name]` | Your name | `James Fleming` |

## Verify Your YAML

```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('REQ-XXX-YYY-ZZZ.yaml'))"

# Should print nothing if valid
# If error, fix the YAML syntax
```

## Run AI Code Generator

```bash
cd /workspaces/control_tower

# Generate code for your feature (which includes this layer)
python build_feature.py "/path/to/FEATURE-XXX-YYY_FeatureName.yaml"
```

## What Gets Generated

After running `build_feature.py`, you'll find:

```
LAYER-XXX-YYY-ZZZ_LayerName/
  REQ-XXX-YYY-ZZZ.yaml          ← Your requirements (input)
  src/
    __init__.py                 ← Generated
    [your_module].py            ← Generated implementation
  tests/
    __init__.py                 ← Generated
    test_[your_module].py       ← Generated tests
  Requirements Verification/    ← Traceability docs
  Testing Outputs/             ← Test results
```

## Example: PROJECT-002 Layer

See working example:
```
/workspaces/professional_excellence/projects/
  PROJECT-002 INDUSTRIALIZATION/
    FEATURE-002-001_Stage_Evidence_File_Recognition/
      LAYER-001_File_Detection/
        REQ-002-001-001.yaml  ← Complete working example
```

Compare your YAML to this example to ensure correct structure.

## Common Issues

### Issue: "Layer spec not found"
**Solution**: Ensure filename matches `requirement_file` in FEATURE.yaml

### Issue: "No requirement file specified"
**Solution**: Add `requirement_file: "REQ-XXX-YYY-ZZZ.yaml"` to FEATURE.yaml

### Issue: YAML syntax error
**Solution**: Check for proper indentation (use spaces, not tabs)

## Need More Details?

See full guide: `/workspaces/control_tower/templates/LAYER_REQUIREMENTS_TEMPLATE_GUIDE.md`

---
**Template Location**: `/workspaces/control_tower/templates/LAYER_REQUIREMENTS_TEMPLATE.yaml`
