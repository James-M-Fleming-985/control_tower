# Control Tower - Project Management Hub

A unified project management system supporting both modern MS Project integration and legacy CSV-based workflows.

## 🚀 Quick Start

```bash
# Check project status (MS Project)
python3 control_tower.py ms-project --action status

# View current milestones
python3 control_tower.py ms-project --action milestones

# Quick help
python3 control_tower.py util help
```

## 📁 Project Structure

```
control_tower/
├── control_tower.py           # Main entry point
├── modules/
│   ├── ms_project/            # MS Project integration (Primary)
│   │   ├── contract_project_manager.py
│   │   ├── ms_project_integration.py
│   │   └── auto_sync_scheduler.py
│   └── csv_system/            # Legacy CSV system
│       ├── quick_query.py
│       ├── column_mapping.py
│       └── standardize_csv_files.py
├── scripts/                   # Helper scripts
│   ├── control_tower_help.sh
│   ├── demo.sh
│   └── safe_github_update.py
├── utils/                     # Utilities
│   ├── date_utils.py
│   └── roadmap_manager.py
├── docs/                      # Documentation
├── cloned_repos/              # Managed repositories
└── todos/                     # Generated reports
```

## 🎯 MS Project System (Recommended)

The primary system for modern project management using MS Project integration.

### Setup
1. Export your MS Project file as XML to: `cloned_repos/contract_projects/xml_workspace/`
2. Run status check: `python3 control_tower.py ms-project --action status`

### Commands
- `python3 control_tower.py ms-project --action status` - Project overview
- `python3 control_tower.py ms-project --action milestones` - Current milestones  
- `python3 control_tower.py ms-project --action sync` - Sync from MS Project
- `python3 control_tower.py ms-project --action update --task "Task Name" --progress 75` - Update progress

## 📊 CSV System (Legacy)

Original CSV-based system for backwards compatibility.

### Commands
- `python3 control_tower.py csv today` - What's due today
- `python3 control_tower.py csv week` - What's due this week
- `python3 control_tower.py csv overdue` - Overdue tasks
- `python3 control_tower.py csv milestones` - Upcoming milestones
- `python3 control_tower.py csv tasks --person "Name"` - Personal tasks

## 🛠️ Utilities

- `python3 control_tower.py util help` - Show help
- `python3 control_tower.py util demo` - Demo functionality
- `python3 control_tower.py util roadmap` - Development roadmap

## 🔧 Development

### Current Focus
- MS Project integration and automation
- PowerPoint report generation
- Contract project workflow optimization

### Adding New Features
1. Add modules to appropriate directory (`modules/ms_project/` or `modules/csv_system/`)
2. Update `__init__.py` files to export new functionality
3. Add commands to `control_tower.py` main interface

## 📋 Notes

- **MS Project System**: Modern, recommended approach with XML integration
- **CSV System**: Legacy support for existing workflows
- **Unified Interface**: Single `control_tower.py` entry point for all functionality
- **Organized Structure**: Modular design for easy maintenance and extension
