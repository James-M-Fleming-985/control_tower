#!/usr/bin/env python3
"""
Surface Finishing Specific NADCAP Analysis - FILTERED PD FORMS ONLY
Only uses the 83 surface finishing specific PD forms identified in the audit scope
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


class SFSpecificNADCAPAnalyzer:
    def __init__(self, base_folder):
        self.base_folder = base_folder
        self.inputs_folder = os.path.join(base_folder, "Inputs")
        self.outputs_folder = os.path.join(base_folder, "outputs")
        self.uncontrolled_folder = os.path.join(
            self.inputs_folder, "uncontrolled_documents"
        )
        self.pd_forms_folder = os.path.join(self.inputs_folder, "pd_forms")

        # Load surface finishing specific PD numbers from the reference
        # analysis
        self.sf_specific_pd_numbers = self.load_sf_specific_pd_numbers()

        # Enhanced synonym mapping
        self.synonym_mapping = {
            "plant": [
                "facility",
                "site",
                "shop",
                "area",
                "location",
                "premises",
                "building",
            ],
            "layout": [
                "arrangement",
                "configuration",
                "setup",
                "design",
                "plan",
                "drawing",
                "sketch",
            ],
            "training": [
                "competency",
                "qualification",
                "education",
                "instruction",
                "development",
                "skill",
            ],
            "personnel": [
                "staff",
                "operators",
                "employees",
                "workers",
                "technicians",
                "engineers",
            ],
            "chemical": [
                "surface finishing",
                "plating",
                "coating",
                "treatment",
                "processing",
            ],
            "process": ["procedure", "method", "operation", "technique", "treatment"],
            "sampling": [
                "inspection",
                "testing",
                "examination",
                "analysis",
                "checking",
            ],
            "inspection": ["testing", "examination", "checking", "analysis", "review"],
            "testing": [
                "inspection",
                "examination",
                "analysis",
                "evaluation",
                "checking",
            ],
            "plans": ["procedures", "protocols", "methods", "instructions", "guides"],
            "equipment": ["machinery", "apparatus", "instruments", "tools", "devices"],
            "maintenance": ["service", "repair", "upkeep", "tpm", "calibration"],
            "documentation": [
                "records",
                "documents",
                "forms",
                "procedures",
                "instructions",
            ],
            "records": ["documentation", "logs", "reports", "data", "forms"],
            "procedures": ["instructions", "methods", "protocols", "guides", "manuals"],
            "control": [
                "management",
                "oversight",
                "supervision",
                "regulation",
                "monitoring",
            ],
            "monitoring": [
                "checking",
                "tracking",
                "surveillance",
                "observation",
                "control",
            ],
            "plating": ["coating", "surface finishing", "electroplating", "deposition"],
            "coating": ["plating", "surface treatment", "finishing", "layer"],
            "finishing": ["coating", "plating", "treatment", "surface treatment"],
            "specification": ["standard", "requirement", "criteria", "guideline"],
            "forms": ["documents", "paperwork", "records", "sheets", "templates"],
        }

        print(
            f"Surface Finishing Specific PD Numbers: {
                len(
                    self.sf_specific_pd_numbers)}"
        )
        print(f"PD Numbers: {sorted(self.sf_specific_pd_numbers)[:10]}...")

    def load_sf_specific_pd_numbers(self):
        """Load surface finishing specific PD numbers from reference analysis"""
        try:
            pd_ref_file = os.path.join(
                self.outputs_folder, "PD_References_Analysis_20250905_0851.xlsx"
            )
            pd_ref_df = pd.read_excel(pd_ref_file)

            sf_pd_numbers = set()
            for idx, row in pd_ref_df.iterrows():
                pd_ref = str(row.get("PD_Reference", ""))
                if pd_ref and pd_ref != "nan" and pd_ref != "N/A":
                    # Clean up the PD reference
                    pd_clean = re.sub(r"[^\w\d]", "", pd_ref.upper())
                    if pd_clean.startswith("PD") and len(pd_clean) > 2:
                        sf_pd_numbers.add(pd_clean)

            return sf_pd_numbers
        except Exception as e:
            print(f"Error loading SF specific PD numbers: {e}")
            return set()

    def is_sf_specific_pd_form(self, filename):
        """Check if a PD form file is surface finishing specific"""
        filename_upper = filename.upper()

        # Extract PD number from filename
        for pd_num in self.sf_specific_pd_numbers:
            if pd_num in filename_upper:
                return True

        return False

    def expand_text_with_synonyms(self, text):
        """Expand text with relevant synonyms"""
        if not text or len(text.strip()) < 3:
            return text

        expanded_terms = [text]
        text_lower = text.lower()

        for key_term, synonyms in self.synonym_mapping.items():
            if key_term in text_lower:
                expanded_terms.extend(synonyms)

        return " ".join(expanded_terms)

    def extract_text_from_file(self, file_path):
        """Extract text from various file formats"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".pdf":
                return self.extract_pdf_text(file_path)
            elif file_ext == ".docx":
                return docx2txt.process(file_path)
            elif file_ext == ".doc":
                try:
                    text = docx2txt.process(file_path)
                    if text and len(text.strip()) > 10:
                        return text
                except BaseException:
                    pass
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

            text_content = []
            for col in df.columns:
                text_content.extend(df[col].astype(str).tolist())

            return " ".join([str(x) for x in text_content if str(x) != "nan"])
        except BaseException:
            return f"Data file: {os.path.basename(file_path)}"

    def extract_document_title(self, file_path, content):
        """Extract document title"""
        filename_title = os.path.splitext(os.path.basename(file_path))[0]

        if not content or len(content.strip()) < 10:
            return filename_title

        lines = content.split("\n")

        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if len(line) > 10 and len(line) < 150:
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
                elif i < 5 and len(line) > 15 and not line.isupper():
                    return line

        return filename_title

    def load_controlled_documents(self):
        """Load controlled documents from Excel inventory"""
        documents = []
        excel_file = None

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
                notes = str(row.get("Notes", "")).strip()

                if cheops_ref and cheops_ref != "nan" and title and title != "nan":
                    content = notes if notes and notes != "nan" else title

                    expanded_title = self.expand_text_with_synonyms(title)
                    expanded_content = self.expand_text_with_synonyms(content)
                    full_text = f"{expanded_title} {expanded_content}"

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
        """Load uncontrolled documents"""
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

                    expanded_title = self.expand_text_with_synonyms(title)
                    expanded_content = self.expand_text_with_synonyms(content)
                    full_text = f"{expanded_title} {expanded_content}"

                    filename = os.path.splitext(file)[0]
                    cheops_ref = f"UNCONTROLLED-{file_count:03d}"

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

        print(f"Found {len(documents)} uncontrolled documents")
        return documents

    def load_sf_specific_pd_forms(self):
        """Load ONLY surface finishing specific PD forms"""
        documents = []

        if not os.path.exists(self.pd_forms_folder):
            print(f"PD forms folder not found: {self.pd_forms_folder}")
            return documents

        print(f"Loading SF-specific PD forms from: {self.pd_forms_folder}")

        supported_extensions = [
            ".pdf",
            ".docx",
            ".doc",
            ".xlsx",
            ".csv",
            ".txt"]
        file_count = 0
        processed_count = 0

        for root, dirs, files in os.walk(self.pd_forms_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in supported_extensions:
                    file_count += 1

                    # FILTER: Only process SF-specific PD forms
                    if self.is_sf_specific_pd_form(file):
                        print(f"Processing SF-specific PD Form: {file}")
                        processed_count += 1

                        content = self.extract_text_from_file(file_path)
                        title = self.extract_document_title(file_path, content)

                        expanded_title = self.expand_text_with_synonyms(title)
                        expanded_content = self.expand_text_with_synonyms(
                            content)
                        full_text = f"{expanded_title} {expanded_content}"

                        filename = os.path.splitext(file)[0]
                        pd_ref = (
                            filename.upper()
                            if filename.upper().startswith("PD")
                            else f"PD-{filename}"
                        )

                        documents.append(
                            {
                                "title": title,
                                "content": content,
                                "cheops_ref": pd_ref,
                                "full_text": full_text,
                                "content_source": "SF-Specific PD Form",
                                "control_status": "PD Form",
                                "document_title": title,
                            }
                        )
                    # else:
                    #     print(f"Skipping non-SF PD Form: {file}")

        print(f"Total PD files found: {file_count}")
        print(f"SF-specific PD forms processed: {processed_count}")
        print(f"Non-SF PD forms skipped: {file_count - processed_count}")
        return documents

    def load_nadcap_requirements(self):
        """Load NADCAP requirements"""
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
        """Extract meaningful requirements with synonym expansion"""
        requirements = []

        for idx, row in nadcap_df.iterrows():
            title = str(row.get("Title", "")).strip()
            title1 = str(row.get("Title.1", "")).strip()
            content = str(row.get("Content", "")).strip()
            guidance = str(row.get("Guidence ", "")).strip()

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
                enhanced_requirement = self.expand_text_with_synonyms(
                    full_requirement)
                requirements.append(enhanced_requirement)
            else:
                requirements.append(f"Requirement {idx + 1}")

        print(
            f"Extracted {
                len(requirements)} requirements with enhanced synonym context"
        )
        return requirements

    def calculate_similarity_matrix(self, requirements, documents):
        """Calculate TF-IDF similarity matrix"""
        print("Calculating TF-IDF similarity scores...")

        doc_texts = [doc["full_text"] for doc in documents]
        all_texts = requirements + doc_texts

        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8,
        )

        tfidf_matrix = vectorizer.fit_transform(all_texts)

        req_matrix = tfidf_matrix[: len(requirements)]
        doc_matrix = tfidf_matrix[len(requirements):]

        similarity_matrix = cosine_similarity(req_matrix, doc_matrix)

        return similarity_matrix

    def find_best_matches(self, requirements, documents, similarity_matrix):
        """Find best matches for each requirement"""
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
        """Generate compliance status"""
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
        """Generate action required"""
        score = best_match["similarity_score"]
        status = best_match["control_status"]

        if score >= 0.7:
            if status in ["Controlled", "PD Form"]:
                return "Verify content alignment and completeness"
            else:
                return "Formalize document control for existing content"
        elif score >= 0.4:
            if status in ["Controlled", "PD Form"]:
                return "Review and enhance existing documentation"
            else:
                return "Enhance content and establish document control"
        elif score >= 0.2:
            if status in ["Controlled", "PD Form"]:
                return "Assess relevance and consider enhancement"
            else:
                return "Evaluate content and consider control establishment"
        else:
            return "Create new documentation"

    def generate_enhanced_gap_description(self, requirement, best_match):
        """Generate detailed gap description"""
        score = best_match["similarity_score"]
        confidence = score * 100
        status = best_match["control_status"]

        status_note = ""
        if status == "PD Form":
            status_note = " (SF-Specific PD Form)"
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
        """Append analysis columns to NADCAP requirements"""
        print("Appending analysis columns to NADCAP requirements...")

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

            if match["similarity_score"] >= 0.2:
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

        enhanced_df["Compliance_Status"] = compliance_statuses
        enhanced_df["Primary_Evidence"] = primary_evidences
        enhanced_df["Action_Required"] = actions_required
        enhanced_df["Gap_Description"] = gap_descriptions
        enhanced_df["Control_Status"] = control_statuses
        enhanced_df["Document_Title"] = document_titles

        return enhanced_df

    def run_sf_specific_analysis(self):
        """Run SF-specific NADCAP gap analysis"""
        print("Surface Finishing Specific NADCAP Gap Analysis")
        print("=" * 50)

        # Load all document types (with SF-specific PD filtering)
        controlled_docs = self.load_controlled_documents()
        uncontrolled_docs = self.load_uncontrolled_documents()
        sf_pd_forms = self.load_sf_specific_pd_forms()

        # Combine all documents
        all_documents = controlled_docs + uncontrolled_docs + sf_pd_forms

        print(f"\nTotal documents for analysis:")
        print(f"  - Controlled: {len(controlled_docs)}")
        print(f"  - Uncontrolled: {len(uncontrolled_docs)}")
        print(f"  - SF-Specific PD Forms: {len(sf_pd_forms)}")
        print(f"  - Total: {len(all_documents)}")

        # Load NADCAP requirements
        nadcap_df = self.load_nadcap_requirements()

        # Extract meaningful requirements
        requirements = self.extract_meaningful_requirements(nadcap_df)

        # Calculate similarity matrix
        similarity_matrix = self.calculate_similarity_matrix(
            requirements, all_documents
        )

        # Find best matches
        best_matches = self.find_best_matches(
            requirements, all_documents, similarity_matrix
        )

        # Append analysis columns
        enhanced_df = self.append_analysis_columns(
            nadcap_df, requirements, best_matches
        )

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(
            self.outputs_folder, f"Enhanced_NADCAP_SF_Specific_PD_Only_{timestamp}.xlsx"
        )
        enhanced_df.to_excel(output_file, index=False)
        print(f"\nSF-Specific NADCAP file saved: {output_file}")

        # Print summary statistics
        print("=" * 50)
        print("SF-Specific Analysis Complete!")
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
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"

    analyzer = SFSpecificNADCAPAnalyzer(base_folder)
    analyzer.run_sf_specific_analysis()


if __name__ == "__main__":
    main()
