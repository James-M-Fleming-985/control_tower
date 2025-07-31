#!/usr/bin/env python3
"""
Analyze XML outline levels to understand project hierarchy
"""

import sys
sys.path.insert(0, '/workspaces/control_tower')

from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator

def analyze_outline_levels():
    generator = SafranPowerPointGenerator()
    
    # Parse all projects
    all_projects = generator._parse_xml_data()
    print(f"📊 Total projects parsed: {len(all_projects)}")
    
    # Group by phase and outline level
    phases = ['Documentation & Training', 'Critical Maintenance', 'Post Stabilization Optimization']
    
    for phase in phases:
        print(f"\n📋 Phase: {phase}")
        phase_projects = [p for p in all_projects if p['phase'] == phase]
        
        # Group by outline level
        levels = {}
        for project in phase_projects:
            level = project['outline_level']
            if level not in levels:
                levels[level] = []
            levels[level].append(project)
        
        # Show structure by outline level
        for level in sorted(levels.keys()):
            print(f"\n   Outline Level {level}: ({len(levels[level])} items)")
            
            # Show in-progress items at this level
            in_progress = [p for p in levels[level] if 0 < p['progress'] < 100]
            if in_progress:
                print(f"   In-progress items at level {level}:")
                for project in in_progress[:10]:  # Show first 10
                    print(f"     • {project['name'][:60]}... - {project['progress']:.1f}%")
            else:
                print(f"     No in-progress items at level {level}")

if __name__ == "__main__":
    analyze_outline_levels()
