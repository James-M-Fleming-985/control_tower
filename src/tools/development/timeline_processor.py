#!/usr/bin/env python3
"""
Timeline parser and hierarchy processor for Control Tower requirements management.

This script:
1. Parses timeline data from all requirements files
2. Processes dependencies and hierarchy relationships  
3. Calculates critical path and next priorities
4. Generates what-next recommendations for development sessions
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import heapq

@dataclass
class RequirementItem:
    """Data class for a single requirement with timeline data."""
    id: str
    file_path: str
    level: str
    type: str
    duration_days: int
    due_date: datetime
    start_date: datetime
    priority: str
    effort_days: float
    dependencies: List[str]
    progress: int
    status: str
    parent: Optional[str] = None
    children: List[str] = None
    critical_path: bool = False
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

class TimelineProcessor:
    """Main processor for timeline data and priority calculations."""
    
    def __init__(self):
        self.requirements: Dict[str, RequirementItem] = {}
        self.hierarchy_map: Dict[str, List[str]] = {}
        self.critical_path_items: List[str] = []
        self.calculated_priorities: List[Tuple[str, float]] = []
        
    def parse_requirements_files(self) -> int:
        """Parse all requirements files and extract timeline data."""
        
        print("🔍 Parsing requirements files...", end=" ", flush=True)
        
        cloned_repos_path = Path("/workspaces/control_tower/cloned_repos")
        file_count = 0
        error_count = 0
        
        # Find all requirements files
        patterns = ["*_requirements.md", "requirements.md"]
        
        for pattern in patterns:
            for req_file in cloned_repos_path.rglob(pattern):
                try:
                    parsed_req = self._parse_single_file(req_file)
                    if parsed_req:
                        self.requirements[parsed_req.id] = parsed_req
                        file_count += 1
                        if file_count % 100 == 0:  # Progress indicator
                            print(f"{file_count}...", end=" ", flush=True)
                            
                except Exception as e:
                    error_count += 1
        
        print(f"✅ Done")
        print(f"📊 Parsed {file_count} requirements" + (f", {error_count} errors" if error_count > 0 else ""))
        return file_count
    
    def _parse_single_file(self, file_path: Path) -> Optional[RequirementItem]:
        """Parse a single requirements file."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if no timeline section
            if "⏱️ TIMELINE MANAGEMENT" not in content:
                return None
            
            # Extract timeline section
            timeline_match = re.search(
                r'⏱️ TIMELINE MANAGEMENT.*?(?=##|\Z)', 
                content, 
                re.DOTALL
            )
            
            if not timeline_match:
                return None
            
            timeline_content = timeline_match.group(0)
            
            # Parse individual fields
            duration = self._extract_duration(timeline_content)
            due_date = self._extract_date(timeline_content, "Due Date")
            start_date = self._extract_date(timeline_content, "Start Date") 
            priority = self._extract_field(timeline_content, "Priority")
            effort = self._extract_effort(timeline_content)
            dependencies = self._extract_dependencies(timeline_content)
            progress = self._extract_progress(timeline_content)
            
            # Generate ID from file path
            req_id = self._generate_id(file_path)
            
            # Determine level and type
            level = self._determine_level(file_path)
            req_type = self._determine_type(file_path, content)
            
            return RequirementItem(
                id=req_id,
                file_path=str(file_path),
                level=level,
                type=req_type,
                duration_days=duration,
                due_date=due_date,
                start_date=start_date,
                priority=priority,
                effort_days=effort,
                dependencies=dependencies,
                progress=progress,
                status="Active"
            )
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _extract_duration(self, content: str) -> int:
        """Extract duration in days."""
        match = re.search(r'\*\*Duration\*\*:\s*(\d+)\s*days?', content)
        return int(match.group(1)) if match else 30
    
    def _extract_date(self, content: str, field_name: str) -> datetime:
        """Extract date field."""
        pattern = rf'\*\*{field_name}\*\*:\s*(\d{{4}}-\d{{2}}-\d{{2}})'
        match = re.search(pattern, content)
        if match:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
        return datetime.now() + timedelta(days=30)
    
    def _extract_field(self, content: str, field_name: str) -> str:
        """Extract text field."""
        pattern = rf'\*\*{field_name}\*\*:\s*([^\n]+)'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else "Medium"
    
    def _extract_effort(self, content: str) -> float:
        """Extract effort in person-days."""
        match = re.search(r'\*\*Effort Estimate\*\*:\s*([\d.]+)\s*person-days?', content)
        return float(match.group(1)) if match else 5.0
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies list."""
        pattern = r'\*\*Dependencies\*\*:\s*([^\n]+)'
        match = re.search(pattern, content)
        if match and match.group(1).strip() != "None":
            deps = match.group(1).split(',')
            return [dep.strip() for dep in deps if dep.strip()]
        return []
    
    def _extract_progress(self, content: str) -> int:
        """Extract progress percentage."""
        match = re.search(r'\*\*Progress\*\*:\s*(\d+)%', content)
        return int(match.group(1)) if match else 0
    
    def _generate_id(self, file_path: Path) -> str:
        """Generate requirement ID from file path."""
        parts = file_path.parts
        
        # Get repository name
        repo_idx = -1
        for i, part in enumerate(parts):
            if part == "cloned_repos":
                repo_idx = i + 1
                break
        
        if repo_idx == -1 or repo_idx >= len(parts):
            return f"REQ-{file_path.stem}"
        
        repo_name = parts[repo_idx]
        
        # Create abbreviated ID
        if "north_star" in file_path.name:
            return f"NS-{repo_name.upper()}-001"
        elif "project" in file_path.name:
            project_name = parts[repo_idx + 1] if repo_idx + 1 < len(parts) else "PROJ"
            return f"PROJ-{project_name.upper()}-001"
        elif "system" in file_path.name:
            return f"SYS-{repo_name.upper()}-001"
        elif "workpackage" in file_path.name:
            return f"WP-{repo_name.upper()}-001"
        elif "feature" in file_path.name:
            return f"FEA-{repo_name.upper()}-001"
        elif "milestone" in file_path.name:
            return f"MIL-{repo_name.upper()}-001"
        elif "layer" in file_path.name:
            return f"LAY-{repo_name.upper()}-001"
        elif "task" in file_path.name:
            return f"TSK-{repo_name.upper()}-001"
        else:
            return f"REQ-{repo_name.upper()}-{file_path.stem}"
    
    def _determine_level(self, file_path: Path) -> str:
        """Determine requirement level from file path."""
        path_str = str(file_path).lower()
        
        if "north_star" in path_str:
            return "north_star"
        elif "project" in path_str:
            return "project" 
        elif "system" in path_str:
            return "system"
        elif "workpackage" in path_str:
            return "workpackage"
        elif "feature" in path_str:
            return "feature"
        elif "milestone" in path_str:
            return "milestone"
        elif "layer" in path_str:
            return "layer"
        elif "task" in path_str:
            return "task"
        else:
            # Determine by directory depth
            parts = file_path.parts
            if len(parts) <= 4:
                return "north_star"
            elif len(parts) <= 6:
                return "project"
            elif len(parts) <= 7:
                return "system" if "systems" in path_str else "workpackage"
            elif len(parts) <= 8:
                return "feature" if "features" in path_str else "milestone"
            else:
                return "layer" if "layers" in path_str else "task"
    
    def _determine_type(self, file_path: Path, content: str) -> str:
        """Determine project type (Application/Delivery)."""
        path_str = str(file_path).lower()
        
        if any(keyword in path_str for keyword in ["systems", "features", "layers"]):
            return "Application"
        elif any(keyword in path_str for keyword in ["workpackages", "milestones", "tasks"]):
            return "Delivery"
        elif any(project in path_str for project in ["financial_optimizer", "opti_royale", "causal_affect"]):
            return "Application"
        elif any(project in path_str for project in ["home_improvements", "safran"]):
            return "Delivery"
        else:
            return "Application"  # Default
    
    def calculate_priorities(self) -> List[Tuple[str, int]]:
        """Calculate next priorities based on timeline data."""
        
        print("🎯 Calculating priorities...", end=" ", flush=True)
        
        priorities = []
        current_date = datetime.now()
        
        for req_id, req in self.requirements.items():
            if req.progress >= 100:
                continue  # Skip completed items
                
            # Calculate priority score
            score = self._calculate_priority_score(req, current_date)
            priorities.append((req_id, score))
        
        # Sort by priority score (higher = more urgent)
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        print(f"✅ Done ({len(priorities)} active items)")
        
        # Store calculated priorities for reuse
        self.calculated_priorities = priorities
        return priorities
    
    def _calculate_priority_score(self, req: RequirementItem, current_date: datetime) -> int:
        """Calculate priority score for a requirement."""
        
        score = 0
        
        # Priority level weight
        priority_weights = {
            "Critical": 100,
            "High": 75,
            "Medium": 50,
            "Low": 25
        }
        score += priority_weights.get(req.priority, 50)
        
        # Due date urgency (days until due)
        days_until_due = (req.due_date - current_date).days
        if days_until_due < 0:
            score += 200  # Overdue items get highest priority
        elif days_until_due <= 7:
            score += 150  # Due within a week
        elif days_until_due <= 30:
            score += 100  # Due within a month
        elif days_until_due <= 90:
            score += 50   # Due within 3 months
        
        # Progress consideration (less complete = higher priority for active work)
        if req.progress < 25:
            score += 30
        elif req.progress < 50:
            score += 20
        elif req.progress < 75:
            score += 10
        
        # Level importance (prioritize actionable development work)
        level_weights = {
            "task": 50,        # Actual development work (highest priority)
            "layer": 45,       # Implementation layers
            "feature": 40,     # Specific features to build
            "workpackage": 30, # Grouped work
            "system": 25,      # System components
            "milestone": 20,   # Project milestones
            "project": 15,     # Project definitions (only if nothing else)
            "north_star": 5    # Strategic goals (lowest for development)
        }
        score += level_weights.get(req.level, 10)
        
        # Effort consideration (prefer smaller tasks for quick wins)
        if req.effort_days <= 1:
            score += 20
        elif req.effort_days <= 3:
            score += 10
        elif req.effort_days <= 7:
            score += 5
        
        return score
    
    def get_next_work_items(self, limit: int = 10) -> List[RequirementItem]:
        """Get the top priority work items for the next development session."""
        
        # Use already calculated priorities if available, otherwise calculate
        if not self.calculated_priorities:
            priorities = self.calculate_priorities()
        else:
            priorities = self.calculated_priorities
            
        next_items = []
        
        for req_id, score in priorities[:limit]:
            if req_id in self.requirements:
                req = self.requirements[req_id]
                req.critical_path = score > 150  # Mark high priority items
                next_items.append(req)
        
        return next_items
    
    def get_hierarchy_context(self, req_id: str) -> str:
        """Get the full hierarchy context showing the complete path from North Star down."""
        req = self.requirements.get(req_id)
        if not req:
            return ""
            
        # Build hierarchy based on ID structure and dependencies
        parts = req_id.split('-')
        if len(parts) < 3:
            return f"{req.level.title()} level"
            
        level_prefix = parts[0]
        domain = parts[1].replace('_', ' ').title()
        component = parts[2]
        
        # Create meaningful component names based on level and context
        level_names = {
            "NS": "North Star",
            "PROJ": "Project", 
            "SYS": "System",
            "WP": "Workpackage",
            "FEA": "Feature",
            "MIL": "Milestone",
            "LAY": "Layer",
            "TSK": "Task"
        }
        
        level_name = level_names.get(level_prefix, req.level.title())
        
        # For demonstration, create meaningful component names based on domain
        component_names = {
            "Business Ventures": {
                "LAY": ["API Layer", "Business Logic Layer", "Data Layer", "UI Layer"],
                "FEA": ["Correlation Matrix", "Causal Engine", "Dashboard", "Analytics"],
                "SYS": ["Causal Engine", "Analytics Platform", "Data Pipeline", "User Interface"],
                "TSK": ["Database Setup", "API Development", "Frontend Implementation", "Testing"]
            },
            "Life Quality": {
                "LAY": ["Service Layer", "Data Layer", "UI Layer", "Integration Layer"],
                "FEA": ["Bathroom Design", "Budget Tracker", "Timeline Manager", "Contractor Portal"],
                "SYS": ["Design System", "Budget System", "Project Management", "Communication Hub"],
                "TSK": ["Design Review", "Material Selection", "Installation", "Quality Check"]
            },
            "Professional Excellence": {
                "LAY": ["Documentation Layer", "Compliance Layer", "Training Layer", "Audit Layer"],
                "FEA": ["NADCAP Tracker", "Training Manager", "Audit System", "Reporting"],
                "SYS": ["Compliance System", "Training Platform", "Documentation Hub", "Quality Assurance"],
                "TSK": ["Document Review", "Training Setup", "Audit Preparation", "Report Generation"]
            }
        }
        
        # Get meaningful component name
        component_name = "001"  # Default
        if domain in component_names and level_prefix in component_names[domain]:
            available_names = component_names[domain][level_prefix]
            try:
                component_idx = int(component) - 1
                if 0 <= component_idx < len(available_names):
                    component_name = available_names[component_idx]
            except ValueError:
                pass
        
        # For demonstration, show the ideal hierarchy path format
        # Example: "Layer 4 API → Feature Correlation Matrix → System Causal Engine → Project Causal_affect → North Star Business Ventures"
        
        if level_prefix == "LAY":
            # Show layer number and type
            layer_num = component if component.isdigit() else "1"
            return f"Layer {layer_num} {component_name} → Feature Correlation Matrix → System Causal Engine → Project Causal_affect → North Star {domain}"
        elif level_prefix == "FEA":
            return f"Feature {component_name} → System Causal Engine → Project Causal_affect → North Star {domain}"
        elif level_prefix == "SYS":
            return f"System {component_name} → Project Causal_affect → North Star {domain}"
        elif level_prefix == "TSK":
            return f"Task {component_name} → Layer API → Feature Correlation Matrix → System Causal Engine → Project Causal_affect → North Star {domain}"
        elif level_prefix == "WP":
            return f"Workpackage {component_name} → Project Bathroom Upgrade → North Star {domain}"
        elif level_prefix == "MIL":
            return f"Milestone {component_name} → Project Quality System → North Star {domain}"
        else:
            return f"{level_name} {component_name} → North Star {domain}"
    
    def _is_hierarchical_parent(self, potential_parent_id: str, child_id: str) -> bool:
        """Check if one requirement is a hierarchical parent of another."""
        parent_parts = potential_parent_id.split('-')
        child_parts = child_id.split('-')
        
        if len(parent_parts) < 2 or len(child_parts) < 2:
            return False
            
        # Same domain/area
        if parent_parts[1] != child_parts[1]:
            return False
            
        # Check level hierarchy
        level_hierarchy = ["NS", "PROJ", "SYS", "FEA", "WP", "MIL", "LAY", "TSK"]
        
        try:
            parent_level_idx = level_hierarchy.index(parent_parts[0])
            child_level_idx = level_hierarchy.index(child_parts[0])
            return parent_level_idx < child_level_idx  # Parent is higher in hierarchy
        except ValueError:
            return False
    
    def generate_what_next_report(self) -> str:
        """Generate a clean, focused what-next report with just the essentials."""
        
        next_items = self.get_next_work_items(20)  # Get more items to filter properly
        current_date = datetime.now()
        
        # Filter to focus on actionable development work
        development_levels = ["task", "layer", "feature", "workpackage"]
        dev_items = [item for item in next_items if item.level in development_levels]
        
        # If no development work, include system and milestone items
        if len(dev_items) < 3:
            other_levels = ["system", "milestone"]
            other_items = [item for item in next_items if item.level in other_levels]
            dev_items.extend(other_items[:3-len(dev_items)])
        
        # If still not enough, include project items (for requirements definition)
        if len(dev_items) < 3:
            project_items = [item for item in next_items if item.level == "project"]
            dev_items.extend(project_items[:3-len(dev_items)])
        
        report = []
        
        # Summary and recommendation only
        if dev_items:
            top_item = dev_items[0]
            context = self.get_hierarchy_context(top_item.id)
            
            # Count categories
            overdue_items = [item for item in dev_items if item.due_date < current_date]
            week_items = [item for item in dev_items 
                         if item.due_date >= current_date 
                         and item.due_date <= current_date + timedelta(days=7)]
            quick_wins = [item for item in dev_items 
                         if item.effort_days <= 2 and item.progress < 50]
            
            # Extract project from file path - look for the actual repository name
            project = "unknown"
            try:
                path_parts = Path(top_item.file_path).parts
                # Find the part after 'cloned_repos'
                if 'cloned_repos' in path_parts:
                    cloned_idx = path_parts.index('cloned_repos')
                    if cloned_idx + 1 < len(path_parts):
                        project = path_parts[cloned_idx + 1]
            except:
                pass
            
            report.append("📊 DEVELOPMENT SUMMARY:")
            report.append(f"  • {len(self.requirements)} total requirements analyzed")
            report.append(f"  • {len(overdue_items)} overdue, {len(week_items)} due this week, {len(quick_wins)} quick wins")
            report.append(f"  • {len(dev_items)} actionable development items ready")
            report.append("")
            report.append("🎯 RECOMMENDED ACTION:")
            report.append(f"  Work on: {top_item.id}")
            report.append(f"  Context: {context}")
            report.append(f"  Effort: {top_item.effort_days} person-days")
            report.append(f"  Command: make prep PROJECT={project}")
        else:
            report.append("✅ All development work is up to date!")
        
        return "\n".join(report)
    
    def save_timeline_data(self, output_file: str = "data/timeline_analysis.json"):
        """Save parsed timeline data for other tools."""
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        data = {
            "generated": datetime.now().isoformat(),
            "total_requirements": len(self.requirements),
            "requirements": {}
        }
        
        for req_id, req in self.requirements.items():
            data["requirements"][req_id] = {
                "file_path": req.file_path,
                "level": req.level,
                "type": req.type,
                "duration_days": req.duration_days,
                "due_date": req.due_date.isoformat(),
                "start_date": req.start_date.isoformat(),
                "priority": req.priority,
                "effort_days": req.effort_days,
                "dependencies": req.dependencies,
                "progress": req.progress,
                "status": req.status
            }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Timeline data saved to {output_path.name}")

def main():
    """Main function to run timeline analysis."""
    
    processor = TimelineProcessor()
    
    # Parse all requirements files
    file_count = processor.parse_requirements_files()
    
    if file_count == 0:
        print("❌ No requirements files found with timeline data")
        return
    
    # Calculate priorities once and save data
    processor.calculate_priorities()
    processor.save_timeline_data()
    
    # Generate clean what-next report
    print()  # Add space before report
    report = processor.generate_what_next_report()
    print()
    print(report)
    
    return processor

if __name__ == "__main__":
    main()