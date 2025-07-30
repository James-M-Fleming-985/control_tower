#!/usr/bin/env python3
"""
Universal PowerPoint Generator for Control Tower
Creates cross-project milestone reports from all repositories

This generator:
1. Scans all repositories for milestone data
2. Creates unified PowerPoint presentations
3. Supports repository-specific and cross-project views
4. Integrates change management information
5. Provides executive-level reporting
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from calendar import monthrange

# Add Control Tower modules to path
sys.path.append("/workspaces/control_tower")
from modules.ms_project.ms_project_integration import MSProjectIntegration
from ..core.repository_scanner import RepositoryScanner

class PowerPointGenerator:
    """
    Generates PowerPoint presentations from milestone data across all repositories
    """
    
    def __init__(self, output_path: str = "/workspaces/control_tower/reports/milestone_presentations"):
        """
        Initialize the PowerPoint generator
        
        Args:
            output_path: Directory for saving generated presentations
        """
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.scanner = RepositoryScanner()
        
        # Default project phases for categorization
        self.default_phases = {
            "planning": {
                "title": "Planning & Design Phase",
                "keywords": ["Planning", "Design", "Requirements", "Analysis", "Specification"],
                "color": "blue"
            },
            "implementation": {
                "title": "Implementation Phase", 
                "keywords": ["Development", "Construction", "Installation", "Implementation", "Build"],
                "color": "green"
            },
            "testing": {
                "title": "Testing & Validation Phase",
                "keywords": ["Testing", "Validation", "Verification", "Commissioning", "QA"],
                "color": "orange"
            },
            "deployment": {
                "title": "Deployment & Go-Live Phase",
                "keywords": ["Deployment", "Go-Live", "Launch", "Production", "Rollout"],
                "color": "red"
            },
            "optimization": {
                "title": "Optimization & Enhancement Phase",
                "keywords": ["Optimization", "Enhancement", "Improvement", "Maintenance"],
                "color": "purple"
            }
        }
    
    def generate_cross_project_report(self, report_date: datetime = None) -> str:
        """
        Generate a cross-project milestone report covering all repositories
        
        Args:
            report_date: Date for the report (defaults to today)
            
        Returns:
            Path to generated PowerPoint file
        """
        if report_date is None:
            report_date = datetime.now()
        
        print(f"📊 Generating Cross-Project Milestone Report for {report_date.strftime('%B %Y')}")
        
        # Gather data from all repositories
        project_data = self._load_all_project_data(report_date)
        
        if not project_data:
            print("❌ No project data found across repositories")
            return None
        
        # Organize data by phases and repositories
        organized_data = self._organize_cross_project_data(project_data, report_date)
        
        # Generate PowerPoint presentation
        output_path = self._generate_cross_project_presentation(organized_data, report_date)
        
        return output_path
    
    def generate_repository_report(self, repository_name: str, report_date: datetime = None) -> str:
        """
        Generate a repository-specific milestone report
        
        Args:
            repository_name: Name of the repository
            report_date: Date for the report (defaults to today)
            
        Returns:
            Path to generated PowerPoint file
        """
        if report_date is None:
            report_date = datetime.now()
        
        print(f"📊 Generating {repository_name} Milestone Report for {report_date.strftime('%B %Y')}")
        
        # Load repository data
        repo_data = self._load_repository_data(repository_name, report_date)
        
        if not repo_data:
            print(f"❌ No data found for repository: {repository_name}")
            return None
        
        # Organize repository data
        organized_data = self._organize_repository_data(repo_data, report_date)
        
        # Generate PowerPoint presentation
        output_path = self._generate_repository_presentation(organized_data, report_date, repository_name)
        
        return output_path
    
    def _load_all_project_data(self, report_date: datetime) -> Dict[str, Any]:
        """Load milestone data from all repositories"""
        
        print("📋 Loading data from all repositories...")
        repositories = self.scanner.scan_all_repositories()
        
        all_data = {
            'repositories': {},
            'total_milestones': 0,
            'report_date': report_date
        }
        
        for repo_name, repo_info in repositories.items():
            print(f"   📂 Processing {repo_name}...")
            repo_data = self._load_repository_data(repo_name, report_date)
            if repo_data:
                all_data['repositories'][repo_name] = repo_data
                all_data['total_milestones'] += len(repo_data.get('milestones', []))
        
        print(f"📋 Loaded data from {len(all_data['repositories'])} repositories")
        print(f"📋 Total milestones: {all_data['total_milestones']}")
        
        return all_data
    
    def _load_repository_data(self, repository_name: str, report_date: datetime) -> Dict[str, Any]:
        """Load milestone data from a specific repository"""
        
        repo_info = self.scanner.get_repository_by_name(repository_name)
        if not repo_info:
            return None
        
        all_milestones = []
        
        for xml_file in repo_info['xml_files']:
            try:
                ms_project = MSProjectIntegration(xml_file)
                if ms_project.read_project_file():
                    
                    for task in ms_project.tasks:
                        if task.get('is_milestone', False):
                            milestone = {
                                'uid': task['uid'],
                                'name': task['name'],
                                'finish_date': self._parse_date(task['finish']),
                                'start_date': self._parse_date(task['start']),
                                'status': 'Complete' if task.get('percent_complete', 0) == 100 else 'Pending',
                                'resource': task.get('resource_names', 'Not assigned'),
                                'percent_complete': task.get('percent_complete', 0),
                                'source_file': Path(xml_file).name,
                                'repository': repository_name
                            }
                            all_milestones.append(milestone)
            
            except Exception as e:
                print(f"⚠️ Error loading {xml_file}: {e}")
        
        return {
            'repository_name': repository_name,
            'milestones': all_milestones,
            'xml_files': repo_info['xml_files'],
            'file_count': len(repo_info['xml_files'])
        }
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse MS Project date string"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00').split('T')[0])
        except:
            return None
    
    def _organize_cross_project_data(self, project_data: Dict, report_date: datetime) -> Dict[str, Any]:
        """Organize cross-project data by phases and time periods"""
        
        print("🔄 Organizing cross-project milestones...")
        
        # Calculate date ranges
        current_month_start = report_date.replace(day=1)
        current_month_end = report_date.replace(day=monthrange(report_date.year, report_date.month)[1])
        
        last_month = current_month_start - timedelta(days=1)
        last_month_start = last_month.replace(day=1)
        
        next_month_start = current_month_end + timedelta(days=1)
        next_month_end = next_month_start.replace(day=monthrange(next_month_start.year, next_month_start.month)[1])
        
        # Initialize organization structure
        organized = {
            'phases': {},
            'repositories': {},
            'summary': {
                'total_repositories': len(project_data['repositories']),
                'total_milestones': project_data['total_milestones'],
                'milestones_due_this_month': 0,
                'milestones_completed_last_month': 0,
                'milestones_due_next_month': 0
            },
            'report_date': report_date,
            'current_month_name': report_date.strftime('%B %Y'),
            'last_month_name': last_month.strftime('%B %Y'),
            'next_month_name': next_month_start.strftime('%B %Y')
        }
        
        # Initialize phases
        for phase_key, phase_info in self.default_phases.items():
            organized['phases'][phase_key] = {
                'title': phase_info['title'],
                'color': phase_info['color'],
                'milestones_due_this_month': [],
                'milestones_completed_last_month': [],
                'milestones_due_next_month': [],
                'repositories': set()
            }
        
        # Process all milestones
        for repo_name, repo_data in project_data['repositories'].items():
            organized['repositories'][repo_name] = {
                'milestones_due_this_month': [],
                'milestones_completed_last_month': [],
                'milestones_due_next_month': [],
                'total_milestones': len(repo_data['milestones'])
            }
            
            for milestone in repo_data['milestones']:
                finish_date = milestone['finish_date']
                
                # Determine phase
                phase = self._categorize_milestone_phase(milestone['name'])
                
                # Categorize by time period
                if finish_date:
                    # Due this month
                    if current_month_start <= finish_date <= current_month_end:
                        organized['phases'][phase]['milestones_due_this_month'].append(milestone)
                        organized['repositories'][repo_name]['milestones_due_this_month'].append(milestone)
                        organized['phases'][phase]['repositories'].add(repo_name)
                        organized['summary']['milestones_due_this_month'] += 1
                    
                    # Completed last month
                    elif (last_month_start <= finish_date <= last_month and 
                          milestone['status'] == 'Complete'):
                        organized['phases'][phase]['milestones_completed_last_month'].append(milestone)
                        organized['repositories'][repo_name]['milestones_completed_last_month'].append(milestone)
                        organized['phases'][phase]['repositories'].add(repo_name)
                        organized['summary']['milestones_completed_last_month'] += 1
                    
                    # Due next month
                    elif next_month_start <= finish_date <= next_month_end:
                        organized['phases'][phase]['milestones_due_next_month'].append(milestone)
                        organized['repositories'][repo_name]['milestones_due_next_month'].append(milestone)
                        organized['phases'][phase]['repositories'].add(repo_name)
                        organized['summary']['milestones_due_next_month'] += 1
        
        # Convert sets to lists for JSON serialization
        for phase_data in organized['phases'].values():
            phase_data['repositories'] = list(phase_data['repositories'])
        
        # Print summary
        print(f"📊 Cross-Project Summary:")
        print(f"   Repositories: {organized['summary']['total_repositories']}")
        print(f"   Total milestones: {organized['summary']['total_milestones']}")
        print(f"   Due this month: {organized['summary']['milestones_due_this_month']}")
        print(f"   Completed last month: {organized['summary']['milestones_completed_last_month']}")
        print(f"   Due next month: {organized['summary']['milestones_due_next_month']}")
        
        return organized
    
    def _organize_repository_data(self, repo_data: Dict, report_date: datetime) -> Dict[str, Any]:
        """Organize repository-specific data"""
        # Similar to cross-project but for single repository
        # Implementation would be similar to _organize_cross_project_data
        # but focused on single repository
        pass
    
    def _categorize_milestone_phase(self, milestone_name: str) -> str:
        """Categorize milestone into project phase based on name"""
        milestone_lower = milestone_name.lower()
        
        for phase_key, phase_info in self.default_phases.items():
            for keyword in phase_info['keywords']:
                if keyword.lower() in milestone_lower:
                    return phase_key
        
        return 'optimization'  # Default phase
    
    def _generate_cross_project_presentation(self, organized_data: Dict, report_date: datetime) -> str:
        """Generate cross-project PowerPoint presentation"""
        
        try:
            from pptx import Presentation
            from pptx.util import Inches, Pt
            from pptx.enum.text import PP_ALIGN
            
            print("📋 Creating cross-project PowerPoint presentation...")
            
            # Create new presentation
            prs = Presentation()
            
            # Title slide
            self._create_cross_project_title_slide(prs, report_date, organized_data)
            
            # Executive summary slide
            self._create_cross_project_summary_slide(prs, organized_data)
            
            # Repository overview slide
            self._create_repository_overview_slide(prs, organized_data)
            
            # Phase-specific slides
            for phase_key, phase_data in organized_data['phases'].items():
                if (phase_data['milestones_due_this_month'] or 
                    phase_data['milestones_completed_last_month'] or 
                    phase_data['milestones_due_next_month']):
                    
                    self._create_cross_project_phase_slide(prs, phase_key, phase_data, organized_data)
            
            # Save presentation
            timestamp = report_date.strftime('%d%m%Y')
            filename = f"Control_Tower_Cross_Project_Report_{timestamp}.pptx"
            output_path = self.output_path / filename
            
            prs.save(str(output_path))
            
            print(f"✅ Cross-project PowerPoint presentation saved: {output_path}")
            return str(output_path)
            
        except ImportError:
            print("❌ python-pptx not installed. Install with: pip install python-pptx")
            return None
        except Exception as e:
            print(f"❌ Error generating presentation: {e}")
            return None
    
    def _generate_repository_presentation(self, organized_data: Dict, report_date: datetime, repo_name: str) -> str:
        """Generate repository-specific PowerPoint presentation"""
        # Implementation similar to cross-project but focused on single repository
        pass
    
    def _create_cross_project_title_slide(self, prs, report_date: datetime, data: Dict):
        """Create cross-project title slide"""
        slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = "Control Tower Cross-Project Status"
        subtitle.text = f"Milestone Report - {report_date.strftime('%d/%m/%Y')}\n{data['summary']['total_repositories']} Repositories • {data['summary']['total_milestones']} Milestones"
    
    def _create_cross_project_summary_slide(self, prs, data: Dict):
        """Create cross-project executive summary slide"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        title.text = "Executive Summary"
        
        content = slide.placeholders[1].text_frame
        content.text = f"Cross-Project Status Overview - {data['current_month_name']}"
        
        # Add summary points
        p = content.add_paragraph()
        p.text = f"• Active Repositories: {data['summary']['total_repositories']}"
        
        p = content.add_paragraph()
        p.text = f"• Total Milestones Tracked: {data['summary']['total_milestones']}"
        
        p = content.add_paragraph()
        p.text = f"• Milestones Due This Month: {data['summary']['milestones_due_this_month']}"
        
        p = content.add_paragraph()
        p.text = f"• Milestones Completed Last Month: {data['summary']['milestones_completed_last_month']}"
        
        p = content.add_paragraph()
        p.text = f"• Milestones Due Next Month: {data['summary']['milestones_due_next_month']}"
    
    def _create_repository_overview_slide(self, prs, data: Dict):
        """Create repository overview slide"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        title.text = "Repository Overview"
        
        content = slide.placeholders[1].text_frame
        content.text = f"Project Status by Repository:"
        
        for repo_name, repo_data in data['repositories'].items():
            p = content.add_paragraph()
            due_count = len(repo_data['milestones_due_this_month'])
            total_count = repo_data['total_milestones']
            status_icon = "🟢" if due_count == 0 else "🟡" if due_count <= 3 else "🔴"
            p.text = f"{status_icon} {repo_name}: {due_count}/{total_count} due this month"
    
    def _create_cross_project_phase_slide(self, prs, phase_key: str, phase_data: Dict, organized_data: Dict):
        """Create a slide for a specific project phase across all repositories"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        title.text = phase_data['title']
        
        content = slide.placeholders[1].text_frame
        content.clear()
        
        # Show which repositories are involved
        if phase_data['repositories']:
            p = content.add_paragraph()
            p.text = f"Active Repositories: {', '.join(phase_data['repositories'])}"
            p.font.bold = True
        
        # Milestones due this month
        if phase_data['milestones_due_this_month']:
            p = content.add_paragraph()
            p.text = f"\nMilestones Due {organized_data['current_month_name']}:"
            p.font.bold = True
            
            for milestone in phase_data['milestones_due_this_month'][:5]:  # Show first 5
                p = content.add_paragraph()
                p.level = 1
                date_str = milestone['finish_date'].strftime('%d/%m/%Y') if milestone['finish_date'] else 'No date'
                status_icon = "✅" if milestone['status'] == 'Complete' else "⏳"
                p.text = f"{status_icon} {milestone['name'][:40]}... ({milestone['repository']}) - {date_str}"
        
        # Similar blocks for completed last month and due next month...

def main():
    """Main function for command line usage"""
    
    print("🚀 CONTROL TOWER POWERPOINT GENERATOR")
    print("="*60)
    
    generator = PowerPointGenerator()
    
    # Generate cross-project report
    report_path = generator.generate_cross_project_report()
    
    if report_path:
        print(f"\n📧 REPORT GENERATED SUCCESSFULLY!")
        print(f"📁 Location: {report_path}")
        print(f"\n📊 NEXT STEPS:")
        print(f"1. Review the generated cross-project presentation")
        print(f"2. Generate repository-specific reports as needed")
        print(f"3. Export to PDF for distribution")
        print(f"4. Set up automated generation schedule")
    else:
        print("❌ Failed to generate report")

if __name__ == "__main__":
    main()
