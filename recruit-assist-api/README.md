# Bershaw Recruitment Platform API

AI-powered recruitment system backend for parsing CVs, normalizing job descriptions, matching candidates to jobs, and managing the hiring pipeline.

## Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 12+
- OpenAI API Key (optional, for LLM features)

### 2. Installation

```bash
# Clone repository
cd recruit-assist-api

# Install dependencies
pip install -e ".[dev]"

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Or create tables directly
python -c "from app.database import init_db; init_db()"
```

### 3. Configuration

Create `.env` file:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recruit_assist
OPENAI_API_KEY=your_api_key_here  # Optional
OPENAI_TIMEOUT=60.0
DEBUG=false
```

### 4. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Test System

```bash
python test_system_integration.py
```

### 6. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

---

## Documentation

### Getting Started

- **[Project Summary](./PROJECT_SUMMARY.md)** - Complete overview of the system
- **[Testing Guide](./TESTING_GUIDE.md)** - How to test the system
- **[Database Setup](./DATABASE_SETUP.md)** - Database configuration guide

### API Documentation

- **[Job Posting Endpoints](./JOB_POSTING_ENDPOINTS.md)** - Job posting CRUD API
- **[Candidate Profile Endpoints](./CANDIDATE_PROFILE_ENDPOINTS.md)** - Profile management API
- **[Matching Algorithm](./MATCHING_ALGORITHM.md)** - How candidate matching works

### Compliance

- **[GDPR Compliance](./GDPR_COMPLIANCE.md)** - GDPR features and compliance guide

### Analysis

- **[Competitive Analysis](./COMPETITIVE_ANALYSIS.md)** - Comparison with Alfa AI

---

## Key Features

✅ **CV Parsing** - AI-powered extraction from PDF/DOCX/TXT  
✅ **JD Normalization** - Convert free-text to structured data  
✅ **Candidate Matching** - Multi-factor scoring algorithm  
✅ **Profile Management** - Track candidates through pipeline  
✅ **Endorsement Generation** - AI-powered candidate endorsements  
✅ **GDPR Compliance** - Data retention, consent, audit logging  
✅ **Database Integration** - PostgreSQL with SQLAlchemy ORM  

---

## API Endpoints

### Core Workflow

1. **Upload CV** → `POST /ingest/cv?save_to_db=true&consent_granted=true`
2. **Normalize JD** → `POST /normalize/jd?save_to_db=true`
3. **Match Candidate** → `POST /matching/match?create_profile=true`
4. **Get Matches** → `GET /matching/jobs/{id}/candidates/top`
5. **Update Profile** → `PATCH /profiles/{id}/interview`
6. **Generate Endorsement** → `POST /endorsement/generate?use_llm=true`

### Quick Reference

- **Health Check:** `GET /healthz`
- **API Info:** `GET /`
- **Interactive Docs:** `GET /docs` (Swagger UI)
- **ReDoc:** `GET /redoc`

See [Project Summary](./PROJECT_SUMMARY.md) for complete endpoint list.

---

## System Architecture

```
┌─────────────────┐
│   FastAPI App   │
├─────────────────┤
│  API Routers    │
│  - Ingest       │
│  - Normalize    │
│  - Matching     │
│  - Candidates   │
│  - Jobs         │
│  - Profiles     │
│  - Endorsement  │
│  - Compliance   │
└────────┬────────┘
         │
┌────────▼────────┐
│  Service Layer  │
│  - CV Parser    │
│  - JD Normalizer│
│  - Matching     │
│  - Endorsement  │
│  - Profile      │
└────────┬────────┘
         │
┌────────▼────────┐      ┌──────────────┐
│   PostgreSQL    │◄────►│   OpenAI     │
│   Database      │      │   (LLM)      │
└─────────────────┘      └──────────────┘
```

---

## Project Status

**Status:** ✅ Implementation Complete (Pending Testing)

### ✅ Completed

- Database setup (PostgreSQL + SQLAlchemy + Alembic)
- CV parsing (LLM-based + fallback)
- JD normalization (LLM-based + fallback)
- Candidate matching algorithm
- Profile management (CRUD)
- Endorsement generation
- GDPR compliance
- Comprehensive error handling
- API documentation

### 🔄 Pending

- Integration testing
- Performance validation
- Real-world CV testing

### ⏭️ Future

- Authentication/Authorization
- Web dashboard
- ATS integrations
- Analytics and reporting

---

## Development

### Project Structure

```
recruit-assist-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection
│   ├── settings.py          # Configuration
│   ├── models.py            # Pydantic models
│   ├── db_models.py         # SQLAlchemy models
│   ├── db_schemas.py        # Database schemas
│   ├── exceptions.py        # Custom exceptions
│   ├── routers/             # API endpoints
│   │   ├── ingest.py
│   │   ├── normalize.py
│   │   ├── matching.py
│   │   ├── candidates.py
│   │   ├── jobs.py
│   │   ├── profiles.py
│   │   ├── endorsement.py
│   │   ├── compliance.py
│   │   └── email.py
│   └── services/            # Business logic
│       ├── cv_parser_llm.py
│       ├── jd_normalizer_llm.py
│       ├── matching_service.py
│       ├── endorsement_llm.py
│       ├── candidate_service.py
│       ├── job_posting_service.py
│       └── profile_service.py
├── alembic/                 # Database migrations
├── tests/                   # Unit tests
├── .env                     # Environment variables
├── pyproject.toml           # Dependencies
└── README.md                # This file
```

### Running Tests

```bash
# Integration test
python test_system_integration.py

# Unit tests
pytest app/tests/ -v
```

### Code Style

```bash
# Format code (if black is installed)
black app/

# Type check (if mypy is installed)
mypy app/
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://postgres:postgres@localhost:5432/recruit_assist` |
| `OPENAI_API_KEY` | OpenAI API key (for LLM features) | (required for LLM) |
| `OPENAI_TIMEOUT` | OpenAI API timeout (seconds) | `60.0` |
| `DEBUG` | Enable debug mode (SQL logging) | `false` |

---

## License

[Your License Here]

---

## Support

For questions or issues, please refer to:
- [Project Summary](./PROJECT_SUMMARY.md) - Complete system overview
- [Testing Guide](./TESTING_GUIDE.md) - Testing instructions
- [API Documentation](./PROJECT_SUMMARY.md#api-endpoints) - Endpoint reference

---

**Version:** 0.1.0  
**Last Updated:** January 2025
