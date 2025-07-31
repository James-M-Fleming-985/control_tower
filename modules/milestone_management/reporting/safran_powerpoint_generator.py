#!/usr/bin/env python3
"""
Safran PowerPoint Generator for Control Tower
Creates professional Safran-branded presentations matching manual format

PHASE 1: Format & Layout Foundation
- Implements exact visual format from manual example
- 4-table layout per page
- Safran branding and logos
- Professional styling

PHASE 2: Data Integration (future)
- Connect to control tower data sources
- Populate with real milestone/task data
"""

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from calendar import monthrange

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Cm
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.dml.color import RGBColor
    from pptx.enum.dml import MSO_THEME_COLOR
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

class SafranPowerPointGenerator:
    """
    Generates Safran-branded PowerPoint presentations matching the manual format
    Focus: First 12 pages with project data from control tower
    
    ORGANIZATION STRUCTURE:
    - Generator scripts: Located in Control Tower /reports (this file)
    - Generated presentations: Saved to each repo's /powerpoint_reports folder
    - Control Tower generates presentations for ALL repos in their respective powerpoint_reports folders
    """
    
    def __init__(self, output_path: str = None, repo_name: str = "contract_projects"):
        """Initialize the Safran PowerPoint generator"""
        self.repo_name = repo_name
        
        # Set correct output path based on repository structure
        if output_path is None:
            if repo_name == "contract_projects":
                # Safran presentations go to the Safran organization folder
                output_path = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/powerpoint_reports"
            else:
                # Other repositories use their main powerpoint_reports folder
                output_path = f"/workspaces/control_tower/cloned_repos/{repo_name}/powerpoint_reports"
        
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Repository-specific XML file mapping
        repo_xml_files = {
            "contract_projects": "ZnNi Line Development Plan-08.xml",  # Safran-specific
            "domain_specific-network_dev": "Network Development Plan.xml",
            "financial_optimizer": "Financial Optimization Project.xml",
            "financial_security_dev": "Financial Security Project.xml",
            "home_improvements": "Home Improvement Projects.xml",
            "LIMS_concept_actual": "LIMS Implementation Plan.xml",  # Independent LIMS project
            "opti_royale": "Optimization Royale Project.xml",
            "relationship_building": "Relationship Building Plan.xml"
        }
        
        # Get the appropriate XML file for this repository
        xml_filename = repo_xml_files.get(repo_name, "project_plan.xml")
        self.xml_file_path = f"/workspaces/control_tower/cloned_repos/{repo_name}/xml_workspace/{xml_filename}"
        
        # Verify XML file exists
        if not os.path.exists(self.xml_file_path):
            print(f"⚠️  Repository-specific XML file not found: {self.xml_file_path}")
            print(f"Creating sample project data for {repo_name}...")
            self._create_sample_xml_data(repo_name, xml_filename)
        
        # Safran brand colors (based on typical corporate colors)
        self.safran_colors = {
            'primary_blue': RGBColor(0, 82, 155),      # Safran primary blue
            'secondary_blue': RGBColor(51, 122, 183),   # Light blue
            'accent_orange': RGBColor(255, 120, 0),     # Safran orange
            'dark_gray': RGBColor(64, 64, 64),          # Text gray
            'light_gray': RGBColor(128, 128, 128),      # Secondary text
            'white': RGBColor(255, 255, 255),           # White
            'table_header': RGBColor(240, 240, 240),    # Table header background
            'green': RGBColor(0, 128, 0),               # Progress green
            'progress_bg': RGBColor(230, 230, 230),     # Progress background
            'red': RGBColor(200, 0, 0)                  # Status red
        }
        
        # Safran project phases (from directory structure)
        self.safran_phases = {
            'phase1': {
                'title': 'ZnNi Line Stabilization - Critical Documentation and Training',
                'short_name': 'Documentation & Training',
                'directory': '1_ZnNi_Line_Stabilization_Critical_Documentation_and_Training',
                'name': 'Documentation & Training'
            },
            'phase2': {
                'title': 'ZnNi Line Stabilization - Critical Maintenance',
                'short_name': 'Critical Maintenance',
                'directory': '2_ZnNi_Line_Stabilization_Critical_Maintenance',
                'name': 'Critical Maintenance'
            },
            'phase3': {
                'title': 'ZnNi Line Post Stabilization Optimization',
                'short_name': 'Post Stabilization Optimization',
                'directory': '3_ZnNi_Line_Post_Stabilization_Optimization',
                'name': 'Post Stabilization Optimization'
            }
        }
    
    def _create_sample_xml_data(self, repo_name: str, xml_filename: str):
        """Create meaningful sample XML data for repository-specific presentations"""
        
        # Repository-specific project data
        repo_projects = {
            "financial_optimizer": {
                "title": "Financial Optimization Platform",
                "phases": [
                    {"name": "Market Analysis & Requirements", "progress": 85, "start_days": 0, "duration": 30},
                    {"name": "Algorithm Development", "progress": 65, "start_days": 20, "duration": 45},
                    {"name": "Portfolio Optimization Engine", "progress": 40, "start_days": 45, "duration": 35},
                    {"name": "Risk Assessment Module", "progress": 25, "start_days": 60, "duration": 40},
                    {"name": "User Interface Development", "progress": 15, "start_days": 80, "duration": 30},
                    {"name": "Integration & Testing", "progress": 5, "start_days": 100, "duration": 25}
                ]
            },
            "domain_specific-network_dev": {
                "title": "Network Development Infrastructure",
                "phases": [
                    {"name": "Network Architecture Design", "progress": 90, "start_days": 0, "duration": 25},
                    {"name": "Security Framework Implementation", "progress": 70, "start_days": 15, "duration": 40},
                    {"name": "Load Balancing Configuration", "progress": 45, "start_days": 35, "duration": 30},
                    {"name": "Monitoring System Setup", "progress": 30, "start_days": 50, "duration": 35},
                    {"name": "Performance Optimization", "progress": 10, "start_days": 70, "duration": 25},
                    {"name": "Documentation & Training", "progress": 0, "start_days": 85, "duration": 20}
                ]
            },
            "LIMS_concept_actual": {
                "title": "Laboratory Information Management System",
                "phases": [
                    {"name": "LIMS Requirements Analysis", "progress": 95, "start_days": 0, "duration": 20},
                    {"name": "Sample Tracking Module", "progress": 75, "start_days": 15, "duration": 35},
                    {"name": "Quality Control Workflows", "progress": 55, "start_days": 30, "duration": 40},
                    {"name": "Reporting & Analytics", "progress": 35, "start_days": 50, "duration": 30},
                    {"name": "Integration with Lab Equipment", "progress": 20, "start_days": 65, "duration": 35},
                    {"name": "Validation & Compliance", "progress": 5, "start_days": 85, "duration": 25}
                ]
            },
            "home_improvements": {
                "title": "Smart Home Improvement Platform",
                "phases": [
                    {"name": "Home Assessment Tools", "progress": 80, "start_days": 0, "duration": 30},
                    {"name": "Project Planning System", "progress": 60, "start_days": 20, "duration": 35},
                    {"name": "Contractor Network Integration", "progress": 40, "start_days": 40, "duration": 40},
                    {"name": "Cost Estimation Engine", "progress": 25, "start_days": 60, "duration": 30},
                    {"name": "Timeline Management", "progress": 15, "start_days": 75, "duration": 25},
                    {"name": "Quality Tracking & Reviews", "progress": 0, "start_days": 90, "duration": 20}
                ]
            },
            "opti_royale": {
                "title": "Optimization Royale Gaming Platform",
                "phases": [
                    {"name": "Game Engine Development", "progress": 85, "start_days": 0, "duration": 40},
                    {"name": "Multiplayer Infrastructure", "progress": 65, "start_days": 25, "duration": 45},
                    {"name": "Optimization Algorithms", "progress": 50, "start_days": 45, "duration": 35},
                    {"name": "User Interface & Experience", "progress": 30, "start_days": 60, "duration": 40},
                    {"name": "Leaderboard & Scoring", "progress": 20, "start_days": 80, "duration": 25},
                    {"name": "Beta Testing & Launch", "progress": 5, "start_days": 95, "duration": 30}
                ]
            },
            "relationship_building": {
                "title": "Professional Relationship Management",
                "phases": [
                    {"name": "Contact Management System", "progress": 90, "start_days": 0, "duration": 25},
                    {"name": "Communication Tracking", "progress": 70, "start_days": 15, "duration": 35},
                    {"name": "Relationship Analytics", "progress": 50, "start_days": 35, "duration": 30},
                    {"name": "Automated Follow-up System", "progress": 35, "start_days": 50, "duration": 35},
                    {"name": "Integration with CRM Tools", "progress": 20, "start_days": 70, "duration": 30},
                    {"name": "Reporting & Insights", "progress": 10, "start_days": 85, "duration": 25}
                ]
            },
            "financial_security_dev": {
                "title": "Financial Security Development Suite",
                "phases": [
                    {"name": "Security Architecture Design", "progress": 85, "start_days": 0, "duration": 30},
                    {"name": "Encryption Implementation", "progress": 70, "start_days": 20, "duration": 40},
                    {"name": "Fraud Detection System", "progress": 50, "start_days": 40, "duration": 45},
                    {"name": "Compliance Framework", "progress": 30, "start_days": 65, "duration": 35},
                    {"name": "Audit Trail System", "progress": 15, "start_days": 80, "duration": 30},
                    {"name": "Security Testing & Validation", "progress": 5, "start_days": 100, "duration": 25}
                ]
            }
        }
        
        # Get project data for this repository
        project_data = repo_projects.get(repo_name, {
            "title": f"{repo_name.replace('_', ' ').title()} Project",
            "phases": [
                {"name": "Planning & Analysis", "progress": 75, "start_days": 0, "duration": 30},
                {"name": "Development Phase 1", "progress": 45, "start_days": 20, "duration": 40},
                {"name": "Development Phase 2", "progress": 25, "start_days": 45, "duration": 35},
                {"name": "Testing & Quality Assurance", "progress": 10, "start_days": 70, "duration": 25},
                {"name": "Deployment & Launch", "progress": 0, "start_days": 85, "duration": 20}
            ]
        })
        
        # Create the XML content
        base_date = datetime.now()
        xml_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Project xmlns="http://schemas.microsoft.com/project">
    <Name>{project_data["title"]}</Name>
    <Title>{project_data["title"]} Development Plan</Title>
    <CreationDate>{base_date.isoformat()}</CreationDate>
    <LastSaved>{base_date.isoformat()}</LastSaved>
    <Tasks>'''
        
        # Add project overview
        xml_content += f'''
        <Task>
            <UID>1</UID>
            <ID>1</ID>
            <Name>{project_data["title"]} Overview</Name>
            <Type>1</Type>
            <IsNull>0</IsNull>
            <CreateDate>{base_date.isoformat()}</CreateDate>
            <Start>{base_date.isoformat()}</Start>
            <Finish>{(base_date + timedelta(days=120)).isoformat()}</Finish>
            <PercentComplete>0</PercentComplete>
            <OutlineLevel>1</OutlineLevel>
        </Task>'''
        
        # Add phases as tasks
        task_id = 2
        for phase in project_data["phases"]:
            start_date = base_date + timedelta(days=phase["start_days"])
            end_date = start_date + timedelta(days=phase["duration"])
            
            # Escape any special characters in phase name
            phase_name = phase["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            xml_content += f'''
        <Task>
            <UID>{task_id}</UID>
            <ID>{task_id}</ID>
            <Name>{phase_name}</Name>
            <Type>1</Type>
            <IsNull>0</IsNull>
            <CreateDate>{base_date.isoformat()}</CreateDate>
            <Start>{start_date.isoformat()}</Start>
            <Finish>{end_date.isoformat()}</Finish>
            <PercentComplete>{int(phase["progress"])}</PercentComplete>
            <OutlineLevel>2</OutlineLevel>
        </Task>'''
            task_id += 1
        
        xml_content += '''
    </Tasks>
</Project>'''
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.xml_file_path), exist_ok=True)
        
        # Write the XML file
        with open(self.xml_file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"✅ Created sample XML data for {repo_name}")
        print(f"📊 Project: {project_data['title']}")
        print(f"📋 Phases: {len(project_data['phases'])} development phases")
        print(f"💾 Saved to: {self.xml_file_path}")
    
    def _parse_xml_data(self):
        """Parse MS Project XML data and extract project information"""
        try:
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()
            
            # MS Project XML namespace
            namespace = {'ms': 'http://schemas.microsoft.com/project'}
            
            projects = []
            
            # Find the Tasks element and iterate through Task children
            tasks_element = root.find('.//ms:Tasks', namespace)
            if tasks_element is None:
                print("❌ No Tasks element found in XML")
                return []
            
            print(f"📋 Found {len(list(tasks_element))} tasks in XML for {self.repo_name}")
            
            # First pass: collect all tasks with their hierarchy and parent relationships
            all_tasks = []
            task_hierarchy = {}  # Store task ID to parent relationships
            
            for task in tasks_element:
                try:
                    # Extract task information using namespace
                    task_id = task.find('ms:ID', namespace)
                    task_name = task.find('ms:Name', namespace)
                    task_start = task.find('ms:Start', namespace)
                    task_finish = task.find('ms:Finish', namespace)
                    task_percent_complete = task.find('ms:PercentComplete', namespace)
                    task_outline_level = task.find('ms:OutlineLevel', namespace)
                    
                    # Skip if required fields are missing
                    if task_name is None or task_name.text is None or task_id is None:
                        continue
                        
                    name = task_name.text.strip()
                    if not name or name in ['', 'Summary Task']:
                        continue
                    
                    # Parse dates
                    start_date = None
                    finish_date = None
                    if task_start is not None and task_start.text:
                        try:
                            start_date = datetime.fromisoformat(task_start.text.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    if task_finish is not None and task_finish.text:
                        try:
                            finish_date = datetime.fromisoformat(task_finish.text.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    # Parse progress
                    progress = 0.0
                    if task_percent_complete is not None and task_percent_complete.text:
                        try:
                            progress = float(task_percent_complete.text)
                            if progress > 100:
                                progress = progress / 100.0 * 100
                        except:
                            progress = 0.0
                    
                    # Parse outline level
                    outline_level = 1
                    if task_outline_level is not None and task_outline_level.text:
                        try:
                            outline_level = int(task_outline_level.text)
                        except:
                            outline_level = 1
                    
                    task_data = {
                        'id': task_id.text,
                        'name': name,
                        'start_date': start_date,
                        'finish_date': finish_date,
                        'progress': progress,
                        'outline_level': outline_level,
                        'parent_path': [],  # Will be populated with parent hierarchy
                        'phase': None  # Will be determined from XML hierarchy
                    }
                    
                    all_tasks.append(task_data)
                    task_hierarchy[task_id.text] = task_data
                    
                except Exception as e:
                    print(f"Error parsing task: {e}")
                    continue
            
            # Second pass: determine phase from XML hierarchy (parent-child relationships)
            for task in all_tasks:
                task['phase'] = self._determine_phase_from_hierarchy(task, all_tasks)
            
            print(f"📊 Parsed {len(all_tasks)} projects from {self.repo_name} XML")
            return all_tasks
            
        except Exception as e:
            print(f"❌ Error parsing XML file: {e}")
            return []
    
    def _determine_phase_from_hierarchy(self, task: dict, all_tasks: list) -> str:
        """Determine phase assignment based on actual XML hierarchy structure"""
        
        # For contract_projects (Safran), use XML hierarchy to determine phase
        if self.repo_name == "contract_projects":
            return self._determine_safran_phase_from_hierarchy(task, all_tasks)
        
        # For other repositories, use the original keyword-based logic
        return self._determine_phase_from_keywords(task['name'])
    
    def _determine_safran_phase_from_hierarchy(self, task: dict, all_tasks: list) -> str:
        """Determine Safran phase based on XML hierarchy structure"""
        
        task_name = task['name'].lower()
        current_level = task['outline_level']
        
        # Level 1: Project Overview (skip)
        if current_level == 1:
            return None  # Skip Level 1 project containers
        
        # Level 2: Main project sections (skip)  
        if current_level == 2:
            return None  # Skip Level 2 stabilization containers
        
        # Direct phase assignment for Level 3 main phase containers
        if current_level == 3:
            if ('critical documentation' in task_name and 'set in place' in task_name):
                return 'Documentation & Training'
            elif 'sf investment strategy' in task_name:
                return 'Documentation & Training'  
            elif 'critical maintenance' in task_name:
                return 'Critical Maintenance'
            elif 'post stabilization optimization' in task_name:
                return 'Post Stabilization Optimization'
        
        # For Level 4 tasks, determine phase by finding their Level 3 parent
        if current_level == 4:
            # Find the most recent Level 3 task that appears before this task in the XML order
            # This represents the hierarchical parent in MS Project structure
            current_task_id = int(task.get('id', '0'))
            
            # Find all Level 3 tasks that come before this Level 4 task
            level3_parent = None
            for potential_parent in sorted(all_tasks, key=lambda x: int(x.get('id', '0'))):
                if (potential_parent['outline_level'] == 3 and 
                    int(potential_parent.get('id', '0')) < current_task_id):
                    level3_parent = potential_parent  # Keep updating to get the most recent one
            
            if level3_parent:
                parent_name = level3_parent['name'].lower()
                
                # Debug output for troubleshooting
                print(f"🔍 Level 4 task '{task['name']}' (ID: {task['id']}) → Level 3 parent '{level3_parent['name']}' (ID: {level3_parent['id']})")
                
                if ('critical documentation' in parent_name and 'set in place' in parent_name):
                    print(f"   ✅ Assigned to: Documentation & Training")
                    return 'Documentation & Training'
                elif 'sf investment strategy' in parent_name:
                    print(f"   ✅ Assigned to: Documentation & Training")
                    return 'Documentation & Training'
                elif 'critical maintenance' in parent_name:
                    print(f"   ✅ Assigned to: Critical Maintenance")
                    return 'Critical Maintenance' 
                elif ('flow rate optimization' in parent_name or 'kardex optimization' in parent_name or 
                      'chiller system optimization' in parent_name or 'asset management optimization' in parent_name or
                      ('operational documentation' in parent_name and 'optimization' in parent_name) or
                      'sf operational documentation' in parent_name or 'sf documentation' in parent_name or
                      'lims roll out' in parent_name or 'optimization' in parent_name):
                    print(f"   ✅ Assigned to: Post Stabilization Optimization")
                    return 'Post Stabilization Optimization'
                else:
                    print(f"   ⚠️  Parent '{parent_name}' doesn't match any phase keywords")
        
        # Fallback: Use task name keywords for direct assignment
        if any(keyword in task_name for keyword in ['critical documentation', 'sf investment', 'training', 'analysis']):
            return 'Documentation & Training'
        elif any(keyword in task_name for keyword in ['critical maintenance', 'vat', 'remove', 'install', 'maintenance']):
            return 'Critical Maintenance'
        elif any(keyword in task_name for keyword in ['optimization', 'flow rate', 'kardex', 'chiller', 'lims', 'sf operational', 'sf documentation']):
            return 'Post Stabilization Optimization'
        
        # Final fallback with debug
        print(f"⚠️  Using fallback for task '{task['name']}' (Level {current_level})")
        return 'Documentation & Training'
    
    def _determine_phase_from_keywords(self, task_name: str) -> str:
        """Fallback keyword-based phase determination for non-Safran repositories"""
        name_lower = task_name.lower()
        
        if any(word in name_lower for word in ['planning', 'analysis', 'requirements', 'design', 'architecture', 'documentation']):
            return 'Documentation & Training'
        elif any(word in name_lower for word in ['development', 'implementation', 'configuration', 'setup', 'integration', 'maintenance']):
            return 'Critical Maintenance'
        elif any(word in name_lower for word in ['testing', 'optimization', 'validation', 'deployment', 'launch']):
            return 'Post Stabilization Optimization'
        
        return 'Documentation & Training'
    
    def _get_projects_for_phase(self, phase: str, projects: list) -> list:
        """Get in-progress Level 4 projects for a specific phase (0% < progress < 100%)"""
        phase_projects = []
        
        # Focus on Level 4 projects only - these are the actual work items
        # Level 4: Detailed project implementations (where actual work happens)
        target_levels = [4]  # Level 4 only for executive reporting focus
        
        # Debug: Show all projects being considered for this phase
        print(f"🔍 Getting projects for phase '{phase}' (Target levels: {target_levels})")
        
        for project in projects:
            # Include Level 4 in-progress projects only
            if (project['phase'] == phase and 
                project['outline_level'] in target_levels and
                project['progress'] > 0 and 
                project['progress'] < 100):
                
                # Include all in-progress projects regardless of date data availability
                phase_projects.append(project)
                print(f"   ✅ Including: {project['name']} (Level {project['outline_level']}, Phase: {project['phase']}, {project['progress']:.0f}%)")
                
                # Warn if dates are missing but still include the project
                if not project['start_date'] or not project['finish_date']:
                    print(f"       ⚠️  Missing dates but included for comprehensive reporting")
        
        # Sort by start date (with fallback for projects without dates)
        def sort_key(project):
            if project['start_date']:
                return project['start_date']
            else:
                # Put projects without dates at the end
                return datetime(2099, 12, 31)
        
        phase_projects.sort(key=sort_key)
        return phase_projects
    
    def generate_safran_presentation(self, report_date: datetime = None) -> str:
        """
        Generate Safran presentation matching manual format (first 12 pages)
        
        Args:
            report_date: Date for the report (defaults to today)
            
        Returns:
            Path to generated PowerPoint file
        """
        if not PPTX_AVAILABLE:
            print("❌ python-pptx not installed. Install with: pip install python-pptx")
            return None
        
        if report_date is None:
            report_date = datetime.now()
        
        print(f"📊 Generating Safran PowerPoint Report for {report_date.strftime('%B %Y')}")
        print("🎨 PHASE 1: Implementing Format & Layout Foundation")
        
        try:
            # Create new presentation
            prs = Presentation()
            
            # Generate the 12 core pages following the 4-slide pattern per phase
            
            # Phase-specific slides (3 phases × 4 slides each = 12 slides)
            for phase_key, phase_info in self.safran_phases.items():
                self._create_phase_title_slide(prs, phase_info, report_date)        # Slides 1, 5, 9
                self._create_phase_timeline_slide(prs, phase_info, report_date)     # Slides 2, 6, 10
                self._create_phase_four_table_slide(prs, phase_info, report_date)   # Slides 3, 7, 11
                self._create_phase_change_mgmt_slide(prs, phase_info, report_date)  # Slides 4, 8, 12
            
            # Save presentation
            timestamp = report_date.strftime('%d%m%Y')
            filename = f"REACh_ZnNi_Line_Flash_Report_{timestamp}_ControlTower.pptx"
            output_path = self.output_path / filename
            
            prs.save(str(output_path))
            
            print(f"✅ Safran PowerPoint presentation saved: {output_path}")
            print(f"📄 Generated 12 pages matching manual format")
            print(f"🎯 Ready for manual slide append workflow")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Error generating Safran presentation: {e}")
            return None
    
    def _create_phase_title_slide(self, prs, phase_info: Dict, report_date: datetime):
        """Create phase title slide (Pattern: Slide 1, 5, 9)"""
        print(f"📄 Creating phase title slide: {phase_info['short_name']}...")
        
        slide_layout = prs.slide_layouts[6]  # Blank layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Add Safran header
        self._add_safran_header(slide)
        
        # Phase title with "SLS SF" prefix - centered and properly spaced for two lines
        title_box = slide.shapes.add_textbox(
            Inches(1), Inches(2.2), Inches(8), Inches(2.0)  # Increased height for two lines
        )
        title_frame = title_box.text_frame
        
        # Split long titles into two lines for better readability
        full_title = f"SLS SF {phase_info['title']}"
        if len(full_title) > 50:  # Split long titles
            # Find a good break point
            words = full_title.split()
            mid_point = len(words) // 2
            line1 = " ".join(words[:mid_point])
            line2 = " ".join(words[mid_point:])
            title_frame.text = f"{line1}\n{line2}"
        else:
            title_frame.text = full_title
            
        self._apply_title_style(title_frame.paragraphs[0])
        
        # Apply centering to all paragraphs in title
        for paragraph in title_frame.paragraphs:
            paragraph.alignment = PP_ALIGN.CENTER
            paragraph.font.size = Pt(22)  # Slightly smaller for two-line titles
            paragraph.font.bold = True
            paragraph.font.color.rgb = self.safran_colors['primary_blue']
        
        # Phase identifier - better positioned
        phase_box = slide.shapes.add_textbox(
            Inches(1), Inches(4.8), Inches(8), Inches(0.5)
        )
        phase_frame = phase_box.text_frame
        phase_frame.text = f"Phase: {phase_info['short_name']}"
        phase_frame.paragraphs[0].font.size = Pt(16)
        phase_frame.paragraphs[0].font.color.rgb = self.safran_colors['accent_orange']
        phase_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    def _create_phase_timeline_slide(self, prs, phase_info: Dict, report_date: datetime):
        """Create timeline graphic slide from MS Project XML (Pattern: Slide 2, 6, 10)"""
        print(f"📄 Creating timeline graphic: {phase_info['short_name']}...")
        
        slide_layout = prs.slide_layouts[6]  # Blank layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Add Safran header
        self._add_safran_header(slide)
        
        # Move title into blue banner to save space for timeline
        banner_title_box = slide.shapes.add_textbox(
            Inches(3), Inches(0.1), Inches(4), Inches(0.6)
        )
        banner_title_frame = banner_title_box.text_frame
        banner_title_frame.text = f"Timeline: {phase_info['short_name']}"
        banner_title_frame.paragraphs[0].font.size = Pt(14)
        banner_title_frame.paragraphs[0].font.bold = True
        banner_title_frame.paragraphs[0].font.color.rgb = self.safran_colors['white']
        banner_title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # Parse XML data and get projects for this phase
        all_projects = self._parse_xml_data()
        # Filter out None phases (Level 1 and 2 containers)
        all_projects = [p for p in all_projects if p['phase'] is not None]
        phase_projects = self._get_projects_for_phase(phase_info['name'], all_projects)
        
        # Debug output to show filtering results
        print(f"🎯 Timeline for {phase_info['name']}: Found {len(phase_projects)} projects (Level 4 only)")
        print(f"   Using Level 4 filtering for focused executive reporting")
        
        # Show specific projects being included
        for i, project in enumerate(phase_projects[:5]):
            print(f"   {i+1}. {project['name']} (Level {project['outline_level']}, {project['progress']:.0f}%)")
        
        if len(phase_projects) > 5:
            print(f"   ... and {len(phase_projects) - 5} more projects")
        
        # Create visual timeline with progress bars - now with consistent formatting
        self._create_visual_timeline(slide, phase_projects, phase_info)
    
    def _create_visual_timeline(self, slide, projects: list, phase_info: Dict):
        """Create visual timeline with progress bars for projects"""
        start_y = Inches(2.2)
        timeline_height = Inches(4)
        timeline_width = Inches(9)
        start_x = Inches(0.5)
        
        # Calculate date range for timeline scaling
        if not projects:
            return
            
    def _create_visual_timeline(self, slide, projects: list, phase_info: Dict):
        """Create visual timeline with progress bars for projects - properly positioned and sized with consistent borders"""
        
        # Create a bordered container for the timeline with consistent dimensions
        container_x = Inches(0.5)
        container_y = Inches(2.0)
        container_width = Inches(9.0)
        container_height = Inches(4.5)
        
        # Add timeline container border for consistency
        timeline_border = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            container_x, container_y,
            container_width, container_height
        )
        timeline_border.fill.background()  # Transparent fill
        timeline_border.line.color.rgb = self.safran_colors['dark_gray']
        timeline_border.line.width = Pt(2)
        
        # Timeline content area (inside the border)
        content_x = container_x + Inches(0.1)
        content_y = container_y + Inches(0.1)
        content_width = container_width - Inches(0.2)
        content_height = container_height - Inches(0.2)
        
        # Calculate date range for timeline scaling
        if not projects:
            # Add "No data" message in center of container
            no_data_box = slide.shapes.add_textbox(
                content_x, content_y + Inches(2), content_width, Inches(0.5)
            )
            no_data_frame = no_data_box.text_frame
            no_data_frame.text = f"No in-progress projects found for {phase_info['short_name']}"
            no_data_frame.paragraphs[0].font.size = Pt(14)
            no_data_frame.paragraphs[0].font.color.rgb = self.safran_colors['light_gray']
            no_data_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            return
            
        # Separate projects with and without dates
        projects_with_dates = [p for p in projects if p['start_date'] and p['finish_date']]
        projects_without_dates = [p for p in projects if not (p['start_date'] and p['finish_date'])]
        
        if projects_with_dates:
            # Create timeline for projects with dates
            all_start_dates = [p['start_date'] for p in projects_with_dates]
            all_end_dates = [p['finish_date'] for p in projects_with_dates]
            
            timeline_start = min(all_start_dates)
            timeline_end = max(all_end_dates)
            total_days = (timeline_end - timeline_start).days + 1
            
            if total_days > 0:
                # Add timeline header with date range - properly positioned within container
                header_box = slide.shapes.add_textbox(
                    content_x, content_y, content_width, Inches(0.3)
                )
                header_frame = header_box.text_frame
                header_frame.text = f"Timeline: {timeline_start.strftime('%m/%d/%Y')} to {timeline_end.strftime('%m/%d/%Y')} ({total_days} days)"
                header_frame.paragraphs[0].font.size = Pt(12)
                header_frame.paragraphs[0].font.color.rgb = self.safran_colors['dark_gray']
                header_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
                
                # Draw timeline projects with dates within the content area
                timeline_area_y = content_y + Inches(0.4)
                timeline_area_height = Inches(3.0)
                self._draw_timeline_projects_with_dates(
                    slide, projects_with_dates, timeline_start, timeline_end, total_days, 
                    content_x, timeline_area_y, content_width, timeline_area_height
                )
        
        # Add projects without dates as a simple list at bottom of container
        if projects_without_dates:
            list_y = content_y + Inches(3.5) if projects_with_dates else content_y + Inches(0.5)
            available_height = (content_y + content_height) - list_y - Inches(0.1)
            self._draw_projects_without_dates(slide, projects_without_dates, content_x, list_y, content_width, available_height)
        
        # Add legend at bottom of container
        legend_y = content_y + content_height - Inches(0.4)
        self._add_timeline_legend(slide, content_x, legend_y, content_width)
    
    def _draw_timeline_projects_with_dates(self, slide, projects, timeline_start, timeline_end, total_days, content_x, content_y, content_width, content_height):
        """Draw projects with valid dates on the timeline within constrained area"""
        project_height = Inches(0.35)
        spacing = Inches(0.45)
        max_projects = min(len(projects), int(content_height.inches / spacing.inches))  # Fit within available space
        
        for i, project in enumerate(projects[:max_projects]):
            y_position = content_y + i * spacing
            
            # Calculate project timeline position and width
            project_start_days = (project['start_date'] - timeline_start).days
            project_duration_days = (project['finish_date'] - project['start_date']).days + 1
            
            # Timeline bar background (full project duration) - constrained within content area
            bar_x = content_x + Inches(3.5) + (project_start_days / total_days) * Inches(5.0)  # Reserve space for labels
            bar_width = (project_duration_days / total_days) * Inches(5.0)
            
            # Ensure bar stays within content area
            max_bar_x = content_x + content_width - Inches(1.0)  # Reserve space for percentage
            if bar_x + bar_width > max_bar_x:
                bar_width = max_bar_x - bar_x
            
            # Ensure minimum visibility
            if bar_width < Inches(0.1):
                bar_width = Inches(0.1)
            
            self._draw_project_timeline_bar_constrained(slide, project, bar_x, y_position, bar_width, project_height, content_x, content_width)
    
    def _draw_projects_without_dates(self, slide, projects, content_x, content_y, content_width, available_height):
        """Draw projects without dates as a simple progress list within constrained area"""
        if not projects or available_height < Inches(0.5):
            return
            
        # Header for projects without timeline data
        header_box = slide.shapes.add_textbox(
            content_x, content_y, content_width, Inches(0.25)
        )
        header_frame = header_box.text_frame
        header_frame.text = "Additional Projects (dates pending):"
        header_frame.paragraphs[0].font.size = Pt(10)
        header_frame.paragraphs[0].font.color.rgb = self.safran_colors['dark_gray']
        header_frame.paragraphs[0].font.bold = True
        
        # List projects without dates
        list_y = content_y + Inches(0.3)
        item_height = Inches(0.25)
        max_projects = min(len(projects), int((available_height.inches - 0.3) / item_height.inches))
        
        for i, project in enumerate(projects[:max_projects]):
            project_y = list_y + i * item_height
            
            project_box = slide.shapes.add_textbox(
                content_x + Inches(0.1), project_y, content_width - Inches(0.2), item_height
            )
            project_frame = project_box.text_frame
            # Truncate project names to fit in constrained area
            project_name = project['name'][:45] + "..." if len(project['name']) > 45 else project['name']
            project_frame.text = f"• {project_name} ({project['progress']:.0f}%)"
            project_frame.paragraphs[0].font.size = Pt(9)
            project_frame.paragraphs[0].font.color.rgb = self.safran_colors['dark_gray']
    
    def _draw_project_timeline_bar_constrained(self, slide, project, bar_x, y_position, bar_width, project_height, content_x, content_width):
        """Draw individual project timeline bar with progress within constrained area"""
        # Background bar (gray)
        bg_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            int(bar_x), int(y_position),
            int(bar_width), int(project_height)
        )
        bg_bar.fill.solid()
        bg_bar.fill.fore_color.rgb = self.safran_colors['progress_bg']
        bg_bar.line.color.rgb = self.safran_colors['dark_gray']
        bg_bar.line.width = Pt(1)
        
        # Progress bar (green, proportional to completion)
        progress_width = int(bar_width * (project['progress'] / 100.0))
        if progress_width > 2:  # Only show if visible (in EMU units)
            progress_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                int(bar_x), int(y_position),
                progress_width, int(project_height)
            )
            progress_bar.fill.solid()
            progress_bar.fill.fore_color.rgb = self.safran_colors['green']
            progress_bar.line.width = Pt(0)
        
        # Project name label (left side) - constrained to available space
        label_width = Inches(3.3)  # Fixed width for consistency
        label_box = slide.shapes.add_textbox(
            int(content_x), int(y_position), int(label_width), int(project_height)
        )
        label_frame = label_box.text_frame
        # Intelligent truncation based on available space
        full_name = project['name']
        max_chars = 35  # Adjusted for constrained space
        if len(full_name) > max_chars:
            label_frame.text = f"{full_name[:max_chars]}..."
        else:
            label_frame.text = full_name
        label_frame.paragraphs[0].font.size = Pt(9)
        label_frame.paragraphs[0].font.color.rgb = self.safran_colors['dark_gray']
        label_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
        
        # Progress percentage (right side) - constrained to stay within content area
        progress_x = content_x + content_width - Inches(0.8)  # Fixed position from right edge
        progress_box = slide.shapes.add_textbox(
            int(progress_x), int(y_position), int(Inches(0.7)), int(project_height)
        )
        progress_frame = progress_box.text_frame
        progress_frame.text = f"{project['progress']:.0f}%"
        progress_frame.paragraphs[0].font.size = Pt(10)
        progress_frame.paragraphs[0].font.color.rgb = self.safran_colors['accent_orange']
        progress_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
    
    def _add_timeline_legend(self, slide, start_x, legend_y, timeline_width):
        """Add timeline legend"""
        legend_box = slide.shapes.add_textbox(
            start_x, legend_y, timeline_width, Inches(0.4)
        )
        legend_frame = legend_box.text_frame
        legend_frame.text = "■ Completed Progress   ■ Remaining Work   Note: Showing in-progress projects (0% < progress < 100%)"
        
        # Style legend
        legend_frame.paragraphs[0].font.size = Pt(10)
        legend_frame.paragraphs[0].font.color.rgb = self.safran_colors['light_gray']
        legend_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    def _create_phase_four_table_slide(self, prs, phase_info: Dict, report_date: datetime):
        """Create 4-table layout slide with MS Project data (Pattern: Slide 3, 7, 11)"""
        print(f"📄 Creating 4-table layout: {phase_info['short_name']}...")
        
        slide_layout = prs.slide_layouts[6]  # Blank layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Add Safran header
        self._add_safran_header(slide)
        
        # Move title into blue banner to save space
        banner_title_box = slide.shapes.add_textbox(
            Inches(3), Inches(0.1), Inches(4), Inches(0.6)
        )
        banner_title_frame = banner_title_box.text_frame
        banner_title_frame.text = f"Milestones & Risks: {phase_info['short_name']}"
        banner_title_frame.paragraphs[0].font.size = Pt(14)
        banner_title_frame.paragraphs[0].font.bold = True
        banner_title_frame.paragraphs[0].font.color.rgb = self.safran_colors['white']
        banner_title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # Create 4-table layout for this phase (MS Project XML data) - properly sized and positioned
        self._create_four_table_layout_from_msproject(slide, report_date, phase_info)
    
    def _create_phase_change_mgmt_slide(self, prs, phase_info: Dict, report_date: datetime):
        """Create change management slide (Pattern: Slide 4, 8, 12)"""
        print(f"📄 Creating change management: {phase_info['short_name']}...")
        
        slide_layout = prs.slide_layouts[6]  # Blank layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Add Safran header
        self._add_safran_header(slide)
        
        # Title
        title_box = slide.shapes.add_textbox(
            Inches(1), Inches(1.2), Inches(8), Inches(0.6)
        )
        title_frame = title_box.text_frame
        title_frame.text = f"Change Management: {phase_info['short_name']}"
        self._apply_title_style(title_frame.paragraphs[0])
        
        # Change management content from control tower
        content_box = slide.shapes.add_textbox(
            Inches(1), Inches(2), Inches(8), Inches(4.5)
        )
        content_frame = content_box.text_frame
        content_frame.text = f"[CHANGE MANAGEMENT CONTENT]\n\nPhase: {phase_info['short_name']}\n\nData Source: Control Tower Change Management Process\n\nContent will include:\n• Change requests for this phase\n• Impact assessments\n• Approval status\n• Implementation timeline\n• Risk mitigation measures\n• Stakeholder communications"
        
        # Style as placeholder for Phase 1
        for paragraph in content_frame.paragraphs:
            paragraph.font.size = Pt(14)
            paragraph.font.color.rgb = self.safran_colors['light_gray']
    
    def _create_four_table_layout_from_msproject(self, slide, report_date: datetime, phase_info: Dict):
        """
        Create the signature 4-table layout from MS Project XML data
        Consistent grid layout with equal sizing and proper spacing
        
        Layout (2x2 grid):
        ┌─────────────────┬─────────────────┐
        │ This Month's    │ Last Month's    │
        │ Milestones      │ Completed       │
        ├─────────────────┼─────────────────┤
        │ Next Month's    │ Risk            │
        │ Milestones      │ Register        │
        └─────────────────┴─────────────────┘
        """
        
        # Consistent table dimensions for 2x2 grid layout
        table_width = Inches(4.4)   # Equal width for all tables
        table_height = Inches(2.8)  # Equal height for all tables
        
        # Grid positioning with proper spacing
        margin_x = Inches(0.3)      # Left margin
        margin_y = Inches(0.9)      # Top margin (after banner)
        gap_x = Inches(0.2)         # Horizontal gap between tables
        gap_y = Inches(0.2)         # Vertical gap between tables
        
        # Calculate positions for 2x2 grid
        left_col_x = margin_x
        right_col_x = margin_x + table_width + gap_x
        top_row_y = margin_y
        bottom_row_y = margin_y + table_height + gap_y
        
        # Verify tables fit on slide (10" wide x 7.5" tall standard)
        total_width = margin_x + table_width + gap_x + table_width + margin_x
        total_height = margin_y + table_height + gap_y + table_height + Inches(0.3)
        
        if total_width > Inches(10) or total_height > Inches(7.5):
            print(f"⚠️  Table layout may exceed slide boundaries: {total_width.inches:.1f}\"W x {total_height.inches:.1f}\"H")
        
        # Get actual Level 4 project data for this phase
        all_projects = self._parse_xml_data()
        all_projects = [p for p in all_projects if p['phase'] is not None]
        phase_projects = self._get_projects_for_phase(phase_info['name'], all_projects)
        
        # Table 1: This Month's Milestones (Top Left) - Real MS Project XML data
        self._create_consistent_milestone_table(
            slide, left_col_x, top_row_y, table_width, table_height,
            "This Month's Milestones", "current", phase_info, phase_projects
        )
        
        # Table 2: Last Month's Completed (Top Right) - Real MS Project XML data
        self._create_consistent_milestone_table(
            slide, right_col_x, top_row_y, table_width, table_height,
            "Last Month's Completed", "completed", phase_info, phase_projects
        )
        
        # Table 3: Next Month's Milestones (Bottom Left) - Real MS Project XML data
        self._create_consistent_milestone_table(
            slide, left_col_x, bottom_row_y, table_width, table_height,
            "Next Month's Milestones", "upcoming", phase_info, phase_projects
        )
        
        # Table 4: Risk Register (Bottom Right) - Control Tower risk data
        self._create_consistent_risk_table(
            slide, right_col_x, bottom_row_y, table_width, table_height,
            "Risk Register", phase_info
        )
    
    def _create_consistent_milestone_table(self, slide, x, y, width, height, title: str, timeframe: str, phase_info: Dict, phase_projects: list = None):
        """Create a milestone table with consistent sizing and accurate data"""
        
        # Table with header + 4 data rows (consistent across all tables)
        table = slide.shapes.add_table(5, 3, int(x), int(y), int(width), int(height)).table
        
        # Set consistent column widths
        table.columns[0].width = int(width * 0.55)  # Milestone name (55%)
        table.columns[1].width = int(width * 0.25)  # Date (25%)
        table.columns[2].width = int(width * 0.20)  # Status (20%)
        
        # Header row with title
        header_cells = table.rows[0].cells
        header_cells[0].text = title
        header_cells[1].text = ""
        header_cells[2].text = ""
        
        # Merge header cells for title
        header_cells[0].merge(header_cells[2])
        
        # Style header
        self._style_table_header(header_cells[0])
        
        # Column headers
        col_header_cells = table.rows[1].cells
        col_header_cells[0].text = "Milestone"
        col_header_cells[1].text = "Date"
        col_header_cells[2].text = "Status"
        
        for cell in col_header_cells:
            self._style_table_column_header(cell)
        
        # Get accurate MS Project data instead of placeholders
        if phase_projects:
            ms_project_data = self._get_real_msproject_milestone_data(timeframe, phase_info, phase_projects)
        else:
            ms_project_data = self._get_msproject_milestone_data(timeframe, phase_info)
        
        # Show exactly 3 rows of data for consistency
        for i in range(3):
            row_cells = table.rows[i + 2].cells
            if i < len(ms_project_data):
                data_row = ms_project_data[i]
                row_cells[0].text = data_row['milestone']
                row_cells[1].text = data_row['date']
                row_cells[2].text = data_row['status']
            else:
                # Fill empty rows to maintain consistent table appearance
                row_cells[0].text = "—"
                row_cells[1].text = "—"
                row_cells[2].text = "—"
            
            for cell in row_cells:
                self._style_table_data_cell(cell)
    
    def _create_consistent_risk_table(self, slide, x, y, width, height, title: str, phase_info: Dict):
        """Create risk register table with consistent sizing"""
        
        # Table with header + 4 data rows (consistent with milestone tables)
        table = slide.shapes.add_table(5, 3, int(x), int(y), int(width), int(height)).table
        
        # Set consistent column widths
        table.columns[0].width = int(width * 0.45)  # Risk description (45%)
        table.columns[1].width = int(width * 0.25)  # Impact (25%)
        table.columns[2].width = int(width * 0.30)  # Mitigation (30%)
        
        # Header row
        header_cells = table.rows[0].cells
        header_cells[0].text = title
        header_cells[1].text = ""
        header_cells[2].text = ""
        
        # Merge header cells for title
        header_cells[0].merge(header_cells[2])
        
        # Style header
        self._style_table_header(header_cells[0])
        
        # Column headers
        col_header_cells = table.rows[1].cells
        col_header_cells[0].text = "Risk"
        col_header_cells[1].text = "Impact"
        col_header_cells[2].text = "Mitigation"
        
        for cell in col_header_cells:
            self._style_table_column_header(cell)
        
        # Control Tower risk data
        control_tower_risks = self._get_control_tower_risk_data(phase_info)
        
        # Show exactly 3 rows of data for consistency
        for i in range(3):
            row_cells = table.rows[i + 2].cells
            if i < len(control_tower_risks):
                risk_row = control_tower_risks[i]
                row_cells[0].text = risk_row['risk']
                row_cells[1].text = risk_row['impact']
                row_cells[2].text = risk_row['mitigation']
            else:
                # Fill empty rows to maintain consistent table appearance
                row_cells[0].text = "—"
                row_cells[1].text = "—"
                row_cells[2].text = "—"
            
            for cell in row_cells:
                self._style_table_data_cell(cell)
    
    def _add_safran_header(self, slide):
        """Add standardized Safran header to slide"""
        # Header background (blue bar)
        header_bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.8)
        )
        header_bg.fill.solid()
        header_bg.fill.fore_color.rgb = self.safran_colors['primary_blue']
        header_bg.line.fill.background()
        
        # Safran logo placeholder (left)
        logo_box = slide.shapes.add_textbox(
            Inches(0.2), Inches(0.1), Inches(2), Inches(0.6)
        )
        logo_frame = logo_box.text_frame
        logo_frame.text = "SAFRAN"
        logo_frame.paragraphs[0].font.size = Pt(18)
        logo_frame.paragraphs[0].font.bold = True
        logo_frame.paragraphs[0].font.color.rgb = self.safran_colors['white']
        
        # REACh identifier (right)
        reach_box = slide.shapes.add_textbox(
            Inches(7), Inches(0.1), Inches(2.8), Inches(0.6)
        )
        reach_frame = reach_box.text_frame
        reach_frame.text = "REACh Program"
        reach_frame.paragraphs[0].font.size = Pt(12)
        reach_frame.paragraphs[0].font.color.rgb = self.safran_colors['white']
        reach_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
    
    def _apply_title_style(self, title_element):
        """Apply Safran title styling with centered alignment"""
        if hasattr(title_element, 'text_frame'):
            paragraph = title_element.text_frame.paragraphs[0]
        else:
            paragraph = title_element
            
        paragraph.font.size = Pt(24)
        paragraph.font.bold = True
        paragraph.font.color.rgb = self.safran_colors['primary_blue']
        paragraph.alignment = PP_ALIGN.CENTER  # Centralized titles for professional look
    
    def _apply_content_style(self, text_frame):
        """Apply Safran content styling"""
        for paragraph in text_frame.paragraphs:
            paragraph.font.size = Pt(14)
            paragraph.font.color.rgb = self.safran_colors['dark_gray']
    
    def _style_table_header(self, cell):
        """Style table header cell"""
        cell.fill.solid()
        cell.fill.fore_color.rgb = self.safran_colors['primary_blue']
        paragraph = cell.text_frame.paragraphs[0]
        paragraph.font.bold = True
        paragraph.font.size = Pt(12)
        paragraph.font.color.rgb = self.safran_colors['white']
        paragraph.alignment = PP_ALIGN.LEFT
    
    def _style_table_column_header(self, cell):
        """Style table column header cell"""
        cell.fill.solid()
        cell.fill.fore_color.rgb = self.safran_colors['table_header']
        paragraph = cell.text_frame.paragraphs[0]
        paragraph.font.bold = True
        paragraph.font.size = Pt(11)
        paragraph.font.color.rgb = self.safran_colors['dark_gray']
        paragraph.alignment = PP_ALIGN.LEFT
    
    def _style_table_data_cell(self, cell):
        """Style table data cell"""
        paragraph = cell.text_frame.paragraphs[0]
        paragraph.font.size = Pt(9)
        paragraph.font.color.rgb = self.safran_colors['dark_gray']
    
    def _get_real_msproject_milestone_data(self, timeframe: str, phase_info: Dict, phase_projects: list) -> List[Dict]:
        """
        Get actual milestone data from MS Project XML for specific timeframe and phase
        Uses real Level 4 project data instead of placeholders
        """
        try:
            current_date = datetime.now()
            current_month_start = current_date.replace(day=1)
            current_month_end = current_date.replace(day=monthrange(current_date.year, current_date.month)[1])
            
            # Safe month calculations with error handling
            if current_date.month > 1:
                last_month = current_date.replace(month=current_date.month-1)
            else:
                last_month = current_date.replace(year=current_date.year-1, month=12)
            last_month_start = last_month.replace(day=1)
            last_month_end = last_month.replace(day=monthrange(last_month.year, last_month.month)[1])
            
            if current_date.month < 12:
                next_month = current_date.replace(month=current_date.month+1)
            else:
                next_month = current_date.replace(year=current_date.year+1, month=1)
            next_month_start = next_month.replace(day=1)
            next_month_end = next_month.replace(day=monthrange(next_month.year, next_month.month)[1])
        except Exception as e:
            print(f"⚠️  Date calculation error: {e}")
            # Return fallback data on date errors
            return self._get_msproject_milestone_data(timeframe, phase_info)
        
        milestones = []
        
        for project in phase_projects:
            try:
                # Determine milestone based on project progress and dates
                if project['start_date'] and project['finish_date']:
                    start_date = project['start_date']
                    end_date = project['finish_date']
                    progress = project['progress']
                    
                    # Create milestones based on timeframe
                    if timeframe == "current":
                        # Projects starting or ending this month
                        if (current_month_start <= start_date <= current_month_end or 
                            current_month_start <= end_date <= current_month_end):
                            status = "In Progress" if 0 < progress < 100 else ("Complete" if progress == 100 else "Planned")
                            milestones.append({
                                'milestone': f"{project['name'][:40]}..." if len(project['name']) > 40 else project['name'],
                                'date': start_date.strftime('%d-%b-%y'),
                                'status': status
                            })
                            
                    elif timeframe == "completed":
                        # Projects completed last month
                        if progress == 100 and (last_month_start <= end_date <= last_month_end):
                            milestones.append({
                                'milestone': f"{project['name'][:40]}..." if len(project['name']) > 40 else project['name'],
                                'date': end_date.strftime('%d-%b-%y'),
                                'status': 'Complete'
                            })
                            
                    elif timeframe == "upcoming":
                        # Projects starting next month
                        if next_month_start <= start_date <= next_month_end:
                            milestones.append({
                                'milestone': f"{project['name'][:40]}..." if len(project['name']) > 40 else project['name'],
                                'date': start_date.strftime('%d-%b-%y'),
                                'status': 'Planned'
                            })
            except Exception as e:
                print(f"⚠️  Error processing project milestone '{project.get('name', 'Unknown')}': {e}")
                continue
        
        # If no real milestones found, return fallback data
        if not milestones:
            return self._get_msproject_milestone_data(timeframe, phase_info)
        
        return milestones[:4]  # Return max 4 milestones

    def _get_msproject_milestone_data(self, timeframe: str, phase_info: Dict) -> List[Dict]:
        """
        Get milestone data from MS Project XML for specific timeframe and phase
        
        Phase 1: Return placeholder data matching manual format
        Phase 2: Parse actual MS Project XML files
        """
        
        phase_name = phase_info.get('name', 'Unknown Phase')
        
        # Phase 1 placeholder data matching Safran format
        if timeframe == "current":
            return [
                {'milestone': f'{phase_name} Kick-off', 'date': '15-Aug-25', 'status': 'In Progress'},
                {'milestone': f'{phase_name} Design Review', 'date': '22-Aug-25', 'status': 'Planned'},
                {'milestone': f'{phase_name} Approval Gate', 'date': '29-Aug-25', 'status': 'Planned'}
            ]
        elif timeframe == "completed":
            return [
                {'milestone': f'{phase_name} Planning', 'date': '08-Jul-25', 'status': 'Complete'},
                {'milestone': f'{phase_name} Resource Allocation', 'date': '15-Jul-25', 'status': 'Complete'},
                {'milestone': f'{phase_name} Team Formation', 'date': '22-Jul-25', 'status': 'Complete'}
            ]
        elif timeframe == "upcoming":
            return [
                {'milestone': f'{phase_name} Implementation', 'date': '05-Sep-25', 'status': 'Planned'},
                {'milestone': f'{phase_name} Testing Phase', 'date': '12-Sep-25', 'status': 'Planned'},
                {'milestone': f'{phase_name} Go-Live', 'date': '19-Sep-25', 'status': 'Planned'}
            ]
        
        return []
    
    def _get_control_tower_risk_data(self, phase_info: Dict) -> List[Dict]:
        """
        Get risk register data from Control Tower for specific phase
        
        Phase 1: Return placeholder data matching manual format
        Phase 2: Integrate with actual Control Tower risk management
        """
        
        phase_name = phase_info.get('name', 'Unknown Phase')
        
        # Phase 1 placeholder data matching Safran risk format
        return [
            {
                'risk': f'{phase_name} Resource Availability',
                'impact': 'Medium',
                'mitigation': 'Backup team identified'
            },
            {
                'risk': f'{phase_name} Technical Complexity',
                'impact': 'High',
                'mitigation': 'Expert consultation scheduled'
            },
            {
                'risk': f'{phase_name} Timeline Constraints',
                'impact': 'Low',
                'mitigation': 'Buffer time allocated'
            }
        ]
    
    def _get_change_management_data(self, phase_info: Dict) -> Dict:
        """
        Get change management data from Control Tower for specific phase
        
        Phase 1: Return placeholder data matching manual format
        Phase 2: Integrate with actual Control Tower change management
        """
        
        phase_name = phase_info.get('name', 'Unknown Phase')
        
        # Phase 1 placeholder data matching Safran change format
        return {
            'stakeholder_engagement': f'{phase_name} stakeholder meetings scheduled weekly',
            'communication_plan': f'{phase_name} updates distributed bi-weekly via team channels',
            'training_requirements': f'{phase_name} training modules developed for key users',
            'resistance_management': f'{phase_name} concerns addressed through one-on-one sessions',
            'success_metrics': f'{phase_name} adoption rate target: 85% by month-end'
        }


def main():
    """Main function for command line usage"""
    
    if not PPTX_AVAILABLE:
        print("❌ python-pptx not installed. Install with: pip install python-pptx")
        return
    
    print("🚀 SAFRAN POWERPOINT GENERATOR - PHASE 1")
    print("="*60)
    print("🎨 Focus: Format & Layout Foundation")
    print("📄 Generating first 12 pages with Safran branding")
    print("📂 Generator: Control Tower /reports (centralized)")
    print("💾 Output: contract_projects/powerpoint_reports/ (organized)")
    print()
    
    generator = SafranPowerPointGenerator()
    
    # Generate Safran presentation
    report_path = generator.generate_safran_presentation()
    
    if report_path:
        print(f"\n📊 SAFRAN PRESENTATION GENERATED SUCCESSFULLY!")
        print(f"📁 Location: {report_path}")
        print(f"📂 Saved to: contract_projects/powerpoint_reports/ (organized structure)")
        print(f"\n🎯 PHASE 1 COMPLETE - NEXT STEPS:")
        print(f"1. Review generated presentation format")
        print(f"2. Compare with manual example")
        print(f"3. Adjust branding and layout as needed")
        print(f"4. Move to Phase 2: Data Integration")
        print(f"\n📋 ORGANIZATION WORKFLOW:")
        print(f"• Generator scripts: Stay in Control Tower /reports")
        print(f"• Generated presentations: Saved to [repo]/powerpoint_reports/")
        print(f"• Each repo has dedicated powerpoint_reports folder")
        print(f"• Control Tower creates presentations for ALL repos")
        print(f"\n📋 PRESENTATION WORKFLOW:")
        print(f"• Control Tower generates pages 1-12 → repo/powerpoint_reports/")
        print(f"• User downloads from powerpoint_reports folder")
        print(f"• User appends additional slides manually")
        print(f"• Final presentation ready for distribution")
    else:
        print("❌ Failed to generate Safran presentation")

if __name__ == "__main__":
    main()
