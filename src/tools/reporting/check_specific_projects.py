#!/usr/bin/env python3
"""
Check specific projects mentioned by user
"""

import sys
sys.path.insert(0, '/workspaces/control_tower')

from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator

def check_specific_projects():
    generator = SafranPowerPointGenerator()
    all_projects = generator._parse_xml_data()
    
    # Projects you mentioned
    target_projects = [
        "Analysis Sheet (Table 1 Implementation) Complete",
        "SF Investment Strategy OEE & OLE Application", 
        "SF Investment Strategy Planning FO Application",
        "Vat 8 Remove & Install",
        "ZnNi Line Flow Rate Optimization",
        "ZnNi Line Kardex Optimization",
        "ZnNi Line First Line Maintenance Plan Roll Out",
        "ZnNi Line Chiller System Optimization",
        "SF Operational Documentation (inc. Training) Optimization",
        "LIMs Roll Out"
    ]
    
    print("🔍 Searching for your specific projects...")
    
    for target in target_projects:
        print(f"\n📋 Looking for: '{target}'")
        found = False
        
        for project in all_projects:
            if target.lower() in project['name'].lower():
                print(f"   ✅ Found: '{project['name']}'")
                print(f"      Phase: {project['phase']}")
                print(f"      Progress: {project['progress']:.1f}%")
                print(f"      Outline Level: {project['outline_level']}")
                found = True
                
        if not found:
            print(f"   ❌ Not found exactly, checking partial matches...")
            partial_matches = []
            for project in all_projects:
                # Check for partial matches
                target_words = target.lower().split()
                project_words = project['name'].lower().split()
                
                # If most words match
                match_count = sum(1 for word in target_words if any(word in pword for pword in project_words))
                if match_count >= len(target_words) * 0.6:  # 60% word match
                    partial_matches.append(project)
            
            if partial_matches:
                print(f"   📝 Partial matches:")
                for match in partial_matches[:3]:
                    print(f"      • '{match['name']}' - {match['progress']:.1f}% - Level {match['outline_level']}")

if __name__ == "__main__":
    check_specific_projects()
