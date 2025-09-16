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
        self.document_structure = None
        self.document_info = {
            "title": "NADCAP Audit Requirements",
            "version": "Unknown",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "total_clauses_extracted": 0
        }
        
        # Global context tracking for section/subsection across pages
        self.current_section = None
        self.current_subsection = None
        
        # Load the document structure map
        self.load_document_structure()
    
    def load_document_structure(self):
        """Load the pre-mapped document structure."""
        structure_file = '/workspaces/control_tower/corrected_nadcap_structure.json'
        
        try:
            with open(structure_file, 'r') as f:
                self.document_structure = json.load(f)
            print(f"Loaded document structure with {len(self.document_structure['sections'])} sections")
            return True
        except FileNotFoundError:
            print(f"Structure file not found: {structure_file}")
            return False
        except Exception as e:
            print(f"Error loading structure file: {str(e)}")
            return False
    
    def update_global_context(self, lines):
        """Update global section/subsection context based on page content"""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for main section headers (e.g., "3. GENERAL QUALITY SYSTEM")
            section_match = re.match(r'^(\d+)\.\s+([A-Z][A-Z\s&,\-\(\)]+)$', line)
            if section_match:
                self.current_section = (section_match.group(1), section_match.group(2))
                # Reset subsection when we enter a new section
                self.current_subsection = None
                continue
            
            # Look for subsection headers (e.g., "3.6 Job Documentation")
            subsection_match = re.match(r'^(\d+\.\d+)\s+([A-Z][^,\n]+?)(?:\s*$|:)', line)
            if subsection_match:
                subsection_num = subsection_match.group(1)
                subsection_title = subsection_match.group(2).strip()
                self.current_subsection = (subsection_num, subsection_title)
                
                # Update section from subsection if we don't have one
                if self.current_section is None:
                    section_parts = subsection_num.split('.')
                    if len(section_parts) >= 1:
                        section_from_subsection = section_parts[0]
                        if (self.document_structure and 
                            section_from_subsection in self.document_structure['sections']):
                            section_info = self.document_structure['sections'][section_from_subsection]
                            self.current_section = (section_from_subsection, section_info['title'])
    
    def find_clause_number_near_line(self, lines, line_index):
        """Find specific clause number near the given line"""
        # Look around the current line for clause patterns
        for i in range(max(0, line_index - 3), min(len(lines), line_index + 2)):
            line = lines[i].strip()
            clause_match = re.search(r'^(\d+\.\d+\.\d+(?:\.\d+)*)', line)
            if clause_match:
                return clause_match.group(1)
        return ""
    
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
    
    def find_hierarchical_section_info(self, page_text, current_line_index):
        """Find the section, subsection, and clause hierarchy by maintaining proper context"""
        lines = page_text.split('\n')
        
        # Initialize with unknown values
        section_num = "Unknown"
        section_title = "Unknown Section"
        subsection_num = ""
        subsection_title = ""
        clause_num = ""
        
        # Track section and subsection context throughout the page
        page_section = None
        page_subsection = None
        
        # First pass: scan the entire page to understand the structure
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Look for main section headers (e.g., "3. GENERAL QUALITY SYSTEM")
            section_match = re.match(r'^(\d+)\.\s+([A-Z][A-Z\s&,\-\(\)]+)$', line)
            if section_match:
                page_section = (section_match.group(1), section_match.group(2))
                continue
            
            # Look for subsection headers (e.g., "3.6 Job Documentation")
            subsection_match = re.match(r'^(\d+\.\d+)\s+([A-Z][^,\n]+?)(?:\s*$|:)', line)
            if subsection_match:
                subsection_num_found = subsection_match.group(1)
                subsection_title_found = subsection_match.group(2).strip()
                
                # If this subsection appears before our target line, use it
                if i <= current_line_index:
                    page_subsection = (subsection_num_found, subsection_title_found)
                    
                    # Update section based on subsection if we don't have a page section
                    if page_section is None:
                        section_parts = subsection_num_found.split('.')
                        if len(section_parts) >= 1:
                            section_from_subsection = section_parts[0]
                            # Get section title from our structure map
                            if (self.document_structure and 
                                section_from_subsection in self.document_structure['sections']):
                                section_info = self.document_structure['sections'][section_from_subsection]
                                page_section = (section_from_subsection, section_info['title'])
        
        # Set the found section and subsection
        if page_section:
            section_num, section_title = page_section
        if page_subsection:
            subsection_num, subsection_title = page_subsection
        
        # Second pass: look for specific clause numbers near the current line
        for i in range(max(0, current_line_index - 5), min(len(lines), current_line_index + 3)):
            line = lines[i].strip() if i < len(lines) else ""
            
            # Look for detailed clause patterns (e.g., "3.6.1.5.1")
            clause_pattern = r'^(\d+\.\d+\.\d+(?:\.\d+)*)'
            clause_match = re.search(clause_pattern, line)
            if clause_match:
                found_clause = clause_match.group(1)
                
                # Use the clause closest to our target line
                if abs(i - current_line_index) <= 2:
                    clause_num = found_clause
                    
                    # Update section/subsection from clause if needed
                    clause_parts = found_clause.split('.')
                    if len(clause_parts) >= 2:
                        clause_section = clause_parts[0]
                        clause_subsection = f"{clause_parts[0]}.{clause_parts[1]}"
                        
                        # Update section if it matches the clause
                        if (self.document_structure and 
                            clause_section in self.document_structure['sections']):
                            section_num = clause_section
                            section_title = self.document_structure['sections'][clause_section]['title']
                        
                        # Update subsection if it matches the clause
                        if (self.document_structure and 
                            clause_subsection in self.document_structure['subsections']):
                            subsection_num = clause_subsection
                            subsection_title = self.document_structure['subsections'][clause_subsection]['title']
                    break
        
        return {
            'section_num': section_num,
            'section_title': section_title,
            'subsection_num': subsection_num,
            'subsection_title': subsection_title,
            'clause_num': clause_num
        }
    
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
        """Process each page to find and extract Yes/No clauses with global context tracking"""
        for page_info in page_data:
            page_num = page_info['page']
            text = page_info['text']
            
            # Process line by line for NADCAP format
            lines = text.split('\n')
            
            # First update global context based on this page's headers
            self.update_global_context(lines)
            
            for i, line in enumerate(lines):
                if self.identify_yes_no_patterns(line):
                    # Found a line with YES/NO pattern
                    
                    # Use global context as primary source
                    section_num = self.current_section[0] if self.current_section else "Unknown"
                    section_title = self.current_section[1] if self.current_section else "Unknown Section"
                    subsection_num = self.current_subsection[0] if self.current_subsection else ""
                    subsection_title = self.current_subsection[1] if self.current_subsection else ""
                    
                    # Look for specific clause numbers near this line
                    clause_num = self.find_clause_number_near_line(lines, i)
                    
                    # If we have a clause number, we can refine the context
                    if clause_num and self.document_structure:
                        clause_parts = clause_num.split('.')
                        if len(clause_parts) >= 2:
                            potential_section = clause_parts[0]
                            potential_subsection = f"{clause_parts[0]}.{clause_parts[1]}"
                            
                            # Override with clause-derived info if available
                            if potential_section in self.document_structure['sections']:
                                section_num = potential_section
                                section_title = self.document_structure['sections'][potential_section]['title']
                            
                            if potential_subsection in self.document_structure.get('subsections', {}):
                                subsection_num = potential_subsection
                                subsection_title = self.document_structure['subsections'][potential_subsection]['title']
                    
                    # Remove YES/NO pattern from the content and clean up
                    content = re.sub(r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\s*$', '', line).strip()
                    
                    # The content often spans multiple lines in PDF. Look backwards to get the complete question
                    content_lines = []
                    
                    # Look backwards to find the complete question text
                    question_started = False
                    for j in range(i, max(0, i-15), -1):  # Look back up to 15 lines
                        if j < len(lines):
                            check_line = lines[j].strip()
                            
                            # Skip empty lines
                            if not check_line:
                                continue
                                
                            # Stop if we hit another YES/NO pattern (previous clause) 
                            if j != i and self.identify_yes_no_patterns(check_line):
                                break
                                
                            # Stop if we hit structural elements
                            if (re.match(r'^\d+\.\s+[A-Z]', check_line) or  # Section headers
                                re.match(r'^\d+\.\d+\s+[A-Z]', check_line) or  # Subsection headers
                                'Nadcap AC7108' in check_line or  # Page headers
                                check_line.lower().startswith('guidance:') or
                                re.match(r'^[-=]+$', check_line)):  # Separator lines
                                break
                            
                            # Clean the line of any embedded YES/NO patterns
                            clean_line = re.sub(r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\s*$', '', check_line).strip()
                            
                            # Skip lines that are just clause numbers
                            if re.match(r'^\d+(?:\.\d+)*\s*$', clean_line):
                                continue
                                
                            # Add meaningful content lines
                            if (clean_line and 
                                len(clean_line) > 5 and
                                not re.match(r'^[A-Z\s]+$', clean_line)):  # Skip all-caps headers
                                content_lines.insert(0, clean_line)
                                question_started = True
                            elif question_started:
                                # If we've started collecting question text and hit an empty meaningful line, stop
                                break
                    
                    # Reconstruct the complete content
                    content = ' '.join(content_lines).strip()
                    
                    # Clean up content - remove any clause numbers from the beginning
                    content = re.sub(r'^\d+(?:\.\d+)*\s*', '', content)
                    content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                    
                    # Remove any remaining YES/NO patterns that might be embedded
                    content = re.sub(r'\s+(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\s*', '', content)
                    content = content.strip()
                    
                    # Final cleanup - ensure question starts properly
                    content = re.sub(r'^[^\w]*', '', content)  # Remove leading non-word characters
                    
                    # Skip if content is still too short or contains obvious formatting artifacts
                    if len(content) < 10 or content.lower() in ['yes no', 'yes no na']:
                        continue
                    
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
                            "subsection": subsection_num,
                            "subsection_title": subsection_title,
                            "clause": clause_num if clause_num else "",  # Empty if no specific clause
                            "content": content,
                            "guidance": guidance,
                            "response_type": response_type
                        }
                        
                        self.extracted_clauses.append(clause_data)
                        clause_display = clause_num if clause_num else f"Section {section_num}"
                        print(f"Found Yes/No clause: {clause_display} on page {page_num} - {content[:50]}...")
    
    def save_to_csv(self, output_path):
        """Save extracted clauses to CSV format with hierarchical structure"""
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Page', 'Section', 'Section_Title', 'Subsection', 'Subsection_Title', 'Clause', 'Content/Question', 'Guidance', 'Notes', 'Yes', 'No', 'NA']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for clause in self.extracted_clauses:
                row = {
                    'Page': clause['page_number'],
                    'Section': clause['section'],
                    'Section_Title': clause['section_title'],
                    'Subsection': clause.get('subsection', ''),
                    'Subsection_Title': clause.get('subsection_title', ''),
                    'Clause': clause['clause'],
                    'Content/Question': clause['content'],
                    'Guidance': clause['guidance'],
                    'Notes': '',  # Empty for user to fill
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
