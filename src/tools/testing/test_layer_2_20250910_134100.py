"""
Layer 2 Specific Tests - Text Processing & Categorization
=========================================================

Test that Layer 2 correctly processes and categorizes text from both
requirements and documents, preparing them for semantic matching.
"""

import pandas as pd
import re
from pathlib import Path
from layered_tdd_framework import Layer2_TextProcessor


def test_specification_text_extraction():
    """Test that we correctly extract text per specification requirements"""
    print("\n" + "=" * 60)
    print("🔧 TESTING SPECIFICATION TEXT EXTRACTION")
    print("=" * 60)

    # Load both files as per NADCAP specification
    requirements_file = "Inputs/NADCAP Audit Requirements 030925.xlsx"
    documents_file = "Inputs/Surface Finishes and MFG 030925.xlsx"

    try:
        req_df = pd.read_excel(requirements_file, header=0)
        doc_df = pd.read_excel(documents_file, header=0)
    except Exception as e:
        print(f"❌ Failed to load specification files: {e}")
        return False

    print(f"✅ Loaded requirements file: {len(req_df)} rows")
    print(f"✅ Loaded documents file: {len(doc_df)} rows")

    # Test requirements text extraction (columns C, E, G, H)
    print(f"\n📋 Testing requirements text extraction:")

    requirements_with_text = 0
    total_text_length = 0

    for i, row in req_df.iterrows():
        # Extract from specified columns per specification
        title = str(row.get("Title", ""))  # Column C
        title2 = str(row.get("Title.1", ""))  # Column E
        content = str(row.get("Content", ""))  # Column G
        guidance = str(row.get("Guidence ", ""))  # Column H

        # Combine text from all specification columns
        combined_text = f"{title} {title2} {content} {guidance}".strip()

        if len(combined_text) > 20:  # Meaningful text threshold
            requirements_with_text += 1
            total_text_length += len(combined_text)

    avg_text_length = (
        total_text_length / requirements_with_text if requirements_with_text > 0 else 0
    )

    print(
        f"   Requirements with meaningful text: {requirements_with_text}/{len(req_df)} ({requirements_with_text/len(req_df)*100:.1f}%)"
    )
    print(f"   Average text length per requirement: {avg_text_length:.0f} characters")

    if requirements_with_text < len(req_df) * 0.85:  # 85% should have meaningful text
        print(f"❌ Too few requirements with meaningful text: {requirements_with_text}")
        return False

    # Test documents text extraction (columns F, I only when populated)
    print(f"\n📚 Testing documents text extraction:")

    documents_with_text = 0
    column_i_used = 0

    for i, row in doc_df.iterrows():
        title = str(row.get("Title", ""))  # Column F
        notes = row.get("Notes", "")  # Column I

        # Per specification: only use Column I when populated
        if pd.notna(notes) and str(notes).strip():
            combined_text = f"{title} {notes}".strip()
            column_i_used += 1
        else:
            combined_text = title.strip()

        if len(combined_text) > 10:  # Meaningful text threshold
            documents_with_text += 1

    print(
        f"   Documents with meaningful text: {documents_with_text}/{len(doc_df)} ({documents_with_text/len(doc_df)*100:.1f}%)"
    )
    print(
        f"   Column I utilized: {column_i_used}/{len(doc_df)} ({column_i_used/len(doc_df)*100:.1f}%)"
    )
    print(f"   Expected Column I usage: 42 documents (per specification)")

    if abs(column_i_used - 42) > 1:  # Should match specification
        print(f"❌ Column I usage mismatch: {column_i_used} (expected 42)")
        return False

    print(f"✅ Text extraction follows specification requirements")
    return True


def test_text_cleaning_and_normalization():
    """Test that text is properly cleaned and normalized for analysis"""
    print("\n" + "=" * 60)
    print("🧹 TESTING TEXT CLEANING & NORMALIZATION")
    print("=" * 60)

    # Test with real data samples
    requirements_file = "Inputs/NADCAP Audit Requirements 030925.xlsx"
    try:
        req_df = pd.read_excel(requirements_file, header=0)
    except Exception as e:
        print(f"❌ Failed to load requirements file: {e}")
        return False

    print(f"✅ Loaded {len(req_df)} requirements for text processing")

    # Test text cleaning on sample data
    processor = Layer2_TextProcessor()

    print(f"\n🔍 Testing text cleaning functions:")

    # Test on actual requirement text
    sample_requirement = req_df.iloc[0]
    raw_text = str(sample_requirement.get("Content", ""))

    if len(raw_text) < 10:
        print(f"❌ Sample requirement text too short: {len(raw_text)} chars")
        return False

    print(f"   Raw text sample: {raw_text[:100]}...")

    # Apply cleaning
    cleaned_text = processor.clean_text(raw_text)
    print(f"   Cleaned text: {cleaned_text[:100]}...")

    # Test cleaning effectiveness
    if len(cleaned_text) < len(raw_text) * 0.5:  # Shouldn't remove too much
        print(
            f"❌ Text cleaning too aggressive: {len(cleaned_text)} vs {len(raw_text)}"
        )
        return False

    # Test normalization
    normalized_text = processor.normalize_text(cleaned_text)
    print(f"   Normalized text: {normalized_text[:100]}...")

    # Test that normalization maintains semantic content
    if len(normalized_text) < len(cleaned_text) * 0.8:
        print(
            f"❌ Text normalization too aggressive: {len(normalized_text)} vs {len(cleaned_text)}"
        )
        return False

    print(f"✅ Text cleaning and normalization working correctly")
    return True


def test_domain_specific_categorization():
    """Test that text is correctly categorized by domain-specific terms"""
    print("\n" + "=" * 60)
    print("🏷️ TESTING DOMAIN-SPECIFIC CATEGORIZATION")
    print("=" * 60)

    processor = Layer2_TextProcessor()

    # Load real data for categorization testing
    requirements_file = "Inputs/NADCAP Audit Requirements 030925.xlsx"
    documents_file = "Inputs/Surface Finishes and MFG 030925.xlsx"

    try:
        req_df = pd.read_excel(requirements_file, header=0)
        doc_df = pd.read_excel(documents_file, header=0)
    except Exception as e:
        print(f"❌ Failed to load files for categorization: {e}")
        return False

    print(f"✅ Loaded data for categorization testing")

    # Test requirement categorization
    print(f"\n📋 Testing requirement categorization:")

    categories_found = {
        "documentation": 0,
        "process_control": 0,
        "quality_assurance": 0,
        "equipment": 0,
        "training": 0,
        "other": 0,
    }

    requirements_processed = 0
    for i, row in req_df.iterrows():
        if i >= 20:  # Test first 20 requirements
            break

        content = str(row.get("Content", ""))
        if len(content) > 10:
            category = processor.categorize_requirement(content)
            if category in categories_found:
                categories_found[category] += 1
            else:
                categories_found["other"] += 1
            requirements_processed += 1

    print(f"   Requirements processed: {requirements_processed}")
    for category, count in categories_found.items():
        percentage = (
            (count / requirements_processed * 100) if requirements_processed > 0 else 0
        )
        print(f"   {category}: {count} ({percentage:.1f}%)")

    # Should find multiple categories in NADCAP requirements
    categories_with_content = sum(1 for count in categories_found.values() if count > 0)
    if categories_with_content < 3:
        print(f"❌ Too few categories identified: {categories_with_content}")
        return False

    # Test document categorization
    print(f"\n📚 Testing document categorization:")

    doc_categories_found = {
        "procedure": 0,
        "guideline": 0,
        "standard": 0,
        "form": 0,
        "other": 0,
    }

    documents_processed = 0
    for i, row in doc_df.iterrows():
        if i >= 15:  # Test first 15 documents
            break

        title = str(row.get("Title", ""))
        if len(title) > 5:
            category = processor.categorize_document(title)
            if category in doc_categories_found:
                doc_categories_found[category] += 1
            else:
                doc_categories_found["other"] += 1
            documents_processed += 1

    print(f"   Documents processed: {documents_processed}")
    for category, count in doc_categories_found.items():
        percentage = (
            (count / documents_processed * 100) if documents_processed > 0 else 0
        )
        print(f"   {category}: {count} ({percentage:.1f}%)")

    # Should find multiple document types
    doc_categories_with_content = sum(
        1 for count in doc_categories_found.values() if count > 0
    )
    if doc_categories_with_content < 2:
        print(
            f"❌ Too few document categories identified: {doc_categories_with_content}"
        )
        return False

    print(f"✅ Domain-specific categorization working correctly")
    return True


def test_term_extraction_and_weighting():
    """Test that key terms are extracted and properly weighted"""
    print("\n" + "=" * 60)
    print("⚖️ TESTING TERM EXTRACTION & WEIGHTING")
    print("=" * 60)

    processor = Layer2_TextProcessor()

    # Test with sample requirement text
    sample_texts = [
        "Is there a drawing/sketch defining the location of each process line",
        "Calibration procedures for measuring equipment must be documented",
        "Surface preparation requirements for electroplating processes",
    ]

    print(f"✅ Testing term extraction on {len(sample_texts)} sample texts")

    all_terms = []
    for i, text in enumerate(sample_texts):
        print(f"\n🔍 Text {i+1}: {text}")

        # Extract terms
        terms = processor.extract_key_terms(text)
        print(f"   Extracted terms: {terms[:10]}")  # Show first 10

        if len(terms) < 3:
            print(f"❌ Too few terms extracted: {len(terms)}")
            return False

        # Test term weighting
        weighted_terms = processor.weight_terms(terms, text)
        print(f"   Weighted terms: {list(weighted_terms.items())[:5]}")  # Show first 5

        if not weighted_terms:
            print(f"❌ Term weighting failed")
            return False

        all_terms.extend(terms)

    # Test term frequency analysis
    print(f"\n📊 Testing term frequency analysis:")

    unique_terms = set(all_terms)
    print(f"   Total terms extracted: {len(all_terms)}")
    print(f"   Unique terms: {len(unique_terms)}")

    if len(unique_terms) < len(all_terms) * 0.5:  # Should have reasonable diversity
        print(
            f"❌ Term diversity too low: {len(unique_terms)} unique out of {len(all_terms)}"
        )
        return False

    # Test domain-specific term detection
    surface_finishing_terms = [
        term
        for term in unique_terms
        if any(
            sf_word in term.lower()
            for sf_word in ["surface", "plating", "coating", "process", "equipment"]
        )
    ]

    print(f"   Surface finishing terms: {len(surface_finishing_terms)}")
    print(f"   Sample SF terms: {list(surface_finishing_terms)[:5]}")

    if len(surface_finishing_terms) < 3:
        print(
            f"❌ Too few surface finishing terms detected: {len(surface_finishing_terms)}"
        )
        return False

    print(f"✅ Term extraction and weighting working correctly")
    return True


def test_preprocessing_pipeline_integration():
    """Test that the complete preprocessing pipeline works end-to-end"""
    print("\n" + "=" * 60)
    print("🔄 TESTING PREPROCESSING PIPELINE INTEGRATION")
    print("=" * 60)

    processor = Layer2_TextProcessor()

    # Test with real NADCAP data
    requirements_file = "Inputs/NADCAP Audit Requirements 030925.xlsx"
    try:
        req_df = pd.read_excel(requirements_file, header=0)
    except Exception as e:
        print(f"❌ Failed to load requirements file: {e}")
        return False

    print(f"✅ Loaded {len(req_df)} requirements for pipeline testing")

    # Test end-to-end processing
    print(f"\n🔄 Testing complete preprocessing pipeline:")

    processed_requirements = []
    pipeline_errors = 0

    for i, row in req_df.iterrows():
        if i >= 10:  # Test first 10 requirements
            break

        try:
            # Extract text per specification
            title = str(row.get("Title", ""))
            content = str(row.get("Content", ""))
            guidance = str(row.get("Guidence ", ""))

            # Run through preprocessing pipeline
            processed_req = processor.preprocess_requirement(title, content, guidance)

            if processed_req and len(processed_req.get("processed_text", "")) > 10:
                processed_requirements.append(processed_req)
            else:
                pipeline_errors += 1

        except Exception as e:
            print(f"   ⚠️ Pipeline error for requirement {i}: {str(e)}")
            pipeline_errors += 1

    success_rate = len(processed_requirements) / 10 * 100

    print(
        f"   Requirements processed successfully: {len(processed_requirements)}/10 ({success_rate:.1f}%)"
    )
    print(f"   Pipeline errors: {pipeline_errors}")

    if success_rate < 80:  # Should process at least 80% successfully
        print(f"❌ Pipeline success rate too low: {success_rate:.1f}%")
        return False

    # Test processed output quality
    print(f"\n✅ Testing processed output quality:")

    if processed_requirements:
        sample_processed = processed_requirements[0]
        print(f"   Sample processed requirement:")
        print(f"     Category: {sample_processed.get('category', 'unknown')}")
        print(f"     Key terms: {sample_processed.get('key_terms', [])[:5]}")
        print(
            f"     Text length: {len(sample_processed.get('processed_text', ''))} chars"
        )

        required_fields = ["category", "key_terms", "processed_text", "weights"]
        missing_fields = [
            field for field in required_fields if field not in sample_processed
        ]

        if missing_fields:
            print(f"❌ Missing required fields in processed output: {missing_fields}")
            return False

    print(f"✅ Preprocessing pipeline integration working correctly")
    return True


def run_layer_2_tests():
    """Run all Layer 2 tests."""
    print("🧪 RUNNING LAYER 2 COMPREHENSIVE TESTS")
    print("=" * 60)

    tests = [
        test_specification_text_extraction,
        test_text_cleaning_and_normalization,
        test_domain_specific_categorization,
        test_term_extraction_and_weighting,
        test_preprocessing_pipeline_integration,
    ]

    results = []
    for test_func in tests:
        try:
            success = test_func()
            results.append(success)
        except Exception as e:
            print(f"🔥 {test_func.__name__}: ERROR - {str(e)}")
            results.append(False)

    passed_tests = sum(results)
    total_tests = len(results)

    print(f"\n📊 LAYER 2 TEST SUMMARY:")
    print(f"   Tests passed: {passed_tests}/{total_tests}")
    print(f"   Success rate: {passed_tests/total_tests*100:.1f}%")

    if passed_tests == total_tests:
        print(f"🎉 ALL LAYER 2 TESTS PASSED! Ready for Layer 3.")
        return True
    else:
        print(f"⚠️  Some Layer 2 tests failed. Fix before proceeding to Layer 3.")
        return False


if __name__ == "__main__":
    run_layer_2_tests()
