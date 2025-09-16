#!/usr/bin/env python3
"""
Analyze the professional_excellence structure to identify unnecessary levels
that would confuse Control Tower's hierarchy detection.
"""
import os
import json

def analyze_structure(base_path):
    """Analyze the professional_excellence structure"""
    pe_path = os.path.join(base_path, 'cloned_repos', 'professional_excellence')
    
    if not os.path.exists(pe_path):
        print(f"❌ professional_excellence not found at {pe_path}")
        return
    
    print("🔍 ANALYZING PROFESSIONAL_EXCELLENCE STRUCTURE")
    print("=" * 60)
    
    structure = {}
    
    # Walk through the directory structure
    for root, dirs, files in os.walk(pe_path):
        rel_path = os.path.relpath(root, pe_path)
        level = rel_path.count(os.sep) + 1 if rel_path != '.' else 1
        
        # Skip deep levels for overview
        if level <= 6:
            indent = "  " * (level - 1)
            folder_name = os.path.basename(root) if root != pe_path else "professional_excellence"
            print(f"{indent}Level {level}: {folder_name}")
            
            if level not in structure:
                structure[level] = []
            structure[level].append({
                'name': folder_name,
                'path': rel_path,
                'files': files,
                'subdirs': dirs
            })
    
    print("\n📊 STRUCTURE ANALYSIS")
    print("=" * 60)
    
    # Analyze the problematic path
    safran_path = os.path.join(pe_path, 'contract_projects', 'projects', 'Safran SF Optimization')
    if os.path.exists(safran_path):
        print("Current structure:")
        print("Level 1: professional_excellence (North Star)")
        print("Level 2: contract_projects (Unclear - Extra level?)")
        print("Level 3: projects (Unclear - Extra level?)")
        print("Level 4: Safran SF Optimization (Project?)")
        print("Level 5: 1_ZnNi_Line_Stabilization... (Workpackage?)")
        print("Level 6: Analysis_Sheet_Table_1_Implementation (Milestone?)")
        
        print("\n🎯 RECOMMENDED STRUCTURE")
        print("=" * 60)
        print("Option 1 - Remove intermediate levels:")
        print("Level 1: professional_excellence (North Star)")
        print("Level 2: Safran SF Optimization (Project)")
        print("Level 3: 1_ZnNi_Line_Stabilization... (Workpackage)")
        print("Level 4: Analysis_Sheet_Table_1_Implementation (Milestone)")
        print("Level 5: [Individual tasks] (Tasks)")
        
        print("\nOption 2 - Treat as Application project:")
        print("Level 1: professional_excellence (North Star)")
        print("Level 2: Safran SF Optimization (Project)")
        print("Level 3: ZnNi_Line_System (System)")
        print("Level 4: Stabilization_Feature (Feature)")
        print("Level 5: Documentation_Layer (Layer)")
        
        # Check for requirements folders
        print("\n📁 REQUIREMENTS FOLDER CHECK")
        print("=" * 60)
        requirements_found = []
        for level in range(1, 7):
            if level == 1:
                req_path = os.path.join(pe_path, 'requirements')
            elif level == 2:
                req_path = os.path.join(pe_path, 'contract_projects', 'requirements')
            elif level == 3:
                req_path = os.path.join(pe_path, 'contract_projects', 'projects', 'requirements')
            elif level == 4:
                req_path = os.path.join(safran_path, 'requirements')
            elif level == 5:
                req_path = os.path.join(safran_path, '1_ZnNi_Line_Stabilization_Critical_Documentation_and_Training', 'requirements')
            elif level == 6:
                req_path = os.path.join(safran_path, '1_ZnNi_Line_Stabilization_Critical_Documentation_and_Training', 'Analysis_Sheet_Table_1_Implementation', 'requirements')
            
            if os.path.exists(req_path):
                requirements_found.append(f"✅ Level {level}: {req_path}")
            else:
                requirements_found.append(f"❌ Level {level}: Missing requirements/")
        
        for req in requirements_found:
            print(req)
    
    print("\n🚨 CONTROL TOWER CONFUSION POINTS")
    print("=" * 60)
    print("1. contract_projects/ and projects/ create ambiguous intermediate levels")
    print("2. Control Tower can't determine if Level 2 is Projects or Systems")
    print("3. No requirements/ folders found - requirements management will fail")
    print("4. Six levels deep but unclear what each level represents")
    print("5. Phase numbers (1_, 2_, 3_) suggest temporal rather than hierarchical organization")
    
    print("\n💡 RESTRUCTURING RECOMMENDATION")
    print("=" * 60)
    print("IMMEDIATE ACTION: Remove contract_projects/projects/ nesting")
    print("RESULT: professional_excellence/Safran SF Optimization/[workpackages]/[milestones]")
    print("BENEFIT: Clear Level 2 (Project) → Level 3 (Workpackage) → Level 4 (Milestone) structure")
    print("REQUIREMENT: Add requirements/ folders at each level for requirements management")

if __name__ == "__main__":
    base_path = "/workspaces/control_tower"
    analyze_structure(base_path)