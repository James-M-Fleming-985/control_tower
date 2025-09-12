#!/usr/bin/env python3
"""
Test script for NADCAP Yes/No clause extraction patterns
Creates a sample PDF-like text to test extraction logic
"""

import re

def test_yes_no_patterns():
    """Test the Yes/No pattern recognition"""
    
    # Sample text blocks that should be detected
    test_cases = [
        "1.1 Does the organization maintain documented quality procedures? Yes ☐ No ☐",
        "2.3 Are calibration records kept for all measuring equipment? Yes □ No □ NA □",
        "3.4 Is personnel training documented and current?\nYes [ ] No [ ]",
        "4.1 Are work instructions available at all workstations?\n☐ Yes ☐ No ☐ NA",
        "5.2 Does the organization have a document control system? Yes: ☐ No: ☐",
        "6.1 Are inspection records maintained for all products?\nYes: [ ] No: [ ] N/A: [ ]",
        "This is not a yes/no question - it's just informational text.",
        "7.1 Does the supplier have ISO 9001 certification? ☐ Yes ☐ No",
    ]
    
    # Patterns from the extraction script
    patterns = [
        r'(?:Yes|YES)\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:No|NO)\s*(?:☐|□|\[\s*\]|\(\s*\))',
        r'(?:Yes|YES)\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:No|NO)\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:NA|N/A)\s*(?:☐|□|\[\s*\]|\(\s*\))',
        r'☐\s*Yes\s*☐\s*No',
        r'☐\s*Yes\s*☐\s*No\s*☐\s*(?:NA|N/A)',
        r'\[\s*\]\s*Yes\s*\[\s*\]\s*No',
        r'\[\s*\]\s*Yes\s*\[\s*\]\s*No\s*\[\s*\]\s*(?:NA|N/A)',
        r'Yes:\s*(?:☐|□|\[\s*\]|\(\s*\))\s*No:\s*(?:☐|□|\[\s*\]|\(\s*\))',
        r'Yes:\s*(?:☐|□|\[\s*\]|\(\s*\))\s*No:\s*(?:☐|□|\[\s*\]|\(\s*\))\s*(?:NA|N/A):\s*(?:☐|□|\[\s*\]|\(\s*\))'
    ]
    
    print("Testing Yes/No Pattern Recognition")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Text: {test_case}")
        
        found = False
        for pattern in patterns:
            if re.search(pattern, test_case, re.IGNORECASE):
                found = True
                print(f"✅ DETECTED as Yes/No clause")
                break
        
        if not found:
            print(f"❌ NOT DETECTED")

def test_clause_extraction():
    """Test clause number extraction"""
    
    test_cases = [
        "1.1 Does the organization maintain procedures?",
        "2.3.4 Are records maintained properly?",
        "A.1 Is documentation current?",
        "B.2.1 Are personnel qualified?",
        "Clause 5.1 Does the system work?",
        "Section 3.2 Is training provided?",
        "This has no clause number",
    ]
    
    patterns = [
        r'^(\d+(?:\.\d+)*)\s',
        r'^([A-Z]\.\d+(?:\.\d+)*)\s',
        r'^(\w+\.\d+)\s',
        r'Clause\s+(\d+(?:\.\d+)*)',
        r'Section\s+(\d+(?:\.\d+)*)',
    ]
    
    print("\n\nTesting Clause Number Extraction")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Text: {test_case}")
        
        found = False
        for pattern in patterns:
            match = re.search(pattern, test_case.strip())
            if match:
                print(f"✅ EXTRACTED: {match.group(1)}")
                found = True
                break
        
        if not found:
            print(f"❌ NO CLAUSE NUMBER FOUND")

if __name__ == "__main__":
    test_yes_no_patterns()
    test_clause_extraction()
