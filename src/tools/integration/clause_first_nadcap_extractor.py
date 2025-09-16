#!/usr/bin/env python3
"""
Clause-First NADCAP Extractor - Logical Approach
Start with clause numbers as triggers, then populate context.
"""

import pdfplumber
import json
import re
import sys
import os
import csv
from datetime import datetime

class ClauseFirstNADCAPExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.clauses = []
        self.page_context = {}  # Store context for each page
        
    def analyze_pdf_structure(self):
        """First pass: Analyze the actual PDF structure."""
        print("🔍 PHASE 1: Analyzing PDF structure...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                
                # Find sections on this page
                sections = []
                subsections = []
                
                for line in lines:
                    line = line.strip()
                    
                    # Section detection patterns
                    section_patterns = [
                        r'^(SECTION\s+\d+)\s*[-–—]\s*(.+)$',  # SECTION 3 - GENERAL QUALITY SYSTEM
                        r'^(\d+\.\s*[A-Z][A-Z\s]+)$',        # 3. GENERAL QUALITY SYSTEM
                        r'^([A-Z\s]+)$'                       # GENERAL QUALITY SYSTEM (if all caps)
                    ]
                    
                    for pattern in section_patterns:
                        match = re.match(pattern, line.upper())
                        if match and len(line) > 10 and 'SECTION' in line.upper():
                            sections.append(line)
                            break
                    
                    # Subsection detection
                    subsection_patterns = [
                        r'^(\d+\.\d+)\s+(.+)$',  # 3.1 Documentation
                        r'^([A-Z]\.\s*.+)$'      # A. Test Records
                    ]
                    
                    for pattern in subsection_patterns:
                        match = re.match(pattern, line)
                        if match and len(line) > 5:
                            subsections.append(line)
                            break
                
                self.page_context[page_num] = {
                    'sections': sections,
                    'subsections': subsections,
                    'text': page_text
                }
                
                if sections or subsections:
                    print(f"  Page {page_num}: {len(sections)} sections, {len(subsections)} subsections")
                    for section in sections:
                        print(f"    Section: {section}")
                    for subsection in subsections[:3]:  # Show first 3
                        print(f"    Subsection: {subsection}")
    
    def find_all_clause_numbers(self):
        """PHASE 2: Find all actual clause numbers in the document."""
        print("\n🎯 PHASE 2: Finding all clause numbers...")
        
        clause_locations = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                
                for line_num, line in enumerate(lines):
                    line = line.strip()
                    
                    # Comprehensive clause number patterns
                    clause_patterns = [
                        # Multi-level hierarchical patterns
                        r'^(\d+\.\d+\.\d+\.\d+\.\d+)\s',     # 3.6.1.5.1
                        r'^(\d+\.\d+\.\d+\.\d+)\s',          # 3.7.3.1
                        r'^(\d+\.\d+\.\d+)\s',               # 3.6.1
                        r'^(\d+\.\d+)\s',                    # 2.7, 3.1
                        
                        # Letter-based patterns
                        r'^([a-z]\))\s',                     # a), b), c)
                        r'^([A-Z]\))\s',                     # A), B), C)
                        r'^\(([a-z])\)\s',                   # (a), (b), (c)
                        r'^\(([A-Z])\)\s',                   # (A), (B), (C)
                        
                        # Mixed patterns
                        r'^([A-Z]\.\d+)\s',                  # A.1, B.2
                        r'^([A-Z]\.)\s',                     # A., B.
                        
                        # Roman numerals
                        r'^([ivxlc]+)\)\s',                  # i), ii), iii)
                        r'^([IVXLC]+)\)\s',                  # I), II), III)
                    ]
                    
                    for pattern in clause_patterns:
                        match = re.match(pattern, line)
                        if match:
                            clause_num = match.group(1)
                            
                            # Validate it's actually a clause (has content after)
                            remaining_text = line[match.end():].strip()
                            if len(remaining_text) > 10:  # Must have substantial content
                                clause_locations.append({
                                    'page': page_num,
                                    'line_num': line_num,
                                    'clause_number': clause_num,
                                    'full_line': line,
                                    'content_start': remaining_text[:100] + '...' if len(remaining_text) > 100 else remaining_text
                                })
                                print(f"  Found clause {clause_num} on page {page_num}: {remaining_text[:50]}...")
                                break
        
        print(f"\n✅ Found {len(clause_locations)} potential clauses")
        return clause_locations
    
    def extract_yes_no_questions(self):
        """PHASE 3: Find all Yes/No questions regardless of clause numbers."""
        print("\n❓ PHASE 3: Finding all Yes/No questions...")
        
        yes_no_questions = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                
                for line_num, line in enumerate(lines):
                    line = line.strip()
                    line_upper = line.upper()
                    
                    # Yes/No pattern detection
                    yes_no_patterns = [
                        r'\bYES\s+NO\s+NA\b',
                        r'\bYES\s+NO\b',
                        r'\b_YES\s+_NO\s+_NA\b',
                        r'\b_YES\s+_NO\b'
                    ]
                    
                    for pattern in yes_no_patterns:
                        if re.search(pattern, line_upper):
                            # This line contains a Yes/No question
                            question_text = re.sub(r'\s*(YES|NO|NA|_YES|_NO|_NA)\s*', '', line_upper).strip()
                            question_text = line.replace('YES NO NA', '').replace('YES NO', '').replace('_YES _NO _NA', '').replace('_YES _NO', '').strip()
                            
                            if len(question_text) > 10:  # Must have substantial question content
                                has_na = 'NA' in line_upper
                                
                                yes_no_questions.append({
                                    'page': page_num,
                                    'line_num': line_num,
                                    'question': question_text,
                                    'has_na': has_na,
                                    'full_line': line
                                })
                                print(f"  Found question on page {page_num}: {question_text[:50]}...")
                            break
        
        print(f"\n✅ Found {len(yes_no_questions)} Yes/No questions")
        return yes_no_questions
    
    def determine_context_for_page(self, page_num):
        """Determine section and subsection context for a given page."""
        # Look at current page and previous pages for context
        current_section = "Unknown"
        current_section_title = "Unknown"
        current_subsection = "Unknown"
        current_subsection_title = "Unknown"
        
        # Search backwards from current page to find most recent section/subsection
        for p in range(page_num, max(1, page_num - 5), -1):  # Check current and up to 4 previous pages
            if p in self.page_context:
                context = self.page_context[p]
                
                # Find most recent section
                if context['sections'] and current_section == "Unknown":
                    section_line = context['sections'][-1]  # Most recent section on this page
                    
                    # Parse section number and title
                    if 'SECTION' in section_line.upper():
                        match = re.search(r'SECTION\s+(\d+)\s*[-–—]\s*(.+)', section_line.upper())
                        if match:
                            current_section = match.group(1)
                            current_section_title = match.group(2).title()
                
                # Find most recent subsection
                if context['subsections'] and current_subsection == "Unknown":
                    subsection_line = context['subsections'][-1]  # Most recent subsection
                    
                    # Parse subsection
                    match = re.match(r'^(\d+\.\d+)\s+(.+)$', subsection_line)
                    if match:
                        current_subsection = match.group(1)
                        current_subsection_title = match.group(2)
                    else:
                        match = re.match(r'^([A-Z]\.\s*.+)$', subsection_line)
                        if match:
                            current_subsection = subsection_line.split('.')[0] + '.'
                            current_subsection_title = subsection_line.split('.', 1)[1].strip()
        
        return current_section, current_section_title, current_subsection, current_subsection_title
    
    def merge_clauses_and_questions(self, clause_locations, yes_no_questions):
        """PHASE 4: Intelligently merge clause numbers with Yes/No questions."""
        print("\n🔗 PHASE 4: Merging clauses with questions...")
        
        merged_clauses = []
        
        # Try to match each Yes/No question with nearby clause numbers
        for question in yes_no_questions:
            q_page = question['page']
            q_line = question['line_num']
            
            # Find the closest clause number (within reasonable distance)
            best_clause = None
            min_distance = float('inf')
            
            for clause in clause_locations:
                c_page = clause['page']
                c_line = clause['line_num']
                
                # Calculate distance (prefer same page, then nearby pages)
                if c_page == q_page:
                    distance = abs(c_line - q_line)
                elif abs(c_page - q_page) == 1:
                    distance = 100 + abs(c_line - q_line)  # Penalty for different page
                else:
                    distance = 1000 + abs(c_page - q_page) * 100  # Larger penalty
                
                # Prefer clause numbers that come before the question
                if c_page < q_page or (c_page == q_page and c_line <= q_line):
                    if distance < min_distance:
                        min_distance = distance
                        best_clause = clause
            
            # Determine context
            section, section_title, subsection, subsection_title = self.determine_context_for_page(q_page)
            
            # Create merged clause entry
            clause_number = best_clause['clause_number'] if best_clause and min_distance < 50 else ""
            
            merged_clause = {
                'page': q_page,
                'section': section,
                'section_title': section_title,
                'subsection': subsection,
                'subsection_title': subsection_title,
                'clause': clause_number,
                'content': question['question'],
                'guidance': "",  # Will be populated in next phase
                'notes': "",     # Will be populated in next phase
                'yes': 'Yes',
                'no': 'No',
                'na': 'NA' if question['has_na'] else ''
            }
            
            merged_clauses.append(merged_clause)
            
            if clause_number:
                print(f"  ✅ Matched clause {clause_number} with question on page {q_page}")
            else:
                print(f"  ⚠️  No clause number found for question on page {q_page}")
        
        print(f"\n✅ Created {len(merged_clauses)} merged clause entries")
        return merged_clauses
    
    def extract_guidance_and_notes(self, clauses):
        """PHASE 5: Extract guidance and notes for each clause."""
        print("\n📝 PHASE 5: Extracting guidance and notes...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for clause in clauses:
                page_num = clause['page']
                page = pdf.pages[page_num - 1]
                page_text = page.extract_text()
                
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                
                # Find the line containing this clause's content
                content_line_index = -1
                for i, line in enumerate(lines):
                    if clause['content'][:30] in line:  # Match first 30 chars
                        content_line_index = i
                        break
                
                if content_line_index >= 0:
                    # Look for guidance and notes in subsequent lines
                    guidance = ""
                    notes = ""
                    
                    for i in range(content_line_index + 1, min(len(lines), content_line_index + 10)):
                        line = lines[i].strip().lower()
                        
                        if 'guidance:' in line:
                            guidance = lines[i].strip()
                        elif 'note:' in line or 'notes:' in line:
                            notes = lines[i].strip()
                        elif line and not any(pattern in line for pattern in ['yes no', 'na']):
                            # Might be continuation of content
                            continue
                        else:
                            break  # Stop at next Yes/No pattern
                    
                    clause['guidance'] = guidance
                    clause['notes'] = notes
        
        return clauses
    
    def run_extraction(self):
        """Run the complete clause-first extraction process."""
        print("🚀 Starting Clause-First NADCAP Extraction")
        print("=" * 60)
        
        # Phase 1: Analyze PDF structure
        self.analyze_pdf_structure()
        
        # Phase 2: Find all clause numbers
        clause_locations = self.find_all_clause_numbers()
        
        # Phase 3: Find all Yes/No questions
        yes_no_questions = self.extract_yes_no_questions()
        
        # Phase 4: Merge clauses with questions
        merged_clauses = self.merge_clauses_and_questions(clause_locations, yes_no_questions)
        
        # Phase 5: Extract guidance and notes
        self.clauses = self.extract_guidance_and_notes(merged_clauses)
        
        print(f"\n🎯 EXTRACTION COMPLETE!")
        print(f"📊 Total clauses: {len(self.clauses)}")
        
        # Show statistics
        clauses_with_numbers = sum(1 for c in self.clauses if c['clause'])
        sections_found = len(set(c['section'] for c in self.clauses if c['section'] != 'Unknown'))
        
        print(f"🔢 Clauses with numbers: {clauses_with_numbers}/{len(self.clauses)} ({clauses_with_numbers/len(self.clauses)*100:.1f}%)")
        print(f"📑 Sections found: {sections_found}")
        
        return self.clauses
    
    def save_results(self):
        """Save results to CSV and Excel."""
        if not self.clauses:
            print("No clauses to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        
        # Save CSV
        csv_filename = f"../outputs/{base_name}_CLAUSE_FIRST_EXTRACTION_{timestamp}.csv"
        
        fieldnames = [
            'Page', 'Section', 'Section_Title', 'Subsection', 'Subsection_Title',
            'Clause', 'Content/Question', 'Guidance', 'Notes', 'Yes', 'No', 'NA'
        ]
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for clause in self.clauses:
                writer.writerow({
                    'Page': clause['page'],
                    'Section': clause['section'],
                    'Section_Title': clause['section_title'],
                    'Subsection': clause['subsection'],
                    'Subsection_Title': clause['subsection_title'],
                    'Clause': clause['clause'],
                    'Content/Question': clause['content'],
                    'Guidance': clause['guidance'],
                    'Notes': clause['notes'],
                    'Yes': clause['yes'],
                    'No': clause['no'],
                    'NA': clause['na']
                })
        
        print(f"✅ CSV saved: {csv_filename}")
        
        # Save Excel
        try:
            import pandas as pd
            df = pd.read_csv(csv_filename)
            excel_filename = f"../outputs/{base_name}_CLAUSE_FIRST_EXTRACTION_{timestamp}.xlsx"
            
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='NADCAP_Clauses', index=False)
                
                # Auto-adjust column widths
                workbook = writer.book
                worksheet = writer.sheets['NADCAP_Clauses']
                
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"✅ Excel saved: {excel_filename}")
            
        except ImportError:
            print("⚠️  pandas not available for Excel export")

def main():
    if len(sys.argv) != 2:
        print("Usage: python clause_first_nadcap_extractor.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file not found: {pdf_file}")
        sys.exit(1)
    
    # Initialize extractor
    extractor = ClauseFirstNADCAPExtractor(pdf_file)
    
    # Run extraction
    clauses = extractor.run_extraction()
    
    # Save results
    extractor.save_results()
    
    print(f"\n✅ Clause-First Extraction Complete!")

if __name__ == "__main__":
    main()
