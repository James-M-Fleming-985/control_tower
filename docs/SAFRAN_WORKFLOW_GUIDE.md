# Safran Complete Workflow - Single Command Operation

## Overview
Complete end-to-end workflow for Safran PowerPoint generation with MS Project synchronization. This system automatically detects MS Project updates, syncs XML data, and generates professional Safran-branded presentations.

## Single Command Usage

### Quick Start
```bash
# Basic workflow for contract_projects (Safran)
python scripts/safran_workflow.py

# Alternative using shell script
./scripts/safran.sh
```

### Advanced Options
```bash
# Force sync even if XML appears current
python scripts/safran_workflow.py --force-sync

# Work with different repository
python scripts/safran_workflow.py --repo LIMS_concept_actual

# Combined options
python scripts/safran_workflow.py --repo contract_projects --force-sync
```

## Complete Workflow Steps

### 1. MS Project Sync
- **Automatic Detection**: Checks ms_project_data folder for newer .xml or .mpp files
- **Smart Sync**: Only syncs if MS Project files are newer than XML workspace
- **File Support**: Handles .xml exports directly, reports .mpp files for manual export
- **Timestamp Tracking**: Compares file modification times for sync decisions

### 2. XML Processing
- **Real Data**: Uses actual MS Project XML with 1000+ tasks
- **Phase Mapping**: Maps XML hierarchy to Safran phases
- **Progress Tracking**: Extracts actual progress percentages
- **Filter Logic**: Shows in-progress projects (0% < progress < 100%)

### 3. PowerPoint Generation
- **Professional Format**: 12-slide Safran-branded presentation
- **Timeline Graphics**: Visual progress bars with actual project data
- **4-Table Layout**: Milestones, risks, and status tables
- **Date Stamping**: Automatic filename with current date

### 4. Output Management
- **Organized Storage**: Saves to Safran organization folder in powerpoint_reports
- **Consistent Naming**: REACh_ZnNi_Line_Flash_Report_DDMMYYYY_ControlTower.pptx
- **Ready Distribution**: Professional format ready for stakeholder review

## File Structure
```
cloned_repos/contract_projects/
├── ms_project_data/              # Place updated MS Project exports here
│   └── ZnNi_Line_Plan_updated.xml
├── xml_workspace/                # Synchronized XML workspace
│   └── ZnNi Line Development Plan-08.xml
└── projects/Safran/powerpoint_reports/  # Generated Safran presentations
    └── REACh_ZnNi_Line_Flash_Report_31072025_ControlTower.pptx
```

## MS Project Update Workflow

### For Real Updates:
1. Export updated XML from MS Project
2. Place in `cloned_repos/contract_projects/ms_project_data/`
3. Run workflow: `python scripts/safran_workflow.py`
4. System detects newer file and syncs automatically

### For Testing:
```bash
# Simulate MS Project update
python scripts/simulate_ms_project_update.py

# Run workflow to see sync in action
python scripts/safran_workflow.py
```

## Repository Support
The workflow supports multiple repositories with repository-specific configurations:

- **contract_projects**: Safran ZnNi Line Development Plan
- **LIMS_concept_actual**: Laboratory Information Management System
- **financial_optimizer**: Financial Optimization Platform
- **domain_specific-network_dev**: Network Development Infrastructure
- **financial_security_dev**: Financial Security Development
- **home_improvements**: Home Improvement Platform
- **opti_royale**: Optimization Gaming Platform
- **relationship_building**: Professional Relationship Management

## Sync Status Messages

### ✅ XML is current, no sync needed
- XML workspace is up to date
- No MS Project files found or XML is newer
- Proceeds directly to presentation generation

### 🔄 Sync needed: mpp_newer
- MS Project file is newer than XML workspace
- Automatic sync will be performed
- XML workspace will be updated

### 🔄 Force sync requested
- User specified --force-sync flag
- Sync performed regardless of timestamps
- Useful for troubleshooting or manual updates

### ❌ No MS Project files to sync from
- ms_project_data folder is empty
- Using existing XML data for presentation
- Place updated MS Project exports in ms_project_data folder

## Output Example
```
🚀 SAFRAN COMPLETE WORKFLOW
==================================================
📅 Date: 2025-07-31 12:11:26
📁 Repository: contract_projects

🔄 MS PROJECT SYNC CHECK
========================================
📁 Repository: contract_projects
📄 XML File: ZnNi Line Development Plan-08.xml
✅ XML exists: 07/30 09:03
📊 MS Project files found: 1
   • ZnNi_Line_Plan_updated.xml (07/31 12:11)
🔄 Sync needed: mpp_newer
📥 Syncing from: ZnNi_Line_Plan_updated.xml
✅ MS Project sync completed

📊 SAFRAN PRESENTATION GENERATION
=============================================
📋 Found 1038 tasks in XML for contract_projects
📊 Parsed 1037 projects from contract_projects XML
✅ Presentation generated: REACh_ZnNi_Line_Flash_Report_31072025_ControlTower.pptx

🎯 WORKFLOW COMPLETED SUCCESSFULLY!
==================================================
✅ MS Project synced to XML workspace
✅ Safran presentation generated
📄 File: REACh_ZnNi_Line_Flash_Report_31072025_ControlTower.pptx
📁 Location: /workspaces/control_tower/cloned_repos/contract_projects/powerpoint_reports
```

## Integration with Existing Systems
- **Control Tower**: Central orchestration from control_tower repository
- **Repository Structure**: Each repository maintains independent powerpoint_reports folder
- **Data Sources**: Real MS Project XML with actual task hierarchy and progress
- **Timeline Graphics**: Professional visual progress indicators
- **Safran Branding**: Corporate colors, logos, and formatting standards

## Troubleshooting

### Import Errors
If SafranPowerPointGenerator import fails:
```bash
pip install python-pptx
```

### Sync Issues
- Check ms_project_data folder permissions
- Verify XML file format (MS Project export)
- Use --force-sync to override timestamp checks

### Missing Files
- Ensure repository structure exists
- Run setup_xml_workspaces.py if needed
- Check file paths match repository naming

## Next Steps After Generation
1. Open presentation from powerpoint_reports folder
2. Review timeline graphics with current project data  
3. Append additional slides as needed
4. Distribute to stakeholders
5. Update MS Project and re-run workflow for next reporting cycle
