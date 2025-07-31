#!/bin/bash
# Safran PowerPoint Generator - Control Tower Reports
# Generates Safran presentations and saves them to the Safran project folder
# 
# Organization:
# - Generator scripts: Control Tower /reports (centralized)
# - Generated presentations: Project folders (distributed)

echo "🚀 RUNNING SAFRAN POWERPOINT GENERATOR"
echo "======================================"
echo "📂 Generator Location: Control Tower /reports"
echo "💾 Output Location: Safran project folder"
echo ""

cd /workspaces/control_tower
python modules/milestone_management/reporting/safran_powerpoint_generator.py

echo ""
echo "✅ Generator completed!"
echo "📁 Presentation saved to: cloned_repos/contract_projects/projects/Safran/"
echo "🎯 Ready for manual slide append workflow"
