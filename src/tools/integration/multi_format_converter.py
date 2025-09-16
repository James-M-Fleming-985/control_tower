#!/usr/bin/env python3
"""
Multi-Format PDF Converter for NADCAP Document
Converts PDF to multiple formats to find the best extraction method:
- HTML (with structure preservation)
- XML (structured markup)
- Markdown (clean text with hierarchy) 
- Plain text (with enhanced structure detection)
- Word document (if possible)
"""

import fitz  # PyMuPDF
import pandas as pd
import re
import sys
import os
from pathlib import Path
import json
from bs4 import BeautifulSoup
import subprocess

class MultiFormatPDFConverter:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.output_dir = Path("converted_formats")
        self.output_dir.mkdir(exist_ok=True)
        
    def convert_to_html(self):
        """Convert PDF to HTML with structure preservation"""
        print("🌐 Converting to HTML...")
        
        html_content = []
        html_content.append("""<!DOCTYPE html>
<html>
<head>
    <title>NADCAP Audit Requirements</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .page { page-break-after: always; border-bottom: 2px solid #ccc; margin-bottom: 20px; }
        .clause { margin: 10px 0; }
        .clause-number { font-weight: bold; color: #0066cc; }
        .question { margin-left: 20px; }
        .guidance { margin-left: 20px; font-style: italic; color: #666; }
        .yes-no { margin-left: 20px; font-weight: bold; }
    </style>
</head>
<body>""")
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            html_content.append(f'<div class="page" id="page-{page_num + 1}">')
            html_content.append(f'<h2>Page {page_num + 1}</h2>')
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect clause numbers
                if re.match(r'^\d+\.\d+(\.\d+)*\s*', line):
                    html_content.append(f'<div class="clause">')
                    html_content.append(f'<span class="clause-number">{line}</span>')
                    html_content.append('</div>')
                elif line.startswith('Guidance:'):
                    html_content.append(f'<div class="guidance">{line}</div>')
                elif re.search(r'\b(YES|NO|NA)\b', line):
                    html_content.append(f'<div class="yes-no">{line}</div>')
                else:
                    html_content.append(f'<div class="question">{line}</div>')
            
            html_content.append('</div>')
        
        html_content.append('</body></html>')
        
        html_file = self.output_dir / "nadcap_document.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_content))
        
        print(f"  ✅ HTML saved: {html_file}")
        return html_file
    
    def convert_to_xml(self):
        """Convert PDF to structured XML"""
        print("📄 Converting to XML...")
        
        xml_content = []
        xml_content.append('<?xml version="1.0" encoding="UTF-8"?>')
        xml_content.append('<nadcap_document>')
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            xml_content.append(f'  <page number="{page_num + 1}">')
            
            lines = text.split('\n')
            current_clause = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect clause numbers
                clause_match = re.match(r'^(\d+\.\d+(?:\.\d+)*)\s*(.*)', line)
                if clause_match:
                    if current_clause:
                        xml_content.append('    </clause>')
                    
                    clause_num = clause_match.group(1)
                    clause_text = clause_match.group(2)
                    
                    # Determine decimal level
                    decimal_count = len(clause_num.split('.')) - 1
                    
                    xml_content.append(f'    <clause number="{clause_num}" decimal_level="{decimal_count}">')
                    if clause_text:
                        xml_content.append(f'      <question>{self.escape_xml(clause_text)}</question>')
                    
                    current_clause = clause_num
                elif current_clause and line.startswith('Guidance:'):
                    xml_content.append(f'      <guidance>{self.escape_xml(line)}</guidance>')
                elif current_clause and re.search(r'\b(YES|NO|NA)\b', line):
                    xml_content.append(f'      <response_options>{self.escape_xml(line)}</response_options>')
                elif current_clause and line:
                    xml_content.append(f'      <content>{self.escape_xml(line)}</content>')
            
            if current_clause:
                xml_content.append('    </clause>')
            
            xml_content.append('  </page>')
        
        xml_content.append('</nadcap_document>')
        
        xml_file = self.output_dir / "nadcap_document.xml"
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_content))
        
        print(f"  ✅ XML saved: {xml_file}")
        return xml_file
    
    def escape_xml(self, text):
        """Escape XML special characters"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
    
    def convert_to_markdown(self):
        """Convert PDF to Markdown with structure"""
        print("📝 Converting to Markdown...")
        
        md_content = []
        md_content.append('# NADCAP Audit Requirements\n')
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            md_content.append(f'\n## Page {page_num + 1}\n')
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect clause numbers and format as headers
                clause_match = re.match(r'^(\d+\.\d+(?:\.\d+)*)\s*(.*)', line)
                if clause_match:
                    clause_num = clause_match.group(1)
                    clause_text = clause_match.group(2)
                    
                    # Different header levels based on decimal depth
                    decimal_count = len(clause_num.split('.'))
                    header_level = min(decimal_count + 2, 6)  # H3 to H6
                    header_prefix = '#' * header_level
                    
                    md_content.append(f'\n{header_prefix} {clause_num} {clause_text}\n')
                elif line.startswith('Guidance:'):
                    md_content.append(f'\n> **{line}**\n')
                elif re.search(r'\b(YES|NO|NA)\b', line):
                    md_content.append(f'\n**Response:** {line}\n')
                else:
                    md_content.append(f'{line}\n')
        
        md_file = self.output_dir / "nadcap_document.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        
        print(f"  ✅ Markdown saved: {md_file}")
        return md_file
    
    def convert_to_structured_text(self):
        """Convert to enhanced structured text"""
        print("📋 Converting to Structured Text...")
        
        text_content = []
        text_content.append('NADCAP AUDIT REQUIREMENTS - STRUCTURED TEXT')
        text_content.append('=' * 60)
        text_content.append('')
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            text_content.append(f'\n[PAGE {page_num + 1}]')
            text_content.append('-' * 40)
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Mark different types of content
                if re.match(r'^\d+\.\d+(\.\d+)*\s*', line):
                    text_content.append(f'\n[CLAUSE] {line}')
                elif line.startswith('Guidance:'):
                    text_content.append(f'[GUIDANCE] {line}')
                elif re.search(r'\b(YES|NO|NA)\b', line):
                    text_content.append(f'[RESPONSE] {line}')
                else:
                    text_content.append(f'[TEXT] {line}')
        
        txt_file = self.output_dir / "nadcap_document_structured.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_content))
        
        print(f"  ✅ Structured Text saved: {txt_file}")
        return txt_file
    
    def try_convert_to_docx(self):
        """Try to convert to Word document using external tools"""
        print("📄 Attempting Word conversion...")
        
        try:
            # Try using pdf2docx if available
            docx_file = self.output_dir / "nadcap_document.docx"
            
            # Simple text-based docx creation
            from docx import Document
            doc = Document()
            
            doc.add_heading('NADCAP Audit Requirements', 0)
            
            for page_num in range(min(5, len(self.doc))):  # First 5 pages for testing
                page = self.doc[page_num]
                text = page.get_text()
                
                doc.add_heading(f'Page {page_num + 1}', level=1)
                
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 2:
                        if re.match(r'^\d+\.\d+(\.\d+)*\s*', line):
                            doc.add_heading(line, level=2)
                        else:
                            doc.add_paragraph(line)
            
            doc.save(str(docx_file))
            print(f"  ✅ Word document saved: {docx_file}")
            return docx_file
            
        except ImportError:
            print("  ⚠️  Word conversion requires python-docx: pip install python-docx")
            return None
        except Exception as e:
            print(f"  ❌ Word conversion failed: {e}")
            return None
    
    def analyze_conversion_results(self):
        """Analyze which format captured the most clauses"""
        print("\n🔍 ANALYZING CONVERSION RESULTS")
        print("=" * 50)
        
        results = {}
        
        # Analyze each format
        formats = [
            ("HTML", "nadcap_document.html"),
            ("XML", "nadcap_document.xml"),
            ("Markdown", "nadcap_document.md"),
            ("Structured Text", "nadcap_document_structured.txt")
        ]
        
        for format_name, filename in formats:
            file_path = self.output_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count clause patterns
                clause_patterns = {
                    '1_decimal': len(re.findall(r'\b\d+\.\d+\b(?!\.\d)', content)),
                    '2_decimal': len(re.findall(r'\b\d+\.\d+\.\d+\b(?!\.\d)', content)),
                    '3_decimal': len(re.findall(r'\b\d+\.\d+\.\d+\.\d+\b(?!\.\d)', content)),
                    '4_decimal': len(re.findall(r'\b\d+\.\d+\.\d+\.\d+\.\d+\b', content))
                }
                
                total_clauses = sum(clause_patterns.values())
                results[format_name] = {
                    'total': total_clauses,
                    'breakdown': clause_patterns,
                    'file_size': file_path.stat().st_size
                }
                
                print(f"📄 {format_name}:")
                print(f"   Total clauses: {total_clauses}")
                print(f"   1-decimal: {clause_patterns['1_decimal']}")
                print(f"   2-decimal: {clause_patterns['2_decimal']}")
                print(f"   3-decimal: {clause_patterns['3_decimal']}")
                print(f"   4-decimal: {clause_patterns['4_decimal']}")
                print(f"   File size: {file_path.stat().st_size:,} bytes")
                print()
        
        # Find best format
        if results:
            best_format = max(results.items(), key=lambda x: x[1]['total'])
            print(f"🏆 BEST FORMAT: {best_format[0]} with {best_format[1]['total']} clauses")
            
        return results
    
    def convert_all_formats(self):
        """Convert PDF to all supported formats"""
        print("🚀 MULTI-FORMAT PDF CONVERTER")
        print("=" * 40)
        print(f"📄 Processing: {self.pdf_path}")
        print(f"📁 Output directory: {self.output_dir}")
        print()
        
        # Convert to different formats
        html_file = self.convert_to_html()
        xml_file = self.convert_to_xml()
        md_file = self.convert_to_markdown()
        txt_file = self.convert_to_structured_text()
        docx_file = self.try_convert_to_docx()
        
        # Analyze results
        results = self.analyze_conversion_results()
        
        print("🎯 RECOMMENDATIONS:")
        print("=" * 30)
        if results:
            best_format = max(results.items(), key=lambda x: x[1]['total'])
            print(f"✅ Use {best_format[0]} format for extraction")
            print(f"   It captured {best_format[1]['total']} clauses")
            
            # Map format names to filenames
            format_files = {
                'HTML': 'nadcap_document.html',
                'XML': 'nadcap_document.xml', 
                'Markdown': 'nadcap_document.md',
                'Structured Text': 'nadcap_document_structured.txt'
            }
            
            best_file = format_files.get(best_format[0], 'unknown')
            print(f"   File: {self.output_dir}/{best_file}")
        
        return results
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 multi_format_converter.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    converter = MultiFormatPDFConverter(pdf_path)
    
    try:
        results = converter.convert_all_formats()
    finally:
        converter.close()

if __name__ == "__main__":
    main()
