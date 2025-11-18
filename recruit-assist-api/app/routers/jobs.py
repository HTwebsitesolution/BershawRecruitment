"""
Job Posting CRUD endpoints.

Endpoints for managing job postings (stored normalized job descriptions).
"""

from __future__ import annotations
import logging
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_schemas import JobPostingResponse, JobPostingDetail, JobPostingCreate, JobPostingUpdate
from app.services.job_posting_service import (
    get_job_posting,
    get_job_postings,
    create_job_posting,
    update_job_posting,
    delete_job_posting,
    job_posting_db_to_response
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobPostingDetail, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobPostingCreate = Body(...),
    db: Session = Depends(get_db)
) -> JobPostingDetail:
    """
    Create a new job posting from normalized JD data.
    
    **Input:**
    - `jd_data`: JobDescriptionNormalized object (required)
    
    **Returns:**
    - Created job posting with all details
    """
    try:
        job_posting = create_job_posting(
            db=db,
            jd=job_data.jd_data,
            original_text=None  # Can be added to JobPostingCreate schema if needed
        )
        
        return job_posting_db_to_response(job_posting, detailed=True)
    
    except Exception as e:
        logger.error(f"Error creating job posting: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job posting: {str(e)}"
        )


@router.get("/", response_model=List[JobPostingResponse])
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term (searches title, client, department)"),
    status: Optional[str] = Query(None, description="Filter by status (active, closed, filled, archived)"),
    client: Optional[str] = Query(None, description="Filter by client name"),
    location_country: Optional[str] = Query(None, description="Filter by country"),
    hiring_urgency: Optional[str] = Query(None, description="Filter by hiring urgency (asap, this_quarter, next_quarter)"),
    db: Session = Depends(get_db)
) -> List[JobPostingResponse]:
    """
    List job postings with filtering and pagination.
    
    **Filters:**
    - `search`: Search by title, client, or department
    - `status`: Filter by status (active, closed, filled, archived)
    - `client`: Filter by client name
    - `location_country`: Filter by country
    - `hiring_urgency`: Filter by urgency (asap, this_quarter, next_quarter)
    
    **Pagination:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records (default: 100, max: 1000)
    """
    try:
        jobs = get_job_postings(
            db=db,
            skip=skip,
            limit=limit,
            search=search,
            status=status,
            client=client,
            location_country=location_country,
            hiring_urgency=hiring_urgency,
        )
        
        return [job_posting_db_to_response(j, detailed=False) for j in jobs]
    
    except Exception as e:
        logger.error(f"Error listing job postings: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list job postings: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobPostingDetail)
async def get_job_detail(
    job_id: UUID,
    db: Session = Depends(get_db)
) -> JobPostingDetail:
    """
    Get a job posting by ID with full details.
    
    **Returns:**
    - All job posting fields including requirements, interview process, etc.
    """
    try:
        job = get_job_posting(db, job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job posting not found: {job_id}"
            )
        
        return job_posting_db_to_response(job, detailed=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error getting job posting: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job posting: {str(e)}"
        )


@router.patch("/{job_id}", response_model=JobPostingDetail)
async def update_job_detail(
    job_id: UUID,
    updates: JobPostingUpdate,
    db: Session = Depends(get_db)
) -> JobPostingDetail:
    """
    Update a job posting.
    
    **Allowed Fields:**
    - `title`: Job title
    - `client`: Client/company name
    - `department`: Department name
    - `location_policy`: Location policy (onsite, hybrid, remote)
    - `status`: Status (active, closed, filled, archived)
    - `hiring_urgency`: Hiring urgency (asap, this_quarter, next_quarter)
    
    **Note:** Only provided fields will be updated.
    """
    try:
        # Convert Pydantic model to dict (exclude None values)
        update_dict = updates.model_dump(exclude_unset=True)
        
        job = update_job_posting(db, job_id, update_dict)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job posting not found: {job_id}"
            )
        
        return job_posting_db_to_response(job, detailed=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error updating job posting: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job posting: {str(e)}"
        )


@router.delete("/{job_id}")
async def delete_job_endpoint(
    job_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a job posting (soft delete - sets status to 'archived').
    
    **Note:** This is a soft delete. The job posting will be marked as archived
    but not permanently removed from the database.
    """
    try:
        success = delete_job_posting(db, job_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job posting not found: {job_id}"
            )
        
        return {
            "success": True,
            "message": f"Job posting {job_id} archived successfully",
            "job_id": str(job_id)
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error deleting job posting: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job posting: {str(e)}"
        )

