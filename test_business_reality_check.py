#!/usr/bin/env python3
"""
Business Logic Layer Reality Check
Quick test to see what business problems still exist in the implementation
"""

import tempfile
import os
from pathlib import Path
from src.business_logic.test_generation_verification_logic import (
    TestGenerationVerifier,
    StageGateEnforcer, 
    TDDComplianceAssessor,
    TestQualityScorer
)

def test_real_business_problems():
    """Test what actual business problems still exist"""
    print("🔍 TESTING REAL BUSINESS PROBLEMS...")
    print("")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Test directory: {temp_dir}")
        
        # TEST 1: Empty directory (no test files)
        print("\n1️⃣ TESTING: Empty directory verification")
        verifier = TestGenerationVerifier(temp_dir)
        
        verification_request = {
            "requirement_id": "TEST_REQ_001",
            "test_directory": temp_dir,
            "expected_test_count": 1,
            "verification_level": "REAL"
        }
        
        result = verifier.verify_test_generation(verification_request)
        print(f"   ✅ Verified: {result.verified}")
        print(f"   📋 Blocking issues: {result.blocking_issues}")
        print(f"   ⭐ Quality score: {result.quality_score}")
        
        if result.verified:
            print("   ❌ BUSINESS PROBLEM: False positive - no tests exist but verification passed!")
        else:
            print("   ✅ WORKING: Correctly detected missing tests")
        
        # TEST 2: Stage gate validation
        print("\n2️⃣ TESTING: Stage gate enforcement")
        enforcer = StageGateEnforcer(temp_dir)
        
        stage_request = {
            "stage_name": "RED_TO_GREEN",
            "requirement_id": "TEST_REQ_001",
            "evidence_required": True,
            "blocking_enabled": True,
            "validation_criteria": {
                "min_test_count": 1,
                "min_coverage": 75.0,
                "real_verification": True
            }
        }
        
        stage_result = enforcer.validate_stage_gate(stage_request)
        print(f"   🚦 Stage status: {stage_result['validation_status']}")
        print(f"   🚫 Can proceed: {stage_result['can_proceed']}")
        print(f"   📋 Blocking reasons: {stage_result['blocking_reasons']}")
        
        if stage_result['can_proceed']:
            print("   ❌ BUSINESS PROBLEM: Stage gate not blocking with no tests!")
        else:
            print("   ✅ WORKING: Stage gate correctly blocking")
        
        # TEST 3: Create a fake test file and test again
        print("\n3️⃣ TESTING: Fake test file detection")
        fake_test = Path(temp_dir) / "test_fake.py"
        fake_test.write_text("# This is not a real test file")
        
        result2 = verifier.verify_test_generation(verification_request)
        print(f"   ✅ Verified with fake file: {result2.verified}")
        print(f"   📋 Blocking issues: {result2.blocking_issues}")
        
        if result2.verified:
            print("   ❌ BUSINESS PROBLEM: Accepting fake test files!")
        else:
            print("   ✅ WORKING: Rejecting fake test files")
        
        # TEST 4: Real test file
        print("\n4️⃣ TESTING: Real test file detection")
        real_test = Path(temp_dir) / "test_real.py"
        real_test.write_text("""
def test_something():
    assert True

def test_another():
    assert 1 + 1 == 2
""")
        
        result3 = verifier.verify_test_generation(verification_request)
        print(f"   ✅ Verified with real file: {result3.verified}")
        print(f"   📋 Blocking issues: {result3.blocking_issues}")
        print(f"   ⭐ Quality score: {result3.quality_score}")
        
        if not result3.verified:
            print("   ❌ BUSINESS PROBLEM: Rejecting valid test files!")
        else:
            print("   ✅ WORKING: Accepting valid test files")

if __name__ == "__main__":
    test_real_business_problems()