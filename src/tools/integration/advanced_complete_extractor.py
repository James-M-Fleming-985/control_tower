#!/usr/bin/env python3
"""
Advanced Complete NADCAP Extractor
Based on successful advanced_pdf_converter.py findings
Creates comprehensive Excel output with all clause levels
"""

import fitz  # PyMuPDF
import pandas as pd
import re
import sys
import os
from pathlib import Path
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

class AdvancedCompleteNADCAPExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.all_clauses = {}  # Store by decimal level
        
    def extract_all_clauses(self):
        """Extract all clause levels using the successful PyMuPDF method"""
        print("🔍 EXTRACTING ALL CLAUSE LEVELS")
        print("=" * 50)
        
        # Initialize storage for different decimal levels
        clause_levels = {
            '1_decimal': [],
            '2_decimal': [],
            '3_decimal': [],
            '4_decimal': []
        }
        
        # Patterns for different decimal levels
        patterns = {
            '1_decimal': r'\b(\d+\.\d+)\b(?!\.\d)',  # 1.1, 2.5 but not 1.1.2
            '2_decimal': r'\b(\d+\.\d+\.\d+)\b(?!\.\d)',  # 1.1.2, 3.5.1 but not 1.1.2.3
            '3_decimal': r'\b(\d+\.\d+\.\d+\.\d+)\b(?!\.\d)',  # 1.1.2.3 but not 1.1.2.3.4
            '4_decimal': r'\b(\d+\.\d+\.\d+\.\d+\.\d+)\b'  # 1.1.2.3.4
        }
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            # Extract clauses for each level
            for level, pattern in patterns.items():
                matches = re.findall(pattern, text)
                
                for match in matches:
                    # Find the line containing this clause
                    clause_line = None
                    question_text = ""
                    guidance_text = ""
                    yes_no_na = ""
                    
                    for i, line in enumerate(lines):
                        if match in line:
                            clause_line = line.strip()
                            
                            # Look for question text (usually follows the clause number)
                            question_parts = []
                            for j in range(i, min(i + 5, len(lines))):
                                line_content = lines[j].strip()
                                if line_content and not re.match(r'^(YES|NO|NA|Guidance:)', line_content):
                                    if match in line_content:
                                        # Remove the clause number to get the question
                                        question_parts.append(line_content.replace(match, '').strip())
                                    elif not re.match(r'^\d+\.\d+', line_content):
                                        question_parts.append(line_content)
                                else:
                                    break
                            
                            question_text = ' '.join(question_parts).strip()
                            
                            # Look for guidance text
                            for j in range(i + 1, min(i + 10, len(lines))):
                                if lines[j].strip().startswith('Guidance:'):
                                    guidance_parts = [lines[j].strip()]
                                    for k in range(j + 1, min(j + 5, len(lines))):
                                        if lines[k].strip() and not re.match(r'^(YES|NO|NA|\d+\.\d+)', lines[k]):
                                            guidance_parts.append(lines[k].strip())
                                        else:
                                            break
                                    guidance_text = ' '.join(guidance_parts)
                                    break
                            
                            # Look for YES/NO/NA indicators
                            for j in range(i + 1, min(i + 8, len(lines))):
                                line_check = lines[j].strip()
                                if re.search(r'\b(YES|NO|NA)\b', line_check):
                                    yes_no_na = "YES/NO/NA"
                                    break
                            
                            break
                    
                    # Clean up question text
                    if question_text:
                        question_text = re.sub(r'\s+', ' ', question_text)
                        question_text = question_text.replace(match, '').strip()
                        if question_text.startswith(':'):
                            question_text = question_text[1:].strip()
                    
                    # Store the clause data
                    clause_data = {
                        'Page': page_num + 1,
                        'Clause_Number': match,
                        'Question': question_text,
                        'Guidance': guidance_text,
                        'Yes_No_NA': yes_no_na,
                        'Section': self.determine_section(match),
                        'Raw_Line': clause_line
                    }
                    
                    clause_levels[level].append(clause_data)
            
            if (page_num + 1) % 10 == 0:
                print(f"  Processed page {page_num + 1}")
        
        # Remove duplicates and sort
        for level in clause_levels:
            # Remove duplicates based on clause number
            unique_clauses = {}
            for clause in clause_levels[level]:
                clause_num = clause['Clause_Number']
                if clause_num not in unique_clauses:
                    unique_clauses[clause_num] = clause
                else:
                    # Keep the one with more content
                    existing = unique_clauses[clause_num]
                    if len(clause['Question']) > len(existing['Question']):
                        unique_clauses[clause_num] = clause
            
            # Convert back to list and sort
            clause_levels[level] = list(unique_clauses.values())
            clause_levels[level].sort(key=lambda x: self.sort_key(x['Clause_Number']))
            
            print(f"  {level}: {len(clause_levels[level])} clauses found")
        
        self.all_clauses = clause_levels
        return clause_levels
    
    def determine_section(self, clause_number):
        """Determine section based on clause number"""
        parts = clause_number.split('.')
        main_section = parts[0]
        
        section_mapping = {
            '1': 'General Requirements',
            '2': 'Quality Management System', 
            '3': 'Process and Quality Planning',
            '4': 'Testing Requirements',
            '5': 'Equipment Requirements'
        }
        
        return section_mapping.get(main_section, f'Section {main_section}')
    
    def sort_key(self, clause_number):
        """Create a sorting key for clause numbers"""
        parts = clause_number.split('.')
        return tuple(int(part) for part in parts)
    
    def create_excel_output(self, output_filename="advanced_complete_nadcap_extraction.xlsx"):
        """Create comprehensive Excel output with multiple tabs"""
        print(f"\n📊 CREATING EXCEL OUTPUT: {output_filename}")
        print("=" * 50)
        
        wb = Workbook()
        # Remove default sheet
        wb.remove(wb.active)
        
        # Define styles
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        center_alignment = Alignment(horizontal="center", vertical="center")
        
        # Create tabs for each decimal level
        for level in ['1_decimal', '2_decimal', '3_decimal', '4_decimal']:
            clauses = self.all_clauses.get(level, [])
            
            if not clauses:
                print(f"  Skipping {level} - no clauses found")
                continue
            
            # Create worksheet
            tab_name = f"{level.replace('_decimal', '')}-Decimal"
            ws = wb.create_sheet(title=tab_name)
            
            # Create DataFrame
            df = pd.DataFrame(clauses)
            
            # Reorder columns
            column_order = ['Page', 'Section', 'Clause_Number', 'Question', 'Guidance', 'Yes_No_NA']
            df = df.reindex(columns=column_order)
            
            # Rename columns for better display
            df.columns = ['Page', 'Section', 'Clause Number', 'Question', 'Guidance', 'Yes/No/NA']
            
            # Add data to worksheet
            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)
            
            # Style headers
            for cell in ws[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set reasonable limits
                adjusted_width = min(max(max_length + 2, 10), 80)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            print(f"  ✅ Created tab '{tab_name}' with {len(clauses)} clauses")
        
        # Create summary tab
        ws_summary = wb.create_sheet(title="Summary", index=0)
        
        summary_data = [
            ['NADCAP Compliance Extraction Summary', ''],
            ['', ''],
            ['Extraction Level', 'Number of Clauses'],
            ['1-Decimal Clauses', len(self.all_clauses.get('1_decimal', []))],
            ['2-Decimal Clauses', len(self.all_clauses.get('2_decimal', []))],
            ['3-Decimal Clauses', len(self.all_clauses.get('3_decimal', []))],
            ['4-Decimal Clauses', len(self.all_clauses.get('4_decimal', []))],
            ['', ''],
            ['Total Clauses', sum(len(self.all_clauses.get(level, [])) for level in self.all_clauses)],
            ['', ''],
            ['PDF Source', self.pdf_path],
            ['Total Pages Processed', len(self.doc)]
        ]
        
        for row in summary_data:
            ws_summary.append(row)
        
        # Style summary
        ws_summary['A1'].font = Font(bold=True, size=16)
        for row in range(3, 8):
            ws_summary[f'A{row}'].font = Font(bold=True)
        
        ws_summary['A9'].font = Font(bold=True, color="FF0000")
        ws_summary['B9'].font = Font(bold=True, color="FF0000")
        
        # Auto-adjust summary columns
        ws_summary.column_dimensions['A'].width = 25
        ws_summary.column_dimensions['B'].width = 20
        
        # Save the workbook
        wb.save(output_filename)
        print(f"  ✅ Excel file saved: {output_filename}")
        
        return output_filename
    
    def generate_report(self):
        """Generate comprehensive extraction report"""
        print(f"\n📋 EXTRACTION REPORT")
        print("=" * 40)
        
        total_clauses = 0
        for level, clauses in self.all_clauses.items():
            count = len(clauses)
            total_clauses += count
            print(f"  {level:12s}: {count:3d} clauses")
            
            if count > 0:
                # Show some examples
                print(f"    Examples: {', '.join([c['Clause_Number'] for c in clauses[:5]])}")
        
        print(f"  {'TOTAL':12s}: {total_clauses:3d} clauses")
        
        return total_clauses
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 advanced_complete_extractor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("🚀 ADVANCED COMPLETE NADCAP EXTRACTOR")
    print("=" * 45)
    print(f"📄 Processing: {pdf_path}")
    
    extractor = AdvancedCompleteNADCAPExtractor(pdf_path)
    
    try:
        # Extract all clauses
        clauses = extractor.extract_all_clauses()
        
        # Generate report
        total = extractor.generate_report()
        
        if total > 0:
            # Create Excel output
            excel_file = extractor.create_excel_output()
            
            print(f"\n🎯 SUCCESS!")
            print(f"  Total clauses extracted: {total}")
            print(f"  Excel output: {excel_file}")
            print(f"  Check each tab for different decimal levels")
        else:
            print("❌ No clauses found!")
            
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
