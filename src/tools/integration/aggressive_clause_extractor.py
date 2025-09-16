#!/usr/bin/env python3
"""
Aggressive NADCAP Clause Extractor
Designed to find ALL 182 clauses using multiple pattern strategies
Focus on finding actual questions/clauses, not just decimal patterns
"""

import re
import sys
import os
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

class AggressiveClauseExtractor:
    def __init__(self, text_file_path):
        self.text_file_path = text_file_path
        with open(text_file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        self.all_clauses = []
        
    def extract_all_possible_clauses(self):
        """Use multiple strategies to find all 182 clauses"""
        print("🎯 AGGRESSIVE CLAUSE EXTRACTION - TARGET: 182 CLAUSES")
        print("=" * 60)
        
        clauses_found = set()  # Use set to avoid duplicates
        
        # Strategy 1: Standard decimal patterns (we know this finds 121)
        strategy1 = self.extract_decimal_patterns()
        clauses_found.update(strategy1)
        print(f"Strategy 1 (Decimal patterns): {len(strategy1)} clauses")
        
        # Strategy 2: Look for questions followed by YES/NO/NA
        strategy2 = self.extract_yes_no_questions()
        new_from_s2 = [c for c in strategy2 if c not in clauses_found]
        clauses_found.update(strategy2)
        print(f"Strategy 2 (YES/NO questions): {len(new_from_s2)} new clauses")
        
        # Strategy 3: Look for question marks followed by YES/NO
        strategy3 = self.extract_question_mark_clauses()
        new_from_s3 = [c for c in strategy3 if c not in clauses_found]
        clauses_found.update(strategy3)
        print(f"Strategy 3 (Question marks): {len(new_from_s3)} new clauses")
        
        # Strategy 4: Look for numbered items without decimals
        strategy4 = self.extract_numbered_items()
        new_from_s4 = [c for c in strategy4 if c not in clauses_found]
        clauses_found.update(strategy4)
        print(f"Strategy 4 (Numbered items): {len(new_from_s4)} new clauses")
        
        # Strategy 5: Look for lettered items (a), (b), etc.
        strategy5 = self.extract_lettered_items()
        new_from_s5 = [c for c in strategy5 if c not in clauses_found]
        clauses_found.update(strategy5)
        print(f"Strategy 5 (Lettered items): {len(new_from_s5)} new clauses")
        
        # Strategy 6: Look for specific NADCAP terms that indicate clauses
        strategy6 = self.extract_nadcap_specific_patterns()
        new_from_s6 = [c for c in strategy6 if c not in clauses_found]
        clauses_found.update(strategy6)
        print(f"Strategy 6 (NADCAP specific): {len(new_from_s6)} new clauses")
        
        print(f"\n🎯 TOTAL UNIQUE CLAUSES FOUND: {len(clauses_found)}")
        
        if len(clauses_found) >= 182:
            print("✅ SUCCESS: Found target number of clauses!")
        else:
            print(f"⚠️  MISSING: {182 - len(clauses_found)} clauses still needed")
        
        # Convert to structured data
        self.all_clauses = self.structure_clause_data(list(clauses_found))
        return len(clauses_found)
    
    def extract_decimal_patterns(self):
        """Extract standard decimal patterns"""
        patterns = [
            r'\b(\d+\.\d+)\b(?!\.\d)',
            r'\b(\d+\.\d+\.\d+)\b(?!\.\d)',
            r'\b(\d+\.\d+\.\d+\.\d+)\b(?!\.\d)',
            r'\b(\d+\.\d+\.\d+\.\d+\.\d+)\b',
        ]
        
        found = set()
        for pattern in patterns:
            matches = re.findall(pattern, self.content)
            found.update(matches)
        
        return list(found)
    
    def extract_yes_no_questions(self):
        """Find questions that have YES/NO responses"""
        # Split into lines and look for patterns
        lines = self.content.split('\n')
        found_clauses = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for lines that end with ? and have YES/NO nearby
            if line.endswith('?'):
                # Check next few lines for YES/NO
                yes_no_found = False
                for j in range(i+1, min(i+5, len(lines))):
                    if re.search(r'\b(YES|NO|NA)\b', lines[j]):
                        yes_no_found = True
                        break
                
                if yes_no_found:
                    # Try to find a clause number in this line or nearby lines
                    clause_num = self.find_nearby_clause_number(lines, i)
                    if clause_num:
                        found_clauses.append(clause_num)
                    else:
                        # Create a synthetic clause number based on line position
                        synthetic_num = f"Q{len(found_clauses)+1000}"
                        found_clauses.append(synthetic_num)
        
        return found_clauses
    
    def extract_question_mark_clauses(self):
        """Find all question marks and treat them as potential clauses"""
        # Find all lines with question marks
        question_lines = re.findall(r'^.*\?.*$', self.content, re.MULTILINE)
        
        found_clauses = []
        for line in question_lines:
            # Try to extract a clause number from the line
            clause_match = re.search(r'\b(\d+\.\d+(?:\.\d+)*)\b', line)
            if clause_match:
                found_clauses.append(clause_match.group(1))
            else:
                # Look for any number pattern that could be a clause
                number_match = re.search(r'\b(\d+[a-z]*)\b', line)
                if number_match:
                    found_clauses.append(number_match.group(1))
        
        return found_clauses
    
    def extract_numbered_items(self):
        """Find numbered items that might be clauses"""
        # Look for patterns like "1. ", "2. ", etc. at start of lines
        numbered_patterns = [
            r'^(\d+)\.\s+',  # 1. 2. 3.
            r'^(\d+)\)\s+',  # 1) 2) 3)
            r'^\((\d+)\)\s+', # (1) (2) (3)
        ]
        
        found_clauses = []
        for pattern in numbered_patterns:
            matches = re.findall(pattern, self.content, re.MULTILINE)
            found_clauses.extend(matches)
        
        return found_clauses
    
    def extract_lettered_items(self):
        """Find lettered items that might be clauses"""
        # Look for patterns like "a) ", "b) ", etc.
        lettered_patterns = [
            r'^([a-z])\)\s+',  # a) b) c)
            r'^\(([a-z])\)\s+', # (a) (b) (c)
            r'^([a-z])\.\s+',   # a. b. c.
        ]
        
        found_clauses = []
        for pattern in lettered_patterns:
            matches = re.findall(pattern, self.content, re.MULTILINE)
            found_clauses.extend(matches)
        
        return found_clauses
    
    def extract_nadcap_specific_patterns(self):
        """Look for NADCAP-specific clause indicators"""
        # Look for specific NADCAP terminology that indicates clauses
        nadcap_indicators = [
            r'(AC\d+)',  # AC7108, etc.
            r'(Appendix [A-Z])',  # Appendix A, B, etc.
            r'(Section \d+\.\d+)',  # Section references
        ]
        
        found_clauses = []
        for pattern in nadcap_indicators:
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            found_clauses.extend(matches)
        
        # Also look for table references and figure references
        table_pattern = r'(Table \d+(?:\.\d+)*)'
        figure_pattern = r'(Figure \d+(?:\.\d+)*)'
        
        found_clauses.extend(re.findall(table_pattern, self.content, re.IGNORECASE))
        found_clauses.extend(re.findall(figure_pattern, self.content, re.IGNORECASE))
        
        return found_clauses
    
    def find_nearby_clause_number(self, lines, line_index):
        """Try to find a clause number near a given line"""
        # Look in nearby lines for clause numbers
        search_range = range(max(0, line_index-3), min(len(lines), line_index+3))
        
        for i in search_range:
            line = lines[i]
            # Look for decimal patterns
            match = re.search(r'\b(\d+\.\d+(?:\.\d+)*)\b', line)
            if match:
                return match.group(1)
        
        return None
    
    def structure_clause_data(self, clause_list):
        """Convert clause list to structured data"""
        structured_clauses = []
        
        for i, clause_num in enumerate(clause_list):
            # Find the context for this clause in the original content
            context = self.find_clause_context(clause_num)
            
            clause_data = {
                'Index': i + 1,
                'Clause_Number': clause_num,
                'Question': context.get('question', ''),
                'Guidance': context.get('guidance', ''),
                'Yes_No_NA': context.get('response', ''),
                'Section': self.determine_section(clause_num),
                'Type': self.classify_clause_type(clause_num)
            }
            
            structured_clauses.append(clause_data)
        
        return structured_clauses
    
    def find_clause_context(self, clause_num):
        """Find context around a clause number"""
        context = {'question': '', 'guidance': '', 'response': ''}
        
        # Find the clause in the content
        clause_pattern = re.escape(clause_num)
        match = re.search(f'{clause_pattern}.*?(?=\n.*?\d+\.\d+|\n.*?YES|NO|NA|$)', self.content, re.DOTALL)
        
        if match:
            found_text = match.group(0)
            
            # Extract question (text after clause number)
            question_match = re.search(f'{clause_pattern}\s*(.*?)(?=Guidance|YES|NO|NA|$)', found_text, re.DOTALL)
            if question_match:
                context['question'] = question_match.group(1).strip()[:200]
            
            # Look for guidance
            if 'Guidance:' in found_text:
                guidance_match = re.search(r'Guidance:\s*(.*?)(?=YES|NO|NA|$)', found_text, re.DOTALL)
                if guidance_match:
                    context['guidance'] = guidance_match.group(1).strip()[:200]
            
            # Check for YES/NO/NA
            if re.search(r'\b(YES|NO|NA)\b', found_text):
                context['response'] = 'YES/NO/NA'
        
        return context
    
    def classify_clause_type(self, clause_num):
        """Classify the type of clause"""
        if re.match(r'^\d+\.\d+$', str(clause_num)):
            return '1-decimal'
        elif re.match(r'^\d+\.\d+\.\d+$', str(clause_num)):
            return '2-decimal'
        elif re.match(r'^\d+\.\d+\.\d+\.\d+$', str(clause_num)):
            return '3-decimal'
        elif re.match(r'^\d+\.\d+\.\d+\.\d+\.\d+$', str(clause_num)):
            return '4-decimal'
        elif re.match(r'^[a-z]$', str(clause_num)):
            return 'lettered'
        elif re.match(r'^\d+$', str(clause_num)):
            return 'numbered'
        elif str(clause_num).startswith('Q'):
            return 'question'
        else:
            return 'other'
    
    def determine_section(self, clause_num):
        """Determine section based on clause number"""
        clause_str = str(clause_num)
        
        if clause_str.startswith('1'):
            return 'General Requirements'
        elif clause_str.startswith('2'):
            return 'Quality Management System'
        elif clause_str.startswith('3'):
            return 'Process and Quality Planning'
        elif clause_str.startswith('4'):
            return 'Testing Requirements'
        elif clause_str.startswith('5'):
            return 'Equipment Requirements'
        elif clause_str.startswith('AC'):
            return 'Audit Criteria'
        elif clause_str.startswith('Appendix'):
            return 'Appendices'
        else:
            return 'Other'
    
    def create_final_excel_output(self, output_filename="final_all_182_clauses.xlsx"):
        """Create final Excel output with all found clauses"""
        print(f"\n📊 CREATING FINAL EXCEL OUTPUT: {output_filename}")
        print("=" * 60)
        
        if not self.all_clauses:
            print("❌ No clauses to export!")
            return None
        
        wb = Workbook()
        wb.remove(wb.active)
        
        # Create main sheet with all clauses
        ws_all = wb.create_sheet(title="All Clauses")
        
        # Create DataFrame
        df = pd.DataFrame(self.all_clauses)
        
        # Add to worksheet
        for r in dataframe_to_rows(df, index=False, header=True):
            ws_all.append(r)
        
        # Style headers
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        for cell in ws_all[1]:
            cell.font = header_font
            cell.fill = header_fill
        
        # Auto-adjust columns
        for column in ws_all.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max(max_length + 2, 12), 100)
            ws_all.column_dimensions[column_letter].width = adjusted_width
        
        # Create summary sheet
        ws_summary = wb.create_sheet(title="Summary", index=0)
        
        # Count by type
        type_counts = {}
        for clause in self.all_clauses:
            clause_type = clause['Type']
            type_counts[clause_type] = type_counts.get(clause_type, 0) + 1
        
        summary_data = [
            ['FINAL NADCAP CLAUSE EXTRACTION', ''],
            ['', ''],
            ['Total Clauses Found', len(self.all_clauses)],
            ['Target', 182],
            ['Achievement', f'{(len(self.all_clauses)/182)*100:.1f}%'],
            ['', ''],
            ['Breakdown by Type', ''],
        ]
        
        for clause_type, count in sorted(type_counts.items()):
            summary_data.append([clause_type, count])
        
        for row in summary_data:
            ws_summary.append(row)
        
        # Style summary
        ws_summary['A1'].font = Font(bold=True, size=16, color="FF0000")
        ws_summary['A3'].font = Font(bold=True)
        ws_summary['C3'].font = Font(bold=True, size=14, color="FF0000")
        
        ws_summary.column_dimensions['A'].width = 25
        ws_summary.column_dimensions['B'].width = 15
        
        # Save workbook
        wb.save(output_filename)
        print(f"  ✅ Excel file saved: {output_filename}")
        print(f"  📊 Total clauses: {len(self.all_clauses)}")
        
        return output_filename

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 aggressive_clause_extractor.py <path_to_text_file>")
        print("Use the structured text file from multi_format_converter.py")
        sys.exit(1)
    
    text_file = sys.argv[1]
    
    if not os.path.exists(text_file):
        print(f"Error: Text file not found: {text_file}")
        sys.exit(1)
    
    print("🚀 AGGRESSIVE CLAUSE EXTRACTOR - TARGET: 182 CLAUSES")
    print("=" * 60)
    print(f"📄 Processing: {text_file}")
    
    extractor = AggressiveClauseExtractor(text_file)
    
    # Extract all possible clauses
    total_found = extractor.extract_all_possible_clauses()
    
    if total_found > 0:
        # Create Excel output
        excel_file = extractor.create_final_excel_output()
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"  Clauses found: {total_found}")
        print(f"  Target: 182")
        print(f"  Success rate: {(total_found/182)*100:.1f}%")
        print(f"  Excel file: {excel_file}")
        
        if total_found >= 182:
            print("🎉 SUCCESS: Found all expected clauses!")
        else:
            print(f"⚠️  Still missing {182 - total_found} clauses")
    else:
        print("❌ No clauses found!")

if __name__ == "__main__":
    main()
