"""
Layer 1 Specific Tests - Data Input & Validation
===============================================

Test that Layer 1 correctly extracts and validates all required context
from the real NADCAP data files.

NOTE: Layer 1 DataValidator not yet implemented - placeholder tests
"""

from pathlib import Path

import pandas as pd

# Layer 1 DataValidator implementation now available
from layered_tdd_framework import Layer1_DataValidator


def test_specification_compliance():
    """Test that our extraction follows NADCAP specification structure"""
    print("\n" + "=" * 60)
    print("🔧 TESTING SPECIFICATION COMPLIANCE")
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

    # Test specification-defined column structure
    print(f"\n📋 Testing specification column structure:")

    # Requirements file must have columns C, E, G, H (per specification)
    req_actual_cols = list(req_df.columns)
    print(f"   Requirements columns: {req_actual_cols[:8]}")  # Show first 8

    # Documents file must have columns F, I (per specification)
    doc_actual_cols = list(doc_df.columns)
    print(f"   Documents columns: {doc_actual_cols[:10]}")  # Show first 10

    # Test that we extract the right columns per specification
    if len(req_actual_cols) < 8:
        print(f"❌ Requirements file missing expected columns (need at least H column)")
        return False

    if len(doc_actual_cols) < 9:
        print(f"❌ Documents file missing expected columns (need at least I column)")
        return False

    print(f"✅ Column structure compliant with specification")

    # Test NADCAP requirement types (per specification)
    print(f"\n📝 Testing NADCAP requirement types:")

    # Count meaningful content in column G (Content column)
    content_entries = 0
    for val in req_df.iloc[:, 6]:  # Column G (0-indexed)
        if pd.notna(val) and len(str(val).strip()) > 10:  # Meaningful content
            content_entries += 1

    print(f"   Content entries found: {content_entries}")

    if content_entries < 25:  # NADCAP should have substantial content
        print(f"❌ Insufficient content entries found: {content_entries}")
        return False

    # Test Column I controlled documents (per your specification)
    print(f"\n📚 Testing Column I controlled documents:")

    # Per specification: Only use Column I when populated
    total_docs = len(doc_df)
    column_i_populated = len(doc_df.iloc[:, 8].dropna())
    column_i_empty = total_docs - column_i_populated

    print(f"   Total documents in inventory: {total_docs}")
    print(f"   Column I populated (usable): {column_i_populated}")
    print(f"   Column I empty (excluded): {column_i_empty}")
    print(
        f"   Column I usage rate: {
            column_i_populated / total_docs * 100:.1f}%"
    )

    # Your specification: 41/42 documents expected with populated Column I
    expected_populated = 42
    if abs(column_i_populated - expected_populated) > 1:  # Allow 1 document variance
        print(
            f"❌ Column I populated count mismatch: {column_i_populated} (expected ~{expected_populated})"
        )
        return False

    print(
        f"   ✅ Column I populated count matches specification: {column_i_populated} ≈ {expected_populated}"
    )

    # Test that analysis should only use the populated Column I entries
    if column_i_populated < 40:  # Conservative minimum
        print(f"❌ Too few usable Column I documents: {column_i_populated}")
        return False

    print(f"✅ Specification compliance verified")
    return True


def test_column_i_usage_specification():
    """Test that analysis only uses populated Column I entries per specification"""
    print("\n" + "=" * 60)
    print("🔧 TESTING COLUMN I USAGE SPECIFICATION")
    print("=" * 60)

    # Load documents file
    documents_file = "Inputs/Surface Finishes and MFG 030925.xlsx"
    try:
        doc_df = pd.read_excel(documents_file, header=0)
    except Exception as e:
        print(f"❌ Failed to load documents file: {e}")
        return False

    print(f"✅ Loaded documents file: {len(doc_df)} rows")

    # Test Column I population specification
    column_i_data = doc_df.iloc[:, 8]  # Column I (Notes)
    populated_entries = column_i_data.dropna()
    empty_entries = column_i_data.isna()

    print(f"\n📋 Column I Population Analysis:")
    print(f"   Total entries: {len(column_i_data)}")
    print(
        f"   Populated entries: {
            len(populated_entries)} ({
            len(populated_entries) /
            len(column_i_data) *
            100:.1f}%)"
    )
    print(
        f"   Empty entries: {
            sum(empty_entries)} ({
            sum(empty_entries) /
            len(column_i_data) *
            100:.1f}%)"
    )

    # Test specification compliance: only populated entries should be used
    print(f"\n🎯 Testing specification compliance:")
    print(
        f"   Specification: Only populated Column I entries should be used in analysis"
    )
    print(
        f"   Usable documents (populated Column I): {
            len(populated_entries)}"
    )
    print(f"   Excluded documents (empty Column I): {sum(empty_entries)}")

    # Verify populated entries have meaningful content
    meaningful_content = 0
    for entry in populated_entries:
        if len(str(entry).strip()) > 50:  # Substantial content
            meaningful_content += 1

    print(
        f"   Populated entries with substantial content: {meaningful_content}")

    if (
        meaningful_content < len(populated_entries) * 0.8
    ):  # 80% should have substantial content
        print(f"❌ Too many populated Column I entries lack substantial content")
        return False

    # Test that our expected 41/42 matches populated count
    expected_usable = 42
    if abs(len(populated_entries) - expected_usable) > 1:
        print(
            f"❌ Usable document count mismatch: {
                len(populated_entries)} (expected ~{expected_usable})"
        )
        return False

    print(f"✅ Column I usage specification compliant")
    print(
        f"   - Only {len(populated_entries)} documents with populated Column I will be used"
    )
    print(
        f"   - {sum(empty_entries)} documents with empty Column I will be excluded")
    return True


def test_layer_1_requirements_context_extraction():
    """Test that we extract all context columns from NADCAP requirements."""
    print("\n🧪 TESTING LAYER 1: Requirements Context Extraction")
    print("-" * 50)

    # Load the actual requirements file
    req_file = Path("Inputs/NADCAP Audit Requirements 030925.xlsx")
    if not req_file.exists():
        print("❌ Requirements file not found")
        return False

    df = pd.read_excel(req_file)
    print(f"✅ Loaded {len(df)} rows from requirements file")

    # Test that key columns exist and have content
    required_columns = {
        "Title": 2,  # Column C
        "Title.1": 4,  # Column E
        "Content": 6,  # Column G
        "Guidence ": 7,  # Column H (note the space)
    }

    for col_name, expected_index in required_columns.items():
        if col_name not in df.columns:
            print(f"❌ Missing required column: {col_name}")
            return False

        non_empty_count = len(df[col_name].dropna())
        total_count = len(df)
        percentage = (non_empty_count / total_count) * 100

        print(
            f"   {col_name}: {non_empty_count}/{total_count} entries ({
                percentage:.1f}%)"
        )

        if col_name == "Content" and percentage < 90:
            print(
                f"   ❌ Content column has insufficient data: {
                    percentage:.1f}%"
            )
            return False

    # Test specific content extraction
    print(f"\n🔍 Testing specific content extraction:")

    # Test the drawing requirement (should be row 0 or 1)
    drawing_req_found = False
    for i in range(min(5, len(df))):
        content = str(df.iloc[i]["Content"]).lower()
        if "drawing" in content and "sketch" in content:
            print(f"   ✅ Found drawing requirement at row {i}")
            print(f"      Content: {df.iloc[i]['Content'][:80]}...")
            print(f"      Title: {df.iloc[i]['Title'][:60]}...")
            print(f"      Guidance: {str(df.iloc[i]['Guidence '])[:60]}...")
            drawing_req_found = True
            break

    if not drawing_req_found:
        print(f"   ❌ Could not find drawing/sketch requirement in first 5 rows")
        return False

    print(f"✅ Layer 1 Requirements Context Extraction: PASSED")
    return True


def test_layer_1_document_inventory_extraction():
    """Test that we extract document titles and context from Surface Finishes file."""
    print("\n🧪 TESTING LAYER 1: Document Inventory Extraction")
    print("-" * 50)

    # Load the Surface Finishes document inventory
    sf_file = Path("Inputs/Surface Finishes and MFG 030925.xlsx")
    if not sf_file.exists():
        print("❌ Surface Finishes file not found")
        return False

    df = pd.read_excel(sf_file)
    print(f"✅ Loaded {len(df)} rows from Surface Finishes inventory")

    # Test that key columns exist
    if "Title" not in df.columns:
        print("❌ Missing 'Title' column (Column F)")
        return False

    if "Notes" not in df.columns:
        print("❌ Missing 'Notes' column (Column I)")
        return False

    # Check content quality
    title_count = len(df["Title"].dropna())
    notes_count = len(df["Notes"].dropna())

    print(
        f"   Titles (Column F): {title_count}/{
            len(df)} entries ({
            title_count / len(df) * 100:.1f}%)"
    )
    print(
        f"   Notes (Column I): {notes_count}/{
            len(df)} entries ({
            notes_count / len(df) * 100:.1f}%)"
    )

    if title_count < len(df) * 0.9:  # Expect 90%+ titles
        print(f"❌ Insufficient title data: {title_count / len(df) * 100:.1f}%")
        return False

    # Test that we can find controlled documents - match actual inventory
    print(f"\n🔍 Testing controlled document identification:")

    controlled_docs = []
    column_i_docs = []  # Track Column I specifically (should be 41/42)

    for i, row in df.iterrows():
        title = str(row["Title"])
        category = str(row.get("Document Category", ""))

        # Column I documents are the main controlled inventory
        if "CHEOPS" in category.upper() or any(
            ref in title.upper() for ref in ["O_INST-GLO", "O-INST-GLO"]
        ):
            column_i_docs.append(title)
            controlled_docs.append(title)
        # Other controlled documents
        elif any(
            term in title.upper()
            for term in [
                "GUIDELINES",
                "STANDARD",
                "QUALIFICATION",
                "PROCEDURE",
                "CALIBRATION",
                "TESTING",
                "SURFACE FINISHES",
            ]
        ):
            controlled_docs.append(title)

    print(f"   Total controlled documents: {len(controlled_docs)}")
    print(f"   Column I documents (CHEOPS/O_INST-GLO): {len(column_i_docs)}")

    # Check against expected count
    expected_column_i = 41  # Your count
    if len(column_i_docs) < expected_column_i - 2:  # Allow small variance
        print(
            f"❌ Column I document count too low: {
                len(column_i_docs)} (expected ~{expected_column_i})"
        )
        print(f"   Sample Column I documents found:")
        for doc in column_i_docs[:5]:
            print(f"      - {doc[:70]}...")
        return False

    print(
        f"   ✅ Column I document count acceptable: {
            len(column_i_docs)} (expected ~{expected_column_i})"
    )

    if len(controlled_docs) < 40:  # Total should be 40+
        print(f"❌ Total controlled documents too low: {len(controlled_docs)}")
        return False

    # Show samples
    print(f"   Sample controlled documents:")
    for doc in controlled_docs[:3]:
        print(f"      - {doc[:70]}...")

    print(f"✅ Layer 1 Document Inventory Extraction: PASSED")
    return True


def test_layer_1_data_validation_logic():
    """Test the Layer1_DataValidator class with real data."""
    print("\n🧪 TESTING LAYER 1: Data Validation Logic")
    print("-" * 50)

    validator = Layer1_DataValidator()

    # Create test data that mimics our real structure
    test_requirements = pd.DataFrame(
        [
            {
                "Requirement": "Is there a drawing/sketch defining the location of each process line?",
                "Section": "2.7",
                "Page": "9",
            },
            {
                "Requirement": "",  # Should be filtered out
                "Section": "2.8",
                "Page": "10",
            },
            {
                "Requirement": "nan",  # Should be filtered out
                "Section": "2.9",
                "Page": "11",
            },
            {
                "Requirement": "Are ammeters and voltmeters calibrated according to procedure?",
                "Section": "3.1",
                "Page": "15",
            },
        ]
    )

    test_documents = pd.DataFrame(
        [
            {
                "Document_Title": "O_INST-GLO-000191: STRESS RELIEF AND DE-EMBRITTLEMENT",
                "Document_Type": "Procedure",
            },
            {
                "Document_Title": "O_INST-GLO-000170: Calibration of Ammeters and Voltmeters",
                "Document_Type": "Procedure",
            },
            {
                "Document_Title": "",  # Should be filtered out
                "Document_Type": "Procedure",
            },
        ]
    )

    # Test validation
    validated_reqs = validator.validate_requirements_data(test_requirements)
    validated_docs = validator.validate_documents_data(test_documents)

    print(f"   Input requirements: {len(test_requirements)}")
    print(f"   Validated requirements: {len(validated_reqs)}")
    print(f"   Input documents: {len(test_documents)}")
    print(f"   Validated documents: {len(validated_docs)}")

    # Should filter out empty/invalid entries
    if len(validated_reqs) != 2:
        print(
            f"❌ Expected 2 validated requirements, got {
                len(validated_reqs)}"
        )
        return False

    if len(validated_docs) != 2:  # Should filter out empty title
        print(
            f"❌ Expected 2 validated documents (after filtering empty), got {
                len(validated_docs)}"
        )
        # Let's debug what we actually got
        print(f"   Validated document titles:")
        for doc in validated_docs:
            print(f"      - {doc.title}")
        return False

    # Test that structure is correct
    first_req = validated_reqs[0]
    if not hasattr(first_req, "text") or not hasattr(first_req, "section"):
        print(f"❌ Validated requirement missing required attributes")
        return False

    print(f"   ✅ Validation logic working correctly")
    print(f"   Sample validated requirement: {first_req.text[:50]}...")

    print(f"✅ Layer 1 Data Validation Logic: PASSED")
    return True


def test_layer_1_enhanced_context():
    """Test that enhanced context extraction works with real data."""
    print("\n🧪 TESTING LAYER 1: Enhanced Context Integration")
    print("-" * 50)

    # Load the latest analysis file to test enhanced context
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("❌ Outputs directory not found")
        return False

    excel_files = list(outputs_dir.glob("*Enhanced*NADCAP*.xlsx"))
    if not excel_files:
        print("❌ No analysis files found")
        return False

    latest_file = max(excel_files, key=lambda f: f.stat().st_mtime)
    df = pd.read_excel(latest_file)

    print(f"✅ Loaded latest analysis: {latest_file.name}")
    print(f"   Total rows: {len(df)}")

    # Test that enhanced context can be created
    enhanced_requirements = []
    for i, row in df.iterrows():
        content = str(row.get("Content", "")).strip()
        if content and content != "nan" and len(content) > 10:
            enhanced_req = {
                "Requirement": content,
                "Title": str(row.get("Title", "")),
                "Sub_Section": str(row.get("Sub Section", "")),
                "Guidance": str(row.get("Guidence ", "")),
                "Full_Context": f"{content} {row.get('Title', '')} {row.get('Sub Section', '')} {row.get('Guidence ', '')}",
            }
            enhanced_requirements.append(enhanced_req)

    print(f"   Enhanced requirements created: {len(enhanced_requirements)}")

    if len(enhanced_requirements) < 150:  # Expect most requirements to be valid
        print(
            f"❌ Insufficient enhanced requirements: {
                len(enhanced_requirements)}"
        )
        return False

    # Test context richness
    sample_req = enhanced_requirements[0]
    context_length = len(sample_req["Full_Context"])
    base_length = len(sample_req["Requirement"])
    context_ratio = context_length / base_length

    print(f"   Sample context analysis:")
    print(f"      Base requirement: {len(sample_req['Requirement'])} chars")
    print(f"      Full context: {context_length} chars")
    print(f"      Context ratio: {context_ratio:.1f}x")

    if context_ratio < 1.5:  # Context should be significantly richer
        print(f"❌ Context not sufficiently enhanced: {context_ratio:.1f}x")
        return False

    print(
        f"   ✅ Enhanced context provides {
            context_ratio:.1f}x more information"
    )

    print(f"✅ Layer 1 Enhanced Context Integration: PASSED")
    return True


def run_layer_1_tests():
    """Run all Layer 1 tests."""
    print("🧪 RUNNING LAYER 1 COMPREHENSIVE TESTS")
    print("=" * 60)

    tests = [
        test_specification_compliance,
        test_column_i_usage_specification,
        test_layer_1_requirements_context_extraction,
        test_layer_1_document_inventory_extraction,
        test_layer_1_data_validation_logic,
        test_layer_1_enhanced_context,
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

    print(f"\n📊 LAYER 1 TEST SUMMARY:")
    print(f"   Tests passed: {passed_tests}/{total_tests}")
    print(f"   Success rate: {passed_tests / total_tests * 100:.1f}%")

    if passed_tests == total_tests:
        print(f"🎉 ALL LAYER 1 TESTS PASSED! Ready for Layer 2.")
        return True
    else:
        print(f"⚠️  Some Layer 1 tests failed. Fix before proceeding to Layer 2.")
        return False


if __name__ == "__main__":
    run_layer_1_tests()
