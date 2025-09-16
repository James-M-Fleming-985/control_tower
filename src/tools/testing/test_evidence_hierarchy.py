#!/usr/bin/env python3
"""
Test Evidence Hierarchy Fix
Check if problematic examples from yesterday are now resolved
"""

import os

import pandas as pd


def test_evidence_hierarchy():
    """Test the evidence hierarchy fix with problematic examples"""

    # Load the latest results
    output_file = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis/outputs/Enhanced_NADCAP_Clean_SF_Analysis_20250910_0737.xlsx"

    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return

    print("🔍 Testing Evidence Hierarchy Fix")
    print("=" * 60)

    # Load the analysis results
    df = pd.read_excel(output_file, sheet_name="NADCAP_Analysis")

    print(f"📊 Total Requirements: {len(df)}")
    print(
        f"✅ Primary Evidence from Column I: {len(df[df['Primary_Source'] == 'Surface Finishes Column I'])}"
    )
    print(
        f"🔄 Secondary Evidence from PD Forms: {len(df[df['Secondary_Source'] == 'SF PD Form'])}"
    )
    print(
        f"📚 Secondary Evidence from MANPs: {len(df[df['Secondary_Source'] == 'SF MANP'])}"
    )

    print("\n🎯 High-Scoring Primary Evidence (Column I):")
    high_primary = df[df["Primary_Score"] > 0.3].sort_values(
        "Primary_Score", ascending=False
    )
    for idx, row in high_primary.head(5).iterrows():
        print(
            f"   - {row['Primary_Evidence']} (Score: {row['Primary_Score']:.3f})")
        print(f"     Requirement: {row['Content'][:80]}...")
        print()

    print("\n🔍 Testing Problematic Examples from Yesterday:")

    # Test 1: Look for competency-related requirements
    competency_reqs = df[
        df["Content"].str.contains(
            "competency|qualified|personnel", case=False, na=False
        )
    ]
    if len(competency_reqs) > 0:
        print(f"\n1️⃣ Competency Requirements: {len(competency_reqs)} found")
        for idx, row in competency_reqs.head(3).iterrows():
            print(f"   Requirement: {row['Content'][:60]}...")
            print(f"   Primary Evidence: {row['Primary_Evidence']}")
            print(f"   Secondary Evidence: {row['Secondary_Evidence']}")
            print(
                f"   ✅ Good match?"
                + (
                    " YES"
                    if "competency" in row["Primary_Evidence"].lower()
                    or "training" in row["Primary_Evidence"].lower()
                    else " NEEDS REVIEW"
                )
            )
            print()

    # Test 2: Look for test piece requirements
    test_piece_reqs = df[
        df["Content"].str.contains(
            "test piece|test specimen", case=False, na=False)
    ]
    if len(test_piece_reqs) > 0:
        print(f"\n2️⃣ Test Piece Requirements: {len(test_piece_reqs)} found")
        for idx, row in test_piece_reqs.head(3).iterrows():
            print(f"   Requirement: {row['Content'][:60]}...")
            print(f"   Primary Evidence: {row['Primary_Evidence']}")
            print(f"   Secondary Evidence: {row['Secondary_Evidence']}")
            print(
                f"   ✅ Good match?"
                + (
                    " YES"
                    if "test piece" in row["Primary_Evidence"].lower()
                    or "test" in row["Primary_Evidence"].lower()
                    else " NEEDS REVIEW"
                )
            )
            print()

    # Test 3: Check that no more dichloromethane training is primary evidence
    # for competency
    dcm_primary = df[
        df["Primary_Evidence"].str.contains(
            "dichloromethane", case=False, na=False)
    ]
    if len(dcm_primary) > 0:
        print(
            f"\n3️⃣ Dichloromethane as Primary Evidence: {
                len(dcm_primary)} cases"
        )
        for idx, row in dcm_primary.iterrows():
            print(f"   Requirement: {row['Content'][:60]}...")
            print(f"   Primary Evidence: {row['Primary_Evidence']}")
            competency_related = (
                "competency" in row["Content"].lower()
                or "qualified" in row["Content"].lower()
            )
            print(
                f"   ⚠️  Issue?"
                + (
                    " YES - DCM for competency req!"
                    if competency_related
                    else " NO - appropriate match"
                )
            )
            print()
    else:
        print(f"\n3️⃣ ✅ No dichloromethane training as primary evidence - GOOD!")

    print("\n📈 Evidence Quality Summary:")
    print(
        f"   Strong Evidence: {len(df[df['Compliance_Status'] == 'Strong Evidence'])}"
    )
    print(
        f"   Potential Evidence: {len(df[df['Compliance_Status'] == 'Potential Evidence'])}"
    )
    print(
        f"   Gap Identified: {len(df[df['Compliance_Status'] == 'Gap Identified'])}")

    coverage_percentage = (
        (
            len(df[df["Compliance_Status"] == "Strong Evidence"])
            + len(df[df["Compliance_Status"] == "Potential Evidence"])
        )
        / len(df)
    ) * 100

    print(
        f"\n🎯 Coverage: {
            coverage_percentage:.1f}% (Strong + Potential Evidence)"
    )

    if coverage_percentage > 85:
        print("✅ Excellent coverage maintained!")
    elif coverage_percentage > 70:
        print("👍 Good coverage achieved!")
    else:
        print("⚠️  Coverage may need improvement")


if __name__ == "__main__":
    test_evidence_hierarchy()
