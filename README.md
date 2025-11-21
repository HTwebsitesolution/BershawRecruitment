# Bershaw Recruitment Platform

AI-powered recruitment platform for end-to-end candidate management, from LinkedIn sourcing to AI interviews to hiring decisions.

## 🎯 Platform Overview

Bershaw Recruitment is a comprehensive AI-powered recruitment system that automates the entire hiring pipeline:

- **AI-Powered CV Parsing** - Extract structured data from PDF/DOCX CVs
- **LinkedIn Outreach Automation** - Chrome extension for personalized messaging
- **Intelligent Candidate Matching** - Multi-factor scoring algorithm
- **AI Interviewer/Messenger** - Automated interviews with GPT-4o
- **Evidence-Based Endorsements** - AI-generated candidate recommendations
- **GDPR Compliance** - Built-in data protection and retention

## 📚 Documentation

### Workflow & Process
- **[Complete Workflow](./COMPLETE_WORKFLOW.md)** - End-to-end process including AI Interviewer
- **[Workflow Summary](./WORKFLOW_SUMMARY.md)** - Quick reference guide
- **[Project Analysis](./PROJECT_ANALYSIS.md)** - Current status and where we left off
- **[Current Workflow](./recruit-assist-api/CURRENT_WORKFLOW.md)** - Detailed technical workflow

### Technical Documentation
- **[Backend API](./recruit-assist-api/README.md)** - FastAPI backend documentation
- **[Chrome Extension](./linkedin-outreach-assist/README.md)** - LinkedIn outreach assistant
- **[Web Frontend](./recruit-assist-web/README.md)** - Dashboard and UI

### Analysis & Planning
- **[Competitive Analysis](./COMPETITIVE_ANALYSIS.md)** - vs. Alfa AI (welovealfa.com)
- **[Checkpoint](./CHECKPOINT.md)** - Development status and next steps
- **[Challenges Implemented](./CHALLENGES_IMPLEMENTED.md)** - Technical challenges solved

## 🤖 Key Feature: AI Interviewer/Messenger

The **AI Interviewer** (AI Personnel) is the centerpiece of the platform:

- Conducts **automated interviews** with candidates via video/chat
- **Generates contextual questions** based on job requirements
- **Adapts in real-time** to candidate responses
- **Extracts deep insights** from conversations
- **Provides actionable recommendations** to recruiters

See [Complete Workflow](./COMPLETE_WORKFLOW.md#-ai-interviewermessenger-ai-personnel---detailed-flow) for detailed AI Interviewer flow.

## 🚀 Quick Start

### Backend API
```bash
cd recruit-assist-api
pip install -e ".[dev]"
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs
```

### Chrome Extension
```bash
cd linkedin-outreach-assist
npm install
npm run build
# Load unpacked extension in Chrome
```

## 📋 Schema Definitions

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

## 📖 Workflow Documentation

- **[Complete Workflow](./COMPLETE_WORKFLOW.md)** - Detailed end-to-end process with AI Interviewer
- **[Workflow Summary](./WORKFLOW_SUMMARY.md)** - Quick reference guide
- **[Visual Workflow](./WORKFLOW_VISUAL.md)** - Visual diagrams and flowcharts
- **[Project Analysis](./PROJECT_ANALYSIS.md)** - Current status and next steps

