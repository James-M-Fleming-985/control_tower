#!/usr/bin/env python3
"""
Extract all MANP and PD form references from the controlled inventory
Outputs clean CSV files for gap analysis
"""

import os
import re
from datetime import datetime

import pandas as pd


def extract_references_from_controlled_inventory():
    """Extract all MANP and PD references from the controlled inventory Excel file"""

    # File paths
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    inputs_folder = os.path.join(base_folder, "Inputs")
    outputs_folder = os.path.join(base_folder, "outputs")

    # Read the controlled inventory
    excel_file = os.path.join(inputs_folder,
                              "Surface Finishes and MFG 030925.xlsx")

    print(f"Reading controlled inventory from: {excel_file}")

    # Read the Surface Finishes sheet
    df = pd.read_excel(excel_file, sheet_name="SURFACE FINISHES")
    print(f"Loaded {len(df)} controlled documents")

    # Initialize lists for found references
    manp_references = []
    pd_references = []

    # MANP pattern: MANP followed by numbers, dots, and dashes
    manp_pattern = r"MANP[-\s]*\d+(?:\.\d+)*(?:\.\d+)*"
    # PD pattern: PD followed by numbers
    pd_pattern = r"PD\s*\d+"

    # Search through all relevant columns
    search_columns = [
        "Source System Reference",
        "Title",
        "Notes",
        "CHEOPS Ref"]

    for idx, row in df.iterrows():
        document_info = {
            "Row": idx + 1,
            "Document_Category": str(row.get("Document Category", "")),
            "OSR_Ref": str(row.get("OSR Ref", "")),
            "CHEOPS_Ref": str(row.get("CHEOPS Ref", "")),
            "Title": str(row.get("Title", "")),
            "Source_System_Reference": str(row.get("Source System Reference", "")),
        }

        # Search each column for references
        for col_name in search_columns:
            if col_name in df.columns:
                cell_content = str(row.get(col_name, ""))

                if cell_content and cell_content != "nan":
                    # Find MANP references
                    manp_matches = re.findall(
                        manp_pattern, cell_content, re.IGNORECASE)
                    for match in manp_matches:
                        manp_ref = {
                            "Reference": match.strip(),
                            "Found_In_Column": col_name,
                            "Found_In_Content": (
                                cell_content[:100] + "..."
                                if len(cell_content) > 100
                                else cell_content
                            ),
                            **document_info,
                        }
                        manp_references.append(manp_ref)

                    # Find PD references
                    pd_matches = re.findall(
                        pd_pattern, cell_content, re.IGNORECASE)
                    for match in pd_matches:
                        pd_ref = {
                            "Reference": match.strip(),
                            "Found_In_Column": col_name,
                            "Found_In_Content": (
                                cell_content[:100] + "..."
                                if len(cell_content) > 100
                                else cell_content
                            ),
                            **document_info,
                        }
                        pd_references.append(pd_ref)

    # Create DataFrames
    manp_df = pd.DataFrame(manp_references)
    pd_df = pd.DataFrame(pd_references)

    # Remove duplicates based on reference number
    if not manp_df.empty:
        manp_df["Reference_Clean"] = (
            manp_df["Reference"].str.replace(
                r"[-\s]", "", regex=True).str.upper()
        )
        manp_df = manp_df.drop_duplicates(subset=["Reference_Clean"])
        manp_df = manp_df.sort_values("Reference_Clean")

    if not pd_df.empty:
        pd_df["Reference_Clean"] = (
            pd_df["Reference"].str.replace(
                r"[-\s]", "", regex=True).str.upper()
        )
        pd_df = pd_df.drop_duplicates(subset=["Reference_Clean"])
        pd_df = pd_df.sort_values("Reference_Clean")

    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # Save to CSV files
    manp_output_file = os.path.join(
        outputs_folder, f"Controlled_Inventory_MANPs_{timestamp}.csv"
    )
    pd_output_file = os.path.join(
        outputs_folder, f"Controlled_Inventory_PD_Forms_{timestamp}.csv"
    )

    if not manp_df.empty:
        manp_df.to_csv(manp_output_file, index=False)
        print(f"\n=== MANP REFERENCES ===")
        print(f"Total MANP references found: {len(manp_df)}")
        print(f"Unique MANPs saved to: {manp_output_file}")
        print("\nMANP References found:")
        for ref in manp_df["Reference"].tolist():
            print(f"  {ref}")
    else:
        print("\n=== MANP REFERENCES ===")
        print("No MANP references found in controlled inventory")

    if not pd_df.empty:
        pd_df.to_csv(pd_output_file, index=False)
        print(f"\n=== PD FORM REFERENCES ===")
        print(f"Total PD form references found: {len(pd_df)}")
        print(f"Unique PD forms saved to: {pd_output_file}")
        print("\nPD Form References found:")
        for ref in pd_df["Reference"].tolist():
            print(f"  {ref}")
    else:
        print("\n=== PD FORM REFERENCES ===")
        print("No PD form references found in controlled inventory")

    # Create summary file
    summary_file = os.path.join(
        outputs_folder, f"Controlled_Inventory_Summary_{timestamp}.csv"
    )
    summary_data = []

    if not manp_df.empty:
        for ref in manp_df["Reference"].tolist():
            summary_data.append(
                {"Type": "MANP", "Reference": ref,
                    "Source": "Controlled Inventory"}
            )

    if not pd_df.empty:
        for ref in pd_df["Reference"].tolist():
            summary_data.append(
                {"Type": "PD Form", "Reference": ref,
                    "Source": "Controlled Inventory"}
            )

    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(summary_file, index=False)
        print(f"\n=== SUMMARY ===")
        print(f"Combined summary saved to: {summary_file}")
        print(f"Total references: {len(summary_data)}")
        print(f"  MANPs: {len(manp_df) if not manp_df.empty else 0}")
        print(f"  PD Forms: {len(pd_df) if not pd_df.empty else 0}")

    return manp_df, pd_df


if __name__ == "__main__":
    print("Extracting MANP and PD Form references from controlled inventory...")
    print("=" * 70)

    manp_df, pd_df = extract_references_from_controlled_inventory()

    print("\n" + "=" * 70)
    print("Analysis complete! CSV files generated in outputs folder.")
