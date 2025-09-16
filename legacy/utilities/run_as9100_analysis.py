#!/usr/bin/env python3
"""
AS9100 Analysis Master Script
Runs the complete AS9100 requirements extraction and gap analysis workflow
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
        'AS9100 PDF': 'AS9100_standard.pdf',
        'Document Inventory': 'sf_document_inventory.csv'
    }
    
    missing_files = []
    for description, filename in files_needed.items():
        if not os.path.exists(filename):
            missing_files.append((description, filename))
    
    if missing_files:
        print("❌ Missing required input files:")
        for description, filename in missing_files:
            print(f"   • {description}: {filename}")
        print("\n📁 Please add these files to the as9100_analysis folder:")
        print("   • AS9100_standard.pdf - Your 56-page AS9100 PDF")
        print("   • sf_document_inventory.csv - Your SF document list")
        print("   • Use sf_document_inventory_template.csv as a starting point")
        return False
    
    return True

def run_workflow():
    """Run the complete AS9100 analysis workflow"""
    print("🚀 STARTING AS9100 ANALYSIS WORKFLOW")
    print("=" * 50)
    
    # Step 1: Extract AS9100 requirements
    print("\n📖 STEP 1: Extracting AS9100 Requirements...")
    try:
        result = subprocess.run([
            sys.executable, 'extract_as9100.py',
            '--input', 'AS9100_standard.pdf',
            '--output', 'outputs'
        ], capture_output=True, text=True, check=True)
        print("✅ AS9100 requirements extracted successfully!")
        requirements_file = None
        for line in result.stdout.split('\n'):
            if 'Results saved to:' in line:
                requirements_file = line.split('Results saved to: ')[-1].strip()
                break
    except subprocess.CalledProcessError as e:
        print(f"❌ Error extracting AS9100 requirements: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    
    # Step 2: Analyze document inventory
    print("\n📊 STEP 2: Analyzing Document Inventory...")
    try:
        result = subprocess.run([
            sys.executable, 'analyze_inventory.py',
            '--input', 'sf_document_inventory.csv',
            '--output', 'outputs'
        ], capture_output=True, text=True, check=True)
        print("✅ Document inventory analyzed successfully!")
        inventory_file = None
        for line in result.stdout.split('\n'):
            if 'Analysis saved to:' in line:
                inventory_file = line.split('Analysis saved to: ')[-1].strip()
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
            template_file = None
            for line in result.stdout.split('\n'):
                if 'Gap analysis template created:' in line:
                    template_file = line.split('Gap analysis template created: ')[-1].strip()
                    break
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating gap template: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False
    else:
        print("❌ Cannot create gap template - missing input files")
        return False
    
    # Workflow complete
    print("\n🎉 WORKFLOW COMPLETE!")
    print("=" * 50)
    print("\n📁 Generated Files:")
    if requirements_file:
        print(f"   📖 AS9100 Requirements: {requirements_file}")
    if inventory_file:
        print(f"   📊 Document Analysis: {inventory_file}")
    if template_file:
        print(f"   📋 Gap Analysis Template: {template_file}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. 📖 Review AS9100 requirements extraction (focus on SF_High_Priority sheet)")
    print("2. 📊 Check document inventory analysis (review SF_Specific_Documents)")
    print("3. 📋 Open gap analysis template and begin manual compliance review")
    print("4. 👥 Work with Mike Warriner & James Bick to complete assessments")
    print("5. 📝 Create action plan based on identified gaps")
    
    print("\n⚠️  IMPORTANT REMINDER:")
    print("   The gap analysis template requires manual expert review")
    print("   Automation provides structure - humans determine actual compliance")
    
    return True

def main():
    """Main workflow execution"""
    print("🔧 AS9100 DOCUMENTATION COMPLIANCE ANALYSIS")
    print("Surface Finishing Department - Automation Setup")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check Python packages
    print("🔍 Checking requirements...")
    check_requirements()
    
    # Check input files
    print("\n📁 Checking input files...")
    if not check_input_files():
        print("\n❌ Setup incomplete. Please add required files and run again.")
        return False
    
    print("✅ All requirements met. Starting workflow...")
    
    # Run the complete workflow
    success = run_workflow()
    
    if success:
        print(f"\n✅ Workflow completed successfully at {datetime.now().strftime('%H:%M:%S')}")
        return True
    else:
        print(f"\n❌ Workflow failed at {datetime.now().strftime('%H:%M:%S')}")
        return False

if __name__ == "__main__":
    main()
