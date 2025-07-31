#!/usr/bin/env python3
"""
Test the project categorization and find in-progress projects
Enhanced with timeline validation and robustness analysis
"""

import sys
sys.path.insert(0, '/workspaces/control_tower')

from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator
from collections import defaultdict

def analyze_projects():
    generator = SafranPowerPointGenerator()
    
    # Parse all projects
    all_projects = generator._parse_xml_data()
    print(f"📊 Total projects parsed: {len(all_projects)}")
    
    # Remove None phases (Level 1/2 containers that are skipped)
    filtered_projects = [p for p in all_projects if p['phase'] is not None]
    print(f"📊 Projects after filtering Level 1/2 containers: {len(filtered_projects)}")
    
    # Analyze by phase
    phases = ['Documentation & Training', 'Critical Maintenance', 'Post Stabilization Optimization']
    
    timeline_summary = {}
    
    for phase in phases:
        print(f"\n📋 Phase: {phase}")
        phase_projects = generator._get_projects_for_phase(phase, all_projects)
        timeline_summary[phase] = len(phase_projects)
        print(f"   In-progress projects: {len(phase_projects)}")
        
        # Show executive summary of projects
        for i, project in enumerate(phase_projects[:5]):  # Show up to 5
            level_indicator = f"L{project['outline_level']}"
            print(f"   {i+1}. [{level_indicator}] {project['name'][:55]}... - {project['progress']:.1f}%")
        
        if len(phase_projects) > 5:
            print(f"   ... and {len(phase_projects) - 5} more projects")
    
    # Show overall statistics
    print(f"\n📈 Project Progress Statistics:")
    not_started = len([p for p in filtered_projects if p['progress'] == 0])
    in_progress = len([p for p in filtered_projects if 0 < p['progress'] < 100])
    completed = len([p for p in filtered_projects if p['progress'] == 100])
    
    print(f"   Not started (0%): {not_started}")
    print(f"   In progress (0% < x < 100%): {in_progress}")
    print(f"   Completed (100%): {completed}")
    
    # Level distribution analysis
    print(f"\n📊 Hierarchy Level Distribution:")
    level_counts = defaultdict(int)
    level_progress = defaultdict(list)
    
    for project in filtered_projects:
        level = project['outline_level']
        level_counts[level] += 1
        if 0 < project['progress'] < 100:
            level_progress[level].append(project)
    
    for level in sorted(level_counts.keys()):
        in_progress_count = len(level_progress[level])
        print(f"   Level {level}: {level_counts[level]} total ({in_progress_count} in-progress)")
    
    # Timeline slide validation
    print(f"\n🎯 TIMELINE SLIDE VALIDATION:")
    print(f"=" * 50)
    print(f"Documentation & Training Slide: {timeline_summary['Documentation & Training']} Level 4 projects")
    print(f"Critical Maintenance Slide: {timeline_summary['Critical Maintenance']} Level 4 projects")
    print(f"Post Stabilization Optimization Slide: {timeline_summary['Post Stabilization Optimization']} Level 3 projects")
    
    # Robustness assessment 
    print(f"\n🔧 ROBUSTNESS ASSESSMENT:")
    print(f"=" * 50)
    
    # Count Level 3 containers (potential parents for new Level 4 projects)
    level3_containers = [p for p in filtered_projects if p['outline_level'] == 3]
    optimization_containers = [p for p in level3_containers if 'optimization' in p['name'].lower()]
    maintenance_containers = [p for p in level3_containers if 'maintenance' in p['name'].lower()]
    documentation_containers = [p for p in level3_containers if 'documentation' in p['name'].lower() or 'training' in p['name'].lower()]
    
    print(f"✅ Level 3 Containers Available:")
    print(f"   Total Level 3 containers: {len(level3_containers)}")
    print(f"   Optimization containers: {len(optimization_containers)} (auto-assign to optimization slide)")
    print(f"   Maintenance containers: {len(maintenance_containers)} (auto-assign to maintenance slide)")
    print(f"   Documentation containers: {len(documentation_containers)} (auto-assign to documentation slide)")
    
    print(f"\n✅ New Project Scenarios:")
    print(f"   📁 Add Level 4 under existing Level 3 container → AUTOMATIC assignment")
    print(f"   📁 Add Level 3 with 'optimization' keyword → AUTO to optimization slide")
    print(f"   📁 Add Level 3 with 'maintenance' keyword → AUTO to maintenance slide")
    print(f"   📁 Add Level 3 with 'documentation' keyword → AUTO to documentation slide")
    print(f"   📁 Add Level 3 without keywords → FALLBACK to documentation slide")
    
    # Show some examples of successful assignments
    print(f"\n🎯 SUCCESSFUL AUTO-ASSIGNMENTS (Examples):")
    print(f"Level 3 → Post Stabilization Optimization:")
    optimization_level3 = [p for p in level3_containers if p['phase'] == 'Post Stabilization Optimization']
    for project in optimization_level3[:3]:
        print(f"   • {project['name'][:60]}")
    
    print(f"\nLevel 4 → Critical Maintenance:")
    level4_maintenance = [p for p in filtered_projects if p['outline_level'] == 4 and p['phase'] == 'Critical Maintenance']
    for project in level4_maintenance[:2]:
        print(f"   • {project['name'][:60]}")
    
    print(f"\nLevel 4 → Documentation & Training:")
    level4_docs = [p for p in filtered_projects if p['outline_level'] == 4 and p['phase'] == 'Documentation & Training']
    for project in level4_docs[:2]:
        print(f"   • {project['name'][:60]}")

if __name__ == "__main__":
    analyze_projects()
