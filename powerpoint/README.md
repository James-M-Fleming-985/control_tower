# PowerPoint Generation

**Purpose**: PowerPoint presentation generation scripts for Control Tower workflows

## Scripts

### `advanced_dashboard_creation.py`
- **Purpose**: Advanced PowerPoint dashboard generation  
- **Function**: Creates professional Safran-branded presentations with milestone data
- **Usage**: Called by `friday_workflow.py` (primary method)
- **Output**: Professional PowerPoint presentations in `/powerpoint_reports/`

### `word_to_powerpoint_dashboard.py`
- **Purpose**: Alternative PowerPoint generation method
- **Function**: Fallback PowerPoint creation when advanced method fails
- **Usage**: Called by `friday_workflow.py` (fallback method)
- **Output**: PowerPoint presentations with Word-based formatting

## Usage

These scripts are typically called automatically by the Friday workflow:

```bash
# Primary usage (via Friday workflow)
cd /workspaces/control_tower  
python workflows/friday_workflow.py --friday-update

# Direct usage (if needed)
python powerpoint/advanced_dashboard_creation.py
python powerpoint/word_to_powerpoint_dashboard.py
```

## Dependencies

- **Data Source**: XML files in `/cloned_repos/contract_projects/xml_workspace/current/`
- **Output Location**: `/cloned_repos/contract_projects/powerpoint_reports/`
- **Branding**: Safran corporate templates and styling

## Output Format

- **Filename**: `REACh_ZnNi_Line_Flash_Report_YYYYMMDD.pptx`
- **Content**: Current milestones, progress updates, change summaries
- **Format**: Professional Safran-branded presentation template
