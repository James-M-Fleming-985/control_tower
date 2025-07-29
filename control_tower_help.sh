#!/bin/bash
# Control Tower Quick Commands
# Easy shortcuts for everyday project management

# Make scripts executable
chmod +x daily_reports.py
chmod +x quick_query.py

echo "🏗️ Control Tower Quick Commands"
echo "================================"
echo ""
echo "📅 DAILY QUERIES:"
echo "  ./quick_query.py today      - What's due today"
echo "  ./quick_query.py week       - What's due this week"
echo "  ./quick_query.py overdue    - Show overdue tasks"
echo ""
echo "🎯 MILESTONE TRACKING:"
echo "  ./quick_query.py milestones         - Next 30 days"
echo "  ./quick_query.py milestones --days 7 - Next 7 days"
echo ""
echo "👤 PERSONAL TASKS:"
echo "  ./quick_query.py mine --person \"James Fleming\""
echo "  ./quick_query.py mine --person \"Scott\""
echo ""
echo "📊 PROJECT STATUS:"
echo "  ./quick_query.py projects           - All projects"
echo "  ./quick_query.py projects --project \"Chiller\""
echo ""
echo "📋 REPORTS:"
echo "  python3 daily_reports.py   - Generate detailed reports"
echo ""
echo "💡 TIP: Run 'python3 daily_reports.py' for detailed reports saved in todos/ folder"
echo ""

# Quick examples
echo "🚀 QUICK EXAMPLES:"
echo "=================="

echo ""
echo "📅 What's due today:"
python3 quick_query.py today

echo ""
echo "📊 Quick project overview:"
python3 quick_query.py projects | head -20
