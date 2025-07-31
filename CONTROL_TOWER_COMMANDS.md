# Control Tower Commands & Report Generation

**Last Updated**: July 31, 2025
**Vers### 🔍 For Management Updates
```bash
# Project status overvi### 🔍 For Management Updates
```bash
# Project status overview
python3 control_tower.py ms-project --action status --repository contract_projects
```

### 📊 For Monthly Stakeholder Presentations
```bash
# Simplest command: Complete workflow
./scripts/safran.sh
```control_tower.py ms-project --action status --repository contract_projects
```

## 🚀 **QUICK SCRIPTS FOR COMMON TASKS**

### 📋 Quick Milestone Report
```bash
# Generate current milestones (for team meetings)
./reports/quick_milestones.sh
```

### 🔍 Quick Status Report  
```bash
# Generate project status (for management updates)
./reports/quick_status.sh
```

### 🚨 Quick Overdue Report
```bash
# Generate overdue tasks (default: top 10)
./reports/quick_overdue.sh

# Generate extended overdue analysis (top 20)
./reports/quick_overdue.sh 20
```

### 📊 Quick Safran Presentation
```bash
# Simplest command: Complete workflow with alias
./scripts/safran.sh

# Complete workflow: MS Project sync + Presentation generation
python scripts/safran_workflow.py

# Manual generation only (uses existing XML)
./reports/generate_safran_presentation.sh
```

### 📦 Complete Report Suite (Optional)
```bash
# Generate ALL reports (use sparingly)
./reports/generate_all_reports.sh
```

### 📊 PowerPoint Reports Overview
```bash
# Show all powerpoint_reports folders and their contents
./reports/show_powerpoint_reports.sh
```

**Note**: Quick scripts provide targeted reports for specific use cases. Use the complete suite only when comprehensive reporting is needed.: 2.0 - Targeted Report Generation Commands

Copy and paste these commands to generate specific reports ready for download and dissemination:

## 🎯 **TARGETED REPORT GENERATION**

### 📊 Safran PowerPoint Presentation
*Generate professional 12-page Safran-branded presentation with latest MS Project data*

```bash
# Simplest command: Complete workflow (RECOMMENDED)
./scripts/safran.sh

# Complete end-to-end workflow
# Syncs MS Project → Updates XML → Generates presentation
cd /workspaces/control_tower
python scripts/safran_workflow.py

# Manual generation only (uses existing XML data)
python modules/milestone_management/reporting/safran_powerpoint_generator.py

# Alternative: Use convenience script
./reports/generate_safran_presentation.sh
```

**Complete Workflow Process**:
1. 🔄 Syncs latest MS Project file to XML workspace
2. 📊 Parses updated XML with 1000+ real project tasks
3. 🎯 Filters tasks by Safran phases and outline levels
4. 🎨 Generates 12-page Safran-branded presentation
5. 💾 Saves to `contract_projects/powerpoint_reports/` with datestamp

**Output**: `/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/powerpoint_reports/REACh_ZnNi_Line_Flash_Report_DDMMYYYY_ControlTower.pptx`
**Use Case**: Monthly stakeholder presentations, project reviews, executive briefings

### 📋 Current Milestone Reports
*Generate specific milestone timeframe reports*

```bash
# Current month milestones only
python3 control_tower.py ms-project --action milestones --period current

# Next month milestones only  
python3 control_tower.py ms-project --action milestones --period next

# Both current and next (for comprehensive planning)
python3 control_tower.py ms-project --action milestones --period both
```

**Output**: `/workspaces/control_tower/reporting/` (timestamped markdown files)
**Use Case**: Weekly planning, milestone tracking, team updates

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

## 🎯 **QUICK ACCESS COMMANDS BY USE CASE**

### 📅 For Weekly Team Meetings
```bash
# Generate current milestone status
python3 control_tower.py ms-project --action milestones --period current
```

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
