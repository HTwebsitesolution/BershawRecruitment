"""
Script to test CV parser with real CV files from the CV folder.

This script:
1. Parses real CV PDF files
2. Extracts key fields (full name, phone, email, location, experience, skills, etc.)
3. Validates against expected output structure
4. Generates a comparison report
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cv_parser_llm import parse_cv_bytes_to_normalized_llm
from app.services.cv_parser import parse_cv_bytes_to_normalized
from app.models import CandidateCVNormalized


def extract_key_fields(cv: CandidateCVNormalized) -> Dict[str, Any]:
    """Extract key fields from parsed CV for comparison."""
    candidate = cv.candidate
    
    # Calculate total experience from experience items
    total_years = 0.0
    if cv.experience:
        for exp in cv.experience:
            if exp.start_date:
                try:
                    start_year = int(exp.start_date.split('-')[0])
                    start_month = int(exp.start_date.split('-')[1]) if len(exp.start_date.split('-')) > 1 else 1
                    
                    if exp.end_date:
                        end_year = int(exp.end_date.split('-')[0])
                        end_month = int(exp.end_date.split('-')[1]) if len(exp.end_date.split('-')) > 1 else 1
                    else:
                        # Current role
                        end_year = datetime.now().year
                        end_month = datetime.now().month
                    
                    # Calculate months
                    months = (end_year - start_year) * 12 + (end_month - start_month)
                    total_years += months / 12.0
                except (ValueError, IndexError) as e:
                    # Skip invalid dates
                    pass
    
    return {
        "full_name": candidate.full_name,
        "phone": candidate.phone,
        "email": candidate.email,
        "location": {
            "city": candidate.location.city if candidate.location else None,
            "country": candidate.location.country if candidate.location else None,
            "remote_preference": candidate.location.remote_preference if candidate.location else None,
        },
        "linkedin_url": candidate.linkedin_url,
        "total_experience_years": round(total_years, 1) if total_years > 0 else None,
        "roles": [{
            "title": exp.title,
            "employer": exp.employer,
            "start_date": exp.start_date,
            "end_date": exp.end_date,
            "is_current": exp.is_current,
        } for exp in cv.experience],
        "skills": [{
            "name": skill.name,
            "category": skill.category,
            "level": skill.level,
        } for skill in cv.skills],
        "education": [{
            "institution": edu.institution,
            "degree": edu.degree,
            "field": edu.field,
            "start_year": edu.start_year,
            "end_year": edu.end_year,
        } for edu in cv.education],
        "certifications": cv.certifications or [],
        "languages": [{
            "name": lang.name,
            "proficiency": lang.proficiency,
        } for lang in cv.languages],
        "salary_expectations": {
            "current": {
                "base_amount": candidate.current_compensation.base_amount if candidate.current_compensation else None,
                "currency": candidate.current_compensation.currency if candidate.current_compensation else None,
            },
            "target": {
                "base_min": candidate.target_compensation.base_min if candidate.target_compensation else None,
                "base_max": candidate.target_compensation.base_max if candidate.target_compensation else None,
                "currency": candidate.target_compensation.currency if candidate.target_compensation else None,
            },
        },
        "notice_period_weeks": candidate.notice_period_weeks,
        "right_to_work": candidate.right_to_work or [],
        "availability_date": candidate.availability_date,
        "parser_version": cv.extraction_meta.parser_version if cv.extraction_meta else None,
        "extraction_date": cv.extraction_meta.extracted_at if cv.extraction_meta else None,
    }


def test_cv_file(cv_path: Path, use_llm: bool = True) -> Dict[str, Any]:
    """Test parsing a single CV file."""
    print(f"\n{'='*60}")
    print(f"Testing: {cv_path.name}")
    print(f"{'='*60}")
    
    try:
        # Read CV file
        with open(cv_path, 'rb') as f:
            cv_bytes = f.read()
        
        print(f"File size: {len(cv_bytes)} bytes")
        
        # Parse CV
        if use_llm:
            print("Using LLM parser...")
            cv = parse_cv_bytes_to_normalized_llm(cv_bytes, filename=cv_path.name)
        else:
            print("Using stub parser...")
            cv = parse_cv_bytes_to_normalized(cv_bytes, filename=cv_path.name)
        
        # Extract key fields
        extracted = extract_key_fields(cv)
        
        # Print summary
        print(f"\n✓ Parsed successfully!")
        print(f"  Name: {extracted['full_name']}")
        print(f"  Email: {extracted['email']}")
        print(f"  Phone: {extracted['phone']}")
        print(f"  Location: {extracted['location']['city']}, {extracted['location']['country']}")
        print(f"  Experience: {extracted['total_experience_years']} years" if extracted['total_experience_years'] else "  Experience: Not calculated")
        print(f"  Roles: {len(extracted['roles'])}")
        print(f"  Skills: {len(extracted['skills'])}")
        print(f"  Education: {len(extracted['education'])}")
        print(f"  Certifications: {len(extracted['certifications'])}")
        print(f"  Languages: {len(extracted['languages'])}")
        print(f"  Notice Period: {extracted['notice_period_weeks']} weeks" if extracted['notice_period_weeks'] else "  Notice Period: Not specified")
        print(f"  Right to Work: {', '.join(extracted['right_to_work']) if extracted['right_to_work'] else 'Not specified'}")
        
        return {
            "file": cv_path.name,
            "success": True,
            "extracted": extracted,
            "full_output": cv.model_dump_json(indent=2, exclude_none=True),
        }
        
    except Exception as e:
        print(f"\n✗ Error parsing CV: {e}")
        import traceback
        traceback.print_exc()
        return {
            "file": cv_path.name,
            "success": False,
            "error": str(e),
        }


def main():
    """Main function to test all CV files."""
    # Find CV folder (should be in parent directory)
    script_dir = Path(__file__).parent
    cv_folder = script_dir.parent / "CV"
    
    if not cv_folder.exists():
        print(f"Error: CV folder not found at {cv_folder}")
        return
    
    # Get all PDF files
    cv_files = list(cv_folder.glob("*.pdf"))
    
    if not cv_files:
        print(f"Error: No PDF files found in {cv_folder}")
        return
    
    print(f"Found {len(cv_files)} CV files to test")
    
    # Test each CV
    results = []
    for cv_file in sorted(cv_files):
        result = test_cv_file(cv_file, use_llm=True)
        results.append(result)
    
    # Save results to JSON
    output_file = script_dir / "cv_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total_files": len(cv_files),
            "successful": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success")),
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Test Summary")
    print(f"{'='*60}")
    print(f"Total files: {len(cv_files)}")
    print(f"Successful: {sum(1 for r in results if r.get('success'))}")
    print(f"Failed: {sum(1 for r in results if not r.get('success'))}")
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()

