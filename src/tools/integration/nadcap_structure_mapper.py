#!/usr/bin/env python3
"""
NADCAP Document Structure Mapper
Pre-extraction step to map the hierarchical structure of NADCAP documents
"""

import sys
import os
import re
import json
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    print("pdfplumber not found. Installing...")
    os.system("pip install pdfplumber")
    import pdfplumber

class NADCAPStructureMapper:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.document_structure = {
            "sections": {},
            "subsections": {},
            "extraction_date": datetime.now().strftime("%Y-%m-%d")
        }
    
    def extract_text_from_pdf(self):
        """Extract all text from PDF with page markers"""
        full_text = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"Mapping structure of PDF: {self.pdf_path}")
                print(f"Total pages: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"Analyzing page {page_num}...")
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
    
    def find_main_sections(self, page_data):
        """Find main sections (2, 3, 4, 5, etc.) and their titles"""
        print("\n=== MAPPING MAIN SECTIONS ===")
        
        for page_info in page_data:
            page_num = page_info['page']
            text = page_info['text']
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for main section patterns like "2. INSTRUCTIONS TO AUDITEE"
                main_section_patterns = [
                    r'^(\d+)\.\s+([A-Z][A-Z\s]+[A-Z])$',  # "3. GENERAL QUALITY SYSTEM"
                    r'^(\d+)\s+([A-Z][A-Z\s]+[A-Z])$',    # "3 GENERAL QUALITY SYSTEM"
                ]
                
                for pattern in main_section_patterns:
                    match = re.search(pattern, line)
                    if match and len(match.group(2)) > 5:  # Ensure meaningful title
                        section_num = match.group(1)
                        section_title = match.group(2).strip()
                        
                        # Filter out obvious false positives
                        if not any(word in section_title for word in ['PAGE', 'REVISION', 'DATE', 'AUDIT']):
                            if section_num not in self.document_structure["sections"]:
                                self.document_structure["sections"][section_num] = {
                                    "title": section_title,
                                    "page": page_num,
                                    "subsections": {}
                                }
                                print(f"Found Section {section_num}: {section_title} (Page {page_num})")
    
    def find_subsections(self, page_data):
        """Find subsections like 3.1, 3.3, 3.5, 3.6, etc."""
        print("\n=== MAPPING SUBSECTIONS ===")
        
        for page_info in page_data:
            page_num = page_info['page']
            text = page_info['text']
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for subsection patterns like "3.3 Continuous Process Improvement"
                subsection_patterns = [
                    r'^(\d+\.\d+)\s+([A-Z][^,\n]+?)(?:\s*$|[:\n])',  # "3.6 Job Documentation"
                    r'^(\d+\.\d+)\s+(.+?)(?:\s*$|[:\n])',            # General subsection
                ]
                
                for pattern in subsection_patterns:
                    match = re.search(pattern, line)
                    if match and len(match.group(2)) > 3:
                        subsection_num = match.group(1)
                        subsection_title = match.group(2).strip()
                        
                        # Clean up title
                        subsection_title = re.sub(r'[:\s]*$', '', subsection_title)
                        
                        # Get main section number (e.g., "3" from "3.6")
                        main_section = subsection_num.split('.')[0]
                        
                        # Only add if we have the main section and title looks meaningful
                        if (main_section in self.document_structure["sections"] and 
                            len(subsection_title) > 3 and
                            any(word in subsection_title.upper() for word in 
                                ['DOCUMENTATION', 'TRAINING', 'PERSONNEL', 'QUALITY', 'PROCESS', 
                                 'CONTROL', 'MANAGEMENT', 'INSPECTION', 'TESTING', 'EQUIPMENT', 
                                 'FACILITIES', 'IMPROVEMENT', 'LAYOUT', 'SYSTEM', 'PLANNING',
                                 'EVALUATION', 'QUALIFICATION', 'CONTINUOUS'])):
                            
                            if subsection_num not in self.document_structure["subsections"]:
                                self.document_structure["subsections"][subsection_num] = {
                                    "title": subsection_title,
                                    "page": page_num,
                                    "parent_section": main_section
                                }
                                print(f"Found Subsection {subsection_num}: {subsection_title} (Page {page_num})")
    
    def find_detailed_structure(self, page_data):
        """Find detailed clause patterns to understand the full hierarchy"""
        print("\n=== MAPPING DETAILED CLAUSE PATTERNS ===")
        
        clause_patterns = {}
        
        for page_info in page_data:
            page_num = page_info['page']
            text = page_info['text']
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Look for various clause number patterns
                detailed_patterns = [
                    r'(\d+\.\d+\.\d+\.\d+\.\d+)',  # 3.6.1.5.1
                    r'(\d+\.\d+\.\d+\.\d+)',       # 3.7.3.1
                    r'(\d+\.\d+\.\d+)',            # 2.3.3
                ]
                
                for pattern in detailed_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if match not in clause_patterns:
                            clause_patterns[match] = page_num
        
        print(f"Found {len(clause_patterns)} detailed clause patterns")
        for clause, page in sorted(clause_patterns.items()):
            print(f"  {clause} (Page {page})")
        
        return clause_patterns
    
    def save_structure_map(self, output_path):
        """Save the document structure map to JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.document_structure, f, indent=2, ensure_ascii=False)
        
        print(f"\nStructure map saved: {output_path}")
    
    def print_structure_summary(self):
        """Print a summary of the discovered structure"""
        print("\n" + "="*60)
        print("NADCAP DOCUMENT STRUCTURE SUMMARY")
        print("="*60)
        
        for section_num in sorted(self.document_structure["sections"].keys(), key=int):
            section = self.document_structure["sections"][section_num]
            print(f"\nSection {section_num}: {section['title']} (Page {section['page']})")
            
            # Find subsections for this main section
            for subsection_num in sorted(self.document_structure["subsections"].keys()):
                subsection = self.document_structure["subsections"][subsection_num]
                if subsection["parent_section"] == section_num:
                    print(f"  └── {subsection_num}: {subsection['title']} (Page {subsection['page']})")
    
    def map_structure(self):
        """Main method to map the document structure"""
        print("Starting NADCAP Document Structure Mapping...")
        print("=" * 60)
        
        # Extract text from PDF
        page_data = self.extract_text_from_pdf()
        if not page_data:
            print("Failed to extract text from PDF")
            return False
        
        # Find main sections
        self.find_main_sections(page_data)
        
        # Find subsections
        self.find_subsections(page_data)
        
        # Find detailed clause patterns
        clause_patterns = self.find_detailed_structure(page_data)
        
        # Print summary
        self.print_structure_summary()
        
        # Save structure map
        outputs_dir = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis/outputs"
        os.makedirs(outputs_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        structure_map_path = os.path.join(outputs_dir, f"NADCAP_document_structure_map_{timestamp}.json")
        self.save_structure_map(structure_map_path)
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python nadcap_structure_mapper.py <pdf_file_path>")
        print("Example: python nadcap_structure_mapper.py NADCAP_Requirements.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    mapper = NADCAPStructureMapper(pdf_path)
    success = mapper.map_structure()
    
    if not success:
        print("Structure mapping failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
