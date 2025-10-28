#!/usr/bin/env python3
"""
Update NADCAP Action Plan due dates from Oct 29, 2025 to Feb 28, 2026
Spreads the dates evenly across the timeframe
"""

from openpyxl import load_workbook
from pathlib import Path
from datetime import datetime, timedelta
import shutil

def update_due_dates():
    # File paths
    wb_path = Path('cloned_repos/professional_excellence/projects/PROJECT-001 NADCAP COMPLIANCE/inputs/NADCAP 2026 Action Plan-291025.xlsx')
    backup_path = wb_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    
    # Create backup
    shutil.copy2(wb_path, backup_path)
    print(f"✅ Backup created: {backup_path.name}")
    
    # Load workbook
    wb = load_workbook(filename=str(wb_path))
    ap = wb['Action Plan']
    
    # Define date range
    start_date = datetime(2025, 10, 29)  # Tomorrow
    end_date = datetime(2026, 2, 28)     # End of February 2026
    total_days = (end_date - start_date).days
    
    print(f"📅 Date Range: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}")
    print(f"⏱️  Total days: {total_days}")
    
    # Count actual actions to update
    actions = []
    for r in range(2, ap.max_row + 1):
        if ap.cell(row=r, column=1).value:  # Has Action ID
            actions.append(r)
    
    total_actions = len(actions)
    print(f"📋 Actions to update: {total_actions}")
    
    if total_actions == 0:
        print("❌ No actions found to update!")
        return
    
    # Calculate date intervals
    days_per_action = total_days / total_actions
    print(f"⚡ Days per action: {days_per_action:.1f}")
    
    # Update due dates
    updated_count = 0
    
    for i, row in enumerate(actions):
        # Calculate due date for this action
        days_offset = int(i * days_per_action)
        due_date = start_date + timedelta(days=days_offset)
        
        # Update the cell (Column F = Due Date)
        old_date = ap.cell(row=row, column=6).value
        ap.cell(row=row, column=6, value=due_date.date())
        
        action_id = ap.cell(row=row, column=1).value
        print(f"  {action_id}: {old_date} → {due_date.strftime('%Y-%m-%d')}")
        
        updated_count += 1
    
    # Save the workbook
    wb.save(str(wb_path))
    print(f"\n✅ Updated {updated_count} due dates")
    print(f"💾 Saved to: {wb_path.name}")
    
    # Show date distribution
    print(f"\n📊 DATE DISTRIBUTION:")
    print(f"   Start: {start_date.strftime('%B %d, %Y')}")
    print(f"   End:   {end_date.strftime('%B %d, %Y')}")
    print(f"   Spread: {total_days} days across {total_actions} actions")
    
    # Show sample dates
    print(f"\n📅 SAMPLE SCHEDULE:")
    sample_indices = [0, total_actions//4, total_actions//2, 3*total_actions//4, total_actions-1]
    for i in sample_indices:
        if i < len(actions):
            row = actions[i]
            action_id = ap.cell(row=row, column=1).value
            due_date = ap.cell(row=row, column=6).value
            print(f"   {action_id}: {due_date}")

if __name__ == "__main__":
    update_due_dates()