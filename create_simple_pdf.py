#!/usr/bin/env python3
"""
Simple PDF creation - converts the HTML file to PDF using weasyprint if available,
or provides clear instructions for browser-based conversion.
"""

import sys
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    html_path = project_root / "Bershaw_Recruitment_Complete_Workflow.html"
    pdf_path = project_root / "Bershaw_Recruitment_Complete_Workflow.pdf"
    
    if not html_path.exists():
        print("Error: HTML file not found. Run generate_workflow_pdf.py first.")
        return 1
    
    print(f"HTML file found: {html_path}")
    print(f"Size: {html_path.stat().st_size / 1024:.2f} KB")
    
    # Try weasyprint
    try:
        from weasyprint import HTML
        print("\nConverting HTML to PDF using weasyprint...")
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        
        if pdf_path.exists():
            print(f"\nSuccess! PDF created: {pdf_path}")
            print(f"Size: {pdf_path.stat().st_size / 1024:.2f} KB")
            return 0
    except ImportError:
        print("\nweasyprint not available.")
    except Exception as e:
        print(f"\nweasyprint error: {e}")
        print("This is common on Windows. Use browser method below.")
    
    # Provide browser instructions
    print("\n" + "="*60)
    print("PDF CONVERSION INSTRUCTIONS")
    print("="*60)
    print(f"\n1. Open this file in your browser:")
    print(f"   {html_path}")
    print("\n2. Press Ctrl+P (or Cmd+P on Mac) to print")
    print("\n3. Select 'Save as PDF' or 'Microsoft Print to PDF' as destination")
    print("\n4. Click 'Save'")
    print("\n5. The PDF will be saved to your chosen location")
    print("\nAlternatively, the HTML file is already formatted and ready to view!")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

