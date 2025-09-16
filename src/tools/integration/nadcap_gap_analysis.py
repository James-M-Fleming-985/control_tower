#!/usr/bin/env python3
"""
Gap Analysis Tool for NADCAP Clauses vs SF Documentation
Compares extracted NADCAP clauses against SF documentation inventory
"""

import pandas as pd
import json
import sys
import os
from datetime import datetime

class NADCAPGapAnalyzer:
    def __init__(self, nadcap_csv_path, sf_inventory_path):
        self.nadcap_csv_path = nadcap_csv_path
        self.sf_inventory_path = sf_inventory_path
        self.nadcap_clauses = None
        self.sf_inventory = None
        self.gap_analysis = []
    
    def load_nadcap_clauses(self):
        """Load extracted NADCAP clauses from CSV"""
        try:
            self.nadcap_clauses = pd.read_csv(self.nadcap_csv_path)
            print(f"Loaded {len(self.nadcap_clauses)} NADCAP clauses")
            return True
        except Exception as e:
            print(f"Error loading NADCAP clauses: {e}")
            return False
    
    def load_sf_inventory(self):
        """Load SF documentation inventory from Excel"""
        try:
            self.sf_inventory = pd.read_excel(self.sf_inventory_path)
            print(f"Loaded {len(self.sf_inventory)} SF documentation entries")
            return True
        except Exception as e:
            print(f"Error loading SF inventory: {e}")
            return False
    
    def analyze_coverage(self):
        """Analyze which NADCAP clauses are covered by existing SF documentation"""
        if self.nadcap_clauses is None or self.sf_inventory is None:
            print("Error: Data not loaded properly")
            return False
        
        print("\nPerforming gap analysis...")
        
        for idx, clause in self.nadcap_clauses.iterrows():
            clause_num = clause['Clause']
            content = clause['Content/Question']
            
            # Simple keyword matching (can be enhanced with more sophisticated matching)
            coverage_found = False
            matching_docs = []
            
            # Extract key terms from the clause content
            key_terms = self.extract_key_terms(content)
            
            # Search SF inventory for matching documentation
            for sf_idx, sf_doc in self.sf_inventory.iterrows():
                if self.check_coverage(key_terms, sf_doc):
                    coverage_found = True
                    matching_docs.append(sf_doc.to_dict())
            
            gap_entry = {
                'clause': clause_num,
                'content': content,
                'guidance': clause.get('Guidance', ''),
                'covered': coverage_found,
                'matching_documents': matching_docs,
                'gap_priority': self.assess_priority(content),
                'recommendations': self.generate_recommendations(content, coverage_found)
            }
            
            self.gap_analysis.append(gap_entry)
        
        return True
    
    def extract_key_terms(self, content):
        """Extract key terms from clause content for matching"""
        # Common quality/compliance terms
        key_terms = []
        
        terms_to_check = [
            'procedure', 'document', 'record', 'calibration', 'training',
            'inspection', 'test', 'equipment', 'personnel', 'quality',
            'control', 'specification', 'standard', 'certification',
            'audit', 'review', 'approval', 'maintenance', 'storage'
        ]
        
        content_lower = content.lower()
        for term in terms_to_check:
            if term in content_lower:
                key_terms.append(term)
        
        return key_terms
    
    def check_coverage(self, key_terms, sf_doc):
        """Check if SF document covers the NADCAP clause requirements"""
        # Convert all SF document fields to string and combine for searching
        if hasattr(sf_doc, 'values'):
            # If it's a pandas Series or dict-like object
            sf_text = ' '.join([str(val) for val in sf_doc if pd.notna(val)]).lower()
        else:
            # If it's already a list or array
            sf_text = ' '.join([str(val) for val in sf_doc if pd.notna(val)]).lower()
        
        # Check if any key terms match
        matches = sum(1 for term in key_terms if term in sf_text)
        
        # Consider it covered if at least 30% of key terms match
        coverage_threshold = 0.3
        return (matches / len(key_terms)) >= coverage_threshold if key_terms else False
    
    def assess_priority(self, content):
        """Assess priority level based on clause content"""
        high_priority_terms = ['safety', 'critical', 'shall', 'must', 'required']
        medium_priority_terms = ['should', 'recommended', 'preferred']
        
        content_lower = content.lower()
        
        if any(term in content_lower for term in high_priority_terms):
            return 'High'
        elif any(term in content_lower for term in medium_priority_terms):
            return 'Medium'
        else:
            return 'Low'
    
    def generate_recommendations(self, content, covered):
        """Generate recommendations for addressing gaps"""
        if covered:
            return "Review existing documentation to ensure full compliance"
        else:
            if 'procedure' in content.lower():
                return "Develop formal procedure document"
            elif 'record' in content.lower():
                return "Implement record-keeping system"
            elif 'training' in content.lower():
                return "Develop training program and documentation"
            else:
                return "Develop supporting documentation to address requirement"
    
    def generate_gap_report(self, output_path):
        """Generate comprehensive gap analysis report"""
        total_clauses = len(self.gap_analysis)
        covered_clauses = sum(1 for gap in self.gap_analysis if gap['covered'])
        gap_clauses = total_clauses - covered_clauses
        
        coverage_percentage = (covered_clauses / total_clauses) * 100 if total_clauses > 0 else 0
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# NADCAP vs SF Documentation Gap Analysis Report\n\n")
            f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**NADCAP Clauses Analyzed:** {total_clauses}\n")
            f.write(f"**Clauses with Coverage:** {covered_clauses}\n")
            f.write(f"**Clauses with Gaps:** {gap_clauses}\n")
            f.write(f"**Coverage Percentage:** {coverage_percentage:.1f}%\n\n")
            
            f.write("## Executive Summary\n")
            if coverage_percentage >= 80:
                f.write("✅ **Good Coverage** - Most NADCAP requirements are addressed by existing documentation.\n")
            elif coverage_percentage >= 60:
                f.write("⚠️ **Moderate Coverage** - Some gaps exist that need attention.\n")
            else:
                f.write("🚨 **Significant Gaps** - Major documentation development needed for compliance.\n")
            
            f.write("\n## Gap Analysis by Priority\n")
            
            priority_counts = {'High': 0, 'Medium': 0, 'Low': 0}
            for gap in self.gap_analysis:
                if not gap['covered']:
                    priority_counts[gap['gap_priority']] += 1
            
            f.write(f"- **High Priority Gaps:** {priority_counts['High']}\n")
            f.write(f"- **Medium Priority Gaps:** {priority_counts['Medium']}\n")
            f.write(f"- **Low Priority Gaps:** {priority_counts['Low']}\n\n")
            
            f.write("## Detailed Gap Analysis\n\n")
            
            for gap in self.gap_analysis:
                if not gap['covered']:  # Only show gaps
                    f.write(f"### Clause {gap['clause']} - {gap['gap_priority']} Priority\n")
                    f.write(f"**Content:** {gap['content']}\n\n")
                    if gap['guidance']:
                        f.write(f"**Guidance:** {gap['guidance']}\n\n")
                    f.write(f"**Status:** ❌ Gap Identified\n")
                    f.write(f"**Recommendation:** {gap['recommendations']}\n\n")
                    f.write("---\n\n")
            
            f.write("## Implementation Roadmap\n\n")
            f.write("### Phase 1: High Priority Items\n")
            high_priority_gaps = [gap for gap in self.gap_analysis if not gap['covered'] and gap['gap_priority'] == 'High']
            for gap in high_priority_gaps:
                f.write(f"- [ ] {gap['clause']}: {gap['recommendations']}\n")
            
            f.write("\n### Phase 2: Medium Priority Items\n")
            medium_priority_gaps = [gap for gap in self.gap_analysis if not gap['covered'] and gap['gap_priority'] == 'Medium']
            for gap in medium_priority_gaps:
                f.write(f"- [ ] {gap['clause']}: {gap['recommendations']}\n")
            
            f.write("\n### Phase 3: Low Priority Items\n")
            low_priority_gaps = [gap for gap in self.gap_analysis if not gap['covered'] and gap['gap_priority'] == 'Low']
            for gap in low_priority_gaps:
                f.write(f"- [ ] {gap['clause']}: {gap['recommendations']}\n")
        
        print(f"Gap analysis report generated: {output_path}")
    
    def generate_gap_csv(self, output_path):
        """Generate CSV with gap analysis results"""
        gap_data = []
        for gap in self.gap_analysis:
            gap_data.append({
                'Clause': gap['clause'],
                'Content': gap['content'],
                'Guidance': gap['guidance'],
                'Covered': 'Yes' if gap['covered'] else 'No',
                'Priority': gap['gap_priority'],
                'Recommendations': gap['recommendations'],
                'Matching_Documents': '; '.join([doc.get('Name', 'Unknown') for doc in gap['matching_documents']])
            })
        
        df = pd.DataFrame(gap_data)
        df.to_csv(output_path, index=False)
        print(f"Gap analysis CSV generated: {output_path}")
    
    def run_analysis(self):
        """Run complete gap analysis"""
        print("Starting NADCAP vs SF Documentation Gap Analysis")
        print("=" * 60)
        
        if not self.load_nadcap_clauses():
            return False
        
        if not self.load_sf_inventory():
            return False
        
        if not self.analyze_coverage():
            return False
        
        # Generate outputs - save to outputs folder
        outputs_dir = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis/outputs"
        
        # Ensure outputs directory exists
        os.makedirs(outputs_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        report_path = os.path.join(outputs_dir, f"NADCAP_SF_gap_analysis_report_{timestamp}.md")
        csv_path = os.path.join(outputs_dir, f"NADCAP_SF_gap_analysis_{timestamp}.csv")
        
        self.generate_gap_report(report_path)
        self.generate_gap_csv(csv_path)
        
        print(f"\nGap Analysis Complete!")
        print(f"Reports generated:")
        print(f"  1. {report_path} - Detailed analysis report")
        print(f"  2. {csv_path} - Gap analysis data for spreadsheet")
        
        return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python nadcap_gap_analysis.py <nadcap_clauses.csv> <sf_inventory.xlsx>")
        print("Example: python nadcap_gap_analysis.py NADCAP_yes_no_clauses.csv surface_finishes_MFG.xlsx")
        sys.exit(1)
    
    nadcap_csv = sys.argv[1]
    sf_inventory = sys.argv[2]
    
    if not os.path.exists(nadcap_csv):
        print(f"Error: NADCAP CSV file not found: {nadcap_csv}")
        sys.exit(1)
    
    if not os.path.exists(sf_inventory):
        print(f"Error: SF inventory file not found: {sf_inventory}")
        sys.exit(1)
    
    analyzer = NADCAPGapAnalyzer(nadcap_csv, sf_inventory)
    success = analyzer.run_analysis()
    
    if not success:
        print("Gap analysis failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
