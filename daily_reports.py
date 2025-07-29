#!/usr/bin/env python3
"""
Daily Reports Generator for Control Tower
Generates daily/weekly reports for project management
"""

import os
import pandas as pd
import json
from datetime import datetime, timedelta
import glob

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
            df = pd.read_csv(task_info['file_path'])
            
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
    
    # Parse dates
    date_columns = ['Start', 'Finish', 'Constraint Date', 'Baseline Start', 'Baseline Finish', 
                   'Actual Start', 'Actual Finish']
    
    for col in date_columns:
        if col in combined_df.columns:
            combined_df[f'{col}_parsed'] = combined_df[col].apply(parse_date)
    
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
        milestone_flag = "🎯 " if task.get('Is Milestone', '') == 'Yes' else ""
        
        report += f"- {milestone_flag}**{task.get('Task Name', 'Unnamed Task')}**\n"
        report += f"  - Project: {task['full_project_name']}\n"
        report += f"  - Progress: {completion}\n"
        
        if pd.notna(task.get('Resource Names', '')):
            report += f"  - Assigned: {task['Resource Names']}\n"
        
        if pd.notna(task.get('Duration', '')):
            report += f"  - Duration: {task['Duration']}\n"
        
        report += "\n"
    
    return report

def generate_milestones_report(df, days_ahead=30):
    """Generate upcoming milestones report"""
    today = datetime.now()
    future_date = today + timedelta(days=days_ahead)
    
    # Filter milestones
    milestones = df[
        (df['Is Milestone'] == 'Yes') |
        (df['Task Name'].str.contains('milestone|gate|approval|complete', case=False, na=False))
    ].copy()
    
    # Filter by date range
    upcoming_milestones = milestones[
        (milestones['Finish_parsed'].notna()) & 
        (milestones['Finish_parsed'] >= today) & 
        (milestones['Finish_parsed'] <= future_date)
    ].copy()
    
    if upcoming_milestones.empty:
        return f"No milestones scheduled in the next {days_ahead} days."
    
    # Sort by date
    upcoming_milestones = upcoming_milestones.sort_values('Finish_parsed')
    
    # Create report
    report = f"# UPCOMING MILESTONES ({days_ahead} DAYS)\n"
    report += f"Generated: {today.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    for _, milestone in upcoming_milestones.iterrows():
        days_until = (milestone['Finish_parsed'] - today).days
        
        urgency = "🔴" if days_until <= 3 else "🟡" if days_until <= 7 else "🟢"
        
        report += f"{urgency} **{milestone.get('Task Name', 'Unnamed Milestone')}**\n"
        report += f"   - Due: {milestone['Finish_parsed'].strftime('%Y-%m-%d (%A)')} ({days_until} days)\n"
        report += f"   - Project: {milestone['full_project_name']}\n"
        report += f"   - Progress: {milestone.get('% Complete', '0%')}\n"
        
        if pd.notna(milestone.get('Resource Names', '')):
            report += f"   - Owner: {milestone['Resource Names']}\n"
        
        report += "\n"
    
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
