#!/usr/bin/env python3
"""
AS9100 Gap Analysis Template Generator
Creates structured template for manual compliance assessment
"""

import pandas as pd
import argparse
import os
from datetime import datetime

class GapAnalysisTemplateGenerator:
    def __init__(self):
        self.gap_template = []
        
    def create_gap_template(self, requirements_file, inventory_file, output_dir):
        """Create gap analysis template combining AS9100 requirements and document inventory"""
        print("🔄 Creating gap analysis template...")
        
        try:
            # Load AS9100 requirements
            print("📖 Loading AS9100 requirements...")
            req_df = pd.read_excel(requirements_file, sheet_name='SF_High_Priority')
            print(f"✅ Loaded {len(req_df)} high-priority requirements")
            
            # Also load medium priority for comprehensive analysis
            try:
                all_req_df = pd.read_excel(requirements_file, sheet_name='All_Requirements')
                medium_req_df = all_req_df[all_req_df['sf_relevance'] == 'Medium']
                print(f"✅ Added {len(medium_req_df)} medium-priority requirements")
                req_df = pd.concat([req_df, medium_req_df], ignore_index=True)
            except:
                print("ℹ️  Using high-priority requirements only")
            
            # Load document inventory
            print("📊 Loading document inventory...")
            doc_df = pd.read_excel(inventory_file, sheet_name='SF_Specific_Documents')
            print(f"✅ Loaded {len(doc_df)} SF-specific documents")
            
            # Create gap analysis template
            for idx, req in req_df.iterrows():
                # Find potentially relevant documents
                relevant_docs = self._find_relevant_documents(req, doc_df)
                
                gap_entry = {
                    'AS9100_Clause': req['clause'],
                    'Requirement_Text': req['requirement'][:200] + '...' if len(req['requirement']) > 200 else req['requirement'],
                    'Category': req['category'],
                    'SF_Priority': req['sf_relevance'],
                    'Page_Reference': req['page'],
                    
                    # Documents to review (suggestions based on keywords)
                    'Potentially_Relevant_Documents': '; '.join(relevant_docs) if relevant_docs else 'No obvious matches - manual review needed',
                    
                    # Manual assessment fields
                    'Compliance_Status': '[SELECT: Compliant / Partial / Missing / Not Applicable]',
                    'Gap_Description': '[MANUAL INPUT: Describe any gaps or deficiencies]',
                    'Current_Documentation_Assessment': '[MANUAL INPUT: Evaluate adequacy of current docs]',
                    'Action_Required': '[MANUAL INPUT: What needs to be done?]',
                    'Priority': '[SELECT: Critical / High / Medium / Low]',
                    'Effort_Estimate': '[SELECT: 1-2 days / 1 week / 2-3 weeks / 1+ month]',
                    'Responsible_Person': '[SELECT: Mike Warriner / James Bick / James Fleming / Other]',
                    'Target_Completion': '[DATE: YYYY-MM-DD]',
                    'Dependencies': '[MANUAL INPUT: Any dependencies or prerequisites]',
                    'Notes': '[MANUAL INPUT: Additional notes or considerations]'
                }
                
                self.gap_template.append(gap_entry)
            
            # Save template
            output_file = self._save_template(output_dir)
            print(f"✅ Gap analysis template created: {output_file}")
            
            return output_file
            
        except Exception as e:
            print(f"❌ Error creating gap template: {e}")
            return None
    
    def _find_relevant_documents(self, requirement, doc_df):
        """Find documents that might be relevant to a requirement"""
        req_text = requirement['requirement'].lower()
        req_category = requirement['category'].lower()
        
        relevant_docs = []
        
        # Keywords to look for in documents
        doc_keywords = {
            'documented information': ['document', 'procedure', 'policy', 'manual'],
            'process': ['process', 'procedure', 'method'],
            'work instruction': ['work instruction', 'wi', 'method'],
            'record': ['record', 'form', 'log', 'register'],
            'training': ['training', 'competence', 'qualification'],
            'control': ['control', 'management', 'planning'],
            'maintenance': ['maintenance', 'calibration', 'equipment'],
            'quality': ['quality', 'inspection', 'test', 'check']
        }
        
        # Check each document
        for idx, doc in doc_df.iterrows():
            doc_name = doc['document_name'].lower()
            doc_desc = str(doc.get('description', '')).lower()
            doc_text = f"{doc_name} {doc_desc}"
            
            # Look for keyword matches
            for keyword_category, keywords in doc_keywords.items():
                if keyword_category in req_text or keyword_category in req_category:
                    if any(keyword in doc_text for keyword in keywords):
                        # Include reference numbers for better identification
                        doc_ref = ""
                        if pd.notna(doc.get('osr_ref', '')) and doc.get('osr_ref', ''):
                            doc_ref = f" (OSR: {doc['osr_ref']})"
                        elif pd.notna(doc.get('cheops_ref', '')) and doc.get('cheops_ref', ''):
                            doc_ref = f" (CHEOPS: {doc['cheops_ref']})"
                        
                        relevant_docs.append(f"{doc['document_name']}{doc_ref}")
                        break
        
        return list(set(relevant_docs))  # Remove duplicates
    
    def _save_template(self, output_dir):
        """Save gap analysis template to Excel"""
        if not self.gap_template:
            print("❌ No template data to save!")
            return None
        
        df = pd.DataFrame(self.gap_template)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = f"{output_dir}/gap_analysis_template_{timestamp}.xlsx"
        
        # Create Excel with multiple sheets and formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main gap analysis template
            df.to_excel(writer, sheet_name='Gap_Analysis_Template', index=False)
            
            # High priority requirements only
            high_priority = df[df['SF_Priority'] == 'High']
            high_priority.to_excel(writer, sheet_name='High_Priority_Only', index=False)
            
            # By category for organized review
            categories = df['Category'].unique()
            for category in sorted(categories):
                cat_df = df[df['Category'] == category]
                sheet_name = category.replace(' ', '_')[:31]
                cat_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Instructions sheet
            instructions = pd.DataFrame([{
                'Instructions': 'AS9100 Gap Analysis Template - How to Use',
                'Step_1': 'Review each requirement in the Gap_Analysis_Template sheet',
                'Step_2': 'For each row, read the AS9100 requirement carefully',
                'Step_3': 'Review the suggested documents (if any)',
                'Step_4': 'Assess compliance status: Compliant/Partial/Missing/Not Applicable',
                'Step_5': 'Describe any gaps in the Gap_Description field',
                'Step_6': 'Specify required actions and assign responsibility',
                'Step_7': 'Set priorities and target completion dates',
                'Step_8': 'Focus on High_Priority_Only sheet first',
                'Note': 'This template requires manual expert review - automation cannot determine actual compliance'
            }])
            instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Generate AS9100 gap analysis template')
    parser.add_argument('--requirements', required=True, help='Path to AS9100 requirements Excel file')
    parser.add_argument('--inventory', required=True, help='Path to document inventory analysis Excel file')
    parser.add_argument('--output', default='outputs', help='Output directory for template')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.requirements):
        print(f"❌ Error: Requirements file not found: {args.requirements}")
        return
    
    if not os.path.exists(args.inventory):
        print(f"❌ Error: Inventory file not found: {args.inventory}")
        return
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Generate template
    generator = GapAnalysisTemplateGenerator()
    template_file = generator.create_gap_template(args.requirements, args.inventory, args.output)
    
    if template_file:
        print("\n🎯 GAP ANALYSIS TEMPLATE READY!")
        print("📋 Next steps:")
        print("1. Open the generated Excel template")
        print("2. Start with 'High_Priority_Only' sheet")
        print("3. Review each requirement manually with Mike Warriner & James Bick")
        print("4. Complete compliance assessment for each row")
        print("5. Use results to create action plan")
        print("\n⚠️  IMPORTANT: This template requires expert manual review")
        print("   Automation cannot determine actual compliance levels")
    
    return template_file

if __name__ == "__main__":
    main()
