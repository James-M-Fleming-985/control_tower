#!/usr/bin/env python3
"""
NADCAP Requirements Extraction Tool - Improved Version
Extracts clauses 2.7.1 to 5.7.1 with clean YES/NO/NA structure
"""

import pdfplumber
import pandas as pd
import re
import argparse
import os
from datetime import datetime

class NADCAPClauseExtractor:
    def __init__(self):
        self.extracted_text = ""
        self.clauses = []
        
    def extract_from_pdf(self, pdf_path):
        """Extract text from NADCAP PDF"""
        print(f"📖 Extracting text from: {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                self.extracted_text = ""
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        # Add page marker for reference
                        self.extracted_text += f"\n--- PAGE {page_num} ---\n"
                        self.extracted_text += page_text + "\n"
                
                print(f"✅ Extracted text from {len(pdf.pages)} pages")
                return True
                
        except Exception as e:
            print(f"❌ Error extracting PDF: {str(e)}")
            return False
    
    def parse_clauses(self):
        """Parse NADCAP clauses 2.7.1 to 5.7.1 that have YES/NO/NA responses directly adjacent"""
        print("🔍 Parsing clauses from 2.7.1 to 5.7.1 with adjacent YES/NO/NA responses...")
        
        lines = self.extracted_text.split('\n')
        current_page = 1
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Track page numbers
            if line.startswith('--- PAGE'):
                try:
                    current_page = int(line.split()[2])
                except:
                    pass
                i += 1
                continue
            
            # Look for lines that contain BOTH a clause number AND a question with YES/NO response
            # Pattern: clause number + question text + YES NO (NA)
            clause_with_response = self._extract_clause_with_adjacent_response(line)
            if clause_with_response:
                clause_number, question_text, yes_col, no_col, na_col = clause_with_response
                
                # Check if clause is in our target range
                if self._is_clause_in_range(clause_number):
                    print(f"   📋 Found clause: {clause_number}")
                    
                    # Look for guidance in the next few lines
                    guidance = self._extract_guidance_following(lines, i)
                    
                    self._add_clause(clause_number, question_text, yes_col, no_col, na_col, guidance, current_page)
                    print(f"      ✅ Added clause {clause_number} (question with adjacent YES/NO)")
            
            # Also check if current line has clause number and next line has question + YES/NO
            elif re.match(r'^\d+\.\d+\.\d+(?:\.\d+)*\s+', line):
                clause_match = re.match(r'^(\d+\.\d+\.\d+(?:\.\d+)*)\s+(.*)', line)
                if clause_match and i + 1 < len(lines):
                    clause_number = clause_match.group(1)
                    first_part = clause_match.group(2).strip()
                    next_line = lines[i + 1].strip()
                    
                    # Check if next line has YES/NO pattern
                    if self._contains_yes_no_pattern(next_line):
                        if self._is_clause_in_range(clause_number):
                            # Extract question and response from the two lines
                            question_text, yes_col, no_col, na_col = self._extract_question_and_response(first_part, next_line)
                            if question_text and yes_col and no_col:
                                print(f"   📋 Found clause: {clause_number}")
                                
                                # Look for guidance
                                guidance = self._extract_guidance_following(lines, i + 1)
                                
                                self._add_clause(clause_number, question_text, yes_col, no_col, na_col, guidance, current_page)
                                print(f"      ✅ Added clause {clause_number} (multi-line question with YES/NO)")
                                i += 1  # Skip the YES/NO line since we processed it
            
            i += 1
        
        print(f"📊 Found {len(self.clauses)} clauses with adjacent YES/NO/NA responses")
        return self.clauses
    
    def _is_clause_in_range(self, clause_number):
        """Check if clause is in the target range (2.7.1 to 5.7.1) including sub-clauses"""
        try:
            parts = [int(x) for x in clause_number.split('.')]
            if len(parts) >= 3:
                major, minor, sub = parts[0], parts[1], parts[2]
                
                # Start: 2.7.1
                start_major, start_minor, start_sub = 2, 7, 1
                # End: 5.7.1  
                end_major, end_minor, end_sub = 5, 7, 1
                
                # Convert to comparable number for range checking
                clause_value = major * 10000 + minor * 100 + sub
                start_value = start_major * 10000 + start_minor * 100 + start_sub
                end_value = end_major * 10000 + end_minor * 100 + end_sub
                
                return start_value <= clause_value <= end_value
                
        except:
            return False
        
        return False
    
    def _extract_clause_with_adjacent_response(self, line):
        """Extract clause number, question, and YES/NO response from a single line"""
        # Pattern: clause number + question + YES NO (NA)
        # Example: "3.6.1.1 Evidence of frozen process approval as required by the customer? YES NO NA"
        
        pattern = r'^(\d+\.\d+\.\d+(?:\.\d+)*)\s+(.+\?)\s+(YES\s+NO(?:\s+NA)?)\s*$'
        match = re.match(pattern, line, re.IGNORECASE)
        
        if match:
            clause_number = match.group(1)
            question_text = match.group(2).strip()
            response_text = match.group(3).strip()
            
            # Parse the response options
            yes_col, no_col, na_col = self._extract_response_columns(response_text)
            
            if yes_col and no_col:  # Only return if we have valid YES/NO
                return (clause_number, question_text, yes_col, no_col, na_col)
        
        return None
    
    def _extract_question_and_response(self, first_part, response_line):
        """Extract question and response from two lines"""
        # First part might be the start of the question
        # Response line might have the rest of question + YES/NO
        
        # Check if response line has question text before YES/NO
        question_part = self._extract_question_before_response(response_line)
        
        if question_part:
            # Combine first part with question part
            full_question = (first_part + " " + question_part).strip()
        else:
            # First part is the complete question
            full_question = first_part.strip()
        
        # Extract response options
        yes_col, no_col, na_col = self._extract_response_columns(response_line)
        
        # Only return if we have a question ending with ? and valid YES/NO
        if full_question.endswith('?') and yes_col and no_col:
            return (full_question, yes_col, no_col, na_col)
        
        return (None, None, None, None)
    
    def _extract_guidance_following(self, lines, start_index):
        """Extract guidance from lines following the current position"""
        guidance = ""
        i = start_index + 1
        
        while i < len(lines) and i < start_index + 5:  # Look ahead max 5 lines
            line = lines[i].strip()
            
            # Stop if we hit another clause or page break
            if re.match(r'^\d+\.\d+\.\d+', line) or line.startswith('--- PAGE'):
                break
            
            # Look for guidance
            if line.lower().startswith('guidance:'):
                guidance = line
                i += 1
                # Continue collecting guidance
                while i < len(lines) and i < start_index + 8:
                    next_line = lines[i].strip()
                    if (next_line and 
                        not re.match(r'^\d+\.\d+\.\d+', next_line) and 
                        not next_line.startswith('--- PAGE') and
                        not self._contains_yes_no_pattern(next_line)):
                        guidance += " " + next_line
                        i += 1
                    else:
                        break
                break
            
            i += 1
        
        return guidance.strip()
    
    def _contains_yes_no_pattern(self, text):
        """Check if text contains YES/NO/NA pattern - very strict matching"""
        if not text:
            return False
            
        # More precise patterns that require proper spacing and word boundaries
        strict_patterns = [
            r'\bYES\s+NO\s+NA\b',      # YES NO NA with word boundaries
            r'\bYES\s+NO\b(?!\s+\w)',   # YES NO but not followed by other words (like "NOT")
            r'YES\s{2,}NO\s{2,}NA',     # YES  NO  NA with multiple spaces
            r'YES\s{2,}NO\b(?!\s+\w)'   # YES  NO with multiple spaces
        ]
        
        for pattern in strict_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_response_columns(self, text):
        """Extract YES, NO, NA as separate columns - strict validation"""
        # Initialize all as empty
        yes_col = ""
        no_col = ""
        na_col = ""
        
        # Only set values if we find a valid pattern
        if re.search(r'\bYES\s+NO\s+NA\b', text, re.IGNORECASE):
            yes_col = "YES"
            no_col = "NO"
            na_col = "NA"
        elif re.search(r'\bYES\s+NO\b(?!\s+\w)', text, re.IGNORECASE):
            yes_col = "YES"
            no_col = "NO"
            na_col = ""  # No NA option
        elif re.search(r'YES\s{2,}NO\s{2,}NA', text, re.IGNORECASE):
            yes_col = "YES"
            no_col = "NO"
            na_col = "NA"
        elif re.search(r'YES\s{2,}NO\b(?!\s+\w)', text, re.IGNORECASE):
            yes_col = "YES"
            no_col = "NO"
            na_col = ""
        
        return yes_col, no_col, na_col
    
    def _extract_question_before_response(self, text):
        """Extract question text that appears before YES/NO response options"""
        # Remove YES NO NA pattern from the text
        patterns = [
            r'\s+YES\s+NO\s+NA\s*$',
            r'\s+YES\s+NO\s*$',
            r'\s+YES\s{2,}NO\s{2,}NA\s*$',
            r'\s+YES\s{2,}NO\s*$'
        ]
        
        question_text = text
        for pattern in patterns:
            question_text = re.sub(pattern, '', question_text, flags=re.IGNORECASE)
        
        return question_text.strip()
    
    def _add_clause(self, clause_number, content, yes_col, no_col, na_col, guidance, page):
        """Add a clause to the collection"""
        
        clause = {
            'Clause': clause_number,
            'Clause_Content': content,
            'YES': yes_col,
            'NO': no_col,
            'NA': na_col,
            'Guidance': guidance,
            'Page_Reference': page,
            'SF_Relevance': self._assess_sf_relevance(content, guidance),
            'ZnNi_Specific': self._is_zn_ni_specific(content, guidance),
            'Implementation_Priority': self._assess_priority(clause_number, content),
            'Document_Type_Needed': self._suggest_document_type(content)
        }
        
        self.clauses.append(clause)
    
    def _assess_sf_relevance(self, content, guidance):
        """Assess relevance to Surface Finishing operations"""
        text_to_analyze = (content + " " + guidance).lower()
        
        critical_keywords = ['process control document', 'pcd', 'quality system', 'nonconformance', 'customer notification']
        high_keywords = ['procedure', 'work instruction', 'training', 'qualification', 'calibration', 'testing']
        medium_keywords = ['documentation', 'record', 'review', 'approval', 'standard']
        
        if any(keyword in text_to_analyze for keyword in critical_keywords):
            return 'Critical'
        elif any(keyword in text_to_analyze for keyword in high_keywords):
            return 'High'
        elif any(keyword in text_to_analyze for keyword in medium_keywords):
            return 'Medium'
        else:
            return 'Low'
    
    def _is_zn_ni_specific(self, content, guidance):
        """Check if requirement is specific to ZnNi operations"""
        text_to_analyze = (content + " " + guidance).lower()
        zn_ni_keywords = ['zinc', 'nickel', 'zn', 'ni', 'plating', 'electroplating', 'chemical processing']
        
        return any(keyword in text_to_analyze for keyword in zn_ni_keywords)
    
    def _assess_priority(self, clause_number, content):
        """Assess implementation priority based on clause and content"""
        # High priority clauses for SF operations
        high_priority_clauses = ['2.7', '3.1', '3.6', '3.10', '4.2', '4.3', '5.1']
        medium_priority_clauses = ['2.8', '3.2', '3.7', '3.9', '4.1', '4.5', '5.2']
        
        for hp_clause in high_priority_clauses:
            if clause_number.startswith(hp_clause):
                return 'High'
        
        for mp_clause in medium_priority_clauses:
            if clause_number.startswith(mp_clause):
                return 'Medium'
        
        # Check content for priority keywords
        text_lower = content.lower()
        critical_words = ['shall', 'must', 'required', 'documented procedure']
        if any(word in text_lower for word in critical_words):
            return 'High'
        
        return 'Low'
    
    def _suggest_document_type(self, content):
        """Suggest type of document needed for compliance"""
        text_lower = content.lower()
        
        if 'procedure' in text_lower:
            return 'Procedure'
        elif 'work instruction' in text_lower or 'instruction' in text_lower:
            return 'Work Instruction'
        elif 'record' in text_lower or 'form' in text_lower:
            return 'Form/Record'
        elif 'training' in text_lower or 'competency' in text_lower:
            return 'Training Document'
        elif 'manual' in text_lower:
            return 'Manual'
        elif 'policy' in text_lower:
            return 'Policy'
        else:
            return 'TBD'
    
    def save_to_excel(self, output_dir):
        """Save clauses to Excel file with clean format"""
        if not self.clauses:
            print("❌ No clauses found to save")
            return None
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nadcap_clauses_clean_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Create DataFrame
        df = pd.DataFrame(self.clauses)
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main clauses sheet with your requested columns
            main_columns = ['Clause', 'Clause_Content', 'YES', 'NO', 'NA', 'Guidance']
            main_df = df[main_columns]
            main_df.to_excel(writer, sheet_name='NADCAP_Clauses_Clean', index=False)
            
            # Full analysis sheet with all metadata
            df.to_excel(writer, sheet_name='Full_Analysis', index=False)
            
            # High priority clauses only
            high_priority = df[df['Implementation_Priority'] == 'High']
            if not high_priority.empty:
                high_priority[main_columns].to_excel(writer, sheet_name='High_Priority', index=False)
            
            # Summary by clause range
            summary_data = []
            for major in range(2, 6):  # 2.x.x to 5.x.x
                clause_prefix = f"{major}."
                clause_count = len(df[df['Clause'].str.startswith(clause_prefix)])
                if clause_count > 0:
                    summary_data.append({
                        'Clause_Range': f"{major}.x.x",
                        'Clause_Count': clause_count,
                        'High_Priority': len(df[(df['Clause'].str.startswith(clause_prefix)) & (df['Implementation_Priority'] == 'High')]),
                        'SF_Critical': len(df[(df['Clause'].str.startswith(clause_prefix)) & (df['SF_Relevance'] == 'Critical')]),
                        'ZnNi_Specific': len(df[(df['Clause'].str.startswith(clause_prefix)) & (df['ZnNi_Specific'] == True)])
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"📊 Results saved to: {filepath}")
        print(f"📈 Summary:")
        print(f"   • Total clauses extracted: {len(self.clauses)}")
        print(f"   • Clause range: 2.7.1 to 5.7.1")
        print(f"   • High priority: {len(df[df['Implementation_Priority'] == 'High'])}")
        print(f"   • SF Critical: {len(df[df['SF_Relevance'] == 'Critical'])}")
        print(f"   • ZnNi specific: {len(df[df['ZnNi_Specific'] == True])}")
        
        return filepath

def main():
    parser = argparse.ArgumentParser(description='Extract NADCAP clauses 2.7.1 to 5.7.1 with clean YES/NO/NA format')
    parser.add_argument('--input', '-i', default='NADCAP Audit Requirements.pdf',
                      help='Input NADCAP PDF file')
    parser.add_argument('--output', '-o', default='outputs',
                      help='Output directory for Excel files')
    
    args = parser.parse_args()
    
    print("🚀 NADCAP Clause Extraction Started (Clean Format)")
    print("📋 Target: Clauses 2.7.1 to 5.7.1 with YES/NO/NA responses")
    print("=" * 60)
    
    try:
        extractor = NADCAPClauseExtractor()
        
        # Extract text from PDF
        if not extractor.extract_from_pdf(args.input):
            print("❌ Failed to extract text from PDF")
            return 1
        
        # Parse clauses
        clauses = extractor.parse_clauses()
        
        if clauses:
            output_file = extractor.save_to_excel(args.output)
            print(f"\n✅ Extraction completed successfully!")
            print(f"📁 Output file: {output_file}")
            print(f"\n📋 Column structure:")
            print(f"   • Clause - Clause number (2.7.1 to 5.7.1)")
            print(f"   • Clause_Content - The requirement text")
            print(f"   • YES - YES response option")
            print(f"   • NO - NO response option") 
            print(f"   • NA - NA response option (if applicable)")
            print(f"   • Guidance - Any specific guidance for the clause")
        else:
            print("❌ No clauses extracted")
            return 1
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
