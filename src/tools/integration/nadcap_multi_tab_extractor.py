#!/usr/bin/env python3
"""
NADCAP MULTI-TAB EXTRACTOR - BY DECIMAL COUNT
==============================================
Creates separate Excel tabs for clauses with 1, 2, 3, and 4 decimal points.
This allows for targeted extraction and manual verification of each decimal level.

Approach:
- Tab 1: 1-decimal clauses (e.g., 3.1, 4.2, 5.3)
- Tab 2: 2-decimal clauses (e.g., 3.1.1, 4.2.3, 5.4.2)
- Tab 3: 3-decimal clauses (e.g., 5.4.2.1, 5.4.2.2)
- Tab 4: 4-decimal clauses (e.g., 3.6.1.5.1, 3.7.3.1.2)
- Tab 5: Questions without clauses (for manual assignment)

Author: Advanced Control Tower
Version: MULTI_TAB_DECIMAL
Date: September 2, 2025
"""

import pdfplumber
import pandas as pd
import re
import sys
from pathlib import Path

def extract_clause_by_decimal_target(text, target_decimal_count):
    """
    Extract clause numbers matching a specific decimal count.
    """
    # Build pattern for exact decimal count
    if target_decimal_count == 0:
        pattern = r'^(\d+)\s+'  # Just a number
    else:
        # Pattern for exact number of decimal points
        decimal_part = r'\.\d+' * target_decimal_count
        pattern = f'^(\\d+{decimal_part})\\s+'
    
    match = re.match(pattern, text.strip())
    
    if match:
        clause_num = match.group(1)
        actual_decimals = clause_num.count('.')
        if actual_decimals == target_decimal_count:
            return clause_num
    return None

def clean_question_text(text, clause_number=None):
    """Clean question text by removing clause number and YES/NO patterns."""
    # Remove clause number from beginning if present
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

def extract_questions_by_decimal_count(pdf, target_decimal_count):
    """
    Extract questions that have clause numbers with specific decimal count.
    """
    questions = []
    
    print(f"\n🎯 EXTRACTING {target_decimal_count}-DECIMAL CLAUSES")
    print("=" * 50)
    
    for page_num in range(1, len(pdf.pages) + 1):
        page = pdf.pages[page_num - 1]
        text = page.extract_text()
        
        if not text:
            continue
        
        lines = text.split('\n')
        current_section = ""
        current_section_title = ""
        current_subsection = ""
        current_subsection_title = ""
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                continue
            
            # Check if this line contains YES/NO/NA (indicating a question)
            if re.search(r'\b(YES|NO|NA|N/A)\b', line, re.IGNORECASE):
                # Try to extract clause number with target decimal count
                clause_number = extract_clause_by_decimal_target(line, target_decimal_count)
                
                if clause_number:
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
                    
                    print(f"✅ {clause_number:12s} | Page {page_num:2d} | {question_text[:50]}...")
                
                # Also check for multi-line questions
                else:
                    # Look for clause number in previous lines
                    clause_found = None
                    question_start_line = None
                    
                    for j in range(max(0, i-5), i):
                        prev_line = lines[j].strip()
                        if prev_line:
                            temp_clause = extract_clause_by_decimal_target(prev_line, target_decimal_count)
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
                        
                        print(f"✅ {clause_found:12s} | Page {page_num:2d} | {question_text[:50]}...")
    
    print(f"📊 Found {len(questions)} questions with {target_decimal_count}-decimal clauses")
    return questions

def extract_questions_without_clauses(pdf):
    """
    Extract questions that don't have identifiable clause numbers.
    """
    questions = []
    
    print(f"\n⚠️  EXTRACTING QUESTIONS WITHOUT CLAUSE NUMBERS")
    print("=" * 50)
    
    for page_num in range(1, len(pdf.pages) + 1):
        page = pdf.pages[page_num - 1]
        text = page.extract_text()
        
        if not text:
            continue
        
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                continue
            
            # Check if this line contains YES/NO/NA (indicating a question)
            if re.search(r'\b(YES|NO|NA|N/A)\b', line, re.IGNORECASE):
                # Check if this line has any clause number (any decimal count)
                has_clause = False
                for decimal_count in range(0, 5):
                    if extract_clause_by_decimal_target(line, decimal_count):
                        has_clause = True
                        break
                
                # Also check previous lines for clause numbers
                if not has_clause:
                    for j in range(max(0, i-5), i):
                        prev_line = lines[j].strip()
                        if prev_line:
                            for decimal_count in range(0, 5):
                                if extract_clause_by_decimal_target(prev_line, decimal_count):
                                    # Check if there's no intervening YES/NO line
                                    has_intervening_yes_no = False
                                    for k in range(j+1, i):
                                        if re.search(r'\b(YES|NO|NA|N/A)\b', lines[k], re.IGNORECASE):
                                            has_intervening_yes_no = True
                                            break
                                    
                                    if not has_intervening_yes_no:
                                        has_clause = True
                                        break
                            if has_clause:
                                break
                
                if not has_clause:
                    question_text = clean_question_text(line)
                    yes, no, na = extract_yes_no_pattern(line)
                    guidance = extract_guidance(lines, i)
                    
                    questions.append({
                        'Page': page_num,
                        'Section': '',
                        'Section_Title': '',
                        'Subsection': '',
                        'Subsection_Title': '',
                        'Clause': '',
                        'Content/Question': question_text,
                        'Guidance': guidance,
                        'Notes': 'NEEDS MANUAL CLAUSE ASSIGNMENT',
                        'Yes': yes,
                        'No': no,
                        'NA': na
                    })
                    
                    print(f"❌ NO CLAUSE     | Page {page_num:2d} | {question_text[:50]}...")
    
    print(f"📊 Found {len(questions)} questions without clause numbers")
    return questions

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 nadcap_multi_tab_extractor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("🎯 NADCAP MULTI-TAB EXTRACTOR - BY DECIMAL COUNT")
    print("=" * 60)
    print("📋 Creating separate tabs for each decimal level")
    print("✅ This will allow manual verification and combination")
    print()
    
    # Generate output filename
    pdf_name = Path(pdf_path).stem
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
    excel_filename = f"../outputs/{pdf_name}_MULTI_TAB_BY_DECIMALS_{timestamp}.xlsx"
    
    all_data = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        # Extract each decimal level separately
        for decimal_count in [1, 2, 3, 4]:
            questions = extract_questions_by_decimal_count(pdf, decimal_count)
            if questions:
                df = pd.DataFrame(questions)
                all_data[f'{decimal_count}-Decimal Clauses'] = df
        
        # Extract questions without clauses
        no_clause_questions = extract_questions_without_clauses(pdf)
        if no_clause_questions:
            df_no_clause = pd.DataFrame(no_clause_questions)
            all_data['No Clause Numbers'] = df_no_clause
    
    # Save to Excel with multiple tabs
    if all_data:
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            total_questions = 0
            
            for sheet_name, df in all_data.items():
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                total_questions += len(df)
                
                # Auto-adjust column widths
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                print(f"✅ Tab '{sheet_name}': {len(df)} questions")
        
        print(f"\n✅ Multi-tab Excel saved: {excel_filename}")
        print(f"📊 Total questions across all tabs: {total_questions}")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Review each tab to verify clause extraction accuracy")
        print(f"2. Check if 3-decimal clauses are properly captured")
        print(f"3. Manually assign clause numbers to 'No Clause Numbers' tab")
        print(f"4. Combine all tabs into a single comprehensive sheet")
        print(f"5. This approach allows targeted debugging of each decimal level")
        
    else:
        print("❌ No questions extracted!")

if __name__ == "__main__":
    main()
