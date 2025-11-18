"""
Candidate CRUD endpoints.

Endpoints for managing candidates (stored parsed CVs).
"""

from __future__ import annotations
import logging
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import Candidate
from app.db_schemas import CandidateResponse, CandidateDetail, CandidateUpdate
from app.services.candidate_service import (
    get_candidate,
    get_candidates,
    update_candidate,
    delete_candidate,
    candidate_db_to_response
)
from app.exceptions import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/", response_model=List[CandidateResponse])
async def list_candidates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term (searches name, email)"),
    status: Optional[str] = Query(None, description="Filter by status (active, archived, deleted)"),
    location_country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db)
) -> List[CandidateResponse]:
    """
    List candidates with filtering and pagination.
    
    **Filters:**
    - `search`: Search by name or email
    - `status`: Filter by status (active, archived, deleted)
    - `location_country`: Filter by country
    
    **Pagination:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records (default: 100, max: 1000)
    """
    try:
        candidates = get_candidates(
            db=db,
            skip=skip,
            limit=limit,
            search=search,
            status=status,
            location_country=location_country,
        )
        
        return [candidate_db_to_response(c, detailed=False) for c in candidates]
    
    except Exception as e:
        logger.error(f"Error listing candidates: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list candidates: {str(e)}"
        )


@router.get("/{candidate_id}", response_model=CandidateDetail)
async def get_candidate_detail(
    candidate_id: UUID,
    db: Session = Depends(get_db)
) -> CandidateDetail:
    """
    Get a candidate by ID with full details.
    
    **Returns:**
    - All candidate fields including experience, skills, education, etc.
    """
    try:
        candidate = get_candidate(db, candidate_id)
        
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate not found: {candidate_id}"
            )
        
        return candidate_db_to_response(candidate, detailed=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error getting candidate: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get candidate: {str(e)}"
        )


@router.patch("/{candidate_id}", response_model=CandidateDetail)
async def update_candidate_detail(
    candidate_id: UUID,
    updates: CandidateUpdate,
    db: Session = Depends(get_db)
) -> CandidateDetail:
    """
    Update a candidate.
    
    **Allowed Fields:**
    - `full_name`: Candidate's full name
    - `email`: Email address
    - `phone`: Phone number
    - `linkedin_url`: LinkedIn profile URL
    - `status`: Status (active, archived, deleted)
    
    **Note:** Only provided fields will be updated.
    """
    try:
        # Convert Pydantic model to dict (exclude None values)
        update_dict = updates.model_dump(exclude_unset=True)
        
        candidate = update_candidate(db, candidate_id, update_dict)
        
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate not found: {candidate_id}"
            )
        
        return candidate_db_to_response(candidate, detailed=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error updating candidate: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update candidate: {str(e)}"
        )


@router.delete("/{candidate_id}")
async def delete_candidate_endpoint(
    candidate_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a candidate (soft delete - sets status to 'deleted').
    
    **Note:** This is a soft delete for GDPR compliance. The candidate record
    will be marked as deleted but not permanently removed from the database.
    """
    try:
        success = delete_candidate(db, candidate_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate not found: {candidate_id}"
            )
        
        return {
            "success": True,
            "message": f"Candidate {candidate_id} deleted successfully",
            "candidate_id": str(candidate_id)
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete candidate: {str(e)}"
        )

