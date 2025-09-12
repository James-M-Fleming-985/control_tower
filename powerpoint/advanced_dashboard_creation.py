#!/usr/bin/env python3
"""
Advanced Dashboard Creation: Using PowerPoint with precise EMU positioning
This approach uses exact EMU (English Metric Units) for pixel-perfect positioning
"""

import os
import sys
from datetime import datetime
import glob
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

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

def create_precise_positioned_dashboard():
    """Create dashboard with precise EMU positioning to avoid overlaps."""
    print("🎯 Creating dashboard with precise EMU positioning...")
    
    files = find_latest_milestone_files()
    if len(files) != 4:
        print(f"❌ Need 4 files, found {len(files)}")
        return None
    
    # Create new presentation
    prs = Presentation()
    
    # Add blank slide
    blank_slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(blank_slide_layout)
    
    # Slide dimensions: 10" x 7.5" (standard)
    slide_width = Emu(9144000)   # 10 inches in EMU
    slide_height = Emu(6858000)  # 7.5 inches in EMU
    
    print(f"📐 Slide dimensions: {slide_width} x {slide_height} EMU")
    
    # Add main title with precise positioning
    title_left = Emu(914400)     # 1 inch from left
    title_top = Emu(457200)      # 0.5 inch from top
    title_width = Emu(7315200)   # 8 inches wide
    title_height = Emu(685800)   # 0.75 inch high
    
    title_textbox = slide.shapes.add_textbox(title_left, title_top, title_width, title_height)
    title_frame = title_textbox.text_frame
    title_frame.text = "ZnNi Line Development - Milestone Dashboard"
    title_para = title_frame.paragraphs[0]
    title_para.alignment = PP_ALIGN.CENTER
    title_para.font.size = Pt(18)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(0, 51, 102)
    
    # Define 2x2 grid positions using EMU for precision
    # Grid spacing: 4.5" wide x 2.75" high per quadrant
    grid_width = Emu(4114800)    # 4.5 inches
    grid_height = Emu(2514600)   # 2.75 inches
    margin_x = Emu(457200)       # 0.5 inch margin
    margin_y = Emu(1371600)      # 1.5 inch from top (below title)
    spacing_x = Emu(228600)      # 0.25 inch spacing between columns
    spacing_y = Emu(228600)      # 0.25 inch spacing between rows
    
    # Calculate exact positions
    positions = {
        'this_month': {
            'left': margin_x,
            'top': margin_y,
            'width': grid_width,
            'height': grid_height,
            'title': 'This Month\'s Milestones'
        },
        'next_month': {
            'left': margin_x + grid_width + spacing_x,
            'top': margin_y, 
            'width': grid_width,
            'height': grid_height,
            'title': 'Next Month\'s Planned'
        },
        'last_month': {
            'left': margin_x,
            'top': margin_y + grid_height + spacing_y,
            'width': grid_width,
            'height': grid_height,
            'title': 'Last Month\'s Completed'
        },
        'risks': {
            'left': margin_x + grid_width + spacing_x,
            'top': margin_y + grid_height + spacing_y,
            'width': grid_width,
            'height': grid_height,
            'title': 'Risk Register'
        }
    }
    
    # Verify positions don't overlap
    print("📐 Verifying positions...")
    for key, pos in positions.items():
        right_edge = pos['left'] + pos['width']
        bottom_edge = pos['top'] + pos['height']
        print(f"   {key}: ({pos['left']}, {pos['top']}) to ({right_edge}, {bottom_edge})")
    
    # Create each quadrant
    for key, file_path in files.items():
        if key in positions:
            pos = positions[key]
            print(f"📊 Creating {key} at precise position...")
            
            # Extract data from source PowerPoint
            data = extract_table_data_from_pptx(file_path)
            
            # Add background rectangle
            bg_rect = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, 
                pos['left'], pos['top'], pos['width'], pos['height']
            )
            bg_fill = bg_rect.fill
            bg_fill.solid()
            bg_fill.fore_color.rgb = RGBColor(240, 248, 255)  # Light blue background
            
            bg_line = bg_rect.line
            bg_line.color.rgb = RGBColor(0, 51, 102)
            bg_line.width = Pt(1)
            
            # Add section title
            title_height_emu = Emu(457200)  # 0.5 inch for title
            section_title = slide.shapes.add_textbox(
                pos['left'] + Emu(114300),  # 0.125 inch padding
                pos['top'] + Emu(114300),   # 0.125 inch padding
                pos['width'] - Emu(228600), # 0.25 inch total padding
                title_height_emu
            )
            
            title_frame = section_title.text_frame
            title_frame.text = pos['title']
            title_para = title_frame.paragraphs[0]
            title_para.alignment = PP_ALIGN.CENTER
            title_para.font.size = Pt(12)
            title_para.font.bold = True
            title_para.font.color.rgb = RGBColor(0, 51, 102)
            
            # Add milestone data
            content_top = pos['top'] + title_height_emu + Emu(114300)  # Below title
            content_height = pos['height'] - title_height_emu - Emu(228600)  # Remaining space
            
            content_box = slide.shapes.add_textbox(
                pos['left'] + Emu(114300),   # 0.125 inch padding
                content_top,
                pos['width'] - Emu(228600),  # 0.25 inch total padding
                content_height
            )
            
            content_frame = content_box.text_frame
            content_frame.word_wrap = True
            
            if data and len(data) > 1:  # Skip header row
                milestone_count = 0
                for row_data in data[1:]:  # Skip header
                    if row_data and any(cell.strip() for cell in row_data) and milestone_count < 3:
                        milestone_text = " | ".join(cell.strip() for cell in row_data if cell.strip())
                        if milestone_count > 0:
                            content_frame.text += "\\n"
                        content_frame.text += f"• {milestone_text}"
                        milestone_count += 1
            else:
                content_frame.text = "No milestones found"
            
            # Format content
            for paragraph in content_frame.paragraphs:
                paragraph.font.size = Pt(9)
                paragraph.font.name = 'Arial'
                paragraph.alignment = PP_ALIGN.LEFT
    
    # Save with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pptx_file = f"/workspaces/control_tower/reports/REACh_ZnNi_Line_Dashboard_Precise_{timestamp}.pptx"
    prs.save(pptx_file)
    print(f"✅ Precise dashboard saved: {pptx_file}")
    
    return pptx_file

def create_table_based_dashboard():
    """Create dashboard using actual PowerPoint tables instead of text boxes."""
    print("📋 Creating dashboard with actual PowerPoint tables...")
    
    files = find_latest_milestone_files()
    if len(files) != 4:
        print(f"❌ Need 4 files, found {len(files)}")
        return None
    
    # Create new presentation
    prs = Presentation()
    
    # Add slide with table layout
    slide_layout = prs.slide_layouts[5]  # Blank slide
    slide = prs.slides.add_slide(slide_layout)
    
    # Add main title
    title_shape = slide.shapes.add_textbox(
        Inches(1), Inches(0.2), Inches(8), Inches(0.8)
    )
    title_frame = title_shape.text_frame
    title_frame.text = "ZnNi Line Development - Milestone Dashboard"
    title_para = title_frame.paragraphs[0]
    title_para.alignment = PP_ALIGN.CENTER
    title_para.font.size = Pt(18)
    title_para.font.bold = True
    title_para.font.color.rgb = RGBColor(0, 51, 102)
    
    # Create a 3x3 table (header + 2x2 data)
    rows = 3
    cols = 3
    left = Inches(0.5)
    top = Inches(1.2)
    width = Inches(9)
    height = Inches(5.5)
    
    table = slide.shapes.add_table(rows, cols, left, top, width, height).table
    
    # Set column widths
    table.columns[0].width = Inches(3)
    table.columns[1].width = Inches(3)
    table.columns[2].width = Inches(3)
    
    # Headers row
    table.cell(0, 0).text = "Period"
    table.cell(0, 1).text = "This Month"
    table.cell(0, 2).text = "Next Month"
    
    # Data rows
    table.cell(1, 0).text = "Last Month"
    table.cell(2, 0).text = "Risks"
    
    # Extract and populate data
    data_mapping = {
        'this_month': (0, 1),
        'next_month': (0, 2), 
        'last_month': (1, 0),
        'risks': (2, 0)
    }
    
    for key, file_path in files.items():
        if key in data_mapping:
            row, col = data_mapping[key]
            if row == 0:  # Adjust for header row
                row = 1 if col == 1 else 1  # This month and next month in row 1
                col = col
            else:
                row = row + 1  # Adjust for header
                col = 1  # Content goes in column 1
            
            # Extract data
            data = extract_table_data_from_pptx(file_path)
            if data and len(data) > 1:
                milestone_text = ""
                count = 0
                for row_data in data[1:]:  # Skip header
                    if row_data and any(cell.strip() for cell in row_data) and count < 2:
                        text = " | ".join(cell.strip() for cell in row_data if cell.strip())
                        if milestone_text:
                            milestone_text += "\\n"
                        milestone_text += f"• {text}"
                        count += 1
                
                table.cell(row, col).text = milestone_text
            
            # Format cell
            cell = table.cell(row, col)
            cell.text_frame.paragraphs[0].font.size = Pt(9)
    
    # Format table
    for row in table.rows:
        for cell in row.cells:
            cell.text_frame.margin_left = Inches(0.1)
            cell.text_frame.margin_right = Inches(0.1)
            cell.text_frame.margin_top = Inches(0.05)
            cell.text_frame.margin_bottom = Inches(0.05)
    
    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pptx_file = f"/workspaces/control_tower/reports/REACh_ZnNi_Line_Dashboard_Table_{timestamp}.pptx"
    prs.save(pptx_file)
    print(f"✅ Table dashboard saved: {pptx_file}")
    
    return pptx_file

def main():
    """Main function to try multiple precise approaches."""
    print("🚀 Starting advanced dashboard creation...")
    
    success_files = []
    
    # Approach 1: Precise EMU positioning
    print("\\n🎯 Approach 1: Precise EMU positioning...")
    precise_file = create_precise_positioned_dashboard()
    if precise_file:
        success_files.append(precise_file)
    
    # Approach 2: Table-based layout
    print("\\n📋 Approach 2: Table-based layout...")
    table_file = create_table_based_dashboard()
    if table_file:
        success_files.append(table_file)
    
    # Results
    print(f"\\n🎯 Results:")
    if success_files:
        print(f"✅ Created {len(success_files)} advanced dashboard file(s):")
        for file in success_files:
            print(f"   📄 {file}")
    else:
        print("❌ No advanced dashboard files created")
    
    return success_files

if __name__ == "__main__":
    main()
