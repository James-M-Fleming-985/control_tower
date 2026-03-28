# Causal Affect Patent Application — STATUS

## Filing Information
- **Jurisdiction:** United Kingdom
- **Type:** Patent Application
- **Status:** DRAFT — Ready for Legal Review
- **Created:** 2026-03-28
- **Last Updated:** 2026-03-28

## Document Inventory

| # | Document | File | Words | Status |
|---|----------|------|-------|--------|
| 1 | Abstract | 01_Abstract.md | ~286 | ✅ Complete |
| 2 | Description | 02_Description.md | ~8,061 | ✅ Complete |
| 3 | Claims | 03_Claims.md | ~2,782 | ✅ Complete |
| 4 | Drawings Info | 04_Drawings_Info.md | ~1,550 | ✅ Complete |
| 5 | Figures | 05_Figures.md | ~2,641 | ✅ Complete |
| 6 | Master Plan | Causal_Affect_Patent_Plan.yaml | — | ✅ Complete |

**Total word count:** ~15,320

## Claims Summary

| Type | Claim Numbers | Count |
|------|---------------|-------|
| Independent: System | 1 | 1 |
| Independent: Method | 11 | 1 |
| Independent: Medium | 18 | 1 |
| Independent: Iterate System | 28 | 1 |
| Dependent (System Claim 1) | 2–10, 24–27, 32–33 | 16 |
| Dependent (Method Claim 11) | 12–17, 34 | 7 |
| Dependent (Medium Claim 18) | 19–23 | 5 |
| Dependent (Iterate Claim 28) | 29–31 | 3 |
| **Total** | | **34** |

## Six Patentable Innovations

| # | Innovation | Description | Claims | Figures |
|---|-----------|-------------|--------|---------|
| ① | Variable-Level Cross-Domain Causal Discovery | Individual variable granularity across 6+ sources | 1,2,3,4,11,34 | 2,3,4 |
| ② | Three-Model Ensemble with Auto Calibration | Granger 40% + OLS 35% + ARIMA 25%, calibrated | 1,5,6,8,11,12,21,24 | 5,7,11 |
| ③ | Autonomous TDD-Driven MVP Generation | 5-phase pipeline: SPEC→RED→GREEN→REFACTOR→VALIDATE | 1,9,10,13,14,15,22,28 | 8,9,10 |
| ④ | Closed-Loop Autonomous Business Pipeline | End-to-end cycle on daily cron schedule | 1,8,11,15,16,17,23,27 | 1,7,10,11,13 |
| ⑤ | Cross-Layer Enforcement Architecture | L1 (behavioural) → L2 (outcomes) only | 1,7,11,20 | 3,6 |
| ⑥ | Build-Iterate Loop with Failure Diagnosis | Self-healing across 7 error categories | 28,29,30,31 | 12 |

## Cross-Reference Validation

- [x] All 14 figures referenced in Description
- [x] All 14 figures referenced in Drawings Info
- [x] All 6 innovations appear in Description (5+ references each)
- [x] All 6 innovations appear in Drawings Info (3+ references each)
- [x] All 6 innovations covered by specific claims
- [x] 4 independent claims (system, method, medium, iterate system)
- [x] 34 total claims (target: 30–35)
- [x] 4 prior art systems named with specific limitations
- [x] Formulas match source code constants
- [x] Algorithm pseudocode provided for key processes

## Prior Art Named

| System | Limitation |
|--------|-----------|
| Alpaca, QuantConnect, Interactive Brokers | Predict but don't build products; single domain |
| GitHub Copilot, Devin, Replit Agent | Build but don't discover opportunities |
| Palantir, Tableau, Power BI | Correlate but don't act autonomously |
| H2O.ai, DataRobot, Google AutoML | Model but don't deploy products |

## Key Formulas (verified against source code)

| Formula | Source File | Line |
|---------|------------|------|
| DEFAULT_WEIGHTS: granger=0.40, ols=0.35, arima=0.25 | ensemble_model.py | ~37 |
| LAYER1_SOURCES = ("wikipedia", "reddit") | ensemble_model.py | ~45 |
| GRANGER_P_THRESHOLD = 0.10 | ensemble_model.py | ~35 |
| MIN_OLS_TRAIN_MONTHS = 6 | ensemble_model.py | ~32 |
| MIN_ARIMA_POINTS = 24 | ensemble_model.py | ~33 |
| ROLLING_WINDOWS = [7, 30, 90] | ensemble_model.py | ~48 |
| Exploitation weights: demand=30, growth=25, timing=20, evidence=15, competition=10 | exploitation_backtester.py | ~27 |
| Pass rate threshold: ≥80% | ai_code_generator_orchestrator.py | — |
| Complexity: LOW=4, MEDIUM=7, HIGH=12 | mvp_builder_service.py | ~83 |
| Stale build timeout: 600 seconds | dashboard_real.py | — |

## Next Steps

1. **Legal review** — Patent attorney to review claims scope and prior art
2. **Formal drawings** — Convert Figure text descriptions to formal patent drawings
3. **Filing** — Submit to UK Intellectual Property Office (UKIPO)
4. **Consider** — Provisional filing for priority date; PCT international within 12 months

## Reference Material

- Existing Communication Patent template: `Communication_optimization_system_patent_*.pdf` (same directory)
- Source code: `/workspaces/control_tower/cloned_repos/business_ventures/`
- Master plan: `Causal_Affect_Patent_Plan.yaml`
