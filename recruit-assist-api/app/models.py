from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, AnyUrl, EmailStr
from datetime import date, datetime

# ---------- Candidate CV (Normalized) ----------

RemotePref = Literal["remote", "hybrid", "onsite", "unspecified"]

class Location(BaseModel):
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    remote_preference: Optional[RemotePref] = None

class Compensation(BaseModel):
    base_amount: Optional[float] = None
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    period: Optional[Literal["year", "month"]] = None
    bonus_ote: Optional[float] = None
    equity: Optional[str] = None

class TargetCompensation(BaseModel):
    base_min: Optional[float] = None
    base_max: Optional[float] = None
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    period: Optional[Literal["year", "month"]] = None

class CandidateIdentity(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[AnyUrl] = None
    location: Optional[Location] = None
    right_to_work: Optional[List[str]] = None
    notice_period_weeks: Optional[int] = Field(default=None, ge=0)
    availability_date: Optional[date] = None
    current_compensation: Optional[Compensation] = None
    target_compensation: Optional[TargetCompensation] = None

class ExperienceItem(BaseModel):
    title: str
    employer: str
    location: Optional[str] = None
    start_date: str = Field(pattern=r"^\d{4}-\d{2}$")
    end_date: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}$")
    is_current: bool = False
    responsibilities: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    team_size: Optional[int] = Field(default=None, ge=0)

class Skill(BaseModel):
    name: str
    category: Optional[Literal["tech", "sales", "analytics", "management", "language", "other"]] = None
    level: Optional[Literal["novice", "intermediate", "advanced", "expert"]] = "intermediate"
    evidence: Optional[List[str]] = None

class EducationItem(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None

class LanguageProficiency(BaseModel):
    name: str
    proficiency: Optional[Literal["basic", "conversational", "fluent", "native"]] = None

class Documents(BaseModel):
    resume_url: Optional[AnyUrl] = None
    cover_letter_url: Optional[AnyUrl] = None

class ExtractionMeta(BaseModel):
    source: Optional[Literal["pdf", "docx", "linkedin", "text", "other"]] = None
    extracted_at: Optional[datetime] = None
    parser_version: Optional[str] = None

class CandidateCVNormalized(BaseModel):
    candidate: CandidateIdentity
    experience: List[ExperienceItem] = []
    skills: List[Skill]
    education: Optional[List[EducationItem]] = None
    certifications: Optional[List[str]] = None
    languages: Optional[List[LanguageProficiency]] = None
    documents: Optional[Documents] = None
    extraction_meta: Optional[ExtractionMeta] = None

# ---------- Job Description (Normalized) ----------

LocationPolicy = Literal["onsite", "hybrid", "remote"]

class PrimaryLocation(BaseModel):
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

class SalaryBand(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    period: Optional[Literal["year", "month"]] = None

class JobCore(BaseModel):
    title: str
    client: str
    department: Optional[str] = None
    location_policy: LocationPolicy
    onsite_days_per_week: Optional[int] = Field(default=None, ge=0, le=5)
    primary_location: Optional[PrimaryLocation] = None
    salary_band: Optional[SalaryBand] = None
    visa_sponsorship: Optional[Literal["available", "not_available", "case_by_case"]] = None
    clearance_required: Optional[str] = None
    hiring_urgency: Optional[Literal["asap", "this_quarter", "next_quarter"]] = None

class RequirementItem(BaseModel):
    name: str
    weight: Optional[float] = Field(default=0.1, ge=0, le=1)
    evidence_hint: Optional[str] = None

class Requirements(BaseModel):
    must_haves: List[RequirementItem]
    nice_to_haves: List[RequirementItem] = []
    years_experience_min: Optional[int] = Field(default=None, ge=0)
    education_required: Optional[str] = None

class InterviewStage(BaseModel):
    stage_name: str
    duration_minutes: Optional[int] = None
    participants: Optional[List[str]] = None
    assessment_focus: Optional[str] = None

class JobDescriptionNormalized(BaseModel):
    job: JobCore
    requirements: Requirements
    interview_process: Optional[List[InterviewStage]] = None
    role_notes: Optional[str] = None

# ---------- Interview Snapshot (for endorsement) ----------

class InterviewSnapshot(BaseModel):
    notice_period_weeks: Optional[int] = None
    target_comp: Optional[TargetCompensation] = None
    motivation: Optional[str] = None
    location_prefs: Optional[str] = None
    top_skills: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    transcript_text: Optional[str] = None

# ---------- Endorsement Output ----------

class EndorsementOut(BaseModel):
    endorsement_text: str

# ---------- Tone Profile ----------

class ToneProfile(BaseModel):
    persona_name: str = "Jean from Bershaw"
    company: str = "Bershaw"
    style_markers: list[str] = Field(default_factory=lambda: [
        "Warm, succinct, professional",
        "States client value prop in one sentence",
        "Direct ask for CV",
        "Uses 'Are you currently exploring?'",
        "Polite close; no emojis; UK spelling"
    ])
    signoff: str = "Best,\nJean"
    # Short message patterns used by generators:
    templates: dict[str, str] = Field(default_factory=lambda: {
        "initial_connect": (
            "Hi {first_name}, I'm Jean from {company}. I'm recruiting for our client, "
            "a globally influential technology innovator transforming the insurance industry. "
            "They're hiring a {role_title} in {location} ({work_mode}). Are you currently exploring? "
            "If so, can you please send your updated CV?"
        ),
        "after_accept_send_jd": (
            "Sure, {first_name}. Please see the attached JD. I'll wait for your CV. "
            "How much is your current and expected salary? How long is your notice period?"
        ),
        "polite_ack": "Thanks for the quick reply, {first_name}."
    })

