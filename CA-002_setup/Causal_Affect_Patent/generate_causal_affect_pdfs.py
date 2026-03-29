#!/usr/bin/env python3
"""
Generate separate PDF documents for UK IPO patent application submission.
Produces: Abstract, Description, Claims, Drawings Info, and Figures PDFs.
Adapted from Communication Patent PDF generator using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
import re
import os
from datetime import datetime

# Timestamp for file versioning (DDMMYY)
TIMESTAMP = "300326"

# Patent title
PATENT_TITLE = ("SYSTEM AND METHOD FOR AUTONOMOUS CROSS-DOMAIN CAUSAL DISCOVERY "
                "AND BUSINESS GENERATION USING ENSEMBLE PREDICTION AND "
                "TEST-DRIVEN DEVELOPMENT")

# Setup styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='Justify',
    alignment=TA_JUSTIFY,
    fontSize=11,
    leading=14,
    spaceAfter=6
))
styles.add(ParagraphStyle(
    name='PatentTitle',
    fontSize=14,
    leading=16,
    alignment=TA_CENTER,
    spaceAfter=12,
    fontName='Helvetica-Bold'
))
styles.add(ParagraphStyle(
    name='PatentHeading',
    fontSize=12,
    leading=14,
    spaceAfter=6,
    spaceBefore=12,
    fontName='Helvetica-Bold'
))
styles.add(ParagraphStyle(
    name='PatentSubHeading',
    fontSize=11,
    leading=13,
    spaceAfter=4,
    spaceBefore=8,
    fontName='Helvetica-Bold'
))
styles.add(ParagraphStyle(
    name='CodeBlock',
    fontName='Courier',
    fontSize=8,
    leading=10,
    leftIndent=20,
    spaceAfter=6,
    spaceBefore=6
))
styles.add(ParagraphStyle(
    name='ClaimText',
    alignment=TA_JUSTIFY,
    fontSize=11,
    leading=14,
    spaceAfter=10,
    leftIndent=0
))
styles.add(ParagraphStyle(
    name='ClaimIndent',
    alignment=TA_JUSTIFY,
    fontSize=11,
    leading=14,
    spaceAfter=4,
    leftIndent=20
))


def clean_text_for_pdf(text):
    """Convert markdown/special characters to PDF-safe format."""
    # XML-escape ampersands first (before other HTML entities)
    text = text.replace('&', '&amp;')
    # Escape angle brackets
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    # Replace common special characters
    text = text.replace('×', 'x')
    text = text.replace('≠', '!=')
    text = text.replace('≥', '&gt;=')
    text = text.replace('≤', '&lt;=')
    text = text.replace('Σ', 'Sum')
    text = text.replace('Δ', 'Delta')
    text = text.replace('θ', 'theta')
    text = text.replace('←', '&lt;-')
    text = text.replace('→', '-&gt;')
    text = text.replace('↛', '-/&gt;')
    text = text.replace('↔', '&lt;-&gt;')
    text = text.replace('─', '-')
    text = text.replace('│', '|')
    text = text.replace('┌', '+')
    text = text.replace('┐', '+')
    text = text.replace('└', '+')
    text = text.replace('┘', '+')
    text = text.replace('├', '+')
    text = text.replace('┤', '+')
    text = text.replace('┬', '+')
    text = text.replace('┴', '+')
    text = text.replace('┼', '+')
    text = text.replace('╔', '+')
    text = text.replace('╗', '+')
    text = text.replace('╚', '+')
    text = text.replace('╝', '+')
    text = text.replace('║', '|')
    text = text.replace('═', '=')
    text = text.replace('╧', '+')
    text = text.replace('▶', '-&gt;')
    text = text.replace('▼', 'v')
    text = text.replace('◀', '&lt;-')
    text = text.replace('◇', '*')
    text = text.replace('✗', 'X')
    text = text.replace('●', '*')
    text = text.replace('█', '#')
    text = text.replace('░', '.')
    text = text.replace('↑', '^')
    text = text.replace('✓', 'Y')
    text = text.replace('•', '*')
    text = text.replace('²', '2')
    text = text.replace('₀', '0')
    text = text.replace('₁', '1')
    text = text.replace(''', "'")
    text = text.replace(''', "'")
    text = text.replace('"', '"')
    text = text.replace('"', '"')
    text = text.replace('—', ' - ')
    text = text.replace('–', '-')
    # Keep circled numbers as text
    for i, c in enumerate('①②③④⑤⑥⑦⑧⑨'):
        text = text.replace(c, f'({i+1})')
    # Handle H-sub-0
    text = text.replace('H₀', 'H0')
    return text


def read_markdown(filepath):
    """Read a markdown file and return its content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def parse_markdown_to_story(content, doc_type='description'):
    """Parse markdown content into ReportLab story elements."""
    story = []
    content = clean_text_for_pdf(content)
    lines = content.split('\n')

    in_code_block = False
    code_lines = []
    in_table = False
    table_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Handle code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                code_text = '\n'.join(code_lines)
                if code_text.strip():
                    story.append(Preformatted(code_text, styles['CodeBlock']))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Handle table rows
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                story.append(Spacer(1, 0.1 * inch))
            # Skip separator rows (|---|---|)
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):
                i += 1
                continue
            # Parse table row
            cells = [c.strip() for c in line.split('|')[1:-1]]
            row_text = '    '.join(cells)
            story.append(Paragraph(row_text, styles['Justify']))
            i += 1
            continue
        elif in_table:
            in_table = False
            story.append(Spacer(1, 0.1 * inch))

        stripped = line.strip()

        # Skip empty lines (add small space)
        if not stripped:
            story.append(Spacer(1, 0.05 * inch))
            i += 1
            continue

        # Skip the top-level title and patent title (already in PDF header)
        if stripped.startswith('# UK PATENT APPLICATION'):
            i += 1
            continue
        if stripped.startswith('## SYSTEM AND METHOD'):
            i += 1
            continue
        if stripped in ('## DESCRIPTION', '## CLAIMS', '## DRAWINGS INFORMATION',
                        '## FIGURES', '## ABSTRACT'):
            i += 1
            continue

        # H3 headings (### SECTION NAME)
        if stripped.startswith('### '):
            heading_text = stripped[4:].strip()
            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph(heading_text, styles['PatentHeading']))
            i += 1
            continue

        # H4 headings (#### Subsection Name)
        if stripped.startswith('#### '):
            heading_text = stripped[5:].strip()
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(heading_text, styles['PatentSubHeading']))
            i += 1
            continue

        # Bold lines that act as sub-sub-headings
        if stripped.startswith('**') and stripped.endswith('**') and len(stripped) < 120:
            heading_text = stripped.strip('*').strip()
            story.append(Spacer(1, 0.05 * inch))
            story.append(Paragraph(f'<b>{heading_text}</b>', styles['Justify']))
            i += 1
            continue

        # Claims: handle claim numbering
        if doc_type == 'claims':
            claim_match = re.match(r'^\*\*Claim\s+(\d+)\.\*\*\s*(.*)', stripped)
            if claim_match:
                claim_num = claim_match.group(1)
                claim_text = claim_match.group(2)
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph(
                    f'<b>Claim {claim_num}.</b> {claim_text}',
                    styles['ClaimText']
                ))
                i += 1
                continue

        # Lettered sub-clauses in claims (a processor; a memory storing...)
        if doc_type == 'claims' and re.match(r'^[a-z]\s', stripped):
            story.append(Paragraph(stripped, styles['ClaimIndent']))
            i += 1
            continue

        # Numbered list items
        if re.match(r'^\d+\.', stripped):
            text = process_inline_formatting(stripped)
            story.append(Paragraph(text, styles['Justify']))
            i += 1
            continue

        # Bullet points
        if stripped.startswith('- ') or stripped.startswith('* '):
            text = process_inline_formatting(stripped[2:])
            story.append(Paragraph(f'    \u2022 {text}', styles['Justify']))
            i += 1
            continue

        # Regular paragraph
        text = process_inline_formatting(stripped)
        if len(text) > 10:
            story.append(Paragraph(text, styles['Justify']))

        i += 1

    return story


def process_inline_formatting(text):
    """Convert markdown inline formatting to ReportLab XML."""
    # Bold: **text** -> <b>text</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic: *text* -> <i>text</i> (but not inside bold)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    # Inline code: `text` -> <font name="Courier">text</font>
    text = re.sub(r'`(.+?)`', r'<font name="Courier" size="9">\1</font>', text)
    return text


def create_pdf(filename, title, subtitle, story_elements):
    """Create a PDF document with header and content."""
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    story = []

    # Add header
    story.append(Paragraph('UK PATENT APPLICATION', styles['PatentTitle']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(title, styles['PatentHeading']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(subtitle, styles['PatentSubHeading']))
    story.append(Spacer(1, 0.3 * inch))

    # Add content
    story.extend(story_elements)

    doc.build(story)

    # Count pages
    from reportlab.lib.pagesizes import A4 as a4size
    from reportlab.pdfgen import canvas as pdf_canvas
    import io
    # Re-read the generated PDF to count pages
    with open(filename, 'rb') as f:
        from reportlab.lib.utils import open_for_read
        data = f.read()
    # Simple page count from PDF
    page_count = data.count(b'/Type /Page') - data.count(b'/Type /Pages')
    print(f"  Created: {filename} ({page_count} pages)")
    return page_count


def generate_figures_pdf(content, filename):
    """Generate a special PDF for figures with monospace formatting."""
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=inch,
        bottomMargin=inch
    )

    story = []
    story.append(Paragraph('UK PATENT APPLICATION', styles['PatentTitle']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(PATENT_TITLE, styles['PatentHeading']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph('FIGURES', styles['PatentSubHeading']))
    story.append(Spacer(1, 0.3 * inch))

    content = clean_text_for_pdf(content)
    lines = content.split('\n')

    in_code_block = False
    code_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip headers
        if stripped.startswith('#'):
            heading = stripped.lstrip('#').strip()
            if heading in ('UK PATENT APPLICATION', 'FIGURES') or heading.startswith('SYSTEM AND METHOD'):
                continue
            # Figure headings
            if heading.startswith('FIGURE'):
                story.append(PageBreak())
                story.append(Paragraph(heading, styles['PatentHeading']))
                continue
            story.append(Paragraph(heading, styles['PatentSubHeading']))
            continue

        if stripped.startswith('```'):
            if in_code_block:
                code_text = '\n'.join(code_lines)
                if code_text.strip():
                    story.append(Preformatted(code_text, styles['CodeBlock']))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if stripped.startswith('---'):
            continue

        if stripped.startswith('**') and stripped.endswith('**'):
            text = stripped.strip('*').strip()
            story.append(Paragraph(f'<b>{text}</b>', styles['Justify']))
            continue

        if stripped and len(stripped) > 5:
            text = process_inline_formatting(stripped)
            story.append(Paragraph(text, styles['Justify']))

    doc.build(story)
    with open(filename, 'rb') as f:
        data = f.read()
    page_count = data.count(b'/Type /Page') - data.count(b'/Type /Pages')
    print(f"  Created: {filename} ({page_count} pages)")
    return page_count


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 70)
    print(f"CAUSAL AFFECT PATENT - PDF GENERATION ({TIMESTAMP})")
    print("=" * 70)

    page_counts = {}

    # 1. Abstract PDF
    print("\n[1/5] Generating Abstract PDF...")
    content = read_markdown(os.path.join(script_dir, '01_Abstract.md'))
    story = parse_markdown_to_story(content, doc_type='abstract')
    filename = os.path.join(script_dir, f'Causal_Affect_Patent_Abstract_{TIMESTAMP}.pdf')
    page_counts['abstract'] = create_pdf(filename, PATENT_TITLE, 'ABSTRACT', story)

    # 2. Description PDF
    print("\n[2/5] Generating Description PDF...")
    content = read_markdown(os.path.join(script_dir, '02_Description.md'))
    story = parse_markdown_to_story(content, doc_type='description')
    filename = os.path.join(script_dir, f'Causal_Affect_Patent_Description_{TIMESTAMP}.pdf')
    page_counts['description'] = create_pdf(filename, PATENT_TITLE, 'DESCRIPTION', story)

    # 3. Claims PDF
    print("\n[3/5] Generating Claims PDF...")
    content = read_markdown(os.path.join(script_dir, '03_Claims.md'))
    story = parse_markdown_to_story(content, doc_type='claims')
    filename = os.path.join(script_dir, f'Causal_Affect_Patent_Claims_{TIMESTAMP}.pdf')
    page_counts['claims'] = create_pdf(filename, PATENT_TITLE, 'CLAIMS', story)

    # 4. Drawings Info PDF
    print("\n[4/5] Generating Drawings Information PDF...")
    content = read_markdown(os.path.join(script_dir, '04_Drawings_Info.md'))
    story = parse_markdown_to_story(content, doc_type='drawings')
    filename = os.path.join(script_dir, f'Causal_Affect_Patent_Drawings_Info_{TIMESTAMP}.pdf')
    page_counts['drawings_info'] = create_pdf(filename, PATENT_TITLE, 'DRAWINGS INFORMATION', story)

    # 5. Figures PDF
    print("\n[5/5] Generating Figures PDF...")
    content = read_markdown(os.path.join(script_dir, '05_Figures.md'))
    filename = os.path.join(script_dir, f'Causal_Affect_Patent_Figures_{TIMESTAMP}.pdf')
    page_counts['figures'] = generate_figures_pdf(content, filename)

    # Print summary
    total_pages = sum(page_counts.values())
    print("\n" + "=" * 70)
    print("SUCCESS: All PDF documents generated!")
    print("=" * 70)
    print(f"\nDocument                   Pages")
    print(f"-" * 40)
    print(f"Abstract                   {page_counts['abstract']}")
    print(f"Description                {page_counts['description']}")
    print(f"Claims                     {page_counts['claims']}")
    print(f"Drawings Information       {page_counts['drawings_info']}")
    print(f"Figures                    {page_counts['figures']}")
    print(f"-" * 40)
    print(f"TOTAL                      {total_pages}")

    # Return info for SUBMISSION_README
    return page_counts, TIMESTAMP


if __name__ == '__main__':
    page_counts, ts = main()
