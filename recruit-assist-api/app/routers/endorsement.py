from __future__ import annotations
import logging
from fastapi import APIRouter, Query
from pydantic import ValidationError as PydanticValidationError
from app.models import CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot, EndorsementOut
from app.services.endorsement_writer import write_endorsement
from app.services.endorsement_llm import generate_endorsement_llm
from app.exceptions import ValidationError, ParseError, LLMError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/endorsement", tags=["endorsement"])


@router.post("/generate", response_model=EndorsementOut)
async def generate_endorsement(
    payload: dict,
    use_llm: bool = Query(False, description="Use LLM-based generation (requires OPENAI_API_KEY)")
) -> EndorsementOut:
    """
    Generate a candidate endorsement based on CV, JD, and interview data.
    
    **Input Requirements:**
    - `candidate`: CandidateCVNormalized object (required)
    - `job`: JobDescriptionNormalized object (required)
    - `interview`: InterviewSnapshot object (optional, defaults to empty)
    
    **Output:**
    - EndorsementOut with endorsement text, recommendation, and fit ratings
    """
    try:
        # Validate required fields
        if "candidate" not in payload:
            raise ValidationError(
                "Missing required field: 'candidate'",
                detail="Please provide a 'candidate' field with CandidateCVNormalized data"
            )
        
        if "job" not in payload:
            raise ValidationError(
                "Missing required field: 'job'",
                detail="Please provide a 'job' field with JobDescriptionNormalized data"
            )
        
        # Parse and validate input models
        try:
            cv = CandidateCVNormalized.model_validate(payload.get("candidate"))
            jd = JobDescriptionNormalized.model_validate(payload.get("job"))
            interview = InterviewSnapshot.model_validate(payload.get("interview", {}))
        except PydanticValidationError as e:
            raise ValidationError(
                "Invalid input data structure",
                detail=f"Validation failed: {str(e)}"
            ) from e
        
        # Generate endorsement
        try:
            if use_llm:
                logger.info("Generating endorsement with LLM")
                return generate_endorsement_llm(cv, jd, interview)
            else:
                logger.info("Generating endorsement with rule-based writer")
                return write_endorsement(cv=cv, jd=jd, interview=interview)
        
        except Exception as e:
            # Check if it's already a RecruitAssistException
            if isinstance(e, (ParseError, ValidationError, LLMError)):
                raise
            
            # Generic errors
            logger.error(f"Error generating endorsement: {str(e)}", exc_info=e)
            raise ParseError(
                f"Failed to generate endorsement: {str(e)}",
                detail="Please ensure all input data is valid and try again"
            )
    
    except (ValidationError, ParseError, LLMError):
        # Re-raise our custom exceptions
        raise
    
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in generate_endorsement: {str(e)}", exc_info=e)
        raise ParseError(
            "An unexpected error occurred while generating the endorsement",
            detail=str(e)
        )

