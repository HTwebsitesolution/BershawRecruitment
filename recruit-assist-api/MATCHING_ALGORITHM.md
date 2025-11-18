# Candidate Matching Algorithm

Intelligent matching system that scores candidates against job postings based on multiple factors.

## Overview

The matching algorithm calculates a **match score** (0.0 to 1.0) by evaluating:

1. **Skills Match** (45% total weight)
   - Must-have skills: **35%** weight
   - Nice-to-have skills: **10%** weight
   
2. **Experience Match** (20% weight)
   - Years of experience vs. requirement
   
3. **Location Match** (15% weight)
   - Country match
   - City match (bonus)
   - Remote preference compatibility
   
4. **Salary Match** (10% weight)
   - Target salary vs. job salary range
   - Currency match
   
5. **Right to Work** (10% weight)
   - Visa/work authorization match

## Scoring Details

### Skills Matching

- **Exact Match** (score: 1.0): Skill name matches requirement exactly (case-insensitive, bidirectional)
- **Partial Match** (score: 0.5): 50%+ token overlap between skill and requirement
- **No Match** (score: 0.0): No overlap

**Example:**
- Requirement: "Node.js & TypeScript"
- Candidate has: "Node.js" → Exact match (1.0)
- Candidate has: "TypeScript" → Exact match (1.0)
- Candidate has: "JavaScript" → Partial match (0.5) if "JS" overlaps with requirement

### Experience Matching

- **Meets/Exceeds** (score: 1.0): Candidate has >= required years
- **Close** (score: 0.8): Candidate has >= 80% of required years
- **Somewhat Close** (score: 0.6): Candidate has >= 60% of required years
- **Below** (score: proportion): Score = actual_years / required_years

**Example:**
- Required: 5 years
- Candidate has: 5+ years → 1.0
- Candidate has: 4 years → 0.8
- Candidate has: 3 years → 0.6

### Location Matching

**Right to Work** (30% of location score):
- Match if candidate can work in job's country

**Country Match** (40% of location score):
- Match if candidate's country == job's country
- **City Match** (20% bonus): Additional score if cities match

**Remote Compatibility** (30% of location score):
- Remote jobs: Work for anyone
- Hybrid jobs: Work for remote/hybrid candidates
- Onsite jobs: Work for onsite/hybrid candidates

### Salary Matching

- **Within Range** (score: 1.0): Candidate's target is within job's salary range
- **Overlap** (score: 0.5-1.0): Ranges overlap (proportional to overlap size)
- **Above Range** (score: 0.0-0.5): Candidate expects more (penalty based on distance)
- **Below Range** (score: 0.7): Candidate expects less (acceptable, slight penalty)
- **Currency Mismatch** (score: 0.3): Different currencies

## API Endpoints

### 1. Match Candidate to Job

**POST** `/matching/match`

Match a specific candidate to a job posting.

**Request:**
```json
{
  "candidate_id": "uuid",
  "job_id": "uuid",
  "create_profile": true
}
```

**Response:**
```json
{
  "success": true,
  "candidate_id": "uuid",
  "job_id": "uuid",
  "candidate_name": "John Doe",
  "job_title": "Senior Backend Engineer",
  "job_client": "TechCorp",
  "match_score": 0.875,
  "match_percentage": 87.5,
  "match_details": {
    "overall_score": 0.875,
    "skills": {
      "must_have_score": 1.0,
      "must_have_matches": [...],
      "nice_have_score": 0.5,
      ...
    },
    "experience": {...},
    "location": {...},
    "salary": {...},
    "breakdown": {...}
  },
  "profile_id": "uuid"
}
```

### 2. Get Matched Candidates for a Job

**GET** `/matching/jobs/{job_id}/candidates`

Get all candidates matched to a job, ranked by match score.

**Query Parameters:**
- `min_score`: Minimum match score (0.0 to 1.0, default: 0.0)
- `limit`: Maximum results (default: 50, max: 500)

**Response:**
```json
[
  {
    "candidate_id": "uuid",
    "job_id": "uuid",
    "match_score": 0.875,
    "candidate_name": "John Doe",
    "job_title": "Senior Backend Engineer",
    "job_client": "TechCorp",
    "match_details": {...}
  }
]
```

### 3. Get Matched Jobs for a Candidate

**GET** `/matching/candidates/{candidate_id}/jobs`

Get all jobs matched to a candidate, ranked by match score.

**Query Parameters:**
- `min_score`: Minimum match score (default: 0.0)
- `limit`: Maximum results (default: 50)

**Response:** Same format as above, but with jobs instead of candidates

### 4. Get Top Candidates (Convenience)

**GET** `/matching/jobs/{job_id}/candidates/top`

Get top N candidates for a job (default: min_score=0.5, top_n=10).

**Query Parameters:**
- `top_n`: Number of top candidates (default: 10, max: 100)
- `min_score`: Minimum match score (default: 0.5)

### 5. Get Recommended Jobs (Convenience)

**GET** `/matching/candidates/{candidate_id}/jobs/recommended`

Get top N recommended jobs for a candidate (default: min_score=0.5, top_n=10).

**Query Parameters:**
- `top_n`: Number of recommended jobs (default: 10, max: 100)
- `min_score`: Minimum match score (default: 0.5)

## Usage Examples

### Example 1: Find best candidates for a job

```bash
# Get top 10 candidates for a job (min 50% match)
curl "http://localhost:8000/matching/jobs/{job_id}/candidates/top?top_n=10&min_score=0.5"
```

### Example 2: Get all candidates above 70% match

```bash
curl "http://localhost:8000/matching/jobs/{job_id}/candidates?min_score=0.7"
```

### Example 3: Find recommended jobs for a candidate

```bash
# Get top 5 recommended jobs
curl "http://localhost:8000/matching/candidates/{candidate_id}/jobs/recommended?top_n=5"
```

### Example 4: Match specific candidate to job

```bash
curl -X POST "http://localhost:8000/matching/match" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "uuid",
    "job_id": "uuid",
    "create_profile": true
  }'
```

## Match Score Interpretation

- **0.9 - 1.0**: Excellent match (strong candidate)
- **0.7 - 0.89**: Good match (viable candidate)
- **0.5 - 0.69**: Fair match (consider if other factors align)
- **0.0 - 0.49**: Poor match (likely not suitable)

## Performance

- **Bulk Matching**: Optimized to handle 100+ candidates/jobs efficiently
- **Caching**: Match scores are stored in CandidateProfile table (can be updated)
- **Pagination**: Results are limited and paginated for performance

## Integration with Profiles

When `create_profile=true`, the matching system automatically:

1. Creates a `CandidateProfile` record linking candidate to job
2. Stores match score and detailed breakdown
3. Updates existing profile if match already exists
4. Enables tracking of candidate status (shortlisted, rejected, etc.)

## Future Enhancements

Potential improvements:

1. **LLM-Based Matching**: Use embeddings for semantic skill matching
2. **Custom Weights**: Allow per-job weight configuration
3. **Industry Context**: Factor in industry experience
4. **Team Size Match**: Match based on previous team sizes
5. **Education Match**: Factor in education requirements
6. **Certification Match**: Match based on certifications
7. **A/B Testing**: Compare matching algorithm versions

## Configuration

Matching weights can be adjusted in `app/services/matching_service.py`:

```python
WEIGHTS = {
    "skills_must_have": 0.35,
    "skills_nice_have": 0.10,
    "experience": 0.20,
    "location": 0.15,
    "salary": 0.10,
    "right_to_work": 0.10,
}
```

**Note:** Weights should sum to 1.0 for accurate scoring.

