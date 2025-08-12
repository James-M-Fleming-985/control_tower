#!/usr/bin/env python3

import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime

def test_xml_parsing():
    """Test XML parsing directly"""
    print("🔧 Testing XML parsing functionality")
    
    xml_file_path = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    
    print(f"📂 XML File: {xml_file_path}")
    print(f"📏 File exists: {os.path.exists(xml_file_path)}")
    
    if not os.path.exists(xml_file_path):
        print("❌ XML file not found!")
        return False
    
    try:
        print("📊 Parsing XML...")
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        print(f"✅ Root element: {root.tag}")
        print(f"📋 Root namespace: {root.nsmap if hasattr(root, 'nsmap') else 'N/A'}")
        
        # MS Project XML namespace
        namespace = {'ms': 'http://schemas.microsoft.com/project'}
        
        # Find all tasks
        print("🔍 Looking for tasks...")
        
        # Try with namespace
        tasks_with_ns = root.findall('.//ms:Task', namespace)
        print(f"🏷️ Tasks with namespace: {len(tasks_with_ns)}")
        
        # Try without namespace
        tasks_without_ns = root.findall('.//Task')
        print(f"🏷️ Tasks without namespace: {len(tasks_without_ns)}")
        
        # Check if we have tasks
        tasks = tasks_with_ns if tasks_with_ns else tasks_without_ns
        
        if tasks:
            print(f"\n📋 Found {len(tasks)} tasks total")
            
            # Process first few tasks
            for i, task in enumerate(tasks[:5]):
                try:
                    # Extract task info
                    if tasks_with_ns:
                        task_id = task.find('ms:ID', namespace)
                        task_name = task.find('ms:n', namespace)
                        task_start = task.find('ms:Start', namespace)
                        task_finish = task.find('ms:Finish', namespace)
                        task_percent = task.find('ms:PercentComplete', namespace)
                        task_outline = task.find('ms:OutlineLevel', namespace)
                    else:
                        task_id = task.find('ID')
                        task_name = task.find('n')
                        task_start = task.find('Start')
                        task_finish = task.find('Finish')
                        task_percent = task.find('PercentComplete')
                        task_outline = task.find('OutlineLevel')
                    
                    id_text = task_id.text if task_id is not None else "N/A"
                    name_text = task_name.text if task_name is not None else "N/A"
                    outline_text = task_outline.text if task_outline is not None else "N/A"
                    percent_text = task_percent.text if task_percent is not None else "0"
                    
                    print(f"  {i+1}. ID: {id_text}, Name: {name_text[:50]}{'...' if len(name_text) > 50 else ''}")
                    print(f"      Level: {outline_text}, Progress: {percent_text}%")
                    
                except Exception as e:
                    print(f"  ❌ Error processing task {i+1}: {e}")
            
            return True
        else:
            print("❌ No tasks found in XML file!")
            return False
            
    except Exception as e:
        print(f"❌ XML parsing error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting XML parsing test...")
    success = test_xml_parsing()
    print(f"\n{'✅ Test successful!' if success else '❌ Test failed!'}")
