#!/usr/bin/env python3
"""
Test script for XML timeline generation
"""

import sys
import os
sys.path.insert(0, '/workspaces/control_tower')

def test_xml_parsing():
    """Test XML parsing functionality"""
    print("🔍 Testing XML parsing...")
    
    try:
        import xml.etree.ElementTree as ET
        from datetime import datetime
        
        xml_path = '/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml'
        
        if not os.path.exists(xml_path):
            print(f"❌ XML file not found: {xml_path}")
            return False
            
        print(f"✅ XML file exists: {xml_path}")
        
        # Parse XML
        tree = ET.parse(xml_path)
        root = tree.getroot()
        print(f"✅ XML parsed successfully, root tag: {root.tag}")
        
        # Find tasks using namespace (like our generator does)
        namespace = {'ms': 'http://schemas.microsoft.com/project'}
        tasks_element = root.find('.//ms:Tasks', namespace)
        if tasks_element is None:
            tasks = root.findall('.//Task')  # Fallback for non-namespaced XML
            print(f"✅ Found {len(tasks)} tasks in XML (no namespace)")
        else:
            tasks = list(tasks_element)
            print(f"✅ Found {len(tasks)} tasks in XML (with namespace)")
        
        # Show some task details with hierarchy levels
        projects_found = 0
        for task in tasks[:20]:  # Check first 20 tasks for better coverage
            name_elem = task.find('ms:Name', namespace) if tasks_element is not None else task.find('Name')
            progress_elem = task.find('ms:PercentComplete', namespace) if tasks_element is not None else task.find('PercentComplete')
            level_elem = task.find('ms:OutlineLevel', namespace) if tasks_element is not None else task.find('OutlineLevel')
            
            if name_elem is not None and name_elem.text and name_elem.text.strip():
                name = name_elem.text.strip()
                progress = 0.0
                level = 1
                
                if progress_elem is not None and progress_elem.text:
                    try:
                        progress = float(progress_elem.text)
                        if progress > 1:  # Handle percentage vs decimal format
                            progress = progress
                        else:
                            progress = progress * 100
                    except:
                        pass
                
                if level_elem is not None and level_elem.text:
                    try:
                        level = int(level_elem.text)
                    except:
                        pass
                
                if 0 < progress < 100:  # In-progress projects
                    print(f"  📋 L{level} Project: {name[:60]} - Progress: {progress:.1f}%")
                    projects_found += 1
        
        print(f"✅ Found {projects_found} in-progress projects")
        return True
        
    except Exception as e:
        print(f"❌ XML parsing error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hierarchy_detection():
    """Test the hierarchy detection and phase assignment logic"""
    print("\n🔗 Testing hierarchy detection...")
    
    try:
        from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator
        
        generator = SafranPowerPointGenerator()
        print("✅ Generator initialized for hierarchy testing")
        
        # Parse XML data using the generator's method
        all_projects = generator._parse_xml_data()
        print(f"✅ Parsed {len(all_projects)} projects from XML")
        
        # Test phase assignment
        phase_counts = {'Documentation & Training': 0, 'Critical Maintenance': 0, 'Post Stabilization Optimization': 0, None: 0}
        level_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
        
        for project in all_projects:
            phase = project.get('phase')
            level = project.get('outline_level', 1)
            
            if phase in phase_counts:
                phase_counts[phase] += 1
            
            if level in level_counts:
                level_counts[level] += 1
        
        print("\n📊 Phase Distribution:")
        for phase, count in phase_counts.items():
            if count > 0:
                print(f"   {phase or 'None (Skipped)'}: {count} projects")
        
        print("\n📋 Outline Level Distribution:")
        for level, count in level_counts.items():
            if count > 0:
                print(f"   Level {level}: {count} tasks")
        
        # Test filtering for each phase
        print("\n🎯 Executive-Level Filtering Test:")
        for phase_name in ['Documentation & Training', 'Critical Maintenance', 'Post Stabilization Optimization']:
            filtered_projects = generator._get_projects_for_phase(phase_name, all_projects)
            print(f"   {phase_name}: {len(filtered_projects)} executive-level projects")
        
        return True
        
    except Exception as e:
        print(f"❌ Hierarchy detection error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_powerpoint_generation():
    """Test PowerPoint generation"""
    print("\n🎨 Testing PowerPoint generation...")
    
    try:
        from pptx import Presentation
        print("✅ python-pptx imported successfully")
        
        from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator
        from datetime import datetime
        
        print("✅ SafranPowerPointGenerator imported")
        
        # Create generator
        generator = SafranPowerPointGenerator()
        print("✅ Generator initialized")
        
        # Generate presentation
        result = generator.generate_safran_presentation(datetime.now())
        
        if result:
            print(f"✅ PowerPoint generated: {result}")
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"✅ File created successfully, size: {file_size} bytes")
            else:
                print(f"❌ File not found: {result}")
        else:
            print("❌ PowerPoint generation failed")
            
        return result is not None
        
    except Exception as e:
        print(f"❌ PowerPoint generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Safran PowerPoint XML Timeline Tests")
    print("=" * 60)
    
    # Test XML parsing
    xml_success = test_xml_parsing()
    
    # Test hierarchy detection and phase assignment
    hierarchy_success = test_hierarchy_detection()
    
    # Test PowerPoint generation
    ppt_success = test_powerpoint_generation()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   XML Parsing: {'✅ PASS' if xml_success else '❌ FAIL'}")
    print(f"   Hierarchy Detection: {'✅ PASS' if hierarchy_success else '❌ FAIL'}")
    print(f"   PowerPoint Generation: {'✅ PASS' if ppt_success else '❌ FAIL'}")
    print("=" * 60)
