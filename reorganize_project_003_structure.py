#!/usr/bin/env python3
"""
Reorganize PROJECT-003 to proper hierarchy: PROJECT → SYSTEM → FEATURE → LAYER
"""

from pathlib import Path
import shutil
import yaml

# Paths
PROJECT_ROOT = Path("/workspaces/professional_excellence/projects/PROJECT-003 REPORT GENERATOR")
SYSTEM_NAME = "SYSTEM-003_ZnNi_Report_Generation"
SYSTEM_ROOT = PROJECT_ROOT / SYSTEM_NAME

# Feature information with proper traceability
FEATURES = [
    {
        "id": "FEATURE-003-001",
        "name": "Data Reader Parser",
        "code": "DATA_PARSER",
        "description": "Reads and parses YAML/XML configuration files for report generation",
        "business_value": [
            "Enables configuration-driven report customization",
            "Validates data integrity before processing",
            "Supports multiple configuration formats"
        ],
        "user_story": "As a Report User, I want to configure report parameters via YAML/XML files, So that I can customize reports without code changes.",
        "prj_reqs": ["PRJ-REQ-001"],
        "sys_reqs": ["SYS-REQ-001", "SYS-REQ-008"],
        "layers": ["LAYER-001_YAML_XML_Reader", "LAYER-002_Data_Model_Validator", "LAYER-003_Schema_Compliance_Checker"]
    },
    {
        "id": "FEATURE-003-002",
        "name": "Risk Aggregator",
        "code": "RISK_AGG",
        "description": "Aggregates and formats risk data from all project folders for inclusion in reports",
        "business_value": [
            "Centralizes risk visibility across all projects",
            "Automates risk report generation",
            "Prioritizes risks by severity"
        ],
        "user_story": "As a Project Manager, I want to see all active risks aggregated in one report, So that I can prioritize mitigation efforts.",
        "prj_reqs": ["PRJ-REQ-002"],
        "sys_reqs": ["SYS-REQ-001", "SYS-REQ-004"],
        "layers": ["LAYER-001_Risk_File_Reader", "LAYER-002_Risk_Filter_Logic", "LAYER-003_Risk_Table_Formatter"]
    },
    {
        "id": "FEATURE-003-003",
        "name": "Gantt Chart Generator",
        "code": "GANTT_GEN",
        "description": "Generates Gantt chart visualizations for project timelines using matplotlib",
        "business_value": [
            "Visual timeline representation for stakeholders",
            "Automated chart generation from project data",
            "Professional-quality image export"
        ],
        "user_story": "As a Stakeholder, I want to see project timelines as Gantt charts, So that I can understand schedule status at a glance.",
        "prj_reqs": ["PRJ-REQ-002", "PRJ-REQ-005"],
        "sys_reqs": ["SYS-REQ-004", "SYS-REQ-007"],
        "layers": ["LAYER-001_Chart_Data_Preparation", "LAYER-002_Matplotlib_Chart_Builder", "LAYER-003_Image_Export"]
    },
    {
        "id": "FEATURE-003-004",
        "name": "Milestone Tracker",
        "code": "MILESTONE_TRK",
        "description": "Tracks and categorizes project milestones, formatting them for quadrant-based display",
        "business_value": [
            "Highlights critical upcoming milestones",
            "Categorizes milestones by timeframe",
            "Enables proactive milestone management"
        ],
        "user_story": "As a Project Manager, I want milestones organized by timeframe, So that I can focus on upcoming critical dates.",
        "prj_reqs": ["PRJ-REQ-002", "PRJ-REQ-003"],
        "sys_reqs": ["SYS-REQ-004", "SYS-REQ-005"],
        "layers": ["LAYER-001_Date_Calculator", "LAYER-002_Milestone_Categorizer", "LAYER-003_Quadrant_Formatter"]
    },
    {
        "id": "FEATURE-003-005",
        "name": "Change Management Logger",
        "code": "CHANGE_LOG",
        "description": "Interactive terminal UI for capturing and logging significant project changes",
        "business_value": [
            "Provides audit trail of key decisions",
            "Enables change management documentation",
            "Structured change capture process"
        ],
        "user_story": "As a Project Manager, I want to log significant changes interactively, So that we maintain a clear change history.",
        "prj_reqs": ["PRJ-REQ-004"],
        "sys_reqs": ["SYS-REQ-003"],
        "layers": ["LAYER-001_Terminal_UI", "LAYER-002_Change_Data_Collector", "LAYER-003_Log_File_Writer"]
    },
    {
        "id": "FEATURE-003-006",
        "name": "PowerPoint Generator",
        "code": "PPT_GEN",
        "description": "Assembles all report components into a branded PowerPoint presentation",
        "business_value": [
            "Professional branded presentations",
            "Automated report assembly",
            "Consistent formatting and styling"
        ],
        "user_story": "As a Report User, I want a complete PowerPoint generated automatically, So that I can present to stakeholders immediately.",
        "prj_reqs": ["PRJ-REQ-001", "PRJ-REQ-002", "PRJ-REQ-005"],
        "sys_reqs": ["SYS-REQ-004", "SYS-REQ-006", "SYS-REQ-007"],
        "layers": ["LAYER-001_Slide_Factory", "LAYER-002_Theme_Applier", "LAYER-003_Content_Inserter", "LAYER-004_Report_Assembler"]
    }
]


def create_feature_requirements_index(feature_info, feature_path):
    """Create FEATURE_REQUIREMENTS_INDEX.yaml for a feature"""
    
    content = f"""# ============================================================================
# FEATURE REQUIREMENTS INDEX: {feature_info['name']}
# ============================================================================
# FEATURE ID: {feature_info['id']}
# VERSION: 1.0.0
# LAST UPDATED: 2025-10-17
# OWNER: James Fleming
# ============================================================================

metadata:
  feature_id: "{feature_info['id']}"
  feature_name: "{feature_info['name']}"
  feature_code: "{feature_info['code']}"
  version: "1.0.0"
  status: "Active"
  created_date: "2025-10-17"
  last_modified: "2025-10-17"
  owner: "James Fleming"
  priority: "MUST HAVE"
  target_date: "2025-10-31"

# ============================================================================
# FEATURE OVERVIEW
# ============================================================================

overview:
  description: |
    {feature_info['description']}
  
  business_value:
"""
    
    for bv in feature_info['business_value']:
        content += f'    - "{bv}"\n'
    
    content += f"""  
  user_story: |
    {feature_info['user_story']}
  
  acceptance_criteria:
    - "All layers build successfully with TDD"
    - "Integration tests pass across all layers"
    - "Performance meets system requirements"
    - "Code coverage > 90%"

# ============================================================================
# LAYER ARCHITECTURE
# ============================================================================

layers:
"""
    
    for idx, layer_name in enumerate(feature_info['layers'], 1):
        layer_id = f"LAYER-{idx:03d}"
        layer_title = layer_name.replace(f"LAYER-{idx:03d}_", "").replace("_", " ")
        req_id = f"REQ-003-{feature_info['id'][-3:]}-{idx:03d}"
        
        content += f"""  - layer_id: "{layer_id}"
    layer_name: "{layer_title}"
    responsibility: "See {req_id}.yaml for detailed requirements"
    requirements:
      - {req_id}
  
"""
    
    content += f"""# ============================================================================
# FEATURE REQUIREMENTS
# ============================================================================

requirements:
  - id: "FEAT-REQ-001"
    title: "{feature_info['name']} Core Functionality"
    description: "Implements complete {feature_info['name']} feature with all layers integrated"
    priority: "MUST HAVE"
    status: "Active"
    traces_to:
      project_requirements: {feature_info['prj_reqs']}
      system_requirements: {feature_info['sys_reqs']}
  
  - id: "FEAT-REQ-002"
    title: "Layer Integration"
    description: "All layers work together seamlessly with proper error handling and data flow"
    priority: "MUST HAVE"
    status: "Active"
    traces_to:
      project_requirements: {feature_info['prj_reqs']}
      system_requirements: ["SYS-REQ-004"]

# ============================================================================
# INTEGRATION POINTS
# ============================================================================

integration:
  upstream_features: []
  downstream_features: []
  shared_components:
    - "src/shared/models"
    - "src/shared/exceptions"
    - "src/shared/utils"

# ============================================================================
# TESTING STRATEGY
# ============================================================================

testing:
  unit_tests:
    location: "tests/unit/"
    coverage_target: "90%"
  
  integration_tests:
    location: "tests/integration/"
    scenarios:
      - "Layer-to-layer integration"
      - "Error propagation"
      - "Data transformation pipeline"
  
  e2e_tests:
    location: "tests/e2e/"
    scenarios:
      - "Complete feature workflow"

# ============================================================================
# DEPLOYMENT
# ============================================================================

deployment:
  dependencies: []
  configuration_required: []
  deployment_steps:
    - "Run layer unit tests"
    - "Run integration tests"
    - "Deploy feature module"
    - "Verify E2E tests"

# ============================================================================
# END OF FEATURE REQUIREMENTS INDEX
# ============================================================================
"""
    
    output_file = feature_path / "FEATURE_REQUIREMENTS_INDEX.yaml"
    output_file.write_text(content)
    print(f"  ✅ Created {output_file.name}")


def reorganize_structure():
    """Reorganize PROJECT-003 structure"""
    
    print("=" * 80)
    print("PROJECT-003 Structure Reorganization")
    print("=" * 80)
    print()
    
    # Step 1: Create SYSTEM directory
    print(f"📁 Creating SYSTEM directory: {SYSTEM_NAME}")
    SYSTEM_ROOT.mkdir(exist_ok=True)
    print()
    
    # Step 2: Move SYSTEM_REQUIREMENTS.yaml to SYSTEM root
    print("📄 Moving SYSTEM_REQUIREMENTS.yaml to SYSTEM root")
    sys_req_source = PROJECT_ROOT / "SYSTEM_REQUIREMENTS.yaml"
    sys_req_dest = SYSTEM_ROOT / "SYSTEM_REQUIREMENTS.yaml"
    if sys_req_source.exists():
        shutil.move(str(sys_req_source), str(sys_req_dest))
        print(f"  ✅ Moved to {sys_req_dest.relative_to(PROJECT_ROOT)}")
    print()
    
    # Step 3: Move all FEATURE directories into SYSTEM
    print("📦 Moving FEATURE directories into SYSTEM")
    for feature_info in FEATURES:
        feature_id = feature_info['id']
        old_feature_path = PROJECT_ROOT / f"{feature_id}_{feature_info['name'].replace(' ', '_')}"
        new_feature_path = SYSTEM_ROOT / f"{feature_id}_{feature_info['name'].replace(' ', '_')}"
        
        if old_feature_path.exists():
            print(f"  Moving {old_feature_path.name}...")
            shutil.move(str(old_feature_path), str(new_feature_path))
            print(f"    ✅ Moved to SYSTEM/{new_feature_path.name}")
            
            # Create FEATURE_REQUIREMENTS_INDEX.yaml
            print(f"    📝 Creating FEATURE_REQUIREMENTS_INDEX.yaml...")
            create_feature_requirements_index(feature_info, new_feature_path)
    print()
    
    # Step 4: Create SYSTEM README
    print("📝 Creating SYSTEM README.md")
    system_readme = SYSTEM_ROOT / "README.md"
    system_readme.write_text(f"""# SYSTEM-003: ZnNi Line Report Generation System

## Overview
Automated PowerPoint report generation system for ZnNi plating line operations.

## Features
This system contains {len(FEATURES)} features:

""" + "\n".join([f"{i+1}. **{f['id']}**: {f['name']}" for i, f in enumerate(FEATURES)]) + f"""

## Structure
Each feature follows the hierarchy:
- FEATURE_REQUIREMENTS_INDEX.yaml (feature-level requirements)
- LAYER-XXX directories (layer implementations)
  - REQ-XXX-XXX-XXX.yaml (layer requirements)
  - src/ (implementation)
  - tests/ (tests)

## Traceability
All features trace to:
- PROJECT_REQUIREMENTS.yaml (project level)
- SYSTEM_REQUIREMENTS.yaml (system level)
- FEATURE_REQUIREMENTS_INDEX.yaml (feature level)
- REQ-XXX-XXX-XXX.yaml (layer level)

## Build Instructions
Use build_feature.py with FEATURE_REQUIREMENTS_INDEX.yaml:
```bash
python build_feature.py "SYSTEM-003_ZnNi_Report_Generation/FEATURE-003-001_Data_Reader_Parser/FEATURE_REQUIREMENTS_INDEX.yaml"
```
""")
    print(f"  ✅ Created {system_readme.relative_to(PROJECT_ROOT)}")
    print()
    
    print("=" * 80)
    print("✅ Reorganization Complete!")
    print("=" * 80)
    print()
    print("New Structure:")
    print(f"  {PROJECT_ROOT.name}/")
    print(f"    ├── PROJECT_REQUIREMENTS.yaml")
    print(f"    ├── {SYSTEM_NAME}/")
    print(f"    │   ├── SYSTEM_REQUIREMENTS.yaml")
    print(f"    │   ├── README.md")
    for feature in FEATURES:
        feature_name = f"{feature['id']}_{feature['name'].replace(' ', '_')}"
        print(f"    │   ├── {feature_name}/")
        print(f"    │   │   ├── FEATURE_REQUIREMENTS_INDEX.yaml")
        print(f"    │   │   └── LAYER-XXX/ (with REQ-XXX-XXX-XXX.yaml)")
    print(f"    ├── src/ (shared source)")
    print(f"    ├── tests/ (shared tests)")
    print(f"    └── config/ (project config)")


if __name__ == "__main__":
    reorganize_structure()
