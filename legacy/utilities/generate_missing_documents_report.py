#!/usr/bin/env python3
"""
Generate Missing Documents Report - Quick Fix
"""

import os
import re
from datetime import datetime

import pandas as pd


def normalize_reference(ref):
    """Normalize reference format for comparison"""
    if "MANP" in ref.upper():
        numbers = re.search(r"(\d+(?:\.\d+)*(?:\.\d+)*)", ref)
        if numbers:
            return f"MANP-{numbers.group(1)}"
    elif "PD" in ref.upper():
        numbers = re.search(r"(\d+)", ref)
        if numbers:
            return f"PD{numbers.group(1)}"
    return ref.upper()


def extract_references_from_files(folder_path, doc_type):
    """Extract references from files in a folder"""
    found_refs = set()

    if not os.path.exists(folder_path):
        return found_refs

    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            if doc_type == "MANP" and "MANP" in file.upper():
                ref = normalize_reference(file)
                if ref:
                    found_refs.add(ref)
            elif doc_type == "PD" and "PD" in file.upper():
                ref = normalize_reference(file)
                if ref:
                    found_refs.add(ref)

    return found_refs


def generate_missing_documents_report():
    """Generate the missing documents report"""

    print("Generating Missing Documents Report...")

    # Paths
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    inputs_folder = os.path.join(base_folder, "Inputs")
    outputs_folder = os.path.join(base_folder, "outputs")

    # Load should-have lists
    manp_file = os.path.join(
        outputs_folder, "Controlled_Inventory_MANPs_20250908_1329.csv"
    )
    pd_file = os.path.join(
        outputs_folder, "Controlled_Inventory_PD_Forms_20250908_1329.csv"
    )

    manp_df = pd.read_csv(manp_file)
    pd_forms_df = pd.read_csv(pd_file)

    should_have_manps = set(
        [normalize_reference(ref) for ref in manp_df["Reference"].tolist()]
    )
    should_have_pds = set(
        [normalize_reference(ref) for ref in pd_forms_df["Reference"].tolist()]
    )

    print(
        f"Should have: {
            len(should_have_manps)} MANPs, {
            len(should_have_pds)} PD forms"
    )

    # Check what we have
    folders = [
        os.path.join(inputs_folder, "pd_forms"),
        os.path.join(inputs_folder, "sf_pd_forms"),
        os.path.join(inputs_folder, "uncontrolled_documents"),
    ]

    found_manps = set()
    found_pds = set()

    for folder in folders:
        found_manps.update(extract_references_from_files(folder, "MANP"))
        found_pds.update(extract_references_from_files(folder, "PD"))

    print(
        f"Actually have: {
            len(found_manps)} MANPs, {
            len(found_pds)} PD forms"
    )

    # Calculate missing
    missing_manps = should_have_manps - found_manps
    missing_pds = should_have_pds - found_pds

    print(f"Missing: {len(missing_manps)} MANPs, {len(missing_pds)} PD forms")

    # Create report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_file = os.path.join(
        outputs_folder, f"Missing_Documents_Report_{timestamp}.csv"
    )

    report_data = []

    # Add missing MANPs
    for manp in sorted(missing_manps):
        report_data.append(
            {
                "Type": "MANP",
                "Reference": manp,
                "Status": "Missing",
                "Required_For": "Surface Finishing NADCAP Compliance",
                "Contact_For_Document": "Scott Niedzwiecki",
                "Priority": "High",
            }
        )

    # Add missing PD forms
    for pd_form in sorted(missing_pds):
        report_data.append(
            {
                "Type": "PD Form",
                "Reference": pd_form,
                "Status": "Missing",
                "Required_For": "Surface Finishing NADCAP Compliance",
                "Contact_For_Document": "Lloyd Harrington / Dean Wilkinson",
                "Priority": "High",
            }
        )

    # Save report
    report_df = pd.DataFrame(report_data)
    report_df.to_csv(report_file, index=False)

    print(f"\n=== REPORT SAVED ===")
    print(f"File: {report_file}")
    print(f"Total missing documents: {len(report_data)}")
    print(f"  Missing MANPs: {len(missing_manps)}")
    print(f"  Missing PD Forms: {len(missing_pds)}")

    # Print summary
    print(f"\n=== MISSING MANPs ({len(missing_manps)}) ===")
    for manp in sorted(missing_manps):
        print(f"  {manp}")

    print(f"\n=== MISSING PD FORMS ({len(missing_pds)}) ===")
    for pd_form in sorted(missing_pds)[:20]:  # Show first 20
        print(f"  {pd_form}")
    if len(missing_pds) > 20:
        print(f"  ... and {len(missing_pds) - 20} more")

    return report_file


if __name__ == "__main__":
    report_file = generate_missing_documents_report()
    print(f"\nMissing documents report saved to: {report_file}")
