#!/usr/bin/env python3
"""
Enhanced Production NADCAP Extractor - Version 2.0
Improved clause number detection for all sections.
"""

import pdfplumber
import json
import re
import sys
import os
from datetime import datetime

class EnhancedProductionNADCAPExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.clauses = []
        self.processed_content = set()
        
        # Global context tracking
        self.current_section = ("", "")  # (number, title)
        self.current_subsection = ("", "")  # (number, title)
        
        # Load section structure
        structure_path = "/workspaces/control_tower/corrected_nadcap_structure.json"
        if os.path.exists(structure_path):
            with open(structure_path, 'r') as f:
                self.section_structure = json.load(f)
        else:
            print(f"Warning: Structure file not found at {structure_path}")
            self.section_structure = {}

    def identify_yes_no_patterns(self, line):
        """Identify lines containing Yes/No patterns with high accuracy."""
        # Convert to uppercase for pattern matching
        line_upper = line.upper()
        
        # Primary patterns - must be uppercase
        primary_patterns = [
            r'\bYES\s+NO\s+NA\b',     # YES NO NA
            r'\bYES\s+NO\b',          # YES NO
            r'\b_YES\s+_NO\s+_NA\b',  # _YES _NO _NA
            r'\b_YES\s+_NO\b'         # _YES _NO
        ]
        
        for pattern in primary_patterns:
            if re.search(pattern, line_upper):
                return True
        
        return False

    def update_global_context(self, lines, current_index):
        """Update global section and subsection context."""
        line = lines[current_index].strip()
        line_upper = line.upper()
        
        # Section detection (exact match from structure)
        for section_key, section_data in self.section_structure.items():
            if section_key.startswith('section_'):
                section_title = section_data.get('title', '').upper()
                if section_title and section_title in line_upper:
                    section_num = section_key.replace('section_', '')
                    self.current_section = (section_num, section_data.get('title', ''))
                    self.current_subsection = ("", "")  # Reset subsection
                    return
        
        # Subsection detection
        subsection_patterns = [
            r'^([A-Z]\.\s*[A-Z][A-Za-z\s]+)',  # A. Subsection Title
            r'^(\d+\.\d+\s+[A-Z][A-Za-z\s]+)', # 3.1 Subsection Title
            r'^([A-Z][a-z]+\s+[A-Z][A-Za-z\s]+)'  # General Subsection
        ]
        
        for pattern in subsection_patterns:
            match = re.match(pattern, line)
            if match:
                subsection_text = match.group(1).strip()
                if len(subsection_text) > 5:  # Avoid short false positives
                    self.current_subsection = (subsection_text.split()[0], subsection_text)
                break

    def extract_clause_details(self, lines, current_index):
        """Enhanced clause number extraction for all sections."""
        clause_num = ""
        
        # Look in a wider range around current position
        search_range = range(max(0, current_index - 15), min(len(lines), current_index + 8))
        
        for i in search_range:
            line = lines[i].strip()
            
            # Enhanced clause patterns based on section
            current_section_num = self.current_section[0] if self.current_section else ""
            
            if current_section_num == "3":
                # Section 3: Hierarchical patterns like 3.6.1.5.1
                patterns = [
                    r'^(\d+\.\d+\.\d+\.\d+\.\d+)',  # 3.6.1.5.1 at start
                    r'^(\d+\.\d+\.\d+\.\d+)',       # 3.7.3.1 at start
                    r'^(\d+\.\d+\.\d+)',            # 3.6.1 at start
                    r'(\d+\.\d+\.\d+\.\d+\.\d+)',   # Anywhere: 3.6.1.5.1
                    r'(\d+\.\d+\.\d+\.\d+)',        # Anywhere: 3.7.3.1
                    r'(\d+\.\d+\.\d+)'              # Anywhere: 3.6.1
                ]
            elif current_section_num == "4":
                # Section 4: Different patterns - might be letters or simple numbers
                patterns = [
                    r'^([A-Z]\.\d+)',               # A.1, B.2, etc.
                    r'^([A-Z]\.)',                  # A., B., etc.
                    r'^(\d+\.\d+)',                 # 4.1, 4.2, etc.
                    r'^(\d+\.)',                    # 4., 5., etc.
                    r'([A-Z]\.\d+)',                # Anywhere: A.1, B.2
                    r'([A-Z]\.)',                   # Anywhere: A., B.
                    r'(\d+\.\d+)',                  # Anywhere: 4.1, 4.2
                    r'^([a-z]\))',                  # a), b), c)
                    r'([a-z]\))',                   # Anywhere: a), b), c)
                ]
            elif current_section_num == "5":
                # Section 5: Equipment and facilities - might have different patterns
                patterns = [
                    r'^([A-Z]\.\d+)',               # A.1, B.2, etc.
                    r'^([A-Z]\.)',                  # A., B., etc.
                    r'^(\d+\.\d+)',                 # 5.1, 5.2, etc.
                    r'^(\d+\.)',                    # 5., 6., etc.
                    r'([A-Z]\.\d+)',                # Anywhere: A.1, B.2
                    r'([A-Z]\.)',                   # Anywhere: A., B.
                    r'(\d+\.\d+)',                  # Anywhere: 5.1, 5.2
                    r'^([a-z]\))',                  # a), b), c)
                    r'([a-z]\))',                   # Anywhere: a), b), c)
                    r'^\(([a-z])\)',                # (a), (b), (c)
                    r'\(([a-z])\)',                 # Anywhere: (a), (b), (c)
                ]
            else:
                # Default patterns for other sections
                patterns = [
                    r'^(\d+\.\d+\.\d+\.\d+\.\d+)',  # Most specific first
                    r'^(\d+\.\d+\.\d+\.\d+)',
                    r'^(\d+\.\d+\.\d+)',
                    r'^(\d+\.\d+)',
                    r'^([A-Z]\.)',
                    r'^([a-z]\))',
                    r'(\d+\.\d+\.\d+)',
                    r'(\d+\.\d+)',
                    r'([A-Z]\.)',
                    r'([a-z]\))'
                ]
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    potential_clause = match.group(1)
                    
                    # Validation based on section
                    if current_section_num == "3":
                        # Section 3: Require at least 3 levels (x.x.x)
                        if potential_clause.count('.') >= 2:
                            clause_num = potential_clause
                            break
                    elif current_section_num in ["4", "5"]:
                        # Sections 4 & 5: More flexible validation
                        if (len(potential_clause) >= 2 and 
                            (potential_clause.count('.') >= 1 or 
                             potential_clause.endswith('.') or 
                             potential_clause.endswith(')'))):
                            clause_num = potential_clause
                            break
                    else:
                        # Default: Any reasonable pattern
                        if len(potential_clause) >= 2:
                            clause_num = potential_clause
                            break
            
            if clause_num:
                break
        
        # Additional check: Look for clause numbers in the content line itself
        if not clause_num:
            current_line = lines[current_index] if current_index < len(lines) else ""
            
            # Context-aware patterns for current content
            if current_section_num == "4":
                content_patterns = [
                    r'^([A-Z]\.\d*)\s',    # A.1 at start
                    r'^([A-Z]\.)\s',       # A. at start
                    r'^([a-z]\))\s',       # a) at start
                ]
            elif current_section_num == "5":
                content_patterns = [
                    r'^([A-Z]\.\d*)\s',    # A.1 at start
                    r'^([A-Z]\.)\s',       # A. at start
                    r'^([a-z]\))\s',       # a) at start
                    r'^\(([a-z])\)\s',     # (a) at start
                ]
            else:
                content_patterns = [
                    r'^(\d+\.\d+\.\d+)\s',  # 3.6.1 at start
                    r'^(\d+\.\d+)\s',       # 4.1 at start
                ]
            
            for pattern in content_patterns:
                match = re.search(pattern, current_line)
                if match:
                    clause_num = match.group(1)
                    break
        
        return clause_num

    def extract_content_guidance_notes(self, lines, current_index):
        """Extract content, guidance, and notes with improved separation."""
        content = ""
        guidance = ""
        notes = ""
        
        # Get the main content line
        if current_index < len(lines):
            content = lines[current_index].strip()
        
        # Look ahead for guidance and notes (common patterns)
        for i in range(current_index + 1, min(len(lines), current_index + 10)):
            line = lines[i].strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Stop if we hit another Yes/No pattern
            if self.identify_yes_no_patterns(line):
                break
            
            # Guidance indicators
            if any(indicator in line_lower for indicator in ['guidance:', 'note:', 'reference:', 'see also:', 'applicable']):
                if 'guidance:' in line_lower or 'see also:' in line_lower:
                    guidance = line
                else:
                    notes = line
                continue
            
            # If it's a continuation of content (no special indicators)
            if not guidance and not notes and len(line) > 20:
                content += " " + line
        
        # Clean up
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        return content, guidance, notes

    def extract_clauses(self):
        """Main extraction with enhanced clause detection."""
        print(f"Opening PDF: {self.pdf_path}")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            print(f"✓ Successfully opened PDF with {len(pdf.pages)} pages")
            print("\nExtracting Yes/No clauses with enhanced production accuracy...")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"Processing page {page_num}...")
                
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                lines = page_text.split('\n')
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Update global context
                    self.update_global_context(lines, i)
                    
                    # Check for Yes/No patterns
                    if self.identify_yes_no_patterns(line):
                        # Skip Section 2 (INSTRUCTIONS TO AUDITEE) - administrative section
                        current_section_num = self.current_section[0] if self.current_section else ""
                        if current_section_num == "2":
                            print(f"  ⏭ Skipping Section 2 administrative clause on page {page_num}")
                            continue
                        
                        # Extract complete content
                        content, guidance, notes = self.extract_content_guidance_notes(lines, i)
                        
                        # Skip if no meaningful content or duplicate
                        if not content or len(content) < 10:
                            continue
                        
                        content_key = content[:100]  # Use first 100 chars as key
                        if content_key in self.processed_content:
                            continue
                        self.processed_content.add(content_key)
                        
                        # Extract clause details with enhanced detection
                        clause_num = self.extract_clause_details(lines, i)
                        
                        # Determine Yes/No/NA structure
                        line_upper = line.upper()
                        has_na = 'NA' in line_upper
                        
                        clause_data = {
                            'page': page_num,
                            'section': self.current_section[0],
                            'section_title': self.current_section[1],
                            'subsection': self.current_subsection[0],
                            'subsection_title': self.current_subsection[1],
                            'clause': clause_num,
                            'content': content,
                            'guidance': guidance,
                            'notes': notes,
                            'yes': 'Yes',
                            'no': 'No',
                            'na': 'NA' if has_na else ''
                        }
                        
                        self.clauses.append(clause_data)
                        
                        print(f"  ✓ Found clause {clause_num or '[no number]'} in Section {current_section_num} on page {page_num}")
            
            print(f"\n✓ Extraction complete! Found {len(self.clauses)} total clauses")
            
            # Print section summary
            section_counts = {}
            clauses_with_numbers = 0
            for clause in self.clauses:
                section = clause['section']
                section_counts[section] = section_counts.get(section, 0) + 1
                if clause['clause']:
                    clauses_with_numbers += 1
            
            print("\nSection distribution:")
            for section in sorted(section_counts.keys()):
                print(f"  Section {section}: {section_counts[section]} clauses")
            
            print(f"\nClause number detection: {clauses_with_numbers}/{len(self.clauses)} ({clauses_with_numbers/len(self.clauses)*100:.1f}%)")
            
            return self.clauses

    def save_results(self):
        """Save results in both JSON and CSV formats."""
        if not self.clauses:
            print("No clauses found to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        
        # Save JSON
        json_filename = f"../outputs/{base_name}_ENHANCED_PRODUCTION_v2_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.clauses, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON saved: {json_filename}")
        
        # Save CSV
        csv_filename = f"../outputs/{base_name}_ENHANCED_PRODUCTION_v2_{timestamp}.csv"
        import csv
        
        fieldnames = [
            'Page', 'Section', 'Section_Title', 'Subsection', 'Subsection_Title',
            'Clause', 'Content/Question', 'Guidance', 'Notes', 'Yes', 'No', 'NA'
        ]
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for clause in self.clauses:
                writer.writerow({
                    'Page': clause['page'],
                    'Section': clause['section'],
                    'Section_Title': clause['section_title'],
                    'Subsection': clause['subsection'],
                    'Subsection_Title': clause['subsection_title'],
                    'Clause': clause['clause'],
                    'Content/Question': clause['content'],
                    'Guidance': clause['guidance'],
                    'Notes': clause['notes'],
                    'Yes': clause['yes'],
                    'No': clause['no'],
                    'NA': clause['na']
                })
        
        print(f"✓ CSV saved: {csv_filename}")
        
        # Save summary report
        summary_filename = f"../outputs/{base_name}_ENHANCED_PRODUCTION_v2_SUMMARY_{timestamp}.md"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("# Enhanced Production NADCAP Extraction Summary - Version 2.0\n\n")
            f.write(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Source Document:** {os.path.basename(self.pdf_path)}\n")
            f.write(f"**Method:** Enhanced Production with Improved Clause Detection\n")
            f.write(f"**Total Clauses:** {len(self.clauses)}\n\n")
            
            # Section-wise clause number detection
            section_stats = {}
            for clause in self.clauses:
                section = clause['section']
                if section not in section_stats:
                    section_stats[section] = {'total': 0, 'with_numbers': 0}
                section_stats[section]['total'] += 1
                if clause['clause']:
                    section_stats[section]['with_numbers'] += 1
            
            f.write("## Clause Number Detection by Section\n")
            total_clauses = len(self.clauses)
            total_with_numbers = sum(stats['with_numbers'] for stats in section_stats.values())
            
            for section in sorted(section_stats.keys()):
                stats = section_stats[section]
                percentage = (stats['with_numbers'] / stats['total'] * 100) if stats['total'] > 0 else 0
                f.write(f"- Section {section}: {stats['with_numbers']}/{stats['total']} ({percentage:.1f}%)\n")
            
            f.write(f"\n**Overall Detection Rate:** {total_with_numbers}/{total_clauses} ({total_with_numbers/total_clauses*100:.1f}%)\n")
            
            f.write("\n## Enhancement Features\n")
            f.write("- Section-specific clause number patterns\n")
            f.write("- Enhanced detection for Sections 4 & 5\n")
            f.write("- Flexible validation based on section context\n")
            f.write("- Improved content extraction and duplicate prevention\n")
            f.write("- Ready for stakeholder presentation\n")
        
        print(f"✓ Summary saved: {summary_filename}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python enhanced_production_nadcap_extractor_v2.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file not found: {pdf_file}")
        sys.exit(1)
    
    # Initialize extractor
    extractor = EnhancedProductionNADCAPExtractor(pdf_file)
    
    # Extract clauses
    clauses = extractor.extract_clauses()
    
    # Save results
    extractor.save_results()
    
    print(f"\n🎯 Enhanced Production Extraction Complete!")
    print(f"📊 Total clauses extracted: {len(clauses)}")
    print(f"📁 Results saved in outputs/ directory")

if __name__ == "__main__":
    main()
