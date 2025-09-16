#!/usr/bin/env python3
"""
Gap Analysis: Compare controlled inventory references against actual VS Code folders
Checks what MANPs and PD forms we have vs what we should have
"""

import os
import re
from datetime import datetime

import pandas as pd


def extract_reference_numbers(text_list, doc_type):
    """Extract clean reference numbers from a list of text/filenames"""
    references = set()

    if doc_type == "MANP":
        # MANP patterns: MANP-3.3.xxx, MANP3.3.xxx, etc.
        pattern = r"MANP[-\s]*(\d+(?:\.\d+)*(?:\.\d+)*)"
    else:  # PD forms
        # PD patterns: PD123, PD-123, PD 123, etc.
        pattern = r"PD[-\s]*(\d+)"

    for text in text_list:
        if text and str(text) != "nan":
            matches = re.findall(pattern, str(text), re.IGNORECASE)
            for match in matches:
                if doc_type == "MANP":
                    references.add(f"MANP-{match}")
                else:
                    references.add(f"PD{match}")

    return sorted(list(references))


def scan_folder_for_documents(folder_path, doc_type):
    """Scan a folder for MANP or PD form files"""
    found_docs = []

    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return []

    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            found_docs.append(file)

    # Extract reference numbers from filenames
    references = extract_reference_numbers(found_docs, doc_type)

    return references, found_docs


def load_should_have_lists():
    """Load the should-have lists from the latest analysis"""
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    outputs_folder = os.path.join(base_folder, "outputs")

    # Find the latest files
    manp_file = os.path.join(
        outputs_folder, "Controlled_Inventory_MANPs_20250908_1329.csv"
    )
    pd_file = os.path.join(
        outputs_folder, "Controlled_Inventory_PD_Forms_20250908_1329.csv"
    )

    print(f"Loading should-have lists...")
    print(f"MANP file: {manp_file}")
    print(f"PD file: {pd_file}")

    # Load MANP references
    manp_df = pd.read_csv(manp_file)
    should_have_manps = manp_df["Reference"].tolist()

    # Load PD form references
    pd_df = pd.read_csv(pd_file)
    should_have_pds = pd_df["Reference"].tolist()

    print(
        f"Should have: {
            len(should_have_manps)} MANPs, {
            len(should_have_pds)} PD forms"
    )

    return should_have_manps, should_have_pds


def normalize_reference(ref):
    """Normalize reference format for comparison"""
    if "MANP" in ref.upper():
        # Extract numbers and normalize to MANP-x.x.x format
        numbers = re.search(r"(\d+(?:\.\d+)*(?:\.\d+)*)", ref)
        if numbers:
            return f"MANP-{numbers.group(1)}"
    elif "PD" in ref.upper():
        # Extract numbers and normalize to PDxxx format
        numbers = re.search(r"(\d+)", ref)
        if numbers:
            return f"PD{numbers.group(1)}"
    return ref.upper()


def run_gap_analysis():
    """Run complete gap analysis comparing should-have vs actual folders"""

    print("=" * 80)
    print("NADCAP DOCUMENTATION GAP ANALYSIS")
    print("=" * 80)

    # Define folder paths
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    inputs_folder = os.path.join(base_folder, "Inputs")
    outputs_folder = os.path.join(base_folder, "outputs")

    folders_to_check = {
        "pd_forms": os.path.join(inputs_folder, "pd_forms"),
        "sf_pd_forms": os.path.join(inputs_folder, "sf_pd_forms"),
        "uncontrolled_documents": os.path.join(inputs_folder, "uncontrolled_documents"),
    }

    # Load should-have lists
    should_have_manps, should_have_pds = load_should_have_lists()

    # Normalize should-have lists
    should_have_manps_norm = [
        normalize_reference(ref) for ref in should_have_manps]
    should_have_pds_norm = [
        normalize_reference(ref) for ref in should_have_pds]

    print(f"\n=== SHOULD HAVE (from controlled inventory) ===")
    print(f"MANPs: {len(should_have_manps_norm)}")
    print(f"PD Forms: {len(should_have_pds_norm)}")

    # Check each folder
    all_found_manps = set()
    all_found_pds = set()

    folder_results = {}

    for folder_name, folder_path in folders_to_check.items():
        print(f"\n=== CHECKING FOLDER: {folder_name} ===")
        print(f"Path: {folder_path}")

        if os.path.exists(folder_path):
            files = [
                f
                for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))
            ]
            print(f"Total files: {len(files)}")

            # Find MANPs
            manp_refs, manp_files = scan_folder_for_documents(
                folder_path, "MANP")
            manp_refs_norm = [normalize_reference(ref) for ref in manp_refs]

            # Find PD forms
            pd_refs, pd_files = scan_folder_for_documents(folder_path, "PD")
            pd_refs_norm = [normalize_reference(ref) for ref in pd_refs]

            print(f"MANPs found: {len(manp_refs_norm)}")
            print(f"PD forms found: {len(pd_refs_norm)}")

            # Add to overall found lists
            all_found_manps.update(manp_refs_norm)
            all_found_pds.update(pd_refs_norm)

            folder_results[folder_name] = {
                "manps": manp_refs_norm,
                "pds": pd_refs_norm,
                "total_files": len(files),
            }
        else:
            print(f"Folder not found!")
            folder_results[folder_name] = {
                "manps": [], "pds": [], "total_files": 0}

    # Calculate gaps
    print(f"\n" + "=" * 80)
    print("GAP ANALYSIS RESULTS")
    print("=" * 80)

    print(f"\n=== SUMMARY ===")
    print(
        f"Should have: {
            len(should_have_manps_norm)} MANPs, {
            len(should_have_pds_norm)} PD forms"
    )
    print(
        f"Actually have: {
            len(all_found_manps)} MANPs, {
            len(all_found_pds)} PD forms"
    )

    # Missing documents
    missing_manps = set(should_have_manps_norm) - all_found_manps
    missing_pds = set(should_have_pds_norm) - all_found_pds

    print(f"\n=== MISSING DOCUMENTS ===")
    print(f"Missing MANPs: {len(missing_manps)}")
    print(f"Missing PD forms: {len(missing_pds)}")

    # Coverage percentage
    manp_coverage = (
        (len(should_have_manps_norm) - len(missing_manps)) /
        len(should_have_manps_norm)
    ) * 100
    pd_coverage = (
        (len(should_have_pds_norm) - len(missing_pds)) / len(should_have_pds_norm)
    ) * 100

    print(f"\n=== COVERAGE ===")
    print(f"MANP Coverage: {manp_coverage:.1f}%")
    print(f"PD Form Coverage: {pd_coverage:.1f}%")

    # Create detailed gap report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    gap_report_file = os.path.join(
        outputs_folder, f"Gap_Analysis_Report_{timestamp}.csv"
    )

    gap_data = []

    # Add missing MANPs
    for manp in sorted(missing_manps):
        gap_data.append(
            {
                "Type": "MANP",
                "Reference": manp,
                "Status": "Missing",
                "Required_For": "Surface Finishing Operations",
                "Contact_For_Document": "Scott Niedzwiecki",
            }
        )

    # Add missing PD forms
    for pd in sorted(missing_pds):
        gap_data.append(
            {
                "Type": "PD Form",
                "Reference": pd,
                "Status": "Missing",
                "Required_For": "Surface Finishing Operations",
                "Contact_For_Document": "Lloyd Harrington / Dean Wilkinson",
            }
        )

    if gap_data:
        gap_df = pd.DataFrame(gap_data)
        gap_df.to_csv(gap_report_file, index=False)
        print(f"\n=== GAP REPORT SAVED ===")
        print(f"File: {gap_report_file}")
        print(f"Total missing documents: {len(gap_data)}")

    # Print missing lists
    if missing_manps:
        print(f"\n=== MISSING MANPs ({len(missing_manps)}) ===")
        for manp in sorted(missing_manps)[:10]:  # Show first 10
            print(f"  {manp}")
        if len(missing_manps) > 10:
            print(f"  ... and {len(missing_manps) - 10} more")

    if missing_pds:
        print(f"\n=== MISSING PD FORMS ({len(missing_pds)}) ===")
        for pd in sorted(missing_pds)[:10]:  # Show first 10
            print(f"  {pd}")
        if len(missing_pds) > 10:
            print(f"  ... and {len(missing_pds) - 10} more")

    print(f"\n" + "=" * 80)
    print(
        "Analysis complete! Contact Scott for missing MANPs, Lloyd/Dean for missing PD forms."
    )
    print("=" * 80)


if __name__ == "__main__":
    run_gap_analysis()
