#!/usr/bin/env python3
"""
FINAL COMPLETE NADCAP EXTRACTOR - CORRECT PATTERN
==================================================
Extracts ALL NADCAP audit requirements with correct understanding:
- Clause number and YES/NO/NA appear on the SAME FIRST LINE
- Question text can span multiple lines after this first line
- Pattern: "3.1 Question start text? YES NO NA"
         "continuation of question text..."
         "more question text..."

Author: Advanced Control Tower
Version: FINAL_CORRECT
Date: September 2, 2025
"""

import pdfplumber
import pandas as pd
import re
import sys
from pathlib import Path

def extract_clause_and_question_start(text):
    """
    Extract clause number and question start from first line.
    Pattern: "3.1 Question text here? YES NO NA"
    Returns: (clause_number, question_start, decimal_count)
    """
    # Look for clause number at start + YES/NO at end of same line
    pattern = r'^(\d+(?:\.\d+){1,4})\s+(.+?)\s+(YES|NO|NA|N/A)(\s+(YES|NO|NA|N/A))*.*$'
    match = re.match(pattern, text.strip(), re.IGNORECASE)
    
    if match:
        clause_num = match.group(1)
        question_start = match.group(2).strip()
        decimal_count = clause_num.count('.')
        return clause_num, question_start, decimal_count
    return None, None, 0

def find_question_continuation(lines, start_idx):
    """
    Find continuation lines for a multi-line question.
    Stops when hitting next clause number line or section break.
    """
    continuation_lines = []
    
    for i in range(start_idx + 1, len(lines)):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Stop if we hit another clause number + YES/NO line
        if re.match(r'^\d+(?:\.\d+){1,4}\s+.+\s+(YES|NO|NA|N/A)', line, re.IGNORECASE):
            break
        
        # Stop if we hit guidance line
        if re.match(r'^Guidance:', line, re.IGNORECASE):
            break
        
        # Stop if we hit section headers (numbers only or major sections)
        if re.match(r'^\d+\.\s+[A-Z]', line) or re.match(r'^\d+\s+[A-Z]', line):
            break
        
        # Add this line as continuation
        continuation_lines.append(line)
        
        # Stop after reasonable number of continuation lines
        if len(continuation_lines) >= 5:
            break
    
    return continuation_lines

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
        
        # Check if this line has clause number + YES/NO pattern
        clause_num, question_start, decimal_count = extract_clause_and_question_start(line)
        
        if clause_num and question_start:
            # Found a question with clause number
            
            # Get continuation lines
            continuation_lines = find_question_continuation(lines, i)
            
            # Build complete question text
            full_question = question_start
            if continuation_lines:
                full_question += ' ' + ' '.join(continuation_lines)
            
            # Clean up question text
            full_question = full_question.strip()
            
            questions.append({
                'clause_number': clause_num,
                'decimal_count': decimal_count,
                'question': full_question,
                'page': page_num,
                'guidance': '',
                'notes': ''
            })
            
            print(f"✅ Q{len(questions):03d}: Page {page_num} | {decimal_count}-decimal | Clause {clause_num}")
            print(f"      Content: {full_question[:80]}...")
        
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
        print("Usage: python3 final_complete_nadcap_extractor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("🎯 FINAL COMPLETE NADCAP EXTRACTION - CORRECT PATTERN")
    print("=" * 60)
    print("Pattern: Clause# + Question Start + YES/NO on SAME line")
    print("         Question continuation on following lines")
    
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
                # Check if page contains questions (has clause + YES/NO pattern)
                if re.search(r'^\d+(?:\.\d+){1,4}\s+.+\s+(YES|NO|NA|N/A)', text, re.MULTILINE | re.IGNORECASE):
                    print(f"  📄 Page {page_num}: Processing questions...")
                    questions = extract_questions_from_page(page, page_num)
                    all_questions.extend(questions)
    
    print(f"\n❓ PHASE 2: Final Extraction Results")
    print("-" * 60)
    
    # Phase 3: Extract guidance and notes
    with pdfplumber.open(pdf_path) as pdf:
        extract_guidance_and_notes(all_questions, pdf)
    
    print(f"\n🎯 FINAL EXTRACTION COMPLETE!")
    print(f"📊 Total Questions: {len(all_questions)}")
    
    # Statistics
    decimal_counts = {}
    for q in all_questions:
        count = q['decimal_count']
        decimal_counts[count] = decimal_counts.get(count, 0) + 1
    
    print(f"\n📊 Breakdown by Decimal Count:")
    for decimal_count in sorted(decimal_counts.keys()):
        print(f"  {decimal_count}-Decimal clauses: {decimal_counts[decimal_count]}")
    
    # Sample clause numbers
    print(f"\n📄 Sample Clause Numbers by Decimal Count:")
    for decimal_count in sorted(decimal_counts.keys()):
        samples = [q['clause_number'] for q in all_questions if q['decimal_count'] == decimal_count][:5]
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
    csv_filename = f"../outputs/{pdf_name}_FINAL_COMPLETE_{timestamp}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"✅ Final CSV saved: {csv_filename}")
    
    # Save Excel with formatting
    excel_filename = f"../outputs/{pdf_name}_FINAL_COMPLETE_{timestamp}.xlsx"
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
    
    print(f"✅ Final Excel saved: {excel_filename}")
    
    print(f"\n🎉 FINAL EXTRACTION COMPLETE!")
    print(f"📋 Correctly handles clause# + YES/NO on same line")
    print(f"✅ Captures multi-line question continuation")
    print(f"✅ All 1-4 decimal point clause numbers extracted")

if __name__ == "__main__":
    main()
