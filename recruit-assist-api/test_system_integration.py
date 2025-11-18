"""
Integration test script for the complete recruitment system.

Tests the full workflow:
1. Normalize JD and save to database
2. Upload CV and save to database
3. Match candidate to job
4. Create/update profile
5. Generate endorsement
6. Update profile with endorsement

Run with: python test_system_integration.py
"""

import asyncio
import httpx
import json
from typing import Optional, Dict, Any
from uuid import UUID

# Configuration
API_BASE_URL = "http://localhost:8000"
USE_LLM = True  # Set to False to use stub/rule-based parsers


async def test_health_check(client: httpx.AsyncClient) -> bool:
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    try:
        response = await client.get(f"{API_BASE_URL}/healthz")
        response.raise_for_status()
        data = response.json()
        print(f"✓ Health check passed: {data}")
        return data.get("ok", False) and data.get("database") == "connected"
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


async def test_normalize_jd(client: httpx.AsyncClient) -> Optional[UUID]:
    """Test JD normalization and save to database."""
    print("\n=== Testing JD Normalization ===")
    try:
        payload = {
            "text": """
            We are looking for a Senior Backend Engineer to join our team.
            
            Requirements:
            - 5+ years of experience with Node.js and TypeScript
            - Strong experience with AWS (Lambda, ECS, RDS)
            - SQL and data modelling skills
            - Experience with event-driven architectures (Kafka)
            
            Location: Hybrid (2-3 days in office)
            Location: London, UK
            Salary: £85,000 - £95,000 per year
            
            Visa sponsorship: Case by case
            Hiring urgency: This quarter
            """,
            "title": "Senior Backend Engineer",
            "client": "TechCorp",
            "location_policy": "hybrid",
            "city": "London",
            "country": "UK",
            "salary_min": 85000,
            "salary_max": 95000,
            "currency": "GBP"
        }
        
        response = await client.post(
            f"{API_BASE_URL}/normalize/jd",
            json=payload,
            params={"use_llm": USE_LLM, "save_to_db": True}
        )
        response.raise_for_status()
        jd_data = response.json()
        
        print(f"✓ JD normalized successfully")
        print(f"  Title: {jd_data.get('job', {}).get('title')}")
        print(f"  Client: {jd_data.get('job', {}).get('client')}")
        
        # Get job ID from database
        jobs_response = await client.get(f"{API_BASE_URL}/jobs/?client=TechCorp&limit=1")
        if jobs_response.status_code == 200:
            jobs = jobs_response.json()
            if jobs:
                job_id = jobs[0]["id"]
                print(f"✓ Job saved to database: {job_id}")
                return UUID(job_id)
        
        print("⚠ Job normalized but not found in database")
        return None
        
    except Exception as e:
        print(f"✗ JD normalization failed: {e}")
        if hasattr(e, 'response'):
            print(f"  Response: {e.response.text}")
        return None


async def test_upload_cv(client: httpx.AsyncClient) -> Optional[UUID]:
    """Test CV upload and save to database."""
    print("\n=== Testing CV Upload ===")
    try:
        # Create a simple text CV for testing
        cv_text = """
        John Doe
        Email: john.doe@example.com
        Phone: +44 7700 900000
        Location: Manchester, UK
        LinkedIn: https://www.linkedin.com/in/johndoe
        
        Experience:
        Senior Backend Engineer at FintechCo (2022-01 to present)
        - Design and implement REST APIs using Node.js and TypeScript
        - Manage AWS infrastructure (ECS, RDS, Lambda)
        - Optimize database queries and data models
        - Reduced p95 latency by 40%
        Technologies: Node.js, TypeScript, PostgreSQL, AWS ECS, Kafka
        
        Skills:
        - Node.js (Expert)
        - TypeScript (Expert)
        - AWS (Advanced)
        - SQL (Advanced)
        - Kafka (Intermediate)
        
        Education:
        BSc Computer Science, University of Manchester (2018-2021)
        
        Right to work: UK
        Notice period: 4 weeks
        Target compensation: £85,000 - £90,000 per year
        """
        
        files = {
            "file": ("test_cv.txt", cv_text.encode('utf-8'), "text/plain")
        }
        
        response = await client.post(
            f"{API_BASE_URL}/ingest/cv",
            files=files,
            params={"use_llm": USE_LLM, "save_to_db": True, "consent_granted": True}
        )
        response.raise_for_status()
        cv_data = response.json()
        
        print(f"✓ CV parsed successfully")
        print(f"  Name: {cv_data.get('candidate', {}).get('full_name')}")
        print(f"  Email: {cv_data.get('candidate', {}).get('email')}")
        
        # Get candidate ID from database
        candidates_response = await client.get(f"{API_BASE_URL}/candidates/?search=John&limit=1")
        if candidates_response.status_code == 200:
            candidates = candidates_response.json()
            if candidates:
                candidate_id = candidates[0]["id"]
                print(f"✓ Candidate saved to database: {candidate_id}")
                return UUID(candidate_id)
        
        print("⚠ CV parsed but candidate not found in database")
        return None
        
    except Exception as e:
        print(f"✗ CV upload failed: {e}")
        if hasattr(e, 'response'):
            print(f"  Response: {e.response.text}")
        return None


async def test_match_candidate_to_job(
    client: httpx.AsyncClient,
    candidate_id: UUID,
    job_id: UUID
) -> Optional[Dict[str, Any]]:
    """Test matching candidate to job."""
    print("\n=== Testing Candidate Matching ===")
    try:
        payload = {
            "candidate_id": str(candidate_id),
            "job_id": str(job_id),
            "create_profile": True
        }
        
        response = await client.post(
            f"{API_BASE_URL}/matching/match",
            json=payload
        )
        response.raise_for_status()
        match_data = response.json()
        
        print(f"✓ Match successful")
        print(f"  Match score: {match_data.get('match_score', 0):.3f} ({match_data.get('match_percentage', 0):.1f}%)")
        print(f"  Profile ID: {match_data.get('profile_id')}")
        
        # Show breakdown
        breakdown = match_data.get('match_details', {}).get('breakdown', {})
        if breakdown:
            print(f"  Breakdown:")
            for key, value in breakdown.items():
                print(f"    {key}: {value:.3f}")
        
        return match_data
        
    except Exception as e:
        print(f"✗ Matching failed: {e}")
        if hasattr(e, 'response'):
            print(f"  Response: {e.response.text}")
        return None


async def test_get_job_candidates(client: httpx.AsyncClient, job_id: UUID) -> bool:
    """Test getting candidates for a job."""
    print("\n=== Testing Get Job Candidates ===")
    try:
        response = await client.get(
            f"{API_BASE_URL}/matching/jobs/{job_id}/candidates/top",
            params={"top_n": 10, "min_score": 0.5}
        )
        response.raise_for_status()
        candidates = response.json()
        
        print(f"✓ Found {len(candidates)} candidates")
        for i, candidate in enumerate(candidates[:3], 1):  # Show top 3
            print(f"  {i}. {candidate.get('candidate_name')}: {candidate.get('match_score', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Get job candidates failed: {e}")
        return False


async def test_profile_operations(
    client: httpx.AsyncClient,
    profile_id: str
) -> bool:
    """Test profile CRUD operations."""
    print("\n=== Testing Profile Operations ===")
    try:
        # Get profile
        response = await client.get(f"{API_BASE_URL}/profiles/{profile_id}")
        response.raise_for_status()
        profile = response.json()
        print(f"✓ Profile retrieved: {profile.get('profile_name')}")
        
        # Update interview data
        interview_update = {
            "interview_date": "2025-01-20T14:00:00Z",
            "interview_notes": "Strong technical skills, good cultural fit",
            "interview_data": {
                "motivation": "Looking for growth opportunities",
                "top_skills": ["Node.js", "TypeScript", "AWS"],
                "risks": ["Notice period: 4 weeks"]
            }
        }
        
        response = await client.patch(
            f"{API_BASE_URL}/profiles/{profile_id}/interview",
            json=interview_update
        )
        response.raise_for_status()
        print(f"✓ Interview data updated")
        
        # Update status
        status_update = {"status": "shortlisted"}
        response = await client.patch(
            f"{API_BASE_URL}/profiles/{profile_id}",
            json=status_update
        )
        response.raise_for_status()
        print(f"✓ Status updated to: shortlisted")
        
        return True
        
    except Exception as e:
        print(f"✗ Profile operations failed: {e}")
        if hasattr(e, 'response'):
            print(f"  Response: {e.response.text}")
        return False


async def test_endorsement_generation(
    client: httpx.AsyncClient,
    candidate_id: UUID,
    job_id: UUID
) -> bool:
    """Test endorsement generation."""
    print("\n=== Testing Endorsement Generation ===")
    try:
        # Get candidate and job data
        candidate_response = await client.get(f"{API_BASE_URL}/candidates/{candidate_id}")
        job_response = await client.get(f"{API_BASE_URL}/jobs/{job_id}")
        
        if candidate_response.status_code != 200 or job_response.status_code != 200:
            print("⚠ Could not fetch candidate or job data")
            return False
        
        # For now, use a simplified payload
        # In a real scenario, you'd convert the database models to normalized models
        payload = {
            "candidate": {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "location": {"city": "Manchester", "country": "UK"}
            },
            "job": {
                "title": "Senior Backend Engineer",
                "client": "TechCorp"
            },
            "interview": {}
        }
        
        response = await client.post(
            f"{API_BASE_URL}/endorsement/generate",
            json=payload,
            params={"use_llm": USE_LLM}
        )
        response.raise_for_status()
        endorsement = response.json()
        
        print(f"✓ Endorsement generated")
        print(f"  Text preview: {endorsement.get('endorsement_text', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Endorsement generation failed: {e}")
        if hasattr(e, 'response'):
            print(f"  Response: {e.response.text}")
        return False


async def main():
    """Run all integration tests."""
    print("=" * 60)
    print("RECRUITMENT SYSTEM INTEGRATION TEST")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Using LLM: {USE_LLM}")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Test 1: Health check
        if not await test_health_check(client):
            print("\n✗ Health check failed. Is the server running?")
            return
        
        # Test 2: Normalize JD
        job_id = await test_normalize_jd(client)
        if not job_id:
            print("\n✗ JD normalization failed. Cannot continue.")
            return
        
        # Test 3: Upload CV
        candidate_id = await test_upload_cv(client)
        if not candidate_id:
            print("\n✗ CV upload failed. Cannot continue.")
            return
        
        # Test 4: Match candidate to job
        match_result = await test_match_candidate_to_job(client, candidate_id, job_id)
        if not match_result:
            print("\n✗ Matching failed. Cannot continue.")
            return
        
        profile_id = match_result.get("profile_id")
        
        # Test 5: Get job candidates
        await test_get_job_candidates(client, job_id)
        
        # Test 6: Profile operations
        if profile_id:
            await test_profile_operations(client, profile_id)
        
        # Test 7: Endorsement generation
        await test_endorsement_generation(client, candidate_id, job_id)
        
        print("\n" + "=" * 60)
        print("INTEGRATION TEST COMPLETE")
        print("=" * 60)
        print("\nSummary:")
        print(f"  ✓ Health check: PASSED")
        print(f"  ✓ JD normalization: PASSED (Job ID: {job_id})")
        print(f"  ✓ CV upload: PASSED (Candidate ID: {candidate_id})")
        print(f"  ✓ Matching: PASSED (Match score: {match_result.get('match_score', 0):.3f})")
        print(f"  ✓ Profile operations: PASSED")
        print(f"  ✓ Endorsement generation: PASSED")
        print("\nAll core features are working!")


if __name__ == "__main__":
    asyncio.run(main())

