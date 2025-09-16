#!/usr/bin/env python3
"""
NADCAP EXTRACTOR - 3-DECIMAL CLAUSES ONLY
==========================================
Focused extraction of ONLY 3-decimal clause numbers (like 5.4.2.1, 5.4.2.2, 5.4.2.3).
This is iteration 3 - focused on 3-decimal patterns.

Author: Advanced Control Tower
Version: 3_DECIMAL_ONLY
Date: September 2, 2025
"""

import pdfplumber
import pandas as pd
import re
import sys
from pathlib import Path

def extract_3_decimal_clause(text):
    """
    Extract ONLY 3-decimal clause numbers (like 5.4.2.1, 5.4.2.2, 5.4.2.3).
    Returns clause number if it's exactly 3 decimals.
    """
    # Look for exactly 3-decimal clause number at start of line
    clause_pattern = r'^(\d+\.\d+\.\d+\.\d+)\s+'
    match = re.match(clause_pattern, text.strip())
    
    if match:
        clause_num = match.group(1)
        # Verify it's exactly 3 decimals
        if clause_num.count('.') == 3:
            return clause_num
    return None

def clean_question_text(text, clause_number=None):
    """Clean question text by removing clause number prefix and YES/NO suffix."""
    if clause_number:
        pattern = re.escape(clause_number) + r'\s+'
        text = re.sub(f'^{pattern}', '', text, flags=re.IGNORECASE)
    
    # Remove YES/NO/NA from end
    text = re.sub(r'\s+(YES|NO|NA|N/A)(\s+(YES|NO|NA|N/A))*.*$', '', text, flags=re.IGNORECASE)
    
    return text.strip()

def extract_yes_no_pattern(text):
    """Extract YES/NO/NA pattern from text."""
    if re.search(r'\bYES\s+NO\s+NA\b', text, re.IGNORECASE):
        return 'Yes', 'No', 'NA'
    elif re.search(r'\bYES\s+NO\b', text, re.IGNORECASE):
        return 'Yes', 'No', ''
    else:
        return '', '', ''

def extract_guidance(lines, start_idx):
    """Extract guidance text that follows a question."""
    guidance_text = ""
    
    for i in range(start_idx + 1, min(start_idx + 5, len(lines))):
        if i < len(lines):
            line = lines[i].strip()
            
            guidance_match = re.search(r'^Guidance:\s*(.+)', line, re.IGNORECASE)
            if guidance_match:
                guidance_text = guidance_match.group(1)
                break
            
            note_match = re.search(r'^NOTE?:\s*(.+)', line, re.IGNORECASE)
            if note_match:
                guidance_text = note_match.group(1)
                break
    
    return guidance_text

def extract_section_info(text):
    """Extract section information from text."""
    section_match = re.search(r'^(\d+)\.\s+(.+)', text.strip())
    if section_match:
        return section_match.group(1), section_match.group(2)
    
    subsection_match = re.search(r'^(\d+\.\d+)\s+(.+)', text.strip())
    if subsection_match:
        return subsection_match.group(1), subsection_match.group(2)
    
    return None, None

def process_page_for_3_decimal_clauses(page, page_num):
    """Process a single page to extract ONLY 3-decimal clause questions."""
    questions = []
    text = page.extract_text()
    
    if not text:
        return questions
    
    lines = text.split('\n')
    current_section = ""
    current_section_title = ""
    current_subsection = ""
    current_subsection_title = ""
    
    # Also check for 3-decimal patterns anywhere in the page, not just at line start
    print(f"🔍 Scanning Page {page_num} for 3-decimal patterns...")
    
    # Search for 3-decimal patterns anywhere in the text
    three_decimal_patterns = re.findall(r'\b(\d+\.\d+\.\d+\.\d+)\b', text)
    if three_decimal_patterns:
        print(f"  📋 Found 3-decimal patterns on page {page_num}: {set(three_decimal_patterns)}")
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Check for section headers
        section_info = extract_section_info(line)
        if section_info[0] and not '.' in section_info[0]:  # Main section
            current_section = section_info[0]
            current_section_title = section_info[1]
            i += 1
            continue
        elif section_info[0] and section_info[0].count('.') == 1:  # Subsection
            current_subsection = section_info[0]
            current_subsection_title = section_info[1]
            i += 1
            continue
        
        # Check if this line contains YES/NO/NA (indicating a question)
        if re.search(r'\b(YES|NO|NA|N/A)\b', line, re.IGNORECASE):
            # Extract 3-decimal clause number from the line
            clause_number = extract_3_decimal_clause(line)
            
            if clause_number:
                # This line has a 3-decimal clause number
                question_text = clean_question_text(line, clause_number)
                yes, no, na = extract_yes_no_pattern(line)
                guidance = extract_guidance(lines, i)
                
                questions.append({
                    'Page': page_num,
                    'Section': current_section,
                    'Section_Title': current_section_title,
                    'Subsection': current_subsection,
                    'Subsection_Title': current_subsection_title,
                    'Clause': clause_number,
                    'Content/Question': question_text,
                    'Guidance': guidance,
                    'Notes': '',
                    'Yes': yes,
                    'No': no,
                    'NA': na
                })
                
                print(f"✅ 3-DEC Q{len(questions):03d}: {clause_number} | Page {page_num} | {question_text[:50]}...")
            
            else:
                # Look for 3-decimal clause number in previous lines (multi-line question)
                clause_found = None
                question_start_line = None
                
                for j in range(max(0, i-5), i):
                    prev_line = lines[j].strip()
                    if prev_line:
                        temp_clause = extract_3_decimal_clause(prev_line)
                        if temp_clause:
                            # Check if there's no intervening YES/NO line
                            has_intervening_yes_no = False
                            for k in range(j+1, i):
                                if re.search(r'\b(YES|NO|NA|N/A)\b', lines[k], re.IGNORECASE):
                                    has_intervening_yes_no = True
                                    break
                            
                            if not has_intervening_yes_no:
                                clause_found = temp_clause
                                question_start_line = j
                                break
                
                if clause_found and question_start_line is not None:
                    # Reconstruct multi-line question
                    question_parts = []
                    for k in range(question_start_line, i + 1):
                        part = lines[k].strip()
                        if k == question_start_line:
                            part = clean_question_text(part, clause_found)
                        if k == i:
                            part = clean_question_text(part)
                        if part:
                            question_parts.append(part)
                    
                    question_text = ' '.join(question_parts)
                    yes, no, na = extract_yes_no_pattern(line)
                    guidance = extract_guidance(lines, i)
                    
                    questions.append({
                        'Page': page_num,
                        'Section': current_section,
                        'Section_Title': current_section_title,
                        'Subsection': current_subsection,
                        'Subsection_Title': current_subsection_title,
                        'Clause': clause_found,
                        'Content/Question': question_text,
                        'Guidance': guidance,
                        'Notes': '',
                        'Yes': yes,
                        'No': no,
                        'NA': na
                    })
                    
                    print(f"✅ 3-DEC Q{len(questions):03d}: {clause_found} | Page {page_num} | {question_text[:50]}...")
        
        i += 1
    
    return questions

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 nadcap_3_decimal_extractor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("🎯 NADCAP EXTRACTOR - 3-DECIMAL CLAUSES ONLY")
    print("=" * 50)
    print("📋 Extracting ONLY 3-decimal clause numbers (like 5.4.2.1, 5.4.2.2, 5.4.2.3)")
    print("🔄 This is iteration 3 - focused on 3-decimal patterns")
    print("🔍 Will also scan for 3-decimal patterns anywhere in the page")
    print()
    
    all_questions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Focus on pages around 28 where we expect to find 5.4.2.x clauses
        target_pages = list(range(27, 32))  # Pages 27-31
        
        for page_num in target_pages:
            if page_num <= len(pdf.pages):
                page = pdf.pages[page_num - 1]
                
                # Check if page contains questions
                text = page.extract_text()
                if text and re.search(r'\b(YES|NO|NA|N/A)\b', text, re.IGNORECASE):
                    questions = process_page_for_3_decimal_clauses(page, page_num)
                    if questions:  # Only print if we found questions
                        print(f"📄 Page {page_num}: Found {len(questions)} 3-decimal clause questions")
                    all_questions.extend(questions)
    
    print(f"\n🎯 3-DECIMAL EXTRACTION COMPLETE!")
    print(f"📊 Total 3-Decimal Questions: {len(all_questions)}")
    
    if all_questions:
        # Show all 3-decimal clauses found
        print(f"\n📋 ALL 3-DECIMAL CLAUSES FOUND:")
        unique_clauses = list(set([q['Clause'] for q in all_questions]))
        unique_clauses.sort(key=lambda x: [int(n) for n in x.split('.')])
        
        for clause in unique_clauses:
            print(f"  {clause}")
    else:
        print("\n❌ NO 3-decimal clauses found with this approach!")
        print("🔍 The clause numbers might be positioned differently in the PDF layout")
    
    # Create DataFrame
    df = pd.DataFrame(all_questions)
    
    # Generate output filename
    pdf_name = Path(pdf_path).stem
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
    
    # Save Excel with 3-decimal tab
    excel_filename = f"../outputs/{pdf_name}_3_DECIMAL_CLAUSES_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='3-Decimal Clauses')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['3-Decimal Clauses']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ 3-Decimal Excel saved: {excel_filename}")
    
    print(f"\n🎉 ITERATION 3 FINISHED!")
    print(f"📋 Next: Create 4-decimal extractor (like 3.6.1.5.1)")
    print(f"🔍 May need different approach for clause number extraction")

if __name__ == "__main__":
    main()
