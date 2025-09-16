#!/usr/bin/env python3
"""
Repository Scanner - Core Discovery Engine Component

Scans North Star repositories for work items, requirements, and project status.
Uses the clean output system for user-friendly messaging.

Part of the hierarchical requirements management system.
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime, date
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import yaml

# Add the scripts/output directory to sys.path for clean formatter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output'))
from clean_formatter import CleanOutput, OutputLevel, StatusType

@dataclass
class WorkItem:
    """Represents a work item found in repositories"""
    id: str
    title: str
    description: str
    repository: str
    file_path: str
    priority: str  # High, Medium, Low, Critical
    status: str    # Not Started, In Progress, Completed, Blocked, Overdue
    due_date: Optional[str]  # ISO format date
    assigned_to: Optional[str]
    dependencies: List[str]
    tags: List[str]
    effort_estimate: Optional[str]  # hours, days, weeks
    business_value: Optional[str]   # High, Medium, Low
    requirement_level: Optional[str]  # NSR, PR, SR, FR
    
    def is_overdue(self) -> bool:
        """Check if work item is overdue"""
        if not self.due_date:
            return False
        try:
            due = datetime.fromisoformat(self.due_date).date()
            return due < date.today() and self.status not in ['Completed']
        except ValueError:
            return False
    
    def is_due_today(self) -> bool:
        """Check if work item is due today"""
        if not self.due_date:
            return False
        try:
            due = datetime.fromisoformat(self.due_date).date()
            return due == date.today() and self.status not in ['Completed']
        except ValueError:
            return False

@dataclass
class RepositoryInfo:
    """Information about a scanned repository"""
    name: str
    path: str
    work_items: List[WorkItem]
    requirements_found: bool
    last_updated: Optional[str]
    total_items: int
    overdue_items: int
    in_progress_items: int
    
class RepositoryScanner:
    """Scans North Star repositories for work items and requirements"""
    
    def __init__(self, base_path: str = "/workspaces/control_tower/cloned_repos", 
                 output_level: OutputLevel = OutputLevel.NORMAL):
        self.base_path = Path(base_path)
        self.formatter = CleanOutput(output_level)
        self.repositories: List[RepositoryInfo] = []
        
        # North Star repository names
        self.north_star_repos = [
            "business_ventures",
            "financial_security", 
            "investment_strategy",
            "life_quality",
            "online_presence",
            "professional_excellence"
        ]
    
    def scan_all_repositories(self) -> List[RepositoryInfo]:
        """Scan all North Star repositories for work items"""
        self.formatter.header("Discovery Results", "Scanning North Star repositories for requirements")
        
        repositories = []
        
        for repo_name in self.north_star_repos:
            repo_path = self.base_path / repo_name
            
            if repo_path.exists() and repo_path.is_dir():
                self.formatter.debug(f"Scanning {repo_name}...")
                repo_info = self._scan_single_repository(repo_name, repo_path)
                repositories.append(repo_info)
                
                # Show immediate feedback for each repo
                if repo_info.requirements_found:
                    self.formatter.status(StatusType.SUCCESS, f"{repo_name}: Found {repo_info.total_items} requirements")
                else:
                    self.formatter.status(StatusType.WARNING, f"{repo_name}: No requirements found")
            else:
                self.formatter.error(f"Repository not found: {repo_name}")
        
        self.repositories = repositories
        self._generate_summary()
        
        return repositories
    
    def _scan_single_repository(self, name: str, path: Path) -> RepositoryInfo:
        """Scan a single repository for work items"""
        work_items = []
        requirements_found = False
        
        # Look for requirements files (only in requirements/ folder)
        requirements_patterns = [
            "requirements/*.md",
            "requirements/*.yml", 
            "requirements/*.yaml",
            "requirements/*.json"
        ]
        
        for pattern in requirements_patterns:
            req_files = list(path.glob(pattern))
            if req_files:
                requirements_found = True
                for req_file in req_files:
                    items = self._parse_requirements_file(req_file, name)
                    work_items.extend(items)
        
        # Look for TODO/FIXME comments in code files (disabled for requirements focus)
        # code_items = self._scan_code_for_todos(path, name)
        # work_items.extend(code_items)
        code_items = []  # Focus only on requirements documents
        
        # Calculate statistics
        total_items = len(work_items)
        overdue_items = sum(1 for item in work_items if item.is_overdue())
        in_progress_items = sum(1 for item in work_items if item.status == "In Progress")
        
        return RepositoryInfo(
            name=name,
            path=str(path),
            work_items=work_items,
            requirements_found=requirements_found,
            last_updated=self._get_last_modified(path),
            total_items=total_items,
            overdue_items=overdue_items,
            in_progress_items=in_progress_items
        )
    
    def _parse_requirements_file(self, file_path: Path, repo_name: str) -> List[WorkItem]:
        """Parse requirements file for work items"""
        work_items = []
        
        try:
            if file_path.suffix.lower() in ['.yml', '.yaml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    work_items = self._extract_from_yaml(data, file_path, repo_name)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    work_items = self._extract_from_json(data, file_path, repo_name)
            else:  # Markdown
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    work_items = self._extract_from_markdown(content, file_path, repo_name)
                    
        except Exception as e:
            self.formatter.error(f"Error parsing {file_path}: {str(e)}")
        
        return work_items
    
    def _extract_from_yaml(self, data: Dict, file_path: Path, repo_name: str) -> List[WorkItem]:
        """Extract work items from YAML requirements"""
        work_items = []
        
        # Handle different YAML structures
        if isinstance(data, dict):
            if 'requirements' in data:
                items = data['requirements']
            elif 'work_items' in data:
                items = data['work_items']
            elif 'tasks' in data:
                items = data['tasks']
            else:
                items = [data]  # Single item
        else:
            items = data if isinstance(data, list) else [data]
        
        for item_data in items:
            if isinstance(item_data, dict):
                work_item = WorkItem(
                    id=item_data.get('id', f"{repo_name}-{len(work_items)+1}"),
                    title=item_data.get('title', item_data.get('name', 'Untitled')),
                    description=item_data.get('description', ''),
                    repository=repo_name,
                    file_path=str(file_path),
                    priority=item_data.get('priority', 'Medium'),
                    status=item_data.get('status', 'Not Started'),
                    due_date=item_data.get('due_date'),
                    assigned_to=item_data.get('assigned_to'),
                    dependencies=item_data.get('dependencies', []),
                    tags=item_data.get('tags', []),
                    effort_estimate=item_data.get('effort_estimate'),
                    business_value=item_data.get('business_value', 'Medium'),
                    requirement_level=item_data.get('requirement_level')
                )
                work_items.append(work_item)
        
        return work_items
    
    def _extract_from_json(self, data: Dict, file_path: Path, repo_name: str) -> List[WorkItem]:
        """Extract work items from JSON requirements"""
        # Similar to YAML but for JSON structure
        return self._extract_from_yaml(data, file_path, repo_name)
    
    def _extract_from_markdown(self, content: str, file_path: Path, repo_name: str) -> List[WorkItem]:
        """Extract work items from Markdown requirements"""
        work_items = []
        lines = content.split('\n')
        
        current_item = None
        item_id_counter = 1
        current_due_date = None
        current_priority = "Medium"
        current_business_value = "Medium"
        current_requirement_level = None
        
        # If parsing North Star files, default to NSR level
        if 'north_star' in str(file_path).lower():
            current_requirement_level = "NSR"
        # For other requirements files, also default to NSR unless explicitly set
        elif 'requirements' in str(file_path).lower():
            current_requirement_level = "NSR"
        
        for line in lines:
            line_clean = line.strip()
            
            # Parse level field  
            if line_clean.startswith('**Level**:'):
                level_text = line_clean.split(':', 1)[1].strip()
                if level_text.startswith('**'):
                    level_text = level_text.strip('*').strip()
                # Extract requirement level from "1 (System)" -> "NSR"
                if '0' in level_text or 'North Star' in level_text:
                    current_requirement_level = "NSR"
                elif '1' in level_text or 'System' in level_text:
                    current_requirement_level = "NSR"
                elif '2' in level_text or 'Project' in level_text:
                    current_requirement_level = "PR"
                elif '3' in level_text or 'Service' in level_text:
                    current_requirement_level = "SR"
                elif '4' in level_text or 'Feature' in level_text:
                    current_requirement_level = "FR"
            
            # Parse due date fields
            elif line_clean.startswith('**Due Date**:'):
                current_due_date = line_clean.split(':', 1)[1].strip()
                if current_due_date.startswith('**'):
                    current_due_date = current_due_date.strip('*').strip()
            
            # Parse priority fields
            elif line_clean.startswith('**Priority**:'):
                current_priority = line_clean.split(':', 1)[1].strip()
                if current_priority.startswith('**'):
                    current_priority = current_priority.strip('*').strip()
            
            # Look for task items (- [ ] or - [x])
            elif line_clean.startswith('- [ ]') or line_clean.startswith('- [x]'):
                if current_item:
                    work_items.append(current_item)
                
                is_completed = line_clean.startswith('- [x]')
                title = line_clean[5:].strip()  # Remove "- [ ] " or "- [x] "
                
                current_item = WorkItem(
                    id=f"{repo_name}-{item_id_counter:03d}",
                    title=title,
                    description="",
                    repository=repo_name,
                    file_path=str(file_path),
                    priority=current_priority,
                    status="Completed" if is_completed else "Not Started",
                    due_date=current_due_date,
                    assigned_to=None,
                    dependencies=[],
                    tags=[],
                    effort_estimate=None,
                    business_value=current_business_value,
                    requirement_level=current_requirement_level
                )
                item_id_counter += 1
            
            # Look for headers as high-level items
            elif line_clean.startswith('#') and not line_clean.startswith('####'):
                if current_item:
                    work_items.append(current_item)
                
                title = line_clean.lstrip('#').strip()
                current_item = WorkItem(
                    id=f"{repo_name}-{item_id_counter:03d}",
                    title=title,
                    description="",
                    repository=repo_name,
                    file_path=str(file_path),
                    priority=current_priority,
                    status="Not Started",
                    due_date=current_due_date,
                    assigned_to=None,
                    dependencies=[],
                    tags=["milestone"],
                    effort_estimate=None,
                    business_value=current_business_value,
                    requirement_level=current_requirement_level
                )
                item_id_counter += 1
        
        if current_item:
            work_items.append(current_item)
        
        return work_items
    
    def _scan_code_for_todos(self, repo_path: Path, repo_name: str) -> List[WorkItem]:
        """Scan code files for TODO/FIXME comments"""
        work_items = []
        
        # File patterns to scan
        code_patterns = ['**/*.py', '**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx', 
                        '**/*.java', '**/*.c', '**/*.cpp', '**/*.h', '**/*.hpp']
        
        todo_counter = 1
        
        for pattern in code_patterns:
            for code_file in repo_path.glob(pattern):
                try:
                    with open(code_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    for line_num, line in enumerate(lines, 1):
                        line_clean = line.strip().upper()
                        
                        if 'TODO' in line_clean or 'FIXME' in line_clean:
                            # Extract the comment
                            comment = line.strip()
                            if '#' in comment:
                                comment = comment.split('#', 1)[1].strip()
                            elif '//' in comment:
                                comment = comment.split('//', 1)[1].strip()
                            
                            priority = "High" if 'FIXME' in line_clean else "Medium"
                            
                            work_item = WorkItem(
                                id=f"{repo_name}-TODO-{todo_counter:03d}",
                                title=f"Code TODO: {comment[:50]}...",
                                description=f"Line {line_num}: {comment}",
                                repository=repo_name,
                                file_path=str(code_file),
                                priority=priority,
                                status="Not Started",
                                due_date=None,
                                assigned_to=None,
                                dependencies=[],
                                tags=["code", "todo"],
                                effort_estimate="1-2 hours",
                                business_value="Low",
                                requirement_level="FR"  # Code TODOs are Feature level
                            )
                            work_items.append(work_item)
                            todo_counter += 1
                            
                except Exception as e:
                    self.formatter.debug(f"Error scanning {code_file}: {str(e)}")
        
        return work_items
    
    def _get_last_modified(self, repo_path: Path) -> Optional[str]:
        """Get the last modification time of the repository"""
        try:
            # Check git log if it's a git repo
            git_dir = repo_path / '.git'
            if git_dir.exists():
                import subprocess
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%ci'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            
            # Fall back to filesystem modification time
            latest_time = 0
            for file_path in repo_path.rglob('*'):
                if file_path.is_file():
                    mtime = file_path.stat().st_mtime
                    latest_time = max(latest_time, mtime)
            
            if latest_time > 0:
                return datetime.fromtimestamp(latest_time).isoformat()
                
        except Exception as e:
            self.formatter.debug(f"Error getting last modified time: {str(e)}")
        
        return None
    
    def _generate_summary(self):
        """Generate summary of scanning results"""
        if not self.repositories:
            self.formatter.error("No repositories found")
            return
        
        total_items = sum(repo.total_items for repo in self.repositories)
        total_overdue = sum(repo.overdue_items for repo in self.repositories)
        total_in_progress = sum(repo.in_progress_items for repo in self.repositories)
        total_repos_with_requirements = sum(1 for repo in self.repositories if repo.requirements_found)
        
        self.formatter.section_break()
        self.formatter.status(StatusType.SUCCESS, "Repository scan complete")
        
        if total_overdue > 0:
            self.formatter.status(StatusType.WARNING, "Some items overdue")
        
        # Check for missing requirements
        missing_requirements = [repo.name for repo in self.repositories if not repo.requirements_found]
        if missing_requirements:
            for repo_name in missing_requirements:
                self.formatter.error("Missing requirements file", f"{repo_name} requirements not found")
        
        # Show sample work items found
        sample_items_shown = 0
        for repo in self.repositories:
            if repo.total_items > 0 and sample_items_shown < 5:
                for item in repo.work_items[:3]:  # Show first 3 items from each repo
                    if sample_items_shown < 5:
                        due_text = f" (due {item.due_date})" if item.due_date else ""
                        priority_icon = "🔴" if item.priority == "Critical" else "🟡" if item.priority == "High" else "🟢"
                        self.formatter.status(StatusType.INFO, f"{priority_icon} [{item.priority}] {item.id}: {item.title[:50]}")
                        sample_items_shown += 1
        
        if total_items > sample_items_shown:
            self.formatter.status(StatusType.INFO, f"... and {total_items - sample_items_shown} more items")
        
        # Summary statistics
        self.formatter.section_break()
        summary_data = [
            {"status": "Total Repositories", "count": len(self.repositories)},
            {"status": "With Requirements", "count": total_repos_with_requirements},
            {"status": "Total Work Items", "count": total_items},
            {"status": "In Progress", "count": total_in_progress},
            {"status": "Overdue", "count": total_overdue}
        ]
        
        for item in summary_data:
            self.formatter.status(StatusType.INFO, f"{item['status']}: {item['count']}")
        
        self.formatter.status(StatusType.SUCCESS, "Environment ready for development")
    
    def get_all_work_items(self) -> List[WorkItem]:
        """Get all work items from all repositories"""
        all_items = []
        for repo in self.repositories:
            all_items.extend(repo.work_items)
        return all_items
    
    def get_work_items_by_priority(self, priority: str) -> List[WorkItem]:
        """Get work items filtered by priority"""
        return [item for item in self.get_all_work_items() if item.priority == priority]
    
    def get_overdue_items(self) -> List[WorkItem]:
        """Get all overdue work items"""
        return [item for item in self.get_all_work_items() if item.is_overdue()]
    
    def get_due_today_items(self) -> List[WorkItem]:
        """Get all items due today"""
        return [item for item in self.get_all_work_items() if item.is_due_today()]
    
    def export_results(self, output_path: str = None) -> str:
        """Export scan results to JSON file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            output_path = f"/workspaces/control_tower/outputs/repository_scan_{timestamp}.json"
        
        results = {
            "scan_timestamp": datetime.now().isoformat(),
            "repositories": [asdict(repo) for repo in self.repositories],
            "summary": {
                "total_repositories": len(self.repositories),
                "total_work_items": sum(repo.total_items for repo in self.repositories),
                "total_overdue": sum(repo.overdue_items for repo in self.repositories),
                "total_in_progress": sum(repo.in_progress_items for repo in self.repositories)
            }
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.formatter.status(StatusType.SUCCESS, f"Scan results exported to {output_path}")
        return output_path

def main():
    """Main entry point for repository scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan North Star repositories for work items")
    parser.add_argument("--base-path", default="/workspaces/control_tower/cloned_repos",
                       help="Base path for repositories")
    parser.add_argument("--output", help="Output file for scan results")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    
    args = parser.parse_args()
    
    # Set output level
    if args.quiet:
        output_level = OutputLevel.QUIET
    elif args.verbose:
        output_level = OutputLevel.VERBOSE
    else:
        output_level = OutputLevel.NORMAL
    
    # Create scanner and run
    scanner = RepositoryScanner(args.base_path, output_level)
    repositories = scanner.scan_all_repositories()
    
    # Export results
    if args.output:
        scanner.export_results(args.output)
    else:
        scanner.export_results()

if __name__ == "__main__":
    main()