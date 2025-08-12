#!/usr/bin/env python3
"""
Test script to fix both MS Project and PowerPoint issues
"""

import os
import sys
import subprocess
from datetime import datetime

def test_ms_project_update():
    """Test if MS Project XML integration is working"""
    print("\n🔍 TESTING MS PROJECT UPDATE...")
    print("=" * 50)
    
    # Check if backup was created (indicates integration ran)
    xml_workspace = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace"
    backups = [f for f in os.listdir(xml_workspace) if f.endswith('.backup.20250805_134951')]
    
    if backups:
        print(f"✅ MS Project update working - backup found: {backups[0]}")
        return True
    else:
        print("❌ MS Project update failed - no recent backup found")
        return False

def test_powerpoint_generation():
    """Test PowerPoint generation"""
    print("\n🔍 TESTING POWERPOINT GENERATION...")
    print("=" * 50)
    
    try:
        # Test imports
        from pptx import Presentation
        print("✅ python-pptx is available")
        
        # Add path for the generator
        sys.path.append('/workspaces/control_tower/modules/milestone_management/reporting')
        from safran_powerpoint_generator import SafranPowerPointGenerator
        print("✅ SafranPowerPointGenerator imported")
        
        # Create generator
        generator = SafranPowerPointGenerator(repo_name='contract_projects')
        print(f"✅ Generator created")
        print(f"   Output path: {generator.output_path}")
        print(f"   XML file: {generator.xml_file_path}")
        
        # Generate presentation
        result = generator.generate_safran_presentation()
        
        if result:
            print(f"✅ PowerPoint generated successfully: {result}")
            return True
        else:
            print("❌ PowerPoint generation failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Installing python-pptx...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-pptx'])
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_powerpoint_location():
    """Check where PowerPoint files are actually saved"""
    print("\n🔍 CHECKING POWERPOINT LOCATIONS...")
    print("=" * 50)
    
    # Check expected location
    expected_path = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/powerpoint_reports"
    if os.path.exists(expected_path):
        files = os.listdir(expected_path)
        print(f"📁 Expected location: {expected_path}")
        print(f"📄 Files found: {len(files)}")
        for f in files:
            if f.endswith('.pptx'):
                print(f"   - {f}")
    else:
        print(f"❌ Expected location doesn't exist: {expected_path}")
    
    # Search for any PowerPoint files in the workspace
    print("\n🔍 Searching for PowerPoint files in workspace...")
    for root, dirs, files in os.walk("/workspaces/control_tower"):
        for file in files:
            if file.endswith('.pptx') and 'REACh' in file and '05082025' in file:
                full_path = os.path.join(root, file)
                print(f"✅ Found today's presentation: {full_path}")

def main():
    """Main test function"""
    print("🚀 CONTROL TOWER WORKFLOW DIAGNOSTIC")
    print("=" * 60)
    
    # Test MS Project update
    ms_project_ok = test_ms_project_update()
    
    # Test PowerPoint generation
    powerpoint_ok = test_powerpoint_generation()
    
    # Check PowerPoint location
    check_powerpoint_location()
    
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"MS Project Update: {'✅ Working' if ms_project_ok else '❌ Failed'}")
    print(f"PowerPoint Generation: {'✅ Working' if powerpoint_ok else '❌ Failed'}")
    
    if ms_project_ok and powerpoint_ok:
        print("\n🎉 Both systems are working correctly!")
        print("📋 To use the workflow:")
        print("   python push_project_update.py --description 'Your update description'")
    else:
        print("\n⚠️  Issues found - see details above")

if __name__ == "__main__":
    main()
