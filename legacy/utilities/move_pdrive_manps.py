#!/usr/bin/env python3
"""
Move MANPs from PDRIVE Inventory to sf_manps folder
- Identifies MANPs that appear in PDRIVE_inventory.xlsx
- Moves matching files from uncontrolled_documents to sf_manps
- Ensures clean separation for gap analysis
"""

import os
import re
import shutil
from datetime import datetime

import pandas as pd


def normalize_reference(ref):
    """Normalize reference format for comparison"""
    if not ref or str(ref) == "nan":
        return None

    ref_str = str(ref).upper().strip()

    if "MANP" in ref_str:
        numbers = re.search(r"(\d+(?:\.\d+)*(?:\.\d+)*)", ref_str)
        if numbers:
            return f"MANP-{numbers.group(1)}"
    elif "PD" in ref_str:
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


def extract_manp_reference_from_filename(filename):
    """Extract MANP reference from filename"""
    manp_match = re.search(
        r"MANP[-\s]*(\d+(?:\.\d+)*(?:\.\d+)*)", filename, re.IGNORECASE
    )
    if manp_match:
        return f"MANP-{manp_match.group(1)}"
    return None


def move_pdrive_manps_to_sf_folder():
    """Move MANPs that appear in PDRIVE inventory to sf_manps folder"""

    print("Moving PDRIVE MANPs to sf_manps folder")
    print("=" * 60)

    # Paths
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    inputs_folder = os.path.join(base_folder, "Inputs")

    source_folder = os.path.join(inputs_folder, "uncontrolled_documents")
    target_folder = os.path.join(inputs_folder, "sf_manps")

    # Create target folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"Created target folder: {target_folder}")

    # Load PDRIVE inventory
    inventory_file = os.path.join(inputs_folder, "PDRIVE_inventory.xlsx")

    if not os.path.exists(inventory_file):
        print(f"ERROR: PDRIVE_inventory.xlsx not found at {inventory_file}")
        return

    print(f"Loading PDRIVE inventory from: {inventory_file}")
    inventory_df = pd.read_excel(inventory_file)

    # Get PDRIVE MANP references (normalized)
    pdrive_manp_references = set()

    for ref in inventory_df["Document Number"]:
        norm_ref = normalize_reference(ref)
        if norm_ref and norm_ref.startswith("MANP"):
            pdrive_manp_references.add(norm_ref)

    print(f"PDRIVE MANP references found: {len(pdrive_manp_references)}")

    # Get files in source folder
    if not os.path.exists(source_folder):
        print(f"ERROR: Source folder not found: {source_folder}")
        return

    source_files = []
    for file in os.listdir(source_folder):
        if os.path.isfile(os.path.join(source_folder, file)):
            source_files.append(file)

    print(f"Files in uncontrolled_documents: {len(source_files)}")

    # Find MANPs to move
    files_to_move = []
    files_not_in_pdrive = []

    for filename in source_files:
        manp_ref = extract_manp_reference_from_filename(filename)

        if manp_ref:  # It's a MANP file
            if manp_ref in pdrive_manp_references:
                files_to_move.append(
                    {
                        "filename": filename,
                        "reference": manp_ref,
                        "status": "In PDRIVE - Will Move",
                    }
                )
            else:
                files_not_in_pdrive.append(
                    {
                        "filename": filename,
                        "reference": manp_ref,
                        "status": "NOT in PDRIVE - Will Stay",
                    }
                )

    print(f"\nAnalysis Results:")
    print(f"  📂 MANP files to move to sf_manps: {len(files_to_move)}")
    print(
        f"  📂 MANP files to stay in uncontrolled: {
            len(files_not_in_pdrive)}"
    )
    print(
        f"  📂 Non-MANP files (unchanged): {
            len(source_files) -
            len(files_to_move) -
            len(files_not_in_pdrive)}"
    )

    # Show what will be moved
    if files_to_move:
        print(f"\n=== FILES TO MOVE ({len(files_to_move)}) ===")
        for item in files_to_move[:10]:  # Show first 10
            print(f"  📄 {item['reference']}: {item['filename']}")
        if len(files_to_move) > 10:
            print(f"  ... and {len(files_to_move) - 10} more")

    # Show what will stay
    if files_not_in_pdrive:
        print(
            f"\n=== MANP FILES STAYING IN UNCONTROLLED ({
                len(files_not_in_pdrive)}) ==="
        )
        for item in files_not_in_pdrive[:5]:  # Show first 5
            print(f"  📄 {item['reference']}: {item['filename']}")
        if len(files_not_in_pdrive) > 5:
            print(f"  ... and {len(files_not_in_pdrive) - 5} more")

    # Confirm before moving
    print(
        f"\n🔄 Ready to move {
            len(files_to_move)} MANP files from uncontrolled_documents to sf_manps"
    )

    # Perform the moves
    moved_files = []
    errors = []

    for item in files_to_move:
        source_path = os.path.join(source_folder, item["filename"])
        target_path = os.path.join(target_folder, item["filename"])

        try:
            shutil.move(source_path, target_path)
            moved_files.append(item)
            print(f"  ✅ Moved: {item['filename']}")
        except Exception as e:
            errors.append({"filename": item["filename"], "error": str(e)})
            print(f"  ❌ Error moving {item['filename']}: {e}")

    # Create summary report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    outputs_folder = os.path.join(base_folder, "outputs")

    # Summary data
    summary_data = []

    # Add moved files
    for item in moved_files:
        summary_data.append(
            {
                "Action": "Moved to sf_manps",
                "Reference": item["reference"],
                "Filename": item["filename"],
                "Reason": "Found in PDRIVE inventory",
            }
        )

    # Add files that stayed
    for item in files_not_in_pdrive:
        summary_data.append(
            {
                "Action": "Stayed in uncontrolled",
                "Reference": item["reference"],
                "Filename": item["filename"],
                "Reason": "NOT in PDRIVE inventory",
            }
        )

    # Add errors
    for error in errors:
        summary_data.append(
            {
                "Action": "ERROR",
                "Reference": "Unknown",
                "Filename": error["filename"],
                "Reason": f"Move failed: {error['error']}",
            }
        )

    # Save summary
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_file = os.path.join(
            outputs_folder, f"MANP_Move_Summary_{timestamp}.xlsx"
        )
        summary_df.to_excel(summary_file, index=False)
        print(f"\n📊 Summary saved to: {summary_file}")

    print(f"\n=== MOVE OPERATION COMPLETE ===")
    print(f"✅ Successfully moved: {len(moved_files)} files")
    print(f"❌ Errors: {len(errors)} files")
    print(
        f"📂 sf_manps folder now contains: {
            len(moved_files)} MANP files from PDRIVE inventory"
    )
    print(
        f"📂 uncontrolled_documents still contains: {
            len(files_not_in_pdrive)} MANP files NOT in PDRIVE"
    )

    # Verify final state
    final_sf_manps_count = len(
        [
            f
            for f in os.listdir(target_folder)
            if os.path.isfile(os.path.join(target_folder, f))
        ]
    )
    remaining_uncontrolled_count = len(
        [
            f
            for f in os.listdir(source_folder)
            if os.path.isfile(os.path.join(source_folder, f))
        ]
    )

    print(f"\n=== VERIFICATION ===")
    print(f"📁 sf_manps folder: {final_sf_manps_count} files")
    print(
        f"📁 uncontrolled_documents folder: {remaining_uncontrolled_count} files")

    return {
        "moved": len(moved_files),
        "stayed": len(files_not_in_pdrive),
        "errors": len(errors),
    }


if __name__ == "__main__":
    result = move_pdrive_manps_to_sf_folder()
    if result:
        print(f"\n✅ MANP organization complete!")
        print(f"📂 Ready for clean gap analysis with organized folders")
        print(f"🎯 sf_manps now contains only PDRIVE-tracked MANPs")
