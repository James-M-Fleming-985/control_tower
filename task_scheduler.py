#!/usr/bin/env python3
"""
Task Scheduler for Control Tower
Move tasks, update dates, reschedule work
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import glob
import argparse
from quick_query import parse_date, load_all_tasks
import os

def find_task_file(task_name_partial):
    """Find which file contains a task with partial name match"""
    task_files = glob.glob("cloned_repos/**/tasks.csv", recursive=True)
    
    for file_path in task_files:
        try:
            df = pd.read_csv(file_path)
            
            # Search for task
            matches = df[df['Task Name'].str.contains(task_name_partial, case=False, na=False)]
            
            if not matches.empty:
                return file_path, matches
                
        except Exception as e:
            continue
    
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
                result += f"  - {task['Task Name']}\n"
            result += "\nPlease be more specific."
            return result
        
        task = matches.iloc[0]
        task_name = task['Task Name']
        
        # Load the file
        df = pd.read_csv(file_path)
        
        # Find the exact row
        task_index = df[df['Task Name'] == task_name].index[0]
        
        # Calculate new finish date
        old_start = parse_date(task.get('Start', ''))
        old_finish = parse_date(task.get('Finish', ''))
        
        if old_start and old_finish:
            duration = old_finish - old_start
            new_start = new_date - duration
            
            # Update dates
            df.at[task_index, 'Start'] = new_start.strftime('%a %d/%m/%y')
            df.at[task_index, 'Finish'] = new_date.strftime('%a %d/%m/%y')
            
        else:
            # Just update finish date
            df.at[task_index, 'Finish'] = new_date.strftime('%a %d/%m/%y')
        
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
    """Search for tasks across all projects"""
    df = load_all_tasks()
    if df.empty:
        return "No task data found."
    
    # Search in task names
    matches = df[df['Task Name'].str.contains(search_term, case=False, na=False)]
    
    if matches.empty:
        return f"No tasks found matching '{search_term}'"
    
    result = f"🔍 SEARCH RESULTS for '{search_term}':\n"
    result += "=" * 40 + "\n"
    
    for _, task in matches.iterrows():
        result += f"📋 {task.get('Task Name', 'Unnamed')}\n"
        result += f"   📂 {task['full_project_name']}\n"
        result += f"   📊 {task.get('% Complete', '0%')} complete\n"
        
        if pd.notna(task.get('Finish_parsed')):
            result += f"   📅 Due: {task['Finish_parsed'].strftime('%Y-%m-%d')}\n"
        
        if pd.notna(task.get('Resource Names', '')):
            result += f"   👤 {task['Resource Names']}\n"
        
        result += "\n"
    
    return result

def main():
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
    
    if args.command == 'move':
        print(move_task_to_date(args.task, args.date))
    elif args.command == 'delay':
        print(delay_task_by_days(args.task, args.days))
    elif args.command == 'complete':
        print(mark_task_complete(args.task))
    elif args.command == 'progress':
        print(update_task_progress(args.task, args.percent))
    elif args.command == 'search':
        print(search_tasks(args.term))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
