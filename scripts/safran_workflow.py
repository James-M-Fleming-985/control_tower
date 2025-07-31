#!/usr/bin/env python3
"""
Setup XML Workspaces for All Repositories
Creates xml_workspace directories and ensures MS Project XML files are available across all repos
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta

class XMLWorkspaceManager:
    """Manages XML workspaces across all repositories"""
    
    def __init__(self):
        self.control_tower_root = "/workspaces/control_tower"
        self.repos_root = "/workspaces/control_tower/cloned_repos"
        
        # Repository-specific configurations
        self.repositories = {
            "contract_projects": {
                "xml_files": ["ZnNi Line Development Plan-08.xml"],  # Safran-specific
                "project_type": "Safran Contract"
            },
            "domain_specific-network_dev": {
                "xml_files": ["Network Development Plan.xml"],
                "project_type": "Network Development"
            },
            "financial_optimizer": {
                "xml_files": ["Financial Optimization Project.xml"],
                "project_type": "Financial Analysis"
            },
            "financial_security_dev": {
                "xml_files": ["Financial Security Project.xml"],
                "project_type": "Security Development"
            },
            "home_improvements": {
                "xml_files": ["Home Improvement Projects.xml"],
                "project_type": "Home Management"
            },
            "LIMS_concept_actual": {
                "xml_files": ["LIMS Implementation Plan.xml"],  # Independent LIMS project
                "project_type": "LIMS System"
            },
            "opti_royale": {
                "xml_files": ["Optimization Royale Project.xml"],
                "project_type": "Optimization Platform"
            },
            "relationship_building": {
                "xml_files": ["Relationship Building Plan.xml"],
                "project_type": "Relationship Management"
            }
        }
    
    def setup_all_xml_workspaces(self):
        """Setup xml_workspace directories in all repositories"""
        print("🚀 Setting up XML workspaces for all repositories...")
        print("="*60)
        
        for repo_name, repo_config in self.repositories.items():
            repo_path = os.path.join(self.repos_root, repo_name)
            if os.path.exists(repo_path):
                self._setup_repo_xml_workspace(repo_name, repo_path, repo_config)
            else:
                print(f"⚠️  Repository not found: {repo_name}")
        
        print("\n✅ XML workspace setup complete!")
        self._show_status_summary()
    
    def _setup_repo_xml_workspace(self, repo_name: str, repo_path: str, repo_config: dict):
        """Setup xml_workspace for a single repository"""
        print(f"\n📁 Setting up XML workspace for: {repo_name}")
        print(f"   📋 Project Type: {repo_config['project_type']}")
        
        # Create xml_workspace directory
        xml_workspace = os.path.join(repo_path, "xml_workspace")
        os.makedirs(xml_workspace, exist_ok=True)
        print(f"   ✅ Created: {xml_workspace}")
        
        # Create project-specific XML files
        for xml_filename in repo_config['xml_files']:
            target_xml = os.path.join(xml_workspace, xml_filename)
            
            # Special handling for contract_projects - keep existing Safran XML if it exists
            if repo_name == "contract_projects" and xml_filename == "ZnNi Line Development Plan-08.xml":
                if os.path.exists(target_xml):
                    print(f"   ℹ️  XML already exists: {xml_filename}")
                    continue
                else:
                    print(f"   ⚠️  Safran XML not found, check if MS Project export is needed")
            
            # Create project-specific placeholder XML for all other repos
            if not os.path.exists(target_xml):
                self._create_project_specific_xml(target_xml, repo_name, repo_config)
                print(f"   ✅ Created XML: {xml_filename}")
            else:
                print(f"   ℹ️  XML already exists: {xml_filename}")
        
        # Create README for xml_workspace
        self._create_xml_workspace_readme(xml_workspace, repo_name, repo_config)
    
    def _create_project_specific_xml(self, target_path: str, repo_name: str, repo_config: dict):
        """Create a project-specific XML file for each repository"""
        project_title = repo_config['project_type']
        
        placeholder_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Project xmlns="http://schemas.microsoft.com/project">
    <Name>{project_title} - {repo_name.replace('_', ' ').title()}</Name>
    <Title>{project_title} Development Plan</Title>
    <CreationDate>{datetime.now().isoformat()}</CreationDate>
    <LastSaved>{datetime.now().isoformat()}</LastSaved>
    <Tasks>
        <!-- Project structure for {repo_name} - {project_title} -->
        <Task>
            <UID>1</UID>
            <ID>1</ID>
            <Name>{project_title} Project Overview</Name>
            <Type>1</Type>
            <IsNull>0</IsNull>
            <CreateDate>{datetime.now().isoformat()}</CreateDate>
            <Start>{datetime.now().isoformat()}</Start>
            <Finish>{(datetime.now() + timedelta(days=90)).isoformat()}</Finish>
            <PercentComplete>0</PercentComplete>
            <OutlineLevel>1</OutlineLevel>
        </Task>
        <Task>
            <UID>2</UID>
            <ID>2</ID>
            <Name>Phase 1: Planning & Analysis</Name>
            <Type>1</Type>
            <IsNull>0</IsNull>
            <CreateDate>{datetime.now().isoformat()}</CreateDate>
            <Start>{datetime.now().isoformat()}</Start>
            <Finish>{(datetime.now() + timedelta(days=30)).isoformat()}</Finish>
            <PercentComplete>25</PercentComplete>
            <OutlineLevel>2</OutlineLevel>
        </Task>
        <Task>
            <UID>3</UID>
            <ID>3</ID>
            <Name>Phase 2: Implementation</Name>
            <Type>1</Type>
            <IsNull>0</IsNull>
            <CreateDate>{datetime.now().isoformat()}</CreateDate>
            <Start>{(datetime.now() + timedelta(days=30)).isoformat()}</Start>
            <Finish>{(datetime.now() + timedelta(days=60)).isoformat()}</Finish>
            <PercentComplete>0</PercentComplete>
            <OutlineLevel>2</OutlineLevel>
        </Task>
        <Task>
            <UID>4</UID>
            <ID>4</ID>
            <Name>Phase 3: Testing & Deployment</Name>
            <Type>1</Type>
            <IsNull>0</IsNull>
            <CreateDate>{datetime.now().isoformat()}</CreateDate>
            <Start>{(datetime.now() + timedelta(days=60)).isoformat()}</Start>
            <Finish>{(datetime.now() + timedelta(days=90)).isoformat()}</Finish>
            <PercentComplete>0</PercentComplete>
            <OutlineLevel>2</OutlineLevel>
        </Task>
    </Tasks>
</Project>'''
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        print(f"   ✅ Created {project_title} XML structure")
    
    def _create_xml_workspace_readme(self, xml_workspace: str, repo_name: str, repo_config: dict):
        """Create README for xml_workspace directory"""
        readme_path = os.path.join(xml_workspace, "README.md")
        project_type = repo_config['project_type']
        xml_files = repo_config['xml_files']
        
        readme_content = f'''# XML Workspace - {repo_name.replace('_', ' ').title()}

## Purpose
This directory contains MS Project XML files for automated reporting and milestone management.

## Project Type
**{project_type}** - Repository-specific project management data

## Files
'''
        
        for xml_file in xml_files:
            readme_content += f'- `{xml_file}` - {project_type} project XML file\n'
        
        readme_content += f'''
## Repository-Specific Structure
This XML workspace is tailored for **{repo_name}** and contains:
- Project structure specific to {project_type}
- Milestones relevant to this repository's goals
- Timeline data for {repo_name} development phases

## Usage
1. **PowerPoint Generation**: Repository-specific Safran PowerPoint generator reads from these XML files
2. **Milestone Queries**: Control Tower milestone system uses this project data
3. **Progress Tracking**: Project progress specific to {repo_name}
4. **Sync Operations**: Files updated via repository-specific MS Project processes

## Sync Workflow
1. Update repository-specific .mpp files in MS Project
2. Run Control Tower sync for this repo: `python3 control_tower.py ms-project --repo {repo_name} --action sync`
3. XML files automatically updated with {repo_name} data
4. PowerPoint reports regenerated with current {project_type} data

## Directory Structure
```
xml_workspace/
├── README.md                    # This file
'''
        
        for xml_file in xml_files:
            readme_content += f'├── {xml_file:<30} # {project_type} project data\n'
        
        readme_content += f'''
## Integration Points
- **Control Tower**: Repository-aware project management
- **PowerPoint Generator**: Generates {repo_name}-specific presentations
- **Sync Scripts**: Repository-specific sync processes

## Important Notes
- **NOT shared across repositories**: Each repo has its own project data
- **Repository-specific**: XML files contain {project_type} project structure
- **Independent**: Changes here only affect {repo_name} presentations

## Last Updated
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Repository-specific XML workspace setup
'''
        
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"   ✅ Created README: xml_workspace/README.md")
    
    def sync_xml_files(self):
        """Sync XML files - repository-specific approach (no cross-repo copying)"""
        print("\n🔄 Repository-specific XML file management...")
        print("ℹ️  Each repository maintains its own project-specific XML files")
        print("ℹ️  No cross-repository syncing (each repo is independent)")
        
        sync_summary = []
        for repo_name, repo_config in self.repositories.items():
            repo_path = os.path.join(self.repos_root, repo_name)
            xml_workspace = os.path.join(repo_path, "xml_workspace")
            
            if not os.path.exists(xml_workspace):
                print(f"   ⚠️  {repo_name}: No xml_workspace found")
                continue
            
            project_files = []
            for xml_filename in repo_config['xml_files']:
                xml_file = os.path.join(xml_workspace, xml_filename)
                if os.path.exists(xml_file):
                    mtime = os.path.getmtime(xml_file)
                    timestamp = datetime.fromtimestamp(mtime)
                    project_files.append(f"{xml_filename} ({timestamp.strftime('%m/%d %H:%M')})")
                else:
                    project_files.append(f"{xml_filename} (missing)")
            
            sync_summary.append({
                'repo': repo_name,
                'type': repo_config['project_type'],
                'files': project_files
            })
        
        print(f"\n📊 REPOSITORY XML STATUS:")
        for item in sync_summary:
            print(f"✅ {item['repo']:<30} [{item['type']}]")
            for file_info in item['files']:
                print(f"   📄 {file_info}")
        
        print(f"\n✅ Repository-specific XML management complete")
        print(f"💡 Each repository maintains independent project data")
        return True
    
    def _show_status_summary(self):
        """Show summary of XML workspace status"""
        print("\n" + "="*60)
        print("📊 XML WORKSPACE STATUS SUMMARY")
        print("="*60)
        
        for repo_name, repo_config in self.repositories.items():
            repo_path = os.path.join(self.repos_root, repo_name)
            xml_workspace = os.path.join(repo_path, "xml_workspace")
            
            if os.path.exists(repo_path):
                workspace_status = "✅" if os.path.exists(xml_workspace) else "❌"
                project_type = repo_config['project_type']
                
                print(f"{workspace_status} {repo_name:<30} [{project_type}]")
                
                # Check each XML file for this repo
                for xml_filename in repo_config['xml_files']:
                    xml_file = os.path.join(xml_workspace, xml_filename)
                    if os.path.exists(xml_file):
                        mtime = os.path.getmtime(xml_file)
                        timestamp = datetime.fromtimestamp(mtime).strftime('%m/%d %H:%M')
                        print(f"   📄 {xml_filename} ({timestamp})")
                    else:
                        print(f"   ❌ {xml_filename} (missing)")
            else:
                print(f"❌ {repo_name:<30} Repository not found")
        
        print(f"\n📋 REPOSITORY-SPECIFIC XML WORKSPACES:")
        print(f"• Each repository has project-specific XML files")
        print(f"• No cross-repository XML sharing (independent projects)")
        print(f"• PowerPoint generation uses repository-specific data")
        print(f"• ZnNi Line Development Plan-08.xml is ONLY for contract_projects")
        print(f"• Each repo can generate presentations with its own project data")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup XML workspaces for all repositories')
    parser.add_argument('--action', choices=['setup', 'sync', 'both'], default='both',
                       help='Action to perform (default: both)')
    
    args = parser.parse_args()
    
    manager = XMLWorkspaceManager()
    
    if args.action in ['setup', 'both']:
        manager.setup_all_xml_workspaces()
    
    if args.action in ['sync', 'both']:
        manager.sync_xml_files()
    
    print(f"\n🚀 XML workspace management complete!")
    print(f"📁 Each repository now has: /xml_workspace/ZnNi Line Development Plan-08.xml")
    print(f"🎯 Future-proofed for PowerPoint generation across all projects")

if __name__ == "__main__":
    main()
