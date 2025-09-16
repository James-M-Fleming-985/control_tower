#!/usr/bin/env python3
"""
Enhanced NADCAP Gap Analysis with PD Forms Integration
======================================================
Comprehensive analysis including controlled documents, uncontrolled documents, and PD forms.
Supports multiple file formats: PDF, DOC, DOCX, XLSX, CSV, TXT
"""

import os
import re
import subprocess
from datetime import datetime

import docx2txt
import numpy as np
import pandas as pd
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class EnhancedNADCAPAnalysisWithPDForms:
    def __init__(self):
        self.base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
        self.inputs_folder = os.path.join(self.base_folder, "Inputs")
        self.uncontrolled_folder = os.path.join(
            self.inputs_folder, "uncontrolled_documents"
        )
        self.pd_forms_folder = os.path.join(self.inputs_folder, "pd_forms")
        self.outputs_folder = os.path.join(self.base_folder, "outputs")

        print(f"Inputs folder: {self.inputs_folder}")
        print(f"Uncontrolled folder: {self.uncontrolled_folder}")
        print(f"PD Forms folder: {self.pd_forms_folder}")
        print(f"Outputs folder: {self.outputs_folder}")

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
        except Exception as e:
            print(f"Error extracting XLSX text from {file_path}: {str(e)}")
            return ""

    def extract_csv_text(self, file_path):
        """Extract text from CSV file"""
        try:
            df = pd.read_csv(file_path)
            return df.to_string()
        except Exception as e:
            print(f"Error extracting CSV text from {file_path}: {str(e)}")
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
            except Exception as e:
                print(f"Error extracting TXT text from {file_path}: {str(e)}")
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
        elif file_ext == ".csv":
            return self.extract_csv_text(file_path)
        elif file_ext == ".txt":
            return self.extract_txt_text(file_path)
        else:
            print(f"Unsupported file type: {file_ext}")
            return ""

    def extract_document_title(self, file_path, content):
        """Extract document title from content or filename"""
        filename_title = os.path.splitext(os.path.basename(file_path))[0]

        if not content or len(content.strip()) < 10:
            return filename_title

        # Try to extract title from content
        lines = content.split("\n")

        # Look for common title patterns
        for i, line in enumerate(lines[:15]):  # Check first 15 lines
            line = line.strip()
            if not line:
                continue

            # Skip common headers/footers
            if any(
                skip in line.lower()
                for skip in [
                    "page ",
                    "document id",
                    "revision",
                    "date:",
                    "author:",
                    "sheet",
                    "form",
                ]
            ):
                continue

            # Look for substantial titles
            if len(line) > len(filename_title) and len(line) < 150:
                # Check if it looks like a title
                if not line.isupper() or " " in line:
                    # Prefer lines with procedure/process keywords
                    if any(
                        indicator in line.lower()
                        for indicator in [
                            "procedure",
                            "instruction",
                            "manual",
                            "guide",
                            "specification",
                            "standard",
                            "control",
                            "process",
                            "form",
                            "document",
                        ]
                    ):
                        return line
                    # Or substantial positioned lines
                    elif i < 5 and len(line) > 15:
                        return line

        # Fallback to filename
        return filename_title

    def load_pd_forms(self):
        """Load PD forms from pd_forms folder"""
        documents = []

        if not os.path.exists(self.pd_forms_folder):
            print(f"PD forms folder not found: {self.pd_forms_folder}")
            return documents

        print(f"Loading PD forms from: {self.pd_forms_folder}")

        supported_extensions = [
            ".pdf",
            ".docx",
            ".doc",
            ".xlsx",
            ".csv",
            ".txt"]
        file_count = 0

        for root, dirs, files in os.walk(self.pd_forms_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in supported_extensions:
                    print(f"Processing PD Form: {file}")
                    file_count += 1

                    # Extract text content
                    content = self.extract_text_from_file(file_path)

                    # Extract enhanced title
                    title = self.extract_document_title(file_path, content)

                    # Extract PD reference from filename
                    filename = os.path.splitext(file)[0]
                    pd_ref = (
                        filename.upper()
                        if filename.upper().startswith("PD")
                        else f"PD-{filename}"
                    )

                    if content and len(content) > 20:
                        documents.append(
                            {
                                "title": title,
                                "content": content,
                                "cheops_ref": pd_ref,
                                "full_text": f"{title} {content}",
                                "content_source": "PD Form Content",
                                "control_status": "PD Form",
                                "file_path": file_path,
                                "file_type": file_ext[1:],
                                "document_title": title,
                            }
                        )
                    else:
                        # Include even if content extraction failed
                        documents.append(
                            {
                                "title": title,
                                "content": "",
                                "cheops_ref": pd_ref,
                                "full_text": title,
                                "content_source": "PD Form Title Only",
                                "control_status": "PD Form",
                                "file_path": file_path,
                                "file_type": file_ext[1:],
                                "document_title": title,
                            }
                        )

        print(f"Found {len(documents)} PD forms")
        return documents

    def load_controlled_documents(self):
        """Load controlled SF documentation inventory"""
        sf_file = os.path.join(
            self.inputs_folder, "Copy of Surface Finishes and MFG 040925.xlsx"
        )
        print(f"Loading controlled documents from: {sf_file}")

        sf_df = pd.read_excel(sf_file)
        print(
            f"Controlled inventory loaded successfully. Shape: {
                sf_df.shape}"
        )

        documents = []
        for idx, row in sf_df.iterrows():
            title = str(row.get("Title", "")).strip()
            content = (
                str(row.iloc[8]).strip() if len(row) > 8 else ""
            )  # Column I (Notes)
            cheops_ref = (
                str(row.iloc[2]).strip() if len(row) > 2 else ""
            )  # Column C (CHEOPS Ref)

            if title and title != "nan" and len(title) > 5:
                if content and content != "nan" and len(content) > 50:
                    full_text = f"{title} {content}"
                    content_source = "Title + Content"
                else:
                    full_text = title
                    content_source = "Title Only"

                documents.append(
                    {
                        "title": title,
                        "content": content if content != "nan" else "",
                        "cheops_ref": cheops_ref if cheops_ref != "nan" else "",
                        "full_text": full_text,
                        "content_source": content_source,
                        "control_status": "Controlled",
                        "file_path": "Controlled Inventory",
                        "file_type": "inventory",
                        "document_title": title,
                    }
                )

        print(f"Found {len(documents)} controlled documents")
        return documents

    def load_uncontrolled_documents(self):
        """Load uncontrolled documents from folder"""
        documents = []

        if not os.path.exists(self.uncontrolled_folder):
            print(
                f"Uncontrolled documents folder not found: {
                    self.uncontrolled_folder}"
            )
            return documents

        print(
            f"Loading uncontrolled documents from: {
                self.uncontrolled_folder}"
        )

        supported_extensions = [".pdf", ".docx", ".doc", ".xlsx", ".txt"]
        file_count = 0

        for root, dirs, files in os.walk(self.uncontrolled_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in supported_extensions:
                    # Skip Excel inventory files to avoid duplication
                    if (
                        "Surface Finishes and MFG" in file
                        or "surface finishes and mfg" in file.lower()
                    ):
                        continue

                    print(f"Processing: {file}")
                    file_count += 1

                    # Extract text content
                    content = self.extract_text_from_file(file_path)

                    # Extract enhanced title
                    title = self.extract_document_title(file_path, content)

                    if content and len(content) > 20:
                        documents.append(
                            {
                                "title": title,
                                "content": content,
                                "cheops_ref": f"UNCONTROLLED-{file_count:03d}",
                                "full_text": f"{title} {content}",
                                "content_source": "File Content",
                                "control_status": "Uncontrolled",
                                "file_path": file_path,
                                "file_type": file_ext[1:],
                                "document_title": title,
                            }
                        )
                    else:
                        documents.append(
                            {
                                "title": title,
                                "content": "",
                                "cheops_ref": f"UNCONTROLLED-{file_count:03d}",
                                "full_text": title,
                                "content_source": "Title Only",
                                "control_status": "Uncontrolled",
                                "file_path": file_path,
                                "file_type": file_ext[1:],
                                "document_title": title,
                            }
                        )

        print(f"Found {len(documents)} uncontrolled documents")
        return documents

    def load_nadcap_requirements(self):
        """Load NADCAP requirements"""
        nadcap_file = os.path.join(
            self.inputs_folder, "NADCAP Audit Requirements 030925.xlsx"
        )
        print(f"Loading NADCAP requirements from: {nadcap_file}")

        nadcap_df = pd.read_excel(nadcap_file)
        print(f"NADCAP file loaded successfully. Shape: {nadcap_df.shape}")

        return nadcap_df

    def extract_meaningful_requirements(self, nadcap_df):
        """Extract meaningful text from NADCAP requirements"""
        requirements = []

        for idx, row in nadcap_df.iterrows():
            # Combine meaningful text columns
            title = str(row.get("Title", "")).strip()
            title1 = str(row.get("Title.1", "")).strip()
            content = str(row.get("Content", "")).strip()
            guidance = str(
                row.get("Guidence ", "")
            ).strip()  # Note the space in column name

            # Build comprehensive requirement text
            requirement_parts = []
            if title and title != "nan":
                requirement_parts.append(title)
            if title1 and title1 != "nan":
                requirement_parts.append(title1)
            if content and content != "nan":
                requirement_parts.append(content)
            if guidance and guidance != "nan":
                requirement_parts.append(guidance)

            if requirement_parts:
                full_requirement = " ".join(requirement_parts)
                requirements.append(full_requirement)
            else:
                requirements.append(f"Requirement {idx + 1}")

        print(
            f"Extracted {
                len(requirements)} requirements with enhanced meaningful context"
        )
        return requirements

    def calculate_similarity_matrix(self, requirements, documents):
        """Calculate TF-IDF similarity matrix"""
        print("Calculating TF-IDF similarity scores...")

        # Prepare document texts
        doc_texts = [doc["full_text"] for doc in documents]

        # Combine requirements and documents for TF-IDF
        all_texts = requirements + doc_texts

        # Calculate TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8,
        )

        tfidf_matrix = vectorizer.fit_transform(all_texts)

        # Calculate similarity between requirements and documents
        req_matrix = tfidf_matrix[: len(requirements)]
        doc_matrix = tfidf_matrix[len(requirements):]

        similarity_matrix = cosine_similarity(req_matrix, doc_matrix)

        return similarity_matrix

    def find_best_matches(self, requirements, documents, similarity_matrix):
        """Find best document matches for each requirement"""
        best_matches = []

        for i, req in enumerate(requirements):
            scores = similarity_matrix[i]
            best_doc_idx = np.argmax(scores)
            best_score = scores[best_doc_idx]

            best_matches.append(
                {
                    "requirement_idx": i,
                    "document_idx": best_doc_idx,
                    "document_title": documents[best_doc_idx].get(
                        "document_title", documents[best_doc_idx]["title"]
                    ),
                    "cheops_ref": documents[best_doc_idx]["cheops_ref"],
                    "control_status": documents[best_doc_idx]["control_status"],
                    "similarity_score": best_score,
                }
            )

        return best_matches

    def generate_enhanced_compliance_status(
            self, similarity_score, control_status):
        """Generate compliance status considering content match and control status"""
        if similarity_score >= 0.7:
            if control_status in ["Controlled", "PD Form"]:
                return "Compliant"
            else:
                return "Content Match - Needs Control"
        elif similarity_score >= 0.4:
            if control_status in ["Controlled", "PD Form"]:
                return "Partial - Controlled"
            else:
                return "Partial - Needs Control"
        elif similarity_score >= 0.2:
            if control_status in ["Controlled", "PD Form"]:
                return "Review Required - Controlled"
            else:
                return "Review Required - Needs Control"
        else:
            return "Non-Compliant"

    def generate_primary_evidence(self, best_match):
        """Generate primary evidence description"""
        if best_match["similarity_score"] >= 0.2:
            return f"{best_match['cheops_ref']} - {best_match['document_title']} [{best_match['control_status']}]"
        else:
            return "No match found"

    def generate_enhanced_action_required(self, requirement, best_match):
        """Generate action required based on match quality and control status"""
        score = best_match["similarity_score"]
        status = best_match["control_status"]

        if score >= 0.7:
            if status in ["Controlled", "PD Form"]:
                return "Verify compliance and maintain"
            else:
                return "Bring document under control"
        elif score >= 0.4:
            return "Review and enhance documentation"
        elif score >= 0.2:
            return "Detailed review required"
        else:
            return "Create new documentation"

    def generate_enhanced_gap_description(self, requirement, best_match):
        """Generate detailed gap description"""
        score = best_match["similarity_score"]
        confidence = score * 100
        status = best_match["control_status"]

        status_note = ""
        if status == "PD Form":
            status_note = " (PD Form)"
        elif status == "Uncontrolled":
            status_note = " (Uncontrolled)"

        if score >= 0.7:
            return f"Strong match (confidence: {confidence:.1f}%){status_note} - verify alignment"
        elif score >= 0.4:
            return f"Moderate match (confidence: {confidence:.1f}%){status_note} - review for gaps"
        elif score >= 0.2:
            return f"Weak match (confidence: {confidence:.1f}%){status_note} - manual review required"
        else:
            return f"No suitable documentation found (confidence: {confidence:.1f}%)"

    def append_analysis_columns(self, nadcap_df, requirements, best_matches):
        """Append enhanced analysis columns to NADCAP requirements"""
        print("Appending enhanced analysis columns to NADCAP requirements...")

        enhanced_df = nadcap_df.copy()

        # Initialize new columns
        enhanced_df["Compliance_Status"] = "Non-Compliant"
        enhanced_df["Primary_Evidence"] = "No match found"
        enhanced_df["Action_Required"] = "Create new documentation"
        enhanced_df["Gap_Description"] = "No documentation found"
        enhanced_df["Control_Status"] = "Unknown"
        enhanced_df["Document_Title"] = "No match found"

        # Fill in analysis results
        for i, match in enumerate(best_matches):
            if i < len(enhanced_df):
                req = requirements[match["requirement_idx"]]

                enhanced_df.loc[i, "Compliance_Status"] = (
                    self.generate_enhanced_compliance_status(
                        match["similarity_score"], match["control_status"]
                    )
                )
                enhanced_df.loc[i, "Primary_Evidence"] = self.generate_primary_evidence(
                    match
                )
                enhanced_df.loc[i, "Action_Required"] = (
                    self.generate_enhanced_action_required(req, match)
                )
                enhanced_df.loc[i, "Gap_Description"] = (
                    self.generate_enhanced_gap_description(req, match)
                )

                if match["similarity_score"] >= 0.2:
                    enhanced_df.loc[i,
                                    "Control_Status"] = match["control_status"]
                    enhanced_df.loc[i,
                                    "Document_Title"] = match["document_title"]
                else:
                    enhanced_df.loc[i, "Control_Status"] = "No Match"
                    enhanced_df.loc[i, "Document_Title"] = "No match found"

        return enhanced_df

    def run_analysis(self):
        """Run complete enhanced NADCAP gap analysis with PD forms"""
        print("Enhanced NADCAP Gap Analysis with PD Forms Integration")
        print("=" * 60)

        # Load all document sources
        controlled_docs = self.load_controlled_documents()
        uncontrolled_docs = self.load_uncontrolled_documents()
        pd_forms = self.load_pd_forms()
        nadcap_df = self.load_nadcap_requirements()

        # Combine all documents
        all_documents = controlled_docs + uncontrolled_docs + pd_forms

        print(f"\nTotal documents for analysis:")
        print(f"  - Controlled: {len(controlled_docs)}")
        print(f"  - Uncontrolled: {len(uncontrolled_docs)}")
        print(f"  - PD Forms: {len(pd_forms)}")
        print(f"  - Total: {len(all_documents)}")

        # Extract meaningful requirements
        requirements = self.extract_meaningful_requirements(nadcap_df)

        # Calculate similarity
        similarity_matrix = self.calculate_similarity_matrix(
            requirements, all_documents
        )

        # Find best matches
        best_matches = self.find_best_matches(
            requirements, all_documents, similarity_matrix
        )

        # Create enhanced analysis
        enhanced_df = self.append_analysis_columns(
            nadcap_df, requirements, best_matches
        )

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(
            self.outputs_folder, f"Enhanced_NADCAP_with_PD_Forms_{timestamp}.xlsx"
        )
        enhanced_df.to_excel(output_file, index=False)

        print(f"\nEnhanced NADCAP file saved: {output_file}")

        # Generate summary
        print("=" * 60)
        print("Analysis Complete!")
        print(f"Results saved to: {self.outputs_folder}")

        summary = enhanced_df["Compliance_Status"].value_counts()
        print("Summary:")
        for status, count in summary.items():
            print(f"- {status}: {count}")

        control_summary = enhanced_df["Control_Status"].value_counts()
        print(f"\nDocument Control Distribution:")
        for status, count in control_summary.items():
            print(f"- {status}: {count}")

        return output_file


def main():
    analyzer = EnhancedNADCAPAnalysisWithPDForms()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
