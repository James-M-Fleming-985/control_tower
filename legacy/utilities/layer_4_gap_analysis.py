#!/usr/bin/env python3
"""
LAYER 4: GAP ANALYSIS GENERATOR
Professional TDD Implementation

Generates enhanced NADCAP compliance reports with:
- Primary/Secondary evidence scoring
- Compliance status and match percentages
- Actionable recommendations
- Industry best practice columns appended to base NADCAP requirements

Input: Layer 3 semantic matching results (93.8% compliance)
Output: Enhanced NADCAP compliance report (Excel format)

Architecture:
- NADCAP Audit Requirements 030925.xlsx (base)
- Layer 3 semantic matcher integration
- Evidence hierarchy processing
- Compliance scoring and status generation
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


class Layer4_GapAnalysisGenerator:
    """
    Professional Gap Analysis Generator for NADCAP Compliance

    Integrates Layer 3 semantic matching with NADCAP requirements
    to generate comprehensive compliance reports with actionable insights.
    """

    def __init__(self):
        """Initialize the Gap Analysis Generator with data sources."""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.inputs_dir = os.path.join(self.base_dir, "Inputs")
        self.outputs_dir = os.path.join(self.base_dir, "outputs")

        # Ensure outputs directory exists
        os.makedirs(self.outputs_dir, exist_ok=True)

        # File paths
        self.nadcap_file = os.path.join(
            self.inputs_dir, "NADCAP Audit Requirements 030925.xlsx"
        )
        self.surface_finishes_file = os.path.join(
            self.inputs_dir, "Surface Finishes and MFG 030925.xlsx"
        )
        self.pd_forms_dir = os.path.join(self.inputs_dir, "sf_pd_forms")
        self.manps_dir = os.path.join(self.inputs_dir, "sf_manps")

        # Layer 3 semantic matcher integration
        self.semantic_matcher = None
        self._initialize_semantic_matcher()

        # Data storage
        self.nadcap_requirements = None
        self.sf_documents = None
        self.gap_analysis_results = None

    def _initialize_semantic_matcher(self):
        """Initialize Layer 3 semantic matcher for evidence scoring."""
        try:
            # Import Layer 3 framework
            sys.path.append(self.base_dir)
            from layered_tdd_framework import Layer3_SemanticMatcher

            self.semantic_matcher = Layer3_SemanticMatcher()
            print("✅ Layer 3 semantic matcher initialized (93.8% compliance)")

        except ImportError as e:
            print(f"⚠️  Layer 3 semantic matcher not available: {e}")
            self.semantic_matcher = None

    def load_nadcap_requirements(self) -> pd.DataFrame:
        """
        Load and parse NADCAP Audit Requirements 030925.xlsx
        Enhanced to combine context columns C, E, G, H for complete requirement understanding

        Returns:
            DataFrame with NADCAP requirements structure and combined context
        """
        try:
            if not os.path.exists(self.nadcap_file):
                raise FileNotFoundError(
                    f"NADCAP requirements file not found: {self.nadcap_file}"
                )

            # Load the Excel file
            excel_data = pd.ExcelFile(self.nadcap_file)
            print(f"📋 Available sheets: {excel_data.sheet_names}")

            # Use the first sheet or find the main requirements sheet
            main_sheet = excel_data.sheet_names[0]
            self.nadcap_requirements = pd.read_excel(
                self.nadcap_file, sheet_name=main_sheet
            )

            print(
                f"✅ Loaded NADCAP requirements: {
                    len(
                        self.nadcap_requirements)} rows"
            )
            print(f"📊 Columns: {list(self.nadcap_requirements.columns)}")

            # Enhanced context processing - combine columns C, E, G, H
            self.nadcap_requirements = self._enhance_nadcap_context(
                self.nadcap_requirements
            )

            return self.nadcap_requirements

        except Exception as e:
            print(f"❌ Error loading NADCAP requirements: {e}")
            return None

    def _enhance_nadcap_context(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enhance NADCAP requirements by combining context columns C, E, G, H

        Based on analysis:
        - Column C: Title (190 entries) - Main requirement titles
        - Column E: Title.1 (185 entries) - Sub-requirement titles
        - Column G: Content (current usage) - Main requirement content
        - Column H: Guidance (131 entries) - Additional guidance text

        Args:
            df: Raw NADCAP requirements DataFrame

        Returns:
            Enhanced DataFrame with combined context column
        """
        try:
            # Get column names (may vary based on Excel structure)
            cols = list(df.columns)
            print(f"🔍 Processing columns: {cols}")

            # Map to actual column names (adjust indices as needed)
            title_col = cols[2] if len(cols) > 2 else None  # Column C
            title1_col = cols[4] if len(cols) > 4 else None  # Column E
            content_col = cols[6] if len(cols) > 6 else None  # Column G
            guidance_col = cols[7] if len(cols) > 7 else None  # Column H

            # Create enhanced context by combining available columns
            enhanced_context = []
            for idx, row in df.iterrows():
                context_parts = []

                # Add Title (Column C)
                if title_col and pd.notna(row[title_col]):
                    title_text = str(row[title_col]).strip()
                    if title_text and title_text != "nan":
                        context_parts.append(f"Title: {title_text}")

                # Add Title.1 (Column E)
                if title1_col and pd.notna(row[title1_col]):
                    title1_text = str(row[title1_col]).strip()
                    if title1_text and title1_text != "nan":
                        context_parts.append(f"Subtitle: {title1_text}")

                # Add Content (Column G) - Primary content
                if content_col and pd.notna(row[content_col]):
                    content_text = str(row[content_col]).strip()
                    if content_text and content_text != "nan":
                        context_parts.append(f"Content: {content_text}")

                # Add Guidance (Column H)
                if guidance_col and pd.notna(row[guidance_col]):
                    guidance_text = str(row[guidance_col]).strip()
                    if guidance_text and guidance_text != "nan":
                        context_parts.append(f"Guidance: {guidance_text}")

                # Combine all parts
                enhanced_text = " | ".join(
                    context_parts) if context_parts else ""
                enhanced_context.append(enhanced_text)

            # Add enhanced context column
            df["enhanced_context"] = enhanced_context

            # Count non-empty enhanced contexts
            non_empty = sum(1 for ctx in enhanced_context if ctx.strip())
            print(
                f"✅ Enhanced context created: {non_empty}/{
                    len(df)} requirements with combined context"
            )

            return df

        except Exception as e:
            print(f"⚠️ Error enhancing NADCAP context: {e}")
            # Return original DataFrame if enhancement fails
            return df

    def load_sf_documents(self) -> Dict[str, List[str]]:
        """
        Load Surface Finishes documents including Column I procedures
        Enhanced to include missing Surface Finishes Column I (41 documents)

        Returns:
            Dictionary with document categories and file lists
        """
        documents = {
            "pd_forms": [],
            "manps": [],
            "column_i_procedures": [],
            "total_count": 0,
        }

        try:
            # Load PD forms
            if os.path.exists(self.pd_forms_dir):
                pd_files = [
                    f
                    for f in os.listdir(self.pd_forms_dir)
                    if f.endswith((".pdf", ".doc", ".docx", ".xlsx"))
                ]
                documents["pd_forms"] = pd_files
                print(f"📄 Found {len(pd_files)} PD forms")

            # Load MANPs
            if os.path.exists(self.manps_dir):
                manp_files = [
                    f
                    for f in os.listdir(self.manps_dir)
                    if f.endswith((".pdf", ".doc", ".docx", ".xlsx"))
                ]
                documents["manps"] = manp_files
                print(f"📋 Found {len(manp_files)} MANP documents")

            # Load Surface Finishes Column I procedures
            column_i_procedures = self._load_surface_finishes_column_i()
            documents["column_i_procedures"] = column_i_procedures
            print(f"🔧 Found {len(column_i_procedures)} Column I procedures")

            documents["total_count"] = (
                len(documents["pd_forms"])
                + len(documents["manps"])
                + len(documents["column_i_procedures"])
            )
            self.sf_documents = documents

            print(f"✅ Total SF documents loaded: {documents['total_count']}")
            return documents

        except Exception as e:
            print(f"❌ Error loading SF documents: {e}")
            return documents

    def _load_surface_finishes_column_i(self) -> List[str]:
        """
        Load Surface Finishes Column I procedures (41 documents)

        Returns:
            List of procedure descriptions from Column I
        """
        column_i_procedures = []

        try:
            # Look for Surface Finishes and MFG 030925.xlsx
            sf_excel_path = os.path.join(
                os.path.dirname(self.nadcap_file),
                "Surface Finishes and MFG 030925.xlsx",
            )

            if not os.path.exists(sf_excel_path):
                print(
                    f"⚠️ Surface Finishes Excel file not found: {sf_excel_path}")
                return column_i_procedures

            # Load the Excel file
            sf_data = pd.read_excel(sf_excel_path)
            print(f"📊 Surface Finishes Excel columns: {list(sf_data.columns)}")

            # Column I should be the 9th column (index 8)
            if len(sf_data.columns) > 8:
                column_i_name = sf_data.columns[8]  # Column I
                column_i_data = sf_data[column_i_name].dropna()

                # Convert to list of procedure descriptions
                procedures = [
                    str(proc).strip()
                    for proc in column_i_data
                    if str(proc).strip() and str(proc) != "nan"
                ]

                column_i_procedures = procedures
                print(
                    f"✅ Loaded {
                        len(column_i_procedures)} Column I procedures")

                # Show sample procedures
                if column_i_procedures:
                    print(f"📋 Sample Column I procedures:")
                    for i, proc in enumerate(column_i_procedures[:3]):
                        print(f"   {i + 1}. {proc[:60]}...")
            else:
                print(
                    f"⚠️ Surface Finishes Excel has only {
                        len(
                            sf_data.columns)} columns, Column I not found"
                )

        except Exception as e:
            print(f"❌ Error loading Surface Finishes Column I: {e}")

        return column_i_procedures

    def calculate_evidence_score(
        self,
        requirement_text: str,
        document_title: str,
        document_type: str = "documentation",
    ) -> float:
        """
        Calculate evidence score using Layer 3 semantic matching

        Args:
            requirement_text: NADCAP requirement text
            document_title: Document title/name
            document_type: Type of document (documentation, calibration, etc.)

        Returns:
            Evidence match score (0.0 - 1.0)
        """
        if self.semantic_matcher is None:
            # Fallback scoring if Layer 3 not available
            return self._fallback_evidence_scoring(
                requirement_text, document_title)

        try:
            # Use Layer 3 semantic matcher for evidence scoring
            score = self.semantic_matcher.calculate_semantic_match(
                requirement_text,
                "compliance",  # requirement category
                document_title,
                document_type,
            )

            return round(score, 3)

        except Exception as e:
            print(f"⚠️  Error in evidence scoring: {e}")
            return self._fallback_evidence_scoring(
                requirement_text, document_title)

    def _fallback_evidence_scoring(
        self, requirement_text: str, document_title: str
    ) -> float:
        """
        Fallback evidence scoring without Layer 3 semantic matcher

        Simple keyword-based matching for basic functionality
        """
        req_words = set(requirement_text.lower().split())
        doc_words = set(document_title.lower().split())

        if not req_words or not doc_words:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(req_words.intersection(doc_words))
        union = len(req_words.union(doc_words))

        return round(intersection / union if union > 0 else 0.0, 3)

    def generate_gap_analysis(self) -> pd.DataFrame:
        """
        Generate the main gap analysis report

        Combines NADCAP requirements with SF document evidence scoring

        Returns:
            Enhanced DataFrame with industry best practice columns
        """
        print("\n🔄 Generating Gap Analysis Report...")

        # Load data sources
        nadcap_df = self.load_nadcap_requirements()
        if nadcap_df is None:
            raise Exception("Failed to load NADCAP requirements")

        sf_docs = self.load_sf_documents()

        # Create enhanced gap analysis structure
        gap_analysis = nadcap_df.copy()

        # Add industry best practice columns
        gap_analysis["Primary_Evidence_Document"] = ""
        gap_analysis["Primary_Evidence_Title"] = ""
        gap_analysis["Primary_Evidence_Score"] = 0.0
        gap_analysis["Secondary_Evidence_Document"] = ""
        gap_analysis["Secondary_Evidence_Title"] = ""
        gap_analysis["Secondary_Evidence_Score"] = 0.0
        gap_analysis["Compliance_Status"] = "Outstanding"
        gap_analysis["Match_Percentage"] = 0.0
        gap_analysis["Recommendation_Action"] = ""
        gap_analysis["Analysis_Date"] = datetime.now().strftime("%Y-%m-%d")

        # Process each NADCAP requirement
        for idx, row in gap_analysis.iterrows():
            # Use enhanced context if available, fallback to Requirement column
            requirement_text = str(row.get("enhanced_context", ""))
            if not requirement_text or requirement_text == "nan":
                requirement_text = str(row.get("Requirement", ""))

            if not requirement_text or requirement_text == "nan":
                continue

            # Find best matching evidence
            primary_evidence = self._find_best_evidence(
                requirement_text, sf_docs)
            secondary_evidence = self._find_secondary_evidence(
                requirement_text, sf_docs, primary_evidence
            )

            # Update row with evidence data
            if primary_evidence:
                gap_analysis.at[idx, "Primary_Evidence_Document"] = primary_evidence[
                    "document"
                ]
                gap_analysis.at[idx, "Primary_Evidence_Title"] = primary_evidence[
                    "title"
                ]
                gap_analysis.at[idx, "Primary_Evidence_Score"] = primary_evidence[
                    "score"
                ]

            if secondary_evidence:
                gap_analysis.at[idx, "Secondary_Evidence_Document"] = (
                    secondary_evidence["document"]
                )
                gap_analysis.at[idx, "Secondary_Evidence_Title"] = secondary_evidence[
                    "title"
                ]
                gap_analysis.at[idx, "Secondary_Evidence_Score"] = secondary_evidence[
                    "score"
                ]

            # Calculate compliance status and match percentage
            compliance_data = self._calculate_compliance_status(
                primary_evidence, secondary_evidence
            )
            gap_analysis.at[idx,
                            "Compliance_Status"] = compliance_data["status"]
            gap_analysis.at[idx, "Match_Percentage"] = compliance_data[
                "match_percentage"
            ]
            gap_analysis.at[idx, "Recommendation_Action"] = compliance_data[
                "recommendation"
            ]

        self.gap_analysis_results = gap_analysis
        print(
            f"✅ Gap analysis complete: {
                len(gap_analysis)} requirements processed")

        return gap_analysis

    def _find_best_evidence(
        self, requirement_text: str, sf_docs: Dict
    ) -> Optional[Dict]:
        """Find the best matching primary evidence document including Column I procedures."""
        best_match = None
        best_score = 0.0

        # Check PD forms first (primary evidence)
        for doc_name in sf_docs["pd_forms"]:
            score = self.calculate_evidence_score(
                requirement_text, doc_name, "documentation"
            )
            if score > best_score:
                best_score = score
                best_match = {
                    "document": f"PD_{doc_name}",
                    "title": doc_name,
                    "score": score,
                    "type": "pd_form",
                }

        # Check MANPs if no good PD form match
        if best_score < 0.5:  # Threshold for considering alternative evidence
            for doc_name in sf_docs["manps"]:
                score = self.calculate_evidence_score(
                    requirement_text, doc_name, "procedures"
                )
                if score > best_score:
                    best_score = score
                    best_match = {
                        "document": f"MANP_{doc_name}",
                        "title": doc_name,
                        "score": score,
                        "type": "manp",
                    }

        # Check Column I procedures (NEW: missing data source)
        if best_score < 0.6:  # Check Column I if still not strong match
            for i, procedure in enumerate(
                    sf_docs.get("column_i_procedures", [])):
                score = self.calculate_evidence_score(
                    requirement_text, procedure, "procedures"
                )
                if score > best_score:
                    best_score = score
                    best_match = {
                        "document": f"SF_ColumnI_{i + 1}",
                        "title": (
                            procedure[:50] +
                            "..." if len(procedure) > 50 else procedure
                        ),
                        "score": score,
                        "type": "column_i_procedure",
                    }

        return best_match if best_score > 0.1 else None

    def _find_secondary_evidence(
        self, requirement_text: str, sf_docs: Dict, primary_evidence: Optional[Dict]
    ) -> Optional[Dict]:
        """Find secondary supporting evidence including Column I procedures."""
        if not primary_evidence:
            return None

        best_secondary = None
        best_score = 0.0

        # Look for supporting evidence in different categories
        if primary_evidence["type"] == "pd_form":
            # Look for supporting MANP
            for doc_name in sf_docs["manps"]:
                score = self.calculate_evidence_score(
                    requirement_text, doc_name, "procedures"
                )
                if score > best_score and score > 0.2:
                    best_score = score
                    best_secondary = {
                        "document": f"MANP_{doc_name}",
                        "title": doc_name,
                        "score": score,
                        "type": "manp",
                    }

            # Also check Column I procedures for supporting evidence
            for i, procedure in enumerate(
                    sf_docs.get("column_i_procedures", [])):
                score = self.calculate_evidence_score(
                    requirement_text, procedure, "procedures"
                )
                if score > best_score and score > 0.2:
                    best_score = score
                    best_secondary = {
                        "document": f"SF_ColumnI_{i + 1}",
                        "title": (
                            procedure[:50] +
                            "..." if len(procedure) > 50 else procedure
                        ),
                        "score": score,
                        "type": "column_i_procedure",
                    }

        elif primary_evidence["type"] == "manp":
            # Look for supporting PD form
            for doc_name in sf_docs["pd_forms"]:
                score = self.calculate_evidence_score(
                    requirement_text, doc_name, "documentation"
                )
                if score > best_score and score > 0.2:
                    best_score = score
                    best_secondary = {
                        "document": f"PD_{doc_name}",
                        "title": doc_name,
                        "score": score,
                        "type": "pd_form",
                    }

        elif primary_evidence["type"] == "column_i_procedure":
            # Look for supporting PD forms and MANPs
            for doc_name in sf_docs["pd_forms"]:
                score = self.calculate_evidence_score(
                    requirement_text, doc_name, "documentation"
                )
                if score > best_score and score > 0.2:
                    best_score = score
                    best_secondary = {
                        "document": f"PD_{doc_name}",
                        "title": doc_name,
                        "score": score,
                        "type": "pd_form",
                    }

            for doc_name in sf_docs["manps"]:
                score = self.calculate_evidence_score(
                    requirement_text, doc_name, "procedures"
                )
                if score > best_score and score > 0.2:
                    best_score = score
                    best_secondary = {
                        "document": f"MANP_{doc_name}",
                        "title": doc_name,
                        "score": score,
                        "type": "manp",
                    }

        return best_secondary

    def _calculate_compliance_status(
        self, primary: Optional[Dict], secondary: Optional[Dict]
    ) -> Dict:
        """Calculate overall compliance status and recommendations."""
        if not primary:
            return {
                "status": "Non-Compliant",
                "match_percentage": 0.0,
                "recommendation": "No matching documentation found. Create or identify appropriate evidence.",
            }

        # Calculate combined match percentage
        primary_score = primary["score"]
        secondary_score = secondary["score"] if secondary else 0.0

        # Weighted combination: primary 70%, secondary 30%
        combined_score = (primary_score * 0.7) + (secondary_score * 0.3)
        match_percentage = round(combined_score * 100, 1)

        # Determine compliance status
        if combined_score >= 0.7:
            status = "Compliant"
            recommendation = (
                "Excellent evidence coverage. Review for continuous improvement."
            )
        elif combined_score >= 0.45:  # Adjusted for 0.7 primary * 0.7 weight = 0.49
            status = "Partially Compliant"
            if secondary:
                doc_name = (
                    primary.get("document", "identified document")
                    if primary
                    else "identified document"
                )
                recommendation = f"Good evidence base. Enhance {doc_name} alignment with requirements."
            else:
                doc_name = (
                    primary.get("document", "identified document")
                    if primary
                    else "identified document"
                )
                recommendation = f"Review {doc_name} and add supporting evidence."
        elif combined_score >= 0.2:
            status = "Non-Compliant"
            doc_name = (
                primary.get("document", "identified document")
                if primary
                else "identified document"
            )
            recommendation = f"Document {doc_name} needs significant review and update to satisfy requirements."
        else:
            status = "Non-Compliant"
            recommendation = "Current documentation insufficient. Develop comprehensive evidence package."

        return {
            "status": status,
            "match_percentage": match_percentage,
            "recommendation": recommendation,
        }

    def export_gap_analysis(
            self, output_filename: Optional[str] = None) -> str:
        """
        Export gap analysis to Excel with professional formatting

        Args:
            output_filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if self.gap_analysis_results is None:
            raise Exception(
                "No gap analysis results to export. Run generate_gap_analysis() first."
            )

        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"NADCAP_Gap_Analysis_{timestamp}.xlsx"

        output_path = os.path.join(self.outputs_dir, output_filename)

        try:
            # Export to Excel with formatting
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                self.gap_analysis_results.to_excel(
                    writer, sheet_name="Gap Analysis", index=False
                )

                # Apply professional formatting
                self._format_gap_analysis_worksheet(
                    writer.sheets["Gap Analysis"])

            print(f"✅ Gap analysis exported: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error exporting gap analysis: {e}")
            raise

    def _format_gap_analysis_worksheet(self, worksheet):
        """Apply professional formatting to the gap analysis worksheet."""
        # Header formatting
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(
            start_color="366092", end_color="366092", fill_type="solid"
        )

        # Apply header formatting
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except BaseException:
                    pass

            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width


def main():
    """Main execution function for testing Layer 4 Gap Analysis Generator."""
    print("🚀 LAYER 4: GAP ANALYSIS GENERATOR")
    print("=" * 50)

    # Initialize generator
    generator = Layer4_GapAnalysisGenerator()

    # Generate gap analysis
    try:
        gap_analysis = generator.generate_gap_analysis()

        # Export results
        output_file = generator.export_gap_analysis()

        # Display summary
        print(f"\n📊 GAP ANALYSIS SUMMARY:")
        print(f"   Requirements processed: {len(gap_analysis)}")

        if "Compliance_Status" in gap_analysis.columns:
            status_counts = gap_analysis["Compliance_Status"].value_counts()
            for status, count in status_counts.items():
                print(f"   {status}: {count}")

        print(f"   Output file: {output_file}")

    except Exception as e:
        print(f"❌ Gap analysis generation failed: {e}")
        raise


if __name__ == "__main__":
    main()
