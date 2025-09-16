#!/usr/bin/env python3
"""
ALL QUESTIONS NADCAP EXTRACTOR - COMPREHENSIVE VERSION
======================================================
Extracts ALL NADCAP audit requirements including:
- Questions WITH clause numbers: "3.1 Question text? YES NO NA"
- Questions WITHOUT clause numbers: "Question text? YES NO NA"
- Multi-line question continuation support

Author: Advanced Control Tower
Version: ALL_QUESTIONS_COMPREHENSIVE
Date: September 2, 2025
"""

import pdfplumber
import pandas as pd
import re
import sys
from pathlib import Path

def extract_clause_number_from_start(text):
    """
    Extract clause number from the start of a line if present.
    Returns: (clause_number, question_text, decimal_count) or (None, question_text, 0)
    """
    # Look for clause number at start + YES/NO at end
    clause_pattern = r'^(\d+(?:\.\d+){1,4})\s+(.+?)\s+(YES|NO|NA|N/A)(\s+(YES|NO|NA|N/A))*.*$'
    match = re.match(clause_pattern, text.strip(), re.IGNORECASE)
    
    if match:
        clause_num = match.group(1)
        question_text = match.group(2).strip()
        decimal_count = clause_num.count('.')
        return clause_num, question_text, decimal_count
    
    # If no clause number, just extract question text before YES/NO
    no_clause_pattern = r'^(.+?)\s+(YES|NO|NA|N/A)(\s+(YES|NO|NA|N/A))*.*$'
    match = re.match(no_clause_pattern, text.strip(), re.IGNORECASE)
    
    if match:
        question_text = match.group(1).strip()
        return None, question_text, 0
    
    return None, text.strip(), 0

def is_guidance_line(text):
    """Check if a line is guidance rather than a question."""
    guidance_patterns = [
        r'^Guidance:',
        r'^NOTE:',
        r'^Note:',
        r'NA applies if',
        r'NA applies when',
        r'A yes answer would be',
        r'limit is exceeded',
        r'that is approved to'
    ]
    
    for pattern in guidance_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def find_question_continuation(lines, start_idx):
    """
    Find continuation lines for a multi-line question.
    Stops when hitting next question or section break.
    """
    continuation_lines = []
    
    for i in range(start_idx + 1, len(lines)):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Stop if we hit another YES/NO line (next question)
        if re.search(r'\b(YES|NO|NA|N/A)\b', line, re.IGNORECASE):
            break
        
        # Stop if we hit guidance line
        if is_guidance_line(line):
            break
        
        # Stop if we hit section headers
        if re.match(r'^\d+\.\s+[A-Z]', line) or re.match(r'^\d+\s+[A-Z]', line):
            break
        
        # Add this line as continuation
        continuation_lines.append(line)
        
        # Stop after reasonable number of continuation lines
        if len(continuation_lines) >= 3:
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
        
        # Skip guidance lines
        if is_guidance_line(line):
            i += 1
            continue
        
        # Check if this line contains YES/NO pattern
        if re.search(r'\b(YES|NO|NA|N/A)\b', line, re.IGNORECASE):
            clause_num, question_text, decimal_count = extract_clause_number_from_start(line)
            
            # Skip if this looks like a definition or non-question
            if len(question_text) < 10:
                i += 1
                continue
            
            # Get continuation lines
            continuation_lines = find_question_continuation(lines, i)
            
            # Build complete question text
            full_question = question_text
            if continuation_lines:
                full_question += ' ' + ' '.join(continuation_lines)
            
            # Clean up question text
            full_question = full_question.strip()
            
            # Skip if this is clearly not a question
            if not (full_question.endswith('?') or 'shall' in full_question.lower() or 
                   'does' in full_question.lower() or 'are' in full_question.lower() or
                   'is' in full_question.lower() or 'has' in full_question.lower() or
                   'evidence' in full_question.lower()):
                i += 1
                continue
            
            questions.append({
                'clause_number': clause_num if clause_num else '',
                'decimal_count': decimal_count,
                'question': full_question,
                'page': page_num,
                'guidance': '',
                'notes': ''
            })
            
            if clause_num:
                print(f"✅ Q{len(questions):03d}: Page {page_num} | {decimal_count}-decimal | Clause {clause_num}")
            else:
                print(f"❓ Q{len(questions):03d}: Page {page_num} | No clause number")
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
                    r'Note:\s*(.+)',
                    r'NA applies if\s*(.+)',
                    r'NA applies when\s*(.+)'
                ]
                
                for line in lines:
                    for pattern in guidance_patterns:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            guidance_text = match.group(1).strip()
                            if len(guidance_text) > 5:  # Only meaningful guidance
                                if question['guidance']:
                                    question['guidance'] += ' | ' + guidance_text
                                else:
                                    question['guidance'] = guidance_text

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 all_questions_nadcap_extractor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("🎯 ALL QUESTIONS NADCAP EXTRACTION - COMPREHENSIVE")
    print("=" * 55)
    print("Capturing:")
    print("✅ Questions WITH clause numbers: '3.1 Question? YES NO'")
    print("✅ Questions WITHOUT clause numbers: 'Question? YES NO'")
    print("✅ Multi-line question continuation")
    
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
    
    print(f"\n❓ PHASE 2: All Questions Extraction Results")
    print("-" * 60)
    
    # Phase 3: Extract guidance and notes
    with pdfplumber.open(pdf_path) as pdf:
        extract_guidance_and_notes(all_questions, pdf)
    
    print(f"\n🎯 ALL QUESTIONS EXTRACTION COMPLETE!")
    print(f"📊 Total Questions: {len(all_questions)}")
    
    # Statistics
    questions_with_clauses = [q for q in all_questions if q['clause_number']]
    questions_without_clauses = [q for q in all_questions if not q['clause_number']]
    
    print(f"\n📊 Question Distribution:")
    print(f"  Questions WITH clause numbers: {len(questions_with_clauses)}")
    print(f"  Questions WITHOUT clause numbers: {len(questions_without_clauses)}")
    
    # Decimal breakdown for questions with clause numbers
    if questions_with_clauses:
        decimal_counts = {}
        for q in questions_with_clauses:
            count = q['decimal_count']
            decimal_counts[count] = decimal_counts.get(count, 0) + 1
        
        print(f"\n📊 Clause Number Breakdown:")
        for decimal_count in sorted(decimal_counts.keys()):
            print(f"  {decimal_count}-Decimal clauses: {decimal_counts[decimal_count]}")
        
        # Sample clause numbers
        print(f"\n📄 Sample Clause Numbers by Decimal Count:")
        for decimal_count in sorted(decimal_counts.keys()):
            samples = [q['clause_number'] for q in questions_with_clauses if q['decimal_count'] == decimal_count][:5]
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
    csv_filename = f"../outputs/{pdf_name}_ALL_QUESTIONS_{timestamp}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"✅ All Questions CSV saved: {csv_filename}")
    
    # Save Excel with formatting
    excel_filename = f"../outputs/{pdf_name}_ALL_QUESTIONS_{timestamp}.xlsx"
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
    
    print(f"✅ All Questions Excel saved: {excel_filename}")
    
    print(f"\n🎉 ALL QUESTIONS EXTRACTION COMPLETE!")
    print(f"📋 Comprehensive extraction of ALL questions")
    print(f"✅ Includes questions with AND without clause numbers")
    print(f"✅ Multi-line question support")
    print(f"✅ Complete audit requirements document")

if __name__ == "__main__":
    main()
