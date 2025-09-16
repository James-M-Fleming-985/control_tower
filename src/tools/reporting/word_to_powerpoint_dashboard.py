#!/usr/bin/env python3
"""
Alternative Approach: Create 4-table dashboard using Word first, then convert to PowerPoint
This approach uses Word's better table handling, then moves the content to PowerPoint
"""

import os
import sys
from datetime import datetime
import glob
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

try:
    from docx import Document
    from docx.shared import Inches as DocxInches, Pt as DocxPt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️  python-docx not available. Install with: pip install python-docx")

def find_latest_milestone_files():
    """Find the latest milestone PowerPoint files."""
    reports_dir = "/workspaces/control_tower/reports"
    
    patterns = {
        'this_month': 'Step_by_Step_Documentation_and_Training_this_month_*.pptx',
        'next_month': 'Step_by_Step_Documentation_and_Training_next_month_planned_*.pptx', 
        'last_month': 'Step_by_Step_Documentation_and_Training_last_month_completed_*.pptx',
        'risks': 'Step_by_Step_Documentation_and_Training_risks_*.pptx'
    }
    
    files = {}
    for key, pattern in patterns.items():
        matching_files = glob.glob(os.path.join(reports_dir, pattern))
        if matching_files:
            latest_file = max(matching_files, key=os.path.getctime)
            files[key] = latest_file
            print(f"📄 Found {key}: {os.path.basename(latest_file)}")
    
    return files

def extract_table_data_from_pptx(pptx_file):
    """Extract table data from a PowerPoint file."""
    try:
        prs = Presentation(pptx_file)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, 'has_table') and shape.has_table:
                    table = shape.table
                    data = []
                    for row in table.rows:
                        row_data = []
                        for cell in row.cells:
                            row_data.append(cell.text.strip())
                        data.append(row_data)
                    return data
    except Exception as e:
        print(f"❌ Error extracting from {pptx_file}: {e}")
    return None

def create_word_dashboard():
    """Create the 4-table dashboard in Word first."""
    if not DOCX_AVAILABLE:
        return None
    
    print("🔍 Creating Word document with 4-table layout...")
    
    # Get source files
    files = find_latest_milestone_files()
    if len(files) != 4:
        print(f"❌ Need 4 files, found {len(files)}")
        return None
    
    # Create Word document
    doc = Document()
    
    # Add title
    title = doc.add_heading('ZnNi Line Development - Milestone Dashboard', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Extract table data from each PowerPoint
    table_data = {}
    titles = {
        'this_month': 'This Month\'s Milestones',
        'next_month': 'Next Month\'s Planned Milestones', 
        'last_month': 'Last Month\'s Completed Milestones',
        'risks': 'Risk Register'
    }
    
    for key, file_path in files.items():
        print(f"📊 Extracting data from {key}...")
        data = extract_table_data_from_pptx(file_path)
        if data:
            table_data[key] = {
                'title': titles[key],
                'data': data
            }
    
    # Create a 2x2 table structure in Word
    # Top row: This Month | Next Month
    # Bottom row: Last Month | Risks
    
    # Create container table (2x2)
    container_table = doc.add_table(rows=2, cols=2)
    container_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Define layout order (clockwise from top-left)
    layout_order = [
        ('this_month', 0, 0),    # Top-left
        ('next_month', 0, 1),    # Top-right  
        ('risks', 1, 1),         # Bottom-right
        ('last_month', 1, 0)     # Bottom-left
    ]
    
    for key, row_idx, col_idx in layout_order:
        if key in table_data:
            cell = container_table.cell(row_idx, col_idx)
            
            # Add title
            title_para = cell.paragraphs[0]
            title_para.text = table_data[key]['title']
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_run = title_para.runs[0]
            title_run.font.size = DocxPt(12)
            title_run.font.bold = True
            
            # Add milestone data
            data = table_data[key]['data']
            if data and len(data) > 1:  # Skip header row
                for row_data in data[1:]:  # Skip header
                    if row_data and any(cell.strip() for cell in row_data):  # Skip empty rows
                        para = cell.add_paragraph()
                        para.text = f"• {' | '.join(cell.strip() for cell in row_data if cell.strip())}"
                        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Save Word document
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    word_file = f"/workspaces/control_tower/reports/milestone_dashboard_{timestamp}.docx"
    doc.save(word_file)
    print(f"✅ Word dashboard saved: {word_file}")
    
    return word_file

def convert_word_to_powerpoint(word_file):
    """Convert the Word dashboard to PowerPoint."""
    if not word_file or not os.path.exists(word_file):
        print("❌ No Word file to convert")
        return None
    
    print("🔄 Converting Word to PowerPoint...")
    
    # Create new PowerPoint presentation
    prs = Presentation()
    
    # Add slide with title and content layout
    slide_layout = prs.slide_layouts[1]  # Title and Content
    slide = prs.slides.add_slide(slide_layout)
    
    # Set title
    title = slide.shapes.title
    title.text = "ZnNi Line Development - Milestone Dashboard"
    title.text_frame.paragraphs[0].font.size = Pt(24)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)  # Safran blue
    
    # Read Word document to extract text
    try:
        if DOCX_AVAILABLE:
            doc = Document(word_file)
            content_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    content_text.append(para.text.strip())
            
            # Add content to PowerPoint
            content = slide.placeholders[1]
            content.text = "\n".join(content_text)
            
            # Format content
            for paragraph in content.text_frame.paragraphs:
                paragraph.font.size = Pt(11)
                paragraph.font.name = 'Arial'
        
    except Exception as e:
        print(f"⚠️  Error reading Word content: {e}")
        # Fallback - add basic content
        content = slide.placeholders[1]
        content.text = "Dashboard content extracted from Word document"
    
    # Save PowerPoint
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pptx_file = f"/workspaces/control_tower/reports/REACh_ZnNi_Line_Dashboard_FromWord_{timestamp}.pptx"
    prs.save(pptx_file)
    print(f"✅ PowerPoint dashboard saved: {pptx_file}")
    
    return pptx_file

def create_alternative_pptx_dashboard():
    """Alternative: Create PowerPoint with simplified positioning approach."""
    print("🔧 Trying alternative PowerPoint approach with simplified positioning...")
    
    files = find_latest_milestone_files()
    if len(files) != 4:
        print(f"❌ Need 4 files, found {len(files)}")
        return None
    
    # Create new presentation
    prs = Presentation()
    
    # Add blank slide
    blank_slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(blank_slide_layout)
    
    # Add main title
    title_left = Inches(1)
    title_top = Inches(0.5)
    title_width = Inches(8)
    title_height = Inches(0.8)
    
    title_textbox = slide.shapes.add_textbox(title_left, title_top, title_width, title_height)
    title_frame = title_textbox.text_frame
    title_frame.text = "ZnNi Line Development - Milestone Dashboard"
    title_para = title_frame.paragraphs[0]
    title_para.alignment = PP_ALIGN.CENTER
    title_para.font.size = Pt(20)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(0, 51, 102)
    
    # Simple vertical layout instead of 2x2 grid
    print("📊 Using vertical layout to avoid positioning issues...")
    
    titles = {
        'this_month': 'This Month\'s Milestones',
        'next_month': 'Next Month\'s Planned Milestones', 
        'last_month': 'Last Month\'s Completed Milestones',
        'risks': 'Risk Register'
    }
    
    y_positions = [Inches(1.5), Inches(3.5), Inches(5.5), Inches(7.5)]
    
    for i, (key, file_path) in enumerate(files.items()):
        if i < len(y_positions):
            # Extract data
            data = extract_table_data_from_pptx(file_path)
            if data:
                # Add section title
                section_left = Inches(0.5)
                section_top = y_positions[i]
                section_width = Inches(9)
                section_height = Inches(1.5)
                
                section_textbox = slide.shapes.add_textbox(section_left, section_top, section_width, section_height)
                section_frame = section_textbox.text_frame
                section_frame.text = f"{titles[key]}:\n"
                
                # Add milestone data
                if len(data) > 1:  # Skip header
                    for row_data in data[1:3]:  # Limit to first 2 milestones
                        if row_data and any(cell.strip() for cell in row_data):
                            milestone_text = " | ".join(cell.strip() for cell in row_data if cell.strip())
                            section_frame.text += f"• {milestone_text}\n"
                
                # Format text
                section_para = section_frame.paragraphs[0]
                section_para.font.size = Pt(10)
                section_para.font.name = 'Arial'
    
    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pptx_file = f"/workspaces/control_tower/reports/REACh_ZnNi_Line_Dashboard_Vertical_{timestamp}.pptx"
    prs.save(pptx_file)
    print(f"✅ Vertical dashboard saved: {pptx_file}")
    
    return pptx_file

def main():
    """Main function to try multiple approaches."""
    print("🚀 Starting dashboard creation with multiple approaches...")
    
    success_files = []
    
    # Approach 1: Word first, then PowerPoint
    if DOCX_AVAILABLE:
        print("\n📝 Approach 1: Creating via Word document...")
        word_file = create_word_dashboard()
        if word_file:
            pptx_file = convert_word_to_powerpoint(word_file)
            if pptx_file:
                success_files.append(pptx_file)
    else:
        print("\n⚠️  Approach 1 skipped: python-docx not available")
    
    # Approach 2: Simplified PowerPoint with vertical layout
    print("\n📊 Approach 2: Simplified PowerPoint vertical layout...")
    vertical_file = create_alternative_pptx_dashboard()
    if vertical_file:
        success_files.append(vertical_file)
    
    # Results
    print(f"\n🎯 Results:")
    if success_files:
        print(f"✅ Created {len(success_files)} dashboard file(s):")
        for file in success_files:
            print(f"   📄 {file}")
    else:
        print("❌ No dashboard files created successfully")
    
    return success_files

if __name__ == "__main__":
    main()
