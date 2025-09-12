#!/usr/bin/env python3
"""
Friday Workflow Implementation
Complete Friday workflow: XML sync, comparison, and PowerPoint generation
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import subprocess
import glob

# Add module paths
sys.path.append('/workspaces/control_tower/modules')
sys.path.append('/workspaces/control_tower/modules/ms_project')

def find_latest_friday_snapshot():
    """Find the most recent Friday snapshot for comparison."""
    snapshots_dir = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/snapshots"
    
    if not os.path.exists(snapshots_dir):
        print("❌ Snapshots directory not found")
        return None
    
    # Look for Friday snapshots
    friday_files = glob.glob(os.path.join(snapshots_dir, "friday_*_ZnNi_Line_Development_Plan-08.xml"))
    
    if not friday_files:
        print("❌ No Friday snapshots found")
        return None
    
    # Sort by filename (which includes date) and get the most recent
    friday_files.sort(reverse=True)
    latest = friday_files[0]
    
    print(f"📅 Latest Friday snapshot: {os.path.basename(latest)}")
    return latest

def sync_xml_to_current():
    """Sync XML from ms_project_data to current folder."""
    print("🔄 Step 1: Syncing XML to current folder...")
    
    try:
        result = subprocess.run([
            'python', '-m', 'modules.ms_project.auto_sync_scheduler', '--once'
        ], capture_output=True, text=True, cwd='/workspaces/control_tower')
        
        if result.returncode == 0:
            print("✅ XML sync completed successfully")
            return True
        else:
            print(f"❌ XML sync failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error during XML sync: {e}")
        return False

def generate_individual_milestone_slides():
    """Generate individual milestone slides (the working part)."""
    print("📊 Step 2: Generating individual milestone slides...")
    
    try:
        result = subprocess.run([
            'python', 'control_tower.py', 'ms-project', '--action', 'reports', '--period', 'current'
        ], capture_output=True, text=True, cwd='/workspaces/control_tower')
        
        if result.returncode == 0:
            print("✅ Individual milestone slides generated successfully")
            return True
        else:
            print(f"⚠️  Individual slides generation: {result.stderr}")
            # Try alternative approach
            return generate_milestone_slides_alternative()
    except Exception as e:
        print(f"⚠️  Error generating slides: {e}")
        return generate_milestone_slides_alternative()

def generate_milestone_slides_alternative():
    """Alternative milestone slide generation."""
    print("🔄 Trying alternative milestone generation...")
    
    # Check if safran generator exists
    safran_generator = "/workspaces/control_tower/modules/milestone_management/reporting/safran_powerpoint_generator.py"
    
    if os.path.exists(safran_generator):
        try:
            result = subprocess.run([
                'python', safran_generator
            ], capture_output=True, text=True, cwd='/workspaces/control_tower')
            
            if result.returncode == 0:
                print("✅ Alternative milestone generation successful")
                return True
            else:
                print(f"❌ Alternative generation failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error in alternative generation: {e}")
    
    return False

def create_combined_dashboard():
    """Create the combined 4-table dashboard."""
    print("🎯 Step 3: Creating combined dashboard...")
    
    # Try the new advanced approach first
    try:
        result = subprocess.run([
            'python', 'powerpoint/advanced_dashboard_creation.py'
        ], capture_output=True, text=True, cwd='/workspaces/control_tower')
        
        if result.returncode == 0:
            print("✅ Advanced dashboard created successfully")
            return True
        else:
            print(f"⚠️  Advanced dashboard: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Error with advanced dashboard: {e}")
    
    # Fallback to Word approach
    try:
        result = subprocess.run([
            'python', 'powerpoint/word_to_powerpoint_dashboard.py'
        ], capture_output=True, text=True, cwd='/workspaces/control_tower')
        
        if result.returncode == 0:
            print("✅ Word-to-PowerPoint dashboard created successfully")
            return True
        else:
            print(f"❌ Word dashboard failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error with Word dashboard: {e}")
    
    return False

def compare_xml_versions(current_xml=None, previous_xml=None):
    """Compare current XML with previous Friday's version."""
    print("📊 Step 4: Comparing XML versions...")
    
    if not current_xml:
        current_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/current/ZnNi Line Development Plan-08.xml"
    
    if not previous_xml:
        previous_xml = find_latest_friday_snapshot()
    
    if not os.path.exists(current_xml):
        print(f"❌ Current XML not found: {current_xml}")
        return False
    
    if not previous_xml or not os.path.exists(previous_xml):
        print("⚠️  No previous Friday snapshot found for comparison")
        return False
    
    # Basic comparison (can be enhanced later)
    current_size = os.path.getsize(current_xml)
    previous_size = os.path.getsize(previous_xml)
    
    current_mtime = os.path.getmtime(current_xml)
    previous_mtime = os.path.getmtime(previous_xml)
    
    print(f"📊 Current XML: {current_size:,} bytes, modified {datetime.fromtimestamp(current_mtime)}")
    print(f"📊 Previous XML: {previous_size:,} bytes, modified {datetime.fromtimestamp(previous_mtime)}")
    
    size_diff = current_size - previous_size
    if size_diff != 0:
        print(f"📈 Size change: {size_diff:+,} bytes")
    else:
        print("📊 No size change detected")
    
    return True

def friday_workflow(compare_only=False, generate_only=False):
    """Execute the complete Friday workflow."""
    print("🚀 Starting Friday Workflow...")
    print(f"📅 Date: {datetime.now().strftime('%A, %B %d, %Y')}")
    print("="*60)
    
    success_steps = 0
    total_steps = 4
    
    if not generate_only:
        # Step 1: Sync XML
        if sync_xml_to_current():
            success_steps += 1
        
        # Step 4: Compare versions (moved up for visibility)
        if compare_xml_versions():
            success_steps += 1
    
    if not compare_only:
        # Step 2: Generate individual slides
        if generate_individual_milestone_slides():
            success_steps += 1
        
        # Step 3: Create combined dashboard
        if create_combined_dashboard():
            success_steps += 1
    
    # Results
    print("="*60)
    print(f"🎯 Friday Workflow Results: {success_steps}/{total_steps} steps completed")
    
    if success_steps == total_steps:
        print("✅ Friday workflow completed successfully!")
        print("📁 Check /reports/ folder for generated files")
    elif success_steps >= 2:
        print("⚠️  Friday workflow partially completed")
        print("📁 Some files may have been generated successfully")
    else:
        print("❌ Friday workflow failed")
    
    return success_steps >= 2

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Friday Workflow - Complete automation')
    parser.add_argument('--compare-only', action='store_true', 
                       help='Only compare XML versions, don\'t generate presentations')
    parser.add_argument('--generate-only', action='store_true',
                       help='Only generate presentations, don\'t sync or compare')
    parser.add_argument('--compare-to-last-week', action='store_true',
                       help='Compare current XML to last Friday\'s snapshot')
    
    args = parser.parse_args()
    
    if args.compare_to_last_week:
        # Just do comparison
        current_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/current/ZnNi Line Development Plan-08.xml"
        previous_xml = find_latest_friday_snapshot()
        return compare_xml_versions(current_xml, previous_xml)
    else:
        # Full workflow
        return friday_workflow(
            compare_only=args.compare_only,
            generate_only=args.generate_only
        )

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
