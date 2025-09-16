#!/usr/bin/env python3
"""
Enhanced NADCAP Gap Analysis Script
Performs advanced keyword matching and semantic analysis between NADCAP requirements
and SF documentation inventory with document context.

Updated for Copy of Surface Finishes and MFG 040925.xlsx with context in Column IE
"""

import os
import re
import warnings
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore")

# Define common stop words for keyword extraction
STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "can",
    "shall",
    "this",
    "that",
    "these",
    "those",
}


class EnhancedNADCAPGapAnalyzer:
    def __init__(self, inputs_folder: str, outputs_folder: str):
        self.inputs_folder = inputs_folder
        self.outputs_folder = outputs_folder
        self.nadcap_file = "NADCAP Audit Requirements 030925.xlsx"
        self.sf_inventory_file = "Copy of Surface Finishes and MFG 040925.xlsx"

        # Ensure outputs folder exists
        os.makedirs(outputs_folder, exist_ok=True)

        # Analysis results storage
        self.nadcap_requirements = None
        self.sf_inventory = None
        self.gap_analysis_results = []

        # Initialize NLP components
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 3), max_features=5000, lowercase=True
        )

    def load_nadcap_requirements(self) -> pd.DataFrame:
        """Load NADCAP requirements from Excel file"""
        try:
            nadcap_path = os.path.join(self.inputs_folder, self.nadcap_file)
            print(f"Loading NADCAP requirements from: {nadcap_path}")

            # Try to read the first sheet
            df = pd.read_excel(nadcap_path, sheet_name=0)
            print(f"NADCAP file loaded successfully. Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")

            # Clean and prepare requirements data
            # Identify likely requirement text columns
            requirement_columns = [
                col
                for col in df.columns
                if any(
                    word in col.lower()
                    for word in ["requirement", "question", "clause", "text", "content"]
                )
            ]

            if not requirement_columns:
                # If no obvious requirement column, use the largest text column
                text_lengths = {}
                for col in df.columns:
                    if df[col].dtype == "object":
                        avg_length = df[col].astype(str).str.len().mean()
                        text_lengths[col] = avg_length

                if text_lengths:
                    requirement_columns = [
                        max(text_lengths.keys(), key=text_lengths.get)
                    ]

            print(f"Using requirement columns: {requirement_columns}")

            # Create standardized columns
            df["requirement_id"] = df.index + 1
            df["requirement_text"] = (
                df[requirement_columns[0]].astype(str)
                if requirement_columns
                else "No requirement text found"
            )
            df["section"] = df.get("Section", "Unknown")
            df["clause"] = df.get("Clause", "Unknown")

            # Clean requirement text
            df["requirement_text_clean"] = df["requirement_text"].apply(
                self.clean_text)

            self.nadcap_requirements = df
            print(f"Processed {len(df)} NADCAP requirements")
            return df

        except Exception as e:
            print(f"Error loading NADCAP requirements: {str(e)}")
            return pd.DataFrame()

    def load_sf_inventory(self) -> pd.DataFrame:
        """Load SF inventory with document context from Column I"""
        try:
            sf_path = os.path.join(self.inputs_folder, self.sf_inventory_file)
            print(f"Loading SF inventory from: {sf_path}")

            # Try to read the first sheet (Tab 1)
            df = pd.read_excel(sf_path, sheet_name=0)
            print(f"SF inventory loaded successfully. Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")

            # Column I is index 8 (A=0, B=1, C=2, ..., I=8)
            context_column_index = 8  # Column I

            # Get column by index if it exists
            if len(df.columns) > context_column_index:
                context_column = df.columns[context_column_index]
                print(
                    f"Found document content in column I (index {context_column_index}): {context_column}"
                )
            else:
                print(f"Column I not found, using last available column")
                context_column = df.columns[-1]

            # Standardize column names
            df["document_name"] = (
                df.iloc[:, 5].astype(str)
                if len(df.columns) > 5
                else df.iloc[:, 0].astype(str)
            )  # Title column (index 5)
            df["document_type"] = (
                df.iloc[:, 0].astype(str) if len(df.columns) > 0 else "Unknown"
            )  # Document Category
            df["document_context"] = (
                df.iloc[:, context_column_index].astype(str)
                if len(df.columns) > context_column_index
                else "No context available"
            )

            # Clean document context
            df["document_context_clean"] = df["document_context"].apply(
                self.clean_text)

            # Create combined text for analysis (name + type + context)
            df["combined_text"] = (
                df["document_name"]
                + " "
                + df["document_type"]
                + " "
                + df["document_context_clean"]
            )

            # Remove rows with minimal information (but be more lenient since
            # we have full document content)
            df = df[df["document_name"].str.len() > 3]
            df = df[
                ~df["document_context"].isin(
                    ["nan", "NaN", "", "No context available"])
            ]
            df = df[
                df["document_context_clean"].str.len() > 10
            ]  # At least some meaningful content

            self.sf_inventory = df
            print(f"Processed {len(df)} SF inventory documents with context")

            # Show sample of what we found
            if len(df) > 0:
                print(f"\nSample document content preview:")
                sample_doc = df.iloc[0]
                print(f"Document: {sample_doc['document_name']}")
                print(
                    f"Content preview: {sample_doc['document_context'][:200]}...")

            return df

        except Exception as e:
            print(f"Error loading SF inventory: {str(e)}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        if pd.isna(text) or text == "nan":
            return ""

        text = str(text).lower()
        # Remove special characters but keep spaces and basic punctuation
        text = re.sub(r"[^\w\s\.\,\;\:\?\!]", " ", text)
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text using simple NLP"""
        if not text or text.strip() == "":
            return []

        # Clean and tokenize
        text = text.lower()
        # Remove punctuation but keep alphanumeric and spaces
        text = re.sub(r"[^\w\s]", " ", text)
        words = text.split()

        # Filter meaningful keywords
        keywords = []
        for word in words:
            if (
                len(word) > 2
                and word not in STOP_WORDS
                and not word.isdigit()
                and word.isalpha()
            ):
                keywords.append(word)

        return list(set(keywords))

    def calculate_keyword_match_score(
            self, req_text: str, doc_text: str) -> float:
        """Calculate keyword overlap score between requirement and document"""
        req_keywords = set(self.extract_keywords(req_text))
        doc_keywords = set(self.extract_keywords(doc_text))

        if not req_keywords:
            return 0.0

        intersection = req_keywords.intersection(doc_keywords)
        return len(intersection) / len(req_keywords)

    def calculate_semantic_similarity(
            self, req_text: str, doc_text: str) -> float:
        """Calculate semantic similarity using TF-IDF cosine similarity"""
        try:
            texts = [req_text, doc_text]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            similarity = cosine_similarity(
                tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except BaseException:
            return 0.0

    def analyze_compliance_match(
            self, requirement: Dict, document: Dict) -> Dict:
        """Analyze compliance match between a requirement and document"""
        req_text = requirement["requirement_text_clean"]
        doc_text = document["combined_text"]

        # Calculate different types of scores
        keyword_score = self.calculate_keyword_match_score(req_text, doc_text)
        semantic_score = self.calculate_semantic_similarity(req_text, doc_text)

        # Calculate weighted combined score (30% keywords + 40% context + 30% semantic)
        # For now, we'll use keyword and semantic, and treat context as part of
        # semantic
        combined_score = (keyword_score * 0.3) + (semantic_score * 0.7)

        # Determine confidence level
        if combined_score >= 0.85:
            confidence_level = "High (85-100%)"
            status = "Compliant"
        elif combined_score >= 0.60:
            confidence_level = "Medium (60-84%)"
            status = "Partial"
        elif combined_score >= 0.30:
            confidence_level = "Low (30-59%)"
            status = "Review Required"
        else:
            confidence_level = "No Match (0-29%)"
            status = "Non-Compliant"

        return {
            "requirement_id": requirement["requirement_id"],
            "requirement_text": requirement["requirement_text"],
            "section": requirement["section"],
            "clause": requirement["clause"],
            "document_name": document["document_name"],
            "document_type": document["document_type"],
            "document_context": document["document_context"],
            "keyword_score": keyword_score,
            "semantic_score": semantic_score,
            "combined_score": combined_score,
            "confidence_level": confidence_level,
            "compliance_status": status,
            "match_justification": f"Keyword overlap: {keyword_score:.2%}, Semantic similarity: {semantic_score:.2%}",
        }

    def run_gap_analysis(self):
        """Run comprehensive gap analysis"""
        print("Starting Enhanced NADCAP Gap Analysis...")
        print("=" * 60)

        # Load data
        if self.nadcap_requirements is None:
            self.load_nadcap_requirements()
        if self.sf_inventory is None:
            self.load_sf_inventory()

        if self.nadcap_requirements.empty or self.sf_inventory.empty:
            print("Error: Could not load required data files")
            return

        print(
            f"Analyzing {len(self.nadcap_requirements)} requirements against {len(self.sf_inventory)} documents..."
        )

        # Analyze each requirement against all documents
        for idx, requirement in self.nadcap_requirements.iterrows():
            print(
                f"Processing requirement {idx + 1}/{len(self.nadcap_requirements)}")

            best_matches = []

            for doc_idx, document in self.sf_inventory.iterrows():
                match_result = self.analyze_compliance_match(
                    requirement.to_dict(), document.to_dict()
                )
                best_matches.append(match_result)

            # Sort by combined score and keep top matches
            best_matches.sort(key=lambda x: x["combined_score"], reverse=True)

            # Store the best match for this requirement
            if best_matches:
                self.gap_analysis_results.append(best_matches[0])

        print(
            f"Gap analysis completed. Processed {
                len(
                    self.gap_analysis_results)} requirement-document matches."
        )

    def generate_enhanced_requirements_matrix(self):
        """Generate the enhanced NADCAP requirements matrix with gap analysis columns"""
        if not self.gap_analysis_results:
            print("No gap analysis results to process")
            return

        # Convert results to DataFrame
        results_df = pd.DataFrame(self.gap_analysis_results)

        # Create the enhanced matrix with all required columns
        enhanced_matrix = pd.DataFrame(
            {
                "Requirement_ID": results_df["requirement_id"],
                "Section": results_df["section"],
                "Clause": results_df["clause"],
                "Requirement_Text": results_df["requirement_text"],
                "Compliance_Status": results_df["compliance_status"],
                "Confidence_Score": (results_df["combined_score"] * 100).round(1),
                "Primary_Evidence": results_df["document_name"],
                "Supporting_Evidence": "",  # Will be populated with additional matches
                "Gap_Description": results_df.apply(
                    self.generate_gap_description, axis=1
                ),
                "Risk_Level": results_df.apply(self.assess_risk_level, axis=1),
                "Action_Required": results_df.apply(
                    self.generate_action_required, axis=1
                ),
                "Estimated_Effort": results_df.apply(self.estimate_effort, axis=1),
                "Priority": results_df.apply(self.calculate_priority, axis=1),
                "Recommended_Owner": "TBD",
                "Target_Completion_Date": "",
                "Match_Justification": results_df["match_justification"],
            }
        )

        # Save enhanced requirements matrix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(
            self.outputs_folder, f"Enhanced_NADCAP_Requirements_Matrix_{timestamp}.xlsx"
        )

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            enhanced_matrix.to_excel(
                writer, sheet_name="Requirements_Matrix", index=False
            )

            # Add summary statistics
            summary_stats = self.generate_summary_statistics(enhanced_matrix)
            summary_stats.to_excel(
                writer, sheet_name="Summary_Dashboard", index=False)

        print(f"Enhanced requirements matrix saved: {output_file}")
        return enhanced_matrix

    def generate_gap_description(self, row):
        """Generate gap description based on compliance status"""
        status = row["compliance_status"]
        confidence = row["combined_score"] * 100  # Convert to percentage

        if status == "Compliant":
            return "No gap identified - requirement appears to be met"
        elif status == "Partial":
            return f"Partial compliance - review document for completeness (confidence: {confidence:.1f}%)"
        elif status == "Review Required":
            return f"Low confidence match - manual review required (confidence: {confidence:.1f}%)"
        else:
            return (
                "No compliant document identified - new documentation may be required"
            )

    def assess_risk_level(self, row):
        """Assess audit risk level based on compliance status and clause importance"""
        status = row["compliance_status"]

        if status == "Non-Compliant":
            return "Critical"
        elif status == "Review Required":
            return "High"
        elif status == "Partial":
            return "Medium"
        else:
            return "Low"

    def generate_action_required(self, row):
        """Generate specific action based on gap analysis"""
        status = row["compliance_status"]
        doc_name = row["document_name"]

        if status == "Compliant":
            return "Validate document adequately addresses requirement"
        elif status == "Partial":
            return f"Review and enhance {doc_name} to fully address requirement"
        elif status == "Review Required":
            return f"Manual review of {doc_name} - verify compliance or identify alternative evidence"
        else:
            return "Create new document or procedure to address requirement"

    def estimate_effort(self, row):
        """Estimate effort required based on action type"""
        status = row["compliance_status"]

        effort_map = {
            "Compliant": "2 hours",
            "Partial": "1 day",
            "Review Required": "4 hours",
            "Non-Compliant": "1-2 weeks",
        }

        return effort_map.get(status, "TBD")

    def calculate_priority(self, row):
        """Calculate priority based on risk and effort"""
        status = row["compliance_status"]

        priority_map = {
            "Non-Compliant": 1,
            "Review Required": 2,
            "Partial": 3,
            "Compliant": 4,
        }

        return priority_map.get(status, 5)

    def generate_summary_statistics(self, enhanced_matrix):
        """Generate summary dashboard statistics"""
        total_requirements = len(enhanced_matrix)

        status_counts = enhanced_matrix["Compliance_Status"].value_counts()

        summary = pd.DataFrame(
            {
                "Metric": [
                    "Total Requirements",
                    "Compliant",
                    "Partial Compliance",
                    "Review Required",
                    "Non-Compliant",
                    "Compliance Percentage",
                    "Average Confidence Score",
                ],
                "Value": [
                    total_requirements,
                    status_counts.get("Compliant", 0),
                    status_counts.get("Partial", 0),
                    status_counts.get("Review Required", 0),
                    status_counts.get("Non-Compliant", 0),
                    f"{((status_counts.get('Compliant', 0) / total_requirements) * 100):.1f}%",
                    f"{enhanced_matrix['Confidence_Score'].mean():.1f}%",
                ],
            }
        )

        return summary

    def run_complete_analysis(self):
        """Run the complete gap analysis workflow"""
        print("Enhanced NADCAP Gap Analysis - Complete Workflow")
        print("=" * 60)

        # Load data
        self.load_nadcap_requirements()
        self.load_sf_inventory()

        # Run analysis
        self.run_gap_analysis()

        # Generate outputs
        enhanced_matrix = self.generate_enhanced_requirements_matrix()

        print("\n" + "=" * 60)
        print("Analysis Complete!")
        print(f"Results saved to: {self.outputs_folder}")

        return enhanced_matrix


def main():
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    inputs_folder = os.path.join(script_dir, "Inputs")
    outputs_folder = os.path.join(script_dir, "outputs")

    # Create analyzer and run analysis
    analyzer = EnhancedNADCAPGapAnalyzer(inputs_folder, outputs_folder)
    results = analyzer.run_complete_analysis()

    if results is not None:
        print(f"\nSummary:")
        print(f"- Total Requirements Analyzed: {len(results)}")
        print(
            f"- Compliant: {len(results[results['Compliance_Status'] == 'Compliant'])}"
        )
        print(
            f"- Partial: {len(results[results['Compliance_Status'] == 'Partial'])}")
        print(
            f"- Review Required: {len(results[results['Compliance_Status'] == 'Review Required'])}"
        )
        print(
            f"- Non-Compliant: {len(results[results['Compliance_Status'] == 'Non-Compliant'])}"
        )


if __name__ == "__main__":
    main()
