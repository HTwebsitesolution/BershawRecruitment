from app.models import CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot
from app.services.endorsement_writer import write_endorsement

def _sample_cv() -> CandidateCVNormalized:
    return CandidateCVNormalized.model_validate({
        "candidate": {
            "full_name": "Alex Morgan",
            "email": "alex@example.com",
            "location": {"city": "Leeds", "country": "UK", "remote_preference": "hybrid"}
        },
        "experience": [{
            "title": "Senior Backend Engineer",
            "employer": "FintechCo",
            "start_date": "2022-01",
            "is_current": True,
            "technologies": ["Node.js", "TypeScript", "Postgres", "AWS ECS"],
            "achievements": ["Reduced p95 latency by 40%"]
        }],
        "skills": [{"name": "Node.js"}, {"name": "AWS"}, {"name": "SQL"}]
    })

def _sample_jd() -> JobDescriptionNormalized:
    return JobDescriptionNormalized.model_validate({
        "job": {
            "title": "Senior Backend Engineer",
            "client": "RetailTech Ltd",
            "location_policy": "hybrid",
            "primary_location": {"city": "Manchester", "country": "UK"}
        },
        "requirements": {
            "must_haves": [
                {"name": "Node.js & TypeScript", "weight": 0.25},
                {"name": "AWS (Lambda/ECS/RDS)", "weight": 0.25},
                {"name": "SQL & data modelling", "weight": 0.15}
            ],
            "nice_to_haves": [{"name": "Kafka/event-driven"}],
            "years_experience_min": 5
        }
    })

def test_write_endorsement_contains_key_sections():
    cv = _sample_cv()
    jd = _sample_jd()
    iv = InterviewSnapshot.model_validate({
        "notice_period_weeks": 4,
        "motivation": "Wants broader architecture ownership.",
        "location_prefs": "Hybrid; 2–3 days in Leeds/Manchester",
        "target_comp": {"base_min": 85000, "base_max": 92000, "currency": "GBP", "period": "year"}
    })
    out = write_endorsement(cv, jd, iv)
    text = out.endorsement_text

    assert "Candidate:" in text
    assert "Fit vs JD:" in text
    assert "Recommendation:" in text
    # Should mark at least two must-haves as met (✔) given the sample CV
    assert text.count("✔") >= 2


