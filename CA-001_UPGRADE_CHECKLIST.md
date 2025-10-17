# CA-001 Upgrade Checklist - Match CA-006 Structure

**Date**: October 17, 2025  
**Task**: Upgrade SYSTEM-CA-001.yaml to match SYSTEM-CA-006.yaml structure  
**Status**: In Progress

---

## 📋 **Sections CA-001 is Missing (Present in CA-006)**

### 1. ✅ **code_generation** Section
**CA-006 has**: Complete 1153-line detailed code generation specification
**CA-001 has**: None

**What to add**:
- `folder_structure` with detailed requirements structure (FEATURE/LAYER folders)
- `source_backend` with app structure, features structure
- `tests` structure
- `documentation` structure
- `phases` with 10+ generation phases

### 2. ✅ **system_requirements** Section  
**CA-006 has**: Detailed performance, scalability, reliability specs
**CA-001 has**: Yes, but needs enhancement to match CA-006 format

### 3. ❌ **E2E Testing** in `testing_requirements`
**CA-006 has**: Only mentions in integration tests (incomplete)
**CA-001 has**: Only mentions in integration tests (incomplete)

**What to add to BOTH**:
- Dedicated `e2e_tests` section
- User journey scenarios
- Production-like deployment requirements

### 4. ✅ **Engagement Metrics** (CA-006 specific)
**CA-001 equivalent**: N/A (data ingestion doesn't have user engagement)

###  5. ✅ **Prioritization Algorithm** (CA-006 specific)
**CA-001 equivalent**: N/A

### 6. ✅ **Analytics Integrations** (CA-006 specific)
**CA-001 equivalent**: `data_sources` section (already present)

---

## 🎯 **Required Changes to CA-001**

### Change 1: Add `code_generation` Section

```yaml
code_generation:
  repository_root: "/workspaces/business_ventures/Causal_affect"
  system_folder: "SYSTEM-CA-001_data_ingestion_processing"
  
  folder_structure:
    requirements:
      description: "Hierarchical folder structure with FEATURE and LAYER folders"
      structure: |
        SYSTEM-CA-001_data_ingestion_processing/
        ├── SYSTEM-CA-001.yaml
        ├── FEATURE-CA-001-01_api_connector/
        │   ├── FEATURE-CA-001-01_api_connector.yaml
        │   ├── LAYER-CA-001-01-01_http_client/
        │   │   └── LAYER-CA-001-01-01_http_client.yaml
        │   └── ... (additional layers)
        └── ... (additional features)
      
      naming_convention:
        feature_folder: "FEATURE-{SYSTEM_ID}-{NUMBER}_{feature_name}"
        feature_file: "FEATURE-{SYSTEM_ID}-{NUMBER}_{feature_name}.yaml"
        layer_folder: "LAYER-{SYSTEM_ID}-{FEATURE_NUM}-{LAYER_NUM}_{layer_name}"
        layer_file: "LAYER-{SYSTEM_ID}-{FEATURE_NUM}-{LAYER_NUM}_{layer_name}.yaml"
    
    source_backend:
      base_path: "src/data_ingestion/backend"
      entry_point: "app/main.py"
      structure:
        app:
          - "__init__.py"
          - "main.py          # Celery app initialization"
          - "config.py        # Settings for all data sources"
          - "tasks/           # Celery tasks for each data source"
          - "db/              # Database connection and models"
          - "middleware/      # Error handling, logging"
        features:
          - "FEATURE-CA-001-01_api_connector/"
          - "FEATURE-CA-001-02_data_validation/"
          - "FEATURE-CA-001-03_timeseries_storage/"
          - "FEATURE-CA-001-04_monitoring/"
  
  phases:
    phase_01_system_infrastructure:
      name: "System Infrastructure"
      files:
        - "app/main.py"
        - "app/config.py"
        - "app/db/connection.py"
    # ... (10 phases total, matching CA-006 pattern)
```

### Change 2: Add E2E Testing Section

```yaml
testing_requirements:
  # ... existing unit_tests and integration_tests ...
  
  e2e_tests:
    minimum_count: 5
    coverage_threshold: 0.70
    environment: "production-like Railway deployment"
    runner: "Pytest with real APIs"
    
    philosophy: |
      E2E tests validate complete data flow from external APIs
      through ingestion pipeline to downstream systems (CA-002).
      Tests run against deployed services with real data sources.
    
    required_scenarios:
      new_data_source_onboarding:
        name: "Admin adds new API source"
        description: "Complete workflow from API key entry to data flowing"
        steps:
          - step: 1
            action: "Admin enters Bloomberg API credentials in admin UI"
            verification: "Connection test succeeds"
          
          - step: 2
            action: "System begins ingestion automatically"
            verification: "Data appears in TimescaleDB within 15 minutes"
          
          - step: 3
            action: "Downstream system (CA-002) receives data"
            verification: "Correlation analysis runs successfully"
        
        acceptance_criteria:
          - "Complete onboarding in < 30 minutes"
          - "Zero data loss during onboarding"
          - "Monitoring dashboard shows source as active"
      
      api_failure_recovery:
        name: "API goes down and recovers"
        description: "System handles failures gracefully without data loss"
        # ... similar structure ...
```

### Change 3: Enhance Structure Consistency

Ensure all sections match CA-006 formatting:
- ✅ metadata
- ✅ deployment
- ✅ code_generation (ADD)
- ✅ system_requirements
- ✅ features
- ✅ acceptance_criteria
- ✅ data_sources (keep as-is)
- ✅ technology_stack
- ✅ dependencies
- ✅ testing_requirements (ENHANCE with E2E)
- ✅ estimated_effort
- ✅ implementation_phases
- ✅ risks

---

## 📝 **Implementation Plan**

### Step 1: Backup Current CA-001
```bash
cp SYSTEM-CA-001.yaml SYSTEM-CA-001.yaml.backup
```

### Step 2: Update CA-001 Structure
1. Add `code_generation` section (lines 50-400, ~350 new lines)
2. Add `e2e_tests` to `testing_requirements` (lines 300-350, ~50 new lines)
3. Reformat sections to match CA-006 indentation/style

### Step 3: Update CA-006 with E2E Tests
1. Add `e2e_tests` section after `integration_tests`

### Step 4: Update Template
1. Ensure `/workspaces/control_tower/templates/SYSTEM_REQUIREMENTS_TEMPLATE.yaml` has both

### Step 5: Create Guide
1. Create `/workspaces/control_tower/templates/SYSTEM_REQUIREMENTS_TEMPLATE_GUIDE.md`

---

## ✅ **Success Criteria**

- [ ] CA-001 has all sections that CA-006 has (except domain-specific ones)
- [ ] CA-001 is 1000+ lines (similar length to CA-006)
- [ ] CA-001 has dedicated E2E testing section
- [ ] CA-006 updated with E2E testing section
- [ ] Template includes E2E testing
- [ ] Template guide documents E2E testing importance

---

## 🎯 **Estimated Time**

- CA-001 upgrade: 30-45 minutes
- CA-006 E2E addition: 15 minutes
- Template updates: 15 minutes
- Documentation: 15 minutes
- **Total**: 75-90 minutes

---

Ready to execute!
