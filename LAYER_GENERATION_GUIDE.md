# Layer Generation Guide - build_feature.py --init-layers

**Date:** October 20, 2025  
**Status:** ✅ Feature Available in build_feature.py

---

## ✅ Yes! The Functionality Exists

The `build_feature.py` tool **already includes** the `--init-layers` command that:

1. ✅ Reads FEATURE_REQUIREMENTS_INDEX.yaml
2. ✅ Creates standardized layer folders (with underscores for Python imports)
3. ✅ Uses AI to derive layer requirements from feature requirements
4. ✅ Generates complete layer YAML files
5. ✅ Creates src/ and tests/ subdirectories
6. ✅ Maintains full traceability

---

## 🚀 How to Use It

### Basic Command

```bash
python3 build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml
```

### With Options

```bash
# Use Anthropic (default, recommended)
python3 build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml \
  --provider anthropic \
  --verbose

# Use OpenAI instead
python3 build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml \
  --provider openai \
  --verbose
```

---

## 📋 What It Does Step-by-Step

### Input: FEATURE_REQUIREMENTS_INDEX.yaml
```yaml
layers:
  - layer_id: LAYER-002-001-001
    name: Hero Section Component
    # ... layer definition
  - layer_id: LAYER-002-001-002
    name: Calculator Landing Pages
    # ... layer definition
```

### Process:

1. **Reads Feature Requirements**
   - Loads FEATURE_REQUIREMENTS_INDEX.yaml
   - Extracts all layer definitions
   - Validates structure

2. **Creates Folder Structure**
   ```
   FEATURE-002-001_Landing_Marketing_Pages/
   ├── LAYER_002_001_001_Hero_Section_Component/
   │   ├── src/
   │   ├── tests/
   │   └── LAYER_002_001_001_Hero_Section_Component.yaml
   ├── LAYER_002_001_002_Calculator_Landing_Pages/
   │   ├── src/
   │   ├── tests/
   │   └── LAYER_002_001_002_Calculator_Landing_Pages.yaml
   ```

3. **AI Derives Layer Requirements**
   - Reads LAYER_REQUIREMENTS_TEMPLATE.yaml
   - Analyzes feature requirements
   - Uses AI to decompose into layer-specific requirements
   - Maps traceability (feature req → layer req)
   - Generates complete YAML for each layer

4. **Writes Layer YAML Files**
   - Each layer gets its own detailed requirements file
   - Includes metadata, requirements, interfaces, acceptance criteria
   - Ready for build_feature.py to build from

### Output:

```
================================================================================
  Layer 1/4: Hero Section Component
================================================================================

📁 Creating folder: LAYER_002_001_001_Hero_Section_Component
   ✓ Created: LAYER_002_001_001_Hero_Section_Component/src/
   ✓ Created: LAYER_002_001_001_Hero_Section_Component/tests/

🤖 Deriving layer requirements from feature requirements...
   ✓ Generated: LAYER_002_001_001_Hero_Section_Component.yaml
   ✓ Layer initialized successfully
```

---

## 💡 Real Example for SYSTEM-002

### For Landing Pages Feature

```bash
cd /workspaces/control_tower/cloned_repos/life_quality/projects/PROJECT-001\ HEALTH_FITNESS_TRACKER/SYSTEM-002_FitTrack_Frontend/FEATURE-002-001_Landing_Marketing_Pages

python3 /workspaces/control_tower/build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml --verbose
```

### Expected Result:

```
✓ Loaded feature: FEATURE-002-001 - Landing & Marketing Pages
✓ Found 4 layers to initialize

Layer 1/4: Hero Section Component
  → Creates LAYER_002_001_001_Hero_Section_Component/
  → Generates LAYER_002_001_001_Hero_Section_Component.yaml

Layer 2/4: Calculator Landing Pages
  → Creates LAYER_002_001_002_Calculator_Landing_Pages/
  → Generates LAYER_002_001_002_Calculator_Landing_Pages.yaml

Layer 3/4: Pricing & About Pages
  → Creates LAYER_002_001_003_Pricing_About_Pages/
  → Generates LAYER_002_001_003_Pricing_About_Pages.yaml

Layer 4/4: SEO & Performance Optimization
  → Creates LAYER_002_001_004_SEO_Performance_Optimization/
  → Generates LAYER_002_001_004_SEO_Performance_Optimization.yaml

✅ All 4 layers initialized successfully!

Next steps:
  1. Review generated layer YAML files
  2. Adjust requirements if needed
  3. Run: python build_feature.py FEATURE_REQUIREMENTS_INDEX.yaml
```

---

## 🎯 For All 5 Features in SYSTEM-002

### Script to Generate All Layers

```bash
#!/bin/bash
# Generate all layer requirements for SYSTEM-002

cd /workspaces/control_tower/cloned_repos/life_quality/projects/PROJECT-001\ HEALTH_FITNESS_TRACKER/SYSTEM-002_FitTrack_Frontend

echo "Generating layers for all 5 features..."

# Feature 1: Landing Pages
cd FEATURE-002-001_Landing_Marketing_Pages
python3 /workspaces/control_tower/build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml --verbose
cd ..

# Feature 2: Authentication
cd FEATURE-002-002_Authentication_Flow
python3 /workspaces/control_tower/build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml --verbose
cd ..

# Feature 3: Calculator Interfaces
cd FEATURE-002-003_Calculator_Interfaces
python3 /workspaces/control_tower/build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml --verbose
cd ..

# Feature 4: User Dashboard
cd FEATURE-002-004_User_Dashboard
python3 /workspaces/control_tower/build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml --verbose
cd ..

# Feature 5: Subscription Checkout
cd FEATURE-002-005_Subscription_Checkout
python3 /workspaces/control_tower/build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml --verbose
cd ..

echo "✅ All layer requirements generated!"
```

### Time Estimate

- **Per feature:** ~2-3 minutes (4 layers × 30-45 seconds each)
- **All 5 features:** ~10-15 minutes total
- **AI tokens:** ~20K-30K tokens (uses Claude or GPT-4)

---

## 🔍 What the AI-Generated Layer YAML Contains

Each layer YAML will have:

### 1. Metadata
```yaml
metadata:
  requirement_id: REQ-002-001-001
  requirement_name: Hero Section Component
  layer_id: LAYER-002-001-001
  layer_folder: LAYER_002_001_001_Hero_Section_Component  # ✅ CRITICAL!
  feature_id: FEATURE-002-001
  system_id: SYSTEM-002
  project_id: PROJECT-001
```

### 2. Requirements
```yaml
requirements:
  functional:
    - requirement_id: FR-002-001-001-001
      title: Responsive hero component
      description: Hero section adapts to all screen sizes...
  non_functional:
    - requirement_id: NFR-002-001-001-001
      title: Performance
      description: Initial render < 1 second
```

### 3. Interfaces
```yaml
interfaces:
  input:
    - name: hero_data
      type: HeroContent
      description: Content for hero section
  output:
    - name: HeroSection
      type: React Component
      description: Rendered hero component
```

### 4. Traceability
```yaml
traceability:
  derived_from_feature_requirements:
    - feature_req_id: FR-002-001-001
      layer_req_id: FR-002-001-001-001
      mapping_explanation: Landing page hero decomposed to component level
```

### 5. Acceptance Criteria
```yaml
acceptance_criteria:
  - criterion_id: AC-002-001-001-001
    description: Hero displays correctly on mobile, tablet, desktop
    verification_method: Visual regression testing
```

---

## ✅ Why This Approach Works

### Benefits:

1. **AI-Powered Requirements Decomposition**
   - Feature requirements → Layer requirements
   - Maintains context and traceability
   - Consistent format

2. **Standardized Folder Names**
   - Python-compatible (underscores not hyphens)
   - Predictable structure
   - Easy imports later

3. **Ready for Build**
   - After init-layers, run `build_feature.py` normally
   - AI has detailed layer specs to generate code from
   - Full traceability maintained

4. **Time Saver**
   - Manual YAML writing: ~30 min per layer = 10 hours for 20 layers
   - AI generation: ~30 seconds per layer = 10 minutes for 20 layers
   - **60x faster!**

---

## 🎯 Recommended Next Steps

### Option 1: Generate All Layers Now (Recommended for Complete Docs)

```bash
# Generate all 20 layer YAMLs (5 features × 4 layers each)
# Time: ~15 minutes total

cd /workspaces/control_tower/cloned_repos/life_quality/projects/PROJECT-001\ HEALTH_FITNESS_TRACKER/SYSTEM-002_FitTrack_Frontend

for feature in FEATURE-002-00{1..5}_*/; do
  cd "$feature"
  python3 /workspaces/control_tower/build_feature.py \
    --init-layers FEATURE_REQUIREMENTS_INDEX.yaml \
    --verbose
  cd ..
done
```

### Option 2: Generate Landing Page Layers Only (Recommended for Fast Start)

```bash
# Generate just Feature 001 layers (4 layers)
# Time: ~3 minutes

cd FEATURE-002-001_Landing_Marketing_Pages
python3 /workspaces/control_tower/build_feature.py \
  --init-layers FEATURE_REQUIREMENTS_INDEX.yaml \
  --verbose
```

Then start building the Next.js app!

### Option 3: Skip Layer Generation, Build Directly

Just create the Next.js project and start coding without layer YAMLs. Less documentation, faster start, but less traceability.

---

## 📊 Comparison Table

| Approach | Time | Documentation | Traceability | Recommended For |
|----------|------|---------------|--------------|-----------------|
| **Generate All Layers** | 15 min | Complete | Full | Large teams, compliance needs |
| **Generate Feature 1 Only** | 3 min | Partial | Good | Solo dev, iterative approach ⭐ |
| **Skip Layer Generation** | 0 min | Minimal | Limited | Prototypes, throwaway code |

---

## 🎬 Ready to Execute?

**Just tell me which option you want:**

**A.** Generate all 20 layer YAMLs now (15 minutes)  
**B.** Generate Feature 001 layers only (3 minutes) ⭐ **RECOMMENDED**  
**C.** Skip layer generation, start Next.js project  

I'll run the commands for you! 🚀

