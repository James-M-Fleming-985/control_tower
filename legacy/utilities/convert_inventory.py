#!/usr/bin/env python3
"""
Document Inventory Converter
Converts your actual SF document inventory format to the analysis format
"""

import pandas as pd
import argparse
from datetime import datetime

def convert_inventory(input_file, output_file, sheet_name=None):
    """Convert your inventory format to analysis format"""
    print(f"🔄 Converting inventory format...")
    
    try:
        # Read your actual inventory - handle Excel files
        if input_file.endswith('.xlsx') or input_file.endswith('.xls'):
            if sheet_name:
                df = pd.read_excel(input_file, sheet_name=sheet_name)
                print(f"📊 Loaded {len(df)} documents from sheet '{sheet_name}'")
            else:
                # Try to read all sheets and show available ones
                excel_file = pd.ExcelFile(input_file)
                print(f"📋 Available sheets: {excel_file.sheet_names}")
                # Use first sheet as default
                df = pd.read_excel(input_file, sheet_name=0)
                print(f"📊 Using first sheet with {len(df)} documents")
        else:
            df = pd.read_csv(input_file)
            print(f"📊 Loaded {len(df)} documents from CSV")
        
        print("📋 Available columns in your file:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        # Map your columns to analysis format using corrected headers
        converted_df = pd.DataFrame()
        
        # Map the columns using your actual headers
        converted_df['Document_Name'] = df.get('Title', 'Unknown Title')
        converted_df['File_Path'] = df.get('Source System Reference', 'Unknown Path')
        converted_df['Document_Type'] = df.get('Document Category', 'Unknown Type')
        converted_df['Last_Modified'] = df.get('Application date (date moved to Applicable)', 'Unknown Date')
        converted_df['Owner'] = df.get('Author', df.get('Approver (resp person)', 'Unknown Owner'))
        converted_df['Status'] = df.get('Status', 'Unknown Status')
        
        # Create comprehensive description from multiple fields
        description_parts = []
        if 'Leading Process' in df.columns and not df['Leading Process'].isna().all():
            description_parts.append('Process: ' + df['Leading Process'].fillna('').astype(str))
        if 'Department' in df.columns and not df['Department'].isna().all():
            description_parts.append('Dept: ' + df['Department'].fillna('').astype(str))
        if 'Notes' in df.columns and not df['Notes'].isna().all():
            description_parts.append('Notes: ' + df['Notes'].fillna('').astype(str))
        if 'Comments' in df.columns and not df['Comments'].isna().all():
            description_parts.append('Comments: ' + df['Comments'].fillna('').astype(str))
        
        if description_parts:
            converted_df['Description'] = description_parts[0]  # Take first non-empty description
            for part in description_parts[1:]:
                converted_df['Description'] = converted_df['Description'] + ' | ' + part
        else:
            converted_df['Description'] = 'No description available'
        
        # Add additional useful fields from your data for reference
        converted_df['OSR_Ref'] = df.get('OSR Ref', '')
        converted_df['CHEOPS_Ref'] = df.get('CHEOPS Ref', '')
        converted_df['Revision'] = df.get('Revision', '')
        converted_df['Next_Review_Due'] = df.get('Next Review Due', '')
        converted_df['BPM'] = df.get('BPM (to sign PCD in OSR)', '')
        converted_df['Checker'] = df.get('Checker', '')
        converted_df['Confirmed_With_Dept'] = df.get('Confirmed with dept?', '')
        
        # Clean up any NaN values
        converted_df = converted_df.fillna('')
        
        # Filter for SF-relevant documents
        print("🔍 Searching for Surface Finishing relevant documents...")
        sf_keywords = ['SF', 'Surface', 'Finishing', 'ZnNi', 'Zinc', 'Nickel', 'Plating', 'Coating']
        
        sf_relevant = converted_df[
            converted_df['Document_Name'].str.contains('|'.join(sf_keywords), case=False, na=False) |
            converted_df['Document_Type'].str.contains('|'.join(sf_keywords), case=False, na=False) |
            converted_df['Description'].str.contains('|'.join(sf_keywords), case=False, na=False)
        ]
        
        print(f"🎯 Found {len(sf_relevant)} SF-relevant documents out of {len(converted_df)} total")
        
        # Show sample of found documents
        if len(sf_relevant) > 0:
            print("📋 Sample SF documents found:")
            for i, row in sf_relevant.head(5).iterrows():
                print(f"  • {row['Document_Name']} ({row['Document_Type']})")
        
        # Save both full and SF-filtered versions
        converted_df.to_csv(output_file, index=False)
        sf_output = output_file.replace('.csv', '_sf_only.csv')
        sf_relevant.to_csv(sf_output, index=False)
        
        print(f"💾 Full converted inventory saved to: {output_file}")
        print(f"💾 SF-only version saved to: {sf_output}")
        print(f"📊 Recommended: Use {sf_output} for focused SF analysis")
        
        return output_file, sf_output
        
    except Exception as e:
        print(f"❌ Error converting inventory: {e}")
        print("\n🔍 Debugging info:")
        try:
            if input_file.endswith('.xlsx') or input_file.endswith('.xls'):
                excel_file = pd.ExcelFile(input_file)
                print(f"Available sheets: {excel_file.sheet_names}")
                if sheet_name:
                    df = pd.read_excel(input_file, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(input_file, sheet_name=0)
            else:
                df = pd.read_csv(input_file)
            print("Available columns:")
            for i, col in enumerate(df.columns):
                print(f"  {i+1}. {col}")
        except Exception as debug_e:
            print(f"Could not read file for debugging: {debug_e}")
        return None, None

def main():
    parser = argparse.ArgumentParser(description='Convert SF document inventory to analysis format')
    parser.add_argument('--input', required=True, help='Path to your actual document inventory CSV or Excel file')
    parser.add_argument('--sheet', help='Excel sheet name (if Excel file with multiple sheets)')
    parser.add_argument('--output', default='sf_document_inventory.csv', help='Output filename')
    
    args = parser.parse_args()
    
    convert_inventory(args.input, args.output, args.sheet)

if __name__ == "__main__":
    main()
