#!/bin/bash
# Quick Overdue Tasks Report
# Generates overdue tasks report for problem resolution
# Usage: ./reports/quick_overdue.sh [limit]

LIMIT=${1:-10}

echo "🚨 GENERATING OVERDUE TASKS REPORT"
echo "=================================="
echo "📅 Report Date: $(date '+%B %d, %Y')"
echo "🎯 Target: Top $LIMIT overdue tasks"
echo ""

cd /workspaces/control_tower
python3 control_tower.py ms-project --action overdue --limit $LIMIT

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Overdue tasks report generated successfully!"
    echo "📁 Location: reporting/ (timestamped file)"
    echo "🎯 Ready for problem resolution"
    echo ""
    echo "💡 Tip: Use './reports/quick_overdue.sh 20' for extended analysis"
else
    echo "❌ Failed to generate overdue tasks report"
fi
