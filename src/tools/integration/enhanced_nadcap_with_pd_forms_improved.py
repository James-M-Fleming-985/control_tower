#!/usr/bin/env python3
"""
Enhanced NADCAP Gap Analysis with PD Forms Integration - IMPROVED VERSION
Addresses threshold and semantic matching issues identified in analysis
"""

import os
import re
import warnings
from datetime import datetime

import docx
import docx2txt
import numpy as np
import pandas as pd
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore")


class ImprovedNADCAPAnalyzer:
    def __init__(self, base_folder):
        self.base_folder = base_folder
        self.inputs_folder = os.path.join(base_folder, "Inputs")
        self.outputs_folder = os.path.join(base_folder, "outputs")
        self.uncontrolled_folder = os.path.join(
            self.inputs_folder, "uncontrolled_documents"
        )
        self.pd_forms_folder = os.path.join(self.inputs_folder, "pd_forms")

        # IMPROVED: Lower threshold and add semantic keywords
        self.similarity_threshold = 0.15  # Lowered from 0.2 to 0.15

        # Add semantic keyword mapping for better PD form matching
        self.functional_keywords = {
            "training": [
                "training",
                "competency",
                "qualification",
                "personnel",
                "skill",
                "education",
            ],
            "maintenance": [
                "maintenance",
                "tpm",
                "equipment",
                "calibration",
                "service",
                "repair",
            ],
            "testing": [
                "testing",
                "inspection",
                "measurement",
                "analysis",
                "check",
                "monitor",
            ],
            "control": [
                "control",
                "procedure",
                "process",
                "method",
                "standard",
                "specification",
            ],
            "documentation": [
                "record",
                "document",
                "form",
                "report",
                "log",
                "certificate",
            ],
            "quality": [
                "quality",
                "compliance",
                "audit",
                "review",
                "assessment",
                "evaluation",
            ],
            "safety": ["safety", "hazard", "risk", "protection", "ppe", "dsear"],
            "environment": ["environment", "waste", "emission", "chemical", "disposal"],
        }

        print(f"Inputs folder: {self.inputs_folder}")
        print(f"Uncontrolled folder: {self.uncontrolled_folder}")
        print(f"PD Forms folder: {self.pd_forms_folder}")
        print(f"Outputs folder: {self.outputs_folder}")

    def extract_text_from_file(self, file_path):
        """Enhanced text extraction with better error handling"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".pdf":
                return self.extract_pdf_text(file_path)
            elif file_ext == ".docx":
                return docx2txt.process(file_path)
            elif file_ext == ".doc":
                try:
                    # Try docx2txt first (works for some .doc files)
                    text = docx2txt.process(file_path)
                    if text and len(text.strip()) > 10:
                        return text
                except BaseException:
                    pass
                # Fallback: basic filename-based content
                return f"Document: {os.path.basename(file_path)}"
            elif file_ext in [".xlsx", ".csv"]:
                return self.extract_excel_csv_text(file_path)
            elif file_ext == ".txt":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            else:
                return f"Document: {os.path.basename(file_path)}"

        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return f"Document: {os.path.basename(file_path)}"

    def extract_pdf_text(self, file_path):
        """Extract text from PDF files"""
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except BaseException:
            return f"PDF Document: {os.path.basename(file_path)}"

    def extract_excel_csv_text(self, file_path):
        """Extract text from Excel/CSV files"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Convert all cell values to text and combine
            text_content = []
            for col in df.columns:
                text_content.extend(df[col].astype(str).tolist())

            return " ".join([str(x) for x in text_content if str(x) != "nan"])
        except BaseException:
            return f"Data file: {os.path.basename(file_path)}"

    def extract_enhanced_semantic_keywords(self, text):
        """Extract semantic keywords from text for better matching"""
        keywords = []
        text_lower = text.lower()

        for category, category_keywords in self.functional_keywords.items():
            for keyword in category_keywords:
                if keyword in text_lower:
                    keywords.append(f"{category}_{keyword}")

        return keywords

    def extract_document_title(self, file_path, content):
        """Enhanced document title extraction"""
        filename_title = os.path.splitext(os.path.basename(file_path))[0]

        if not content or len(content.strip()) < 10:
            return filename_title

        # Try to extract title from content with better patterns
        lines = content.split("\n")

        # Look for title patterns - improved logic
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 150:
                # Check for title indicators
                if any(
                    indicator in line.lower()
                    for indicator in [
                        "procedure",
                        "manual",
                        "guide",
                        "specification",
                        "standard",
                        "control",
                        "process",
                        "form",
                        "document",
                        "competency",
                        "training",
                    ]
                ):
                    return line
                # Or check for substantial positioned lines
                elif i < 5 and len(line) > 15 and not line.isupper():
                    return line

        # Fallback to filename
        return filename_title

    def load_controlled_documents(self):
        """Load controlled documents from Excel inventory"""
        documents = []
        excel_file = None

        # Find the Excel inventory file
        for file in os.listdir(self.inputs_folder):
            if file.endswith(".xlsx") and (
                "surface" in file.lower() or "finishes" in file.lower()
            ):
                excel_file = os.path.join(self.inputs_folder, file)
                break

        if not excel_file:
            print("No controlled inventory Excel file found")
            return documents

        print(f"Loading controlled documents from: {excel_file}")

        try:
            df = pd.read_excel(excel_file)
            print(
                f"Controlled inventory loaded successfully. Shape: {
                    df.shape}"
            )

            for idx, row in df.iterrows():
                cheops_ref = str(row.get("CHEOPS Ref", "")).strip()
                title = str(row.get("Title", "")).strip()
                # Column I analysis context
                notes = str(row.get("Notes", "")).strip()

                if cheops_ref and cheops_ref != "nan" and title and title != "nan":
                    # Use Notes column as content if available, otherwise use
                    # title
                    content = notes if notes and notes != "nan" else title

                    # Enhanced text combination for controlled docs
                    semantic_keywords = self.extract_enhanced_semantic_keywords(
                        f"{title} {content}"
                    )
                    full_text = f"{title} {content} {
                        ' '.join(semantic_keywords)}"

                    documents.append(
                        {
                            "title": title,
                            "content": content,
                            "cheops_ref": cheops_ref,
                            "full_text": full_text,
                            "content_source": "Controlled Inventory",
                            "control_status": "Controlled",
                            "document_title": title,
                        }
                    )

        except Exception as e:
            print(f"Error loading controlled documents: {e}")

        print(f"Found {len(documents)} controlled documents")
        return documents

    def load_uncontrolled_documents(self):
        """Load uncontrolled documents from folder"""
        documents = []

        if not os.path.exists(self.uncontrolled_folder):
            print(f"Uncontrolled folder not found: {self.uncontrolled_folder}")
            return documents

        print(
            f"Loading uncontrolled documents from: {
                self.uncontrolled_folder}"
        )

        supported_extensions = [".pdf", ".docx", ".doc", ".txt"]
        file_count = 0

        for root, dirs, files in os.walk(self.uncontrolled_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in supported_extensions:
                    print(f"Processing: {file}")
                    file_count += 1

                    content = self.extract_text_from_file(file_path)
                    title = self.extract_document_title(file_path, content)

                    # Enhanced semantic analysis
                    semantic_keywords = self.extract_enhanced_semantic_keywords(
                        content)
                    full_text = f"{title} {content} {
                        ' '.join(semantic_keywords)}"

                    filename = os.path.splitext(file)[0]
                    cheops_ref = f"UNCONTROLLED-{file_count:03d}"

                    if content and len(content) > 20:
                        documents.append(
                            {
                                "title": title,
                                "content": content,
                                "cheops_ref": cheops_ref,
                                "full_text": full_text,
                                "content_source": "Uncontrolled Document",
                                "control_status": "Uncontrolled",
                                "document_title": title,
                            }
                        )
                    else:
                        documents.append(
                            {
                                "title": title,
                                "content": title,
                                "cheops_ref": cheops_ref,
                                "full_text": title,
                                "content_source": "Uncontrolled Document",
                                "control_status": "Uncontrolled",
                                "document_title": title,
                            }
                        )

        print(f"Found {len(documents)} uncontrolled documents")
        return documents

    def load_pd_forms(self):
        """Enhanced PD forms loading with better semantic analysis"""
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

                    content = self.extract_text_from_file(file_path)
                    title = self.extract_document_title(file_path, content)

                    # Enhanced semantic analysis for PD forms
                    semantic_keywords = self.extract_enhanced_semantic_keywords(
                        f"{title} {content}"
                    )

                    # Extract PD reference from filename
                    filename = os.path.splitext(file)[0]
                    pd_ref = (
                        filename.upper()
                        if filename.upper().startswith("PD")
                        else f"PD-{filename}"
                    )

                    full_text = f"{title} {content} {
                        ' '.join(semantic_keywords)}"

                    if content and len(content) > 20:
                        documents.append(
                            {
                                "title": title,
                                "content": content,
                                "cheops_ref": pd_ref,
                                "full_text": full_text,
                                "content_source": "PD Form Content",
                                "control_status": "PD Form",
                                "document_title": title,
                            }
                        )
                    else:
                        documents.append(
                            {
                                "title": title,
                                "content": title,
                                "cheops_ref": pd_ref,
                                "full_text": f"{title} {' '.join(semantic_keywords)}",
                                "content_source": "PD Form Title",
                                "control_status": "PD Form",
                                "document_title": title,
                            }
                        )

        print(f"Found {len(documents)} PD forms")
        return documents

    def load_nadcap_requirements(self):
        """Load NADCAP requirements from Excel file"""
        nadcap_file = None

        for file in os.listdir(self.inputs_folder):
            if file.endswith(".xlsx") and "nadcap" in file.lower():
                nadcap_file = os.path.join(self.inputs_folder, file)
                break

        if not nadcap_file:
            raise FileNotFoundError("NADCAP requirements file not found")

        print(f"Loading NADCAP requirements from: {nadcap_file}")
        df = pd.read_excel(nadcap_file)
        print(f"NADCAP file loaded successfully. Shape: {df.shape}")

        return df

    def extract_meaningful_requirements(self, nadcap_df):
        """Enhanced requirement extraction with semantic keywords"""
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
                # Add semantic keywords to enhance matching
                semantic_keywords = self.extract_enhanced_semantic_keywords(
                    full_requirement
                )
                enhanced_requirement = (
                    f"{full_requirement} {' '.join(semantic_keywords)}"
                )
                requirements.append(enhanced_requirement)
            else:
                requirements.append(f"Requirement {idx + 1}")

        print(
            f"Extracted {
                len(requirements)} requirements with enhanced semantic context"
        )
        return requirements

    def calculate_similarity_matrix(self, requirements, documents):
        """Enhanced TF-IDF similarity calculation"""
        print("Calculating enhanced TF-IDF similarity scores...")

        # Prepare document texts
        doc_texts = [doc["full_text"] for doc in documents]

        # Combine requirements and documents for TF-IDF
        all_texts = requirements + doc_texts

        # Enhanced TF-IDF with better parameters for technical documents
        vectorizer = TfidfVectorizer(
            max_features=8000,  # Increased from 5000
            stop_words="english",
            # Include trigrams for better technical matching
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.85,  # Slightly higher max_df
            sublinear_tf=True,  # Use sublinear TF scaling
        )

        tfidf_matrix = vectorizer.fit_transform(all_texts)

        # Calculate similarity between requirements and documents
        req_matrix = tfidf_matrix[: len(requirements)]
        doc_matrix = tfidf_matrix[len(requirements):]

        similarity_matrix = cosine_similarity(req_matrix, doc_matrix)

        return similarity_matrix

    def find_best_matches(self, requirements, documents, similarity_matrix):
        """Find best matches using improved threshold"""
        best_matches = []

        for i in range(len(requirements)):
            scores = similarity_matrix[i]
            best_idx = np.argmax(scores)
            best_score = scores[best_idx]

            best_matches.append(
                {
                    "document_index": best_idx,
                    "similarity_score": best_score,
                    "document_title": documents[best_idx]["document_title"],
                    "cheops_ref": documents[best_idx]["cheops_ref"],
                    "control_status": documents[best_idx]["control_status"],
                }
            )

        return best_matches

    def generate_enhanced_compliance_status(
            self, similarity_score, control_status):
        """Enhanced compliance status with improved thresholds"""
        if similarity_score >= 0.6:  # Lowered from 0.7
            if control_status in ["Controlled", "PD Form"]:
                return "Compliant"
            else:
                return "Content Match - Needs Control"
        elif similarity_score >= 0.3:  # Lowered from 0.4
            if control_status in ["Controlled", "PD Form"]:
                return "Partial - Controlled"
            else:
                return "Partial - Needs Control"
        elif similarity_score >= self.similarity_threshold:  # Now 0.15 instead of 0.2
            if control_status in ["Controlled", "PD Form"]:
                return "Review Required - Controlled"
            else:
                return "Review Required - Needs Control"
        else:
            return "Non-Compliant"

    def generate_primary_evidence(self, best_match):
        """Generate primary evidence description"""
        if best_match["similarity_score"] >= self.similarity_threshold:
            return f"{best_match['cheops_ref']} - {best_match['document_title']} [{best_match['control_status']}]"
        else:
            return "No match found"

    def generate_enhanced_action_required(self, requirement, best_match):
        """Enhanced action required based on improved matching"""
        score = best_match["similarity_score"]
        status = best_match["control_status"]

        if score >= 0.6:
            if status in ["Controlled", "PD Form"]:
                return "Verify content alignment and completeness"
            else:
                return "Formalize document control for existing content"
        elif score >= 0.3:
            if status in ["Controlled", "PD Form"]:
                return "Review and enhance existing documentation"
            else:
                return "Enhance content and establish document control"
        elif score >= self.similarity_threshold:
            if status in ["Controlled", "PD Form"]:
                return "Assess relevance and consider enhancement"
            else:
                return "Evaluate content and consider control establishment"
        else:
            return "Create new documentation"

    def generate_enhanced_gap_description(self, requirement, best_match):
        """Enhanced gap description"""
        score = best_match["similarity_score"]
        confidence = score * 100
        status = best_match["control_status"]

        status_note = ""
        if status == "PD Form":
            status_note = " (PD Form)"
        elif status == "Uncontrolled":
            status_note = " (Uncontrolled)"

        if score >= 0.6:
            return f"Strong match (confidence: {confidence:.1f}%){status_note} - verify alignment"
        elif score >= 0.3:
            return f"Moderate match (confidence: {confidence:.1f}%){status_note} - review for gaps"
        elif score >= self.similarity_threshold:
            return f"Potential match (confidence: {confidence:.1f}%){status_note} - manual review required"
        else:
            return f"No suitable documentation found (confidence: {confidence:.1f}%)"

    def append_analysis_columns(self, nadcap_df, requirements, best_matches):
        """Append enhanced analysis columns to NADCAP requirements"""
        print("Appending enhanced analysis columns to NADCAP requirements...")

        enhanced_df = nadcap_df.copy()

        compliance_statuses = []
        primary_evidences = []
        actions_required = []
        gap_descriptions = []
        control_statuses = []
        document_titles = []

        for i, match in enumerate(best_matches):
            compliance_status = self.generate_enhanced_compliance_status(
                match["similarity_score"], match["control_status"]
            )

            primary_evidence = self.generate_primary_evidence(match)
            action_required = self.generate_enhanced_action_required(
                requirements[i], match
            )
            gap_description = self.generate_enhanced_gap_description(
                requirements[i], match
            )

            # Determine control status
            if match["similarity_score"] >= self.similarity_threshold:
                control_status = match["control_status"]
                document_title = match["document_title"]
            else:
                control_status = "No Match"
                document_title = "No match found"

            compliance_statuses.append(compliance_status)
            primary_evidences.append(primary_evidence)
            actions_required.append(action_required)
            gap_descriptions.append(gap_description)
            control_statuses.append(control_status)
            document_titles.append(document_title)

        # Add new columns
        enhanced_df["Compliance_Status"] = compliance_statuses
        enhanced_df["Primary_Evidence"] = primary_evidences
        enhanced_df["Action_Required"] = actions_required
        enhanced_df["Gap_Description"] = gap_descriptions
        enhanced_df["Control_Status"] = control_statuses
        enhanced_df["Document_Title"] = document_titles

        return enhanced_df

    def run_enhanced_analysis(self):
        """Run the enhanced NADCAP gap analysis"""
        print("Enhanced NADCAP Gap Analysis with Improved Matching")
        print("=" * 60)

        # Load all document types
        controlled_docs = self.load_controlled_documents()
        uncontrolled_docs = self.load_uncontrolled_documents()
        pd_forms = self.load_pd_forms()

        # Combine all documents
        all_documents = controlled_docs + uncontrolled_docs + pd_forms

        print(f"\nTotal documents for analysis:")
        print(f"  - Controlled: {len(controlled_docs)}")
        print(f"  - Uncontrolled: {len(uncontrolled_docs)}")
        print(f"  - PD Forms: {len(pd_forms)}")
        print(f"  - Total: {len(all_documents)}")

        # Load NADCAP requirements
        nadcap_df = self.load_nadcap_requirements()

        # Extract meaningful requirements with semantic enhancement
        requirements = self.extract_meaningful_requirements(nadcap_df)

        # Calculate similarity matrix
        similarity_matrix = self.calculate_similarity_matrix(
            requirements, all_documents
        )

        # Find best matches
        best_matches = self.find_best_matches(
            requirements, all_documents, similarity_matrix
        )

        # Append enhanced analysis columns
        enhanced_df = self.append_analysis_columns(
            nadcap_df, requirements, best_matches
        )

        # Save enhanced results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(
            self.outputs_folder, f"Enhanced_NADCAP_Improved_Threshold_{timestamp}.xlsx"
        )
        enhanced_df.to_excel(output_file, index=False)
        print(f"\nEnhanced NADCAP file saved: {output_file}")

        # Print summary statistics
        print("=" * 60)
        print("Analysis Complete!")
        print(f"Results saved to: {self.outputs_folder}")

        summary = enhanced_df["Compliance_Status"].value_counts()
        print("Summary:")
        for status, count in summary.items():
            print(f"- {status}: {count}")

        print(f"\nDocument Control Distribution:")
        control_summary = enhanced_df["Control_Status"].value_counts()
        for status, count in control_summary.items():
            print(f"- {status}: {count}")


def main():
    # Set the base folder path
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"

    # Create analyzer and run enhanced analysis
    analyzer = ImprovedNADCAPAnalyzer(base_folder)
    analyzer.run_enhanced_analysis()


if __name__ == "__main__":
    main()
