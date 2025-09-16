#!/usr/bin/env python3
"""
Repository Scanner for Control Tower
Discovers and manages MS Project XML files across all repositories

This scanner:
1. Finds all repositories in the Control Tower workspace
2. Locates MS Project XML files in each repository
3. Provides repository metadata and file management
4. Supports multi-project milestone management
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class RepositoryScanner:
    """
    Scans all Control Tower repositories for MS Project XML files
    """
    
    def __init__(self, base_path: str = "/workspaces/control_tower"):
        """
        Initialize the repository scanner
        
        Args:
            base_path: Base path to Control Tower workspace
        """
        self.base_path = Path(base_path)
        self.cloned_repos_path = self.base_path / "cloned_repos"
        self.xml_workspace_paths = [
            "xml_workspace",
            "project_files",
            "ms_project",
            "planning"
        ]
    
    def scan_all_repositories(self) -> Dict[str, Dict]:
        """
        Scan all repositories for MS Project XML files
        
        Returns:
            Dict mapping repository names to their XML file information
        """
        repositories = {}
        
        if not self.cloned_repos_path.exists():
            print(f"⚠️ Cloned repos directory not found: {self.cloned_repos_path}")
            return repositories
        
        print("🔍 Scanning all repositories for MS Project XML files...")
        
        # Scan each repository directory
        for repo_dir in self.cloned_repos_path.iterdir():
            if repo_dir.is_dir():
                repo_info = self._scan_repository(repo_dir)
                if repo_info['xml_files']:
                    repositories[repo_dir.name] = repo_info
        
        print(f"✅ Found XML files in {len(repositories)} repositories")
        return repositories
    
    def _scan_repository(self, repo_path: Path) -> Dict:
        """
        Scan a single repository for XML files
        
        Args:
            repo_path: Path to the repository directory
            
        Returns:
            Repository information dictionary
        """
        repo_info = {
            'path': str(repo_path),
            'name': repo_path.name,
            'xml_files': [],
            'xml_directories': [],
            'last_scanned': datetime.now()
        }
        
        # Look for XML files in common locations
        for xml_dir_name in self.xml_workspace_paths:
            xml_dir = repo_path / xml_dir_name
            if xml_dir.exists():
                repo_info['xml_directories'].append(str(xml_dir))
                xml_files = self._find_xml_files(xml_dir)
                repo_info['xml_files'].extend(xml_files)
        
        # Also search root directory and common subdirectories
        additional_paths = [
            repo_path,
            repo_path / "projects",
            repo_path / "planning",
            repo_path / "schedules"
        ]
        
        for search_path in additional_paths:
            if search_path.exists():
                xml_files = self._find_xml_files(search_path, recursive=False)
                repo_info['xml_files'].extend(xml_files)
        
        # Remove duplicates
        repo_info['xml_files'] = list(set(repo_info['xml_files']))
        
        return repo_info
    
    def _find_xml_files(self, directory: Path, recursive: bool = True) -> List[str]:
        """
        Find MS Project XML files in a directory
        
        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            
        Returns:
            List of XML file paths
        """
        xml_files = []
        
        try:
            # Search patterns for MS Project files
            patterns = [
                "*.xml",
                "*.mpp",  # Native MS Project format
                "*project*.xml",
                "*schedule*.xml",
                "*plan*.xml"
            ]
            
            for pattern in patterns:
                if recursive:
                    search_pattern = str(directory / "**" / pattern)
                    files = glob.glob(search_pattern, recursive=True)
                else:
                    search_pattern = str(directory / pattern)
                    files = glob.glob(search_pattern)
                
                # Filter for likely MS Project files
                for file_path in files:
                    if self._is_likely_ms_project_file(file_path):
                        xml_files.append(file_path)
        
        except Exception as e:
            print(f"⚠️ Error scanning {directory}: {e}")
        
        return xml_files
    
    def _is_likely_ms_project_file(self, file_path: str) -> bool:
        """
        Check if a file is likely an MS Project XML file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if likely an MS Project file
        """
        file_path = Path(file_path)
        
        # Check file extension
        if file_path.suffix.lower() not in ['.xml', '.mpp']:
            return False
        
        # Check file size (MS Project files are usually substantial)
        try:
            file_size = file_path.stat().st_size
            if file_size < 1000:  # Less than 1KB probably not a project file
                return False
        except:
            return False
        
        # Check filename patterns
        filename_lower = file_path.name.lower()
        ms_project_indicators = [
            'project', 'schedule', 'plan', 'timeline', 'milestone',
            'gantt', 'task', 'development', 'implementation'
        ]
        
        if any(indicator in filename_lower for indicator in ms_project_indicators):
            return True
        
        # For XML files, try to peek at content
        if file_path.suffix.lower() == '.xml':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_few_lines = f.read(1000)
                    if any(tag in first_few_lines for tag in ['<Project', '<Task', '<Resource']):
                        return True
            except:
                pass
        
        return False
    
    def get_repository_by_name(self, repo_name: str) -> Optional[Dict]:
        """
        Get repository information by name
        
        Args:
            repo_name: Name of the repository
            
        Returns:
            Repository information or None if not found
        """
        repositories = self.scan_all_repositories()
        return repositories.get(repo_name)
    
    def list_all_xml_files(self) -> List[Dict]:
        """
        Get a flat list of all XML files across all repositories
        
        Returns:
            List of dictionaries with file information
        """
        all_files = []
        repositories = self.scan_all_repositories()
        
        for repo_name, repo_info in repositories.items():
            for xml_file in repo_info['xml_files']:
                file_info = {
                    'repository': repo_name,
                    'file_path': xml_file,
                    'file_name': Path(xml_file).name,
                    'file_size': self._get_file_size(xml_file),
                    'last_modified': self._get_last_modified(xml_file)
                }
                all_files.append(file_info)
        
        return sorted(all_files, key=lambda x: x['last_modified'], reverse=True)
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except:
            return 0
    
    def _get_last_modified(self, file_path: str) -> datetime:
        """Get last modified datetime"""
        try:
            timestamp = Path(file_path).stat().st_mtime
            return datetime.fromtimestamp(timestamp)
        except:
            return datetime.min

def main():
    """Main function for command line usage"""
    print("🚀 CONTROL TOWER REPOSITORY SCANNER")
    print("="*50)
    
    scanner = RepositoryScanner()
    repositories = scanner.scan_all_repositories()
    
    if not repositories:
        print("❌ No MS Project XML files found in any repository")
        return
    
    print(f"\n📊 DISCOVERY SUMMARY:")
    print(f"   Repositories with XML files: {len(repositories)}")
    
    total_files = sum(len(repo['xml_files']) for repo in repositories.values())
    print(f"   Total XML files found: {total_files}")
    print()
    
    print("📂 REPOSITORY BREAKDOWN:")
    for repo_name, repo_info in repositories.items():
        print(f"\n   📁 {repo_name}:")
        print(f"      XML files: {len(repo_info['xml_files'])}")
        print(f"      XML directories: {len(repo_info['xml_directories'])}")
        
        # Show first few files
        for i, xml_file in enumerate(repo_info['xml_files'][:3]):
            file_name = Path(xml_file).name
            file_size = scanner._get_file_size(xml_file)
            print(f"         • {file_name} ({file_size:,} bytes)")
        
        if len(repo_info['xml_files']) > 3:
            print(f"         ... and {len(repo_info['xml_files']) - 3} more files")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   • Use milestone_detector to scan for changes across all repositories")
    print(f"   • Configure automated workflows for each repository")
    print(f"   • Set up PowerPoint reporting for multi-project status")

if __name__ == "__main__":
    main()
