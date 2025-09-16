#!/usr/bin/env python3
"""
Enhanced NADCAP Gap Analysis - Append Columns Version
Appends 4 analysis columns to the original NADCAP requirements file
"""

import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class NADCAPColumnAppender:
    def __init__(self):
        self.base_path = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
        self.inputs_folder = os.path.join(self.base_path, "Inputs")
        self.outputs_folder = os.path.join(self.base_path, "outputs")

        # Ensure output directory exists
        os.makedirs(self.outputs_folder, exist_ok=True)

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

    def load_sf_inventory(self):
        """Load SF documentation inventory"""
        sf_file = os.path.join(
            self.inputs_folder, "Copy of Surface Finishes and MFG 040925.xlsx"
        )
        print(f"Loading SF inventory from: {sf_file}")

        sf_df = pd.read_excel(sf_file)
        print(f"SF inventory loaded successfully. Shape: {sf_df.shape}")
        print(f"Columns: {list(sf_df.columns)}")

        # Extract documents with content (Column I = index 8 = Notes)
        documents = []
        for idx, row in sf_df.iterrows():
            title = str(row.get("Title", "")).strip()
            content = (
                str(row.iloc[8]).strip() if len(row) > 8 else ""
            )  # Column I (Notes)
            cheops_ref = (
                str(row.iloc[2]).strip() if len(row) > 2 else ""
            )  # Column C (CHEOPS Ref)

            # Include ALL documents with meaningful titles (not just those with
            # Column I content)
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
                    }
                )

        print(f"Found {len(documents)} documents with searchable content")
        # Count content sources
        title_only = sum(
            1 for doc in documents if doc["content_source"] == "Title Only"
        )
        title_content = sum(
            1 for doc in documents if doc["content_source"] == "Title + Content"
        )
        print(f"  - Title Only: {title_only}")
        print(f"  - Title + Content: {title_content}")
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

        # Prepare texts for vectorization
        req_texts = [req["enriched_text"] for req in requirements]
        doc_texts = [doc["full_text"] for doc in documents]
        all_texts = req_texts + doc_texts

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
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
                    "document_title": documents[best_doc_idx]["title"],
                    "cheops_ref": documents[best_doc_idx]["cheops_ref"],
                    "similarity_score": best_score,
                }
            )

        return best_matches

    def generate_compliance_status(self, similarity_score):
        """Generate compliance status based on similarity score"""
        if similarity_score >= 0.7:
            return "Compliant"
        elif similarity_score >= 0.4:
            return "Partial"
        elif similarity_score >= 0.2:
            return "Review Required"
        else:
            return "Non-Compliant"

    def generate_primary_evidence(self, best_match):
        """Generate primary evidence with CHEOPS reference"""
        if best_match["similarity_score"] >= 0.2:
            cheops = best_match["cheops_ref"]
            title = best_match["document_title"]
            if cheops:
                return f"{cheops} - {title}"
            else:
                return title
        else:
            return "No match found"

    def generate_action_required(self, requirement, best_match):
        """Generate action required based on compliance status"""
        score = best_match["similarity_score"]

        if score >= 0.7:
            return "Verify compliance documentation"
        elif score >= 0.4:
            return "Review and enhance existing documentation"
        elif score >= 0.2:
            return "Manual review required - low confidence match"
        else:
            return "Create new documentation to address requirement"

    def generate_gap_description(self, requirement, best_match):
        """Generate gap description"""
        score = best_match["similarity_score"]
        confidence = score * 100

        if score >= 0.7:
            return f"Strong match found (confidence: {confidence:.1f}%) - verify completeness"
        elif score >= 0.4:
            return f"Partial match (confidence: {confidence:.1f}%) - may need additional documentation"
        elif score >= 0.2:
            return f"Weak match (confidence: {
                confidence:.1f}%) - manual review required"
        else:
            return f"No suitable documentation found (confidence: {confidence:.1f}%)"

    def append_analysis_columns(self, nadcap_df, requirements, best_matches):
        """Append the 4 analysis columns to the original NADCAP DataFrame"""
        print("Appending analysis columns to NADCAP requirements...")

        # Create a copy of the original DataFrame
        enhanced_df = nadcap_df.copy()

        # Initialize new columns
        enhanced_df["Compliance_Status"] = "Non-Compliant"
        enhanced_df["Primary_Evidence"] = "No match found"
        enhanced_df["Action_Required"] = "Review requirement"
        enhanced_df["Gap_Description"] = "No supporting documentation identified"

        # Update rows with analysis results
        for i, (req, match) in enumerate(zip(requirements, best_matches)):
            if i < len(enhanced_df):
                enhanced_df.loc[i, "Compliance_Status"] = (
                    self.generate_compliance_status(match["similarity_score"])
                )
                enhanced_df.loc[i, "Primary_Evidence"] = self.generate_primary_evidence(
                    match
                )
                enhanced_df.loc[i, "Action_Required"] = self.generate_action_required(
                    req, match
                )
                enhanced_df.loc[i, "Gap_Description"] = self.generate_gap_description(
                    req, match
                )

        return enhanced_df

    def run_analysis(self):
        """Run the complete analysis and append columns"""
        print("Enhanced NADCAP Gap Analysis - Column Appender")
        print("=" * 60)

        # Load data
        nadcap_df = self.load_nadcap_requirements()
        documents = self.load_sf_inventory()
        requirements = self.extract_requirements(nadcap_df)

        # Calculate similarities
        similarity_matrix = self.calculate_similarity_scores(
            requirements, documents)
        best_matches = self.find_best_matches(
            requirements, documents, similarity_matrix
        )

        # Append analysis columns
        enhanced_df = self.append_analysis_columns(
            nadcap_df, requirements, best_matches
        )

        # Save enhanced file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(
            self.outputs_folder, f"NADCAP_Requirements_Enhanced_{timestamp}.xlsx"
        )
        enhanced_df.to_excel(output_file, index=False)

        print(f"\nEnhanced NADCAP file saved: {output_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("Analysis Complete!")
        print(f"Results saved to: {output_file}")
        print(f"\nSummary:")
        print(f"- Total Requirements Analyzed: {len(requirements)}")

        # Count compliance statuses
        status_counts = enhanced_df["Compliance_Status"].value_counts()
        for status, count in status_counts.items():
            print(f"- {status}: {count}")

        return enhanced_df


def main():
    """Main execution function"""
    analyzer = NADCAPColumnAppender()
    result = analyzer.run_analysis()
    return result


if __name__ == "__main__":
    main()
