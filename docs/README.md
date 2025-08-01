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

## MS Project Integration Workflow

### Complete Single-Command Workflow

When you're ready to commit project changes:

```bash
## 🚀 Quick Start - Single Command Workflow with Milestone/Risk Tracking

The complete automated workflow with enhanced milestone and risk tracking:

```bash
# Execute complete workflow with change tracking
python push_project_update.py --description "Update SF Investment Strategy OEE & OLE Application timeline"
```

**What this single command does:**

1. **📊 Milestone & Risk Analysis**: Tracks changes to milestones and risks since last update
2. **📝 Change Management**: Opens terminal form for change documentation
3. **🔄 MS Project Integration**: Updates project files with changes
4. **📈 PowerPoint Generation**: Updates presentations with real milestone/risk change data

**Repository commits are handled separately** - use your normal git workflow when ready.

**Enhanced Features:**

- **Milestone Tracking**: Detects new, completed, modified, and rescheduled milestones
- **Risk Tracking**: Identifies new risks, resolved risks, and impact changes
- **Change History**: Maintains snapshots for comparison between updates
- **Smart Updates**: Only updates presentation tables when actual changes detected
- **Automated Documentation**: Includes milestone/risk changes in PowerPoint slides

**Milestone Change Detection:**
- ✅ New milestones added
- ✅ Milestones completed (status changed to Complete)
- ✅ Modified milestone dates or status
- ✅ Removed milestones

**Risk Change Detection:**
- ⚠️ New risks identified
- ✅ Risks resolved (status changed to Resolved/Closed)
- 📊 Risk impact level changes
- 🔄 Risk mitigation updates

**PowerPoint Table Updates:**
- This Month's Milestones
- Last Month's Completed Milestones
- Next Month's Milestones
- Risk Register (with real data from risk_register.csv)

All tables automatically update with real data when changes are detected.

**Separate Repository Workflow:**
```bash
# After workflow completion, commit when ready:
git add .
git commit -m "Project update with milestone/risk changes"
git push origin main
```
```

**What this command does:**
1. 🔗 Integrates XML changes into ZnNi Line Development Plan-08
2. 📋 Opens change management form in terminal (you fill this out)
3. 🔄 Updates MS Project integration and sync
4. 📊 Updates PowerPoint presentations (timelines, milestones, change slides)
5. 📤 Commits changes to repository

### Development Workflow

1. **Ask for help**: "Help me update the project to add/change XYZ"
2. **Review changes**: I generate/modify XML files based on your requirements  
3. **Commit changes**: Run `python push_project_update.py --description "What changed"`
4. **Fill form**: Change management form opens in terminal
5. **Done**: Everything else happens automatically!

### Quick Commands

```bash
# Show all available commands
python ms_project_help.py

# Test change management form only
python modules/ms_project/change_management.py request

# View recent changes  
python modules/ms_project/change_management.py recent --days 7

# Current milestones
python modules/ms_project/contract_project_manager.py --action milestones --period current
```

### Adding New Features
1. Add modules to appropriate directory (`modules/ms_project/` or `modules/csv_system/`)
2. Update `__init__.py` files to export new functionality
3. Add commands to `control_tower.py` main interface

## 📋 Notes

- **MS Project System**: Modern, recommended approach with XML integration
- **CSV System**: Legacy support for existing workflows
- **Unified Interface**: Single `control_tower.py` entry point for all functionality
- **Organized Structure**: Modular design for easy maintenance and extension
