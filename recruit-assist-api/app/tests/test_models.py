from app.models import (
    CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot
)

def test_candidate_model_validation():
    payload = {
        "candidate": {
            "full_name": "Alex Morgan",
            "email": "alex@example.com",
            "location": {"city": "Leeds", "country": "UK", "remote_preference": "hybrid"},
            "notice_period_weeks": 4
        },
        "experience": [
            {
                "title": "Senior Backend Engineer",
                "employer": "FintechCo",
                "start_date": "2022-01",
                "is_current": True,
                "technologies": ["Node.js", "TypeScript", "AWS ECS"]
            }
        ],
        "skills": [{"name": "Node.js"}, {"name": "AWS"}]
    }
    model = CandidateCVNormalized.model_validate(payload)
    assert model.candidate.full_name == "Alex Morgan"
    assert model.experience[0].is_current is True
    assert model.skills[0].name == "Node.js"

def test_job_model_validation():
    payload = {
        "job": {
            "title": "Senior Backend Engineer",
            "client": "RetailTech Ltd",
            "location_policy": "hybrid",
            "primary_location": {"city": "Manchester", "country": "UK"}
        },
        "requirements": {
            "must_haves": [{"name": "Node.js & TypeScript", "weight": 0.25}],
            "nice_to_haves": [{"name": "Kafka/event-driven"}],
            "years_experience_min": 5
        }
    }
    jd = JobDescriptionNormalized.model_validate(payload)
    assert jd.job.title == "Senior Backend Engineer"
    assert jd.requirements.must_haves[0].name.startswith("Node.js")

def test_interview_snapshot_validation():
    iv = InterviewSnapshot.model_validate({
        "notice_period_weeks": 4,
        "motivation": "Broader architecture ownership",
        "location_prefs": "Hybrid"
    })
    assert iv.notice_period_weeks == 4
    assert "architecture" in iv.motivation


