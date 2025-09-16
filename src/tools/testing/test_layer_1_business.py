#!/usr/bin/env python3
"""
Layer 1 Business Validation Tests
=================================

BUSINESS PURPOSE: Data Validation & Structuring
BUSINESS SUCCESS CRITERIA:
1. Load all required data (no missing critical data)
2. Understand data structure (columns C, E, G, H parsed correctly) 
3. Output ready for Layer 2 (clean, structured, validated data)

This validates Layer 1 does what it's supposed to do from a business perspective.
"""

import pandas as pd
import sys
import os
from layered_tdd_framework import Layer1_DataValidator

def test_layer_1_business_data_completeness():
    """
    BUSINESS TEST 1: Load all required data
    
    Business Question: Does Layer 1 load all the data we need to run the business?
    """
    print("\n🏢 BUSINESS TEST 1: Data Completeness")
    print("=" * 50)
    
    validator = Layer1_DataValidator()
    
    # Load real NADCAP files
    try:
        requirements_df = pd.read_excel("Inputs/NADCAP Audit Requirements 030925.xlsx")
        documents_df = pd.read_excel("Inputs/Surface Finishes and MFG 030925.xlsx")
        print(f"✅ Successfully loaded real NADCAP data")
        print(f"   Requirements file: {len(requirements_df)} rows")
        print(f"   Documents file: {len(documents_df)} rows")
    except Exception as e:
        print(f"❌ BUSINESS FAILURE: Cannot load required data files")
        print(f"   Error: {e}")
        return False
    
    # Business validation: Do we have the minimum data to operate?
    required_requirements = 180  # Based on business needs
    required_documents = 40      # Based on Column I specification
    
    if len(requirements_df) < required_requirements:
        print(f"❌ BUSINESS FAILURE: Insufficient requirements data")
        print(f"   Expected: ≥{required_requirements}, Got: {len(requirements_df)}")
        return False
        
    if len(documents_df) < required_documents:
        print(f"❌ BUSINESS FAILURE: Insufficient documents data")
        print(f"   Expected: ≥{required_documents}, Got: {len(documents_df)}")
        return False
    
    print(f"✅ BUSINESS SUCCESS: All required data loaded")
    return True

def test_layer_1_business_structure_understanding():
    """
    BUSINESS TEST 2: Understand data structure
    
    Business Question: Does Layer 1 correctly understand and parse our data structure?
    """
    print("\n🏢 BUSINESS TEST 2: Data Structure Understanding")
    print("=" * 55)
    
    validator = Layer1_DataValidator()
    
    # Load real data
    requirements_df = pd.read_excel("Inputs/NADCAP Audit Requirements 030925.xlsx")
    documents_df = pd.read_excel("Inputs/Surface Finishes and MFG 030925.xlsx")
    
    # Business validation: Can Layer 1 extract the business-critical columns?
    critical_columns = {
        'requirements': ['Title', 'Title.1', 'Content', 'Guidence '],  # C, E, G, H
        'documents': ['Title', 'Notes']  # F, I
    }
    
    # Test requirements structure understanding
    for col in critical_columns['requirements']:
        if col not in requirements_df.columns:
            print(f"❌ BUSINESS FAILURE: Missing critical requirements column '{col}'")
            return False
        
        populated_count = requirements_df[col].notna().sum()
        print(f"   Requirements {col}: {populated_count} populated entries")
    
    # Test documents structure understanding  
    for col in critical_columns['documents']:
        if col not in documents_df.columns:
            print(f"❌ BUSINESS FAILURE: Missing critical documents column '{col}'")
            return False
            
        populated_count = documents_df[col].notna().sum()
        print(f"   Documents {col}: {populated_count} populated entries")
    
    # Business validation: Can Layer 1 apply Column I filtering correctly?
    column_i_populated = documents_df['Notes'].notna().sum()
    expected_column_i = 41  # Business specification
    
    if column_i_populated < expected_column_i:
        print(f"❌ BUSINESS FAILURE: Column I population below business requirements")
        print(f"   Expected: ≥{expected_column_i}, Got: {column_i_populated}")
        return False
    
    print(f"✅ BUSINESS SUCCESS: Data structure correctly understood")
    print(f"   Column I compliance: {column_i_populated}/{len(documents_df)} documents")
    return True

def test_layer_1_business_layer_2_readiness():
    """
    BUSINESS TEST 3: Output ready for Layer 2
    
    Business Question: Does Layer 1 output clean, structured data that Layer 2 can use?
    """
    print("\n🏢 BUSINESS TEST 3: Layer 2 Readiness")
    print("=" * 45)
    
    validator = Layer1_DataValidator()
    
    # Load and process real data
    requirements_df = pd.read_excel("Inputs/NADCAP Audit Requirements 030925.xlsx")
    documents_df = pd.read_excel("Inputs/Surface Finishes and MFG 030925.xlsx")
    
    # Process through Layer 1
    validated_requirements = validator.validate_requirements_data(requirements_df)
    validated_documents = validator.validate_documents_data(documents_df)
    
    # Business validation: Is the output usable by Layer 2?
    
    # 1. Data quantity validation
    min_requirements_for_business = 150  # Business needs at least this many
    min_documents_for_business = 35      # Business needs at least this many
    
    if len(validated_requirements) < min_requirements_for_business:
        print(f"❌ BUSINESS FAILURE: Insufficient processed requirements for Layer 2")
        print(f"   Expected: ≥{min_requirements_for_business}, Got: {len(validated_requirements)}")
        return False
        
    if len(validated_documents) < min_documents_for_business:
        print(f"❌ BUSINESS FAILURE: Insufficient processed documents for Layer 2")
        print(f"   Expected: ≥{min_documents_for_business}, Got: {len(validated_documents)}")
        return False
    
    # 2. Data quality validation
    sample_req = validated_requirements[0]
    sample_doc = validated_documents[0]
    
    # Check required fields are present
    required_req_fields = ['id', 'text', 'section', 'enhanced_context', 'title', 'title_1', 'guidance']
    required_doc_fields = ['id', 'title', 'content', 'document_type']
    
    for field in required_req_fields:
        if not hasattr(sample_req, field):
            print(f"❌ BUSINESS FAILURE: Requirements missing field '{field}' for Layer 2")
            return False
            
    for field in required_doc_fields:
        if not hasattr(sample_doc, field):
            print(f"❌ BUSINESS FAILURE: Documents missing field '{field}' for Layer 2")
            return False
    
    # ENHANCED VALIDATION: Check individual field population
    individual_fields_populated = {
        'title': sample_req.title,
        'title_1': sample_req.title_1,
        'guidance': sample_req.guidance
    }
    
    populated_count = sum(1 for v in individual_fields_populated.values() if v)
    
    print(f"✅ BUSINESS SUCCESS: Output ready for Layer 2 processing")
    print(f"   Processed requirements: {len(validated_requirements)}")
    print(f"   Processed documents: {len(validated_documents)}")
    print(f"   Individual fields preserved: {populated_count}/3 (title, title_1, guidance)")
    print(f"   Sample enhanced context: {len(sample_req.enhanced_context)} chars")
    print(f"   Data structure: Complete and validated")
    
    # Business validation: Layer 2 needs access to individual components
    if populated_count < 2:  # At least title + one other field should be populated
        print(f"⚠️  WARNING: Layer 2 may have limited individual field access")
        print(f"   Available fields: {[k for k, v in individual_fields_populated.items() if v]}")
        return False
    return True

def run_layer_1_business_validation():
    """Run all Layer 1 business validation tests"""
    print("🏢 LAYER 1 BUSINESS VALIDATION")
    print("==============================")
    print("Purpose: Validate Layer 1 does what it's supposed to do from business perspective")
    print("Success Criteria: Load data + Understand structure + Ready for Layer 2")
    print()
    
    tests = [
        test_layer_1_business_data_completeness,
        test_layer_1_business_structure_understanding, 
        test_layer_1_business_layer_2_readiness
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"   {test.__name__}: FAILED")
        except Exception as e:
            print(f"   {test.__name__}: ERROR - {e}")
    
    print(f"\n📊 LAYER 1 BUSINESS VALIDATION RESULTS:")
    print(f"   Tests passed: {passed}/{total}")
    print(f"   Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print(f"🎉 LAYER 1 BUSINESS SUCCESS: Ready to solve business problems!")
        return True
    else:
        print(f"❌ LAYER 1 BUSINESS FAILURE: Not ready for production use")
        return False

if __name__ == "__main__":
    success = run_layer_1_business_validation()
    sys.exit(0 if success else 1)
