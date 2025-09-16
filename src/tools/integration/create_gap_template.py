#!/usr/bin/env python3
"""
NADCAP Gap Analysis Template Generator
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
        """Create gap analysis template combining NADCAP requirements and document inventory"""
        print("🔄 Creating gap analysis template...")
        
        try:
            # Load NADCAP requirements
            print("📖 Loading NADCAP requirements...")
            req_df = pd.read_excel(requirements_file, sheet_name='High_Priority')
            print(f"✅ Loaded {len(req_df)} high-priority requirements")
            
            # Also load critical priority for comprehensive analysis
            try:
                all_req_df = pd.read_excel(requirements_file, sheet_name='NADCAP_Requirements')
                critical_req_df = all_req_df[all_req_df['SF_Relevance'] == 'Critical']
                print(f"✅ Added {len(critical_req_df)} critical-priority requirements")
                req_df = pd.concat([req_df, critical_req_df], ignore_index=True)
                # Remove duplicates
                req_df = req_df.drop_duplicates(subset=['Clause', 'Requirement'])
            except:
                print("ℹ️  Using high-priority requirements only")
            
            # Load document inventory
            print("📊 Loading document inventory...")
            doc_df = pd.read_excel(inventory_file, sheet_name='NADCAP_Priority')
            print(f"✅ Loaded {len(doc_df)} NADCAP-relevant documents")
            
            # Create gap analysis template
            for idx, req in req_df.iterrows():
                # Find potentially relevant documents
                relevant_docs = self._find_relevant_documents(req, doc_df)
                
                gap_entry = {
                    'NADCAP_Clause': req['Clause'],
                    'Requirement_Text': req['Requirement'][:200] + '...' if len(req['Requirement']) > 200 else req['Requirement'],
                    'Category': req['Category'],
                    'SF_Priority': req['SF_Relevance'],
                    'Audit_Risk': req['Audit_Risk'],
                    'ZnNi_Specific': req.get('ZnNi_Specific', False),
                    
                    # Documents to review (suggestions based on keywords)
                    'Potentially_Relevant_Documents': '; '.join(relevant_docs) if relevant_docs else 'No obvious matches - manual review needed',
                    
                    # Manual assessment fields
                    'Compliance_Status': '[SELECT: Compliant / Partial / Missing / Not Applicable]',
                    'Gap_Description': '[MANUAL INPUT: Describe any gaps or deficiencies]',
                    'Current_Documentation_Assessment': '[MANUAL INPUT: Evaluate adequacy of current docs]',
                    'Action_Required': '[MANUAL INPUT: What needs to be done?]',
                    'Priority': '[SELECT: Critical / High / Medium / Low]',
                    'Effort_Estimate': '[SELECT: 1-2 days / 1 week / 2-3 weeks / 1+ month]',
                    'Responsible_Person': '[SELECT: Mike Warriner / James Bick / James Fleming / Quality Manager / Other]',
                    'Target_Completion': '[DATE: YYYY-MM-DD]',
                    'Dependencies': '[MANUAL INPUT: Any dependencies or prerequisites]',
                    'NADCAP_Audit_Evidence': '[MANUAL INPUT: What evidence will auditor look for?]',
                    'Implementation_Notes': '[MANUAL INPUT: Implementation approach and considerations]',
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
        req_text = requirement['Requirement'].lower()
        req_category = requirement['Category'].lower()
        req_clause = requirement['Clause'].lower()
        
        relevant_docs = []
        
        # NADCAP-specific keywords to look for in documents
        doc_keywords = {
            'process control': ['process control', 'pcd', 'procedure', 'process'],
            'testing': ['test', 'inspection', 'lot test', 'periodic test'],
            'calibration': ['calibration', 'cal', 'equipment', 'instrument'],
            'training': ['training', 'competence', 'qualification', 'personnel'],
            'traceability': ['traceability', 'lot', 'batch', 'material id'],
            'buy-off': ['buy-off', 'sign-off', 'approval', 'verification'],
            'record': ['record', 'form', 'log', 'documentation'],
            'parameter': ['parameter', 'temperature', 'current', 'voltage', 'time'],
            'supplier': ['supplier', 'vendor', 'purchasing', 'material'],
            'quality system': ['quality', 'system', 'manual', 'policy'],
            'facility': ['facility', 'housekeeping', 'storage', 'environment'],
            'nonconforming': ['nonconform', 'deviation', 'rework', 'reject']
        }
        
        # Check each document
        for idx, doc in doc_df.iterrows():
            doc_name = doc['document_name'].lower()
            doc_desc = str(doc.get('description', '')).lower()
            doc_relevance = str(doc.get('nadcap_relevance', '')).lower()
            doc_text = f"{doc_name} {doc_desc} {doc_relevance}"
            
            # Direct clause matching
            if req_clause in doc_relevance:
                doc_ref = self._get_doc_reference(doc)
                relevant_docs.append(f"{doc['document_name']}{doc_ref}")
                continue
            
            # Look for keyword matches
            for keyword_category, keywords in doc_keywords.items():
                if keyword_category in req_text or keyword_category in req_category:
                    if any(keyword in doc_text for keyword in keywords):
                        doc_ref = self._get_doc_reference(doc)
                        relevant_docs.append(f"{doc['document_name']}{doc_ref}")
                        break
            
            # Check for ZnNi specific matching if requirement is ZnNi specific
            if requirement.get('ZnNi_Specific', False):
                zn_ni_keywords = ['zinc', 'nickel', 'zn', 'ni', 'plating', 'chemical']
                if any(keyword in doc_text for keyword in zn_ni_keywords):
                    doc_ref = self._get_doc_reference(doc)
                    relevant_docs.append(f"{doc['document_name']}{doc_ref}")
        
        return list(set(relevant_docs))  # Remove duplicates
    
    def _get_doc_reference(self, doc):
        """Get document reference for identification"""
        if pd.notna(doc.get('osr_ref', '')) and doc.get('osr_ref', ''):
            return f" (OSR: {doc['osr_ref']})"
        elif pd.notna(doc.get('cheops_ref', '')) and doc.get('cheops_ref', ''):
            return f" (CHEOPS: {doc['cheops_ref']})"
        else:
            return ""
    
    def _save_template(self, output_dir):
        """Save gap analysis template to Excel"""
        if not self.gap_template:
            print("❌ No template data to save!")
            return None
        
        df = pd.DataFrame(self.gap_template)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{output_dir}/NADCAP_GAP_ANALYSIS_TEMPLATE_UPDATED_{timestamp}.xlsx"
        
        # Create Excel with multiple sheets and formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main gap analysis template
            df.to_excel(writer, sheet_name='Gap_Analysis_Template', index=False)
            
            # Critical and high priority requirements only
            critical_high = df[df['SF_Priority'].isin(['Critical', 'High'])]
            critical_high.to_excel(writer, sheet_name='Critical_High_Priority', index=False)
            
            # ZnNi specific requirements
            zn_ni_specific = df[df['ZnNi_Specific'] == True]
            if not zn_ni_specific.empty:
                zn_ni_specific.to_excel(writer, sheet_name='ZnNi_Specific', index=False)
            
            # By audit risk level
            for risk_level in ['High', 'Medium', 'Low']:
                risk_df = df[df['Audit_Risk'] == risk_level]
                if not risk_df.empty:
                    risk_df.to_excel(writer, sheet_name=f'{risk_level}_Risk', index=False)
            
            # By NADCAP category
            categories = df['Category'].unique()
            for category in sorted(categories):
                cat_df = df[df['Category'] == category]
                sheet_name = category.replace(' ', '_').replace('(', '').replace(')', '')[:31]
                cat_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Instructions sheet
            instructions = pd.DataFrame([{
                'Section': 'NADCAP Gap Analysis Instructions',
                'Instructions': '''
1. COMPLIANCE STATUS OPTIONS:
   - Compliant: Requirement is fully met with adequate documentation
   - Partial: Requirement is partially met but has gaps or weaknesses
   - Missing: Requirement is not addressed or documented
   - Not Applicable: Requirement does not apply to ZnNi line operations

2. PRIORITY LEVELS:
   - Critical: Must be addressed before NADCAP audit
   - High: Should be addressed within 1-2 months
   - Medium: Should be addressed within 3-6 months
   - Low: Can be addressed as time permits

3. EFFORT ESTIMATES:
   - 1-2 days: Simple document updates or minor procedure changes
   - 1 week: New procedure development or moderate training
   - 2-3 weeks: Complex procedure development or system implementation
   - 1+ month: Major system changes or extensive training programs

4. RESPONSIBLE PERSONS:
   - Mike Warriner: Surface Finishing Operations Manager
   - James Bick: Technical Lead
   - James Fleming: Project Manager
   - Quality Manager: Quality system requirements
   - Other: Specify in notes

5. AUDIT EVIDENCE:
   Consider what the NADCAP auditor will look for:
   - Documentation (procedures, work instructions, records)
   - Implementation evidence (completed forms, training records)
   - Process verification (calibration records, test results)
   - Personnel competence (training completion, qualification records)

6. COMPLETION APPROACH:
   - Start with Critical and High priority items
   - Focus on ZnNi specific requirements first
   - Address high audit risk items early
   - Consider dependencies between requirements

7. REVIEW PROCESS:
   - Complete assessment for each requirement
   - Identify document gaps and needed actions
   - Estimate effort and assign responsibility
   - Create implementation timeline
   - Regular progress review meetings
                '''
            }])
            instructions.to_excel(writer, sheet_name='Instructions', index=False)
            
            # Summary statistics
            summary_data = []
            summary_data.append({'Metric': 'Total Requirements', 'Count': len(df)})
            summary_data.append({'Metric': 'Critical Priority', 'Count': len(df[df['SF_Priority'] == 'Critical'])})
            summary_data.append({'Metric': 'High Priority', 'Count': len(df[df['SF_Priority'] == 'High'])})
            summary_data.append({'Metric': 'ZnNi Specific', 'Count': len(df[df['ZnNi_Specific'] == True])})
            summary_data.append({'Metric': 'High Audit Risk', 'Count': len(df[df['Audit_Risk'] == 'High'])})
            
            # Category breakdown
            for category in df['Category'].value_counts().index:
                count = len(df[df['Category'] == category])
                summary_data.append({'Metric': f'Category: {category}', 'Count': count})
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"📊 Template saved to: {output_file}")
        print(f"📈 Summary: {len(self.gap_template)} requirements included")
        print(f"   • Critical: {len(df[df['SF_Priority']=='Critical'])}")
        print(f"   • High: {len(df[df['SF_Priority']=='High'])}")
        print(f"   • ZnNi Specific: {len(df[df['ZnNi_Specific']==True])}")
        print(f"   • High Risk: {len(df[df['Audit_Risk']=='High'])}")
        
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Create NADCAP gap analysis template')
    parser.add_argument('--requirements', '-r', required=True,
                      help='Requirements Excel file from extract_nadcap.py')
    parser.add_argument('--inventory', '-i', required=True,
                      help='Inventory analysis Excel file from analyze_inventory.py')
    parser.add_argument('--output', '-o', default='outputs',
                      help='Output directory for template file')
    
    args = parser.parse_args()
    
    print("🚀 Gap Analysis Template Generation Started")
    print("=" * 50)
    
    try:
        generator = GapAnalysisTemplateGenerator()
        output_file = generator.create_gap_template(
            args.requirements, 
            args.inventory, 
            args.output
        )
        
        if output_file:
            print(f"\n✅ Template generated successfully!")
            print(f"📁 Output file: {output_file}")
            print("\n🎯 Next steps:")
            print("   1. Open the Excel template")
            print("   2. Start with Critical_High_Priority sheet")
            print("   3. Complete manual assessment for each requirement")
            print("   4. Create implementation timeline based on priorities")
        else:
            print("❌ Template generation failed")
            
    except Exception as e:
        print(f"❌ Error during template generation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
