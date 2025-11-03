from __future__ import annotations
from typing import Optional
from datetime import datetime
from app.models import (
    CandidateCVNormalized, CandidateIdentity, Location, ExperienceItem, Skill, Documents, ExtractionMeta
)

# Placeholder "parser". Swap for your real PDF/DOCX parser later.
def parse_cv_bytes_to_normalized(
    data: bytes, filename: Optional[str] = None, parser_version: str = "cvx-1.0.0"
) -> CandidateCVNormalized:
    # In a demo, we can't parse real files. Return a sensible mocked structure.
    # Use the filename to seed mock names to make demos feel real.
    base_name = (filename or "candidate").split(".")[0].replace("_", " ").title()

    candidate = CandidateIdentity(
        full_name=f"{base_name}",
        email="candidate@example.com",
        phone="+44 7700 900000",
        linkedin_url="https://www.linkedin.com/in/example",
        location=Location(city="Manchester", country="UK", remote_preference="hybrid"),
        right_to_work=["UK"],
        notice_period_weeks=None,  # unknown until interview
    )

    experience = [
        ExperienceItem(
            title="Senior Backend Engineer",
            employer="FintechCo",
            location="Manchester",
            start_date="2022-01",
            end_date=None,
            is_current=True,
            responsibilities=["Design REST APIs", "Own on-call"],
            achievements=["Reduced p95 latency by 40%"],
            technologies=["Node.js", "TypeScript", "Postgres", "AWS ECS"],
            team_size=3,
        )
    ]

    skills = [
        Skill(name="Node.js", category="tech", level="expert", evidence=["Built high-throughput APIs"]),
        Skill(name="AWS", category="tech", level="advanced", evidence=["ECS, RDS in production"]),
        Skill(name="SQL", category="tech", level="advanced")
    ]

    documents = Documents(resume_url="https://files.example.com/resume/mock.pdf")

    meta = ExtractionMeta(source="pdf", extracted_at=datetime.utcnow(), parser_version=parser_version)

    return CandidateCVNormalized(
        candidate=candidate,
        experience=experience,
        skills=skills,
        documents=documents,
        extraction_meta=meta
    )

