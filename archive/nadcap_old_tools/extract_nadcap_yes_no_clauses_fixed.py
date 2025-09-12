#!/usr/bin/env python3
"""
NADCAP Audit Requirements - Yes/No Clause Extraction Script
Specifically extracts clauses with Yes/No or Yes/No/NA response options
and formats them for compliance tracking and gap analysis.
"""

import sys
import os
import re
import csv
import json
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    print("pdfplumber not found. Installing...")
    os.system("pip install pdfplumber")
    import pdfplumber

class NADCAPYesNoExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.extracted_clauses = []
        self.document_info = {
            "title": "NADCAP Audit Requirements",
            "version": "Unknown",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "total_clauses_extracted": 0
        }
    
    def extract_text_from_pdf(self):
        """Extract all text from PDF with page markers"""
        full_text = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"Processing PDF: {self.pdf_path}")
                print(f"Total pages: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"Processing page {page_num}...")
                    text = page.extract_text()
                    if text:
                        full_text.append({
                            'page': page_num,
                            'text': text
                        })
                
                return full_text
                
        except Exception as e:
            print(f"Error extracting PDF: {str(e)}")
            return []
    
    def identify_yes_no_patterns(self, text):
        """
        Identify patterns that indicate Yes/No or Yes/No/NA response options
        """
        # Common patterns for Yes/No responses - Updated to match NADCAP format
        patterns = [
            # Original checkbox patterns
            r'(?:Yes|YES)\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:No|NO)\s*(?:☐|□|\[\s*\]|\(\s*\))',
            r'(?:Yes|YES)\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:No|NO)\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:NA|N/A)\s*(?:☐|□|\[\s*\]|\(\s*\))',
            r'☐\s*(?:Yes|YES)\s*☐\s*(?:No|NO)',
            r'☐\s*(?:Yes|YES)\s*☐\s*(?:No|NO)\s*☐\s*(?:NA|N/A)',
            r'\[\s*\]\s*(?:Yes|YES)\s*\[\s*\]\s*(?:No|NO)',
            r'\[\s*\]\s*(?:Yes|YES)\s*\[\s*\]\s*(?:No|NO)\s*\[\s*\]\s*(?:NA|N/A)',
            r'(?:Yes|YES):\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:No|NO):\s*(?:☐|□|\[\s*\]|\(\s*\))',
            r'(?:Yes|YES):\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:No|NO):\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:NA|N/A):\s*(?:☐|□|\[\s*\]|\(\s*\))',
            
            # NADCAP specific patterns (simple text without checkboxes)
            r'(?:YES|Yes)\s+(?:NO|No)\s*$',  # YES NO at end of line
            r'(?:YES|Yes)\s+(?:NO|No)\s+(?:NA|N/A)\s*$',  # YES NO NA at end of line
            r'(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\s*$',  # YES NO or YES NO NA at end of line
            
            # Additional NADCAP patterns with more flexibility
            r'\b(?:YES|Yes)\s+(?:NO|No)\b',  # YES NO anywhere in text
            r'\b(?:YES|Yes)\s+(?:NO|No)\s+(?:NA|N/A)\b',  # YES NO NA anywhere in text
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def find_section_info(self, page_text, current_line_index):
        """Find the section number and title for a clause"""
        lines = page_text.split('\n')
        
        # Look backwards from current line to find section headers
        for i in range(current_line_index, max(0, current_line_index - 25), -1):
            line = lines[i].strip() if i < len(lines) else ""
            
            # Look for section title patterns like "3.6 Job Documentation"
            section_patterns = [
                r'^(\d+(?:\.\d+)*)\s+([A-Z][^,\n]+?)(?:\s*$|[:\n])',  # "3.6 Job Documentation"
                r'^(\d+(?:\.\d+)*)\s+(.+?)(?:\s*$|[:\n])',  # General numbered section
            ]
            
            for pattern in section_patterns:
                match = re.search(pattern, line)
                if match and len(match.group(2)) > 5:  # Ensure it's a meaningful title
                    section_num = match.group(1)
                    section_title = match.group(2).strip()
                    
                    # Clean up common artifacts and remove trailing punctuation
                    section_title = re.sub(r'\s+', ' ', section_title)
                    section_title = re.sub(r'[:\s]*$', '', section_title)  # Remove trailing : or spaces
                    
                    # Make sure it looks like a real section title
                    if any(word in section_title.upper() for word in ['DOCUMENTATION', 'TRAINING', 'PERSONNEL', 'QUALITY', 'PROCESS', 'CONTROL', 'MANAGEMENT', 'INSPECTION', 'TESTING', 'EQUIPMENT', 'FACILITIES', 'IMPROVEMENT', 'LAYOUT', 'SYSTEM']):
                        return section_num, section_title
        
        return "General", "General Requirements"
    
    def extract_specific_clause_number(self, text_lines, line_index):
        """Extract the specific clause number (not section number) for a requirement"""
        # Look for specific clause patterns in the current and nearby lines
        for i in range(max(0, line_index - 2), min(len(text_lines), line_index + 2)):
            line = text_lines[i].strip()
            
            # Look for detailed clause patterns like 3.6.1.5.1, 3.7.3.1.1, etc.
            detailed_patterns = [
                r'(\d+\.\d+\.\d+\.\d+\.\d+)',  # 3.6.1.5.1
                r'(\d+\.\d+\.\d+\.\d+)',       # 3.7.3.1
                r'(\d+\.\d+\.\d+)',            # 3.6.1
            ]
            
            for pattern in detailed_patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1)
        
        # If no specific clause found, return empty to indicate it's a general section question
        return ""
    
    def extract_full_guidance(self, text_lines, current_line_index):
        """Extract complete guidance text for a clause"""
        guidance_lines = []
        
        # Look for guidance in the lines following the current clause
        for j in range(current_line_index + 1, min(current_line_index + 10, len(text_lines))):
            next_line = text_lines[j].strip()
            
            if not next_line:
                continue
                
            # Stop if we hit another YES/NO pattern (next clause)
            if self.identify_yes_no_patterns(next_line):
                break
                
            # Stop if we hit a new section or clause number
            if re.match(r'^\d+(?:\.\d+)*\s+[A-Z]', next_line):
                break
                
            # Check if this looks like guidance
            if any(word in next_line.lower() for word in ['guidance:', 'note:', 'see also:', 'refer', 'example', 'include', 'na applies', 'see as9100', 'see ac7108']):
                guidance_lines.append(next_line)
                
                # Continue collecting guidance lines until we hit a stopping point
                for k in range(j + 1, min(j + 5, len(text_lines))):
                    if k < len(text_lines):
                        continuation_line = text_lines[k].strip()
                        if (continuation_line and 
                            not self.identify_yes_no_patterns(continuation_line) and
                            not re.match(r'^\d+(?:\.\d+)*\s', continuation_line) and
                            not continuation_line.lower().startswith('guidance:')):
                            guidance_lines.append(continuation_line)
                        else:
                            break
                break
            
            # Or if it's indented (common for guidance)
            elif next_line.startswith('    ') or next_line.startswith('\t'):
                guidance_lines.append(next_line.strip())
        
        # Join and clean up guidance
        if guidance_lines:
            full_guidance = ' '.join(guidance_lines)
            # Clean up extra spaces and formatting
            full_guidance = re.sub(r'\s+', ' ', full_guidance)
            return full_guidance.strip()
        
        return ""
    
    def process_yes_no_clauses(self, page_data):
        """Process each page to find and extract Yes/No clauses with improved structure"""
        for page_info in page_data:
            page_num = page_info['page']
            text = page_info['text']
            
            # Process line by line for NADCAP format
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                if self.identify_yes_no_patterns(line):
                    # Found a line with YES/NO pattern
                    
                    # Find section information
                    section_num, section_title = self.find_section_info(text, i)
                    
                    # Extract specific clause number (if any)
                    specific_clause = self.extract_specific_clause_number(lines, i)
                    
                    # Remove YES/NO pattern from the content
                    content = re.sub(r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\s*$', '', line).strip()
                    
                    # If content is empty or very short, look for content in previous lines
                    if len(content) < 10:
                        content_lines = []
                        # Look back up to 3 lines for the main content
                        for j in range(max(0, i-3), i+1):
                            if j < len(lines):
                                line_content = re.sub(r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\s*$', '', lines[j]).strip()
                                if line_content and not re.match(r'^\d+(?:\.\d+)*\s*$', line_content):  # Skip standalone numbers
                                    content_lines.append(line_content)
                        content = ' '.join(content_lines).strip()
                    
                    # Clean up content - remove any clause numbers from the beginning
                    content = re.sub(r'^\d+(?:\.\d+)*\s*', '', content)
                    content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                    
                    # Extract full guidance text
                    guidance = self.extract_full_guidance(lines, i)
                    
                    # Determine response type
                    response_type = "yes_no_na" if re.search(r'\b(?:NA|N/A)\b', line, re.IGNORECASE) else "yes_no"
                    
                    # Only add if we have meaningful content
                    if content and len(content) > 5:
                        clause_data = {
                            "page_number": page_num,
                            "section": section_num,
                            "section_title": section_title,
                            "clause": specific_clause if specific_clause else "",  # Empty if no specific clause
                            "content": content,
                            "guidance": guidance,
                            "response_type": response_type
                        }
                        
                        self.extracted_clauses.append(clause_data)
                        clause_display = specific_clause if specific_clause else f"Section {section_num}"
                        print(f"Found Yes/No clause: {clause_display} on page {page_num} - {content[:50]}...")
    
    def save_to_csv(self, output_path):
        """Save extracted clauses to CSV format with improved structure"""
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Page', 'Section', 'Section_Title', 'Clause', 'Content/Question', 'Guidance', 'Yes', 'No', 'NA']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for clause in self.extracted_clauses:
                row = {
                    'Page': clause['page_number'],
                    'Section': clause['section'],
                    'Section_Title': clause['section_title'],
                    'Clause': clause['clause'],
                    'Content/Question': clause['content'],
                    'Guidance': clause['guidance'],
                    'Yes': '',  # Empty for user to fill
                    'No': '',   # Empty for user to fill
                    'NA': '' if clause['response_type'] == 'yes_no' else ''  # Only show if NA is applicable
                }
                writer.writerow(row)
        
        print(f"CSV file saved: {output_path}")
    
    def save_to_json(self, output_path):
        """Save extracted clauses to JSON format"""
        self.document_info['total_clauses_extracted'] = len(self.extracted_clauses)
        
        output_data = {
            "document_info": self.document_info,
            "clauses": self.extracted_clauses
        }
        
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"JSON file saved: {output_path}")
    
    def generate_summary_report(self, output_path):
        """Generate a summary report of the extraction"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# NADCAP Yes/No Clause Extraction Summary\n\n")
            f.write(f"**Extraction Date:** {self.document_info['extraction_date']}\n")
            f.write(f"**Source Document:** {os.path.basename(self.pdf_path)}\n")
            f.write(f"**Total Clauses Extracted:** {len(self.extracted_clauses)}\n\n")
            
            yes_no_count = sum(1 for c in self.extracted_clauses if c['response_type'] == 'yes_no')
            yes_no_na_count = sum(1 for c in self.extracted_clauses if c['response_type'] == 'yes_no_na')
            
            f.write("## Clause Breakdown\n")
            f.write(f"- Yes/No clauses: {yes_no_count}\n")
            f.write(f"- Yes/No/NA clauses: {yes_no_na_count}\n\n")
            
            f.write("## Extracted Clauses Preview\n")
            for i, clause in enumerate(self.extracted_clauses[:10]):  # Show first 10
                clause_display = clause['clause'] if clause['clause'] else f"Section {clause['section']}"
                f.write(f"### {clause_display}\n")
                f.write(f"**Section:** {clause['section']} - {clause['section_title']}\n")
                f.write(f"**Content:** {clause['content'][:100]}...\n")
                if clause['guidance']:
                    f.write(f"**Guidance:** {clause['guidance'][:150]}...\n")
                f.write(f"**Response Type:** {clause['response_type']}\n")
                f.write(f"**Page:** {clause['page_number']}\n\n")
        
        print(f"Summary report saved: {output_path}")
    
    def extract_all(self):
        """Main extraction method"""
        print("Starting NADCAP Yes/No Clause Extraction...")
        print("=" * 60)
        
        # Extract text from PDF
        page_data = self.extract_text_from_pdf()
        if not page_data:
            print("Failed to extract text from PDF")
            return False
        
        # Process Yes/No clauses
        print("\nSearching for Yes/No clauses...")
        self.process_yes_no_clauses(page_data)
        
        if not self.extracted_clauses:
            print("No Yes/No clauses found in the document.")
            return False
        
        print(f"\nFound {len(self.extracted_clauses)} Yes/No clauses")
        
        # Generate output files - save to outputs folder with timestamps
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Define outputs directory
        outputs_dir = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis/outputs"
        
        # Ensure outputs directory exists
        os.makedirs(outputs_dir, exist_ok=True)
        
        csv_path = os.path.join(outputs_dir, f"{base_name}_yes_no_clauses_{timestamp}.csv")
        json_path = os.path.join(outputs_dir, f"{base_name}_clauses_structured_{timestamp}.json")
        summary_path = os.path.join(outputs_dir, f"{base_name}_extraction_summary_{timestamp}.md")
        
        self.save_to_csv(csv_path)
        self.save_to_json(json_path)
        self.generate_summary_report(summary_path)
        
        print("\n" + "=" * 60)
        print("Extraction Complete!")
        print(f"Files generated:")
        print(f"  1. {csv_path} - Ready for compliance tracking")
        print(f"  2. {json_path} - Structured data for analysis")
        print(f"  3. {summary_path} - Extraction summary report")
        print("\nNext steps:")
        print("  1. Review the CSV file for accuracy")
        print("  2. Load your SF documentation inventory (MFG.xlsx)")
        print("  3. Perform gap analysis against extracted clauses")
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_nadcap_yes_no_clauses.py <pdf_file_path>")
        print("Example: python extract_nadcap_yes_no_clauses.py NADCAP_Requirements.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    extractor = NADCAPYesNoExtractor(pdf_path)
    success = extractor.extract_all()
    
    if not success:
        print("Extraction failed. Please check the PDF file and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
