# Layer vs Feature Execution Contract

**Date:** October 13, 2025  
**Purpose:** Define clear separation of concerns between layer-level and feature-level operations in `build_feature.py`

---

## Critical Success Factors ✅

### 1. **Layer-Level Work Happens FIRST (Unchanged)**
### 2. **Feature-Level Work Happens AFTER All Layers Complete**
### 3. **Artifacts Save to Correct Locations**

---

## Execution Flow Contract

```
build_feature.py FEATURE-003-03-03_failure_handling.yaml

┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: LAYER-LEVEL OPERATIONS (EXISTING - UNCHANGED)     │
└─────────────────────────────────────────────────────────────┘

FOR EACH layer IN feature.layers:
  ┌───────────────────────────────────────────────┐
  │ Layer Build: LAYER-003-03-03-01               │
  ├───────────────────────────────────────────────┤
  │ 1. Load layer YAML requirements               │
  │ 2. Call AICodeGeneratorOrchestrator           │
  │    - RED: Generate layer unit tests           │
  │    - GREEN: Generate layer implementation     │
  │    - REFACTOR: Improve layer code             │
  │    - VERIFY: Run layer tests + coverage       │
  │ 3. Generate LAYER-LEVEL reports:              │
  │    ├─ requirements_verification_*.yaml        │
  │    ├─ test_pyramid_report_*.yaml              │
  │    ├─ traceability_matrix_*.yaml              │
  │    └─ quality_gates_report_*.yaml             │
  │ 4. Save artifacts to:                         │
  │    LAYER-003-03-03-01/                        │
  │    ├─ src/implementation.py                   │
  │    ├─ tests/test_*.py (4 files)               │
  │    └─ Requirements Verification/ (4 reports)  │
  └───────────────────────────────────────────────┘
  
  ✅ LAYER-01 COMPLETE
  
  ┌───────────────────────────────────────────────┐
  │ Layer Build: LAYER-003-03-03-02               │
  ├───────────────────────────────────────────────┤
  │ [Same process as LAYER-01]                    │
  │ Save to: LAYER-003-03-03-02/                  │
  └───────────────────────────────────────────────┘
  
  ✅ LAYER-02 COMPLETE
  
  ┌───────────────────────────────────────────────┐
  │ Layer Build: LAYER-003-03-03-03               │
  ├───────────────────────────────────────────────┤
  │ [Same process as LAYER-01]                    │
  │ Save to: LAYER-003-03-03-03/                  │
  └───────────────────────────────────────────────┘
  
  ✅ LAYER-03 COMPLETE

✅ ALL LAYERS COMPLETE - Layer-level artifacts saved

┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: FEATURE-LEVEL OPERATIONS (NEW)                    │
│ ONLY RUNS AFTER ALL LAYERS SUCCESSFULLY COMPLETE           │
└─────────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────┐
  │ Feature Integration Layer Generation          │
  ├───────────────────────────────────────────────┤
  │ 1. Collect layer implementations:             │
  │    ├─ Read LAYER-01/src/implementation.py     │
  │    ├─ Read LAYER-02/src/implementation.py     │
  │    └─ Read LAYER-03/src/implementation.py     │
  │ 2. Read FEATURE YAML:                         │
  │    ├─ integration_scenarios                   │
  │    ├─ e2e_scenarios                           │
  │    └─ feature_acceptance_criteria             │
  │ 3. Build feature integration prompt:          │
  │    "Generate code that orchestrates:          │
  │     - LAYER-01: ViolationDetector            │
  │     - LAYER-02: RemediationGenerator         │
  │     - LAYER-03: RecoveryStateManager"        │
  │ 4. Call AI to generate integration code       │
  │ 5. Save to:                                   │
  │    FEATURE-003-03-03/                         │
  │    └─ src/feature_integration.py              │
  └───────────────────────────────────────────────┘
  
  ✅ FEATURE INTEGRATION CODE GENERATED
  
  ┌───────────────────────────────────────────────┐
  │ Feature-Level Test Generation                 │
  ├───────────────────────────────────────────────┤
  │ 1. Generate FEATURE unit tests:               │
  │    - Test FeatureOrchestrator class           │
  │    - Test layer dependency injection          │
  │    - Test configuration management            │
  │ 2. Generate FEATURE integration tests:        │
  │    - Test LAYER-01 → LAYER-02 interaction     │
  │    - Test LAYER-02 → LAYER-03 interaction     │
  │    - Test complete detection→remediation→state│
  │ 3. Generate FEATURE E2E tests:                │
  │    - Test complete failure recovery workflow  │
  │    - Test actor interaction scenarios         │
  │    - From FEATURE YAML e2e_scenarios          │
  │ 4. Save to:                                   │
  │    FEATURE-003-03-03/                         │
  │    └─ tests/test_feature_integration.py       │
  └───────────────────────────────────────────────┘
  
  ✅ FEATURE TESTS GENERATED
  
  ┌───────────────────────────────────────────────┐
  │ Feature-Level Verification                    │
  ├───────────────────────────────────────────────┤
  │ 1. Run FEATURE tests:                         │
  │    pytest FEATURE-003-03-03/tests/            │
  │          test_feature_*.py                    │
  │          --cov=FEATURE-003-03-03/src/         │
  │ 2. Generate FEATURE requirements verification:│
  │    - Map feature ACs to feature tests         │
  │    - Include layer rollup:                    │
  │      * LAYER-01: 3 ACs verified              │
  │      * LAYER-02: 4 ACs verified              │
  │      * LAYER-03: 4 ACs verified              │
  │    - Verify feature integration scenarios     │
  │ 3. Generate FEATURE test pyramid:             │
  │    - Aggregate layer tests:                   │
  │      * Unit: 15 (from all layers)            │
  │      * Integration: 9 (from all layers)      │
  │      * E2E: 7 (from all layers)              │
  │    - Add feature tests:                       │
  │      * Unit: 5 (feature orchestrator)        │
  │      * Integration: 3 (layer interactions)   │
  │      * E2E: 2 (complete workflows)           │
  │    - Total: 20 unit, 12 integration, 9 E2E   │
  │ 4. Generate FEATURE traceability:             │
  │    - Feature requirements → Feature tests     │
  │    - Feature tests → Feature integration code │
  │    - Layer rollup (all layer traceability)    │
  │ 5. Generate FEATURE quality gates:            │
  │    - Feature integration coverage ≥ 70%      │
  │    - All integration scenarios tested         │
  │    - All E2E scenarios tested                 │
  │ 6. Save to:                                   │
  │    FEATURE-003-03-03/                         │
  │    └─ Requirements Verification/              │
  │       ├─ requirements_verification_*.yaml     │
  │       ├─ test_pyramid_report_*.yaml           │
  │       ├─ traceability_matrix_*.yaml           │
  │       └─ quality_gates_report_*.yaml          │
  └───────────────────────────────────────────────┘
  
  ✅ FEATURE VERIFICATION COMPLETE

┌─────────────────────────────────────────────────────────────┐
│ BUILD COMPLETE                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Artifact Location Contract

### Layer-Level Artifacts (3 locations)

```
FEATURE-003-03-03 Failure Handling and Recovery/
├── LAYER-003-03-03-01 Violation Detector/
│   ├── src/
│   │   └── implementation.py                    ← LAYER-01 implementation
│   ├── tests/
│   │   ├── test_generated_*.py (4 files)        ← LAYER-01 tests
│   │   └── [unit, integration, E2E for LAYER-01]
│   └── Requirements Verification/
│       ├── requirements_verification_*.yaml     ← LAYER-01 requirements
│       ├── test_pyramid_report_*.yaml           ← LAYER-01 pyramid
│       ├── traceability_matrix_*.yaml           ← LAYER-01 traceability
│       └── quality_gates_report_*.yaml          ← LAYER-01 gates
│
├── LAYER-003-03-03-02 Remediation Generator/
│   ├── src/implementation.py                    ← LAYER-02 implementation
│   ├── tests/test_generated_*.py (4 files)      ← LAYER-02 tests
│   └── Requirements Verification/ (4 reports)   ← LAYER-02 reports
│
└── LAYER-003-03-03-03 Recovery State Manager/
    ├── src/implementation.py                    ← LAYER-03 implementation
    ├── tests/test_generated_*.py (3 files)      ← LAYER-03 tests
    └── Requirements Verification/ (4 reports)   ← LAYER-03 reports
```

**Scope:** Each layer directory is SELF-CONTAINED with its own implementation, tests, and reports.

### Feature-Level Artifacts (1 location)

```
FEATURE-003-03-03 Failure Handling and Recovery/
├── src/
│   └── feature_integration.py                   ← FEATURE integration code
│                                                    (orchestrates all 3 layers)
├── tests/
│   └── test_feature_integration.py              ← FEATURE tests
│       ├── class TestFeatureUnit               ← Feature unit tests
│       ├── class TestFeatureIntegration        ← Cross-layer integration
│       └── class TestFeatureE2E                ← Complete workflows
│
└── Requirements Verification/
    ├── requirements_verification_*.yaml         ← FEATURE requirements
    │   └── Includes layer_rollup section       ← Aggregates layer ACs
    ├── test_pyramid_report_*.yaml               ← FEATURE pyramid
    │   └── Includes layer_aggregate section    ← Aggregates layer tests
    ├── traceability_matrix_*.yaml               ← FEATURE traceability
    │   └── Includes layer_traceability section ← Links to layer traces
    └── quality_gates_report_*.yaml              ← FEATURE gates
        └── Includes layer_summary section      ← Aggregates layer gates
```

**Scope:** Feature directory contains ORCHESTRATION code that uses the layers, plus feature-level verification.

---

## Key Nuances - Layer vs Feature

### Layer-Level Operations (Existing)

| Aspect | Layer Behavior | Example |
|--------|---------------|---------|
| **Input** | Layer YAML requirements | `LAYER-003-03-03-01_violation_detector.yaml` |
| **Scope** | Single layer in isolation | ViolationDetector class only |
| **Tests** | Test layer implementation | Test ViolationDetector methods |
| **ACs** | Layer acceptance criteria | "AC-001: Detect mock usage" |
| **Reports** | Layer metrics only | Coverage of ViolationDetector code |
| **Output** | `LAYER-003-03-03-01/` directory | Self-contained layer artifacts |

### Feature-Level Operations (New)

| Aspect | Feature Behavior | Example |
|--------|-----------------|---------|
| **Input** | FEATURE YAML + All layer implementations | Feature YAML + 3 layer implementations |
| **Scope** | Multi-layer orchestration | How layers work TOGETHER |
| **Tests** | Test layer interactions | Test Detector → Generator → StateManager flow |
| **ACs** | Feature acceptance criteria | "Complete failure handling workflow" |
| **Reports** | Feature metrics + layer aggregate | Coverage of integration + layer summary |
| **Output** | `FEATURE-003-03-03/` root directory | Feature orchestration artifacts |

### Critical Differences

#### What Layer Tests Cover ✅
```python
# LAYER-01 tests
def test_violation_detector_detects_mock():
    """Test that ViolationDetector finds mock usage"""
    detector = ViolationDetector()
    result = detector.detect(code_with_mock)
    assert "MOCK_DETECTED" in result.violations
```

**Scope:** Testing ViolationDetector IN ISOLATION

#### What Feature Tests Cover ✅
```python
# FEATURE integration test
@pytest.mark.integration
def test_detection_to_remediation_flow():
    """Test that violations flow from detector to generator"""
    orchestrator = FeatureOrchestrator()
    
    # Use ACTUAL layer implementations
    violations = orchestrator.detector.detect(bad_code)
    options = orchestrator.generator.generate_remediation(violations)
    state = orchestrator.state_manager.save_state(options)
    
    assert len(options) > 0
    assert state.persisted == True
```

**Scope:** Testing how LAYERS INTERACT through feature orchestration

---

## Code Implementation Contract

### Phase 1: Layer Building (Existing - Do NOT Change)

```python
def build_feature(self):
    """Build all layers for the feature."""
    
    layers = self.feature_spec['layers']
    
    for layer_info in layers:
        print(f"\n{'='*80}")
        print(f"Building Layer: {layer_info['layer_id']}")
        print(f"{'='*80}\n")
        
        # Find layer YAML
        layer_spec = self._find_layer_spec(layer_info)
        
        # Build layer using orchestrator
        success = self.build_layer(layer_info, layer_spec)
        
        if not success:
            return False
        
        # Artifacts AUTOMATICALLY saved to:
        # {layer_spec.parent}/src/implementation.py
        # {layer_spec.parent}/tests/test_*.py
        # {layer_spec.parent}/Requirements Verification/*.yaml
        
        print(f"✅ Layer {layer_info['layer_id']} built successfully\n")
    
    # ✅ ALL LAYERS COMPLETE - artifacts in layer directories
    
    # NOW proceed to feature-level work
    # [NEW CODE GOES HERE]
```

### Phase 2: Feature Integration (NEW - Add After Layer Loop)

```python
def build_feature(self):
    # ... [Layer building loop above] ...
    
    # ✅ ALL LAYERS COMPLETE
    print(f"\n{'='*80}")
    print(f"ALL LAYERS COMPLETE - Building Feature Integration")
    print(f"{'='*80}\n")
    
    # NEW: Build feature integration layer
    if not self._skip_feature_integration:
        
        # Collect layer implementations
        layer_implementations = self._collect_layer_implementations(layers)
        
        # Create feature integration spec
        feature_spec = FeatureIntegrationSpec(
            feature_id=self.feature_spec['feature_id'],
            feature_name=self.feature_spec['name'],
            feature_dir=self.feature_dir,  # FEATURE-003-03-03 root
            layers=layers,
            integration_scenarios=self.feature_spec.get('integration_scenarios', []),
            e2e_scenarios=self.feature_spec.get('e2e_scenarios', []),
            layer_implementations=layer_implementations
        )
        
        # Generate feature integration code
        print("Generating feature integration code...")
        integration_success = self.generate_feature_integration(feature_spec)
        if not integration_success:
            print("❌ Feature integration generation failed")
            return False
        
        # Save to: FEATURE-003-03-03/src/feature_integration.py
        print(f"✅ Feature integration code saved to {self.feature_dir}/src/")
        
        # Generate feature tests
        print("\nGenerating feature-level tests...")
        test_success = self.generate_feature_tests(feature_spec)
        if not test_success:
            print("❌ Feature test generation failed")
            return False
        
        # Save to: FEATURE-003-03-03/tests/test_feature_integration.py
        print(f"✅ Feature tests saved to {self.feature_dir}/tests/")
        
        # Run feature verification
        print("\nRunning feature-level verification...")
        verification_success = self.run_feature_verification(feature_spec)
        if not verification_success:
            print("❌ Feature verification failed")
            return False
        
        # Save to: FEATURE-003-03-03/Requirements Verification/*.yaml
        print(f"✅ Feature verification reports saved to {self.feature_dir}/Requirements Verification/")
    
    # Final summary
    self.show_complete_summary(layers, feature_spec if not self._skip_feature_integration else None)
    return True
```

### Artifact Saving Contract

```python
def generate_feature_integration(self, spec: FeatureIntegrationSpec) -> bool:
    """Generate feature integration code."""
    
    # Generate code using AI
    code = self._call_ai_for_integration(spec)
    
    # CRITICAL: Save to FEATURE directory, NOT layer directory
    output_path = spec.feature_dir / "src" / "feature_integration.py"
    #             ^^^^^^^^^^^^^^^
    #             FEATURE-003-03-03/ (root)
    #             NOT LAYER-003-03-03-01/
    
    output_path.parent.mkdir(exist_ok=True, parents=True)
    output_path.write_text(code)
    
    return True

def generate_feature_tests(self, spec: FeatureIntegrationSpec) -> bool:
    """Generate feature-level tests."""
    
    # Generate tests using AI
    tests = self._call_ai_for_feature_tests(spec)
    
    # CRITICAL: Save to FEATURE tests directory, NOT layer tests directory
    output_path = spec.feature_dir / "tests" / "test_feature_integration.py"
    #             ^^^^^^^^^^^^^^^
    #             FEATURE-003-03-03/tests/
    #             NOT LAYER-003-03-03-01/tests/
    
    output_path.parent.mkdir(exist_ok=True, parents=True)
    output_path.write_text(tests)
    
    return True

def run_feature_verification(self, spec: FeatureIntegrationSpec) -> bool:
    """Run feature-level verification and generate reports."""
    
    # Run feature tests (NOT layer tests)
    test_results = self._run_pytest(
        test_dir=spec.feature_dir / "tests",
        test_pattern="test_feature_*.py",  # Only feature tests
        coverage_dir=spec.feature_dir / "src"  # Only feature integration code
    )
    
    # Aggregate layer metrics
    layer_metrics = self._aggregate_layer_metrics(spec.layers)
    
    # Generate reports
    reports = self._generate_feature_reports(
        feature_spec=spec,
        test_results=test_results,
        layer_metrics=layer_metrics
    )
    
    # CRITICAL: Save to FEATURE Requirements Verification, NOT layer
    report_dir = spec.feature_dir / "Requirements Verification"
    #            ^^^^^^^^^^^^^^^
    #            FEATURE-003-03-03/Requirements Verification/
    #            NOT LAYER-003-03-03-01/Requirements Verification/
    
    report_dir.mkdir(exist_ok=True, parents=True)
    
    for report_name, report_content in reports.items():
        report_path = report_dir / f"{report_name}_{self.timestamp}.yaml"
        self._save_yaml(report_path, report_content)
    
    return True
```

---

## Validation Checklist

Before committing any implementation, verify:

### Layer-Level Validation ✅

- [ ] Each layer directory has `src/implementation.py`
- [ ] Each layer directory has `tests/test_*.py` files
- [ ] Each layer directory has `Requirements Verification/` with 4 reports
- [ ] Layer tests only import layer code (not other layers)
- [ ] Layer reports only reference layer requirements
- [ ] No layer artifacts in feature root directory

### Feature-Level Validation ✅

- [ ] Feature root has `src/feature_integration.py`
- [ ] Feature root has `tests/test_feature_integration.py`
- [ ] Feature root has `Requirements Verification/` with 4 reports
- [ ] Feature tests import ALL layer implementations
- [ ] Feature reports include layer rollup/aggregate sections
- [ ] No feature artifacts in layer directories

### Separation Validation ✅

- [ ] Layer tests run independently: `pytest LAYER-01/tests/`
- [ ] Feature tests run independently: `pytest FEATURE-003-03-03/tests/test_feature_*.py`
- [ ] Layer tests don't fail if feature tests aren't generated yet
- [ ] Feature tests can find and import all layer implementations
- [ ] Clear distinction in test pyramid report (layer vs feature)

---

## Final Directory Structure Verification

```bash
# After successful build, this should be the structure:

FEATURE-003-03-03 Failure Handling and Recovery/
│
├── LAYER-003-03-03-01 Violation Detector/      ← LAYER artifacts
│   ├── src/implementation.py
│   ├── tests/test_*.py (4 files)
│   └── Requirements Verification/ (4 reports)
│
├── LAYER-003-03-03-02 Remediation Generator/   ← LAYER artifacts
│   ├── src/implementation.py
│   ├── tests/test_*.py (4 files)
│   └── Requirements Verification/ (4 reports)
│
├── LAYER-003-03-03-03 Recovery State Manager/  ← LAYER artifacts
│   ├── src/implementation.py
│   ├── tests/test_*.py (3 files)
│   └── Requirements Verification/ (4 reports)
│
├── src/                                        ← FEATURE artifacts
│   └── feature_integration.py
│
├── tests/                                      ← FEATURE artifacts
│   └── test_feature_integration.py
│
└── Requirements Verification/                  ← FEATURE artifacts
    ├── requirements_verification_*.yaml
    ├── test_pyramid_report_*.yaml
    ├── traceability_matrix_*.yaml
    └── quality_gates_report_*.yaml
```

**Key Observation:** Layer artifacts stay in layer folders. Feature artifacts stay in feature root. NO MIXING.

---

## Summary

✅ **We understand the nuances:**

1. **Layer work happens FIRST** - Each layer built completely before moving to next
2. **Feature work happens AFTER** - Only when all layers successfully complete
3. **Artifacts save to correct locations** - Layer artifacts in layer folders, feature artifacts in feature root
4. **Layer tests test layers** - Test single layer in isolation
5. **Feature tests test integration** - Test how layers work together
6. **Reports distinguish scope** - Layer reports for layer metrics, feature reports aggregate layers

✅ **We're ready to proceed** with Phase 1 implementation!

The enhancement will maintain clean separation between layer-level and feature-level concerns while enabling complete feature verification in one command. 🚀
