# Control Tower Milestone Management System

Universal milestone change detection and reporting across all repositories with MS Project XML files.

## 🎯 Overview

This system provides automated milestone management capabilities that work across all Control Tower repositories:

- **Universal Repository Scanning**: Automatically discovers MS Project XML files in all repositories
- **Change Detection**: Compares milestone snapshots to detect additions, removals, and modifications
- **Cross-Project Reporting**: Generates PowerPoint presentations with data from all projects
- **Automated Monitoring**: Watches XML files for changes and triggers workflows automatically
- **Business Context Collection**: Prompts for reasons and contingencies when changes are detected

## 📁 Structure

```
modules/milestone_management/
├── __init__.py                     # Main module exports
├── cli.py                         # Command-line interface
├── core/
│   ├── __init__.py
│   ├── repository_scanner.py      # Discovers XML files across repos
│   └── milestone_detector.py      # Detects and manages changes
├── reporting/
│   ├── __init__.py
│   └── powerpoint_generator.py    # Creates PowerPoint presentations
└── automation/
    ├── __init__.py
    └── workflow_manager.py         # Manages automated workflows

milestone_management.py             # Simple main entry point
```

## 🚀 Quick Start

### Option 1: Simple Interface
```bash
cd /workspaces/control_tower
python milestone_management.py
```

### Option 2: Command Line Interface
```bash
# Scan all repositories for XML files
python -m modules.milestone_management.cli scan

# Detect changes across all repositories
python -m modules.milestone_management.cli detect

# Generate PowerPoint reports
python -m modules.milestone_management.cli report

# Start automated monitoring
python -m modules.milestone_management.cli monitor

# Check system status
python -m modules.milestone_management.cli status
```

### Option 3: Python API
```python
from modules.milestone_management import (
    RepositoryScanner, 
    MilestoneChangeDetector,
    PowerPointGenerator,
    WorkflowManager
)

# Scan repositories
scanner = RepositoryScanner()
repositories = scanner.scan_all_repositories()

# Detect changes
detector = MilestoneChangeDetector()
changes = detector.scan_all_repositories_for_changes()

# Generate reports
generator = PowerPointGenerator()
report_path = generator.generate_cross_project_report()

# Start automated monitoring
manager = WorkflowManager()
manager.start_automated_monitoring()
```

## 🔧 Installation

The system will automatically install dependencies when needed:

```bash
pip install watchdog python-pptx
```

## 📊 Features

### Repository Discovery
- Automatically finds all repositories in `/workspaces/control_tower/cloned_repos/`
- Locates MS Project XML files in common directories:
  - `xml_workspace/`
  - `project_files/`
  - `ms_project/`
  - `planning/`
  - Root directory and `projects/` subdirectory

### Change Detection
- **Baseline Creation**: Creates initial snapshots of all milestones
- **Change Types Detected**:
  - Milestone added/removed
  - Name changes
  - Date changes (start/finish)
  - Resource assignment changes
  - Completion percentage changes
- **Business Context**: Prompts for reason and contingency planning
- **Cross-Repository**: Works across all repositories simultaneously

### PowerPoint Generation
- **Cross-Project Reports**: Unified view of all repositories
- **Repository-Specific Reports**: Detailed reports per repository
- **Phase-Based Organization**: Categorizes milestones by project phase
- **Time-Based Sections**:
  - Milestones due this month
  - Milestones completed last month
  - Milestones due next month

### Automated Monitoring
- **File Watching**: Monitors all XML files for changes
- **Event-Driven**: Automatically triggers workflows on file modifications
- **Multi-Repository**: Watches multiple repositories simultaneously
- **Background Service**: Runs continuously with minimal resource usage

## 📈 Data Storage

All data is stored in `/workspaces/control_tower/data/milestone_management/`:

- `{repository}_{filename}_snapshot.pkl`: Milestone snapshots
- `{repository}_{filename}_changes.json`: Change logs with business context
- Reports saved to `/workspaces/control_tower/reports/milestone_presentations/`

## 🔄 Workflow Examples

### Daily Monitoring
1. Start automated monitoring: `python milestone_management.py` → Option 1
2. System watches all XML files across repositories
3. When changes detected:
   - User prompted for business context
   - Change logged with timestamp and reason
   - PowerPoint presentations automatically updated
   - Reports saved to reports directory

### Weekly Reporting
1. Generate reports: `python -m modules.milestone_management.cli report`
2. Creates cross-project presentation with:
   - Executive summary across all repositories
   - Repository breakdown
   - Phase-based milestone organization
   - Timeline views (this month, last month, next month)

### Project Status Checks
1. Check status: `python -m modules.milestone_management.cli status`
2. Shows:
   - Number of repositories being tracked
   - Total XML files monitored
   - Recent changes across all projects
   - System health indicators

## 🎯 Integration with Existing Systems

This new system **replaces** the standalone Safran-specific files and provides:

- **Broader Scope**: Works with all repositories, not just contract_projects
- **Unified Interface**: Single system for all milestone management
- **Future-Proof**: Automatically picks up new repositories as they're added
- **Scalable**: Handles multiple XML files per repository
- **Consistent**: Same workflow and reporting across all projects

## 📋 Migration from Old System

The standalone files in the Safran directory can be removed as this system provides all the same functionality plus:

- Multi-repository support
- Better organization
- More robust error handling
- Unified reporting
- Automated discovery

## 🚨 Important Notes

1. **First Run**: Will create baseline snapshots - no changes detected initially
2. **Dependencies**: System will prompt to install required packages
3. **File Locations**: Automatically discovers XML files in standard locations
4. **Business Context**: Always prompts for reasons when changes detected
5. **Cross-Repository**: Changes in any repository trigger cross-project report updates

## 💡 Best Practices

1. **Start Monitoring Early**: Begin automated monitoring to catch all changes
2. **Provide Good Context**: When prompted, give clear business reasons for changes
3. **Regular Reports**: Generate cross-project reports for executive updates
4. **Repository Naming**: Use clear repository names for better reporting
5. **XML Organization**: Keep XML files in standard directories for auto-discovery

This system provides enterprise-level milestone management across all your Control Tower repositories!
