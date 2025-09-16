#!/usr/bin/env python3
"""
Document Inventory Analyzer for NADCAP
Analyzes and categorizes SF document inventory for NADCAP gap analysis
"""

import pandas as pd
import argparse
import os
from datetime import datetime, date
import re

class DocumentInventoryAnalyzer:
    def __init__(self):
        self.documents = []
        self.analysis_results = {}
        
    def categorize_document_type(self, doc_name, doc_type=None):
        """Categorize documents by type based on name and type field"""
        name_lower = doc_name.lower()
        
        # Use explicit document type if provided
        if doc_type:
            type_lower = doc_type.lower()
            if 'procedure' in type_lower or 'proc' in type_lower:
                return 'Procedure'
            elif 'work instruction' in type_lower or 'wi' in type_lower:
                return 'Work Instruction'
            elif 'form' in type_lower or 'record' in type_lower:
                return 'Form/Record'
            elif 'manual' in type_lower or 'policy' in type_lower:
                return 'Manual/Policy'
            elif 'training' in type_lower:
                return 'Training Material'
            elif 'pcd' in type_lower or 'process control' in type_lower:
                return 'Process Control Document'
        
        # Analyze document name
        if any(word in name_lower for word in ['procedure', 'proc']):
            return 'Procedure'
        elif any(word in name_lower for word in ['work instruction', 'wi', 'work-instruction']):
            return 'Work Instruction'  
        elif any(word in name_lower for word in ['form', 'record', 'log', 'checklist']):
            return 'Form/Record'
        elif any(word in name_lower for word in ['manual', 'policy', 'standard']):
            return 'Manual/Policy'
        elif any(word in name_lower for word in ['training', 'competence', 'qualification']):
            return 'Training Material'
        elif any(word in name_lower for word in ['specification', 'spec', 'drawing']):
            return 'Specification/Drawing'
        elif any(word in name_lower for word in ['pcd', 'process control']):
            return 'Process Control Document'
        elif any(word in name_lower for word in ['calibration', 'cal']):
            return 'Calibration Record'
        else:
            return 'Other'
    
    def assess_document_status(self, last_modified, current_status=None):
        """Assess document status based on last modified date and current status"""
        if current_status:
            status_lower = current_status.lower()
            if 'current' in status_lower:
                return 'Current'
            elif 'outdated' in status_lower or 'old' in status_lower:
                return 'Outdated'
            elif 'draft' in status_lower:
                return 'Draft'
        
        # Analyze by date if no explicit status
        try:
            if isinstance(last_modified, str):
                mod_date = datetime.strptime(last_modified, '%Y-%m-%d').date()
            else:
                mod_date = last_modified
            
            today = date.today()
            days_old = (today - mod_date).days
            
            if days_old <= 365:  # Less than 1 year
                return 'Current'
            elif days_old <= 730:  # 1-2 years
                return 'Outdated'
            else:  # More than 2 years
                return 'Very Old'
                
        except:
            return 'Unknown'
    
    def determine_nadcap_relevance(self, doc_name, doc_type, description=""):
        """Determine potential NADCAP AC7108 clause relevance"""
        text_to_analyze = f"{doc_name} {doc_type} {description}".lower()
        
        relevance_mapping = {
            'Quality System (3.1)': ['quality system', 'as9100', 'iso', 'quality manual'],
            'Process Control Documents (3.6)': ['process control', 'pcd', 'process parameter', 'specification'],
            'Process Planning (3.7)': ['process plan', 'planning', 'routing', 'traveler'],
            'Purchasing/Suppliers (3.8)': ['supplier', 'purchasing', 'material', 'vendor'],
            'Material Traceability (3.9)': ['traceability', 'material id', 'lot', 'batch'],
            'Processing (3.10)': ['processing', 'operation', 'zinc', 'nickel', 'plating', 'chemical'],
            'Facility/Housekeeping (3.11)': ['facility', 'housekeeping', 'storage', 'environment'],
            'Non-conforming Parts (3.12)': ['nonconform', 'deviation', 'rework', 'reject'],
            'Lot Testing (4.2)': ['lot test', 'sample', 'test specimen', 'testing'],
            'Periodic Testing (4.3)': ['periodic test', 'routine test', 'frequency'],
            'Equipment/Calibration (4.4)': ['equipment', 'calibration', 'instrument', 'maintenance'],
            'Personnel Training (4.5)': ['personnel', 'training', 'competence', 'qualification'],
            'Records/Documentation (4.6)': ['record', 'documentation', 'buy-off', 'traveler'],
            'Buy-off Procedures (App E)': ['buy-off', 'sign-off', 'approval', 'verification'],
            'Process Parameters (App D)': ['parameter', 'temperature', 'current', 'voltage', 'time']
        }
        
        matches = []
        for clause, keywords in relevance_mapping.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                matches.append(clause)
        
        return '; '.join(matches) if matches else 'General'
    
    def assess_nadcap_priority(self, doc_name, doc_type, description=""):
        """Assess priority for NADCAP compliance"""
        text_to_analyze = f"{doc_name} {doc_type} {description}".lower()
        
        critical_keywords = ['process control', 'pcd', 'testing', 'calibration', 'buy-off', 'parameter']
        high_keywords = ['training', 'procedure', 'quality', 'traceability', 'record']
        medium_keywords = ['supplier', 'facility', 'housekeeping', 'maintenance']
        
        if any(keyword in text_to_analyze for keyword in critical_keywords):
            return 'Critical'
        elif any(keyword in text_to_analyze for keyword in high_keywords):
            return 'High'
        elif any(keyword in text_to_analyze for keyword in medium_keywords):
            return 'Medium'
        else:
            return 'Low'
    
    def analyze_inventory(self, file_path):
        """Analyze the document inventory from CSV or Excel file"""
        print(f"📊 Analyzing document inventory: {file_path}")
        
        try:
            # Check if it's Excel file (Surface Finishes and MFG.xlsx)
            if file_path.endswith('.xlsx') and 'Surface Finishes and MFG' in file_path:
                print("   📋 Loading from Surface Finishes and MFG.xlsx SURFACE FINISHES sheet...")
                df = pd.read_excel(file_path, sheet_name='SURFACE FINISHES')
                print(f"📄 Found {len(df)} documents in Surface Finishes inventory")
                
                # Analyze each document with correct column mapping
                for idx, row in df.iterrows():
                    doc_analysis = {
                        'document_name': row.get('Title', ''),
                        'osr_ref': row.get('OSR Ref', ''),
                        'cheops_ref': row.get('CHEOPS Ref', ''),
                        'file_path': '',  # Not available in this format
                        'original_type': row.get('Document Category', ''),
                        'last_modified': '',  # Not available in this format
                        'owner': row.get('Department', ''),
                        'original_status': row.get('Status', ''),
                        'description': row.get('Notes', ''),
                        'revision': row.get('Revision', ''),
                        'next_review_due': row.get('Next Review Due', ''),
                        'leading_process': row.get('Leading Process', ''),
                        'author': row.get('Author', ''),
                        'approver': row.get('Approver (resp person)', ''),
                        'comments': row.get('Comments', ''),
                        'application_date': row.get('Application date (date moved to Applicable)', ''),
                        
                        # Analysis results
                        'categorized_type': self.categorize_document_type(
                            row.get('Title', ''), 
                            row.get('Document Category', '')
                        ),
                        'assessed_status': self.assess_document_status(
                            '',  # No last modified in this format
                            row.get('Status', '')
                        ),
                        'nadcap_relevance': self.determine_nadcap_relevance(
                            row.get('Title', ''),
                            row.get('Document Category', ''),
                            row.get('Notes', '')
                        ),
                        'nadcap_priority': self.assess_nadcap_priority(
                            row.get('Title', ''),
                            row.get('Document Category', ''),
                            row.get('Notes', '')
                        ),
                        'sf_specific': 'sf' in row.get('Title', '').lower() or 'surface' in row.get('Title', '').lower(),
                        'zn_ni_specific': any(keyword in row.get('Title', '').lower() + str(row.get('Notes', '')).lower() 
                                           for keyword in ['zinc', 'nickel', 'zn', 'ni', 'plating']),
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                    
                    self.documents.append(doc_analysis)
            
            else:
                # Original CSV format fallback
                df = pd.read_csv(file_path)
                print(f"📄 Found {len(df)} documents in CSV format")
                
                # Analyze each document with original CSV structure
                for idx, row in df.iterrows():
                    doc_analysis = {
                        'document_name': row.get('Document_Name', ''),
                        'osr_ref': row.get('OSR_Ref', ''),
                        'cheops_ref': row.get('CHEOPS_Ref', ''),
                        'file_path': row.get('File_Path', ''),
                        'original_type': row.get('Document_Type', ''),
                        'last_modified': row.get('Last_Modified', ''),
                        'owner': row.get('Owner', ''),
                        'original_status': row.get('Status', ''),
                        'description': row.get('Description', ''),
                        'revision': row.get('Revision', ''),
                        'next_review_due': row.get('Next_Review_Due', ''),
                        'leading_process': '',
                        'author': '',
                        'approver': '',
                        'comments': '',
                        'application_date': '',
                        
                        # Analysis results
                        'categorized_type': self.categorize_document_type(
                            row.get('Document_Name', ''), 
                            row.get('Document_Type', '')
                        ),
                        'assessed_status': self.assess_document_status(
                            row.get('Last_Modified', ''),
                            row.get('Status', '')
                        ),
                        'nadcap_relevance': self.determine_nadcap_relevance(
                            row.get('Document_Name', ''),
                            row.get('Document_Type', ''),
                            row.get('Description', '')
                        ),
                        'nadcap_priority': self.assess_nadcap_priority(
                            row.get('Document_Name', ''),
                            row.get('Document_Type', ''),
                            row.get('Description', '')
                        ),
                        'sf_specific': 'sf' in row.get('Document_Name', '').lower() or 'surface' in row.get('Document_Name', '').lower(),
                        'zn_ni_specific': any(keyword in row.get('Document_Name', '').lower() + row.get('Description', '').lower() 
                                           for keyword in ['zinc', 'nickel', 'zn', 'ni', 'plating']),
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                    
                    self.documents.append(doc_analysis)
            
            # Generate summary statistics
            self._generate_summary_stats()
            
            print(f"✅ Analysis completed: {len(self.documents)} documents processed")
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing inventory: {e}")
            return False
    
    def _generate_summary_stats(self):
        """Generate summary statistics"""
        df = pd.DataFrame(self.documents)
        
        self.analysis_results = {
            'total_documents': len(self.documents),
            'by_type': df['categorized_type'].value_counts().to_dict(),
            'by_status': df['assessed_status'].value_counts().to_dict(),
            'by_nadcap_priority': df['nadcap_priority'].value_counts().to_dict(),
            'sf_specific_count': df['sf_specific'].sum(),
            'zn_ni_specific_count': df['zn_ni_specific'].sum(),
            'outdated_count': len(df[df['assessed_status'].isin(['Outdated', 'Very Old'])]),
            'missing_owner_count': len(df[df['owner'].isin(['', 'Unknown', None])]),
            'analysis_date': datetime.now().isoformat()
        }
    
    def save_to_excel(self, output_dir):
        """Save analysis to Excel file"""
        if not self.documents:
            print("❌ No documents analyzed to save")
            return None
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"NADCAP_DOCUMENT_ANALYSIS_UPDATED_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Create DataFrames
        documents_df = pd.DataFrame(self.documents)
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main documents analysis
            documents_df.to_excel(writer, sheet_name='Document_Analysis', index=False)
            
            # Summary statistics
            summary_data = []
            for category, stats in self.analysis_results.items():
                if isinstance(stats, dict):
                    for key, value in stats.items():
                        summary_data.append({'Category': category, 'Item': key, 'Count': value})
                else:
                    summary_data.append({'Category': category, 'Item': 'Total', 'Count': stats})
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=False)
            
            # NADCAP priority documents
            nadcap_priority = documents_df[documents_df['nadcap_priority'].isin(['Critical', 'High'])]
            nadcap_priority.to_excel(writer, sheet_name='NADCAP_Priority', index=False)
            
            # Outdated documents
            outdated = documents_df[documents_df['assessed_status'].isin(['Outdated', 'Very Old'])]
            if not outdated.empty:
                outdated.to_excel(writer, sheet_name='Outdated_Documents', index=False)
            
            # SF/ZnNi specific documents
            sf_specific = documents_df[(documents_df['sf_specific'] == True) | (documents_df['zn_ni_specific'] == True)]
            if not sf_specific.empty:
                sf_specific.to_excel(writer, sheet_name='SF_ZnNi_Specific', index=False)
            
            # Documents by NADCAP relevance
            relevance_summary = documents_df.groupby('nadcap_relevance').agg({
                'document_name': 'count',
                'nadcap_priority': lambda x: f"Critical: {sum(x=='Critical')}, High: {sum(x=='High')}, Medium: {sum(x=='Medium')}, Low: {sum(x=='Low')}"
            }).rename(columns={'document_name': 'Document_Count'})
            relevance_summary.to_excel(writer, sheet_name='NADCAP_Relevance')
        
        print(f"📊 Analysis saved to: {filepath}")
        print(f"📈 Summary:")
        print(f"   • Total Documents: {self.analysis_results['total_documents']}")
        print(f"   • SF Specific: {self.analysis_results['sf_specific_count']}")
        print(f"   • ZnNi Specific: {self.analysis_results['zn_ni_specific_count']}")
        print(f"   • Critical Priority: {self.analysis_results['by_nadcap_priority'].get('Critical', 0)}")
        print(f"   • High Priority: {self.analysis_results['by_nadcap_priority'].get('High', 0)}")
        print(f"   • Outdated: {self.analysis_results['outdated_count']}")
        
        return filepath

def main():
    parser = argparse.ArgumentParser(description='Analyze SF document inventory for NADCAP')
    parser.add_argument('--input', '-i', default='sf_document_inventory.csv',
                      help='Input CSV file with document inventory')
    parser.add_argument('--output', '-o', default='outputs',
                      help='Output directory for Excel files')
    
    args = parser.parse_args()
    
    print("🚀 Document Inventory Analysis Started")
    print("=" * 50)
    
    try:
        analyzer = DocumentInventoryAnalyzer()
        success = analyzer.analyze_inventory(args.input)
        
        if success:
            output_file = analyzer.save_to_excel(args.output)
            print(f"\n✅ Analysis completed successfully!")
            print(f"📁 Output file: {output_file}")
        else:
            print("❌ Analysis failed")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
