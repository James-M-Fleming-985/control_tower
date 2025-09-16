#!/usr/bin/env python3
"""
Complete Inventory Analysis: PDRIVE vs VS Code Folders
- Marks PDRIVE inventory items as found/missing
- Identifies documents in VS Code that are NOT in PDRIVE inventory
- Creates comprehensive status report
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


def scan_folder_for_files(folder_path):
    """Get all files in a folder"""
    files = []
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, file)):
                files.append(file)
    return files


def extract_references_from_filenames(file_list):
    """Extract MANP and PD references from filenames with file mapping"""
    references_to_files = {}

    for filename in file_list:
        # Try to extract MANP references
        manp_match = re.search(
            r"MANP[-\s]*(\d+(?:\.\d+)*(?:\.\d+)*)", filename, re.IGNORECASE
        )
        if manp_match:
            ref = f"MANP-{manp_match.group(1)}"
            if ref not in references_to_files:
                references_to_files[ref] = []
            references_to_files[ref].append(filename)

        # Try to extract PD references
        pd_match = re.search(r"PD[-\s]*(\d+)", filename, re.IGNORECASE)
        if pd_match:
            ref = f"PD{pd_match.group(1)}"
            if ref not in references_to_files:
                references_to_files[ref] = []
            references_to_files[ref].append(filename)

    return references_to_files


def complete_inventory_analysis():
    """Complete analysis: PDRIVE inventory + orphaned documents"""

    print("Complete Inventory Analysis: PDRIVE vs VS Code Folders")
    print("=" * 80)

    # Paths
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    inputs_folder = os.path.join(base_folder, "Inputs")
    outputs_folder = os.path.join(base_folder, "outputs")

    # Load PDRIVE inventory
    inventory_file = os.path.join(inputs_folder, "PDRIVE_inventory.xlsx")

    if not os.path.exists(inventory_file):
        print(f"ERROR: PDRIVE_inventory.xlsx not found at {inventory_file}")
        return

    print(f"Loading PDRIVE inventory from: {inventory_file}")

    inventory_df = pd.read_excel(inventory_file)
    print(f"PDRIVE inventory: {len(inventory_df)} items")

    # Get PDRIVE references
    pdrive_references = set()
    for ref in inventory_df["Document Number"]:
        norm_ref = normalize_reference(ref)
        if norm_ref:
            pdrive_references.add(norm_ref)

    print(f"PDRIVE normalized references: {len(pdrive_references)}")

    # Scan our 3 folders
    folders = {
        "pd_forms": os.path.join(inputs_folder, "pd_forms"),
        "sf_pd_forms": os.path.join(inputs_folder, "sf_pd_forms"),
        "uncontrolled_documents": os.path.join(inputs_folder, "uncontrolled_documents"),
    }

    all_our_references_to_files = {}
    folder_details = {}

    for folder_name, folder_path in folders.items():
        print(f"\nScanning folder: {folder_name}")

        files = scan_folder_for_files(folder_path)
        references_to_files = extract_references_from_filenames(files)

        print(f"  Files: {len(files)}")
        print(f"  References: {len(references_to_files)}")

        # Merge into overall collection
        for ref, files_list in references_to_files.items():
            if ref not in all_our_references_to_files:
                all_our_references_to_files[ref] = {}
            all_our_references_to_files[ref][folder_name] = files_list

        folder_details[folder_name] = {
            "files": files,
            "references_to_files": references_to_files,
        }

    all_our_references = set(all_our_references_to_files.keys())
    print(
        f"\nTotal unique references in our folders: {
            len(all_our_references)}"
    )

    # PART 1: Check PDRIVE inventory against what we have
    print(f"\n=== PART 1: CHECKING PDRIVE INVENTORY ===")

    inventory_df["Reference_Normalized"] = inventory_df["Document Number"].apply(
        normalize_reference
    )
    inventory_df["Have_Document"] = False
    inventory_df["Found_In_Folder"] = ""
    inventory_df["Filename_Examples"] = ""
    inventory_df["Status"] = "Missing from VS Code"

    pdrive_matches = 0

    for idx, row in inventory_df.iterrows():
        ref_norm = row["Reference_Normalized"]

        if ref_norm and ref_norm in all_our_references:
            inventory_df.at[idx, "Have_Document"] = True
            inventory_df.at[idx, "Status"] = "Found in VS Code"
            pdrive_matches += 1

            # Get folder and file details
            folders_found = []
            example_files = []

            for folder_name, files_list in all_our_references_to_files[
                ref_norm
            ].items():
                folders_found.append(folder_name)
                # Max 2 examples per folder
                example_files.extend(files_list[:2])

            inventory_df.at[idx, "Found_In_Folder"] = ", ".join(folders_found)
            inventory_df.at[idx, "Filename_Examples"] = ", ".join(
                example_files[:3]
            )  # Max 3 total examples

    print(f"PDRIVE items we have: {pdrive_matches}")
    print(f"PDRIVE items missing: {len(inventory_df) - pdrive_matches}")

    # PART 2: Find orphaned documents (in our folders but NOT in PDRIVE)
    print(f"\n=== PART 2: FINDING ORPHANED DOCUMENTS ===")

    orphaned_references = all_our_references - pdrive_references
    print(
        f"Orphaned documents (in VS Code but NOT in PDRIVE): {
            len(orphaned_references)}"
    )

    # Create orphaned documents DataFrame
    orphaned_data = []

    for ref in sorted(orphaned_references):
        # Determine document type
        if ref.startswith("MANP"):
            doc_type = "MANP"
            department = "Surface Finishing"  # Assume SF for MANPs
        elif ref.startswith("PD"):
            doc_type = "PD Form"
            department = "Unknown"  # We don't know department for orphaned PDs
        else:
            doc_type = "Unknown"
            department = "Unknown"

        # Get folder and file details
        folders_found = []
        example_files = []

        for folder_name, files_list in all_our_references_to_files[ref].items(
        ):
            folders_found.append(folder_name)
            example_files.extend(files_list[:2])

        orphaned_data.append(
            {
                "Document Type": doc_type,
                "Document Number": (
                    ref.replace("MANP-", "").replace("PD", "")
                    if ref.startswith(("MANP", "PD"))
                    else ref
                ),
                "Department": department,
                "Title": "NOT IN PDRIVE INVENTORY",
                "Reference_Normalized": ref,
                "Have_Document": True,
                "Found_In_Folder": ", ".join(folders_found),
                "Filename_Examples": ", ".join(example_files[:3]),
                "Status": "Orphaned (Not in PDRIVE inventory)",
            }
        )

    orphaned_df = pd.DataFrame(orphaned_data)

    # PART 3: Combine everything
    print(f"\n=== PART 3: CREATING COMPLETE INVENTORY ===")

    # Reorder columns for consistency
    column_order = [
        "Status",
        "Have_Document",
        "Document Type",
        "Document Number",
        "Reference_Normalized",
        "Department",
        "Title",
        "Found_In_Folder",
        "Filename_Examples",
    ]

    # Ensure both DataFrames have the same columns
    for col in column_order:
        if col not in inventory_df.columns:
            inventory_df[col] = ""
        if col not in orphaned_df.columns:
            orphaned_df[col] = ""

    # Reorder columns
    inventory_df = inventory_df[column_order]
    orphaned_df = orphaned_df[column_order]

    # Combine DataFrames
    complete_df = pd.concat([inventory_df, orphaned_df], ignore_index=True)

    # Save complete inventory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(
        outputs_folder, f"Complete_Inventory_Analysis_{timestamp}.xlsx"
    )

    # Create multiple sheets
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        # Sheet 1: Complete inventory
        complete_df.to_excel(
            writer,
            sheet_name="Complete_Inventory",
            index=False)

        # Sheet 2: Missing from VS Code
        missing_df = complete_df[complete_df["Status"]
                                 == "Missing from VS Code"]
        missing_df.to_excel(
            writer,
            sheet_name="Missing_From_VSCode",
            index=False)

        # Sheet 3: Orphaned documents
        orphaned_df.to_excel(
            writer,
            sheet_name="Orphaned_Documents",
            index=False)

        # Sheet 4: Summary
        summary_data = [
            ["Metric", "Count"],
            ["Total PDRIVE Inventory Items", len(inventory_df)],
            ["PDRIVE Items We Have", pdrive_matches],
            ["PDRIVE Items Missing", len(inventory_df) - pdrive_matches],
            ["PDRIVE Coverage %",
             f"{(pdrive_matches / len(inventory_df) * 100):.1f}%"],
            [""],
            ["Orphaned Documents (Not in PDRIVE)", len(orphaned_references)],
            ["Total Unique Documents in VS Code", len(all_our_references)],
            [""],
            ["Complete Inventory Total", len(complete_df)],
        ]
        summary_df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

    print(f"\n=== COMPLETE ANALYSIS RESULTS ===")
    print(f"📋 Total PDRIVE inventory items: {len(inventory_df)}")
    print(f"✅ PDRIVE items we have: {pdrive_matches}")
    print(f"❌ PDRIVE items missing: {len(inventory_df) - pdrive_matches}")
    print(
        f"📊 PDRIVE coverage: {(pdrive_matches / len(inventory_df) * 100):.1f}%")
    print(f"")
    print(f"🔍 Orphaned documents (not in PDRIVE): {len(orphaned_references)}")
    print(f"📁 Total unique documents in VS Code: {len(all_our_references)}")
    print(f"📄 Complete inventory total: {len(complete_df)}")

    print(f"\n=== OUTPUT SAVED ===")
    print(f"File: {output_file}")
    print(f"Sheets created:")
    print(f"  - Complete_Inventory: All documents with status")
    print(
        f"  - Missing_From_VSCode: {len(inventory_df) -
                                    pdrive_matches} missing documents"
    )
    print(
        f"  - Orphaned_Documents: {len(orphaned_references)} orphaned documents")
    print(f"  - Summary: Analysis statistics")

    # Show some orphaned examples
    if len(orphaned_references) > 0:
        print(f"\n=== SAMPLE ORPHANED DOCUMENTS ===")
        for ref in sorted(orphaned_references)[:10]:
            folders = list(all_our_references_to_files[ref].keys())
            print(f"  🔍 {ref} (found in: {', '.join(folders)})")
        if len(orphaned_references) > 10:
            print(
                f"  ... and {
                    len(orphaned_references) -
                    10} more orphaned documents"
            )

    return output_file


if __name__ == "__main__":
    output_file = complete_inventory_analysis()
    if output_file:
        print(f"\n✅ Complete inventory analysis finished!")
        print(f"📂 Results saved to: {output_file}")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review 'Missing_From_VSCode' sheet for documents to chase")
        print(f"   2. Review 'Orphaned_Documents' sheet for potential PDRIVE additions")
        print(f"   3. Use complete inventory to track progress")
