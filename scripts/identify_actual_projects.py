#!/usr/bin/env python3
"""
Focused analysis to identify the ACTUAL PROJECTS within each repository
that need requirements management, excluding supporting infrastructure.
"""
import os

def identify_actual_projects():
    """Identify the real projects that need requirements management"""
    print("🎯 IDENTIFYING ACTUAL PROJECTS FOR REQUIREMENTS MANAGEMENT")
    print("=" * 70)
    
    base_path = "/workspaces/control_tower/cloned_repos"
    
    # Define what we know are the actual projects vs infrastructure
    known_projects = {
        "business_ventures": ["financial_optimizer", "opti_royale", "Causal_affect"],
        "financial_security": [],  # Need to identify
        "investment_strategy": [],  # Need to identify  
        "life_quality": ["home_improvements"],
        "online_presence": [],  # Need to identify
        "professional_excellence": ["Safran SF Optimization"]
    }
    
    infrastructure_folders = ["docs", "workflows", "templates", "metrics", "tests"]
    
    actual_projects = {}
    
    for repo in known_projects.keys():
        repo_path = os.path.join(base_path, repo)
        if not os.path.exists(repo_path):
            continue
            
        print(f"\n📂 {repo.upper()}")
        print("-" * 40)
        
        all_items = [item for item in os.listdir(repo_path) 
                    if os.path.isdir(os.path.join(repo_path, item)) and not item.startswith('.')]
        
        projects = [item for item in all_items if item not in infrastructure_folders]
        infrastructure = [item for item in all_items if item in infrastructure_folders]
        
        print(f"🏗️  Infrastructure folders: {infrastructure}")
        print(f"🎯 Actual projects: {projects}")
        
        actual_projects[repo] = projects
        
        # Analyze each actual project
        for project in projects:
            analyze_actual_project(repo_path, project)
    
    print(f"\n📊 SUMMARY - ACTUAL PROJECTS NEEDING REQUIREMENTS MANAGEMENT")
    print("=" * 70)
    
    total_projects = 0
    for repo, projects in actual_projects.items():
        total_projects += len(projects)
        if projects:
            print(f"✅ {repo}: {len(projects)} projects")
            for project in projects:
                print(f"   - {project}")
        else:
            print(f"⚠️  {repo}: No actual projects found")
    
    print(f"\n🎯 TOTAL ACTUAL PROJECTS: {total_projects}")
    
    return actual_projects

def analyze_actual_project(repo_path, project_name):
    """Analyze an actual project's current state"""
    project_path = os.path.join(repo_path, project_name)
    
    # Check if it has requirements folder
    has_requirements = os.path.exists(os.path.join(project_path, "requirements"))
    
    # Count levels
    max_depth = get_max_depth(project_path)
    
    # Determine project type
    project_type = determine_project_type(project_path)
    
    print(f"   📁 {project_name}:")
    print(f"      Requirements: {'✅' if has_requirements else '❌'}")
    print(f"      Max Depth: Level {max_depth}")
    print(f"      Type: {project_type}")

def get_max_depth(project_path, current_depth=2):
    """Recursively determine maximum hierarchy depth"""
    max_found = current_depth
    
    try:
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path) and item != "requirements" and not item.startswith('.'):
                depth_here = get_max_depth(item_path, current_depth + 1)
                max_found = max(max_found, depth_here)
    except (PermissionError, OSError):
        pass
    
    return max_found

def determine_project_type(project_path):
    """Determine if project is Application or Delivery type"""
    try:
        items = os.listdir(project_path)
        items = [item for item in items if not item.startswith('.') and item != 'requirements']
        
        # Application indicators
        app_indicators = ['systems', 'features', 'layers', 'modules', 'services', 'components']
        # Delivery indicators  
        delivery_indicators = ['workpackages', 'milestones', 'tasks', 'phases']
        
        app_score = sum(1 for item in items if any(indicator in item.lower() for indicator in app_indicators))
        delivery_score = sum(1 for item in items if any(indicator in item.lower() for indicator in delivery_indicators))
        
        # Check for numbered phases (delivery pattern)
        numbered_phases = sum(1 for item in items if item.startswith(('1_', '2_', '3_', '4_', '5_')))
        
        if numbered_phases > 0:
            return "Delivery (numbered phases)"
        elif app_score > delivery_score:
            return "Application"
        elif delivery_score > app_score:
            return "Delivery"
        else:
            return "Unknown"
            
    except (PermissionError, OSError):
        return "Error reading"

if __name__ == "__main__":
    actual_projects = identify_actual_projects()
    
    print(f"\n🚀 NEXT STEP: Create requirements structure for these {sum(len(projects) for projects in actual_projects.values())} actual projects")