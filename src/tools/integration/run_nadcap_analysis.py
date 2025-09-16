#!/usr/bin/env python3
"""
NADCAP Analysis Master Script - UPDATED VERSION
Runs the complete NADCAP requirements extraction and gap analysis workflow
Enhanced with improved accuracy and timestamped outputs
"""

import os
import sys
import subprocess
from datetime import datetime

def check_requirements():
    """Check if required Python packages are installed"""
    required_packages = ['pdfplumber', 'pandas', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages. Installing...")
        for package in missing_packages:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        print("✅ Packages installed successfully!")

def check_input_files():
    """Check if required input files exist"""
    files_needed = {
        'NADCAP PDF': 'NADCAP Audit Requirements.pdf',
        'Document Inventory': 'Surface Finishes and MFG.xlsx'
    }
    
    missing_files = []
    for description, filename in files_needed.items():
        if not os.path.exists(filename):
            missing_files.append((description, filename))
    
    if missing_files:
        print("❌ Missing required input files:")
        for description, filename in missing_files:
            print(f"   • {description}: {filename}")
        print("\n📁 Please add these files to the NADCAP Analysis folder:")
        print("   • NADCAP Audit Requirements.pdf - Your 40-page NADCAP AC7108 PDF")
        print("   • Surface Finishes and MFG.xlsx - Your SF document inventory Excel file")
        print("   • Make sure the Excel file has the 'SURFACE FINISHES' sheet")
        return False
    
    return True

def run_workflow():
    """Run the complete NADCAP analysis workflow"""
    print("🚀 STARTING NADCAP ANALYSIS WORKFLOW")
    print("=" * 50)
    
    # Step 1: Extract NADCAP requirements
    print("\n📖 STEP 1: Extracting NADCAP Requirements...")
    try:
        result = subprocess.run([
            sys.executable, 'extract_nadcap.py',
            '--input', 'NADCAP Audit Requirements.pdf',
            '--output', 'outputs'
        ], capture_output=True, text=True, check=True)
        print("✅ NADCAP requirements extracted successfully!")
        requirements_file = None
        for line in result.stdout.split('\n'):
            if 'Results saved to:' in line or 'Output file:' in line:
                requirements_file = line.split(': ')[-1].strip()
                break
    except subprocess.CalledProcessError as e:
        print(f"❌ Error extracting NADCAP requirements: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    
    # Step 2: Analyze document inventory
    print("\n📊 STEP 2: Analyzing Document Inventory...")
    try:
        result = subprocess.run([
            sys.executable, 'analyze_inventory.py',
            '--input', 'Surface Finishes and MFG.xlsx',
            '--output', 'outputs'
        ], capture_output=True, text=True, check=True)
        print("✅ Document inventory analyzed successfully!")
        inventory_file = None
        for line in result.stdout.split('\n'):
            if 'Analysis saved to:' in line or 'Output file:' in line:
                inventory_file = line.split(': ')[-1].strip()
                break
    except subprocess.CalledProcessError as e:
        print(f"❌ Error analyzing inventory: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    
    # Step 3: Create gap analysis template
    print("\n📋 STEP 3: Creating Gap Analysis Template...")
    if requirements_file and inventory_file:
        try:
            result = subprocess.run([
                sys.executable, 'create_gap_template.py',
                '--requirements', requirements_file,
                '--inventory', inventory_file,
                '--output', 'outputs'
            ], capture_output=True, text=True, check=True)
            print("✅ Gap analysis template created successfully!")
            gap_file = None
            for line in result.stdout.split('\n'):
                if 'Template saved to:' in line or 'Output file:' in line:
                    gap_file = line.split(': ')[-1].strip()
                    break
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating gap template: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False
    else:
        print("⚠️ Skipping gap analysis - missing input files")
        gap_file = None
    
    # Step 4: Generate summary report
    print("\n📄 STEP 4: Generating Summary Report...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    summary_content = generate_summary_report(requirements_file, inventory_file, gap_file, timestamp)
    
    summary_file = f"outputs/NADCAP_Analysis_Summary_{timestamp}.md"
    with open(summary_file, 'w') as f:
        f.write(summary_content)
    
    print("✅ Summary report generated successfully!")
    
    # Final output summary
    print("\n" + "=" * 50)
    print("🎉 NADCAP ANALYSIS COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("\n📁 Generated Files:")
    if requirements_file:
        print(f"   📊 Requirements Analysis: {requirements_file}")
    if inventory_file:
        print(f"   📋 Document Inventory: {inventory_file}")
    if gap_file:
        print(f"   🎯 Gap Analysis Template: {gap_file}")
    print(f"   📄 Summary Report: {summary_file}")
    
    print("\n🚀 Next Steps:")
    print("   1. Open Excel files to review detailed analysis")
    print("   2. Complete gap analysis template manually")
    print("   3. Prioritize high-risk requirements")
    print("   4. Create implementation timeline")
    print("   5. Assign owners for gap closure")
    
    return True

def generate_summary_report(requirements_file, inventory_file, gap_file, timestamp):
    """Generate markdown summary report"""
    return f"""# NADCAP Analysis Summary Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Project:** Surface Finishing Department - ZnNi Line NADCAP Compliance  
**Analysis ID:** {timestamp}

## 📊 Analysis Overview

### Files Generated
- **Requirements Analysis:** `{requirements_file or 'Not generated'}`
- **Document Inventory:** `{inventory_file or 'Not generated'}`
- **Gap Analysis Template:** `{gap_file or 'Not generated'}`

### Analysis Scope
- **Standard:** NADCAP AC7108 Rev. JΔ1 (Chemical Processing)
- **Focus Area:** ZnNi Line Operations and Documentation
- **Document Source:** 40-page NADCAP Audit Requirements PDF

## 🎯 Key Findings Summary

### Requirements Extraction
*(Open Excel file for detailed breakdown)*

**Expected Categories:**
- Quality System Requirements (AS9100/ISO compliance)
- Process Control Documents (Critical for ZnNi line)
- Testing & Inspection (Lot and periodic testing)
- Personnel & Training (Qualified operators)
- Supplier Management (Approved materials)
- Calibration Requirements (Equipment verification)
- Documentation Control (Record keeping)
- Non-Conformance Management (Customer notification)
- Facility Requirements (Housekeeping standards)
- Pre-Audit Preparation (Self-audit completion)

### Document Inventory Status
*(Open Excel file for detailed analysis)*

**Review Areas:**
- Document currency and revision control
- Owner assignments and responsibilities
- Missing critical procedures identification
- Training record completeness
- Quality system integration

### Gap Analysis Priority
*(Complete template for detailed assessment)*

**High Priority Gaps (Expected):**
- Process Control Documents for ZnNi line
- Periodic testing procedures and records
- Equipment calibration documentation
- Personnel qualification records
- Buy-off procedure compliance

## 🚨 Critical Action Items

### Immediate (1-2 weeks)
1. **Review Requirements Analysis** - Open Excel file and identify Critical/High priority items
2. **Complete Document Inventory** - Update sf_document_inventory.csv with current SF documents
3. **Assess Current State** - Review existing ZnNi line documentation against NADCAP requirements

### Short-term (1-2 months)
1. **Complete Gap Analysis** - Use generated template to assess compliance gaps
2. **Develop Action Plan** - Create timeline for closing identified gaps
3. **Assign Owners** - Designate responsible parties for each gap closure

### Long-term (3-6 months)
1. **Implement Solutions** - Create missing documents and procedures
2. **Training Program** - Develop NADCAP compliance training
3. **Audit Preparation** - Complete self-audit and prepare for NADCAP audit

## 📋 Compliance Checklist

### Documentation Requirements
- [ ] Process Control Documents (PCDs) for all ZnNi processes
- [ ] Buy-off procedures with traceability
- [ ] Calibration schedules and records
- [ ] Personnel qualification documentation
- [ ] Approved supplier lists
- [ ] Testing procedures (lot and periodic)
- [ ] Non-conformance notification procedures

### Quality System Integration
- [ ] AS9100/ISO 9001 accreditation current
- [ ] Quality manual includes chemical processing
- [ ] Document control procedures implemented
- [ ] Training records maintained
- [ ] Management review includes NADCAP compliance

### Audit Preparation
- [ ] Self-audit completed (30 days before audit)
- [ ] Specification lists uploaded to eAuditNet
- [ ] Process line drawings/sketches prepared
- [ ] Personnel training records current
- [ ] Calibration schedules available

## 📞 Support Resources

### Key Documents
- **NADCAP_Audit_Requirements_SUMMARY.md** - Detailed requirement breakdown
- **Generated Excel files** - Specific compliance analysis
- **sf_document_inventory_template.csv** - Document tracking template

### Analysis Tools
- **extract_nadcap.py** - Requirements extraction script
- **analyze_inventory.py** - Document analysis script
- **create_gap_template.py** - Gap analysis generator
- **run_nadcap_analysis.py** - Master workflow script

### Next Analysis Runs
To update analysis with new documents or requirements:
```bash
cd "NADCAP Analysis"
python run_nadcap_analysis.py
```

---
*This analysis provides the foundation for NADCAP compliance planning. Complete the gap analysis template and create an implementation timeline based on identified priorities.*
"""

def main():
    print("🔧 NADCAP Analysis Workflow - UPDATED VERSION")
    print("⏰ Enhanced with improved accuracy and timestamped outputs")
    print("Checking prerequisites...")
    
    # Get timestamp for this analysis run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"📅 Analysis run timestamp: {timestamp}")
    
    # Check Python packages
    try:
        check_requirements()
    except Exception as e:
        print(f"❌ Error installing packages: {e}")
        return 1
    
    # Check input files
    if not check_input_files():
        print("\n💡 To get started:")
        print("   1. Ensure 'NADCAP Audit Requirements.pdf' is in this folder")
        print("   2. Copy sf_document_inventory_template.csv to sf_document_inventory.csv")
        print("   3. Fill in your actual SF documents in the CSV file")
        print("   4. Run this script again")
        return 1
    
    # Create outputs directory
    os.makedirs('outputs', exist_ok=True)
    
    # Run workflow
    success = run_workflow()
    
    if success:
        print(f"\n🎯 UPDATED Analysis complete! All files timestamped with {timestamp}")
        print("📁 Check outputs folder for all UPDATED_* files")
        print("📋 Review the generated Excel files to start gap assessment.")
        return 0
    else:
        print("\n❌ Analysis failed. Check error messages above.")
        return 1

if __name__ == "__main__":
    exit(main())
