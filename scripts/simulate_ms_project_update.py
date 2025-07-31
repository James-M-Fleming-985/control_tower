#!/usr/bin/env python3
"""
Simulate MS Project Update for Testing
Copies the current XML with a newer timestamp to ms_project_data folder
"""

import os
import shutil
from datetime import datetime

def simulate_ms_project_update():
    """Simulate an updated MS Project export"""
    
    source_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    target_dir = "/workspaces/control_tower/cloned_repos/contract_projects/ms_project_data"
    target_file = os.path.join(target_dir, "ZnNi Line Development Plan-08_updated.xml")
    
    if not os.path.exists(source_xml):
        print(f"❌ Source XML not found: {source_xml}")
        return False
    
    # Ensure target directory exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Copy the file
    shutil.copy2(source_xml, target_file)
    
    # Update timestamp to current time
    current_time = datetime.now().timestamp()
    os.utime(target_file, (current_time, current_time))
    
    print(f"✅ Simulated MS Project update")
    print(f"📄 File: {os.path.basename(target_file)}")
    print(f"📁 Location: {target_dir}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%m/%d %H:%M')}")
    print(f"\nNow run: python scripts/safran_workflow.py --repo contract_projects")
    
    return True

if __name__ == "__main__":
    simulate_ms_project_update()
