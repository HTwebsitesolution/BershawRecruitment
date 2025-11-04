import pytest
import json
from app.models import JobDescriptionNormalized
from app.services import jd_normalizer_llm


class DummyMessage:
    def __init__(self, text):
        self.content = text


class DummyChoice:
    def __init__(self, text):
        self.message = DummyMessage(text)


class DummyResp:
    def __init__(self, text):
        self.choices = [DummyChoice(text)]


class DummyClient:
    class chat:
        class completions:
            @staticmethod
            def create(model, messages, **kwargs):
                # Return a valid JobDescriptionNormalized JSON structure
                jd_json = {
                    "job": {
                        "title": "Senior Backend Engineer",
                        "client": "TechCorp Ltd",
                        "department": "Engineering",
                        "location_policy": "hybrid",
                        "onsite_days_per_week": 2,
                        "primary_location": {
                            "city": "London",
                            "country": "UK"
                        },
                        "salary_band": {
                            "min": 85000,
                            "max": 95000,
                            "currency": "GBP",
                            "period": "year"
                        },
                        "visa_sponsorship": "case_by_case",
                        "hiring_urgency": "this_quarter"
                    },
                    "requirements": {
                        "must_haves": [
                            {"name": "Node.js & TypeScript", "weight": 0.3},
                            {"name": "AWS (Lambda/ECS/RDS)", "weight": 0.25},
                            {"name": "SQL & data modelling", "weight": 0.15}
                        ],
                        "nice_to_haves": [
                            {"name": "Kafka/event-driven", "weight": 0.05},
                            {"name": "Kubernetes", "weight": 0.05}
                        ],
                        "years_experience_min": 5,
                        "education_required": None
                    },
                    "role_notes": "Extracted from free-text JD using LLM"
                }
                return DummyResp(json.dumps(jd_json))


def test_normalize_jd_llm_monkeypatch(monkeypatch):
    monkeypatch.setattr(jd_normalizer_llm, "get_openai", lambda: DummyClient())

    # Test with free-text JD
    result = jd_normalizer_llm.normalize_jd_llm(
        text="We're looking for a Senior Backend Engineer to join our team. Must have Node.js, TypeScript, and AWS experience. Hybrid role in London. Salary: £85-95k."
    )

    assert isinstance(result, JobDescriptionNormalized)
    assert result.job.title == "Senior Backend Engineer"
    assert result.job.client == "TechCorp Ltd"
    assert result.job.location_policy == "hybrid"
    assert result.job.primary_location is not None
    assert result.job.primary_location.city == "London"
    assert result.job.primary_location.country == "UK"
    assert result.job.salary_band is not None
    assert result.job.salary_band.min == 85000
    assert result.job.salary_band.max == 95000
    assert len(result.requirements.must_haves) > 0
    assert any("Node.js" in req.name for req in result.requirements.must_haves)


def test_normalize_jd_llm_with_hints(monkeypatch):
    monkeypatch.setattr(jd_normalizer_llm, "get_openai", lambda: DummyClient())

    # Test with structured hints (should be passed to LLM as overrides)
    result = jd_normalizer_llm.normalize_jd_llm(
        text="Looking for a backend engineer...",
        title="Backend Developer",
        client="Startup Inc",
        location_policy="remote",
        salary_min=70000,
        salary_max=90000,
        currency="GBP"
    )

    assert isinstance(result, JobDescriptionNormalized)
    assert result.job.title  # Should be set (either from hint or LLM response)


def test_normalize_jd_llm_fallback_no_api_key(monkeypatch):
    """Test that it falls back to rule-based when API key not configured"""
    # Mock get_openai to raise RuntimeError (no API key)
    def raise_runtime_error():
        raise RuntimeError("OPENAI_API_KEY not configured")
    
    monkeypatch.setattr(jd_normalizer_llm, "get_openai", raise_runtime_error)

    # Should fall back to rule-based normalization
    result = jd_normalizer_llm.normalize_jd_llm(text="Some job description")

    assert isinstance(result, JobDescriptionNormalized)
    # Fallback should still return valid structure (with defaults)
    assert result.job.title  # Should have a default title
    assert result.job.client  # Should have a default client
