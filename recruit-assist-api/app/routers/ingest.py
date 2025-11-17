from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Query
from app.models import CandidateCVNormalized
from app.services.cv_parser import parse_cv_bytes_to_normalized
from app.services.cv_parser_llm import parse_cv_bytes_to_normalized_llm

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/cv", response_model=CandidateCVNormalized)
async def ingest_cv(
    file: UploadFile = File(...),
    use_llm: bool = Query(False, description="Use LLM-based extraction (requires OPENAI_API_KEY)")
) -> CandidateCVNormalized:
    """
    Upload a CV (PDF/DOCX/TXT) and receive normalized Candidate JSON.
    
    - Default: Uses stub parser (returns mock data for demo)
    - With ?use_llm=true: Uses LLM-based extraction from actual CV content
      (requires OPENAI_API_KEY to be set in environment)
    """
    data = await file.read()
    
    if use_llm:
        return parse_cv_bytes_to_normalized_llm(data, filename=file.filename)
    else:
        return parse_cv_bytes_to_normalized(data, filename=file.filename)

