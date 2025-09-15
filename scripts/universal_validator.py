#!/usr/bin/env python3
"""
Universal Professional Standards Validator
Enforces professional standards across ALL requirement levels
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import json
import datetime


class UniversalValidator:
    """Universal validator for all requirement levels"""
    
    def __init__(self, workspace_root: str = "/workspaces/control_tower"):
        self.workspace_root = Path(workspace_root)
        self.evidence_dir = self.workspace_root / "evidence"
        self.validation_reports_dir = self.evidence_dir / "validation_reports"
        
        # Create evidence directories
        self.validation_reports_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_system(self, system_name: str) -> Dict[str, Any]:
        """Validate entire system with all projects"""
        print(f"🏗️ SYSTEM VALIDATION: {system_name}")
        print("=" * 60)
        
        # Find all projects in system
        projects = self._discover_projects_in_system(system_name)
        
        overall_results = {
            "system": system_name,
            "validation_type": "SYSTEM",
            "timestamp": datetime.datetime.now().isoformat(),
            "projects": {},
            "overall_status": "UNKNOWN",
            "total_projects": len(projects),
            "passed_projects": 0,
            "failed_projects": 0
        }
        
        for project in projects:
            print(f"\n📋 Validating Project: {project}")
            project_result = self.validate_project(project)
            overall_results["projects"][project] = project_result
            
            if project_result.get("overall_status") == "PROFESSIONAL_COMPLETE":
                overall_results["passed_projects"] += 1
            else:
                overall_results["failed_projects"] += 1
        
        # Calculate overall status
        if overall_results["passed_projects"] == overall_results["total_projects"]:
            overall_results["overall_status"] = "SYSTEM_COMPLETE"
        elif overall_results["passed_projects"] > 0:
            overall_results["overall_status"] = "PARTIAL_COMPLETION"
        else:
            overall_results["overall_status"] = "SYSTEM_INCOMPLETE"
        
        self._display_system_results(overall_results)
        return overall_results
    
    def validate_project(self, project_name: str) -> Dict[str, Any]:
        """Validate entire project with all features"""
        print(f"📋 PROJECT VALIDATION: {project_name}")
        print("-" * 40)
        
        # Find all features in project
        features = self._discover_features_in_project(project_name)
        
        project_results = {
            "project": project_name,
            "validation_type": "PROJECT",
            "timestamp": datetime.datetime.now().isoformat(),
            "features": {},
            "overall_status": "UNKNOWN",
            "total_features": len(features),
            "passed_features": 0,
            "failed_features": 0
        }
        
        for feature in features:
            print(f"  🔍 Validating Feature: {feature}")
            feature_result = self.validate_feature(feature)
            project_results["features"][feature] = feature_result
            
            if feature_result.get("overall_status") == "PROFESSIONAL_COMPLETE":
                project_results["passed_features"] += 1
            else:
                project_results["failed_features"] += 1
        
        # Calculate overall status
        if project_results["passed_features"] == project_results["total_features"]:
            project_results["overall_status"] = "PROFESSIONAL_COMPLETE"
        elif project_results["passed_features"] > 0:
            project_results["overall_status"] = "PARTIAL_COMPLETION"
        else:
            project_results["overall_status"] = "PROJECT_INCOMPLETE"
        
        return project_results
    
    def validate_feature(self, feature_name: str) -> Dict[str, Any]:
        """Validate feature with all components"""
        print(f"    🎯 FEATURE VALIDATION: {feature_name}")
        
        # Find all components in feature
        components = self._discover_components_in_feature(feature_name)
        
        feature_results = {
            "feature": feature_name,
            "validation_type": "FEATURE",
            "timestamp": datetime.datetime.now().isoformat(),
            "components": {},
            "overall_status": "UNKNOWN",
            "total_components": len(components),
            "passed_components": 0,
            "failed_components": 0
        }
        
        for component in components:
            print(f"      🔧 Validating Component: {component}")
            component_result = self.validate_component(component)
            feature_results["components"][component] = component_result
            
            if component_result.get("overall_status") == "PROFESSIONAL_COMPLETE":
                feature_results["passed_components"] += 1
            else:
                feature_results["failed_components"] += 1
        
        # Calculate overall status
        if feature_results["passed_components"] == feature_results["total_components"]:
            feature_results["overall_status"] = "PROFESSIONAL_COMPLETE"
        elif feature_results["passed_components"] > 0:
            feature_results["overall_status"] = "PARTIAL_COMPLETION"
        else:
            feature_results["overall_status"] = "FEATURE_INCOMPLETE"
        
        return feature_results
    
    def validate_component(self, component_name: str) -> Dict[str, Any]:
        """Validate individual component using professional validator"""
        try:
            # Use the existing professional validator
            result = subprocess.run([
                "python", "scripts/professional_validator.py", component_name
            ], cwd=self.workspace_root, capture_output=True, text=True)
            
            component_results = {
                "component": component_name,
                "validation_type": "COMPONENT",
                "timestamp": datetime.datetime.now().isoformat(),
                "validation_passed": result.returncode == 0,
                "validation_output": result.stdout + result.stderr,
                "overall_status": "PROFESSIONAL_COMPLETE" if result.returncode == 0 else "COMPONENT_INCOMPLETE"
            }
            
            return component_results
            
        except Exception as e:
            return {
                "component": component_name,
                "validation_type": "COMPONENT",
                "error": str(e),
                "overall_status": "VALIDATION_ERROR"
            }
    
    def _discover_projects_in_system(self, system_name: str) -> List[str]:
        """Discover all projects in a system"""
        # This is a simplified discovery - in practice would scan requirements files
        if system_name == "control_tower":
            return ["what-next", "work-on", "automated-tdd"]
        elif system_name == "hierarchical":
            return ["repository-scanner", "work-item-discoverer", "priority-calculator"]
        else:
            return [system_name]  # Fallback
    
    def _discover_features_in_project(self, project_name: str) -> List[str]:
        """Discover all features in a project"""
        # This is a simplified discovery - in practice would scan feature files
        if project_name == "what-next":
            return ["repository_scanner", "work_item_discoverer", "priority_calculator", "hierarchy_formatter"]
        elif project_name == "work-on":
            return ["test_generator", "tdd_workflow_engine", "tdd_progress_formatter", "git_safety_manager", "tool_integration_manager"]
        else:
            return [project_name]  # Fallback
    
    def _discover_components_in_feature(self, feature_name: str) -> List[str]:
        """Discover all components in a feature"""
        # This is simplified - in practice would scan implementation files
        return [feature_name]  # For now, treat feature as single component
    
    def _display_system_results(self, results: Dict[str, Any]):
        """Display system validation results"""
        print(f"\n🏗️ SYSTEM VALIDATION RESULTS: {results['system']}")
        print("=" * 60)
        
        status = results["overall_status"]
        if status == "SYSTEM_COMPLETE":
            print("✅ STATUS: SYSTEM PROFESSIONALLY COMPLETE")
        elif status == "PARTIAL_COMPLETION":
            print("⚠️  STATUS: PARTIAL SYSTEM COMPLETION")
        else:
            print("❌ STATUS: SYSTEM INCOMPLETE")
        
        print(f"\n📊 SYSTEM BREAKDOWN:")
        print(f"  Total Projects: {results['total_projects']}")
        print(f"  ✅ Passed: {results['passed_projects']}")
        print(f"  ❌ Failed: {results['failed_projects']}")
        
        print(f"\n📋 PROJECT DETAILS:")
        for project_name, project_result in results["projects"].items():
            status_icon = "✅" if project_result.get("overall_status") == "PROFESSIONAL_COMPLETE" else "❌"
            print(f"  {status_icon} {project_name}: {project_result.get('overall_status', 'UNKNOWN')}")
        
        # Save results
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.validation_reports_dir / f"system_{results['system']}_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Evidence Report: {report_path}")
        print("=" * 60)


def main():
    """Main entry point for universal validation"""
    parser = argparse.ArgumentParser(description='Universal Professional Standards Validator')
    parser.add_argument('--system', help='Validate entire system')
    parser.add_argument('--project', help='Validate entire project')
    parser.add_argument('--feature', help='Validate feature with all components')
    parser.add_argument('--component', help='Validate individual component')
    
    args = parser.parse_args()
    
    validator = UniversalValidator()
    
    if args.system:
        results = validator.validate_system(args.system)
        exit_code = 0 if results["overall_status"] == "SYSTEM_COMPLETE" else 1
    elif args.project:
        results = validator.validate_project(args.project)
        exit_code = 0 if results["overall_status"] == "PROFESSIONAL_COMPLETE" else 1
    elif args.feature:
        results = validator.validate_feature(args.feature)
        exit_code = 0 if results["overall_status"] == "PROFESSIONAL_COMPLETE" else 1
    elif args.component:
        results = validator.validate_component(args.component)
        exit_code = 0 if results["overall_status"] == "PROFESSIONAL_COMPLETE" else 1
    else:
        print("Error: Must specify --system, --project, --feature, or --component")
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()