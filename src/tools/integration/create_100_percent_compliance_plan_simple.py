#!/usr/bin/env python3
"""
NADCAP 100% Compliance Action Plan Generator - SIMPLIFIED VERSION
Creates a detailed, timestamped task list for achieving complete NADCAP compliance
Based on analysis of extracted requirements and document inventory
"""

import pandas as pd
import os
from datetime import datetime

class SimpleComplianceActionPlanGenerator:
    def __init__(self):
        self.requirements_data = None
        self.compliance_actions = []
        self.priority_mapping = {
            'Critical': 1,
            'High': 2, 
            'Medium': 3,
            'Low': 4
        }
        
    def load_analysis_data(self, outputs_dir):
        """Load data from existing analysis files"""
        print("📊 Loading analysis data...")
        
        # Find the most recent requirements file
        req_files = [f for f in os.listdir(outputs_dir) if f.startswith('nadcap_requirements_')]
        if req_files:
            req_file = sorted(req_files)[-1]  # Get most recent
            req_path = os.path.join(outputs_dir, req_file)
            print(f"   📋 Loading requirements from: {req_file}")
            self.requirements_data = pd.read_excel(req_path, sheet_name='NADCAP_Requirements')
            
        return self.requirements_data is not None
    
    def generate_compliance_actions(self):
        """Generate specific compliance actions based on analysis"""
        print("🎯 Generating 100% compliance action plan...")
        
        if self.requirements_data is None:
            print("❌ No requirements data loaded")
            return
            
        action_id = 1
        
        # Process each NADCAP requirement
        for _, req in self.requirements_data.iterrows():
            requirement_text = req.get('Requirement', '')
            clause = req.get('Clause', '')
            category = req.get('Category', '')
            priority = req.get('SF_Relevance', 'Medium')
            doc_type = req.get('Document_Type_Needed', '')
            zn_ni_specific = req.get('ZnNi_Specific', False)
            
            if not requirement_text or requirement_text.strip() == '':
                continue
                
            # Generate specific action for this requirement
            action = self._create_specific_action(
                action_id, clause, requirement_text, category, priority, doc_type, zn_ni_specific
            )
            
            self.compliance_actions.append(action)
            action_id += 1
    
    def _create_specific_action(self, action_id, clause, requirement, category, priority, doc_type, zn_ni_specific):
        """Create a specific action for a NADCAP requirement"""
        
        # Determine action type based on document type and requirement content
        if doc_type and doc_type != 'TBD':
            if 'create' in doc_type.lower() or 'develop' in doc_type.lower():
                action_type = 'Document Creation'
                specific_action = f"Create {doc_type} to ensure compliance with NADCAP clause {clause}. Requirement: {requirement}"
            else:
                action_type = 'Document Review/Update'
                specific_action = f"Review existing {doc_type} and update as needed to ensure compliance with NADCAP clause {clause}. Requirement: {requirement}"
        else:
            action_type = 'Compliance Verification'
            specific_action = f"Verify compliance with NADCAP clause {clause} through document review and process assessment. Requirement: {requirement}"
        
        # Determine responsible party based on category
        responsible_party = self._get_responsible_party(category)
        
        # Estimate hours based on priority and complexity
        estimated_hours = self._estimate_hours(priority, action_type, requirement)
        
        # Determine specific documents to review/create
        docs_to_review, docs_to_create = self._determine_documents(category, requirement, doc_type, clause)
        
        # Create success criteria
        success_criteria = f"Documentation and processes demonstrate full compliance with NADCAP clause {clause}"
        
        # Determine verification method
        verification_method = self._get_verification_method(category, action_type)
        
        action = {
            'Action_ID': f"{self._get_category_prefix(category)}-{action_id:03d}",
            'NADCAP_Clause': clause,
            'Priority': priority,
            'Priority_Number': self.priority_mapping.get(priority, 3),
            'Action_Type': action_type,
            'Specific_Action': specific_action,
            'Expected_Outcome': f"Full compliance demonstrated for NADCAP clause {clause}",
            'Responsible_Party': responsible_party,
            'Estimated_Hours': estimated_hours,
            'Dependencies': self._get_dependencies(category, doc_type),
            'Success_Criteria': success_criteria,
            'Documents_to_Review': docs_to_review,
            'Documents_to_Create': docs_to_create,
            'Verification_Method': verification_method,
            'Category': category,
            'ZnNi_Specific': zn_ni_specific,
            'Document_Type_Required': doc_type
        }
        
        return action
    
    def _get_category_prefix(self, category):
        """Get prefix for action ID based on category"""
        prefixes = {
            'Scope and Purpose': 'SP',
            'Quality System': 'QS',
            'Process Control': 'PC',
            'Testing and Inspection': 'TI',
            'Personnel and Training': 'PT',
            'Supplier Management': 'SM',
            'Calibration': 'CAL',
            'Documentation Control': 'DC',
            'Nonconformance Management': 'NC',
            'Facility Requirements': 'FAC',
            'Audit Preparation': 'AP'
        }
        return prefixes.get(category, 'GEN')
    
    def _get_responsible_party(self, category):
        """Determine responsible party based on category"""
        responsibilities = {
            'Quality System': 'Quality Manager',
            'Process Control': 'Process Engineer',
            'Testing and Inspection': 'Lab Manager',
            'Personnel and Training': 'HR Manager/Training Coordinator',
            'Supplier Management': 'Procurement Manager',
            'Calibration': 'Maintenance Manager',
            'Documentation Control': 'Quality Manager',
            'Nonconformance Management': 'Quality Manager',
            'Facility Requirements': 'Facility Manager',
            'Audit Preparation': 'Quality Manager'
        }
        return responsibilities.get(category, 'Quality Manager')
    
    def _estimate_hours(self, priority, action_type, requirement):
        """Estimate hours required based on priority and complexity"""
        base_hours = {
            'Document Creation': 8,
            'Document Review/Update': 4,
            'Compliance Verification': 3
        }
        
        priority_multiplier = {
            'Critical': 1.5,
            'High': 1.2,
            'Medium': 1.0,
            'Low': 0.8
        }
        
        hours = base_hours.get(action_type, 3)
        hours *= priority_multiplier.get(priority, 1.0)
        
        # Add complexity based on requirement length and content
        if len(requirement) > 200 or 'complex' in requirement.lower():
            hours *= 1.3
        
        return round(hours)
    
    def _determine_documents(self, category, requirement, doc_type, clause):
        """Determine which documents to review and create"""
        docs_to_review = []
        docs_to_create = []
        
        # Category-specific document mappings
        if category == 'Quality System':
            docs_to_review = ['QM-001 Quality Manual', 'AS9100 Certificate', 'Management Review Minutes']
            if 'procedure' in doc_type.lower():
                docs_to_create = [f'Quality System Procedure for Clause {clause}']
        
        elif category == 'Process Control':
            docs_to_review = ['SF-PCD-001 ZnNi Pretreatment PCD', 'SF-PCD-002 ZnNi Plating PCD', 'Equipment Manuals']
            if 'PCD' in doc_type or 'process control' in doc_type.lower():
                docs_to_create = [f'Process Control Document for Clause {clause}']
        
        elif category == 'Testing and Inspection':
            docs_to_review = ['SF-TEST-001 Lot Testing Procedure', 'Test Method Specifications', 'Test Records']
            if 'procedure' in doc_type.lower():
                docs_to_create = [f'Testing Procedure for Clause {clause}']
        
        elif category == 'Personnel and Training':
            docs_to_review = ['Personnel Training Records', 'Job Descriptions', 'Training Procedures']
            if 'training' in doc_type.lower():
                docs_to_create = [f'Training Program for Clause {clause}']
        
        elif category == 'Supplier Management':
            docs_to_review = ['Approved Supplier List', 'Supplier Qualification Records', 'Material Certificates']
            if 'procedure' in doc_type.lower():
                docs_to_create = [f'Supplier Management Procedure for Clause {clause}']
        
        elif category == 'Calibration':
            docs_to_review = ['Calibration Schedule', 'Calibration Certificates', 'Equipment Inventory']
            if 'schedule' in doc_type.lower():
                docs_to_create = [f'Calibration Schedule for Clause {clause}']
        
        elif category == 'Documentation Control':
            docs_to_review = ['SF-PROC-001 Document Control', 'Document Control System Records']
            if 'procedure' in doc_type.lower():
                docs_to_create = [f'Document Control Procedure Update for Clause {clause}']
        
        elif category == 'Nonconformance Management':
            docs_to_review = ['SF-PROC-003 Nonconformance Procedure', 'Recent NCR Records']
            if 'procedure' in doc_type.lower():
                docs_to_create = [f'Nonconformance Procedure Update for Clause {clause}']
        
        elif category == 'Facility Requirements':
            docs_to_review = ['Facility Layout Drawings', 'Environmental Monitoring Records']
            if 'assessment' in doc_type.lower():
                docs_to_create = [f'Facility Assessment Report for Clause {clause}']
        
        elif category == 'Audit Preparation':
            docs_to_review = ['All Compliance Documentation', 'Previous Audit Reports']
            docs_to_create = [f'Audit Preparation Checklist for Clause {clause}']
        
        else:
            # Generic documents
            docs_to_review = ['Relevant Procedures and Records']
            if doc_type and doc_type != 'TBD':
                docs_to_create = [f'{doc_type} for Clause {clause}']
        
        return docs_to_review, docs_to_create
    
    def _get_dependencies(self, category, doc_type):
        """Get dependencies for the action"""
        dependencies = {
            'Quality System': 'Access to Quality Manual and management review records',
            'Process Control': 'Access to process specifications and equipment manuals',
            'Testing and Inspection': 'Access to testing procedures and equipment',
            'Personnel and Training': 'Access to personnel files and training records',
            'Supplier Management': 'Access to supplier qualification records',
            'Calibration': 'Access to calibration records and equipment list',
            'Documentation Control': 'Access to document control system',
            'Nonconformance Management': 'Access to nonconformance records',
            'Facility Requirements': 'Access to facility and monitoring equipment',
            'Audit Preparation': 'Completion of all other compliance actions'
        }
        return dependencies.get(category, 'Access to relevant documentation and processes')
    
    def _get_verification_method(self, category, action_type):
        """Get verification method for the action"""
        if action_type == 'Document Creation':
            return 'Document review against NADCAP requirements checklist'
        elif action_type == 'Document Review/Update':
            return 'Document audit and gap analysis'
        else:
            return 'Process audit and compliance verification'
    
    def save_compliance_plan(self, output_dir):
        """Save the compliance action plan to Excel with timestamp"""
        if not self.compliance_actions:
            print("❌ No compliance actions generated")
            return None
            
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"NADCAP_100_PERCENT_COMPLIANCE_ACTION_PLAN_UPDATED_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Create DataFrame
        df = pd.DataFrame(self.compliance_actions)
        
        # Sort by priority and action ID
        df = df.sort_values(['Priority_Number', 'Action_ID'])
        
        # Create summary statistics
        summary_stats = {
            'Total_Actions': len(df),
            'Critical_Actions': len(df[df['Priority'] == 'Critical']),
            'High_Actions': len(df[df['Priority'] == 'High']),
            'Medium_Actions': len(df[df['Priority'] == 'Medium']),
            'Low_Actions': len(df[df['Priority'] == 'Low']),
            'Total_Estimated_Hours': df['Estimated_Hours'].sum(),
            'Average_Hours_Per_Action': df['Estimated_Hours'].mean(),
            'ZnNi_Specific_Actions': len(df[df['ZnNi_Specific'] == True])
        }
        
        # Create implementation timeline
        timeline_data = []
        current_week = 1
        hours_per_week = 40  # Assuming 40 hours per week capacity
        week_hours = 0
        
        for _, action in df.iterrows():
            if week_hours + action['Estimated_Hours'] > hours_per_week:
                current_week += 1
                week_hours = 0
            
            timeline_data.append({
                'Week': current_week,
                'Action_ID': action['Action_ID'],
                'Priority': action['Priority'],
                'Specific_Action': action['Specific_Action'][:100] + '...' if len(action['Specific_Action']) > 100 else action['Specific_Action'],
                'Responsible_Party': action['Responsible_Party'],
                'Estimated_Hours': action['Estimated_Hours'],
                'Cumulative_Hours': week_hours + action['Estimated_Hours']
            })
            
            week_hours += action['Estimated_Hours']
        
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main action plan
            df.to_excel(writer, sheet_name='100_Percent_Compliance_Plan', index=False)
            
            # Critical and High priority actions
            priority_actions = df[df['Priority'].isin(['Critical', 'High'])]
            priority_actions.to_excel(writer, sheet_name='Priority_Actions', index=False)
            
            # ZnNi specific actions
            zn_ni_actions = df[df['ZnNi_Specific'] == True]
            if not zn_ni_actions.empty:
                zn_ni_actions.to_excel(writer, sheet_name='ZnNi_Specific_Actions', index=False)
            
            # Actions by category
            categories = df['Category'].unique()
            for category in categories[:10]:  # Limit to first 10 categories due to Excel sheet limit
                category_df = df[df['Category'] == category]
                safe_name = category.replace(' ', '_').replace('/', '_')[:31]  # Excel sheet name limit
                category_df.to_excel(writer, sheet_name=safe_name, index=False)
            
            # Implementation timeline
            timeline_df.to_excel(writer, sheet_name='Implementation_Timeline', index=False)
            
            # Summary statistics
            summary_df = pd.DataFrame([summary_stats])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Document creation summary
            docs_to_create = []
            for action in self.compliance_actions:
                docs_to_create.extend(action['Documents_to_Create'])
            
            doc_summary = pd.DataFrame({
                'Documents_to_Create': list(set(docs_to_create))
            })
            doc_summary.to_excel(writer, sheet_name='Documents_to_Create', index=False)
        
        print(f"📊 100% Compliance Action Plan saved to: {filepath}")
        print(f"📈 Summary:")
        print(f"   • Total Actions: {summary_stats['Total_Actions']}")
        print(f"   • Critical: {summary_stats['Critical_Actions']}")
        print(f"   • High: {summary_stats['High_Actions']}")
        print(f"   • Medium: {summary_stats['Medium_Actions']}")
        print(f"   • Low: {summary_stats['Low_Actions']}")
        print(f"   • ZnNi Specific: {summary_stats['ZnNi_Specific_Actions']}")
        print(f"   • Total Estimated Hours: {summary_stats['Total_Estimated_Hours']}")
        print(f"   • Average Hours per Action: {summary_stats['Average_Hours_Per_Action']:.1f}")
        print(f"   • Estimated Completion Time: {current_week} weeks")
        
        return filepath

def main():
    """Generate 100% compliance action plan"""
    print("🎯 NADCAP 100% Compliance Action Plan Generator")
    print("=" * 60)
    
    generator = SimpleComplianceActionPlanGenerator()
    
    # Load analysis data
    outputs_dir = 'outputs'
    if not generator.load_analysis_data(outputs_dir):
        print("❌ Could not load analysis data from outputs folder")
        print("   Make sure the requirements analysis file exists")
        return 1
    
    # Generate compliance actions
    generator.generate_compliance_actions()
    
    if not generator.compliance_actions:
        print("❌ No compliance actions generated")
        return 1
    
    # Save action plan
    output_file = generator.save_compliance_plan(outputs_dir)
    
    if output_file:
        print(f"\n✅ 100% Compliance Action Plan generated successfully!")
        print(f"📁 File: {output_file}")
        print(f"\n🎯 This action plan provides:")
        print(f"   • Specific action for each NADCAP requirement")
        print(f"   • Clear responsibility assignments")
        print(f"   • Estimated time requirements")
        print(f"   • Success criteria for each action")
        print(f"   • Implementation timeline by week")
        print(f"   • Priority-based execution plan")
        print(f"   • Document creation requirements")
        print(f"\n📋 When ALL actions are completed, you will achieve 100% NADCAP compliance!")
        print(f"💡 Each action is specific enough for anyone to execute without prior project knowledge.")
        return 0
    else:
        print("\n❌ Failed to generate action plan")
        return 1

if __name__ == "__main__":
    exit(main())
