# Candidate Profile Endpoints Documentation

Complete CRUD endpoints for managing candidate profiles that link candidates to jobs,
including match scores, endorsements, and interview data.

## Overview

Candidate Profiles represent the relationship between a candidate and a specific job posting.
They store:
- Match scores and details (from matching algorithm)
- Endorsements (text, recommendation, fit score)
- Interview data (date, notes, transcript, insights)
- Status (active, shortlisted, rejected, hired, archived)

## Endpoints

### 1. Create Profile

**POST** `/profiles/`

Create a new candidate profile.

**Request Body:**
```json
{
  "candidate_id": "uuid",
  "job_posting_id": "uuid",
  "profile_name": "Senior Engineer - TechCorp",
  "company_name": "TechCorp",
  "role_title": "Senior Backend Engineer",
  "interview_notes": "Initial screening completed",
  "interview_data": {
    "motivation": "Looking for new challenges",
    "target_comp": {"min": 85000, "max": 95000},
    "location_prefs": "Hybrid preferred"
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "candidate_id": "uuid",
  "job_posting_id": "uuid",
  "profile_name": "Senior Engineer - TechCorp",
  "status": "active",
  "created_at": "2025-01-15T10:30:00Z",
  ...
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/profiles/" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "uuid",
    "job_posting_id": "uuid",
    "profile_name": "Senior Engineer - TechCorp"
  }'
```

### 2. List Profiles

**GET** `/profiles/`

List candidate profiles with filtering.

**Query Parameters:**
- `candidate_id`: Filter by candidate ID
- `job_id`: Filter by job posting ID
- `status`: Filter by status (active, shortlisted, rejected, hired, archived)
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100, max: 1000)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "candidate_id": "uuid",
    "job_posting_id": "uuid",
    "profile_name": "Senior Engineer - TechCorp",
    "match_score": 0.875,
    "status": "active",
    ...
  }
]
```

**Examples:**
```bash
# List profiles for a candidate
curl "http://localhost:8000/profiles/?candidate_id={candidate_id}"

# List profiles for a job
curl "http://localhost:8000/profiles/?job_id={job_id}"

# List shortlisted profiles
curl "http://localhost:8000/profiles/?status=shortlisted"
```

### 3. Get Profile Details

**GET** `/profiles/{profile_id}`

Get a profile by ID with full details.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "candidate_id": "uuid",
  "job_posting_id": "uuid",
  "profile_name": "Senior Engineer - TechCorp",
  "interview_date": "2025-01-20T14:00:00Z",
  "interview_notes": "...",
  "interview_transcript": "...",
  "interview_data": {...},
  "endorsement_text": "...",
  "endorsement_recommendation": "Proceed",
  "endorsement_fit_score": 0.85,
  "match_score": 0.875,
  "match_details": {...},
  "status": "active",
  ...
}
```

**Example:**
```bash
curl "http://localhost:8000/profiles/{profile_id}"
```

### 4. Get Profiles for a Candidate

**GET** `/profiles/candidates/{candidate_id}/profiles`

Get all profiles for a specific candidate.

**Query Parameters:**
- `status`: Filter by status (optional)
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100)

**Response:** `200 OK` (list of profiles sorted by created_at, newest first)

**Example:**
```bash
curl "http://localhost:8000/profiles/candidates/{candidate_id}/profiles?status=active"
```

### 5. Get Profiles for a Job

**GET** `/profiles/jobs/{job_id}/profiles`

Get all profiles for a specific job posting.

**Query Parameters:**
- `status`: Filter by status (optional)
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100)

**Response:** `200 OK` (list of profiles sorted by match_score, best matches first)

**Example:**
```bash
curl "http://localhost:8000/profiles/jobs/{job_id}/profiles?status=shortlisted"
```

### 6. Update Profile

**PATCH** `/profiles/{profile_id}`

Update a profile. Only provided fields will be updated.

**Request Body:**
```json
{
  "status": "shortlisted",
  "profile_name": "Senior Engineer - TechCorp (Shortlisted)",
  "interview_notes": "Updated after interview"
}
```

**Response:** `200 OK` (updated profile details)

**Example:**
```bash
curl -X PATCH "http://localhost:8000/profiles/{profile_id}" \
  -H "Content-Type: application/json" \
  -d '{"status": "shortlisted"}'
```

### 7. Update Endorsement

**PATCH** `/profiles/{profile_id}/endorsement`

Update endorsement data for a profile.

**Request Body:**
```json
{
  "endorsement_text": "Strong candidate with excellent skills...",
  "endorsement_recommendation": "Proceed",
  "endorsement_fit_score": 0.85
}
```

**Response:** `200 OK` (updated profile details)

**Example:**
```bash
curl -X PATCH "http://localhost:8000/profiles/{profile_id}/endorsement" \
  -H "Content-Type: application/json" \
  -d '{
    "endorsement_recommendation": "Proceed",
    "endorsement_fit_score": 0.85
  }'
```

### 8. Update Interview Data

**PATCH** `/profiles/{profile_id}/interview`

Update interview data for a profile.

**Request Body:**
```json
{
  "interview_date": "2025-01-20T14:00:00Z",
  "interview_notes": "Strong technical skills, good cultural fit",
  "interview_transcript": "...",
  "interview_data": {
    "motivation": "Looking for growth opportunities",
    "top_skills": ["Node.js", "TypeScript", "AWS"],
    "risks": ["Notice period: 4 weeks"]
  }
}
```

**Response:** `200 OK` (updated profile details)

**Example:**
```bash
curl -X PATCH "http://localhost:8000/profiles/{profile_id}/interview" \
  -H "Content-Type: application/json" \
  -d '{
    "interview_date": "2025-01-20T14:00:00Z",
    "interview_notes": "Excellent candidate"
  }'
```

### 9. Update Match Data

**PATCH** `/profiles/{profile_id}/match`

Update match data for a profile (usually updated automatically by matching algorithm).

**Request Body:**
```json
{
  "match_score": 0.875,
  "match_details": {
    "overall_score": 0.875,
    "skills": {...},
    "experience": {...},
    ...
  }
}
```

**Response:** `200 OK` (updated profile details)

**Example:**
```bash
curl -X PATCH "http://localhost:8000/profiles/{profile_id}/match" \
  -H "Content-Type: application/json" \
  -d '{
    "match_score": 0.875,
    "match_details": {...}
  }'
```

### 10. Delete Profile

**DELETE** `/profiles/{profile_id}`

Soft delete a profile (sets status to 'archived').

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Profile {profile_id} archived successfully",
  "profile_id": "uuid"
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/profiles/{profile_id}"
```

## Integration with Matching System

Profiles are automatically created when matching candidates to jobs:

```bash
# Match candidate to job (creates profile if create_profile=true)
POST /matching/match
{
  "candidate_id": "uuid",
  "job_id": "uuid",
  "create_profile": true
}

# Response includes profile_id
{
  "profile_id": "uuid",
  "match_score": 0.875,
  ...
}
```

## Profile Status Values

- `active`: Profile is active (default)
- `shortlisted`: Candidate is shortlisted for the role
- `rejected`: Candidate has been rejected
- `hired`: Candidate has been hired
- `archived`: Profile is archived (soft deleted)

## Workflow Example

### Complete Profile Lifecycle

1. **Match candidate to job** (creates profile with match score):
```bash
POST /matching/match
{
  "candidate_id": "uuid",
  "job_id": "uuid",
  "create_profile": true
}
```

2. **Add interview data**:
```bash
PATCH /profiles/{profile_id}/interview
{
  "interview_date": "2025-01-20T14:00:00Z",
  "interview_notes": "Strong candidate"
}
```

3. **Generate and update endorsement**:
```bash
# Generate endorsement
POST /endorsement/generate?use_llm=true
{
  "candidate": {...},
  "job": {...},
  "interview": {...}
}

# Update profile with endorsement
PATCH /profiles/{profile_id}/endorsement
{
  "endorsement_text": "...",
  "endorsement_recommendation": "Proceed",
  "endorsement_fit_score": 0.85
}
```

4. **Update status**:
```bash
PATCH /profiles/{profile_id}
{
  "status": "shortlisted"
}
```

5. **Get all shortlisted profiles for a job**:
```bash
GET /profiles/jobs/{job_id}/profiles?status=shortlisted
```

## Use Cases

### 1. Track Candidate Through Pipeline

- Create profile when matching candidate to job
- Update status as candidate progresses (shortlisted → hired)
- Add interview data and notes at each stage
- Store endorsement and recommendation

### 2. Manage Multiple Candidates for a Job

- Get all profiles for a job (sorted by match score)
- Filter by status (shortlisted, rejected, etc.)
- Compare candidates side-by-side
- Update status as decisions are made

### 3. Track Candidate Applications

- Get all profiles for a candidate
- See all jobs they've been matched to
- Track application status for each role
- Review match scores and endorsements

## Next Steps

With profiles, you can now:
1. ✅ Link candidates to jobs
2. ✅ Store match scores and details
3. ✅ Track interview data
4. ✅ Store endorsements and recommendations
5. ✅ Manage candidate status through pipeline
6. ⏭️ Generate reports and analytics
7. ⏭️ Create candidate shortlists
8. ⏭️ Track hiring metrics

