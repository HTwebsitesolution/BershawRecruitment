#!/usr/bin/env python3
"""
Create PDF directly from markdown files using reportlab.
This is a fallback when weasyprint is not available.
"""

import sys
from pathlib import Path
from datetime import datetime

def read_file(filepath):
    """Read a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

def create_pdf_with_reportlab(files, output_path):
    """Create PDF using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
        import re
        
        doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        
        heading1_style = ParagraphStyle(
            'CustomH1',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=20,
            spaceBefore=30,
        )
        
        heading2_style = ParagraphStyle(
            'CustomH2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=20,
        )
        
        heading3_style = ParagraphStyle(
            'CustomH3',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=10,
            spaceBefore=15,
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
        )
        
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Code'],
            fontSize=9,
            fontName='Courier',
            backColor=colors.HexColor('#f4f4f4'),
            leftIndent=10,
            rightIndent=10,
        )
        
        # Cover page
        story.append(Spacer(1, 3*cm))
        story.append(Paragraph("Bershaw Recruitment Platform", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Complete Workflow Documentation", styles['Heading2']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("End-to-End Recruitment Process with AI Interviewer/Messenger", styles['Normal']))
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(PageBreak())
        
        # Process each file
        for filepath, title in files:
            if not Path(filepath).exists():
                continue
                
            print(f"Processing {filepath}...")
            content = read_file(filepath)
            
            if not content:
                continue
            
            # Add section title
            story.append(Paragraph(title, heading1_style))
            story.append(Spacer(1, 20))
            
            # Process content line by line
            lines = content.split('\n')
            in_code_block = False
            code_lines = []
            
            for line in lines:
                line = line.rstrip()
                
                # Handle code blocks
                if line.startswith('```'):
                    if in_code_block:
                        # End code block
                        if code_lines:
                            code_text = '\n'.join(code_lines)
                            story.append(Paragraph(f"<font face='Courier' size=9>{code_text}</font>", code_style))
                            story.append(Spacer(1, 10))
                        code_lines = []
                        in_code_block = False
                    else:
                        in_code_block = True
                    continue
                
                if in_code_block:
                    code_lines.append(line)
                    continue
                
                # Skip empty lines
                if not line.strip():
                    story.append(Spacer(1, 6))
                    continue
                
                # Headers
                if line.startswith('# '):
                    story.append(Paragraph(line[2:], heading1_style))
                    story.append(Spacer(1, 12))
                elif line.startswith('## '):
                    story.append(Paragraph(line[3:], heading2_style))
                    story.append(Spacer(1, 10))
                elif line.startswith('### '):
                    story.append(Paragraph(line[4:], heading3_style))
                    story.append(Spacer(1, 8))
                elif line.startswith('#### '):
                    story.append(Paragraph(line[5:], styles['Heading4']))
                    story.append(Spacer(1, 6))
                # Horizontal rule
                elif line.startswith('---'):
                    story.append(Spacer(1, 20))
                # List items
                elif line.startswith('- ') or line.startswith('* '):
                    text = line[2:].strip()
                    # Convert markdown to HTML-like for reportlab
                    text = text.replace('**', '<b>').replace('**', '</b>')
                    text = text.replace('`', '<font face="Courier">').replace('`', '</font>')
                    story.append(Paragraph(f"• {text}", normal_style))
                    story.append(Spacer(1, 4))
                # Numbered list
                elif re.match(r'^\d+\.\s', line):
                    text = re.sub(r'^\d+\.\s', '', line)
                    text = text.replace('**', '<b>').replace('**', '</b>')
                    story.append(Paragraph(text, normal_style))
                    story.append(Spacer(1, 4))
                # Regular text
                else:
                    # Convert markdown to HTML-like
                    text = line
                    text = text.replace('**', '<b>').replace('**', '</b>')
                    text = text.replace('*', '<i>').replace('*', '</i>')
                    text = text.replace('`', '<font face="Courier" size=9>').replace('`', '</font>')
                    # Escape HTML
                    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    # Restore our intentional tags
                    text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
                    text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
                    text = text.replace('&lt;font', '<font').replace('&lt;/font&gt;', '</font>')
                    
                    if text.strip():
                        story.append(Paragraph(text, normal_style))
                        story.append(Spacer(1, 6))
            
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        return True
        
    except ImportError:
        print("reportlab not installed. Install with: pip install reportlab")
        return False
    except Exception as e:
        print(f"Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    project_root = Path(__file__).parent
    
    workflow_files = [
        ("COMPLETE_WORKFLOW.md", "Complete Workflow"),
        ("WORKFLOW_SUMMARY.md", "Workflow Summary"),
        ("WORKFLOW_VISUAL.md", "Visual Workflow Diagrams")
    ]
    
    # Check which files exist
    existing_files = []
    for filename, title in workflow_files:
        filepath = project_root / filename
        if filepath.exists():
            existing_files.append((str(filepath), title))
        else:
            print(f"Warning: {filename} not found")
    
    if not existing_files:
        print("Error: No workflow files found!")
        return 1
    
    output_path = project_root / "Bershaw_Recruitment_Complete_Workflow.pdf"
    
    print(f"Creating PDF: {output_path}")
    if create_pdf_with_reportlab(existing_files, output_path):
        print(f"Success! PDF saved to: {output_path}")
        if output_path.exists():
            print(f"   File size: {output_path.stat().st_size / 1024:.2f} KB")
        return 0
    else:
        print("Failed to create PDF")
        return 1

if __name__ == "__main__":
    sys.exit(main())

