#!/usr/bin/env python3
"""
Enhanced NADCAP Gap Analysis with Uncontrolled Document Support
Analyzes both controlled inventory and uncontrolled documents
Includes document control status in compliance assessment
"""

import os
import re
import subprocess
import warnings
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime

import docx2txt
import numpy as np
import pandas as pd
import PyPDF2
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore")


# Document text extraction libraries


class EnhancedNADCAPAnalyzer:
    def __init__(self):
        self.base_folder = os.path.dirname(os.path.abspath(__file__))
        self.inputs_folder = os.path.join(self.base_folder, "Inputs")
        self.outputs_folder = os.path.join(self.base_folder, "outputs")
        self.uncontrolled_folder = os.path.join(
            self.inputs_folder, "uncontrolled_documents"
        )

        # Create outputs folder if it doesn't exist
        os.makedirs(self.outputs_folder, exist_ok=True)

    def extract_text_from_file(self, file_path):
        """Extract text content from various file formats"""
        try:
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
                print(f"Unsupported file format: {file_ext}")
                return ""
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return ""

    def extract_pdf_text(self, file_path):
        """Extract text from PDF file"""
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except BaseException:
            return ""

    def extract_docx_text(self, file_path):
        """Extract text from Word document"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except BaseException:
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
                print(
                    f"Antiword could not process {file_path}, trying docx2txt...")
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

    def extract_document_title(self, file_path, content):
        """Extract the actual document title from content, with enhanced detection"""
        filename_title = os.path.splitext(os.path.basename(file_path))[0]

        if not content or len(content.strip()) < 10:
            return filename_title

        # Clean and split content into lines
        lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        lines = [line.strip() for line in lines if line.strip()]

        # Priority 1: Look for explicit title patterns
        title_patterns = [
            r"^TITLE\s*:?\s*(.+)$",
            r"^DOCUMENT\s+TITLE\s*:?\s*(.+)$",
            r"^PROCEDURE\s+TITLE\s*:?\s*(.+)$",
            r"^MANUAL\s+TITLE\s*:?\s*(.+)$",
            r"^WORK\s+INSTRUCTION\s*:?\s*(.+)$",
            r"^OPERATING\s+INSTRUCTION\s*:?\s*(.+)$",
        ]

        for line in lines[:20]:  # Check first 20 lines
            for pattern in title_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    if len(title) > 5 and len(title) < 200:
                        return title

        # Priority 2: Look for centered or prominent text (likely titles)
        for i, line in enumerate(lines[:15]):
            if not line:
                continue

            # Skip obvious non-titles
            skip_patterns = [
                r"^\d+[\./]\d+[\./]\d+",  # dates
                r"^page\s+\d+",  # page numbers
                r"^revision\s*:",  # revision info
                r"^document\s+id\s*:",  # document IDs
                r"^author\s*:",  # author info
                r"^approved\s+by\s*:",  # approval info
                r"^effective\s+date\s*:",  # dates
                r"^confidential",  # confidentiality notices
                r"^copyright",  # copyright notices
                r"^\w+\s*[-\s]\s*\d+\s*[-\s]\s*\d+",  # MANP-3-3-542 format
            ]

            if any(re.match(pattern, line, re.IGNORECASE)
                   for pattern in skip_patterns):
                continue

            # Look for substantial, meaningful titles
            if 10 <= len(line) <= 150:
                # Strong title indicators
                strong_indicators = [
                    "procedure",
                    "instruction",
                    "manual",
                    "guide",
                    "specification",
                    "standard",
                    "control",
                    "process",
                    "method",
                    "protocol",
                    "operation",
                    "maintenance",
                    "calibration",
                    "inspection",
                    "testing",
                    "quality",
                    "safety",
                    "training",
                    "analysis",
                    "surface",
                    "finishing",
                    "plating",
                    "coating",
                    "treatment",
                ]

                # Check if line contains strong title indicators
                if any(indicator in line.lower()
                       for indicator in strong_indicators):
                    # Additional validation: not all uppercase unless it's a
                    # proper title
                    if not line.isupper() or len(line.split()) >= 3:
                        return line

                # For early lines (likely titles), be more permissive
                if i <= 3 and len(line) >= 15:
                    # Check if it's not just a reference number
                    if not re.match(r"^[A-Z0-9\.\-\s]+$", line):
                        return line
                    # Even if it is uppercase, if it has multiple words it
                    # might be a title
                    elif len(line.split()) >= 3:
                        return line

        # Priority 3: Look for any substantial line that could be a title
        for i, line in enumerate(lines[:10]):
            if 15 <= len(line) <= 100:
                # Skip pure reference numbers or codes
                if not re.match(r"^[A-Z0-9\.\-\s]+$", line):
                    return line
                # But include descriptive uppercase text
                elif len(line.split()) >= 4 and any(
                    word.lower()
                    in [
                        "surface",
                        "finishing",
                        "plating",
                        "coating",
                        "process",
                        "procedure",
                        "control",
                        "quality",
                        "safety",
                        "maintenance",
                        "operation",
                        "instruction",
                        "manual",
                        "standard",
                        "specification",
                        "method",
                        "analysis",
                        "testing",
                        "inspection",
                        "calibration",
                        "training",
                    ]
                    for word in line.split()
                ):
                    return line

        # Priority 4: Look for longer lines that might be descriptive titles
        for line in lines[:8]:
            if 20 <= len(line) <= 80 and len(line.split()) >= 4:
                # Exclude obvious non-titles
                if not any(
                    exclude in line.lower()
                    for exclude in [
                        "copyright",
                        "confidential",
                        "proprietary",
                        "page",
                        "revision",
                        "document id",
                        "effective date",
                    ]
                ):
                    return line

        # Final fallback: use filename but try to make it more readable
        return filename_title

    def load_uncontrolled_documents(self):
        """Scan and load uncontrolled documents from folder"""
        documents = []

        if not os.path.exists(self.uncontrolled_folder):
            print(
                f"Uncontrolled documents folder not found: {
                    self.uncontrolled_folder}"
            )
            return documents

        print(
            f"Scanning uncontrolled documents from: {
                self.uncontrolled_folder}"
        )

        supported_extensions = [".pdf", ".docx", ".doc", ".xlsx", ".txt"]
        file_count = 0

        for root, dirs, files in os.walk(self.uncontrolled_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in supported_extensions:
                    print(f"Processing: {file}")
                    file_count += 1

                    # Extract text content first
                    content = self.extract_text_from_file(file_path)

                    # Extract enhanced title from content or fallback to
                    # filename
                    title = self.extract_document_title(file_path, content)

                    if (
                        content and len(content) > 20
                    ):  # Only include files with meaningful content
                        documents.append(
                            {
                                "title": title,
                                "content": content,
                                "cheops_ref": f"UNCONTROLLED-{file_count:03d}",
                                "full_text": f"{title} {content}",
                                "content_source": "File Content",
                                "control_status": "Uncontrolled",
                                "file_path": file_path,
                                "file_type": file_ext[1:],  # Remove the dot
                                "document_title": title,  # Add explicit document title field
                            }
                        )
                    else:
                        # Include file with title only if content extraction
                        # failed
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
                                "document_title": title,  # Add explicit document title field
                            }
                        )

        print(f"Found {len(documents)} uncontrolled documents")
        return documents

    def load_nadcap_requirements(self):
        """Load the original NADCAP requirements file"""
        nadcap_file = os.path.join(
            self.inputs_folder, "NADCAP Audit Requirements 030925.xlsx"
        )
        print(f"Loading NADCAP requirements from: {nadcap_file}")

        nadcap_df = pd.read_excel(nadcap_file)
        print(f"NADCAP file loaded successfully. Shape: {nadcap_df.shape}")
        print(f"Columns: {list(nadcap_df.columns)}")

        return nadcap_df

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

            # Include ALL documents with meaningful titles
            if title and title != "nan" and len(title) > 5:
                # Use title as primary searchable text, supplement with content
                # if available
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
                        "document_title": title,  # Add explicit document title field
                    }
                )

        print(f"Found {len(documents)} controlled documents")
        return documents

    def extract_requirements(self, nadcap_df):
        """Extract requirements with enhanced meaningful context"""
        requirements = []

        for idx, row in nadcap_df.iterrows():
            clause = str(row.get("Clause", "")).strip()
            content = str(row.get("Content", "")).strip()
            # Column C - section title
            title = str(row.get("Title", "")).strip()
            # Column E - subsection title
            title_1 = str(row.get("Title.1", "")).strip()
            guidance = str(
                row.get(
                    "Guidence ",
                    "")).strip()  # Column H - guidance

            if clause and clause != "nan" and content and content != "nan":
                # Build enriched requirement text with meaningful context (skip
                # numeric sections)
                context_parts = []

                # Add section title (meaningful text)
                if title and title != "nan":
                    context_parts.append(title)

                # Add subsection title (meaningful text)
                if title_1 and title_1 != "nan":
                    context_parts.append(title_1)

                # Combine meaningful context
                context_text = " ".join(context_parts)

                # Build enriched text with title, content, and guidance
                enriched_parts = []
                if context_text:
                    enriched_parts.append(context_text)
                enriched_parts.append(content)
                if guidance and guidance != "nan":
                    enriched_parts.append(guidance)

                enriched_text = " ".join(enriched_parts).strip()

                requirements.append(
                    {
                        "clause": clause,
                        "content": content,
                        "enriched_text": enriched_text,
                        "section_context": context_text,
                        "guidance": guidance,
                    }
                )

        print(
            f"Extracted {
                len(requirements)} requirements with enhanced meaningful context"
        )
        return requirements

    def calculate_similarity_scores(self, requirements, documents):
        """Calculate TF-IDF similarity scores"""
        print("Calculating TF-IDF similarity scores...")

        # Prepare text data
        req_texts = [req["enriched_text"] for req in requirements]
        doc_texts = [doc["full_text"] for doc in documents]

        # Combine for TF-IDF vectorization
        all_texts = req_texts + doc_texts

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
        )

        tfidf_matrix = vectorizer.fit_transform(all_texts)

        # Split back into requirements and documents
        req_vectors = tfidf_matrix[: len(requirements)]
        doc_vectors = tfidf_matrix[len(requirements):]

        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(req_vectors, doc_vectors)

        return similarity_matrix

    def find_best_matches(self, requirements, documents, similarity_matrix):
        """Find best document matches for each requirement"""
        best_matches = []

        for i, req in enumerate(requirements):
            # Get similarity scores for this requirement
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
        """Generate compliance status considering both content match and control status"""
        if similarity_score >= 0.7:
            if control_status == "Controlled":
                return "Compliant"
            else:
                return "Content Match - Needs Control"
        elif similarity_score >= 0.4:
            if control_status == "Controlled":
                return "Partial - Controlled"
            else:
                return "Partial - Needs Control"
        elif similarity_score >= 0.2:
            if control_status == "Controlled":
                return "Review Required - Controlled"
            else:
                return "Review Required - Needs Control"
        else:
            return "Non-Compliant"

    def generate_primary_evidence(self, best_match):
        """Generate primary evidence with CHEOPS reference and control status"""
        if best_match["similarity_score"] >= 0.2:
            cheops = best_match["cheops_ref"]
            title = best_match["document_title"]
            status = best_match["control_status"]

            if cheops:
                return f"{cheops} - {title} [{status}]"
            else:
                return f"{title} [{status}]"
        else:
            return "No match found"

    def generate_enhanced_action_required(self, requirement, best_match):
        """Generate action required considering control status"""
        score = best_match["similarity_score"]
        control_status = best_match["control_status"]

        if score >= 0.7:
            if control_status == "Controlled":
                return "Verify document completeness and maintain controls"
            else:
                return "Bring matching document into controlled environment"
        elif score >= 0.4:
            if control_status == "Controlled":
                return "Review and enhance existing controlled documentation"
            else:
                return "Enhance document content and establish controls"
        elif score >= 0.2:
            if control_status == "Controlled":
                return "Manual review required - verify controlled document addresses requirement"
            else:
                return "Manual review required - consider bringing into controlled environment"
        else:
            return "Create new controlled documentation to address requirement"

    def generate_enhanced_gap_description(self, requirement, best_match):
        """Generate enhanced gap description with control consideration"""
        score = best_match["similarity_score"]
        confidence = score * 100
        control_status = best_match["control_status"]

        status_note = f" ({control_status})"

        if score >= 0.7:
            return f"Strong match found (confidence: {confidence:.1f}%){status_note} - verify completeness"
        elif score >= 0.4:
            return f"Partial match (confidence: {confidence:.1f}%){status_note} - may need enhancement"
        elif score >= 0.2:
            return f"Weak match (confidence: {confidence:.1f}%){status_note} - manual review required"
        else:
            return f"No suitable documentation found (confidence: {confidence:.1f}%)"

    def append_analysis_columns(self, nadcap_df, requirements, best_matches):
        """Append enhanced analysis columns to NADCAP requirements"""
        print("Appending enhanced analysis columns to NADCAP requirements...")

        # Create a copy of the original dataframe
        enhanced_df = nadcap_df.copy()

        # Initialize new columns
        enhanced_df["Compliance_Status"] = "Non-Compliant"
        enhanced_df["Primary_Evidence"] = "No match found"
        enhanced_df["Action_Required"] = "Create new documentation"
        enhanced_df["Gap_Description"] = "No documentation found"
        enhanced_df["Control_Status"] = "Unknown"
        # Add document title column
        enhanced_df["Document_Title"] = "No match found"

        # Fill in the analysis results
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

                # Only assign control status if there's actually a match
                # (similarity >= 0.2)
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
        """Run the complete enhanced NADCAP gap analysis"""
        print("Enhanced NADCAP Gap Analysis with Uncontrolled Documents")
        print("=" * 60)

        # Load data
        nadcap_df = self.load_nadcap_requirements()
        controlled_docs = self.load_controlled_documents()
        uncontrolled_docs = self.load_uncontrolled_documents()

        # Combine all documents
        all_documents = controlled_docs + uncontrolled_docs
        print(f"\nTotal documents for analysis:")
        print(f"  - Controlled: {len(controlled_docs)}")
        print(f"  - Uncontrolled: {len(uncontrolled_docs)}")
        print(f"  - Total: {len(all_documents)}")

        # Extract requirements
        requirements = self.extract_requirements(nadcap_df)

        # Calculate similarities
        similarity_matrix = self.calculate_similarity_scores(
            requirements, all_documents
        )

        # Find best matches
        best_matches = self.find_best_matches(
            requirements, all_documents, similarity_matrix
        )

        # Create enhanced output
        enhanced_df = self.append_analysis_columns(
            nadcap_df, requirements, best_matches
        )

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(
            self.outputs_folder, f"Enhanced_NADCAP_with_Uncontrolled_{timestamp}.xlsx"
        )
        enhanced_df.to_excel(output_file, index=False)

        print(f"\nEnhanced NADCAP file saved: {output_file}")
        print("=" * 60)
        print("Analysis Complete!")
        print(f"Results saved to: {self.outputs_folder}")

        # Generate summary
        status_counts = enhanced_df["Compliance_Status"].value_counts()
        control_counts = enhanced_df["Control_Status"].value_counts()

        print(f"\nSummary:")
        print(f"- Total Requirements Analyzed: {len(enhanced_df)}")
        for status, count in status_counts.items():
            print(f"- {status}: {count}")

        print(f"\nDocument Control Distribution:")
        for control, count in control_counts.items():
            print(f"- {control}: {count}")


if __name__ == "__main__":
    analyzer = EnhancedNADCAPAnalyzer()
    analyzer.run_analysis()
