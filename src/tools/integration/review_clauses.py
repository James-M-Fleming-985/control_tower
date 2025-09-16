#!/usr/bin/env python3
"""
Quick review of extracted clauses
"""
import pandas as pd

# Read the latest file
filename = "nadcap_clauses_clean_20250827_153707.xlsx"

# Read the main sheet
df = pd.read_excel(filename, sheet_name='NADCAP_Clauses_Clean')

print("🔍 NADCAP Clauses Extracted:")
print("=" * 50)
print(f"Total clauses found: {len(df)}")
print()

for index, row in df.iterrows():
    print(f"📋 Clause {row['Clause']}:")
    print(f"   Content: {row['Clause_Content'][:100]}...")
    print(f"   Responses: {row['YES']} | {row['NO']} | {row['NA']}")
    print(f"   Guidance: {row['Guidance'][:50]}..." if pd.notna(row['Guidance']) and row['Guidance'] else "   Guidance: None")
    print()
