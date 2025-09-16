#!/usr/bin/env python3
"""
Create requirements folder structure for the remaining actual projects:
- business_ventures/Causal_affect
- business_ventures/financial_optimizer  
- business_ventures/opti_royale

Also ensure all repositories have Level 1 requirements folders.
"""
import os
import shutil
from datetime import datetime

def create_requirements_for_remaining_projects():
    """Create requirements structure for all remaining projects"""
    print("🔧 CREATING REQUIREMENTS STRUCTURE FOR REMAINING PROJECTS")
    print("=" * 65)
    
    base_path = "/workspaces/control_tower/cloned_repos"
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/workspaces/control_tower/backups/requirements_creation_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Projects that need requirements structure
    projects_to_fix = [
        ("business_ventures", "Causal_affect"),
        ("business_ventures", "financial_optimizer"), 
        ("business_ventures", "opti_royale")
    ]
    
    # All repositories that need Level 1 requirements
    repositories = [
        "business_ventures",
        "financial_security", 
        "investment_strategy",
        "life_quality",
        "online_presence", 
        "professional_excellence"
    ]
    
    success_count = 0
    
    # 1. Ensure all repositories have Level 1 requirements
    print("📁 Step 1: Creating Level 1 requirements folders")
    print("-" * 50)
    
    for repo in repositories:
        repo_path = os.path.join(base_path, repo)
        level1_req = os.path.join(repo_path, "requirements")
        
        if not os.path.exists(level1_req):
            os.makedirs(level1_req, exist_ok=True)
            print(f"✅ Created {repo}/requirements/")
        else:
            print(f"✅ {repo}/requirements/ already exists")
    
    # 2. Create full hierarchy for actual projects
    print(f"\n🎯 Step 2: Creating full requirements hierarchy for actual projects")
    print("-" * 50)
    
    for repo_name, project_name in projects_to_fix:
        project_path = os.path.join(base_path, repo_name, project_name)
        
        if not os.path.exists(project_path):
            print(f"❌ Project not found: {repo_name}/{project_name}")
            continue
        
        print(f"\n📂 Processing: {repo_name}/{project_name}")
        
        # Backup current state
        backup_target = os.path.join(backup_dir, f"{repo_name}_{project_name}")
        if os.path.exists(project_path):
            shutil.copytree(project_path, backup_target)
            print(f"   💾 Backup created: {backup_target}")
        
        # Create requirements structure
        if create_project_requirements_structure(project_path, project_name):
            success_count += 1
            print(f"   ✅ Requirements structure created for {project_name}")
        else:
            print(f"   ❌ Failed to create requirements for {project_name}")
    
    # 3. Verification
    print(f"\n🔍 Step 3: Verification")
    print("-" * 50)
    
    verify_requirements_structure(base_path, projects_to_fix)
    
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    print(f"✅ Successfully processed: {success_count}/{len(projects_to_fix)} projects")
    print(f"💾 Backup created at: {backup_dir}")
    
    if success_count == len(projects_to_fix):
        print(f"\n🎉 ALL PROJECTS NOW HAVE REQUIREMENTS STRUCTURE!")
        print("   Ready for template population")
        return True
    else:
        print(f"\n⚠️  Some projects had issues - check above for details")
        return False

def create_project_requirements_structure(project_path, project_name):
    """Create requirements folders at all levels of a project"""
    try:
        # Level 2: Project requirements
        level2_req = os.path.join(project_path, "requirements")
        os.makedirs(level2_req, exist_ok=True)
        print(f"      ✅ Level 2: requirements/")
        
        # Level 3: For each directory in project (Systems/Workpackages)
        level3_count = 0
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path) and item != "requirements" and not item.startswith('.'):
                level3_req = os.path.join(item_path, "requirements")
                os.makedirs(level3_req, exist_ok=True)
                level3_count += 1
                print(f"      ✅ Level 3: {item}/requirements/")
                
                # Level 4: For each subdirectory (Features/Milestones)
                level4_count = 0
                try:
                    for subitem in os.listdir(item_path):
                        subitem_path = os.path.join(item_path, subitem)
                        if os.path.isdir(subitem_path) and subitem != "requirements" and not subitem.startswith('.'):
                            level4_req = os.path.join(subitem_path, "requirements")
                            os.makedirs(level4_req, exist_ok=True)
                            level4_count += 1
                            
                            # Level 5: For each sub-subdirectory (Layers/Tasks) - but limit depth
                            level5_count = 0
                            try:
                                for subsubitem in os.listdir(subitem_path):
                                    subsubitem_path = os.path.join(subitem_path, subsubitem)
                                    if (os.path.isdir(subsubitem_path) and 
                                        subsubitem != "requirements" and 
                                        not subsubitem.startswith('.') and
                                        level5_count < 10):  # Limit to prevent excessive depth
                                        level5_req = os.path.join(subsubitem_path, "requirements")
                                        os.makedirs(level5_req, exist_ok=True)
                                        level5_count += 1
                            except (PermissionError, OSError):
                                pass
                                
                            if level5_count > 0:
                                print(f"         ✅ Level 5: Created {level5_count} requirements folders under {item}/{subitem}/")
                                
                except (PermissionError, OSError):
                    pass
                    
                if level4_count > 0:
                    print(f"      ✅ Level 4: Created {level4_count} requirements folders under {item}/")
        
        print(f"      📊 Created requirements at {level3_count} Level 3 locations")
        return True
        
    except Exception as e:
        print(f"      ❌ Error creating requirements structure: {e}")
        return False

def verify_requirements_structure(base_path, projects_to_fix):
    """Verify that requirements folders were created correctly"""
    print("Verifying requirements structure...")
    
    for repo_name, project_name in projects_to_fix:
        project_path = os.path.join(base_path, repo_name, project_name)
        
        if not os.path.exists(project_path):
            continue
            
        # Count requirements folders at each level
        level2_req = os.path.join(project_path, "requirements")
        has_level2 = os.path.exists(level2_req)
        
        level3_count = 0
        level4_count = 0
        
        try:
            for item in os.listdir(project_path):
                item_path = os.path.join(project_path, item)
                if os.path.isdir(item_path) and item != "requirements":
                    level3_req = os.path.join(item_path, "requirements")
                    if os.path.exists(level3_req):
                        level3_count += 1
                    
                    try:
                        for subitem in os.listdir(item_path):
                            subitem_path = os.path.join(item_path, subitem)
                            if os.path.isdir(subitem_path) and subitem != "requirements":
                                level4_req = os.path.join(subitem_path, "requirements")
                                if os.path.exists(level4_req):
                                    level4_count += 1
                    except (PermissionError, OSError):
                        pass
        except (PermissionError, OSError):
            pass
        
        print(f"   📊 {repo_name}/{project_name}:")
        print(f"      Level 2: {'✅' if has_level2 else '❌'}")
        print(f"      Level 3: {level3_count} requirements folders")
        print(f"      Level 4: {level4_count} requirements folders")

if __name__ == "__main__":
    success = create_requirements_for_remaining_projects()
    
    if success:
        print(f"\n🚀 READY FOR NEXT STEP:")
        print("   All projects now have requirements folder structure")
        print("   Can proceed to populate with time-based requirement templates")
    else:
        print(f"\n🔧 MANUAL REVIEW NEEDED:")
        print("   Some issues occurred - check the output above")