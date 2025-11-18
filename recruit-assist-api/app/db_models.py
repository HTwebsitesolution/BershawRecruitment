"""
Database models for SQLAlchemy ORM.

Defines database tables for:
- Candidates (parsed CVs)
- Candidate Profiles (enriched candidate data)
- Job Postings (job descriptions)
"""

from __future__ import annotations
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from app.database import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Candidate(Base, TimestampMixin):
    """
    Candidate table - stores parsed CV data.
    
    This table stores the normalized CV data after parsing.
    One candidate can have multiple profiles (for different roles/companies).
    """
    __tablename__ = "candidates"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Candidate identity (required fields)
    full_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    
    # Location
    location_city = Column(String(100), nullable=True, index=True)
    location_region = Column(String(100), nullable=True)
    location_country = Column(String(100), nullable=True, index=True)
    remote_preference = Column(String(20), nullable=True)  # remote, hybrid, onsite, unspecified
    
    # Work authorization
    right_to_work = Column(JSON, nullable=True)  # Array of country codes
    
    # Availability
    notice_period_weeks = Column(Integer, nullable=True)
    availability_date = Column(DateTime, nullable=True)
    
    # Compensation (stored as JSON for flexibility)
    current_compensation = Column(JSON, nullable=True)  # {base_amount, currency, period, bonus_ote, equity}
    target_compensation = Column(JSON, nullable=True)  # {base_min, base_max, currency, period}
    
    # Experience (stored as JSON array)
    experience = Column(JSON, nullable=False, default=list)  # Array of ExperienceItem
    
    # Skills (stored as JSON array)
    skills = Column(JSON, nullable=False, default=list)  # Array of Skill
    
    # Education (stored as JSON array)
    education = Column(JSON, nullable=False, default=list)  # Array of EducationItem
    
    # Additional data
    certifications = Column(JSON, nullable=True)  # Array of strings
    languages = Column(JSON, nullable=True)  # Array of LanguageProficiency
    
    # Documents
    resume_url = Column(String(500), nullable=True)
    cover_letter_url = Column(String(500), nullable=True)
    
    # Extraction metadata
    extraction_source = Column(String(50), nullable=True)  # pdf, docx, text, other
    extraction_date = Column(DateTime, nullable=True)
    parser_version = Column(String(50), nullable=True)  # e.g., "cvx-1.2.0"
    
    # GDPR compliance
    consent_granted = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime, nullable=True)
    data_retention_until = Column(DateTime, nullable=True, index=True)
    
    # Status
    status = Column(String(50), default="active", nullable=False, index=True)  # active, archived, deleted
    
    # Relationships
    profiles = relationship("CandidateProfile", back_populates="candidate", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_candidate_email", "email"),
        Index("idx_candidate_name", "full_name"),
        Index("idx_candidate_location", "location_country", "location_city"),
        Index("idx_candidate_status", "status"),
        Index("idx_candidate_retention", "data_retention_until"),
    )
    
    def __repr__(self) -> str:
        return f"<Candidate(id={self.id}, name={self.full_name}, email={self.email})>"


class CandidateProfile(Base, TimestampMixin):
    """
    Candidate Profile table - enriched candidate data for specific roles/companies.
    
    This table stores additional candidate information that may be role-specific or
    company-specific, such as interview notes, endorsements, match scores, etc.
    """
    __tablename__ = "candidate_profiles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to Candidate
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Profile metadata
    profile_name = Column(String(255), nullable=True)  # e.g., "Senior Engineer - TechCorp"
    company_name = Column(String(255), nullable=True, index=True)
    role_title = Column(String(255), nullable=True, index=True)
    
    # Interview data
    interview_date = Column(DateTime, nullable=True)
    interview_notes = Column(Text, nullable=True)
    interview_transcript = Column(Text, nullable=True)
    
    # Interview insights (stored as JSON)
    interview_data = Column(JSON, nullable=True)  # {motivation, target_comp, location_prefs, top_skills, risks, etc.}
    
    # Booking data
    booking_link = Column(String(500), nullable=True)  # Calendar booking link
    booking_id = Column(String(255), nullable=True)  # Provider booking ID
    booking_provider = Column(String(50), nullable=True)  # google, calendly, outlook, manual
    booking_status = Column(String(50), nullable=True)  # pending, confirmed, cancelled, completed
    booking_expires_at = Column(DateTime, nullable=True)
    
    # AI Interview data
    ai_interview_id = Column(String(255), nullable=True)  # AI interviewer session ID
    ai_interview_provider = Column(String(50), nullable=True)  # hirevue, myinterview, custom
    ai_interview_link = Column(String(500), nullable=True)  # Interview link
    ai_interview_status = Column(String(50), nullable=True)  # scheduled, in_progress, completed, cancelled
    ai_interview_scheduled_at = Column(DateTime, nullable=True)
    
    # Endorsement
    endorsement_text = Column(Text, nullable=True)
    endorsement_recommendation = Column(String(20), nullable=True)  # Proceed, Hold, Reject
    endorsement_fit_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Match data (if linked to a job posting)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True, index=True)
    match_score = Column(Float, nullable=True)  # 0.0 to 1.0
    match_details = Column(JSON, nullable=True)  # {skills_match, experience_match, location_match, etc.}
    
    # Status
    status = Column(String(50), default="active", nullable=False, index=True)  # active, shortlisted, rejected, hired, archived
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="profiles")
    job_posting = relationship("JobPosting", back_populates="profiles")
    
    # Indexes
    __table_args__ = (
        Index("idx_profile_candidate", "candidate_id"),
        Index("idx_profile_job", "job_posting_id"),
        Index("idx_profile_status", "status"),
        Index("idx_profile_match_score", "match_score"),
    )
    
    def __repr__(self) -> str:
        return f"<CandidateProfile(id={self.id}, candidate_id={self.candidate_id}, role={self.role_title})>"


class JobPosting(Base, TimestampMixin):
    """
    Job Posting table - stores normalized job descriptions.
    
    This table stores job postings with normalized data from job descriptions.
    """
    __tablename__ = "job_postings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job core information
    title = Column(String(255), nullable=False, index=True)
    client = Column(String(255), nullable=False, index=True)
    department = Column(String(255), nullable=True)
    
    # Location
    location_policy = Column(String(20), nullable=True)  # onsite, hybrid, remote
    onsite_days_per_week = Column(Integer, nullable=True)
    primary_location_city = Column(String(100), nullable=True, index=True)
    primary_location_region = Column(String(100), nullable=True)
    primary_location_country = Column(String(100), nullable=True, index=True)
    
    # Compensation
    salary_band_min = Column(Float, nullable=True)
    salary_band_max = Column(Float, nullable=True)
    salary_currency = Column(String(3), nullable=True)  # ISO 4217 code
    salary_period = Column(String(10), nullable=True)  # year, month
    
    # Requirements (stored as JSON for flexibility)
    requirements = Column(JSON, nullable=False)  # {must_haves, nice_to_haves, years_experience_min, education_required}
    
    # Additional information
    visa_sponsorship = Column(String(20), nullable=True)  # available, not_available, case_by_case
    clearance_required = Column(String(255), nullable=True)
    hiring_urgency = Column(String(20), nullable=True)  # asap, this_quarter, next_quarter
    
    # Interview process
    interview_process = Column(JSON, nullable=True)  # Array of InterviewStage
    
    # Additional notes
    role_notes = Column(Text, nullable=True)
    
    # Normalization metadata
    original_text = Column(Text, nullable=True)  # Original job description text (if provided)
    normalization_date = Column(DateTime, nullable=True)
    normalizer_version = Column(String(50), nullable=True)  # e.g., "jdx-1.0.0"
    
    # Status
    status = Column(String(50), default="active", nullable=False, index=True)  # active, closed, filled, archived
    
    # Relationships
    profiles = relationship("CandidateProfile", back_populates="job_posting")
    
    # Indexes
    __table_args__ = (
        Index("idx_job_title", "title"),
        Index("idx_job_client", "client"),
        Index("idx_job_location", "primary_location_country", "primary_location_city"),
        Index("idx_job_status", "status"),
        Index("idx_job_urgency", "hiring_urgency"),
    )
    
    def __repr__(self) -> str:
        return f"<JobPosting(id={self.id}, title={self.title}, client={self.client})>"

