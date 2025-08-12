#!/usr/bin/env python3
"""
Direct execution of the CSV to XML conversion
"""

import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

def simple_csv_to_xml():
    csv_file = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/1_ZnNi_Line_Stabilization_Critical_Documentation_and_Training/SF_OEE_and_OLE/SF_Investment_Strategy_OEE_OLE_Import.csv"
    output_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/SF_Investment_Strategy_COMPLETE_TEST.xml"
    
    print("🔄 Simple CSV to XML Converter")
    print("=" * 50)
    
    # Read CSV
    tasks = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Name', '').strip():
                tasks.append({
                    'id': row.get('ID', '').strip(),
                    'name': row.get('Name', '').strip(),
                    'duration': row.get('Duration', '').strip(),
                    'start': row.get('Start', '').strip(),
                    'finish': row.get('Finish', '').strip(),
                    'milestone': row.get('Milestone', '').strip().lower() == 'yes'
                })
    
    print(f"📋 Loaded {len(tasks)} tasks")
    
    # Create basic XML
    root = ET.Element("Project", xmlns="http://schemas.microsoft.com/project")
    
    # Basic project info
    ET.SubElement(root, "Name").text = "SF Investment Strategy OEE & OLE Application"
    ET.SubElement(root, "Title").text = "SF Investment Strategy OEE & OLE Application"
    ET.SubElement(root, "CreationDate").text = datetime.now().isoformat()
    
    # Tasks
    tasks_elem = ET.SubElement(root, "Tasks")
    for task in tasks:
        task_elem = ET.SubElement(tasks_elem, "Task")
        ET.SubElement(task_elem, "UID").text = task['id']
        ET.SubElement(task_elem, "ID").text = task['id']
        ET.SubElement(task_elem, "Name").text = task['name']
        ET.SubElement(task_elem, "Milestone").text = "1" if task['milestone'] else "0"
    
    # Write XML
    tree = ET.ElementTree(root)
    tree.write(output_xml, encoding='utf-8', xml_declaration=True)
    
    print(f"✅ Basic XML created: {output_xml}")
    print(f"📊 Tasks: {len(tasks)}")
    
if __name__ == "__main__":
    simple_csv_to_xml()
