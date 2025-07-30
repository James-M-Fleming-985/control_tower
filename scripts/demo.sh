#!/bin/bash
# Control Tower Demo Script
# Shows the power of everyday project management commands

echo "🏗️ CONTROL TOWER DEMO"
echo "====================="
echo ""

echo "📊 CURRENT PROJECT HEALTH:"
echo "=========================="
python3 repo_queries/quick_query.py projects
echo ""

echo "📅 WHAT'S DUE TODAY:"
echo "==================="
python3 repo_queries/quick_query.py today
echo ""

echo "📅 WHAT'S DUE THIS WEEK:"
echo "======================="
python3 repo_queries/quick_query.py week
echo ""

echo "⚠️ OVERDUE TASKS:"
echo "================="
python3 repo_queries/quick_query.py overdue
echo ""

echo "🎯 UPCOMING MILESTONES:"
echo "======================"
python3 repo_queries/quick_query.py milestones --days 14
echo ""

echo "📋 GENERATING DETAILED REPORTS..."
echo "=================================="
python3 repo_queries/daily_reports.py
echo ""

echo "📁 REPORTS SAVED IN todos/ FOLDER:"
echo "=================================="
ls -la todos/
echo ""

echo "💡 TIP: Use these commands daily for project management:"
echo "======================================================="
echo "  python3 repo_queries/quick_query.py today           # Morning routine"
echo "  python3 repo_queries/quick_query.py week            # Weekly planning"
echo "  python3 repo_queries/quick_query.py mine --person 'Name'  # Personal tasks"
echo "  python3 repo_queries/daily_reports.py        # Detailed reports"
echo ""
echo "🎯 Control Tower - Your project command center!"
