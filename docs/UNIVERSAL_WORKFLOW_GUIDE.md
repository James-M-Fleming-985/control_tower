# Universal MS Project Workflow Documentation

## Overview

The Universal MS Project Workflow is a flexible system that can update **any project** in your MS Project from CSV data. It supports multiple project types, CSV formats, and integration scenarios.

## Key Features

### 🔧 **Completely Configurable**
- **Project Settings**: Name, title, calendar settings
- **Column Mapping**: Map any CSV column names to project fields
- **Date Formats**: Support for DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, etc.
- **Work Calendar**: Customize work hours, days per week, etc.
- **Integration Options**: Standalone projects or integrate into existing MS Project files

### 📊 **Multiple Project Types Supported**

1. **Standalone Projects** - New independent projects
2. **Integrated Projects** - Add/replace sections in existing MS Project files
3. **Contract Projects** - Customer deliverable schedules
4. **Investment Projects** - Strategic initiative tracking
5. **Any Custom Project Type** - Define your own configuration

### 🎯 **Flexible CSV Support**

The system can work with **any CSV structure**. Just configure the column mapping:

```json
"column_mapping": {
    "id": "Your ID Column",
    "name": "Your Task Name Column", 
    "duration": "Your Duration Column",
    "start": "Your Start Date Column",
    "finish": "Your End Date Column",
    "predecessors": "Your Dependencies Column",
    "resources": "Your Resource Assignment Column",
    "milestone": "Your Milestone Flag Column"
}
```

## Quick Start

### 1. List Available Configurations
```bash
./scripts/universal_workflow.sh list
```

### 2. Create New Configuration for Your Project
```bash
./scripts/universal_workflow.sh create-config
```

### 3. Convert Any CSV to MS Project XML
```bash
./scripts/universal_workflow.sh convert data/your_tasks.csv your_config output.xml
```

## Configuration Examples

### Example 1: Manufacturing Project
```json
{
  "project": {
    "name": "Production Line Upgrade",
    "title": "Q3 Manufacturing Enhancement"
  },
  "column_mapping": {
    "id": "Work Order",
    "name": "Activity",
    "duration": "Days Required",
    "start": "Planned Start",
    "finish": "Target Completion",
    "predecessors": "Prerequisites",
    "resources": "Assigned Team",
    "milestone": "Critical Path"
  },
  "calendar": {
    "start_hour": 6,
    "end_hour": 14,
    "hours_per_day": 8
  },
  "integration": {
    "enabled": true,
    "target_project_name": "Manufacturing Projects",
    "target_outline_level": 3
  }
}
```

### Example 2: Software Development
```json
{
  "project": {
    "name": "Application Modernization",
    "title": "Legacy System Migration"
  },
  "column_mapping": {
    "id": "Story ID",
    "name": "User Story",
    "duration": "Story Points",
    "start": "Sprint Start",
    "finish": "Sprint End",
    "predecessors": "Blockers",
    "resources": "Developer",
    "milestone": "Demo Ready"
  },
  "calendar": {
    "start_hour": 9,
    "end_hour": 17,
    "hours_per_day": 6
  }
}
```

### Example 3: Construction Project
```json
{
  "project": {
    "name": "Building Renovation",
    "title": "Office Space Modernization"
  },
  "column_mapping": {
    "id": "Phase",
    "name": "Construction Activity",
    "duration": "Duration (Weeks)",
    "start": "Start Week",
    "finish": "End Week", 
    "predecessors": "Depends On",
    "resources": "Contractor",
    "milestone": "Inspection Required"
  },
  "calendar": {
    "start_hour": 7,
    "end_hour": 15,
    "hours_per_day": 8,
    "days_per_month": 22
  }
}
```

## Integration Modes

### Mode 1: Standalone Project
Creates a completely new MS Project file:
```json
"integration": {
  "enabled": false
}
```

### Mode 2: Replace Existing Project Section
Replaces a specific project section in an existing MS Project:
```json
"integration": {
  "enabled": true,
  "target_project_name": "SF Investment Strategy",
  "target_outline_level": 4,
  "replace_existing": true
}
```

### Mode 3: Add to Existing Project
Adds tasks to an existing project without replacing:
```json
"integration": {
  "enabled": true,
  "target_project_name": "Main Project",
  "target_outline_level": 2,
  "replace_existing": false
}
```

## CSV Format Flexibility

### Common CSV Formats Supported

**Format 1: Traditional Project Management**
```csv
ID,Task Name,Duration (Days),Start Date,End Date,Dependencies,Assigned To,Milestone
1,Planning Phase,5,2025-04-01,2025-04-05,,Project Manager,Yes
2,Requirements Gathering,10,2025-04-06,2025-04-15,1,Business Analyst,No
```

**Format 2: Agile/Scrum**
```csv
Story ID,User Story,Story Points,Sprint Start,Sprint End,Blockers,Developer,Demo Ready
US001,Login Feature,8,2025-04-01,2025-04-14,,John Smith,True
US002,Dashboard,13,2025-04-15,2025-04-28,US001,Jane Doe,False
```

**Format 3: Manufacturing**
```csv
Work Order,Activity,Days Required,Planned Start,Target Completion,Prerequisites,Assigned Team,Critical Path
WO001,Equipment Setup,2,01/04/2025,03/04/2025,,Maintenance Team,Yes
WO002,Production Run,7,04/04/2025,10/04/2025,WO001,Production Team,No
```

## Date Format Support

The system automatically detects and converts these date formats:
- **DD/MM/YYYY** (28/04/2025)
- **MM/DD/YYYY** (04/28/2025)
- **YYYY-MM-DD** (2025-04-28)
- **DD-MM-YYYY** (28-04-2025)
- **YYYY/MM/DD** (2025/04/28)
- **DD.MM.YYYY** (28.04.2025)

## Command Reference

### Basic Commands
```bash
# Show all available project configurations
./scripts/universal_workflow.sh list

# Create a new configuration template
./scripts/universal_workflow.sh create-config

# Convert CSV to XML (standalone)
./scripts/universal_workflow.sh convert data/tasks.csv standalone_project output.xml

# Convert CSV to XML (integrated)
./scripts/universal_workflow.sh convert data/tasks.csv sf_investment output.xml main_project.xml

# Quick SF Investment conversion
./scripts/universal_workflow.sh sf-investment
```

### Advanced Usage
```bash
# Direct Python script usage
python3 scripts/universal_ms_project_generator.py \
  --csv data/your_project.csv \
  --config config/your_config.json \
  --output output/your_project.xml \
  --main-xml path/to/main_project.xml
```

## Use Cases

### ✅ **Any Project Type**
- Manufacturing projects
- Software development
- Construction projects
- Research initiatives
- Customer contracts
- Strategic programs
- Maintenance schedules
- Training programs

### ✅ **Any Data Source**
- Excel exports
- Database exports
- ERP system data
- Third-party tools
- Manual CSV files
- API data feeds

### ✅ **Any Integration Scenario**
- New standalone projects
- Replace project sections
- Add to existing projects
- Merge multiple data sources
- Update specific project phases

## Benefits

1. **🔄 Reusable**: Create once, use for any project type
2. **⚡ Fast**: Automated conversion process
3. **🎯 Accurate**: Proper MS Project formatting and compatibility
4. **🔧 Flexible**: Configurable for any CSV structure
5. **📈 Scalable**: Handle projects of any size
6. **🔗 Integrated**: Works with existing MS Project files
7. **📋 Documented**: Clear configuration and usage examples

## Getting Started with Your Project

1. **Identify your CSV structure**
2. **Choose or create a configuration** that matches your needs
3. **Test with a small dataset** first
4. **Refine the configuration** if needed
5. **Scale to full project data**

The system is designed to work with **any project management workflow** and **any CSV data structure**. Just configure it once for your specific needs!
