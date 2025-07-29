#!/usr/bin/env python3
"""
Quick Query Tool for Control Tower
Find tasks, see upcoming work, check milestones
Uses proper column mapping to handle CSV structure
"""

import csv
import os
import pandas as pd
from datetime import datetime, timedelta
import glob
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.date_utils import parse_date_flexible, format_date
from column_mapping import (TaskColumns, get_task_name, get_duration, 
                          get_start_date, get_finish_date, get_resource_names, 
                          get_percent_complete, is_milestone, get_project_name_from_path)

def parse_date(date_str):
    """Parse date string in various formats"""
    if pd.isna(date_str) or date_str == "" or date_str == "NA":
        return None
    
    # Convert to string if it's not already
    if not isinstance(date_str, str):
        date_str = str(date_str)
    
    # Skip numeric-only values (these are likely task IDs, not dates)
    if date_str.replace('.', '').replace('-', '').isdigit():
        return None
    
    # Skip values that contain "hrs" (these are durations)
    if 'hrs' in date_str.lower() or 'hr' in date_str.lower():
        return None
    
    # Skip values that contain "FS" or other task references
    if any(ref in date_str for ref in ['FS', 'SF', '%]']):
        return None
    
    formats = [
        "%a %d/%m/%y",  # Mon 14/04/25
        "%d/%m/%y",     # 14/04/25
        "%Y-%m-%d",     # 2025-04-14
        "%m/%d/%Y",     # 04/14/2025
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def load_all_tasks():
    """Load all tasks from all repositories using proper column mapping"""
    import pandas as pd
    
    task_files = glob.glob("cloned_repos/**/tasks.csv", recursive=True)
    all_tasks = []
    
    for file_path in task_files:
        try:
            # Read CSV with proper column handling
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                continue
            
            # Parse the CSV manually for better control
            reader = csv.reader(lines)
            rows = list(reader)
            
            if not rows:
                continue
            
            # Skip header row and process data
            data_rows = rows[1:] if rows[0][0] == '% Complete' else rows
            
            for row in data_rows:
                if len(row) < 20:  # Ensure we have enough columns
                    continue
                
                # Extract data using proper column mapping
                task_data = {
                    'task_name': get_task_name(row),
                    'duration': get_duration(row),
                    'start_date': get_start_date(row),
                    'finish_date': get_finish_date(row),
                    'resource_names': get_resource_names(row),
                    'percent_complete': get_percent_complete(row),
                    'is_milestone': is_milestone(row),
                    'project_name': get_project_name_from_path(file_path),
                    'file_path': file_path
                }
                
                # Parse dates
                task_data['start_parsed'] = parse_date(task_data['start_date'])
                task_data['finish_parsed'] = parse_date(task_data['finish_date'])
                
                all_tasks.append(task_data)
            
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
    
    # Convert to DataFrame
    return pd.DataFrame(all_tasks) if all_tasks else pd.DataFrame()

def whats_due_today():
    """Show what's due today"""
    df = load_all_tasks()
    if df.empty:
        return "No task data found."
    
    today = datetime.now().date()
    
    due_today = df[
        (df['Finish_parsed'].notna()) & 
        (df['Finish_parsed'].apply(lambda x: x.date() if pd.notna(x) else None) == today) &
        (df['% Complete'] != '100%')
    ]
    
    if due_today.empty:
        return "🎉 Nothing due today!"
    
    result = f"📅 DUE TODAY ({today.strftime('%Y-%m-%d')}):\n"
    result += "=" * 40 + "\n"
    
    for _, task in due_today.iterrows():
        # Check if it's a milestone (0 days duration and 0 hrs work)
        is_milestone = (str(task.get('Task Mode', '')).find('0 days') != -1 and 
                       str(task.get('Finish', '')).find('0 hrs') != -1)
        milestone = "🎯 " if is_milestone else ""
        
        # Task names are in the Milestone column due to column shift
        task_name = task.get('Milestone', 'Unnamed')
        result += f"{milestone}{task_name}\n"
        result += f"  📂 {task['full_project_name']}\n"
        result += f"  📊 {task.get('% Complete', '0%')} complete\n"
        if pd.notna(task.get('Resource Names', '')):
            result += f"  👤 {task['Resource Names']}\n"
        result += "\n"
    
    return result

def whats_due_this_week():
    """Show what's due this week"""
    df = load_all_tasks()
    if df.empty:
        return "No task data found."
    
    today = datetime.now()
    week_end = today + timedelta(days=7)
    
    due_week = df[
        (df['Finish_parsed'].notna()) & 
        (df['Finish_parsed'] >= today) & 
        (df['Finish_parsed'] <= week_end) &
        (df['% Complete'] != '100%')
    ].sort_values('Finish_parsed')
    
    if due_week.empty:
        return "🎉 Nothing due this week!"
    
    result = f"📅 DUE THIS WEEK:\n"
    result += "=" * 30 + "\n"
    
    current_date = None
    for _, task in due_week.iterrows():
        task_date = task['Finish_parsed'].strftime('%A %d/%m')
        
        if task_date != current_date:
            result += f"\n{task_date}:\n"
            current_date = task_date
        
        # Check if it's a milestone (0 days duration and 0 hrs work)
        is_milestone = (str(task.get('Task Mode', '')).find('0 days') != -1 and 
                       str(task.get('Finish', '')).find('0 hrs') != -1)
        milestone = "🎯 " if is_milestone else ""
        
        # Task names are in the Milestone column due to column shift
        task_name = task.get('Milestone', 'Unnamed')
        result += f"  {milestone}{task_name}\n"
        result += f"    📂 {task['full_project_name']}\n"
        
        if pd.notna(task.get('Resource Names', '')):
            result += f"    👤 {task['Resource Names']}\n"
    
    return result

def show_overdue():
    """Show overdue tasks"""
    df = load_all_tasks()
    if df.empty:
        return "No task data found."
    
    today = datetime.now()
    
    overdue = df[
        (df['Finish_parsed'].notna()) & 
        (df['Finish_parsed'] < today) &
        (df['% Complete'] != '100%')
    ].sort_values('Finish_parsed')
    
    if overdue.empty:
        return "🎉 No overdue tasks!"
    
    result = f"⚠️ OVERDUE TASKS:\n"
    result += "=" * 25 + "\n"
    
    for _, task in overdue.iterrows():
        days_overdue = (today - task['Finish_parsed']).days
        
        # Task names are in the Milestone column due to column shift
        task_name = task.get('Milestone', 'Unnamed')
        result += f"🔴 {task_name}\n"
        result += f"   📅 Due: {task['Finish_parsed'].strftime('%Y-%m-%d')} ({days_overdue} days ago)\n"
        result += f"   📂 {task['full_project_name']}\n"
        result += f"   📊 {task.get('% Complete', '0%')} complete\n"
        
        if pd.notna(task.get('Resource Names', '')):
            result += f"   👤 {task['Resource Names']}\n"
        result += "\n"
    
    return result

def show_milestones(days=30):
    """Show upcoming milestones"""
    df = load_all_tasks()
    if df.empty:
        return "No task data found."
    
    today = datetime.now()
    future = today + timedelta(days=days)
    
    # Milestones are identified by 0 days duration and 0 hrs work
    # Due to column shift: Duration is in 'Task Mode' column, Work is in 'Finish' column
    milestones = df[
        (df['Task Mode'].str.contains('0 days', case=False, na=False)) &
        (df['Finish'].str.contains('0 hrs', case=False, na=False)) &
        (df['Finish_parsed'].notna()) & 
        (df['Finish_parsed'] >= today) & 
        (df['Finish_parsed'] <= future)
    ].sort_values('Finish_parsed')
    
    if milestones.empty:
        return f"No milestones in next {days} days."
    
    result = f"🎯 MILESTONES (next {days} days):\n"
    result += "=" * 35 + "\n"
    
    for _, milestone in milestones.iterrows():
        days_until = (milestone['Finish_parsed'] - today).days
        urgency = "🔴" if days_until <= 3 else "🟡" if days_until <= 7 else "🟢"
        
        # Task names are in the Milestone column due to column shift
        task_name = milestone.get('Milestone', 'Unnamed')
        result += f"{urgency} {task_name}\n"
        result += f"   📅 {milestone['Finish_parsed'].strftime('%Y-%m-%d')} ({days_until} days)\n"
        result += f"   📂 {milestone['full_project_name']}\n"
        result += f"   📊 {milestone.get('% Complete', '0%')} complete\n"
        
        # Resource names are in the shifted position (Predecessors column)
        owner = milestone.get('Predecessors', '')
        if pd.notna(owner) and owner != '' and not str(owner).startswith(('FS', 'SS', 'FF', 'SF')):
            # Clean up the owner name (remove [%] brackets if present)  
            clean_owner = str(owner).split('[')[0].strip() if '[' in str(owner) else str(owner).strip()
            result += f"   👤 {clean_owner}\n"
        result += "\n"
    
    return result

def show_my_tasks(person_name):
    """Show tasks assigned to a specific person"""
    df = load_all_tasks()
    if df.empty:
        return "No task data found."
    
    # Filter tasks assigned to person (case insensitive)
    my_tasks = df[
        df['Resource Names'].str.contains(person_name, case=False, na=False) &
        (df['% Complete'] != '100%')
    ]
    
    if my_tasks.empty:
        return f"No active tasks found for {person_name}."
    
    # Sort by due date
    my_tasks = my_tasks.sort_values('Finish_parsed', na_position='last')
    
    result = f"👤 TASKS FOR {person_name.upper()}:\n"
    result += "=" * 35 + "\n"
    
    for _, task in my_tasks.iterrows():
        # Task names are in the Milestone column due to column shift
        task_name = task.get('Milestone', 'Unnamed')
        result += f"📋 {task_name}\n"
        result += f"   📂 {task['full_project_name']}\n"
        result += f"   📊 {task.get('% Complete', '0%')} complete\n"
        
        if pd.notna(task.get('Finish_parsed')):
            due_date = task['Finish_parsed'].strftime('%Y-%m-%d')
            days_until = (task['Finish_parsed'] - datetime.now()).days
            
            if days_until < 0:
                result += f"   ⚠️ OVERDUE: {due_date} ({abs(days_until)} days ago)\n"
            elif days_until <= 3:
                result += f"   🔴 Due: {due_date} ({days_until} days)\n"
            elif days_until <= 7:
                result += f"   🟡 Due: {due_date} ({days_until} days)\n"
            else:
                result += f"   📅 Due: {due_date} ({days_until} days)\n"
        
        result += "\n"
    
    return result

def show_project_status(project_filter=""):
    """Show status of projects"""
    df = load_all_tasks()
    if df.empty:
        return "No task data found."
    
    # Filter by project if specified
    if project_filter:
        df = df[df['full_project_name'].str.contains(project_filter, case=False, na=False)]
    
    # Group by project
    project_stats = []
    
    for project in df['full_project_name'].unique():
        project_tasks = df[df['full_project_name'] == project]
        
        total_tasks = len(project_tasks)
        completed_tasks = len(project_tasks[project_tasks['% Complete'] == '100%'])
        
        # Calculate average completion
        completion_values = []
        for pct in project_tasks['% Complete']:
            if pd.notna(pct) and pct != '':
                try:
                    # Remove % sign and convert to float
                    val = float(str(pct).replace('%', ''))
                    completion_values.append(val)
                except:
                    completion_values.append(0)
        
        avg_completion = sum(completion_values) / len(completion_values) if completion_values else 0
        
        # Check for overdue tasks
        today = datetime.now()
        overdue_tasks = len(project_tasks[
            (project_tasks['Finish_parsed'].notna()) & 
            (project_tasks['Finish_parsed'] < today) &
            (project_tasks['% Complete'] != '100%')
        ])
        
        project_stats.append({
            'project': project,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'avg_completion': avg_completion,
            'overdue_tasks': overdue_tasks
        })
    
    # Sort by average completion (lowest first - most attention needed)
    project_stats.sort(key=lambda x: x['avg_completion'])
    
    result = f"📊 PROJECT STATUS:\n"
    result += "=" * 25 + "\n"
    
    for stats in project_stats:
        completion_bar = "█" * int(stats['avg_completion'] / 10) + "░" * (10 - int(stats['avg_completion'] / 10))
        
        result += f"📂 {stats['project']}\n"
        result += f"   Progress: [{completion_bar}] {stats['avg_completion']:.1f}%\n"
        result += f"   Tasks: {stats['completed_tasks']}/{stats['total_tasks']} completed\n"
        
        if stats['overdue_tasks'] > 0:
            result += f"   ⚠️ {stats['overdue_tasks']} overdue tasks\n"
        
        result += "\n"
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Control Tower Quick Queries')
    parser.add_argument('command', choices=['today', 'week', 'overdue', 'milestones', 'mine', 'projects'], 
                       help='What to show')
    parser.add_argument('--person', help='Name for "mine" command')
    parser.add_argument('--project', help='Filter for projects')
    parser.add_argument('--days', type=int, default=30, help='Days ahead for milestones')
    
    args = parser.parse_args()
    
    if args.command == 'today':
        print(whats_due_today())
    elif args.command == 'week':
        print(whats_due_this_week())
    elif args.command == 'overdue':
        print(show_overdue())
    elif args.command == 'milestones':
        print(show_milestones(args.days))
    elif args.command == 'mine':
        if not args.person:
            print("Please specify --person for 'mine' command")
            return
        print(show_my_tasks(args.person))
    elif args.command == 'projects':
        print(show_project_status(args.project or ""))

if __name__ == "__main__":
    main()
