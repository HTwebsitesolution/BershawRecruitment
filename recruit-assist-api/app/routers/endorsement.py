from __future__ import annotations
from fastapi import APIRouter
from app.models import CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot, EndorsementOut
from app.services.endorsement_writer import write_endorsement

router = APIRouter(prefix="/endorsement", tags=["endorsement"])

class EndorsementIn(CandidateCVNormalized, total=False):  # not used directly, but keeping pattern in mind
    pass

@router.post("/generate", response_model=EndorsementOut)
async def generate_endorsement(
    payload: dict
) -> EndorsementOut:
    """
    Accepts:
    {
      "candidate": CandidateCVNormalized,
      "job": JobDescriptionNormalized,
      "interview": InterviewSnapshot
    }
    """
    # Pydantic-validate nested payload
    cv = CandidateCVNormalized.model_validate(payload.get("candidate"))
    jd = JobDescriptionNormalized.model_validate(payload.get("job"))
    interview = InterviewSnapshot.model_validate(payload.get("interview", {}))
    return write_endorsement(cv=cv, jd=jd, interview=interview)

