# 🔄 CONTROL TOWER WORKFLOWS
**Project Management & Task Orchestration Platform**

---

## 📋 FRIDAY WORKFLOW DOCUMENTATION

**Purpose**: Weekly PowerPoint generation with XML comparison and change management tracking  
**Maintained By**: James Fleming  
**Last Updated**: September 1, 2025  
**Document Version**: 4.0 - Streamlined Edition

---

## 🏁 **FRIDAY WORKFLOW**

### **Purpose**
Weekly stakeholder presentation generation with automated change detection, comparison analysis, and PowerPoint report creation.

### **Frequency**
Every Friday for weekly stakeholder meetings and progress reviews.

### **Duration**
10-15 minutes (automated process)

### **Command**
```bash
python friday_workflow.py --friday-update
```

---

## 🔄 **WORKFLOW PROCESS**

### **Step 1: XML Upload** 📁
- **Action**: Manual upload of latest XML export from MS Project
- **Location**: `/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/current/`
- **Filename**: `ZnNi Line Development Plan-08.xml`
- **Frequency**: As needed when MS Project is updated

### **Step 2: Friday Workflow Execution** ⚡
```bash
python friday_workflow.py --friday-update
```

#### **Automated Processes:**

#### **2.1 XML Snapshot Creation** 📸
- **Action**: Creates timestamped snapshot of current XML
- **Location**: `xml_workspace/snapshots/friday_YYYYMMDD_*.xml`
- **Purpose**: Historical tracking and comparison baseline

#### **2.2 Change Comparison** 📊
- **Action**: Compares current XML with previous Friday's snapshot
- **Analysis**: 
  - Milestone date changes
  - Progress updates
  - New/removed tasks
  - Resource assignment changes
- **Output**: Change detection report

#### **2.3 PowerPoint Generation** 🎨
- **Action**: Generates Safran-branded PowerPoint presentation
- **Content**:
  - Current milestone status
  - Progress updates since last week
  - Upcoming milestones
  - Change summary
- **Output**: `powerpoint_reports/REACh_ZnNi_Line_Flash_Report_YYYYMMDD.pptx`

#### **2.4 Change Management Documentation** 📋
- **Action**: Creates change tracking documentation
- **Purpose**: Audit trail for milestone changes
- **Integration**: Embedded in PowerPoint presentation

---

## � **FILE STRUCTURE**

```
/workspaces/control_tower/
├── friday_workflow.py                          # Main workflow script
├── cloned_repos/contract_projects/
│   ├── xml_workspace/
│   │   ├── current/
│   │   │   └── ZnNi Line Development Plan-08.xml    # Current project data
│   │   └── snapshots/
│   │       ├── friday_20250830_143022.xml           # Previous snapshots
│   │       └── friday_20250906_141533.xml           # Historical tracking
│   └── powerpoint_reports/
│       ├── REACh_ZnNi_Line_Flash_Report_20250830.pptx
│       └── REACh_ZnNi_Line_Flash_Report_20250906.pptx
└── reporting/                                  # Milestone reports
    ├── milestones_current_20250906_141245.md
    └── milestones_next_20250906_141301.md
```

---

## 🎯 **WORKFLOW BENEFITS**

### **Automated Change Detection** 🔍
- **Eliminates Manual Comparison**: No need to manually check what changed
- **Comprehensive Analysis**: Captures all milestone, date, and progress changes
- **Historical Tracking**: Maintains week-over-week change history

### **Consistent Presentation Format** 📊
- **Safran Branding**: Professional corporate presentation template
- **Standardized Layout**: Consistent milestone reporting format
- **Automated Generation**: No manual PowerPoint creation required

### **Change Management Integration** 📋
- **Audit Trail**: Documents all changes with timestamps
- **Business Context**: Links technical changes to business impact
- **Stakeholder Communication**: Clear change summaries for management

### **Time Efficiency** ⏱️
- **Single Command**: One command generates complete Friday deliverable
- **Automated Process**: Runs without manual intervention
- **Consistent Output**: Same high-quality presentation every week

---

## 🔄 **TYPICAL FRIDAY WORKFLOW**

### **Morning Preparation** (5 minutes)
1. **Upload Latest XML**: Export from MS Project and upload to `current/` folder
2. **Verify Upload**: Confirm XML file timestamp is current

### **Workflow Execution** (2 minutes)
```bash
cd /workspaces/control_tower
python friday_workflow.py --friday-update
```

### **Review & Distribution** (5 minutes)
1. **Review Generated PowerPoint**: Check `powerpoint_reports/` for latest presentation
2. **Review Change Summary**: Verify detected changes are accurate
3. **Distribute to Stakeholders**: Send presentation for Friday meeting

---

## 🎨 **POWERPOINT OUTPUT DETAILS**

### **Slide Structure**
1. **Title Slide**: REACh ZnNi Line Flash Report with date
2. **Executive Summary**: Key changes and progress overview
3. **Current Milestones**: This month's milestone status
4. **Upcoming Milestones**: Next month's planned milestones
5. **Progress Tracking**: Completion percentages and trends
6. **Change Summary**: Week-over-week changes detected
7. **Risk & Issues**: Overdue items and blockers
8. **Action Items**: Next steps and responsibilities

### **Branding Elements**
- **Safran Corporate Colors**: Blue and orange color scheme
- **Professional Layout**: Clean, readable table formats
- **Consistent Typography**: Corporate font standards
- **Logo Integration**: Safran branding elements

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues & Solutions**
