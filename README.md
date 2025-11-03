# Bershaw Recruitment

CV processing and candidate management system with normalized JSON schema definitions.

## Schema Definitions

### Candidate CV Normalized Schema

The `schemas/candidate_cv_normalized.json` file defines the normalized structure for extracting and storing candidate CV information. This schema includes:

- **Candidate Information**: Personal details, contact information, location, work authorization, compensation expectations
- **Experience**: Employment history with roles, responsibilities, achievements, and technologies used
- **Skills**: Technical and soft skills with proficiency levels and evidence
- **Education**: Academic background
- **Certifications**: Professional certifications
- **Languages**: Language proficiencies
- **Documents**: Links to resume and cover letter files
- **Extraction Metadata**: Source information and parser version

### Job Description Normalized Schema

The `schemas/job_description_normalized.json` file defines the normalized structure for extracting and storing job description information. This schema includes:

- **Job Information**: Title, client, department, location policy, salary band, visa sponsorship, clearance requirements, hiring urgency
- **Requirements**: Must-have and nice-to-have skills with weighted scoring, minimum years of experience, education requirements
- **Interview Process**: Stages with duration, participants, and assessment focus
- **Role Notes**: Additional context and notes about the role

## Usage

These schemas can be used for:
- Validating extracted CV and job description data
- Standardizing parsing outputs from various sources
- API request/response validation
- Database schema design
- Matching candidates to job requirements

## Prompt Library

### Endorsement Prompt (few-shot ready)

See `prompts/endorsement_prompt.txt` for a structured prompt to generate concise, audit-friendly candidate endorsements grounded in evidence from CVs and interviews.

Inputs:
- `CandidateCVNormalized` JSON
- `JobDescriptionNormalized` JSON
- `Interview` JSON (notice_period_weeks?, target_comp?, motivation?, location_prefs?, top_skills[]?, risks[]?, transcript_text)

Output: Plain text endorsement with fit ratings, evidence quotes, and recommendation.

## Schema Validation

The schema follows JSON Schema Draft 7 specification and can be used with any JSON Schema validator.

