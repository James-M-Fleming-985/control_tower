#!/usr/bin/env python3
"""
Enhanced NADCAP Clause Extraction Tool - Phase 1A
PyMuPDF-based extraction with improved accuracy for stakeholder deliverables

This tool provides enhanced extraction capabilities using PyMuPDF for better
handling of complex PDF structures and hierarchical content.
"""

import sys
import os
import re
import csv
import json
from datetime import datetime
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not found. Installing...")
    os.system("pip install PyMuPDF")
    import fitz

class EnhancedNADCAPExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.extracted_clauses = []
        self.document_structure = None
        self.document_info = {
            "title": "NADCAP Audit Requirements",
            "version": "Enhanced PyMuPDF Extraction",
            "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_clauses_extracted": 0,
            "extraction_method": "PyMuPDF Enhanced"
        }
        
        # Enhanced context tracking
        self.current_section = None
        self.current_subsection = None
        self.section_hierarchy = {}
        
        # Load document structure if available
        self.load_document_structure()
    
    def load_document_structure(self):
        """Load the document structure map if available."""
        structure_file = '/workspaces/control_tower/corrected_nadcap_structure.json'
        
        try:
            with open(structure_file, 'r') as f:
                self.document_structure = json.load(f)
            print(f"✓ Loaded document structure with {len(self.document_structure['sections'])} sections")
        except FileNotFoundError:
            print("⚠ Document structure file not found, using pattern detection")
            self.document_structure = None
    
    def analyze_document_structure(self, doc):
        """Analyze the document to build section hierarchy."""
        print("Analyzing document structure...")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get text blocks with position information
            blocks = page.get_text("blocks")
            
            for block in blocks:
                if block[6] == 0:  # Text block (not image)
                    text = block[4].strip()
                    
                    # Look for section headers (larger font, specific patterns)
                    section_pattern = r'^(\d+)\s+([A-Z][A-Z\s&]+)$'
                    subsection_pattern = r'^(\d+\.\d+)\s+([A-Z][A-Za-z\s&]+)$'
                    
                    section_match = re.match(section_pattern, text)
                    subsection_match = re.match(subsection_pattern, text)
                    
                    if section_match:
                        section_num = section_match.group(1)
                        section_title = section_match.group(2).strip()
                        self.section_hierarchy[section_num] = {
                            'title': section_title,
                            'page': page_num + 1,
                            'subsections': {}
                        }
                        print(f"  Found section {section_num}: {section_title}")
                    
                    elif subsection_match:
                        subsection_num = subsection_match.group(1)
                        subsection_title = subsection_match.group(2).strip()
                        section_num = subsection_num.split('.')[0]
                        
                        if section_num in self.section_hierarchy:
                            self.section_hierarchy[section_num]['subsections'][subsection_num] = {
                                'title': subsection_title,
                                'page': page_num + 1
                            }
                            print(f"    Found subsection {subsection_num}: {subsection_title}")
    
    def identify_yes_no_patterns(self, text):
        """Enhanced Yes/No pattern detection."""
        yes_no_patterns = [
            r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\b',
            r'\b(?:Yes|YES)\s*/\s*(?:No|NO)(?:\s*/\s*(?:NA|N/A))?\b',
            r'\[\s*\]\s*(?:YES|Yes)\s+\[\s*\]\s*(?:NO|No)(?:\s+\[\s*\]\s*(?:NA|N/A))?',
            r'(?:YES|Yes)\s*\|\s*(?:NO|No)(?:\s*\|\s*(?:NA|N/A))?',
            r'☐\s*(?:YES|Yes)\s+☐\s*(?:NO|No)(?:\s+☐\s*(?:NA|N/A))?'
        ]
        
        for pattern in yes_no_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def extract_clause_context(self, page, block_index, blocks):
        """Extract context for a clause including section/subsection info with improved accuracy."""
        # Get current page number
        page_num = page.number + 1
        
        # Initialize context
        section_num = ""
        section_title = ""
        subsection_num = ""
        subsection_title = ""
        clause_num = ""
        
        # Get all text from current page for better context analysis
        page_text = page.get_text()
        lines = page_text.split('\n')
        
        # Find current block position in page text to establish context
        current_block_text = blocks[block_index][4].strip()
        current_line_index = -1
        
        for i, line in enumerate(lines):
            if current_block_text[:30] in line or line[:30] in current_block_text:
                current_line_index = i
                break
        
        if current_line_index == -1:
            current_line_index = len(lines) // 2  # Default to middle if not found
        
        # Look backward from current position to find section context
        for i in range(current_line_index, max(0, current_line_index - 50), -1):
            line = lines[i].strip()
            
            # Look for main section headers (e.g., "3 GENERAL QUALITY SYSTEM")
            main_section_pattern = r'^(\d+)\s+([A-Z][A-Z\s&/,()-]+)$'
            main_section_match = re.match(main_section_pattern, line)
            if main_section_match and not section_num:
                section_num = main_section_match.group(1)
                section_title = main_section_match.group(2).strip()
            
            # Look for subsection headers (e.g., "3.3 Continuous Process Improvement")
            subsection_pattern = r'^(\d+\.\d+)\s+([A-Z][A-Za-z\s&/,()-]+)$'
            subsection_match = re.match(subsection_pattern, line)
            if subsection_match and not subsection_num:
                subsection_num = subsection_match.group(1)
                subsection_title = subsection_match.group(2).strip()
                # Extract section from subsection if not found
                if not section_num:
                    section_num = subsection_num.split('.')[0]
            
            # Look for specific clause numbers
            clause_pattern = r'^(\d+\.\d+\.\d+(?:\.\d+)*)\s*'
            clause_match = re.match(clause_pattern, line)
            if clause_match and not clause_num:
                clause_num = clause_match.group(1)
                # Extract section and subsection from clause if not found
                parts = clause_num.split('.')
                if not section_num and len(parts) >= 1:
                    section_num = parts[0]
                if not subsection_num and len(parts) >= 2:
                    subsection_num = f"{parts[0]}.{parts[1]}"
        
        # Use document structure if available to fill in titles
        if self.document_structure:
            if section_num in self.document_structure.get('sections', {}):
                section_title = self.document_structure['sections'][section_num].get('title', section_title)
            if subsection_num in self.document_structure.get('subsections', {}):
                subsection_title = self.document_structure['subsections'][subsection_num].get('title', subsection_title)
        
        # Use built hierarchy as fallback
        elif section_num in self.section_hierarchy:
            if not section_title:
                section_title = self.section_hierarchy[section_num]['title']
            if subsection_num in self.section_hierarchy[section_num].get('subsections', {}):
                if not subsection_title:
                    subsection_title = self.section_hierarchy[section_num]['subsections'][subsection_num]['title']
        
        return {
            'page_number': page_num,
            'section': section_num,
            'section_title': section_title,
            'subsection': subsection_num,
            'subsection_title': subsection_title,
            'clause': clause_num
        }
    
    def extract_complete_content(self, page, block_index, blocks):
        """Extract complete content for a clause with full question, guidance, and notes."""
        content_lines = []
        guidance_lines = []
        notes_lines = []
        
        # Get full page text for better context
        page_text = page.get_text()
        lines = page_text.split('\n')
        
        # Start with current block
        current_block = blocks[block_index]
        current_text = current_block[4].strip()
        
        # Find position in page text
        current_line_index = -1
        for i, line in enumerate(lines):
            if current_text[:30] in line or line[:30] in current_text:
                current_line_index = i
                break
        
        if current_line_index == -1:
            # Fallback: use block text directly
            content_text = re.sub(r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\b', '', current_text)
            content_text = re.sub(r'\[\s*\]\s*(?:YES|Yes)\s+\[\s*\]\s*(?:NO|No)(?:\s+\[\s*\]\s*(?:NA|N/A))?', '', content_text)
            content_lines.append(content_text.strip())
        else:
            # Extract complete question starting from current line
            collecting_content = True
            collecting_guidance = False
            collecting_notes = False
            
            # Process lines starting from current position
            for i in range(current_line_index, min(len(lines), current_line_index + 15)):
                line = lines[i].strip()
                if not line:
                    continue
                
                # Check if we hit another YES/NO pattern (end of current clause)
                if i > current_line_index and self.identify_yes_no_patterns(line):
                    break
                
                # Check if we hit a new clause or section
                if i > current_line_index and re.match(r'^\d+(?:\.\d+)*\s+[A-Z]', line):
                    break
                
                # Check for guidance indicators
                if re.search(r'\bGuidance\s*:', line, re.IGNORECASE):
                    collecting_content = False
                    collecting_guidance = True
                    collecting_notes = False
                    guidance_lines.append(re.sub(r'^.*?Guidance\s*:\s*', '', line, flags=re.IGNORECASE))
                    continue
                
                # Check for notes indicators
                if re.search(r'\bNOTE\s*:', line, re.IGNORECASE):
                    collecting_content = False
                    collecting_guidance = False
                    collecting_notes = True
                    notes_lines.append(re.sub(r'^.*?NOTE\s*:\s*', '', line, flags=re.IGNORECASE))
                    continue
                
                # Collect based on current mode
                if collecting_content:
                    # Remove YES/NO patterns from content
                    clean_line = re.sub(r'\b(?:YES|Yes)\s+(?:NO|No)(?:\s+(?:NA|N/A))?\b', '', line)
                    clean_line = re.sub(r'\[\s*\]\s*(?:YES|Yes)\s+\[\s*\]\s*(?:NO|No)(?:\s+\[\s*\]\s*(?:NA|N/A))?', '', clean_line)
                    clean_line = clean_line.strip()
                    if clean_line and len(clean_line) > 2:
                        content_lines.append(clean_line)
                elif collecting_guidance:
                    guidance_lines.append(line)
                elif collecting_notes:
                    notes_lines.append(line)
        
        # Reconstruct content
        content = ' '.join(content_lines).strip()
        guidance = ' '.join(guidance_lines).strip()
        notes = ' '.join(notes_lines).strip()
        
        # Clean up content - remove leading clause numbers
        content = re.sub(r'^\d+(?:\.\d+)*\s*', '', content)
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        content = content.strip()
        
        # Clean up guidance and notes
        guidance = re.sub(r'\s+', ' ', guidance).strip()
        notes = re.sub(r'\s+', ' ', notes).strip()
        
        # Determine response type
        response_type = "yes_no_na" if re.search(r'\b(?:NA|N/A)\b', current_text, re.IGNORECASE) else "yes_no"
        
        return content, guidance, notes, response_type
    
    def extract_clauses(self):
        """Main extraction method using PyMuPDF."""
        print(f"Opening PDF: {self.pdf_path}")
        
        try:
            doc = fitz.open(self.pdf_path)
            print(f"✓ Successfully opened PDF with {len(doc)} pages")
        except Exception as e:
            print(f"✗ Error opening PDF: {e}")
            return False
        
        # First pass: analyze document structure
        self.analyze_document_structure(doc)
        
        print("\nExtracting Yes/No clauses...")
        
        # Second pass: extract clauses
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            
            for block_index, block in enumerate(blocks):
                if block[6] == 0:  # Text block
                    text = block[4].strip()
                    
                    # Check if this block contains Yes/No patterns
                    if self.identify_yes_no_patterns(text):
                        # Extract context
                        context = self.extract_clause_context(page, block_index, blocks)
                        
                        # Extract complete content including guidance and notes
                        content, guidance, notes, response_type = self.extract_complete_content(page, block_index, blocks)
                        
                        # Only add if we have meaningful content
                        if content and len(content) > 10:
                            clause_data = {
                                "page_number": context['page_number'],
                                "section": context['section'],
                                "section_title": context['section_title'],
                                "subsection": context['subsection'],
                                "subsection_title": context['subsection_title'],
                                "clause": context['clause'],
                                "content": content,
                                "guidance": guidance,
                                "notes": notes,
                                "response_type": response_type
                            }
                            
                            self.extracted_clauses.append(clause_data)
                            
                            # Display progress
                            clause_display = context['clause'] if context['clause'] else f"Section {context['section']}"
                            if not clause_display or clause_display == "Section ":
                                clause_display = f"Page {context['page_number']}"
                            print(f"  ✓ Found: {clause_display} - {content[:60]}...")
        
        doc.close()
        print(f"\n✓ Extraction complete: {len(self.extracted_clauses)} clauses found")
        return True
    
    def save_to_csv(self, output_path):
        """Save extracted clauses to CSV format with complete accuracy."""
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Enhanced headers with proper Yes/No/NA columns
            fieldnames = ['Page', 'Section', 'Section_Title', 'Subsection', 'Subsection_Title', 'Clause', 'Content/Question', 'Guidance', 'Notes', 'Yes', 'No', 'NA']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for clause in self.extracted_clauses:
                row = {
                    'Page': clause['page_number'],
                    'Section': clause.get('section', ''),
                    'Section_Title': clause.get('section_title', ''),
                    'Subsection': clause.get('subsection', ''),
                    'Subsection_Title': clause.get('subsection_title', ''),
                    'Clause': clause.get('clause', ''),
                    'Content/Question': clause['content'],
                    'Guidance': clause.get('guidance', ''),
                    'Notes': clause.get('notes', ''),
                    'Yes': '',  # Empty for user to populate
                    'No': '',   # Empty for user to populate
                    'NA': '' if clause['response_type'] == 'yes_no' else ''  # Show NA column if applicable
                }
                writer.writerow(row)
        
        print(f"✓ CSV file saved: {output_path}")
    
    def save_to_json(self, output_path):
        """Save extracted clauses to JSON format."""
        self.document_info['total_clauses_extracted'] = len(self.extracted_clauses)
        
        output_data = {
            "document_info": self.document_info,
            "clauses": self.extracted_clauses,
            "section_hierarchy": self.section_hierarchy
        }
        
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON file saved: {output_path}")
    
    def generate_summary_report(self, output_path):
        """Generate enhanced summary report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Enhanced NADCAP Clause Extraction Summary - Phase 1A\n\n")
            f.write(f"**Extraction Date:** {self.document_info['extraction_date']}\n")
            f.write(f"**Source Document:** {os.path.basename(self.pdf_path)}\n")
            f.write(f"**Extraction Method:** {self.document_info['extraction_method']}\n")
            f.write(f"**Total Clauses Extracted:** {len(self.extracted_clauses)}\n\n")
            
            # Statistics
            yes_no_count = sum(1 for c in self.extracted_clauses if c['response_type'] == 'yes_no')
            yes_no_na_count = sum(1 for c in self.extracted_clauses if c['response_type'] == 'yes_no_na')
            
            f.write("## Extraction Statistics\n")
            f.write(f"- Yes/No clauses: {yes_no_count}\n")
            f.write(f"- Yes/No/NA clauses: {yes_no_na_count}\n")
            f.write(f"- Sections identified: {len(self.section_hierarchy)}\n\n")
            
            # Section breakdown
            f.write("## Section Breakdown\n")
            section_counts = {}
            for clause in self.extracted_clauses:
                section = clause['section']
                section_counts[section] = section_counts.get(section, 0) + 1
            
            for section, count in sorted(section_counts.items()):
                section_title = self.section_hierarchy.get(section, {}).get('title', 'Unknown')
                f.write(f"- Section {section} ({section_title}): {count} clauses\n")
            
            f.write("\n## Ready for Phase 1A Analysis\n")
            f.write("This extraction is optimized for immediate stakeholder deliverables and keyword matching analysis.\n")
        
        print(f"✓ Summary report saved: {output_path}")
    
    def extract_all(self):
        """Main extraction workflow for Phase 1A deliverables."""
        print("=" * 60)
        print("Enhanced NADCAP Extraction Tool - Phase 1A")
        print("=" * 60)
        
        # Perform extraction
        if not self.extract_clauses():
            return False
        
        if not self.extracted_clauses:
            print("⚠ No Yes/No clauses found in the document")
            return False
        
        # Generate output files
        base_name = Path(self.pdf_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        outputs_dir = Path(__file__).parent.parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        csv_path = outputs_dir / f"{base_name}_enhanced_extraction_{timestamp}.csv"
        json_path = outputs_dir / f"{base_name}_enhanced_extraction_{timestamp}.json"
        summary_path = outputs_dir / f"{base_name}_enhanced_summary_{timestamp}.md"
        
        self.save_to_csv(csv_path)
        self.save_to_json(json_path)
        self.generate_summary_report(summary_path)
        
        print("\n" + "=" * 60)
        print("Phase 1A Extraction Complete!")
        print("=" * 60)
        print("Files generated:")
        print(f"  1. {csv_path}")
        print(f"  2. {json_path}")
        print(f"  3. {summary_path}")
        print("\nNext Phase 1A Steps:")
        print("  1. Review extraction accuracy")
        print("  2. Select priority SF documents (10-15)")
        print("  3. Run enhanced keyword matching analysis")
        print("  4. Generate stakeholder presentation")
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python enhanced_nadcap_extractor.py <pdf_file_path>")
        print("Example: python enhanced_nadcap_extractor.py NADCAP_Requirements.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    extractor = EnhancedNADCAPExtractor(pdf_path)
    success = extractor.extract_all()
    
    if not success:
        print("Extraction failed. Please check the PDF file and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
