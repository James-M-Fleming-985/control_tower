# Control Tower Scripts Directory

This directory contains organized scripts and tools for Control Tower project management.

## 📁 **Directory Structure**

### `/safran_tools/` - **Safran Contract Project Tools**
Specialized tools for Safran contract project management and PowerPoint generation:
- ✅ `update_xml_and_regenerate.py` - **PRIMARY WORKFLOW TOOL** for daily updates
- ✅ `analyze_outline_levels.py` - Project hierarchy analysis
- ✅ `check_specific_projects.py` - Project search and verification
- ✅ `generate_final_powerpoint.py` - Executive presentation generation

### `/analysis_tools/` - **General Analysis Tools**
Cross-repository analysis and data validation tools:
- `analyze_projects.py` - General project analysis across all repositories
- `analyze_xml.py` - XML data structure and integrity analysis

### `/testing_tools/` - **Testing & Validation Tools**
Testing utilities for Control Tower components:
- `test_xml_timeline.py` - XML timeline parsing and validation testing

### **Root Level Production Scripts**
- `safran_workflow.py` - Comprehensive Safran workflow automation
- `simulate_ms_project_update.py` - MS Project update simulation
- `safe_github_update.py` - Safe GitHub repository updates

## 🎯 **Quick Access**

### **Daily Safran Workflow**
```bash
cd scripts/safran_tools
python3 update_xml_and_regenerate.py
```

### **Project Analysis**
```bash
cd scripts/analysis_tools
python3 analyze_projects.py
```

### **Testing & Validation**
```bash
cd scripts/testing_tools
python3 test_xml_timeline.py
```

## 📋 **Organization Principles**

1. **By Purpose** - Tools grouped by their primary function
2. **By Scope** - Safran-specific vs. general-purpose tools
3. **By Usage** - Production tools vs. analysis vs. testing
4. **Clear Documentation** - Each directory has detailed README

## ✅ **Production Quality**

All organized tools maintain:
- ✅ **Production Standards** - Ready for daily use
- ✅ **Clear Documentation** - Purpose and usage documented
- ✅ **Proper Integration** - Work with Control Tower core
- ✅ **Safety Features** - Backup and validation included

## 🔗 **Integration Points**

Tools integrate with:
- **Control Tower Core** - Main system functionality
- **Module System** - Milestone management modules
- **Repository Structure** - Cloned repos and data sources
- **Reporting System** - PowerPoint and milestone reporting

## ⚠️ **Usage Guidelines**

1. **Safran Tools** - Use only for contract projects
2. **Analysis Tools** - Safe for any project analysis
3. **Testing Tools** - Use for validation and debugging
4. **Check READMEs** - Each directory has specific guidance

## 🚀 **Getting Started**

1. **For Safran Work** → Go to `/safran_tools/`
2. **For Analysis** → Go to `/analysis_tools/`  
3. **For Testing** → Go to `/testing_tools/`
4. **Read Directory READMEs** for detailed guidance
