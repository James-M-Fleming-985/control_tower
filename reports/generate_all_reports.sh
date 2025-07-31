#!/bin/bash
# Control Tower - Optional Complete Report Generation Suite
# Use only when comprehensive report package is needed
# For most cases, use specific report commands instead
# 
# Usage: ./reports/generate_all_reports.sh
# Note: This generates ALL reports - usually you want specific ones

echo "🚀 CONTROL TOWER - COMPLETE REPORT SUITE (OPTIONAL)"
echo "=================================================="
echo "⚠️  This generates ALL reports - consider specific commands instead"
echo "📅 Report Date: $(date '+%B %d, %Y')"
echo ""

read -p "Generate complete report suite? This creates all reports (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled. Use specific commands for targeted reports:"
    echo "   📊 Safran presentation: python modules/milestone_management/reporting/safran_powerpoint_generator.py"
    echo "   📋 Milestones: python3 control_tower.py ms-project --action milestones --period current --repository contract_projects"
    echo "   🔍 Status: python3 control_tower.py ms-project --action status --repository contract_projects"
    exit 0
fi

cd /workspaces/control_tower

# Step 1: Generate Safran PowerPoint presentation
echo "📊 Step 1/4: Generating Safran PowerPoint Presentation..."
echo "   Target: cloned_repos/contract_projects/projects/Safran/"
python modules/milestone_management/reporting/safran_powerpoint_generator.py
if [ $? -eq 0 ]; then
    echo "   ✅ Safran presentation generated successfully"
else
    echo "   ❌ Failed to generate Safran presentation"
fi
echo ""

# Step 2: Generate milestone reports
echo "📋 Step 2/4: Generating Milestone Reports..."
echo "   Generating current and next month milestones..."
python3 control_tower.py ms-project --action milestones --period both --repository contract_projects
if [ $? -eq 0 ]; then
    echo "   ✅ Milestone reports generated successfully"
else
    echo "   ❌ Failed to generate milestone reports"
fi
echo ""

# Step 3: Generate status overview
echo "🔍 Step 3/4: Generating Project Status Overview..."
python3 control_tower.py ms-project --action status --repository contract_projects
if [ $? -eq 0 ]; then
    echo "   ✅ Status overview generated successfully"
else
    echo "   ❌ Failed to generate status overview"
fi
echo ""

# Step 4: Check for overdue items
echo "⚠️ Step 4/4: Checking Overdue Tasks..."
python3 control_tower.py ms-project --action overdue --limit 10 --repository contract_projects
if [ $? -eq 0 ]; then
    echo "   ✅ Overdue tasks report generated successfully"
else
    echo "   ❌ Failed to generate overdue tasks report"
fi
echo ""

# Summary
echo "📦 REPORT GENERATION COMPLETE!"
echo "=============================="
echo ""
echo "📁 Generated Files:"
echo "   📊 PowerPoint Presentations:"
echo "      Location: cloned_repos/contract_projects/projects/Safran/"
ls -la cloned_repos/contract_projects/projects/Safran/*.pptx 2>/dev/null | sed 's/^/      /' || echo "      (No PowerPoint files found)"

echo ""
echo "   📋 Milestone & Status Reports:"
echo "      Location: reporting/"
ls -la reporting/*$(date +%Y%m%d)*.md 2>/dev/null | sed 's/^/      /' || echo "      (No reports found for today)"

echo ""
echo "🎯 Ready for Download & Dissemination:"
echo "   1. PowerPoint: Ready for manual slide append workflow"
echo "   2. Reports: Ready for stakeholder distribution"
echo "   3. All files timestamped for version control"
echo ""
echo "✅ Report generation workflow completed successfully!"
