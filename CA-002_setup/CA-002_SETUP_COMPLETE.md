# CA-002 Correlation Analysis Engine - Setup Complete

## Status: Ready for Deployment ✅

**Date**: January 19, 2025  
**System**: CA-002 Correlation Analysis Engine  
**Location**: `/workspaces/control_tower/CA-002_setup/`

---

## What Was Created

### 1. System Requirements YAML
- **File**: `SYSTEM-CA-002.yaml` (1,350+ lines)
- **Content**:
  - Comprehensive metadata and deployment configuration
  - 4 features with 19 total layers defined
  - 29 implementation phases (20K tokens each, Claude Opus 4)
  - Complete technology stack specifications
  - Integration with CA-001 and CA-006
  - Performance requirements and acceptance criteria
  - Risk assessment and mitigation strategies

### 2. Feature Requirements YAMLs (4 files)
- `FEATURE-CA-002-01_statistical_correlation_calculator.yaml`
  - Pearson, Spearman, Kendall, Partial, Lagged correlation calculators
  - 5 layers with NumPy, SciPy, Pandas, Statsmodels

- `FEATURE-CA-002-02_causality_testing_engine.yaml`
  - Granger causality, VAR, IRF, Transfer Entropy, DAG inference
  - 5 layers with Statsmodels, CausalNex, NetworkX

- `FEATURE-CA-002-03_correlation_exploitation_scorer.yaml`
  - Significance, Effect Size, Stability, Actionability, Market scoring
  - 5 layers with weighted exploitation algorithm

- `FEATURE-CA-002-04_correlation_dashboard_and_visualization.yaml`
  - Heatmap, Time Series, Network Graph, Leaderboard components
  - 4 layers with React, D3.js, Recharts

### 3. Layer Requirements YAMLs (19 files)
All layer YAMLs created with:
- Complete metadata and specifications
- Input/output contracts defined
- Acceptance criteria established
- Traceability to features and system

**Layer breakdown**:
- Feature 01: 5 layers (statistical correlations)
- Feature 02: 5 layers (causality testing)
- Feature 03: 5 layers (exploitation scoring)
- Feature 04: 4 layers (dashboard visualization)

### 4. Deployment Scripts
- `deploy_ca002.sh` - Complete setup and deployment script
- `generate_requirements.py` - Requirements YAML generator (already executed)

---

## Architecture Overview

### System Pipeline
```
CA-001 (Data Ingestion)
    ↓
CA-002 (Correlation Analysis) ← **Building This**
    ↓
CA-003 (Drift Forecasting)
    ↓
CA-004 (Recommendation Engine)
    ↓
CA-005 (MVP Generation & Deployment)
    ↓
CA-006 (Feedback Collection)
    ↓ (loop back)
CA-002
```

### CA-002 Data Flow
```
1. CA-001 TimescaleDB → Time-series data retrieval
2. Feature 01 → Statistical correlation calculations
3. Feature 02 → Causality testing (distinguish correlation vs causation)
4. Feature 03 → Exploitation scoring (rank by MVP potential)
5. Feature 04 → Dashboard visualization (interactive exploration)
6. Output → High-potential correlations to CA-003 & CA-004
```

### Integration Points
- **Input**: CA-001 TimescaleDB (time-series data, 15-20 external APIs)
- **Output**: 
  - CA-003 (strong correlations for drift forecasting)
  - CA-004 (exploitable correlations for MVP recommendations)
- **Feedback Loop**: CA-006 (MVP performance → refine correlation scoring)

---

## Deployment Instructions

### Prerequisites
1. Causal_affect repository must be cloned:
   ```bash
   mkdir -p /workspaces/business_ventures
   cd /workspaces/business_ventures
   git clone <causal_affect_repo_url>
   ```

### Deployment Steps

#### Step 1: Run Deployment Script
```bash
cd /workspaces/control_tower/CA-002_setup
./deploy_ca002.sh
```

This will:
- Create `SYSTEM-CA-002_correlation_analysis/` directory
- Copy SYSTEM-CA-002.yaml to system root
- Create 4 feature directories with requirements YAMLs
- Create 19 layer directories with requirements YAMLs
- Set up `src/`, `docs/`, `tests/` folders

#### Step 2: Verify Structure
```bash
cd /workspaces/business_ventures/Causal_affect/SYSTEM-CA-002_correlation_analysis
tree -L 3
```

Expected structure:
```
SYSTEM-CA-002_correlation_analysis/
├── SYSTEM-CA-002.yaml
├── src/
│   ├── backend/app/
│   └── frontend/
├── docs/
├── tests/
├── FEATURE-CA-002-01_statistical_correlation/
│   ├── FEATURE-CA-002-01_statistical_correlation.yaml
│   ├── LAYER-CA-002-01-01_pearson_calculator/
│   │   └── LAYER-CA-002-01-01_pearson_calculator.yaml
│   ├── LAYER-CA-002-01-02_spearman_calculator/
│   │   └── LAYER-CA-002-01-02_spearman_calculator.yaml
│   ├── LAYER-CA-002-01-03_kendall_calculator/
│   ├── LAYER-CA-002-01-04_partial_correlation/
│   └── LAYER-CA-002-01-05_lagged_correlation/
├── FEATURE-CA-002-02_causality_testing/
│   ├── FEATURE-CA-002-02_causality_testing.yaml
│   ├── LAYER-CA-002-02-01_granger_test/
│   ├── LAYER-CA-002-02-02_var_model/
│   ├── LAYER-CA-002-02-03_irf_calculator/
│   ├── LAYER-CA-002-02-04_transfer_entropy/
│   └── LAYER-CA-002-02-05_dag_inference/
├── FEATURE-CA-002-03_correlation_scorer/
│   ├── FEATURE-CA-002-03_correlation_scorer.yaml
│   ├── LAYER-CA-002-03-01_significance_calculator/
│   ├── LAYER-CA-002-03-02_effect_size_analyzer/
│   ├── LAYER-CA-002-03-03_stability_tracker/
│   ├── LAYER-CA-002-03-04_actionability_classifier/
│   └── LAYER-CA-002-03-05_market_estimator/
└── FEATURE-CA-002-04_correlation_dashboard/
    ├── FEATURE-CA-002-04_correlation_dashboard.yaml
    ├── LAYER-CA-002-04-01_heatmap_generator/
    ├── LAYER-CA-002-04-02_time_series_plotter/
    ├── LAYER-CA-002-04-03_network_graph/
    └── LAYER-CA-002-04-04_leaderboard/
```

#### Step 3: Build System with AI Code Generator
```bash
cd /workspaces/control_tower
python build_system.py /workspaces/business_ventures/Causal_affect/SYSTEM-CA-002_correlation_analysis/SYSTEM-CA-002.yaml
```

This will:
- Execute 29 implementation phases (20K tokens each)
- Generate ~60-80 Python files
- Create FastAPI backend with 4 feature modules
- Generate React frontend dashboard
- Create Docker configuration
- Build test suite
- Estimated time: 2-3 hours
- Estimated cost: $25-35 (Claude Opus 4 API)

#### Step 4: Test & Deploy
```bash
cd /workspaces/business_ventures/Causal_affect/SYSTEM-CA-002_correlation_analysis

# Run tests
pytest src/backend/app/features/*/tests/

# Start locally with Docker Compose
docker-compose up

# Deploy to Railway (Railway Pro subscription)
railway up
```

---

## Build Configuration

### AI Model Settings
- **Model**: Claude Opus 4
- **Tokens per phase**: 20,480
- **Total phases**: 29
- **Total estimated tokens**: ~590K
- **Estimated cost**: $25-35
- **Estimated time**: 2-3 hours

### Technology Stack
**Backend**:
- FastAPI 0.104+
- NumPy, SciPy, Pandas (correlation calculations)
- Statsmodels (statistical tests)
- CausalNex, NetworkX (causality inference)
- PostgreSQL 15 (shared with CA-001)
- Redis 7 (caching)
- asyncio, asyncpg (async operations)

**Frontend**:
- React 18 + TypeScript
- D3.js (network graphs)
- Recharts (time-series plots)
- Plotly.js (heatmaps)
- Zustand (state management)
- Vite (build tool)

**Deployment**:
- Railway (Platform)
- Docker (Containers)
- GitHub Actions (CI/CD)

---

## Feature Specifications

### Feature 01: Statistical Correlation Calculator
**Purpose**: Calculate multiple correlation types between variable pairs

**Layers**:
1. **Pearson**: Linear correlation (r coefficient, p-values, CI)
2. **Spearman**: Rank-based monotonic correlation
3. **Kendall**: Tau correlation for ordinal data
4. **Partial**: Correlation controlling for confounders
5. **Lagged**: Time-delayed correlations (0-30 day lags)

**Key Algorithms**:
- Pearson: `scipy.stats.pearsonr`
- Spearman: `scipy.stats.spearmanr`
- Kendall: `scipy.stats.kendalltau`
- Partial: `statsmodels.regression.linear_model`
- Lagged: Custom rolling window implementation

### Feature 02: Causality Testing Engine
**Purpose**: Distinguish correlation from causation

**Layers**:
1. **Granger Test**: Tests if X Granger-causes Y
2. **VAR Model**: Vector Autoregression for multivariate time-series
3. **IRF Calculator**: Impulse Response Functions (shock propagation)
4. **Transfer Entropy**: Information-theoretic causality measure
5. **DAG Inference**: Causal structure learning with NetworkX

**Key Algorithms**:
- Granger: `statsmodels.tsa.stattools.grangercausalitytests`
- VAR: `statsmodels.tsa.vector_ar.var_model.VAR`
- IRF: `statsmodels.tsa.vector_ar.irf.IRAnalysis`
- Transfer Entropy: Custom implementation with `scipy.stats`
- DAG: `causalnex.structure.notears.from_pandas`

### Feature 03: Correlation Exploitation Scorer
**Purpose**: Rank correlations by MVP opportunity potential

**Scoring Formula**:
```
Exploitation Score = 
  0.30 × Statistical Significance (p-value, sample size)
  + 0.25 × Effect Size (Cohen's d, correlation magnitude)
  + 0.20 × Temporal Stability (rolling window variance)
  + 0.15 × Actionability (MVP feasibility classification)
  + 0.10 × Market Size (search volume estimate)
```

**Layers**:
1. **Significance**: P-values, Bonferroni/FDR corrections
2. **Effect Size**: Cohen's d, r-to-d conversion
3. **Stability**: Rolling correlation variance
4. **Actionability**: MVP feasibility classifier (H/M/L)
5. **Market Estimator**: Search volume → TAM proxy

### Feature 04: Correlation Dashboard & Visualization
**Purpose**: Interactive exploration of correlations

**Layers**:
1. **Heatmap Generator**: Correlation matrix with D3.js
2. **Time Series Plotter**: Dual-axis time-series with Recharts
3. **Network Graph**: Causal DAG with force-directed layout
4. **Leaderboard**: Top 20 exploitable correlations table

**Key Features**:
- Real-time filtering and search
- Drill-down detail views
- Export to JSON/CSV
- Responsive design (mobile-friendly)

---

## Performance Requirements

### Calculation Performance
- 1000 correlation pairs: < 5 minutes
- 100 Granger causality tests: < 10 minutes
- Dashboard initial load: < 2 seconds
- Search/filter operations: < 500ms

### Data Capacity
- Support 100K+ data points per variable
- Handle 1000+ variable pairs
- Store 10K+ correlation results
- Cache results for 24 hours

### Scalability
- Phase 1: 1 backend + 1 frontend replica
- Phase 2: 2-3 backend replicas (horizontal scaling)
- Database connection pooling (50 connections)
- Redis cache with LRU eviction

---

## Testing Strategy

### Unit Tests (>85% coverage)
- Correlation calculation accuracy (compare to SciPy)
- Causality test correctness (match statsmodels)
- Scoring algorithm validation (weighted formula)
- Edge cases (missing data, constant series, perfect correlation)

### Integration Tests
- CA-001 database queries
- End-to-end correlation pipeline
- Dashboard data aggregation
- Caching behavior

### End-to-End Tests
- User calculates correlations via API
- User views heatmap in dashboard
- User explores causal network graph
- User exports correlation report

---

## Files Created (Summary)

### Requirements YAMLs
```
/workspaces/control_tower/CA-002_setup/
├── SYSTEM-CA-002.yaml                                          (1,350+ lines)
├── FEATURE-CA-002-01_statistical_correlation_calculator.yaml   (320+ lines)
├── FEATURE-CA-002-02_causality_testing_engine.yaml             (320+ lines)
├── FEATURE-CA-002-03_correlation_exploitation_scorer.yaml      (320+ lines)
├── FEATURE-CA-002-04_correlation_dashboard_and_visualization.yaml (300+ lines)
├── LAYER-CA-002-01-01_pearson_calculator.yaml                  (150+ lines)
├── LAYER-CA-002-01-02_spearman_calculator.yaml                 (150+ lines)
├── LAYER-CA-002-01-03_kendall_calculator.yaml                  (150+ lines)
├── LAYER-CA-002-01-04_partial_correlation.yaml                 (150+ lines)
├── LAYER-CA-002-01-05_lagged_correlation.yaml                  (150+ lines)
├── LAYER-CA-002-02-01_granger_test.yaml                        (150+ lines)
├── LAYER-CA-002-02-02_var_model.yaml                           (150+ lines)
├── LAYER-CA-002-02-03_irf_calculator.yaml                      (150+ lines)
├── LAYER-CA-002-02-04_transfer_entropy.yaml                    (150+ lines)
├── LAYER-CA-002-02-05_dag_inference.yaml                       (150+ lines)
├── LAYER-CA-002-03-01_significance_calculator.yaml             (150+ lines)
├── LAYER-CA-002-03-02_effect_size_analyzer.yaml                (150+ lines)
├── LAYER-CA-002-03-03_stability_tracker.yaml                   (150+ lines)
├── LAYER-CA-002-03-04_actionability_classifier.yaml            (150+ lines)
├── LAYER-CA-002-03-05_market_estimator.yaml                    (150+ lines)
├── LAYER-CA-002-04-01_heatmap_generator.yaml                   (150+ lines)
├── LAYER-CA-002-04-02_time_series_plotter.yaml                 (150+ lines)
├── LAYER-CA-002-04-03_network_graph.yaml                       (150+ lines)
└── LAYER-CA-002-04-04_leaderboard.yaml                         (150+ lines)

Total: 24 YAML files, ~4,500 lines
```

### Scripts
```
/workspaces/control_tower/CA-002_setup/
├── deploy_ca002.sh          - Complete deployment script
└── generate_requirements.py - YAML generator (already executed)
```

---

## Next Steps

### Immediate (Today)
1. ✅ Review generated YAML files (quick scan for accuracy)
2. ⏭️ Run `deploy_ca002.sh` to create directory structure
3. ⏭️ Verify structure in Causal_affect repository

### Short-term (This Week)
4. ⏭️ Execute `build_system.py` to generate implementation
5. ⏭️ Review generated code (FastAPI routes, correlation services, tests)
6. ⏭️ Run test suite and validate calculations
7. ⏭️ Deploy to Railway for testing

### Medium-term (Next 2 Weeks)
8. ⏭️ Integrate with CA-001 database
9. ⏭️ Test end-to-end correlation → causality → scoring pipeline
10. ⏭️ Build CA-003 (Drift Forecasting) to consume CA-002 output
11. ⏭️ Build CA-004 (Recommendation Engine) for MVP suggestions

---

## Risk Mitigation

### Risk 1: Calculation Performance
- **Mitigation**: NumPy vectorization, parallel processing, Redis caching
- **Status**: Addressed in layer specifications

### Risk 2: False Positives in Causality
- **Mitigation**: Multiple test agreement, correction methods, significance thresholds
- **Status**: Layers 02-01 through 02-05 implement multiple tests

### Risk 3: Dashboard Performance (1000+ variables)
- **Mitigation**: Pagination, lazy loading, server-side filtering
- **Status**: Feature 04 layers designed for performance

### Risk 4: CA-001 Integration Breaking
- **Mitigation**: Clear interface contract, versioned API, integration tests
- **Status**: Integration layer in phase 06 of build

---

## Success Criteria

### Phase 1: Build Complete (Week 1)
- ✅ All 24 YAML files created
- ⏭️ `build_system.py` generates ~60-80 files
- ⏭️ Backend starts without errors
- ⏭️ All tests pass (>85% coverage)

### Phase 2: Integration Working (Week 2)
- ⏭️ CA-001 TimescaleDB queries successful
- ⏭️ Correlations calculated correctly (match SciPy)
- ⏭️ Dashboard loads and displays heatmap
- ⏭️ Top 10 exploitable correlations ranked

### Phase 3: Production Ready (Week 3-4)
- ⏭️ Deployed to Railway
- ⏭️ CA-003 consuming CA-002 output
- ⏭️ CA-004 generating MVP recommendations
- ⏭️ End-to-end automation working (data → correlations → drift → recommendations → MVP → feedback)

---

## Contact & Support

**System Owner**: Causal Affect Team  
**Status**: Setup Complete, Ready for Deployment  
**Documentation**: This file + SYSTEM-CA-002.yaml + 23 other YAMLs  
**Location**: `/workspaces/control_tower/CA-002_setup/`

---

**Setup Complete**: January 19, 2025  
**Ready for `deploy_ca002.sh` execution** ✅
