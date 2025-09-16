#!/usr/bin/env python3
"""
Diagnostic Script: Column I Document Utilization Analysis
Investigate why only 21 out of 41 Column I documents are being used as primary evidence
"""

import os
from collections import Counter, defaultdict

import numpy as np
import pandas as pd


def analyze_document_utilization():
    """Analyze Column I document utilization in NADCAP analysis"""

    print("🔍 COLUMN I DOCUMENT UTILIZATION ANALYSIS")
    print("=" * 60)

    # Load the latest results
    output_file = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis/outputs/Enhanced_NADCAP_Clean_SF_Analysis_20250910_0737.xlsx"

    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return

    # Load analysis results
    df = pd.read_excel(output_file, sheet_name="NADCAP_Analysis")

    print(f"📊 Total NADCAP Requirements: {len(df)}")

    # Count unique primary evidence documents
    primary_evidence_docs = df[df["Primary_Source"] == "Surface Finishes Column I"][
        "Primary_Evidence"
    ].value_counts()

    print(
        f"📋 Unique Column I Documents Used as Primary Evidence: {
            len(primary_evidence_docs)}"
    )
    print(f"🎯 Expected Column I Documents Available: 41")
    print(
        f"📉 Utilization Rate: {
            len(primary_evidence_docs)}/41 = {
            (
                len(primary_evidence_docs) / 41) * 100:.1f}%"
    )

    print(f"\n🏆 TOP PERFORMING COLUMN I DOCUMENTS:")
    for i, (doc, count) in enumerate(
            primary_evidence_docs.head(10).items(), 1):
        print(f"   {i:2d}. {doc} → {count} requirements")

    # Analyze score distribution
    col_i_scores = df[df["Primary_Source"] == "Surface Finishes Column I"][
        "Primary_Score"
    ]

    print(f"\n📈 PRIMARY EVIDENCE SCORE DISTRIBUTION:")
    print(f"   Mean Score: {col_i_scores.mean():.3f}")
    print(f"   Median Score: {col_i_scores.median():.3f}")
    print(f"   Max Score: {col_i_scores.max():.3f}")
    print(f"   Min Score: {col_i_scores.min():.3f}")

    # Score ranges
    high_scores = len(col_i_scores[col_i_scores > 0.3])
    medium_scores = len(
        col_i_scores[(col_i_scores > 0.15) & (col_i_scores <= 0.3)])
    low_scores = len(col_i_scores[col_i_scores <= 0.15])

    print(f"\n🎯 SCORE BREAKDOWN:")
    print(f"   High (>0.3): {high_scores} requirements")
    print(f"   Medium (0.15-0.3): {medium_scores} requirements")
    print(f"   Low (≤0.15): {low_scores} requirements")

    # Check if there are documents with very low scores
    very_low_scores = df[
        (df["Primary_Source"] == "Surface Finishes Column I")
        & (df["Primary_Score"] < 0.05)
    ]
    if len(very_low_scores) > 0:
        print(
            f"\n⚠️  VERY LOW SCORING MATCHES (<0.05): {
                len(very_low_scores)} requirements"
        )
        print("   These might indicate poor matches or algorithm issues...")

        for idx, row in very_low_scores.head(5).iterrows():
            print(f"   - Req: {row['Content'][:50]}...")
            print(f"     Evidence: {row['Primary_Evidence']}")
            print(f"     Score: {row['Primary_Score']:.4f}")
            print()

    # Look for unused documents by examining what's NOT in the primary
    # evidence list
    print(f"\n🔍 INVESTIGATING DOCUMENT COVERAGE...")

    # Load the source data to see all 41 documents
    surface_finishes_file = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis/Inputs/Surface Finishes and MFG 030925.xlsx"

    if os.path.exists(surface_finishes_file):
        source_df = pd.read_excel(surface_finishes_file)

        # Extract CHEOPS references from Column I
        column_i_refs = []
        for idx, row in source_df.iterrows():
            cheops_ref = str(row.get("CHEOPS Ref", "")).strip()
            title = str(row.get("Title", "")).strip()
            notes = str(row.get("Notes", "")).strip()

            if (
                cheops_ref
                and cheops_ref != "nan"
                and len(cheops_ref) > 5
                and title
                and title != "nan"
                and len(title) > 5
                and notes
                and notes != "nan"
                and len(notes) > 5
            ):

                display_ref = f"{cheops_ref}: {title}"
                column_i_refs.append(display_ref)

        print(f"📋 All Column I Documents Available: {len(column_i_refs)}")

        # Find unused documents
        used_docs = set(primary_evidence_docs.index)
        all_docs = set(column_i_refs)
        unused_docs = all_docs - used_docs

        print(f"\n❌ UNUSED COLUMN I DOCUMENTS: {len(unused_docs)}")
        if unused_docs:
            print("   Documents NOT being used as primary evidence:")
            for doc in sorted(list(unused_docs))[:10]:  # Show first 10
                print(f"   - {doc}")
            if len(unused_docs) > 10:
                print(f"   ... and {len(unused_docs) - 10} more")

        # Analyze unused document patterns
        if unused_docs:
            print(f"\n🔬 ANALYZING UNUSED DOCUMENT PATTERNS:")
            unused_titles = [
                doc.split(": ", 1)[1] if ": " in doc else doc for doc in unused_docs
            ]

            # Look for common terms in unused docs
            unused_text = " ".join(unused_titles).lower()
            common_words = [
                "surface",
                "finishing",
                "plating",
                "coating",
                "quality",
                "procedure",
                "control",
                "test",
                "maintenance",
                "training",
                "safety",
                "management",
            ]

            for word in common_words:
                if word in unused_text:
                    count = unused_text.count(word)
                    if count > 0:
                        print(
                            f"   '{word}' appears {count} times in unused document titles"
                        )

    print(f"\n💡 POTENTIAL ISSUES TO INVESTIGATE:")
    print(f"   1. Are synonym mappings comprehensive enough?")
    print(f"   2. Are TF-IDF parameters optimal for matching?")
    print(f"   3. Should we lower similarity thresholds?")
    print(
        f"   4. Are some documents too specialized to match general NADCAP requirements?"
    )

    return {
        "total_docs_available": 41,
        "docs_used": len(primary_evidence_docs),
        "utilization_rate": (len(primary_evidence_docs) / 41) * 100,
        "avg_score": col_i_scores.mean(),
        "high_scores": high_scores,
        "medium_scores": medium_scores,
        "low_scores": low_scores,
    }


if __name__ == "__main__":
    results = analyze_document_utilization()
    print(f"\n📋 SUMMARY:")
    print(
        f"   Utilization: {
            results['utilization_rate']:.1f}% ({
            results['docs_used']}/{
            results['total_docs_available']})"
    )
    print(f"   Average Score: {results['avg_score']:.3f}")
    print(f"   Strong Evidence: {results['high_scores']} requirements")
