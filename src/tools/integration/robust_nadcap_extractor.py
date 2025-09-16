#!/usr/bin/env python3
"""
Robust NADCAP PDF Extractor using PyMuPDF
Font-aware structure detection for accurate section/subsection mapping
"""

import fitz  # PyMuPDF
import re
import csv
import json
from datetime import datetime
import sys
import os

class RobustNADCAPExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.extracted_clauses = []
        self.current_section = None
        self.current_subsection = None
        
    def analyze_font_styles(self):
        """Analyze font styles to identify headers vs content"""
        font_styles = {}
        
        for page_num in range(min(10, len(self.doc))):  # Sample first 10 pages
            page = self.doc[page_num]
            blocks = page.get_text("dict")
            
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                font_key = f"{span['font']}_{span['size']:.1f}_{span['flags']}"
                                if font_key not in font_styles:
                                    font_styles[font_key] = []
                                font_styles[font_key].append(text[:50])
        
        # Identify likely header fonts (larger size, bold, contains section numbers)
        header_fonts = []
        for font_key, samples in font_styles.items():
            font_name, size, flags = font_key.split('_')
            size = float(size)
            
            # Check if samples contain section-like patterns
            section_patterns = sum(1 for s in samples if re.match(r'^\d+\.', s))
            if section_patterns > 0 and size > 10:  # Likely headers
                header_fonts.append(font_key)
        
        return header_fonts, font_styles
    
    def extract_structured_text(self):
        """Extract text with font and position information"""
        structured_data = []
        header_fonts, _ = self.analyze_font_styles()
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks = page.get_text("dict")
            
            page_data = {
                'page': page_num + 1,
                'elements': []
            }
            
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        font_info = None
                        
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                line_text += text + " "
                                if font_info is None:
                                    font_info = {
                                        'font': span['font'],
                                        'size': span['size'],
                                        'flags': span['flags'],
                                        'font_key': f"{span['font']}_{span['size']:.1f}_{span['flags']}"
                                    }
                        
                        if line_text.strip():
                            element = {
                                'text': line_text.strip(),
                                'font_info': font_info,
                                'is_header': font_info['font_key'] in header_fonts if font_info else False,
                                'bbox': line.get('bbox', [0, 0, 0, 0])
                            }
                            page_data['elements'].append(element)
            
            structured_data.append(page_data)
        
        return structured_data
    
    def process_structured_extraction(self, structured_data):
        """Process the structured data to extract clauses"""
        
        for page_data in structured_data:
            page_num = page_data['page']
            elements = page_data['elements']
            
            # Update section/subsection context based on headers
            for element in elements:
                text = element['text']
                
                # Check for main sections (e.g., "3. GENERAL QUALITY SYSTEM")
                section_match = re.match(r'^(\d+)\.\s+([A-Z][A-Z\s&,\-\(\)]+)$', text)
                if section_match or element['is_header']:
                    if section_match:
                        self.current_section = {
                            'number': section_match.group(1),
                            'title': section_match.group(2).strip()
                        }
                        self.current_subsection = None
                        print(f"Found Section {self.current_section['number']}: {self.current_section['title']} (Page {page_num})")
                        continue
                
                # Check for subsections (e.g., "3.6 Job Documentation")
                subsection_match = re.match(r'^(\d+\.\d+)\s+([A-Z][^,\n]+?)(?:\s*$|:)', text)
                if subsection_match:
                    self.current_subsection = {
                        'number': subsection_match.group(1),
                        'title': subsection_match.group(2).strip()
                    }
                    print(f"  Found Subsection {self.current_subsection['number']}: {self.current_subsection['title']} (Page {page_num})")
                    continue
                
                # Check for YES/NO clauses
                if re.search(r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\b', text):
                    self.extract_clause(text, page_num, elements, element)
    
    def extract_clause(self, yes_no_line, page_num, all_elements, current_element):
        """Extract a single clause with complete content"""
        
        # Find the question text (may be on previous lines)
        current_idx = all_elements.index(current_element)
        question_parts = []
        
        # Look backward for question text
        for i in range(current_idx, max(0, current_idx - 5), -1):
            elem = all_elements[i]
            text = elem['text']
            
            # Skip if this is a header or section marker
            if elem['is_header'] or re.match(r'^\d+\.\s', text) or 'Nadcap AC7108' in text:
                break
                
            # Clean up YES/NO from text
            clean_text = re.sub(r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\s*$', '', text).strip()
            
            if clean_text and len(clean_text) > 10:
                question_parts.insert(0, clean_text)
            elif question_parts:  # Stop if we've collected text and hit empty line
                break
        
        # Reconstruct complete question
        full_question = ' '.join(question_parts).strip()
        
        # Clean up the question
        full_question = re.sub(r'\s+', ' ', full_question)
        full_question = re.sub(r'^\d+(?:\.\d+)*\s*', '', full_question)  # Remove clause numbers
        
        # Look for guidance (following lines)
        guidance = ""
        for i in range(current_idx + 1, min(len(all_elements), current_idx + 5)):
            elem = all_elements[i]
            text = elem['text']
            
            if text.upper().startswith('GUIDANCE:'):
                guidance = text
                break
            elif re.search(r'\b(?:YES|Yes)\s+(?:NO|No)', text):  # Hit next question
                break
        
        # Find specific clause number
        clause_num = ""
        for i in range(max(0, current_idx - 3), min(len(all_elements), current_idx + 2)):
            elem = all_elements[i]
            clause_match = re.search(r'^(\d+\.\d+\.\d+(?:\.\d+)*)', elem['text'])
            if clause_match:
                clause_num = clause_match.group(1)
                break
        
        # Determine response type
        response_type = "yes_no_na" if re.search(r'\b(?:NA|N/A)\b', yes_no_line, re.IGNORECASE) else "yes_no"
        
        # Build clause record
        clause = {
            'page': page_num,
            'section_num': self.current_section['number'] if self.current_section else "Unknown",
            'section_title': self.current_section['title'] if self.current_section else "Unknown Section",
            'subsection_num': self.current_subsection['number'] if self.current_subsection else "",
            'subsection_title': self.current_subsection['title'] if self.current_subsection else "",
            'clause': clause_num,
            'content': full_question,
            'guidance': guidance.replace('GUIDANCE:', '').strip() if guidance else "",
            'response_type': response_type,
            'yes_no_line': yes_no_line
        }
        
        # Only add if we have meaningful content
        if len(full_question) > 15:
            self.extracted_clauses.append(clause)
            print(f"Extracted clause on page {page_num}: {full_question[:60]}...")
    
    def save_to_csv(self, output_path):
        """Save extracted clauses to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        csv_path = output_path.replace('.csv', f'_robust_{timestamp}.csv')
        
        fieldnames = ['Page', 'Section', 'Section_Title', 'Subsection', 'Subsection_Title', 
                     'Clause', 'Content/Question', 'Guidance', 'Notes', 'Yes', 'No', 'NA']
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for clause in self.extracted_clauses:
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
        
        print(f"\nRobust CSV saved: {csv_path}")
        print(f"Total clauses extracted: {len(self.extracted_clauses)}")
        return csv_path
    
    def extract_all(self):
        """Main extraction method"""
        print("Starting Robust NADCAP Extraction with PyMuPDF...")
        print("=" * 60)
        
        try:
            # Extract structured text with font information
            structured_data = self.extract_structured_text()
            
            # Process the structured data
            self.process_structured_extraction(structured_data)
            
            # Generate output path
            output_dir = os.path.join(os.path.dirname(self.pdf_path), 'outputs')
            os.makedirs(output_dir, exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            csv_path = os.path.join(output_dir, f"{base_name}_robust_extraction.csv")
            
            # Save results
            final_csv = self.save_to_csv(csv_path)
            
            return True, final_csv
            
        except Exception as e:
            print(f"Error during extraction: {str(e)}")
            return False, None
        finally:
            self.doc.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python robust_nadcap_extractor.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    extractor = RobustNADCAPExtractor(pdf_path)
    success, output_file = extractor.extract_all()
    
    if success:
        print(f"\n✅ Extraction completed successfully!")
        print(f"📁 Output file: {output_file}")
        print(f"\nReady for stakeholder presentation!")
    else:
        print("❌ Extraction failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
