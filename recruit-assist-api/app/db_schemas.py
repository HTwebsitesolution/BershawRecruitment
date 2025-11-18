"""
Pydantic schemas for database models.

Used for API request/response validation and serialization.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from app.models import CandidateCVNormalized, JobDescriptionNormalized


# Candidate Schemas
class CandidateBase(BaseModel):
    """Base schema for Candidate."""
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema for creating a Candidate from parsed CV."""
    cv_data: CandidateCVNormalized
    consent_granted: bool = False


class CandidateUpdate(BaseModel):
    """Schema for updating a Candidate."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: Optional[str] = None


class CandidateResponse(CandidateBase):
    """Schema for Candidate API response."""
    id: UUID
    location_city: Optional[str] = None
    location_country: Optional[str] = None
    notice_period_weeks: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CandidateDetail(CandidateResponse):
    """Detailed Candidate schema with all fields."""
    location_region: Optional[str] = None
    remote_preference: Optional[str] = None
    right_to_work: Optional[List[str]] = None
    availability_date: Optional[datetime] = None
    current_compensation: Optional[Dict[str, Any]] = None
    target_compensation: Optional[Dict[str, Any]] = None
    experience: List[Dict[str, Any]]
    skills: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: Optional[List[str]] = None
    languages: Optional[List[Dict[str, Any]]] = None
    resume_url: Optional[str] = None
    cover_letter_url: Optional[str] = None
    parser_version: Optional[str] = None
    data_retention_until: Optional[datetime] = None


# Candidate Profile Schemas
class CandidateProfileBase(BaseModel):
    """Base schema for CandidateProfile."""
    profile_name: Optional[str] = None
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    job_posting_id: Optional[UUID] = None


class CandidateProfileCreate(CandidateProfileBase):
    """Schema for creating a CandidateProfile."""
    candidate_id: UUID
    interview_notes: Optional[str] = None
    interview_data: Optional[Dict[str, Any]] = None


class CandidateProfileUpdate(BaseModel):
    """Schema for updating a CandidateProfile."""
    profile_name: Optional[str] = None
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    interview_notes: Optional[str] = None
    interview_data: Optional[Dict[str, Any]] = None
    endorsement_text: Optional[str] = None
    endorsement_recommendation: Optional[str] = None
    endorsement_fit_score: Optional[float] = None
    match_score: Optional[float] = None
    match_details: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class CandidateProfileResponse(CandidateProfileBase):
    """Schema for CandidateProfile API response."""
    id: UUID
    candidate_id: UUID
    match_score: Optional[float] = None
    endorsement_recommendation: Optional[str] = None
    endorsement_fit_score: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CandidateProfileDetail(CandidateProfileResponse):
    """Detailed CandidateProfile schema with all fields."""
    interview_date: Optional[datetime] = None
    interview_notes: Optional[str] = None
    interview_transcript: Optional[str] = None
    interview_data: Optional[Dict[str, Any]] = None
    endorsement_text: Optional[str] = None
    match_details: Optional[Dict[str, Any]] = None
    
    # Booking fields
    booking_link: Optional[str] = None
    booking_id: Optional[str] = None
    booking_provider: Optional[str] = None
    booking_status: Optional[str] = None
    booking_expires_at: Optional[datetime] = None
    
    # AI Interview fields
    ai_interview_id: Optional[str] = None
    ai_interview_provider: Optional[str] = None
    ai_interview_link: Optional[str] = None
    ai_interview_status: Optional[str] = None
    ai_interview_scheduled_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Job Posting Schemas
class JobPostingBase(BaseModel):
    """Base schema for JobPosting."""
    title: str
    client: str
    department: Optional[str] = None


class JobPostingCreate(JobPostingBase):
    """Schema for creating a JobPosting from normalized JD."""
    jd_data: JobDescriptionNormalized


class JobPostingUpdate(BaseModel):
    """Schema for updating a JobPosting."""
    title: Optional[str] = None
    client: Optional[str] = None
    department: Optional[str] = None
    location_policy: Optional[str] = None
    status: Optional[str] = None
    hiring_urgency: Optional[str] = None


class JobPostingResponse(JobPostingBase):
    """Schema for JobPosting API response."""
    id: UUID
    location_policy: Optional[str] = None
    primary_location_city: Optional[str] = None
    primary_location_country: Optional[str] = None
    salary_band_min: Optional[float] = None
    salary_band_max: Optional[float] = None
    salary_currency: Optional[str] = None
    hiring_urgency: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class JobPostingDetail(JobPostingResponse):
    """Detailed JobPosting schema with all fields."""
    onsite_days_per_week: Optional[int] = None
    primary_location_region: Optional[str] = None
    salary_period: Optional[str] = None
    requirements: Dict[str, Any]
    visa_sponsorship: Optional[str] = None
    clearance_required: Optional[str] = None
    interview_process: Optional[List[Dict[str, Any]]] = None
    role_notes: Optional[str] = None

