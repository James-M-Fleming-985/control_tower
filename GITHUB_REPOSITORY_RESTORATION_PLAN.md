# 🔧 GITHUB REPOSITORY RESTORATION PLAN

**Date**: September 17, 2025  
**Purpose**: Restore proper repository structures on GitHub BEFORE cloning

---

## 🎯 RESTORATION STRATEGY

**PRINCIPLE: Fix GitHub first, then clone clean structures**

1. ✅ **USE CONTROL_TOWER AS SOURCE OF TRUTH** - All evidence is preserved here
2. ✅ **RESTORE STRUCTURES ON GITHUB** - Push correct organization to each repo  
3. ✅ **VERIFY ALIGNMENT** - Ensure GitHub matches architecture document
4. ✅ **THEN CLONE CLEAN** - Only clone once structures are correct

---

## 📋 RESTORATION TASKS

### **PRIORITY 1: investment_strategy Repository**

**CURRENT STATE**: Minimal/empty on GitHub  
**REQUIRED STRUCTURE**: 
```
investment_strategy/
├── README.md
├── projects/
│   └── PROJECT-001/
│       ├── PROJECT-001_portfolio_management_system.md
│       └── SYSTEM-001-05_rebalancing_automation/
│           ├── SYSTEM-001-05_rebalancing_automation.md
│           └── features/
│               └── FEATURE-001-05-02_automated_rebalancing_execution.md
└── requirements/
    └── investment_requirements.md
```

**EVIDENCE SOURCE**: 15+ test files in control_tower reference this exact structure

**RESTORATION METHOD**:
1. Create project structure locally in control_tower
2. Copy content from control_tower evidence 
3. Push to GitHub investment_strategy repo
4. Verify structure matches references

---

### **PRIORITY 2: professional_excellence Repository**

**CURRENT STATE**: Just README.md on GitHub  
**REQUIRED STRUCTURE**:
```
professional_excellence/
├── README.md  
├── contract_projects/
│   ├── projects/
│   │   └── Safran/
│   │       └── 3_ZnNi_Line_Post_Stabilization_Optimization/
│   │           └── SF_Documentation_Inc_Training_Optimization/
│   │               └── NADCAP Analysis/
│   │                   ├── nadcap_requirements.xlsx
│   │                   ├── compliance_analysis.py
│   │                   └── test_nadcap_extraction.py
│   └── xml_workspace/
│       ├── current/
│       └── snapshots/
└── requirements/
    └── professional_requirements.md
```

**EVIDENCE SOURCE**: test files, monitoring configs, and workflow scripts reference this structure

**RESTORATION METHOD**:
1. Extract Safran/NADCAP work from control_tower src/tools/integration/
2. Recreate contract_projects structure
3. Move NADCAP analysis tools to correct location
4. Push to GitHub professional_excellence repo

---

### **PRIORITY 3: business_ventures Repository**

**CURRENT STATE**: Minimal on GitHub  
**REQUIRED STRUCTURE**:
```
business_ventures/
├── README.md
├── Causal_affect/
│   ├── README.md
│   └── (content from separate Causal_affect repo)
├── opti_royale/
│   ├── README.md  
│   ├── services/
│   └── (content from separate opti_royale repo)
└── financial_optimizer/
    ├── README.md
    └── (content from separate financial_optimizer repo)
```

**EVIDENCE SOURCE**: Repository consolidation plan and hierarchy reports

**RESTORATION METHOD**:
1. Clone separate repos (Causal_affect, opti_royale, financial_optimizer) 
2. Move content into business_ventures structure
3. Push consolidated structure to GitHub
4. Archive separate repos (don't delete - keep as backup)

---

## 🛠️ IMPLEMENTATION STEPS

### **STEP 1: Create Restoration Scripts**
```bash
# restore_investment_strategy.sh
# restore_professional_excellence.sh  
# restore_business_ventures.sh
# verify_structures.sh
```

### **STEP 2: Execute Restoration**
```bash
./restore_investment_strategy.sh
./restore_professional_excellence.sh
./restore_business_ventures.sh
```

### **STEP 3: Verify Alignment**
```bash
./verify_structures.sh
```

### **STEP 4: Update Architecture Document**
```bash
# Update CONTROL_TOWER_UNIFIED_WORKSPACE_ARCHITECTURE.md
# Mark structures as "RESTORED" instead of "NEEDS RESTORATION"
```

---

## 🔍 VERIFICATION CRITERIA

**Each repository must have**:
- ✅ Proper project/system/feature hierarchy
- ✅ All referenced files from control_tower tests
- ✅ README.md explaining structure
- ✅ Requirements documentation
- ✅ Evidence trail of restoration

**Success Criteria**:
- ✅ All test file references resolve correctly
- ✅ Architecture document matches GitHub reality
- ✅ No broken paths in control_tower references
- ✅ NADCAP TDD work accessible in professional_excellence

---

## 🚨 SAFETY MEASURES

**Before restoration**:
- ✅ Create backup of current GitHub state
- ✅ Document what currently exists
- ✅ Create restoration evidence log

**During restoration**:
- ✅ One repository at a time
- ✅ Verify each step before proceeding
- ✅ Log all operations with evidence

**After restoration**:
- ✅ Test sync workflow with restored structures
- ✅ Verify NADCAP TDD work is accessible
- ✅ Update protection system to monitor new structures

---

**NEXT ACTION**: Create restoration scripts starting with investment_strategy