#!/usr/bin/env python3
"""
NADCAP Compliance Metrics Generator for PowerPoint
Creates presentation-ready metrics, charts, and summary data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import json

class NADCAPMetricsGenerator:
    def __init__(self):
        self.compliance_data = None
        self.requirements_data = None
        self.metrics = {}
        
    def load_data(self, outputs_dir):
        """Load compliance action plan and requirements data"""
        print("📊 Loading compliance and requirements data...")
        
        # Find the most recent compliance action plan
        compliance_files = [f for f in os.listdir(outputs_dir) 
                          if f.startswith('NADCAP_100_PERCENT_COMPLIANCE_ACTION_PLAN')]
        if compliance_files:
            compliance_file = sorted(compliance_files)[-1]
            compliance_path = os.path.join(outputs_dir, compliance_file)
            print(f"   📋 Loading compliance plan: {compliance_file}")
            self.compliance_data = pd.read_excel(compliance_path, sheet_name='100_Percent_Compliance_Plan')
        
        # Find the most recent requirements file
        req_files = [f for f in os.listdir(outputs_dir) if f.startswith('nadcap_requirements_')]
        if req_files:
            req_file = sorted(req_files)[-1]
            req_path = os.path.join(outputs_dir, req_file)
            print(f"   📄 Loading requirements: {req_file}")
            self.requirements_data = pd.read_excel(req_path, sheet_name='NADCAP_Requirements')
            
        return self.compliance_data is not None and self.requirements_data is not None
    
    def calculate_metrics(self):
        """Calculate key metrics for PowerPoint presentation"""
        print("📈 Calculating presentation metrics...")
        
        if self.compliance_data is None:
            print("❌ No compliance data loaded")
            return
        
        df = self.compliance_data
        
        # Basic metrics
        self.metrics['total_actions'] = len(df)
        self.metrics['total_hours'] = df['Estimated_Hours'].sum()
        self.metrics['completion_weeks'] = round(self.metrics['total_hours'] / 40)  # Assuming 40 hrs/week
        
        # Priority breakdown
        priority_counts = df['Priority'].value_counts()
        self.metrics['critical_actions'] = priority_counts.get('Critical', 0)
        self.metrics['high_actions'] = priority_counts.get('High', 0)
        self.metrics['medium_actions'] = priority_counts.get('Medium', 0)
        self.metrics['low_actions'] = priority_counts.get('Low', 0)
        
        # Percentage calculations
        self.metrics['critical_percentage'] = round((self.metrics['critical_actions'] / self.metrics['total_actions']) * 100, 1)
        self.metrics['high_percentage'] = round((self.metrics['high_actions'] / self.metrics['total_actions']) * 100, 1)
        
        # Category breakdown
        category_counts = df['Category'].value_counts()
        self.metrics['top_categories'] = category_counts.head(5).to_dict()
        
        # Responsible party breakdown
        party_counts = df['Responsible_Party'].value_counts()
        self.metrics['responsible_parties'] = party_counts.to_dict()
        
        # ZnNi specific metrics
        zn_ni_actions = df[df['ZnNi_Specific'] == True]
        self.metrics['zn_ni_actions'] = len(zn_ni_actions)
        self.metrics['zn_ni_percentage'] = round((self.metrics['zn_ni_actions'] / self.metrics['total_actions']) * 100, 1)
        self.metrics['zn_ni_hours'] = zn_ni_actions['Estimated_Hours'].sum()
        
        # Action type breakdown
        action_type_counts = df['Action_Type'].value_counts()
        self.metrics['action_types'] = action_type_counts.to_dict()
        
        # Requirements coverage metrics
        if self.requirements_data is not None:
            req_df = self.requirements_data
            self.metrics['total_requirements'] = len(req_df)
            self.metrics['coverage_percentage'] = round((self.metrics['total_actions'] / self.metrics['total_requirements']) * 100, 1)
            
            # Requirement priority breakdown
            req_priority = req_df['SF_Relevance'].value_counts()
            self.metrics['requirement_priorities'] = req_priority.to_dict()
        
        # Timeline metrics
        priority_hours = {
            'Critical': df[df['Priority'] == 'Critical']['Estimated_Hours'].sum(),
            'High': df[df['Priority'] == 'High']['Estimated_Hours'].sum(),
            'Medium': df[df['Priority'] == 'Medium']['Estimated_Hours'].sum(),
            'Low': df[df['Priority'] == 'Low']['Estimated_Hours'].sum()
        }
        self.metrics['priority_hours'] = priority_hours
        
        # Calculate milestone dates (assuming start date is today)
        start_date = datetime.now()
        self.metrics['critical_completion_weeks'] = round(priority_hours['Critical'] / 40, 1)
        self.metrics['high_completion_weeks'] = round((priority_hours['Critical'] + priority_hours['High']) / 40, 1)
        
        print(f"✅ Metrics calculated for {self.metrics['total_actions']} actions")
    
    def create_charts(self, output_dir):
        """Create PowerPoint-ready charts"""
        print("📊 Creating PowerPoint charts...")
        
        # Set style for professional charts
        plt.style.use('default')
        sns.set_palette("husl")
        
        charts_created = []
        
        # 1. Priority Distribution Pie Chart
        fig, ax = plt.subplots(figsize=(10, 8))
        priorities = ['Critical', 'High', 'Medium', 'Low']
        values = [self.metrics[f'{p.lower()}_actions'] for p in priorities]
        colors = ['#FF4444', '#FF8C00', '#FFD700', '#90EE90']
        
        wedges, texts, autotexts = ax.pie(values, labels=priorities, autopct='%1.1f%%', 
                                         colors=colors, startangle=90, textprops={'fontsize': 14})
        ax.set_title('NADCAP Compliance Actions by Priority', fontsize=18, fontweight='bold', pad=20)
        
        # Add total in center
        ax.text(0, 0, f'Total\n{self.metrics["total_actions"]}\nActions', 
                ha='center', va='center', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        chart1_path = os.path.join(output_dir, 'nadcap_priority_distribution.png')
        plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts_created.append(chart1_path)
        
        # 2. Category Breakdown Bar Chart
        fig, ax = plt.subplots(figsize=(12, 8))
        categories = list(self.metrics['top_categories'].keys())[:8]  # Top 8 categories
        category_values = [self.metrics['top_categories'][cat] for cat in categories]
        
        bars = ax.barh(categories, category_values, color='steelblue')
        ax.set_xlabel('Number of Actions', fontsize=14)
        ax.set_title('Actions by NADCAP Category (Top 8)', fontsize=18, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontsize=12)
        
        plt.tight_layout()
        chart2_path = os.path.join(output_dir, 'nadcap_category_breakdown.png')
        plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts_created.append(chart2_path)
        
        # 3. Timeline and Resource Requirements
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Timeline chart
        timeline_data = ['Critical\n(Immediate)', 'High\n(Weeks 1-4)', 'Medium\n(Weeks 5-10)', 'Low\n(Weeks 11-15)']
        timeline_hours = [self.metrics['priority_hours'][p] for p in ['Critical', 'High', 'Medium', 'Low']]
        timeline_colors = ['#FF4444', '#FF8C00', '#FFD700', '#90EE90']
        
        bars1 = ax1.bar(timeline_data, timeline_hours, color=timeline_colors)
        ax1.set_ylabel('Hours Required', fontsize=14)
        ax1.set_title('Implementation Timeline by Priority', fontsize=16, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{int(height)}h', ha='center', va='bottom', fontsize=12)
        
        # Responsible parties chart
        parties = list(self.metrics['responsible_parties'].keys())[:6]  # Top 6
        party_values = [self.metrics['responsible_parties'][party] for party in parties]
        
        bars2 = ax2.bar(range(len(parties)), party_values, color='darkseagreen')
        ax2.set_xticks(range(len(parties)))
        ax2.set_xticklabels([p.replace(' ', '\n') for p in parties], fontsize=10)
        ax2.set_ylabel('Number of Actions', fontsize=14)
        ax2.set_title('Actions by Responsible Party', fontsize=16, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom', fontsize=12)
        
        plt.tight_layout()
        chart3_path = os.path.join(output_dir, 'nadcap_timeline_resources.png')
        plt.savefig(chart3_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts_created.append(chart3_path)
        
        # 4. ZnNi Specific Analysis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        zn_ni_data = ['ZnNi Specific', 'General NADCAP']
        zn_ni_values = [self.metrics['zn_ni_actions'], 
                       self.metrics['total_actions'] - self.metrics['zn_ni_actions']]
        zn_ni_colors = ['#FF6B35', '#4ECDC4']
        
        wedges, texts, autotexts = ax.pie(zn_ni_values, labels=zn_ni_data, autopct='%1.1f%%',
                                         colors=zn_ni_colors, startangle=90, textprops={'fontsize': 14})
        ax.set_title('ZnNi Line Specific vs General NADCAP Actions', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        chart4_path = os.path.join(output_dir, 'nadcap_znni_specific.png')
        plt.savefig(chart4_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts_created.append(chart4_path)
        
        print(f"✅ Created {len(charts_created)} PowerPoint-ready charts")
        return charts_created
    
    def create_powerpoint_summary(self, output_dir):
        """Create a PowerPoint-ready summary document"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = os.path.join(output_dir, f'NADCAP_POWERPOINT_METRICS_SUMMARY_{timestamp}.md')
        
        summary_content = f"""# NADCAP Compliance Metrics - PowerPoint Ready
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 🎯 KEY PERFORMANCE INDICATORS (KPIs)

### Overall Compliance Metrics
- **Total Actions Required:** {self.metrics['total_actions']}
- **Total Hours Estimated:** {self.metrics['total_hours']} hours
- **Estimated Completion:** {self.metrics['completion_weeks']} weeks
- **Requirements Coverage:** {self.metrics.get('coverage_percentage', 'N/A')}%

### Priority Breakdown
- **Critical Actions:** {self.metrics['critical_actions']} ({self.metrics['critical_percentage']}%)
- **High Priority:** {self.metrics['high_actions']} ({self.metrics['high_percentage']}%)
- **Medium Priority:** {self.metrics['medium_actions']} 
- **Low Priority:** {self.metrics['low_actions']}

### ZnNi Line Specific
- **ZnNi Specific Actions:** {self.metrics['zn_ni_actions']} ({self.metrics['zn_ni_percentage']}%)
- **ZnNi Hours Required:** {self.metrics['zn_ni_hours']} hours

---

## 📊 POWERPOINT SLIDE CONTENT

### Slide 1: Executive Summary
**Title:** NADCAP AC7108 Compliance Action Plan

**Key Points:**
• {self.metrics['total_actions']} specific actions identified for 100% compliance
• {self.metrics['completion_weeks']}-week implementation timeline
• {self.metrics['total_hours']} total hours of effort required
• {self.metrics['critical_actions'] + self.metrics['high_actions']} priority actions for immediate focus

### Slide 2: Priority Distribution
**Title:** Action Priority Breakdown

**Statistics:**
• Critical (Immediate): {self.metrics['critical_actions']} actions ({self.metrics['critical_percentage']}%)
• High Priority: {self.metrics['high_actions']} actions ({self.metrics['high_percentage']}%)
• Medium Priority: {self.metrics['medium_actions']} actions
• Low Priority: {self.metrics['low_actions']} actions

**Visual:** Use nadcap_priority_distribution.png chart

### Slide 3: Implementation Timeline
**Title:** Phased Implementation Approach

**Timeline:**
• **Phase 1 (Immediate):** {self.metrics['critical_actions']} critical actions ({self.metrics['priority_hours']['Critical']} hours)
• **Phase 2 (Weeks 1-4):** {self.metrics['high_actions']} high priority actions ({self.metrics['priority_hours']['High']} hours)
• **Phase 3 (Weeks 5-10):** {self.metrics['medium_actions']} medium priority actions ({self.metrics['priority_hours']['Medium']} hours)
• **Phase 4 (Weeks 11-15):** {self.metrics['low_actions']} low priority actions ({self.metrics['priority_hours']['Low']} hours)

**Visual:** Use nadcap_timeline_resources.png chart

### Slide 4: Resource Requirements
**Title:** Team Responsibilities and Effort Distribution

**Key Responsibilities:**"""

        # Add top responsible parties
        for party, count in list(self.metrics['responsible_parties'].items())[:5]:
            summary_content += f"\n• **{party}:** {count} actions"
        
        summary_content += f"""

**Visual:** Use nadcap_timeline_resources.png chart (right panel)

### Slide 5: ZnNi Line Focus
**Title:** ZnNi Line Specific Requirements

**Key Metrics:**
• {self.metrics['zn_ni_actions']} actions specifically target ZnNi line operations
• {self.metrics['zn_ni_percentage']}% of total compliance effort is ZnNi-focused
• {self.metrics['zn_ni_hours']} hours dedicated to ZnNi line compliance

**Visual:** Use nadcap_znni_specific.png chart

### Slide 6: Category Breakdown
**Title:** NADCAP Requirement Categories

**Top Categories by Action Count:**"""

        # Add top categories
        for category, count in list(self.metrics['top_categories'].items())[:5]:
            summary_content += f"\n• **{category}:** {count} actions"
        
        summary_content += f"""

**Visual:** Use nadcap_category_breakdown.png chart

---

## 📈 EXECUTIVE DASHBOARD NUMBERS

### For C-Level Presentation:
- **Business Impact:** 100% NADCAP compliance achieved in {self.metrics['completion_weeks']} weeks
- **Resource Investment:** {self.metrics['total_hours']} hours = {round(self.metrics['total_hours']/40, 1)} person-weeks
- **Risk Mitigation:** {self.metrics['critical_actions']} critical compliance gaps addressed immediately
- **Operational Excellence:** {self.metrics['zn_ni_actions']} ZnNi line improvements implemented

### ROI Considerations:
- **Audit Readiness:** Complete NADCAP compliance framework
- **Customer Confidence:** Demonstrated systematic approach to quality
- **Operational Efficiency:** Structured process improvements
- **Risk Reduction:** Proactive gap closure before audit

---

## 📋 NEXT STEPS FOR PRESENTATION

1. **Use Charts:** All PNG files are high-resolution for PowerPoint
2. **Copy Metrics:** Use exact numbers provided above
3. **Emphasize Timeline:** {self.metrics['completion_weeks']}-week completion is realistic and achievable
4. **Highlight ZnNi Focus:** {self.metrics['zn_ni_percentage']}% focus on core business line
5. **Show Systematic Approach:** {self.metrics['total_actions']} specific, measurable actions

---

## 📁 CHART FILES CREATED
- `nadcap_priority_distribution.png` - Priority breakdown pie chart
- `nadcap_category_breakdown.png` - Category analysis bar chart  
- `nadcap_timeline_resources.png` - Timeline and resources overview
- `nadcap_znni_specific.png` - ZnNi specific analysis

---

*All metrics calculated from comprehensive NADCAP AC7108 compliance analysis*
*Charts optimized for PowerPoint presentation use*
"""

        with open(summary_file, 'w') as f:
            f.write(summary_content)
        
        print(f"📄 PowerPoint summary created: {summary_file}")
        return summary_file
    
    def create_json_metrics(self, output_dir):
        """Create JSON file with all metrics for easy data access"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = os.path.join(output_dir, f'nadcap_metrics_data_{timestamp}.json')
        
        # Convert pandas/numpy types to Python native types for JSON serialization
        json_metrics = {}
        for key, value in self.metrics.items():
            if isinstance(value, dict):
                json_metrics[key] = {k: int(v) if hasattr(v, 'dtype') else v for k, v in value.items()}
            elif hasattr(value, 'dtype'):  # numpy/pandas numeric types
                json_metrics[key] = int(value) if 'int' in str(value.dtype) else float(value)
            else:
                json_metrics[key] = value
        
        # Prepare JSON-serializable data
        json_data = {
            'generated_timestamp': datetime.now().isoformat(),
            'summary_metrics': json_metrics,
            'powerpoint_ready': {
                'title_slide': f"NADCAP AC7108 Compliance - {json_metrics['total_actions']} Actions, {json_metrics['completion_weeks']} Weeks",
                'key_numbers': {
                    'total_actions': json_metrics['total_actions'],
                    'completion_weeks': json_metrics['completion_weeks'],
                    'critical_actions': json_metrics['critical_actions'],
                    'high_actions': json_metrics['high_actions'],
                    'zn_ni_percentage': json_metrics['zn_ni_percentage']
                }
            }
        }
        
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"📊 JSON metrics data created: {json_file}")
        return json_file

def main():
    """Generate PowerPoint-ready metrics and charts"""
    print("📊 NADCAP PowerPoint Metrics Generator")
    print("=" * 50)
    
    generator = NADCAPMetricsGenerator()
    
    # Load data
    outputs_dir = 'outputs'
    if not generator.load_data(outputs_dir):
        print("❌ Could not load compliance and requirements data")
        return 1
    
    # Calculate metrics
    generator.calculate_metrics()
    
    # Create charts
    charts = generator.create_charts(outputs_dir)
    
    # Create PowerPoint summary
    summary_file = generator.create_powerpoint_summary(outputs_dir)
    
    # Create JSON data
    json_file = generator.create_json_metrics(outputs_dir)
    
    print(f"\n✅ PowerPoint metrics package created successfully!")
    print(f"📁 Files generated:")
    print(f"   📄 {summary_file}")
    print(f"   📊 {json_file}")
    for chart in charts:
        print(f"   📈 {chart}")
    
    print(f"\n🎯 PowerPoint Ready Content:")
    print(f"   • {generator.metrics['total_actions']} total actions for 100% compliance")
    print(f"   • {generator.metrics['completion_weeks']}-week implementation timeline")
    print(f"   • {generator.metrics['critical_actions']} critical priority actions")
    print(f"   • {generator.metrics['zn_ni_percentage']}% ZnNi line specific focus")
    print(f"   • 4 high-resolution charts for slides")
    print(f"   • Complete slide content ready to copy")
    
    return 0

if __name__ == "__main__":
    exit(main())
