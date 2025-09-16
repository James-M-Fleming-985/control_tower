#!/usr/bin/env python3
"""
XML Update Helper for MS Project Data
Use this script to update the XML file and regenerate PowerPoint with latest data
"""

import os
import shutil
from datetime import datetime

def backup_current_xml():
    """Backup current XML file before replacing"""
    xml_path = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    backup_path = f"/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if os.path.exists(xml_path):
        shutil.copy2(xml_path, backup_path)
        print(f"✅ Current XML backed up to: {backup_path}")
    else:
        print(f"❌ XML file not found: {xml_path}")

def check_xml_modification_time():
    """Check when the XML file was last modified"""
    xml_path = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    
    if os.path.exists(xml_path):
        mod_time = os.path.getmtime(xml_path)
        mod_datetime = datetime.fromtimestamp(mod_time)
        print(f"📅 Current XML file last modified: {mod_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if it's recent (within last 24 hours)
        time_diff = datetime.now() - mod_datetime
        if time_diff.total_seconds() < 86400:  # 24 hours
            print(f"✅ File is recent (modified {time_diff.total_seconds()/3600:.1f} hours ago)")
        else:
            print(f"⚠️  File is older (modified {time_diff.days} days ago)")
            print("   Consider updating with latest MS Project export")
    else:
        print(f"❌ XML file not found: {xml_path}")

def generate_updated_powerpoint():
    """Generate PowerPoint with current XML data"""
    import sys
    sys.path.insert(0, '/workspaces/control_tower')
    
    try:
        from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator
        
        print("🎨 Generating PowerPoint with current XML data...")
        generator = SafranPowerPointGenerator()
        result = generator.generate_safran_presentation(datetime.now())
        
        if result:
            print(f"✅ PowerPoint generated: {result}")
        else:
            print("❌ PowerPoint generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔄 MS Project XML Update Helper")
    print("=" * 50)
    
    # Check current XML status
    check_xml_modification_time()
    
    # Backup current XML
    backup_current_xml()
    
    print("\n📋 To update XML file:")
    print("1. Export latest XML from MS Project")
    print("2. Replace the file at: /workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml")
    print("3. Run this script again to generate updated PowerPoint")
    
    print("\n🎨 Generating PowerPoint with current data...")
    generate_updated_powerpoint()
    
    print("\n✅ Ready for XML update when you have the latest file!")
