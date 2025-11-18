"""
Interview Scheduling Endpoints

Endpoints for automated interview scheduling including calendar booking
and AI interviewer integration.
"""

from __future__ import annotations
import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.db_models import CandidateProfile
from app.services.profile_service import get_profile, update_profile
from app.services.calendar_service import calendar_service
from app.services.ai_interviewer_service import ai_interviewer_service
from app.db_schemas import CandidateProfileDetail
from app.services.profile_service import profile_db_to_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scheduling", tags=["scheduling"])


class BookingRequest(BaseModel):
    """Schema for creating a booking."""
    profile_id: UUID
    duration_minutes: int = Field(30, ge=15, le=120, description="Interview duration in minutes")
    provider: str = Field("calendly", description="Calendar provider: google, calendly, outlook, manual")
    preferred_times: Optional[List[datetime]] = Field(None, description="Preferred time slots")
    timezone: str = Field("Europe/London", description="Timezone for scheduling")


class BookingResponse(BaseModel):
    """Schema for booking response."""
    booking_link: str
    booking_id: str
    provider: str
    duration_minutes: int
    expires_at: str
    status: str


class AIInterviewRequest(BaseModel):
    """Schema for scheduling AI interview."""
    profile_id: UUID
    interview_type: str = Field("general", description="Type: general, technical, cultural")
    duration_minutes: int = Field(45, ge=30, le=90)
    provider: str = Field("custom", description="Provider: hirevue, myinterview, custom")
    questions: Optional[List[str]] = Field(None, description="Custom interview questions")


@router.post("/book", response_model=BookingResponse)
async def create_booking(
    request: BookingRequest = Body(...),
    db: Session = Depends(get_db)
) -> BookingResponse:
    """
    Create a calendar booking link for interview scheduling.
    
    **Providers:**
    - `calendly` - Calendly booking link (requires CALENDLY_API_KEY)
    - `google` - Google Calendar link (requires GOOGLE_CALENDAR_API_KEY)
    - `outlook` - Outlook Calendar link (requires MICROSOFT_GRAPH_CLIENT_ID)
    - `manual` - Custom booking link
    
    **Returns:**
    - Booking link to send to candidate
    - Booking ID for tracking
    - Expiration date
    """
    try:
        # Get profile
        profile = get_profile(db, request.profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {request.profile_id}"
            )
        
        # Get candidate data
        from app.services.candidate_service import get_candidate
        candidate = get_candidate(db, profile.candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate not found: {profile.candidate_id}"
            )
        
        # Get job data for context
        from app.services.job_posting_service import get_job_posting
        job = get_job_posting(db, profile.job_posting_id) if profile.job_posting_id else None
        
        # Create booking link
        booking_result = calendar_service.create_booking_link(
            profile_id=request.profile_id,
            candidate_email=candidate.email or "",
            candidate_name=candidate.full_name,
            duration_minutes=request.duration_minutes,
            provider=request.provider,
            preferred_times=request.preferred_times,
            timezone=request.timezone
        )
        
        # Update profile with booking data
        profile.booking_link = booking_result["booking_link"]
        profile.booking_id = booking_result["booking_id"]
        profile.booking_provider = booking_result["provider"]
        profile.booking_status = "pending"
        profile.booking_expires_at = datetime.fromisoformat(booking_result["expires_at"].replace("Z", "+00:00"))
        profile.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Created booking for profile {request.profile_id}: {booking_result['booking_id']}")
        
        return BookingResponse(
            booking_link=booking_result["booking_link"],
            booking_id=booking_result["booking_id"],
            provider=booking_result["provider"],
            duration_minutes=booking_result["duration_minutes"],
            expires_at=booking_result["expires_at"],
            status="pending"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error creating booking: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.post("/ai-interview", response_model=dict)
async def schedule_ai_interview(
    request: AIInterviewRequest = Body(...),
    db: Session = Depends(get_db)
) -> dict:
    """
    Schedule an AI-powered interview.
    
    **Providers:**
    - `custom` - Custom OpenAI-based interviewer (default)
    - `hirevue` - HireVue commercial service (requires HIREVUE_API_KEY)
    - `myinterview` - MyInterview commercial service (requires MYINTERVIEW_API_KEY)
    
    **Interview Types:**
    - `general` - General interview questions
    - `technical` - Technical skills assessment
    - `cultural` - Cultural fit assessment
    
    **Returns:**
    - Interview link to send to candidate
    - Interview ID for tracking
    - Scheduled time
    """
    try:
        # Get profile
        profile = get_profile(db, request.profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {request.profile_id}"
            )
        
        # Get candidate and job data
        from app.services.candidate_service import get_candidate
        from app.services.job_posting_service import get_job_posting
        
        candidate = get_candidate(db, profile.candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate not found: {profile.candidate_id}"
            )
        
        job = get_job_posting(db, profile.job_posting_id) if profile.job_posting_id else None
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job posting not found for profile {request.profile_id}"
            )
        
        # Generate questions if not provided
        questions = request.questions
        if not questions:
            job_requirements = job.requirements or {}
            questions = ai_interviewer_service.create_interview_questions(
                job_requirements,
                interview_type=request.interview_type,
                num_questions=5
            )
        
        # Schedule interview
        interview_result = ai_interviewer_service.schedule_interview(
            profile_id=request.profile_id,
            candidate_email=candidate.email or "",
            candidate_name=candidate.full_name,
            job_title=job.title,
            job_client=job.client or "",
            interview_type=request.interview_type,
            duration_minutes=request.duration_minutes,
            questions=questions,
            provider=request.provider
        )
        
        # Update profile with AI interview data
        profile.ai_interview_id = interview_result["interview_id"]
        profile.ai_interview_provider = interview_result["provider"]
        profile.ai_interview_link = interview_result["interview_link"]
        profile.ai_interview_status = interview_result["status"]
        profile.ai_interview_scheduled_at = datetime.fromisoformat(interview_result["scheduled_at"].replace("Z", "+00:00"))
        profile.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Scheduled AI interview for profile {request.profile_id}: {interview_result['interview_id']}")
        
        return {
            "success": True,
            "interview_id": interview_result["interview_id"],
            "interview_link": interview_result["interview_link"],
            "provider": interview_result["provider"],
            "interview_type": interview_result["interview_type"],
            "duration_minutes": interview_result["duration_minutes"],
            "scheduled_at": interview_result["scheduled_at"],
            "status": interview_result["status"],
            "questions": questions
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error scheduling AI interview: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule AI interview: {str(e)}"
        )


@router.post("/ai-interview/{interview_id}/transcript")
async def fetch_interview_transcript(
    interview_id: str,
    profile_id: UUID = Query(...),
    db: Session = Depends(get_db)
) -> dict:
    """
    Fetch interview transcript after AI interview is completed.
    
    **Note:** This endpoint should be called after the interview is completed
    to automatically extract and save the transcript.
    """
    try:
        # Get profile
        profile = get_profile(db, profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        if profile.ai_interview_id != interview_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Interview ID {interview_id} does not match profile {profile_id}"
            )
        
        provider = profile.ai_interview_provider or "custom"
        
        # Get interview results (including transcript)
        interview_results = ai_interviewer_service.get_interview_results(interview_id, provider)
        
        # Update profile with transcript
        if interview_results.get("transcript"):
            profile.interview_transcript = interview_results["transcript"]
            profile.ai_interview_status = "completed"
            
            # Extract insights if available
            if interview_results.get("insights"):
                current_interview_data = profile.interview_data or {}
                current_interview_data.update(interview_results["insights"])
                profile.interview_data = current_interview_data
            
            profile.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(profile)
        
        logger.info(f"Fetched transcript for interview {interview_id}")
        
        return {
            "success": True,
            "interview_id": interview_id,
            "transcript": interview_results.get("transcript"),
            "insights": interview_results.get("insights"),
            "scores": interview_results.get("scores"),
            "recommendation": interview_results.get("recommendation"),
            "profile_updated": True
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error fetching interview transcript: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch interview transcript: {str(e)}"
        )


@router.get("/booking/{booking_id}/status")
async def get_booking_status(
    booking_id: str,
    provider: str = Query("calendly", description="Calendar provider"),
    db: Session = Depends(get_db)
) -> dict:
    """Get the status of a booking."""
    try:
        booking_status = calendar_service.get_booking_status(booking_id, provider)
        return booking_status
    
    except Exception as e:
        logger.error(f"Error getting booking status: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get booking status: {str(e)}"
        )


@router.post("/booking/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    provider: str = Query("calendly", description="Calendar provider"),
    db: Session = Depends(get_db)
) -> dict:
    """Cancel a scheduled booking."""
    try:
        # Find profile by booking_id
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.booking_id == booking_id
        ).first()
        
        success = calendar_service.cancel_booking(booking_id, provider)
        
        if profile and success:
            profile.booking_status = "cancelled"
            profile.updated_at = datetime.utcnow()
            db.commit()
        
        logger.info(f"Cancelled booking {booking_id}")
        
        return {
            "success": success,
            "booking_id": booking_id,
            "status": "cancelled"
        }
    
    except Exception as e:
        logger.error(f"Error cancelling booking: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel booking: {str(e)}"
        )

