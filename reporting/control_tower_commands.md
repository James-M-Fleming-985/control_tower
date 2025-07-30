# Control Tower Queries

**Last Updated**: 2025-07-30 15:30:00

Copy and paste these commands to quickly rerun reports:

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
