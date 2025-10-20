# Layer Requirements Template Usage Guide

## Overview
The `LAYER_REQUIREMENTS_TEMPLATE.yaml` is a standardized template for creating layer requirement specifications that can be processed by the AI Code Generator (`build_feature.py`).

## Quick Start

### 1. Copy the Template
```bash
# Copy template to your layer directory
cp /workspaces/control_tower/templates/LAYER_REQUIREMENTS_TEMPLATE.yaml \
   "/path/to/your/LAYER-XXX-YYY-ZZZ_LayerName/REQ-XXX-YYY-ZZZ.yaml"
```

### 2. Update Placeholders
Search for all `[PLACEHOLDER]` values and replace with your specific information:
- `[REQ-XXX-YYY-ZZZ]` → Your requirement ID (e.g., `REQ-003-001-001`)
- `[Brief Layer Title]` → Short descriptive title
- `[LAYER-XXX_YYY_LayerName]` → Your layer ID
- `[FEATURE-XXX-YYY_FeatureName]` → Parent feature ID
- `[module_name]` → Your Python module name
- `[ClassName]` → Your main class name

### 3. Fill in Specifications
Complete these critical sections:
- **requirement.description**: What this layer does
- **specification.classes**: Classes and methods to implement
- **acceptance_criteria**: How to verify it works
- **week_1_task.steps**: TDD implementation steps

### 4. Run AI Code Generator
```bash
cd /workspaces/control_tower
python build_feature.py "/path/to/your/FEATURE-XXX-YYY_FeatureName.yaml"
```

## Template Sections Explained

### Metadata Section
```yaml
metadata:
  requirement_id: "REQ-003-001-001"  # Unique identifier
  requirement_title: "YAML File Reader"
  layer: "LAYER-001_YAML_XML_Reader"
  feature: "FEATURE-003-001_Data_Reader_Parser"
  version: "1.0.0"
  status: "Active"
  priority: "MUST HAVE"
```

**Purpose**: Identifies and tracks this requirement uniquely.

**Key Fields**:
- `requirement_id`: Must match filename (e.g., `REQ-003-001-001.yaml`)
- `layer`: Must match layer directory name
- `feature`: Must match parent feature directory name
- `priority`: Use MoSCoW prioritization (MUST/SHOULD/COULD/WONT HAVE)

### Requirement Definition
```yaml
requirement:
  title: "YAML File Reader"
  description: |
    Reads YAML files from project folders, handles encoding issues,
    validates basic structure before parsing.
  rationale: |
    Centralized file reading logic with error handling enables
    other layers to work with structured data.
```

**Purpose**: Explains WHAT and WHY.

**Best Practices**:
- Keep description focused on behavior, not implementation
- Rationale should explain business value
- Use concrete examples when helpful

### Specification Section
```yaml
specification:
  structure:
    entry_point: "src/data_reader/yaml_reader.py"
    modules:
      - "yaml_reader.py"
      - "xml_reader.py"
  
  classes:
    - name: "YAMLReader"
      purpose: "Read and parse YAML files"
      methods:
        - name: "read_file"
          signature: "read_file(path: Path) -> Dict[str, Any]"
          purpose: "Read YAML file and return as dictionary"
```

**Purpose**: Technical blueprint for implementation.

**Critical Details**:
- `entry_point`: Main file to generate
- `classes.methods`: Complete method signatures
- `implementation_details.libraries`: Required packages
- `inputs/outputs`: Data contracts

### Acceptance Criteria
```yaml
acceptance_criteria:
  - criterion: "Reads valid YAML files without errors"
    test: "pytest tests/unit/test_yaml_reader.py::test_read_valid_yaml"
  
  - criterion: "Handles UTF-8 and UTF-16 encoding"
    test: "Upload UTF-16 file, verify correct parsing"
  
  - criterion: "Raises YAMLError for malformed files"
    test: "Pass invalid YAML, verify exception raised"
```

**Purpose**: Defines "done" for this layer.

**Best Practices**:
- Each criterion should be testable
- Include both positive and negative test cases
- Specify performance criteria if relevant

### TDD Implementation Plan
```yaml
week_1_task:
  title: "Build YAML Reader (TDD Approach)"
  steps:
    - step: 1
      action: "Write failing unit tests (RED phase)"
      file: "tests/unit/test_yaml_reader.py"
      tests:
        - "test_read_valid_yaml"
        - "test_read_utf16_encoded_file"
        - "test_raise_error_on_invalid_yaml"
      duration: "20 min"
    
    - step: 2
      action: "Run pytest to confirm RED phase"
      command: "pytest tests/unit/test_yaml_reader.py -v"
      expected: "All tests FAIL (as expected)"
      duration: "2 min"
```

**Purpose**: Step-by-step TDD implementation guide.

**What build_feature.py Uses**:
- Uses this to generate test files first (RED phase)
- Then generates implementation (GREEN phase)
- Validates against acceptance criteria

## Example: Real Layer Requirements

See working example:
```
/workspaces/professional_excellence/projects/PROJECT-002 INDUSTRIALIZATION/
  FEATURE-002-001_Stage_Evidence_File_Recognition/
    LAYER-001_File_Detection/
      REQ-002-001-001.yaml  ← Complete working example
```

## Naming Conventions

### File Naming
```
REQ-[PROJECT]-[FEATURE]-[LAYER].yaml

Examples:
- REQ-002-001-001.yaml  (Project 002, Feature 001, Layer 001)
- REQ-003-002-003.yaml  (Project 003, Feature 002, Layer 003)
```

### Directory Structure
```
FEATURE-XXX-YYY_FeatureName/
  LAYER-XXX-YYY-ZZZ_LayerName/
    REQ-XXX-YYY-ZZZ.yaml          ← Requirements file
    src/                           ← Generated implementation
    tests/                         ← Generated tests
    Requirements Verification/     ← Traceability docs
    Testing Outputs/              ← Test results
```

## What build_feature.py Expects

The AI Code Generator reads these specific fields:

### Required Fields
```yaml
metadata:
  requirement_id: "..."           # ✓ Must be present
  layer: "..."                    # ✓ Must match directory
  feature: "..."                  # ✓ Must match parent feature

specification:
  classes:                        # ✓ Used to generate code
    - name: "..."
      methods: [...]
  
  inputs: [...]                   # ✓ Used for interface definition
  outputs: [...]                  # ✓ Used for interface definition

acceptance_criteria: [...]        # ✓ Used for test generation

week_1_task:
  steps: [...]                    # ✓ Used for TDD workflow
```

### Optional but Recommended
```yaml
requirement:
  description: "..."              # Used in AI prompts for context
  rationale: "..."                # Helps AI understand intent

integration:
  input_from: [...]               # Used for layer orchestration
  output_to: [...]                # Used for feature integration

testing_strategy:
  unit_tests: {...}               # Guides test generation
  fixtures: {...}                 # Generates test data
```

## Common Mistakes

### ❌ Don't Do This
```yaml
# Vague description
description: "This layer processes data"

# Missing method signatures
methods:
  - "do_something"  # ❌ No types

# Untestable criterion
acceptance_criteria:
  - criterion: "Works correctly"  # ❌ How to verify?
```

### ✅ Do This
```yaml
# Specific description
description: |
  Reads YAML files from P:\Projects\, parses into Python dicts,
  validates schema using Pydantic models, raises FileNotFoundError
  if file missing, raises YAMLError if malformed.

# Complete method signatures
methods:
  - name: "read_file"
    signature: "read_file(path: Path) -> Dict[str, Any]"

# Testable criterion
acceptance_criteria:
  - criterion: "Reads valid YAML files without errors"
    test: "pytest tests/unit/test_yaml_reader.py::test_read_valid_yaml -v"
```

## Integration with build_feature.py

### Workflow
1. **Create FEATURE.yaml** referencing layer requirements
2. **Create LAYER requirements** using this template
3. **Run build_feature.py** to generate code
4. **AI reads layer YAML** to understand what to build
5. **Generated code appears** in `LAYER/src/` and `LAYER/tests/`

### Example Feature YAML
```yaml
feature_id: "FEATURE-003-001"
name: "Data Reader and Parser"

layers:
  - layer_id: "LAYER-001"
    name: "YAML XML Reader"
    requirement_file: "REQ-003-001-001.yaml"  # ← Points to this template
  
  - layer_id: "LAYER-002"
    name: "Data Model Validator"
    requirement_file: "REQ-003-001-002.yaml"
```

## Customization Tips

### For Simple Layers
Minimum required sections:
- metadata
- requirement (description)
- specification (classes with methods)
- acceptance_criteria (at least 3)
- week_1_task (RED/GREEN/REFACTOR steps)

### For Complex Layers
Add these sections:
- integration (detailed input/output contracts)
- testing_strategy (comprehensive test plan)
- deployment (configuration requirements)
- notes (design decisions, gotchas)

## Quick Reference Commands

```bash
# Copy template
cp /workspaces/control_tower/templates/LAYER_REQUIREMENTS_TEMPLATE.yaml \
   "./LAYER-001_MyLayer/REQ-001-001-001.yaml"

# Edit requirement
code "./LAYER-001_MyLayer/REQ-001-001-001.yaml"

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('REQ-001-001-001.yaml'))"

# Run AI Code Generator
python /workspaces/control_tower/build_feature.py "./FEATURE-001_MyFeature.yaml"

# Verify generated code
pytest LAYER-001_MyLayer/tests/ -v
```

## Support

**Template Location**: `/workspaces/control_tower/templates/LAYER_REQUIREMENTS_TEMPLATE.yaml`

**Example Requirements**: 
- `/workspaces/professional_excellence/projects/PROJECT-002 INDUSTRIALIZATION/`

**AI Code Generator**: `/workspaces/control_tower/build_feature.py`

---
**Last Updated**: October 16, 2025
