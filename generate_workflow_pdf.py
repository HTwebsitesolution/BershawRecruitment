#!/usr/bin/env python3
"""
Generate PDF from workflow documentation.
Creates a well-formatted HTML file that can be converted to PDF or printed directly.
"""

import os
import sys
from pathlib import Path

def read_markdown_file(filepath):
    """Read a markdown file and return its content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        return ""
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

def markdown_to_html(markdown_text):
    """Convert markdown to HTML with proper formatting."""
    try:
        import markdown
        # Use extensions for better formatting
        md = markdown.Markdown(extensions=['extra', 'toc', 'codehilite', 'tables', 'fenced_code'])
        html = md.convert(markdown_text)
        return html
    except ImportError:
        # Fallback: basic markdown conversion
        print("markdown library not available, using basic conversion")
        html = markdown_text
        # Escape HTML
        html = html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Headers
        html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        html = html.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        # Bold
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        # Code blocks
        html = html.replace('```', '<pre><code>').replace('```', '</code></pre>')
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        return f"<p>{html}</p>"

def create_html_document(content_parts, output_path):
    """Create a well-formatted HTML document."""
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bershaw Recruitment - Complete Workflow Documentation</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: 'Segoe UI', 'Arial', 'Helvetica', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }
        
        .cover-page {
            page-break-after: always;
            text-align: center;
            padding: 50px 20px;
        }
        
        .cover-page h1 {
            font-size: 32pt;
            color: #2563eb;
            margin-bottom: 20px;
            border: none;
        }
        
        .cover-page .subtitle {
            font-size: 16pt;
            color: #666;
            margin-top: 30px;
        }
        
        .cover-page .date {
            font-size: 12pt;
            color: #999;
            margin-top: 50px;
        }
        
        h1 {
            font-size: 24pt;
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
            page-break-after: avoid;
        }
        
        h2 {
            font-size: 18pt;
            color: #1e40af;
            margin-top: 30px;
            margin-bottom: 15px;
            page-break-after: avoid;
            border-left: 4px solid #2563eb;
            padding-left: 15px;
        }
        
        h3 {
            font-size: 14pt;
            color: #1e40af;
            margin-top: 25px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }
        
        h4 {
            font-size: 12pt;
            color: #374151;
            margin-top: 20px;
            margin-bottom: 8px;
        }
        
        p {
            margin: 10px 0;
            text-align: justify;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', 'Consolas', monospace;
            font-size: 10pt;
            color: #e83e8c;
        }
        
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-left: 4px solid #2563eb;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            page-break-inside: avoid;
            font-family: 'Courier New', 'Consolas', monospace;
            font-size: 9pt;
            line-height: 1.4;
        }
        
        pre code {
            background: none;
            padding: 0;
            color: #333;
        }
        
        blockquote {
            border-left: 4px solid #2563eb;
            padding-left: 15px;
            margin-left: 0;
            color: #666;
            font-style: italic;
            background-color: #f8f9fa;
            padding: 15px;
            margin: 15px 0;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
            font-size: 10pt;
        }
        
        th, td {
            border: 1px solid #dee2e6;
            padding: 10px;
            text-align: left;
        }
        
        th {
            background-color: #2563eb;
            color: white;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        ul, ol {
            margin: 15px 0;
            padding-left: 30px;
        }
        
        li {
            margin: 8px 0;
        }
        
        .page-break {
            page-break-before: always;
            margin-top: 50px;
        }
        
        .toc {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 30px 0;
            page-break-inside: avoid;
        }
        
        .toc h2 {
            margin-top: 0;
            border: none;
            padding: 0;
        }
        
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        
        .toc li {
            margin: 8px 0;
        }
        
        .toc a {
            color: #2563eb;
            text-decoration: none;
        }
        
        .toc a:hover {
            text-decoration: underline;
        }
        
        .highlight {
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        .note {
            background-color: #e7f3ff;
            border-left: 4px solid #2563eb;
            padding: 15px;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .warning {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .success {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        hr {
            border: none;
            border-top: 2px solid #e9ecef;
            margin: 30px 0;
        }
        
        strong {
            color: #1e40af;
            font-weight: 600;
        }
        
        em {
            color: #666;
        }
        
        @media print {
            body {
                max-width: 100%;
                padding: 0;
            }
            
            .page-break {
                page-break-before: always;
            }
            
            h1, h2, h3 {
                page-break-after: avoid;
            }
            
            pre, blockquote, table {
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="cover-page">
        <h1>Bershaw Recruitment Platform</h1>
        <h2>Complete Workflow Documentation</h2>
        <p class="subtitle">End-to-End Recruitment Process with AI Interviewer/Messenger</p>
        <p class="date">Generated: {date}</p>
    </div>
    
    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
            <li><a href="#overview">Overview</a></li>
            <li><a href="#complete-workflow">Complete Workflow</a></li>
            <li><a href="#ai-interviewer">AI Interviewer/Messenger</a></li>
            <li><a href="#workflow-summary">Workflow Summary</a></li>
            <li><a href="#visual-workflow">Visual Workflow Diagrams</a></li>
        </ul>
    </div>
    
    {content}
    
    <div style="page-break-before: always; margin-top: 50px; text-align: center; color: #999; font-size: 10pt;">
        <p>Bershaw Recruitment Platform - Complete Workflow Documentation</p>
        <p>End of Document</p>
    </div>
</body>
</html>"""
    
    from datetime import datetime
    date_str = datetime.now().strftime("%B %d, %Y")
    
    # Combine all content
    full_content = "\n\n".join(content_parts)
    
    # Replace placeholders manually to avoid issues with CSS curly braces
    html = html_template.replace('{date}', date_str).replace('{content}', full_content)
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return True

def try_convert_to_pdf(html_path, pdf_path):
    """Try to convert HTML to PDF using available tools."""
    # Try weasyprint
    try:
        from weasyprint import HTML
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return True
    except:
        pass
    
    # Try pdfkit
    try:
        import pdfkit
        pdfkit.from_file(str(html_path), str(pdf_path))
        return True
    except:
        pass
    
    return False

def main():
    """Main function to generate PDF."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir
    
    # Files to include
    workflow_files = [
        ("COMPLETE_WORKFLOW.md", "Complete Workflow"),
        ("WORKFLOW_SUMMARY.md", "Workflow Summary"),
        ("WORKFLOW_VISUAL.md", "Visual Workflow")
    ]
    
    # Check if files exist and read content
    content_parts = []
    existing_files = []
    
    for filename, title in workflow_files:
        filepath = project_root / filename
        if filepath.exists():
            print(f"Reading {filename}...")
            content = read_markdown_file(filepath)
            if content:
                html_content = markdown_to_html(content)
                content_parts.append(f'<div class="page-break"><h1 id="{filename.lower().replace(".md", "").replace("_", "-")}">{title}</h1>{html_content}</div>')
                existing_files.append(filepath)
        else:
            print(f"Warning: {filename} not found")
    
    if not content_parts:
        print("Error: No workflow files found!")
        return 1
    
    # Output paths
    html_path = project_root / "Bershaw_Recruitment_Complete_Workflow.html"
    pdf_path = project_root / "Bershaw_Recruitment_Complete_Workflow.pdf"
    
    print(f"\nGenerating HTML: {html_path}")
    create_html_document(content_parts, html_path)
    print(f"Success! HTML saved to: {html_path}")
    
    # Try to convert to PDF
    print(f"\nAttempting to convert to PDF: {pdf_path}")
    if try_convert_to_pdf(html_path, pdf_path):
        print(f"Success! PDF saved to: {pdf_path}")
        print(f"   File size: {pdf_path.stat().st_size / 1024:.2f} KB")
    else:
        print("Could not automatically convert to PDF.")
        print("\nAlternative options:")
        print(f"1. Open {html_path} in your browser")
        print("2. Press Ctrl+P (or Cmd+P on Mac)")
        print("3. Select 'Save as PDF' as the destination")
        print("4. Click Save")
        print("\nOr install weasyprint: pip install weasyprint")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
