#!/usr/bin/env python3
"""
HTML-Based Complete NADCAP Extractor
Uses the HTML conversion to extract all clause patterns more accurately
Specifically designed to capture all 181-182 expected clauses
"""

import re
import sys
import os
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from bs4 import BeautifulSoup

class HTMLBasedNADCAPExtractor:
    def __init__(self, html_path):
        self.html_path = html_path
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        self.all_clauses = {}
        
    def extract_comprehensive_clauses(self):
        """Extract all possible clause patterns from HTML"""
        print("🔍 COMPREHENSIVE CLAUSE EXTRACTION FROM HTML")
        print("=" * 55)
        
        # Initialize storage
        clause_levels = {
            '1_decimal': [],
            '2_decimal': [],
            '3_decimal': [],
            '4_decimal': [],
            '5_decimal': [],  # Add 5-decimal in case they exist
            'lettered': [],   # Like 1.a, 2.b etc
            'parenthetical': []  # Like 1(a), 2(b) etc
        }
        
        # Enhanced patterns to catch more variations
        patterns = {
            '1_decimal': [
                r'\b(\d+\.\d+)\b(?!\.\d)',  # Standard 1.1, 2.5
                r'^(\d+\.\d+)\s',           # At start of line
                r'(\d+\.\d+)\s*[A-Z]',      # Followed by capital letter
            ],
            '2_decimal': [
                r'\b(\d+\.\d+\.\d+)\b(?!\.\d)',
                r'^(\d+\.\d+\.\d+)\s',
                r'(\d+\.\d+\.\d+)\s*[A-Z]',
            ],
            '3_decimal': [
                r'\b(\d+\.\d+\.\d+\.\d+)\b(?!\.\d)',
                r'^(\d+\.\d+\.\d+\.\d+)\s',
                r'(\d+\.\d+\.\d+\.\d+)\s*[A-Z]',
            ],
            '4_decimal': [
                r'\b(\d+\.\d+\.\d+\.\d+\.\d+)\b(?!\.\d)',
                r'^(\d+\.\d+\.\d+\.\d+\.\d+)\s',
                r'(\d+\.\d+\.\d+\.\d+\.\d+)\s*[A-Z]',
            ],
            '5_decimal': [
                r'\b(\d+\.\d+\.\d+\.\d+\.\d+\.\d+)\b',
                r'^(\d+\.\d+\.\d+\.\d+\.\d+\.\d+)\s',
            ],
            'lettered': [
                r'\b(\d+\.[a-z]+)\b',       # 1.a, 2.b
                r'\b(\d+\.\d+\.[a-z]+)\b', # 1.1.a, 2.3.b
            ],
            'parenthetical': [
                r'\b(\d+\([a-z]+\))\b',     # 1(a), 2(b)
                r'\b(\d+\.\d+\([a-z]+\))\b', # 1.1(a), 2.3(b)
            ]
        }
        
        # Get all pages
        pages = self.soup.find_all('div', class_='page')
        print(f"Found {len(pages)} pages to process")
        
        total_found = 0
        
        for page_idx, page in enumerate(pages):
            page_num = page_idx + 1
            page_text = page.get_text()
            
            # Also look at the raw HTML to catch clauses that might be in spans
            page_html = str(page)
            
            # Search in both text and HTML
            search_contents = [page_text, page_html]
            
            for level, pattern_list in patterns.items():
                found_in_page = set()
                
                for content in search_contents:
                    for pattern in pattern_list:
                        matches = re.findall(pattern, content, re.MULTILINE)
                        found_in_page.update(matches)
                
                # Process each found clause
                for match in found_in_page:
                    # Clean the match
                    match = match.strip()
                    if not match:
                        continue
                    
                    # Find context around this clause
                    context = self.extract_clause_context(page, match, page_text)
                    
                    clause_data = {
                        'Page': page_num,
                        'Clause_Number': match,
                        'Question': context.get('question', ''),
                        'Guidance': context.get('guidance', ''),
                        'Yes_No_NA': context.get('response', ''),
                        'Section': self.determine_section(match),
                        'Context': context.get('full_context', ''),
                        'Level': level
                    }
                    
                    clause_levels[level].append(clause_data)
                    total_found += 1
            
            if page_num % 10 == 0:
                print(f"  Processed page {page_num}, found {total_found} total clauses so far")
        
        # Remove duplicates and sort
        final_totals = {}
        for level in clause_levels:
            # Remove duplicates based on clause number
            unique_clauses = {}
            for clause in clause_levels[level]:
                clause_num = clause['Clause_Number']
                if clause_num not in unique_clauses:
                    unique_clauses[clause_num] = clause
                else:
                    # Keep the one with more context
                    existing = unique_clauses[clause_num]
                    if len(clause['Question']) > len(existing['Question']):
                        unique_clauses[clause_num] = clause
            
            # Convert back to list and sort
            clause_levels[level] = list(unique_clauses.values())
            if clause_levels[level]:
                clause_levels[level].sort(key=lambda x: self.sort_key(x['Clause_Number']))
            
            final_totals[level] = len(clause_levels[level])
            if final_totals[level] > 0:
                print(f"  {level:15s}: {final_totals[level]:3d} unique clauses")
        
        total_unique = sum(final_totals.values())
        print(f"  {'TOTAL UNIQUE':15s}: {total_unique:3d} clauses")
        
        self.all_clauses = clause_levels
        return clause_levels, total_unique
    
    def extract_clause_context(self, page, clause_number, page_text):
        """Extract context around a clause number"""
        context = {
            'question': '',
            'guidance': '',
            'response': '',
            'full_context': ''
        }
        
        # Split page into lines for analysis
        lines = page_text.split('\n')
        
        # Find the line with this clause number
        clause_line_idx = -1
        for i, line in enumerate(lines):
            if clause_number in line:
                clause_line_idx = i
                break
        
        if clause_line_idx >= 0:
            # Extract context around the clause
            start_idx = max(0, clause_line_idx - 2)
            end_idx = min(len(lines), clause_line_idx + 10)
            
            context_lines = lines[start_idx:end_idx]
            context['full_context'] = ' '.join([l.strip() for l in context_lines if l.strip()])
            
            # Look for question text (usually after clause number)
            question_parts = []
            for i in range(clause_line_idx, min(clause_line_idx + 5, len(lines))):
                line = lines[i].strip()
                if line and not re.match(r'^(YES|NO|NA|Guidance:)', line, re.IGNORECASE):
                    # Remove clause number from line
                    cleaned_line = re.sub(r'\b\d+\.\d+(\.\d+)*\s*', '', line).strip()
                    if cleaned_line and len(cleaned_line) > 3:
                        question_parts.append(cleaned_line)
            
            context['question'] = ' '.join(question_parts)[:200]  # Limit length
            
            # Look for guidance
            for i in range(clause_line_idx, min(clause_line_idx + 8, len(lines))):
                line = lines[i].strip()
                if line.lower().startswith('guidance:'):
                    guidance_parts = [line]
                    # Get following guidance lines
                    for j in range(i + 1, min(i + 4, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not re.match(r'^(YES|NO|NA|\d+\.\d+)', next_line):
                            guidance_parts.append(next_line)
                        else:
                            break
                    context['guidance'] = ' '.join(guidance_parts)[:200]
                    break
            
            # Look for YES/NO/NA
            for i in range(clause_line_idx, min(clause_line_idx + 6, len(lines))):
                line = lines[i].strip()
                if re.search(r'\b(YES|NO|NA)\b', line, re.IGNORECASE):
                    context['response'] = 'YES/NO/NA'
                    break
        
        return context
    
    def determine_section(self, clause_number):
        """Determine section based on clause number"""
        # Handle different formats
        if re.match(r'^\d+\.\d+', clause_number):
            main_section = clause_number.split('.')[0]
        elif re.match(r'^\d+', clause_number):
            main_section = clause_number[0]
        else:
            main_section = '0'
        
        section_mapping = {
            '1': 'General Requirements',
            '2': 'Quality Management System', 
            '3': 'Process and Quality Planning',
            '4': 'Testing Requirements',
            '5': 'Equipment Requirements',
            '6': 'Additional Requirements',
            '7': 'Appendices',
            '8': 'References',
            '9': 'Other'
        }
        
        return section_mapping.get(main_section, f'Section {main_section}')
    
    def sort_key(self, clause_number):
        """Create a sorting key for clause numbers"""
        try:
            # Handle numeric decimal clauses
            if re.match(r'^\d+(\.\d+)*$', clause_number):
                parts = clause_number.split('.')
                return tuple(int(part) for part in parts)
            else:
                # Handle non-standard formats
                return (999, clause_number)
        except:
            return (999, clause_number)
    
    def create_enhanced_excel_output(self, output_filename="comprehensive_nadcap_extraction.xlsx"):
        """Create comprehensive Excel output with all found clauses"""
        print(f"\n📊 CREATING ENHANCED EXCEL OUTPUT: {output_filename}")
        print("=" * 60)
        
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        # Define styles
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        center_alignment = Alignment(horizontal="center", vertical="center")
        
        # Create tabs for each level that has clauses
        tab_count = 0
        for level in ['1_decimal', '2_decimal', '3_decimal', '4_decimal', '5_decimal', 'lettered', 'parenthetical']:
            clauses = self.all_clauses.get(level, [])
            
            if not clauses:
                continue
            
            # Create worksheet
            tab_name = level.replace('_decimal', '-Dec').replace('_', ' ').title()
            ws = wb.create_sheet(title=tab_name)
            
            # Create DataFrame
            df = pd.DataFrame(clauses)
            
            # Reorder columns
            column_order = ['Page', 'Section', 'Clause_Number', 'Question', 'Guidance', 'Yes_No_NA', 'Level']
            df = df.reindex(columns=column_order)
            
            # Rename columns
            df.columns = ['Page', 'Section', 'Clause Number', 'Question', 'Guidance', 'Yes/No/NA', 'Type']
            
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
                
                adjusted_width = min(max(max_length + 2, 12), 100)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            print(f"  ✅ Created tab '{tab_name}' with {len(clauses)} clauses")
            tab_count += 1
        
        # Create comprehensive summary tab
        ws_summary = wb.create_sheet(title="Summary", index=0)
        
        total_clauses = sum(len(self.all_clauses.get(level, [])) for level in self.all_clauses)
        
        summary_data = [
            ['COMPREHENSIVE NADCAP EXTRACTION SUMMARY', ''],
            ['', ''],
            ['Extraction Method', 'HTML-Based Enhanced Pattern Matching'],
            ['', ''],
            ['Clause Type', 'Count'],
            ['1-Decimal Clauses', len(self.all_clauses.get('1_decimal', []))],
            ['2-Decimal Clauses', len(self.all_clauses.get('2_decimal', []))],
            ['3-Decimal Clauses', len(self.all_clauses.get('3_decimal', []))],
            ['4-Decimal Clauses', len(self.all_clauses.get('4_decimal', []))],
            ['5-Decimal Clauses', len(self.all_clauses.get('5_decimal', []))],
            ['Lettered Clauses', len(self.all_clauses.get('lettered', []))],
            ['Parenthetical Clauses', len(self.all_clauses.get('parenthetical', []))],
            ['', ''],
            ['TOTAL CLAUSES FOUND', total_clauses],
            ['TARGET (Expected)', '181-182'],
            ['Coverage', f'{(total_clauses/182)*100:.1f}%'],
            ['', ''],
            ['Source HTML File', self.html_path],
        ]
        
        for row in summary_data:
            ws_summary.append(row)
        
        # Style summary
        ws_summary['A1'].font = Font(bold=True, size=16, color="FF0000")
        ws_summary['A14'].font = Font(bold=True, size=14, color="FF0000")
        ws_summary['B14'].font = Font(bold=True, size=14, color="FF0000")
        
        ws_summary.column_dimensions['A'].width = 30
        ws_summary.column_dimensions['B'].width = 25
        
        # Save workbook
        wb.save(output_filename)
        print(f"  ✅ Excel file saved: {output_filename}")
        print(f"  📊 Total tabs created: {tab_count + 1} (including summary)")
        
        return output_filename
    
    def generate_detailed_report(self, total_found):
        """Generate detailed extraction report"""
        print(f"\n📋 DETAILED EXTRACTION REPORT")
        print("=" * 50)
        
        print(f"Total clauses found: {total_found}")
        print(f"Target clauses: 181-182")
        print(f"Coverage: {(total_found/182)*100:.1f}%")
        
        if total_found >= 181:
            print("🎯 SUCCESS: Found expected number of clauses!")
        elif total_found >= 160:
            print("✅ GOOD: Found most clauses, minor gaps remain")
        elif total_found >= 140:
            print("⚠️  PARTIAL: Found majority but significant gaps")
        else:
            print("❌ INCOMPLETE: Major clauses missing")
        
        # Show examples from each category
        for level, clauses in self.all_clauses.items():
            if clauses:
                print(f"\n{level.replace('_', ' ').title()}:")
                examples = [c['Clause_Number'] for c in clauses[:8]]
                print(f"  Examples: {', '.join(examples)}")
                if len(clauses) > 8:
                    print(f"  ... and {len(clauses) - 8} more")
        
        return total_found

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 html_based_extractor.py <path_to_html_file>")
        print("Note: First run multi_format_converter.py to generate the HTML file")
        sys.exit(1)
    
    html_path = sys.argv[1]
    
    if not os.path.exists(html_path):
        print(f"Error: HTML file not found: {html_path}")
        print("Run multi_format_converter.py first to generate the HTML file")
        sys.exit(1)
    
    print("🚀 HTML-BASED COMPREHENSIVE NADCAP EXTRACTOR")
    print("=" * 55)
    print(f"📄 Processing: {html_path}")
    
    extractor = HTMLBasedNADCAPExtractor(html_path)
    
    # Extract all clauses
    clauses, total_found = extractor.extract_comprehensive_clauses()
    
    # Generate detailed report
    extractor.generate_detailed_report(total_found)
    
    if total_found > 0:
        # Create Excel output
        excel_file = extractor.create_enhanced_excel_output()
        
        print(f"\n🎯 EXTRACTION COMPLETE!")
        print(f"  Total clauses: {total_found}")
        print(f"  Excel output: {excel_file}")
        print(f"  Target achieved: {(total_found/182)*100:.1f}%")
    else:
        print("❌ No clauses found!")

if __name__ == "__main__":
    main()
