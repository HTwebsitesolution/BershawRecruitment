"""
Service layer for Candidate operations.

Converts between Pydantic models (API) and SQLAlchemy models (database).
"""

from __future__ import annotations
import logging
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from uuid import UUID

from app.models import CandidateCVNormalized
from app.db_models import Candidate
from app.db_schemas import CandidateResponse, CandidateDetail
from app.services.gdpr import gdpr_manager

logger = logging.getLogger(__name__)


def cv_to_candidate_db(cv: CandidateCVNormalized, consent_granted: bool = False) -> Candidate:
    """
    Convert CandidateCVNormalized (Pydantic) to Candidate (SQLAlchemy).
    
    Args:
        cv: Parsed CV data
        consent_granted: Whether consent has been granted
    
    Returns:
        Candidate database model
    """
    candidate_data = cv.candidate
    
    # Extract location data
    location = candidate_data.location if candidate_data.location else None
    
    # Calculate retention date
    retention_until = None
    if consent_granted:
        retention_until = gdpr_manager.calculate_expiry_date(datetime.utcnow())
    
    # Convert experience, skills, education to JSON
    experience_json = [exp.model_dump(exclude_none=True) for exp in cv.experience]
    skills_json = [skill.model_dump(exclude_none=True) for skill in cv.skills]
    education_json = [edu.model_dump(exclude_none=True) for edu in cv.education]
    languages_json = [lang.model_dump(exclude_none=True) for lang in cv.languages] if cv.languages else None
    
    # Extract compensation
    current_comp = None
    if candidate_data.current_compensation:
        current_comp = candidate_data.current_compensation.model_dump(exclude_none=True)
    
    target_comp = None
    if candidate_data.target_compensation:
        target_comp = candidate_data.target_compensation.model_dump(exclude_none=True)
    
    # Extract extraction metadata
    extraction_meta = cv.extraction_meta if cv.extraction_meta else None
    
    return Candidate(
        full_name=candidate_data.full_name,
        email=candidate_data.email,
        phone=candidate_data.phone,
        linkedin_url=candidate_data.linkedin_url,
        location_city=location.city if location else None,
        location_region=location.region if location else None,
        location_country=location.country if location else None,
        remote_preference=location.remote_preference.value if location and location.remote_preference else None,
        right_to_work=candidate_data.right_to_work,
        notice_period_weeks=candidate_data.notice_period_weeks,
        availability_date=candidate_data.availability_date,
        current_compensation=current_comp,
        target_compensation=target_comp,
        experience=experience_json,
        skills=skills_json,
        education=education_json,
        certifications=cv.certifications,
        languages=languages_json,
        resume_url=cv.documents.resume_url if cv.documents else None,
        cover_letter_url=cv.documents.cover_letter_url if cv.documents else None,
        extraction_source=extraction_meta.source if extraction_meta else None,
        extraction_date=extraction_meta.extracted_at if extraction_meta else datetime.utcnow(),
        parser_version=extraction_meta.parser_version if extraction_meta else None,
        consent_granted=consent_granted,
        consent_date=datetime.utcnow() if consent_granted else None,
        data_retention_until=retention_until,
        status="active",
    )


def candidate_db_to_response(candidate: Candidate, detailed: bool = False) -> CandidateResponse | CandidateDetail:
    """
    Convert Candidate (SQLAlchemy) to CandidateResponse or CandidateDetail (Pydantic).
    
    Args:
        candidate: Database model
        detailed: Whether to return detailed schema
    
    Returns:
        CandidateResponse or CandidateDetail
    """
    if detailed:
        return CandidateDetail(
            id=candidate.id,
            full_name=candidate.full_name,
            email=candidate.email,
            phone=candidate.phone,
            linkedin_url=candidate.linkedin_url,
            location_city=candidate.location_city,
            location_region=candidate.location_region,
            location_country=candidate.location_country,
            remote_preference=candidate.remote_preference,
            right_to_work=candidate.right_to_work,
            notice_period_weeks=candidate.notice_period_weeks,
            availability_date=candidate.availability_date,
            current_compensation=candidate.current_compensation,
            target_compensation=candidate.target_compensation,
            experience=candidate.experience,
            skills=candidate.skills,
            education=candidate.education,
            certifications=candidate.certifications,
            languages=candidate.languages,
            resume_url=candidate.resume_url,
            cover_letter_url=candidate.cover_letter_url,
            parser_version=candidate.parser_version,
            data_retention_until=candidate.data_retention_until,
            status=candidate.status,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
        )
    else:
        return CandidateResponse(
            id=candidate.id,
            full_name=candidate.full_name,
            email=candidate.email,
            phone=candidate.phone,
            linkedin_url=candidate.linkedin_url,
            location_city=candidate.location_city,
            location_country=candidate.location_country,
            notice_period_weeks=candidate.notice_period_weeks,
            status=candidate.status,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
        )


def create_candidate(db: Session, cv: CandidateCVNormalized, consent_granted: bool = False) -> Candidate:
    """
    Create a new candidate from parsed CV data.
    
    Args:
        db: Database session
        cv: Parsed CV data
        consent_granted: Whether consent has been granted
    
    Returns:
        Created Candidate database model
    """
    candidate = cv_to_candidate_db(cv, consent_granted=consent_granted)
    
    # Create audit log
    gdpr_manager.create_audit_log(
        action="upload",
        details={"email_hash": gdpr_manager.hash_personal_data(candidate.email) if candidate.email else None}
    )
    
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    
    logger.info(f"Created candidate: {candidate.id} ({candidate.full_name})")
    return candidate


def get_candidate(db: Session, candidate_id: UUID) -> Optional[Candidate]:
    """Get a candidate by ID."""
    return db.query(Candidate).filter(Candidate.id == candidate_id).first()


def get_candidates(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    location_country: Optional[str] = None,
) -> List[Candidate]:
    """
    Get candidates with filtering and pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term (searches name, email)
        status: Filter by status
        location_country: Filter by country
    
    Returns:
        List of Candidate database models
    """
    query = db.query(Candidate)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Candidate.full_name.ilike(f"%{search}%"),
                Candidate.email.ilike(f"%{search}%"),
            )
        )
    
    if status:
        query = query.filter(Candidate.status == status)
    
    if location_country:
        query = query.filter(Candidate.location_country == location_country)
    
    # Filter out deleted candidates by default
    query = query.filter(Candidate.status != "deleted")
    
    # Order by created_at descending (newest first)
    query = query.order_by(Candidate.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def update_candidate(
    db: Session,
    candidate_id: UUID,
    updates: dict
) -> Optional[Candidate]:
    """Update a candidate."""
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        return None
    
    # Update fields
    for key, value in updates.items():
        if hasattr(candidate, key) and value is not None:
            setattr(candidate, key, value)
    
    candidate.updated_at = datetime.utcnow()
    
    # Create audit log
    gdpr_manager.create_audit_log(
        action="update",
        cv_id=str(candidate_id),
        details={"fields_updated": list(updates.keys())}
    )
    
    db.commit()
    db.refresh(candidate)
    
    logger.info(f"Updated candidate: {candidate_id}")
    return candidate


def delete_candidate(db: Session, candidate_id: UUID) -> bool:
    """
    Soft delete a candidate (sets status to 'deleted' for GDPR compliance).
    
    Args:
        db: Database session
        candidate_id: Candidate ID
    
    Returns:
        True if deleted, False if not found
    """
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        return False
    
    # Soft delete (set status to 'deleted')
    candidate.status = "deleted"
    candidate.updated_at = datetime.utcnow()
    
    # Create audit log
    deletion_record = gdpr_manager.prepare_for_deletion({
        "id": str(candidate_id),
        "extraction_meta": {
            "parser_version": candidate.parser_version,
            "source": candidate.extraction_source,
            "extracted_at": candidate.extraction_date.isoformat() if candidate.extraction_date else None,
        }
    })
    
    gdpr_manager.create_audit_log(
        action="delete",
        cv_id=str(candidate_id),
        details=deletion_record
    )
    
    db.commit()
    
    logger.info(f"Soft deleted candidate: {candidate_id}")
    return True

