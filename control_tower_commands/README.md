# Control Tower Commands

**Purpose**: Essential command reference for Control Tower operations

## Documents

### `CONTROL_TOWER_COMMANDS.md` ⭐ **CURRENT**
- **Purpose**: Streamlined command reference (Version 4.0)
- **Content**: 3 essential commands for daily operations
- **Commands**:
  1. Current month milestones
  2. Next month milestones  
  3. Friday workflow
- **Status**: Active, up-to-date, simplified for daily use

### `CONTROL_TOWER_COMMANDS_BACKUP.md` 📚 **ARCHIVE**
- **Purpose**: Legacy command reference (Version 3.0)
- **Content**: Comprehensive historical commands and workflows
- **Status**: Archived for reference, not for daily use
- **Note**: Contains extensive historical documentation

## Quick Command Reference

### Essential Daily Commands
```bash
# 1. Current month milestones (includes overdue)
python3 control_tower.py ms-project --action milestones --period current

# 2. Next month milestones (for planning)
python3 control_tower.py ms-project --action milestones --period next

# 3. Friday workflow (weekly presentations)
python workflows/friday_workflow.py --friday-update
```

## File Structure Reference
```
/workspaces/control_tower/
├── control_tower.py                    # Main entry point
├── workflows/friday_workflow.py        # Friday workflow
├── cloned_repos/contract_projects/
│   ├── xml_workspace/current/          # Upload XML here
│   └── powerpoint_reports/             # Generated presentations
└── reporting/                          # Milestone reports
```

## Usage Notes

- **XML Data Source**: All commands read from `/xml_workspace/current/ZnNi Line Development Plan-08.xml`
- **Update Process**: Manually upload fresh XML exports from MS Project
- **Output Locations**: Reports in `/reporting/`, presentations in `/powerpoint_reports/`

---

**For detailed workflow documentation, see**: `/docs/CONTROL_TOWER_WORKFLOWS.md`
