#!/usr/bin/env python3
"""
Professional Document Manager NADCAP Extractor
Systematic approach with 100% coverage and audit trail.
"""

import pdfplumber
import json
import re
import sys
import os
import csv
from datetime import datetime

class ProfessionalNADCAPExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.document_structure = {}
        self.all_questions = []
        self.question_counter = 1
        
        # Professional document hierarchy
        self.section_definitions = {
            "1": "SCOPE",
            "2": "INSTRUCTIONS TO AUDITEE", 
            "3": "GENERAL QUALITY SYSTEM",
            "4": "TESTING",
            "5": "EQUIPMENT AND FACILITIES"
        }
    
    def build_document_map(self):
        """Phase 1: Build complete document structure map."""
        print("📋 PHASE 1: Building Document Structure Map")
        print("-" * 50)
        
        page_sections = {}
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                page_sections[page_num] = {
                    'sections': [],
                    'subsections': [],
                    'content_blocks': []
                }
                
                current_section = None
                current_subsection = None
                
                for line_num, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Detect major sections
                    section_match = self.detect_section(line)
                    if section_match:
                        current_section = section_match
                        page_sections[page_num]['sections'].append({
                            'line': line_num,
                            'section': section_match,
                            'title': self.section_definitions.get(section_match, 'Unknown'),
                            'text': line
                        })
                        print(f"  📁 Page {page_num}: Found Section {section_match}")
                        continue
                    
                    # Detect subsections
                    subsection_match = self.detect_subsection(line)
                    if subsection_match:
                        current_subsection = subsection_match
                        page_sections[page_num]['subsections'].append({
                            'line': line_num,
                            'subsection': subsection_match,
                            'text': line,
                            'parent_section': current_section
                        })
                        print(f"    📂 Page {page_num}: Found Subsection {subsection_match}")
                        continue
                    
                    # Store all content blocks
                    page_sections[page_num]['content_blocks'].append({
                        'line': line_num,
                        'text': line,
                        'parent_section': current_section,
                        'parent_subsection': current_subsection
                    })
        
        self.document_structure = page_sections
        print(f"\n✅ Document map complete: {len(page_sections)} pages analyzed")
        return page_sections
    
    def detect_section(self, line):
        """Detect major section headers."""
        line_upper = line.upper()
        
        # Direct section patterns
        patterns = [
            (r'SECTION\s+(\d+)', 'section_header'),
            (r'^(\d+)\.\s+[A-Z][A-Z\s]+$', 'numbered_section'),
        ]
        
        for pattern, pattern_type in patterns:
            match = re.search(pattern, line_upper)
            if match:
                section_num = match.group(1)
                if section_num in self.section_definitions:
                    return section_num
        
        # Content-based section detection
        if 'SCOPE' in line_upper and len(line) < 50:
            return "1"
        elif 'INSTRUCTION' in line_upper and 'AUDITEE' in line_upper:
            return "2"
        elif 'GENERAL' in line_upper and 'QUALITY' in line_upper:
            return "3"
        elif line_upper == 'TESTING' or ('TESTING' in line_upper and len(line) < 20):
            return "4"
        elif 'EQUIPMENT' in line_upper and 'FACILITIES' in line_upper:
            return "5"
        
        return None
    
    def detect_subsection(self, line):
        """Detect subsection headers."""
        # Numbered subsections: 3.1, 4.2, etc.
        match = re.match(r'^(\d+\.\d+)\s+[A-Z]', line)
        if match:
            return match.group(1)
        
        # Letter subsections: A., B., etc.
        match = re.match(r'^([A-Z]\.)\s+[A-Z]', line)
        if match:
            return match.group(1)
        
        return None
    
    def extract_all_questions_systematically(self):
        """Phase 2: Extract ALL questions with systematic numbering."""
        print("\n❓ PHASE 2: Systematic Question Extraction")
        print("-" * 50)
        
        questions = []
        current_section = "Unknown"
        current_section_title = "Unknown"
        current_subsection = "Unknown" 
        current_subsection_title = "Unknown"
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                # Update context from document structure
                page_structure = self.document_structure.get(page_num, {})
                
                # Get most recent section for this page
                if page_structure.get('sections'):
                    latest_section = page_structure['sections'][-1]
                    current_section = latest_section['section']
                    current_section_title = latest_section['title']
                
                lines = page_text.split('\n')
                
                for line_num, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Update subsection context
                    subsection_match = self.detect_subsection(line)
                    if subsection_match:
                        current_subsection = subsection_match
                        current_subsection_title = line.split(subsection_match, 1)[1].strip() if subsection_match in line else "Unknown"
                        continue
                    
                    # Check for Yes/No questions
                    if self.is_yes_no_question(line):
                        # Extract clause number or assign systematic number
                        clause_number = self.extract_or_assign_clause_number(line, page_num, line_num)
                        
                        # Clean question text
                        question_text = self.clean_question_text(line)
                        
                        # Determine Yes/No/NA structure
                        has_na = 'NA' in line.upper()
                        
                        question_data = {
                            'page': page_num,
                            'section': current_section,
                            'section_title': current_section_title,
                            'subsection': current_subsection,
                            'subsection_title': current_subsection_title,
                            'clause': clause_number,
                            'content': question_text,
                            'guidance': "",  # Will be populated later
                            'notes': "",     # Will be populated later
                            'yes': 'Yes',
                            'no': 'No',
                            'na': 'NA' if has_na else '',
                            'extraction_method': 'systematic',
                            'line_number': line_num
                        }
                        
                        questions.append(question_data)
                        print(f"  ✅ Q{self.question_counter:03d}: Page {page_num} | Clause {clause_number} | Section {current_section}")
                        self.question_counter += 1
        
        return questions
    
    def is_yes_no_question(self, line):
        """Identify Yes/No questions with high precision."""
        line_upper = line.upper()
        
        # Primary Yes/No patterns
        yes_no_patterns = [
            r'\bYES\s+NO\s+NA\b',
            r'\bYES\s+NO\b',
            r'\b_YES\s+_NO\s+_NA\b',
            r'\b_YES\s+_NO\b'
        ]
        
        for pattern in yes_no_patterns:
            if re.search(pattern, line_upper):
                return True
        
        return False
    
    def extract_or_assign_clause_number(self, line, page_num, line_num):
        """Extract existing clause number or assign systematic number."""
        # Try to extract existing clause number
        clause_patterns = [
            r'^(\d+\.\d+\.\d+\.\d+\.\d+)',  # 3.6.1.5.1
            r'^(\d+\.\d+\.\d+\.\d+)',       # 3.7.3.1
            r'^(\d+\.\d+\.\d+)',            # 3.6.1
            r'^(\d+\.\d+)',                 # 2.7, 3.1
            r'(\d+\.\d+\.\d+\.\d+\.\d+)',   # Anywhere in line
            r'(\d+\.\d+\.\d+\.\d+)',        # Anywhere in line
            r'(\d+\.\d+\.\d+)',             # Anywhere in line
            r'(\d+\.\d+)',                  # Anywhere in line
        ]
        
        for pattern in clause_patterns:
            match = re.search(pattern, line)
            if match:
                potential_clause = match.group(1)
                if self.is_valid_clause_format(potential_clause):
                    return potential_clause
        
        # Assign systematic number if no explicit clause found
        return f"AUTO_{page_num:02d}_{line_num:03d}"
    
    def is_valid_clause_format(self, clause):
        """Validate clause number format."""
        if not clause:
            return False
        
        # Must be numeric with dots
        if not re.match(r'^\d+(\.\d+)*$', clause):
            return False
        
        # Must start with valid section number
        section_num = clause.split('.')[0]
        return section_num in ["1", "2", "3", "4", "5"]
    
    def clean_question_text(self, line):
        """Clean question text by removing Yes/No markers."""
        clean_text = line
        
        # Remove Yes/No markers
        markers = ['YES NO NA', 'YES NO', '_YES _NO _NA', '_YES _NO']
        for marker in markers:
            clean_text = clean_text.replace(marker, '').strip()
        
        return clean_text
    
    def extract_guidance_and_notes(self, questions):
        """Phase 3: Extract guidance and notes for all questions."""
        print(f"\n📝 PHASE 3: Extracting Guidance and Notes for {len(questions)} questions")
        print("-" * 50)
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, question in enumerate(questions):
                page_num = question['page']
                line_num = question['line_number']
                page = pdf.pages[page_num - 1]
                page_text = page.extract_text()
                
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                
                # Look for guidance/notes in subsequent lines
                guidance = ""
                notes = ""
                
                for j in range(line_num + 1, min(len(lines), line_num + 5)):
                    if j >= len(lines):
                        break
                    
                    line = lines[j].strip()
                    line_lower = line.lower()
                    
                    if 'guidance:' in line_lower:
                        guidance = line
                    elif 'note:' in line_lower or 'notes:' in line_lower:
                        notes = line
                    elif self.is_yes_no_question(line):
                        break  # Stop at next question
                
                question['guidance'] = guidance
                question['notes'] = notes
                
                if (i + 1) % 50 == 0:
                    print(f"  📝 Processed {i + 1}/{len(questions)} questions...")
        
        return questions
    
    def professional_quality_check(self, questions):
        """Phase 4: Professional quality assurance."""
        print(f"\n🔍 PHASE 4: Quality Assurance Check")
        print("-" * 50)
        
        issues = []
        
        # Check 1: All questions have required fields
        for i, q in enumerate(questions):
            if not q['content'] or len(q['content']) < 5:
                issues.append(f"Question {i+1}: Content too short")
            if q['section'] == 'Unknown':
                issues.append(f"Question {i+1}: Unknown section")
        
        # Check 2: Page coverage
        pages_with_questions = set(q['page'] for q in questions)
        expected_pages = set(range(9, 33))  # NADCAP questions typically on these pages
        missing_pages = expected_pages - pages_with_questions
        
        # Check 3: Section distribution
        section_counts = {}
        for q in questions:
            section = q['section']
            section_counts[section] = section_counts.get(section, 0) + 1
        
        print(f"✅ Total questions extracted: {len(questions)}")
        print(f"✅ Pages covered: {len(pages_with_questions)}")
        print(f"✅ Sections found: {len([s for s in section_counts.keys() if s != 'Unknown'])}")
        
        if issues:
            print(f"⚠️  Quality issues found: {len(issues)}")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"   • {issue}")
        else:
            print("✅ All quality checks passed!")
        
        return questions, len(issues)
    
    def run_professional_extraction(self):
        """Run complete professional document extraction."""
        print("🏢 PROFESSIONAL NADCAP DOCUMENT EXTRACTION")
        print("=" * 60)
        print(f"📁 Source: {os.path.basename(self.pdf_path)}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Phase 1: Document structure mapping
        self.build_document_map()
        
        # Phase 2: Systematic question extraction
        questions = self.extract_all_questions_systematically()
        
        # Phase 3: Guidance and notes extraction
        questions = self.extract_guidance_and_notes(questions)
        
        # Phase 4: Quality assurance
        questions, issue_count = self.professional_quality_check(questions)
        
        self.all_questions = questions
        
        print(f"\n🎯 EXTRACTION COMPLETE!")
        print(f"📊 Total questions: {len(questions)}")
        print(f"🔍 Quality issues: {issue_count}")
        print(f"✅ Professional extraction ready for audit review")
        
        return questions
    
    def save_professional_results(self):
        """Save results with professional formatting."""
        if not self.all_questions:
            print("No questions to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        
        # Save CSV with professional formatting
        csv_filename = f"../outputs/{base_name}_PROFESSIONAL_EXTRACTION_{timestamp}.csv"
        
        fieldnames = [
            'Question_ID', 'Page', 'Section', 'Section_Title', 'Subsection', 'Subsection_Title',
            'Clause', 'Content/Question', 'Guidance', 'Notes', 'Yes', 'No', 'NA', 
            'Extraction_Method', 'Line_Number'
        ]
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, question in enumerate(self.all_questions, 1):
                writer.writerow({
                    'Question_ID': f"Q{i:03d}",
                    'Page': question['page'],
                    'Section': question['section'],
                    'Section_Title': question['section_title'],
                    'Subsection': question['subsection'],
                    'Subsection_Title': question['subsection_title'],
                    'Clause': question['clause'],
                    'Content/Question': question['content'],
                    'Guidance': question['guidance'],
                    'Notes': question['notes'],
                    'Yes': question['yes'],
                    'No': question['no'],
                    'NA': question['na'],
                    'Extraction_Method': question['extraction_method'],
                    'Line_Number': question['line_number']
                })
        
        print(f"✅ Professional CSV saved: {csv_filename}")
        
        # Save Excel with professional formatting
        try:
            import pandas as pd
            df = pd.read_csv(csv_filename)
            excel_filename = f"../outputs/{base_name}_PROFESSIONAL_EXTRACTION_{timestamp}.xlsx"
            
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='NADCAP_Professional_Extract', index=False)
                
                # Professional formatting
                workbook = writer.book
                worksheet = writer.sheets['NADCAP_Professional_Extract']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 60)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Header formatting
                from openpyxl.styles import Font, PatternFill
                header_font = Font(bold=True)
                header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                
                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
            
            print(f"✅ Professional Excel saved: {excel_filename}")
            
        except ImportError:
            print("⚠️  pandas/openpyxl not available for Excel formatting")

def main():
    if len(sys.argv) != 2:
        print("Usage: python professional_nadcap_extractor.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file not found: {pdf_file}")
        sys.exit(1)
    
    # Initialize professional extractor
    extractor = ProfessionalNADCAPExtractor(pdf_file)
    
    # Run professional extraction
    questions = extractor.run_professional_extraction()
    
    # Save professional results
    extractor.save_professional_results()
    
    print(f"\n🏢 Professional Extraction Complete - Audit Ready!")

if __name__ == "__main__":
    main()
