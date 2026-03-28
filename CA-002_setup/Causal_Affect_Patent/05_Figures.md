# UK PATENT APPLICATION

## FIGURES

The following simple flow diagrams describe the content of each figure for formal patent drawing conversion. All figures use standard patent drawing conventions: rectangular boxes for processes, diamond shapes for decisions, cylinders for databases, and directional arrows for data flow.

---

### FIGURE 1: System Architecture Overview
**Innovation ④ — Closed-Loop Autonomous Business Pipeline**
**Claims: 1, 11, 16**

```
┌──────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS PIPELINE (9 STAGES)                    │
│                                                                      │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐            │
│  │ Stage 1 │──▶│ Stage 2 │──▶│ Stage 3 │──▶│ Stage 4 │            │
│  │  Data   │   │Standard-│   │  N×N    │   │ Granger │            │
│  │Ingestion│   │isation  │   │Correlat.│   │Causality│            │
│  └─────────┘   └─────────┘   └─────────┘   └────┬────┘            │
│                                                   │                  │
│                                                   ▼                  │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐            │
│  │ Stage 9 │◀──│ Stage 8 │◀──│ Stage 7 │◀──│ Stage 5 │            │
│  │Outcome  │   │  Deploy  │   │TDD Code │   │Ensemble │            │
│  │Measure- │   │Automation│   │  Gen.   │   │Predict. │            │
│  │  ment   │   └─────────┘   └─────────┘   └────┬────┘            │
│  └────┬────┘                                     │                  │
│       │                                    ┌─────────┐              │
│       │         FEEDBACK LOOP              │ Stage 6 │              │
│       └───────────────────────────────────▶│Exploit. │              │
│         (Weight Recalibration)             │ Scoring │              │
│                                            └─────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

---

### FIGURE 2: Multi-Source Data Ingestion Pipeline
**Innovation ① — Variable-Level Cross-Domain Causal Discovery**
**Claims: 1, 2, 11**

```
  LAYER 1 (Behavioural)          LAYER 2 (Outcomes)
  ┌────────────┐                 ┌────────────┐
  │ Wikipedia  │                 │    FRED    │
  │ Pageviews  │                 │ (Economic) │
  └─────┬──────┘                 └─────┬──────┘
        │                              │
  ┌─────┴──────┐                 ┌─────┴──────┐
  │   Reddit   │                 │   Stock    │
  │  Activity  │                 │   Market   │
  └─────┬──────┘                 └─────┬──────┘
        │                              │
        │                        ┌─────┴──────┐
        │                        │   ArXiv    │
        │                        │Publications│
        │                        └─────┬──────┘
        │                              │
        │                        ┌─────┴──────┐
        │                        │   GDELT    │
        │                        │ Geopolitics│
        │                        └─────┬──────┘
        │                              │
        ▼                              ▼
  ┌──────────────────────────────────────────┐
  │         STANDARDISATION MODULE           │
  │  variable_id | source | timestamp | value│
  └──────────────────┬───────────────────────┘
                     │
                     ▼
              ╔══════════════╗
              ║ PostgreSQL   ║
              ║ TimeSeriesData║
              ║ Variable     ║
              ║ Metadata     ║
              ╚══════════════╝
              61 variables
              3,721 pairs
```

---

### FIGURE 3: Cross-Domain Correlation Engine
**Innovations ① and ⑤**
**Claims: 1, 3, 11**

```
      ┌─────────────────────────────────┐
      │   ALL ACTIVE VARIABLES (N=61)   │
      └──────────────┬──────────────────┘
                     │
                     ▼
      ┌─────────────────────────────────┐
      │   PAIRWISE (i,j) where i < j   │
      │   Upper triangle: 3,721 pairs  │
      └──────────────┬──────────────────┘
                     │
            ┌────────┼────────┐
            ▼        ▼        ▼
      ┌─────────┐┌─────────┐┌─────────┐
      │ Pearson ││Spearman ││ Kendall │
      │ r, p    ││ ρ, p    ││ τ, p    │
      └────┬────┘└────┬────┘└────┬────┘
           └──────────┼──────────┘
                      ▼
      ┌─────────────────────────────────┐
      │    SIGNIFICANCE FILTER          │
      │    p < 0.05                     │
      │    Min 20 aligned data points   │
      └──────────────┬──────────────────┘
                     │
                     ▼
      ┌─────────────────────────────────┐
      │    CROSS-DOMAIN FILTER ⑤        │
      │    Exclude same-source pairs    │
      │    Require: source1 ≠ source2   │
      └──────────────┬──────────────────┘
                     │
                     ▼
              ╔══════════════╗
              ║ Correlation  ║
              ║ Result Table ║
              ╚══════════════╝
```

---

### FIGURE 4: Bidirectional Granger Causality System
**Innovation ①**
**Claims: 1, 4, 11, 34**

```
    ┌──────────────────────────────────────────┐
    │   SIGNIFICANT CROSS-DOMAIN PAIR (X, Y)   │
    └──────────────────┬───────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
  ┌──────────────┐           ┌──────────────┐
  │ FORWARD TEST │           │ REVERSE TEST │
  │ H₀: X ↛ Y   │           │ H₀: Y ↛ X   │
  │ p_xy         │           │ p_yx         │
  └──────┬───────┘           └──────┬───────┘
         │                          │
         │   ┌──────────────────┐   │
         │   │  FREQ-ADAPTIVE   │   │
         │   │  LAG SELECTION   │   │
         │   │                  │   │
         │   │ Daily:  252 lags │   │
         │   │ Weekly:  52 lags │   │
         │   │ Monthly: 12 lags │   │
         │   │ Quarterly: 4     │   │
         │   │ Yearly:    2     │   │
         │   │                  │   │
         │   │ Min: 30 points   │   │
         │   │ Buffer: 5-10     │   │
         │   └──────────────────┘   │
         │                          │
         └────────────┬─────────────┘
                      ▼
        ┌──────────────────────────┐
        │   DIRECTION ASSIGNMENT   │
        │                          │
        │ p_xy<0.05 & p_yx≥0.05   │──▶ x_to_y
        │ p_yx<0.05 & p_xy≥0.05   │──▶ y_to_x
        │ p_xy<0.05 & p_yx<0.05   │──▶ bidirectional
        │ p_xy≥0.05 & p_yx≥0.05   │──▶ none
        └──────────────────────────┘
```

---

### FIGURE 5: Three-Model Ensemble Architecture
**Innovation ②**
**Claims: 1, 5, 6, 11, 12, 21, 24**

```
                ┌──────────────────┐
                │ SIGNAL TIME-SERIES│
                └────────┬─────────┘
                         │
                ┌────────┴─────────┐
                │ FEATURE ENGINE   │
                │ Windows: 7,30,90 │
                │ Mean, StdDev, CV │
                └────────┬─────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │  GRANGER   │ │    OLS     │ │   ARIMA    │
   │ Weight:0.40│ │ Weight:0.35│ │ Weight:0.25│
   │            │ │            │ │            │
   │ Conf: 1-p  │ │ Conf: R²   │ │ Order:     │
   │ Uses: lag, │ │ Min: 6 mo  │ │ (1,1,1)    │
   │ direction  │ │ Expanding  │ │ Min: 24 pts│
   │            │ │ window     │ │            │
   │ dir, conf  │ │ dir, conf  │ │ dir, conf  │
   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
         │              │              │
         └──────────────┼──────────────┘
                        ▼
         ┌──────────────────────────────┐
         │     WEIGHTED VOTING          │
         │                              │
         │ up   = Σ(w_i × c_i) "up"    │
         │ down = Σ(w_i × c_i) "down"  │
         │                              │
         │ dir = up≥down ? "up" : "down"│
         │ conf = min(|up-down|/Σw, 1)  │
         └──────────────┬───────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │   PREDICTION    │
              │ direction, conf │
              │ change_pct      │
              └─────────────────┘
                        │
           ◀════════════╧═══════════════▶
           ║  WEIGHT CALIBRATION ②      ║
           ║  ≥10 validated predictions ║
           ║  accuracy_i / Σ(accuracy)  ║
           ╚════════════════════════════╝
```

---

### FIGURE 6: Cross-Layer Enforcement
**Innovation ⑤**
**Claims: 1, 7, 11, 20**

```
   ┌─────────────────┐              ┌─────────────────┐
   │    LAYER 1      │              │    LAYER 2      │
   │  (Behavioural)  │              │   (Outcomes)    │
   │                 │              │                 │
   │  ● Wikipedia    │═══Signal════▶│  ● FRED         │
   │  ● Reddit       │═══════════▶ │  ● Stock        │
   │                 │   Signal    │  ● ArXiv        │
   │                 │     →       │  ● GDELT        │
   │                 │   Target    │                 │
   └────────┬────────┘              └─────────────────┘
            │
            │  ╔═══════════════════════════════════╗
   ✗────────┘  ║ SQL FILTER (database level):      ║
   Wikipedia   ║                                   ║
     ↔         ║ cross_layer = OR(                 ║
   Reddit      ║   AND(v1 IN L1, v2 NOT IN L1),   ║
   BLOCKED     ║   AND(v2 IN L1, v1 NOT IN L1)    ║
               ║ )                                 ║
   ✗           ║                                   ║
   FRED ↔      ║ LAYER1_SOURCES = ("wikipedia",    ║
   Stock       ║                    "reddit")      ║
   BLOCKED     ╚═══════════════════════════════════╝
```

---

### FIGURE 7: Exploitation Scoring Pipeline
**Innovations ② and ④**
**Claims: 1, 8, 11, 17, 26**

```
   ┌──────────────────────────────────────────┐
   │       FIVE-COMPONENT SCORING             │
   │                                          │
   │  Demand ──────── × 30 ──┐               │
   │  Growth ──────── × 25 ──┤               │
   │  Timing ──────── × 20 ──┼──▶ Σ = Score  │
   │  Evidence ─────── × 15 ──┤    (0-100)   │
   │  Competition ──── × 10 ──┘               │
   └──────────────────┬───────────────────────┘
                      │
                      ▼
   ┌──────────────────────────────────────────┐
   │        ACTION TYPE CLASSIFIER            │
   │                                          │
   │  Score + Viability ──▶  ◇ BUY           │
   │                         ◇ SELL           │
   │                         ◇ BUILD ─────────┼──▶ TDD Pipeline
   │                         ◇ MONITOR        │    (Figure 8)
   └──────────────────────────────────────────┘
                      │
                      ▼
   ┌──────────────────────────────────────────┐
   │     EXPLOITATION BACKTESTER ④            │
   │                                          │
   │  actual_pct = ((outcome - baseline)      │
   │                / |baseline|) × 100       │
   │                                          │
   │  direction_accuracy = correct / measured │
   │  mean_abs_error = mean(|actual - pred|)  │
   └──────────────────────────────────────────┘
```

---

### FIGURE 8: Autonomous TDD Code Generation Overview
**Innovation ③**
**Claims: 1, 9, 11, 13, 16, 28**

```
   ┌─────────────────┐
   │  Exploitation    │
   │  Recommendation  │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐     ┌────────────────┐
   │   1. SPEC       │────▶│  YAML Spec     │
   │   Generation    │     │  (AC, tests)   │
   └────────┬────────┘     └────────────────┘
            │
            ▼
   ┌─────────────────┐     ┌────────────────┐
   │   2. RED        │────▶│  Failing tests │
   │   Test Creation │ ◀───│  + stub module │
   └────────┬────────┘  AI └────────────────┘
            │
            ▼
   ┌─────────────────┐     ┌────────────────┐
   │   3. GREEN      │     │  pass_rate =   │
   │   Implementation│◀───▶│  passed /      │
   │   (max 5 retry) │  AI │  (P + F + E)   │
   └────────┬────────┘     └────────────────┘
            │
            ◇ pass_rate ≥ 80%?
           / \
         Yes   No ──▶ retry (up to 5×)
          │
          ▼
   ┌─────────────────┐
   │   4. REFACTOR   │◀──── AI
   │   Quality       │
   │   (keep if      │
   │    regresses)   │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │   5. VALIDATE   │
   │   ast.parse     │
   │   py_compile    │
   │   final pytest  │
   └────────┬────────┘
            │
       ┌────┴────┐
       ▼         ▼
   ┌──────┐  ┌──────┐
   │ LIVE │  │FAILED│
   │  ✓   │  │  ✗   │
   └──────┘  └──────┘
```

---

### FIGURE 9: Five-Phase TDD Pipeline Detail
**Innovation ③**
**Claims: 9, 10, 13, 14, 22, 28**

```
   SPEC PHASE                          RED PHASE
   ┌──────────────────────┐            ┌──────────────────────┐
   │ Keyword Analysis     │            │ Generate test files   │
   │ 8 categories:        │            │ from YAML spec        │
   │ frontend, backend,   │            │                       │
   │ database, auth,      │            │ Create stub module    │
   │ deployment, payments,│            │ with NotImplemented-  │
   │ analytics, CRUD      │            │ Error for all imports │
   │                      │            │                       │
   │ Template Matching:   │            │ Verify: all tests     │
   │  Layer align: 30pts  │            │ fail (confirmed RED)  │
   │  Tag match:  15pts   │            └──────────────────────┘
   │  Framework:  10pts   │
   │  Desc words:  5pts   │            GREEN PHASE
   │  (max 20)            │            ┌──────────────────────┐
   │                      │            │ Extract symbols:      │
   │ Complexity Tiers:    │            │ regex: from X import Y│
   │  LOW:    4 AC        │            │                       │
   │  MEDIUM: 7 AC        │            │ Submit to AI:         │
   │  HIGH:  12 AC        │            │  • test code          │
   └──────────────────────┘            │  • symbol list        │
                                       │  • prev failure (if   │
   REFACTOR PHASE                      │    retry attempt)     │
   ┌──────────────────────┐            │                       │
   │ AI improves quality  │            │ pass_rate ≥ 80%?      │
   │                      │            │  Yes → REFACTOR       │
   │ Regression guard:    │            │  No  → retry (max 5)  │
   │ If new tests fail,   │            └──────────────────────┘
   │ keep pre-refactor    │
   │ version              │            VALIDATE PHASE
   └──────────────────────┘            ┌──────────────────────┐
                                       │ 1. ast.parse (syntax)│
   ERROR CATEGORIES                    │ 2. py_compile (all   │
   ┌──────────────────────┐            │    files)            │
   │ ● syntax             │            │ 3. Final pytest run  │
   │ ● test               │            │ 4. Record metrics:   │
   │ ● frontend           │            │    file_count,       │
   │ ● import             │            │    line_count        │
   │ ● wiring             │            │ 5. Status: LIVE or   │
   │ ● config             │            │    FAILED + error    │
   │ ● runtime            │            │    breakdown JSON    │
   └──────────────────────┘            └──────────────────────┘
```

---

### FIGURE 10: Deployment Automation Flow
**Innovations ③ and ④**
**Claims: 1, 9, 11, 15, 16, 33**

```
   ┌──────────────────────────────────────────────────────┐
   │                GITHUB TRACK                          │
   │                                                      │
   │  PyGithub ──▶ create_repo(auto_init=True)            │
   │           ──▶ Git Tree API:                          │
   │               InputGitTreeElement                    │
   │               mode="100644", type="blob"             │
   │           ──▶ create_commit(tree, parent)            │
   │           ──▶ update_ref(commit_sha)                 │
   │           ──▶ Return: verified commit SHA ✓          │
   └──────────────────────┬───────────────────────────────┘
                          │
                          ▼
   ┌──────────────────────────────────────────────────────┐
   │                RAILWAY TRACK (GraphQL)               │
   │                                                      │
   │  1. projectCreate(input:{name}) → {id, name}        │
   │  2. serviceCreate(input:{projectId,name}) → {id}    │
   │  3. serviceInstanceDeploy(serviceId, envId, image)   │
   │     → {id, status}                                   │
   │  4. Poll status until: SUCCESS | FAILED              │
   └──────────────────────┬───────────────────────────────┘
                          │
                          ▼
   ┌──────────────────────────────────────────────────────┐
   │           BUILD STATUS STATE MACHINE                 │
   │                                                      │
   │  QUEUED ──▶ GENERATING ──▶ LIVE ✓                    │
   │                    │                                  │
   │                    └──▶ FAILED ✗                      │
   │                                                      │
   │  STALE DETECTION: any active state > 600s → FAILED   │
   │  (QUEUED | GENERATING | UPLOADING | DEPLOYING)       │
   └──────────────────────────────────────────────────────┘
```

---

### FIGURE 11: Outcome Measurement and Feedback Loop
**Innovations ② and ④**
**Claims: 1, 5, 6, 11, 12, 16, 17, 25**

```
   ┌──────────────────────────────────────────────────────┐
   │  TRACK 1: PREDICTION VALIDATION (Daily 02:30 UTC)    │
   │                                                      │
   │  Query: status='pending' AND target_date ≤ today     │
   │  Fetch: actual value from TimeSeriesData             │
   │  Compute: actual_direction, actual_change_pct        │
   │  Set: direction_correct = (predicted == actual)      │
   │  Update: status → 'validated'                        │
   └──────────────────────┬───────────────────────────────┘
                          │
   ┌──────────────────────┼───────────────────────────────┐
   │  TRACK 2: WALK-FORWARD BACKTEST (Mon 04:00 UTC)      │
   │                                                      │
   │  For split_idx = 6 to len(data)-1:                   │
   │    train = data[0:split_idx]                         │
   │    slope, intercept = polyfit(x_train, y_train, 1)   │
   │    predicted_y = slope × x_next + intercept          │
   │    direction_correct = (pred_dir == actual_dir)      │
   │    R² = 1 - (ss_res / ss_tot)                        │
   │    Store: model_version='backtest_walkforward'       │
   └──────────────────────┼───────────────────────────────┘
                          │
   ┌──────────────────────┼───────────────────────────────┐
   │  TRACK 3: EXPLOITATION BACKTEST                      │
   │                                                      │
   │  Window: created_at → created_at + (months × 30d)   │
   │  actual_pct = ((outcome-baseline)/|baseline|) × 100 │
   │  Direction accuracy across all measured recs         │
   │  Mean absolute error: mean(|actual - predicted|)     │
   └──────────────────────┼───────────────────────────────┘
                          │
                          ▼
   ┌──────────────────────────────────────────────────────┐
   │  WEIGHT RECALIBRATION                                │
   │                                                      │
   │  Ensemble:   accuracy_i / Σ(accuracy) → new weights  │
   │  Exploit.:   discriminative components → boost ±5pts │
   │                                                      │
   │  ╔═══════════════════════════════════════════╗       │
   │  ║ Feeds back to Ensemble Engine (Figure 5) ║       │
   │  ╚═══════════════════════════════════════════╝       │
   └──────────────────────────────────────────────────────┘
```

---

### FIGURE 12: Build-Iterate Loop
**Innovation ⑥**
**Claims: 28, 29, 30, 31**

```
   ┌─────────────┐
   │ FAILED BUILD │
   │ (parent)     │
   └──────┬──────┘
          │
          ▼
   ┌──────────────────────────────────────────┐
   │     FAILURE DIAGNOSIS MODULE             │
   │                                          │
   │  Classify errors (7 categories):         │
   │  ┌────────┬────┐                         │
   │  │syntax  │ 3  │ ████                    │
   │  │test    │ 7  │ ████████                │
   │  │frontend│ 0  │                         │
   │  │import  │ 2  │ ███                     │
   │  │wiring  │ 1  │ ██                      │
   │  │config  │ 0  │                         │
   │  │runtime │ 1  │ ██                      │
   │  └────────┴────┘                         │
   │  Store: error_breakdown (JSON)           │
   └──────────────┬───────────────────────────┘
                  │
                  ▼
   ┌──────────────────────────────────────────┐
   │    ITERATION CONTEXT GENERATOR           │
   │                                          │
   │  Collect:                                │
   │  ① Parent error_breakdown (JSON)         │
   │  ② Parent generated files (source code)  │
   │  ③ Current ensemble predictions          │
   │     for related signals                  │
   └──────────────┬───────────────────────────┘
                  │
                  ▼
   ┌──────────────────────────────────────────┐
   │    CONCURRENCY GUARD                     │
   │                                          │
   │  ◇ Active build in chain?                │
   │    (QUEUED or GENERATING)                │
   │                                          │
   │    Yes ──▶ BLOCK (return error)          │
   │    No  ──▶ PROCEED                       │
   └──────────────┬───────────────────────────┘
                  │ (No)
                  ▼
   ┌──────────────────────────────────────────┐
   │    CHILD BUILD SPAWNER                   │
   │                                          │
   │  New MVPBuild:                           │
   │    parent_build_id = parent.id           │
   │    iteration_number = parent.iter + 1    │
   │    iterate_reason = "Fix: test errors    │
   │      (7), syntax (3), import (2)"        │
   └──────────────┬───────────────────────────┘
                  │
                  ▼
   ┌──────────────────────────────────────────┐
   │   RE-ENTER TDD PIPELINE (Figure 8)      │
   │   with enriched context                  │
   └──────────────────────────────────────────┘

   ITERATION CHAIN TIMELINE:
   ┌──────┐    ┌──────┐    ┌──────┐
   │ v1   │───▶│ v2   │───▶│ v3   │
   │FAILED│    │FAILED│    │ LIVE │
   └──────┘    └──────┘    └──────┘
```

---

### FIGURE 13: Autonomous Scheduling Timeline
**Innovation ④**
**Claims: 1, 11, 16, 23, 27**

```
   UTC    DAILY                          WEEKLY
   ─────┬────────────────────────────────────────────
   00:00│
        │
   01:00│──▶ Wikipedia Ingestion (L1)
        │    30min spacing (rate limits)
   01:30│──▶ Reddit Ingestion (L1)
        │
   02:00│──▶ GDELT Ingestion (L2)
        │
   02:30│──▶ Update Prediction Actuals
        │    (validate matured predictions)
   03:00│                                Sunday:
        │                                Snapshot Baselines
        │
   04:00│                                Monday:
        │                                Walk-Forward Backtest
   05:00│──▶ Ensemble Predictions
        │    (all L1→L2 pairs, max 200)
        │
        │    Data Dependencies:
        │    ┌─────────────────────────────────┐
        │    │ Ingestion → Analysis → Predict  │
        │    │ (01:00)    (02:30)    (05:00)   │
        │    └─────────────────────────────────┘
   ─────┴────────────────────────────────────────────
```

---

### FIGURE 14: End-to-End Example Scenario
**All Innovations: ①②③④⑤⑥**
**Claims: 1, 11, 16**

```
   STEP 1: DATA INGESTION ①
   ┌────────────────────────┐     ┌────────────────────────┐
   │ Wikipedia              │     │ FRED / Stock           │
   │ "Artificial_intelli-   │     │ NASDAQ Composite       │
   │  gence" pageviews      │     │ Index values           │
   │ (Layer 1)              │     │ (Layer 2)              │
   └───────────┬────────────┘     └───────────┬────────────┘
               │                              │
               ▼                              ▼
   STEP 2: CORRELATION ①⑤
   ┌──────────────────────────────────────────────┐
   │ Pearson r = 0.72, p < 0.001                  │
   │ 60 aligned data points                       │
   │ Cross-layer: Wikipedia (L1) ↔ NASDAQ (L2) ✓  │
   └──────────────────────┬───────────────────────┘
                          │
                          ▼
   STEP 3: GRANGER CAUSALITY ①
   ┌──────────────────────────────────────────────┐
   │ Forward:  Wiki → NASDAQ  p = 0.03 at lag 3  │
   │ Reverse:  NASDAQ → Wiki  p = 0.28           │
   │ Direction: x_to_y (Wiki Granger-causes NASDAQ│
   │            with 3-month lead)                │
   └──────────────────────┬───────────────────────┘
                          │
                          ▼
   STEP 4: ENSEMBLE PREDICTION ②
   ┌──────────────────────────────────────────────┐
   │ Granger: up, conf=0.97  (0.40 × 0.97=0.388) │
   │ OLS:     up, conf=0.68  (0.35 × 0.68=0.238) │
   │ ARIMA:   up, conf=0.55  (0.25 × 0.55=0.138) │
   │                                              │
   │ up_score = 0.388+0.238+0.138 = 0.764        │
   │ Direction: UP, Confidence: 0.764             │
   └──────────────────────┬───────────────────────┘
                          │
                          ▼
   STEP 5: EXPLOITATION SCORING ②④
   ┌──────────────────────────────────────────────┐
   │ Demand:     0.85 × 30 = 25.5                │
   │ Growth:     0.60 × 25 = 15.0                │
   │ Timing:     0.70 × 20 = 14.0                │
   │ Evidence:   0.97 × 15 = 14.6                │
   │ Competition: 0.30 × 10 =  3.0                │
   │ Score: 72.1  Action: BUILD                   │
   └──────────────────────┬───────────────────────┘
                          │
                          ▼
   STEP 6: TDD BUILD ③
   ┌──────────────────────────────────────────────┐
   │ Complexity: MEDIUM (7 acceptance criteria)   │
   │ "AI-sector stock predictor from Wiki trends" │
   │ SPEC → RED → GREEN (92% pass) → REFACTOR    │
   │ → VALIDATE ✓                                │
   └──────────────────────┬───────────────────────┘
                          │
                          ▼
   STEP 7: DEPLOYMENT ③④
   ┌──────────────────────────────────────────────┐
   │ GitHub: "ai-stock-predictor-mvp" repo        │
   │ Railway: project + service + deploy          │
   │ Status: LIVE ✓                               │
   │ URL: https://ai-stock-predictor.up.railway.app│
   └──────────────────────┬───────────────────────┘
                          │
                          ▼
   STEP 8: OUTCOME VALIDATION ②④
   ┌──────────────────────────────────────────────┐
   │ +3 months (matching Granger lag 3):          │
   │ Predicted: UP                                │
   │ Actual NASDAQ: +8.3%  Direction: UP ✓        │
   │ direction_correct = True                     │
   │ Granger weight recalibrated: 0.40 → 0.42    │
   └──────────────────────────────────────────────┘
```
