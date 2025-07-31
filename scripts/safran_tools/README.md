# Safran Tools Directory

This directory contains specialized tools for Safran contract project management and PowerPoint generation.

## ✅ **Production Tools**

### Core Workflow
- `update_xml_and_regenerate.py` - **PRIMARY WORKFLOW TOOL**
  - Updates XML files with backup and safety checks
  - Regenerates PowerPoint presentations automatically
  - **Use this for daily Safran presentation updates**

### Analysis & Debugging
- `analyze_outline_levels.py` - **Hierarchy Analysis**
  - Analyzes MS Project outline levels within Safran phases
  - Shows project structure and progress by hierarchy level
  - **Use for understanding project organization**

- `check_specific_projects.py` - **Project Search**
  - Searches for specific project names in Safran XML data
  - Fuzzy matching with partial name support
  - **Use to verify specific projects exist in data**

### PowerPoint Generation
- `generate_final_powerpoint.py` - **Final Presentation Generator**
  - Creates polished Safran PowerPoint presentations
  - **Use for executive-level reporting**

## 🎯 **Primary Production System**

The main Safran PowerPoint generation system is located in:
```
/modules/milestone_management/reporting/safran_powerpoint_generator.py
```

All tools in this directory integrate with that core system.

## 📋 **Usage Patterns**

### Daily Updates
```bash
cd /workspaces/control_tower/scripts/safran_tools
python3 update_xml_and_regenerate.py
```

### Project Analysis
```bash
python3 analyze_outline_levels.py
python3 check_specific_projects.py
```

### Final Presentation
```bash
python3 generate_final_powerpoint.py
```

## 🔗 **Integration**

All tools properly integrate with:
- Control Tower milestone management
- MS Project XML data structure
- Safran contract project workflows
- Executive reporting requirements

## ⚠️ **Important Notes**

- These tools are **specifically for Safran contract projects**
- They require proper XML data in `/cloned_repos/contract_projects/xml_workspace/`
- Do not use these tools for non-Safran projects
- All tools maintain production-quality standards
