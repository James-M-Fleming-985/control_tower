#!/usr/bin/env python3
"""
Debug script to see the raw text around clause 3.6.1
"""
import pdfplumber
import re

# Extract text from PDF
with pdfplumber.open('NADCAP Audit Requirements.pdf') as pdf:
    full_text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"

# Find text around clause 3.6.1
lines = full_text.split('\n')

print("🔍 Looking for clause 3.6.1 context...")
print("=" * 60)

for i, line in enumerate(lines):
    if '3.6.1' in line and not '3.6.1.' in line:  # Find the main 3.6.1 section
        print(f"Found 3.6.1 at line {i}: {line}")
        print("\nContext (20 lines):")
        print("-" * 40)
        
        # Show context around this line
        start = max(0, i - 5)
        end = min(len(lines), i + 15)
        
        for j in range(start, end):
            marker = ">>> " if j == i else "    "
            print(f"{marker}{j:3d}: {lines[j]}")
        
        break

# Also look for any YES NO patterns
print("\n\n🔍 Looking for YES NO patterns...")
print("=" * 60)

for i, line in enumerate(lines):
    if re.search(r'YES\s+NO', line, re.IGNORECASE):
        print(f"Line {i}: {line}")
        # Show a bit of context
        if i > 0:
            print(f"   {i-1}: {lines[i-1]}")
        if i < len(lines) - 1:
            print(f"   {i+1}: {lines[i+1]}")
        print()
        
        if i > 100:  # Limit output
            break
