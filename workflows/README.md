# Workflows

**Purpose**: Core Control Tower workflow scripts

## Scripts

### `friday_workflow.py`
- **Purpose**: Complete Friday workflow automation
- **Function**: XML comparison, PowerPoint generation, change management
- **Usage**: `python workflows/friday_workflow.py --friday-update`
- **Dependencies**: PowerPoint generation scripts in `/powerpoint/`

### `milestone_management.py`  
- **Purpose**: Milestone management functionality
- **Function**: Milestone tracking and reporting capabilities
- **Usage**: Used by other scripts for milestone operations

## Dependencies

- **PowerPoint Generation**: `/powerpoint/` folder
- **XML Workspace**: `/cloned_repos/contract_projects/xml_workspace/`
- **Core Modules**: `/modules/` folder

## Usage

All workflow scripts should be run from the project root directory:

```bash
cd /workspaces/control_tower
python workflows/[script_name].py [arguments]
```
