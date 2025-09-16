#!/usr/bin/env python3
"""
Check PDRIVE Inventory Against VS Code Folders
Marks which documents we have vs don't have in our 3 folders
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

    return ref_str


def scan_folder_for_files(folder_path):
    """Get all files in a folder"""
    files = []
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, file)):
                files.append(file)
    return files


def extract_references_from_filenames(file_list):
    """Extract MANP and PD references from filenames"""
    references = set()

    for filename in file_list:
        # Try to extract MANP references
        manp_match = re.search(
            r"MANP[-\s]*(\d+(?:\.\d+)*(?:\.\d+)*)", filename, re.IGNORECASE
        )
        if manp_match:
            references.add(f"MANP-{manp_match.group(1)}")

        # Try to extract PD references
        pd_match = re.search(r"PD[-\s]*(\d+)", filename, re.IGNORECASE)
        if pd_match:
            references.add(f"PD{pd_match.group(1)}")

    return references


def check_inventory_against_folders():
    """Check PDRIVE inventory against our VS Code folders"""

    print("Checking PDRIVE Inventory Against VS Code Folders...")
    print("=" * 70)

    # Paths
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    inputs_folder = os.path.join(base_folder, "Inputs")
    outputs_folder = os.path.join(base_folder, "outputs")

    # Load PDRIVE inventory
    inventory_file = os.path.join(inputs_folder, "PDRIVE_inventory.xlsx")

    if not os.path.exists(inventory_file):
        print(f"ERROR: PDRIVE_inventory.xlsx not found at {inventory_file}")
        return

    print(f"Loading inventory from: {inventory_file}")

    # Try to read the Excel file - check what sheets are available
    try:
        excel_data = pd.read_excel(inventory_file, sheet_name=None)
        print(f"Available sheets: {list(excel_data.keys())}")

        # Use the first sheet or look for common names
        if "Sheet1" in excel_data:
            inventory_df = excel_data["Sheet1"]
        elif "Inventory" in excel_data:
            inventory_df = excel_data["Inventory"]
        elif "PDRIVE" in excel_data:
            inventory_df = excel_data["PDRIVE"]
        else:
            # Use the first sheet
            sheet_name = list(excel_data.keys())[0]
            inventory_df = excel_data[sheet_name]
            print(f"Using sheet: {sheet_name}")

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    print(f"Loaded inventory with {len(inventory_df)} rows")
    print(f"Columns: {list(inventory_df.columns)}")

    # Scan our 3 folders
    folders = {
        "pd_forms": os.path.join(inputs_folder, "pd_forms"),
        "sf_pd_forms": os.path.join(inputs_folder, "sf_pd_forms"),
        "uncontrolled_documents": os.path.join(inputs_folder, "uncontrolled_documents"),
    }

    all_our_files = []
    all_our_references = set()

    folder_details = {}

    for folder_name, folder_path in folders.items():
        print(f"\nScanning folder: {folder_name}")
        print(f"Path: {folder_path}")

        files = scan_folder_for_files(folder_path)
        references = extract_references_from_filenames(files)

        print(f"  Files found: {len(files)}")
        print(f"  References extracted: {len(references)}")

        all_our_files.extend(files)
        all_our_references.update(references)

        folder_details[folder_name] = {
            "files": files, "references": references}

    print(
        f"\nTotal unique references across all folders: {
            len(all_our_references)}"
    )
    print(f"Total files across all folders: {len(all_our_files)}")

    # Now check inventory against what we have
    inventory_df["Reference_Normalized"] = inventory_df["Document Number"].apply(
        normalize_reference
    )

    # Add columns to track what we have
    inventory_df["Have_Document"] = False
    inventory_df["Found_In_Folder"] = ""
    inventory_df["Filename_Match"] = ""

    # Check each inventory item
    matches_found = 0

    for idx, row in inventory_df.iterrows():
        ref_norm = row["Reference_Normalized"]

        if ref_norm and ref_norm in all_our_references:
            inventory_df.at[idx, "Have_Document"] = True
            matches_found += 1

            # Find which folder(s) contain this reference
            found_folders = []
            found_files = []

            for folder_name, details in folder_details.items():
                if ref_norm in details["references"]:
                    found_folders.append(folder_name)
                    # Find the specific file(s)
                    for file in details["files"]:
                        file_refs = extract_references_from_filenames([file])
                        if ref_norm in file_refs:
                            found_files.append(file)

            inventory_df.at[idx, "Found_In_Folder"] = ", ".join(found_folders)
            inventory_df.at[idx, "Filename_Match"] = ", ".join(
                found_files[:3]
            )  # Limit to first 3 matches

    print(f"\n=== MATCHING RESULTS ===")
    print(f"Inventory items: {len(inventory_df)}")
    print(f"Items we have: {matches_found}")
    print(f"Items we're missing: {len(inventory_df) - matches_found}")
    print(f"Coverage: {(matches_found / len(inventory_df) * 100):.1f}%")

    # Save updated inventory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(
        outputs_folder, f"PDRIVE_Inventory_Checked_{timestamp}.xlsx"
    )

    # Create summary columns at the beginning
    result_df = inventory_df.copy()
    cols = list(result_df.columns)

    # Reorder columns to put status first
    status_cols = [
        "Have_Document",
        "Found_In_Folder",
        "Filename_Match",
        "Reference_Normalized",
    ]
    other_cols = [col for col in cols if col not in status_cols]
    new_order = status_cols + other_cols

    result_df = result_df[new_order]

    # Save to Excel
    result_df.to_excel(output_file, index=False)

    print(f"\n=== OUTPUT SAVED ===")
    print(f"Updated inventory saved to: {output_file}")

    # Show summary stats
    have_count = result_df["Have_Document"].sum()
    missing_count = len(result_df) - have_count

    print(f"\nSummary:")
    print(f"  ✅ Have: {have_count} documents")
    print(f"  ❌ Missing: {missing_count} documents")
    print(f"  📊 Coverage: {(have_count / len(result_df) * 100):.1f}%")

    # Show some examples of what we're missing
    missing_items = result_df[~result_df["Have_Document"]]
    if len(missing_items) > 0:
        print(f"\n=== SAMPLE MISSING ITEMS ===")
        for idx, row in missing_items.head(10).iterrows():
            ref = (
                row["Reference_Normalized"]
                if row["Reference_Normalized"]
                else row["Document Number"]
            )
            doc_type = row["Document Type"]
            print(f"  ❌ {ref} ({doc_type})")
        if len(missing_items) > 10:
            print(f"  ... and {len(missing_items) - 10} more")

    return output_file


if __name__ == "__main__":
    output_file = check_inventory_against_folders()
    if output_file:
        print(f"\n✅ Inventory check complete! Results saved to: {output_file}")
