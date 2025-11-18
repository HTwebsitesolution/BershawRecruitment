"""
Candidate Profile CRUD endpoints.

Endpoints for managing candidate profiles (linked to jobs with match scores,
endorsements, and interview data).
"""

from __future__ import annotations
import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.db_schemas import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    CandidateProfileResponse,
    CandidateProfileDetail
)
from app.services.profile_service import (
    create_profile,
    get_profile,
    get_profiles_by_candidate,
    get_profiles_by_job,
    get_profile_by_candidate_and_job,
    update_profile,
    update_profile_endorsement,
    update_profile_interview,
    update_profile_match,
    delete_profile,
    profile_db_to_response
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["profiles"])


class EndorsementUpdate(BaseModel):
    """Schema for updating endorsement data."""
    endorsement_text: Optional[str] = None
    endorsement_recommendation: Optional[str] = Field(None, description="Proceed, Hold, or Reject")
    endorsement_fit_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Fit score (0.0 to 1.0)")


class InterviewUpdate(BaseModel):
    """Schema for updating interview data."""
    interview_date: Optional[datetime] = None
    interview_notes: Optional[str] = None
    interview_transcript: Optional[str] = None
    interview_data: Optional[dict] = None


class MatchUpdate(BaseModel):
    """Schema for updating match data."""
    match_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Match score (0.0 to 1.0)")
    match_details: Optional[dict] = None


@router.post("/", response_model=CandidateProfileDetail, status_code=status.HTTP_201_CREATED)
async def create_profile_endpoint(
    profile_data: CandidateProfileCreate = Body(...),
    db: Session = Depends(get_db)
) -> CandidateProfileDetail:
    """
    Create a new candidate profile.
    
    **Input:**
    - `candidate_id`: Candidate ID (required)
    - `job_posting_id`: Job posting ID (optional)
    - `profile_name`: Profile name (optional)
    - `company_name`: Company name (optional)
    - `role_title`: Role title (optional)
    - `interview_notes`: Interview notes (optional)
    - `interview_data`: Interview insights JSON (optional)
    
    **Returns:**
    - Created profile with all details
    """
    try:
        profile = create_profile(db, profile_data)
        return profile_db_to_response(profile, detailed=True)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Error creating profile: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )


@router.get("/", response_model=List[CandidateProfileResponse])
async def list_profiles(
    candidate_id: Optional[UUID] = Query(None, description="Filter by candidate ID"),
    job_id: Optional[UUID] = Query(None, description="Filter by job posting ID"),
    status: Optional[str] = Query(None, description="Filter by status (active, shortlisted, rejected, hired, archived)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db)
) -> List[CandidateProfileResponse]:
    """
    List candidate profiles with filtering.
    
    **Filters:**
    - `candidate_id`: Filter by candidate ID
    - `job_id`: Filter by job posting ID
    - `status`: Filter by status (active, shortlisted, rejected, hired, archived)
    
    **Pagination:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records (default: 100, max: 1000)
    """
    try:
        if candidate_id and job_id:
            # Get specific profile by candidate and job
            profile = get_profile_by_candidate_and_job(db, candidate_id, job_id)
            return [profile_db_to_response(profile, detailed=False)] if profile else []
        elif candidate_id:
            # Get profiles for a candidate
            profiles = get_profiles_by_candidate(db, candidate_id, status=status, skip=skip, limit=limit)
        elif job_id:
            # Get profiles for a job
            profiles = get_profiles_by_job(db, job_id, status=status, skip=skip, limit=limit)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one of 'candidate_id' or 'job_id' must be provided"
            )
        
        return [profile_db_to_response(p, detailed=False) for p in profiles]
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error listing profiles: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list profiles: {str(e)}"
        )


@router.get("/{profile_id}", response_model=CandidateProfileDetail)
async def get_profile_endpoint(
    profile_id: UUID,
    db: Session = Depends(get_db)
) -> CandidateProfileDetail:
    """
    Get a candidate profile by ID with full details.
    
    **Returns:**
    - All profile fields including match details, endorsement, interview data, etc.
    """
    try:
        profile = get_profile(db, profile_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        return profile_db_to_response(profile, detailed=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error getting profile: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/profiles", response_model=List[CandidateProfileResponse])
async def get_candidate_profiles(
    candidate_id: UUID,
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[CandidateProfileResponse]:
    """
    Get all profiles for a candidate.
    
    **Returns:**
    - List of profiles sorted by created_at (newest first)
    """
    try:
        profiles = get_profiles_by_candidate(db, candidate_id, status=status, skip=skip, limit=limit)
        return [profile_db_to_response(p, detailed=False) for p in profiles]
    
    except Exception as e:
        logger.error(f"Error getting candidate profiles: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get candidate profiles: {str(e)}"
        )


@router.get("/jobs/{job_id}/profiles", response_model=List[CandidateProfileResponse])
async def get_job_profiles(
    job_id: UUID,
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[CandidateProfileResponse]:
    """
    Get all profiles for a job posting.
    
    **Returns:**
    - List of profiles sorted by match_score (best matches first)
    """
    try:
        profiles = get_profiles_by_job(db, job_id, status=status, skip=skip, limit=limit)
        return [profile_db_to_response(p, detailed=False) for p in profiles]
    
    except Exception as e:
        logger.error(f"Error getting job profiles: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job profiles: {str(e)}"
        )


@router.patch("/{profile_id}", response_model=CandidateProfileDetail)
async def update_profile_endpoint(
    profile_id: UUID,
    updates: CandidateProfileUpdate = Body(...),
    db: Session = Depends(get_db)
) -> CandidateProfileDetail:
    """
    Update a candidate profile.
    
    **Allowed Fields:**
    - `profile_name`: Profile name
    - `company_name`: Company name
    - `role_title`: Role title
    - `interview_notes`: Interview notes
    - `interview_data`: Interview insights JSON
    - `endorsement_text`: Endorsement text
    - `endorsement_recommendation`: Recommendation (Proceed, Hold, Reject)
    - `endorsement_fit_score`: Fit score (0.0 to 1.0)
    - `match_score`: Match score (0.0 to 1.0)
    - `match_details`: Match details JSON
    - `status`: Status (active, shortlisted, rejected, hired, archived)
    
    **Note:** Only provided fields will be updated.
    """
    try:
        profile = update_profile(db, profile_id, updates)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        return profile_db_to_response(profile, detailed=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error updating profile: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.patch("/{profile_id}/endorsement", response_model=CandidateProfileDetail)
async def update_profile_endorsement_endpoint(
    profile_id: UUID,
    endorsement: EndorsementUpdate = Body(...),
    db: Session = Depends(get_db)
) -> CandidateProfileDetail:
    """
    Update endorsement data for a profile.
    
    **Input:**
    - `endorsement_text`: Endorsement text (optional)
    - `endorsement_recommendation`: Recommendation - Proceed, Hold, or Reject (optional)
    - `endorsement_fit_score`: Fit score 0.0 to 1.0 (optional)
    """
    try:
        profile = update_profile_endorsement(
            db,
            profile_id,
            endorsement_text=endorsement.endorsement_text,
            endorsement_recommendation=endorsement.endorsement_recommendation,
            endorsement_fit_score=endorsement.endorsement_fit_score
        )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        return profile_db_to_response(profile, detailed=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error updating endorsement: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update endorsement: {str(e)}"
        )


@router.patch("/{profile_id}/interview", response_model=CandidateProfileDetail)
async def update_profile_interview_endpoint(
    profile_id: UUID,
    interview: InterviewUpdate = Body(...),
    db: Session = Depends(get_db)
) -> CandidateProfileDetail:
    """
    Update interview data for a profile.
    
    **Input:**
    - `interview_date`: Interview date (optional)
    - `interview_notes`: Interview notes (optional)
    - `interview_transcript`: Interview transcript (optional)
    - `interview_data`: Interview insights JSON (optional)
    """
    try:
        profile = update_profile_interview(
            db,
            profile_id,
            interview_date=interview.interview_date,
            interview_notes=interview.interview_notes,
            interview_transcript=interview.interview_transcript,
            interview_data=interview.interview_data
        )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        return profile_db_to_response(profile, detailed=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error updating interview: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update interview: {str(e)}"
        )


@router.patch("/{profile_id}/match", response_model=CandidateProfileDetail)
async def update_profile_match_endpoint(
    profile_id: UUID,
    match: MatchUpdate = Body(...),
    db: Session = Depends(get_db)
) -> CandidateProfileDetail:
    """
    Update match data for a profile.
    
    **Input:**
    - `match_score`: Match score 0.0 to 1.0 (optional)
    - `match_details`: Match details JSON (optional)
    """
    try:
        profile = update_profile_match(
            db,
            profile_id,
            match_score=match.match_score,
            match_details=match.match_details
        )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        return profile_db_to_response(profile, detailed=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error updating match: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update match: {str(e)}"
        )


@router.delete("/{profile_id}")
async def delete_profile_endpoint(
    profile_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a candidate profile (soft delete - sets status to 'archived').
    
    **Note:** This is a soft delete. The profile will be marked as archived
    but not permanently removed from the database.
    """
    try:
        success = delete_profile(db, profile_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found: {profile_id}"
            )
        
        return {
            "success": True,
            "message": f"Profile {profile_id} archived successfully",
            "profile_id": str(profile_id)
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error deleting profile: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}"
        )

