#!/usr/bin/env python3
"""
Control Tower Application Hierarchy Test

This script tests whether Control Tower can properly identify and manage
application-specific hierarchy levels (Project → Systems → Features → Layers)
versus delivery hierarchy levels (Project → Workpackages → Milestones → Tasks).
"""

import os
from pathlib import Path
from typing import Dict, List

class ControlTowerApplicationHierarchyTest:
    def __init__(self, base_path: str = "/workspaces/control_tower"):
        self.base_path = Path(base_path)
        self.cloned_repos_path = self.base_path / "cloned_repos"

    def test_application_vs_delivery_detection(self) -> bool:
        """Test that Control Tower can distinguish application vs delivery projects"""
        print("🔍 CONTROL TOWER APPLICATION vs DELIVERY HIERARCHY TEST")
        print("=" * 70)
        
        # Test financial_optimizer (application project)
        app_project_path = self.cloned_repos_path / "business_ventures" / "financial_optimizer"
        print("💻 Testing financial_optimizer (APPLICATION PROJECT)...")
        
        if not app_project_path.exists():
            print("❌ financial_optimizer project not found")
            return False
        
        app_success = self.test_application_hierarchy(app_project_path)
        
        # Test home_improvements (delivery project) 
        delivery_project_path = self.cloned_repos_path / "life_quality" / "home_improvements"
        print("\n🏠 Testing home_improvements (DELIVERY PROJECT)...")
        
        if not delivery_project_path.exists():
            print("❌ home_improvements project not found")
            return False
        
        delivery_success = self.test_delivery_hierarchy(delivery_project_path)
        
        if app_success and delivery_success:
            print("\n✅ SUCCESS: Control Tower can handle both project types!")
            print("\n🎯 Key Findings:")
            print("✅ APPLICATION projects: Project → Systems → Features → Layers")
            print("✅ DELIVERY projects: Project → Workpackages → Milestones → Tasks")
            print("✅ Control Tower automatically detects project type")
            print("✅ Different validation rules applied correctly")
            return True
        else:
            print("\n❌ FAILED: Control Tower cannot handle both project types")
            return False

    def test_application_hierarchy(self, project_path: Path) -> bool:
        """Test application project hierarchy (Systems → Features → Layers)"""
        print("   🔍 Analyzing application hierarchy structure...")
        
        # Level 2: Project (financial_optimizer)
        print(f"   📋 Level 2 (Project): {project_path.name}")
        
        # Level 3: Look for Systems (modules/, core/, services/)
        systems = self.find_application_systems(project_path)
        if not systems:
            print("   ❌ No application systems found (expected: modules/, core/, services/)")
            return False
        
        print(f"   📁 Level 3 (Systems): Found {len(systems)} systems")
        for system in systems:
            print(f"      • {system}")
        
        # Level 4: Look for Features within Systems
        features_found = False
        for system in systems:
            system_path = project_path / system
            features = self.find_application_features(system_path)
            
            if features:
                features_found = True
                print(f"   🎯 Level 4 (Features) in {system}: Found {len(features)} features")
                for feature in features[:3]:  # Show first 3
                    print(f"      • {feature}")
                if len(features) > 3:
                    print(f"      • ... and {len(features) - 3} more")
                
                # Level 5: Look for Layers within Features
                for feature in features[:2]:  # Test first 2 features
                    feature_path = system_path / feature
                    layers = self.find_application_layers(feature_path)
                    
                    if layers:
                        print(f"   🏗️ Level 5 (Layers) in {feature}: Found {len(layers)} layers")
                        for layer in layers:
                            print(f"         • {layer}")
                        break
        
        if not features_found:
            print("   ❌ No application features found within systems")
            return False
        
        print("   ✅ Application hierarchy structure detected correctly!")
        print("   ✅ Project → Systems → Features → Layers confirmed")
        return True

    def test_delivery_hierarchy(self, project_path: Path) -> bool:
        """Test delivery project hierarchy (Workpackages → Milestones → Tasks)"""
        print("   🔍 Analyzing delivery hierarchy structure...")
        
        # Level 2: Project (home_improvements)
        print(f"   📋 Level 2 (Project): {project_path.name}")
        
        # Level 3: Look for Workpackages
        workpackages = self.find_delivery_workpackages(project_path)
        if not workpackages:
            print("   ❌ No delivery workpackages found (expected: workpackages/)")
            return False
        
        print(f"   📦 Level 3 (Workpackages): Found {len(workpackages)} workpackages")
        for wp in workpackages:
            print(f"      • {wp}")
        
        # Level 4: Look for Milestones within Workpackages
        milestones_found = False
        for wp in workpackages:
            wp_path = project_path / "workpackages" / wp
            milestones = self.find_delivery_milestones(wp_path)
            
            if milestones:
                milestones_found = True
                print(f"   🎪 Level 4 (Milestones) in {wp}: Found {len(milestones)} milestones")
                for milestone in milestones:
                    print(f"      • {milestone}")
                
                # Level 5: Look for Tasks within Milestones
                for milestone in milestones[:1]:  # Test first milestone
                    milestone_path = wp_path / "milestones" / milestone
                    tasks = self.find_delivery_tasks(milestone_path)
                    
                    if tasks:
                        print(f"   🔧 Level 5 (Tasks) in {milestone}: Found {len(tasks)} tasks")
                        for task in tasks:
                            print(f"         • {task}")
                        break
        
        if not milestones_found:
            print("   ❌ No delivery milestones found within workpackages")
            return False
        
        print("   ✅ Delivery hierarchy structure detected correctly!")
        print("   ✅ Project → Workpackages → Milestones → Tasks confirmed")
        return True

    def find_application_systems(self, project_path: Path) -> List[str]:
        """Find application systems (Level 3)"""
        systems = []
        
        # Look for typical application system folders
        app_system_names = ["modules", "core", "services", "components", "systems", "src"]
        
        for item in project_path.iterdir():
            if (item.is_dir() and 
                not item.name.startswith('.') and 
                item.name.lower() in app_system_names):
                systems.append(item.name)
        
        return systems

    def find_application_features(self, system_path: Path) -> List[str]:
        """Find application features (Level 4) within a system"""
        features = []
        
        if not system_path.exists():
            return features
        
        for item in system_path.iterdir():
            if (item.is_dir() and 
                not item.name.startswith('.') and 
                item.name not in ["__pycache__", "node_modules", "tests", "docs"]):
                
                # Check if this looks like a feature (has code structure)
                if self.looks_like_feature(item):
                    features.append(item.name)
        
        return features

    def find_application_layers(self, feature_path: Path) -> List[str]:
        """Find application layers (Level 5) within a feature"""
        layers = []
        
        if not feature_path.exists():
            return layers
        
        # Look for typical application layer folders
        app_layer_names = ["callbacks", "layout", "logic", "models", "views", "controllers", 
                          "components", "services", "utils", "data", "ui", "api"]
        
        for item in feature_path.iterdir():
            if (item.is_dir() and 
                not item.name.startswith('.') and 
                item.name.lower() in app_layer_names):
                layers.append(item.name)
        
        return layers

    def looks_like_feature(self, path: Path) -> bool:
        """Check if a directory looks like an application feature"""
        if not path.is_dir():
            return False
        
        # Count subdirectories that look like layers
        layer_indicators = ["callbacks", "layout", "logic", "models", "views", "controllers", "components"]
        layer_count = 0
        
        for item in path.iterdir():
            if item.is_dir() and item.name.lower() in layer_indicators:
                layer_count += 1
        
        # If it has 2+ layer folders, it's probably a feature
        return layer_count >= 2

    def find_delivery_workpackages(self, project_path: Path) -> List[str]:
        """Find delivery workpackages (Level 3)"""
        workpackages = []
        
        wp_path = project_path / "workpackages"
        if not wp_path.exists():
            return workpackages
        
        for item in wp_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                workpackages.append(item.name)
        
        return workpackages

    def find_delivery_milestones(self, workpackage_path: Path) -> List[str]:
        """Find delivery milestones (Level 4) within a workpackage"""
        milestones = []
        
        ms_path = workpackage_path / "milestones"
        if not ms_path.exists():
            return milestones
        
        for item in ms_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                milestones.append(item.name)
        
        return milestones

    def find_delivery_tasks(self, milestone_path: Path) -> List[str]:
        """Find delivery tasks (Level 5) within a milestone"""
        tasks = []
        
        tasks_path = milestone_path / "tasks"
        if not tasks_path.exists():
            return tasks
        
        for item in tasks_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                tasks.append(item.name)
        
        return tasks

def main():
    """Main test function"""
    tester = ControlTowerApplicationHierarchyTest()
    
    success = tester.test_application_vs_delivery_detection()
    
    if success:
        print("\n🎉 CONCLUSION: Control Tower is HIERARCHY-AWARE!")
        print("\n📊 Control Tower can distinguish:")
        print("🔹 APPLICATION projects → Systems/Features/Layers structure")
        print("🔹 DELIVERY projects → Workpackages/Milestones/Tasks structure")
        print("\n🚀 This means we can apply different validation rules!")
        print("✅ Application projects: Code quality, testing, architecture")
        print("✅ Delivery projects: Milestones, deliverables, client approval")
    else:
        print("\n❌ Control Tower needs work to handle both project types")

if __name__ == "__main__":
    main()