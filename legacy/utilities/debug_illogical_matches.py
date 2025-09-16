#!/usr/bin/env python3
"""
Debug Illogical Matching Issue
Investigate why "drawing/sketch" matches to "stress relief" document
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


def debug_illogical_matches():
    """Debug why we're getting nonsensical matches"""

    print("🔧 DEBUGGING ILLOGICAL MATCHING ISSUE")
    print("=" * 60)

    # Load the latest results
    output_file = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis/outputs/Enhanced_NADCAP_Clean_SF_Analysis_20250910_0906.xlsx"

    df = pd.read_excel(output_file, sheet_name="NADCAP_Analysis")

    # Find the specific problematic matches
    print("🔍 EXAMINING PROBLEMATIC MATCHES:")

    # Match 1: Drawing/sketch → Stress Relief
    drawing_reqs = df[
        df["Content"].str.contains(
            "drawing.*sketch|sketch.*drawing", case=False, na=False
        )
    ]
    if not drawing_reqs.empty:
        print(f"\n1️⃣ DRAWING/SKETCH REQUIREMENTS:")
        for idx, row in drawing_reqs.iterrows():
            print(f"   Requirement: {row['Content'][:80]}...")
            print(f"   Primary Evidence: {row['Primary_Evidence']}")
            print(f"   Score: {row['Primary_Score']}")
            print(
                f"   ❌ LOGICAL? No way 'stress relief' relates to 'drawing/sketch'!")
            print()

    # Match 2: Upload documents → Calibration
    upload_reqs = df[
        df["Content"].str.contains(
            "upload.*documents|documents.*upload", case=False, na=False
        )
    ]
    if not upload_reqs.empty:
        print(f"2️⃣ DOCUMENT UPLOAD REQUIREMENTS:")
        for idx, row in upload_reqs.iterrows():
            print(f"   Requirement: {row['Content'][:80]}...")
            print(f"   Primary Evidence: {row['Primary_Evidence']}")
            print(f"   Score: {row['Primary_Score']}")
            print(
                f"   ❌ LOGICAL? No way 'calibration' relates to 'uploading documents'!"
            )
            print()

    # Initialize analyzer to investigate the matching process
    base_folder = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/3_ZnNi_Line_Post_Stabilization_Optimization/SF_Documentation_Inc_Training_Optimization/NADCAP Analysis"
    analyzer = UpdatedSFNADCAPAnalyzer(base_folder)

    # Load documents and requirements to analyze the texts
    controlled_docs = analyzer.load_controlled_documents_from_surface_finishes()
    nadcap_df = analyzer.load_nadcap_requirements()
    requirements = analyzer.extract_meaningful_requirements(nadcap_df)

    print(f"\n🔬 ROOT CAUSE ANALYSIS:")

    # Find the stress relief document
    stress_relief_doc = None
    for doc in controlled_docs:
        if "STRESS RELIEF" in doc.get("display_reference", doc["cheops_ref"]):
            stress_relief_doc = doc
            break

    if stress_relief_doc:
        print(f"\n📄 STRESS RELIEF DOCUMENT CONTENT:")
        content = stress_relief_doc["full_text"]
        print(f"   Content preview: {content[:200]}...")

        # Check if it contains any drawing/sketch related terms
        sketch_terms = [
            "drawing",
            "sketch",
            "diagram",
            "layout",
            "map",
            "plan"]
        found_terms = [
            term for term in sketch_terms if term.lower() in content.lower()]

        if found_terms:
            print(f"   🔍 Found sketch-related terms: {found_terms}")
            print(f"   💡 This might explain the weak connection")
        else:
            print(f"   ❌ NO sketch-related terms found!")
            print(f"   🚨 This is a completely illogical match!")

    # Test manual similarity calculation
    print(f"\n🧮 MANUAL SIMILARITY TEST:")

    # Find the drawing requirement
    drawing_req = None
    for req in requirements:
        if "drawing" in req["text"].lower(
        ) and "sketch" in req["text"].lower():
            drawing_req = req
            break

    if drawing_req and stress_relief_doc:
        print(f"   Requirement: {drawing_req['text'][:100]}...")
        print(f"   Expanded: {drawing_req['expanded_text'][:150]}...")
        print(f"   Document: {stress_relief_doc['full_text'][:150]}...")

        # Manual TF-IDF test
        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        texts = [drawing_req["expanded_text"], stress_relief_doc["full_text"]]

        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity = cosine_similarity(
                tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            print(f"   Manual similarity score: {similarity:.4f}")

            # Show what terms are creating the similarity
            feature_names = vectorizer.get_feature_names_out()
            req_vector = tfidf_matrix[0].toarray()[0]
            doc_vector = tfidf_matrix[1].toarray()[0]

            # Find common terms
            common_scores = []
            for i, (req_score, doc_score) in enumerate(
                    zip(req_vector, doc_vector)):
                if req_score > 0 and doc_score > 0:
                    common_scores.append(
                        (feature_names[i], req_score * doc_score))

            common_scores.sort(key=lambda x: x[1], reverse=True)

            if common_scores:
                print(f"   Common terms creating similarity:")
                for term, score in common_scores[:5]:
                    print(f"     - '{term}': {score:.4f}")

        except Exception as e:
            print(f"   Error in manual calculation: {e}")

    print(f"\n🚨 FUNDAMENTAL PROBLEMS IDENTIFIED:")
    print(
        f"   1. Algorithm forces ALL documents to be used, even with nonsensical matches"
    )
    print(f"   2. Low similarity thresholds (0.05) allow completely unrelated matches")
    print(f"   3. TF-IDF may be finding spurious common words")
    print(f"   4. 'Comprehensive allocation' sacrifices logic for coverage")

    print(f"\n💡 SOLUTIONS NEEDED:")
    print(f"   1. Implement minimum logical relevance checks")
    print(f"   2. Allow documents to remain unmatched if no logical connection")
    print(f"   3. Add semantic validation beyond TF-IDF scores")
    print(f"   4. Prioritize logical matching over 100% document utilization")


if __name__ == "__main__":
    debug_illogical_matches()
