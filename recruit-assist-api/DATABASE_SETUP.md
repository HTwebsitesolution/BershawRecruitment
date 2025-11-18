# Database Setup Guide

This guide explains how to set up PostgreSQL database for Bershaw Recruitment platform.

## Prerequisites

- PostgreSQL 12+ installed and running
- Python 3.10+ with pip

## Installation

### 1. Install Dependencies

```bash
cd recruit-assist-api
pip install -e ".[dev]"
```

This installs:
- SQLAlchemy 2.0+ (ORM)
- psycopg2-binary (PostgreSQL driver)
- Alembic (database migrations)

### 2. Set Up PostgreSQL Database

#### Option A: Local PostgreSQL

```bash
# Create database
createdb recruit_assist

# Or using psql
psql -U postgres
CREATE DATABASE recruit_assist;
```

#### Option B: Docker PostgreSQL

```bash
docker run --name recruit-assist-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=recruit_assist \
  -p 5432:5432 \
  -d postgres:15
```

### 3. Configure Database URL

Create or update `.env` file in `recruit-assist-api` directory:

```bash
# Database configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recruit_assist

# Debug mode (optional - logs SQL queries)
DEBUG=false

# OpenAI API key (for LLM features)
OPENAI_API_KEY=your_api_key_here
```

**Default Database URL Format:**
```
postgresql://username:password@host:port/database_name
```

### 4. Initialize Database

#### Option A: Using Alembic (Recommended)

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### Option B: Create Tables Directly

```bash
# Run Python script to create tables
python -c "from app.database import init_db; init_db()"
```

### 5. Verify Database Connection

```bash
# Check health endpoint
curl http://localhost:8000/healthz

# Should return:
# {
#   "ok": true,
#   "database": "connected",
#   "status": "healthy"
# }
```

## Database Schema

### Tables

1. **candidates** - Stores parsed CV data
   - Primary key: `id` (UUID)
   - Indexes: email, full_name, location, status, data_retention_until

2. **candidate_profiles** - Stores enriched candidate data for specific roles
   - Primary key: `id` (UUID)
   - Foreign key: `candidate_id` → candidates.id
   - Foreign key: `job_posting_id` → job_postings.id
   - Indexes: candidate_id, job_posting_id, status, match_score

3. **job_postings** - Stores normalized job descriptions
   - Primary key: `id` (UUID)
   - Indexes: title, client, location, status, hiring_urgency

### Relationships

- Candidate → CandidateProfile (one-to-many)
- JobPosting → CandidateProfile (one-to-many)

## Usage

### Upload CV and Save to Database

```bash
curl -X POST "http://localhost:8000/ingest/cv?use_llm=true&save_to_db=true&consent_granted=true" \
  -F "file=@CV/example.pdf"
```

### List Candidates

```bash
curl "http://localhost:8000/candidates/?skip=0&limit=100"
```

### Get Candidate Details

```bash
curl "http://localhost:8000/candidates/{candidate_id}"
```

### Search Candidates

```bash
curl "http://localhost:8000/candidates/?search=john&location_country=UK"
```

### Update Candidate

```bash
curl -X PATCH "http://localhost:8000/candidates/{candidate_id}" \
  -H "Content-Type: application/json" \
  -d '{"status": "archived"}'
```

### Delete Candidate (Soft Delete)

```bash
curl -X DELETE "http://localhost:8000/candidates/{candidate_id}"
```

## Database Migrations

### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Manual migration
alembic revision -m "Description of changes"
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific revision
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Migration History

```bash
# Show migration history
alembic history

# Show current revision
alembic current
```

## Data Retention (GDPR)

The database automatically manages data retention:

- Default retention period: 730 days (2 years)
- `data_retention_until` field stores expiry date
- Soft deletes used (status set to 'deleted')
- Audit logs for all data access

### Check Retention Status

```bash
curl "http://localhost:8000/compliance/retention/policy"
```

### Delete Expired Data

```bash
# TODO: Implement automated cleanup job
# This would be a scheduled task that:
# 1. Queries candidates where data_retention_until < now()
# 2. Soft deletes them (status = 'deleted')
# 3. Creates audit log entry
```

## Troubleshooting

### Connection Issues

**Error: "Connection refused"**
- Check PostgreSQL is running: `pg_isready` or `docker ps`
- Verify DATABASE_URL in `.env` file
- Check firewall/port 5432 is accessible

**Error: "Database does not exist"**
- Create database: `createdb recruit_assist`
- Or update DATABASE_URL to point to existing database

**Error: "Authentication failed"**
- Check username/password in DATABASE_URL
- Verify PostgreSQL user permissions

### Migration Issues

**Error: "Target database is not up to date"**
```bash
# Check current revision
alembic current

# Apply missing migrations
alembic upgrade head
```

**Error: "Can't locate revision"**
```bash
# Show history
alembic history

# Reset to specific revision (use with caution)
alembic downgrade <revision_id>
alembic upgrade head
```

## Production Checklist

- [ ] Use environment variables for database credentials
- [ ] Enable SSL/TLS for database connections
- [ ] Set up connection pooling (already configured)
- [ ] Configure automated backups
- [ ] Set up monitoring and alerting
- [ ] Implement automated retention policy enforcement
- [ ] Set up database replication (if needed)
- [ ] Configure database user permissions (least privilege)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://postgres:postgres@localhost:5432/recruit_assist` |
| `DEBUG` | Enable SQL query logging | `false` |

## Next Steps

1. ✅ Database setup complete
2. ⏭️ Create job posting endpoints (next)
3. ⏭️ Implement candidate matching algorithm
4. ⏭️ Add database indexes for performance
5. ⏭️ Set up automated backups

