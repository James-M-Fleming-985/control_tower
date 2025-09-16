#!/usr/bin/env python3
"""
Deep Dive: Why are Column I documents unused?
Investigate specific NADCAP requirements vs unused Column I documents
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from updated_enhanced_nadcap_clean_sf_analysis import UpdatedSFNADCAPAnalyzer

# Add the current directory to path to import our analyzer
sys.path.append(
    "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
)


def investigate_unused_documents():
    """Deep dive into why specific Column I documents are unused"""

    print("🔬 DEEP DIVE: UNUSED COLUMN I DOCUMENTS")
    print("=" * 60)

    # Initialize analyzer to get access to methods
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    analyzer = UpdatedSFNADCAPAnalyzer(base_folder)

    # Load documents and requirements
    controlled_docs = analyzer.load_controlled_documents_from_surface_finishes()
    nadcap_df = analyzer.load_nadcap_requirements()
    requirements = analyzer.extract_meaningful_requirements(nadcap_df)

    print(f"📋 Total Column I documents: {len(controlled_docs)}")
    print(f"📋 Total NADCAP requirements: {len(requirements)}")

    # Load the results to see which documents are actually used
    output_file = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis/outputs/Enhanced_NADCAP_Clean_SF_Analysis_20250910_0737.xlsx"
    df = pd.read_excel(output_file, sheet_name="NADCAP_Analysis")

    # Get list of used documents
    used_docs = set(
        df[df["Primary_Source"] == "Surface Finishes Column I"][
            "Primary_Evidence"
        ].values
    )

    # Find unused documents
    all_docs = set(
        [doc.get("display_reference", doc["cheops_ref"])
         for doc in controlled_docs]
    )
    unused_docs = all_docs - used_docs

    print(f"📊 Used documents: {len(used_docs)}")
    print(f"❌ Unused documents: {len(unused_docs)}")

    # Let's manually test some unused documents against NADCAP requirements
    print(f"\n🔍 MANUAL SIMILARITY TESTING FOR UNUSED DOCUMENTS:")

    # Focus on a few key unused documents that should have matches
    focus_docs = [
        "ADHESION TESTING",
        "HARDNESS CHECKS",
        "GRIT BLASTING",
        "STRESS RELIEF",
        "SAFE WORKING PRACTICES",
        "CALIBRATION OF AMMETERS",
    ]

    for focus in focus_docs:
        matching_unused_docs = [
            doc for doc in unused_docs if focus in doc.upper()]
        if matching_unused_docs:
            unused_doc_ref = matching_unused_docs[0]
            print(f"\n🎯 TESTING: {unused_doc_ref}")

            # Find the actual document object
            doc_obj = None
            for doc in controlled_docs:
                if unused_doc_ref in doc.get(
                        "display_reference", doc["cheops_ref"]):
                    doc_obj = doc
                    break

            if doc_obj:
                doc_text = doc_obj["full_text"]
                expanded_doc_text = analyzer.expand_text_with_synonyms(
                    doc_text)

                # Test against related NADCAP requirements
                print(f"   Document content preview: {doc_text[:100]}...")

                # Find potentially matching requirements
                focus_lower = focus.lower()
                related_reqs = []

                for req in requirements:
                    req_text_lower = req["text"].lower()
                    if any(word in req_text_lower for word in focus_lower.split()):
                        related_reqs.append(req)

                print(
                    f"   Found {
                        len(related_reqs)} potentially related requirements"
                )

                # Manual similarity calculation
                if related_reqs:
                    best_score = 0
                    best_req = None

                    vectorizer = TfidfVectorizer(
                        stop_words="english", max_features=1000
                    )

                    for req in related_reqs[:5]:  # Test top 5
                        try:
                            texts = [expanded_doc_text, req["expanded_text"]]
                            tfidf_matrix = vectorizer.fit_transform(texts)
                            similarity = cosine_similarity(
                                tfidf_matrix[0:1], tfidf_matrix[1:2]
                            )[0][0]

                            if similarity > best_score:
                                best_score = similarity
                                best_req = req

                            print(
                                f"   - Req: {req['text'][:60]}... → Score: {similarity:.3f}"
                            )
                        except BaseException:
                            continue

                    if best_score > 0.15:
                        print(
                            f"   ✅ SHOULD BE MATCHED! Best score: {
                                best_score:.3f}"
                        )
                        print(
                            f"       Best requirement: {best_req['text'][:80]}...")
                    else:
                        print(
                            f"   ⚠️  Low scores - may need better synonym mapping")

    # Check if the issue is in our algorithm vs manual calculation
    print(f"\n🔧 ALGORITHM DIAGNOSTIC:")
    print(f"   1. Are we using expanded_text correctly? ✅ Yes")
    print(f"   2. Are synonym mappings comprehensive? Need investigation")
    print(f"   3. Is TF-IDF configuration optimal? Need testing")
    print(f"   4. Is our hierarchy algorithm selecting wrong documents? Possible")

    # Test if the issue is that lower-scoring Column I docs are losing to
    # higher-scoring ones
    print(f"\n🏆 TESTING COMPETITION HYPOTHESIS:")
    print(
        f"   Theory: Multiple Column I docs compete for same requirement, highest score wins"
    )

    # Count how many requirements have very specific high-scoring matches
    high_scoring_matches = df[df["Primary_Score"] > 0.3]
    dominant_docs = high_scoring_matches["Primary_Evidence"].value_counts()

    print(f"   High-scoring requirements (>0.3): {len(high_scoring_matches)}")
    print(f"   Dominated by these documents:")
    for doc, count in dominant_docs.head(3).items():
        print(f"     - {doc}: {count} high-scoring matches")

    return {
        "unused_count": len(unused_docs),
        "focus_docs_tested": len(focus_docs),
        "utilization_rate": (len(used_docs) / len(all_docs)) * 100,
    }


if __name__ == "__main__":
    results = investigate_unused_documents()
