#!/usr/bin/env python3
"""
ACCURATE NADCAP PDF EXTRACTOR - REAL CLAUSE NUMBERS
===================================================
Extracts ACTUAL clause numbers directly from PDF text (not artificially generated).
Captures complete structure: Page, Section, Section Title, Subsection, Subsection Title, 
Clause Number, Question, Guidance, Notes, Yes/No/NA.

Based on user feedback showing 3-decimal clauses like 5.4.2.1, 5.4.2.2, etc.
that were being missed by previous artificial generation approaches.

Author: Advanced Control Tower
Version: ACCURATE_REAL_CLAUSES
Date: September 2, 2025
"""

import pdfplumber
import pandas as pd
import re
import sys
from pathlib import Path

def extract_actual_clause_number(text):
    """
    Extract the actual clause number from the beginning of a line.
    Handles 1-4 decimal point patterns and returns the REAL clause number from PDF.
    """
    # Look for clause number at the very start of the line
    clause_pattern = r'^(\d+(?:\.\d+){0,4})\s+'
    match = re.match(clause_pattern, text.strip())
    
    if match:
        clause_num = match.group(1)
        decimal_count = clause_num.count('.')
        return clause_num, decimal_count
    return None, 0

def extract_section_info(text):
    """
    Extract section and subsection information from text.
    """
    section_match = re.search(r'^(\d+)\.\s+(.+)', text.strip())
    if section_match:
        return section_match.group(1), section_match.group(2)
    
    subsection_match = re.search(r'^(\d+\.\d+)\s+(.+)', text.strip())
    if subsection_match:
        return subsection_match.group(1), subsection_match.group(2)
    
    return None, None

def clean_question_text(text, clause_number=None):
    """
    Clean question text by removing clause number prefix and YES/NO suffix.
    """
    # Remove clause number from beginning if present
    if clause_number:
        pattern = re.escape(clause_number) + r'\s+'
        text = re.sub(f'^{pattern}', '', text, flags=re.IGNORECASE)
    
    # Remove YES/NO/NA from end
    text = re.sub(r'\s+(YES|NO|NA|N/A)(\s+(YES|NO|NA|N/A))*.*$', '', text, flags=re.IGNORECASE)
    
    return text.strip()

def extract_yes_no_pattern(text):
    """
    Extract YES/NO/NA pattern from text.
    """
    # Look for YES NO NA pattern
    if re.search(r'\bYES\s+NO\s+NA\b', text, re.IGNORECASE):
        return 'Yes', 'No', 'NA'
    elif re.search(r'\bYES\s+NO\b', text, re.IGNORECASE):
        return 'Yes', 'No', ''
    else:
        return '', '', ''

def extract_guidance(lines, start_idx):
    """
    Extract guidance text that follows a question.
    """
    guidance_text = ""
    
    # Look in the next few lines for guidance
    for i in range(start_idx + 1, min(start_idx + 5, len(lines))):
        if i < len(lines):
            line = lines[i].strip()
            
            # Check for guidance patterns
            guidance_match = re.search(r'^Guidance:\s*(.+)', line, re.IGNORECASE)
            if guidance_match:
                guidance_text = guidance_match.group(1)
                break
            
            # Check for note patterns
            note_match = re.search(r'^NOTE?:\s*(.+)', line, re.IGNORECASE)
            if note_match:
                guidance_text = note_match.group(1)
                break
    
    return guidance_text

def process_page_for_questions(page, page_num):
    """
    Process a single page to extract all questions with their actual clause numbers.
    """
    questions = []
    text = page.extract_text()
    
    if not text:
        return questions
    
    lines = text.split('\n')
    current_section = ""
    current_section_title = ""
    current_subsection = ""
    current_subsection_title = ""
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Check for section headers (e.g., "3. GENERAL QUALITY SYSTEM")
        section_info = extract_section_info(line)
        if section_info[0] and not '.' in section_info[0]:  # Main section
            current_section = section_info[0]
            current_section_title = section_info[1]
            print(f"📋 Found Section {current_section}: {current_section_title}")
            i += 1
            continue
        elif section_info[0] and section_info[0].count('.') == 1:  # Subsection
            current_subsection = section_info[0]
            current_subsection_title = section_info[1]
            print(f"  📝 Found Subsection {current_subsection}: {current_subsection_title}")
            i += 1
            continue
        
        # Check if this line contains YES/NO/NA (indicating a question)
        if re.search(r'\b(YES|NO|NA|N/A)\b', line, re.IGNORECASE):
            # Extract actual clause number from the line
            clause_number, decimal_count = extract_actual_clause_number(line)
            
            if clause_number:
                # This line has a clause number - it's a direct question
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
                    'Notes': '',  # Can be enhanced later
                    'Yes': yes,
                    'No': no,
                    'NA': na
                })
                
                print(f"✅ Q{len(questions):03d}: {clause_number} ({decimal_count}-decimal) | {question_text[:50]}...")
            
            else:
                # Look for clause number in previous lines (multi-line question)
                clause_found = None
                question_start_line = None
                
                # Look back up to 5 lines for a clause number
                for j in range(max(0, i-5), i):
                    prev_line = lines[j].strip()
                    if prev_line:
                        temp_clause, temp_decimal = extract_actual_clause_number(prev_line)
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
                            # Remove clause number from first line
                            part = clean_question_text(part, clause_found)
                        if k == i:
                            # Remove YES/NO from last line
                            part = clean_question_text(part)
                        if part:
                            question_parts.append(part)
                    
                    question_text = ' '.join(question_parts)
                    yes, no, na = extract_yes_no_pattern(line)
                    guidance = extract_guidance(lines, i)
                    decimal_count = clause_found.count('.')
                    
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
                    
                    print(f"✅ Q{len(questions):03d}: {clause_found} ({decimal_count}-decimal) | {question_text[:50]}...")
                
                else:
                    # Question without identifiable clause number
                    question_text = clean_question_text(line)
                    yes, no, na = extract_yes_no_pattern(line)
                    guidance = extract_guidance(lines, i)
                    
                    questions.append({
                        'Page': page_num,
                        'Section': current_section,
                        'Section_Title': current_section_title,
                        'Subsection': current_subsection,
                        'Subsection_Title': current_subsection_title,
                        'Clause': '',
                        'Content/Question': question_text,
                        'Guidance': guidance,
                        'Notes': '',
                        'Yes': yes,
                        'No': no,
                        'NA': na
                    })
                    
                    print(f"⚠️  Q{len(questions):03d}: NO CLAUSE | {question_text[:50]}...")
        
        i += 1
    
    return questions

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 accurate_nadcap_extractor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("🎯 ACCURATE NADCAP EXTRACTOR - REAL CLAUSE NUMBERS")
    print("=" * 60)
    print("📋 Extracting ACTUAL clause numbers from PDF (not artificially generated)")
    print("✅ Including 1, 2, 3, and 4 decimal point clause numbers")
    print()
    
    all_questions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(1, len(pdf.pages) + 1):
            page = pdf.pages[page_num - 1]
            
            # Check if page contains questions
            text = page.extract_text()
            if text and re.search(r'\b(YES|NO|NA|N/A)\b', text, re.IGNORECASE):
                print(f"\n📄 Processing Page {page_num}...")
                questions = process_page_for_questions(page, page_num)
                all_questions.extend(questions)
    
    print(f"\n🎯 EXTRACTION COMPLETE!")
    print(f"📊 Total Questions Extracted: {len(all_questions)}")
    
    # Analyze clause number distribution
    questions_with_clauses = [q for q in all_questions if q['Clause']]
    questions_without_clauses = [q for q in all_questions if not q['Clause']]
    
    print(f"✅ Questions WITH clause numbers: {len(questions_with_clauses)}")
    print(f"❌ Questions WITHOUT clause numbers: {len(questions_without_clauses)}")
    
    if questions_with_clauses:
        # Count by decimal places
        decimal_counts = {}
        for q in questions_with_clauses:
            decimal_count = q['Clause'].count('.')
            decimal_counts[decimal_count] = decimal_counts.get(decimal_count, 0) + 1
        
        print(f"\n📊 Clause Number Distribution:")
        for decimal_count in sorted(decimal_counts.keys()):
            print(f"  {decimal_count}-decimal clauses: {decimal_counts[decimal_count]}")
        
        # Show some 3-decimal examples if found
        three_decimal_examples = [q for q in questions_with_clauses if q['Clause'].count('.') == 3]
        if three_decimal_examples:
            print(f"\n🎯 3-DECIMAL CLAUSE EXAMPLES FOUND:")
            for q in three_decimal_examples[:10]:
                print(f"  {q['Clause']} | {q['Content/Question'][:50]}...")
    
    # Create DataFrame
    df = pd.DataFrame(all_questions)
    
    # Generate output filename
    pdf_name = Path(pdf_path).stem
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
    
    # Save CSV
    csv_filename = f"../outputs/{pdf_name}_ACCURATE_REAL_CLAUSES_{timestamp}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"✅ Accurate CSV saved: {csv_filename}")
    
    # Save Excel with formatting
    excel_filename = f"../outputs/{pdf_name}_ACCURATE_REAL_CLAUSES_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='NADCAP Requirements')
        
        # Get the worksheet
        worksheet = writer.sheets['NADCAP Requirements']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            
            # Set reasonable limits
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Accurate Excel saved: {excel_filename}")
    
    print(f"\n🎉 ACCURATE EXTRACTION FINISHED!")
    print(f"📋 Real clause numbers extracted directly from PDF")
    print(f"✅ Complete structure: Page, Section, Subsection, Clause, Question, Guidance, Yes/No/NA")
    print(f"🎯 Should now include all 3-decimal clauses like 5.4.2.1, 5.4.2.2, etc.")

if __name__ == "__main__":
    main()
