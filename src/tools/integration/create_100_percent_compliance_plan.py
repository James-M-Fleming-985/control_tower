#!/usr/bin/env python3
"""
NADCAP 100% Compliance Action Plan Generator
Creates a detailed, timestamped task list for achieving complete NADCAP compliance
Based on analysis of extracted requirements and document inventory
"""

import pandas as pd
import os
from datetime import datetime
import json

class ComplianceActionPlanGenerator:
    def __init__(self):
        self.requirements_data = None
        self.inventory_data = None
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
            # Try different sheet names based on file version
            try:
                self.requirements_data = pd.read_excel(req_path, sheet_name='Audit_Questions')
            except ValueError:
                # Fallback to older format
                self.requirements_data = pd.read_excel(req_path, sheet_name='NADCAP_Requirements')
                print("   📝 Using NADCAP_Requirements sheet (older format)")
        
        # Find the most recent inventory analysis file
        inv_files = [f for f in os.listdir(outputs_dir) if f.startswith('document_inventory_analysis_')]
        if inv_files:
            inv_file = sorted(inv_files)[-1]  # Get most recent
            inv_path = os.path.join(outputs_dir, inv_file)
            print(f"   📄 Loading inventory from: {inv_file}")
            try:
                self.inventory_data = pd.read_excel(inv_path, sheet_name='Document_Analysis')
            except ValueError:
                # Fallback to first sheet
                self.inventory_data = pd.read_excel(inv_path, sheet_name=0)
                print("   📝 Using first sheet (fallback)")
            
        return self.requirements_data is not None and self.inventory_data is not None
    
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
            
            if not requirement_text or requirement_text.strip() == '':
                continue
                
            # Generate specific actions based on requirement type and current gaps
            actions = self._create_actions_for_requirement(
                action_id, clause, requirement_text, category, priority, doc_type
            )
            
            self.compliance_actions.extend(actions)
            action_id += len(actions)
    
    def _create_actions_for_requirement(self, start_id, clause, requirement_text, category, priority, doc_type):
        """Create specific actions for a NADCAP requirement"""
        actions = []
        
        # Clean up the requirement text
        clean_requirement = requirement_text.replace('\n', ' ').replace('  ', ' ').strip()
        
        # Map categories to SF document types and actions
        action_templates = {
            'Quality System': self._quality_system_actions,
            'Process Control': self._process_control_actions,
            'Testing and Inspection': self._testing_inspection_actions,
            'Personnel and Training': self._personnel_training_actions,
            'Supplier Management': self._supplier_management_actions,
            'Calibration': self._calibration_actions,
            'Documentation Control': self._documentation_control_actions,
            'Nonconformance Management': self._nonconformance_actions,
            'Facility Requirements': self._facility_actions,
            'Audit Preparation': self._audit_prep_actions
        }
        
        # Get category-specific actions
        if category in action_templates:
            category_actions = action_templates[category](start_id, clause, clean_requirement, priority, doc_type)
            actions.extend(category_actions)
        else:
            # Generic action for uncategorized requirements
            actions.append(self._create_generic_action(start_id, clause, clean_requirement, priority, doc_type))
            
        return actions
    
    def _quality_system_actions(self, action_id, clause, requirement, priority, doc_type):
        """Generate quality system related actions"""
        actions = []
        
        if 'AS9100' in requirement or 'ISO 9001' in requirement:
            actions.append({
                'Action_ID': f"QS-{action_id:03d}",
                'NADCAP_Clause': clause,
                'Priority': priority,
                'Priority_Number': self.priority_mapping.get(priority, 3),
                'Action_Type': 'Document Review',
                'Specific_Action': f"Review Quality Manual (QM-001) to verify compliance with NADCAP clause {clause}. Requirement: {requirement}",
                'Expected_Outcome': f"Quality Manual demonstrates compliance with clause {clause}",
                'Responsible_Party': 'Quality Manager',
                'Estimated_Hours': 2,
                'Dependencies': 'Access to current Quality Manual',
                'Success_Criteria': 'Quality Manual explicitly addresses requirement and references NADCAP compliance',
                'Documents_to_Review': ['QM-001 Quality Manual', 'AS9100 Certificate'],
                'Documents_to_Create': [],
                'Verification_Method': 'Document audit against NADCAP clause',
                'Category': 'Quality System'
            })
        
        if 'management review' in question.lower():
            actions.append({
                'Action_ID': f"QS-{action_id+1:03d}",
                'NADCAP_Clause': clause,
                'Priority': priority,
                'Priority_Number': self.priority_mapping.get(priority, 3),
                'Action_Type': 'Process Verification',
                'Specific_Action': f"Review last 3 management review meeting minutes to ensure NADCAP compliance is addressed. Requirement: {question}",
                'Expected_Outcome': f"Management review process includes NADCAP compliance monitoring",
                'Responsible_Party': 'Quality Manager',
                'Estimated_Hours': 3,
                'Dependencies': 'Access to management review minutes',
                'Success_Criteria': 'NADCAP compliance is agenda item in management reviews',
                'Documents_to_Review': ['Management Review Minutes (last 3)', 'Management Review Procedure'],
                'Documents_to_Create': ['Updated Management Review Agenda Template (if needed)'],
                'Verification_Method': 'Review meeting minutes and interview management',
                'Category': 'Quality System'
            })
        
        return actions
    
    def _process_control_actions(self, action_id, clause, question, priority):
        """Generate process control related actions"""
        actions = []
        
        if 'process control document' in question.lower() or 'PCD' in question:
            actions.append({
                'Action_ID': f"PC-{action_id:03d}",
                'NADCAP_Clause': clause,
                'Priority': priority,
                'Priority_Number': self.priority_mapping.get(priority, 3),
                'Action_Type': 'Document Review/Creation',
                'Specific_Action': f"Review ZnNi process control documents (SF-PCD-001, SF-PCD-002) for compliance with clause {clause}. Create missing PCDs if gaps identified. Requirement: {question}",
                'Expected_Outcome': f"All ZnNi processes have compliant process control documents",
                'Responsible_Party': 'Process Engineer',
                'Estimated_Hours': 8,
                'Dependencies': 'Access to current process specifications, equipment manuals',
                'Success_Criteria': 'Each ZnNi process has detailed PCD covering all NADCAP requirements',
                'Documents_to_Review': ['SF-PCD-001 ZnNi Pretreatment', 'SF-PCD-002 ZnNi Plating', 'Equipment Manuals'],
                'Documents_to_Create': ['Updated PCDs (if gaps found)', 'Process Flow Diagrams'],
                'Verification_Method': 'Document review against NADCAP PCD requirements checklist',
                'Category': 'Process Control'
            })
        
        if 'buy-off' in question.lower() or 'buyoff' in question.lower():
            actions.append({
                'Action_ID': f"PC-{action_id+1:03d}",
                'NADCAP_Clause': clause,
                'Priority': priority,
                'Priority_Number': self.priority_mapping.get(priority, 3),
                'Action_Type': 'Procedure Verification',
                'Specific_Action': f"Review buy-off procedure (SF-PROC-005) to ensure compliance with clause {clause}. Verify traceability and documentation requirements. Requirement: {question}",
                'Expected_Outcome': f"Buy-off procedure meets all NADCAP traceability requirements",
                'Responsible_Party': 'Quality Engineer',
                'Estimated_Hours': 4,
                'Dependencies': 'Access to buy-off procedure and recent buy-off records',
                'Success_Criteria': 'Buy-off procedure includes all NADCAP-required elements',
                'Documents_to_Review': ['SF-PROC-005 Buy-off Procedure', 'Recent buy-off records (last 10)'],
                'Documents_to_Create': ['Updated buy-off procedure (if needed)', 'Buy-off checklist'],
                'Verification_Method': 'Procedure review and record sampling',
                'Category': 'Process Control'
            })
            
        return actions
    
    def _testing_inspection_actions(self, action_id, clause, question, priority):
        """Generate testing and inspection related actions"""
        actions = []
        
        if 'lot testing' in question.lower():
            actions.append({
                'Action_ID': f"TI-{action_id:03d}",
                'NADCAP_Clause': clause,
                'Priority': priority,
                'Priority_Number': self.priority_mapping.get(priority, 3),
                'Action_Type': 'Procedure Review/Update',
                'Specific_Action': f"Review lot testing procedure (SF-TEST-001) for compliance with clause {clause}. Verify test methods, frequency, and documentation. Requirement: {question}",
                'Expected_Outcome': f"Lot testing procedure meets all NADCAP requirements",
                'Responsible_Party': 'Lab Manager',
                'Estimated_Hours': 6,
                'Dependencies': 'Access to testing procedures, equipment, and recent test records',
                'Success_Criteria': 'Lot testing procedure covers all NADCAP-required tests',
                'Documents_to_Review': ['SF-TEST-001 Lot Testing Procedure', 'Test method specifications', 'Recent test records'],
                'Documents_to_Create': ['Updated testing procedure (if needed)', 'Test record templates'],
                'Verification_Method': 'Procedure review and test record audit',
                'Category': 'Testing and Inspection'
            })
        
        if 'periodic testing' in question.lower():
            actions.append({
                'Action_ID': f"TI-{action_id+1:03d}",
                'NADCAP_Clause': clause,
                'Priority': priority,
                'Priority_Number': self.priority_mapping.get(priority, 3),
                'Action_Type': 'Schedule Verification',
                'Specific_Action': f"Review periodic testing schedule and records for compliance with clause {clause}. Verify frequency meets NADCAP requirements. Requirement: {question}",
                'Expected_Outcome': f"Periodic testing schedule complies with NADCAP frequency requirements",
                'Responsible_Party': 'Lab Manager',
                'Estimated_Hours': 4,
                'Dependencies': 'Access to testing schedule and historical records',
                'Success_Criteria': 'Periodic testing performed at NADCAP-required intervals',
                'Documents_to_Review': ['Periodic Testing Schedule', 'Historical test records (last 2 years)'],
                'Documents_to_Create': ['Updated testing schedule (if needed)'],
                'Verification_Method': 'Schedule review and frequency analysis',
                'Category': 'Testing and Inspection'
            })
            
        return actions
    
    def _personnel_training_actions(self, action_id, clause, question, priority):
        """Generate personnel and training related actions"""
        actions = []
        
        actions.append({
            'Action_ID': f"PT-{action_id:03d}",
            'NADCAP_Clause': clause,
            'Priority': priority,
            'Priority_Number': self.priority_mapping.get(priority, 3),
            'Action_Type': 'Training Record Review',
            'Specific_Action': f"Review training records for all ZnNi line personnel to ensure compliance with clause {clause}. Requirement: {question}",
            'Expected_Outcome': f"All personnel have current, documented training per NADCAP requirements",
            'Responsible_Party': 'HR Manager/Training Coordinator',
            'Estimated_Hours': 6,
            'Dependencies': 'Access to personnel files and training records',
            'Success_Criteria': 'All personnel have documented qualification for their assigned tasks',
            'Documents_to_Review': ['Personnel training records', 'Job descriptions', 'Training procedures'],
            'Documents_to_Create': ['Training gap analysis', 'Updated training plan (if needed)'],
            'Verification_Method': 'Training record audit and competency verification',
            'Category': 'Personnel and Training'
        })
        
        return actions
    
    def _supplier_management_actions(self, action_id, clause, question, priority):
        """Generate supplier management related actions"""
        actions = []
        
        actions.append({
            'Action_ID': f"SM-{action_id:03d}",
            'NADCAP_Clause': clause,
            'Priority': priority,
            'Priority_Number': self.priority_mapping.get(priority, 3),
            'Action_Type': 'Supplier Verification',
            'Specific_Action': f"Review approved supplier list and qualification records for compliance with clause {clause}. Requirement: {question}",
            'Expected_Outcome': f"All suppliers meet NADCAP qualification requirements",
            'Responsible_Party': 'Procurement Manager',
            'Estimated_Hours': 4,
            'Dependencies': 'Access to supplier qualification records',
            'Success_Criteria': 'All suppliers have appropriate certifications and approvals',
            'Documents_to_Review': ['Approved Supplier List', 'Supplier qualification records', 'Material certificates'],
            'Documents_to_Create': ['Supplier gap analysis', 'Updated qualification criteria (if needed)'],
            'Verification_Method': 'Supplier record review and certification verification',
            'Category': 'Supplier Management'
        })
        
        return actions
    
    def _calibration_actions(self, action_id, clause, question, priority):
        """Generate calibration related actions"""
        actions = []
        
        actions.append({
            'Action_ID': f"CAL-{action_id:03d}",
            'NADCAP_Clause': clause,
            'Priority': priority,
            'Priority_Number': self.priority_mapping.get(priority, 3),
            'Action_Type': 'Calibration Verification',
            'Specific_Action': f"Review calibration schedule and records for all ZnNi line equipment to ensure compliance with clause {clause}. Requirement: {question}",
            'Expected_Outcome': f"All equipment calibration meets NADCAP requirements",
            'Responsible_Party': 'Maintenance Manager',
            'Estimated_Hours': 5,
            'Dependencies': 'Access to calibration records and equipment list',
            'Success_Criteria': 'All equipment calibrated per NADCAP requirements with valid certificates',
            'Documents_to_Review': ['Calibration Schedule', 'Calibration Certificates', 'Equipment Inventory'],
            'Documents_to_Create': ['Calibration gap analysis', 'Updated calibration schedule (if needed)'],
            'Verification_Method': 'Calibration record audit and certificate verification',
            'Category': 'Calibration'
        })
        
        return actions
    
    def _documentation_control_actions(self, action_id, clause, question, priority):
        """Generate documentation control related actions"""
        actions = []
        
        actions.append({
            'Action_ID': f"DC-{action_id:03d}",
            'NADCAP_Clause': clause,
            'Priority': priority,
            'Priority_Number': self.priority_mapping.get(priority, 3),
            'Action_Type': 'Document Control Review',
            'Specific_Action': f"Review document control procedure (SF-PROC-001) for compliance with clause {clause}. Verify version control and approval process. Requirement: {question}",
            'Expected_Outcome': f"Document control system meets all NADCAP requirements",
            'Responsible_Party': 'Quality Manager',
            'Estimated_Hours': 3,
            'Dependencies': 'Access to document control procedure and system',
            'Success_Criteria': 'Document control procedure covers all NADCAP requirements',
            'Documents_to_Review': ['SF-PROC-001 Document Control', 'Document control system records'],
            'Documents_to_Create': ['Updated document control procedure (if needed)'],
            'Verification_Method': 'Procedure review and system audit',
            'Category': 'Documentation Control'
        })
        
        return actions
    
    def _nonconformance_actions(self, action_id, clause, question, priority):
        """Generate nonconformance management related actions"""
        actions = []
        
        actions.append({
            'Action_ID': f"NC-{action_id:03d}",
            'NADCAP_Clause': clause,
            'Priority': priority,
            'Priority_Number': self.priority_mapping.get(priority, 3),
            'Action_Type': 'Nonconformance Procedure Review',
            'Specific_Action': f"Review nonconformance procedure (SF-PROC-003) for compliance with clause {clause}. Verify customer notification requirements. Requirement: {question}",
            'Expected_Outcome': f"Nonconformance procedure meets all NADCAP notification requirements",
            'Responsible_Party': 'Quality Manager',
            'Estimated_Hours': 4,
            'Dependencies': 'Access to nonconformance procedure and recent NCR records',
            'Success_Criteria': 'Nonconformance procedure includes all NADCAP-required elements',
            'Documents_to_Review': ['SF-PROC-003 Nonconformance Procedure', 'Recent NCR records'],
            'Documents_to_Create': ['Updated nonconformance procedure (if needed)'],
            'Verification_Method': 'Procedure review and NCR sampling',
            'Category': 'Nonconformance Management'
        })
        
        return actions
    
    def _facility_actions(self, action_id, clause, question, priority):
        """Generate facility related actions"""
        actions = []
        
        actions.append({
            'Action_ID': f"FAC-{action_id:03d}",
            'NADCAP_Clause': clause,
            'Priority': priority,
            'Priority_Number': self.priority_mapping.get(priority, 3),
            'Action_Type': 'Facility Assessment',
            'Specific_Action': f"Conduct facility assessment for compliance with clause {clause}. Document current state and identify gaps. Requirement: {question}",
            'Expected_Outcome': f"Facility meets all NADCAP requirements for clause {clause}",
            'Responsible_Party': 'Facility Manager',
            'Estimated_Hours': 3,
            'Dependencies': 'Access to facility and NADCAP facility requirements',
            'Success_Criteria': 'Facility assessment shows compliance with all applicable requirements',
            'Documents_to_Review': ['Facility layout drawings', 'Environmental monitoring records'],
            'Documents_to_Create': ['Facility assessment report', 'Gap closure plan (if needed)'],
            'Verification_Method': 'Physical facility inspection against NADCAP criteria',
            'Category': 'Facility Requirements'
        })
        
        return actions
    
    def _audit_prep_actions(self, action_id, clause, question, priority):
        """Generate audit preparation related actions"""
        actions = []
        
        actions.append({
            'Action_ID': f"AP-{action_id:03d}",
            'NADCAP_Clause': clause,
            'Priority': priority,
            'Priority_Number': self.priority_mapping.get(priority, 3),
            'Action_Type': 'Audit Preparation',
            'Specific_Action': f"Complete audit preparation activity for compliance with clause {clause}. Requirement: {question}",
            'Expected_Outcome': f"Audit preparation meets NADCAP requirements for clause {clause}",
            'Responsible_Party': 'Quality Manager',
            'Estimated_Hours': 2,
            'Dependencies': 'Completion of all other compliance actions',
            'Success_Criteria': 'Audit preparation demonstrates full compliance readiness',
            'Documents_to_Review': ['All compliance documentation'],
            'Documents_to_Create': ['Audit preparation checklist'],
            'Verification_Method': 'Self-audit against NADCAP requirements',
            'Category': 'Audit Preparation'
        })
        
        return actions
    
    def _create_generic_action(self, action_id, clause, question, priority):
        """Create a generic action for uncategorized requirements"""
        return {
            'Action_ID': f"GEN-{action_id:03d}",
            'NADCAP_Clause': clause,
            'Priority': priority,
            'Priority_Number': self.priority_mapping.get(priority, 3),
            'Action_Type': 'Compliance Review',
            'Specific_Action': f"Review current processes and documentation for compliance with clause {clause}. Requirement: {question}",
            'Expected_Outcome': f"Full compliance demonstrated for clause {clause}",
            'Responsible_Party': 'Quality Manager',
            'Estimated_Hours': 3,
            'Dependencies': 'Access to relevant documentation and processes',
            'Success_Criteria': 'Compliance demonstrated through documentation or process evidence',
            'Documents_to_Review': ['Relevant procedures and records'],
            'Documents_to_Create': ['Compliance evidence documentation'],
            'Verification_Method': 'Document review and process audit',
            'Category': 'General Compliance'
        }
    
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
            'Actions_by_Category': df['Category'].value_counts().to_dict()
        }
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main action plan
            df.to_excel(writer, sheet_name='100_Percent_Compliance_Plan', index=False)
            
            # Critical and High priority actions
            priority_actions = df[df['Priority'].isin(['Critical', 'High'])]
            priority_actions.to_excel(writer, sheet_name='Priority_Actions', index=False)
            
            # Actions by category
            for category in df['Category'].unique():
                category_df = df[df['Category'] == category]
                safe_name = category.replace(' ', '_').replace('/', '_')[:31]  # Excel sheet name limit
                category_df.to_excel(writer, sheet_name=safe_name, index=False)
            
            # Summary statistics
            summary_df = pd.DataFrame([summary_stats])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Implementation timeline (by priority)
            timeline_data = []
            week = 1
            for priority in ['Critical', 'High', 'Medium', 'Low']:
                priority_df = df[df['Priority'] == priority]
                for _, action in priority_df.iterrows():
                    timeline_data.append({
                        'Week': week,
                        'Action_ID': action['Action_ID'],
                        'Priority': action['Priority'],
                        'Specific_Action': action['Specific_Action'],
                        'Responsible_Party': action['Responsible_Party'],
                        'Estimated_Hours': action['Estimated_Hours']
                    })
                    if len(timeline_data) % 5 == 0:  # Every 5 actions, move to next week
                        week += 1
            
            timeline_df = pd.DataFrame(timeline_data)
            timeline_df.to_excel(writer, sheet_name='Implementation_Timeline', index=False)
        
        print(f"📊 100% Compliance Action Plan saved to: {filepath}")
        print(f"📈 Summary:")
        print(f"   • Total Actions: {summary_stats['Total_Actions']}")
        print(f"   • Critical: {summary_stats['Critical_Actions']}")
        print(f"   • High: {summary_stats['High_Actions']}")
        print(f"   • Medium: {summary_stats['Medium_Actions']}")
        print(f"   • Low: {summary_stats['Low_Actions']}")
        print(f"   • Total Estimated Hours: {summary_stats['Total_Estimated_Hours']}")
        print(f"   • Average Hours per Action: {summary_stats['Average_Hours_Per_Action']:.1f}")
        
        return filepath

def main():
    """Generate 100% compliance action plan"""
    print("🎯 NADCAP 100% Compliance Action Plan Generator")
    print("=" * 60)
    
    generator = ComplianceActionPlanGenerator()
    
    # Load analysis data
    outputs_dir = 'outputs'
    if not generator.load_analysis_data(outputs_dir):
        print("❌ Could not load analysis data from outputs folder")
        print("   Make sure the requirements and inventory analysis files exist")
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
        print(f"   • Specific actions for each NADCAP requirement")
        print(f"   • Clear responsibility assignments")
        print(f"   • Estimated time requirements")
        print(f"   • Success criteria for each action")
        print(f"   • Implementation timeline")
        print(f"   • Priority-based execution plan")
        print(f"\n📋 When all actions are completed, you will achieve 100% NADCAP compliance!")
        return 0
    else:
        print("\n❌ Failed to generate action plan")
        return 1

if __name__ == "__main__":
    exit(main())
