#!/usr/bin/env python3
"""
NADCAP Audit Requirements PDF Text Extraction Script
Extracts and processes PDF content for analysis and summarization
"""

import sys
import os
try:
    import pdfplumber
except ImportError:
    print("pdfplumber not found. Installing...")
    os.system("pip install pdfplumber")
    import pdfplumber

def extract_pdf_text(pdf_path, output_path):
    """
    Extract text from PDF and save to text file
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = []
            
            print(f"Processing PDF: {pdf_path}")
            print(f"Total pages: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"Processing page {page_num}...")
                text = page.extract_text()
                if text:
                    full_text.append(f"\n--- PAGE {page_num} ---\n")
                    full_text.append(text)
                    full_text.append("\n")
            
            # Save extracted text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(''.join(full_text))
            
            print(f"Text extraction complete!")
            print(f"Output saved to: {output_path}")
            print(f"Total characters extracted: {len(''.join(full_text))}")
            
            return True
            
    except Exception as e:
        print(f"Error extracting PDF: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_nadcap_pdf.py <pdf_file_path>")
        print("Example: python extract_nadcap_pdf.py NADCAP_Requirements.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Create output filename
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = f"{base_name}_extracted_text.txt"
    
    print("NADCAP Audit Requirements PDF Extraction")
    print("=" * 50)
    
    success = extract_pdf_text(pdf_path, output_path)
    
    if success:
        print("\nExtraction successful!")
        print(f"Next steps:")
        print(f"1. Review the extracted text file: {output_path}")
        print(f"2. The text file can now be analyzed for key requirements")
        print(f"3. Use the extracted content for compliance analysis")
    else:
        print("\nExtraction failed. Please check the PDF file and try again.")

if __name__ == "__main__":
    main()
