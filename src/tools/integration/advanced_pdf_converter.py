#!/usr/bin/env python3
"""
Advanced PDF Converter for NADCAP Compliance Document
Uses multiple methods to extract data more reliably:
1. PyMuPDF (fitz) for better text extraction
2. OCR with Tesseract for image-based text
3. PDF to Image conversion for visual analysis
4. Structured data extraction with multiple fallbacks
"""

import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import re
import sys
import os
from pathlib import Path
import json

class AdvancedPDFConverter:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.extracted_data = []
        
    def method_1_pymupdf_extraction(self):
        """Method 1: Use PyMuPDF for better text extraction"""
        print("🔍 METHOD 1: PyMuPDF Text Extraction")
        print("=" * 50)
        
        all_text_data = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            
            # Get text with layout information
            text_dict = page.get_text("dict")
            text_blocks = page.get_text("blocks")
            raw_text = page.get_text()
            
            # Store different extraction methods
            page_data = {
                'page_number': page_num + 1,
                'raw_text': raw_text,
                'text_blocks': text_blocks,
                'text_dict': text_dict
            }
            
            all_text_data.append(page_data)
            
            # Look for clause patterns in raw text
            clause_patterns = re.findall(r'\b(\d+\.\d+(?:\.\d+)*)\s+([^\n]+)', raw_text)
            if clause_patterns:
                print(f"Page {page_num + 1}: Found {len(clause_patterns)} potential clauses")
                for pattern in clause_patterns[:3]:  # Show first 3
                    print(f"  {pattern[0]}: {pattern[1][:50]}...")
        
        return all_text_data
    
    def method_2_ocr_extraction(self, max_pages=5):
        """Method 2: OCR extraction for pages that might have image-based text"""
        print(f"\n🔍 METHOD 2: OCR Extraction (first {max_pages} pages)")
        print("=" * 50)
        
        ocr_data = []
        
        try:
            # Convert PDF pages to images
            images = convert_from_path(self.pdf_path, first_page=1, last_page=max_pages, dpi=200)
            
            for i, image in enumerate(images):
                print(f"Processing page {i+1} with OCR...")
                
                # Extract text using OCR
                ocr_text = pytesseract.image_to_string(image, config='--psm 6')
                
                # Look for clause patterns in OCR text
                clause_patterns = re.findall(r'\b(\d+\.\d+(?:\.\d+)*)\s+([^\n]+)', ocr_text)
                
                ocr_data.append({
                    'page_number': i + 1,
                    'ocr_text': ocr_text,
                    'clause_patterns': clause_patterns
                })
                
                if clause_patterns:
                    print(f"  OCR found {len(clause_patterns)} potential clauses")
                    for pattern in clause_patterns[:2]:  # Show first 2
                        print(f"    {pattern[0]}: {pattern[1][:40]}...")
                        
        except Exception as e:
            print(f"OCR extraction failed: {e}")
            
        return ocr_data
    
    def method_3_structured_search(self):
        """Method 3: Search for specific patterns and structures"""
        print(f"\n🔍 METHOD 3: Structured Pattern Search")
        print("=" * 50)
        
        structured_data = []
        
        # Target patterns we know exist from user's image
        target_patterns = {
            '1_decimal': r'\b(\d+\.\d+)\b',
            '2_decimal': r'\b(\d+\.\d+\.\d+)\b', 
            '3_decimal': r'\b(\d+\.\d+\.\d+\.\d+)\b',
            '4_decimal': r'\b(\d+\.\d+\.\d+\.\d+\.\d+)\b'
        }
        
        question_patterns = [
            r'The\s+\w+\s+ID\?',
            r'The\s+operating\s+range\?',
            r'The\s+uniformity\s+requirement\?',
            r'The\s+qualified\s+working\s+zone\?'
        ]
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            page_results = {
                'page_number': page_num + 1,
                'found_patterns': {},
                'questions_found': [],
                'yes_no_lines': []
            }
            
            # Search for decimal patterns
            for pattern_name, pattern in target_patterns.items():
                matches = re.findall(pattern, text)
                if matches:
                    page_results['found_patterns'][pattern_name] = list(set(matches))
            
            # Search for question patterns
            for q_pattern in question_patterns:
                matches = re.findall(q_pattern, text, re.IGNORECASE)
                if matches:
                    page_results['questions_found'].extend(matches)
            
            # Find YES/NO lines
            lines = text.split('\n')
            for line in lines:
                if re.search(r'\b(YES|NO|NA)\b', line, re.IGNORECASE):
                    page_results['yes_no_lines'].append(line.strip())
            
            if (page_results['found_patterns'] or 
                page_results['questions_found'] or 
                page_results['yes_no_lines']):
                structured_data.append(page_results)
                
                print(f"Page {page_num + 1}:")
                if page_results['found_patterns']:
                    print(f"  Patterns: {page_results['found_patterns']}")
                if page_results['questions_found']:
                    print(f"  Questions: {page_results['questions_found'][:2]}")
                if page_results['yes_no_lines']:
                    print(f"  YES/NO lines: {len(page_results['yes_no_lines'])}")
        
        return structured_data
    
    def method_4_export_to_text(self):
        """Method 4: Export each page as clean text file for manual review"""
        print(f"\n🔍 METHOD 4: Export to Text Files")
        print("=" * 50)
        
        output_dir = Path("pdf_text_export")
        output_dir.mkdir(exist_ok=True)
        
        exported_files = []
        
        for page_num in range(min(10, len(self.doc))):  # First 10 pages
            page = self.doc[page_num]
            text = page.get_text()
            
            # Clean up the text
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line and len(line) > 2:  # Skip empty and very short lines
                    cleaned_lines.append(line)
            
            cleaned_text = '\n'.join(cleaned_lines)
            
            # Export to file
            output_file = output_dir / f"page_{page_num + 1:02d}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"PAGE {page_num + 1}\n")
                f.write("=" * 50 + "\n\n")
                f.write(cleaned_text)
            
            exported_files.append(str(output_file))
            print(f"  Exported: {output_file}")
        
        return exported_files
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive analysis report"""
        print(f"\n📊 COMPREHENSIVE ANALYSIS REPORT")
        print("=" * 60)
        
        # Run all methods
        pymupdf_data = self.method_1_pymupdf_extraction()
        ocr_data = self.method_2_ocr_extraction()
        structured_data = self.method_3_structured_search()
        exported_files = self.method_4_export_to_text()
        
        # Create summary
        summary = {
            'pdf_path': self.pdf_path,
            'total_pages': len(self.doc),
            'pymupdf_results': len(pymupdf_data),
            'ocr_results': len(ocr_data),
            'structured_results': len(structured_data),
            'exported_files': len(exported_files)
        }
        
        # Save comprehensive results
        results = {
            'summary': summary,
            'pymupdf_data': pymupdf_data,
            'ocr_data': ocr_data,
            'structured_data': structured_data,
            'exported_files': exported_files
        }
        
        # Save to JSON
        output_file = "comprehensive_pdf_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Analysis complete!")
        print(f"📄 Summary:")
        print(f"  Total pages analyzed: {summary['total_pages']}")
        print(f"  PyMuPDF results: {summary['pymupdf_results']} pages")
        print(f"  OCR results: {summary['ocr_results']} pages")
        print(f"  Structured findings: {summary['structured_results']} pages")
        print(f"  Text files exported: {summary['exported_files']}")
        print(f"  Full results saved to: {output_file}")
        
        return results
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 advanced_pdf_converter.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print("🚀 ADVANCED PDF CONVERTER FOR NADCAP COMPLIANCE")
    print("=" * 60)
    print(f"📄 Processing: {pdf_path}")
    
    converter = AdvancedPDFConverter(pdf_path)
    
    try:
        results = converter.generate_comprehensive_report()
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print("=" * 30)
        
        # Analyze which method worked best
        if any(page['found_patterns'] for page in results['structured_data']):
            print("✅ Structured pattern search found clause numbers!")
            print("   Recommend using this method for extraction.")
        
        if results['ocr_data'] and any(page['clause_patterns'] for page in results['ocr_data']):
            print("✅ OCR extraction found additional patterns!")
            print("   Recommend combining OCR with text extraction.")
        
        print("📁 Check the 'pdf_text_export' folder for individual page text files.")
        print("📊 Review 'comprehensive_pdf_analysis.json' for detailed results.")
        
    finally:
        converter.close()

if __name__ == "__main__":
    main()
