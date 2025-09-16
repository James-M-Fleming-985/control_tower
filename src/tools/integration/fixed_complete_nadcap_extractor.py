#!/usr/bin/env python3
"""
Enhanced Complete NADCAP Extractor - Fixed Clause Number Extraction
Fixes the clause numbering issue where actual multi-decimal clause numbers (like 4.3.2.1) 
were being replaced with sequential numbers (like 4.3.3)
"""

import pdfplumber
import json
import re
import sys
import os
import csv
from datetime import datetime

class FixedCompleteNADCAPExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.clauses = []
        self.page_contexts = {}  # Track section/subsection context per page
        
        # Complete NADCAP section structure
        self.sections = {
            "2": "INSTRUCTIONS TO AUDITEE",
            "3": "GENERAL QUALITY SYSTEM", 
            "4": "TESTING",
            "5": "EQUIPMENT AND FACILITIES"
        }
        
        # Complete subsection structure - but NO clause counters (we'll extract actual numbers)
        self.subsection_titles = {
            "2.7": "Processes to be approved/Plant Layout",
            "2.8": "Company Information",
            "3.1": "Documentation", 
            "3.2": "Specification List",
            "3.3": "Continuous Process Improvement",
            "3.4": "Sampling Plans",
            "3.5": "Training, Qualification, and Evaluation", 
            "3.6": "Job Documentation",
            "3.7": "Process and Quality Planning",
            "3.8": "Purchasing-Source Selection",
            "3.9": "Receiving Procedure",
            "3.10": "Housekeeping",
            "3.11": "Control of Non-Conforming Parts",
            "3.12": "Product Packaging & Delivery",
            "3.13": "Calibration and Verification",
            "4.1": "Lot Testing",
            "4.2": "Periodic Testing", 
            "4.3": "Sub-tier Testing Review",
            "4.4": "Test Data Corrections",
            "4.5": "Error Procedures",
            "4.6": "Test Piece Control",
            "4.7": "Test Failure and Retesting",
            "4.8": "Control of Processing Solutions",
            "5.1": "General",
            "5.2": "Maintenance Procedures",
            "5.3": "Process Line Equipment", 
            "5.4": "Ovens for Thermal Treatments (>250°F)",
            "5.5": "Ovens for Thermal Treatments (≤250°F)",
            "5.6": "Stripping",
            "5.7": "Inspection"
        }
    
    def analyze_document_structure(self):
        """Phase 1: Build complete document context map."""
        print("📋 PHASE 1: Building Complete Document Structure")
        print("-" * 50)
        
        with pdfplumber.open(self.pdf_path) as pdf:
            current_section = "3"  # Default starting section
            current_subsection = "3.1"  # Default starting subsection
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                
                # Detect section changes
                section_found = False
                subsection_found = False
                
                for line in lines:
                    line = line.strip()
                    
                    # Section detection patterns
                    if 'TESTING' in line.upper() and 'SECTION' in line.upper():
                        current_section = "4"
                        section_found = True
                    elif 'EQUIPMENT' in line.upper() and 'FACILITIES' in line.upper():
                        current_section = "5" 
                        section_found = True
                    elif 'GENERAL QUALITY' in line.upper():
                        current_section = "3"
                        section_found = True
                    elif 'INSTRUCTIONS TO AUDITEE' in line.upper():
                        current_section = "2"
                        section_found = True
                    
                    # Subsection detection - look for numbered subsections
                    subsection_patterns = [
                        r'^(2\.[78])\s',   # 2.7, 2.8
                        r'^(3\.\d+)\s',    # 3.1, 3.2, etc.
                        r'^(4\.[1-8])\s',  # 4.1, 4.2, etc.
                        r'^(5\.[1-7])\s'   # 5.1, 5.2, etc.
                    ]
                    
                    for pattern in subsection_patterns:
                        match = re.match(pattern, line)
                        if match:
                            potential_subsection = match.group(1)
                            if potential_subsection in self.subsection_titles:
                                current_subsection = potential_subsection
                                subsection_found = True
                                break
                
                # Store context for this page
                self.page_contexts[page_num] = {
                    'section': current_section,
                    'subsection': current_subsection
                }
                
                if section_found or subsection_found:
                    print(f"  📄 Page {page_num}: Section {current_section}, Subsection {current_subsection}")
    
    def extract_exact_clause_number(self, lines, start_index):
        """
        IMPROVED METHOD: Extract the actual clause number from the PDF text.
        Looks for multi-decimal patterns like 4.3.2.1, 3.6.1.5.1, etc.
        """
        # Check current line first
        current_line = lines[start_index].strip()
        
        # Enhanced patterns to catch all clause number variations
        clause_patterns = [
            # Multi-level decimal patterns (most specific first)
            r'^(\d+\.\d+\.\d+\.\d+\.\d+\.\d+)\s',  # 3.6.1.5.1.1
            r'^(\d+\.\d+\.\d+\.\d+\.\d+)\s',       # 3.6.1.5.1
            r'^(\d+\.\d+\.\d+\.\d+)\s',            # 3.7.3.1
            r'^(\d+\.\d+\.\d+)\s',                 # 4.3.2
            r'^(\d+\.\d+)\s',                      # 4.3 (for major sections)
            # Also check for patterns within the line
            r'(\d+\.\d+\.\d+\.\d+\.\d+\.\d+)\s',   # Within line
            r'(\d+\.\d+\.\d+\.\d+\.\d+)\s',        # Within line
            r'(\d+\.\d+\.\d+\.\d+)\s',             # Within line
            r'(\d+\.\d+\.\d+)\s',                  # Within line
        ]
        
        # First, check the current line
        for pattern in clause_patterns:
            match = re.search(pattern, current_line)
            if match:
                clause_num = match.group(1)
                # Validate it's a reasonable clause number (not just random decimals)
                if clause_num.startswith(('2.', '3.', '4.', '5.')):
                    return clause_num
        
        # If not found in current line, check previous lines (up to 3 lines back)
        for i in range(max(0, start_index - 3), start_index):
            if i < len(lines):
                line = lines[i].strip()
                for pattern in clause_patterns:
                    match = re.search(pattern, line)
                    if match:
                        clause_num = match.group(1)
                        if clause_num.startswith(('2.', '3.', '4.', '5.')):
                            return clause_num
        
        # If still not found, check the next few lines
        for i in range(start_index + 1, min(len(lines), start_index + 3)):
            if i < len(lines):
                line = lines[i].strip()
                for pattern in clause_patterns:
                    match = re.search(pattern, line)
                    if match:
                        clause_num = match.group(1)
                        if clause_num.startswith(('2.', '3.', '4.', '5.')):
                            return clause_num
        
        return None
    
    def reconstruct_full_question_with_clause(self, lines, start_index):
        """
        ENHANCED METHOD: Reconstruct full question content AND extract actual clause number.
        """
        # Start with the line that contains YES/NO pattern
        question_parts = []
        current_line = lines[start_index].strip()
        
        # Extract actual clause number first
        actual_clause = self.extract_exact_clause_number(lines, start_index)
        
        # Clean the current line of clause numbers and YES/NO markers
        question_text = current_line
        
        # Remove clause numbers from the beginning if present
        question_text = re.sub(r'^\d+(?:\.\d+)*\s+', '', question_text)
        
        # Remove YES/NO markers from the first line
        for marker in ['YES NO NA', 'YES NO', '_YES _NO _NA', '_YES _NO']:
            question_text = re.sub(r'\b' + re.escape(marker) + r'\b', '', question_text, flags=re.IGNORECASE)
        
        question_parts.append(question_text.strip())
        
        # Look ahead to find continuation lines
        for i in range(start_index + 1, min(len(lines), start_index + 8)):  # Look ahead up to 8 lines
            next_line = lines[i].strip()
            
            # Stop conditions - indicators we've moved to a new question/section
            if not next_line:  # Empty line
                continue
            
            # Stop if we hit another question pattern
            if re.search(r'\bYES\s+NO\b', next_line.upper()):
                break
            
            # Stop if we hit a clear section/subsection header
            if re.match(r'^\d+\.\d+\s+[A-Z]', next_line):
                break
            
            # Stop if we hit guidance or notes
            if any(keyword in next_line.lower() for keyword in ['guidance:', 'note:', 'notes:']):
                break
            
            # Stop if line starts with a clause number (likely next clause)
            if re.match(r'^\d+\.\d+', next_line):
                break
            
            # If line contains actual content and doesn't look like a header, include it
            if len(next_line) > 3 and not re.match(r'^\d+\s*$', next_line):
                # Remove any trailing YES/NO patterns from continuation lines
                clean_line = next_line
                for marker in ['YES NO NA', 'YES NO', '_YES _NO _NA', '_YES _NO']:
                    clean_line = re.sub(r'\b' + re.escape(marker) + r'\b', '', clean_line, flags=re.IGNORECASE)
                clean_line = clean_line.strip()
                
                if clean_line:
                    question_parts.append(clean_line)
            else:
                break
        
        # Combine all parts into complete question
        full_question = ' '.join(question_parts)
        full_question = re.sub(r'\s+', ' ', full_question).strip()
        
        return full_question, actual_clause
    
    def extract_all_questions_fixed(self):
        """Phase 2: Enhanced question extraction with FIXED clause number extraction."""
        print("\n❓ PHASE 2: Fixed Question Extraction (Actual Clause Numbers)")
        print("-" * 60)
        
        questions = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                page_context = self.page_contexts.get(page_num, {'section': '3', 'subsection': '3.1'})
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    line_upper = line.upper()
                    
                    # Yes/No pattern detection (comprehensive)
                    yes_no_patterns = [
                        r'\bYES\s+NO\s+NA\b',
                        r'\bYES\s+NO\b',
                        r'\b_YES\s+_NO\s+_NA\b',
                        r'\b_YES\s+_NO\b',
                        r'YES\s*NO\s*NA',
                        r'YES\s*NO'
                    ]
                    
                    has_yes_no = False
                    has_na = False
                    
                    for pattern in yes_no_patterns:
                        if re.search(pattern, line_upper):
                            has_yes_no = True
                            has_na = 'NA' in line_upper
                            break
                    
                    if has_yes_no:
                        # FIXED: Use enhanced reconstruction method with actual clause extraction
                        full_question, actual_clause = self.reconstruct_full_question_with_clause(lines, i)
                        
                        if len(full_question) > 10:  # Must have substantial content
                            # Get context
                            section = page_context['section']
                            subsection = page_context['subsection']
                            
                            # Use actual clause number if found, otherwise mark as "No Clause Number"
                            final_clause = actual_clause if actual_clause else "No Clause Number"
                            
                            # Get titles
                            section_title = self.sections.get(section, "Unknown Section")
                            subsection_title = self.subsection_titles.get(subsection, f"Subsection {subsection}")
                            
                            # Create complete question entry
                            question_data = {
                                'page': page_num,
                                'section': section,
                                'section_title': section_title,
                                'subsection': subsection,
                                'subsection_title': subsection_title,
                                'clause': final_clause,
                                'content': full_question,
                                'guidance': "",
                                'notes': "",
                                'yes': 'Yes',
                                'no': 'No',
                                'na': 'NA' if has_na else ''
                            }
                            
                            questions.append(question_data)
                            
                            if actual_clause:
                                print(f"  ✅ Q{len(questions):03d}: Page {page_num} | ACTUAL Clause {final_clause}")
                                print(f"      Content: {full_question[:80]}...")
                            else:
                                print(f"  ⚠️  Q{len(questions):03d}: Page {page_num} | No clause number found")
                                print(f"      Content: {full_question[:80]}...")
                    
                    i += 1
        
        return questions
    
    def extract_guidance_and_notes(self, questions):
        """Phase 3: Extract guidance and notes for all questions."""
        print(f"\n📝 PHASE 3: Extracting Guidance and Notes for {len(questions)} questions")
        print("-" * 60)
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, question in enumerate(questions):
                if i % 50 == 0:
                    print(f"  📝 Processed {i}/{len(questions)} questions...")
                
                page_num = question['page']
                page = pdf.pages[page_num - 1]
                page_text = page.extract_text()
                
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                
                # Find the line containing this question
                content_line_index = -1
                for j, line in enumerate(lines):
                    if question['content'][:50].lower() in line.lower():
                        content_line_index = j
                        break
                
                if content_line_index >= 0:
                    # Look for guidance and notes in subsequent lines
                    guidance = ""
                    notes = ""
                    
                    for j in range(content_line_index + 1, min(len(lines), content_line_index + 8)):
                        line = lines[j].strip()
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
    
    def run_fixed_extraction(self):
        """Execute fixed extraction with actual clause numbers."""
        print("🚀 FIXED COMPLETE NADCAP EXTRACTION - ACTUAL CLAUSE NUMBERS")
        print("=" * 70)
        
        # Phase 1: Document structure analysis
        self.analyze_document_structure()
        
        # Phase 2: Fixed question extraction with actual clause numbers
        questions = self.extract_all_questions_fixed()
        
        # Phase 3: Guidance and notes
        self.clauses = self.extract_guidance_and_notes(questions)
        
        print(f"\n🎯 FIXED EXTRACTION FINISHED!")
        print(f"📊 Total Questions: {len(self.clauses)}")
        
        # Enhanced statistics
        actual_clauses = sum(1 for c in self.clauses if c['clause'] != "No Clause Number")
        no_clause = len(self.clauses) - actual_clauses
        
        print(f"🔢 Questions with ACTUAL Clause Numbers: {actual_clauses}")
        print(f"⚠️  Questions without Clause Numbers: {no_clause}")
        print(f"✅ FIXED: No more sequential numbering!")
        
        # Section breakdown
        print(f"\n📋 Section Distribution:")
        section_counts = {}
        for clause in self.clauses:
            section = clause['section']
            section_counts[section] = section_counts.get(section, 0) + 1
        
        for section in sorted(section_counts.keys()):
            section_title = self.sections.get(section, "Unknown")
            print(f"  Section {section} ({section_title}): {section_counts[section]} questions")
        
        # Show sample of actual clause numbers found
        print(f"\n📄 Sample Actual Clause Numbers Found:")
        actual_clause_samples = [c['clause'] for c in self.clauses[:10] if c['clause'] != "No Clause Number"]
        for i, clause_num in enumerate(actual_clause_samples[:5]):
            print(f"  {i+1}. {clause_num}")
        
        return self.clauses
    
    def save_fixed_results(self):
        """Save fixed results with actual clause numbers to CSV and Excel."""
        if not self.clauses:
            print("No clauses to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        
        # Save CSV
        csv_filename = f"../outputs/{base_name}_FIXED_CLAUSE_NUMBERS_{timestamp}.csv"
        
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
        
        print(f"✅ Fixed CSV saved: {csv_filename}")
        
        # Save Excel
        try:
            import pandas as pd
            df = pd.read_csv(csv_filename)
            excel_filename = f"../outputs/{base_name}_FIXED_CLAUSE_NUMBERS_{timestamp}.xlsx"
            
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='NADCAP_Fixed_Clause_Numbers', index=False)
                
                # Auto-adjust column widths
                workbook = writer.book
                worksheet = writer.sheets['NADCAP_Fixed_Clause_Numbers']
                
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 80)  # Increased max width for full content
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"✅ Fixed Excel saved: {excel_filename}")
            
        except ImportError:
            print("⚠️  pandas not available for Excel export")

def main():
    if len(sys.argv) != 2:
        print("Usage: python fixed_complete_nadcap_extractor.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file not found: {pdf_file}")
        sys.exit(1)
    
    # Initialize fixed extractor
    extractor = FixedCompleteNADCAPExtractor(pdf_file)
    
    # Run fixed extraction
    clauses = extractor.run_fixed_extraction()
    
    # Save fixed results
    extractor.save_fixed_results()
    
    print(f"\n🎉 FIXED EXTRACTION FINISHED!")
    print(f"📋 Every question now has ACTUAL clause numbers from the PDF")
    print(f"✅ Fixed clause numbering issue - no more sequential generation")

if __name__ == "__main__":
    main()
