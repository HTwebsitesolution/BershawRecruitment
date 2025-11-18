"""
Candidate Matching Endpoints

Endpoints for matching candidates to job postings.
"""

from __future__ import annotations
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.db_models import Candidate, JobPosting, CandidateProfile
from app.services.matching_service import (
    match_candidate_to_job,
    calculate_match_score,
    match_all_candidates_to_job,
    match_candidate_to_all_jobs
)
from app.services.candidate_service import get_candidate
from app.services.job_posting_service import get_job_posting

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matching", tags=["matching"])


class MatchResult(BaseModel):
    """Schema for match result."""
    candidate_id: UUID
    job_id: UUID
    match_score: float
    match_details: dict
    candidate_name: str
    job_title: str
    job_client: str


class MatchRequest(BaseModel):
    """Schema for match request."""
    candidate_id: UUID
    job_id: UUID
    create_profile: bool = True  # Whether to create/update CandidateProfile


@router.post("/match", response_model=dict)
async def create_match(
    request: MatchRequest = Body(...),
    db: Session = Depends(get_db)
) -> dict:
    """
    Match a candidate to a job posting.
    
    Calculates match score based on:
    - Skills (must-haves and nice-to-haves): 35% + 10%
    - Experience (years): 20%
    - Location (country, remote preference): 15%
    - Salary (target vs job range): 10%
    - Right to work (visa/authorization): 10%
    
    **Returns:**
    - Match score (0.0 to 1.0)
    - Detailed breakdown by category
    - CandidateProfile (if create_profile=true)
    """
    try:
        match_score, match_details, profile = match_candidate_to_job(
            db=db,
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            create_profile=request.create_profile
        )
        
        candidate = get_candidate(db, request.candidate_id)
        job = get_job_posting(db, request.job_id)
        
        return {
            "success": True,
            "candidate_id": str(request.candidate_id),
            "job_id": str(request.job_id),
            "candidate_name": candidate.full_name if candidate else None,
            "job_title": job.title if job else None,
            "job_client": job.client if job else None,
            "match_score": round(match_score, 3),
            "match_percentage": round(match_score * 100, 1),
            "match_details": match_details,
            "profile_id": str(profile.id) if profile else None,
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Error matching candidate to job: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match candidate to job: {str(e)}"
        )


@router.get("/jobs/{job_id}/candidates", response_model=List[MatchResult])
async def get_job_candidates(
    job_id: UUID,
    min_score: Optional[float] = Query(0.0, ge=0.0, le=1.0, description="Minimum match score (0.0 to 1.0)"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of candidates to return"),
    db: Session = Depends(get_db)
) -> List[MatchResult]:
    """
    Get matched candidates for a job posting, ranked by match score.
    
    **Returns:**
    - List of candidates sorted by match score (highest first)
    - Each result includes match score and details
    - Filtered by minimum score threshold
    
    **Use Cases:**
    - Find best candidates for a job
    - Review top matches for a position
    - Export candidate shortlist
    """
    try:
        job = get_job_posting(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job posting not found: {job_id}"
            )
        
        # Use optimized matching function
        matched_candidates = match_all_candidates_to_job(db, job_id, min_score=min_score, limit=limit)
        
        # Convert to match results
        matches = []
        for candidate, match_score, match_details in matched_candidates:
            matches.append({
                "candidate_id": candidate.id,
                "job_id": job_id,
                "match_score": match_score,
                "match_details": match_details,
                "candidate_name": candidate.full_name,
                "job_title": job.title,
                "job_client": job.client,
            })
        
        return [MatchResult(**match) for match in matches]
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error getting job candidates: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job candidates: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/jobs", response_model=List[MatchResult])
async def get_candidate_jobs(
    candidate_id: UUID,
    min_score: Optional[float] = Query(0.0, ge=0.0, le=1.0, description="Minimum match score (0.0 to 1.0)"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of jobs to return"),
    db: Session = Depends(get_db)
) -> List[MatchResult]:
    """
    Get matched job postings for a candidate, ranked by match score.
    
    **Returns:**
    - List of jobs sorted by match score (highest first)
    - Each result includes match score and details
    - Filtered by minimum score threshold
    
    **Use Cases:**
    - Find best jobs for a candidate
    - Suggest roles to a candidate
    - Candidate job recommendations
    """
    try:
        candidate = get_candidate(db, candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate not found: {candidate_id}"
            )
        
        # Use optimized matching function
        matched_jobs = match_candidate_to_all_jobs(db, candidate_id, min_score=min_score, limit=limit)
        
        # Convert to match results
        matches = []
        for job, match_score, match_details in matched_jobs:
            matches.append({
                "candidate_id": candidate_id,
                "job_id": job.id,
                "match_score": match_score,
                "match_details": match_details,
                "candidate_name": candidate.full_name,
                "job_title": job.title,
                "job_client": job.client,
            })
        
        return [MatchResult(**match) for match in matches]
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error getting candidate jobs: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get candidate jobs: {str(e)}"
        )


@router.get("/jobs/{job_id}/candidates/top", response_model=List[MatchResult])
async def get_top_job_candidates(
    job_id: UUID,
    top_n: int = Query(10, ge=1, le=100, description="Number of top candidates to return"),
    min_score: Optional[float] = Query(0.5, ge=0.0, le=1.0, description="Minimum match score"),
    db: Session = Depends(get_db)
) -> List[MatchResult]:
    """
    Get top N candidates for a job posting (convenience endpoint).
    
    Equivalent to `/jobs/{job_id}/candidates?min_score={min_score}&limit={top_n}`
    but with default minimum score of 0.5 for better quality results.
    """
    return await get_job_candidates(job_id, min_score=min_score, limit=top_n, db=db)


@router.get("/candidates/{candidate_id}/jobs/recommended", response_model=List[MatchResult])
async def get_recommended_jobs(
    candidate_id: UUID,
    top_n: int = Query(10, ge=1, le=100, description="Number of recommended jobs to return"),
    min_score: Optional[float] = Query(0.5, ge=0.0, le=1.0, description="Minimum match score"),
    db: Session = Depends(get_db)
) -> List[MatchResult]:
    """
    Get top N recommended jobs for a candidate (convenience endpoint).
    
    Equivalent to `/candidates/{candidate_id}/jobs?min_score={min_score}&limit={top_n}`
    but with default minimum score of 0.5 for better quality results.
    """
    return await get_candidate_jobs(candidate_id, min_score=min_score, limit=top_n, db=db)

