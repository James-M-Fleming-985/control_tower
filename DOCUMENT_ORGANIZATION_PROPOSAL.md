# 📁 CONTROL TOWER DOCUMENT ORGANIZATION PROPOSAL

**Created:** September 16, 2025  
**Purpose:** Proposed organization of all Control Tower requirements documents  
**Status:** PENDING REVIEW & CONFIRMATION

---

## 🏗️ PROPOSED FOLDER STRUCTURE

```
/workspaces/control_tower/
├── requirements/
│   └── north_star_requirements.md (Level 1 - Control Tower North Star)
├── projects/
│   ├── PROJECT-CT-001_TDD_automation_system/
│   │   └── SYSTEM-CT-001-01_TDD_enforcer_engine/
│   │       └── features/
│   │           └── FEATURE-CT-001-01-01_stage5_green_automation/
│   │               └── layers/
│   │                   └── LAYER-CT-001-01-01-01_stage5_green_automation.md
│   ├── PROJECT-CT-002_requirements_management_system/
│   │   └── features/
│   │       ├── FEATURE-CT-002-01_hierarchical_requirements.md
│   │       └── FEATURE-CT-002-02_make_work_on.md
│   └── PROJECT-CT-003_work_discovery_system/
│       └── features/
│           └── FEATURE-CT-003-01_what_next_discovery.md
├── milestones/
│   ├── MILESTONE-CT-001_phase1_completion.md
│   └── MILESTONE-CT-002_phase2_completion.md
└── templates/
    └── PROFESSIONAL_STANDARDS_TEMPLATE.md
```

---

## 📋 DOCUMENT MAPPING PROPOSAL

### **LEVEL 1 (Repository/North Star Level)**
**Location:** `/workspaces/control_tower/requirements/`

| Current Document | Proposed New Location | Reasoning |
|-----------------|----------------------|-----------|
| `HIERARCHICAL_REQUIREMENTS_MANAGEMENT_SYSTEM.md` | `requirements/north_star_requirements.md` | This is Control Tower's "North Star" equivalent |

### **LEVEL 2 (Project Level)**
**Location:** `/workspaces/control_tower/projects/PROJECT-CT-XXX/`

*Need to create project-level requirement documents*

### **LEVEL 3 (System Level)**  
**Location:** `/workspaces/control_tower/projects/PROJECT-CT-XXX/SYSTEM-CT-XXX/`

| Current Document | Proposed New Location | Reasoning |
|-----------------|----------------------|-----------|
| `requirements/hierarchical_system_requirements.md` | `projects/PROJECT-CT-002_requirements_management_system/SYSTEM-CT-002-01_hierarchical_system.md` | System-level requirements for hierarchical management |

### **LEVEL 4 (Feature Level)**
**Location:** `/workspaces/control_tower/projects/PROJECT-CT-XXX/SYSTEM-CT-XXX/features/`

| Current Document | Proposed New Location | Reasoning |
|-----------------|----------------------|-----------|
| `requirements/features/FEATURE-MAKE-WORK-ON-001.md` | `projects/PROJECT-CT-002_requirements_management_system/features/FEATURE-CT-002-01_make_work_on.md` | Make work-on feature |
| `requirements/features/FR-001-WHAT-NEXT.md` | `projects/PROJECT-CT-003_work_discovery_system/features/FEATURE-CT-003-01_what_next_discovery.md` | What-next discovery feature |

### **LEVEL 5 (Layer Level)**
**Location:** `/workspaces/control_tower/projects/PROJECT-CT-XXX/SYSTEM-CT-XXX/features/FEATURE-CT-XXX/layers/`

| Current Document | Proposed New Location | Reasoning |
|-----------------|----------------------|-----------|
| `STAGE5_TDD_AUTOMATION_REQUIREMENTS.md` | `projects/PROJECT-CT-001_TDD_automation_system/SYSTEM-CT-001-01_TDD_enforcer_engine/features/FEATURE-CT-001-01-01_stage5_green_automation/layers/LAYER-CT-001-01-01-01_stage5_green_automation.md` | Stage 5 is a layer within TDD automation feature |
| `requirements/layers/LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001.md` | `projects/PROJECT-CT-002_requirements_management_system/features/FEATURE-CT-002-02_requirements_parser/layers/LAYER-CT-002-02-01_requirements_parser.md` | Layer for requirements parsing |

### **MILESTONES**
**Location:** `/workspaces/control_tower/milestones/`

| Current Document | Proposed New Location | Reasoning |
|-----------------|----------------------|-----------|
| `requirements/phases/PHASE-1-LAYER-REQUIREMENTS.md` | `milestones/MILESTONE-CT-001_phase1_completion.md` | Phase 1 milestone |
| `requirements/phases/PHASE-2-LAYER-REQUIREMENTS.md` | `milestones/MILESTONE-CT-002_phase2_completion.md` | Phase 2 milestone |

### **DOCUMENTS TO EVALUATE/ARCHIVE**

| Document | Status | Action Needed |
|----------|--------|---------------|
| `requirements/master_north_star_requirements.md` | Duplicate? | Compare with HRMS document |
| `requirements/THE_NORTH_STAR.md` | Unclear | Review content vs HRMS |
| `requirements/DRAFT_PROJECT-001_portfolio_architecture_strategy.md` | Draft | Determine if relevant to Control Tower |
| `requirements/DRAFT_PROJECT-002_capital_generation_acceleration.md` | Draft | Determine if relevant to Control Tower |
| `requirements/DRAFT_PROJECT-003_automated_investment_system.md` | Draft | Determine if relevant to Control Tower |
| `requirements/DRAFT_PROJECT-004_debt_elimination_strategy.md` | Draft | Determine if relevant to Control Tower |
| `requirements/DRAFT_PROJECT-005_alternative_investment_integration.md` | Draft | Determine if relevant to Control Tower |
| `requirements/DRAFT_PROJECT-006_tax_optimization_strategy.md` | Draft | Determine if relevant to Control Tower |
| `requirements/DRAFT_SYSTEM-001-01_portfolio_analysis_design.md` | Draft | Determine if relevant to Control Tower |
| `requirements/PROFESSIONAL_STANDARDS_ENFORCEMENT.md` | Keep | Move to templates or root |

---

## 🎯 QUESTIONS FOR REVIEW

1. **HRMS Document:** Should `HIERARCHICAL_REQUIREMENTS_MANAGEMENT_SYSTEM.md` become the Control Tower `north_star_requirements.md`?

2. **Draft Documents:** The DRAFT_PROJECT documents appear to be investment-related. Should these be:
   - Moved to investment_strategy repository?
   - Deleted as obsolete?
   - Kept as Control Tower features?

3. **North Star Duplicates:** We have multiple "north star" type documents. Which is the authoritative one?

4. **Professional Standards:** Should `PROFESSIONAL_STANDARDS_ENFORCEMENT.md` stay in templates or move elsewhere?

---

## ✅ NEXT STEPS (PENDING YOUR APPROVAL)

1. **Move documents** to proposed locations
2. **Create missing project/system requirement documents**
3. **Archive or relocate** draft documents based on your decision
4. **Test `make what-next`** to ensure discovery works
5. **Update any references** to moved documents

**Please review and let me know what should be adjusted before I execute the moves!**