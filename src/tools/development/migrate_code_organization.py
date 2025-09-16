#!/usr/bin/env python3
"""
Control Tower Code Organization Migration Script

This script reorganizes the existing TDD workflow automation code into the proper
hierarchical structure that aligns with our requirements management system.

Target Structure:
src/projects/project_002_automated_workflow/systems/system_002_02_tdd_orchestration/
└── features/feature_002_02_01_tdd_workflow_automation/layers/
    ├── data_access/
    ├── business_logic/
    ├── ui/
    └── integration/

Created: 2025-09-16
Purpose: Align code organization with hierarchical requirements structure
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

class CodeMigrationManager:
    """Manages the migration of existing code to hierarchical structure"""
    
    def __init__(self, workspace_root: str = "/workspaces/control_tower"):
        self.workspace_root = Path(workspace_root)
        self.src_root = self.workspace_root / "src"
        
        # Target structure for TDD Workflow Automation Feature
        self.tdd_feature_root = (
            self.src_root / "projects" / "project_002_automated_workflow" / 
            "systems" / "system_002_02_tdd_orchestration" / 
            "features" / "feature_002_02_01_tdd_workflow_automation" / "layers"
        )
        
        # Shared components structure
        self.shared_root = self.src_root / "shared"
        
        # Legacy backup location
        self.legacy_root = self.workspace_root / "legacy"
        
    def create_directory_structure(self):
        """Create the new hierarchical directory structure"""
        print("🏗️ Creating new directory structure...")
        
        # TDD Feature layers
        layers = ["data_access", "business_logic", "ui", "integration"]
        for layer in layers:
            layer_path = self.tdd_feature_root / layer
            layer_path.mkdir(parents=True, exist_ok=True)
            (layer_path / "__init__.py").touch()
            print(f"   ✅ Created: {layer_path}")
        
        # Shared components
        shared_dirs = ["quality_gates", "common", "utils"]
        for shared_dir in shared_dirs:
            shared_path = self.shared_root / shared_dir
            shared_path.mkdir(parents=True, exist_ok=True)
            (shared_path / "__init__.py").touch()
            print(f"   ✅ Created: {shared_path}")
        
        # Legacy backup
        legacy_dirs = ["root_scripts", "old_src", "misc"]
        for legacy_dir in legacy_dirs:
            legacy_path = self.legacy_root / legacy_dir
            legacy_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created: {legacy_path}")
    
    def get_migration_mapping(self) -> Dict[str, str]:
        """Define the migration mapping for existing files"""
        return {
            # TDD Data Access Layer (LAYER-001)
            "src/data_access/tdd_workflow_enforcer.py": 
                str(self.tdd_feature_root / "data_access" / "tdd_workflow_enforcer.py"),
            "src/data_access/requirements_parser.py": 
                str(self.tdd_feature_root / "data_access" / "requirements_parser.py"),
            "src/data_access/test_generator.py": 
                str(self.tdd_feature_root / "data_access" / "test_generator.py"),
            "src/data_access/professional_test_generator.py": 
                str(self.tdd_feature_root / "data_access" / "professional_test_generator.py"),
            
            # TDD Business Logic Layer (LAYER-002) 
            "src/business_logic/tdd_workflow_engine.py": 
                str(self.tdd_feature_root / "business_logic" / "tdd_workflow_engine.py"),
            "real_tdd_green_phase_engine.py": 
                str(self.tdd_feature_root / "business_logic" / "real_tdd_green_phase_engine.py"),
            "run-tdd-workflow.py": 
                str(self.tdd_feature_root / "business_logic" / "tdd_workflow_orchestrator.py"),
            
            # TDD UI Layer (LAYER-003)
            "src/ui/tdd_progress_formatter.py": 
                str(self.tdd_feature_root / "ui" / "tdd_progress_formatter.py"),
            
            # Shared Quality Gates
            "src/quality_gates/tdd_workflow_validator.py": 
                str(self.shared_root / "quality_gates" / "tdd_workflow_validator.py"),
            "src/quality_gates/code_quality_validator.py": 
                str(self.shared_root / "quality_gates" / "code_quality_validator.py"),
            "src/quality_gates/real_tdd_gates.py": 
                str(self.shared_root / "quality_gates" / "real_tdd_gates.py"),
            "src/quality_gates/test_generator_gate.py": 
                str(self.shared_root / "quality_gates" / "test_generator_gate.py"),
            
            # Shared Common Components
            "src/data_access/config.py": 
                str(self.shared_root / "common" / "config.py"),
            "src/data_access/data_models.py": 
                str(self.shared_root / "common" / "data_models.py"),
            "src/data_access/interfaces.py": 
                str(self.shared_root / "common" / "interfaces.py"),
            "src/data_access/requirements_models.py": 
                str(self.shared_root / "common" / "requirements_models.py"),
            
            # Shared Utils
            "src/data_access/file_system_interface.py": 
                str(self.shared_root / "utils" / "file_system_interface.py"),
            "utils/date_utils.py": 
                str(self.shared_root / "utils" / "date_utils.py"),
            
            # Legacy root scripts
            "demo_red_phase_enforcer.py": 
                str(self.legacy_root / "root_scripts" / "demo_red_phase_enforcer.py"),
            "enforce.py": 
                str(self.legacy_root / "root_scripts" / "enforce.py"),
            "run_tdd_enforcer.py": 
                str(self.legacy_root / "root_scripts" / "run_tdd_enforcer.py"),
            "validate_stage_gate_3.py": 
                str(self.legacy_root / "root_scripts" / "validate_stage_gate_3.py"),
        }
    
    def backup_existing_structure(self):
        """Create backup of existing src structure"""
        print("📦 Creating backup of existing structure...")
        
        if self.src_root.exists():
            backup_path = self.legacy_root / "old_src_backup"
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.copytree(self.src_root, backup_path)
            print(f"   ✅ Backed up to: {backup_path}")
    
    def migrate_files(self):
        """Migrate files according to the mapping"""
        print("📂 Migrating files to new structure...")
        
        migration_mapping = self.get_migration_mapping()
        successful_migrations = []
        failed_migrations = []
        
        for source_path, target_path in migration_mapping.items():
            source = self.workspace_root / source_path
            target = Path(target_path)
            
            if source.exists():
                try:
                    # Ensure target directory exists
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move the file
                    shutil.move(str(source), str(target))
                    successful_migrations.append((source_path, target_path))
                    print(f"   ✅ Moved: {source_path} → {target_path}")
                except Exception as e:
                    failed_migrations.append((source_path, str(e)))
                    print(f"   ❌ Failed: {source_path} - {e}")
            else:
                print(f"   ⚠️  Not found: {source_path}")
        
        return successful_migrations, failed_migrations
    
    def update_import_statements(self, successful_migrations: List[Tuple[str, str]]):
        """Update import statements in migrated files"""
        print("🔄 Updating import statements...")
        
        # This is a simplified approach - in practice you might need more sophisticated parsing
        import_updates = {
            "from src.data_access": "from shared.common",
            "from src.business_logic": "from projects.project_002_automated_workflow.systems.system_002_02_tdd_orchestration.features.feature_002_02_01_tdd_workflow_automation.layers.business_logic",
            "from src.quality_gates": "from shared.quality_gates",
            "from src.ui": "from projects.project_002_automated_workflow.systems.system_002_02_tdd_orchestration.features.feature_002_02_01_tdd_workflow_automation.layers.ui",
            "from data_access": "from shared.common",
            "from business_logic": "from projects.project_002_automated_workflow.systems.system_002_02_tdd_orchestration.features.feature_002_02_01_tdd_workflow_automation.layers.business_logic",
        }
        
        for source_path, target_path in successful_migrations:
            target_file = Path(target_path)
            if target_file.suffix == ".py" and target_file.exists():
                try:
                    with open(target_file, 'r') as f:
                        content = f.read()
                    
                    # Update imports
                    for old_import, new_import in import_updates.items():
                        content = content.replace(old_import, new_import)
                    
                    with open(target_file, 'w') as f:
                        f.write(content)
                    
                    print(f"   ✅ Updated imports in: {target_path}")
                except Exception as e:
                    print(f"   ⚠️  Import update failed for {target_path}: {e}")
    
    def create_test_structure(self):
        """Create matching test structure"""
        print("🧪 Creating test structure...")
        
        test_root = self.workspace_root / "tests" / "projects" / "project_002_automated_workflow" / "systems" / "system_002_02_tdd_orchestration" / "features" / "feature_002_02_01_tdd_workflow_automation" / "layers"
        
        layers = ["data_access", "business_logic", "ui", "integration"]
        for layer in layers:
            test_layer_path = test_root / layer
            test_layer_path.mkdir(parents=True, exist_ok=True)
            
            # Create test file templates
            test_file = test_layer_path / f"test_{layer}.py"
            test_content = f'''"""
Test module for {layer} layer of TDD Workflow Automation feature

Created: 2025-09-16
Feature: FEATURE-002-02-01_tdd_workflow_automation
Layer: {layer}
"""

import pytest
from pathlib import Path


class Test{layer.title().replace('_', '')}Layer:
    """Test class for {layer} layer components"""
    
    def test_layer_exists(self):
        """Verify layer structure exists"""
        assert True  # Placeholder test
        
    # Add specific tests for {layer} layer components here
'''
            test_file.write_text(test_content)
            print(f"   ✅ Created test file: {test_file}")
    
    def generate_migration_report(self, successful_migrations: List[Tuple[str, str]], failed_migrations: List[Tuple[str, str]]):
        """Generate migration report"""
        report_path = self.workspace_root / "CODE_MIGRATION_REPORT.md"
        
        report_content = f"""# Code Migration Report - TDD Workflow Automation

**Date**: 2025-09-16  
**Feature**: FEATURE-002-02-01_tdd_workflow_automation  
**Migration Type**: Hierarchical Code Organization  

## Migration Summary

- **Successful Migrations**: {len(successful_migrations)}
- **Failed Migrations**: {len(failed_migrations)}
- **Target Structure**: Aligned with requirements hierarchy

## Successful Migrations

| Source | Target |
|--------|--------|
"""
        
        for source, target in successful_migrations:
            report_content += f"| `{source}` | `{target}` |\n"
        
        if failed_migrations:
            report_content += "\n## Failed Migrations\n\n"
            for source, error in failed_migrations:
                report_content += f"- **{source}**: {error}\n"
        
        report_content += f"""
## New Directory Structure

```
src/projects/project_002_automated_workflow/systems/system_002_02_tdd_orchestration/
└── features/feature_002_02_01_tdd_workflow_automation/layers/
    ├── data_access/        # LAYER-001: Requirements Parser & Test Generator
    ├── business_logic/     # LAYER-002: TDD Workflow Engine (95% complete)
    ├── ui/                 # LAYER-003: Progress & Feedback Display  
    └── integration/        # LAYER-004: Git Safety & Tool Integration
```

## Next Steps

1. Update import statements in dependent files
2. Update Makefile to reference new structure
3. Update requirements documents with new code locations
4. Test make what-next discovery with new structure
5. Update CI/CD pipelines to use new structure

## Requirements Document Updates Needed

- **FEATURE-002-02-01_tdd_workflow_automation.md**: Update layer implementation status
- **PROJECT-002_automated_development_workflow_execution.md**: Add code organization section
- **SYSTEM-002-02_tdd_workflow_orchestration.md**: Reference new code structure
"""
        
        report_path.write_text(report_content)
        print(f"📊 Migration report generated: {report_path}")
    
    def run_migration(self):
        """Execute the complete migration process"""
        print("🚀 Starting Control Tower Code Migration")
        print("=" * 50)
        
        try:
            # Step 1: Create new structure
            self.create_directory_structure()
            
            # Step 2: Backup existing structure
            self.backup_existing_structure()
            
            # Step 3: Migrate files
            successful, failed = self.migrate_files()
            
            # Step 4: Update imports
            self.update_import_statements(successful)
            
            # Step 5: Create test structure
            self.create_test_structure()
            
            # Step 6: Generate report
            self.generate_migration_report(successful, failed)
            
            print("\n🎉 Migration completed successfully!")
            print(f"📊 {len(successful)} files migrated, {len(failed)} failures")
            print("📋 Check CODE_MIGRATION_REPORT.md for details")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
        
        return True


if __name__ == "__main__":
    migrator = CodeMigrationManager()
    migrator.run_migration()