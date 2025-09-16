#!/usr/bin/env python3
"""
Analyze existing CSV output to identify patterns in clause detection and suggest improvements.
"""

import pandas as pd
import re
import sys
import os

def analyze_content_for_clause_patterns(content_text):
    """Analyze content text for potential clause number patterns."""
    if pd.isna(content_text) or content_text == '':
        return []
    
    # Look for various clause number patterns in the content
    patterns = [
        r'(\d+\.\d+\.\d+\.\d+\.\d+)',  # 3.6.1.5.1 (5 levels)
        r'(\d+\.\d+\.\d+\.\d+)',       # 3.7.3.1 (4 levels)
        r'(\d+\.\d+\.\d+)',            # 3.6.1 (3 levels)
        r'(\d+\.\d+)',                 # 3.6 (2 levels)
    ]
    
    found_patterns = []
    for pattern in patterns:
        matches = re.findall(pattern, str(content_text))
        for match in matches:
            # Only keep technical section numbers (3, 4, 5)
            if match.startswith(('3.', '4.', '5.')):
                found_patterns.append(match)
    
    return found_patterns

def main():
    csv_file = "../outputs/NADCAP Audit Requirements_PRODUCTION_FINAL_20250829_0829.csv"
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        return
    
    df = pd.read_csv(csv_file)
    
    print("=== NADCAP Clause Detection Analysis ===\n")
    
    # Overall statistics
    total_rows = len(df)
    with_clause_num = df[df['Clause'].notna() & (df['Clause'] != '')].shape[0]
    without_clause_num = total_rows - with_clause_num
    
    print(f"Total clauses: {total_rows}")
    print(f"With clause numbers: {with_clause_num} ({with_clause_num/total_rows*100:.1f}%)")
    print(f"Without clause numbers: {without_clause_num} ({without_clause_num/total_rows*100:.1f}%)\n")
    
    # Analyze by section
    print("=== Section Analysis ===")
    for section in sorted(df['Section'].unique()):
        section_df = df[df['Section'] == section]
        section_total = len(section_df)
        section_with_clause = section_df[section_df['Clause'].notna() & (section_df['Clause'] != '')].shape[0]
        print(f"Section {section}: {section_with_clause}/{section_total} ({section_with_clause/section_total*100:.1f}% have clause numbers)")
    
    print("\n=== Pattern Analysis in Content ===")
    
    # Look for potential clause numbers embedded in content
    pattern_found_count = 0
    missed_opportunities = []
    
    for _, row in df.iterrows():
        if pd.isna(row['Clause']) or row['Clause'] == '':
            # This row is missing a clause number, check if we can find patterns in content
            content = str(row['Content/Question']) if pd.notna(row['Content/Question']) else ""
            guidance = str(row['Guidance']) if pd.notna(row['Guidance']) else ""
            notes = str(row['Notes']) if pd.notna(row['Notes']) else ""
            
            all_text = f"{content} {guidance} {notes}"
            found_patterns = analyze_content_for_clause_patterns(all_text)
            
            if found_patterns:
                pattern_found_count += 1
                missed_opportunities.append({
                    'section': row['Section'],
                    'subsection': row['Subsection'] if pd.notna(row['Subsection']) else '',
                    'patterns': found_patterns,
                    'content': content[:100] + "..." if len(content) > 100 else content
                })
    
    print(f"Found potential clause patterns in {pattern_found_count} rows without detected clause numbers\n")
    
    # Show some examples of missed opportunities
    print("=== Missed Clause Detection Opportunities (First 10) ===")
    for i, missed in enumerate(missed_opportunities[:10], 1):
        print(f"{i}. Section {missed['section']}, Subsection: {missed['subsection']}")
        print(f"   Potential clauses: {missed['patterns']}")
        print(f"   Content: {missed['content']}")
        print()
    
    # Show successful detections for comparison
    print("=== Successfully Detected Clauses (For Pattern Comparison) ===")
    successful_clauses = df[df['Clause'].notna() & (df['Clause'] != '')]
    for i, (_, row) in enumerate(successful_clauses.head(5).iterrows(), 1):
        print(f"{i}. Clause: {row['Clause']}")
        content = str(row['Content/Question']) if pd.notna(row['Content/Question']) else ""
        print(f"   Content: {content[:100]}..." if len(content) > 100 else f"   Content: {content}")
        print()
    
    # Recommendations
    print("=== Recommendations ===")
    print("1. Section 2 appears to be administrative - consider skipping as planned")
    print("2. Sections 4 and 5 have 0% clause detection - need enhanced patterns")
    print("3. Section 3 has some success (26.7%) but can be improved")
    print(f"4. Found {pattern_found_count} potential clause numbers in content - extraction patterns need refinement")
    print("5. Consider expanding search range and improving regex patterns for embedded clause numbers")

if __name__ == "__main__":
    main()
