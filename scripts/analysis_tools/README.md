# Analysis Tools Directory

This directory contains general-purpose analysis tools for Control Tower project management.

## 🔍 **Available Tools**

### Project Analysis
- `analyze_projects.py` - **General Project Analysis**
  - Analyzes project data across all repositories
  - Provides insights into project structure and progress
  - **Use for cross-project analysis**

### XML Analysis
- `analyze_xml.py` - **XML Data Analysis**
  - Analyzes XML file structure and content
  - Validates XML parsing and data integrity
  - **Use for debugging XML data issues**

## 📊 **Purpose**

These tools provide analytical capabilities that complement the main Control Tower system:

1. **Data Validation** - Verify project data integrity
2. **Cross-Repository Analysis** - Understand patterns across projects
3. **Structure Analysis** - Examine project organization
4. **Debug Support** - Troubleshoot data issues

## 🎯 **Usage Patterns**

### General Project Analysis
```bash
cd /workspaces/control_tower/scripts/analysis_tools
python3 analyze_projects.py
```

### XML Data Validation
```bash
python3 analyze_xml.py
```

## 🔗 **Integration**

These tools integrate with:
- Control Tower core system
- Multiple repository data sources
- General project management workflows
- Cross-project reporting needs

## 📋 **Scope**

Unlike Safran-specific tools, these analysis tools:
- Work across **all repositories**
- Provide **general-purpose** analysis
- Support **cross-project** insights
- Enable **system-wide** debugging

## ⚠️ **Important Notes**

- These are **analysis tools**, not production workflows
- Use for **investigation and debugging**
- Complement but don't replace core Control Tower functionality
- Safe to run on any project data
