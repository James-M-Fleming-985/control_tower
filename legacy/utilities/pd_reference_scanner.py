#!/usr/bin/env python3
"""
PD Reference Scanner for Surface Finishing Documentation
========================================================
Scans all SF documentation (controlled + uncontrolled) to find PD form references.
This helps identify which group-wide PD forms are relevant to Surface Finishing
and should be included in NADCAP compliance analysis.
"""

import os
import re
import subprocess
from datetime import datetime

import docx2txt
import pandas as pd
import PyPDF2


class PDReferenceScanner:
    def __init__(self):
        self.base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
        self.inputs_folder = os.path.join(self.base_folder, "Inputs")
        self.uncontrolled_folder = os.path.join(
            self.inputs_folder, "uncontrolled_documents"
        )
        self.outputs_folder = os.path.join(self.base_folder, "outputs")

        # PD reference patterns
        self.pd_patterns = [
            r"\bPD\s*[-\s]*\d+(?:\.\d+)*\b",  # PD123, PD-123, PD 123, PD123.1
            r"\bPD\d+(?:\.\d+)*\b",  # PD123, PD123.1
            r"PD[-\s]\d+(?:\.\d+)*",  # PD-123, PD 123
            # Process Document 123
            r"Process\s+Document\s*[-\s]*\d+(?:\.\d+)*",
            # PROCESS DOCUMENT 123
            r"PROCESS\s+DOCUMENT\s*[-\s]*\d+(?:\.\d+)*",
        ]

        self.found_references = []

    def extract_pdf_text(self, file_path):
        """Extract text from PDF file"""
        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text from {file_path}: {str(e)}")
            return ""

    def extract_docx_text(self, file_path):
        """Extract text from DOCX file"""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            print(f"Error extracting DOCX text from {file_path}: {str(e)}")
            return ""

    def extract_doc_text(self, file_path):
        """Extract text from legacy .doc file"""
        try:
            # First try antiword
            result = subprocess.run(
                ["antiword", file_path], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                # Fallback to docx2txt
                text = docx2txt.process(file_path)
                return text.strip() if text else ""
        except subprocess.TimeoutExpired:
            print(f"Timeout extracting text from {file_path}")
            return ""
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return ""

    def extract_xlsx_text(self, file_path):
        """Extract text from Excel file"""
        try:
            df = pd.read_excel(file_path, sheet_name=None)
            text = ""
            for sheet_name, sheet_df in df.items():
                text += f"Sheet: {sheet_name}\n"
                text += sheet_df.to_string() + "\n\n"
            return text.strip()
        except BaseException:
            return ""

    def extract_txt_text(self, file_path):
        """Extract text from text file"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except BaseException:
            try:
                with open(file_path, "r", encoding="latin1") as file:
                    return file.read().strip()
            except BaseException:
                return ""

    def extract_text_from_file(self, file_path):
        """Extract text from various file types"""
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".pdf":
            return self.extract_pdf_text(file_path)
        elif file_ext == ".docx":
            return self.extract_docx_text(file_path)
        elif file_ext == ".doc":
            return self.extract_doc_text(file_path)
        elif file_ext == ".xlsx":
            return self.extract_xlsx_text(file_path)
        elif file_ext == ".txt":
            return self.extract_txt_text(file_path)
        else:
            return ""

    def find_pd_references(self, text):
        """Find all PD references in text"""
        references = set()

        for pattern in self.pd_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref = match.group().strip()
                # Clean up the reference
                ref = re.sub(r"\s+", " ", ref)  # Normalize spaces
                references.add(ref.upper())

        return list(references)

    def scan_controlled_documents(self):
        """Scan controlled SF documentation inventory for PD references"""
        print("Scanning controlled documents inventory...")

        sf_file = os.path.join(
            self.inputs_folder, "Copy of Surface Finishes and MFG 040925.xlsx"
        )
        if not os.path.exists(sf_file):
            print(f"Controlled documents file not found: {sf_file}")
            return

        sf_df = pd.read_excel(sf_file)
        print(f"Loaded {len(sf_df)} controlled documents")

        for idx, row in sf_df.iterrows():
            title = str(row.get("Title", "")).strip()
            content = (
                str(row.iloc[8]).strip() if len(row) > 8 else ""
            )  # Column I (Notes)
            cheops_ref = (
                str(row.iloc[2]).strip() if len(row) > 2 else ""
            )  # Column C (CHEOPS Ref)

            # Search in title
            if title and title != "nan":
                refs = self.find_pd_references(title)
                for ref in refs:
                    self.found_references.append(
                        {
                            "PD_Reference": ref,
                            "Found_In": "Controlled Document Title",
                            "Document_Reference": cheops_ref,
                            "Document_Title": title,
                            "Source_Type": "Controlled",
                            "File_Path": "Controlled Inventory",
                        }
                    )  # Search in content/notes
            if content and content != "nan" and len(content) > 10:
                refs = self.find_pd_references(content)
                for ref in refs:
                    self.found_references.append(
                        {
                            "PD_Reference": ref,
                            "Found_In": "Controlled Document Content",
                            "Document_Reference": cheops_ref,
                            "Document_Title": title,
                            "Source_Type": "Controlled",
                            "File_Path": "Controlled Inventory",
                        }
                    )

    def scan_uncontrolled_documents(self):
        """Scan uncontrolled documents folder for PD references"""
        print("Scanning uncontrolled documents...")

        if not os.path.exists(self.uncontrolled_folder):
            print(
                f"Uncontrolled documents folder not found: {
                    self.uncontrolled_folder}"
            )
            return

        supported_extensions = [".pdf", ".docx", ".doc", ".xlsx", ".txt"]
        file_count = 0

        for root, dirs, files in os.walk(self.uncontrolled_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in supported_extensions:
                    # Skip Excel inventory files to avoid duplication with
                    # controlled scanning
                    if (
                        "Surface Finishes and MFG" in file
                        or "surface finishes and mfg" in file.lower()
                    ):
                        print(f"Skipping inventory duplicate: {file}")
                        continue

                    print(f"Scanning: {file}")
                    file_count += 1

                    # Extract text content
                    content = self.extract_text_from_file(file_path)
                    filename = os.path.splitext(file)[0]

                    # Extract actual document reference from filename (e.g., MANP3.3.580)
                    # If it's a MANP, use that; otherwise use filename as
                    # reference
                    if filename.upper().startswith("MANP"):
                        doc_reference = filename
                    elif any(
                        keyword in filename.upper()
                        for keyword in ["PD", "INST", "FORM", "PROC"]
                    ):
                        doc_reference = filename
                    else:
                        doc_reference = f"UNCONTROLLED-{file_count:03d}"

                    # Search in filename
                    refs = self.find_pd_references(filename)
                    for ref in refs:
                        self.found_references.append(
                            {
                                "PD_Reference": ref,
                                "Found_In": "Filename",
                                "Document_Reference": doc_reference,
                                "Document_Title": "",  # Leave blank for uncontrolled
                                "Source_Type": "Uncontrolled",
                                "File_Path": file_path,
                            }
                        )

                    # Search in content
                    if content and len(content) > 20:
                        refs = self.find_pd_references(content)
                        for ref in refs:
                            self.found_references.append(
                                {
                                    "PD_Reference": ref,
                                    "Found_In": "Document Content",
                                    "Document_Reference": doc_reference,  # Use same doc_reference from above
                                    "Document_Title": "",  # Leave blank for uncontrolled
                                    "Source_Type": "Uncontrolled",
                                    "File_Path": file_path,
                                }
                            )

    def scan_nadcap_requirements(self):
        """Scan NADCAP requirements for PD references"""
        print("Scanning NADCAP requirements...")

        nadcap_file = os.path.join(
            self.inputs_folder, "NADCAP Audit Requirements 030925.xlsx"
        )
        if not os.path.exists(nadcap_file):
            print(f"NADCAP requirements file not found: {nadcap_file}")
            return

        nadcap_df = pd.read_excel(nadcap_file)
        print(f"Loaded {len(nadcap_df)} NADCAP requirements")

        for idx, row in nadcap_df.iterrows():
            # Check all text columns
            for col in ["Title", "Title.1", "Content", "Guidence ", "Notes"]:
                if col in row and pd.notna(row[col]):
                    text = str(row[col]).strip()
                    if text and len(text) > 5:
                        refs = self.find_pd_references(text)
                        for ref in refs:
                            self.found_references.append(
                                {
                                    "PD_Reference": ref,
                                    "Found_In": f"NADCAP {col}",
                                    "Document_Reference": f"NADCAP-{idx + 1:03d}",
                                    "Document_Title": f"NADCAP Requirement {idx + 1}",
                                    "Source_Type": "NADCAP Requirement",
                                    "File_Path": nadcap_file,
                                }
                            )

    def analyze_and_export_results(self):
        """Analyze PD references and export results"""
        if not self.found_references:
            print("No PD references found!")
            return

        # Convert to DataFrame
        df = pd.DataFrame(self.found_references)

        # Get unique PD references
        unique_pds = df["PD_Reference"].unique()

        print(f"\n=== PD REFERENCE ANALYSIS ===")
        print(f"Total PD references found: {len(self.found_references)}")
        print(f"Unique PD forms identified: {len(unique_pds)}")

        # Summary by source type
        print(f"\nPD References by Source Type:")
        source_summary = df.groupby("Source_Type").size()
        for source, count in source_summary.items():
            print(f"  {source}: {count} references")

        # Top PD references
        print(f"\nMost Referenced PD Forms:")
        pd_counts = df["PD_Reference"].value_counts().head(10)
        for pd_ref, count in pd_counts.items():
            print(f"  {pd_ref}: {count} references")

        # Export detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(
            self.outputs_folder, f"PD_References_Analysis_{timestamp}.xlsx"
        )

        # Create summary sheet
        summary_data = []
        for pd_ref in unique_pds:
            refs = df[df["PD_Reference"] == pd_ref]
            summary_data.append(
                {
                    "PD_Reference": pd_ref,
                    "Total_References": len(refs),
                    "In_Controlled_Docs": len(
                        refs[refs["Source_Type"] == "Controlled"]
                    ),
                    "In_Uncontrolled_Docs": len(
                        refs[refs["Source_Type"] == "Uncontrolled"]
                    ),
                    "In_NADCAP_Requirements": len(
                        refs[refs["Source_Type"] == "NADCAP Requirement"]
                    ),
                    "First_Found_In": (
                        refs.iloc[0]["Document_Title"]
                        if refs.iloc[0]["Document_Title"]
                        else refs.iloc[0]["Document_Reference"]
                    ),
                    "First_Document_Ref": refs.iloc[0]["Document_Reference"],
                }
            )

        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values(
            "Total_References", ascending=False)

        # Export to Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            summary_df.to_excel(writer, sheet_name="PD_Summary", index=False)
            df.to_excel(writer, sheet_name="All_References", index=False)

            # Create sheet for unique PDs only
            unique_df = summary_df[
                ["PD_Reference", "Total_References", "First_Document_Ref"]
            ].copy()
            unique_df.to_excel(
                writer,
                sheet_name="Unique_PDs_List",
                index=False)

        print(f"\nResults exported to: {output_file}")

        # Print list of unique PDs for easy copying
        print(f"\n=== UNIQUE PD FORMS TO COLLECT ===")
        print("Copy these PD forms to your analysis folder:")
        for pd_ref in sorted(unique_pds):
            print(f"  {pd_ref}")

        return output_file, unique_pds

    def run_scan(self):
        """Run complete PD reference scan"""
        print("PD Reference Scanner for Surface Finishing Documentation")
        print("=" * 60)

        # Scan all sources
        self.scan_controlled_documents()
        self.scan_uncontrolled_documents()
        self.scan_nadcap_requirements()

        # Analyze and export
        return self.analyze_and_export_results()


def main():
    scanner = PDReferenceScanner()
    scanner.run_scan()


if __name__ == "__main__":
    main()
