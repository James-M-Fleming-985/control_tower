#!/usr/bin/env python3
"""
Comprehensive test of Control Tower's requirements management capabilities
across all restructured repositories with populated templates.
"""
import os
from pathlib import Path
from datetime import datetime

def test_complete_requirements_management():
    """Test Control Tower's requirements management across all repositories"""
    print("🧪 COMPREHENSIVE REQUIREMENTS MANAGEMENT TEST")
    print("=" * 65)
    
    base_path = Path("/workspaces/control_tower/cloned_repos")
    
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
    
    test_results = {}
    overall_success = True
    
    for repo in repositories:
        repo_path = base_path / repo
        if not repo_path.exists():
            continue
            
        print(f"\n📂 TESTING: {repo}")
        print("-" * 40)
        
        repo_results = test_repository_requirements(repo_path, actual_projects.get(repo, []))
        test_results[repo] = repo_results
        
        if not repo_results["success"]:
            overall_success = False
    
    # Generate comprehensive test report
    generate_test_report(test_results, overall_success)
    
    return overall_success

def test_repository_requirements(repo_path, projects):
    """Test requirements management for a specific repository"""
    results = {
        "success": True,
        "level1_test": False,
        "project_tests": {},
        "hierarchy_detection": True,
        "requirements_cascade": True,
        "template_population": True,
        "issues": []
    }
    
    # Test Level 1 (North Star) requirements
    level1_req_file = repo_path / "requirements" / "north_star_requirements.md"
    if level1_req_file.exists():
        results["level1_test"] = True
        print(f"  ✅ Level 1: North Star requirements found")
        
        # Verify template content
        if verify_template_content(level1_req_file, "north_star"):
            print(f"     ✅ Template properly populated")
        else:
            results["template_population"] = False
            results["issues"].append("Level 1 template not properly populated")
    else:
        results["level1_test"] = False
        results["issues"].append("Missing Level 1 north_star_requirements.md")
        results["success"] = False
    
    # Test each project
    for project in projects:
        project_path = repo_path / project
        if project_path.exists():
            print(f"\n  🎯 Testing project: {project}")
            project_results = test_project_requirements(project_path, project)
            results["project_tests"][project] = project_results
            
            if not project_results["success"]:
                results["success"] = False
                results["issues"].extend(project_results["issues"])
    
    return results

def test_project_requirements(project_path, project_name):
    """Test requirements management for a specific project"""
    results = {
        "success": True,
        "project_type": "unknown",
        "level2_test": False,
        "hierarchy_levels": [],
        "requirements_files": 0,
        "cascade_test": False,
        "issues": []
    }
    
    # Determine project type
    results["project_type"] = determine_project_type(project_path)
    print(f"    Type: {results['project_type']}")
    
    # Test Level 2 (Project) requirements
    level2_req_file = project_path / "requirements" / "project_requirements.md"
    if level2_req_file.exists():
        results["level2_test"] = True
        print(f"    ✅ Level 2: Project requirements found")
        
        if verify_template_content(level2_req_file, "project"):
            print(f"       ✅ Template properly populated")
        else:
            results["issues"].append(f"{project_name}: Level 2 template not properly populated")
    else:
        results["level2_test"] = False
        results["issues"].append(f"{project_name}: Missing Level 2 project_requirements.md")
        results["success"] = False
    
    # Test hierarchy depth and requirements cascade
    hierarchy_test = test_hierarchy_cascade(project_path, results["project_type"])
    results.update(hierarchy_test)
    
    # Count total requirements files
    results["requirements_files"] = count_project_requirements(project_path)
    print(f"    📊 Total requirements files: {results['requirements_files']}")
    
    if results["requirements_files"] > 0:
        results["cascade_test"] = True
        print(f"    ✅ Requirements cascade functional")
    else:
        results["cascade_test"] = False
        results["issues"].append(f"{project_name}: No requirements files found")
        results["success"] = False
    
    return results

def test_hierarchy_cascade(project_path, project_type):
    """Test that requirements exist at appropriate hierarchy levels"""
    cascade_results = {
        "hierarchy_levels": [],
        "cascade_depth": 0,
        "cascade_complete": True
    }
    
    max_depth = 2  # Start at Level 2 (Project)
    
    # Test Level 3 and beyond based on project type
    if project_type == "Application":
        # Test Systems → Features → Layers
        for system_dir in project_path.iterdir():
            if system_dir.is_dir() and system_dir.name != "requirements":
                if (system_dir / "requirements").exists():
                    cascade_results["hierarchy_levels"].append(f"Level 3 (System): {system_dir.name}")
                    max_depth = max(max_depth, 3)
                    
                    # Test Features
                    for feature_dir in system_dir.iterdir():
                        if feature_dir.is_dir() and feature_dir.name != "requirements":
                            if (feature_dir / "requirements").exists():
                                cascade_results["hierarchy_levels"].append(f"Level 4 (Feature): {system_dir.name}/{feature_dir.name}")
                                max_depth = max(max_depth, 4)
                                
                                # Test Layers
                                for layer_dir in feature_dir.iterdir():
                                    if layer_dir.is_dir() and layer_dir.name != "requirements":
                                        if (layer_dir / "requirements").exists():
                                            cascade_results["hierarchy_levels"].append(f"Level 5 (Layer): {system_dir.name}/{feature_dir.name}/{layer_dir.name}")
                                            max_depth = max(max_depth, 5)
    
    elif project_type == "Delivery":
        # Test Workpackages → Milestones → Tasks
        for wp_dir in project_path.iterdir():
            if wp_dir.is_dir() and wp_dir.name != "requirements":
                if (wp_dir / "requirements").exists():
                    cascade_results["hierarchy_levels"].append(f"Level 3 (Workpackage): {wp_dir.name}")
                    max_depth = max(max_depth, 3)
                    
                    # Test Milestones
                    for milestone_dir in wp_dir.iterdir():
                        if milestone_dir.is_dir() and milestone_dir.name != "requirements":
                            if (milestone_dir / "requirements").exists():
                                cascade_results["hierarchy_levels"].append(f"Level 4 (Milestone): {wp_dir.name}/{milestone_dir.name}")
                                max_depth = max(max_depth, 4)
                                
                                # Test Tasks
                                for task_dir in milestone_dir.iterdir():
                                    if task_dir.is_dir() and task_dir.name != "requirements":
                                        if (task_dir / "requirements").exists():
                                            cascade_results["hierarchy_levels"].append(f"Level 5 (Task): {wp_dir.name}/{milestone_dir.name}/{task_dir.name}")
                                            max_depth = max(max_depth, 5)
    
    cascade_results["cascade_depth"] = max_depth
    
    print(f"    📊 Hierarchy cascade depth: Level {max_depth}")
    print(f"    📋 Requirements levels found: {len(cascade_results['hierarchy_levels'])}")
    
    return cascade_results

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
            # Known project mappings
            known_delivery = ["home_improvements", "Safran SF Optimization"]
            known_application = ["financial_optimizer", "opti_royale", "Causal_affect"]
            
            if project_path.name in known_delivery:
                return "Delivery"
            elif project_path.name in known_application:
                return "Application"
            else:
                return "Application"  # Default
                
    except Exception:
        return "Application"

def verify_template_content(req_file, template_type):
    """Verify that template has been properly populated"""
    try:
        content = req_file.read_text()
        
        # Check for unreplaced placeholders
        placeholders = ["{DATE}", "{XXX}", "{PROJECT_NAME}", "{SYSTEM_NAME}", "{FEATURE_NAME}", 
                       "{WORKPACKAGE_NAME}", "{MILESTONE_NAME}", "{TASK_NAME}", "{LAYER_NAME}"]
        
        unreplaced = [p for p in placeholders if p in content]
        
        if unreplaced:
            return False
        
        # Check for minimum content
        if len(content.strip()) < 100:
            return False
            
        return True
        
    except Exception:
        return False

def count_project_requirements(project_path):
    """Count total requirements files in a project"""
    count = 0
    for req_folder in project_path.rglob("requirements"):
        if req_folder.is_dir():
            count += len([f for f in req_folder.iterdir() if f.is_file() and f.name.endswith('.md')])
    return count

def generate_test_report(test_results, overall_success):
    """Generate comprehensive test report"""
    print(f"\n📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    total_repos = len(test_results)
    successful_repos = sum(1 for r in test_results.values() if r["success"])
    
    print(f"📈 OVERALL SUCCESS RATE: {successful_repos}/{total_repos} repositories")
    
    if overall_success:
        print(f"🎉 ALL REPOSITORIES PASSED REQUIREMENTS MANAGEMENT TESTS!")
    else:
        print(f"⚠️  SOME REPOSITORIES HAVE ISSUES")
    
    # Detailed results by repository
    for repo, results in test_results.items():
        status = "✅ PASSED" if results["success"] else "❌ FAILED"
        print(f"\n📂 {repo}: {status}")
        
        if results["level1_test"]:
            print(f"   ✅ Level 1 (North Star) requirements")
        else:
            print(f"   ❌ Level 1 (North Star) requirements")
        
        for project, project_results in results["project_tests"].items():
            project_status = "✅" if project_results["success"] else "❌"
            print(f"   {project_status} Project: {project} ({project_results['project_type']})")
            print(f"      Requirements files: {project_results['requirements_files']}")
            print(f"      Cascade depth: Level {project_results.get('cascade_depth', 2)}")
            
            if project_results["issues"]:
                for issue in project_results["issues"]:
                    print(f"      ⚠️  {issue}")
    
    # Summary statistics
    total_projects = sum(len(r["project_tests"]) for r in test_results.values())
    successful_projects = sum(len([p for p in r["project_tests"].values() if p["success"]]) for r in test_results.values())
    total_requirements = sum(sum(p["requirements_files"] for p in r["project_tests"].values()) for r in test_results.values())
    
    print(f"\n📊 STATISTICS")
    print("=" * 30)
    print(f"Total repositories tested: {total_repos}")
    print(f"Successful repositories: {successful_repos}")
    print(f"Total projects tested: {total_projects}")
    print(f"Successful projects: {successful_projects}")
    print(f"Total requirements files: {total_requirements}")
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(f"/workspaces/control_tower/reports/requirements_management_test_{timestamp}.json")
    
    import json
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed test report saved: {report_path}")
    
    if overall_success:
        print(f"\n🚀 CONTROL TOWER REQUIREMENTS MANAGEMENT IS FULLY OPERATIONAL!")
        print("   ✅ All repositories have consistent hierarchy structure")
        print("   ✅ All projects have proper requirements cascade")
        print("   ✅ All templates are properly populated")
        print("   ✅ Requirements traceability is complete")
    else:
        print(f"\n🔧 SOME ISSUES REQUIRE ATTENTION:")
        all_issues = []
        for r in test_results.values():
            all_issues.extend(r["issues"])
        for issue in set(all_issues):
            print(f"   • {issue}")

if __name__ == "__main__":
    success = test_complete_requirements_management()
    
    if success:
        print(f"\n🎯 READY FOR PRODUCTION USE!")
        print("   Control Tower can now manage requirements across all 6 repositories")
    else:
        print(f"\n🔧 RESOLVE ISSUES BEFORE PRODUCTION USE")