#!/usr/bin/env python3
"""
NADCAP Requirements Extraction Tool
Extracts and categorizes requirements from NADCAP AC7108 PDF for SF Documentation project
"""

import pdfplumber
import pandas as pd
import re
import argparse
import os
from datetime import datetime

class NADCAPExtractor:
    def __init__(self):
        self.requirements = []
        self.verification_data = {}
        
    def categorize_by_clause(self, clause):
        """Categorize requirements using NADCAP AC7108 structure with precise numbering"""
        
        # Handle Appendix clauses
        if clause.startswith('Appendix'):
            appendix_map = {
                'Appendix A': 'Appendix A - Process Control Requirements',
                'Appendix B': 'Appendix B - Test Methods and Standards',
                'Appendix C': 'Appendix C - Material Requirements',
                'Appendix D': 'Appendix D - Process Parameters Recording',
                'Appendix E': 'Appendix E - Buy-off Procedures',
                'Appendix F': 'Appendix F - Equipment Requirements',
                'Appendix G': 'Appendix G - Testing Frequency Requirements'
            }
            for app_key, app_name in appendix_map.items():
                if clause.startswith(app_key):
                    return app_name
            return 'Appendix Requirements'
        
        # Handle detailed clause numbering (e.g., 9.3.1)
        detailed_categories = {
            '1.': 'Scope and Purpose',
            '2.': 'Referenced Standards and Documents',
            '3.1': 'Quality System Requirements',
            '3.2': 'Analysis and Testing Provider Requirements',
            '3.3': 'Self-Audit Requirements',
            '3.4': 'Pre-Audit Requirements',
            '3.5': 'Audit Process Requirements',
            '3.6': 'Process Control Documents',
            '3.7': 'Process and Quality Planning',
            '3.8': 'Purchasing and Source Selection',
            '3.9': 'Material Identification and Traceability',
            '3.10': 'Processing Requirements',
            '3.11': 'Facility and Housekeeping Requirements',
            '3.12': 'Non-conforming Parts Management',
            '3.13': 'Workmanship Standards',
            '4.1': 'Testing and Inspection General',
            '4.2': 'Lot Testing Requirements',
            '4.3': 'Periodic Testing Requirements',
            '4.4': 'Equipment and Facility Requirements',
            '4.5': 'Personnel Requirements',
            '4.6': 'Records and Documentation Requirements',
            '5.': 'Audit Closure Requirements',
            '6.': 'Corrective Action Requirements',
            '7.': 'Surveillance Requirements',
            '8.': 'Certificate Management',
            '9.1': 'Special Process Requirements',
            '9.2': 'Customer Specific Requirements',
            '9.3': 'Facility Requirements',
            '9.4': 'Sub-tier Management',
            '10.': 'Additional Requirements'
        }
        
        # Find exact match first
        if clause in detailed_categories:
            return detailed_categories[clause]
        
        # Find best partial match
        for category_clause, category_name in detailed_categories.items():
            if clause.startswith(category_clause):
                return category_name
        
        # Fallback to major section
        if clause.startswith('3.'):
            return 'Quality System and Process Requirements'
        elif clause.startswith('4.'):
            return 'Testing and Inspection Requirements'
        elif clause.startswith('9.'):
            return 'Special Requirements'
        else:
            return 'General Requirements'
    
    def determine_sf_relevance(self, clause, requirement_text):
        """Determine if requirement is relevant to SF ZnNi line operations"""
        sf_critical = ['3.6', '3.10', '4.2', '4.3', 'D.', 'E.', 'G.']  # Process control, testing, parameters
        sf_high_priority = ['3.1', '3.7', '3.9', '4.1', '4.5', '4.6', 'F.']  # Quality system, planning, personnel
        sf_medium_priority = ['3.8', '3.11', '3.12', '4.4', 'A.', 'B.', 'C.']  # Purchasing, facility, equipment
        sf_low_priority = ['3.2', '3.3', '3.4', '3.5', '3.13']  # Administrative and audit prep
        
        for priority_clause in sf_critical:
            if clause.startswith(priority_clause):
                return 'Critical'
                
        for priority_clause in sf_high_priority:
            if clause.startswith(priority_clause):
                return 'High'
                
        for priority_clause in sf_medium_priority:
            if clause.startswith(priority_clause):
                return 'Medium'
                
        for priority_clause in sf_low_priority:
            if clause.startswith(priority_clause):
                return 'Low'
        
        # Check content for ZnNi-relevant keywords
        zn_ni_keywords = ['zinc', 'nickel', 'plating', 'chemical processing', 'solution', 'process control', 
                         'temperature', 'current density', 'testing', 'calibration', 'traceability']
        text_lower = requirement_text.lower()
        if any(keyword in text_lower for keyword in zn_ni_keywords):
            return 'High'
            
        # Check for general compliance keywords
        compliance_keywords = ['shall', 'must', 'required', 'documented', 'procedure', 'record']
        if any(keyword in text_lower for keyword in compliance_keywords):
            return 'Medium'
            
        return 'Low'
    
    def extract_requirements(self, pdf_path):
        """Extract requirements from NADCAP PDF"""
        print(f"🔍 Extracting requirements from: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            
            print(f"📄 Processing {len(pdf.pages)} pages...")
            for page_num, page in enumerate(pdf.pages, 1):
                if page_num % 5 == 0:
                    print(f"   📖 Processing page {page_num}/{len(pdf.pages)}")
                
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        
        # Extract requirements based on NADCAP structure
        self._parse_nadcap_requirements(full_text)
        
        print(f"✅ Extracted {len(self.requirements)} requirements")
        return self.requirements
    
    def _parse_nadcap_requirements(self, text):
        """Parse NADCAP-specific requirement patterns with precise clause numbering"""
        
        # Primary pattern: Look for requirements ending with YES NO or YES NO NA
        # These are the actual audit questions
        requirement_pattern = r'([^?]+\?)\s+(YES\s+NO(?:\s+NA)?)\s*'
        
        # Find all audit questions
        matches = re.finditer(requirement_pattern, text, re.MULTILINE | re.DOTALL)
        
        question_number = 1
        current_section = "Unknown"
        
        for match in matches:
            question_text = match.group(1).strip()
            response_options = match.group(2).strip()
            
            # Clean up the question text
            question_text = re.sub(r'\s+', ' ', question_text)  # Normalize whitespace
            question_text = re.sub(r'^[^\w]*', '', question_text)  # Remove leading non-word chars
            
            # Try to identify section context from surrounding text
            match_start = match.start()
            context_start = max(0, match_start - 500)
            context_text = text[context_start:match_start]
            
            # Look for section headers in context
            section_match = re.search(r'(\d+\.?\d*\.?\d*)\s+([A-Z][^\.]+)', context_text[-200:])
            if section_match:
                current_section = f"{section_match.group(1).strip()} {section_match.group(2).strip()}"
            
            # Look for page headers for additional context
            page_match = re.search(r'Nadcap AC7108.*?-\s*(\d+)\s*-', context_text[-300:])
            page_number = page_match.group(1) if page_match else "Unknown"
            
            if len(question_text) > 20:  # Only include substantial questions
                clause = f"Q{question_number:03d}"  # Create question numbering
                self._add_requirement(clause, question_text, current_section, response_options, page_number)
                question_number += 1
        
        # Also look for numbered sections/clauses that might contain requirements
        section_pattern = r'(\d+\.?\d*\.?\d*)\s+([A-Z][A-Za-z\s,&/\-]+?)(?=\d+\.|\n|$)'
        section_matches = re.finditer(section_pattern, text, re.MULTILINE)
        
        for match in section_matches:
            clause_num = match.group(1).strip()
            section_title = match.group(2).strip()
            
            # Only include substantial sections
            if len(section_title) > 10 and len(clause_num) > 1:
                self._add_section_header(clause_num, section_title)
        
        # Look for appendix requirements
        appendix_pattern = r'(Appendix [A-G](?:\.\d+)*)\s*([^Y]+?)(?=Appendix|$)'
        appendix_matches = re.finditer(appendix_pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in appendix_matches:
            clause = match.group(1).strip()
            content = match.group(2).strip()
            
            if len(content) > 50:  # Only substantial content
                # Look for specific requirements in appendix content
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 30 and any(word in line.lower() for word in ['shall', 'must', 'required', 'ensure']):
                        self._add_requirement(clause, line, f"Appendix Requirements", "Reference", "Appendix")
    
    def _add_requirement(self, clause, requirement_text, section="Unknown", response_options="YES NO", page="Unknown"):
        """Add a requirement to the list with all metadata"""
        requirement = {
            'Question_ID': clause,
            'Clause': clause,
            'Section': section,
            'Requirement': requirement_text,
            'Response_Options': response_options,
            'Page_Reference': page,
            'Category': self.categorize_by_clause(clause),
            'SF_Relevance': self.determine_sf_relevance(clause, requirement_text),
            'Audit_Risk': self._assess_audit_risk(clause, requirement_text),
            'Implementation_Effort': self._estimate_effort(requirement_text),
            'Document_Type_Needed': self._suggest_document_type(requirement_text),
            'ZnNi_Specific': self._is_zn_ni_specific(requirement_text),
            'Requirement_Type': self._classify_requirement_type(requirement_text),
            'Audit_Evidence_Required': self._suggest_audit_evidence(clause, requirement_text)
        }
        self.requirements.append(requirement)
    
    def _add_section_header(self, clause_num, section_title):
        """Add section header as context"""
        requirement = {
            'Question_ID': f"SEC-{clause_num}",
            'Clause': clause_num,
            'Section': section_title,
            'Requirement': f"Section: {section_title}",
            'Response_Options': "SECTION HEADER",
            'Page_Reference': "Various",
            'Category': self.categorize_by_clause(clause_num),
            'SF_Relevance': 'Context',
            'Audit_Risk': 'N/A',
            'Implementation_Effort': 'N/A',
            'Document_Type_Needed': 'Section Header',
            'ZnNi_Specific': False,
            'Requirement_Type': 'Section Header',
            'Audit_Evidence_Required': 'N/A'
        }
        self.requirements.append(requirement)
    
    def _classify_requirement_type(self, requirement_text):
        """Classify the type of requirement"""
        text_lower = requirement_text.lower()
        
        if any(word in text_lower for word in ['document', 'procedure', 'written', 'record']):
            return 'Documentation'
        elif any(word in text_lower for word in ['train', 'competent', 'qualified', 'personnel']):
            return 'Personnel'
        elif any(word in text_lower for word in ['calibrat', 'equipment', 'instrument']):
            return 'Equipment'
        elif any(word in text_lower for word in ['test', 'inspect', 'sample', 'verify']):
            return 'Testing'
        elif any(word in text_lower for word in ['process', 'parameter', 'control']):
            return 'Process Control'
        else:
            return 'General'
    
    def _suggest_audit_evidence(self, clause, requirement_text):
        """Suggest what evidence an auditor would look for"""
        text_lower = requirement_text.lower()
        
        if 'document' in text_lower or 'procedure' in text_lower:
            return 'Written procedures, work instructions, controlled documents'
        elif 'record' in text_lower:
            return 'Completed records, logs, data sheets'
        elif 'training' in text_lower or 'competent' in text_lower:
            return 'Training records, competency assessments, qualification certificates'
        elif 'calibrat' in text_lower:
            return 'Calibration certificates, calibration schedules, equipment records'
        elif 'test' in text_lower:
            return 'Test results, test procedures, test equipment calibration'
        elif 'supplier' in text_lower:
            return 'Approved supplier lists, supplier assessments, purchase orders'
        else:
            return 'Implementation evidence, compliance records'
    
    def _assess_audit_risk(self, clause, requirement_text):
        """Assess audit risk level for requirement"""
        high_risk_clauses = ['3.6', '3.10', '4.2', '4.3', 'D.', 'E.']
        medium_risk_clauses = ['3.1', '3.7', '3.9', '4.1', '4.5', '4.6']
        
        if any(clause.startswith(risk_clause) for risk_clause in high_risk_clauses):
            return 'High'
        elif any(clause.startswith(risk_clause) for risk_clause in medium_risk_clauses):
            return 'Medium'
        else:
            return 'Low'
    
    def _estimate_effort(self, requirement_text):
        """Estimate implementation effort"""
        text_lower = requirement_text.lower()
        
        high_effort_keywords = ['system', 'program', 'training', 'procedure development', 'equipment']
        medium_effort_keywords = ['document', 'record', 'procedure', 'instruction']
        low_effort_keywords = ['maintain', 'ensure', 'verify', 'check']
        
        if any(keyword in text_lower for keyword in high_effort_keywords):
            return 'High'
        elif any(keyword in text_lower for keyword in medium_effort_keywords):
            return 'Medium'
        else:
            return 'Low'
    
    def _suggest_document_type(self, requirement_text):
        """Suggest type of document needed"""
        text_lower = requirement_text.lower()
        
        if 'procedure' in text_lower or 'process' in text_lower:
            return 'Procedure'
        elif 'instruction' in text_lower or 'work' in text_lower:
            return 'Work Instruction'
        elif 'record' in text_lower or 'log' in text_lower:
            return 'Form/Record'
        elif 'manual' in text_lower or 'training' in text_lower:
            return 'Manual'
        elif 'policy' in text_lower:
            return 'Policy'
        else:
            return 'TBD'
    
    def _is_zn_ni_specific(self, requirement_text):
        """Check if requirement is specific to ZnNi processing"""
        zn_ni_keywords = ['zinc', 'nickel', 'plating', 'chemical', 'solution', 'bath']
        text_lower = requirement_text.lower()
        return any(keyword in text_lower for keyword in zn_ni_keywords)
    
    def save_to_excel(self, output_dir):
        """Save requirements to Excel file"""
        if not self.requirements:
            print("❌ No requirements found to save")
            return None
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nadcap_requirements_UPDATED_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Create DataFrame
        df = pd.DataFrame(self.requirements)
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main requirements sheet
            df.to_excel(writer, sheet_name='NADCAP_Requirements', index=False)
            
            # Actual audit questions only (excluding section headers)
            audit_questions = df[df['Response_Options'] != 'SECTION HEADER']
            audit_questions.to_excel(writer, sheet_name='Audit_Questions', index=False)
            
            # Summary by category
            category_summary = audit_questions.groupby('Category').agg({
                'Question_ID': 'count',
                'SF_Relevance': lambda x: f"Critical: {sum(x=='Critical')}, High: {sum(x=='High')}, Medium: {sum(x=='Medium')}, Low: {sum(x=='Low')}"
            }).rename(columns={'Question_ID': 'Question_Count'})
            category_summary.to_excel(writer, sheet_name='Category_Summary')
            
            # High priority requirements
            high_priority = audit_questions[audit_questions['SF_Relevance'].isin(['Critical', 'High'])]
            high_priority.to_excel(writer, sheet_name='High_Priority', index=False)
            
            # ZnNi specific requirements
            zn_ni_specific = audit_questions[audit_questions['ZnNi_Specific'] == True]
            if not zn_ni_specific.empty:
                zn_ni_specific.to_excel(writer, sheet_name='ZnNi_Specific', index=False)
            
            # By response type
            response_summary = audit_questions.groupby('Response_Options').agg({
                'Question_ID': 'count'
            }).rename(columns={'Question_ID': 'Count'})
            response_summary.to_excel(writer, sheet_name='Response_Types')
            
            # Section headers sheet
            section_headers = df[df['Response_Options'] == 'SECTION HEADER']
            if not section_headers.empty:
                section_headers.to_excel(writer, sheet_name='Section_Headers', index=False)
        
        print(f"📊 Results saved to: {filepath}")
        print(f"📈 Summary: {len(self.requirements)} total items extracted")
        print(f"   • Audit Questions: {len(audit_questions)}")
        print(f"   • Section Headers: {len(df) - len(audit_questions)}")
        print(f"   • Critical: {len(audit_questions[audit_questions['SF_Relevance']=='Critical'])}")
        print(f"   • High: {len(audit_questions[audit_questions['SF_Relevance']=='High'])}")
        print(f"   • Medium: {len(audit_questions[audit_questions['SF_Relevance']=='Medium'])}")
        print(f"   • Low: {len(audit_questions[audit_questions['SF_Relevance']=='Low'])}")
        
        return filepath

def main():
    parser = argparse.ArgumentParser(description='Extract NADCAP requirements from PDF')
    parser.add_argument('--input', '-i', default='NADCAP Audit Requirements.pdf',
                      help='Input NADCAP PDF file')
    parser.add_argument('--output', '-o', default='outputs',
                      help='Output directory for Excel files')
    parser.add_argument('--focus', '-f', 
                      help='Focus areas (comma-separated): process_control,testing,quality_system')
    
    args = parser.parse_args()
    
    print("🚀 NADCAP Requirements Extraction Started")
    print("=" * 50)
    
    try:
        extractor = NADCAPExtractor()
        requirements = extractor.extract_requirements(args.input)
        
        if requirements:
            output_file = extractor.save_to_excel(args.output)
            print(f"\n✅ Extraction completed successfully!")
            print(f"📁 Output file: {output_file}")
        else:
            print("❌ No requirements extracted")
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
