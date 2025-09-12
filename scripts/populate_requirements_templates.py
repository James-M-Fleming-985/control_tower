#!/usr/bin/env python3
"""
Populate all requirements/ folders across all repositories with the appropriate
time-based requirement templates based on hierarchy level and project type.
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

def populate_requirements_templates():
    """Populate all requirements folders with appropriate templates"""
    print("📝 POPULATING REQUIREMENTS FOLDERS WITH TEMPLATES")
    print("=" * 60)
    
    base_path = Path("/workspaces/control_tower/cloned_repos")
    templates_path = Path("/workspaces/control_tower/requirements_templates")
    
    # Template mapping based on level and project type
    template_mapping = {
        "north_star": "north_star_template.md",
        "project_application": "project_application_template.md", 
        "project_delivery": "project_delivery_template.md",
        "system": "system_application_template.md",
        "workpackage": "workpackage_delivery_template.md",
        "feature": "feature_application_template.md",
        "milestone": "milestone_delivery_template.md",
        "layer": "layer_application_template.md",
        "task": "task_delivery_template.md"
    }
    
    # Verify templates exist
    missing_templates = []
    for template_file in template_mapping.values():
        template_path = templates_path / template_file
        if not template_path.exists():
            missing_templates.append(template_file)
    
    if missing_templates:
        print(f"❌ Missing templates: {missing_templates}")
        return False
    
    print("✅ All required templates found")
    
    repositories = [
        "business_ventures",
        "financial_security", 
        "investment_strategy",
        "life_quality",
        "online_presence", 
        "professional_excellence"
    ]
    
    actual_projects = {
        "business_ventures": ["Causal_affect", "financial_optimizer", "opti_royale"],
        "life_quality": ["home_improvements"],
        "professional_excellence": ["Safran SF Optimization"]
    }
    
    populated_count = 0
    
    # Process each repository
    for repo in repositories:
        repo_path = base_path / repo
        if not repo_path.exists():
            continue
            
        print(f"\n📂 PROCESSING: {repo}")
        print("-" * 40)
        
        # Level 1: North Star requirements
        if populate_level1_requirements(repo_path, templates_path, template_mapping):
            populated_count += 1
        
        # Process actual projects in this repository
        projects = actual_projects.get(repo, [])
        for project in projects:
            project_path = repo_path / project
            if project_path.exists():
                print(f"  🎯 Processing project: {project}")
                project_type = determine_project_type(project_path)
                print(f"     Type: {project_type}")
                
                if populate_project_requirements(project_path, templates_path, template_mapping, project_type):
                    populated_count += 1
    
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    print(f"✅ Successfully populated: {populated_count} requirement areas")
    
    # Create a verification report
    create_population_report(base_path, actual_projects)
    
    return populated_count > 0

def populate_level1_requirements(repo_path, templates_path, template_mapping):
    """Populate Level 1 (North Star) requirements"""
    req_folder = repo_path / "requirements"
    if not req_folder.exists():
        return False
    
    # Check if already populated
    req_file = req_folder / "north_star_requirements.md"
    if req_file.exists():
        print(f"  ℹ️  Level 1 requirements already exist")
        return True
    
    # Copy and customize north star template
    template_path = templates_path / template_mapping["north_star"]
    if template_path.exists():
        shutil.copy2(template_path, req_file)
        
        # Customize template with repository name
        customize_template(req_file, {
            "REPOSITORY_NAME": repo_path.name.title().replace("_", " "),
            "DATE": datetime.now().strftime("%Y-%m-%d"),
            "LEVEL": "1 (North Star)"
        })
        
        print(f"  ✅ Level 1: Created north_star_requirements.md")
        return True
    
    return False

def populate_project_requirements(project_path, templates_path, template_mapping, project_type):
    """Populate requirements for a specific project based on its type"""
    success_count = 0
    
    # Level 2: Project requirements
    req_folder = project_path / "requirements"
    if req_folder.exists():
        template_key = f"project_{project_type.lower()}"
        template_file = template_mapping.get(template_key)
        
        if template_file:
            req_file = req_folder / f"project_requirements.md"
            if not req_file.exists():
                template_path = templates_path / template_file
                if template_path.exists():
                    shutil.copy2(template_path, req_file)
                    customize_template(req_file, {
                        "PROJECT_NAME": project_path.name.title().replace("_", " "),
                        "DATE": datetime.now().strftime("%Y-%m-%d"),
                        "LEVEL": "2 (Project)"
                    })
                    print(f"     ✅ Level 2: Created project_requirements.md")
                    success_count += 1
    
    # Level 3 and beyond based on project type
    if project_type == "Application":
        success_count += populate_application_requirements(project_path, templates_path, template_mapping)
    elif project_type == "Delivery":
        success_count += populate_delivery_requirements(project_path, templates_path, template_mapping)
    
    return success_count > 0

def populate_application_requirements(project_path, templates_path, template_mapping):
    """Populate requirements for Application projects (Systems → Features → Layers)"""
    success_count = 0
    
    # Level 3: Systems
    for system_dir in project_path.iterdir():
        if system_dir.is_dir() and system_dir.name != "requirements":
            req_folder = system_dir / "requirements"
            if req_folder.exists():
                req_file = req_folder / "system_requirements.md"
                if not req_file.exists():
                    template_path = templates_path / template_mapping["system"]
                    if template_path.exists():
                        shutil.copy2(template_path, req_file)
                        customize_template(req_file, {
                            "SYSTEM_NAME": system_dir.name.title().replace("_", " "),
                            "DATE": datetime.now().strftime("%Y-%m-%d"),
                            "LEVEL": "3 (System)"
                        })
                        success_count += 1
                
                # Level 4: Features
                for feature_dir in system_dir.iterdir():
                    if feature_dir.is_dir() and feature_dir.name != "requirements":
                        feature_req_folder = feature_dir / "requirements"
                        if feature_req_folder.exists():
                            req_file = feature_req_folder / "feature_requirements.md"
                            if not req_file.exists():
                                template_path = templates_path / template_mapping["feature"]
                                if template_path.exists():
                                    shutil.copy2(template_path, req_file)
                                    customize_template(req_file, {
                                        "FEATURE_NAME": feature_dir.name.title().replace("_", " "),
                                        "DATE": datetime.now().strftime("%Y-%m-%d"),
                                        "LEVEL": "4 (Feature)"
                                    })
                                    success_count += 1
                            
                            # Level 5: Layers
                            for layer_dir in feature_dir.iterdir():
                                if layer_dir.is_dir() and layer_dir.name != "requirements":
                                    layer_req_folder = layer_dir / "requirements"
                                    if layer_req_folder.exists():
                                        req_file = layer_req_folder / "layer_requirements.md"
                                        if not req_file.exists():
                                            template_path = templates_path / template_mapping["layer"]
                                            if template_path.exists():
                                                shutil.copy2(template_path, req_file)
                                                customize_template(req_file, {
                                                    "LAYER_NAME": layer_dir.name.title().replace("_", " "),
                                                    "DATE": datetime.now().strftime("%Y-%m-%d"),
                                                    "LEVEL": "5 (Layer)"
                                                })
                                                success_count += 1
    
    return success_count

def populate_delivery_requirements(project_path, templates_path, template_mapping):
    """Populate requirements for Delivery projects (Workpackages → Milestones → Tasks)"""
    success_count = 0
    
    # Level 3: Workpackages  
    for wp_dir in project_path.iterdir():
        if wp_dir.is_dir() and wp_dir.name != "requirements":
            req_folder = wp_dir / "requirements"
            if req_folder.exists():
                req_file = req_folder / "workpackage_requirements.md"
                if not req_file.exists():
                    template_path = templates_path / template_mapping["workpackage"]
                    if template_path.exists():
                        shutil.copy2(template_path, req_file)
                        customize_template(req_file, {
                            "WORKPACKAGE_NAME": wp_dir.name.title().replace("_", " "),
                            "DATE": datetime.now().strftime("%Y-%m-%d"),
                            "LEVEL": "3 (Workpackage)"
                        })
                        success_count += 1
                
                # Level 4: Milestones
                for milestone_dir in wp_dir.iterdir():
                    if milestone_dir.is_dir() and milestone_dir.name != "requirements":
                        milestone_req_folder = milestone_dir / "requirements"
                        if milestone_req_folder.exists():
                            req_file = milestone_req_folder / "milestone_requirements.md"
                            if not req_file.exists():
                                template_path = templates_path / template_mapping["milestone"]
                                if template_path.exists():
                                    shutil.copy2(template_path, req_file)
                                    customize_template(req_file, {
                                        "MILESTONE_NAME": milestone_dir.name.title().replace("_", " "),
                                        "DATE": datetime.now().strftime("%Y-%m-%d"),
                                        "LEVEL": "4 (Milestone)"
                                    })
                                    success_count += 1
                                
                                # Level 5: Tasks (if they exist)
                                for task_dir in milestone_dir.iterdir():
                                    if task_dir.is_dir() and task_dir.name != "requirements":
                                        task_req_folder = task_dir / "requirements"
                                        if task_req_folder.exists():
                                            req_file = task_req_folder / "task_requirements.md"
                                            if not req_file.exists():
                                                template_path = templates_path / template_mapping["task"]
                                                if template_path.exists():
                                                    shutil.copy2(template_path, req_file)
                                                    customize_template(req_file, {
                                                        "TASK_NAME": task_dir.name.title().replace("_", " "),
                                                        "DATE": datetime.now().strftime("%Y-%m-%d"),
                                                        "LEVEL": "5 (Task)"
                                                    })
                                                    success_count += 1
    
    return success_count

def determine_project_type(project_path):
    """Determine if project is Application or Delivery type"""
    try:
        items = [item.name for item in project_path.iterdir() if item.is_dir() and item.name != 'requirements']
        
        # Application indicators
        app_indicators = ['systems', 'features', 'layers', 'modules', 'services', 'components']
        # Delivery indicators  
        delivery_indicators = ['workpackages', 'milestones', 'tasks', 'phases']
        
        app_score = sum(1 for item in items if any(indicator in item.lower() for indicator in app_indicators))
        delivery_score = sum(1 for item in items if any(indicator in item.lower() for indicator in delivery_indicators))
        
        # Check for numbered phases (delivery pattern)
        numbered_phases = sum(1 for item in items if item.startswith(('1_', '2_', '3_', '4_', '5_')))
        
        if numbered_phases > 0:
            return "Delivery"
        elif app_score > delivery_score:
            return "Application"
        elif delivery_score > app_score:
            return "Delivery"
        else:
            # Default based on known patterns
            known_delivery = ["home_improvements", "Safran SF Optimization"]
            known_application = ["financial_optimizer", "opti_royale"]
            
            if project_path.name in known_delivery:
                return "Delivery"
            elif project_path.name in known_application:
                return "Application"
            else:
                return "Application"  # Default
                
    except Exception:
        return "Application"  # Default fallback

def customize_template(req_file, replacements):
    """Customize template with specific values"""
    try:
        content = req_file.read_text()
        
        for placeholder, value in replacements.items():
            content = content.replace(f"{{{placeholder}}}", value)
        
        req_file.write_text(content)
        
    except Exception as e:
        print(f"  ⚠️  Error customizing template {req_file}: {e}")

def create_population_report(base_path, actual_projects):
    """Create a report of populated requirements"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(f"/workspaces/control_tower/reports/requirements_population_{timestamp}.md")
    
    report_content = f"""# Requirements Population Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
All requirements folders have been populated with appropriate templates based on:
- **Hierarchy Level**: Level 1 (North Star) → Level 2 (Project) → Level 3+ (Systems/Workpackages)
- **Project Type**: Application (Systems→Features→Layers) vs Delivery (Workpackages→Milestones→Tasks)

## Populated Repositories
"""
    
    for repo in ["business_ventures", "financial_security", "investment_strategy", "life_quality", "online_presence", "professional_excellence"]:
        repo_path = base_path / repo
        if repo_path.exists():
            report_content += f"\n### {repo}\n"
            
            # Level 1
            level1_req = repo_path / "requirements" / "north_star_requirements.md"
            if level1_req.exists():
                report_content += f"- ✅ Level 1: north_star_requirements.md\\n"
            
            # Projects
            projects = actual_projects.get(repo, [])
            for project in projects:
                project_path = repo_path / project
                if project_path.exists():
                    report_content += f"- 🎯 Project: {project}\\n"
                    
                    # Count requirements files
                    req_count = count_requirements_files(project_path)
                    report_content += f"  - Requirements files: {req_count}\\n"
    
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report_content)
    print(f"\n📄 Population report saved: {report_path}")

def count_requirements_files(project_path):
    """Count total requirements files in a project"""
    count = 0
    for req_folder in project_path.rglob("requirements"):
        if req_folder.is_dir():
            count += len([f for f in req_folder.iterdir() if f.is_file() and f.name.endswith('.md')])
    return count

if __name__ == "__main__":
    success = populate_requirements_templates()
    
    if success:
        print(f"\n🎉 REQUIREMENTS POPULATION COMPLETE!")
        print("   All requirements folders now contain appropriate templates")
        print("   Templates are customized with project-specific information")
        print("   Ready for Control Tower requirements management testing")
    else:
        print(f"\n❌ REQUIREMENTS POPULATION FAILED")
        print("   Check the errors above and resolve before proceeding")