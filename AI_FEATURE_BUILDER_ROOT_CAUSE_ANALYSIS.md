# AI Feature Builder — Root Cause Analysis & Corrective Action Plan

**Date:** February 13, 2026  
**Project:** Causal Affect (SYSTEM-CA-002 Correlation Analysis)  
**Pipeline:** AI Feature Builder (GitHub Actions → build_feature.py → Railway)  
**Status:** Post-Incident Review — 5 Root Causes Identified, 5 Corrective Actions Proposed

---

## 1. Executive Summary

The AI Feature Builder was intended as a "fire and forget" pipeline: dispatch a GitHub Actions workflow → build 3 features via AI code generation → test → integrate into production app → commit → push → Railway auto-deploys. This did not happen. Out of 14 commits required to get the features live, **9 were manual intervention** — the automation only achieved 3 clean AI-generated commits.

---

## 2. Timeline of Events

| Date | Commit | Description | Type |
|------|--------|-------------|------|
| Feb 10 12:05 | `2cbf74084` | Add GitHub Actions workflow for AI feature building | Setup |
| Feb 10 14:21 | `9e7acca47` | Fix feature YAMLs: correct folder naming and template format | **Manual Fix** |
| Feb 10 20:13 | `84a9aa18a` | fix(CA-002-08): Update lag range from 30 to 90 days | **Manual Fix** |
| Feb 10 21:12 | `f3e480c51` | Restructure feature YAMLs with UI context | **Manual Fix** |
| Feb 10 21:23 | `2a730d8ab` | fix: Add top-level acceptance_criteria to all 9 layer YAMLs | **Manual Fix** |
| Feb 11 15:10 | `86ad4b384` | 🤖 AI-generated: FEATURE-CA-002-06 implementation | ✅ Automated |
| Feb 11 15:41 | `02765e57b` | fix: Strip markdown code fences from AI-generated Python files | **Manual Fix** |
| Feb 11 15:59 | `954f1b760` | 🤖 AI-generated: FEATURE-CA-002-08 implementation | ✅ Automated |
| Feb 11 16:49 | `ff1adbe24` | 🤖 AI-generated: FEATURE-CA-002-09 implementation | ✅ Automated |
| Feb 12 10:13 | `0ea8d7de5` | fix: Wire AI-built features CA-002-06/08/09 into production causality router | **Manual Fix** |
| Feb 12 10:22 | `abb6384cb` | feat: Add production_integration section to CA-002-08 YAML template | **Manual Fix** |
| Feb 12 13:13 | `3776681f1` | fix: Wire causality_router into production main.py | **Manual Fix** |
| Feb 12 13:56 | `86071fbf8` | fix: Make causality_router importable from root main.py | **Manual Fix** |
| Feb 13 08:44 | `3c2f1b7fb` | feat: Add lag analysis, regression & prediction to signal modal | **Manual Fix** |

**Workflow Runs (GitHub Actions):**

| Run ID | Date | Duration | Input | Result |
|--------|------|----------|-------|--------|
| 21864387129 | Feb 10 12:12 | 0s | push trigger | ❌ Failed (workflow file issue) |
| 21865654339 | Feb 10 12:52 | 1m14s | dispatch | ✅ Success (dry run) |
| 21866344336 | Feb 10 13:14 | 1m3s | dispatch | ✅ Success (dry run) |
| 21869416519 | Feb 10 14:43 | 6m8s | dispatch | ✅ Success (single feature) |
| 21870999605 | Feb 10 15:25 | 23m27s | ALL_IN_ORDER | ✅ Success (4 features built, **no push**) |
| 21910307229 | Feb 11 15:02 | 7m42s | FEATURE-CA-002-06 | ✅ Success |
| 21912081526 | Feb 11 15:49 | 9m59s | FEATURE-CA-002-08 | ✅ Success |
| 21913998259 | Feb 11 16:41 | 8m34s | FEATURE-CA-002-09 | ✅ Success |

---

## 3. Root Causes

### RC-1: Feature YAMLs Were Not Ready for the Pipeline

**Category:** Input Validation / Preparation Failure  
**Severity:** HIGH — Blocked the entire pipeline on first attempt  
**Manual fixes required:** 4 commits (Feb 10)

**What happened:**
- Layer folder names used hyphens instead of underscores (e.g., `LAYER-CA-002-06-01` vs expected `LAYER_CA_002_06_01_Causality_Router`)
- Layer YAMLs were missing top-level `acceptance_criteria` keys required by the AI code generator's prompt builder
- Feature YAML template format didn't match what `build_feature.py` expects (missing `metadata.requirement_name` and `metadata.requirement_id`)
- Business logic parameters were incorrect (lag range 30 vs 90 days)

**Why it wasn't caught:**
- The workflow's validation step (`✅ Validate configuration`) only checks that the YAML **file** exists via `find` — it never validates the internal structure
- No schema validation exists for feature or layer YAMLs
- The `build_feature.py --init-layers` step that generates correct folder structure was not run as part of the pipeline

---

### RC-2: AI Code Generator Outputs Markdown-Fenced Code

**Category:** Output Quality / Code Cleaning  
**Severity:** MEDIUM — Produces un-importable Python files  
**Manual fixes required:** 1 commit (`02765e57b`)

**What happened:**
- AI provider returns code wrapped in ` ```python ... ``` ` markers
- Generated `.py` files contained these markers, making them un-importable
- Required manual stripping of markdown fences from all generated files

**Why it wasn't caught:**
- `build_feature.py` has `clean_generated_code()` and `_extract_code_from_response()` functions that strip fences
- However, the layer-level AI code generator orchestrator (`layer/orchestrator/ai_code_generator_orchestrator.py`) writes raw AI responses directly to disk in some code paths, bypassing the fence-stripping logic
- The `_validate_generated_code()` step uses `ast.parse()` which would catch syntax errors, but it runs **after** the file is written and before `_ship_to_production()` — it logs the error but the workflow still reports "success"

**Affected files:**
- `layer/orchestrator/ai_code_generator_orchestrator.py` — file write paths in RED/GREEN/REFACTOR phases

---

### RC-3: No Production Wiring — Feature YAMLs Lacked `production_integration` Section

**Category:** Architecture Gap / Missing Configuration  
**Severity:** CRITICAL — Features built but completely disconnected from live app  
**Manual fixes required:** 4 commits (Feb 12)

**What happened:**
- `build_feature.py` has full production wiring logic (`generate_production_wiring()`) that:
  - Generates FastAPI endpoint code from a `production_integration` YAML section
  - Injects routes into the target router file
  - Verifies the router is mounted in `main.py`
- **None of the 3 feature YAMLs had a `production_integration` section**
- The builder printed a warning but continued:
  ```
  ⚠️  No 'production_integration' section in feature YAML.
       Feature code is built but NOT connected to the live app.
  ```
- This warning was lost in CI log output — there's no failure gate

**Manual work required:**
1. Manually created endpoint code in `causality_router.py` for Granger, lag, regression features
2. Manually added router mounting in `main.py`
3. Manually fixed import paths so the router was discoverable
4. Retrospectively added `production_integration` section to YAML (too late)

**Key code location:** `build_feature.py` lines 2034-2048 — the `prod_config` check

---

### RC-4: No Git Push in Workflow — Two Competing Commit/Push Mechanisms

**Category:** Deployment / CI Configuration Failure  
**Severity:** CRITICAL — Generated code never reached the target repository  
**Manual fixes required:** N/A (features were eventually pushed via individual runs)

**What happened:**
- The workflow YAML originally had a "Commit & Push" step, but it was removed with the comment:
  > *"NOTE: Commit & push is now handled by build_feature.py's _ship_to_production() method. The builder is fully end-to-end."*
- `build_feature.py`'s `_ship_to_production()` tries `git push origin main` from within Python subprocess
- In CI, this fails silently because:
  1. It runs from the `control_tower/` directory, not `target_repo/`
  2. `_find_repo_root()` walks up from the feature directory and may find the wrong `.git`
  3. The git remote auth uses the checkout action's ephemeral token, which may differ from `CROSS_REPO_PAT`
  4. Push failures are caught as exceptions and printed as warnings — they don't fail the workflow step

**The result:** The Feb 10 `ALL_IN_ORDER` run built all 4 features, marked "success", but **nothing was pushed**. The generated code existed only on the ephemeral CI runner and was destroyed when the job completed.

**Eventually fixed by:** Running individual features one-at-a-time (Feb 11), where the workflow's shell script `git add -A && git commit` step happened to work because the working directory was correct.

**Key code locations:**
- `.github/workflows/ai-feature-builder.yml` lines 226-240 — the removed commit/push step
- `build_feature.py` lines 1765-1877 — `_ship_to_production()` method

---

### RC-5: No System-Level Integration Step

**Category:** Architecture Gap — Missing Pipeline Stage  
**Severity:** HIGH — Features exist as standalone modules, not integrated into the running app  
**Manual fixes required:** 1 commit (`3c2f1b7fb`)

**What happened:**
- The pipeline builds at FEATURE granularity: LAYER → feature_integration.py
- There is no SYSTEM-level step that takes the generated features and wires them into:
  - The actual deployed FastAPI routers
  - The frontend UI components (signal modal, dashboard)
  - The database models
  - The deployment configuration
- The `production_integration` per-feature approach (RC-3) is a partial workaround, but even when present, it only handles backend API wiring — not frontend integration

**Architecture gap documented in:** `AI_CODE_GENERATOR_ARCHITECTURE_ENHANCEMENT.md` (Oct 15, 2025)

```
Current:    LAYERS → build_feature.py → FEATURE ✅
Missing:    FEATURES → build_system.py → SYSTEM ❌
Missing:    SYSTEMS → build_project.py → PROJECT ❌
```

---

## 4. Corrective Actions

### CA-1: YAML Schema Validation Gate

**Blocks:** RC-1 (Feature YAMLs not ready)  
**Priority:** P1 — Must implement first  
**Effort:** 2-3 hours  
**Owner:** TBD

**Description:**
Create `validate_feature_yaml.py` — a pre-flight validation script that is run as the first step in the workflow, before any AI generation. It must validate:

1. **Feature YAML structure:**
   - `metadata.requirement_id` exists and matches `FEATURE-XX-YYY-ZZ` pattern
   - `metadata.requirement_name` exists and is non-empty
   - `acceptance_criteria` is a non-empty list with `criterion_id` and `description` per item
   - `layers` is a non-empty list

2. **Layer resolution:**
   - Each `layers[].requirement_file` resolves to an existing file
   - Layer folder naming matches `standardize_layer_folder_name()` convention
   - Each layer YAML has `acceptance_criteria` (non-empty list)

3. **Production integration (for fire-and-forget mode):**
   - `production_integration` section exists when `--require-production-wiring` flag is passed
   - `target_router_file` points to an existing file
   - `app_entry_point` points to an existing file
   - `operations` list is non-empty

4. **Workflow integration:**
   ```yaml
   - name: "🔍 Validate feature YAMLs (deep)"
     run: |
       for YAML in "${YAML_PATHS[@]}"; do
         python control_tower/validate_feature_yaml.py "$YAML" \
           --strict --require-production-wiring
       done
   ```

**Acceptance criteria:**
- [ ] `validate_feature_yaml.py` exists and is executable
- [ ] Validates all fields listed above
- [ ] Exits non-zero with clear error message on any failure
- [ ] Workflow fails fast before any Anthropic API calls are made
- [ ] All existing feature YAMLs pass validation (fix them if not)

---

### CA-2: Fix Markdown Fence Stripping in Layer Orchestrator

**Blocks:** RC-2 (AI outputs markdown-fenced code)  
**Priority:** P1 — Quick fix  
**Effort:** 30 minutes  
**Owner:** TBD

**Description:**
Apply `clean_generated_code()` at the layer orchestrator's file-writing paths so every generated `.py` file is cleaned before disk write.

**Changes required:**

1. **In `layer/orchestrator/ai_code_generator_orchestrator.py`:**
   - After every `ai_provider.generate_code()` call, apply fence stripping before writing to file
   - Import or duplicate `clean_generated_code()` from `build_feature.py`
   - Apply in RED phase (test generation), GREEN phase (implementation), and REFACTOR phase

2. **Alternatively, add a post-write cleanup step:**
   ```python
   # After all files are written, strip any remaining markdown fences
   for py_file in feature_dir.rglob("*.py"):
       content = py_file.read_text()
       if content.startswith("```"):
           cleaned = clean_generated_code(content)
           py_file.write_text(cleaned)
   ```

**Acceptance criteria:**
- [ ] No generated `.py` file contains ` ```python ` or ` ``` ` markers
- [ ] `_validate_generated_code()` passes without syntax errors from fences
- [ ] Existing `clean_generated_code()` tests still pass

---

### CA-3: Require `production_integration` in Feature YAMLs

**Blocks:** RC-3 (No production wiring)  
**Priority:** P1 — Required for fire-and-forget  
**Effort:** 1-2 hours  
**Owner:** TBD

**Description:**
Make the `production_integration` section mandatory for any feature intended for the automated pipeline. Create a template and update all existing feature YAMLs.

**Changes required:**

1. **Create a `production_integration` template section** in feature YAML documentation:
   ```yaml
   production_integration:
     target_router_file: "src/backend/app/causality_router.py"
     app_entry_point: "src/backend/app/main.py"
     import_alias: "LagAnalysisOrchestrator"
     module_name: "feature_integration_08"
     endpoint_prefix: "/lag-analysis"
     health_endpoint: true
     operations:
       - name: run_lag_analysis
         http_method: post
         path: /analyze
         description: "Run lag analysis between two variables"
         request_model: LagAnalysisRequest
         orchestrator_method: analyze
     pydantic_models:
       - name: LagAnalysisRequest
         fields:
           - name: variable_a
             type: str
             description: "First variable ID"
           - name: variable_b
             type: str
             description: "Second variable ID"
           - name: max_lag
             type: int
             default: 90
             description: "Maximum lag in days"
   ```

2. **Update all 3 feature YAMLs** (CA-002-06, -08, -09) with correct `production_integration` sections

3. **Make `build_feature.py` fail (not warn)** when `production_integration` is missing and running in CI mode:
   ```python
   if not prod_config and os.getenv('CI'):
       print("❌ BLOCKED: No 'production_integration' section in feature YAML.")
       print("   Fire-and-forget mode requires production wiring configuration.")
       return False
   ```

4. **Validate in CA-1** (`validate_feature_yaml.py`)

**Acceptance criteria:**
- [ ] All feature YAMLs for CA-002-06, -08, -09 have valid `production_integration` sections
- [ ] `build_feature.py` fails with non-zero exit code in CI when section is missing
- [ ] `generate_production_wiring()` successfully wires endpoints when section is present
- [ ] Router mounting in `main.py` is verified by the builder

---

### CA-4: Restore Reliable Git Push in Workflow

**Blocks:** RC-4 (No git push in CI)  
**Priority:** P0 — Critical, without this nothing deploys  
**Effort:** 30 minutes  
**Owner:** TBD

**Description:**
Remove the reliance on `build_feature.py`'s internal `_ship_to_production()` for CI commits/pushes. Add an explicit, deterministic commit-and-push step to the workflow YAML that uses the known-good `CROSS_REPO_PAT` token.

**Changes required:**

1. **Add a new workflow step** after the build steps (both single and ALL_IN_ORDER):
   ```yaml
   - name: "🚀 Commit and push to target repo"
     if: inputs.dry_run != true
     working-directory: target_repo
     run: |
       git config user.name "github-actions[bot]"
       git config user.email "github-actions[bot]@users.noreply.github.com"
       
       # Stage all changes
       git add -A
       
       # Check if there are changes to commit
       if git diff --cached --quiet; then
         echo "ℹ️  No changes to commit"
         exit 0
       fi
       
       # Count changed files
       CHANGED=$(git diff --cached --stat | tail -1)
       echo "📝 Changes: $CHANGED"
       
       # Commit
       FEATURE="${{ inputs.feature_id }}"
       git commit -m "🤖 AI Feature Builder: ${FEATURE}" \
         -m "Automated build by AI Feature Builder workflow" \
         -m "Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
       
       # Push using CROSS_REPO_PAT
       git push origin main
       
       echo "✅ Pushed to origin/main — Railway deployment triggered"
   ```

2. **Disable `_ship_to_production()` when running in CI** (to avoid double-commit):
   ```python
   # In build_feature.py, at the start of _ship_to_production():
   if os.getenv('CI'):
       print("  ℹ️  Running in CI — commit/push handled by workflow")
       return True
   ```

3. **Ensure the checkout step has correct token:**
   ```yaml
   - name: "📥 Checkout target repository"
     uses: actions/checkout@v4
     with:
       repository: ${{ inputs.target_repo }}
       token: ${{ secrets.CROSS_REPO_PAT }}  # Must have push permissions
       path: target_repo
       fetch-depth: 0
   ```

**Acceptance criteria:**
- [ ] `git push origin main` executes successfully in workflow
- [ ] `CROSS_REPO_PAT` secret has `repo` scope with push permissions
- [ ] Commit message includes workflow run link for traceability
- [ ] No duplicate commits (CI push vs `_ship_to_production()`)
- [ ] Dry run mode skips commit/push entirely

---

### CA-5: Build System-Level Integration Step

**Blocks:** RC-5 (No system integration)  
**Priority:** P2 — Important but larger effort  
**Effort:** 4-8 hours  
**Owner:** TBD

**Description:**
Implement a system-level integration step that runs after all features are built. This bridges the gap between individual feature `feature_integration.py` modules and the deployed application.

**Two implementation options:**

#### Option A: Lightweight — Enhance `production_integration` (Recommended First)

Enhance the existing per-feature `production_integration` wiring to be more robust:

1. **After all features are built in `ALL_IN_ORDER` mode**, add a verification step:
   ```python
   # verify_system_integration.py
   def verify_system_integration(repo_root, features_built):
       """Verify all built features are wired into the production app."""
       main_py = repo_root / "src/backend/app/main.py"
       main_content = main_py.read_text()
       
       for feature in features_built:
           router_file = feature.production_integration.target_router_file
           if router_file not in main_content:
               print(f"❌ {feature.feature_id}: Router not mounted in main.py")
               return False
           
           # Verify endpoints respond
           for op in feature.production_integration.operations:
               endpoint = f"{feature.production_integration.endpoint_prefix}{op.path}"
               print(f"  ✓ {endpoint} ({op.http_method.upper()})")
       
       return True
   ```

2. **Add a workflow step:**
   ```yaml
   - name: "🔗 Verify system integration"
     if: inputs.feature_id == 'ALL_IN_ORDER' && inputs.dry_run != true
     run: |
       cd control_tower
       python verify_system_integration.py "../target_repo/${{ inputs.target_path }}"
   ```

#### Option B: Full — Implement `build_system.py`

As documented in `AI_CODE_GENERATOR_ARCHITECTURE_ENHANCEMENT.md`:

1. Create `build_system.py` that:
   - Reads `SYSTEM-CA-002.yaml`
   - Discovers all child `FEATURE-XX` directories
   - Loads each `feature_integration.py`
   - Generates/updates FastAPI application structure:
     - `app/main.py` with all routers mounted
     - `app/api/v1/*.py` router files (one per feature)
     - `app/models/*.py` Pydantic/SQLAlchemy models
   - Generates deployment files (Dockerfile, railway.json, requirements.txt)
   - Runs system-level acceptance tests

2. Add to workflow:
   ```yaml
   - name: "🏗️ System integration"
     if: inputs.feature_id == 'ALL_IN_ORDER'
     run: |
       cd control_tower
       python build_system.py "../target_repo/${{ inputs.target_path }}/SYSTEM-CA-002.yaml"
   ```

**Recommendation:** Start with Option A (1-2 hours). Move to Option B when building the next system.

**Acceptance criteria:**
- [ ] After `ALL_IN_ORDER` build, all features are verified as wired into production
- [ ] `main.py` contains correct router imports and mounting
- [ ] All feature endpoints are enumerable from the system YAML
- [ ] Smoke test confirms no import errors in the production entry point

---

## 5. Implementation Priority Matrix

| CA | Priority | Effort | Blocks | Dependency |
|----|----------|--------|--------|------------|
| **CA-4** | P0 | 30 min | RC-4 (no push) | None — do first |
| **CA-2** | P1 | 30 min | RC-2 (markdown fences) | None |
| **CA-1** | P1 | 2-3 hrs | RC-1 (YAML validation) | None |
| **CA-3** | P1 | 1-2 hrs | RC-3 (no prod wiring) | CA-1 (validation uses same schema) |
| **CA-5** | P2 | 2-8 hrs | RC-5 (no system integration) | CA-3 (needs prod wiring first) |

**Recommended execution order:** CA-4 → CA-2 → CA-1 → CA-3 → CA-5

**Total estimated effort:** 6-14 hours

---

## 6. Verification Plan

After implementing all corrective actions, run the following end-to-end test:

1. **Reset:** Create a new feature YAML (e.g., `FEATURE-CA-002-11_test_feature`) with all required sections including `production_integration`
2. **Dispatch:** Trigger the workflow with `FEATURE-CA-002-11` from GitHub Actions
3. **Verify:**
   - [ ] YAML validation passes (CA-1)
   - [ ] AI generates code without markdown fences (CA-2)
   - [ ] Production wiring is applied automatically (CA-3)
   - [ ] Commit and push succeed to `business_ventures` repo (CA-4)
   - [ ] Railway deployment triggers automatically
   - [ ] New endpoint is accessible on production URL
4. **No manual intervention required** at any step

---

## 7. Appendix: Key File Locations

| File | Purpose |
|------|---------|
| `.github/workflows/ai-feature-builder.yml` | GitHub Actions workflow definition |
| `build_feature.py` | Main feature builder (2191 lines) |
| `build_feature.py:1765-1877` | `_ship_to_production()` — git commit/push |
| `build_feature.py:2034-2048` | Production integration check |
| `build_feature.py:1380-1540` | `generate_production_wiring()` |
| `layer/orchestrator/ai_code_generator_orchestrator.py` | Layer-level AI code generation |
| `CAUSAL_AFFECT_GOALS_IMPLEMENTATION_PLAN.yaml` | Project specification |
| `AI_CODE_GENERATOR_ARCHITECTURE_ENHANCEMENT.md` | Architecture gap documentation |
| `AI_CODE_GENERATOR_FIX_SUMMARY.md` | Previous fix for test generation |
