import pytest
from app.models import CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot
from app.services import endorsement_llm


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
                return DummyResp("Candidate: Alex — Leeds, UK\nBackground: ...\nMotivation: ...\nCompensation: Unknown → Unknown\nNotice: Unknown\nLocation: Hybrid\nFit vs JD:\n- Node: ✔ — ...\nRisks/Unknowns: None material\nRecommendation: Proceed — ...")


def test_generate_endorsement_llm_monkeypatch(monkeypatch):
    monkeypatch.setattr(endorsement_llm, "get_openai", lambda: DummyClient())

    cv = CandidateCVNormalized.model_validate({
        "candidate": {"full_name": "Alex", "location": {"city": "Leeds", "country": "UK"}},
        "experience": [{"title": "Engineer", "employer": "Co", "start_date": "2022-01", "is_current": True}],
        "skills": [{"name": "Node"}]
    })
    jd = JobDescriptionNormalized.model_validate({
        "job": {"title": "Engineer", "client": "Client", "location_policy": "hybrid"},
        "requirements": {"must_haves": [{"name": "Node"}], "nice_to_haves": []}
    })
    iv = InterviewSnapshot.model_validate({})
    out = endorsement_llm.generate_endorsement_llm(cv, jd, iv)
    assert "Candidate:" in out.endorsement_text
