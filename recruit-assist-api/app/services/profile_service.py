"""
Service layer for Candidate Profile operations.

Manages profiles that link candidates to jobs, including match scores,
endorsements, and interview data.
"""

from __future__ import annotations
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from uuid import UUID

from app.db_models import CandidateProfile, Candidate, JobPosting
from app.db_schemas import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    CandidateProfileResponse,
    CandidateProfileDetail
)

logger = logging.getLogger(__name__)


def create_profile(
    db: Session,
    profile_data: CandidateProfileCreate
) -> CandidateProfile:
    """
    Create a new candidate profile.
    
    Args:
        db: Database session
        profile_data: Profile creation data
    
    Returns:
        Created CandidateProfile
    """
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == profile_data.candidate_id).first()
    if not candidate:
        raise ValueError(f"Candidate not found: {profile_data.candidate_id}")
    
    # Verify job posting exists if provided
    if profile_data.job_posting_id:
        job = db.query(JobPosting).filter(JobPosting.id == profile_data.job_posting_id).first()
        if not job:
            raise ValueError(f"Job posting not found: {profile_data.job_posting_id}")
    
    # Create profile
    profile = CandidateProfile(
        candidate_id=profile_data.candidate_id,
        job_posting_id=profile_data.job_posting_id,
        profile_name=profile_data.profile_name,
        company_name=profile_data.company_name,
        role_title=profile_data.role_title,
        interview_notes=profile_data.interview_notes,
        interview_data=profile_data.interview_data,
        status="active"
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    logger.info(f"Created profile {profile.id} for candidate {profile_data.candidate_id}")
    return profile


def get_profile(db: Session, profile_id: UUID) -> Optional[CandidateProfile]:
    """Get a profile by ID."""
    return db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()


def get_profiles_by_candidate(
    db: Session,
    candidate_id: UUID,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[CandidateProfile]:
    """
    Get all profiles for a candidate.
    
    Args:
        db: Database session
        candidate_id: Candidate ID
        status: Filter by status (optional)
        skip: Number of records to skip
        limit: Maximum number of records
    
    Returns:
        List of CandidateProfile
    """
    query = db.query(CandidateProfile).filter(
        CandidateProfile.candidate_id == candidate_id
    )
    
    if status:
        query = query.filter(CandidateProfile.status == status)
    
    # Filter out archived by default
    query = query.filter(CandidateProfile.status != "archived")
    
    # Order by created_at descending (newest first)
    query = query.order_by(CandidateProfile.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def get_profiles_by_job(
    db: Session,
    job_id: UUID,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[CandidateProfile]:
    """
    Get all profiles for a job posting.
    
    Args:
        db: Database session
        job_id: Job posting ID
        status: Filter by status (optional)
        skip: Number of records to skip
        limit: Maximum number of records
    
    Returns:
        List of CandidateProfile
    """
    query = db.query(CandidateProfile).filter(
        CandidateProfile.job_posting_id == job_id
    )
    
    if status:
        query = query.filter(CandidateProfile.status == status)
    
    # Filter out archived by default
    query = query.filter(CandidateProfile.status != "archived")
    
    # Order by match_score descending (best matches first)
    query = query.order_by(CandidateProfile.match_score.desc().nulls_last())
    
    return query.offset(skip).limit(limit).all()


def get_profile_by_candidate_and_job(
    db: Session,
    candidate_id: UUID,
    job_id: UUID
) -> Optional[CandidateProfile]:
    """Get a profile by candidate and job posting IDs."""
    return db.query(CandidateProfile).filter(
        CandidateProfile.candidate_id == candidate_id,
        CandidateProfile.job_posting_id == job_id
    ).first()


def update_profile(
    db: Session,
    profile_id: UUID,
    updates: CandidateProfileUpdate
) -> Optional[CandidateProfile]:
    """
    Update a candidate profile.
    
    Args:
        db: Database session
        profile_id: Profile ID
        updates: Update data
    
    Returns:
        Updated CandidateProfile or None if not found
    """
    profile = get_profile(db, profile_id)
    if not profile:
        return None
    
    # Convert Pydantic model to dict (exclude None values)
    update_dict = updates.model_dump(exclude_unset=True)
    
    # Update fields
    for key, value in update_dict.items():
        if hasattr(profile, key) and value is not None:
            setattr(profile, key, value)
    
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    
    logger.info(f"Updated profile {profile_id}")
    return profile


def update_profile_endorsement(
    db: Session,
    profile_id: UUID,
    endorsement_text: Optional[str] = None,
    endorsement_recommendation: Optional[str] = None,
    endorsement_fit_score: Optional[float] = None
) -> Optional[CandidateProfile]:
    """
    Update endorsement data for a profile.
    
    Args:
        db: Database session
        profile_id: Profile ID
        endorsement_text: Endorsement text
        endorsement_recommendation: Recommendation (Proceed, Hold, Reject)
        endorsement_fit_score: Fit score (0.0 to 1.0)
    
    Returns:
        Updated CandidateProfile or None if not found
    """
    profile = get_profile(db, profile_id)
    if not profile:
        return None
    
    if endorsement_text is not None:
        profile.endorsement_text = endorsement_text
    if endorsement_recommendation is not None:
        profile.endorsement_recommendation = endorsement_recommendation
    if endorsement_fit_score is not None:
        profile.endorsement_fit_score = endorsement_fit_score
    
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    
    logger.info(f"Updated endorsement for profile {profile_id}")
    return profile


def update_profile_interview(
    db: Session,
    profile_id: UUID,
    interview_date: Optional[datetime] = None,
    interview_notes: Optional[str] = None,
    interview_transcript: Optional[str] = None,
    interview_data: Optional[Dict[str, Any]] = None
) -> Optional[CandidateProfile]:
    """
    Update interview data for a profile.
    
    Args:
        db: Database session
        profile_id: Profile ID
        interview_date: Interview date
        interview_notes: Interview notes
        interview_transcript: Interview transcript
        interview_data: Interview insights (JSON)
    
    Returns:
        Updated CandidateProfile or None if not found
    """
    profile = get_profile(db, profile_id)
    if not profile:
        return None
    
    if interview_date is not None:
        profile.interview_date = interview_date
    if interview_notes is not None:
        profile.interview_notes = interview_notes
    if interview_transcript is not None:
        profile.interview_transcript = interview_transcript
    if interview_data is not None:
        profile.interview_data = interview_data
    
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    
    logger.info(f"Updated interview data for profile {profile_id}")
    return profile


def update_profile_match(
    db: Session,
    profile_id: UUID,
    match_score: Optional[float] = None,
    match_details: Optional[Dict[str, Any]] = None
) -> Optional[CandidateProfile]:
    """
    Update match data for a profile.
    
    Args:
        db: Database session
        profile_id: Profile ID
        match_score: Match score (0.0 to 1.0)
        match_details: Match details (JSON)
    
    Returns:
        Updated CandidateProfile or None if not found
    """
    profile = get_profile(db, profile_id)
    if not profile:
        return None
    
    if match_score is not None:
        profile.match_score = match_score
    if match_details is not None:
        profile.match_details = match_details
    
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    
    logger.info(f"Updated match data for profile {profile_id}")
    return profile


def delete_profile(db: Session, profile_id: UUID) -> bool:
    """
    Soft delete a profile (sets status to 'archived').
    
    Args:
        db: Database session
        profile_id: Profile ID
    
    Returns:
        True if deleted, False if not found
    """
    profile = get_profile(db, profile_id)
    if not profile:
        return False
    
    # Soft delete (set status to 'archived')
    profile.status = "archived"
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Archived profile {profile_id}")
    return True


def profile_db_to_response(
    profile: CandidateProfile,
    detailed: bool = False
) -> CandidateProfileResponse | CandidateProfileDetail:
    """
    Convert CandidateProfile (SQLAlchemy) to response schema (Pydantic).
    
    Args:
        profile: Database model
        detailed: Whether to return detailed schema
    
    Returns:
        CandidateProfileResponse or CandidateProfileDetail
    """
    # Import here to avoid circular dependency
    from app.db_schemas import CandidateProfileDetail
    
    if detailed:
        return CandidateProfileDetail(
            id=profile.id,
            candidate_id=profile.candidate_id,
            job_posting_id=profile.job_posting_id,
            profile_name=profile.profile_name,
            company_name=profile.company_name,
            role_title=profile.role_title,
            interview_date=profile.interview_date,
            interview_notes=profile.interview_notes,
            interview_transcript=profile.interview_transcript,
            interview_data=profile.interview_data,
            endorsement_text=profile.endorsement_text,
            endorsement_recommendation=profile.endorsement_recommendation,
            endorsement_fit_score=profile.endorsement_fit_score,
            match_score=profile.match_score,
            match_details=profile.match_details,
            status=profile.status,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            # Booking fields
            booking_link=profile.booking_link,
            booking_id=profile.booking_id,
            booking_provider=profile.booking_provider,
            booking_status=profile.booking_status,
            booking_expires_at=profile.booking_expires_at,
            # AI Interview fields
            ai_interview_id=profile.ai_interview_id,
            ai_interview_provider=profile.ai_interview_provider,
            ai_interview_link=profile.ai_interview_link,
            ai_interview_status=profile.ai_interview_status,
            ai_interview_scheduled_at=profile.ai_interview_scheduled_at,
        )
    else:
        return CandidateProfileResponse(
            id=profile.id,
            candidate_id=profile.candidate_id,
            job_posting_id=profile.job_posting_id,
            profile_name=profile.profile_name,
            company_name=profile.company_name,
            role_title=profile.role_title,
            match_score=profile.match_score,
            endorsement_recommendation=profile.endorsement_recommendation,
            endorsement_fit_score=profile.endorsement_fit_score,
            status=profile.status,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

