#!/usr/bin/env python3
"""
🎯 WORK DISCOVERY ENGINE
Provides actionable "what should I work on next" recommendations.

This is the core implementation of FR-001: Work Discovery and Prioritization
Updated to use the new repository scanner and priority calculator system.
"""

import os
import sys
import argparse

# Add the discovery module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'discovery'))
from repository_scanner import RepositoryScanner, OutputLevel
from priority_calculator import PriorityCalculator

# Add the scripts/output directory to sys.path for clean formatter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'output'))
from clean_formatter import CleanOutput, StatusType

def main():
    """Main entry point for work discovery engine - answers 'what should I work on next?'"""
    parser = argparse.ArgumentParser(description="Get actionable work recommendations")
    parser.add_argument("--base-path", default="/workspaces/control_tower/cloned_repos",
                       help="Base path for repositories")
    parser.add_argument("--top", type=int, default=1, help="Number of recommendations (default: 1)")
    parser.add_argument("--export", help="Export results to specified file")
    parser.add_argument("--repository", help="Focus on specific repository")
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
    
    formatter = CleanOutput(output_level)
    
    # Quick scan (don't show full repository details for what-next)
    formatter.status(StatusType.INFO, "Analyzing work across North Star repositories...")
    
    # Create scanner and get work items (quiet mode for what-next)
    scanner = RepositoryScanner(args.base_path, OutputLevel.QUIET)
    repositories = scanner.scan_all_repositories()
    all_work_items = scanner.get_all_work_items()
    
    if not all_work_items:
        formatter.status(StatusType.WARNING, "No work items found")
        formatter.status(StatusType.INFO, "Try: make health-check  # to verify repository connectivity")
        return
    
    # Filter by repository if specified
    if args.repository:
        all_work_items = [item for item in all_work_items if item.repository == args.repository]
        if not all_work_items:
            formatter.error(f"No work items found in repository: {args.repository}")
            return
    
    # Calculate priorities and get recommendations
    calculator = PriorityCalculator(output_level)
    priority_scores = calculator.calculate_priorities(all_work_items)
    
    # Get top recommendations
    top_recommendations = calculator.get_top_recommendations(priority_scores, args.top)
    
    if not top_recommendations:
        formatter.status(StatusType.INFO, "No prioritized work items found")
        return
    
    # For single recommendation (default), show focused output
    if args.top == 1 and top_recommendations:
        rec = top_recommendations[0]
        item = rec.work_item
        
        formatter.section_break()
        formatter.header("🎯 Your Next Priority")
        
        formatter.status(StatusType.SUCCESS, f"{rec.recommendation}")
        formatter.status(StatusType.INFO, f"📋 {item.title}")
        formatter.status(StatusType.INFO, f"📁 {item.repository} → {item.id}")
        
        # Show key reasoning
        if rec.reasoning:
            formatter.status(StatusType.INFO, f"💡 {rec.reasoning[0]}")
        
        formatter.section_break()
        formatter.status(StatusType.SUCCESS, f"▶️  {rec.next_action}")
        formatter.status(StatusType.INFO, "    # Start working on this item")
        
        # Show context commands
        formatter.section_break()
        formatter.status(StatusType.INFO, "📚 Related commands:")
        formatter.status(StatusType.INFO, f"   make health-check    # Verify system connectivity")
        formatter.status(StatusType.INFO, f"   make what-next --top=3    # See more options")
        if item.repository:
            formatter.status(StatusType.INFO, f"   make what-next --repository={item.repository}    # Focus on {item.repository}")
    
    else:
        # Show multiple recommendations
        calculator.format_recommendations(top_recommendations)
    
    # Export results if requested
    if args.export:
        import json
        from datetime import datetime
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "total_items_analyzed": len(all_work_items),
            "recommendations": [
                {
                    "rank": i + 1,
                    "item_id": rec.work_item.id,
                    "title": rec.work_item.title,
                    "repository": rec.work_item.repository,
                    "recommendation": rec.recommendation,
                    "score": rec.total_score,
                    "next_action": rec.next_action,
                    "reasoning": rec.reasoning
                }
                for i, rec in enumerate(top_recommendations)
            ]
        }
        
        with open(args.export, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        formatter.status(StatusType.SUCCESS, f"Recommendations exported to {args.export}")

if __name__ == "__main__":
    main()
import sys
import argparse
from pathlib import Path

# Add the discovery module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'discovery'))
from repository_scanner import RepositoryScanner, OutputLevel

def main():
    """Main entry point for work discovery engine"""
    parser = argparse.ArgumentParser(description="Discover and prioritize work across North Star repositories")
    parser.add_argument("--base-path", default="/workspaces/control_tower/cloned_repos",
                       help="Base path for repositories")
    parser.add_argument("--export", help="Export results to specified file")
    parser.add_argument("--repository", help="Focus on specific repository")
    parser.add_argument("--level", help="Focus on specific level")
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
    
    # Create scanner and run discovery
    scanner = RepositoryScanner(args.base_path, output_level)
    repositories = scanner.scan_all_repositories()
    
    # Export results if requested
    if args.export:
        scanner.export_results(args.export)
    
    # TODO: Add priority calculator and what-next recommendations
    # This will be implemented in the next phase

if __name__ == "__main__":
    main()
        self.work_items: List[WorkItem] = []
        self.current_date = datetime.now()
        
    def discover_all_work(self) -> List[WorkItem]:
        """Main discovery method - scans all repositories for work items"""
        print("🔍 SCANNING ALL REPOSITORIES FOR WORK ITEMS")
        print("=" * 60)
        
        for repo in self.repositories:
            repo_path = self.base_path / repo
            if repo_path.exists():
                print(f"📂 Scanning {repo}...")
                self._scan_repository(repo, repo_path)
            else:
                print(f"⚠️  Repository {repo} not found at {repo_path}")
        
        return self._prioritize_work_items()
    
    def _scan_repository(self, repo_name: str, repo_path: Path):
        """Scan a single repository for work items"""
        
        # Scan for different requirement levels
        self._scan_north_star_requirements(repo_name, repo_path)
        self._scan_project_requirements(repo_name, repo_path)
        self._scan_system_requirements(repo_name, repo_path)
        self._scan_feature_workpackage_requirements(repo_name, repo_path)
        self._scan_layer_requirements(repo_name, repo_path)
        self._scan_task_requirements(repo_name, repo_path)
    
    def _scan_north_star_requirements(self, repo_name: str, repo_path: Path):
        """Scan Level 0: North Star requirements"""
        north_star_files = list(repo_path.glob("**/NORTH_STAR*.md"))
        north_star_files.extend(list(repo_path.glob("**/north_star*.md")))
        
        for file_path in north_star_files:
            work_item = self._parse_requirement_file(repo_name, file_path, 0)
            if work_item:
                self.work_items.append(work_item)
    
    def _scan_project_requirements(self, repo_name: str, repo_path: Path):
        """Scan Level 2: Project requirements"""
        project_files = list(repo_path.glob("**/PROJECT-*.md"))
        
        for file_path in project_files:
            work_item = self._parse_requirement_file(repo_name, file_path, 2)
            if work_item:
                self.work_items.append(work_item)
    
    def _scan_system_requirements(self, repo_name: str, repo_path: Path):
        """Scan Level 3: System requirements"""
        system_files = list(repo_path.glob("**/SYSTEM-*.md"))
        
        for file_path in system_files:
            work_item = self._parse_requirement_file(repo_name, file_path, 3)
            if work_item:
                self.work_items.append(work_item)
    
    def _scan_feature_workpackage_requirements(self, repo_name: str, repo_path: Path):
        """Scan Level 4: Feature/Workpackage requirements"""
        feature_files = list(repo_path.glob("**/FEATURE-*.md"))
        feature_files.extend(list(repo_path.glob("**/WORKPACKAGE-*.md")))
        
        for file_path in feature_files:
            work_item = self._parse_requirement_file(repo_name, file_path, 4)
            if work_item:
                self.work_items.append(work_item)
    
    def _scan_layer_requirements(self, repo_name: str, repo_path: Path):
        """Scan Level 5: Layer requirements"""
        layer_files = list(repo_path.glob("**/LAYER-*.md"))
        
        for file_path in layer_files:
            work_item = self._parse_requirement_file(repo_name, file_path, 5)
            if work_item:
                self.work_items.append(work_item)
    
    def _scan_task_requirements(self, repo_name: str, repo_path: Path):
        """Scan Level 6: Task requirements"""
        task_files = list(repo_path.glob("**/TASK-*.md"))
        
        for file_path in task_files:
            work_item = self._parse_requirement_file(repo_name, file_path, 6)
            if work_item:
                self.work_items.append(work_item)
    
    def _parse_requirement_file(self, repo_name: str, file_path: Path, level: int) -> Optional[WorkItem]:
        """Parse a requirement file to extract work item information"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract basic information
            title = self._extract_title(content)
            req_id = self._extract_requirement_id(content, file_path.name)
            status = self._extract_status(content)
            progress = self._extract_progress(content)
            due_date = self._extract_due_date(content)
            effort = self._extract_effort_estimate(content)
            dependencies = self._extract_dependencies(content)
            
            # Determine priority based on multiple factors
            priority = self._calculate_priority(content, due_date, progress, level)
            
            # Extract blocking factors
            blocking_factors = self._extract_blocking_factors(content, file_path)
            
            # Generate next actions
            next_actions = self._generate_next_actions(content, status, progress, level)
            
            # Get file modification time
            last_updated = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")
            
            return WorkItem(
                id=req_id,
                title=title,
                level=level,
                repository=repo_name,
                status=status,
                priority=priority,
                effort_estimate=effort,
                due_date=due_date,
                dependencies=dependencies,
                blocking_factors=blocking_factors,
                progress_percentage=progress,
                next_actions=next_actions,
                file_path=str(file_path),
                last_updated=last_updated
            )
            
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
            return None
    
    def _extract_title(self, content: str) -> str:
        """Extract title from requirement file"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Unknown Requirement"
    
    def _extract_requirement_id(self, content: str, filename: str) -> str:
        """Extract requirement ID from content or filename"""
        # Look for ID in content first
        id_match = re.search(r'\*\*Requirement ID\*\*:\s*([A-Z0-9-]+)', content)
        if id_match:
            return id_match.group(1)
        
        # Fall back to filename parsing
        filename_parts = filename.replace('.md', '').split('_')
        if filename_parts:
            return filename_parts[0]
        
        return filename.replace('.md', '')
    
    def _extract_status(self, content: str) -> str:
        """Extract status from requirement file"""
        status_match = re.search(r'\*\*Status\*\*:\s*([A-Za-z\s]+)', content)
        if status_match:
            return status_match.group(1).strip()
        
        # Look for common status indicators
        if 'completed' in content.lower():
            return 'Completed'
        elif 'in progress' in content.lower() or 'in-progress' in content.lower():
            return 'In Progress'
        elif 'blocked' in content.lower():
            return 'Blocked'
        elif 'not started' in content.lower() or 'not-started' in content.lower():
            return 'Not Started'
        
        return 'Unknown'
    
    def _extract_progress(self, content: str) -> int:
        """Extract progress percentage from requirement file"""
        progress_match = re.search(r'\*\*Progress\*\*:\s*(\d+)%', content)
        if progress_match:
            return int(progress_match.group(1))
        
        progress_match = re.search(r'(\d+)%\s*complete', content.lower())
        if progress_match:
            return int(progress_match.group(1))
        
        # Estimate based on status
        status = self._extract_status(content).lower()
        if 'completed' in status:
            return 100
        elif 'in progress' in status:
            return 50
        elif 'not started' in status:
            return 0
        
        return 0
    
    def _extract_due_date(self, content: str) -> Optional[str]:
        """Extract due date from requirement file"""
        due_date_match = re.search(r'\*\*Due Date\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
        if due_date_match:
            return due_date_match.group(1)
        
        # Look for other date patterns
        date_match = re.search(r'due by\s*(\d{4}-\d{2}-\d{2})', content.lower())
        if date_match:
            return date_match.group(1)
        
        return None
    
    def _extract_effort_estimate(self, content: str) -> str:
        """Extract effort estimate from requirement file"""
        effort_match = re.search(r'\*\*Effort Estimate\*\*:\s*([^\n]+)', content)
        if effort_match:
            return effort_match.group(1).strip()
        
        # Look for common effort patterns
        effort_patterns = [
            r'(\d+)\s*days?',
            r'(\d+)\s*weeks?',
            r'(\d+)\s*hours?',
            r'(\d+)\s*person[- ]days?'
        ]
        
        for pattern in effort_patterns:
            match = re.search(pattern, content.lower())
            if match:
                return f"{match.group(1)} {pattern.split('(')[1].split(')')[0]}"
        
        return "Unknown"
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from requirement file"""
        dependencies = []
        
        # Look for dependencies section
        dep_section = re.search(r'\*\*Dependencies\*\*:\s*([^\n*]+)', content)
        if dep_section:
            dep_text = dep_section.group(1)
            # Split by common separators
            deps = re.split(r'[,;]', dep_text)
            dependencies.extend([dep.strip() for dep in deps if dep.strip()])
        
        # Look for dependency patterns
        dep_patterns = [
            r'depends on\s+([A-Z0-9-]+)',
            r'requires\s+([A-Z0-9-]+)',
            r'blocked by\s+([A-Z0-9-]+)'
        ]
        
        for pattern in dep_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dependencies.extend(matches)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _calculate_priority(self, content: str, due_date: Optional[str], progress: int, level: int) -> int:
        """Calculate priority score (1-10, 10 being highest)"""
        priority = 5  # Base priority
        
        # Timeline urgency
        if due_date:
            try:
                due = datetime.strptime(due_date, "%Y-%m-%d")
                days_until_due = (due - self.current_date).days
                
                if days_until_due < 0:  # Overdue
                    priority += 4
                elif days_until_due <= 7:  # Due within a week
                    priority += 3
                elif days_until_due <= 30:  # Due within a month
                    priority += 2
                elif days_until_due <= 90:  # Due within 3 months
                    priority += 1
            except ValueError:
                pass
        
        # Level importance (higher levels are more strategic)
        if level <= 2:  # North Star, Repository, Project
            priority += 2
        elif level <= 4:  # System, Feature/Workpackage
            priority += 1
        
        # Progress consideration
        if progress == 0:  # Not started
            priority += 1
        elif 0 < progress < 100:  # In progress
            priority += 2
        # Completed items get no priority boost
        
        # Critical/high priority indicators in content
        if any(term in content.lower() for term in ['critical', 'urgent', 'high priority', 'blocker']):
            priority += 2
        
        # North Star impact
        if any(term in content.lower() for term in ['north star', 'strategic', 'foundation']):
            priority += 1
        
        return min(priority, 10)  # Cap at 10
    
    def _extract_blocking_factors(self, content: str, file_path: Path) -> List[str]:
        """Identify blocking factors for the work item"""
        blocking_factors = []
        
        # Look for explicit blocking factors
        if 'blocked' in content.lower():
            blocking_factors.append("Marked as blocked in requirements")
        
        # Check for missing dependencies
        dependencies = self._extract_dependencies(content)
        for dep in dependencies:
            # This is a simplified check - in practice, you'd check if dependencies are completed
            blocking_factors.append(f"Depends on {dep}")
        
        # Check for missing files or structure
        if not self._has_tests(file_path):
            blocking_factors.append("No test structure exists")
        
        if not self._has_documentation(file_path):
            blocking_factors.append("Documentation incomplete")
        
        return blocking_factors
    
    def _has_tests(self, file_path: Path) -> bool:
        """Check if tests exist for this requirement"""
        # Look for test files in common locations
        test_dirs = ['tests', 'test', 'testing']
        req_name = file_path.stem
        
        for test_dir in test_dirs:
            test_path = file_path.parent / test_dir
            if test_path.exists():
                test_files = list(test_path.glob(f"*{req_name}*"))
                if test_files:
                    return True
        
        return False
    
    def _has_documentation(self, file_path: Path) -> bool:
        """Check if adequate documentation exists"""
        content = file_path.read_text(encoding='utf-8')
        
        # Basic documentation checks
        required_sections = [
            'requirements?',
            'objectives?',
            'success criteria',
            'acceptance criteria'
        ]
        
        found_sections = 0
        for section in required_sections:
            if re.search(section, content, re.IGNORECASE):
                found_sections += 1
        
        return found_sections >= 2  # At least 2 required sections
    
    def _generate_next_actions(self, content: str, status: str, progress: int, level: int) -> List[str]:
        """Generate specific next actions for the work item"""
        next_actions = []
        
        status_lower = status.lower()
        
        if 'not started' in status_lower or progress == 0:
            next_actions.extend([
                f"Run: make work-on LEVEL={level} ID={{requirement_id}}",
                "Review requirement documentation",
                "Set up development environment",
                "Create initial test structure"
            ])
        elif 'in progress' in status_lower:
            next_actions.extend([
                f"Run: make test-cycle LEVEL={level} ID={{requirement_id}}",
                "Continue development work",
                "Update progress tracking",
                "Run quality checks"
            ])
        elif 'blocked' in status_lower:
            next_actions.extend([
                "Resolve blocking dependencies",
                "Update stakeholders on status",
                "Consider alternative approaches",
                "Escalate if needed"
            ])
        elif progress >= 90:
            next_actions.extend([
                f"Run: make ship LEVEL={level} ID={{requirement_id}}",
                "Final quality gate validation",
                "Prepare for production deployment",
                "Update completion metrics"
            ])
        
        return next_actions
    
    def _prioritize_work_items(self) -> List[WorkItem]:
        """Sort and prioritize all discovered work items"""
        print(f"\n📊 PRIORITIZING {len(self.work_items)} WORK ITEMS")
        
        # Sort by priority (descending), then by due date
        sorted_items = sorted(
            self.work_items,
            key=lambda x: (
                -x.priority,  # Higher priority first
                x.due_date or "9999-12-31",  # Items with due dates first
                x.level,  # Lower level numbers (more strategic) first
                x.repository  # Alphabetical by repository
            )
        )
        
        return sorted_items
    
    def generate_summary_report(self, work_items: List[WorkItem]) -> None:
        """Generate comprehensive summary report"""
        print("\n🎯 WORK DISCOVERY SUMMARY REPORT")
        print("=" * 60)
        
        # Overall statistics
        total_items = len(work_items)
        overdue_items = self._count_overdue_items(work_items)
        high_priority_items = len([item for item in work_items if item.priority >= 8])
        blocked_items = len([item for item in work_items if 'blocked' in item.status.lower()])
        
        print(f"📋 OVERALL STATISTICS:")
        print(f"   Total Work Items: {total_items}")
        print(f"   High Priority (8+): {high_priority_items}")
        print(f"   Overdue Items: {overdue_items}")
        print(f"   Blocked Items: {blocked_items}")
        
        # By repository
        print(f"\n📂 BY REPOSITORY:")
        repo_counts = {}
        for item in work_items:
            repo_counts[item.repository] = repo_counts.get(item.repository, 0) + 1
        
        for repo, count in sorted(repo_counts.items()):
            print(f"   {repo}: {count} items")
        
        # By level
        print(f"\n📊 BY LEVEL:")
        level_counts = {}
        level_names = {
            0: "North Star",
            1: "Repository", 
            2: "Project",
            3: "System",
            4: "Feature/Workpackage",
            5: "Layer",
            6: "Task"
        }
        
        for item in work_items:
            level_name = level_names.get(item.level, f"Level {item.level}")
            level_counts[level_name] = level_counts.get(level_name, 0) + 1
        
        for level_name, count in level_counts.items():
            print(f"   {level_name}: {count} items")
        
        # Top 10 priority items
        print(f"\n🔥 TOP 10 PRIORITY WORK ITEMS:")
        for i, item in enumerate(work_items[:10], 1):
            due_indicator = ""
            if item.due_date:
                try:
                    due = datetime.strptime(item.due_date, "%Y-%m-%d")
                    days_until = (due - self.current_date).days
                    if days_until < 0:
                        due_indicator = f" (OVERDUE by {abs(days_until)} days)"
                    elif days_until <= 7:
                        due_indicator = f" (Due in {days_until} days)"
                except ValueError:
                    pass
            
            blocking_indicator = ""
            if item.blocking_factors:
                blocking_indicator = f" [BLOCKED: {len(item.blocking_factors)} factors]"
            
            print(f"   {i:2d}. [{item.priority}/10] {item.id}: {item.title}")
            print(f"       📂 {item.repository} | 📊 Level {item.level} | 🎯 {item.progress_percentage}% complete")
            print(f"       ⏰ Effort: {item.effort_estimate}{due_indicator}{blocking_indicator}")
            
            if item.next_actions:
                print(f"       🔄 Next: {item.next_actions[0]}")
            print()
    
    def _count_overdue_items(self, work_items: List[WorkItem]) -> int:
        """Count items that are overdue"""
        overdue_count = 0
        for item in work_items:
            if item.due_date:
                try:
                    due = datetime.strptime(item.due_date, "%Y-%m-%d")
                    if due < self.current_date and item.progress_percentage < 100:
                        overdue_count += 1
                except ValueError:
                    pass
        return overdue_count
    
    def export_work_items(self, work_items: List[WorkItem], output_file: str) -> None:
        """Export work items to JSON file"""
        work_data = [asdict(item) for item in work_items]
        
        with open(output_file, 'w') as f:
            json.dump(work_data, f, indent=2, default=str)
        
        print(f"📄 Work items exported to {output_file}")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Discover and prioritize work across North Star repositories")
    parser.add_argument("--export", type=str, help="Export results to JSON file")
    parser.add_argument("--repository", type=str, help="Focus on specific repository")
    parser.add_argument("--level", type=int, choices=range(0, 7), help="Focus on specific level")
    parser.add_argument("--top", type=int, default=10, help="Show top N priority items")
    
    args = parser.parse_args()
    
    # Initialize discovery engine
    engine = WorkDiscoveryEngine()
    
    # Discover all work
    work_items = engine.discover_all_work()
    
    # Filter if requested
    if args.repository:
        work_items = [item for item in work_items if item.repository == args.repository]
    
    if args.level is not None:
        work_items = [item for item in work_items if item.level == args.level]
    
    # Generate summary report
    engine.generate_summary_report(work_items)
    
    # Show actionable next steps
    if work_items:
        print(f"\n🚀 RECOMMENDED NEXT ACTIONS:")
        print("=" * 40)
        top_item = work_items[0]
        print(f"🎯 HIGHEST PRIORITY: {top_item.id}")
        print(f"   📋 {top_item.title}")
        print(f"   📂 Repository: {top_item.repository}")
        print(f"   📊 Level: {top_item.level}")
        print(f"   🎯 Progress: {top_item.progress_percentage}%")
        
        if top_item.next_actions:
            print(f"\n   🔄 NEXT ACTIONS:")
            for action in top_item.next_actions:
                formatted_action = action.replace("{requirement_id}", top_item.id)
                print(f"      • {formatted_action}")
        
        if top_item.blocking_factors:
            print(f"\n   ⚠️  BLOCKING FACTORS:")
            for factor in top_item.blocking_factors:
                print(f"      • {factor}")
    
    # Export if requested
    if args.export:
        engine.export_work_items(work_items, args.export)
    
    return 0 if work_items else 1

if __name__ == "__main__":
    sys.exit(main())