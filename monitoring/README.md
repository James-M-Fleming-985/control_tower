# Monitoring

**Purpose**: XML file monitoring and change detection scripts

## Scripts

### `monitor_xml_changes.py`
- **Purpose**: Real-time monitoring of XML file changes
- **Function**: Detects changes in project XML files and triggers automated updates
- **Features**:
  - Continuous file monitoring
  - Change detection and analysis
  - Automatic PowerPoint regeneration
  - Change management integration

## Usage

### Continuous Monitoring
```bash
cd /workspaces/control_tower
python monitoring/monitor_xml_changes.py --watch
```

### Single Check
```bash
python monitoring/monitor_xml_changes.py --check
```

### Force Update
```bash
python monitoring/monitor_xml_changes.py --force-update
```

## Features

- **File Watching**: Monitors XML files for timestamp/content changes
- **Change Analysis**: Identifies specific changes (milestones, dates, progress)
- **Auto-Update**: Triggers PowerPoint regeneration when changes detected
- **State Tracking**: Maintains monitoring state between runs
- **Integration**: Works with change management workflows

## Configuration

- **Monitored File**: `/cloned_repos/contract_projects/xml_workspace/current/ZnNi Line Development Plan-08.xml`
- **State File**: `/data/.xml_monitor_state.json`
- **Output**: Updated presentations in `/powerpoint_reports/`

## Dependencies

- **PowerPoint Scripts**: `/powerpoint/` folder for regeneration
- **Change Management**: Integration with milestone tracking systems
