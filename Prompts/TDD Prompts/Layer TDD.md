Prompt 1

MANDATORY EXECUTION ORDER:
1. [Specific action with measurable outcome]
2. [Next specific action with measurable outcome]  
3. [Verification step with clear success criteria]

COMPLETION CRITERIA:
- [ ] Specific deliverable 1 exists
- [ ] Specific deliverable 2 passes test X
- [ ] All N items are processed (no exceptions)

BLOCKING RULES:
- Do NOT proceed to step 2 until step 1 is 100% complete
- Do NOT summarize or explain - EXECUTE
- Do NOT make assumptions - ask if unclear

Prompt 2

MANDATORY EXECUTION ORDER:
1. Run: python tools/exhaustive_requirements_parser.py
2. Verify: Check that tests/failing_tests/ contains exactly N test files (one per requirement)
3. Run: pytest tests/failing_tests/ -v --tb=short
4. Confirm: All tests FAIL with expected error messages

COMPLETION CRITERIA:
- [ ] tests/failing_tests/test_fr_001_failing_tests.py exists and runs
- [ ] tests/failing_tests/test_fr_002_failing_tests.py exists and runs  
- [ ] tests/failing_tests/test_fr_003_failing_tests.py exists and runs
- [ ] tests/failing_tests/test_fr_004_failing_tests.py exists and runs
- [ ] All 4 test files contain failing tests that produce AttributeError
- [ ] Pytest shows X/X tests FAILED (RED phase confirmed)

BLOCKING RULES:
- Do NOT proceed until ALL test files exist
- Do NOT move to GREEN phase until ALL tests fail
- Do NOT explain what you're doing - just execute and report results