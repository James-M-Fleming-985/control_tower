#!/usr/bin/env python3
"""
Final NADCAP Gap Analysis & Action Plan Generator
- Current state analysis with available documents
- Gap identification against official requirements
- Step-by-step action plan generation
- Ready for Scott consultation
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


def extract_references_from_filenames(file_list):
    """Extract references from filenames"""
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


def scan_folder_for_files(folder_path):
    """Get all files in a folder"""
    files = []
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, file)):
                files.append(file)
    return files


def final_gap_analysis_and_action_plan():
    """Generate final gap analysis and comprehensive action plan"""

    print("FINAL NADCAP GAP ANALYSIS & ACTION PLAN")
    print("=" * 80)

    # Paths
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    inputs_folder = os.path.join(base_folder, "Inputs")
    outputs_folder = os.path.join(base_folder, "outputs")

    # 1. Load official requirements (from controlled inventory analysis)
    print("📋 STEP 1: Loading Official Requirements")

    # Check if we have the controlled inventory extraction results
    controlled_refs_file = os.path.join(
        outputs_folder, "controlled_inventory_references_20250908_1330.csv"
    )

    if os.path.exists(controlled_refs_file):
        print(f"   Loading from: {controlled_refs_file}")
        controlled_df = pd.read_csv(controlled_refs_file)

        # Get official requirements
        official_manps = set()
        official_pds = set()

        for _, row in controlled_df.iterrows():
            if row["Type"] == "MANP":
                official_manps.add(f"MANP-{row['Reference']}")
            elif row["Type"] == "PD":
                official_pds.add(f"PD{row['Reference']}")

        print(f"   📑 Official MANPs required: {len(official_manps)}")
        print(f"   📄 Official PD forms required: {len(official_pds)}")
    else:
        print(
            "   ⚠️  Controlled inventory file not found - using placeholder requirements"
        )
        # Use known requirements from previous analysis
        official_manps = {
            f"MANP-3.3.{i}" for i in range(600, 641)}  # Example set
        official_pds = {f"PD{i}" for i in range(100, 200)}  # Example set

    all_official_requirements = official_manps | official_pds

    # 2. Current state inventory
    print(f"\n📁 STEP 2: Current State Inventory")

    # Scan current folders
    folders = {
        "pd_forms": os.path.join(inputs_folder, "pd_forms"),
        "sf_pd_forms": os.path.join(inputs_folder, "sf_pd_forms"),
        "uncontrolled_documents": os.path.join(inputs_folder, "uncontrolled_documents"),
    }

    all_current_references = set()
    folder_details = {}

    for folder_name, folder_path in folders.items():
        files = scan_folder_for_files(folder_path)
        references_to_files = extract_references_from_filenames(files)

        print(
            f"   📂 {folder_name}: {
                len(files)} files, {
                len(references_to_files)} references"
        )

        all_current_references.update(references_to_files.keys())
        folder_details[folder_name] = {
            "files": files,
            "references": references_to_files,
        }

    print(
        f"   📊 Total current unique references: {
            len(all_current_references)}"
    )

    # Account for the 52 additional PD forms found but not moved
    print(f"   ➕ Plus 52 additional PD forms identified but not yet organized")

    # 3. Gap Analysis
    print(f"\n🔍 STEP 3: Gap Analysis")

    # What we have vs what's required
    have_official = all_current_references & all_official_requirements
    missing_official = all_official_requirements - all_current_references
    extra_documents = all_current_references - all_official_requirements

    # Break down by type
    missing_manps = {ref for ref in missing_official if ref.startswith("MANP")}
    missing_pds = {ref for ref in missing_official if ref.startswith("PD")}

    have_manps = {ref for ref in have_official if ref.startswith("MANP")}
    have_pds = {ref for ref in have_official if ref.startswith("PD")}

    print(f"   ✅ Have (official requirements): {len(have_official)}")
    print(f"      📑 MANPs: {len(have_manps)}")
    print(f"      📄 PD forms: {len(have_pds)}")
    print(f"   ❌ Missing (official requirements): {len(missing_official)}")
    print(f"      📑 MANPs: {len(missing_manps)}")
    print(f"      📄 PD forms: {len(missing_pds)}")
    print(
        f"   📋 Extra documents (not in requirements): {
            len(extra_documents)}"
    )

    # Coverage percentages
    manp_coverage = (
        (len(have_manps) / len(official_manps) * 100) if official_manps else 0
    )
    pd_coverage = (
        len(have_pds) /
        len(official_pds) *
        100) if official_pds else 0
    overall_coverage = (
        (len(have_official) / len(all_official_requirements) * 100)
        if all_official_requirements
        else 0
    )

    print(f"   📊 Coverage Rates:")
    print(f"      📑 MANP Coverage: {manp_coverage:.1f}%")
    print(f"      📄 PD Form Coverage: {pd_coverage:.1f}%")
    print(f"      🎯 Overall Coverage: {overall_coverage:.1f}%")

    # 4. Generate Action Plan
    print(f"\n🎯 STEP 4: Comprehensive Action Plan")

    action_plan = []

    # Immediate actions
    action_plan.append(
        {
            "Priority": "HIGH",
            "Category": "Stakeholder Engagement",
            "Action": "Contact Scott Niedzwiecki for MANP inventory consultation",
            "Details": f"Discuss {len(missing_manps)} missing MANPs and verify inventory completeness",
            "Timeline": "This Week",
            "Status": "PENDING",
        }
    )

    action_plan.append(
        {
            "Priority": "HIGH",
            "Category": "Document Organization",
            "Action": "Organize 52 additional PD forms found in analysis",
            "Details": "Move identified PD forms to sf_pd_forms folder for proper tracking",
            "Timeline": "This Week",
            "Status": "PENDING",
        }
    )

    # Document procurement
    if missing_pds:
        action_plan.append(
            {
                "Priority": "HIGH",
                "Category": "Document Procurement",
                "Action": f"Acquire {len(missing_pds)} missing PD forms",
                "Details": "Contact Lloyd Harrington/Dean Wilkinson for missing PD forms from official requirements",
                "Timeline": "2 Weeks",
                "Status": "PENDING",
            }
        )

    if missing_manps:
        action_plan.append(
            {
                "Priority": "MEDIUM",
                "Category": "Document Procurement",
                "Action": f"Acquire {len(missing_manps)} missing MANPs",
                "Details": "Work with Scott to identify sources for missing MANP documents",
                "Timeline": "3 Weeks",
                "Status": "PENDING",
            }
        )

    # Learning exercise
    action_plan.append(
        {
            "Priority": "MEDIUM",
            "Category": "Content Analysis",
            "Action": "Analyze 34 candidate SF-specific MANPs for content and titles",
            "Details": "Learning exercise to understand MANP content and populate title information",
            "Timeline": "2 Weeks",
            "Status": "PENDING",
        }
    )

    # Documentation management
    action_plan.append(
        {
            "Priority": "LOW",
            "Category": "Documentation Management",
            "Action": f"Review {len(extra_documents)} extra documents for relevance",
            "Details": "Determine if extra documents should be retained or archived",
            "Timeline": "4 Weeks",
            "Status": "PENDING",
        }
    )

    # System improvements
    action_plan.append(
        {
            "Priority": "MEDIUM",
            "Category": "Process Improvement",
            "Action": "Establish document tracking system",
            "Details": "Create systematic approach for ongoing NADCAP document management",
            "Timeline": "3 Weeks",
            "Status": "PENDING",
        }
    )

    # 5. Create comprehensive output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = os.path.join(
        outputs_folder, f"Final_NADCAP_Gap_Analysis_Action_Plan_{timestamp}.xlsx"
    )

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        # Gap analysis summary
        gap_data = [
            ["Category", "Required", "Have", "Missing", "Coverage %"],
            [
                "MANPs",
                len(official_manps),
                len(have_manps),
                len(missing_manps),
                f"{manp_coverage:.1f}%",
            ],
            [
                "PD Forms",
                len(official_pds),
                len(have_pds),
                len(missing_pds),
                f"{pd_coverage:.1f}%",
            ],
            [
                "TOTAL",
                len(all_official_requirements),
                len(have_official),
                len(missing_official),
                f"{overall_coverage:.1f}%",
            ],
        ]
        gap_df = pd.DataFrame(gap_data[1:], columns=gap_data[0])
        gap_df.to_excel(writer, sheet_name="Gap_Analysis_Summary", index=False)

        # Action plan
        action_df = pd.DataFrame(action_plan)
        action_df.to_excel(writer, sheet_name="Action_Plan", index=False)

        # Missing documents detail
        missing_detail = []
        for ref in sorted(missing_manps):
            missing_detail.append(
                {"Type": "MANP", "Reference": ref,
                    "Priority": "Discuss with Scott"}
            )
        for ref in sorted(missing_pds):
            missing_detail.append(
                {"Type": "PD Form", "Reference": ref,
                    "Priority": "Contact Lloyd/Dean"}
            )

        missing_df = pd.DataFrame(missing_detail)
        missing_df.to_excel(
            writer,
            sheet_name="Missing_Documents",
            index=False)

        # Current inventory
        current_detail = []
        for folder_name, details in folder_details.items():
            for ref, files in details["references"].items():
                current_detail.append(
                    {
                        "Reference": ref,
                        "Folder": folder_name,
                        "Files_Count": len(files),
                        "Example_File": files[0] if files else "",
                        "Status": (
                            "Official Requirement"
                            if ref in all_official_requirements
                            else "Extra Document"
                        ),
                    }
                )

        current_df = pd.DataFrame(current_detail)
        current_df.to_excel(
            writer,
            sheet_name="Current_Inventory",
            index=False)

    # 6. Print action plan summary
    print(f"\n📋 ACTION PLAN SUMMARY ({len(action_plan)} items):")
    for i, action in enumerate(action_plan, 1):
        print(f"   {i}. [{action['Priority']}] {action['Action']}")
        print(f"      ⏱️  Timeline: {action['Timeline']}")
        print(f"      📝 Details: {action['Details']}")
        print()

    print(f"=== NEXT STEPS FOR SCOTT MEETING ===")
    print(f"📊 Present gap analysis: {overall_coverage:.1f}% coverage")
    print(f"📑 Discuss {len(missing_manps)} missing MANPs")
    print(f"📄 Plan for {len(missing_pds)} missing PD forms")
    print(f"📂 Review extra documents strategy")
    print(f"🔄 Establish ongoing document management process")

    print(f"\n=== OUTPUT SAVED ===")
    print(f"📂 File: {output_file}")
    print(
        f"📊 Sheets: Gap_Analysis_Summary, Action_Plan, Missing_Documents, Current_Inventory"
    )

    return output_file, {
        "overall_coverage": overall_coverage,
        "missing_manps": len(missing_manps),
        "missing_pds": len(missing_pds),
        "total_actions": len(action_plan),
    }


if __name__ == "__main__":
    output_file, summary = final_gap_analysis_and_action_plan()
    if output_file:
        print(f"\n✅ Final NADCAP gap analysis and action plan complete!")
        print(f"📂 Ready for Scott consultation with comprehensive documentation")
        print(
            f"🎯 {
                summary['overall_coverage']:.1f}% coverage | {
                summary['total_actions']} action items"
        )
