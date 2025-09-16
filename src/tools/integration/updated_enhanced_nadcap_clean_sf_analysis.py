#!/usr/bin/env python3
"""
Updated Enhanced NADCAP Clean SF Analysis
- Uses Surface Finishes and MLG 030925.xlsx specifically
- Uses sf_pd_forms folder with newly added files
- Omits uncontrolled_documents to avoid contamination
- Enhanced synonym mapping for better matching
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


class UpdatedSFNADCAPAnalyzer:
    def __init__(self, base_folder):
        self.base_folder = base_folder
        self.inputs_folder = os.path.join(base_folder, "Inputs")
        self.outputs_folder = os.path.join(base_folder, "outputs")
        self.sf_pd_forms_folder = os.path.join(
            self.inputs_folder, "sf_pd_forms")
        self.sf_manps_folder = os.path.join(self.inputs_folder, "sf_manps")

        # Enhanced synonym mapping with more comprehensive terms
        self.synonym_mapping = {
            "plant": [
                "facility",
                "site",
                "shop",
                "area",
                "location",
                "premises",
                "building",
                "factory",
                "mill",
            ],
            "layout": [
                "arrangement",
                "configuration",
                "setup",
                "design",
                "plan",
                "drawing",
                "sketch",
                "blueprint",
                "diagram",
            ],
            "training": [
                "competency",
                "qualification",
                "education",
                "instruction",
                "development",
                "skill",
                "certification",
                "learning",
            ],
            "personnel": [
                "staff",
                "operators",
                "employees",
                "workers",
                "technicians",
                "engineers",
                "team",
                "workforce",
            ],
            "chemical": [
                "surface finishing",
                "plating",
                "coating",
                "treatment",
                "processing",
                "chemistry",
                "solution",
            ],
            "process": [
                "procedure",
                "method",
                "operation",
                "technique",
                "treatment",
                "workflow",
                "protocol",
            ],
            "sampling": [
                "inspection",
                "testing",
                "examination",
                "analysis",
                "checking",
                "evaluation",
                "assessment",
            ],
            "inspection": [
                "testing",
                "examination",
                "checking",
                "analysis",
                "review",
                "audit",
                "verification",
            ],
            "testing": [
                "inspection",
                "examination",
                "analysis",
                "evaluation",
                "checking",
                "validation",
                "assessment",
            ],
            "plans": [
                "procedures",
                "protocols",
                "methods",
                "instructions",
                "guides",
                "manuals",
                "documentation",
            ],
            "equipment": [
                "machinery",
                "apparatus",
                "instruments",
                "tools",
                "devices",
                "hardware",
                "systems",
            ],
            "maintenance": [
                "service",
                "repair",
                "upkeep",
                "tpm",
                "calibration",
                "preventive",
                "corrective",
            ],
            "documentation": [
                "records",
                "documents",
                "forms",
                "procedures",
                "instructions",
                "paperwork",
                "files",
            ],
            "records": [
                "documentation",
                "logs",
                "reports",
                "data",
                "forms",
                "files",
                "archives",
            ],
            "procedures": [
                "instructions",
                "methods",
                "protocols",
                "guides",
                "manuals",
                "sops",
                "work instructions",
            ],
            "control": [
                "management",
                "oversight",
                "supervision",
                "regulation",
                "monitoring",
                "governance",
            ],
            "monitoring": [
                "checking",
                "tracking",
                "surveillance",
                "observation",
                "control",
                "supervision",
            ],
            "plating": [
                "coating",
                "surface finishing",
                "electroplating",
                "deposition",
                "finishing",
            ],
            "coating": [
                "plating",
                "surface treatment",
                "finishing",
                "layer",
                "film",
                "application",
            ],
            "finishing": [
                "coating",
                "plating",
                "treatment",
                "surface treatment",
                "processing",
            ],
            "specification": [
                "standard",
                "requirement",
                "criteria",
                "guideline",
                "spec",
                "requirement",
            ],
            "forms": [
                "documents",
                "paperwork",
                "records",
                "sheets",
                "templates",
                "checklists",
            ],
            "calibration": [
                "adjustment",
                "verification",
                "validation",
                "check",
                "standardization",
            ],
            "approval": [
                "authorization",
                "validation",
                "acceptance",
                "endorsement",
                "sign-off",
            ],
            "inventory": [
                "stock",
                "supplies",
                "materials",
                "parts",
                "components",
                "resources",
            ],
            "storage": [
                "warehousing",
                "keeping",
                "containment",
                "housing",
                "repository",
            ],
            "quality": [
                "qc",
                "qa",
                "assurance",
                "standards",
                "excellence",
                "compliance",
            ],
            "environment": [
                "environmental",
                "workplace",
                "conditions",
                "atmosphere",
                "surroundings",
            ],
            "safety": ["health", "security", "protection", "hazard", "risk", "safe"],
            "waste": ["disposal", "scrap", "reject", "byproduct", "effluent"],
            "manp": ["manual", "procedure", "instruction", "protocol", "guide"],
            "surface": ["coating", "plating", "finishing", "treatment", "layer"],
        }

        print(f"SF PD Forms folder: {self.sf_pd_forms_folder}")
        print(f"SF MANPs folder: {self.sf_manps_folder}")

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
            elif file_ext in [".xlsx", ".xls", ".csv"]:
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
            return self.clean_title_from_filename(filename_title)

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
                        "competency",
                        "training",
                    ]
                ):
                    return self.clean_extracted_title(line, filename_title)
                elif i < 5 and len(line) > 15 and not line.isupper():
                    return self.clean_extracted_title(line, filename_title)

        return self.clean_title_from_filename(filename_title)

    def clean_title_from_filename(self, filename):
        """Clean title extracted from filename"""
        # Remove PD numbers and common prefixes
        clean_title = re.sub(r"^PD\d+\s*", "", filename, flags=re.IGNORECASE)
        clean_title = re.sub(
            r"^(Document|Data file):\s*", "", clean_title, flags=re.IGNORECASE
        )
        clean_title = clean_title.strip()

        # If title is still mostly the PD number, extract meaningful part
        if len(clean_title) < 10 and "PD" in filename:
            # Look for descriptive text after PD number
            parts = filename.split()
            meaningful_parts = [
                part for part in parts if not re.match(r"^PD\d+$", part, re.IGNORECASE)
            ]
            if meaningful_parts:
                clean_title = " ".join(meaningful_parts)

        return clean_title if clean_title else filename

    def clean_extracted_title(self, extracted_title, filename):
        """Clean title extracted from document content"""
        # Remove common prefixes
        clean_title = re.sub(
            r"^(Document|Data file):\s*", "", extracted_title, flags=re.IGNORECASE
        )
        clean_title = re.sub(
            r"^PD\d+\s*",
            "",
            clean_title,
            flags=re.IGNORECASE)
        clean_title = clean_title.strip()

        # If the cleaned title is too short or just numbers, fall back to
        # filename
        if len(clean_title) < 5 or clean_title.isdigit():
            return self.clean_title_from_filename(filename)

        return clean_title

    def load_controlled_documents_from_surface_finishes(self):
        """Load controlled documents specifically from Surface Finishes and MLG 030925.xlsx, targeting column I with proper CHEOPS refs and titles"""
        documents = []

        # Look specifically for the Surface Finishes and MLG 030925.xlsx file
        target_file = os.path.join(
            self.inputs_folder, "Surface Finishes and MFG 030925.xlsx"
        )

        if not os.path.exists(target_file):
            print(f"Target file not found: {target_file}")
            return documents

        print(f"Loading controlled documents from: {target_file}")
        print(
            "Targeting column I for document content with CHEOPS references and titles"
        )

        try:
            # Read the first sheet (tab 1) specifically
            df = pd.read_excel(target_file,
                               sheet_name=0)  # Sheet index 0 = tab 1
            print(f"Loaded first sheet. Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")

            # Check if we have enough columns to access column I (index 8)
            if df.shape[1] < 9:
                print(
                    f"Error: Not enough columns. Only {
                        df.shape[1]} columns found, need at least 9 for column I"
                )
                return documents

            # Get column I (index 8) - Notes column
            column_i = df.iloc[:, 8]  # Column I is the 9th column (index 8)
            column_i_name = df.columns[8] if len(
                df.columns) > 8 else "Column_I"

            # Get CHEOPS Ref column (usually column C, index 2)
            cheops_column = df.iloc[:, 2] if df.shape[1] > 2 else None
            cheops_column_name = df.columns[2] if len(
                df.columns) > 2 else "CHEOPS_Ref"

            # Get Title column (usually column F, index 5)
            title_column = df.iloc[:, 5] if df.shape[1] > 5 else None
            title_column_name = df.columns[5] if len(
                df.columns) > 5 else "Title"

            print(
                f"Processing column I ('{column_i_name}') with {
                    len(column_i)} rows"
            )
            print(f"CHEOPS Ref column: '{cheops_column_name}'")
            print(f"Title column: '{title_column_name}'")

            # Process each row in column I that has content
            valid_documents = 0
            for idx, cell_value in enumerate(column_i):
                cell_content = str(cell_value).strip()

                # Only process cells with substantial content
                if cell_content and cell_content != "nan" and len(
                        cell_content) > 50:
                    # Get CHEOPS reference for this row
                    cheops_ref = (
                        str(cheops_column.iloc[idx]).strip()
                        if cheops_column is not None
                        else ""
                    )
                    if cheops_ref == "nan" or not cheops_ref:
                        cheops_ref = f"SF-ROW-{idx + 1:03d}"

                    # Get title for this row
                    doc_title = (
                        str(title_column.iloc[idx]).strip()
                        if title_column is not None
                        else ""
                    )
                    if doc_title == "nan" or not doc_title:
                        doc_title = f"Surface Finishing Document {idx + 1}"

                    # Create display title with reference and title
                    display_title = f"{cheops_ref}: {doc_title}"

                    # Expand with synonyms for better matching
                    expanded_title = self.expand_text_with_synonyms(
                        display_title)
                    expanded_content = self.expand_text_with_synonyms(
                        cell_content)
                    full_text = f"{expanded_title} {expanded_content}"

                    documents.append(
                        {
                            "title": display_title,
                            "content": cell_content,
                            "cheops_ref": cheops_ref,
                            "full_text": full_text,
                            "content_source": "Surface Finishes Column I",
                            "control_status": "Controlled",
                            "document_title": doc_title,
                            "display_reference": display_title,  # For primary evidence display
                        }
                    )
                    valid_documents += 1

            print(
                f"Found {valid_documents} valid documents in column I with proper references"
            )

            # Show sample of what we found
            if documents:
                print(f"Sample CHEOPS reference: {documents[0]['cheops_ref']}")
                print(f"Sample title: {documents[0]['document_title']}")
                print(f"Sample display: {documents[0]['display_reference']}")

        except Exception as e:
            print(f"Error loading Surface Finishes and MLG file: {e}")
            import traceback

            traceback.print_exc()

        print(
            f"Found {
                len(documents)} controlled documents from Surface Finishes and MLG column I"
        )
        return documents

    def load_sf_pd_forms(self):
        """Load SF-specific PD forms from sf_pd_forms folder"""
        documents = []

        if not os.path.exists(self.sf_pd_forms_folder):
            print(f"SF PD forms folder not found: {self.sf_pd_forms_folder}")
            return documents

        print(f"Loading SF PD forms from: {self.sf_pd_forms_folder}")

        supported_extensions = [
            ".pdf",
            ".docx",
            ".doc",
            ".txt",
            ".xlsx",
            ".xls"]
        file_count = 0

        for root, dirs, files in os.walk(self.sf_pd_forms_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in supported_extensions:
                    print(f"Processing SF PD form: {file}")
                    file_count += 1

                    content = self.extract_text_from_file(file_path)
                    title = self.extract_document_title(file_path, content)

                    expanded_title = self.expand_text_with_synonyms(title)
                    expanded_content = self.expand_text_with_synonyms(content)
                    full_text = f"{expanded_title} {expanded_content}"

                    # Extract PD reference from filename if possible
                    pd_match = re.search(r"PD[-\s]*(\d+)", file, re.IGNORECASE)
                    cheops_ref = (
                        f"PD{pd_match.group(1)}"
                        if pd_match
                        else f"SF-PD-{file_count:03d}"
                    )

                    # Create display reference combining CHEOPS ref and title
                    display_title = f"{cheops_ref}: {title}"

                    documents.append(
                        {
                            "title": title,
                            "content": content,
                            "cheops_ref": cheops_ref,
                            "full_text": full_text,
                            "content_source": "SF PD Form",
                            "control_status": "PD Form",
                            "document_title": title,
                            "display_reference": display_title,  # For primary evidence display
                        }
                    )

        print(f"Found {len(documents)} SF PD forms")
        return documents

    def load_sf_manps(self):
        """Load SF-specific MANPs from sf_manps folder if it exists"""
        documents = []

        if not os.path.exists(self.sf_manps_folder):
            print(f"SF MANPs folder not found: {self.sf_manps_folder}")
            return documents

        print(f"Loading SF MANPs from: {self.sf_manps_folder}")

        supported_extensions = [".pdf", ".docx", ".doc", ".txt"]
        file_count = 0

        for root, dirs, files in os.walk(self.sf_manps_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in supported_extensions:
                    print(f"Processing SF MANP: {file}")
                    file_count += 1

                    content = self.extract_text_from_file(file_path)
                    title = self.extract_document_title(file_path, content)

                    expanded_title = self.expand_text_with_synonyms(title)
                    expanded_content = self.expand_text_with_synonyms(content)
                    full_text = f"{expanded_title} {expanded_content}"

                    # Extract MANP reference from filename if possible
                    manp_match = re.search(
                        r"MANP[-\s]*(\d+(?:\.\d+)*)", file, re.IGNORECASE
                    )
                    cheops_ref = (
                        f"MANP-{manp_match.group(1)}"
                        if manp_match
                        else f"SF-MANP-{file_count:03d}"
                    )

                    # Create display reference combining CHEOPS ref and title
                    display_title = f"{cheops_ref}: {title}"

                    documents.append(
                        {
                            "title": title,
                            "content": content,
                            "cheops_ref": cheops_ref,
                            "full_text": full_text,
                            "content_source": "SF MANP",
                            "control_status": "MANP",
                            "document_title": title,
                            "display_reference": display_title,  # For primary evidence display
                        }
                    )

        print(f"Found {len(documents)} SF MANPs")
        return documents

    def load_nadcap_requirements(self):
        """Load NADCAP requirements from Excel file"""
        excel_file = None

        for file in os.listdir(self.inputs_folder):
            if file.endswith(".xlsx") and (
                "nadcap" in file.lower() or "ac7" in file.lower()
            ):
                excel_file = os.path.join(self.inputs_folder, file)
                break

        if not excel_file:
            print("No NADCAP requirements file found")
            return pd.DataFrame()

        print(f"Loading NADCAP requirements from: {excel_file}")

        try:
            df = pd.read_excel(excel_file)
            print(
                f"NADCAP requirements loaded successfully. Shape: {
                    df.shape}"
            )
            return df
        except Exception as e:
            print(f"Error loading NADCAP requirements: {e}")
            return pd.DataFrame()

    def extract_meaningful_requirements(self, nadcap_df):
        """Extract meaningful requirements from NADCAP dataframe with enhanced context"""
        requirements = []

        if nadcap_df.empty:
            return requirements

        # Define key columns for enhanced extraction
        content_columns = [
            "Title",
            "Title.1",
            "Clause",
            "Content",
        ]  # Core requirement content
        context_columns = [
            "Section",
            "Sub Section",
            "Guidence "]  # Additional context

        print(
            f"Extracting requirements from content columns: {content_columns}")
        print(f"Adding context from: {context_columns}")

        for idx, row in nadcap_df.iterrows():
            # Extract core requirement content
            requirement_text = ""
            for col in content_columns:
                if col in nadcap_df.columns:
                    cell_value = str(row.get(col, "")).strip()
                    if cell_value and cell_value != "nan" and len(
                            cell_value) > 3:
                        requirement_text += f" {cell_value}"

            # Extract contextual information
            context_text = ""
            section = str(row.get("Section", "")).strip()
            sub_section = str(row.get("Sub Section", "")).strip()
            guidance = str(row.get("Guidence ", "")).strip()

            if section and section != "nan":
                context_text += f" Section {section}"
            if sub_section and sub_section != "nan":
                context_text += f" Subsection {sub_section}"
            if guidance and guidance != "nan" and len(guidance) > 10:
                context_text += f" Guidance: {guidance}"

            # Combine requirement with context for better matching
            full_requirement_text = requirement_text + context_text

            if len(requirement_text.strip()) > 20:
                expanded_requirement = self.expand_text_with_synonyms(
                    full_requirement_text
                )
                requirements.append(
                    {
                        "index": idx,
                        "text": requirement_text.strip(),
                        "context": context_text.strip(),
                        "full_text": full_requirement_text.strip(),
                        "expanded_text": expanded_requirement,
                        "section": section,
                        "sub_section": sub_section,
                        "guidance": guidance,
                    }
                )

        print(
            f"Extracted {
                len(requirements)} meaningful requirements with enhanced context"
        )
        return requirements

    def calculate_similarity_matrix(self, requirements, documents):
        """Calculate similarity matrix between requirements and documents"""
        if not requirements or not documents:
            return np.array([])

        print("Calculating similarity matrix...")

        # Prepare texts for vectorization
        requirement_texts = [req["expanded_text"] for req in requirements]
        document_texts = [doc["full_text"] for doc in documents]

        # Combine all texts for TF-IDF
        all_texts = requirement_texts + document_texts

        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            # Split back into requirements and documents
            req_matrix = tfidf_matrix[: len(requirements)]
            doc_matrix = tfidf_matrix[len(requirements):]

            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(req_matrix, doc_matrix)

            print(f"Similarity matrix shape: {similarity_matrix.shape}")
            return similarity_matrix

        except Exception as e:
            print(f"Error calculating similarity matrix: {e}")
            return np.array([])

    def find_best_matches_with_hierarchy(
        self, requirements, documents, similarity_matrix
    ):
        """
        Comprehensive allocation algorithm to ensure ALL Column I documents are utilized
        Strategy: Every controlled document should provide evidence for NADCAP requirements
        """
        evidence_matches = []

        if similarity_matrix.size == 0:
            return evidence_matches

        print("Finding comprehensive matches to utilize ALL Column I documents...")

        # Separate documents by source for hierarchy
        column_i_docs = []
        pd_form_docs = []
        manp_docs = []

        for idx, doc in enumerate(documents):
            if doc["content_source"] == "Surface Finishes Column I":
                column_i_docs.append((idx, doc))
            elif doc["content_source"] == "SF PD Form":
                pd_form_docs.append((idx, doc))
            elif doc["content_source"] == "SF MANP":
                manp_docs.append((idx, doc))

        print(
            f"Document hierarchy: Column I ({
                len(column_i_docs)}), PD Forms ({
                len(pd_form_docs)}), MANPs ({
                len(manp_docs)})"
        )

        # COMPREHENSIVE STRATEGY: Ensure every Column I document gets used
        # Create document-requirement score matrix
        doc_req_scores = {}

        for doc_idx, doc in column_i_docs:
            doc_ref = doc.get("display_reference", doc["cheops_ref"])
            doc_req_scores[doc_ref] = []

            for req_idx, requirement in enumerate(requirements):
                if req_idx < similarity_matrix.shape[0]:
                    score = similarity_matrix[req_idx][doc_idx]
                    doc_req_scores[doc_ref].append(
                        {"req_idx": req_idx, "requirement": requirement, "score": score}
                    )

            # Sort by score for this document
            doc_req_scores[doc_ref].sort(
                key=lambda x: x["score"], reverse=True)

        print(
            f"📊 Document-Requirement matrix created for {
                len(doc_req_scores)} documents"
        )

        # ALLOCATION STRATEGY: Assign every document to its best requirements
        allocated_requirements = set()
        document_allocations = {}

        # Sort documents by their best score to prioritize high-quality matches
        # first
        sorted_docs = []
        for doc_ref, req_scores in doc_req_scores.items():
            best_score = req_scores[0]["score"] if req_scores else 0
            sorted_docs.append((doc_ref, best_score, req_scores))

        sorted_docs.sort(key=lambda x: x[1], reverse=True)

        print(f"📋 Processing documents in order of best available scores...")

        # Allocate each document to requirements
        for doc_ref, best_score, req_scores in sorted_docs:
            allocated_for_this_doc = 0
            min_score_threshold = 0.05  # Very low threshold to ensure allocation

            for score_entry in req_scores:
                req_idx = score_entry["req_idx"]
                score = score_entry["score"]

                # Allocate if:
                # 1. Requirement not already allocated AND score above threshold, OR
                # 2. This document hasn't been allocated yet (force at least
                # one allocation per doc)
                if (
                    req_idx not in allocated_requirements
                    and score >= min_score_threshold
                ) or (allocated_for_this_doc == 0 and score > 0):

                    allocated_requirements.add(req_idx)

                    if doc_ref not in document_allocations:
                        document_allocations[doc_ref] = []

                    document_allocations[doc_ref].append(
                        {
                            "req_idx": req_idx,
                            "requirement": score_entry["requirement"],
                            "score": score,
                        }
                    )

                    allocated_for_this_doc += 1

                    # Limit allocations per document to distribute evenly
                    if allocated_for_this_doc >= 8:  # Max 8 requirements per document
                        break

            if allocated_for_this_doc == 0:
                print(
                    f"⚠️  Warning: {doc_ref} could not be allocated to any requirement"
                )

        print(
            f"✅ Allocated {
                len(allocated_requirements)} requirements across {
                len(document_allocations)} documents"
        )

        # Create evidence matches for allocated requirements
        for doc_ref, allocations in document_allocations.items():
            for allocation in allocations:
                req_idx = allocation["req_idx"]
                requirement = allocation["requirement"]
                primary_score = allocation["score"]

                # Find the document object
                primary_doc = None
                for doc_idx, doc in column_i_docs:
                    if doc.get("display_reference",
                               doc["cheops_ref"]) == doc_ref:
                        primary_doc = doc
                        break

                if primary_doc:
                    primary_evidence = {
                        "document": primary_doc,
                        "score": primary_score,
                        "confidence": (
                            "High"
                            if primary_score > 0.3
                            else "Medium" if primary_score > 0.15 else "Low"
                        ),
                    }

                    # Find secondary evidence
                    secondary_evidence = None
                    secondary_score = 0

                    if req_idx < similarity_matrix.shape[0]:
                        similarities = similarity_matrix[req_idx]
                        for doc_idx, doc in pd_form_docs + manp_docs:
                            score = similarities[doc_idx]
                            if score > secondary_score:
                                secondary_score = score
                                secondary_evidence = {
                                    "document": doc,
                                    "score": score,
                                    "confidence": (
                                        "High"
                                        if score > 0.3
                                        else "Medium" if score > 0.15 else "Low"
                                    ),
                                }

                    # Determine compliance status
                    if primary_score > 0.15:
                        compliance_status = (
                            "Strong Evidence"
                            if primary_score > 0.3
                            else "Potential Evidence"
                        )
                        action = (
                            "Document Verified - Ready for Audit"
                            if primary_score > 0.3
                            else "Review and Update as Required"
                        )
                    else:
                        # Still potential since we have a controlled doc
                        compliance_status = "Potential Evidence"
                        action = (
                            "Review Document Relevance - Controlled Evidence Available"
                        )

                    evidence_matches.append(
                        {
                            "req_index": requirement["index"],
                            "primary_evidence": primary_evidence,
                            "secondary_evidence": secondary_evidence,
                            "compliance_status": compliance_status,
                            "recommended_action": action,
                            "requirement_text": requirement["text"],
                            "section": requirement.get("section", ""),
                            "guidance": requirement.get("guidance", ""),
                        }
                    )

        # Handle any unallocated requirements
        for req_idx, requirement in enumerate(requirements):
            if req_idx not in allocated_requirements:
                evidence_matches.append(
                    {
                        "req_index": requirement["index"],
                        "primary_evidence": None,
                        "secondary_evidence": None,
                        "compliance_status": "Gap Identified",
                        "recommended_action": "Generate and Release Document",
                        "requirement_text": requirement["text"],
                        "section": requirement.get("section", ""),
                        "guidance": requirement.get("guidance", ""),
                    }
                )

        # Report comprehensive utilization
        print(f"\n📊 COMPREHENSIVE DOCUMENT UTILIZATION:")
        print(
            f"   Column I documents allocated: {
                len(document_allocations)}/{
                len(column_i_docs)}"
        )
        print(
            f"   Utilization rate: {
                (
                    len(document_allocations) / len(column_i_docs)) * 100:.1f}%"
        )
        print(
            f"   Requirements with primary evidence: {
                len(
                    [
                        m for m in evidence_matches if m['primary_evidence']])}"
        )

        if len(document_allocations) < len(column_i_docs):
            unused_docs = len(column_i_docs) - len(document_allocations)
            print(
                f"   ⚠️  Still {unused_docs} documents unused - may need lower thresholds"
            )

        print(
            f"\nFound {
                len(evidence_matches)} evidence matches with comprehensive allocation"
        )
        return evidence_matches

    def _create_evidence_match(
        self, requirement, column_i_scores, secondary_docs, similarities
    ):
        """Helper to create evidence match structure"""

        # Primary evidence (best Column I match)
        primary_evidence = None
        if column_i_scores and column_i_scores[0]["score"] > 0:
            best_col_i = column_i_scores[0]
            primary_evidence = {
                "document": best_col_i["doc"],
                "score": best_col_i["score"],
                "confidence": (
                    "High"
                    if best_col_i["score"] > 0.3
                    else "Medium" if best_col_i["score"] > 0.15 else "Low"
                ),
            }

        # Secondary evidence (best PD form/MANP)
        secondary_evidence = None
        secondary_score = 0

        for doc_idx, doc in secondary_docs:
            score = similarities[doc_idx]
            if score > secondary_score:
                secondary_score = score
                secondary_evidence = {
                    "document": doc,
                    "score": score,
                    "confidence": (
                        "High" if score > 0.3 else "Medium" if score > 0.15 else "Low"
                    ),
                }

        # Determine compliance status based on primary evidence
        if primary_evidence and primary_evidence["score"] > 0.15:
            compliance_status = (
                "Strong Evidence"
                if primary_evidence["score"] > 0.3
                else "Potential Evidence"
            )
            action = (
                "Document Verified - Ready for Audit"
                if primary_evidence["score"] > 0.3
                else "Review and Update as Required"
            )
        else:
            compliance_status = "Gap Identified"
            action = "Generate and Release Document"

        return {
            "req_index": requirement["index"],
            "primary_evidence": primary_evidence,
            "secondary_evidence": secondary_evidence,
            "compliance_status": compliance_status,
            "recommended_action": action,
            "requirement_text": requirement["text"],
            "section": requirement.get("section", ""),
            "guidance": requirement.get("guidance", ""),
        }

    def _calculate_relative_strength(
            self, score, all_scores, score_type="Primary"):
        """Calculate relative strength based on score distribution"""
        if not all_scores or score == 0:
            return "No Match"

        # Filter out zero scores for percentile calculation
        non_zero_scores = [s for s in all_scores if s > 0]
        if not non_zero_scores:
            return "No Match"

        # Calculate percentiles from actual data distribution
        scores_sorted = sorted(non_zero_scores, reverse=True)
        total_count = len(scores_sorted)

        # Find score's position in the distribution
        score_rank = sum(1 for s in scores_sorted if s >= score)
        percentile = (score_rank / total_count) * 100

        # Relative strength thresholds based on distribution
        if percentile <= 10:  # Top 10%
            return "Excellent"
        elif percentile <= 25:  # Top 25%
            return "Strong"
        elif percentile <= 50:  # Top 50%
            return "Good"
        elif percentile <= 75:  # Top 75%
            return "Fair"
        else:  # Bottom 25%
            return "Weak"

    def append_analysis_columns(
            self, nadcap_df, requirements, evidence_matches):
        """Append analysis columns to the original NADCAP dataframe with evidence hierarchy"""
        if nadcap_df.empty:
            return pd.DataFrame()

        print("Appending analysis columns with evidence hierarchy...")

        # Create copies of the original columns
        enhanced_df = nadcap_df.copy()

        # Initialize new columns with evidence hierarchy
        enhanced_df["Primary_Evidence"] = ""
        enhanced_df["Primary_Score"] = 0.0
        enhanced_df["Primary_Strength"] = "No Match"
        enhanced_df["Primary_Source"] = ""
        enhanced_df["Secondary_Evidence"] = ""
        enhanced_df["Secondary_Score"] = 0.0
        enhanced_df["Secondary_Strength"] = "No Match"
        enhanced_df["Secondary_Source"] = ""
        enhanced_df["Compliance_Status"] = "Needs Review"
        enhanced_df["Recommended_Action"] = ""
        enhanced_df["Section_Context"] = ""
        enhanced_df["Guidance_Context"] = ""

        # Collect all scores for relative strength calculation
        all_primary_scores = []
        all_secondary_scores = []

        for match in evidence_matches:
            if match["primary_evidence"]:
                all_primary_scores.append(match["primary_evidence"]["score"])
            if match["secondary_evidence"]:
                all_secondary_scores.append(
                    match["secondary_evidence"]["score"])

        print(
            f"Score distribution - Primary: {
                len(all_primary_scores)} scores, Secondary: {
                len(all_secondary_scores)} scores"
        )

        # Fill in the analysis results
        for match in evidence_matches:
            req_idx = match["req_index"]
            if req_idx < len(enhanced_df):
                # Primary Evidence (Surface Finishes Column I)
                if match["primary_evidence"]:
                    primary_doc = match["primary_evidence"]["document"]
                    primary_ref = primary_doc.get(
                        "display_reference", primary_doc["cheops_ref"]
                    )
                    primary_score = match["primary_evidence"]["score"]
                    primary_strength = self._calculate_relative_strength(
                        primary_score, all_primary_scores, "Primary"
                    )

                    enhanced_df.at[req_idx, "Primary_Evidence"] = primary_ref
                    enhanced_df.at[req_idx, "Primary_Score"] = round(
                        primary_score, 3)
                    enhanced_df.at[req_idx,
                                   "Primary_Strength"] = primary_strength
                    enhanced_df.at[req_idx, "Primary_Source"] = primary_doc[
                        "content_source"
                    ]
                else:
                    enhanced_df.at[req_idx, "Primary_Evidence"] = (
                        "No controlled document found"
                    )
                    enhanced_df.at[req_idx, "Primary_Score"] = 0.0
                    enhanced_df.at[req_idx, "Primary_Strength"] = "No Match"
                    enhanced_df.at[req_idx, "Primary_Source"] = "N/A"

                # Secondary Evidence (PD Forms/MANPs)
                if match["secondary_evidence"]:
                    secondary_doc = match["secondary_evidence"]["document"]
                    secondary_ref = secondary_doc.get(
                        "display_reference", secondary_doc["cheops_ref"]
                    )
                    secondary_score = match["secondary_evidence"]["score"]
                    secondary_strength = self._calculate_relative_strength(
                        secondary_score, all_secondary_scores, "Secondary"
                    )

                    enhanced_df.at[req_idx,
                                   "Secondary_Evidence"] = secondary_ref
                    enhanced_df.at[req_idx, "Secondary_Score"] = round(
                        secondary_score, 3
                    )
                    enhanced_df.at[req_idx,
                                   "Secondary_Strength"] = secondary_strength
                    enhanced_df.at[req_idx, "Secondary_Source"] = secondary_doc[
                        "content_source"
                    ]
                else:
                    enhanced_df.at[req_idx, "Secondary_Evidence"] = (
                        "No supporting document found"
                    )
                    enhanced_df.at[req_idx, "Secondary_Score"] = 0.0
                    enhanced_df.at[req_idx, "Secondary_Strength"] = "No Match"
                    enhanced_df.at[req_idx, "Secondary_Source"] = "N/A"

                # Compliance Status and Action (based on primary evidence only)
                enhanced_df.at[req_idx, "Compliance_Status"] = match[
                    "compliance_status"
                ]
                enhanced_df.at[req_idx, "Recommended_Action"] = match[
                    "recommended_action"
                ]

                # Context Information
                enhanced_df.at[req_idx, "Section_Context"] = match.get(
                    "section", "")
                enhanced_df.at[req_idx, "Guidance_Context"] = match.get(
                    "guidance", "")

        # Set default action for any unmatched requirements (those still marked
        # as 'Needs Review')
        unmatched_mask = enhanced_df["Compliance_Status"] == "Needs Review"
        enhanced_df.loc[unmatched_mask, "Compliance_Status"] = "Gap Identified"
        enhanced_df.loc[unmatched_mask, "Recommended_Action"] = (
            "Generate and Release Document"
        )
        enhanced_df.loc[unmatched_mask, "Primary_Evidence"] = (
            "No controlled document found"
        )
        enhanced_df.loc[unmatched_mask, "Secondary_Evidence"] = (
            "No supporting document found"
        )
        enhanced_df.loc[unmatched_mask, "Primary_Strength"] = "No Match"
        enhanced_df.loc[unmatched_mask, "Secondary_Strength"] = "No Match"

        # Print relative strength distribution for diagnostics
        primary_strength_dist = enhanced_df["Primary_Strength"].value_counts()
        secondary_strength_dist = enhanced_df["Secondary_Strength"].value_counts(
        )

        print(f"\n📊 PRIMARY EVIDENCE STRENGTH DISTRIBUTION:")
        for strength, count in primary_strength_dist.items():
            print(f"   {strength}: {count}")

        print(f"\n📊 SECONDARY EVIDENCE STRENGTH DISTRIBUTION:")
        for strength, count in secondary_strength_dist.items():
            print(f"   {strength}: {count}")

        print(f"\nEnhanced dataframe shape: {enhanced_df.shape}")
        return enhanced_df

    def get_match_strength(self, score):
        """Determine match strength based on similarity score"""
        if score >= 0.35:
            return "Excellent"
        elif score >= 0.25:
            return "Strong"
        elif score >= 0.15:
            return "Medium"
        elif score >= 0.10:
            return "Weak"
        elif score > 0:
            return "Very Weak"
        else:
            return "No Match"

    def run_updated_sf_analysis(self):
        """Run the updated SF-specific NADCAP analysis targeting Column I and sf_pd_forms"""
        print("Starting Updated SF-Specific NADCAP Analysis")
        print(
            "Targeting: Column I from Surface Finishes and MLG 030925.xlsx + sf_pd_forms"
        )
        print("=" * 80)

        # Load documents from updated sources
        controlled_docs = self.load_controlled_documents_from_surface_finishes()
        sf_pd_forms = self.load_sf_pd_forms()
        sf_manps = self.load_sf_manps()

        # Combine documents with emphasis on sf_pd_forms and column I content
        all_documents = controlled_docs + sf_pd_forms + sf_manps

        print(f"\nTotal documents for analysis:")
        print(f"  - Surface Finishes Column I: {len(controlled_docs)}")
        print(f"  - SF PD Forms: {len(sf_pd_forms)}")
        print(f"  - SF MANPs: {len(sf_manps)}")
        print(f"  - Total: {len(all_documents)}")

        if len(controlled_docs) == 0:
            print("⚠️  Warning: No content loaded from Surface Finishes Column I")
        if len(sf_pd_forms) == 0:
            print("⚠️  Warning: No SF PD Forms loaded")

        # Load NADCAP requirements
        nadcap_df = self.load_nadcap_requirements()

        if nadcap_df.empty:
            print("No NADCAP requirements found. Cannot proceed with analysis.")
            return

        if len(all_documents) == 0:
            print(
                "No documents found for analysis. Please check file paths and content."
            )
            return

        # Extract meaningful requirements
        requirements = self.extract_meaningful_requirements(nadcap_df)

        # Calculate similarity matrix
        similarity_matrix = self.calculate_similarity_matrix(
            requirements, all_documents
        )

        # Find evidence matches with hierarchy
        evidence_matches = self.find_best_matches_with_hierarchy(
            requirements, all_documents, similarity_matrix
        )

        # Append analysis columns
        enhanced_df = self.append_analysis_columns(
            nadcap_df, requirements, evidence_matches
        )

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(
            self.outputs_folder, f"Enhanced_NADCAP_Clean_SF_Analysis_{timestamp}.xlsx"
        )

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            enhanced_df.to_excel(
                writer, sheet_name="NADCAP_Analysis", index=False)

            # Create summary sheet
            summary_data = [
                ["Metric", "Count"],
                ["Total NADCAP Requirements", len(enhanced_df)],
                ["Surface Finishes Column I Documents", len(controlled_docs)],
                ["SF PD Forms", len(sf_pd_forms)],
                ["SF MANPs", len(sf_manps)],
                ["Total Evidence Documents", len(all_documents)],
                [
                    "Strong Evidence",
                    len(
                        enhanced_df[
                            enhanced_df["Compliance_Status"] == "Strong Evidence"
                        ]
                    ),
                ],
                [
                    "Potential Evidence",
                    len(
                        enhanced_df[
                            enhanced_df["Compliance_Status"] == "Potential Evidence"
                        ]
                    ),
                ],
                [
                    "Gaps Identified",
                    len(
                        enhanced_df[
                            enhanced_df["Compliance_Status"] == "Gap Identified"
                        ]
                    ),
                ],
            ]
            summary_df = pd.DataFrame(
                summary_data[1:], columns=summary_data[0])
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

        print(
            f"\nUpdated Clean SF-Specific NADCAP Analysis saved: {output_file}")

        # Print summary statistics
        print("=" * 80)
        print("Updated SF-Specific Analysis Complete!")
        print(
            f"✅ Column I Content: {
                len(controlled_docs)} documents processed"
        )
        print(f"✅ SF PD Forms: {len(sf_pd_forms)} documents processed")
        print(f"Results saved to: {output_file}")

        if not enhanced_df.empty:
            summary = enhanced_df["Compliance_Status"].value_counts()
            print("\nCompliance Status Summary:")
            for status, count in summary.items():
                print(f"- {status}: {count}")

            print(f"\nDocument Source Distribution:")
            primary_source_summary = enhanced_df["Primary_Source"].value_counts(
            )
            print("Primary Evidence Sources:")
            for source, count in primary_source_summary.items():
                print(f"- {source}: {count}")

            secondary_source_summary = enhanced_df["Secondary_Source"].value_counts(
            )
            print("Secondary Evidence Sources:")
            for source, count in secondary_source_summary.items():
                print(f"- {source}: {count}")

            # Show primary evidence from Column I specifically
            col_i_matches = enhanced_df[
                enhanced_df["Primary_Source"] == "Surface Finishes Column I"
            ]
            if len(col_i_matches) > 0:
                print(
                    f"\n📊 Primary Evidence from Column I: {
                        len(col_i_matches)}"
                )
                for idx, row in col_i_matches.head(3).iterrows():
                    evidence = row.get("Primary_Evidence", "N/A")
                    score = row.get("Primary_Score", 0)
                    print(f"  - {evidence} (Score: {score})")

            # Show high-scoring primary evidence
            high_scoring = enhanced_df[enhanced_df["Primary_Score"] > 0.3]
            if len(high_scoring) > 0:
                print(
                    f"\n🎯 High-Scoring Primary Evidence: {len(high_scoring)}")
                for idx, row in high_scoring.head(5).iterrows():
                    evidence = row.get("Primary_Evidence", "N/A")
                    score = row.get("Primary_Score", 0)
                    source = row.get("Primary_Source", "N/A")
                    print(f"  - {evidence} (Score: {score}, Source: {source})")

        return output_file


def main():
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"

    analyzer = UpdatedSFNADCAPAnalyzer(base_folder)
    analyzer.run_updated_sf_analysis()


if __name__ == "__main__":
    main()
