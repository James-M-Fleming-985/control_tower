#!/usr/bin/env python3
"""
Repository Hierarchy Compliance Validator

This script validates that all North Star repositories follow the correct 6-level hierarchy:
Level 0: Control Tower (this repo)
Level 1: North Star Domains (business_ventures, professional_excellence, etc.)
Level 2: Projects (either Application or Delivery type)
Level 3: Systems (Application) / Workpackages (Delivery)
Level 4: Features (Application) / Milestones (Delivery)  
Level 5: Layers (Application) / Tasks (Delivery)
Level 6: Components (both types)
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ProjectType(Enum):
    APPLICATION = "application"
    DELIVERY = "delivery"
    UNKNOWN = "unknown"

class HierarchyLevel(Enum):
    CONTROL_TOWER = 0
    NORTH_STAR = 1
    PROJECT = 2
    SYSTEM_WORKPACKAGE = 3
    FEATURE_MILESTONE = 4
    LAYER_TASK = 5
    COMPONENT = 6

@dataclass
class HierarchyIssue:
    repo_name: str
    level: int
    path: str
    issue_type: str
    description: str
    recommendation: str

@dataclass
class HierarchyNode:
    name: str
    path: str
    level: HierarchyLevel
    project_type: ProjectType
    children: List['HierarchyNode']
    issues: List[HierarchyIssue]

class HierarchyValidator:
    def __init__(self, base_path: str = "/workspaces/control_tower"):
        self.base_path = Path(base_path)
        self.cloned_repos_path = self.base_path / "cloned_repos"
        self.validation_results = {}
        
        # Expected naming patterns for each level
        self.expected_patterns = {
            HierarchyLevel.PROJECT: {
                "application": ["_app", "_system", "_platform", "_service"],
                "delivery": ["_project", "_delivery", "_initiative"]
            },
            HierarchyLevel.SYSTEM_WORKPACKAGE: {
                "application": ["system_", "service_", "module_", "component_"],
                "delivery": ["workpackage_", "wp_", "phase_"]
            },
            HierarchyLevel.FEATURE_MILESTONE: {
                "application": ["feature_", "capability_", "function_"],
                "delivery": ["milestone_", "m_", "deliverable_"]
            },
            HierarchyLevel.LAYER_TASK: {
                "application": ["layer_", "tier_", "interface_"],
                "delivery": ["task_", "activity_", "action_"]
            }
        }

    def validate_all_repositories(self) -> Dict[str, List[HierarchyIssue]]:
        """Validate hierarchy compliance across all North Star repositories"""
        print("🔍 Starting Repository Hierarchy Compliance Validation...")
        print("=" * 60)
        
        all_issues = {}
        
        if not self.cloned_repos_path.exists():
            print(f"❌ ERROR: cloned_repos directory not found at {self.cloned_repos_path}")
            return all_issues
            
        # Get all North Star repositories
        north_star_repos = [d for d in self.cloned_repos_path.iterdir() 
                           if d.is_dir() and not d.name.startswith('.')]
        
        print(f"📂 Found {len(north_star_repos)} North Star repositories:")
        for repo in north_star_repos:
            print(f"   • {repo.name}")
        print()
        
        # Validate each repository
        for repo_dir in north_star_repos:
            print(f"🔍 Validating {repo_dir.name}...")
            issues = self.validate_repository(repo_dir)
            all_issues[repo_dir.name] = issues
            
            if issues:
                print(f"   ⚠️  Found {len(issues)} hierarchy issues")
            else:
                print(f"   ✅ Hierarchy compliant")
        
        return all_issues

    def validate_repository(self, repo_path: Path) -> List[HierarchyIssue]:
        """Validate hierarchy compliance for a single repository"""
        issues = []
        
        # Check if this is a North Star repository (Level 1)
        if not self.is_north_star_repository(repo_path):
            issues.append(HierarchyIssue(
                repo_name=repo_path.name,
                level=1,
                path=str(repo_path),
                issue_type="structure",
                description="Missing North Star repository structure",
                recommendation="Add required North Star folders: docs/, requirements/, templates/, tests/, workflows/, metrics/"
            ))
        
        # Find and validate projects (Level 2)
        projects = self.find_projects(repo_path)
        
        if not projects:
            issues.append(HierarchyIssue(
                repo_name=repo_path.name,
                level=2,
                path=str(repo_path),
                issue_type="missing_projects",
                description="No projects found in repository",
                recommendation="Create project folders following Level 2 structure"
            ))
        
        for project_path in projects:
            project_issues = self.validate_project_hierarchy(repo_path.name, project_path)
            issues.extend(project_issues)
        
        return issues

    def is_north_star_repository(self, repo_path: Path) -> bool:
        """Check if repository has required North Star structure"""
        required_folders = ["docs", "requirements", "templates", "tests", "workflows", "metrics"]
        existing_folders = [d.name for d in repo_path.iterdir() if d.is_dir()]
        
        # Check if at least 4 of 6 required folders exist
        found_folders = sum(1 for folder in required_folders if folder in existing_folders)
        return found_folders >= 4

    def find_projects(self, repo_path: Path) -> List[Path]:
        """Find all project directories in the repository"""
        projects = []
        
        # Look for direct project folders (legacy structure)
        for item in repo_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in ["docs", "requirements", "templates", "tests", "workflows", "metrics"]:
                # Check if this looks like a project
                if self.looks_like_project(item):
                    projects.append(item)
        
        # Look for projects in a projects/ subfolder (new structure)
        projects_dir = repo_path / "projects"
        if projects_dir.exists():
            for item in projects_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    projects.append(item)
        
        return projects

    def looks_like_project(self, path: Path) -> bool:
        """Determine if a directory looks like a project"""
        # Check for project indicators
        project_indicators = [
            "README.md", "requirements.txt", "package.json", 
            ".git", "src/", "modules/", "components/",
            "systems/", "features/", "layers/", "workpackages/", 
            "milestones/", "tasks/"
        ]
        
        contents = [item.name for item in path.iterdir()]
        
        # If it has at least 2 project indicators, consider it a project
        found_indicators = sum(1 for indicator in project_indicators if indicator in contents)
        return found_indicators >= 2

    def determine_project_type(self, project_path: Path) -> ProjectType:
        """Determine if project is Application or Delivery type"""
        contents = [item.name.lower() for item in project_path.iterdir() if item.is_dir()]
        
        # Application project indicators
        app_indicators = ["src", "modules", "components", "systems", "features", "layers", "services", "core"]
        
        # Delivery project indicators  
        delivery_indicators = ["workpackages", "milestones", "tasks", "deliverables", "phases"]
        
        app_score = sum(1 for indicator in app_indicators if any(indicator in content for content in contents))
        delivery_score = sum(1 for indicator in delivery_indicators if any(indicator in content for content in contents))
        
        if app_score > delivery_score:
            return ProjectType.APPLICATION
        elif delivery_score > app_score:
            return ProjectType.DELIVERY
        else:
            return ProjectType.UNKNOWN

    def validate_project_hierarchy(self, repo_name: str, project_path: Path) -> List[HierarchyIssue]:
        """Validate the hierarchy within a specific project"""
        issues = []
        project_type = self.determine_project_type(project_path)
        
        if project_type == ProjectType.UNKNOWN:
            issues.append(HierarchyIssue(
                repo_name=repo_name,
                level=2,
                path=str(project_path),
                issue_type="unclear_type",
                description="Cannot determine if project is Application or Delivery type",
                recommendation="Add clear Application folders (src/, systems/, features/, layers/) or Delivery folders (workpackages/, milestones/, tasks/)"
            ))
        
        # Check Level 3: Systems/Workpackages
        level3_issues = self.validate_level3_structure(repo_name, project_path, project_type)
        issues.extend(level3_issues)
        
        return issues

    def validate_level3_structure(self, repo_name: str, project_path: Path, project_type: ProjectType) -> List[HierarchyIssue]:
        """Validate Level 3 structure (Systems for Application, Workpackages for Delivery)"""
        issues = []
        
        if project_type == ProjectType.APPLICATION:
            expected_folders = ["systems", "modules", "components", "services"]
            level_name = "Systems"
        elif project_type == ProjectType.DELIVERY:
            expected_folders = ["workpackages", "phases", "deliverables"]
            level_name = "Workpackages"
        else:
            return issues  # Skip if type unknown
        
        # Check if project has proper Level 3 structure
        existing_folders = [d.name.lower() for d in project_path.iterdir() if d.is_dir()]
        
        found_level3 = any(folder in existing_folders for folder in expected_folders)
        
        if not found_level3:
            issues.append(HierarchyIssue(
                repo_name=repo_name,
                level=3,
                path=str(project_path),
                issue_type="missing_level3",
                description=f"Missing Level 3 ({level_name}) structure",
                recommendation=f"Create {level_name.lower()}/ folder and organize content into proper hierarchy"
            ))
        
        # Check for flat structure (everything in project root)
        file_count = len([f for f in project_path.iterdir() if f.is_file() and not f.name.startswith('.')])
        folder_count = len([f for f in project_path.iterdir() if f.is_dir() and not f.name.startswith('.')])
        
        if file_count > 10 and folder_count < 3:
            issues.append(HierarchyIssue(
                repo_name=repo_name,
                level=3,
                path=str(project_path),
                issue_type="flat_structure",
                description="Project has flat structure with too many files in root",
                recommendation="Organize files into proper hierarchical structure with systems/workpackages"
            ))
        
        return issues

    def generate_compliance_report(self, all_issues: Dict[str, List[HierarchyIssue]]) -> str:
        """Generate a comprehensive compliance report"""
        report = []
        report.append("# 📊 REPOSITORY HIERARCHY COMPLIANCE REPORT")
        report.append(f"**Generated**: {Path(__file__).name}")
        report.append(f"**Date**: September 12, 2025")
        report.append("")
        report.append("## 🎯 Expected Hierarchy Structure")
        report.append("```")
        report.append("Level 0: Control Tower (control_tower/)")
        report.append("├── Level 1: North Star Domains (business_ventures/, professional_excellence/, etc.)")
        report.append("    ├── Level 2: Projects (either Application or Delivery)")
        report.append("        ├── Level 3: Systems (App) / Workpackages (Delivery)")
        report.append("            ├── Level 4: Features (App) / Milestones (Delivery)")
        report.append("                ├── Level 5: Layers (App) / Tasks (Delivery)")
        report.append("                    └── Level 6: Components (both types)")
        report.append("```")
        report.append("")
        
        # Summary statistics
        total_repos = len(all_issues)
        compliant_repos = len([repo for repo, issues in all_issues.items() if not issues])
        total_issues = sum(len(issues) for issues in all_issues.values())
        
        report.append("## 📈 Compliance Summary")
        report.append(f"- **Total Repositories**: {total_repos}")
        report.append(f"- **Compliant Repositories**: {compliant_repos}")
        report.append(f"- **Non-compliant Repositories**: {total_repos - compliant_repos}")
        report.append(f"- **Total Issues Found**: {total_issues}")
        report.append(f"- **Compliance Rate**: {(compliant_repos/total_repos)*100:.1f}%")
        report.append("")
        
        # Detailed results per repository
        for repo_name, issues in all_issues.items():
            report.append(f"## 📁 {repo_name}")
            
            if not issues:
                report.append("✅ **COMPLIANT** - Repository follows correct hierarchy structure")
            else:
                report.append(f"⚠️ **NON-COMPLIANT** - {len(issues)} issues found:")
                
                # Group issues by level
                issues_by_level = {}
                for issue in issues:
                    level = f"Level {issue.level}"
                    if level not in issues_by_level:
                        issues_by_level[level] = []
                    issues_by_level[level].append(issue)
                
                for level, level_issues in sorted(issues_by_level.items()):
                    report.append(f"\n### {level} Issues:")
                    for issue in level_issues:
                        report.append(f"- **{issue.issue_type}**: {issue.description}")
                        report.append(f"  - *Recommendation*: {issue.recommendation}")
                        report.append(f"  - *Path*: `{issue.path}`")
            report.append("")
        
        # Recommendations section
        if total_issues > 0:
            report.append("## 🔧 Priority Recommendations")
            report.append("")
            
            # Count issue types
            issue_types = {}
            for issues in all_issues.values():
                for issue in issues:
                    if issue.issue_type not in issue_types:
                        issue_types[issue.issue_type] = 0
                    issue_types[issue.issue_type] += 1
            
            report.append("### Most Common Issues:")
            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                report.append(f"- **{issue_type}**: {count} occurrences")
            
            report.append("")
            report.append("### Next Steps:")
            report.append("1. **Address Structure Issues**: Focus on repositories with missing Level 3 structure")
            report.append("2. **Clarify Project Types**: Determine Application vs Delivery for unclear projects")
            report.append("3. **Implement Hierarchy**: Create proper folder structures following the 6-level hierarchy")
            report.append("4. **Validate Compliance**: Re-run this script after making changes")
        
        return "\n".join(report)

def main():
    """Main validation function"""
    validator = HierarchyValidator()
    
    # Run validation
    all_issues = validator.validate_all_repositories()
    
    # Generate report
    report = validator.generate_compliance_report(all_issues)
    
    # Save report
    report_path = Path("/workspaces/control_tower/reports/hierarchy_compliance_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📊 Compliance report saved to: {report_path}")
    print("\n" + "=" * 60)
    print("🎯 VALIDATION COMPLETE")
    
    # Print summary to console
    total_repos = len(all_issues)
    compliant_repos = len([repo for repo, issues in all_issues.items() if not issues])
    total_issues = sum(len(issues) for issues in all_issues.values())
    
    print(f"📈 SUMMARY:")
    print(f"   • Total Repositories: {total_repos}")
    print(f"   • Compliant: {compliant_repos}")
    print(f"   • Non-compliant: {total_repos - compliant_repos}")
    print(f"   • Total Issues: {total_issues}")
    print(f"   • Compliance Rate: {(compliant_repos/total_repos)*100:.1f}%")
    
    if total_issues > 0:
        print(f"\n⚠️  {total_issues} hierarchy issues found. See report for details.")
    else:
        print("\n✅ All repositories are hierarchy compliant!")

if __name__ == "__main__":
    main()