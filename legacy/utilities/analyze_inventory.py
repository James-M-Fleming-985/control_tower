#!/usr/bin/env python3
"""
Document Inventory Analyzer
Analyzes and categorizes SF document inventory for AS9100 gap analysis
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
    
    def determine_as9100_relevance(self, doc_name, doc_type, description=""):
        """Determine potential AS9100 clause relevance"""
        text_to_analyze = f"{doc_name} {doc_type} {description}".lower()
        
        relevance_mapping = {
            'Documentation Control (7.5)': ['document control', 'version control', 'document management'],
            'Process Control (8.1/8.5)': ['process', 'procedure', 'operation', 'production', 'manufacturing'],
            'Work Instructions (8.5)': ['work instruction', 'wi', 'method', 'step-by-step'],
            'Training/Competence (7.2)': ['training', 'competence', 'qualification', 'skill'],
            'Records (7.5.3)': ['record', 'form', 'log', 'register', 'checklist'],
            'Quality Planning (8.1)': ['quality plan', 'planning', 'schedule'],
            'Maintenance (8.5.1)': ['maintenance', 'calibration', 'equipment'],
            'Safety (8.8)': ['safety', 'hazard', 'chemical', 'ppe'],
            'Nonconformity (8.7/10.2)': ['nonconform', 'defect', 'corrective', 'deviation'],
            'Monitoring (9.1)': ['monitoring', 'measurement', 'inspection', 'test']
        }
        
        matches = []
        for clause, keywords in relevance_mapping.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                matches.append(clause)
        
        return '; '.join(matches) if matches else 'General'
    
    def analyze_inventory(self, csv_path):
        """Analyze the document inventory"""
        print(f"📊 Analyzing document inventory: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            print(f"📄 Found {len(df)} documents to analyze")
            
            # Analyze each document
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
                    
                    # Analysis results
                    'categorized_type': self.categorize_document_type(
                        row.get('Document_Name', ''), 
                        row.get('Document_Type', '')
                    ),
                    'assessed_status': self.assess_document_status(
                        row.get('Last_Modified', ''),
                        row.get('Status', '')
                    ),
                    'as9100_relevance': self.determine_as9100_relevance(
                        row.get('Document_Name', ''),
                        row.get('Document_Type', ''),
                        row.get('Description', '')
                    ),
                    'sf_specific': 'sf' in row.get('Document_Name', '').lower() or 'surface' in row.get('Document_Name', '').lower(),
                    'analysis_timestamp': datetime.now().isoformat()
                }
                
                self.documents.append(doc_analysis)
            
            # Generate summary statistics
            self.analysis_results = self._generate_summary()
            
        except Exception as e:
            print(f"❌ Error analyzing inventory: {e}")
            return None
        
        print("✅ Inventory analysis complete!")
        return self.documents
    
    def _generate_summary(self):
        """Generate summary statistics"""
        df = pd.DataFrame(self.documents)
        
        summary = {
            'total_documents': len(df),
            'by_type': df['categorized_type'].value_counts().to_dict(),
            'by_status': df['assessed_status'].value_counts().to_dict(),
            'sf_specific_count': df['sf_specific'].sum(),
            'documents_needing_update': len(df[df['assessed_status'].isin(['Outdated', 'Very Old'])]),
            'current_documents': len(df[df['assessed_status'] == 'Current']),
        }
        
        return summary
    
    def print_summary(self):
        """Print analysis summary"""
        print("\n📊 DOCUMENT INVENTORY ANALYSIS SUMMARY:")
        print(f"📁 Total documents: {self.analysis_results['total_documents']}")
        print(f"🎯 SF-specific documents: {self.analysis_results['sf_specific_count']}")
        print(f"✅ Current documents: {self.analysis_results['current_documents']}")
        print(f"⚠️  Documents needing update: {self.analysis_results['documents_needing_update']}")
        
        print("\n📋 Document Types:")
        for doc_type, count in self.analysis_results['by_type'].items():
            print(f"  • {doc_type}: {count}")
        
        print("\n📅 Document Status:")
        for status, count in self.analysis_results['by_status'].items():
            print(f"  • {status}: {count}")
    
    def save_results(self, output_dir):
        """Save analysis results to Excel"""
        if not self.documents:
            print("❌ No documents to save!")
            return None
        
        df = pd.DataFrame(self.documents)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = f"{output_dir}/document_inventory_analysis_{timestamp}.xlsx"
        
        # Create Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main analysis sheet
            df.to_excel(writer, sheet_name='Document_Analysis', index=False)
            
            # SF-specific documents
            sf_docs = df[df['sf_specific'] == True]
            sf_docs.to_excel(writer, sheet_name='SF_Specific_Documents', index=False)
            
            # Documents needing update
            outdated = df[df['assessed_status'].isin(['Outdated', 'Very Old'])]
            outdated.to_excel(writer, sheet_name='Documents_Need_Update', index=False)
            
            # By document type
            for doc_type in df['categorized_type'].unique():
                type_docs = df[df['categorized_type'] == doc_type]
                sheet_name = doc_type.replace('/', '_').replace(' ', '_')[:31]
                type_docs.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Summary statistics
            summary_df = pd.DataFrame([self.analysis_results])
            summary_df.to_excel(writer, sheet_name='Analysis_Summary', index=False)
        
        print(f"💾 Analysis saved to: {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Analyze SF document inventory for AS9100 gap analysis')
    parser.add_argument('--input', required=True, help='Path to document inventory CSV file')
    parser.add_argument('--output', default='outputs', help='Output directory for results')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        print("\n📁 Please create your document inventory CSV using the template")
        return
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Analyze inventory
    analyzer = DocumentInventoryAnalyzer()
    documents = analyzer.analyze_inventory(args.input)
    
    if documents:
        # Print summary
        analyzer.print_summary()
        
        # Save results
        output_file = analyzer.save_results(args.output)
        
        print("\n🎯 NEXT STEPS:")
        print("1. Review the generated Excel file")
        print("2. Focus on 'SF_Specific_Documents' sheet")
        print("3. Check 'Documents_Need_Update' for priority updates")
        print("4. Use this analysis for AS9100 gap assessment")
    
    return output_file

if __name__ == "__main__":
    main()
