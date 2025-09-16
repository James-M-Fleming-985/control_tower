#!/usr/bin/env python3
"""
AS9100 Requirements Extraction Tool
Extracts and categorizes requirements from AS9100 PDF for SF Documentation project
"""

import pdfplumber
import pandas as pd
import re
import argparse
import os
from datetime import datetime

class AS9100Extractor:
    def __init__(self):
        self.requirements = []
        self.verification_data = {}
        
    def categorize_by_clause(self, clause):
        """Categorize requirements using AS9100's own structure"""
        categories = {
            '4.1': 'Understanding the organization',
            '4.2': 'Understanding stakeholder needs', 
            '4.3': 'QMS scope',
            '4.4': 'QMS and processes',
            '5.1': 'Leadership and commitment',
            '5.2': 'Policy',
            '5.3': 'Organizational roles',
            '6.1': 'Risk and opportunities',
            '6.2': 'Quality objectives',
            '6.3': 'Planning of changes',
            '7.1': 'Resources',
            '7.2': 'Competence',
            '7.3': 'Awareness',
            '7.4': 'Communication',
            '7.5': 'Documented information',  # KEY for SF project
            '8.1': 'Operational planning',
            '8.2': 'Customer requirements',
            '8.3': 'Design and development',
            '8.4': 'External providers',
            '8.5': 'Production and service',
            '8.6': 'Product release',
            '8.7': 'Nonconforming outputs',
            '9.1': 'Monitoring and measurement',
            '9.2': 'Internal audit',
            '9.3': 'Management review',
            '10.1': 'General improvement',
            '10.2': 'Nonconformity and corrective action',
            '10.3': 'Continual improvement'
        }
        
        # Find best match for clause
        for prefix, category in categories.items():
            if clause.startswith(prefix):
                return category
        
        # Fallback to major section
        major_sections = {
            '4': 'Context of organization',
            '5': 'Leadership', 
            '6': 'Planning',
            '7': 'Support',
            '8': 'Operation', 
            '9': 'Performance evaluation',
            '10': 'Improvement'
        }
        
        for prefix, category in major_sections.items():
            if clause.startswith(prefix + '.'):
                return category
        
        return 'Other'
    
    def determine_sf_relevance(self, clause, requirement_text):
        """Determine if requirement is relevant to SF documentation"""
        sf_high_priority = ['7.5']  # Documentation control
        sf_medium_priority = ['8.1', '8.5', '7.2', '4.4', '8.7', '9.1']
        sf_low_priority = ['5.1', '6.1', '6.2', '9.2', '10.2']
        
        for priority_clause in sf_high_priority:
            if clause.startswith(priority_clause):
                return 'High'
                
        for priority_clause in sf_medium_priority:
            if clause.startswith(priority_clause):
                return 'Medium'
                
        for priority_clause in sf_low_priority:
            if clause.startswith(priority_clause):
                return 'Low'
        
        # Check content for SF-relevant keywords
        sf_keywords = ['document', 'procedure', 'work instruction', 'record', 'training', 'competence', 'process control']
        text_lower = requirement_text.lower()
        if any(keyword in text_lower for keyword in sf_keywords):
            return 'Medium'
            
        return 'Low'
    
    def extract_requirements(self, pdf_path):
        """Extract all requirements from AS9100 PDF"""
        print(f"🔍 Extracting requirements from: {pdf_path}")
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"📄 Total pages: {total_pages}")
            
            pages_with_requirements = set()
            total_shall_count = 0
            current_section = "Unknown"
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"⏳ Processing page {page_num}/{total_pages}...", end='\r')
                
                text = page.extract_text()
                if not text:
                    continue
                
                # Count total 'shall' statements for verification
                shall_count = len(re.findall(r'\\bshall\\b', text, re.IGNORECASE))
                total_shall_count += shall_count
                
                # Extract section headers (like "7.5 Documented Information")
                section_matches = re.findall(r'^(\\d+(?:\\.\\d+)*(?:\\.\\d+)?)\\s+([A-Z][^\\n]+)', text, re.MULTILINE)
                for section_num, section_title in section_matches:
                    current_section = f"{section_num} {section_title.strip()}"
                
                # Extract requirements with more flexible patterns
                patterns = [
                    # Pattern 1: Direct "shall" statements with context
                    r'([^.!?]+shall[^.!?]+[.!?])',
                    # Pattern 2: Organization shall statements
                    r'(The organization shall[^.!?]+[.!?])',
                    # Pattern 3: Documented information shall statements  
                    r'(.*documented information.*shall[^.!?]+[.!?])',
                    # Pattern 4: Quality management system shall statements
                    r'(.*quality management system.*shall[^.!?]+[.!?])'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    
                    for requirement in matches:
                        # Clean up the requirement text
                        requirement_cleaned = re.sub(r'\\s+', ' ', requirement.strip())
                        
                        # Skip if too short or doesn't contain meaningful content
                        if len(requirement_cleaned) < 30:
                            continue
                            
                        # Skip if it's just a note or example
                        if requirement_cleaned.lower().startswith(('note', 'example', 'see', 'figure')):
                            continue
                        
                        # Try to extract or infer clause number from context
                        clause_number = self._extract_clause_number(text, requirement_cleaned, current_section)
                        
                        pages_with_requirements.add(page_num)
                        
                        self.requirements.append({
                            'clause': clause_number,
                            'requirement': requirement_cleaned,
                            'category': self.categorize_by_clause(clause_number),
                            'sf_relevance': self.determine_sf_relevance(clause_number, requirement_cleaned),
                            'page': page_num,
                            'section_context': current_section,
                            'extracted_timestamp': datetime.now().isoformat()
                        })
            
            # Remove duplicates based on similar content
            self.requirements = self._remove_duplicate_requirements()
            
            # Store verification data
            self.verification_data = {
                'total_pages': total_pages,
                'pages_with_requirements': len(pages_with_requirements),
                'pages_without_requirements': total_pages - len(pages_with_requirements),
                'total_shall_statements': total_shall_count,
                'requirements_extracted': len(self.requirements),
                'extraction_rate': len(self.requirements) / max(total_shall_count, 1) * 100
            }
            
        print(f"\\n✅ Extraction complete!")
        return self.requirements
    
    def _extract_clause_number(self, page_text, requirement, current_section):
        """Try to extract or infer clause number from context"""
        # Look for explicit clause numbers near the requirement
        clause_pattern = r'(\\d+\\.\\d+(?:\\.\\d+)?(?:\\.\\d+)?)'
        
        # Find all clause numbers on the page
        clause_matches = re.findall(clause_pattern, page_text)
        
        if clause_matches:
            # Use the last found clause number as it's likely the current context
            return clause_matches[-1]
        
        # Fall back to section-based inference
        if current_section and current_section != "Unknown":
            section_match = re.match(r'(\\d+(?:\\.\\d+)*)', current_section)
            if section_match:
                return section_match.group(1)
        
        # Infer from content keywords
        content_lower = requirement.lower()
        if 'documented information' in content_lower:
            return '7.5'
        elif 'quality management system' in content_lower:
            return '4.4'
        elif 'operational planning' in content_lower:
            return '8.1'
        elif 'competence' in content_lower:
            return '7.2'
        elif 'management review' in content_lower:
            return '9.3'
        elif 'internal audit' in content_lower:
            return '9.2'
        
        return 'Unclassified'
    
    def _remove_duplicate_requirements(self):
        """Remove duplicate or very similar requirements"""
        unique_requirements = []
        seen_content = set()
        
        for req in self.requirements:
            # Create a simplified version for comparison
            simplified = re.sub(r'[^a-zA-Z0-9\\s]', '', req['requirement'].lower())
            simplified = re.sub(r'\\s+', ' ', simplified).strip()
            
            # Only add if we haven't seen similar content
            if simplified not in seen_content and len(simplified) > 20:
                seen_content.add(simplified)
                unique_requirements.append(req)
        
        return unique_requirements
    
    def verify_extraction_completeness(self):
        """Verify the extraction was comprehensive"""
        print("\\n🔍 EXTRACTION VERIFICATION:")
        print(f"📊 Total requirements extracted: {self.verification_data['requirements_extracted']}")
        print(f"📄 Pages with requirements: {self.verification_data['pages_with_requirements']}/{self.verification_data['total_pages']}")
        print(f"📈 Extraction rate: {self.verification_data['extraction_rate']:.1f}%")
        
        # Check AS9100 section coverage
        expected_sections = ['4', '5', '6', '7', '8', '9', '10']
        found_sections = set()
        
        for req in self.requirements:
            clause = req['clause']
            major_section = clause.split('.')[0]
            found_sections.add(major_section)
        
        print("\\n📋 AS9100 Section Coverage:")
        for section in expected_sections:
            status = "✅" if section in found_sections else "❌"
            print(f"{status} Section {section}")
        
        missing_sections = set(expected_sections) - found_sections
        if missing_sections:
            print(f"⚠️  WARNING: Missing sections: {missing_sections}")
        
        # Check SF-relevant requirements
        sf_high = len([r for r in self.requirements if r['sf_relevance'] == 'High'])
        sf_medium = len([r for r in self.requirements if r['sf_relevance'] == 'Medium'])
        sf_low = len([r for r in self.requirements if r['sf_relevance'] == 'Low'])
        
        print(f"\\n🎯 SF Relevance Breakdown:")
        print(f"🔴 High priority: {sf_high} requirements")
        print(f"🟡 Medium priority: {sf_medium} requirements") 
        print(f"🟢 Low priority: {sf_low} requirements")
        
        return self.verification_data
    
    def save_results(self, output_dir):
        """Save extraction results to Excel"""
        if not self.requirements:
            print("❌ No requirements to save!")
            return None
            
        df = pd.DataFrame(self.requirements)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = f"{output_dir}/as9100_requirements_{timestamp}.xlsx"
        
        # Create Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main requirements sheet
            df.to_excel(writer, sheet_name='All_Requirements', index=False)
            
            # High priority SF requirements
            sf_high = df[df['sf_relevance'] == 'High']
            sf_high.to_excel(writer, sheet_name='SF_High_Priority', index=False)
            
            # Requirements by category
            categories = df['category'].unique()
            for category in sorted(categories):
                cat_df = df[df['category'] == category]
                sheet_name = category.replace(' ', '_')[:31]  # Excel sheet name limit
                cat_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Verification summary
            verification_df = pd.DataFrame([self.verification_data])
            verification_df.to_excel(writer, sheet_name='Extraction_Summary', index=False)
        
        print(f"💾 Results saved to: {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Extract AS9100 requirements for SF Documentation project')
    parser.add_argument('--input', required=True, help='Path to AS9100 PDF file')
    parser.add_argument('--output', default='outputs', help='Output directory for results')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        print("\\n📁 Please place your AS9100 PDF in the as9100_analysis folder")
        return
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Extract requirements
    extractor = AS9100Extractor()
    requirements = extractor.extract_requirements(args.input)
    
    # Verify extraction
    verification = extractor.verify_extraction_completeness()
    
    # Save results
    output_file = extractor.save_results(args.output)
    
    print("\\n🎯 NEXT STEPS:")
    print("1. Review the generated Excel file")
    print("2. Focus on 'SF_High_Priority' sheet for documentation requirements")
    print("3. Use 'All_Requirements' sheet for comprehensive gap analysis")
    print("4. Manual review required to determine actual compliance gaps")
    
    return output_file

if __name__ == "__main__":
    main()
