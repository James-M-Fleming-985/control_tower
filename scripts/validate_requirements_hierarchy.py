#!/usr/bin/env python3
"""
Requirements Hierarchy Structure Validator

This script validates that repositories follow the correct 6-level requirements management hierarchy:
Level 1: North Star Domain (business_ventures/, professional_excellence/, etc.)
Level 2: Projects (financial_optimizer/, contract_projects/, etc.)
Level 3: Systems/Workpackages (organized functional groups)
Level 4: Features/Milestones (specific capabilities or deliverables)
Level 5: Layers/Tasks (implementation details or work items)
Level 6: Components (atomic elements)

Focus: Checking structural organization for requirements cascade, NOT project types.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class HierarchyIssue:
    repo_name: str
    level: int
    path: str
    issue_type: str
    description: str
    recommendation: str

@dataclass
class RequirementsStructure:
    name: str
    path: str
    level: int
    has_requirements: bool
    children: List['RequirementsStructure']
    expected_child_count: int
    actual_child_count: int

class RequirementsHierarchyValidator:
    def __init__(self, base_path: str = "/workspaces/control_tower"):
        self.base_path = Path(base_path)
        self.cloned_repos_path = self.base_path / "cloned_repos"
        self.validation_results = {}
        
        # Expected structure patterns for requirements hierarchy
        self.level_names = {
            1: "North Star Domain",
            2: "Project", 
            3: "System/Workpackage",
            4: "Feature/Milestone",
            5: "Layer/Task",
            6: "Component"
        }
        
        # Minimum expected structure depth
        self.min_levels = 3  # At least down to Systems/Workpackages
        self.ideal_levels = 5  # Ideally down to Layers/Tasks

    def validate_requirements_hierarchy(self) -> Dict[str, List[HierarchyIssue]]:
        """Validate requirements hierarchy structure across all repositories"""
        print("🔍 Validating Requirements Management Hierarchy Structure...")
        print("=" * 70)
        print("📋 Checking for proper 6-level requirements cascade:")
        print("   Level 1: North Star Domain")
        print("   Level 2: Projects") 
        print("   Level 3: Systems/Workpackages")
        print("   Level 4: Features/Milestones")
        print("   Level 5: Layers/Tasks")
        print("   Level 6: Components")
        print("=" * 70)
        
        all_issues = {}
        
        if not self.cloned_repos_path.exists():
            print(f"❌ ERROR: cloned_repos directory not found at {self.cloned_repos_path}")
            return all_issues
            
        # Get all North Star repositories (Level 1)
        north_star_repos = [d for d in self.cloned_repos_path.iterdir() 
                           if d.is_dir() and not d.name.startswith('.')]
        
        print(f"📂 Found {len(north_star_repos)} North Star repositories:")
        for repo in north_star_repos:
            print(f"   • {repo.name}")
        print()
        
        # Validate each repository's requirements structure
        for repo_dir in north_star_repos:
            print(f"🔍 Validating requirements structure in {repo_dir.name}...")
            issues = self.validate_repository_requirements_structure(repo_dir)
            all_issues[repo_dir.name] = issues
            
            if issues:
                print(f"   ⚠️  Found {len(issues)} requirements structure issues")
            else:
                print(f"   ✅ Requirements hierarchy properly structured")
        
        return all_issues

    def validate_repository_requirements_structure(self, repo_path: Path) -> List[HierarchyIssue]:
        """Validate the requirements hierarchy structure for a single repository"""
        issues = []
        
        # Level 1: North Star Domain - Already correct (the repo itself)
        print(f"     📁 Level 1 (North Star): {repo_path.name}")
        
        # Level 2: Find Projects
        projects = self.find_projects_in_repo(repo_path)
        
        if not projects:
            issues.append(HierarchyIssue(
                repo_name=repo_path.name,
                level=2,
                path=str(repo_path),
                issue_type="no_projects",
                description="No projects found in North Star repository",
                recommendation="Create project folders to organize work at Level 2"
            ))
            return issues
        
        print(f"     📁 Level 2 (Projects): Found {len(projects)} projects")
        for project_path in projects:
            print(f"        • {project_path.name}")
            project_issues = self.validate_project_requirements_structure(repo_path.name, project_path)
            issues.extend(project_issues)
        
        return issues

    def find_projects_in_repo(self, repo_path: Path) -> List[Path]:
        """Find all project directories in the repository"""
        projects = []
        
        # Look for direct project folders (current structure)
        for item in repo_path.iterdir():
            if (item.is_dir() and 
                not item.name.startswith('.') and 
                item.name not in ["docs", "requirements", "templates", "tests", "workflows", "metrics"]):
                
                # If it has content that looks like a project, include it
                if self.looks_like_project(item):
                    projects.append(item)
        
        # Also look in projects/ subfolder if it exists
        projects_dir = repo_path / "projects"
        if projects_dir.exists():
            for item in projects_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    projects.append(item)
        
        return projects

    def looks_like_project(self, path: Path) -> bool:
        """Determine if a directory looks like a project (has substantial content)"""
        # Count files and subdirectories
        contents = list(path.iterdir())
        
        # Must have at least some content
        if len(contents) < 2:
            return False
            
        # Look for project indicators
        has_code_files = any(item.suffix in ['.py', '.js', '.ts', '.md', '.json', '.yml', '.yaml'] 
                           for item in contents if item.is_file())
        has_subdirs = any(item.is_dir() for item in contents)
        
        return has_code_files or has_subdirs

    def validate_project_requirements_structure(self, repo_name: str, project_path: Path) -> List[HierarchyIssue]:
        """Validate Level 3+ structure within a project for requirements management"""
        issues = []
        
        # Check for project-level requirements folder
        project_requirements = project_path / "requirements"
        if not project_requirements.exists():
            issues.append(HierarchyIssue(
                repo_name=repo_name,
                level=2,
                path=str(project_path),
                issue_type="missing_project_requirements",
                description=f"Project '{project_path.name}' missing requirements/ folder",
                recommendation="Create requirements/ folder to store project-level requirements files"
            ))
        
        # Level 3: Look for proper Systems/Workpackages structure
        level3_structure = self.analyze_proper_level3_structure(project_path)
        
        if not level3_structure:
            issues.append(HierarchyIssue(
                repo_name=repo_name,
                level=3,
                path=str(project_path),
                issue_type="missing_level3_structure",
                description=f"Project '{project_path.name}' missing Level 3 (Systems/Workpackages) organization",
                recommendation="Create systems/ or workpackages/ folders to organize Level 3 requirements structure"
            ))
            return issues
        
        print(f"        📁 Level 3 (Systems/Workpackages): Found {len(level3_structure)}")
        for system_name in level3_structure:
            print(f"           • {system_name}")
        
        # Check each Level 3 item for proper requirements structure
        for level3_item in level3_structure:
            level3_path = project_path / level3_item
            level3_issues = self.validate_requirements_cascade_structure(repo_name, level3_path, 3)
            issues.extend(level3_issues)
        
        return issues

    def analyze_proper_level3_structure(self, project_path: Path) -> List[str]:
        """Analyze what looks like proper Level 3 structure for requirements management"""
        level3_items = []
        
        # Look for explicit Level 3 folders
        expected_level3_names = ["systems", "workpackages", "modules", "services", "components"]
        
        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if this is a proper Level 3 folder
                if (item.name.lower() in expected_level3_names or
                    item.name.lower().endswith('_systems') or
                    item.name.lower().endswith('_workpackages') or
                    item.name.lower().endswith('_modules')):
                    level3_items.append(item.name)
        
        return level3_items

    def validate_requirements_cascade_structure(self, repo_name: str, parent_path: Path, parent_level: int) -> List[HierarchyIssue]:
        """Validate proper requirements cascade structure at each level"""
        issues = []
        current_level = parent_level + 1
        
        # Check for requirements folder at this level
        requirements_folder = parent_path / "requirements"
        if not requirements_folder.exists():
            level_name = self.level_names.get(parent_level, f"Level {parent_level}")
            issues.append(HierarchyIssue(
                repo_name=repo_name,
                level=parent_level,
                path=str(parent_path),
                issue_type="missing_requirements_folder",
                description=f"{level_name} '{parent_path.name}' missing requirements/ folder",
                recommendation=f"Create requirements/ folder to store {level_name.lower()} requirements files"
            ))
        
        # Check for proper next level structure
        if current_level <= 5:  # Don't go deeper than Layer/Task level
            next_level_structure = self.find_proper_next_level_structure(parent_path, current_level)
            
            if not next_level_structure:
                level_name = self.level_names.get(current_level, f"Level {current_level}")
                parent_level_name = self.level_names.get(parent_level, f"Level {parent_level}")
                issues.append(HierarchyIssue(
                    repo_name=repo_name,
                    level=current_level,
                    path=str(parent_path),
                    issue_type="missing_next_level_structure",
                    description=f"{parent_level_name} '{parent_path.name}' missing {level_name} organization",
                    recommendation=f"Create proper {level_name.lower()} folders to continue requirements hierarchy"
                ))
            else:
                level_name = self.level_names.get(current_level, f"Level {current_level}")
                print(f"           {'  ' * (current_level-3)}📁 {level_name}: Found {len(next_level_structure)}")
                for item_name in next_level_structure:
                    print(f"           {'  ' * (current_level-2)}• {item_name}")
                    
                    # Recursively check deeper levels
                    item_path = parent_path / item_name
                    deeper_issues = self.validate_requirements_cascade_structure(repo_name, item_path, current_level)
                    issues.extend(deeper_issues)
        
        return issues

    def find_proper_next_level_structure(self, parent_path: Path, level: int) -> List[str]:
        """Find proper structure for the next level in requirements hierarchy"""
        items = []
        
        # Expected folder patterns for each level
        if level == 4:  # Features/Milestones
            expected_patterns = ["features", "milestones", "capabilities", "deliverables"]
            subfolder_name = None
            for pattern in expected_patterns:
                potential_folder = parent_path / pattern
                if potential_folder.exists() and potential_folder.is_dir():
                    subfolder_name = pattern
                    break
            
            if subfolder_name:
                # Look inside the features/milestones folder
                subfolder_path = parent_path / subfolder_name
                items = [item.name for item in subfolder_path.iterdir() 
                        if item.is_dir() and not item.name.startswith('.')]
            
        elif level == 5:  # Layers/Tasks
            expected_patterns = ["layers", "tasks", "activities", "components"]
            subfolder_name = None
            for pattern in expected_patterns:
                potential_folder = parent_path / pattern
                if potential_folder.exists() and potential_folder.is_dir():
                    subfolder_name = pattern
                    break
            
            if subfolder_name:
                subfolder_path = parent_path / subfolder_name
                items = [item.name for item in subfolder_path.iterdir() 
                        if item.is_dir() and not item.name.startswith('.')]
        
        # If no proper subfolder structure found, look for direct subfolders (legacy)
        if not items:
            items = [item.name for item in parent_path.iterdir() 
                    if (item.is_dir() and 
                        not item.name.startswith('.') and 
                        item.name.lower() not in ['docs', 'tests', 'assets', 'data', 'config', 'requirements'])]
        
        return items

    def generate_requirements_compliance_report(self, all_issues: Dict[str, List[HierarchyIssue]]) -> str:
        """Generate a comprehensive requirements hierarchy compliance report"""
        report = []
        report.append("# 📊 REQUIREMENTS HIERARCHY COMPLIANCE REPORT")
        report.append(f"**Generated**: {Path(__file__).name}")
        report.append(f"**Date**: September 12, 2025")
        report.append("")
        report.append("## 🎯 Requirements Management Hierarchy")
        report.append("```")
        report.append("Level 1: North Star Domain → Strategic requirements")
        report.append("├── Level 2: Projects → Project-level requirements")
        report.append("    ├── Level 3: Systems/Workpackages → Functional requirements")
        report.append("        ├── Level 4: Features/Milestones → Detailed requirements")
        report.append("            ├── Level 5: Layers/Tasks → Implementation requirements")
        report.append("                └── Level 6: Components → Technical requirements")
        report.append("```")
        report.append("")
        
        # Summary statistics
        total_repos = len(all_issues)
        compliant_repos = len([repo for repo, issues in all_issues.items() if not issues])
        total_issues = sum(len(issues) for issues in all_issues.values())
        
        report.append("## 📈 Requirements Structure Summary")
        report.append(f"- **Total North Star Repositories**: {total_repos}")
        report.append(f"- **Properly Structured**: {compliant_repos}")
        report.append(f"- **Need Restructuring**: {total_repos - compliant_repos}")
        report.append(f"- **Total Structure Issues**: {total_issues}")
        report.append(f"- **Structure Compliance**: {(compliant_repos/total_repos)*100:.1f}%")
        report.append("")
        
        # Detailed analysis per repository
        for repo_name, issues in all_issues.items():
            report.append(f"## 📁 {repo_name}")
            
            if not issues:
                report.append("✅ **WELL STRUCTURED** - Requirements hierarchy properly organized")
            else:
                report.append(f"⚠️ **NEEDS ATTENTION** - {len(issues)} structure issues:")
                
                # Group issues by level
                issues_by_level = {}
                for issue in issues:
                    level_key = f"Level {issue.level}"
                    if level_key not in issues_by_level:
                        issues_by_level[level_key] = []
                    issues_by_level[level_key].append(issue)
                
                for level, level_issues in sorted(issues_by_level.items()):
                    report.append(f"\n### {level} ({self.level_names.get(int(level.split()[1]), 'Unknown')}):")
                    for issue in level_issues:
                        report.append(f"- **{issue.issue_type}**: {issue.description}")
                        report.append(f"  - *Recommendation*: {issue.recommendation}")
                        report.append(f"  - *Path*: `{issue.path}`")
            report.append("")
        
        # Action items
        if total_issues > 0:
            report.append("## 🔧 Recommended Actions")
            report.append("")
            
            # Prioritize by issue type
            issue_counts = {}
            for issues in all_issues.values():
                for issue in issues:
                    if issue.issue_type not in issue_counts:
                        issue_counts[issue.issue_type] = 0
                    issue_counts[issue.issue_type] += 1
            
            report.append("### Priority Issues:")
            for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                report.append(f"- **{issue_type}**: {count} instances")
            
            report.append("")
            report.append("### Implementation Plan:")
            report.append("1. **Create Level 3 Structure**: Organize projects into Systems/Workpackages")
            report.append("2. **Add Level 4 Organization**: Break systems into Features/Milestones")
            report.append("3. **Implement Level 5 Details**: Organize features into Layers/Tasks")
            report.append("4. **Requirements Integration**: Ensure each level can cascade requirements properly")
            report.append("5. **Validate Structure**: Re-run validation after restructuring")
        else:
            report.append("## ✅ All Repositories Well Structured")
            report.append("All repositories follow proper requirements management hierarchy!")
        
        return "\n".join(report)

def main():
    """Main validation function"""
    validator = RequirementsHierarchyValidator()
    
    # Run validation
    all_issues = validator.validate_requirements_hierarchy()
    
    # Generate report
    report = validator.generate_requirements_compliance_report(all_issues)
    
    # Save report
    report_path = Path("/workspaces/control_tower/reports/requirements_hierarchy_compliance.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📊 Requirements hierarchy report saved to: {report_path}")
    print("\n" + "=" * 70)
    print("🎯 REQUIREMENTS HIERARCHY VALIDATION COMPLETE")
    
    # Print summary
    total_repos = len(all_issues)
    compliant_repos = len([repo for repo, issues in all_issues.items() if not issues])
    total_issues = sum(len(issues) for issues in all_issues.values())
    
    print(f"📈 SUMMARY:")
    print(f"   • North Star Repositories: {total_repos}")
    print(f"   • Well Structured: {compliant_repos}")
    print(f"   • Need Attention: {total_repos - compliant_repos}")
    print(f"   • Structure Issues: {total_issues}")
    print(f"   • Compliance Rate: {(compliant_repos/total_repos)*100:.1f}%")
    
    if total_issues > 0:
        print(f"\n⚠️  Requirements hierarchy needs attention in {total_repos - compliant_repos} repositories")
        print("💡 Focus on creating proper Level 3+ organization for requirements cascade")
    else:
        print("\n✅ All repositories have proper requirements hierarchy structure!")

if __name__ == "__main__":
    main()