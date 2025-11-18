from __future__ import annotations
import logging
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from app.models import JobDescriptionNormalized
from app.database import get_db
from app.services.jd_normalizer import normalize_jd
from app.services.jd_normalizer_llm import normalize_jd_llm
from app.services.job_posting_service import create_job_posting
from app.exceptions import ValidationError, ParseError, LLMError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/normalize", tags=["normalize"])

# Maximum text length for JD normalization (100KB)
MAX_TEXT_LENGTH = 100 * 1024


class JDNormalizeIn(BaseModel):
    text: Optional[str] = Field(None, max_length=MAX_TEXT_LENGTH, description="Free-text job description")
    title: Optional[str] = None
    client: Optional[str] = None
    location_policy: Optional[str] = Field(None, description="Location policy: 'onsite', 'hybrid', or 'remote'")
    city: Optional[str] = None
    country: Optional[str] = None
    salary_min: Optional[float] = Field(None, ge=0, description="Minimum salary")
    salary_max: Optional[float] = Field(None, ge=0, description="Maximum salary")
    currency: Optional[str] = Field("GBP", pattern="^[A-Z]{3}$", description="ISO 4217 currency code (3 letters)")
    
    @field_validator("location_policy")
    @classmethod
    def validate_location_policy(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in {"onsite", "hybrid", "remote"}:
            raise ValueError("location_policy must be one of: 'onsite', 'hybrid', 'remote'")
        return v
    
    @model_validator(mode='after')
    def validate_salary_range(self) -> 'JDNormalizeIn':
        """Validate that salary_max >= salary_min if both are provided."""
        if self.salary_max is not None and self.salary_min is not None:
            if self.salary_max < self.salary_min:
                raise ValueError("salary_max must be greater than or equal to salary_min")
        return self


@router.post("/jd", response_model=JobDescriptionNormalized)
async def normalize_jd_endpoint(
    payload: JDNormalizeIn,
    use_llm: bool = Query(False, description="Use LLM-based extraction (requires OPENAI_API_KEY)"),
    save_to_db: bool = Query(False, description="Save normalized JD to database"),
    db: Session = Depends(get_db)
) -> JobDescriptionNormalized:
    """
    Accepts free-text JD or structured hints and returns normalized JD JSON.
    
    - Default: Uses rule-based normalization
    - With ?use_llm=true: Uses LLM-based extraction from actual JD text
      (requires OPENAI_API_KEY to be set in environment)
    - With ?save_to_db=true: Saves normalized JD to database as a job posting
    
    **Input Validation:**
    - Text length: Maximum 100KB
    - Location policy: Must be 'onsite', 'hybrid', or 'remote'
    - Salary: salary_max must be >= salary_min
    - Currency: Must be a valid 3-letter ISO 4217 code
    """
    try:
        # Validate that at least some input is provided
        if not payload.text and not payload.title:
            raise ValidationError(
                "At least one of 'text' or 'title' must be provided",
                detail="Please provide either free-text job description or at least a job title"
            )
        
        # Validate text length if provided
        if payload.text and len(payload.text) > MAX_TEXT_LENGTH:
            raise ValidationError(
                f"Text too long: {len(payload.text)} characters",
                detail=f"Maximum text length is {MAX_TEXT_LENGTH} characters"
            )
        
        try:
            if use_llm:
                logger.info(f"Normalizing JD with LLM (text length: {len(payload.text) if payload.text else 0})")
                jd_data = normalize_jd_llm(
                    text=payload.text,
                    title=payload.title,
                    client=payload.client,
                    location_policy=payload.location_policy,
                    city=payload.city,
                    country=payload.country,
                    salary_min=payload.salary_min,
                    salary_max=payload.salary_max,
                    currency=payload.currency or "GBP"
                )
            else:
                logger.info(f"Normalizing JD with rule-based parser (text length: {len(payload.text) if payload.text else 0})")
                jd_data = normalize_jd(
                    text=payload.text,
                    title=payload.title,
                    client=payload.client,
                    location_policy=payload.location_policy,
                    city=payload.city,
                    country=payload.country,
                    salary_min=payload.salary_min,
                    salary_max=payload.salary_max,
                    currency=payload.currency or "GBP"
                )
            
            # Save to database if requested
            if save_to_db:
                try:
                    job_posting = create_job_posting(db, jd_data, original_text=payload.text)
                    logger.info(f"Saved job posting to database: {job_posting.id} ({job_posting.title} at {job_posting.client})")
                except Exception as e:
                    logger.error(f"Failed to save job posting to database: {e}", exc_info=e)
                    # Don't fail the request if database save fails
                    # Return the normalized JD data anyway
            
            return jd_data
        
        except ValueError as e:
            # Pydantic validation errors
            raise ValidationError(
                f"Invalid JD data structure: {str(e)}",
                detail="The normalized JD data does not match the expected schema"
            )
        
        except Exception as e:
            # Check if it's already a RecruitAssistException
            if isinstance(e, (ParseError, ValidationError, LLMError)):
                raise
            
            # Generic parsing errors
            logger.error(f"Error normalizing JD: {str(e)}", exc_info=e)
            raise ParseError(
                f"Failed to normalize JD: {str(e)}",
                detail="Please ensure the input data is valid and try again"
            )
    
    except (ValidationError, ParseError, LLMError):
        # Re-raise our custom exceptions
        raise
    
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in normalize_jd_endpoint: {str(e)}", exc_info=e)
        raise ParseError(
            "An unexpected error occurred while normalizing the JD",
            detail=str(e)
        )

