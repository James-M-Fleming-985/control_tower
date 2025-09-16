#!/usr/bin/env python3
"""
Check SF PD Forms Coverage in PDRIVE Inventory
- Analyze what's in sf_pd_forms folder
- Check which ones appear in PDRIVE_inventory.xlsx
- Identify SF-specific documents not in PDRIVE tracking
"""

import os
import re
from datetime import datetime

import pandas as pd


def normalize_reference(ref):
    """Normalize reference format for comparison"""
    if not ref or str(ref) == "nan":
        return None

    ref_str = str(ref).upper().strip()

    if "MANP" in ref_str:
        # Extract numbers: MANP-3.3.xxx or MANP3.3.xxx
        numbers = re.search(r"(\d+(?:\.\d+)*(?:\.\d+)*)", ref_str)
        if numbers:
            return f"MANP-{numbers.group(1)}"
    elif "PD" in ref_str:
        # Extract numbers: PD123 or PD-123 or PD 123
        numbers = re.search(r"(\d+)", ref_str)
        if numbers:
            return f"PD{numbers.group(1)}"
    else:
        # Check if it's a MANP-style number (like 3.3.633)
        manp_pattern = re.match(r"^(\d+\.\d+\.\d+)$", ref_str)
        if manp_pattern:
            return f"MANP-{manp_pattern.group(1)}"

        # Check if it's a PD-style number (like 123)
        pd_pattern = re.match(r"^(\d+)$", ref_str)
        if pd_pattern:
            return f"PD{pd_pattern.group(1)}"

    return ref_str


def extract_references_from_filenames(file_list):
    """Extract MANP and PD references from filenames with detailed mapping"""
    references_to_files = {}
    unmatched_files = []

    for filename in file_list:
        found_ref = False

        # Try to extract MANP references
        manp_match = re.search(
            r"MANP[-\s]*(\d+(?:\.\d+)*(?:\.\d+)*)", filename, re.IGNORECASE
        )
        if manp_match:
            ref = f"MANP-{manp_match.group(1)}"
            if ref not in references_to_files:
                references_to_files[ref] = []
            references_to_files[ref].append(filename)
            found_ref = True

        # Try to extract PD references
        pd_match = re.search(r"PD[-\s]*(\d+)", filename, re.IGNORECASE)
        if pd_match:
            ref = f"PD{pd_match.group(1)}"
            if ref not in references_to_files:
                references_to_files[ref] = []
            references_to_files[ref].append(filename)
            found_ref = True

        if not found_ref:
            unmatched_files.append(filename)

    return references_to_files, unmatched_files


def check_sf_pd_forms_coverage():
    """Check what's in sf_pd_forms vs PDRIVE inventory"""

    print("SF PD Forms Coverage Analysis")
    print("=" * 60)

    # Paths
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    inputs_folder = os.path.join(base_folder, "Inputs")
    outputs_folder = os.path.join(base_folder, "outputs")
    sf_pd_forms_folder = os.path.join(inputs_folder, "sf_pd_forms")

    # Load PDRIVE inventory
    inventory_file = os.path.join(inputs_folder, "PDRIVE_inventory.xlsx")

    if not os.path.exists(inventory_file):
        print(f"ERROR: PDRIVE_inventory.xlsx not found at {inventory_file}")
        return

    print(f"Loading PDRIVE inventory from: {inventory_file}")
    inventory_df = pd.read_excel(inventory_file)

    # Get PDRIVE references (normalized)
    pdrive_references = set()
    for ref in inventory_df["Document Number"]:
        norm_ref = normalize_reference(ref)
        if norm_ref:
            pdrive_references.add(norm_ref)

    print(f"PDRIVE inventory: {len(inventory_df)} items")
    print(f"PDRIVE normalized references: {len(pdrive_references)}")

    # Scan sf_pd_forms folder
    print(f"\nScanning SF PD Forms folder: {sf_pd_forms_folder}")

    if not os.path.exists(sf_pd_forms_folder):
        print(f"ERROR: sf_pd_forms folder not found at {sf_pd_forms_folder}")
        return

    sf_files = []
    for file in os.listdir(sf_pd_forms_folder):
        if os.path.isfile(os.path.join(sf_pd_forms_folder, file)):
            sf_files.append(file)

    print(f"SF PD Forms files found: {len(sf_files)}")

    # Extract references from SF files
    sf_references_to_files, unmatched_sf_files = extract_references_from_filenames(
        sf_files
    )

    print(
        f"SF files with extractable references: {
            len(sf_references_to_files)}"
    )
    print(
        f"SF files without extractable references: {
            len(unmatched_sf_files)}"
    )

    # Check coverage
    print(f"\n=== SF PD FORMS COVERAGE ANALYSIS ===")

    sf_in_pdrive = []
    sf_not_in_pdrive = []

    for sf_ref, files in sf_references_to_files.items():
        if sf_ref in pdrive_references:
            sf_in_pdrive.append(
                {"Reference": sf_ref, "Files": files, "Status": "In PDRIVE"}
            )
        else:
            sf_not_in_pdrive.append(
                {"Reference": sf_ref, "Files": files, "Status": "NOT in PDRIVE"}
            )

    print(f"SF references IN PDRIVE inventory: {len(sf_in_pdrive)}")
    print(f"SF references NOT in PDRIVE inventory: {len(sf_not_in_pdrive)}")
    print(
        f"SF coverage: {(len(sf_in_pdrive) / len(sf_references_to_files) * 100):.1f}%"
    )

    # Create detailed report
    report_data = []

    # Add covered items
    for item in sf_in_pdrive:
        report_data.append(
            {
                "Reference": item["Reference"],
                "Status": "In PDRIVE",
                "Files_Count": len(item["Files"]),
                "Example_Filename": item["Files"][0] if item["Files"] else "",
                "All_Filenames": ", ".join(item["Files"]),
            }
        )

    # Add uncovered items
    for item in sf_not_in_pdrive:
        report_data.append(
            {
                "Reference": item["Reference"],
                "Status": "NOT in PDRIVE",
                "Files_Count": len(item["Files"]),
                "Example_Filename": item["Files"][0] if item["Files"] else "",
                "All_Filenames": ", ".join(item["Files"]),
            }
        )

    # Add unmatched files
    for filename in unmatched_sf_files:
        report_data.append(
            {
                "Reference": "NO_REFERENCE_EXTRACTED",
                "Status": "No Reference Pattern",
                "Files_Count": 1,
                "Example_Filename": filename,
                "All_Filenames": filename,
            }
        )

    # Create DataFrame and save
    report_df = pd.DataFrame(report_data)

    # Sort by status and reference
    report_df = report_df.sort_values(["Status", "Reference"])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(
        outputs_folder, f"SF_PD_Forms_Coverage_Analysis_{timestamp}.xlsx"
    )

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        # Main report
        report_df.to_excel(
            writer,
            sheet_name="SF_Coverage_Analysis",
            index=False)

        # Summary sheet
        summary_data = [
            ["Metric", "Count"],
            ["Total SF PD Forms Files", len(sf_files)],
            ["SF Files with Extractable References",
                len(sf_references_to_files)],
            ["SF Files without References", len(unmatched_sf_files)],
            [""],
            ["SF References IN PDRIVE", len(sf_in_pdrive)],
            ["SF References NOT in PDRIVE", len(sf_not_in_pdrive)],
            [
                "SF Coverage %",
                f"{(len(sf_in_pdrive) / len(sf_references_to_files) * 100):.1f}%",
            ],
            [""],
            ["Total PDRIVE Items", len(inventory_df)],
            ["PDRIVE Normalized References", len(pdrive_references)],
        ]
        summary_df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        # Not in PDRIVE sheet
        not_in_pdrive_df = report_df[report_df["Status"] == "NOT in PDRIVE"]
        not_in_pdrive_df.to_excel(
            writer, sheet_name="Not_In_PDRIVE", index=False)

    print(f"\n=== DETAILED RESULTS ===")

    if sf_not_in_pdrive:
        print(f"\n🔍 SF References NOT in PDRIVE ({len(sf_not_in_pdrive)}):")
        for item in sf_not_in_pdrive[:10]:  # Show first 10
            print(f"  ❌ {item['Reference']} ({len(item['Files'])} files)")
        if len(sf_not_in_pdrive) > 10:
            print(f"  ... and {len(sf_not_in_pdrive) - 10} more")

    if unmatched_sf_files:
        print(
            f"\n📄 SF Files without extractable references ({
                len(unmatched_sf_files)}):"
        )
        for filename in unmatched_sf_files[:5]:  # Show first 5
            print(f"  🤔 {filename}")
        if len(unmatched_sf_files) > 5:
            print(f"  ... and {len(unmatched_sf_files) - 5} more")

    print(f"\n=== OUTPUT SAVED ===")
    print(f"File: {output_file}")
    print(f"Sheets:")
    print(f"  - SF_Coverage_Analysis: Complete analysis")
    print(f"  - Not_In_PDRIVE: {len(sf_not_in_pdrive)} SF items not tracked")
    print(f"  - Summary: Key statistics")

    # Answer the user's question directly
    if len(sf_not_in_pdrive) == 0 and len(unmatched_sf_files) == 0:
        print(
            f"\n✅ ANSWER: YES, everything in sf_pd_forms appears in PDRIVE inventory!"
        )
    else:
        print(
            f"\n❌ ANSWER: NO, not everything in sf_pd_forms appears in PDRIVE inventory."
        )
        print(f"   - {len(sf_not_in_pdrive)} SF references NOT in PDRIVE")
        print(
            f"   - {len(unmatched_sf_files)} files with no extractable reference")

    return output_file


if __name__ == "__main__":
    output_file = check_sf_pd_forms_coverage()
    if output_file:
        print(f"\n✅ SF PD Forms coverage analysis complete!")
        print(f"📂 Results saved to: {output_file}")
