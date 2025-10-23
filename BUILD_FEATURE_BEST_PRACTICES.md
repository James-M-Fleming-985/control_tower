# Build Feature Best Practices - Two-Step vs One-Step

**Date:** October 20, 2025

---

## 🎯 Answer: Yes, Two Steps IS the Best Practice

The two-step process is **intentionally designed** this way and is the **recommended approach**.

---

## 📋 The Two-Step Process (RECOMMENDED)

### Step 1: `--init-layers` (Requirements Derivation)
```bash
python3 build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml --verbose
```

**What it does:**
- Uses AI to decompose feature requirements → layer requirements
- Creates layer folders with correct naming
- Generates detailed layer YAML specifications
- Creates empty src/ and tests/ directories

**Why this step exists:**
- Allows you to **review and edit** layer requirements before building
- Separates requirements phase from implementation phase
- Gives you a chance to **catch issues early**
- Lets you **adjust AI-generated requirements** before expensive code generation

### Step 2: Build Feature (Code Generation)
```bash
python3 build_feature.py FEATURE_REQUIREMENTS_INDEX.yaml --verbose
```

**What it does:**
- Reads the layer YAML specifications
- Generates implementation code for each layer
- Creates test files
- Runs TDD cycle
- Generates verification reports

**Why this step is separate:**
- Code generation is **expensive** (time + API costs)
- You might want to **manually write code** instead of generating
- You can **regenerate code** without redoing requirements
- Allows **iterative refinement** of implementation

---

## 🔄 The Workflow in Practice

### Best Practice Flow

```bash
# 1. Create feature requirements (manual)
vim FEATURE_REQUIREMENTS_INDEX.yaml

# 2. Generate layer requirements (AI-assisted)
python3 build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml

# 3. REVIEW & EDIT layer YAMLs (important!)
vim LAYER_002_001_001_Homepage_Hero_Section/LAYER_*.yaml
# Check: Are requirements correct?
# Check: Are interfaces well-defined?
# Check: Are acceptance criteria clear?

# 4. Build implementation (AI-generated code)
python3 build_feature.py FEATURE_REQUIREMENTS_INDEX.yaml

# 5. Review generated code, adjust, iterate
```

---

## ✅ Why Two Steps is Better

### Advantages of Separation

**1. Cost Efficiency**
- Requirements generation: ~30 seconds per layer, ~1K tokens
- Code generation: ~5 minutes per layer, ~10K+ tokens
- If requirements are wrong, you only redo step 1 (cheap!)

**2. Quality Control**
- Human review between requirements and implementation
- Catch architectural issues early
- Adjust layer interfaces before generating code
- Ensure traceability is correct

**3. Flexibility**
- Can skip code generation and write manually
- Can use different AI models for each step
- Can regenerate code without changing requirements
- Can version control requirements separately

**4. Team Collaboration**
- Senior dev reviews layer requirements
- Junior dev generates/reviews code
- Requirements become documentation
- Clear handoff points

**5. Iterative Development**
- Generate requirements once
- Regenerate code multiple times
- Adjust implementation without changing requirements
- Test different code generation prompts

---

## ❌ One-Step Process (NOT RECOMMENDED)

### Hypothetical: If you could do it in one step

```bash
# If there was a --build-all flag (there isn't)
python3 build_feature.py --build-all FEATURE_REQUIREMENTS_INDEX.yaml
```

**Problems:**
- ❌ No chance to review layer requirements
- ❌ If AI misunderstands feature, wastes time/money generating wrong code
- ❌ Can't catch interface issues before implementation
- ❌ No human-in-the-loop quality gate
- ❌ Harder to debug (was it requirements or implementation?)
- ❌ Can't use manual code writing workflow

---

## 📊 Comparison Table

| Aspect | Two-Step | One-Step |
|--------|----------|----------|
| **Review Opportunity** | ✅ Yes, between steps | ❌ No |
| **Cost if Wrong** | 💰 Cheap (redo step 1) | 💰💰💰 Expensive (redo all) |
| **Flexibility** | ✅ High | ❌ Low |
| **Quality Control** | ✅ Human gate | ❌ No gate |
| **Manual Override** | ✅ Easy | ❌ Hard |
| **Version Control** | ✅ Separate commits | ❌ One big commit |
| **Team Workflow** | ✅ Clear handoff | ❌ All-or-nothing |
| **Speed** | ⚠️ Slower total | ✅ Faster (but risky) |

---

## 🎓 Real-World Example

### Scenario: Building a React component

**Two-Step Approach:**
```bash
# Step 1: Generate layer requirements
python3 build_feature.py --init-layers FEATURE_REQUIREMENTS_INDEX.yaml

# Review: Oh, the AI thinks we need 5 props, but we only need 3
vim LAYER_002_001_001_Homepage_Hero_Section/LAYER_*.yaml
# Edit: Remove 2 unnecessary props

# Step 2: Generate code with corrected requirements
python3 build_feature.py FEATURE_REQUIREMENTS_INDEX.yaml
# Result: Clean component with 3 props ✅

Total time: 2 min + 5 min = 7 minutes
Total cost: 1K + 10K = 11K tokens
```

**One-Step Approach (if it existed):**
```bash
# One step: Generate everything
python3 build_feature.py --build-all FEATURE_REQUIREMENTS_INDEX.yaml

# Oh no, the component has 5 props instead of 3!
# Have to regenerate everything

Total time: 7 min + 7 min (regenerate) = 14 minutes
Total cost: 11K + 11K = 22K tokens
```

---

## 🏗️ Architecture Pattern

The two-step process follows **separation of concerns**:

```
Feature Requirements (WHAT)
    ↓ (AI Derivation - Step 1)
Layer Requirements (HOW - Abstract)
    ↓ (Human Review - Quality Gate)
Layer Requirements (HOW - Validated)
    ↓ (AI Generation - Step 2)
Implementation Code (HOW - Concrete)
```

This is similar to:
- **Architecture → Design → Implementation** (software engineering)
- **Requirements → Specs → Code** (waterfall, but faster)
- **Stories → Tasks → Code** (agile, but AI-assisted)

---

## 💡 When to Skip Step 1

You might skip `--init-layers` if:

1. **You manually write layer YAMLs**
   - You're an expert and know exactly what you want
   - You have a template to copy from
   - Requirements are very simple

2. **You're iterating on existing code**
   - Layer YAMLs already exist
   - Just regenerating implementation
   - Tweaking code generation prompts

3. **You're prototyping**
   - Exploring ideas quickly
   - Don't care about requirements documentation
   - Will throw away and rewrite properly later

But even then, **most teams should use both steps** for production code.

---

## 🎯 Best Practice Checklist

When building a new feature:

- [ ] Create FEATURE_REQUIREMENTS_INDEX.yaml (manual)
- [ ] Run `--init-layers` to generate layer YAMLs
- [ ] **Review all layer YAMLs** (don't skip!)
- [ ] Edit layer YAMLs if needed
- [ ] Commit layer YAMLs to git
- [ ] Run build to generate implementation
- [ ] Review generated code
- [ ] Run tests
- [ ] Commit implementation to git

**Key Point:** The **review after step 1** is the most important part!

---

## 📚 See Also

- `BUILD_FEATURE_TWO_STEP_PROCESS.md` - Detailed technical explanation
- `LAYER_GENERATION_GUIDE.md` - How to use --init-layers
- Feature Builder documentation in `build_feature.py` docstrings

---

## 🎬 Summary

**Question:** Is two-step the best practice?

**Answer:** **YES!** 

The two-step process is:
- ✅ Intentionally designed this way
- ✅ Recommended for all production code
- ✅ More efficient despite seeming slower
- ✅ Higher quality output
- ✅ Better team workflow
- ✅ Lower total cost

**Bottom line:** Use both steps. Review between them. You'll save time and money in the long run.

