#!/usr/bin/env python3
"""
Comprehensive audit of all 6 repositories in cloned_repos/ to check:
1. Hierarchy structure consistency
2. Requirements folder presence at each level
3. Project type detection (Application vs Delivery)
4. Structural issues that would confuse Control Tower
"""
import os
import json
from datetime import datetime

def audit_all_repositories():
    """Audit all 6 repositories for hierarchy compliance"""
    print("🔍 COMPREHENSIVE REPOSITORY AUDIT")
    print("=" * 60)
    
    base_path = "/workspaces/control_tower/cloned_repos"
    repositories = [
        "business_ventures",
        "financial_security", 
        "investment_strategy",
        "life_quality",
        "online_presence",
        "professional_excellence"
    ]
    
    audit_results = {}
    
    for repo in repositories:
        repo_path = os.path.join(base_path, repo)
        if os.path.exists(repo_path):
            print(f"\n📂 AUDITING: {repo}")
            print("-" * 40)
            audit_results[repo] = audit_repository_structure(repo_path, repo)
        else:
            print(f"❌ {repo} not found")
            audit_results[repo] = {"status": "missing", "issues": ["Repository not found"]}
    
    # Generate summary report
    generate_audit_summary(audit_results)
    
    return audit_results

def audit_repository_structure(repo_path, repo_name):
    """Audit a single repository's structure"""
    result = {
        "status": "analyzed",
        "hierarchy_levels": {},
        "requirements_folders": [],
        "missing_requirements": [],
        "project_type": "unknown",
        "projects": [],
        "issues": [],
        "recommendations": []
    }
    
    # Level 1: Repository root
    level1_req = os.path.join(repo_path, 'requirements')
    if os.path.exists(level1_req):
        result["requirements_folders"].append("Level 1: requirements/")
    else:
        result["missing_requirements"].append("Level 1: Missing requirements/")
        result["issues"].append("Missing Level 1 requirements folder")
    
    # Check for projects at Level 2
    projects = []
    for item in os.listdir(repo_path):
        item_path = os.path.join(repo_path, item)
        if os.path.isdir(item_path) and not item.startswith('.') and item != 'requirements':
            projects.append(item)
    
    result["projects"] = projects
    print(f"Found {len(projects)} projects: {projects}")
    
    # Analyze each project
    for project in projects:
        project_path = os.path.join(repo_path, project)
        project_analysis = analyze_project_structure(project_path, project)
        result["hierarchy_levels"][project] = project_analysis
        
        # Check project-level requirements
        project_req = os.path.join(project_path, 'requirements')
        if os.path.exists(project_req):
            result["requirements_folders"].append(f"Level 2 ({project}): requirements/")
        else:
            result["missing_requirements"].append(f"Level 2 ({project}): Missing requirements/")
            result["issues"].append(f"Project {project} missing requirements folder")
    
    # Determine overall repository health
    if len(result["issues"]) == 0:
        result["status"] = "compliant"
    elif len(result["issues"]) <= 2:
        result["status"] = "minor_issues"
    else:
        result["status"] = "needs_restructuring"
    
    return result

def analyze_project_structure(project_path, project_name):
    """Analyze the internal structure of a project"""
    analysis = {
        "project_type": "unknown",
        "level3_items": [],
        "level4_items": [],
        "max_depth": 2,
        "structure_issues": [],
        "requirements_at_levels": []
    }
    
    # Check Level 3 items
    level3_items = []
    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        if os.path.isdir(item_path) and item != 'requirements':
            level3_items.append(item)
    
    analysis["level3_items"] = level3_items
    analysis["max_depth"] = 3 if level3_items else 2
    
    # Determine project type based on naming patterns
    if any(item.lower() in ['systems', 'features', 'layers', 'modules', 'services'] for item in level3_items):
        analysis["project_type"] = "Application"
    elif any(item.lower() in ['workpackages', 'milestones', 'tasks'] for item in level3_items):
        analysis["project_type"] = "Delivery"
    elif any(item.startswith(('1_', '2_', '3_')) for item in level3_items):
        analysis["project_type"] = "Delivery (numbered phases)"
    else:
        analysis["project_type"] = "Unknown - needs classification"
    
    # Check for Level 4 items and requirements
    for level3_item in level3_items:
        level3_path = os.path.join(project_path, level3_item)
        
        # Check for requirements at Level 3
        level3_req = os.path.join(level3_path, 'requirements')
        if os.path.exists(level3_req):
            analysis["requirements_at_levels"].append(f"Level 3 ({level3_item}): ✅")
        else:
            analysis["requirements_at_levels"].append(f"Level 3 ({level3_item}): ❌")
        
        # Check Level 4 items
        if os.path.exists(level3_path):
            level4_items = [item for item in os.listdir(level3_path) 
                           if os.path.isdir(os.path.join(level3_path, item)) and item != 'requirements']
            
            if level4_items:
                analysis["level4_items"].extend([f"{level3_item}/{item}" for item in level4_items])
                analysis["max_depth"] = 4
                
                # Check Level 4 requirements
                for level4_item in level4_items:
                    level4_path = os.path.join(level3_path, level4_item)
                    level4_req = os.path.join(level4_path, 'requirements')
                    if os.path.exists(level4_req):
                        analysis["requirements_at_levels"].append(f"Level 4 ({level3_item}/{level4_item}): ✅")
                    else:
                        analysis["requirements_at_levels"].append(f"Level 4 ({level3_item}/{level4_item}): ❌")
    
    print(f"  Project: {project_name}")
    print(f"    Type: {analysis['project_type']}")
    print(f"    Max Depth: Level {analysis['max_depth']}")
    print(f"    Level 3 Items: {len(analysis['level3_items'])}")
    print(f"    Level 4 Items: {len(analysis['level4_items'])}")
    
    return analysis

def generate_audit_summary(audit_results):
    """Generate a comprehensive summary of the audit"""
    print(f"\n📊 AUDIT SUMMARY")
    print("=" * 60)
    
    compliant_repos = []
    minor_issues_repos = []
    needs_restructuring_repos = []
    
    for repo, result in audit_results.items():
        status = result.get("status", "unknown")
        if status == "compliant":
            compliant_repos.append(repo)
        elif status == "minor_issues":
            minor_issues_repos.append(repo)
        else:
            needs_restructuring_repos.append(repo)
    
    print(f"✅ COMPLIANT REPOSITORIES ({len(compliant_repos)}):")
    for repo in compliant_repos:
        print(f"   - {repo}")
    
    print(f"\n⚠️  MINOR ISSUES ({len(minor_issues_repos)}):")
    for repo in minor_issues_repos:
        issues = audit_results[repo].get("issues", [])
        print(f"   - {repo}: {len(issues)} issues")
        for issue in issues[:2]:  # Show first 2 issues
            print(f"     • {issue}")
    
    print(f"\n🔧 NEEDS RESTRUCTURING ({len(needs_restructuring_repos)}):")
    for repo in needs_restructuring_repos:
        issues = audit_results[repo].get("issues", [])
        print(f"   - {repo}: {len(issues)} issues")
        for issue in issues[:3]:  # Show first 3 issues
            print(f"     • {issue}")
    
    # Requirements folder summary
    print(f"\n📁 REQUIREMENTS FOLDER STATUS")
    print("=" * 40)
    
    total_missing = 0
    for repo, result in audit_results.items():
        missing = result.get("missing_requirements", [])
        total_missing += len(missing)
        if missing:
            print(f"❌ {repo}: {len(missing)} missing requirements folders")
        else:
            print(f"✅ {repo}: All requirements folders present")
    
    print(f"\n🎯 NEXT ACTIONS REQUIRED:")
    print("=" * 40)
    
    if needs_restructuring_repos:
        print(f"1. RESTRUCTURE: {', '.join(needs_restructuring_repos)}")
    
    if total_missing > 0:
        print(f"2. ADD REQUIREMENTS FOLDERS: {total_missing} missing across all repos")
    
    if compliant_repos:
        print(f"3. POPULATE TEMPLATES: Ready to populate {', '.join(compliant_repos)}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"/workspaces/control_tower/reports/repository_audit_{timestamp}.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"\n📄 Detailed report saved: {report_file}")

if __name__ == "__main__":
    audit_results = audit_all_repositories()