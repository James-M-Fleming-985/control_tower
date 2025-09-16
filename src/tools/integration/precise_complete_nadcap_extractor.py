#!/usr/bin/env python3
"""
PRECISE COMPLETE NADCAP EXTRACTOR - FINAL VERSION
===================================================
Extracts ALL NADCAP audit requirements with precise clause number identification.
Based on analysis showing clause numbers appear at START of YES/NO lines.

Pattern observed:
- "3.1 Question text here? YES NO NA"
- "3.6.1.5.1 Question text here? YES NO NA" 
- Sometimes questions span multiple lines before YES/NO

Author: Advanced Control Tower
Version: PRECISE_FINAL
Date: September 2, 2025
"""

import pdfplumber
import pandas as pd
import re
import sys
from pathlib import Path

def extract_clause_number_from_start(text):
    """
    Extract clause number from the start of a line.
    Handles 1-4 decimal point patterns: 3.1, 3.1.1, 3.1.1.1, 3.1.1.1.1
    """
    # Look for clause number at the very start of the line
    clause_pattern = r'^(\d+(?:\.\d+){1,4})\s+'
    match = re.match(clause_pattern, text.strip())
    
    if match:
        clause_num = match.group(1)
        decimal_count = clause_num.count('.')
        return clause_num, decimal_count
    return None, 0

def reconstruct_full_question(lines, start_idx, end_idx):
    """
    Reconstruct the full question text from multiple lines.
    Removes clause number prefix and YES/NO suffix.
    """
    question_parts = []
    
    for i in range(start_idx, end_idx + 1):
        line = lines[i].strip()
        
        # Remove clause number from first line
        if i == start_idx:
            clause_pattern = r'^\d+(?:\.\d+){1,4}\s+'
            line = re.sub(clause_pattern, '', line)
        
        # Remove YES/NO/NA from last line
        if i == end_idx:
            line = re.sub(r'\s+(YES|NO|NA|N/A)(\s+(YES|NO|NA|N/A))*.*$', '', line, flags=re.IGNORECASE)
        
        if line:
            question_parts.append(line)
    
    return ' '.join(question_parts).strip()

def extract_questions_from_page(page, page_num):
    """Extract all questions from a single page."""
    questions = []
    text = page.extract_text()
    
    if not text:
        return questions
    
    lines = text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Check if this line contains YES/NO/NA pattern
        yes_no_pattern = r'\b(YES|NO|NA|N/A)\b'
        
        if re.search(yes_no_pattern, line, re.IGNORECASE):
            # Check if this line starts with a clause number
            clause_num, decimal_count = extract_clause_number_from_start(line)
            
            if clause_num:
                # Single line question with clause number
                question_text = reconstruct_full_question(lines, i, i)
                
                questions.append({
                    'clause_number': clause_num,
                    'decimal_count': decimal_count,
                    'question': question_text,
                    'page': page_num,
                    'guidance': '',
                    'notes': ''
                })
                
                print(f"✅ Q{len(questions):03d}: Page {page_num} | {decimal_count}-decimal | Clause {clause_num}")
                print(f"      Content: {question_text[:60]}...")
            else:
                # Check if previous lines contain the clause number (multi-line question)
                question_start_idx = None
                found_clause = None
                found_decimal_count = 0
                
                # Look backwards up to 5 lines for clause number
                for j in range(max(0, i-5), i):
                    prev_line = lines[j].strip()
                    if prev_line:
                        temp_clause, temp_decimal = extract_clause_number_from_start(prev_line)
                        if temp_clause:
                            # Check if there's no intervening YES/NO line
                            has_intervening_yes_no = False
                            for k in range(j+1, i):
                                if re.search(yes_no_pattern, lines[k], re.IGNORECASE):
                                    has_intervening_yes_no = True
                                    break
                            
                            if not has_intervening_yes_no:
                                question_start_idx = j
                                found_clause = temp_clause
                                found_decimal_count = temp_decimal
                                break
                
                if found_clause and question_start_idx is not None:
                    # Multi-line question
                    question_text = reconstruct_full_question(lines, question_start_idx, i)
                    
                    questions.append({
                        'clause_number': found_clause,
                        'decimal_count': found_decimal_count,
                        'question': question_text,
                        'page': page_num,
                        'guidance': '',
                        'notes': ''
                    })
                    
                    print(f"✅ Q{len(questions):03d}: Page {page_num} | {found_decimal_count}-decimal | Clause {found_clause}")
                    print(f"      Content: {question_text[:60]}...")
                else:
                    # Question without clause number
                    questions.append({
                        'clause_number': '',
                        'decimal_count': 0,
                        'question': line,
                        'page': page_num,
                        'guidance': '',
                        'notes': ''
                    })
                    
                    print(f"⚠️  Q{len(questions):03d}: Page {page_num} | No clause number")
                    print(f"      Content: {line[:60]}...")
        
        i += 1
    
    return questions

def extract_guidance_and_notes(questions, pdf):
    """Extract guidance and notes for each question."""
    print(f"\n📝 PHASE 3: Extracting Guidance and Notes for {len(questions)} questions")
    print("-" * 70)
    
    for idx, question in enumerate(questions):
        if idx % 50 == 0:
            print(f"📝 Processed {idx}/{len(questions)} questions...")
        
        page_num = question['page']
        if page_num <= len(pdf.pages):
            page = pdf.pages[page_num - 1]
            text = page.extract_text()
            
            if text:
                lines = text.split('\n')
                
                # Look for guidance after the question
                guidance_patterns = [
                    r'Guidance:\s*(.+)',
                    r'NOTE:\s*(.+)',
                    r'Note:\s*(.+)'
                ]
                
                for line in lines:
                    for pattern in guidance_patterns:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            guidance_text = match.group(1).strip()
                            if len(guidance_text) > 10:  # Only meaningful guidance
                                if question['guidance']:
                                    question['guidance'] += ' | ' + guidance_text
                                else:
                                    question['guidance'] = guidance_text
                                break

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 precise_complete_nadcap_extractor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("🎯 PRECISE COMPLETE NADCAP EXTRACTION - FINAL VERSION")
    print("=" * 60)
    
    # Phase 1: Extract all questions
    print("\n📋 PHASE 1: Building Complete Document Structure")
    print("-" * 50)
    
    all_questions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(1, len(pdf.pages) + 1):
            page = pdf.pages[page_num - 1]
            
            # Look for pages with substantive content
            text = page.extract_text()
            if text and len(text) > 100:
                # Check if page contains questions (has YES/NO pattern)
                if re.search(r'\b(YES|NO|NA|N/A)\b', text, re.IGNORECASE):
                    print(f"  📄 Page {page_num}: Processing questions...")
                    questions = extract_questions_from_page(page, page_num)
                    all_questions.extend(questions)
    
    print(f"\n❓ PHASE 2: Precise Extraction Results")
    print("-" * 60)
    
    # Phase 3: Extract guidance and notes
    with pdfplumber.open(pdf_path) as pdf:
        extract_guidance_and_notes(all_questions, pdf)
    
    print(f"\n🎯 PRECISE EXTRACTION FINISHED!")
    print(f"📊 Total Questions: {len(all_questions)}")
    
    # Statistics
    questions_with_clauses = [q for q in all_questions if q['clause_number']]
    questions_without_clauses = [q for q in all_questions if not q['clause_number']]
    
    print(f"\n📊 Clause Number Distribution:")
    print(f"  Questions WITH clause numbers: {len(questions_with_clauses)}")
    print(f"  Questions WITHOUT clause numbers: {len(questions_without_clauses)}")
    
    # Decimal breakdown
    decimal_counts = {}
    for q in questions_with_clauses:
        count = q['decimal_count']
        decimal_counts[count] = decimal_counts.get(count, 0) + 1
    
    print(f"\n📊 Breakdown by Decimal Count:")
    for decimal_count in sorted(decimal_counts.keys()):
        print(f"  {decimal_count}-Decimal clauses: {decimal_counts[decimal_count]}")
    
    # Sample clause numbers
    print(f"\n📄 Sample Clause Numbers by Decimal Count:")
    for decimal_count in sorted(decimal_counts.keys()):
        samples = [q['clause_number'] for q in questions_with_clauses if q['decimal_count'] == decimal_count][:3]
        print(f"  {decimal_count} decimals: {', '.join(samples)}")
    
    # Create DataFrame
    df = pd.DataFrame(all_questions)
    
    # Reorder columns for better readability
    column_order = ['clause_number', 'question', 'page', 'guidance', 'notes']
    df = df[column_order]
    
    # Generate output filename
    pdf_name = Path(pdf_path).stem
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
    
    # Save CSV
    csv_filename = f"../outputs/{pdf_name}_PRECISE_FINAL_{timestamp}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"✅ Precise CSV saved: {csv_filename}")
    
    # Save Excel with formatting
    excel_filename = f"../outputs/{pdf_name}_PRECISE_FINAL_{timestamp}.xlsx"
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
    
    print(f"✅ Precise Excel saved: {excel_filename}")
    
    print(f"\n🎉 PRECISE EXTRACTION FINISHED!")
    print(f"📋 Final extraction capturing clause numbers at line start")
    print(f"✅ Handles 1-4 decimal point clause numbers with precision")

if __name__ == "__main__":
    main()
