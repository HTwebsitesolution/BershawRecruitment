# Recruit Assist API (FastAPI skeleton)

### Install & run
```bash
# Install dependencies (including dev dependencies for testing)
pip install -e ".[dev]"

# Run the server
uvicorn app.main:app --reload
```

### Environment Variables

For LLM-based features, create a `.env` file in the `recruit-assist-api` directory:

```bash
# Required for LLM features (endorsement generation, outreach personalization)
OPENAI_API_KEY=YOUR_NEW_ROTATED_KEY_HERE
```

**Note**: If `OPENAI_API_KEY` is not set, services will automatically fallback to rule-based/template-based implementations for testing purposes.

#### Local Development

```bash
# Set environment variable
export OPENAI_API_KEY=YOUR_NEW_ROTATED_KEY_HERE

# Run the server
uvicorn app.main:app --reload
```

#### Docker

**Important**: Pass the API key at runtime (don't bake it into the image):

```bash
# Build the image
docker build -t recruit-assist-api:dev .

# Run with environment variable
docker run -p 8000:8000 --env OPENAI_API_KEY=YOUR_NEW_ROTATED_KEY_HERE recruit-assist-api:dev
```

If using Docker Compose, reference the `.env` file:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
```

### Running tests
```bash
# From project root
pip install -e ".[dev]"
pytest

# For coverage
pytest --cov=app --cov-report=term-missing

# In Docker (optional quick check)
docker build -t recruit-assist-api:dev .
docker run --rm -it recruit-assist-api:dev pytest
```

## Endpoints

**POST /ingest/cv** — form-data file field `file` → normalized candidate JSON (mock parser now)

**POST /normalize/jd** — `{ text?: string, ... }` → normalized JD JSON

**POST /endorsement/generate** —

```json
{
  "candidate": { ...CandidateCVNormalized... },
  "job": { ...JobDescriptionNormalized... },
  "interview": { ...InterviewSnapshot... }
}
```

## Example payload for /endorsement/generate

```json
{
  "candidate": {
    "candidate": {
      "full_name": "Alex Morgan",
      "email": "alex@example.com",
      "location": { "city": "Leeds", "country": "UK", "remote_preference": "hybrid" }
    },
    "experience": [
      { "title": "Senior Backend Engineer", "employer": "FintechCo", "start_date": "2022-01", "is_current": true,
        "technologies": ["Node.js", "TypeScript", "Postgres", "AWS ECS"],
        "achievements": ["Reduced p95 latency by 40%"] }
    ],
    "skills": [ { "name": "Node.js" }, { "name": "AWS" }, { "name": "SQL" } ]
  },
  "job": {
    "job": {
      "title": "Senior Backend Engineer",
      "client": "RetailTech Ltd",
      "location_policy": "hybrid",
      "primary_location": { "city": "Manchester", "country": "UK" }
    },
    "requirements": {
      "must_haves": [
        { "name": "Node.js & TypeScript", "weight": 0.25 },
        { "name": "AWS (Lambda/ECS/RDS)", "weight": 0.25 },
        { "name": "SQL & data modelling", "weight": 0.15 }
      ],
      "nice_to_haves": [ { "name": "Kafka/event-driven" } ],
      "years_experience_min": 5
    }
  },
  "interview": {
    "notice_period_weeks": 4,
    "motivation": "Wants broader architecture ownership.",
    "location_prefs": "Hybrid; 2–3 days in Leeds/Manchester",
    "target_comp": { "base_min": 85000, "base_max": 92000, "currency": "GBP", "period": "year" }
  }
}
```
