#!/usr/bin/env python3
"""
Fixed NADCAP Extractor - Decimal Point Logic
Simple approach: clause numbers = numbers with multiple decimal points + manual single decimals
"""

import pdfplumber
import json
import re
import sys
import os
import csv
from datetime import datetime

class FixedNADCAPExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.clauses = []
        
        # Known single decimal clause numbers (manual list)
        self.single_decimal_clauses = {
            "2.7": "Processes to be approved/Plant Layout",
            "2.8": "Company Information", 
            "3.1": "Documentation",
            "4.1": "Lot Testing",
            "4.2": "Periodic Testing"
        }
        
        # Section structure
        self.section_structure = {
            "2": "INSTRUCTIONS TO AUDITEE",
            "3": "GENERAL QUALITY SYSTEM", 
            "4": "TESTING",
            "5": "EQUIPMENT AND FACILITIES"
        }
    
    def extract_clause_number_from_line(self, line):
        """Extract clause number using decimal point logic."""
        # Primary pattern: Multiple decimal points (2+)
        multi_decimal_pattern = r'^(\d+\.\d+\.\d+(?:\.\d+)*)\s'
        match = re.match(multi_decimal_pattern, line.strip())
        if match:
            return match.group(1)
        
        # Secondary pattern: Known single decimal cases
        single_decimal_pattern = r'^(\d+\.\d+)\s'
        match = re.match(single_decimal_pattern, line.strip())
        if match:
            clause = match.group(1)
            if clause in self.single_decimal_clauses:
                return clause
        
        return None
    
    def get_section_from_clause(self, clause_number):
        """Get section info from clause number."""
        if not clause_number:
            return "Unknown", "Unknown"
        
        section_num = clause_number.split('.')[0]
        section_title = self.section_structure.get(section_num, "Unknown")
        return section_num, section_title
    
    def get_subsection_from_clause(self, clause_number):
        """Get subsection info from clause number.""" 
        if not clause_number:
            return "Unknown", "Unknown"
        
        # For single decimals, use the full number as subsection
        if clause_number.count('.') == 1:
            subsection_title = self.single_decimal_clauses.get(clause_number, f"Subsection {clause_number}")
            return clause_number, subsection_title
        
        # For multiple decimals, use first two levels as subsection
        parts = clause_number.split('.')
        if len(parts) >= 2:
            subsection_num = f"{parts[0]}.{parts[1]}"
            
            # Common subsection titles
            subsection_titles = {
                "3.5": "Training, Qualification, and Evaluation",
                "3.6": "Job Documentation", 
                "3.7": "Process and Quality Planning",
                "3.8": "Purchasing-Source Selection",
                "3.9": "Receiving Procedure",
                "3.10": "Housekeeping",
                "3.11": "Control of Non-Conforming Parts",
                "3.12": "Product Packaging & Delivery",
                "3.13": "Calibration and Verification"
            }
            
            subsection_title = subsection_titles.get(subsection_num, f"Subsection {subsection_num}")
            return subsection_num, subsection_title
        
        return "Unknown", "Unknown"
    
    def extract_all_questions(self):
        """Extract all Yes/No questions with proper clause detection."""
        print("🔍 Extracting questions with decimal point clause logic...")
        
        questions = []
        
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
                    
                    has_yes_no = False
                    has_na = False
                    
                    for pattern in yes_no_patterns:
                        if re.search(pattern, line_upper):
                            has_yes_no = True
                            has_na = 'NA' in line_upper
                            break
                    
                    if has_yes_no:
                        # Extract question text (remove YES NO markers)
                        question_text = line
                        for marker in ['YES NO NA', 'YES NO', '_YES _NO _NA', '_YES _NO']:
                            question_text = question_text.replace(marker, '').strip()
                        
                        if len(question_text) > 10:  # Must have substantial content
                            # Try to extract clause number from this line or nearby lines
                            clause_number = self.find_clause_number_nearby(lines, line_num)
                            
                            # Get section and subsection info
                            section_num, section_title = self.get_section_from_clause(clause_number)
                            subsection_num, subsection_title = self.get_subsection_from_clause(clause_number)
                            
                            # Create question entry
                            question_data = {
                                'page': page_num,
                                'section': section_num,
                                'section_title': section_title,
                                'subsection': subsection_num, 
                                'subsection_title': subsection_title,
                                'clause': clause_number or f"Q{len(questions)+1:03d}",
                                'content': question_text,
                                'guidance': "",
                                'notes': "",
                                'yes': 'Yes',
                                'no': 'No',
                                'na': 'NA' if has_na else ''
                            }
                            
                            questions.append(question_data)
                            
                            if clause_number:
                                print(f"  ✅ Page {page_num}: Found {clause_number} → Section {section_num}")
                            else:
                                print(f"  ⚠️  Page {page_num}: Question without clause number")
        
        return questions
    
    def find_clause_number_nearby(self, lines, line_num):
        """Find clause number in nearby lines using decimal logic."""
        # Check current line first
        clause = self.extract_clause_number_from_line(lines[line_num])
        if clause:
            return clause
        
        # Check previous lines (up to 10 lines back)
        for i in range(max(0, line_num - 10), line_num):
            clause = self.extract_clause_number_from_line(lines[i])
            if clause:
                return clause
        
        # Check next few lines
        for i in range(line_num + 1, min(len(lines), line_num + 5)):
            clause = self.extract_clause_number_from_line(lines[i])
            if clause:
                return clause
        
        return None
    
    def extract_guidance_and_notes(self, questions):
        """Extract guidance and notes for each question."""
        print("📝 Extracting guidance and notes...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for question in questions:
                page_num = question['page']
                page = pdf.pages[page_num - 1]
                page_text = page.extract_text()
                
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                
                # Find the line containing this question
                content_line_index = -1
                for i, line in enumerate(lines):
                    if question['content'][:30].lower() in line.lower():
                        content_line_index = i
                        break
                
                if content_line_index >= 0:
                    # Look for guidance and notes in subsequent lines
                    guidance = ""
                    notes = ""
                    
                    for i in range(content_line_index + 1, min(len(lines), content_line_index + 5)):
                        line = lines[i].strip()
                        line_lower = line.lower()
                        
                        if 'guidance:' in line_lower:
                            guidance = line
                        elif 'note:' in line_lower or 'notes:' in line_lower:
                            notes = line
                        elif line and not any(pattern in line_lower for pattern in ['yes no', 'na']):
                            continue
                        else:
                            break
                    
                    question['guidance'] = guidance
                    question['notes'] = notes
        
        return questions
    
    def run_extraction(self):
        """Run the complete extraction with decimal point logic."""
        print("🚀 Starting Fixed NADCAP Extraction - Decimal Point Logic")
        print("=" * 60)
        
        # Extract all questions
        questions = self.extract_all_questions()
        
        # Extract guidance and notes
        self.clauses = self.extract_guidance_and_notes(questions)
        
        print(f"\n🎯 EXTRACTION COMPLETE!")
        print(f"📊 Total questions: {len(self.clauses)}")
        
        # Statistics
        clauses_with_real_numbers = sum(1 for c in self.clauses if not c['clause'].startswith('Q'))
        
        print(f"🔢 Questions with real clause numbers: {clauses_with_real_numbers}/{len(self.clauses)} ({clauses_with_real_numbers/len(self.clauses)*100:.1f}%)")
        
        # Show clause number examples
        print("\n📋 CLAUSE NUMBER EXAMPLES:")
        real_clauses = [c for c in self.clauses if not c['clause'].startswith('Q')][:10]
        for clause_data in real_clauses:
            print(f"  {clause_data['clause']} (Page {clause_data['page']}) → Section {clause_data['section']}")
        
        return self.clauses
    
    def save_results(self):
        """Save results to CSV and Excel."""
        if not self.clauses:
            print("No clauses to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        
        # Save CSV
        csv_filename = f"../outputs/{base_name}_FIXED_DECIMAL_EXTRACTION_{timestamp}.csv"
        
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
            excel_filename = f"../outputs/{base_name}_FIXED_DECIMAL_EXTRACTION_{timestamp}.xlsx"
            
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
        print("Usage: python fixed_nadcap_extractor.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file not found: {pdf_file}")
        sys.exit(1)
    
    # Initialize extractor
    extractor = FixedNADCAPExtractor(pdf_file)
    
    # Run extraction
    clauses = extractor.run_extraction()
    
    # Save results
    extractor.save_results()
    
    print(f"\n✅ Fixed Decimal Point Extraction Complete!")

if __name__ == "__main__":
    main()
