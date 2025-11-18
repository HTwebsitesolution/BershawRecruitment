# Job Posting Endpoints Documentation

Complete CRUD endpoints for managing job postings in the database.

## Endpoints

### 1. Create Job Posting

**POST** `/jobs/`

Create a new job posting from normalized JD data.

**Request Body:**
```json
{
  "jd_data": {
    "job": {
      "title": "Senior Backend Engineer",
      "client": "TechCorp",
      "department": "Engineering",
      "location_policy": "hybrid",
      "primary_location": {
        "city": "London",
        "country": "UK"
      },
      "salary_band": {
        "min": 85000,
        "max": 95000,
        "currency": "GBP",
        "period": "year"
      }
    },
    "requirements": {
      "must_haves": [
        {"name": "Node.js & TypeScript", "weight": 0.25}
      ],
      "nice_to_haves": []
    }
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "title": "Senior Backend Engineer",
  "client": "TechCorp",
  "status": "active",
  ...
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "jd_data": {
      "job": {
        "title": "Senior Engineer",
        "client": "TechCorp",
        "location_policy": "hybrid"
      },
      "requirements": {
        "must_haves": []
      }
    }
  }'
```

### 2. List Job Postings

**GET** `/jobs/`

List job postings with filtering and pagination.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100, max: 1000)
- `search`: Search term (searches title, client, department)
- `status`: Filter by status (active, closed, filled, archived)
- `client`: Filter by client name
- `location_country`: Filter by country
- `hiring_urgency`: Filter by urgency (asap, this_quarter, next_quarter)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "Senior Backend Engineer",
    "client": "TechCorp",
    "status": "active",
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

**Examples:**
```bash
# List all active jobs
curl "http://localhost:8000/jobs/?status=active"

# Search for jobs
curl "http://localhost:8000/jobs/?search=engineer&location_country=UK"

# Filter by client
curl "http://localhost:8000/jobs/?client=TechCorp&hiring_urgency=asap"
```

### 3. Get Job Posting Details

**GET** `/jobs/{job_id}`

Get a job posting by ID with full details.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "title": "Senior Backend Engineer",
  "client": "TechCorp",
  "requirements": {
    "must_haves": [...],
    "nice_to_haves": [...]
  },
  "interview_process": [...],
  "role_notes": "...",
  ...
}
```

**Example:**
```bash
curl "http://localhost:8000/jobs/{job_id}"
```

### 4. Update Job Posting

**PATCH** `/jobs/{job_id}`

Update a job posting. Only provided fields will be updated.

**Request Body:**
```json
{
  "status": "closed",
  "hiring_urgency": "this_quarter"
}
```

**Response:** `200 OK` (updated job posting details)

**Example:**
```bash
curl -X PATCH "http://localhost:8000/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"status": "closed"}'
```

### 5. Delete Job Posting

**DELETE** `/jobs/{job_id}`

Soft delete a job posting (sets status to 'archived').

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Job posting {job_id} archived successfully",
  "job_id": "uuid"
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/jobs/{job_id}"
```

## Normalize and Save to Database

You can normalize a JD and save it to the database in one step:

**POST** `/normalize/jd?save_to_db=true`

**Example:**
```bash
curl -X POST "http://localhost:8000/normalize/jd?use_llm=true&save_to_db=true" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "We are looking for a Senior Backend Engineer...",
    "title": "Senior Backend Engineer",
    "client": "TechCorp"
  }'
```

This will:
1. Normalize the JD (using LLM if `use_llm=true`)
2. Save it to database as a job posting (if `save_to_db=true`)
3. Return the normalized JD data

## Integration with Existing Workflow

### Current Flow:
1. Normalize JD via `/normalize/jd` → Get normalized JD
2. Upload CV via `/ingest/cv` → Get normalized CV
3. Generate endorsement via `/endorsement/generate` (using normalized data)

### New Flow with Database:
1. Normalize JD via `/normalize/jd?save_to_db=true` → JD saved to database, returns normalized JD
2. Upload CV via `/ingest/cv?save_to_db=true&consent_granted=true` → CV saved to database, returns normalized CV
3. Generate endorsement via `/endorsement/generate` → Uses normalized data (can also fetch from DB by ID)
4. Query candidates via `/candidates/` → List all candidates
5. Query jobs via `/jobs/` → List all job postings

## Database Schema

Job postings are stored in the `job_postings` table with:
- All job core fields (title, client, location, salary, etc.)
- Requirements as JSON (must_haves, nice_to_haves)
- Interview process as JSON array
- Original text (if provided)
- Normalization metadata (date, version)
- Status (active, closed, filled, archived)

## Next Steps

With job postings and candidates in the database, you can now:
1. ✅ Create job postings
2. ✅ Create candidates
3. ⏭️ **Implement candidate matching** - Match candidates to jobs (next task)
4. ⏭️ Create candidate profiles - Link candidates to specific jobs
5. ⏭️ Store match scores and recommendations

