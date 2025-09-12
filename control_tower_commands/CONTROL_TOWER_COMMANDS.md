# Control Tower Commands

**Last Updated**: September 1, 2025
**Version**: 4.0 - Streamlined Essential Commands

## 🎯 **ESSENTIAL COMMANDS**

### 1. 📋 **Current Month Milestones**
*Generate current month milestone report (includes uncompleted milestones from previous months)*

```bash
python3 control_tower.py ms-project --action milestones --period current
```

**Purpose**: Weekly team meetings, milestone tracking, overdue identification
**Output**: `/workspaces/control_tower/reporting/` (timestamped markdown files)
**Features**: 
- Shows current month milestones
- Includes overdue milestones from previous months (marked with 🚨)
- Dynamic month labels
- Resource assignment visibility
- Last XML sync time verification

### 2. 📅 **Next Month Milestones**
*Generate next month milestone preview for planning*

```bash
python3 control_tower.py ms-project --action milestones --period next
```

**Purpose**: Project planning, upcoming milestone preparation
**Output**: `/workspaces/control_tower/reporting/` (timestamped markdown files)
**Features**:
- Shows upcoming month milestones
- Resource planning visibility
- Schedule preview for planning meetings

### 3. 🏁 **Friday Workflow**
*Complete weekly workflow with XML comparison and PowerPoint generation*

```bash
python workflows/friday_workflow.py --friday-update
```

**Purpose**: Weekly stakeholder presentations, change management, progress tracking
**Output**: 
- PowerPoint presentation: `/workspaces/control_tower/cloned_repos/contract_projects/powerpoint_reports/`
- XML snapshot: `/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/snapshots/`
**Features**:
- Compares current XML with previous Friday's snapshot
- Generates Safran-branded PowerPoint presentation
- Creates weekly change management documentation
- Archives XML snapshots for historical tracking

## 📁 **FILE STRUCTURE**

```
/workspaces/control_tower/
├── cloned_repos/contract_projects/
│   ├── xml_workspace/
│   │   ├── current/
│   │   │   └── ZnNi Line Development Plan-08.xml    # Upload your latest XML here
│   │   └── snapshots/                               # Friday workflow archives
│   └── powerpoint_reports/                          # Generated presentations
└── reporting/                                       # Milestone reports
```

## 🔄 **WORKFLOW PROCESS**

1. **Upload XML**: Manually upload latest XML export from MS Project to `xml_workspace/current/`
2. **Run Commands**: Use the 3 commands above based on your needs
3. **Review Outputs**: Check generated reports in `reporting/` and `powerpoint_reports/`

---

**XML Data Source**: `/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/current/ZnNi Line Development Plan-08.xml`

*All commands read from this XML file. Update this file with fresh MS Project exports when data needs refreshing.*
