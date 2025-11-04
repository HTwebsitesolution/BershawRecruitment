from fastapi import APIRouter, Query
from app.models import CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot, EndorsementOut
from app.services.endorsement_writer import write_endorsement
from app.services.endorsement_llm import generate_endorsement_llm

router = APIRouter(prefix="/endorsement", tags=["endorsement"])

@router.post("/generate", response_model=EndorsementOut)
async def generate_endorsement(payload: dict, use_llm: bool = Query(False)):
    cv = CandidateCVNormalized.model_validate(payload.get("candidate"))
    jd = JobDescriptionNormalized.model_validate(payload.get("job"))
    interview = InterviewSnapshot.model_validate(payload.get("interview", {}))

    if use_llm:
        return generate_endorsement_llm(cv, jd, interview)
    return write_endorsement(cv=cv, jd=jd, interview=interview)

