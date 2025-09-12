# Control Tower Commands & Report Generation

**Last Updated**: August 8, 2025
**Version**: 3.0 - Friday Workflow & Updated Folder Structure

Copy and paste these commands to generate specific reports ready for download and dissemination:

## 📁 **UPDATED FOLDER STRUCTURE**

### **Key Folders for Friday Workflow:**
```
/workspaces/control_tower/
├── xml_imports_to_ms_project/           # NEW: XML exports for MS Project import
│   └── [RepoName]_[ProjectName]_[YYYYMMDD_HHMMSS].xml
├── cloned_repos/
│   └── contract_projects/
│       ├── xml_workspace/               # XML uploads from MS Project
│       │   └── ZnNi Line Development Plan-08.xml
│       └── powerpoint_reports/          # Generated PowerPoint presentations
│           └── REACh_ZnNi_Line_Flash_Report_[YYYYMMDD].pptx
└── friday_workflow.py                   # NEW: Main Friday workflow script
```

### **File Naming Conventions:**
- **PowerPoint Reports**: `REACh_ZnNi_Line_Flash_Report_YYYYMMDD.pptx`
- **XML Imports**: `[RepoName]_[ProjectName]_YYYYMMDD_HHMMSS.xml`
  - Example: `contract_projects_ZnNi_Line_Development_20250808_143022.xml`

## 🚀 **FRIDAY WORKFLOW COMMANDS** ✅ **WORKING**

### **Complete Friday Workflow** ✅ **CURRENT WORKING PROCESS**
```bash
# Step 1: Upload fresh XML export to ms_project_data folder
# (Manual step - upload your XML export from MS Project)

# Step 2: Auto-sync XML to current folder and create snapshots
python -m modules.ms_project.auto_sync_scheduler --once

# Step 3: Generate individual milestone slides (working perfectly)
python control_tower.py ms-project --action reports --period current

# Step 4: Generate comparison report vs last Friday (planned)
python control_tower.py friday --compare-to-last-week
```

**Current Working Process**:
1. **XML Upload**: Upload fresh XML export to `/ms_project_data/` folder
2. **Auto-Sync**: System automatically copies to `/current/` and creates snapshot in `/snapshots/`
3. **Individual Slides**: Generate perfect milestone slides (7 slides with professional formatting)
4. **Comparison**: Compare current vs previous Friday snapshot (in development)
5. **Output Files**: 
   - Individual PowerPoint slides: `powerpoint_reports/milestone_slides_YYYYMMDD/`
   - Combined dashboard: `REACh_ZnNi_Line_Flash_Report_YYYYMMDD.pptx` (4-table layout in progress)
   - XML Snapshot: `xml_workspace/snapshots/friday_YYYYMMDD_*`

### **Known Issues & Workarounds**:
- ✅ **Individual milestone slides**: Working perfectly with real data (87 milestones)
- 🔄 **4-table combined dashboard**: Technical layout issues being resolved
- ✅ **XML sync and snapshots**: Fully automated and working
- ✅ **Data extraction**: Flawless milestone detection and formatting

### **XML Export for MS Project Import**
```bash
# Generate XML file for MS Project import (new projects/bulk changes)
python generate_ms_project_import.py --repository contract_projects --project "New Project Name" --output xml_imports_to_ms_project/

# Output naming: contract_projects_New_Project_Name_20250808_143022.xml
```

## 🧹 **SCRIPT CLEANUP & LEGACY CODE**

### **Scripts to Keep (Still Needed):**
```
/scripts/
├── safran.sh                           # Legacy PowerPoint generation (backup)
├── safran_workflow.py                  # Core workflow logic (referenced by friday_workflow.py)
├── generate_safran_presentation.py     # PowerPoint generator (keep as module)
└── safran_tools/
    └── generate_final_powerpoint.py    # PowerPoint generation engine
```

### **Scripts to Remove (Redundant/Obsolete):**
```
/scripts/
├── create_clean_xml.py                 # REMOVE: Superseded by friday_workflow.py
├── create_corrected_simple.py          # REMOVE: Development testing script
├── create_replacement_xml.py           # REMOVE: Old XML manipulation
├── csv_to_ms_project_xml.py           # REMOVE: CSV conversion not used
├── demo.sh                             # REMOVE: Demo script
├── fix_xml_namespaces.py               # REMOVE: Fixed in core modules
├── generate_corrected_xml.py           # REMOVE: Superseded by friday_workflow.py
├── generate_final_xml.py               # REMOVE: Superseded by friday_workflow.py
├── restructure_sf_investment.py        # REMOVE: One-time script completed
├── setup_xml_workspaces.py             # REMOVE: Setup completed
├── simple_csv_to_xml.py                # REMOVE: CSV conversion not used
├── simple_csv_to_xml_fixed.py          # REMOVE: CSV conversion not used
├── simulate_ms_project_update.py       # REMOVE: Testing script
├── sync_all_repos.sh                   # REMOVE: Manual sync approach deprecated
├── test_converter.py                   # REMOVE: Testing script
├── universal_ms_project_generator.py   # REMOVE: Superseded by friday_workflow.py
├── universal_workflow.sh               # REMOVE: Superseded by friday_workflow.py
└── analysis_tools/                     # REMOVE: Development analysis tools
    └── testing_tools/                  # REMOVE: Development testing tools
```

### **Cleanup Commands:**
```bash
# Remove redundant scripts (recommended)
cd /workspaces/control_tower/scripts
rm -f create_clean_xml.py create_corrected_simple.py create_replacement_xml.py
rm -f csv_to_ms_project_xml.py demo.sh fix_xml_namespaces.py
rm -f generate_corrected_xml.py generate_final_xml.py restructure_sf_investment.py
rm -f setup_xml_workspaces.py simple_csv_to_xml.py simple_csv_to_xml_fixed.py
rm -f simulate_ms_project_update.py sync_all_repos.sh test_converter.py
rm -f universal_ms_project_generator.py universal_workflow.sh
rm -rf analysis_tools/ testing_tools/

# Keep essential scripts only
# Results in clean /scripts/ folder with only active workflow scripts
```

## 🎯 **CURRENT ACTIVE COMMANDS**

### **📊 Safran PowerPoint Presentation**
*Generate professional 12-page Safran-branded presentation with latest MS Project data*

```bash
# NEW: Friday workflow (RECOMMENDED)
python friday_workflow.py --friday-update

# Legacy: Complete workflow (BACKUP)
./scripts/safran.sh

# Manual generation only (uses existing XML data)
python scripts/generate_safran_presentation.py
```

**Output Location**: `/workspaces/control_tower/cloned_repos/contract_projects/powerpoint_reports/REACh_ZnNi_Line_Flash_Report_YYYYMMDD.pptx`
**Use Case**: Friday stakeholder presentations with change management

### 📋 Current Milestone Reports
*Generate specific milestone timeframe reports with overdue detection*

```bash
# Current month milestones only (includes overdue detection)
python3 control_tower.py ms-project --action milestones --period current

# Next month milestones only  
python3 control_tower.py ms-project --action milestones --period next

# Both current and next (for comprehensive planning)
python3 control_tower.py ms-project --action milestones --period both
```

**Features**:
- ✅ Dynamic month labels (shows actual current month)
- 🚨 Overdue milestone detection (marked with red alert icon)
- ⏳ Pending milestone tracking
- 📊 Resource assignment visibility
- 📅 Shows last XML sync time to verify data currency

**Output**: `/workspaces/control_tower/reporting/` (timestamped markdown files)
**Use Case**: Weekly planning, milestone tracking, team updates, overdue identification

**⚠️ Important**: If MS Project changes aren't reflected, run manual sync (see MS Project Sync Commands below)

### 🔍 Project Status Reports
*Generate targeted status information*

```bash
# Overall project health
python3 control_tower.py ms-project --action status

# Focus on overdue items (adjust limit as needed)
python3 control_tower.py ms-project --action overdue --limit 5

# Extended overdue analysis
python3 control_tower.py ms-project --action overdue --limit 20
```

**Output**: `/workspaces/control_tower/reporting/` (timestamped markdown files)
**Use Case**: Problem identification, urgent action items, management briefings

### 🔄 MS Project Sync Commands
*Two distinct sync processes: Background sync + Manual workflow execution*

#### **Background Sync (MS Project ↔️ Main XML)**
*Automatic sync to keep main XML file current - NO COMMAND NEEDED*
```bash
# ❓ VERIFICATION NEEDED: This should happen automatically
# Issue: Background sync appears broken (milestone reports not reflecting MS Project changes)
# When broken: Manual XML export required from MS Project to XML workspace
```

#### **Complete Workflow Execution (Manual)**
*Full workflow per WORKFLOW.md: XML integration → Remote MS Project → Change management → PowerPoint*
```bash
# NEW: Complete workflow with remote execution (RECOMMENDED)
python3 control_tower.py ms-project --action remote-sync

# Alternative: Direct workflow execution
python push_project_update.py --description "Your update description" --project "Project Name"

# Check remote configuration
python push_project_update.py --config-check
```

#### **Legacy Sync Commands (Troubleshooting)**
```bash
# Force sync from .mpp file (if available)
python3 control_tower.py ms-project --action force-sync

# Regular sync check
python3 control_tower.py ms-project --action sync
```

**🌟 NEW: Complete Workflow with Remote Execution**:
The `remote-sync` action provides a single command that:
1. **XML Integration**: Merges standalone project files into main XML
2. **Remote Execution**: Copies XML to Windows → Launches MS Project → Syncs back
3. **Change Management**: Terminal form for milestone change approval
4. **PowerPoint Generation**: Updates presentations with latest data
5. **Status Reporting**: Comprehensive workflow completion summary

**Cross-Platform Execution**:
- **Linux/Codespaces → Windows**: Automated remote execution via SSH/SCP
- **Local Windows**: Direct MS Project integration
- **WSL Environment**: Hybrid local/remote execution
- **Containerized**: Seamless connectivity to target Windows machine

**When Automatic Sync Fails** (configuration issues):
1. **Manual XML Export Required**: 
   - Open: `D:\Downloads\ZnNi Line Development Plan-08.mpp`
   - File → Export → Save as XML Format (.xml)
   - Save as: `/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml`
   
2. **Verify Sync Status**: The milestone commands will show last sync time
3. **Re-run Queries**: After manual export, milestone data will reflect latest MS Project changes

**Output**: Updated XML workspace + Remote MS Project sync + PowerPoint presentations
**Use Case**: Complete project update workflow, automated cross-platform sync, change management integration

## 🎯 **QUICK ACCESS COMMANDS BY USE CASE**

### 📅 For Weekly Team Meetings
```bash
# Generate current milestone status (includes overdue detection)
python3 control_tower.py ms-project --action milestones --period current

# Or complete workflow with latest sync
python3 control_tower.py ms-project --action remote-sync
```
**Shows**: Current month milestones with 🚨 overdue alerts and ⏳ pending status
**New**: Complete workflow option syncs latest data automatically

### 📊 For Monthly Stakeholder Presentations
```bash
# Generate Safran PowerPoint presentation
python modules/milestone_management/reporting/safran_powerpoint_generator.py
```

### 🚨 For Problem Resolution
```bash
# Check overdue tasks
python3 control_tower.py ms-project --action overdue --limit 10
```

### 📈 For Project Planning
```bash
# Review upcoming milestones
python3 control_tower.py ms-project --action milestones --period next
```

### 🔍 For Management Updates
```bash
# Project status overview
python3 control_tower.py ms-project --action status
```

### 📊 For Monthly Stakeholder Presentations
```bash
# Generate Safran PowerPoint presentation
python modules/milestone_management/reporting/safran_powerpoint_generator.py
```

### 🚨 For Problem Resolution
```bash
# Check overdue tasks
python3 control_tower.py ms-project --action overdue --limit 10 --repository contract_projects
```

### 📈 For Project Planning
```bash
# Review upcoming milestones
python3 control_tower.py ms-project --action milestones --period next --repository contract_projects
```

### � For Management Updates
```bash
# Project status overview
python3 control_tower.py ms-project --action status --repository contract_projects
```

## 🔧 Multi-Repository Support

The Control Tower now supports multiple repositories with XML files. Commands require:

- `--repository <repo_name>` - Target specific repository (e.g., contract_projects, financial_optimizer)
- `--xml-file <filename>` - Specify XML file when updating (for repos with multiple XML files)
- `--all-repos` - Query across all repositories with XML files

### Current Repository Structure:
- **contract_projects**: `ZnNi Line Development Plan-08.xml` (Safran project)
- **financial_optimizer**: (Ready for XML files when added)
- **Other repos**: (Will be auto-discovered when XML files are added)


## Milestones Queries
*Commands now support --repository parameter for multi-repo queries*

### Current Month Milestones
*First run: 2025-07-30 10:07:15 | Run count: 5*

```bash
# For Safran project
python3 control_tower.py ms-project --action milestones --period current --repository contract_projects

# For all repositories
python3 control_tower.py ms-project --action milestones --period current --all-repos
```

### Next Month Milestones
*First run: 2025-07-30 10:26:07 | Run count: 5*

```bash
# For Safran project
python3 control_tower.py ms-project --action milestones --period next --repository contract_projects

# For all repositories
python3 control_tower.py ms-project --action milestones --period next --all-repos
```

### Both Current and Next Month Milestones
*First run: 2025-07-30 11:45:44 | Run count: 1*

```bash
# For Safran project
python3 control_tower.py ms-project --action milestones --period both --repository contract_projects

# For all repositories
python3 control_tower.py ms-project --action milestones --period both --all-repos
```

## Overdue Queries
*Now supports multi-repository queries*

### Overdue Tasks Report
*First run: 2025-07-30 10:07:23 | Run count: 1*

```bash
# For Safran project
python3 control_tower.py ms-project --action overdue --limit 5 --repository contract_projects

# For all repositories
python3 control_tower.py ms-project --action overdue --limit 5 --all-repos
```

## Status Queries
*Now supports multi-repository status*

### Project Status Report
*First run: 2025-07-30 10:07:03 | Run count: 2*

```bash
# For Safran project
python3 control_tower.py ms-project --action status --repository contract_projects

# For all repositories
python3 control_tower.py ms-project --action status --all-repos
```

## XML Update Commands
*Commands now require --repository and --xml-file parameters for multi-repo support*

### Task Progress Update
*Updates task progress in XML (triggers change management)*

```bash
# For Safran project
python3 control_tower.py ms-project --action update --repository contract_projects --xml-file "ZnNi Line Development Plan-08.xml" --task "Task Name" --progress 75

# For other repositories (when XML files are added)
python3 control_tower.py ms-project --action update --repository financial_optimizer --xml-file "Financial_Project.xml" --task "Task Name" --progress 75
```

### Task Date Update
*Updates task finish date in XML*

```bash
# For Safran project
python3 control_tower.py ms-project --action update --repository contract_projects --xml-file "ZnNi Line Development Plan-08.xml" --task "Task Name" --finish-date "2025-08-15"
```

### Complete Task Update
*Marks task as 100% complete with dates*

```bash
# For Safran project
python3 control_tower.py ms-project --action update --repository contract_projects --xml-file "ZnNi Line Development Plan-08.xml" --task "Task Name" --progress 100 --start-date "2025-07-01" --finish-date "2025-07-30"
```

## Task Scheduler Commands

### Move Task to Date
*Reschedules task/milestone to specific date*

```bash
python3 task_scheduler.py move "Task Name" "2025-08-15"
```

### Delay Task by Days
*Delays task/milestone by number of days*

```bash
python3 task_scheduler.py delay "Task Name" 7
```

### Mark Task Complete
*Marks task as 100% complete*

```bash
python3 task_scheduler.py complete "Task Name"
```

### Update Task Progress
*Updates task progress percentage*

```bash
python3 task_scheduler.py progress "Task Name" 85
```

### Search for Tasks
*Find tasks matching search term*

```bash
python3 task_scheduler.py search "keyword"
```

## Automated Change Management
*Updated to use new unified milestone management system*

### Start File Watcher Service
*Automatically detects XML changes across all repositories*

```bash
# Monitor all repositories with XML files
python3 milestone_management.py
# Select option 1 - Start Automated Monitoring

# Or use CLI directly
python3 -m modules.milestone_management.cli monitor
```

### Manual Change Detection
*Run change detection across all repositories once*

```bash
# Detect changes in all repositories
python3 -m modules.milestone_management.cli detect

# Detect changes in specific repository
python3 -m modules.milestone_management.cli detect --repository contract_projects
```

### Generate PowerPoint Reports
*Create cross-project presentations*

```bash
# Generate report for all repositories
python3 -m modules.milestone_management.cli report

# Generate report for specific repository
python3 -m modules.milestone_management.cli report --repository contract_projects
```

### System Status Check
*Check status of milestone management system*

```bash
python3 -m modules.milestone_management.cli status
```

### Repository Scan
*Discover XML files across all repositories*

```bash
python3 -m modules.milestone_management.cli scan
```

---

## 📋 **COMMAND SUMMARY - QUICK REFERENCE**

### ⚡ **MOST USED COMMANDS**

#### 1. Complete Safran Presentation Workflow
```bash
# Simplest command - everything in one step
./scripts/safran.sh
```
**What it does**: MS Project sync → XML update → Safran presentation generation → Saves to powerpoint_reports/

#### 2. Weekly Milestone Tracking
```bash
python3 control_tower.py ms-project --action milestones --period current --repository contract_projects
```

#### 3. Problem Identification
```bash
python3 control_tower.py ms-project --action overdue --limit 10 --repository contract_projects
```

### 🎯 **WORKFLOW PROCESS**

The complete Safran workflow (`./scripts/safran.sh`) executes:

1. **🔄 MS Project Sync**: Checks for updated MS Project files in `ms_project_data/`
2. **📊 XML Update**: Syncs latest changes to `xml_workspace/ZnNi Line Development Plan-08.xml`
3. **🎨 Presentation Generation**: Creates 12-page Safran-branded PowerPoint
4. **💾 Output**: Saves timestamped presentation to `contract_projects/powerpoint_reports/`

**Output File**: `REACh_ZnNi_Line_Flash_Report_DDMMYYYY_ControlTower.pptx`

### 📁 **FILE LOCATIONS**

- **MS Project Source**: `/workspaces/control_tower/cloned_repos/contract_projects/ms_project_data/`
- **XML Workspace**: `/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/`
- **Generated Presentations**: `/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/powerpoint_reports/`
- **Command Scripts**: `/workspaces/control_tower/scripts/`

### 🚀 **QUICK COMMANDS BY USE CASE**

| Use Case | Command |
|----------|---------|
| 📊 Monthly Stakeholder Presentation | `./scripts/safran.sh` |
| 📅 Weekly Team Meeting | `python3 control_tower.py ms-project --action milestones --period current --repository contract_projects` |
| 🚨 Problem Resolution | `python3 control_tower.py ms-project --action overdue --limit 10 --repository contract_projects` |
| 📈 Project Planning | `python3 control_tower.py ms-project --action milestones --period next --repository contract_projects` |
| 🔍 Management Updates | `python3 control_tower.py ms-project --action status --repository contract_projects` |

---

**Control Tower Version**: 3.0 - Complete Safran Workflow Integration  
**Last Updated**: July 31, 2025
