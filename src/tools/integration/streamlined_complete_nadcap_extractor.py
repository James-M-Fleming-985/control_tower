#!/usr/bin/env python3
"""
Streamlined NADCAP Extractor - Precise Clause Number Extraction
Handles clause numbers with 1-4 decimal points that have YES/NO/NA on the same line
"""

import pdfplumber
import json
import re
import sys
import os
import csv
from datetime import datetime

class StreamlinedNADCAPExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.clauses = []
        self.page_contexts = {}
        
        # Complete NADCAP section structure
        self.sections = {
            "2": "INSTRUCTIONS TO AUDITEE",
            "3": "GENERAL QUALITY SYSTEM", 
            "4": "TESTING",
            "5": "EQUIPMENT AND FACILITIES"
        }
        
        # Subsection titles
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
            current_section = "3"
            current_subsection = "3.1"
            
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
                    
                    # Subsection detection
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
    
    def extract_clause_from_yes_no_line(self, line):
        """
        PRECISE METHOD: Extract clause number from lines that contain YES/NO/NA.
        Since all clause numbers appear on the same line as YES/NO, this is very targeted.
        """
        # Comprehensive patterns for clause numbers (1-4 decimal points) that appear with YES/NO
        clause_patterns = [
            # Pattern: Clause Number + Content + YES/NO/NA
            r'^(\d+\.\d+\.\d+\.\d+)\s+(.+?)\s+YES\s+NO',           # 4 decimals: 3.6.1.5 content YES NO
            r'^(\d+\.\d+\.\d+)\s+(.+?)\s+YES\s+NO',               # 3 decimals: 4.3.2 content YES NO
            r'^(\d+\.\d+)\s+(.+?)\s+YES\s+NO',                    # 2 decimals: 3.1 content YES NO
            r'^(\d+)\s+(.+?)\s+YES\s+NO',                         # 1 decimal: 3 content YES NO (rare)
            
            # Also check for patterns anywhere in the line
            r'(\d+\.\d+\.\d+\.\d+)\s+(.+?)\s+YES\s+NO',           # 4 decimals anywhere
            r'(\d+\.\d+\.\d+)\s+(.+?)\s+YES\s+NO',               # 3 decimals anywhere
            r'(\d+\.\d+)\s+(.+?)\s+YES\s+NO',                    # 2 decimals anywhere
        ]
        
        for pattern in clause_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                clause_num = match.group(1)
                content = match.group(2).strip()
                
                # Validate it's a NADCAP clause number
                if clause_num.startswith(('2.', '3.', '4.', '5.')) or clause_num in ['2', '3', '4', '5']:
                    return clause_num, content
        
        # If no clause number found, still extract content
        content_match = re.search(r'^(.+?)\s+YES\s+NO', line, re.IGNORECASE)
        if content_match:
            return None, content_match.group(1).strip()
        
        return None, None
    
    def reconstruct_full_question_content(self, lines, start_index, initial_content):
        """
        Reconstruct full question content starting with initial content from the YES/NO line.
        """
        question_parts = [initial_content] if initial_content else []
        
        # Look ahead for continuation lines (but be conservative since most content is on one line)
        for i in range(start_index + 1, min(len(lines), start_index + 3)):  # Only check 2 lines ahead
            next_line = lines[i].strip()
            
            if not next_line:
                continue
            
            # Stop if we hit another YES/NO pattern (next question)
            if re.search(r'\bYES\s+NO\b', next_line.upper()):
                break
            
            # Stop if we hit a section header
            if re.match(r'^\d+\.\d+\s+[A-Z]', next_line):
                break
            
            # Stop if we hit guidance/notes
            if any(keyword in next_line.lower() for keyword in ['guidance:', 'note:', 'notes:']):
                break
            
            # If it looks like a reasonable continuation
            if len(next_line) > 5 and not re.match(r'^\d+(?:\.\d+)*\s*$', next_line):
                question_parts.append(next_line)
            else:
                break
        
        # Combine and clean up
        full_question = ' '.join(question_parts)
        full_question = re.sub(r'\s+', ' ', full_question).strip()
        
        return full_question
    
    def extract_all_questions_streamlined(self):
        """Phase 2: Streamlined extraction focusing on YES/NO lines with clause numbers."""
        print("\n❓ PHASE 2: Streamlined Extraction (YES/NO Lines with Clause Numbers)")
        print("-" * 70)
        
        questions = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                page_context = self.page_contexts.get(page_num, {'section': '3', 'subsection': '3.1'})
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # Look for lines with YES/NO pattern
                    if re.search(r'\bYES\s+NO\b', line.upper()):
                        # Extract clause number and content from this line
                        clause_num, initial_content = self.extract_clause_from_yes_no_line(line)
                        
                        if initial_content:  # Must have some content
                            # Reconstruct full question content
                            full_question = self.reconstruct_full_question_content(lines, i, initial_content)
                            
                            if len(full_question) > 5:
                                # Get context
                                section = page_context['section']
                                subsection = page_context['subsection']
                                
                                # Use clause number if found, otherwise mark as no clause
                                final_clause = clause_num if clause_num else "No Clause Number"
                                
                                # Get titles
                                section_title = self.sections.get(section, "Unknown Section")
                                subsection_title = self.subsection_titles.get(subsection, f"Subsection {subsection}")
                                
                                # Determine if NA is available
                                has_na = 'NA' in line.upper()
                                
                                # Create question entry
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
                                
                                # Log with decimal count
                                if clause_num:
                                    decimal_count = clause_num.count('.')
                                    decimal_type = f"{decimal_count}-decimal" if decimal_count > 0 else "0-decimal"
                                    print(f"  ✅ Q{len(questions):03d}: Page {page_num} | {decimal_type} | Clause {final_clause}")
                                else:
                                    print(f"  ⚠️  Q{len(questions):03d}: Page {page_num} | No clause number")
                                
                                print(f"      Content: {full_question[:70]}...")
        
        return questions
    
    def extract_guidance_and_notes(self, questions):
        """Phase 3: Extract guidance and notes."""
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
                    if question['content'][:30].lower() in line.lower():
                        content_line_index = j
                        break
                
                if content_line_index >= 0:
                    # Look for guidance and notes in subsequent lines
                    guidance = ""
                    notes = ""
                    
                    for j in range(content_line_index + 1, min(len(lines), content_line_index + 5)):
                        line = lines[j].strip()
                        line_lower = line.lower()
                        
                        if 'guidance:' in line_lower:
                            guidance = line
                        elif 'note:' in line_lower or 'notes:' in line_lower:
                            notes = line
                    
                    question['guidance'] = guidance
                    question['notes'] = notes
        
        return questions
    
    def run_streamlined_extraction(self):
        """Execute streamlined extraction."""
        print("🚀 STREAMLINED NADCAP EXTRACTION - PRECISE CLAUSE NUMBERS")
        print("=" * 70)
        
        # Phase 1: Document structure analysis
        self.analyze_document_structure()
        
        # Phase 2: Streamlined extraction
        questions = self.extract_all_questions_streamlined()
        
        # Phase 3: Guidance and notes
        self.clauses = self.extract_guidance_and_notes(questions)
        
        print(f"\n🎯 STREAMLINED EXTRACTION FINISHED!")
        print(f"📊 Total Questions: {len(self.clauses)}")
        
        # Detailed statistics by decimal count
        clause_stats = {"No Clause": 0}
        for clause in self.clauses:
            if clause['clause'] == "No Clause Number":
                clause_stats["No Clause"] += 1
            else:
                decimal_count = clause['clause'].count('.')
                clause_type = f"{decimal_count}-Decimal"
                clause_stats[clause_type] = clause_stats.get(clause_type, 0) + 1
        
        print(f"\n📊 Clause Number Distribution:")
        total_with_clauses = sum(count for key, count in clause_stats.items() if key != "No Clause")
        print(f"  Questions WITH clause numbers: {total_with_clauses}")
        print(f"  Questions WITHOUT clause numbers: {clause_stats['No Clause']}")
        print(f"\n📊 Breakdown by Decimal Count:")
        for clause_type, count in sorted(clause_stats.items()):
            if clause_type != "No Clause":
                print(f"  {clause_type} clauses: {count}")
        
        # Show samples of each type
        print(f"\n📄 Sample Clause Numbers by Decimal Count:")
        for decimal_count in range(5):  # 0 to 4 decimals
            clause_type = f"{decimal_count}-Decimal"
            samples = [c['clause'] for c in self.clauses 
                      if c['clause'] != "No Clause Number" and c['clause'].count('.') == decimal_count][:3]
            if samples:
                print(f"  {decimal_count} decimals: {', '.join(samples)}")
        
        return self.clauses
    
    def save_streamlined_results(self):
        """Save streamlined results to CSV and Excel."""
        if not self.clauses:
            print("No clauses to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        
        # Save CSV
        csv_filename = f"../outputs/{base_name}_STREAMLINED_ALL_DECIMALS_{timestamp}.csv"
        
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
        
        print(f"✅ Streamlined CSV saved: {csv_filename}")
        
        # Save Excel
        try:
            import pandas as pd
            df = pd.read_csv(csv_filename)
            excel_filename = f"../outputs/{base_name}_STREAMLINED_ALL_DECIMALS_{timestamp}.xlsx"
            
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='NADCAP_Streamlined_All_Decimals', index=False)
                
                # Auto-adjust column widths
                workbook = writer.book
                worksheet = writer.sheets['NADCAP_Streamlined_All_Decimals']
                
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 80)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"✅ Streamlined Excel saved: {excel_filename}")
            
        except ImportError:
            print("⚠️  pandas not available for Excel export")

def main():
    if len(sys.argv) != 2:
        print("Usage: python streamlined_complete_nadcap_extractor.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file not found: {pdf_file}")
        sys.exit(1)
    
    # Initialize streamlined extractor
    extractor = StreamlinedNADCAPExtractor(pdf_file)
    
    # Run streamlined extraction
    clauses = extractor.run_streamlined_extraction()
    
    # Save streamlined results
    extractor.save_streamlined_results()
    
    print(f"\n🎉 STREAMLINED EXTRACTION FINISHED!")
    print(f"📋 Precise extraction of clause numbers (1-4 decimal points)")
    print(f"✅ Focused on YES/NO lines for maximum accuracy")

if __name__ == "__main__":
    main()
