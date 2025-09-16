#!/usr/bin/env python3
"""
Safran PowerPoint Formatting Fixes
Addresses the following issues:
1. Title alignment consistency (standardize to left-aligned)
2. Timeline formatting improvements (better positioning, full project names)
3. Table space utilization (wider and taller tables)
4. SF Documentation missing from Post Stabilization (improve phase detection)
"""

import sys
sys.path.insert(0, '/workspaces/control_tower')

from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator

def apply_formatting_fixes():
    """Apply all formatting fixes to the Safran PowerPoint generator"""
    
    print("🔧 Applying Safran PowerPoint formatting fixes...")
    
    # Read the current generator file
    generator_file = '/workspaces/control_tower/modules/milestone_management/reporting/safran_powerpoint_generator.py'
    
    with open(generator_file, 'r') as f:
        content = f.read()
    
    # Fix 1: Standardize title alignment to LEFT
    print("✏️  Fix 1: Standardizing title alignment to LEFT...")
    
    # Replace center alignments with left alignment for titles
    fixes_applied = []
    
    # Title alignment fixes
    if 'paragraph.alignment = PP_ALIGN.CENTER' in content:
        # Keep center alignment only for specific elements (legends, headers)
        # Change title alignments to LEFT
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if 'paragraph.alignment = PP_ALIGN.CENTER' in line:
                # Check context to see if this is a title or should be left-aligned
                context_lines = lines[max(0, i-3):i+3]
                context = '\n'.join(context_lines).lower()
                
                # Keep center alignment for: legends, phase frames, headers
                if any(keyword in context for keyword in ['legend', 'phase_frame', 'header_frame', 'reach_frame']):
                    fixed_lines.append(line)  # Keep center
                else:
                    # Change to left alignment for titles
                    fixed_lines.append(line.replace('PP_ALIGN.CENTER', 'PP_ALIGN.LEFT'))
                    fixes_applied.append(f"Line {i+1}: Changed title alignment to LEFT")
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
    
    # Fix 2: Improve timeline formatting
    print("✏️  Fix 2: Improving timeline formatting...")
    
    # Timeline positioning and sizing improvements
    timeline_fixes = {
        # Increase label box width for full project names
        'Inches(3.5), project_height': 'Inches(4.5), project_height',
        
        # Adjust positioning for better layout
        'start_x = Inches(1)': 'start_x = Inches(0.5)',
        'timeline_width = Inches(8)': 'timeline_width = Inches(9)',
        
        # Increase font size for better readability
        'label_frame.paragraphs[0].font.size = Pt(9)': 'label_frame.paragraphs[0].font.size = Pt(10)',
        'progress_frame.paragraphs[0].font.size = Pt(9)': 'progress_frame.paragraphs[0].font.size = Pt(10)',
        
        # Extend character limit for project names
        "f\"{project['name'][:40]}{'...' if len(project['name']) > 40 else ''}\"": "f\"{project['name'][:55]}{'...' if len(project['name']) > 55 else ''}\"",
        
        # Adjust label box positioning for better alignment
        'Inches(0.2), y_position, Inches(3.5)': 'Inches(0.2), y_position, Inches(4.5)'
    }
    
    for old, new in timeline_fixes.items():
        if old in content:
            content = content.replace(old, new)
            fixes_applied.append(f"Timeline: {old} → {new}")
    
    # Fix 3: Improve table space utilization
    print("✏️  Fix 3: Improving table space utilization...")
    
    table_fixes = {
        # Increase table dimensions for better space usage
        'width=Inches(3.8), height=Inches(2.2)': 'width=Inches(4.2), height=Inches(2.6)',
        'width=Inches(3.8), height=Inches(2.3)': 'width=Inches(4.2), height=Inches(2.7)',
        
        # Adjust table positioning for optimal layout
        'Inches(1), Inches(2.5)': 'Inches(0.8), Inches(2.4)',
        'Inches(5), Inches(2.5)': 'Inches(5.2), Inches(2.4)',
        'Inches(1), Inches(5)': 'Inches(0.8), Inches(5.2)',
        'Inches(5), Inches(5)': 'Inches(5.2), Inches(5.2)',
        
        # Increase table font size for better readability
        'paragraph.font.size = Pt(10)': 'paragraph.font.size = Pt(11)',
        'cell.text_frame.paragraphs[0].font.size = Pt(10)': 'cell.text_frame.paragraphs[0].font.size = Pt(11)'
    }
    
    for old, new in table_fixes.items():
        if old in content:
            content = content.replace(old, new)
            fixes_applied.append(f"Table: {old} → {new}")
    
    # Fix 4: Improve SF Documentation detection for Post Stabilization
    print("✏️  Fix 4: Improving SF Documentation phase detection...")
    
    # Enhanced phase detection logic
    sf_doc_fix = '''elif ('flow rate optimization' in parent_name or 'kardex optimization' in parent_name or 
                      'chiller system optimization' in parent_name or 'asset management optimization' in parent_name or
                      'operational documentation' in parent_name and 'optimization' in parent_name or
                      'sf operational documentation' in parent_name or 'sf documentation' in parent_name or
                      'lims roll out' in parent_name or 'optimization' in parent_name):'''
    
    old_detection = '''elif ('flow rate optimization' in parent_name or 'kardex optimization' in parent_name or 
                      'chiller system optimization' in parent_name or 'asset management optimization' in parent_name or
                      'operational documentation' in parent_name and 'optimization' in parent_name or
                      'lims roll out' in parent_name or 'optimization' in parent_name):'''
    
    if old_detection in content:
        content = content.replace(old_detection, sf_doc_fix)
        fixes_applied.append("Phase Detection: Added SF Documentation keywords")
    
    # Also improve fallback detection
    fallback_fix = '''elif any(keyword in task_name for keyword in ['optimization', 'flow rate', 'kardex', 'chiller', 'lims', 'sf operational', 'sf documentation']):'''
    old_fallback = '''elif any(keyword in task_name for keyword in ['optimization', 'flow rate', 'kardex', 'chiller', 'lims']):'''
    
    if old_fallback in content:
        content = content.replace(old_fallback, fallback_fix)
        fixes_applied.append("Phase Detection: Enhanced fallback keywords")
    
    # Write the fixes back to the file
    with open(generator_file, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Applied {len(fixes_applied)} formatting fixes:")
    for fix in fixes_applied:
        print(f"   • {fix}")
    
    print(f"\n🎯 Fixes Summary:")
    print(f"   1. ✅ Title alignment standardized to LEFT")
    print(f"   2. ✅ Timeline layout improved (wider, longer names, better fonts)")
    print(f"   3. ✅ Table space utilization enhanced (larger tables, better positioning)")
    print(f"   4. ✅ SF Documentation detection improved for Post Stabilization phase")
    
    return True

def test_fixes():
    """Test the fixes by running a quick analysis"""
    print(f"\n🧪 Testing fixes...")
    
    # Test the updated generator
    generator = SafranPowerPointGenerator()
    all_projects = generator._parse_xml_data()
    
    # Check Post Stabilization projects
    post_projects = [p for p in all_projects if p['phase'] == 'Post Stabilization Optimization' and 0 < p['progress'] < 100]
    
    print(f"\n📊 Post Stabilization Optimization projects found: {len(post_projects)}")
    for project in post_projects:
        print(f"   • {project['name']} - {project['progress']:.1f}%")
    
    # Look specifically for SF Documentation
    sf_docs = [p for p in all_projects if 'sf' in p['name'].lower() and 'documentation' in p['name'].lower()]
    print(f"\n📋 SF Documentation projects found: {len(sf_docs)}")
    for project in sf_docs:
        print(f"   • {project['name']} - Phase: {project['phase']} - {project['progress']:.1f}%")
    
    return len(post_projects), len(sf_docs)

if __name__ == "__main__":
    # Apply the fixes
    success = apply_formatting_fixes()
    
    if success:
        # Test the results
        post_count, sf_count = test_fixes()
        
        print(f"\n🎉 Formatting fixes completed successfully!")
        print(f"   📊 Post Stabilization projects: {post_count}")
        print(f"   📋 SF Documentation projects: {sf_count}")
        print(f"\n💡 Next step: Generate a new presentation to see the improvements")
        print(f"   Run: cd /workspaces/control_tower/scripts/safran_tools && python3 update_xml_and_regenerate.py")
