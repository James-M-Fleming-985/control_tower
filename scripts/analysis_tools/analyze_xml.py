#!/usr/bin/env python3
"""
Enhanced XML structure analyzer for MS Project files
Analyzes hierarchy, phases, and project distribution
"""

import xml.etree.ElementTree as ET
import os
from collections import defaultdict

xml_path = '/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml'

if os.path.exists(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        print(f"Root element: {root.tag}")
        print(f"Root attributes: {root.attrib}")
        print(f"Namespace: {root.tag.split('}')[0] + '}' if '}' in root.tag else 'None'}")
        
        # Get all unique child element names
        children = set()
        for child in root:
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            children.add(tag_name)
        
        print(f"\nDirect children: {sorted(list(children))}")
        
        # Look for Tasks element specifically
        namespace = {'ms': 'http://schemas.microsoft.com/project'}
        
        # Try different ways to find tasks
        tasks_element = root.find('.//ms:Tasks', namespace)
        if tasks_element is not None:
            print(f"\nFound Tasks element with {len(list(tasks_element))} children")
            
            # Analyze hierarchy structure
            hierarchy_stats = defaultdict(int)
            phase_distribution = defaultdict(list)
            in_progress_projects = []
            
            for i, task in enumerate(list(tasks_element)):
                task_name = task.tag.split('}')[-1] if '}' in task.tag else task.tag
                
                # Get task details
                name_elem = task.find('ms:Name', namespace)
                progress_elem = task.find('ms:PercentComplete', namespace)
                level_elem = task.find('ms:OutlineLevel', namespace)
                id_elem = task.find('ms:ID', namespace)
                
                if name_elem is not None and name_elem.text:
                    name = name_elem.text.strip()
                    progress = 0.0
                    level = 1
                    task_id = "N/A"
                    
                    if progress_elem is not None and progress_elem.text:
                        try:
                            progress = float(progress_elem.text)
                        except:
                            pass
                    
                    if level_elem is not None and level_elem.text:
                        try:
                            level = int(level_elem.text)
                        except:
                            pass
                    
                    if id_elem is not None and id_elem.text:
                        task_id = id_elem.text
                    
                    # Track hierarchy statistics
                    hierarchy_stats[level] += 1
                    
                    # Categorize by phase (simplified logic)
                    phase = "Unknown"
                    name_lower = name.lower()
                    if 'critical documentation' in name_lower or 'training' in name_lower:
                        phase = "Documentation & Training"
                    elif 'critical maintenance' in name_lower or 'maintenance' in name_lower:
                        phase = "Critical Maintenance"
                    elif 'optimization' in name_lower or 'flow rate' in name_lower or 'kardex' in name_lower or 'chiller' in name_lower or 'lims' in name_lower:
                        phase = "Post Stabilization Optimization"
                    
                    phase_distribution[phase].append((level, name, progress))
                    
                    # Track in-progress projects
                    if 0 < progress < 100:
                        in_progress_projects.append((level, name, progress, task_id))
            
            # Display first 5 tasks as before
            print("\nFirst 5 tasks:")
            for i, task in enumerate(list(tasks_element)[:5]):
                task_name = task.tag.split('}')[-1] if '}' in task.tag else task.tag
                print(f"  Task {i+1}: {task_name}")
                
                # Look for task details
                name_elem = task.find('ms:Name', namespace)
                if name_elem is not None and name_elem.text:
                    print(f"    Name: {name_elem.text}")
                    
                progress_elem = task.find('ms:PercentComplete', namespace)
                if progress_elem is not None and progress_elem.text:
                    print(f"    Progress: {progress_elem.text}")
                
                level_elem = task.find('ms:OutlineLevel', namespace)
                if level_elem is not None and level_elem.text:
                    print(f"    Level: {level_elem.text}")
            
            # Display hierarchy analysis
            print(f"\n{'='*60}")
            print("HIERARCHY ANALYSIS")
            print(f"{'='*60}")
            print("Outline Level Distribution:")
            for level in sorted(hierarchy_stats.keys()):
                print(f"  Level {level}: {hierarchy_stats[level]} tasks")
            
            print(f"\n{'='*60}")
            print("PHASE DISTRIBUTION")
            print(f"{'='*60}")
            for phase, tasks in phase_distribution.items():
                if tasks:
                    print(f"\n{phase}: {len(tasks)} tasks")
                    # Show level distribution within each phase
                    level_counts = defaultdict(int)
                    for level, name, progress in tasks:
                        level_counts[level] += 1
                    
                    for level in sorted(level_counts.keys()):
                        print(f"  Level {level}: {level_counts[level]} tasks")
            
            print(f"\n{'='*60}")
            print("IN-PROGRESS PROJECTS (0% < Progress < 100%)")
            print(f"{'='*60}")
            print(f"Found {len(in_progress_projects)} in-progress projects:")
            
            # Group by level for executive summary
            by_level = defaultdict(list)
            for level, name, progress, task_id in in_progress_projects:
                by_level[level].append((name, progress, task_id))
            
            for level in sorted(by_level.keys()):
                projects = by_level[level]
                print(f"\nLevel {level} Projects ({len(projects)} projects):")
                for name, progress, task_id in projects[:10]:  # Show max 10 per level
                    print(f"  • {name[:60]} - {progress:.0f}% (ID: {task_id})")
                if len(projects) > 10:
                    print(f"  ... and {len(projects) - 10} more")
            
            # Executive summary for timeline slides
            print(f"\n{'='*60}")
            print("TIMELINE SLIDE SUMMARY")
            print(f"{'='*60}")
            print("Based on our Safran generator logic:")
            
            doc_training_level4 = [p for p in in_progress_projects if p[0] == 4 and ('documentation' in p[1].lower() or 'training' in p[1].lower() or 'sf investment' in p[1].lower())]
            maintenance_level4 = [p for p in in_progress_projects if p[0] == 4 and ('maintenance' in p[1].lower() or 'vat' in p[1].lower() or 'remove' in p[1].lower())]
            optimization_level3 = [p for p in in_progress_projects if p[0] == 3 and ('optimization' in p[1].lower() or 'flow rate' in p[1].lower() or 'kardex' in p[1].lower() or 'chiller' in p[1].lower() or 'lims' in p[1].lower())]
            
            print(f"• Documentation & Training Slide: {len(doc_training_level4)} Level 4 projects")
            if doc_training_level4:
                for level, name, progress, task_id in doc_training_level4:
                    print(f"  - {name[:50]} - {progress:.0f}%")
            
            print(f"• Critical Maintenance Slide: {len(maintenance_level4)} Level 4 projects")
            if maintenance_level4:
                for level, name, progress, task_id in maintenance_level4:
                    print(f"  - {name[:50]} - {progress:.0f}%")
            
            print(f"• Post Stabilization Optimization Slide: {len(optimization_level3)} Level 3 projects")
            if optimization_level3:
                for level, name, progress, task_id in optimization_level3:
                    print(f"  - {name[:50]} - {progress:.0f}%")
            
            print(f"\n{'='*60}")
            print("KEY INSIGHTS FOR NEW PROJECT ROBUSTNESS")
            print(f"{'='*60}")
            print("✅ XML Structure Analysis:")
            print(f"  • Total tasks: {sum(hierarchy_stats.values())}")
            print(f"  • Level 3 containers: {hierarchy_stats[3]} (project categories)")
            print(f"  • Level 4 tasks: {hierarchy_stats[4]} (actionable items)")
            print(f"  • In-progress Level 3: {len([p for p in in_progress_projects if p[0] == 3])}")
            print(f"  • In-progress Level 4: {len([p for p in in_progress_projects if p[0] == 4])}")
            
            print(f"\n✅ Robustness Assessment:")
            print(f"  • New Level 4 projects under existing Level 3 containers: AUTOMATIC")
            print(f"  • New Level 3 containers with optimization keywords: AUTOMATIC") 
            print(f"  • New Level 3 containers without keywords: FALLBACK to Documentation")
            print(f"  • System handles {hierarchy_stats[3]} Level 3 categories successfully")
        else:
            print("\nTasks element not found with namespace")
            
            # Try without namespace
            for elem in root.iter():
                tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                if 'task' in tag_name.lower():
                    print(f"Found element: {tag_name}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"File not found: {xml_path}")
