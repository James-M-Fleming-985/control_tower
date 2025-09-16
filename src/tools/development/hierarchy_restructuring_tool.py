#!/usr/bin/env python3
"""
Repository Hierarchy Restructuring Tool

This tool analyzes current inconsistent hierarchies and provides restructuring recommendations
to ensure consistent requirements management across all repositories from Control Tower.

The goal is to establish consistent hierarchy so that:
1. Control Tower knows exactly what level it's working at
2. Requirements can cascade properly through all levels
3. System behavior is consistent across all repositories
4. Each level has proper requirements/ folders for validation
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class HierarchyMapping:
    current_path: str
    current_level: int
    suggested_path: str
    suggested_level: int
    reasoning: str

@dataclass
class RestructuringPlan:
    repository: str
    project: str
    current_structure: Dict
    suggested_structure: Dict
    mappings: List[HierarchyMapping]
    priority: str  # "high", "medium", "low"

class HierarchyRestructurer:
    def __init__(self, base_path: str = "/workspaces/control_tower"):
        self.base_path = Path(base_path)
        self.cloned_repos_path = self.base_path / "cloned_repos"
        
        # Standard hierarchy definitions
        self.standard_hierarchy = {
            1: "North Star Domain",
            2: "Project", 
            3: "System/Workpackage",
            4: "Feature/Milestone",
            5: "Layer/Task",
            6: "Component"
        }
        
        # Project type patterns
        self.project_patterns = {
            "application": {
                3: ["systems", "modules", "services"],
                4: ["features", "capabilities"],
                5: ["layers", "components"],
                6: ["components", "elements"]
            },
            "delivery": {
                3: ["workpackages", "phases"],
                4: ["milestones", "deliverables"],
                5: ["tasks", "activities"],
                6: ["components", "items"]
            }
        }

    def analyze_all_repositories(self) -> Dict[str, List[RestructuringPlan]]:
        """Analyze all repositories and create restructuring plans"""
        print("🔍 Analyzing Repository Hierarchies for Restructuring...")
        print("=" * 70)
        
        all_plans = {}
        
        if not self.cloned_repos_path.exists():
            print(f"❌ ERROR: cloned_repos directory not found")
            return all_plans
        
        # Get all North Star repositories
        repos = [d for d in self.cloned_repos_path.iterdir() 
                if d.is_dir() and not d.name.startswith('.')]
        
        for repo_dir in repos:
            print(f"\n📂 Analyzing {repo_dir.name}...")
            plans = self.analyze_repository(repo_dir)
            if plans:
                all_plans[repo_dir.name] = plans
                print(f"   📋 Created {len(plans)} restructuring plans")
            else:
                print(f"   ✅ No restructuring needed")
        
        return all_plans

    def analyze_repository(self, repo_path: Path) -> List[RestructuringPlan]:
        """Analyze a single repository and create restructuring plans"""
        plans = []
        
        # Find all projects in repository
        projects = self.find_projects(repo_path)
        
        for project_path in projects:
            plan = self.analyze_project_structure(repo_path.name, project_path)
            if plan:
                plans.append(plan)
        
        return plans

    def find_projects(self, repo_path: Path) -> List[Path]:
        """Find all project directories in repository"""
        projects = []
        
        # Look for direct projects
        for item in repo_path.iterdir():
            if (item.is_dir() and 
                not item.name.startswith('.') and 
                item.name not in ["docs", "requirements", "templates", "tests", "workflows", "metrics"]):
                
                if self.looks_like_project(item):
                    projects.append(item)
        
        # Look in projects/ subfolder
        projects_dir = repo_path / "projects"
        if projects_dir.exists():
            for item in projects_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    projects.append(item)
        
        return projects

    def looks_like_project(self, path: Path) -> bool:
        """Check if directory looks like a project"""
        contents = list(path.iterdir())
        return len(contents) >= 2  # Has some content

    def analyze_project_structure(self, repo_name: str, project_path: Path) -> Optional[RestructuringPlan]:
        """Analyze a project's structure and create restructuring plan"""
        
        # Determine project type
        project_type = self.determine_project_type(project_path)
        
        # Analyze current structure
        current_structure = self.map_current_structure(project_path)
        
        # Create suggested structure
        suggested_structure = self.create_suggested_structure(project_path, project_type)
        
        # Create mappings
        mappings = self.create_restructuring_mappings(project_path, current_structure, suggested_structure)
        
        # Determine priority
        priority = self.calculate_restructuring_priority(current_structure, suggested_structure)
        
        if mappings:  # Only create plan if restructuring is needed
            return RestructuringPlan(
                repository=repo_name,
                project=project_path.name,
                current_structure=current_structure,
                suggested_structure=suggested_structure,
                mappings=mappings,
                priority=priority
            )
        
        return None

    def determine_project_type(self, project_path: Path) -> str:
        """Determine if project is application or delivery type"""
        
        # Look at folder names and patterns
        folders = [item.name.lower() for item in project_path.iterdir() if item.is_dir()]
        
        # Application indicators
        app_indicators = ["src", "modules", "components", "systems", "services", "core", "features", "layers"]
        app_score = sum(1 for indicator in app_indicators if any(indicator in folder for folder in folders))
        
        # Delivery indicators
        delivery_indicators = ["workpackages", "milestones", "tasks", "phases", "deliverables", "projects"]
        delivery_score = sum(1 for indicator in delivery_indicators if any(indicator in folder for folder in folders))
        
        # Special case: home improvement type projects
        home_indicators = ["kitchen", "bathroom", "garage", "renovation", "improvement"]
        home_score = sum(1 for indicator in home_indicators if any(indicator in folder for folder in folders))
        
        if home_score > 0 or "home" in project_path.name.lower():
            return "delivery"
        elif app_score > delivery_score:
            return "application"
        elif delivery_score > 0:
            return "delivery"
        else:
            return "delivery"  # Default to delivery for unclear cases

    def map_current_structure(self, project_path: Path, level: int = 2, max_depth: int = 6) -> Dict:
        """Map the current structure of a project"""
        structure = {
            "name": project_path.name,
            "level": level,
            "path": str(project_path),
            "children": []
        }
        
        if level < max_depth:
            for item in project_path.iterdir():
                if (item.is_dir() and 
                    not item.name.startswith('.') and 
                    item.name.lower() not in ["docs", "tests", "assets", "data", "config", "__pycache__", "node_modules"]):
                    
                    child_structure = self.map_current_structure(item, level + 1, max_depth)
                    structure["children"].append(child_structure)
        
        return structure

    def create_suggested_structure(self, project_path: Path, project_type: str) -> Dict:
        """Create suggested structure based on project type"""
        
        if project_type == "delivery":
            # For delivery projects like home_improvements
            if "home" in project_path.name.lower() or "improvement" in project_path.name.lower():
                return self.create_home_improvement_structure(project_path)
            else:
                return self.create_generic_delivery_structure(project_path)
        else:
            return self.create_application_structure(project_path)

    def create_home_improvement_structure(self, project_path: Path) -> Dict:
        """Create suggested structure for home improvement projects"""
        
        # Analyze current renovation areas
        current_areas = []
        self._find_renovation_areas(project_path, current_areas)
        
        structure = {
            "name": project_path.name,
            "level": 2,
            "path": str(project_path),
            "children": [
                {
                    "name": "requirements",
                    "level": 2,
                    "path": str(project_path / "requirements"),
                    "type": "requirements_folder"
                },
                {
                    "name": "workpackages",
                    "level": 3,
                    "path": str(project_path / "workpackages"),
                    "children": []
                }
            ]
        }
        
        # Add workpackages for each renovation area
        workpackages_node = structure["children"][1]
        for area in current_areas:
            workpackage = {
                "name": area.lower().replace(" ", "_"),
                "level": 3,
                "path": str(project_path / "workpackages" / area.lower().replace(" ", "_")),
                "children": [
                    {
                        "name": "requirements",
                        "level": 3,
                        "path": str(project_path / "workpackages" / area.lower().replace(" ", "_") / "requirements"),
                        "type": "requirements_folder"
                    },
                    {
                        "name": "milestones",
                        "level": 4,
                        "path": str(project_path / "workpackages" / area.lower().replace(" ", "_") / "milestones"),
                        "children": [
                            {
                                "name": "planning_complete",
                                "level": 4,
                                "children": [
                                    {"name": "requirements", "type": "requirements_folder"},
                                    {"name": "tasks", "level": 5, "children": [
                                        {"name": "design_approval", "level": 5},
                                        {"name": "permits_obtained", "level": 5},
                                        {"name": "contractor_selected", "level": 5}
                                    ]}
                                ]
                            },
                            {
                                "name": "materials_procured",
                                "level": 4,
                                "children": [
                                    {"name": "requirements", "type": "requirements_folder"},
                                    {"name": "tasks", "level": 5, "children": [
                                        {"name": "material_selection", "level": 5},
                                        {"name": "supplier_coordination", "level": 5},
                                        {"name": "delivery_scheduled", "level": 5}
                                    ]}
                                ]
                            },
                            {
                                "name": "work_completed",
                                "level": 4,
                                "children": [
                                    {"name": "requirements", "type": "requirements_folder"},
                                    {"name": "tasks", "level": 5, "children": [
                                        {"name": "construction_work", "level": 5},
                                        {"name": "quality_inspection", "level": 5},
                                        {"name": "final_approval", "level": 5}
                                    ]}
                                ]
                            }
                        ]
                    }
                ]
            }
            workpackages_node["children"].append(workpackage)
        
        return structure

    def _find_renovation_areas(self, path: Path, areas: List[str], depth: int = 0):
        """Find renovation areas in current structure"""
        if depth > 3:  # Don't go too deep
            return
            
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                name = item.name.replace("_", " ").replace("-", " ").title()
                
                # Look for renovation keywords
                renovation_keywords = ["kitchen", "bathroom", "garage", "bedroom", "living", "dining", "exterior", "landscaping"]
                if any(keyword in name.lower() for keyword in renovation_keywords):
                    if name not in areas:
                        areas.append(name)
                else:
                    # Recurse into subdirectories
                    self._find_renovation_areas(item, areas, depth + 1)

    def create_generic_delivery_structure(self, project_path: Path) -> Dict:
        """Create suggested structure for generic delivery projects"""
        return {
            "name": project_path.name,
            "level": 2,
            "path": str(project_path),
            "children": [
                {
                    "name": "requirements",
                    "level": 2,
                    "path": str(project_path / "requirements"),
                    "type": "requirements_folder"
                },
                {
                    "name": "workpackages",
                    "level": 3,
                    "path": str(project_path / "workpackages"),
                    "children": []
                }
            ]
        }

    def create_application_structure(self, project_path: Path) -> Dict:
        """Create suggested structure for application projects"""
        return {
            "name": project_path.name,
            "level": 2,
            "path": str(project_path),
            "children": [
                {
                    "name": "requirements",
                    "level": 2,
                    "path": str(project_path / "requirements"),
                    "type": "requirements_folder"
                },
                {
                    "name": "systems",
                    "level": 3,
                    "path": str(project_path / "systems"),
                    "children": []
                }
            ]
        }

    def create_restructuring_mappings(self, project_path: Path, current: Dict, suggested: Dict) -> List[HierarchyMapping]:
        """Create mappings between current and suggested structures"""
        mappings = []
        
        # Simple check: if structures are very different, we need restructuring
        current_depth = self._calculate_depth(current) if current else 1
        suggested_depth = self._calculate_depth(suggested) if suggested else 1
        
        if abs(current_depth - suggested_depth) > 1:
            mappings.append(HierarchyMapping(
                current_path=str(project_path),
                current_level=2,
                suggested_path=str(project_path),
                suggested_level=2,
                reasoning="Project needs restructuring for consistent requirements hierarchy"
            ))
        
        return mappings

    def _compare_structures(self, current: Dict, suggested: Dict, mappings: List[HierarchyMapping]):
        """Compare current and suggested structures recursively"""
        # Simple implementation - just check if major restructuring needed
        pass

    def calculate_restructuring_priority(self, current: Dict, suggested: Dict) -> str:
        """Calculate priority for restructuring based on complexity"""
        
        # Count levels and inconsistencies
        current_depth = self._calculate_depth(current)
        suggested_depth = self._calculate_depth(suggested)
        
        # Simple heuristic
        if current_depth < 3:
            return "high"  # Definitely needs restructuring
        elif abs(current_depth - suggested_depth) > 2:
            return "high"
        else:
            return "medium"

    def _calculate_depth(self, structure: Dict) -> int:
        """Calculate the depth of a structure"""
        if not structure or "children" not in structure or not structure["children"]:
            return 1
        
        max_child_depth = max(self._calculate_depth(child) for child in structure["children"])
        return 1 + max_child_depth

    def generate_restructuring_report(self, all_plans: Dict[str, List[RestructuringPlan]]) -> str:
        """Generate comprehensive restructuring report"""
        report = []
        report.append("# 🔧 REPOSITORY HIERARCHY RESTRUCTURING PLAN")
        report.append(f"**Generated**: September 12, 2025")
        report.append("")
        report.append("## 🎯 Goal: Consistent Requirements Management Hierarchy")
        report.append("")
        report.append("The current inconsistent hierarchies break Control Tower requirements management.")
        report.append("This plan establishes consistent structure so that:")
        report.append("- Control Tower knows exactly what level it's working at")
        report.append("- Requirements can cascade properly through all levels")
        report.append("- System behavior is consistent across all repositories")
        report.append("- Each level has proper requirements/ folders for validation")
        report.append("")
        
        # Summary
        total_plans = sum(len(plans) for plans in all_plans.values())
        high_priority = sum(1 for plans in all_plans.values() for plan in plans if plan.priority == "high")
        
        report.append("## 📊 Restructuring Summary")
        report.append(f"- **Total Projects**: {total_plans}")
        report.append(f"- **High Priority**: {high_priority}")
        report.append(f"- **Repositories Affected**: {len(all_plans)}")
        report.append("")
        
        # Detailed plans
        for repo_name, plans in all_plans.items():
            report.append(f"## 📁 {repo_name}")
            
            for plan in plans:
                report.append(f"### {plan.project} ({plan.priority.upper()} PRIORITY)")
                
                report.append("**Current Issues:**")
                report.append(f"- Inconsistent hierarchy prevents proper requirements cascade")
                report.append(f"- Control Tower cannot determine correct working level")
                report.append(f"- Missing requirements/ folders at key levels")
                
                report.append("\n**Suggested Structure:**")
                self._format_structure_for_report(plan.suggested_structure, report, "")
                
                report.append("")
        
        return "\n".join(report)

    def _format_structure_for_report(self, structure: Dict, report: List[str], indent: str):
        """Format structure for report display"""
        name = structure.get("name", "")
        level = structure.get("level", "")
        
        if structure.get("type") == "requirements_folder":
            report.append(f"{indent}├── 📋 {name}/ (requirements)")
        else:
            report.append(f"{indent}├── 📁 {name}/ (Level {level})")
        
        children = structure.get("children", [])
        for i, child in enumerate(children):
            child_indent = indent + ("│   " if i < len(children) - 1 else "    ")
            self._format_structure_for_report(child, report, child_indent)

def main():
    """Main restructuring analysis function"""
    restructurer = HierarchyRestructurer()
    
    # Analyze all repositories
    all_plans = restructurer.analyze_all_repositories()
    
    # Generate report
    report = restructurer.generate_restructuring_report(all_plans)
    
    # Save report
    report_path = Path("/workspaces/control_tower/reports/hierarchy_restructuring_plan.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📊 Restructuring plan saved to: {report_path}")
    print("🎯 ANALYSIS COMPLETE")

if __name__ == "__main__":
    main()