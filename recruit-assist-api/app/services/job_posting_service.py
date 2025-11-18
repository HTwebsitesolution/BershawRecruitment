"""
Service layer for Job Posting operations.

Converts between Pydantic models (API) and SQLAlchemy models (database).
"""

from __future__ import annotations
import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from uuid import UUID

from app.models import JobDescriptionNormalized
from app.db_models import JobPosting
from app.db_schemas import JobPostingResponse, JobPostingDetail

logger = logging.getLogger(__name__)


def jd_to_job_posting_db(jd: JobDescriptionNormalized, original_text: Optional[str] = None) -> JobPosting:
    """
    Convert JobDescriptionNormalized (Pydantic) to JobPosting (SQLAlchemy).
    
    Args:
        jd: Normalized JD data
        original_text: Original job description text (if provided)
    
    Returns:
        JobPosting database model
    """
    job_data = jd.job
    requirements_data = jd.requirements
    
    # Extract primary location
    primary_location = job_data.primary_location if job_data.primary_location else None
    
    # Extract salary band
    salary_band = job_data.salary_band if job_data.salary_band else None
    
    # Convert requirements to JSON
    requirements_json = {
        "must_haves": [req.model_dump(exclude_none=True) for req in requirements_data.must_haves],
        "nice_to_haves": [req.model_dump(exclude_none=True) for req in requirements_data.nice_to_haves],
        "years_experience_min": requirements_data.years_experience_min,
        "education_required": requirements_data.education_required,
    }
    
    # Convert interview process to JSON
    interview_process_json = None
    if jd.interview_process:
        interview_process_json = [stage.model_dump(exclude_none=True) for stage in jd.interview_process]
    
    # Extract location policy (Literal type, so just use as string)
    location_policy_value = str(job_data.location_policy) if job_data.location_policy else None
    
    return JobPosting(
        title=job_data.title,
        client=job_data.client,
        department=job_data.department,
        location_policy=location_policy_value,
        onsite_days_per_week=job_data.onsite_days_per_week,
        primary_location_city=primary_location.city if primary_location else None,
        primary_location_region=primary_location.region if primary_location else None,
        primary_location_country=primary_location.country if primary_location else None,
        salary_band_min=salary_band.min if salary_band else None,
        salary_band_max=salary_band.max if salary_band else None,
        salary_currency=salary_band.currency if salary_band else None,
        salary_period=str(salary_band.period) if salary_band and salary_band.period else None,
        requirements=requirements_json,
        visa_sponsorship=str(job_data.visa_sponsorship) if job_data.visa_sponsorship else None,
        clearance_required=job_data.clearance_required,
        hiring_urgency=str(job_data.hiring_urgency) if job_data.hiring_urgency else None,
        interview_process=interview_process_json,
        role_notes=jd.role_notes,
        original_text=original_text,
        normalization_date=datetime.utcnow(),
        normalizer_version="jdx-1.0.0",  # Default version
        status="active",
    )


def job_posting_db_to_response(job: JobPosting, detailed: bool = False) -> JobPostingResponse | JobPostingDetail:
    """
    Convert JobPosting (SQLAlchemy) to JobPostingResponse or JobPostingDetail (Pydantic).
    
    Args:
        job: Database model
        detailed: Whether to return detailed schema
    
    Returns:
        JobPostingResponse or JobPostingDetail
    """
    if detailed:
        return JobPostingDetail(
            id=job.id,
            title=job.title,
            client=job.client,
            department=job.department,
            location_policy=job.location_policy,
            onsite_days_per_week=job.onsite_days_per_week,
            primary_location_city=job.primary_location_city,
            primary_location_region=job.primary_location_region,
            primary_location_country=job.primary_location_country,
            salary_band_min=job.salary_band_min,
            salary_band_max=job.salary_band_max,
            salary_currency=job.salary_currency,
            salary_period=job.salary_period,
            requirements=job.requirements,
            visa_sponsorship=job.visa_sponsorship,
            clearance_required=job.clearance_required,
            hiring_urgency=job.hiring_urgency,
            interview_process=job.interview_process,
            role_notes=job.role_notes,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
    else:
        return JobPostingResponse(
            id=job.id,
            title=job.title,
            client=job.client,
            department=job.department,
            location_policy=job.location_policy,
            primary_location_city=job.primary_location_city,
            primary_location_country=job.primary_location_country,
            salary_band_min=job.salary_band_min,
            salary_band_max=job.salary_band_max,
            salary_currency=job.salary_currency,
            hiring_urgency=job.hiring_urgency,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )


def create_job_posting(db: Session, jd: JobDescriptionNormalized, original_text: Optional[str] = None) -> JobPosting:
    """
    Create a new job posting from normalized JD data.
    
    Args:
        db: Database session
        jd: Normalized JD data
        original_text: Original job description text (if provided)
    
    Returns:
        Created JobPosting database model
    """
    job_posting = jd_to_job_posting_db(jd, original_text=original_text)
    
    db.add(job_posting)
    db.commit()
    db.refresh(job_posting)
    
    logger.info(f"Created job posting: {job_posting.id} ({job_posting.title} at {job_posting.client})")
    return job_posting


def get_job_posting(db: Session, job_id: UUID) -> Optional[JobPosting]:
    """Get a job posting by ID."""
    return db.query(JobPosting).filter(JobPosting.id == job_id).first()


def get_job_postings(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    client: Optional[str] = None,
    location_country: Optional[str] = None,
    hiring_urgency: Optional[str] = None,
) -> List[JobPosting]:
    """
    Get job postings with filtering and pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term (searches title, client)
        status: Filter by status (active, closed, filled, archived)
        client: Filter by client name
        location_country: Filter by country
        hiring_urgency: Filter by hiring urgency
    
    Returns:
        List of JobPosting database models
    """
    query = db.query(JobPosting)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                JobPosting.title.ilike(f"%{search}%"),
                JobPosting.client.ilike(f"%{search}%"),
                JobPosting.department.ilike(f"%{search}%"),
            )
        )
    
    if status:
        query = query.filter(JobPosting.status == status)
    
    if client:
        query = query.filter(JobPosting.client.ilike(f"%{client}%"))
    
    if location_country:
        query = query.filter(JobPosting.primary_location_country == location_country)
    
    if hiring_urgency:
        query = query.filter(JobPosting.hiring_urgency == hiring_urgency)
    
    # Filter out archived jobs by default
    query = query.filter(JobPosting.status != "archived")
    
    # Order by created_at descending (newest first)
    query = query.order_by(JobPosting.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def update_job_posting(
    db: Session,
    job_id: UUID,
    updates: dict
) -> Optional[JobPosting]:
    """Update a job posting."""
    job = get_job_posting(db, job_id)
    if not job:
        return None
    
    # Update fields
    for key, value in updates.items():
        if hasattr(job, key) and value is not None:
            setattr(job, key, value)
    
    job.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(job)
    
    logger.info(f"Updated job posting: {job_id}")
    return job


def delete_job_posting(db: Session, job_id: UUID) -> bool:
    """
    Soft delete a job posting (sets status to 'archived').
    
    Args:
        db: Database session
        job_id: Job posting ID
    
    Returns:
        True if deleted, False if not found
    """
    job = get_job_posting(db, job_id)
    if not job:
        return False
    
    # Soft delete (set status to 'archived')
    job.status = "archived"
    job.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Archived job posting: {job_id}")
    return True

