# Testing Guide

This guide explains how to test the complete recruitment system.

## Prerequisites

1. **Database Setup**
   ```bash
   # Ensure PostgreSQL is running
   # Create database
   createdb recruit_assist
   
   # Or use Docker
   docker run --name recruit-assist-db \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=recruit_assist \
     -p 5432:5432 -d postgres:15
   ```

2. **Environment Variables**
   ```bash
   # Create .env file in recruit-assist-api/
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recruit_assist
   OPENAI_API_KEY=your_api_key_here  # Optional, for LLM features
   DEBUG=false
   ```

3. **Install Dependencies**
   ```bash
   cd recruit-assist-api
   pip install -e ".[dev]"
   ```

4. **Initialize Database**
   ```bash
   # Create tables
   python -c "from app.database import init_db; init_db()"
   
   # Or use Alembic (recommended)
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

5. **Start Server**
   ```bash
   cd recruit-assist-api
   uvicorn app.main:app --reload --port 8000
   ```

## Running Tests

### 1. Integration Test (Recommended)

Run the complete integration test that exercises the full workflow:

```bash
cd recruit-assist-api
python test_system_integration.py
```

**What it tests:**
- Health check and database connection
- JD normalization and database save
- CV upload and database save
- Candidate matching to job
- Profile operations (CRUD)
- Endorsement generation

**Expected output:**
```
============================================================
RECRUITMENT SYSTEM INTEGRATION TEST
============================================================
API Base URL: http://localhost:8000
Using LLM: True
============================================================

=== Testing Health Check ===
✓ Health check passed: {'ok': True, 'database': 'connected', 'status': 'healthy'}

=== Testing JD Normalization ===
✓ JD normalized successfully
  Title: Senior Backend Engineer
  Client: TechCorp
✓ Job saved to database: <uuid>

=== Testing CV Upload ===
✓ CV parsed successfully
  Name: John Doe
  Email: john.doe@example.com
✓ Candidate saved to database: <uuid>

=== Testing Candidate Matching ===
✓ Match successful
  Match score: 0.875 (87.5%)
  Profile ID: <uuid>
  Breakdown:
    must_have_skills_contribution: 0.350
    nice_have_skills_contribution: 0.050
    experience_contribution: 0.200
    location_contribution: 0.150
    salary_contribution: 0.100
    right_to_work_contribution: 0.100

=== Testing Get Job Candidates ===
✓ Found 1 candidates
  1. John Doe: 0.875

=== Testing Profile Operations ===
✓ Profile retrieved: John Doe - Senior Backend Engineer at TechCorp
✓ Interview data updated
✓ Status updated to: shortlisted

=== Testing Endorsement Generation ===
✓ Endorsement generated
  Text preview: Candidate: John Doe — Manchester, UK...

============================================================
INTEGRATION TEST COMPLETE
============================================================
```

### 2. Manual API Testing

#### Test Health Check
```bash
curl http://localhost:8000/healthz
```

#### Test JD Normalization
```bash
curl -X POST "http://localhost:8000/normalize/jd?use_llm=true&save_to_db=true" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "We are looking for a Senior Backend Engineer...",
    "title": "Senior Backend Engineer",
    "client": "TechCorp",
    "location_policy": "hybrid",
    "city": "London",
    "country": "UK",
    "salary_min": 85000,
    "salary_max": 95000,
    "currency": "GBP"
  }'
```

#### Test CV Upload
```bash
curl -X POST "http://localhost:8000/ingest/cv?use_llm=true&save_to_db=true&consent_granted=true" \
  -F "file=@CV/example.pdf"
```

#### Test Matching
```bash
# First, get candidate and job IDs from previous steps
curl -X POST "http://localhost:8000/matching/match" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "<candidate_id>",
    "job_id": "<job_id>",
    "create_profile": true
  }'
```

#### Test Get Job Candidates
```bash
curl "http://localhost:8000/matching/jobs/<job_id>/candidates/top?top_n=10&min_score=0.5"
```

#### Test Profile Operations
```bash
# Get profile
curl "http://localhost:8000/profiles/<profile_id>"

# Update interview data
curl -X PATCH "http://localhost:8000/profiles/<profile_id>/interview" \
  -H "Content-Type: application/json" \
  -d '{
    "interview_notes": "Strong candidate",
    "interview_data": {"motivation": "Looking for growth"}
  }'

# Update status
curl -X PATCH "http://localhost:8000/profiles/<profile_id>" \
  -H "Content-Type: application/json" \
  -d '{"status": "shortlisted"}'
```

### 3. Unit Tests

Run existing unit tests:

```bash
cd recruit-assist-api
pytest app/tests/ -v
```

## Common Issues

### Database Connection Failed

**Error:** `database: "disconnected"`

**Solution:**
1. Check PostgreSQL is running: `pg_isready` or `docker ps`
2. Verify DATABASE_URL in `.env` file
3. Check database exists: `psql -l | grep recruit_assist`

### LLM Features Not Working

**Error:** `LLM operation failed` or `OPENAI_API_KEY not configured`

**Solution:**
1. Set `OPENAI_API_KEY` in `.env` file
2. Or use `use_llm=false` to use rule-based/stub parsers

### Migration Errors

**Error:** `Target database is not up to date`

**Solution:**
```bash
# Check current revision
alembic current

# Apply migrations
alembic upgrade head
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill
```

## Test Data

### Sample JD Text
```
We are looking for a Senior Backend Engineer to join our team.

Requirements:
- 5+ years of experience with Node.js and TypeScript
- Strong experience with AWS (Lambda, ECS, RDS)
- SQL and data modelling skills
- Experience with event-driven architectures (Kafka)

Location: Hybrid (2-3 days in office)
Location: London, UK
Salary: £85,000 - £95,000 per year

Visa sponsorship: Case by case
Hiring urgency: This quarter
```

### Sample CV Text
```
John Doe
Email: john.doe@example.com
Phone: +44 7700 900000
Location: Manchester, UK

Experience:
Senior Backend Engineer at FintechCo (2022-01 to present)
- Design and implement REST APIs using Node.js and TypeScript
- Manage AWS infrastructure (ECS, RDS, Lambda)
- Optimize database queries and data models
Technologies: Node.js, TypeScript, PostgreSQL, AWS ECS, Kafka

Skills:
- Node.js (Expert)
- TypeScript (Expert)
- AWS (Advanced)
- SQL (Advanced)

Education:
BSc Computer Science, University of Manchester (2018-2021)

Right to work: UK
Notice period: 4 weeks
Target compensation: £85,000 - £90,000 per year
```

## Next Steps After Testing

Once tests pass:

1. ✅ Verify database tables are created
2. ✅ Check data is being saved correctly
3. ✅ Validate match scores are reasonable
4. ✅ Test with real CVs from your CV folder
5. ✅ Review match results for accuracy
6. ✅ Adjust matching weights if needed

## Performance Testing

For larger datasets:

```bash
# Test with multiple CVs
for file in CV/*.pdf; do
  curl -X POST "http://localhost:8000/ingest/cv?use_llm=true&save_to_db=true" \
    -F "file=@$file"
done

# Test matching performance
time curl "http://localhost:8000/matching/jobs/<job_id>/candidates?limit=100"
```

## Troubleshooting

### Check Logs
```bash
# Server logs will show detailed error messages
# Check terminal where uvicorn is running
```

### Database Inspection
```bash
# Connect to database
psql -U postgres -d recruit_assist

# Check tables
\dt

# Check candidates
SELECT id, full_name, email FROM candidates LIMIT 5;

# Check jobs
SELECT id, title, client FROM job_postings LIMIT 5;

# Check profiles
SELECT id, candidate_id, job_posting_id, match_score, status FROM candidate_profiles LIMIT 5;
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

