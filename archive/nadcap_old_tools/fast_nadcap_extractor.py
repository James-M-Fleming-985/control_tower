#!/usr/bin/env python3
"""
FAST & ACCURATE NADCAP Extractor for Stakeholder Presentation
Combines PyMuPDF robustness with simplified logic
"""

import fitz  # PyMuPDF
import re
import csv
from datetime import datetime
import sys
import os

def extract_nadcap_fast(pdf_path):
    """Fast, accurate extraction using PyMuPDF"""
    
    doc = fitz.open(pdf_path)
    clauses = []
    current_section = None
    current_subsection = None
    
    print("Fast NADCAP Extraction Starting...")
    print("=" * 50)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')
        
        actual_page = page_num + 1
        print(f"Processing page {actual_page}...")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Update section context
            section_match = re.match(r'^(\d+)\.\s+([A-Z][A-Z\s&,\-\(\)]+)$', line)
            if section_match:
                current_section = (section_match.group(1), section_match.group(2))
                current_subsection = None
                print(f"  Section {current_section[0]}: {current_section[1]}")
                continue
            
            # Update subsection context
            subsection_match = re.match(r'^(\d+\.\d+)\s+([A-Z][^,\n]+?)(?:\s*$|:)', line)
            if subsection_match:
                current_subsection = (subsection_match.group(1), subsection_match.group(2).strip())
                print(f"    Subsection {current_subsection[0]}: {current_subsection[1]}")
                continue
            
            # Find YES/NO clauses - handle multi-line patterns
            if (re.search(r'\bYES\b', line, re.IGNORECASE) and 
                (re.search(r'\bNO\b', line, re.IGNORECASE) or
                 (i + 1 < len(lines) and re.search(r'\bNO\b', lines[i + 1], re.IGNORECASE)))):
                
                # Check next few lines for NO and NA if not on same line
                combined_line = line
                if i + 1 < len(lines):
                    combined_line += " " + lines[i + 1]
                if i + 2 < len(lines):
                    combined_line += " " + lines[i + 2]
                
                # Extract complete question text
                question_parts = []
                
                # Look backward for question text
                for j in range(i, max(0, i-5), -1):
                    check_line = lines[j].strip()
                    if not check_line:
                        continue
                    
                    # Skip headers and structural elements
                    if (re.match(r'^\d+\.\s', check_line) or 
                        'Nadcap AC7108' in check_line or
                        check_line.upper().startswith('GUIDANCE:')):
                        break
                    
                    # Clean YES/NO from line
                    clean_line = re.sub(r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\s*$', '', check_line).strip()
                    
                    if clean_line and len(clean_line) > 10:
                        question_parts.insert(0, clean_line)
                    elif question_parts:
                        break
                
                # Reconstruct question
                full_question = ' '.join(question_parts).strip()
                full_question = re.sub(r'^\d+(?:\.\d+)*\s*', '', full_question)  # Remove clause numbers
                full_question = re.sub(r'\s+', ' ', full_question)  # Normalize whitespace
                
                # Find guidance
                guidance = ""
                for j in range(i + 1, min(len(lines), i + 3)):
                    if j < len(lines) and lines[j].strip().upper().startswith('GUIDANCE:'):
                        guidance = lines[j].strip().replace('GUIDANCE:', '').strip()
                        break
                
                # Find clause number from combined content or nearby lines
                clause_num = ""
                for j in range(max(0, i-3), min(len(lines), i+2)):
                    if j < len(lines):
                        clause_match = re.search(r'^(\d+\.\d+\.\d+(?:\.\d+)*)', lines[j])
                        if clause_match:
                            clause_num = clause_match.group(1)
                            break
                # Also check combined line
                if not clause_num:
                    clause_match = re.search(r'(\d+\.\d+\.\d+(?:\.\d+)*)', combined_line)
                    if clause_match:
                        clause_num = clause_match.group(1)
                
                # Determine response type from combined content
                response_type = "yes_no_na" if re.search(r'\b(?:NA|N/A)\b', combined_line, re.IGNORECASE) else "yes_no"
                
                # Create clause record
                if len(full_question) > 15:  # Only meaningful questions
                    clause = {
                        'page': actual_page,
                        'section_num': current_section[0] if current_section else "Unknown",
                        'section_title': current_section[1] if current_section else "Unknown Section",
                        'subsection_num': current_subsection[0] if current_subsection else "",
                        'subsection_title': current_subsection[1] if current_subsection else "",
                        'clause': clause_num,
                        'content': full_question,
                        'guidance': guidance,
                        'response_type': response_type
                    }
                    clauses.append(clause)
                    print(f"    ✓ Clause: {full_question[:50]}...")
    
    doc.close()
    
    # Save to CSV
    output_dir = os.path.join(os.path.dirname(pdf_path), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    csv_path = os.path.join(output_dir, f"{base_name}_FINAL_{timestamp}.csv")
    
    fieldnames = ['Page', 'Section', 'Section_Title', 'Subsection', 'Subsection_Title', 
                 'Clause', 'Content/Question', 'Guidance', 'Notes', 'Yes', 'No', 'NA']
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for clause in clauses:
            writer.writerow({
                'Page': clause['page'],
                'Section': clause['section_num'],
                'Section_Title': clause['section_title'],
                'Subsection': clause['subsection_num'],
                'Subsection_Title': clause['subsection_title'],
                'Clause': clause['clause'],
                'Content/Question': clause['content'],
                'Guidance': clause['guidance'],
                'Notes': '',
                'Yes': '',
                'No': '',
                'NA': 'X' if clause['response_type'] == 'yes_no_na' else ''
            })
    
    print(f"\n🎯 FINAL EXTRACTION COMPLETE!")
    print(f"📊 Total clauses: {len(clauses)}")
    print(f"📁 File saved: {csv_path}")
    print(f"⏰ Ready for presentation!")
    
    return csv_path, len(clauses)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fast_nadcap_extractor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extract_nadcap_fast(pdf_path)
