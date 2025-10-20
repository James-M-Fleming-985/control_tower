# System Build Tool - Requirements Review

## Created Files for Review

1. **`SYSTEM_BUILD_REQUIREMENTS.yaml`** (Main Requirements Doc)
   - Complete specification for build_system.py
   - Exact mapping from build_feature.py (623 lines → ~650 lines)
   - All required methods, dataclasses, and workflows
   - Comprehensive prompt building requirements
   - System-level verification and testing requirements
   - Generated output structure specification

2. **`cleanup_before_proper_implementation.sh`** (Cleanup Script)
   - Removes simplified build_system.py (backs up as v2_simplified)
   - Removes manually created files (config.py, database.py, __init__.py)
   - Preserves AI-generated main.py as reference
   - Ready to run after you approve requirements

## What Went Wrong (Learning)

### Attempt 1: Template-based (v1)
- ❌ Used f-string templates instead of AI Code Generator
- ❌ Not consistent with architecture
- Result: Backed up as `build_system_v1_template_based.py.backup`

### Attempt 2: Simplified AI version (v2)
- ❌ Only 230 lines (should be ~650 like build_feature.py)
- ❌ Weak prompt → only generated main.py (175 lines)
- ❌ Missing: _collect_feature_implementations, proper JSON parsing, verification, testing
- ❌ Not following the pattern you explicitly requested
- Result: Will backup as `build_system_v2_simplified.py.backup`

### What You Actually Asked For
> "Create the system.build.py in the same way as feature.build.py which does all the system level testing and verification"

Translation:
- ✅ Copy build_feature.py structure EXACTLY
- ✅ Replace layer operations with feature operations
- ✅ Keep ALL methods (collection, prompt building, generation, verification, reporting)
- ✅ Add system-level testing
- ✅ Add acceptance criteria validation
- ✅ Make it reusable for future system builds

## Requirements Document Structure

```yaml
metadata:
  - Document type, ID, status, priority

purpose:
  - Why we need this
  - Architectural consistency

reference_implementation:
  - Source: build_feature.py (623 lines)
  - Pattern to replicate

architecture_mapping:
  - build_feature: LAYERS → FEATURE
  - build_system: FEATURES → SYSTEM

required_dataclasses:
  - FeatureInfo (replaces LayerInfo)
  - SystemIntegrationSpec (replaces FeatureIntegrationSpec)

required_class_structure:
  SystemBuilder (mirrors FeatureBuilder):
    - initialization methods
    - specification_loading
    - feature_discovery
    - implementation_collection ← CRITICAL
    - ai_prompt_building ← MOST IMPORTANT
    - code_extraction (JSON parsing)
    - ai_generation (call AICodeGeneratorOrchestrator)
    - verification (system-level testing)
    - reporting (comprehensive markdown report)
    - orchestration (build_system main workflow)

required_cli_interface:
  - argparse with system path, --provider, --verbose
  - Examples matching build_feature.py

generated_output_structure:
  SYSTEM-XX/src/backend/:
    - app/main.py (FastAPI app)
    - app/config.py (Pydantic Settings)
    - app/api/v1/{feature}.py (routers)
    - app/db/ (database layer)
    - app/models/ (schemas and ORM)
    - app/services/ (business logic)
    - requirements.txt
    - .env.example
    - docker-compose.dev.yml
  Total: 10-15 files

verification_checklist:
  - Structure validation
  - Syntax validation
  - Import resolution
  - Acceptance criteria validation

implementation_constraints:
  Must: Follow build_feature.py exactly, use AI, comprehensive prompt
  Must NOT: Use templates, skip verification, simplify

cleanup_required:
  - Delete simplified build_system.py
  - Delete manually created files
  - Keep references for comparison
```

## Review Checklist

Please verify:

- [ ] **FeatureInfo dataclass** - Has all needed fields?
- [ ] **_build_system_integration_prompt** - Specification detailed enough?
  - System context
  - Feature descriptions with extracted classes
  - Acceptance criteria
  - Integration requirements (FastAPI, routers, DB, etc.)
  - Implementation guidelines
  - JSON output format request
- [ ] **Verification requirements** - Should it run actual pytest or just validation?
- [ ] **Generated output structure** - Any missing files?
- [ ] **Cleanup steps** - Correct files to remove?

## Questions for You

1. **Prompt detail level**: Is the `_build_system_integration_prompt` specification comprehensive enough? Should I add more examples?

2. **Verification depth**: Should `run_system_verification()` actually execute pytest tests, or just validate structure/syntax?

3. **Additional outputs**: Any other files the backend needs? (README.md, Dockerfile, pytest.ini, etc.)?

4. **Missing requirements**: Anything else the tool should do that's not in the YAML?

## Next Steps (After Your Approval)

1. ✅ You review `SYSTEM_BUILD_REQUIREMENTS.yaml`
2. ✅ You approve or request changes
3. ✅ Run `cleanup_before_proper_implementation.sh`
4. ✅ I implement build_system.py following the spec EXACTLY
5. ✅ Test on SYSTEM-CA-006.yaml
6. ✅ Verify complete backend generation (10-15 files)
7. ✅ Start backend and confirm it works

## Files to Review

📄 **Primary**: `/workspaces/control_tower/SYSTEM_BUILD_REQUIREMENTS.yaml`  
🧹 **Cleanup**: `/workspaces/control_tower/cleanup_before_proper_implementation.sh`

**Please review and let me know if I should proceed or if you need any changes to the requirements!**
