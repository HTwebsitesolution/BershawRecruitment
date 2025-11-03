from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.models import JobDescriptionNormalized
from app.services.jd_normalizer import normalize_jd

router = APIRouter(prefix="/normalize", tags=["normalize"])

class JDNormalizeIn(BaseModel):
    text: Optional[str] = None
    title: Optional[str] = None
    client: Optional[str] = None
    location_policy: Optional[str] = None  # 'onsite'|'hybrid'|'remote'
    city: Optional[str] = None
    country: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = "GBP"

@router.post("/jd", response_model=JobDescriptionNormalized)
async def normalize_jd_endpoint(payload: JDNormalizeIn) -> JobDescriptionNormalized:
    """
    Accepts free-text JD or structured hints and returns normalized JD JSON.
    """
    return normalize_jd(
        text=payload.text,
        title=payload.title,
        client=payload.client,
        location_policy=payload.location_policy,
        city=payload.city,
        country=payload.country,
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        currency=payload.currency
    )

