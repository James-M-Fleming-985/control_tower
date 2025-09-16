#!/usr/bin/env python3
"""
Simple NADCAP Metrics CSV Generator
Creates a simple CSV with key metrics for easy copy/paste to PowerPoint
"""

import pandas as pd
import os
from datetime import datetime

def generate_simple_metrics_csv():
    """Generate simple metrics CSV from compliance action plan"""
    print("📊 Generating simple metrics CSV for PowerPoint...")
    
    # Find the most recent compliance action plan
    outputs_dir = 'outputs'
    compliance_files = [f for f in os.listdir(outputs_dir) 
                      if f.startswith('NADCAP_100_PERCENT_COMPLIANCE_ACTION_PLAN')]
    
    if not compliance_files:
        print("❌ No compliance action plan found")
        return
    
    compliance_file = sorted(compliance_files)[-1]
    compliance_path = os.path.join(outputs_dir, compliance_file)
    print(f"   📋 Loading: {compliance_file}")
    
    # Load the data
    df = pd.read_excel(compliance_path, sheet_name='100_Percent_Compliance_Plan')
    
    # Calculate key metrics
    total_actions = len(df)
    total_hours = df['Estimated_Hours'].sum()
    completion_weeks = round(total_hours / 40)  # 40 hours per week
    
    # Priority breakdown
    priority_counts = df['Priority'].value_counts()
    critical_actions = priority_counts.get('Critical', 0)
    high_actions = priority_counts.get('High', 0)
    medium_actions = priority_counts.get('Medium', 0)
    low_actions = priority_counts.get('Low', 0)
    
    # ZnNi specific
    zn_ni_actions = len(df[df['ZnNi_Specific'] == True])
    zn_ni_percentage = round((zn_ni_actions / total_actions) * 100, 1)
    zn_ni_hours = df[df['ZnNi_Specific'] == True]['Estimated_Hours'].sum()
    
    # Create simple metrics table
    metrics_data = [
        ['Metric', 'Value', 'Unit'],
        ['Total Actions Required', total_actions, 'actions'],
        ['Total Hours Estimated', total_hours, 'hours'],
        ['Implementation Timeline', completion_weeks, 'weeks'],
        ['Critical Priority Actions', critical_actions, 'actions'],
        ['High Priority Actions', high_actions, 'actions'],
        ['Medium Priority Actions', medium_actions, 'actions'],
        ['Low Priority Actions', low_actions, 'actions'],
        ['Priority Actions (Critical + High)', critical_actions + high_actions, 'actions'],
        ['ZnNi Specific Actions', zn_ni_actions, 'actions'],
        ['ZnNi Focus Percentage', zn_ni_percentage, '%'],
        ['ZnNi Specific Hours', zn_ni_hours, 'hours'],
        ['Critical Percentage', round((critical_actions/total_actions)*100, 1), '%'],
        ['High Percentage', round((high_actions/total_actions)*100, 1), '%'],
        ['Average Hours per Action', round(total_hours/total_actions, 1), 'hours'],
    ]
    
    # Create DataFrame and save as CSV
    metrics_df = pd.DataFrame(metrics_data[1:], columns=metrics_data[0])
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'NADCAP_METRICS_POWERPOINT_{timestamp}.csv'
    csv_path = os.path.join(outputs_dir, csv_filename)
    
    metrics_df.to_csv(csv_path, index=False)
    
    print(f"✅ Metrics CSV created: {csv_path}")
    print(f"\n📊 Key Metrics Summary:")
    print(f"   • Total Actions: {total_actions}")
    print(f"   • Timeline: {completion_weeks} weeks")
    print(f"   • Priority Actions: {critical_actions + high_actions}")
    print(f"   • ZnNi Focus: {zn_ni_percentage}%")
    
    # Also create a version formatted for easy PowerPoint copy/paste
    powerpoint_data = [
        ['NADCAP Compliance Metrics', ''],
        ['Total Actions', total_actions],
        ['Implementation Timeline', f'{completion_weeks} weeks'],
        ['Total Hours', f'{total_hours} hours'],
        ['Priority Actions', f'{critical_actions + high_actions} actions'],
        ['Critical Actions', f'{critical_actions} actions'],
        ['High Priority Actions', f'{high_actions} actions'],
        ['ZnNi Line Specific', f'{zn_ni_actions} actions ({zn_ni_percentage}%)'],
        ['Average per Action', f'{round(total_hours/total_actions, 1)} hours'],
    ]
    
    powerpoint_df = pd.DataFrame(powerpoint_data, columns=['Metric', 'Value'])
    powerpoint_filename = f'NADCAP_POWERPOINT_COPY_PASTE_{timestamp}.csv'
    powerpoint_path = os.path.join(outputs_dir, powerpoint_filename)
    
    powerpoint_df.to_csv(powerpoint_path, index=False)
    
    print(f"✅ PowerPoint copy/paste CSV: {powerpoint_path}")
    
    # Create Excel-ready metrics sheet for adding to action plan
    excel_metrics_data = {
        'Metric': [
            'Total Actions', 'Total Hours', 'Completion Weeks', 'Critical Actions',
            'High Actions', 'Medium Actions', 'Low Actions', 'Priority Actions',
            'ZnNi Actions', 'ZnNi Percentage', 'ZnNi Hours', 'Avg Hours/Action'
        ],
        'Formula': [
            '=COUNTA(100_Percent_Compliance_Plan.A:A)-1',  # Total actions (excluding header)
            '=SUM(100_Percent_Compliance_Plan.H:H)',       # Total hours
            '=H2/40',                                       # Completion weeks
            '=COUNTIF(100_Percent_Compliance_Plan.C:C,"Critical")',  # Critical
            '=COUNTIF(100_Percent_Compliance_Plan.C:C,"High")',      # High
            '=COUNTIF(100_Percent_Compliance_Plan.C:C,"Medium")',    # Medium
            '=COUNTIF(100_Percent_Compliance_Plan.C:C,"Low")',       # Low
            '=E2+F2',                                       # Priority actions
            '=COUNTIF(100_Percent_Compliance_Plan.M:M,TRUE)',        # ZnNi actions
            '=J2/B2*100',                                   # ZnNi percentage
            '=SUMIF(100_Percent_Compliance_Plan.M:M,TRUE,100_Percent_Compliance_Plan.H:H)', # ZnNi hours
            '=C2/B2'                                        # Average hours per action
        ],
        'Current_Value': [
            total_actions, total_hours, completion_weeks, critical_actions,
            high_actions, medium_actions, low_actions, critical_actions + high_actions,
            zn_ni_actions, zn_ni_percentage, zn_ni_hours, round(total_hours/total_actions, 1)
        ]
    }
    
    excel_metrics_df = pd.DataFrame(excel_metrics_data)
    excel_metrics_filename = f'NADCAP_EXCEL_METRICS_SHEET_{timestamp}.csv'
    excel_metrics_path = os.path.join(outputs_dir, excel_metrics_filename)
    
    excel_metrics_df.to_csv(excel_metrics_path, index=False)
    
    print(f"✅ Excel metrics sheet template: {excel_metrics_path}")
    print(f"\n💡 Instructions:")
    print(f"   1. Copy {powerpoint_filename} data directly to PowerPoint table")
    print(f"   2. Add {excel_metrics_filename} as 'Metrics' sheet to action plan Excel")
    print(f"   3. Use Formula column for live calculations that update automatically")
    
    return csv_path, powerpoint_path, excel_metrics_path

if __name__ == "__main__":
    generate_simple_metrics_csv()
