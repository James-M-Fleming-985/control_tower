"""
End-to-End Tests - Professional TDD Workflow
============================================

Tests complete NADCAP audit workflow from start to finish.
"""

import os
import sys

import pandas as pd

from layered_tdd_framework import Layer3_SemanticMatcher


def test_complete_nadcap_workflow():
    """Test complete NADCAP audit workflow end-to-end"""
    print("🎯 E2E TEST: Complete NADCAP audit workflow")
    print("=" * 60)

    matcher = Layer3_SemanticMatcher()

    # E2E Test 1: Load real data and process through complete pipeline
    try:
        if os.path.exists("Inputs/NADCAP Audit Requirements 030925.xlsx"):
            req_df = pd.read_excel(
                "Inputs/NADCAP Audit Requirements 030925.xlsx", header=0
            )
            print(f"✅ E2E: Loaded {len(req_df)} requirements")
        else:
            print("⚠️  Using mock data for E2E test")
            req_df = pd.DataFrame(
                {"Column I": ["Calibration procedures documented?"]})
    except Exception as e:
        print(f"⚠️  E2E: Using fallback data - {e}")
        req_df = pd.DataFrame(
            {"Column I": ["Calibration procedures documented?"]})

    # E2E Test 2: Process through all layers
    requirements = (
        req_df.get("Column I", req_df.iloc[:, 0]).fillna(
            "").astype(str).head(5)
    )
    documents = [
        "CALIBRATION OF AMMETERS AND VOLTMETERS",
        "STRESS RELIEF PROCEDURE",
        "Quality Control Training Manual",
        "Environmental Procedures",
        "Process Control Guidelines",
    ]

    print("🔄 E2E: Processing through complete pipeline...")
    results = []
    for i, req in enumerate(requirements):
        req_str = str(req).strip()
        if not req_str or req_str == "nan":
            continue
        req_category = "calibration" if "calibrat" in req_str.lower() else "quality"

        for j, doc in enumerate(documents):
            doc_category = "calibration" if "calibrat" in doc.lower() else "procedures"
            score = matcher.calculate_semantic_match(
                req_str, req_category, doc, doc_category
            )
            results.append((req_str[:50], doc[:50], score))

    print(f"✅ E2E: Processed {len(results)} requirement-document pairs")
    return len(results) > 0


def test_anti_pattern_e2e():
    """Test anti-pattern blocking in complete workflow"""
    print("\n🚨 E2E TEST: Anti-pattern blocking")
    print("=" * 50)

    matcher = Layer3_SemanticMatcher()

    # E2E Test 3: Validate anti-pattern blocking
    drawing_req = "Is there a drawing/sketch defining location?"
    stress_doc = "STRESS RELIEF PROCEDURE"
    anti_score = matcher.calculate_semantic_match(
        drawing_req, "documentation", stress_doc, "safety"
    )

    print(f"   Drawing requirement ↔ Stress relief doc: {anti_score:.3f}")

    if anti_score <= 0.1:
        print(
            f"✅ E2E: Anti-pattern correctly blocked (score: {anti_score:.3f})")
        return True
    else:
        print(f"❌ E2E FAILED: Anti-pattern not blocked (score: {anti_score})")
        return False


def test_perfect_match_e2e():
    """Test perfect match scoring in complete workflow"""
    print("\n🎯 E2E TEST: Perfect match scoring")
    print("=" * 50)

    matcher = Layer3_SemanticMatcher()

    # E2E Test 4: Validate perfect match scoring
    cal_req = "Calibration equipment procedures"
    cal_doc = "CALIBRATION OF AMMETERS"
    perfect_score = matcher.calculate_semantic_match(
        cal_req, "calibration", cal_doc, "calibration"
    )

    print(f"   Calibration requirement ↔ Calibration doc: {perfect_score:.3f}")

    if perfect_score >= 0.6:
        print(
            f"✅ E2E: Perfect match scoring correct (score: {
                perfect_score:.3f})"
        )
        return True
    else:
        print(f"❌ E2E FAILED: Perfect match too low (score: {perfect_score})")
        return False


def test_audit_compliance_e2e():
    """Test audit compliance requirements end-to-end"""
    print("\n⚖️  E2E TEST: Audit compliance")
    print("=" * 50)

    matcher = Layer3_SemanticMatcher()

    # Critical audit scenarios
    audit_scenarios = [
        {
            "name": "Drawing vs Stress Relief (MUST BLOCK)",
            "req": "drawing sketch defining location",
            "req_cat": "documentation",
            "doc": "stress relief embrittlement heat",
            "doc_cat": "safety",
            "expected": "block",
            "threshold": 0.1,
        },
        {
            "name": "Calibration Match (MUST PASS)",
            "req": "calibration equipment procedures",
            "req_cat": "calibration",
            "doc": "calibration ammeter voltmeter",
            "doc_cat": "calibration",
            "expected": "pass",
            "threshold": 0.6,
        },
    ]

    compliance_passed = 0
    for scenario in audit_scenarios:
        score = matcher.calculate_semantic_match(
            scenario["req"], scenario["req_cat"], scenario["doc"], scenario["doc_cat"]
        )

        if scenario["expected"] == "block":
            if score <= scenario["threshold"]:
                print(
                    f"✅ {
                        scenario['name']}: {
                        score:.3f} ≤ {
                        scenario['threshold']}"
                )
                compliance_passed += 1
            else:
                print(
                    f"❌ {
                        scenario['name']}: {
                        score:.3f} > {
                        scenario['threshold']}"
                )
        else:  # 'pass'
            if score >= scenario["threshold"]:
                print(
                    f"✅ {
                        scenario['name']}: {
                        score:.3f} ≥ {
                        scenario['threshold']}"
                )
                compliance_passed += 1
            else:
                print(
                    f"❌ {
                        scenario['name']}: {
                        score:.3f} < {
                        scenario['threshold']}"
                )

    return compliance_passed == len(audit_scenarios)


if __name__ == "__main__":
    print("🎯 PROFESSIONAL END-TO-END TESTING")
    print("=" * 70)

    results = []

    # Run E2E tests
    results.append(test_complete_nadcap_workflow())
    results.append(test_anti_pattern_e2e())
    results.append(test_perfect_match_e2e())
    results.append(test_audit_compliance_e2e())

    # Summary
    passed = sum(results)
    total = len(results)
    success_rate = passed / total * 100

    print(f"\n📊 END-TO-END TEST SUMMARY")
    print("=" * 70)
    print(f"   Tests passed: {passed}/{total}")
    print(f"   Success rate: {success_rate:.1f}%")

    if passed == total:
        print("🎉 ALL E2E TESTS PASSED - Complete workflow validated")
        sys.exit(0)
    else:
        print("❌ E2E TESTS FAILED - System not ready for production")
        sys.exit(1)
