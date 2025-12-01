# Requirements-Driven Development Process - MANDATORY FOR AI CODE GENERATION

## CRITICAL: This Process is NOT Optional

**Cost Impact**: Running the AI code generator without proper requirements costs:
- 10,000-50,000 tokens per layer generation attempt
- Multiple re-generations when requirements are unclear
- Developer time fixing generated code that doesn't meet needs

**Quality Impact**: Skipping requirements hierarchy leads to:
- Generated code that doesn't integrate properly
- Missing traceability (can't verify what requirement is being met)
- Inconsistent interfaces between layers
- Code that works standalone but fails in system integration

## Requirements Hierarchy (TOP-DOWN ONLY)

```
PROJECT Requirements (business goals)
    ↓ decomposed into
SYSTEM Requirements (technical systems)  
    ↓ decomposed into
FEATURE Requirements (user-facing capabilities)
    ↓ decomposed into
LAYER Requirements (implementation components)
    ↓ AI Code Generator produces
SOURCE CODE (Python, JavaScript, etc.)
```

**NEVER start at Layer level!** Always work top-down.

## Step-by-Step Process

### Step 1: Verify or Create PROJECT Requirements

**Location**: `/[project_name]/PROJECT_REQUIREMENTS.yaml`

**Check if exists**:
```bash
ls -la /workspaces/control_tower/systems3-project-reporter/PROJECT_REQUIREMENTS.yaml
```

**If missing**: Create from template:
```bash
cp /workspaces/control_tower/templates/PROJECT_REQUIREMENTS_TEMPLATE.yaml \
   /workspaces/control_tower/systems3-project-reporter/PROJECT_REQUIREMENTS.yaml
```

**Fill in**:
- Project business goals
- Success metrics  
- Stakeholders
- High-level capabilities needed

### Step 2: Verify or Create SYSTEM Requirements

**Location**: `/[project_name]/SYSTEM-XXX_[system_name]/SYSTEM-XXX.yaml`

**Check if exists**:
```bash
ls -la /workspaces/control_tower/systems3-project-reporter/SYSTEM-003_PowerPoint_Report_Generator/SYSTEM-003.yaml
```

**If missing**: Create from template:
```bash
cp /workspaces/control_tower/templates/SYSTEM_REQUIREMENTS_TEMPLATE.yaml \
   /workspaces/control_tower/systems3-project-reporter/SYSTEM-003_PowerPoint_Report_Generator/SYSTEM-003.yaml
```

**Fill in**:
- **traceability.parent_project_requirements**: Link to PROJECT requirements
- **shared_interfaces**: Define response structures ALL features must use
- System capabilities decomposed from project goals
- Deployment configuration

**CRITICAL**: Define `shared_interfaces.cli_response_structure` or `shared_interfaces.api_response_structure` here. ALL features MUST use this exact structure.

### Step 3: Create or Verify FEATURE Requirements

**Location**: `/[project_name]/FEATURE-XXX-YYY_[feature_name]/FEATURE-XXX-YYY.yaml`

**Check if exists**:
```bash
ls -la /workspaces/control_tower/systems3-project-reporter/FEATURE-WEB-006_PowerPoint_Export/FEATURE-WEB-006_PowerPoint_Report_Builder.yaml
```

**If missing**: Create from template:
```bash
cp /workspaces/control_tower/templates/FEATURE_REQUIREMENTS_TEMPLATE.yaml \
   /workspaces/control_tower/systems3-project-reporter/FEATURE-WEB-006_PowerPoint_Export/FEATURE-WEB-006_PowerPoint_Report_Builder.yaml
```

**Fill in**:
- **metadata.traceability.parent_system**: Link to SYSTEM
- **metadata.traceability.parent_system_requirements**: List which SYS-REQ-XXX this implements
- **shared_interfaces.response_structure**: COPY EXACT structure from parent SYSTEM
- User stories, acceptance criteria
- Feature capabilities

**CRITICAL**: The `shared_interfaces` section MUST match parent SYSTEM requirements EXACTLY. Copy-paste, don't paraphrase.

### Step 4: Generate LAYER Requirements (Automated)

**DO NOT manually create layer folders!** Use the automated tool:

```bash
cd /workspaces/control_tower
python build_feature.py --init-layers \
  systems3-project-reporter/FEATURE-WEB-006_PowerPoint_Export/FEATURE-WEB-006_PowerPoint_Report_Builder.yaml
```

**This automatically**:
- Creates LAYER folders with correct naming (LAYER_XXX_YYY_ZZZ_Name)
- Generates REQ-XXX-YYY-ZZZ.yaml files with traceability populated
- Links layers to parent feature requirements
- Creates proper folder structure for Python imports

**Then fill in each generated layer YAML**:
- **specification.classes**: Define classes and methods to implement
- **specification.implementation_details**: Libraries, patterns, error handling
- **testing.unit_tests**: List test cases
- **interfaces.public_methods**: Define public API
- **dependencies**: Internal and external dependencies

### Step 5: Generate Code with AI

**Only after Step 4 is complete!**

```bash
cd /workspaces/control_tower
python build_layer.py \
  "systems3-project-reporter/FEATURE-WEB-006_PowerPoint_Export/LAYER_XXX_YYY_ZZZ_LayerName/REQ-XXX-YYY-ZZZ.yaml"
```

**The AI reads**:
- Layer requirements (what to build)
- Parent feature requirements (why)
- Parent system requirements (interfaces to use)
- Traceability chain (context)

**The AI generates**:
- `src/implementation.py` - Production code
- `tests/test_*.py` - Unit tests
- Following the exact specifications in the YAML

## Common Mistakes That Cost Time and Money

### ❌ WRONG: Start coding without requirements
```
User: "Can you add canvas editor for PowerPoint slides?"
Agent: *writes code directly*
Result: Code doesn't integrate, missing requirements, no traceability
```

### ❌ WRONG: Skip straight to Layer requirements
```
Agent: *creates LAYER_PHASE2_001 without Feature/System requirements*
Result: AI generator produces generic code, doesn't understand context
```

### ❌ WRONG: Copy requirements but change structure
```yaml
# Parent SYSTEM says:
shared_interfaces:
  response_structure:
    fields:
      - name: "status"
        type: "ResponseStatus enum"

# Feature copies but "improves":
shared_interfaces:
  response_structure:
    fields:
      - name: "success"  # ❌ Changed field name!
        type: "bool"      # ❌ Changed type!
```
Result: Integration breaks, orchestrator can't read responses

### ✅ CORRECT: Follow the hierarchy
```
1. Check PROJECT requirements exist
2. Check SYSTEM requirements exist and define shared_interfaces
3. Create FEATURE requirements linking to SYSTEM
4. Run build_feature.py --init-layers to generate LAYER structure
5. Fill in LAYER specifications
6. Run build_layer.py to generate code
7. Code integrates perfectly, traceability complete
```

## Agent Checklist: Before Running AI Code Generator

- [ ] **PROJECT requirements exist** and define business goals
- [ ] **SYSTEM requirements exist** and define `shared_interfaces`
- [ ] **FEATURE requirements exist** and link to SYSTEM
- [ ] **FEATURE shared_interfaces** EXACTLY match SYSTEM (copy-paste verified)
- [ ] **LAYER folders auto-generated** via `build_feature.py --init-layers`
- [ ] **LAYER specifications complete**:
  - [ ] `specification.classes` with methods defined
  - [ ] `specification.implementation_details` with libraries
  - [ ] `testing.unit_tests` list populated
  - [ ] `interfaces.public_methods` defined
  - [ ] `dependencies` listed
- [ ] **Traceability verified**: Can trace layer → feature → system → project

## Quick Reference Commands

```bash
# Check if requirements exist
ls -la /workspaces/control_tower/systems3-project-reporter/PROJECT_REQUIREMENTS.yaml
ls -la /workspaces/control_tower/systems3-project-reporter/SYSTEM-*/SYSTEM-*.yaml
ls -la /workspaces/control_tower/systems3-project-reporter/FEATURE-*/FEATURE-*.yaml

# Create from templates
cp /workspaces/control_tower/templates/SYSTEM_REQUIREMENTS_TEMPLATE.yaml <destination>
cp /workspaces/control_tower/templates/FEATURE_REQUIREMENTS_TEMPLATE.yaml <destination>

# Generate layer structure
cd /workspaces/control_tower
python build_feature.py --init-layers <path_to_FEATURE_REQUIREMENTS.yaml>

# Generate code
cd /workspaces/control_tower
python build_layer.py "<path_to_REQ-XXX-YYY-ZZZ.yaml>"
```

## Cost Savings

**Following this process**:
- 1 AI generation attempt (5,000-10,000 tokens)
- Code works first time
- Clear traceability
- Easy maintenance

**Skipping this process**:
- 3-5 AI generation attempts (15,000-50,000 tokens)
- Manual fixes required
- Missing traceability
- Integration issues
- Technical debt

**Estimated savings**: 2-5x fewer tokens, 3-10x less developer time

## Integration with Deployment Process

This requirements process integrates with the Railway deployment checklist:

1. **Requirements Phase** (This document) - Define what to build
2. **Development Phase** - AI generates code from requirements
3. **Integration Phase** - Wire generated code into application
4. **Deployment Phase** - Follow `.github/AGENT_DEPLOYMENT_INSTRUCTIONS.md`

Both processes are mandatory for quality, cost-effective development.
