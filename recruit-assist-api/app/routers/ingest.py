from __future__ import annotations
from fastapi import APIRouter, UploadFile, File
from app.models import CandidateCVNormalized
from app.services.cv_parser import parse_cv_bytes_to_normalized

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/cv", response_model=CandidateCVNormalized)
async def ingest_cv(file: UploadFile = File(...)) -> CandidateCVNormalized:
    """
    Upload a CV (PDF/DOCX/TXT) and receive normalized Candidate JSON.
    NOTE: This is a demo parser returning mocked structured content.
    """
    data = await file.read()
    return parse_cv_bytes_to_normalized(data, filename=file.filename)

