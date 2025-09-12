#!/usr/bin/env python3
"""
Hierarchy Restructuring Implementation Tool

This tool implements the hierarchy restructuring plans to establish consistent
requirements management structure across all repositories.

Priority: Start with home_improvements as pilot project.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class HierarchyRestructuringImplementer:
    def __init__(self, base_path: str = "/workspaces/control_tower"):
        self.base_path = Path(base_path)
        self.cloned_repos_path = self.base_path / "cloned_repos"
        self.backup_path = self.base_path / "backups" / "pre_restructuring"
        
        # Ensure backup directory exists
        self.backup_path.mkdir(parents=True, exist_ok=True)

    def restructure_home_improvements(self) -> bool:
        """Restructure home_improvements project as pilot implementation"""
        print("🏠 Restructuring home_improvements project...")
        print("=" * 60)
        
        project_path = self.cloned_repos_path / "life_quality" / "home_improvements"
        
        if not project_path.exists():
            print(f"❌ ERROR: home_improvements project not found at {project_path}")
            return False
        
        # Step 1: Create backup
        if not self.create_backup(project_path):
            return False
        
        # Step 2: Analyze current structure
        current_areas = self.analyze_current_renovation_areas(project_path)
        print(f"📋 Found renovation areas: {current_areas}")
        
        # Step 3: Create new structure
        if not self.create_new_home_improvements_structure(project_path, current_areas):
            return False
        
        # Step 4: Migrate content
        if not self.migrate_home_improvements_content(project_path, current_areas):
            return False
        
        print("✅ home_improvements restructuring completed successfully!")
        return True

    def create_backup(self, project_path: Path) -> bool:
        """Create backup of current project structure"""
        backup_name = f"{project_path.parent.name}_{project_path.name}_backup"
        backup_target = self.backup_path / backup_name
        
        try:
            if backup_target.exists():
                shutil.rmtree(backup_target)
            
            shutil.copytree(project_path, backup_target)
            print(f"📦 Backup created: {backup_target}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

    def analyze_current_renovation_areas(self, project_path: Path) -> List[str]:
        """Analyze current renovation areas in the project"""
        areas = []
        
        # Look in projects/Home_Projects/ for current areas
        home_projects_path = project_path / "projects" / "Home_Projects"
        
        if home_projects_path.exists():
            for item in home_projects_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Clean up the name
                    area_name = item.name.replace("_", " ").replace("-", " ").title()
                    area_name = area_name.replace("A ", "").replace("B ", "").replace("C ", "")
                    areas.append(area_name.strip())
        
        return areas

    def create_new_home_improvements_structure(self, project_path: Path, renovation_areas: List[str]) -> bool:
        """Create the new consistent hierarchy structure"""
        print("🏗️ Creating new hierarchy structure...")
        
        try:
            # Create project-level requirements folder
            requirements_path = project_path / "requirements"
            requirements_path.mkdir(exist_ok=True)
            
            # Create project-level requirements file
            self.create_project_requirements_file(requirements_path, renovation_areas)
            
            # Create workpackages folder
            workpackages_path = project_path / "workpackages"
            workpackages_path.mkdir(exist_ok=True)
            
            # Create each renovation area as a workpackage
            for area in renovation_areas:
                area_folder_name = area.lower().replace(" ", "_")
                self.create_workpackage_structure(workpackages_path, area_folder_name, area)
            
            print(f"   ✅ Created structure for {len(renovation_areas)} workpackages")
            return True
            
        except Exception as e:
            print(f"❌ Structure creation failed: {e}")
            return False

    def create_project_requirements_file(self, requirements_path: Path, renovation_areas: List[str]):
        """Create project-level requirements file"""
        content = f"""# Home Improvements Project Requirements

**Project Level**: Level 2 (Project)
**Project Type**: Delivery Project
**Generated**: September 12, 2025

## 📋 Project Overview
This project manages home improvement initiatives across multiple renovation areas.

## 🎯 Project Success Criteria
- [ ] All renovation areas completed to specification
- [ ] Budget maintained within approved limits
- [ ] Quality standards met for all workpackages
- [ ] Timeline adherence across all milestones
- [ ] Client satisfaction ≥ 95%

## 📦 Workpackages (Level 3)
"""
        
        for area in renovation_areas:
            area_folder = area.lower().replace(" ", "_")
            content += f"- **{area}** (`workpackages/{area_folder}/`)\n"
        
        content += f"""
## 🔗 Requirements Traceability
- **Parent**: life_quality (North Star Domain)
- **Children**: {len(renovation_areas)} workpackages
- **Template**: project_delivery_template.md

## 📊 Success Metrics
- **Budget Performance**: Target ±5% of approved budget
- **Schedule Performance**: Target 100% on-time milestone delivery
- **Quality Performance**: Target ≥95% client satisfaction
- **Scope Performance**: Target 100% deliverable acceptance

## 🔄 Requirements Cascade
Each workpackage inherits these project requirements and cascades to:
1. **Milestone Requirements** (Level 4)
2. **Task Requirements** (Level 5)
3. **Component Requirements** (Level 6)
"""
        
        with open(requirements_path / "project_requirements.md", 'w') as f:
            f.write(content)

    def create_workpackage_structure(self, workpackages_path: Path, folder_name: str, display_name: str):
        """Create complete workpackage structure with milestones and tasks"""
        
        # Create workpackage folder
        wp_path = workpackages_path / folder_name
        wp_path.mkdir(exist_ok=True)
        
        # Create workpackage requirements
        wp_req_path = wp_path / "requirements"
        wp_req_path.mkdir(exist_ok=True)
        self.create_workpackage_requirements_file(wp_req_path, display_name)
        
        # Create milestones folder
        milestones_path = wp_path / "milestones"
        milestones_path.mkdir(exist_ok=True)
        
        # Create standard milestones for renovation projects
        standard_milestones = [
            ("planning_complete", "Planning Complete"),
            ("materials_procured", "Materials Procured"),
            ("work_completed", "Work Completed")
        ]
        
        for milestone_folder, milestone_name in standard_milestones:
            self.create_milestone_structure(milestones_path, milestone_folder, milestone_name, display_name)

    def create_workpackage_requirements_file(self, requirements_path: Path, workpackage_name: str):
        """Create workpackage-level requirements file"""
        content = f"""# {workpackage_name} Workpackage Requirements

**Workpackage Level**: Level 3 (Workpackage)
**Project Type**: Delivery Project
**Parent Project**: home_improvements
**Generated**: September 12, 2025

## 📋 Workpackage Overview
This workpackage manages the complete {workpackage_name.lower()} renovation process.

## 🎯 Workpackage Success Criteria
- [ ] All milestones completed on schedule
- [ ] Quality standards met for all deliverables
- [ ] Budget maintained within workpackage allocation
- [ ] Client approval obtained for all phases
- [ ] Handover documentation complete

## 🎪 Milestones (Level 4)
- **Planning Complete** (`milestones/planning_complete/`)
- **Materials Procured** (`milestones/materials_procured/`)
- **Work Completed** (`milestones/work_completed/`)

## 🔗 Requirements Traceability
- **Parent**: home_improvements project
- **Children**: 3 milestones
- **Template**: workpackage_delivery_template.md

## 📊 Success Metrics
- **Timeline Performance**: All milestones ±2 days of plan
- **Quality Gates**: 100% quality checkpoints passed
- **Budget Performance**: Within ±10% of workpackage budget
- **Client Engagement**: ≥2 client reviews per milestone

## 🔄 Requirements Cascade
This workpackage cascades requirements to:
1. **Milestone Requirements** (Level 4)
2. **Task Requirements** (Level 5)
3. **Component Requirements** (Level 6)
"""
        
        with open(requirements_path / "workpackage_requirements.md", 'w') as f:
            f.write(content)

    def create_milestone_structure(self, milestones_path: Path, folder_name: str, milestone_name: str, workpackage_name: str):
        """Create complete milestone structure with tasks"""
        
        # Create milestone folder
        milestone_path = milestones_path / folder_name
        milestone_path.mkdir(exist_ok=True)
        
        # Create milestone requirements
        ms_req_path = milestone_path / "requirements"
        ms_req_path.mkdir(exist_ok=True)
        self.create_milestone_requirements_file(ms_req_path, milestone_name, workpackage_name)
        
        # Create tasks folder
        tasks_path = milestone_path / "tasks"
        tasks_path.mkdir(exist_ok=True)
        
        # Create milestone-specific tasks
        if folder_name == "planning_complete":
            tasks = ["design_approval", "permits_obtained", "contractor_selected"]
        elif folder_name == "materials_procured":
            tasks = ["material_selection", "supplier_coordination", "delivery_scheduled"]
        elif folder_name == "work_completed":
            tasks = ["construction_work", "quality_inspection", "final_approval"]
        else:
            tasks = ["task_1", "task_2", "task_3"]
        
        for task in tasks:
            self.create_task_structure(tasks_path, task, milestone_name, workpackage_name)

    def create_milestone_requirements_file(self, requirements_path: Path, milestone_name: str, workpackage_name: str):
        """Create milestone-level requirements file"""
        content = f"""# {milestone_name} Milestone Requirements

**Milestone Level**: Level 4 (Milestone)
**Project Type**: Delivery Project
**Parent Workpackage**: {workpackage_name}
**Generated**: September 12, 2025

## 📋 Milestone Overview
This milestone represents the completion of {milestone_name.lower()} phase for {workpackage_name.lower()}.

## 🎯 Milestone Success Criteria
- [ ] All tasks completed to specification
- [ ] Quality assessment passed
- [ ] Client approval obtained
- [ ] Documentation completed
- [ ] Handover to next milestone ready

## 🔗 Requirements Traceability
- **Parent**: {workpackage_name} workpackage
- **Children**: Multiple tasks (Level 5)
- **Template**: milestone_delivery_template.md

## 📊 Success Metrics
- **Task Completion**: 100% of assigned tasks completed
- **Quality Score**: ≥8/10 on quality assessment
- **Review Efficiency**: ≤3 review cycles to approval
- **Approval Rate**: 100% stakeholder sign-off
- **Documentation**: 100% required documentation complete

## 🔄 Requirements Cascade
This milestone cascades requirements to:
1. **Task Requirements** (Level 5)
2. **Component Requirements** (Level 6)
"""
        
        with open(requirements_path / "milestone_requirements.md", 'w') as f:
            f.write(content)

    def create_task_structure(self, tasks_path: Path, task_name: str, milestone_name: str, workpackage_name: str):
        """Create individual task folder with requirements"""
        
        # Create task folder
        task_path = tasks_path / task_name
        task_path.mkdir(exist_ok=True)
        
        # Create task requirements file
        self.create_task_requirements_file(task_path, task_name, milestone_name, workpackage_name)

    def create_task_requirements_file(self, task_path: Path, task_name: str, milestone_name: str, workpackage_name: str):
        """Create task-level requirements file"""
        task_display = task_name.replace("_", " ").title()
        
        content = f"""# {task_display} Task Requirements

**Task Level**: Level 5 (Task)
**Project Type**: Delivery Project
**Parent Milestone**: {milestone_name}
**Parent Workpackage**: {workpackage_name}
**Generated**: September 12, 2025

## 📋 Task Overview
This task implements {task_display.lower()} as part of {milestone_name.lower()}.

## 🎯 Task Success Criteria
- [ ] Output specification met 100%
- [ ] Quality standards satisfied
- [ ] Time performance within ±20% of estimate
- [ ] Resource usage within budget
- [ ] Integration with related work successful

## 🔗 Requirements Traceability
- **Parent**: {milestone_name} milestone
- **Template**: task_delivery_template.md

## 📊 Success Metrics
- **Output Compliance**: 100% specification compliance
- **Quality Standards**: All quality criteria met
- **Time Performance**: Within ±20% of estimated time
- **Resource Efficiency**: Within allocated resource budget
- **Integration Success**: Successful integration verification

## ✅ Completion Checklist
- [ ] All specified outputs produced
- [ ] Quality verification completed
- [ ] Integration testing passed
- [ ] Documentation updated
- [ ] Handover completed
"""
        
        with open(task_path / "task_requirements.md", 'w') as f:
            f.write(content)

    def migrate_home_improvements_content(self, project_path: Path, renovation_areas: List[str]) -> bool:
        """Migrate existing content to new structure"""
        print("📦 Migrating existing content...")
        
        try:
            # Move any existing project files to appropriate locations
            old_projects_path = project_path / "projects"
            
            if old_projects_path.exists():
                # Archive the old structure
                archive_path = project_path / "archive_old_structure"
                if archive_path.exists():
                    shutil.rmtree(archive_path)
                shutil.move(str(old_projects_path), str(archive_path))
                print(f"   📁 Archived old structure to: {archive_path}")
            
            # Move other existing files to archive if they don't fit new structure
            items_to_archive = ["powerpoint_reports", "xml_workspace"]
            
            for item_name in items_to_archive:
                item_path = project_path / item_name
                if item_path.exists():
                    archive_item_path = project_path / "archive_old_structure" / item_name
                    archive_item_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item_path), str(archive_item_path))
                    print(f"   📁 Archived {item_name}")
            
            print("   ✅ Content migration completed")
            return True
            
        except Exception as e:
            print(f"❌ Content migration failed: {e}")
            return False

def main():
    """Main restructuring implementation"""
    implementer = HierarchyRestructuringImplementer()
    
    print("🔧 HIERARCHY RESTRUCTURING IMPLEMENTATION")
    print("=" * 60)
    print("Starting with home_improvements as pilot project...")
    print()
    
    success = implementer.restructure_home_improvements()
    
    if success:
        print("\n✅ RESTRUCTURING COMPLETED SUCCESSFULLY!")
        print("🎯 home_improvements now has consistent requirements hierarchy")
        print("📋 Each level has proper requirements/ folders")
        print("🔗 Requirements can now cascade properly through all levels")
        print("\nNext steps:")
        print("1. Validate requirements management works correctly")
        print("2. Apply same restructuring to other projects")
        print("3. Update Control Tower to use new structure")
    else:
        print("\n❌ RESTRUCTURING FAILED!")
        print("Check error messages above and retry")

if __name__ == "__main__":
    main()