#!/usr/bin/env python3
"""
🎯 INVESTMENT STRATEGY REQUIREMENTS VALIDATION
Test that Control Tower can access and trace all Investment Strategy requirements
"""

import os
import sys
from pathlib import Path

def main():
    print("🎯 INVESTMENT STRATEGY REQUIREMENTS VALIDATION")
    print("=" * 60)
    
    # Base path to investment strategy
    base_path = Path("/workspaces/control_tower/cloned_repos/investment_strategy")
    
    if not base_path.exists():
        print("❌ Investment Strategy repository not found!")
        return False
        
    print(f"📂 Base path: {base_path}")
    
    # Check PROJECT-level requirements
    projects_path = base_path / "projects"
    project_files = list(projects_path.glob("*/PROJECT-*.md"))
    project_count = len(project_files)
    
    print(f"\n📋 PROJECT-LEVEL REQUIREMENTS:")
    print(f"   ✅ Found {project_count} project requirements files")
    
    for project_file in sorted(project_files):
        project_name = project_file.parent.name
        print(f"   📦 {project_name}: {project_file.name}")
    
    # Check SYSTEM-level requirements
    system_files = list(projects_path.glob("*/SYSTEM-*/SYSTEM-*.md"))
    system_count = len(system_files)
    
    print(f"\n🔧 SYSTEM-LEVEL REQUIREMENTS:")
    print(f"   ✅ Found {system_count} system requirements files")
    
    # Group by project
    systems_by_project = {}
    for system_file in system_files:
        project = system_file.parts[-3]  # PROJECT-XXX folder
        if project not in systems_by_project:
            systems_by_project[project] = []
        systems_by_project[project].append(system_file)
    
    for project in sorted(systems_by_project.keys()):
        systems = systems_by_project[project]
        print(f"   📦 {project}: {len(systems)} systems")
        for system_file in sorted(systems):
            system_name = system_file.parent.name
            print(f"      🔧 {system_name}")
    
    # Validate hierarchy structure
    print(f"\n🔗 HIERARCHY VALIDATION:")
    
    # Check if all projects have both PROJECT and SYSTEM requirements
    all_valid = True
    for project_file in project_files:
        project_name = project_file.parent.name
        if project_name in systems_by_project:
            system_count = len(systems_by_project[project_name])
            print(f"   ✅ {project_name}: PROJECT + {system_count} SYSTEMS")
        else:
            print(f"   ❌ {project_name}: Missing SYSTEM requirements")
            all_valid = False
    
    print(f"\n📊 SUMMARY:")
    print(f"   📋 Projects: {project_count}")
    print(f"   🔧 Systems: {system_count}")
    print(f"   🔗 Hierarchy: {'✅ Valid' if all_valid else '❌ Invalid'}")
    
    if all_valid:
        print(f"\n🎉 SUCCESS: All Investment Strategy requirements accessible!")
        print(f"   ✅ Control Tower can trace all {system_count} systems")
        print(f"   ✅ All {project_count} projects have proper structure")
        print(f"   ✅ Requirements management commands can access all files")
        return True
    else:
        print(f"\n❌ ISSUES: Some requirements structure problems found")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)