"""
Candidate Matching Service

Scores candidates against job postings based on multiple factors:
- Skills match (must-haves and nice-to-haves)
- Experience match (years of experience)
- Location match (remote preference, country)
- Salary match (target vs job salary band)
- Right to work (visa requirements)
"""

from __future__ import annotations
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID

from app.db_models import Candidate, JobPosting, CandidateProfile
from app.services.candidate_service import get_candidate
from app.services.job_posting_service import get_job_posting

logger = logging.getLogger(__name__)

# Matching weights (must sum to 1.0)
WEIGHTS = {
    "skills_must_have": 0.35,  # Most important - must-have skills
    "skills_nice_have": 0.10,  # Nice-to-have skills
    "experience": 0.20,  # Years of experience
    "location": 0.15,  # Location and remote preference
    "salary": 0.10,  # Salary expectations vs job range
    "right_to_work": 0.10,  # Visa/work authorization
}


def _normalize_skill_name(skill_name: str) -> str:
    """Normalize skill name for comparison (lowercase, strip, handle variations)."""
    # Remove common variations
    normalized = skill_name.lower().strip()
    # Handle common aliases (can be expanded)
    aliases = {
        "node": "node.js",
        "nodejs": "node.js",
        "js": "javascript",
        "reactjs": "react",
        "vuejs": "vue",
        "postgres": "postgresql",
        "aws": "amazon web services",
    }
    for alias, canonical in aliases.items():
        if alias in normalized:
            normalized = normalized.replace(alias, canonical)
    return normalized


def _check_skill_match(requirement: str, candidate_skills: List[str], candidate_technologies: List[str]) -> Tuple[float, str]:
    """
    Check if a requirement matches candidate skills.
    
    Returns:
        Tuple of (match_score, evidence)
        - match_score: 1.0 (exact match), 0.5 (partial match), 0.0 (no match)
        - evidence: String with matched skill/technology
    """
    req_lower = _normalize_skill_name(requirement)
    req_tokens = set(req_lower.split())
    
    # Check for exact match in skills
    for skill in candidate_skills:
        skill_normalized = _normalize_skill_name(skill)
        if req_lower in skill_normalized or skill_normalized in req_lower:
            return 1.0, skill
    
    # Check for token overlap (partial match)
    for skill in candidate_skills:
        skill_normalized = _normalize_skill_name(skill)
        skill_tokens = set(skill_normalized.split())
        overlap = req_tokens.intersection(skill_tokens)
        if overlap and len(overlap) >= len(req_tokens) * 0.5:  # At least 50% token overlap
            return 0.5, skill
    
    # Check technologies from experience
    for tech in candidate_technologies:
        tech_normalized = _normalize_skill_name(tech)
        if req_lower in tech_normalized or tech_normalized in req_lower:
            return 1.0, tech
        
        tech_tokens = set(tech_normalized.split())
        overlap = req_tokens.intersection(tech_tokens)
        if overlap and len(overlap) >= len(req_tokens) * 0.5:
            return 0.5, tech
    
    return 0.0, ""


def calculate_skills_score(
    must_haves: List[Dict[str, Any]],
    nice_to_haves: List[Dict[str, Any]],
    candidate_skills: List[str],
    candidate_technologies: List[str]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate skills match score (0.0 to 1.0).
    
    Args:
        must_haves: List of must-have requirements (with name and weight)
        nice_to_haves: List of nice-to-have requirements (with name and weight)
        candidate_skills: List of candidate skill names
        candidate_technologies: List of technologies from experience
    
    Returns:
        Tuple of (score, details)
    """
    must_have_score = 0.0
    must_have_matches = []
    must_have_total_weight = sum(req.get("weight", 0.5) for req in must_haves)
    
    if must_have_total_weight > 0:
        for req in must_haves:
            req_name = req.get("name", "")
            req_weight = req.get("weight", 0.5)
            match_score, evidence = _check_skill_match(req_name, candidate_skills, candidate_technologies)
            
            if match_score > 0:
                must_have_score += (match_score * req_weight) / must_have_total_weight
                must_have_matches.append({
                    "requirement": req_name,
                    "match_score": match_score,
                    "evidence": evidence,
                    "weight": req_weight
                })
    
    nice_have_score = 0.0
    nice_have_matches = []
    nice_have_total_weight = sum(req.get("weight", 0.3) for req in nice_to_haves)
    
    if nice_have_total_weight > 0:
        for req in nice_to_haves:
            req_name = req.get("name", "")
            req_weight = req.get("weight", 0.3)
            match_score, evidence = _check_skill_match(req_name, candidate_skills, candidate_technologies)
            
            if match_score > 0:
                nice_have_score += (match_score * req_weight) / nice_have_total_weight
                nice_have_matches.append({
                    "requirement": req_name,
                    "match_score": match_score,
                    "evidence": evidence,
                    "weight": req_weight
                })
    
    # Return separate scores (will be combined in overall score calculation)
    return {
        "must_have_score": must_have_score,
        "nice_have_score": nice_have_score,
    }, {
        "must_have_score": must_have_score,
        "must_have_matches": must_have_matches,
        "must_have_total": len(must_haves),
        "nice_have_score": nice_have_score,
        "nice_have_matches": nice_have_matches,
        "nice_have_total": len(nice_to_haves),
    }


def calculate_experience_score(
    required_years: Optional[int],
    candidate_experience: List[Dict[str, Any]]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate experience match score based on years of experience.
    
    Args:
        required_years: Minimum years required (from JD)
        candidate_experience: List of experience items from CV
    
    Returns:
        Tuple of (score, details)
    """
    if not required_years or required_years == 0:
        return 1.0, {"years_required": 0, "years_actual": 0, "score": 1.0}
    
    # Calculate total years from experience
    total_years = 0.0
    for exp in candidate_experience:
        start_date = exp.get("start_date")
        end_date = exp.get("end_date")
        
        if start_date:
            try:
                start_year = int(start_date.split('-')[0])
                start_month = int(start_date.split('-')[1]) if len(start_date.split('-')) > 1 else 1
                
                if end_date:
                    end_year = int(end_date.split('-')[0])
                    end_month = int(end_date.split('-')[1]) if len(end_date.split('-')) > 1 else 1
                else:
                    # Current role
                    now = datetime.utcnow()
                    end_year = now.year
                    end_month = now.month
                
                # Calculate months
                months = (end_year - start_year) * 12 + (end_month - start_month)
                total_years += months / 12.0
            except (ValueError, IndexError):
                pass
    
    # Score based on meeting/exceeding requirement
    if total_years >= required_years:
        score = 1.0  # Meets or exceeds requirement
    elif total_years >= required_years * 0.8:
        score = 0.8  # Close to requirement (within 20%)
    elif total_years >= required_years * 0.6:
        score = 0.6  # Somewhat close (within 40%)
    else:
        score = max(0.0, total_years / required_years)  # Proportion of requirement
    
    return score, {
        "years_required": required_years,
        "years_actual": round(total_years, 1),
        "score": score
    }


def calculate_location_score(
    job_location_country: Optional[str],
    job_location_city: Optional[str],
    job_location_policy: Optional[str],
    candidate_location_country: Optional[str],
    candidate_location_city: Optional[str],
    candidate_remote_pref: Optional[str],
    candidate_right_to_work: Optional[List[str]]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate location match score.
    
    Args:
        job_location_country: Job country
        job_location_city: Job city (optional)
        job_location_policy: Job location policy (onsite, hybrid, remote)
        candidate_location_country: Candidate country
        candidate_location_city: Candidate city (optional)
        candidate_remote_pref: Candidate remote preference
        candidate_right_to_work: List of countries candidate can work in
    
    Returns:
        Tuple of (score, details)
    """
    score = 0.0
    details = {
        "location_match": False,
        "remote_compatibility": False,
        "right_to_work": False,
    }
    
    # Check right to work
    if job_location_country and candidate_right_to_work:
        if job_location_country in candidate_right_to_work:
            details["right_to_work"] = True
            score += 0.3  # 30% of location score
        elif any(country.upper() == job_location_country.upper() for country in candidate_right_to_work):
            details["right_to_work"] = True
            score += 0.3
    
    # Check country match
    if job_location_country and candidate_location_country:
        if job_location_country.upper() == candidate_location_country.upper():
            details["location_match"] = True
            score += 0.4  # 40% of location score
            
            # Bonus for city match
            if job_location_city and candidate_location_city:
                if job_location_city.upper() == candidate_location_city.upper():
                    score += 0.2  # Additional 20% for city match
    
    # Check remote preference compatibility
    if job_location_policy and candidate_remote_pref:
        job_policy = job_location_policy.lower()
        candidate_pref = candidate_remote_pref.lower() if candidate_remote_pref else ""
        
        # Remote jobs work for anyone
        if job_policy == "remote":
            details["remote_compatibility"] = True
            score += 0.3
        # Hybrid jobs work for remote/hybrid candidates
        elif job_policy == "hybrid" and candidate_pref in ["remote", "hybrid"]:
            details["remote_compatibility"] = True
            score += 0.3
        # Onsite jobs work for onsite/hybrid candidates
        elif job_policy == "onsite" and candidate_pref in ["onsite", "hybrid"]:
            details["remote_compatibility"] = True
            score += 0.3
    
    return min(1.0, score), details


def calculate_salary_score(
    job_salary_min: Optional[float],
    job_salary_max: Optional[float],
    job_salary_currency: Optional[str],
    candidate_target_min: Optional[float],
    candidate_target_max: Optional[float],
    candidate_target_currency: Optional[str]
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate salary match score.
    
    Args:
        job_salary_min: Job minimum salary
        job_salary_max: Job maximum salary
        job_salary_currency: Job salary currency
        candidate_target_min: Candidate target minimum
        candidate_target_max: Candidate target maximum
        candidate_target_currency: Candidate target currency
    
    Returns:
        Tuple of (score, details)
    """
    # If no salary info, return neutral score
    if not job_salary_min or not candidate_target_min:
        return 0.5, {"score": 0.5, "reason": "Insufficient salary data"}
    
    # Currency mismatch reduces score
    currency_match = True
    if job_salary_currency and candidate_target_currency:
        currency_match = job_salary_currency.upper() == candidate_target_currency.upper()
    
    if not currency_match:
        return 0.3, {"score": 0.3, "reason": "Currency mismatch"}
    
    # Check if candidate's target range overlaps with job's range
    candidate_avg = (candidate_target_min + (candidate_target_max or candidate_target_min)) / 2
    job_avg = (job_salary_min + (job_salary_max or job_salary_min)) / 2
    
    # Perfect match: candidate's range is within job's range
    if candidate_target_min >= job_salary_min and (not candidate_target_max or candidate_target_max <= job_salary_max):
        return 1.0, {"score": 1.0, "candidate_avg": candidate_avg, "job_avg": job_avg, "reason": "Target within job range"}
    
    # Overlap: ranges overlap
    if candidate_target_min <= job_salary_max and (not candidate_target_max or candidate_target_max >= job_salary_min):
        overlap_min = max(candidate_target_min, job_salary_min)
        overlap_max = min(candidate_target_max or float('inf'), job_salary_max or float('inf'))
        overlap_size = overlap_max - overlap_min
        job_range_size = (job_salary_max or job_salary_min) - job_salary_min
        overlap_ratio = overlap_size / job_range_size if job_range_size > 0 else 0
        return 0.5 + (overlap_ratio * 0.5), {"score": 0.5 + (overlap_ratio * 0.5), "overlap_ratio": overlap_ratio, "reason": "Partial overlap"}
    
    # No overlap: calculate penalty based on distance
    if candidate_avg > job_avg:
        # Candidate expects more than job offers
        penalty = min(1.0, (candidate_avg - job_avg) / job_avg)  # Penalty as percentage
        return max(0.0, 0.5 - penalty), {"score": max(0.0, 0.5 - penalty), "penalty": penalty, "reason": "Target above job range"}
    else:
        # Candidate expects less than job offers (good, but slight penalty for being too low)
        return 0.7, {"score": 0.7, "reason": "Target below job range (acceptable)"}


def calculate_match_score(
    candidate: Candidate,
    job: JobPosting
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate overall match score between candidate and job posting.
    
    Args:
        candidate: Candidate database model
        job: Job posting database model
    
    Returns:
        Tuple of (overall_score, match_details)
        - overall_score: 0.0 to 1.0
        - match_details: Dict with breakdown by category
    """
    # Extract candidate skills and technologies
    candidate_skills = [skill.get("name", "") for skill in (candidate.skills or []) if skill.get("name")]
    candidate_technologies = []
    for exp in (candidate.experience or []):
        for tech in (exp.get("technologies") or []):
            if tech and tech not in candidate_technologies:
                candidate_technologies.append(tech)
    
    # Extract requirements
    requirements = job.requirements or {}
    must_haves = requirements.get("must_haves", [])
    nice_to_haves = requirements.get("nice_to_haves", [])
    required_years = requirements.get("years_experience_min")
    
    # Calculate component scores
    skills_scores, skills_details = calculate_skills_score(
        must_haves, nice_to_haves, candidate_skills, candidate_technologies
    )
    must_have_skills_score = skills_scores["must_have_score"]
    nice_have_skills_score = skills_scores["nice_have_score"]
    
    experience_score, experience_details = calculate_experience_score(
        required_years, candidate.experience or []
    )
    
    location_score, location_details = calculate_location_score(
        job.primary_location_country,
        job.primary_location_city,
        job.location_policy,
        candidate.location_country,
        candidate.location_city,
        candidate.remote_preference,
        candidate.right_to_work
    )
    
    # Extract salary info
    target_comp = candidate.target_compensation or {}
    salary_score, salary_details = calculate_salary_score(
        job.salary_band_min,
        job.salary_band_max,
        job.salary_currency,
        target_comp.get("base_min"),
        target_comp.get("base_max"),
        target_comp.get("currency")
    )
    
    # Calculate weighted overall score
    right_to_work_score = 1.0 if location_details.get("right_to_work") else 0.0
    
    overall_score = (
        must_have_skills_score * WEIGHTS["skills_must_have"] +
        nice_have_skills_score * WEIGHTS["skills_nice_have"] +
        experience_score * WEIGHTS["experience"] +
        location_score * WEIGHTS["location"] +
        salary_score * WEIGHTS["salary"] +
        right_to_work_score * WEIGHTS["right_to_work"]
    )
    
    # Build match details
    match_details = {
        "overall_score": round(overall_score, 3),
        "skills": skills_details,
        "experience": experience_details,
        "location": location_details,
        "salary": salary_details,
        "weights": WEIGHTS,
        "breakdown": {
            "must_have_skills_contribution": round(must_have_skills_score * WEIGHTS["skills_must_have"], 3),
            "nice_have_skills_contribution": round(nice_have_skills_score * WEIGHTS["skills_nice_have"], 3),
            "experience_contribution": round(experience_score * WEIGHTS["experience"], 3),
            "location_contribution": round(location_score * WEIGHTS["location"], 3),
            "salary_contribution": round(salary_score * WEIGHTS["salary"], 3),
            "right_to_work_contribution": round(right_to_work_score * WEIGHTS["right_to_work"], 3),
        }
    }
    
    return overall_score, match_details


def match_candidate_to_job(
    db: Session,
    candidate_id: UUID,
    job_id: UUID,
    create_profile: bool = True
) -> Tuple[float, Dict[str, Any], Optional[CandidateProfile]]:
    """
    Match a candidate to a job posting and optionally create/update a profile.
    
    Args:
        db: Database session
        candidate_id: Candidate ID
        job_id: Job posting ID
        create_profile: Whether to create/update CandidateProfile
    
    Returns:
        Tuple of (match_score, match_details, profile)
    """
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise ValueError(f"Candidate not found: {candidate_id}")
    
    job = get_job_posting(db, job_id)
    if not job:
        raise ValueError(f"Job posting not found: {job_id}")
    
    # Calculate match score
    match_score, match_details = calculate_match_score(candidate, job)
    
    # Create or update profile if requested
    profile = None
    if create_profile:
        # Check if profile already exists
        existing_profile = db.query(CandidateProfile).filter(
            CandidateProfile.candidate_id == candidate_id,
            CandidateProfile.job_posting_id == job_id
        ).first()
        
        if existing_profile:
            # Update existing profile
            existing_profile.match_score = match_score
            existing_profile.match_details = match_details
            existing_profile.updated_at = datetime.utcnow()
            profile = existing_profile
        else:
            # Create new profile
            profile = CandidateProfile(
                candidate_id=candidate_id,
                job_posting_id=job_id,
                profile_name=f"{candidate.full_name} - {job.title} at {job.client}",
                company_name=job.client,
                role_title=job.title,
                match_score=match_score,
                match_details=match_details,
                status="active"
            )
            db.add(profile)
        
        db.commit()
        db.refresh(profile)
    
    logger.info(f"Matched candidate {candidate_id} to job {job_id}: score={match_score:.3f}")
    
    return match_score, match_details, profile


def match_all_candidates_to_job(
    db: Session,
    job_id: UUID,
    min_score: float = 0.0,
    limit: int = 100
) -> List[Tuple[Candidate, float, Dict[str, Any]]]:
    """
    Match all candidates to a job posting.
    
    Args:
        db: Database session
        job_id: Job posting ID
        min_score: Minimum match score to include
        limit: Maximum number of results
    
    Returns:
        List of tuples (candidate, match_score, match_details) sorted by score
    """
    job = get_job_posting(db, job_id)
    if not job:
        raise ValueError(f"Job posting not found: {job_id}")
    
    # Get all active candidates
    candidates = db.query(Candidate).filter(
        Candidate.status == "active"
    ).limit(limit * 10).all()  # Get more candidates than limit to account for filtering
    
    # Calculate matches
    matches = []
    for candidate in candidates:
        try:
            match_score, match_details = calculate_match_score(candidate, job)
            if match_score >= min_score:
                matches.append((candidate, match_score, match_details))
        except Exception as e:
            logger.warning(f"Error calculating match for candidate {candidate.id}: {e}")
            continue
    
    # Sort by match score (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    
    # Limit results
    return matches[:limit]


def match_candidate_to_all_jobs(
    db: Session,
    candidate_id: UUID,
    min_score: float = 0.0,
    limit: int = 100
) -> List[Tuple[JobPosting, float, Dict[str, Any]]]:
    """
    Match a candidate to all job postings.
    
    Args:
        db: Database session
        candidate_id: Candidate ID
        min_score: Minimum match score to include
        limit: Maximum number of results
    
    Returns:
        List of tuples (job, match_score, match_details) sorted by score
    """
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise ValueError(f"Candidate not found: {candidate_id}")
    
    # Get all active job postings
    jobs = db.query(JobPosting).filter(
        JobPosting.status == "active"
    ).limit(limit * 10).all()  # Get more jobs than limit to account for filtering
    
    # Calculate matches
    matches = []
    for job in jobs:
        try:
            match_score, match_details = calculate_match_score(candidate, job)
            if match_score >= min_score:
                matches.append((job, match_score, match_details))
        except Exception as e:
            logger.warning(f"Error calculating match for job {job.id}: {e}")
            continue
    
    # Sort by match score (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    
    # Limit results
    return matches[:limit]

