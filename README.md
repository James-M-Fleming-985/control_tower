# Control Tower - Project Management Command Center 🏗️

Your central hub for managing multiple GitHub repositories and projects with intelligent task tracking, milestone monitoring, and automated reporting.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/your-username/control_tower
cd control_tower

# Sync all your repositories
./sync_all_repos.sh

# Get today's agenda
python3 quick_query.py today

# Generate comprehensive reports
python3 daily_reports.py
```

## 📋 Daily Commands

### ⚡ Quick Status Checks
```bash
# What's due today?
python3 quick_query.py today

# What's due this week?
python3 quick_query.py week

# Show overdue tasks
python3 quick_query.py overdue

# Upcoming milestones (next 30 days)
python3 quick_query.py milestones

# Milestones this week only
python3 quick_query.py milestones --days 7
```

### 👤 Personal Task Management
```bash
# Show my tasks
python3 quick_query.py mine --person "James Fleming"

# Show someone else's tasks
python3 quick_query.py mine --person "Scott"
```

### 📊 Project Overview
```bash
# All projects status
python3 quick_query.py projects

# Filter by project name
python3 quick_query.py projects --project "Chiller"
python3 quick_query.py projects --project "LIMS"
```

## 🔧 Task Management

### Search and Find Tasks
```bash
# Search for tasks
python3 task_scheduler.py search "design"
python3 task_scheduler.py search "milestone"
```

### Move and Schedule Tasks
```bash
# Move task to specific date
python3 task_scheduler.py move "chiller design" "2025-08-15"

# Delay task by 5 days
python3 task_scheduler.py delay "platform install" 5

# Move task forward by 2 days
python3 task_scheduler.py delay "testing phase" -2
```

### Update Task Progress
```bash
# Mark task as complete
python3 task_scheduler.py complete "kick off meeting"

# Update progress percentage
python3 task_scheduler.py progress "design phase" 75
```

## 📋 Automated Reports

### Generate Daily Reports
```bash
# Generate all reports (saved in todos/ folder)
python3 daily_reports.py
```

This creates timestamped reports:
- `todos/YYYYMMDD_HHMM_whats_due_this_week.md`
- `todos/YYYYMMDD_HHMM_upcoming_milestones.md` 
- `todos/YYYYMMDD_HHMM_overdue_tasks.md`

## 🚨 Common Use Cases

### "What do I need to do today?"
```bash
python3 quick_query.py today
```

### "Can I move Task A to next week?"
```bash
# Search for the task first
python3 task_scheduler.py search "Task A"

# Move it to next week
python3 task_scheduler.py move "Task A" "2025-08-08"
```

### "What's the highest priority risk?"
```bash
# Check overdue tasks
python3 quick_query.py overdue

# Check immediate milestones
python3 quick_query.py milestones --days 3
```

---

**Control Tower** - Bringing order to project chaos, one command at a time! 🎯
