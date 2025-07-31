#!/bin/bash
# Quick Project Status Report
# Generates project status overview for management updates
# Usage: ./reports/quick_status.sh

echo "🔍 GENERATING PROJECT STATUS REPORT"
echo "==================================="
echo "📅 Report Date: $(date '+%B %d, %Y')"
echo "🎯 Target: Overall project health"
echo ""

cd /workspaces/control_tower
python3 control_tower.py ms-project --action status

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Project status report generated successfully!"
    echo "📁 Location: reporting/ (timestamped file)"
    echo "🎯 Ready for management briefing"
else
    echo "❌ Failed to generate status report"
fi
