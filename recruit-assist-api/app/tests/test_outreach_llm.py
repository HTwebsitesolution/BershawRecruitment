import pytest
from app.models import ToneProfile
from app.services import outreach_llm


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
                return DummyResp("Hi Peter, I'm Jean from Bershaw. They're hiring a Country Manager in Davao (hybrid). Are you currently exploring? If so, can you please send your updated CV?")


def test_draft_connect_llm_monkeypatch(monkeypatch):
    monkeypatch.setattr(outreach_llm, "get_openai", lambda: DummyClient())
    tp = ToneProfile()
    text = outreach_llm.draft_connect_llm(tp, first_name="Peter", role_title="Country Manager", location="Davao", work_mode="hybrid")
    assert "Are you currently exploring?" in text
    assert "updated CV" in text
