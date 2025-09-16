#!/usr/bin/env python3
"""
Restructure professional_excellence to remove unnecessary levels that confuse Control Tower.
This will flatten contract_projects/projects/ into a clean Level 2 Project structure.
"""
import os
import shutil
import json
from datetime import datetime

def restructure_professional_excellence(base_path):
    """Restructure professional_excellence to remove confusing intermediate levels"""
    pe_path = os.path.join(base_path, 'cloned_repos', 'professional_excellence')
    
    if not os.path.exists(pe_path):
        print(f"❌ professional_excellence not found at {pe_path}")
        return False
    
    print("🔧 RESTRUCTURING PROFESSIONAL_EXCELLENCE")
    print("=" * 60)
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(base_path, 'backups', f'professional_excellence_restructure_{timestamp}')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup current structure
    current_structure = os.path.join(pe_path, 'contract_projects')
    if os.path.exists(current_structure):
        backup_target = os.path.join(backup_dir, 'contract_projects_original')
        shutil.copytree(current_structure, backup_target)
        print(f"✅ Backup created: {backup_target}")
    
    # Identify the problematic structure
    projects_path = os.path.join(pe_path, 'contract_projects', 'projects')
    if not os.path.exists(projects_path):
        print("❌ Expected structure contract_projects/projects/ not found")
        return False
    
    # List all projects in the projects folder
    projects = [d for d in os.listdir(projects_path) 
               if os.path.isdir(os.path.join(projects_path, d))]
    
    print(f"📂 Found {len(projects)} projects to move:")
    for project in projects:
        print(f"  - {project}")
    
    # Move each project directly to professional_excellence root level
    for project in projects:
        source = os.path.join(projects_path, project)
        target = os.path.join(pe_path, project)
        
        if os.path.exists(target):
            print(f"⚠️  Target already exists: {target}")
            # Create unique name
            counter = 1
            while os.path.exists(f"{target}_{counter}"):
                counter += 1
            target = f"{target}_{counter}"
            print(f"   Moving to: {target}")
        
        shutil.move(source, target)
        print(f"✅ Moved: {project} → Level 2")
    
    # Remove now-empty intermediate directories
    if os.path.exists(projects_path) and not os.listdir(projects_path):
        os.rmdir(projects_path)
        print("✅ Removed empty projects/ directory")
    
    # Check if contract_projects is now empty (except for .git and xml_workspace)
    contract_contents = os.listdir(os.path.join(pe_path, 'contract_projects'))
    important_contents = [item for item in contract_contents if item not in ['.git', 'xml_workspace']]
    
    if not important_contents:
        print("ℹ️  contract_projects/ now only contains .git and xml_workspace")
        print("   Consider if these should be moved or if the folder can be renamed")
    
    # Create requirements folders for the new structure
    create_requirements_structure(pe_path, projects)
    
    # Verify the new structure
    verify_restructuring(pe_path, projects)
    
    return True

def create_requirements_structure(pe_path, projects):
    """Create requirements/ folders at each level of the new hierarchy"""
    print("\n📁 CREATING REQUIREMENTS STRUCTURE")
    print("=" * 60)
    
    # Level 1 already has requirements folder
    level1_req = os.path.join(pe_path, 'requirements')
    if os.path.exists(level1_req):
        print("✅ Level 1 requirements/ already exists")
    else:
        os.makedirs(level1_req, exist_ok=True)
        print("✅ Created Level 1 requirements/")
    
    # Create requirements for each project (Level 2)
    for project in projects:
        project_path = os.path.join(pe_path, project)
        if not os.path.exists(project_path):
            continue
            
        # Level 2 - Project requirements
        level2_req = os.path.join(project_path, 'requirements')
        os.makedirs(level2_req, exist_ok=True)
        print(f"✅ Created Level 2 requirements/ for {project}")
        
        # Level 3 - Workpackage requirements
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path) and item != 'requirements':
                level3_req = os.path.join(item_path, 'requirements')
                os.makedirs(level3_req, exist_ok=True)
                print(f"✅ Created Level 3 requirements/ for {project}/{item}")
                
                # Level 4 - Milestone requirements
                for subitem in os.listdir(item_path):
                    subitem_path = os.path.join(item_path, subitem)
                    if os.path.isdir(subitem_path) and subitem != 'requirements':
                        level4_req = os.path.join(subitem_path, 'requirements')
                        os.makedirs(level4_req, exist_ok=True)
                        print(f"✅ Created Level 4 requirements/ for {project}/{item}/{subitem}")

def verify_restructuring(pe_path, projects):
    """Verify the restructuring was successful"""
    print("\n🔍 VERIFYING RESTRUCTURING")
    print("=" * 60)
    
    success = True
    
    # Check that projects are now at Level 2
    for project in projects:
        project_path = os.path.join(pe_path, project)
        if os.path.exists(project_path):
            print(f"✅ {project} successfully moved to Level 2")
            
            # Check for requirements folder
            req_path = os.path.join(project_path, 'requirements')
            if os.path.exists(req_path):
                print(f"✅ {project} has requirements/ folder")
            else:
                print(f"❌ {project} missing requirements/ folder")
                success = False
        else:
            print(f"❌ {project} not found at Level 2")
            success = False
    
    # Verify new hierarchy levels
    print("\n📊 NEW HIERARCHY STRUCTURE:")
    print("Level 1: professional_excellence (North Star)")
    for project in projects:
        if os.path.exists(os.path.join(pe_path, project)):
            print(f"Level 2: {project} (Project)")
            
            # Show workpackages
            project_path = os.path.join(pe_path, project)
            for item in os.listdir(project_path):
                if os.path.isdir(os.path.join(project_path, item)) and item != 'requirements':
                    print(f"  Level 3: {item} (Workpackage)")
    
    if success:
        print("\n🎉 RESTRUCTURING SUCCESSFUL!")
        print("✅ Removed confusing intermediate levels")
        print("✅ Clear Level 2 Projects established")
        print("✅ Requirements structure in place")
        print("✅ Control Tower can now properly detect hierarchy levels")
    else:
        print("\n⚠️  RESTRUCTURING HAD ISSUES - Check above for details")
    
    return success

if __name__ == "__main__":
    base_path = "/workspaces/control_tower"
    success = restructure_professional_excellence(base_path)
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. Test Control Tower hierarchy detection on restructured professional_excellence")
        print("2. Verify requirements management works through all levels")
        print("3. Update any scripts that reference the old structure")
        print("4. Consider applying similar restructuring to other projects if needed")
    else:
        print("\n🔧 MANUAL INTERVENTION REQUIRED")
        print("Check the issues above and resolve before proceeding")