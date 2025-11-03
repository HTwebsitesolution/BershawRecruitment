from __future__ import annotations
from typing import Optional
from app.models import JobDescriptionNormalized, JobCore, Requirements, RequirementItem, PrimaryLocation, SalaryBand

# Very light heuristic normaliser from free text
def normalize_jd(
    text: Optional[str] = None,
    *,
    title: Optional[str] = None,
    client: Optional[str] = None,
    location_policy: Optional[str] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    currency: Optional[str] = "GBP",
) -> JobDescriptionNormalized:
    # Fallbacks for demo
    title = title or "Senior Backend Engineer"
    client = client or "RetailTech Ltd"
    location_policy = location_policy or "hybrid"

    musts = [
        RequirementItem(name="Node.js & TypeScript", weight=0.25),
        RequirementItem(name="AWS (Lambda/ECS/RDS)", weight=0.25),
        RequirementItem(name="SQL & data modelling", weight=0.15)
    ]
    nices = [RequirementItem(name="Kafka/event-driven", weight=0.05), RequirementItem(name="Kubernetes", weight=0.05)]

    job = JobCore(
        title=title,
        client=client,
        department="Engineering",
        location_policy=location_policy,  # type: ignore[arg-type]
        onsite_days_per_week=2 if location_policy == "hybrid" else None,
        primary_location=PrimaryLocation(city=city or "Manchester", country=country or "UK"),
        salary_band=SalaryBand(min=salary_min or 85000, max=salary_max or 95000, currency=currency, period="year"),
        visa_sponsorship="case_by_case",
        hiring_urgency="this_quarter",
    )

    reqs = Requirements(
        must_haves=musts,
        nice_to_haves=nices,
        years_experience_min=5
    )

    return JobDescriptionNormalized(job=job, requirements=reqs, role_notes="Normalized from free text JD.")

