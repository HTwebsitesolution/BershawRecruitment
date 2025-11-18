import pytest
import json
from datetime import datetime
from app.models import CandidateCVNormalized
from app.services import cv_parser_llm


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
                # Return a valid CandidateCVNormalized JSON structure
                cv_json = {
                    "candidate": {
                        "full_name": "John Smith",
                        "email": "john.smith@example.com",
                        "phone": "+44 7700 900123",
                        "linkedin_url": "https://www.linkedin.com/in/johnsmith",
                        "location": {
                            "city": "Manchester",
                            "country": "UK",
                            "remote_preference": "hybrid"
                        },
                        "right_to_work": ["UK"],
                        "notice_period_weeks": None
                    },
                    "experience": [
                        {
                            "title": "Senior Backend Engineer",
                            "employer": "FintechCo",
                            "location": "Manchester",
                            "start_date": "2022-01",
                            "end_date": None,
                            "is_current": True,
                            "responsibilities": [
                                "Design REST APIs",
                                "Own on-call rotation"
                            ],
                            "achievements": [
                                "Reduced p95 latency by 40%"
                            ],
                            "technologies": ["Node.js", "TypeScript", "Postgres", "AWS ECS"],
                            "team_size": 3
                        }
                    ],
                    "skills": [
                        {
                            "name": "Node.js",
                            "category": "tech",
                            "level": "expert",
                            "evidence": ["Built high-throughput APIs"]
                        },
                        {
                            "name": "AWS",
                            "category": "tech",
                            "level": "advanced",
                            "evidence": ["ECS, RDS in production"]
                        }
                    ],
                    "extraction_meta": {
                        "source": "pdf",
                        "extracted_at": datetime.utcnow().isoformat(),
                        "parser_version": "cvx-1.2.0"
                    }
                }
                return DummyResp(json.dumps(cv_json))


def test_parse_cv_bytes_to_normalized_llm_pdf(monkeypatch):
    """Test LLM-based CV parsing with PDF file"""
    # Mock OpenAI client
    monkeypatch.setattr(cv_parser_llm, "get_openai", lambda: DummyClient())
    
    # Mock text extraction to return sample CV text
    def mock_extract_text(data, filename):
        return """John Smith
Senior Backend Engineer
Email: john.smith@example.com
Phone: +44 7700 900123
LinkedIn: https://www.linkedin.com/in/johnsmith
Location: Manchester, UK

EXPERIENCE
Senior Backend Engineer | FintechCo | Manchester | Jan 2022 - Present
- Design REST APIs
- Own on-call rotation
- Reduced p95 latency by 40%
Technologies: Node.js, TypeScript, Postgres, AWS ECS
Team size: 3

SKILLS
- Node.js (Expert) - Built high-throughput APIs
- AWS (Advanced) - ECS, RDS in production
"""
    
    monkeypatch.setattr(cv_parser_llm, "_extract_text_from_bytes", mock_extract_text)
    
    # Create dummy PDF bytes (just needs to pass the initial check)
    pdf_bytes = b"%PDF-1.4\n" + b"dummy content" * 100
    
    result = cv_parser_llm.parse_cv_bytes_to_normalized_llm(
        data=pdf_bytes,
        filename="john_smith_cv.pdf"
    )
    
    assert isinstance(result, CandidateCVNormalized)
    assert result.candidate.full_name == "John Smith"
    assert result.candidate.email == "john.smith@example.com"
    assert result.candidate.location is not None
    assert result.candidate.location.city == "Manchester"
    assert result.candidate.location.country == "UK"
    assert len(result.experience) > 0
    assert result.experience[0].title == "Senior Backend Engineer"
    assert result.experience[0].employer == "FintechCo"
    assert result.experience[0].is_current is True
    assert len(result.skills) > 0
    assert any(s.name == "Node.js" for s in result.skills)
    assert result.extraction_meta is not None
    assert result.extraction_meta.source == "pdf"


def test_parse_cv_bytes_to_normalized_llm_docx(monkeypatch):
    """Test LLM-based CV parsing with DOCX file"""
    # Mock OpenAI client
    monkeypatch.setattr(cv_parser_llm, "get_openai", lambda: DummyClient())
    
    # Mock text extraction
    def mock_extract_text(data, filename):
        return "John Smith\nSenior Backend Engineer\n..."
    
    monkeypatch.setattr(cv_parser_llm, "_extract_text_from_bytes", mock_extract_text)
    
    # Create dummy DOCX bytes (ZIP signature)
    docx_bytes = b"PK\x03\x04" + b"dummy content" * 100
    
    result = cv_parser_llm.parse_cv_bytes_to_normalized_llm(
        data=docx_bytes,
        filename="cv.docx"
    )
    
    assert isinstance(result, CandidateCVNormalized)
    assert result.candidate.full_name == "John Smith"
    assert result.extraction_meta is not None


def test_parse_cv_bytes_to_normalized_llm_fallback_no_api_key(monkeypatch):
    """Test that it falls back to stub parser when API key not configured"""
    # Mock get_openai to raise RuntimeError (no API key)
    def raise_runtime_error():
        raise RuntimeError("OPENAI_API_KEY not configured")
    
    monkeypatch.setattr(cv_parser_llm, "get_openai", raise_runtime_error)
    
    # Should fall back to stub parser
    pdf_bytes = b"%PDF-1.4\n" + b"dummy content"
    result = cv_parser_llm.parse_cv_bytes_to_normalized_llm(
        data=pdf_bytes,
        filename="test_cv.pdf"
    )
    
    assert isinstance(result, CandidateCVNormalized)
    # Stub parser should return valid structure
    assert result.candidate.full_name  # Should have a name (from filename)
    assert len(result.skills) > 0  # Stub should have skills


def test_parse_cv_bytes_to_normalized_llm_fallback_empty_text(monkeypatch):
    """Test that it falls back to stub parser when text extraction returns empty"""
    # Mock OpenAI client
    monkeypatch.setattr(cv_parser_llm, "get_openai", lambda: DummyClient())
    
    # Mock text extraction to return empty string
    def mock_extract_text_empty(data, filename):
        return ""
    
    monkeypatch.setattr(cv_parser_llm, "_extract_text_from_bytes", mock_extract_text_empty)
    
    pdf_bytes = b"%PDF-1.4\n" + b"dummy content"
    result = cv_parser_llm.parse_cv_bytes_to_normalized_llm(
        data=pdf_bytes,
        filename="empty_cv.pdf"
    )
    
    assert isinstance(result, CandidateCVNormalized)
    # Should fall back to stub, so should have valid structure
    assert result.candidate.full_name


def test_parse_cv_bytes_to_normalized_llm_fallback_invalid_json(monkeypatch):
    """Test that it falls back to stub parser when LLM returns invalid JSON"""
    # Mock OpenAI client to return invalid JSON
    class DummyClientInvalid:
        class chat:
            class completions:
                @staticmethod
                def create(model, messages, **kwargs):
                    return DummyResp("This is not valid JSON")
    
    monkeypatch.setattr(cv_parser_llm, "get_openai", lambda: DummyClientInvalid())
    
    # Mock text extraction
    def mock_extract_text(data, filename):
        return "Some CV text"
    
    monkeypatch.setattr(cv_parser_llm, "_extract_text_from_bytes", mock_extract_text)
    
    pdf_bytes = b"%PDF-1.4\n" + b"dummy content"
    result = cv_parser_llm.parse_cv_bytes_to_normalized_llm(
        data=pdf_bytes,
        filename="test_cv.pdf"
    )
    
    assert isinstance(result, CandidateCVNormalized)
    # Should fall back to stub
    assert result.candidate.full_name


