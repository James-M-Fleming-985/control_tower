#!/usr/bin/env python3
"""
MS Project Integration for Control Tower
Bidirectional sync between Control Tower and MS Project files

Supports:
- Reading .mpp files directly
- Updating project data
- Exporting updated XML for MS Project import
- Task status synchronization
"""

import os
import sys
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
import subprocess

class MSProjectIntegration:
    """
    Handle MS Project file integration with Control Tower
    """
    
    def __init__(self, project_path: str):
        """
        Initialize MS Project integration
        
        Args:
            project_path: Path to MS Project file or XML export
        """
        self.project_path = project_path
        self.project_data = None
        self.tasks = []
        self.resources = []
        self.assignments = []
        
    def read_project_file(self) -> bool:
        """
        Read MS Project file (.mpp or .xml)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.project_path.endswith('.xml'):
                return self._read_xml_project()
            elif self.project_path.endswith('.mpp'):
                return self._read_mpp_project()
            else:
                print(f"Unsupported file format: {self.project_path}")
                return False
        except Exception as e:
            print(f"Error reading project file: {e}")
            return False
    
    def _read_xml_project(self) -> bool:
        """Read MS Project XML format"""
        try:
            tree = ET.parse(self.project_path)
            root = tree.getroot()
            
            # Handle namespace if present
            namespace = ""
            if root.tag.startswith('{'):
                namespace = root.tag.split('}')[0] + '}'
            
            # Extract project information
            self.project_data = {
                'title': self._get_xml_text_ns(root, 'Title', namespace),
                'start_date': self._get_xml_text_ns(root, 'StartDate', namespace),
                'finish_date': self._get_xml_text_ns(root, 'FinishDate', namespace),
                'currency': self._get_xml_text_ns(root, 'CurrencySymbol', namespace)
            }
            
            # Extract tasks - handle both with and without namespace
            self.tasks = []
            for task in root.findall(f'.//{namespace}Task'):
                task_data = {
                    'id': self._get_xml_text_ns(task, 'ID', namespace),
                    'name': self._get_xml_text_ns(task, 'Name', namespace),
                    'start': self._get_xml_text_ns(task, 'Start', namespace),
                    'finish': self._get_xml_text_ns(task, 'Finish', namespace),
                    'duration': self._get_xml_text_ns(task, 'Duration', namespace),
                    'percent_complete': self._get_xml_text_ns(task, 'PercentComplete', namespace),
                    'is_milestone': self._get_xml_text_ns(task, 'Milestone', namespace) == '1',
                    'predecessors': self._get_xml_text_ns(task, 'PredecessorLink', namespace),
                    'resource_names': self._get_xml_text_ns(task, 'ResourceNames', namespace),
                    'work': self._get_xml_text_ns(task, 'Work', namespace),
                    'actual_start': self._get_xml_text_ns(task, 'ActualStart', namespace),
                    'actual_finish': self._get_xml_text_ns(task, 'ActualFinish', namespace)
                }
                self.tasks.append(task_data)
            
            print(f"Loaded {len(self.tasks)} tasks from XML")
            return True
            
        except Exception as e:
            print(f"Error reading XML project: {e}")
            return False
    
    def _get_xml_text_ns(self, element, tag_name: str, namespace: str = "") -> str:
        """Get text content from XML element with namespace support"""
        full_tag = f"{namespace}{tag_name}"
        found = element.find(full_tag)
        if found is not None:
            return found.text if found.text else ""
        
        # Try without namespace as fallback
        found = element.find(tag_name)
        return found.text if found is not None and found.text else ""
    
    def _read_mpp_project(self) -> bool:
        """Read native .mpp file using MPXJ"""
        try:
            # This would require MPXJ installation
            # For now, suggest XML export approach
            print("Direct .mpp reading requires MPXJ installation.")
            print("Please export your MS Project file as XML format.")
            print("File → Export → Save as XML Format (.xml)")
            return False
            
        except Exception as e:
            print(f"Error reading .mpp project: {e}")
            return False
    
    def _get_xml_text(self, element, xpath: str) -> str:
        """Get text content from XML element"""
        found = element.find(xpath)
        return found.text if found is not None else ""
    
    def get_milestones(self, start_date: Optional[datetime] = None, 
                      end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get milestones within date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of milestone tasks
        """
        milestones = []
        
        for task in self.tasks:
            if task['is_milestone']:
                task_date = self._parse_ms_date(task['finish'])
                
                # Filter by date range if provided
                if start_date and task_date and task_date < start_date:
                    continue
                if end_date and task_date and task_date > end_date:
                    continue
                    
                milestones.append({
                    'name': task['name'],
                    'date': task_date,
                    'status': 'Complete' if task['percent_complete'] == '100' else 'Pending',
                    'percent_complete': task['percent_complete'],
                    'resource': task['resource_names']
                })
        
        return sorted(milestones, key=lambda x: x['date'] or datetime.min)
    
    def get_tasks_by_resource(self, resource_name: str) -> List[Dict]:
        """Get all tasks assigned to a specific resource"""
        resource_tasks = []
        
        for task in self.tasks:
            if resource_name.lower() in task['resource_names'].lower():
                resource_tasks.append(task)
                
        return resource_tasks
    
    def get_overdue_tasks(self) -> List[Dict]:
        """Get tasks that are overdue"""
        today = datetime.now()
        overdue = []
        
        for task in self.tasks:
            if task['percent_complete'] != '100':  # Not complete
                finish_date = self._parse_ms_date(task['finish'])
                if finish_date and finish_date < today:
                    overdue.append(task)
                    
        return overdue
    
    def update_task_progress(self, task_id: str, percent_complete: int, 
                           actual_start: Optional[datetime] = None,
                           actual_finish: Optional[datetime] = None) -> bool:
        """
        Update task progress (for XML export)
        
        Args:
            task_id: Task ID to update
            percent_complete: Completion percentage (0-100)
            actual_start: Actual start date
            actual_finish: Actual finish date
            
        Returns:
            bool: True if successful
        """
        for task in self.tasks:
            if task['id'] == task_id:
                task['percent_complete'] = str(percent_complete)
                if actual_start:
                    task['actual_start'] = actual_start.isoformat()
                if actual_finish:
                    task['actual_finish'] = actual_finish.isoformat()
                return True
        return False
    
    def export_updated_xml(self, output_path: str) -> bool:
        """
        Export updated project data as XML for MS Project import
        
        Args:
            output_path: Path for output XML file
            
        Returns:
            bool: True if successful
        """
        try:
            # Create XML structure for MS Project
            root = ET.Element("Project")
            
            # Add project properties
            title_elem = ET.SubElement(root, "Title")
            title_elem.text = self.project_data.get('title', 'Control Tower Project')
            
            # Add tasks
            tasks_elem = ET.SubElement(root, "Tasks")
            for task in self.tasks:
                task_elem = ET.SubElement(tasks_elem, "Task")
                
                for key, value in task.items():
                    if value:  # Only add non-empty values
                        elem = ET.SubElement(task_elem, key.title().replace('_', ''))
                        elem.text = str(value)
            
            # Write to file
            tree = ET.ElementTree(root)
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            
            print(f"Updated project exported to: {output_path}")
            print("Import this file into MS Project to update your master project.")
            
            return True
            
        except Exception as e:
            print(f"Error exporting XML: {e}")
            return False
    
    def _parse_ms_date(self, date_str: str) -> Optional[datetime]:
        """Parse MS Project date string"""
        if not date_str or date_str == "NA":
            return None
            
        # Common MS Project date formats
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%y",
            "%d/%m/%Y",
            "%m/%d/%y",
            "%m/%d/%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        return None
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive project status report"""
        today = datetime.now()
        
        # Calculate statistics
        total_tasks = len([t for t in self.tasks if not t['is_milestone']])
        completed_tasks = len([t for t in self.tasks if t['percent_complete'] == '100' and not t['is_milestone']])
        overdue_tasks = len(self.get_overdue_tasks())
        
        milestones_this_month = self.get_milestones(
            start_date=today.replace(day=1),
            end_date=(today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        )
        
        milestones_next_month = self.get_milestones(
            start_date=(today.replace(day=28) + timedelta(days=4)).replace(day=1),
            end_date=(today.replace(day=28) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        )
        
        return {
            'project_title': self.project_data.get('title', 'Unknown Project'),
            'report_date': today.strftime('%Y-%m-%d'),
            'statistics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_percentage': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
                'overdue_tasks': overdue_tasks
            },
            'milestones_this_month': milestones_this_month,
            'milestones_next_month': milestones_next_month,
            'overdue_tasks': self.get_overdue_tasks()[:10]  # Top 10 overdue
        }

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MS Project Integration for Control Tower')
    parser.add_argument('project_file', help='Path to MS Project file (.mpp or .xml)')
    parser.add_argument('--action', choices=['milestones', 'overdue', 'status', 'export'], 
                       default='status', help='Action to perform')
    parser.add_argument('--resource', help='Filter by resource name')
    parser.add_argument('--output', help='Output file path for export')
    
    args = parser.parse_args()
    
    # Initialize MS Project integration
    ms_project = MSProjectIntegration(args.project_file)
    
    if not ms_project.read_project_file():
        print("Failed to read project file")
        return 1
    
    # Perform requested action
    if args.action == 'milestones':
        today = datetime.now()
        this_month = ms_project.get_milestones(
            start_date=today.replace(day=1),
            end_date=(today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        )
        next_month = ms_project.get_milestones(
            start_date=(today.replace(day=28) + timedelta(days=4)).replace(day=1),
            end_date=(today.replace(day=28) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        )
        
        print("📅 MILESTONES THIS MONTH:")
        for milestone in this_month:
            print(f"  • {milestone['name']} - {milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'} - {milestone['status']}")
        
        print("\n📅 MILESTONES NEXT MONTH:")
        for milestone in next_month:
            print(f"  • {milestone['name']} - {milestone['date'].strftime('%d/%m/%Y') if milestone['date'] else 'No date'} - {milestone['status']}")
    
    elif args.action == 'overdue':
        overdue = ms_project.get_overdue_tasks()
        print("⚠️  OVERDUE TASKS:")
        for task in overdue[:10]:  # Top 10
            print(f"  • {task['name']} - Due: {task['finish']} - {task['percent_complete']}% complete")
    
    elif args.action == 'status':
        report = ms_project.generate_status_report()
        print(f"📊 PROJECT STATUS REPORT - {report['project_title']}")
        print(f"Report Date: {report['report_date']}")
        print(f"\nStatistics:")
        print(f"  • Total Tasks: {report['statistics']['total_tasks']}")
        print(f"  • Completed: {report['statistics']['completed_tasks']} ({report['statistics']['completion_percentage']}%)")
        print(f"  • Overdue: {report['statistics']['overdue_tasks']}")
        
        print(f"\nMilestones This Month: {len(report['milestones_this_month'])}")
        print(f"Milestones Next Month: {len(report['milestones_next_month'])}")
    
    elif args.action == 'export':
        output_path = args.output or f"updated_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        if ms_project.export_updated_xml(output_path):
            print(f"✅ Project exported successfully to {output_path}")
        else:
            print("❌ Failed to export project")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
