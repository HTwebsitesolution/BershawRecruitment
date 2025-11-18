from __future__ import annotations
import logging
from fastapi import APIRouter, UploadFile, File, Query, Depends
from sqlalchemy.orm import Session
from app.models import CandidateCVNormalized
from app.database import get_db
from app.services.cv_parser import parse_cv_bytes_to_normalized
from app.services.cv_parser_llm import parse_cv_bytes_to_normalized_llm
from app.services.candidate_service import create_candidate, candidate_db_to_response
from app.exceptions import ParseError, FileError, LLMError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingest"])

# File size limits (10MB for CV uploads)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


@router.post("/cv", response_model=CandidateCVNormalized)
async def ingest_cv(
    file: UploadFile = File(...),
    use_llm: bool = Query(False, description="Use LLM-based extraction (requires OPENAI_API_KEY)"),
    save_to_db: bool = Query(False, description="Save parsed CV to database"),
    consent_granted: bool = Query(False, description="Whether consent has been granted for data processing"),
    db: Session = Depends(get_db)
) -> CandidateCVNormalized:
    """
    Upload a CV (PDF/DOCX/TXT) and receive normalized Candidate JSON.
    
    - Default: Uses stub parser (returns mock data for demo)
    - With ?use_llm=true: Uses LLM-based extraction from actual CV content
      (requires OPENAI_API_KEY to be set in environment)
    
    **File Requirements:**
    - Maximum size: 10MB
    - Allowed formats: PDF, DOCX, DOC, TXT
    """
    try:
        # Validate file extension
        if file.filename:
            file_ext = "." + file.filename.lower().split(".")[-1] if "." in file.filename else ""
            if file_ext not in ALLOWED_EXTENSIONS:
                raise FileError(
                    f"Unsupported file format: {file_ext}",
                    detail=f"Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
                )
        
        # Read file data
        data = await file.read()
        
        # Validate file size
        if len(data) > MAX_FILE_SIZE:
            raise FileError(
                f"File too large: {len(data) / 1024 / 1024:.2f}MB",
                detail=f"Maximum file size is {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        if len(data) == 0:
            raise FileError(
                "File is empty",
                detail="Please upload a non-empty file"
            )
        
        # Parse CV
        try:
            if use_llm:
                logger.info(f"Parsing CV with LLM: {file.filename} ({len(data)} bytes)")
                cv_data = parse_cv_bytes_to_normalized_llm(data, filename=file.filename)
            else:
                logger.info(f"Parsing CV with stub parser: {file.filename} ({len(data)} bytes)")
                cv_data = parse_cv_bytes_to_normalized(data, filename=file.filename)
            
            # Save to database if requested
            if save_to_db:
                try:
                    candidate = create_candidate(db, cv_data, consent_granted=consent_granted)
                    logger.info(f"Saved candidate to database: {candidate.id} ({candidate.full_name})")
                except Exception as e:
                    logger.error(f"Failed to save candidate to database: {e}", exc_info=e)
                    # Don't fail the request if database save fails
                    # Return the parsed CV data anyway
            
            return cv_data
        
        except ValueError as e:
            # Pydantic validation errors
            raise ValidationError(
                f"Invalid CV data structure: {str(e)}",
                detail="The parsed CV data does not match the expected schema"
            )
        
        except Exception as e:
            # Check if it's already a RecruitAssistException
            if isinstance(e, (ParseError, FileError, ValidationError, LLMError)):
                raise
            
            # Generic parsing errors
            logger.error(f"Error parsing CV: {str(e)}", exc_info=e)
            raise ParseError(
                f"Failed to parse CV: {str(e)}",
                detail="Please ensure the file is a valid PDF, DOCX, or text file and try again"
            )
    
    except (FileError, ParseError, ValidationError, LLMError):
        # Re-raise our custom exceptions
        raise
    
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in ingest_cv: {str(e)}", exc_info=e)
        raise ParseError(
            "An unexpected error occurred while processing the CV",
            detail=str(e)
        )

