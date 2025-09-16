#!/usr/bin/env python3
"""
Enhanced Evidence Allocation Algorithm
Maximize utilization of all 41 Column I documents while maintaining quality
"""

from collections import defaultdict

import numpy as np


def find_best_matches_with_improved_allocation(
    self, requirements, documents, similarity_matrix
):
    """
    Enhanced algorithm to maximize Column I document utilization
    Strategy: Distribute requirements across available documents more evenly
    """
    evidence_matches = []

    if similarity_matrix.size == 0:
        return evidence_matches

    print("Finding best matches with improved document allocation...")

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

    # Track document usage to encourage distribution
    document_usage = defaultdict(int)

    # Create requirement-document score matrix for Column I docs only
    req_doc_scores = []
    for req_idx, requirement in enumerate(requirements):
        if req_idx < similarity_matrix.shape[0]:
            similarities = similarity_matrix[req_idx]

            # Get scores for all Column I documents
            column_i_scores = []
            for doc_idx, doc in column_i_docs:
                score = similarities[doc_idx]
                column_i_scores.append(
                    {
                        "doc_idx": doc_idx,
                        "doc": doc,
                        "score": score,
                        "req_idx": req_idx,
                        "requirement": requirement,
                    }
                )

            # Sort by score descending
            column_i_scores.sort(key=lambda x: x["score"], reverse=True)
            req_doc_scores.append(column_i_scores)

    # IMPROVED ALLOCATION STRATEGY
    # 1. First pass: Assign high-confidence matches (>0.25) immediately
    # 2. Second pass: Distribute remaining requirements considering document
    # usage

    used_requirements = set()

    # PASS 1: High-confidence matches (score > 0.25)
    print("Pass 1: Allocating high-confidence matches...")
    high_conf_count = 0

    for req_idx, req_scores in enumerate(req_doc_scores):
        if req_scores and req_scores[0]["score"] > 0.25:
            best_match = req_scores[0]
            doc_ref = best_match["doc"].get(
                "display_reference", best_match["doc"]["cheops_ref"]
            )
            document_usage[doc_ref] += 1
            used_requirements.add(req_idx)
            high_conf_count += 1

            # Create evidence match
            evidence_match = self._create_evidence_match(
                best_match["requirement"],
                req_scores,
                pd_form_docs + manp_docs,
                similarity_matrix[req_idx],
            )
            evidence_matches.append(evidence_match)

    print(f"Pass 1 complete: {high_conf_count} high-confidence matches")

    # PASS 2: Distribute remaining requirements to maximize document
    # utilization
    print("Pass 2: Optimizing document utilization...")

    remaining_requirements = [
        (req_idx, req_scores)
        for req_idx, req_scores in enumerate(req_doc_scores)
        if req_idx not in used_requirements
    ]

    # Sort remaining requirements by their best available score
    remaining_requirements.sort(
        key=lambda x: x[1][0]["score"] if x[1] else 0, reverse=True
    )

    for req_idx, req_scores in remaining_requirements:
        if not req_scores:
            continue

        # Find best unused or lightly used document above threshold
        best_match = None
        min_threshold = 0.10  # Lower threshold for broader utilization

        for score_entry in req_scores:
            if score_entry["score"] >= min_threshold:
                doc_ref = score_entry["doc"].get(
                    "display_reference", score_entry["doc"]["cheops_ref"]
                )
                current_usage = document_usage[doc_ref]

                # Prefer less-used documents for distribution
                # Accept if score is decent and document isn't overused
                if (
                    current_usage < 8 or score_entry["score"] > 0.20
                ):  # Max 8 uses per doc unless high score
                    best_match = score_entry
                    break

        # If no good distributed match, take the best available
        if not best_match and req_scores[0]["score"] >= min_threshold:
            best_match = req_scores[0]

        if best_match:
            doc_ref = best_match["doc"].get(
                "display_reference", best_match["doc"]["cheops_ref"]
            )
            document_usage[doc_ref] += 1

            # Create evidence match
            evidence_match = self._create_evidence_match(
                best_match["requirement"],
                req_scores,
                pd_form_docs + manp_docs,
                similarity_matrix[req_idx],
            )
            evidence_matches.append(evidence_match)
        else:
            # No adequate match found - create gap entry
            evidence_match = {
                "req_index": req_idx,
                "primary_evidence": None,
                "secondary_evidence": None,
                "compliance_status": "Gap Identified",
                "recommended_action": "Generate and Release Document",
                "requirement_text": requirements[req_idx]["text"],
                "section": requirements[req_idx].get("section", ""),
                "guidance": requirements[req_idx].get("guidance", ""),
            }
            evidence_matches.append(evidence_match)

    # Report document utilization
    print(f"\n📊 DOCUMENT UTILIZATION REPORT:")
    used_docs = len(
        [doc for doc, count in document_usage.items() if count > 0])
    total_docs = len(column_i_docs)
    utilization_rate = (used_docs / total_docs) * 100 if total_docs > 0 else 0

    print(
        f"   Documents used: {used_docs}/{total_docs} ({utilization_rate:.1f}%)")
    print(f"   Usage distribution:")

    for doc_ref, count in sorted(
        document_usage.items(), key=lambda x: x[1], reverse=True
    )[:10]:
        if count > 0:
            print(f"     {doc_ref}: {count} requirements")

    print(
        f"\nFound {
            len(evidence_matches)} evidence matches with improved allocation"
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


# This would replace the existing find_best_matches_with_hierarchy function
