#!/usr/bin/env python3
"""
Debug Document Allocation Issue
Find why algorithm reports 27 docs used but output shows 21
"""

import os

import pandas as pd


def debug_allocation_issue():
    """Debug the document allocation discrepancy"""

    print("🔧 DEBUGGING DOCUMENT ALLOCATION ISSUE")
    print("=" * 60)

    # Load the latest results
    output_file = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis/outputs/Enhanced_NADCAP_Clean_SF_Analysis_20250910_0811.xlsx"

    df = pd.read_excel(output_file, sheet_name="NADCAP_Analysis")

    # Analyze the actual document usage in the output
    actual_used_docs = df[df["Primary_Source"] == "Surface Finishes Column I"][
        "Primary_Evidence"
    ].value_counts()

    print(f"📊 ACTUAL DOCUMENT USAGE IN OUTPUT:")
    print(f"   Unique documents used: {len(actual_used_docs)}")
    print(
        f"   Total requirements with Column I primary evidence: {len(df[df['Primary_Source'] == 'Surface Finishes Column I'])}"
    )

    print(f"\n📋 DOCUMENTS ACTUALLY USED:")
    for i, (doc, count) in enumerate(actual_used_docs.items(), 1):
        print(f"   {i:2d}. {doc} → {count} requirements")

    # The issue is likely in the algorithm - let me check if there are any
    # requirements that should have different primary evidence

    # Look for patterns in unused docs that should be matched
    print(f"\n🔍 CHECKING FOR MISSED OPPORTUNITIES:")

    # Check if any requirements mention specific terms that unused docs cover
    test_terms = [
        ("adhesion", "ADHESION TESTING"),
        ("hardness", "HARDNESS CHECKS"),
        ("grit blasting", "GRIT BLASTING"),
        ("calibration", "CALIBRATION"),
        ("stress relief", "STRESS RELIEF"),
    ]

    for term, doc_type in test_terms:
        matching_reqs = df[df["Content"].str.contains(
            term, case=False, na=False)]
        if not matching_reqs.empty:
            print(
                f"\n   Requirements mentioning '{term}': {
                    len(matching_reqs)}"
            )
            for idx, row in matching_reqs.head(2).iterrows():
                print(f"     - Req: {row['Content'][:50]}...")
                print(
                    f"       Current Primary: {row['Primary_Evidence'][:50]}...")
                print(f"       Score: {row['Primary_Score']}")
                if doc_type.lower() not in row["Primary_Evidence"].lower():
                    print(
                        f"       ⚠️  Should potentially match to {doc_type} document!")

    # Check if the issue is that the same high-scoring documents are dominating
    dominant_docs = actual_used_docs.head(5)
    total_dominated = dominant_docs.sum()

    print(f"\n🎯 DOMINANCE ANALYSIS:")
    print(
        f"   Top 5 documents handle: {total_dominated}/{
            len(df)} requirements ({
            (
                total_dominated / len(df)) * 100:.1f}%)"
    )
    print(
        f"   This suggests the algorithm is still too concentrated on high-scoring docs"
    )

    # The real issue: my algorithm may be tracking usage but not properly
    # distributing
    print(f"\n🔧 LIKELY ISSUE:")
    print(f"   1. Algorithm tracks document usage internally")
    print(f"   2. But still selects highest scoring document for each requirement")
    print(f"   3. Load balancing logic isn't working properly")
    print(f"   4. Need to force more aggressive distribution")

    return len(actual_used_docs)


if __name__ == "__main__":
    actual_count = debug_allocation_issue()
    print(
        f"\n📝 CONCLUSION: Algorithm needs fix to actually distribute requirements across {
            41 - actual_count} more documents"
    )
