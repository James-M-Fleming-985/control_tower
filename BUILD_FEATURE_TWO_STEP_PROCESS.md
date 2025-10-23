# build_feature.py - Two-Step Process Explained

**Date:** October 20, 2025

---

## ✅ Understanding the Two Steps

### Step 1: `--init-layers` (PREPARATION ONLY)
**What it does:**
- Reads `FEATURE_REQUIREMENTS_INDEX.yaml`
- Creates layer folders (e.g., `LAYER_002_001_001_Homepage_Hero_Section/`)
- Uses AI to derive layer requirements from feature requirements
- Generates layer YAML files (e.g., `LAYER_002_001_001_Homepage_Hero_Section.yaml`)
- Creates empty `src/` and `tests/` subdirectories

**What it does NOT do:**
- ❌ Does NOT generate implementation code
- ❌ Does NOT create Python/TypeScript files
- ❌ Does NOT create test files
- ❌ Does NOT build the feature

**Command:**
```bash
python3 build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml
```

**Output:**
```
FEATURE-002-001_Landing_Marketing_Pages/
├── LAYER_002_001_001_Homepage_Hero_Section/
│   ├── src/                                    # EMPTY!
│   ├── tests/                                  # EMPTY!
│   └── LAYER_002_001_001_Homepage_Hero_Section.yaml  # ✅ Created
```

---

### Step 2: Build Feature (ACTUAL BUILD)
**What it does:**
- Reads `FEATURE_REQUIREMENTS_INDEX.yaml`
- Finds all layer YAML files
- For each layer:
  - Uses AI to generate implementation code
  - Creates Python/TypeScript/React files in `src/`
  - Generates test files in `tests/`
  - Creates layer integration code
- Creates feature-level integration
- Generates verification artifacts

**Command:**
```bash
python3 build_feature.py FEATURE_REQUIREMENTS_INDEX.yaml
```

**Output:**
```
FEATURE-002-001_Landing_Marketing_Pages/
├── LAYER_002_001_001_Homepage_Hero_Section/
│   ├── src/
│   │   ├── HeroSection.tsx                    # ✅ Generated!
│   │   ├── HeroContent.ts                     # ✅ Generated!
│   │   └── index.ts                           # ✅ Generated!
│   ├── tests/
│   │   ├── HeroSection.test.tsx               # ✅ Generated!
│   │   └── HeroContent.test.ts                # ✅ Generated!
│   └── LAYER_002_001_001_Homepage_Hero_Section.yaml
├── feature_integration.py                     # ✅ Generated!
└── feature_verification.json                  # ✅ Generated!
```

---

## 🔄 Complete Workflow

### Full Process from Scratch

```bash
# 1. Navigate to feature folder
cd FEATURE-002-001_Landing_Marketing_Pages

# 2. OPTIONAL: Initialize layer structure (if not already done)
python3 /workspaces/control_tower/build_feature.py \
  --init-layers FEATURE_REQUIREMENTS_INDEX.yaml \
  --verbose

# 3. REQUIRED: Build the actual feature implementation
python3 /workspaces/control_tower/build_feature.py \
  FEATURE_REQUIREMENTS_INDEX.yaml \
  --verbose
```

### If You Already Ran `--init-layers`

```bash
# You're already in step 2! Just run:
python3 /workspaces/control_tower/build_feature.py \
  FEATURE_REQUIREMENTS_INDEX.yaml \
  --verbose
```

---

## 📋 What We Have Now

### Current State (After `--init-layers`)

```
FEATURE-002-001_Landing_Marketing_Pages/
├── FEATURE_REQUIREMENTS_INDEX.yaml            ✅ Exists
├── LAYER_002_001_001_Homepage_Hero_Section/
│   ├── src/                                   ⚠️ EMPTY
│   ├── tests/                                 ⚠️ EMPTY
│   └── LAYER_002_001_001_Homepage_Hero_Section.yaml  ✅ Exists
├── LAYER_002_001_002_Calculator_Landing_Pages/
│   ├── src/                                   ⚠️ EMPTY
│   ├── tests/                                 ⚠️ EMPTY
│   └── LAYER_002_001_002_Calculator_Landing_Pages.yaml  ✅ Exists
├── LAYER_002_001_003_Pricing_Page/
│   ├── src/                                   ⚠️ EMPTY
│   ├── tests/                                 ⚠️ EMPTY
│   └── LAYER_002_001_003_Pricing_Page.yaml   ✅ Exists
└── LAYER_002_001_004_SEO_Meta_Tags_&_Schema/
    ├── src/                                   ⚠️ EMPTY
    ├── tests/                                 ⚠️ EMPTY
    └── LAYER_002_001_004_SEO_Meta_Tags_&_Schema.yaml  ✅ Exists
```

**Status:** 
- ✅ Structure prepared
- ✅ Requirements defined
- ❌ **Code NOT generated yet**

---

## 🚀 Next Step: Run the Actual Build

To generate the implementation code:

```bash
cd /workspaces/control_tower/cloned_repos/life_quality/projects/PROJECT-001\ HEALTH_FITNESS_TRACKER/SYSTEM-002_FitTrack_Frontend/FEATURE-002-001_Landing_Marketing_Pages

python3 /workspaces/control_tower/build_feature.py \
  FEATURE_REQUIREMENTS_INDEX.yaml \
  --verbose
```

This will:
1. Read all 4 layer YAML files
2. Generate React/TypeScript components for each layer
3. Generate test files
4. Create feature integration code
5. Generate verification artifacts

**Estimated time:** 10-20 minutes (4 layers × 2-5 min per layer)

---

## ❓ Why Two Steps?

### Design Philosophy

**Step 1 (`--init-layers`)** - Requirements Derivation
- Separates requirements analysis from implementation
- Lets you review/edit layer requirements before building
- Faster iteration on requirements
- Can be done once and committed to git

**Step 2 (build)** - Code Generation
- Generates actual implementation
- Takes longer (AI generates code)
- Can be re-run to regenerate code if needed
- Implementation based on finalized requirements

### Benefits

1. **Review Requirements First**
   - Check layer YAML files before building
   - Adjust requirements if needed
   - Catch issues early

2. **Faster Iteration**
   - Don't regenerate requirements every time
   - Only regenerate code when needed

3. **Version Control**
   - Commit requirements separately from code
   - Track requirement changes vs implementation changes

4. **Flexibility**
   - Can manually write code instead of generating
   - Can use different AI models for different steps
   - Can skip AI generation and use as templates

---

## 🎯 Summary

| Command | Purpose | Creates | Time |
|---------|---------|---------|------|
| `--init-layers` | Requirements prep | YAML files, empty folders | 2-5 min |
| `build_feature.py` | Code generation | Implementation files, tests | 10-20 min |

**Current Status:**
- ✅ Step 1 complete (requirements defined)
- ⏳ Step 2 pending (code not generated)

**To proceed:** Run `build_feature.py FEATURE_REQUIREMENTS_INDEX.yaml --verbose`

---

## 💡 Important Note

The `--init-layers` step is **OPTIONAL**. You can:
- Skip it and manually write layer YAML files
- Skip it and the build will fail (needs layer YAMLs)
- Use it to auto-generate layer YAMLs from feature requirements

But once you have layer YAML files (however they were created), you **MUST** run the main `build_feature.py` command to generate implementation code.

