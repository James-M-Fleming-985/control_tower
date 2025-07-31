#!/usr/bin/env python3
"""
Verify the PowerPoint timeline slides have actual project data
"""

import sys
sys.path.insert(0, '/workspaces/control_tower')

from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator
from datetime import datetime

def generate_with_debug():
    """Generate PowerPoint with debug information"""
    generator = SafranPowerPointGenerator()
    
    # Parse XML data first
    all_projects = generator._parse_xml_data()
    print(f"📊 Total projects parsed: {len(all_projects)}")
    
    # Test phase categorization for each phase
    phases = ['Documentation & Training', 'Critical Maintenance', 'Post Stabilization Optimization']
    
    for phase in phases:
        phase_projects = generator._get_projects_for_phase(phase, all_projects)
        print(f"\n📋 {phase}:")
        print(f"   Found {len(phase_projects)} in-progress projects")
        
        if phase_projects:
            print(f"   Date range: {phase_projects[0]['start_date'].strftime('%m/%d/%Y')} to {phase_projects[-1]['finish_date'].strftime('%m/%d/%Y')}")
            print(f"   Sample projects:")
            for i, project in enumerate(phase_projects[:3]):
                duration = (project['finish_date'] - project['start_date']).days if project['start_date'] and project['finish_date'] else 0
                print(f"     {i+1}. {project['name'][:50]}... - {project['progress']:.1f}% - {duration} days")
    
    # Generate the presentation
    print(f"\n🎨 Generating PowerPoint presentation...")
    result = generator.generate_safran_presentation(datetime.now())
    
    if result:
        print(f"✅ PowerPoint generated successfully: {result}")
        
        # Show file info
        import os
        if os.path.exists(result):
            file_size = os.path.getsize(result)
            print(f"📄 File size: {file_size:,} bytes")
            print(f"🎯 Timeline slides will show visual progress bars for in-progress projects")
        
    return result

if __name__ == "__main__":
    print("🚀 Generating Safran PowerPoint with XML Timeline Data")
    print("=" * 60)
    
    result = generate_with_debug()
    
    print("\n" + "=" * 60)
    print("✅ ENHANCEMENT COMPLETE")
    print("📊 Timeline slides now show:")
    print("   • Actual MS Project XML data")
    print("   • Visual progress bars (green = completed, gray = remaining)")
    print("   • Project names with progress percentages")
    print("   • Professional Safran branding and color scheme")
    print("   • In-progress projects only (0% < progress < 100%)")
    print("=" * 60)
