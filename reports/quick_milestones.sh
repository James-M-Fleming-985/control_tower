#!/bin/bash
# Quick Current Milestones Report
# Generates current month milestone status for team meetings
# Usage: ./reports/quick_milestones.sh

echo "📋 GENERATING CURRENT MILESTONES REPORT"
echo "======================================="
echo "📅 Report Date: $(date '+%B %d, %Y')"
echo "🎯 Target: Current month milestones"
echo ""

cd /workspaces/control_tower
python3 control_tower.py ms-project --action milestones --period current

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Current milestones report generated successfully!"
    echo "📁 Location: reporting/ (timestamped file)"
    echo "🎯 Ready for team meeting review"
else
    echo "❌ Failed to generate milestones report"
fi
