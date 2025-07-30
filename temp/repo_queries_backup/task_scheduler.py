#!/usr/bin/env python3
"""
Task Scheduler for Control Tower
Move tasks, update dates, reschedule work
Uses proper column mapping to handle CSV structure
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import glob
import argparse
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repo_queries.quick_query import parse_date, load_all_tasks
from column_mapping import (TaskColumns, get_task_name, get_duration, 
                          get_start_date, get_finish_date, get_resource_names, 
                          get_percent_complete, get_project_name_from_path)

def find_task_file(task_name_partial):
    """Find which file contains a task with partial name match"""
    # Ensure we're in the right directory
    if not os.path.exists("cloned_repos"):
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    task_files = glob.glob("cloned_repos/**/tasks.csv", recursive=True)
    
    print(f"Searching in {len(task_files)} task files...")  # Debug output
    
    for file_path in task_files:
        try:
            # Read CSV with proper column handling
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
            
            # If first line starts with "% Complete", it has headers
            if first_line.startswith('% Complete'):
                df = pd.read_csv(file_path)
            else:
                # Read without headers and add them manually
                df = pd.read_csv(file_path, header=None)
                from column_mapping import ACTUAL_COLUMNS
                df.columns = ACTUAL_COLUMNS
            
            # Search for task using the correct column mapping
            # Task names are actually in the 'Task Mode' column (index 5)
            task_name_col = df.columns[TaskColumns.TASK_NAME]  # 'Task Mode' column
            matches = df[df[task_name_col].str.contains(task_name_partial, case=False, na=False)]
            
            if not matches.empty:
                print(f"Found match in {file_path}")  # Debug output
                return file_path, matches
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")  # Debug output
            continue
    
    print("No matches found in any file")  # Debug output
    return None, pd.DataFrame()

def move_task_to_date(task_name_partial, new_date_str):
    """Move a task to a new date"""
    try:
        # Parse new date
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d')
        
        # Find the task
        file_path, matches = find_task_file(task_name_partial)
        
        if matches.empty:
            return f"❌ No task found matching '{task_name_partial}'"
        
        if len(matches) > 1:
            result = f"🔍 Multiple tasks found matching '{task_name_partial}':\n"
            for _, task in matches.iterrows():
                # Use the correct column for task name
                task_name = get_task_name(task.tolist())
                result += f"  - {task_name}\n"
            result += "\nPlease be more specific."
            return result
        
        task = matches.iloc[0]
        task_name = get_task_name(task.tolist())  # Use proper column mapping
        
        # Load the file with proper column handling
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
        
        if first_line.startswith('% Complete'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_csv(file_path, header=None)
            from column_mapping import ACTUAL_COLUMNS
            df.columns = ACTUAL_COLUMNS
        
        # Find the exact row using correct task name column
        task_name_col = df.columns[TaskColumns.TASK_NAME]
        task_index = df[df[task_name_col] == task_name].index[0]
        
        # Get dates using proper column mapping
        start_date_col = df.columns[TaskColumns.START_DATE]
        finish_date_col = df.columns[TaskColumns.FINISH_DATE]
        
        old_start = parse_date(get_start_date(task.tolist()))
        old_finish = parse_date(get_finish_date(task.tolist()))
        
        if old_start and old_finish:
            duration = old_finish - old_start
            new_start = new_date - duration
            
            # Update dates using proper column mapping
            df.at[task_index, start_date_col] = new_start.strftime('%a %d/%m/%y')
            df.at[task_index, finish_date_col] = new_date.strftime('%a %d/%m/%y')
            
        else:
            # Just update finish date using proper column mapping
            df.at[task_index, finish_date_col] = new_date.strftime('%a %d/%m/%y')
        
        # Save file
        df.to_csv(file_path, index=False)
        
        return f"✅ Moved '{task_name}' to {new_date.strftime('%Y-%m-%d')}\n📁 Updated: {file_path}"
        
    except ValueError:
        return f"❌ Invalid date format '{new_date_str}'. Use YYYY-MM-DD format."
    except Exception as e:
        return f"❌ Error: {e}"

def delay_task_by_days(task_name_partial, delay_days):
    """Delay a task by N days"""
    try:
        # Find the task
        file_path, matches = find_task_file(task_name_partial)
        
        if matches.empty:
            return f"❌ No task found matching '{task_name_partial}'"
        
        if len(matches) > 1:
            result = f"🔍 Multiple tasks found matching '{task_name_partial}':\n"
            for _, task in matches.iterrows():
                result += f"  - {task['Task Name']}\n"
            result += "\nPlease be more specific."
            return result
        
        task = matches.iloc[0]
        task_name = task['Task Name']
        
        # Load the file
        df = pd.read_csv(file_path)
        
        # Find the exact row
        task_index = df[df['Task Name'] == task_name].index[0]
        
        # Update dates
        old_start = parse_date(task.get('Start', ''))
        old_finish = parse_date(task.get('Finish', ''))
        
        if old_start:
            new_start = old_start + timedelta(days=delay_days)
            df.at[task_index, 'Start'] = new_start.strftime('%a %d/%m/%y')
        
        if old_finish:
            new_finish = old_finish + timedelta(days=delay_days)
            df.at[task_index, 'Finish'] = new_finish.strftime('%a %d/%m/%y')
        
        # Save file
        df.to_csv(file_path, index=False)
        
        action = "delayed" if delay_days > 0 else "moved forward"
        return f"✅ {task_name} {action} by {abs(delay_days)} days\n📁 Updated: {file_path}"
        
    except Exception as e:
        return f"❌ Error: {e}"

def mark_task_complete(task_name_partial):
    """Mark a task as 100% complete"""
    try:
        # Find the task
        file_path, matches = find_task_file(task_name_partial)
        
        if matches.empty:
            return f"❌ No task found matching '{task_name_partial}'"
        
        if len(matches) > 1:
            result = f"🔍 Multiple tasks found matching '{task_name_partial}':\n"
            for _, task in matches.iterrows():
                result += f"  - {task['Task Name']}\n"
            result += "\nPlease be more specific."
            return result
        
        task = matches.iloc[0]
        task_name = task['Task Name']
        
        # Load the file
        df = pd.read_csv(file_path)
        
        # Find the exact row
        task_index = df[df['Task Name'] == task_name].index[0]
        
        # Mark complete
        df.at[task_index, '% Complete'] = '100%'
        
        # Set actual finish date to today
        if 'Actual Finish' in df.columns:
            df.at[task_index, 'Actual Finish'] = datetime.now().strftime('%a %d/%m/%y')
        
        # Save file
        df.to_csv(file_path, index=False)
        
        return f"✅ Marked '{task_name}' as complete\n📁 Updated: {file_path}"
        
    except Exception as e:
        return f"❌ Error: {e}"

def update_task_progress(task_name_partial, progress_percent):
    """Update task progress percentage"""
    try:
        # Validate progress
        if not (0 <= progress_percent <= 100):
            return "❌ Progress must be between 0 and 100"
        
        # Find the task
        file_path, matches = find_task_file(task_name_partial)
        
        if matches.empty:
            return f"❌ No task found matching '{task_name_partial}'"
        
        if len(matches) > 1:
            result = f"🔍 Multiple tasks found matching '{task_name_partial}':\n"
            for _, task in matches.iterrows():
                result += f"  - {task['Task Name']}\n"
            result += "\nPlease be more specific."
            return result
        
        task = matches.iloc[0]
        task_name = task['Task Name']
        
        # Load the file
        df = pd.read_csv(file_path)
        
        # Find the exact row
        task_index = df[df['Task Name'] == task_name].index[0]
        
        # Update progress
        df.at[task_index, '% Complete'] = f'{progress_percent}%'
        
        # If marking as complete, set actual finish
        if progress_percent == 100 and 'Actual Finish' in df.columns:
            df.at[task_index, 'Actual Finish'] = datetime.now().strftime('%a %d/%m/%y')
        
        # Save file
        df.to_csv(file_path, index=False)
        
        return f"✅ Updated '{task_name}' to {progress_percent}% complete\n📁 Updated: {file_path}"
        
    except Exception as e:
        return f"❌ Error: {e}"

def search_tasks(search_term):
    """Search for tasks across all projects using proper column mapping"""
    print(f"Loading all tasks...")  # Debug
    df = load_all_tasks()
    print(f"Loaded {len(df)} tasks")  # Debug
    
    if df.empty:
        return "No task data found."
    
    # Search in task names using the corrected data structure
    matches = df[df['task_name'].str.contains(search_term, case=False, na=False)]
    print(f"Found {len(matches)} matches")  # Debug
    
    if matches.empty:
        return f"No tasks found matching '{search_term}'"
    
    result = f"🔍 SEARCH RESULTS for '{search_term}':\n"
    result += "=" * 40 + "\n"
    
    for _, task in matches.iterrows():
        # Task names are actually in the Milestone column due to CSV shift
        result += f"📋 {task['task_name']}\n"
        result += f"   📂 {task['project_name']}\n"
        result += f"   📊 {task['percent_complete']} complete\n"
        
        # Show working finish date (actual due date)
        if pd.notna(task.get('Working_Finish_parsed')):
            result += f"   📅 Due: {task['Working_Finish_parsed'].strftime('%Y-%m-%d')}\n"
        elif pd.notna(task.get('Finish_parsed')):  # Fallback
            result += f"   � Due: {task['Finish_parsed'].strftime('%Y-%m-%d')}\n"
        
        # Show working finish date in original format for compatibility 
        working_finish = task.get('Duration', '')  # Duration column has working finish dates
        if working_finish and working_finish != '':
            result += f"   👤 {working_finish}\n"
        
        result += "\n"
    
    return result

def main():
    print("Task Scheduler starting...")  # Debug
    parser = argparse.ArgumentParser(description='Control Tower Task Scheduler')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Move command
    move_parser = subparsers.add_parser('move', help='Move task to specific date')
    move_parser.add_argument('task', help='Partial task name to search for')
    move_parser.add_argument('date', help='New date (YYYY-MM-DD)')
    
    # Delay command
    delay_parser = subparsers.add_parser('delay', help='Delay task by N days')
    delay_parser.add_argument('task', help='Partial task name to search for')
    delay_parser.add_argument('days', type=int, help='Days to delay (negative to move forward)')
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark task as 100% complete')
    complete_parser.add_argument('task', help='Partial task name to search for')
    
    # Progress command
    progress_parser = subparsers.add_parser('progress', help='Update task progress percentage')
    progress_parser.add_argument('task', help='Partial task name to search for')
    progress_parser.add_argument('percent', type=int, help='Progress percentage (0-100)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for tasks')
    search_parser.add_argument('term', help='Search term')
    
    args = parser.parse_args()
    print(f"Command: {args.command}")  # Debug
    
    if args.command == 'move':
        print(move_task_to_date(args.task, args.date))
    elif args.command == 'delay':
        print(delay_task_by_days(args.task, args.days))
    elif args.command == 'complete':
        print(mark_task_complete(args.task))
    elif args.command == 'progress':
        print(update_task_progress(args.task, args.percent))
    elif args.command == 'search':
        print("Starting search...")  # Debug
        print(search_tasks(args.term))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
