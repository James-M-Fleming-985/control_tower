# Feature Requirements Template Guide

## Overview

This template is used to create **Feature Requirements Index** files that serve as the entry point for `build_feature.py` to generate complete features with all their layers using AI.

## File Naming Convention

```
FEATURE_REQUIREMENTS_INDEX.yaml
```

Place this file in your feature directory:
```
SYSTEM-XXX-XX SystemName/
  └── FEATURE-XXX-XXX_FeatureName/
      ├── FEATURE_REQUIREMENTS_INDEX.yaml  ← This file
      ├── LAYER-001 LayerName1/
      │   └── REQ-XXX-XXX-001.yaml
      ├── LAYER-002 LayerName2/
      │   └── REQ-XXX-XXX-002.yaml
      └── ...
```

## Critical Requirements for build_feature.py

### 1. Metadata Section

**MUST HAVE** these exact keys:
- `requirement_id`: The feature ID (e.g., "FEATURE-003-001")
- `requirement_name`: Human-readable feature name (e.g., "Data Reader Parser")

```yaml
metadata:
  requirement_id: "FEATURE-003-001"
  requirement_name: "Data Reader Parser"
  # ... other metadata fields
```

⚠️ **Common Mistake**: Using `feature_id` and `feature_name` instead of `requirement_id` and `requirement_name` will cause `build_feature.py` to fail.

### 2. Layers Array

Each layer entry **MUST HAVE**:
- `layer_id`: Short layer ID (e.g., "LAYER-001")
- `name`: Human-readable name with spaces (e.g., "File Detection")
- `requirement_file`: The YAML filename (e.g., "REQ-003-001-001.yaml")

```yaml
layers:
  - layer_id: "LAYER-001"
    name: "YAML XML Reader"
    requirement_file: "REQ-003-001-001.yaml"
    responsibility: "Reads and parses YAML/XML files"
    technology: "Python (pyyaml, xml.etree)"
    requirements:
      - REQ-003-001-001
```

### 3. Directory Structure Expected by build_feature.py

`build_feature.py` constructs paths like this:

```python
layer_dir = f"{layer_info['layer_id']} {layer_info['name']}"
layer_path = feature_path.parent / layer_dir / layer_file
```

So your directory structure **MUST BE**:

```
FEATURE-XXX-XXX_FeatureName/
  ├── FEATURE_REQUIREMENTS_INDEX.yaml
  ├── LAYER-001 YAML XML Reader/          ← Space, not underscore!
  │   └── REQ-XXX-XXX-001.yaml
  ├── LAYER-002 Data Model Validator/     ← Matches the 'name' field
  │   └── REQ-XXX-XXX-002.yaml
  └── LAYER-003 Schema Compliance Checker/
      └── REQ-XXX-XXX-003.yaml
```

⚠️ **Critical**: Directory names must be `LAYER-XXX LayerName` with **spaces**, not `LAYER-XXX_Layer_Name` with underscores.

## Section-by-Section Guide

### Metadata Section

```yaml
metadata:
  requirement_id: "FEATURE-003-002"      # Feature ID (REQUIRED by build_feature.py)
  requirement_name: "Risk Aggregator"    # Feature name (REQUIRED by build_feature.py)
  feature_code: "RISK_AGG"              # Short code for internal use
  version: "1.0.0"                       # Semantic version
  status: "Active"                       # Active, Deprecated, Planned
  created_date: "2025-10-17"            # YYYY-MM-DD
  last_modified: "2025-10-17"           # YYYY-MM-DD
  owner: "James Fleming"                # Person responsible
  priority: "MUST HAVE"                 # MUST HAVE, SHOULD HAVE, NICE TO HAVE
  target_date: "2025-10-31"             # Deadline
```

### Overview Section

Describes the feature at a high level:

```yaml
overview:
  description: |
    Multi-line description of what this feature does.
    Explain the problem it solves and how it fits into the system.
  
  business_value:
    - "Specific business benefit 1"
    - "Quantifiable benefit with metrics if possible"
    - "User impact or time savings"
  
  user_story: |
    As a [role],
    I want to [action],
    So that [benefit].
  
  acceptance_criteria:
    - "Measurable criterion 1"
    - "Testable criterion 2"
    - "Observable outcome 3"
```

### Layers Section

**This is the most important section for `build_feature.py`.**

```yaml
layers:
  - layer_id: "LAYER-001"                          # Short ID (REQUIRED)
    name: "Risk File Reader"                       # Name with spaces (REQUIRED)
    requirement_file: "REQ-003-002-001.yaml"      # Layer YAML filename (REQUIRED)
    responsibility: "Reads risks.yaml files from all project folders"
    technology: "Python (pyyaml library)"
    requirements:
      - REQ-003-002-001                            # Reference to layer requirement ID
```

The `name` field should match the directory name (with spaces).

### Requirements Section

Feature-level requirements that trace to project/system requirements:

```yaml
requirements:
  - id: "FEAT-REQ-001"
    title: "Risk Aggregation Core"
    description: "Implements complete risk aggregation with all layers"
    priority: "MUST HAVE"
    status: "Active"
    traces_to:
      project_requirements: ['PRJ-REQ-002']
      system_requirements: ['SYS-REQ-001', 'SYS-REQ-004']
      layer_requirements: ['REQ-003-002-001', 'REQ-003-002-002']
```

### Integration Section

```yaml
integration:
  upstream_features:
    - "FEATURE-003-001"  # Features this one depends on
  
  downstream_features:
    - "FEATURE-003-006"  # Features that depend on this one
  
  shared_components:
    - "src/shared/models"
    - "src/shared/exceptions"
```

### Testing Section

```yaml
testing:
  unit_tests:
    location: "tests/unit/"
    coverage_target: "90%"
  
  integration_tests:
    location: "tests/integration/"
    scenarios:
      - "Layer-to-layer data flow"
      - "Error handling and propagation"
  
  e2e_tests:
    location: "tests/e2e/"
    scenarios:
      - "Complete feature workflow end-to-end"
```

### Traceability Section

Maps feature to higher-level requirements and lower-level layers:

```yaml
traceability:
  implements_project_requirements:
    - PRJ-REQ-001
    - PRJ-REQ-002
  
  implements_system_requirements:
    - SYS-REQ-001
    - SYS-REQ-004
  
  distills_to_layers:
    - LAYER-001: REQ-003-002-001 (Risk File Reader)
    - LAYER-002: REQ-003-002-002 (Risk Filter Logic)
    - LAYER-003: REQ-003-002-003 (Risk Table Formatter)
```

## Usage with build_feature.py

Once you have created your FEATURE_REQUIREMENTS_INDEX.yaml:

```bash
cd /workspaces/control_tower

python build_feature.py \
  "/path/to/FEATURE-XXX-XXX_FeatureName/FEATURE_REQUIREMENTS_INDEX.yaml" \
  --provider anthropic \
  --verbose
```

The tool will:
1. Load the feature specification
2. For each layer in the `layers` array:
   - Find the layer requirement YAML in `LAYER-XXX LayerName/` directory
   - Generate code using AI Code Generator
   - Run TDD cycle (RED-GREEN-REFACTOR)
   - Create verification reports
3. Generate feature integration tests
4. Create E2E tests

## Common Pitfalls

### ❌ Wrong: Using underscores in directory names
```
LAYER-001_Risk_File_Reader/  # build_feature.py won't find this!
```

### ✅ Correct: Using spaces in directory names
```
LAYER-001 Risk File Reader/  # Matches the 'name' field
```

### ❌ Wrong: Using feature_id/feature_name in metadata
```yaml
metadata:
  feature_id: "FEATURE-003-001"    # Wrong key!
  feature_name: "Data Reader"      # Wrong key!
```

### ✅ Correct: Using requirement_id/requirement_name
```yaml
metadata:
  requirement_id: "FEATURE-003-001"   # Correct!
  requirement_name: "Data Reader"     # Correct!
```

### ❌ Wrong: Missing requirement_file in layer
```yaml
layers:
  - layer_id: "LAYER-001"
    name: "Risk File Reader"
    # Missing requirement_file! build_feature.py will fail
```

### ✅ Correct: All required fields present
```yaml
layers:
  - layer_id: "LAYER-001"
    name: "Risk File Reader"
    requirement_file: "REQ-003-002-001.yaml"  # Required!
```

## Complete Example

See `/workspaces/professional_excellence/projects/PROJECT-002 INDUSTRIALIZATION/FEATURE-002-001_Stage_Evidence_File_Recognition/FEATURE_REQUIREMENTS_INDEX.yaml` for a working example that has been successfully used with `build_feature.py`.

## Related Templates

- **Layer Requirements Template**: `/workspaces/control_tower/templates/LAYER_REQUIREMENTS_TEMPLATE.yaml`
- **Layer Template Guide**: `/workspaces/control_tower/templates/LAYER_REQUIREMENTS_TEMPLATE_GUIDE.md`
- **System Requirements Template**: Create system-level requirements for the SYSTEM-XXX folder
- **Project Requirements Template**: Create project-level requirements for the PROJECT-XXX folder

## Template Location

This template is saved in the control_tower repository so it can be used across all projects and repositories:

```
/workspaces/control_tower/templates/
  ├── FEATURE_REQUIREMENTS_TEMPLATE.yaml
  ├── FEATURE_REQUIREMENTS_TEMPLATE_GUIDE.md
  ├── LAYER_REQUIREMENTS_TEMPLATE.yaml
  └── LAYER_REQUIREMENTS_TEMPLATE_GUIDE.md
```

## Version History

- **v1.0.0** (2025-10-17): Initial template creation based on build_feature.py requirements and PROJECT-002 working examples
