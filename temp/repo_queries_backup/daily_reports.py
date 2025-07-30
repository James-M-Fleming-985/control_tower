#!/usr/bin/env python3
"""
Daily Reports Generator for Control Tower
Generates daily/weekly reports for project management
Uses proper column mapping to handle CSV structure
"""

import os
import pandas as pd
import json
import csv
import sys
from datetime import datetime, timedelta
import glob

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from column_mapping import (TaskColumns, get_task_name, get_duration, 
                          get_start_date, get_finish_date, get_resource_names, 
                          get_percent_complete, is_milestone, get_project_name_from_path)

def load_repos_config():
    """Load repository configuration"""
    try:
        with open('repos.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("repos.json not found. Please run sync_all_repos.sh first.")
        return {}

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
    
    # Common date formats
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

def find_all_task_files():
    """Find all tasks.csv files in cloned repositories"""
    task_files = []
    
    # Search in cloned_repos directory
    pattern = "cloned_repos/**/tasks.csv"
    files = glob.glob(pattern, recursive=True)
    
    for file_path in files:
        # Extract project/repo info from path
        path_parts = file_path.split('/')
        if len(path_parts) >= 3:
            repo_name = path_parts[1]  # cloned_repos/[repo_name]/...
            project_path = '/'.join(path_parts[2:-1])  # everything between repo and tasks.csv
            
            task_files.append({
                'file_path': file_path,
                'repo_name': repo_name,
                'project_path': project_path,
                'full_project_name': f"{repo_name}/{project_path}" if project_path else repo_name
            })
    
    return task_files

def load_task_data(task_files):
    """Load and combine task data from all files"""
    all_tasks = []
    
    for task_info in task_files:
        try:
            # Check if file has headers or starts with data
            with open(task_info['file_path'], 'r') as f:
                first_line = f.readline().strip()
            
            # If first line starts with "% Complete", it has headers
            if first_line.startswith('% Complete'):
                # File has headers
                df = pd.read_csv(task_info['file_path'])
            else:
                # Read without headers and add them manually
                df = pd.read_csv(task_info['file_path'], header=None)
                df.columns = ['% Complete', 'Constraint Date', 'Constraint Type', 'Is Milestone', 'Milestone', 'Task Mode', 'Task Name', 'Duration', 'Start', 'Finish', 'Predecessors', 'Work', 'Resource Names', 'Baseline Start', 'Baseline Finish', 'Actual Start', 'Actual Finish', 'Physical % Complete', 'Number1', 'Number2']
            
            # Add metadata columns
            df['source_repo'] = task_info['repo_name']
            df['source_project'] = task_info['project_path']
            df['full_project_name'] = task_info['full_project_name']
            df['source_file'] = task_info['file_path']
            
            all_tasks.append(df)
            print(f"Loaded {len(df)} tasks from {task_info['full_project_name']}")
            
        except Exception as e:
            print(f"Error loading {task_info['file_path']}: {e}")
    
    if not all_tasks:
        print("No task data found!")
        return pd.DataFrame()
    
    # Combine all dataframes
    combined_df = pd.concat(all_tasks, ignore_index=True, sort=False)
    
    # Parse dates - accounting for column shift in CSV files
    # Due to missing 'Constraint Date' values, actual working dates are shifted:
    # - Working Start dates are in 'Task Name' column 
    # - Working Finish dates are in 'Duration' column
    # - Baseline dates are in 'Start' and 'Finish' columns
    date_columns = [
        ('Task Name', 'Working_Start_parsed'),    # Actual working start dates
        ('Duration', 'Working_Finish_parsed'),    # Actual working finish dates  
        ('Start', 'Baseline_Start_parsed'),       # Baseline start dates
        ('Finish', 'Baseline_Finish_parsed'),     # Baseline finish dates
        ('Constraint Date', 'Constraint_Date_parsed'),
        ('Baseline Start', 'Original_Baseline_Start_parsed'), 
        ('Baseline Finish', 'Original_Baseline_Finish_parsed'),
        ('Actual Start', 'Actual_Start_parsed'),
        ('Actual Finish', 'Actual_Finish_parsed')
    ]
    
    for source_col, target_col in date_columns:
        if source_col in combined_df.columns:
            combined_df[target_col] = combined_df[source_col].apply(parse_date)
    
    # For backward compatibility, use working dates as the main parsed dates
    if 'Working_Start_parsed' in combined_df.columns:
        combined_df['Start_parsed'] = combined_df['Working_Start_parsed']
    if 'Working_Finish_parsed' in combined_df.columns:
        combined_df['Finish_parsed'] = combined_df['Working_Finish_parsed']
    
    return combined_df

def generate_whats_due_report(df, days_ahead=7):
    """Generate what's due report for next N days"""
    today = datetime.now()
    future_date = today + timedelta(days=days_ahead)
    
    # Filter tasks due in the next N days
    due_tasks = df[
        (df['Finish_parsed'].notna()) & 
        (df['Finish_parsed'] >= today) & 
        (df['Finish_parsed'] <= future_date) &
        (df['% Complete'] != '100%')  # Not completed
    ].copy()
    
    if due_tasks.empty:
        return "No tasks due in the next {} days! 🎉".format(days_ahead)
    
    # Sort by finish date
    due_tasks = due_tasks.sort_values('Finish_parsed')
    
    # Create report
    report = f"# TASKS DUE IN NEXT {days_ahead} DAYS\n"
    report += f"Generated: {today.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    current_date = None
    for _, task in due_tasks.iterrows():
        task_date = task['Finish_parsed'].strftime('%Y-%m-%d (%A)')
        
        if task_date != current_date:
            report += f"\n## 📅 {task_date}\n"
            current_date = task_date
        
        # Task details
        completion = task.get('% Complete', '0%')
        
        # Check if it's a milestone (0 days duration and 0 hrs work)
        # Due to column shift: Duration is in 'Task Mode' column, Work is in 'Finish' column
        is_milestone = (str(task.get('Task Mode', '')).find('0 days') != -1 and 
                       str(task.get('Finish', '')).find('0 hrs') != -1)
        milestone_flag = "🎯 " if is_milestone else ""
        
        # Task names are actually in the Milestone column due to CSV column shift
        task_name = task.get('Milestone', 'Unnamed Task')
        report += f"- {milestone_flag}**{task_name}**\n"
        
        # Extract just the project name from the full path
        project_name = task['full_project_name'].split('/')[-1] if task['full_project_name'] else 'Unknown Project'
        report += f"  - Project: {project_name}\n"
        report += f"  - Progress: {completion}\n"
        
        # Due to column shift, actual resource names are in the 'Predecessors' column (column 11)
        owner = task.get('Predecessors', '')
        if pd.notna(owner) and owner != '' and not str(owner).startswith(('FS', 'SS', 'FF', 'SF')):
            # Clean up the owner name (remove [%] brackets if present)
            clean_owner = str(owner).split('[')[0].strip() if '[' in str(owner) else str(owner).strip()
            report += f"  - Owner: {clean_owner}\n"
        
        if pd.notna(task.get('Duration', '')):
            report += f"  - Duration: {task['Duration']}\n"
        
        report += "\n"
    
    return report

def generate_milestones_report(df, days_ahead=30):
    """Generate upcoming milestones report organized by month"""
    today = datetime.now()
    
    # Calculate month boundaries
    current_month_start = today.replace(day=1)
    if today.month == 12:
        next_month_start = today.replace(year=today.year + 1, month=1, day=1)
        next_month_end = next_month_start.replace(month=2, day=1) - timedelta(days=1)
    else:
        next_month_start = today.replace(month=today.month + 1, day=1)
        if today.month == 11:
            next_month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            next_month_end = today.replace(month=today.month + 2, day=1) - timedelta(days=1)
    
    current_month_end = next_month_start - timedelta(days=1)
    
    # Filter milestones using proper column mapping
    # Load all tasks using the correct column mapping system
    milestone_tasks = []
    
    # Process each file using proper column mapping
    for task_info in find_all_task_files():
        try:
            with open(task_info['file_path'], 'r') as f:
                lines = f.readlines()
            
            if not lines:
                continue
            
            # Parse CSV manually for proper column handling
            reader = csv.reader(lines)
            rows = list(reader)
            
            if not rows:
                continue
            
            # Skip header row and process data
            data_rows = rows[1:] if rows[0][0] == '% Complete' else rows
            
            for row in data_rows:
                if len(row) < 20:  # Ensure we have enough columns
                    continue
                
                # Check if this is a milestone using proper column mapping
                if is_milestone(row):
                    # Parse the finish date using proper column mapping
                    finish_date_str = get_finish_date(row)
                    finish_parsed = parse_date(finish_date_str)
                    
                    if finish_parsed:
                        milestone_tasks.append({
                            'task_name': get_task_name(row),
                            'finish_parsed': finish_parsed,
                            'finish_date': finish_date_str,
                            'percent_complete': get_percent_complete(row),
                            'resource_names': get_resource_names(row),
                            'project_name': get_project_name_from_path(task_info['file_path']),
                            'full_project_name': task_info['full_project_name']
                        })
        except Exception as e:
            print(f"Warning: Could not process {task_info['file_path']}: {e}")
    
    # Convert to DataFrame for easier filtering
    milestones_df = pd.DataFrame(milestone_tasks)
    
    # Convert to DataFrame for easier filtering
    milestones_df = pd.DataFrame(milestone_tasks)
    
    if milestones_df.empty:
        # Create report with no milestones
        report = f"# 🎯 UPCOMING MILESTONES BY MONTH\n"
        report += f"Generated: {today.strftime('%Y-%m-%d %H:%M')}\n\n"
        report += f"## 📅 THIS MONTH ({today.strftime('%B %Y')})\n"
        report += f"No milestones remaining this month.\n\n"
        report += f"## 📅 NEXT MONTH ({next_month_start.strftime('%B %Y')})\n"
        report += f"No milestones scheduled for {next_month_start.strftime('%B %Y')}.\n\n"
        report += f"## 📊 Summary\nNo upcoming milestones found.\n"
        return report
    
    # Split milestones by month
    this_month_milestones = milestones_df[
        (milestones_df['finish_parsed'] >= today) & 
        (milestones_df['finish_parsed'] <= current_month_end)
    ].copy()
    
    next_month_milestones = milestones_df[
        (milestones_df['finish_parsed'] >= next_month_start) & 
        (milestones_df['finish_parsed'] <= next_month_end)
    ].copy()
    
    # Create report
    report = f"# 🎯 UPCOMING MILESTONES BY MONTH\n"
    report += f"Generated: {today.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # This Month Section
    report += f"## 📅 THIS MONTH ({today.strftime('%B %Y')})\n"
    if this_month_milestones.empty:
        report += f"No milestones remaining this month.\n\n"
    else:
        this_month_milestones = this_month_milestones.sort_values('finish_parsed')
        for _, milestone in this_month_milestones.iterrows():
            days_until = (milestone['finish_parsed'] - today).days
            urgency = "🔴" if days_until <= 3 else "🟡" if days_until <= 7 else "🟢"
            
            report += f"{urgency} **{milestone['task_name']}**\n"
            report += f"   - Due: {milestone['finish_parsed'].strftime('%Y-%m-%d (%A)')} ({days_until} days)\n"
            report += f"   - Project: {milestone['project_name']}\n"
            report += f"   - Progress: {milestone['percent_complete']}\n"
            
            # Show resource assignment if available
            if milestone['resource_names']:
                report += f"   - Owner: {milestone['resource_names']}\n"
            
            report += "\n"
    
    # Next Month Section
    next_month_name = next_month_start.strftime('%B %Y')
    report += f"## 📅 NEXT MONTH ({next_month_name})\n"
    if next_month_milestones.empty:
        report += f"No milestones scheduled for {next_month_name}.\n\n"
    else:
        next_month_milestones = next_month_milestones.sort_values('finish_parsed')
        for _, milestone in next_month_milestones.iterrows():
            days_until = (milestone['finish_parsed'] - today).days
            
            report += f"🟢 **{milestone['task_name']}**\n"
            report += f"   - Due: {milestone['finish_parsed'].strftime('%Y-%m-%d (%A)')} ({days_until} days)\n"
            report += f"   - Project: {milestone['project_name']}\n"
            report += f"   - Progress: {milestone['percent_complete']}\n"
            
            # Show resource assignment if available
            if milestone['resource_names']:
                report += f"   - Owner: {milestone['resource_names']}\n"
            
            report += "\n"
    
    total_milestones = len(this_month_milestones) + len(next_month_milestones)
    if total_milestones == 0:
        report += "## 📊 Summary\nNo upcoming milestones found in the next two months.\n"
    else:
        report += f"## 📊 Summary\n"
        report += f"- This month: {len(this_month_milestones)} milestones\n"
        report += f"- Next month: {len(next_month_milestones)} milestones\n"
        report += f"- **Total: {total_milestones} milestones**\n"
    
    return report

def generate_overdue_report(df):
    """Generate overdue tasks report"""
    today = datetime.now()
    
    # Filter overdue tasks
    overdue_tasks = df[
        (df['Finish_parsed'].notna()) & 
        (df['Finish_parsed'] < today) &
        (df['% Complete'] != '100%')  # Not completed
    ].copy()
    
    if overdue_tasks.empty:
        return "No overdue tasks! 🎉"
    
    # Sort by how overdue (most overdue first)
    overdue_tasks = overdue_tasks.sort_values('Finish_parsed')
    
    # Create report
    report = f"# ⚠️ OVERDUE TASKS\n"
    report += f"Generated: {today.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    for _, task in overdue_tasks.iterrows():
        days_overdue = (today - task['Finish_parsed']).days
        
        report += f"🔴 **{task.get('Task Name', 'Unnamed Task')}**\n"
        report += f"   - Was due: {task['Finish_parsed'].strftime('%Y-%m-%d (%A)')} ({days_overdue} days ago)\n"
        report += f"   - Project: {task['full_project_name']}\n"
        report += f"   - Progress: {task.get('% Complete', '0%')}\n"
        
        if pd.notna(task.get('Resource Names', '')):
            report += f"   - Assigned: {task['Resource Names']}\n"
        
        report += "\n"
    
    return report

def save_report(report_content, filename):
    """Save report to todos folder"""
    os.makedirs('todos', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filepath = f"todos/{timestamp}_{filename}"
    
    with open(filepath, 'w') as f:
        f.write(report_content)
    
    print(f"Report saved: {filepath}")
    return filepath

def main():
    """Main function to generate daily reports"""
    print("🏗️ Control Tower Daily Reports Generator")
    print("=" * 50)
    
    # Find all task files
    print("Scanning for task files...")
    task_files = find_all_task_files()
    
    if not task_files:
        print("No task files found. Run sync_all_repos.sh first.")
        return
    
    print(f"Found {len(task_files)} task files")
    
    # Load all task data
    print("Loading task data...")
    df = load_task_data(task_files)
    
    if df.empty:
        print("No task data loaded.")
        return
    
    print(f"Loaded {len(df)} total tasks")
    
    # Generate reports
    print("\nGenerating reports...")
    
    # What's due this week
    due_report = generate_whats_due_report(df, days_ahead=7)
    save_report(due_report, "whats_due_this_week.md")
    
    # Upcoming milestones
    milestones_report = generate_milestones_report(df, days_ahead=30)
    save_report(milestones_report, "upcoming_milestones.md")
    
    # Overdue tasks
    overdue_report = generate_overdue_report(df)
    save_report(overdue_report, "overdue_tasks.md")
    
    # Quick summary for console
    print("\n" + "=" * 50)
    print("📊 QUICK SUMMARY")
    print("=" * 50)
    
    today = datetime.now()
    
    # Due this week count
    due_this_week = df[
        (df['Finish_parsed'].notna()) & 
        (df['Finish_parsed'] >= today) & 
        (df['Finish_parsed'] <= today + timedelta(days=7)) &
        (df['% Complete'] != '100%')
    ]
    
    # Overdue count
    overdue = df[
        (df['Finish_parsed'].notna()) & 
        (df['Finish_parsed'] < today) &
        (df['% Complete'] != '100%')
    ]
    
    # Milestones this month
    milestones_month = df[
        ((df['Is Milestone'] == 'Yes') | 
         (df['Task Name'].str.contains('milestone|gate|approval|complete', case=False, na=False))) &
        (df['Finish_parsed'].notna()) & 
        (df['Finish_parsed'] >= today) & 
        (df['Finish_parsed'] <= today + timedelta(days=30))
    ]
    
    print(f"📅 Due this week: {len(due_this_week)} tasks")
    print(f"⚠️ Overdue: {len(overdue)} tasks")
    print(f"🎯 Milestones next 30 days: {len(milestones_month)} milestones")
    print(f"📁 Reports saved in: todos/")

if __name__ == "__main__":
    main()
