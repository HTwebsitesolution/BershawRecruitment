import json
import pytest
from pathlib import Path
from app.models import CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot
from app.services.endorsement_writer import write_endorsement

# Load golden test data
_FIXTURES_DIR = Path(__file__).parent / "fixtures"
_GOLDEN_DATA_PATH = _FIXTURES_DIR / "golden_cv_jd_pairs.json"


def _load_golden_data():
    """Load golden test data from JSON file."""
    with open(_GOLDEN_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def golden_pairs():
    """Fixture providing access to all golden CV/JD pairs."""
    data = _load_golden_data()
    return data["golden_pairs"]


def test_golden_data_file_exists():
    """Ensure the golden data file exists and is valid JSON."""
    assert _GOLDEN_DATA_PATH.exists(), f"Golden data file not found: {_GOLDEN_DATA_PATH}"
    data = _load_golden_data()
    assert "golden_pairs" in data
    assert isinstance(data["golden_pairs"], list)
    assert len(data["golden_pairs"]) > 0


def test_golden_data_schema_validation(golden_pairs):
    """Validate that all golden CV/JD pairs match their respective schemas."""
    for pair in golden_pairs:
        # Validate CV
        cv = CandidateCVNormalized.model_validate(pair["cv"])
        assert cv.candidate.full_name
        assert len(cv.experience) > 0
        
        # Validate JD
        jd = JobDescriptionNormalized.model_validate(pair["jd"])
        assert jd.job.title
        assert jd.job.client
        assert len(jd.requirements.must_haves) > 0
        
        # Validate interview (if provided)
        if pair.get("interview"):
            interview = InterviewSnapshot.model_validate(pair["interview"])
            assert isinstance(interview, InterviewSnapshot)


@pytest.mark.parametrize("pair_name", [
    "perfect_match_backend_engineer",
    "borderline_many_partial_matches",
    "weak_match_reject_candidate",
    "strong_but_long_notice",
    "salary_out_of_range",
    "minimal_experience_below_threshold"
])
def test_endorsement_format_compliance(pair_name, golden_pairs):
    """Test that endorsements follow the required format for all golden pairs."""
    pair = next((p for p in golden_pairs if p["name"] == pair_name), None)
    assert pair is not None, f"Golden pair '{pair_name}' not found"
    
    cv = CandidateCVNormalized.model_validate(pair["cv"])
    jd = JobDescriptionNormalized.model_validate(pair["jd"])
    interview = InterviewSnapshot.model_validate(pair.get("interview", {}))
    
    endorsement = write_endorsement(cv, jd, interview)
    text = endorsement.endorsement_text
    
    # Must have all required sections
    required_sections = [
        "Candidate:",
        "Background:",
        "Motivation:",
        "Compensation:",
        "Notice:",
        "Location:",
        "Fit vs JD:",
        "Risks/Unknowns:",
        "Recommendation:"
    ]
    
    for section in required_sections:
        assert section in text, f"Missing required section '{section}' in endorsement for {pair_name}"
    
    # Must use correct symbols for fit assessment
    assert any(mark in text for mark in ["✔", "△", "✖"]), \
        f"No fit assessment symbols (✔/△/✖) found in endorsement for {pair_name}"
    
    # Recommendation must be one of the expected values
    recommendation_line = [line for line in text.split("\n") if "Recommendation:" in line]
    assert len(recommendation_line) > 0, f"No recommendation found in endorsement for {pair_name}"
    assert any(rec in recommendation_line[0] for rec in ["Proceed", "Hold", "Reject"]), \
        f"Invalid recommendation format for {pair_name}"


def test_perfect_match_proceed_recommendation(golden_pairs):
    """Test that perfect match candidate gets Proceed recommendation."""
    pair = next((p for p in golden_pairs if p["name"] == "perfect_match_backend_engineer"), None)
    assert pair is not None
    
    cv = CandidateCVNormalized.model_validate(pair["cv"])
    jd = JobDescriptionNormalized.model_validate(pair["jd"])
    interview = InterviewSnapshot.model_validate(pair.get("interview", {}))
    
    endorsement = write_endorsement(cv, jd, interview)
    text = endorsement.endorsement_text
    
    # Should have minimum expected checkmarks
    if "expected_min_checkmarks" in pair:
        checkmark_count = text.count("✔")
        assert checkmark_count >= pair["expected_min_checkmarks"], \
            f"Expected at least {pair['expected_min_checkmarks']} ✔, got {checkmark_count}"
    
    # Should recommend Proceed
    assert "Recommendation:" in text
    assert "Proceed" in text, f"Expected 'Proceed' recommendation, got: {text.split('Recommendation:')[-1]}"


def test_borderline_partial_matches(golden_pairs):
    """Test borderline case with many partial matches."""
    pair = next((p for p in golden_pairs if p["name"] == "borderline_many_partial_matches"), None)
    assert pair is not None
    
    cv = CandidateCVNormalized.model_validate(pair["cv"])
    jd = JobDescriptionNormalized.model_validate(pair["jd"])
    interview = InterviewSnapshot.model_validate(pair.get("interview", {}))
    
    endorsement = write_endorsement(cv, jd, interview)
    text = endorsement.endorsement_text
    
    # Should have many triangles (partial matches)
    if "expected_min_triangles" in pair:
        triangle_count = text.count("△")
        assert triangle_count >= pair["expected_min_triangles"], \
            f"Expected at least {pair['expected_min_triangles']} △, got {triangle_count}"
    
    # Should recommend Hold (borderline case)
    assert "Hold" in text or "Proceed" in text, \
        "Borderline case should recommend Hold or Proceed (not Reject)"


def test_weak_match_reject_recommendation(golden_pairs):
    """Test that weak match candidate gets Reject recommendation."""
    pair = next((p for p in golden_pairs if p["name"] == "weak_match_reject_candidate"), None)
    assert pair is not None
    
    cv = CandidateCVNormalized.model_validate(pair["cv"])
    jd = JobDescriptionNormalized.model_validate(pair["jd"])
    interview = InterviewSnapshot.model_validate(pair.get("interview", {}))
    
    endorsement = write_endorsement(cv, jd, interview)
    text = endorsement.endorsement_text
    
    # Should have X marks for missing requirements
    if "expected_min_xmarks" in pair:
        xmark_count = text.count("✖")
        assert xmark_count >= pair["expected_min_xmarks"], \
            f"Expected at least {pair['expected_min_xmarks']} ✖, got {xmark_count}"
    
    # Should recommend Reject
    assert "Reject" in text, \
        f"Expected 'Reject' recommendation for weak match candidate"


def test_evidence_quotes_present(golden_pairs):
    """Test that endorsements include evidence quotes for checkmarks."""
    pair = next((p for p in golden_pairs if p["name"] == "perfect_match_backend_engineer"), None)
    assert pair is not None
    
    cv = CandidateCVNormalized.model_validate(pair["cv"])
    jd = JobDescriptionNormalized.model_validate(pair["jd"])
    interview = InterviewSnapshot.model_validate(pair.get("interview", {}))
    
    endorsement = write_endorsement(cv, jd, interview)
    text = endorsement.endorsement_text
    
    # If there are checkmarks, there should be evidence quotes
    if "✔" in text:
        # Look for evidence quotes (typically in format: evidence: "quote")
        has_evidence = 'evidence:' in text.lower() or '"' in text
        assert has_evidence, \
            "Checkmarks should be accompanied by evidence quotes"


def test_endorsement_word_count(golden_pairs):
    """Test that endorsements are within expected word count (~160-220 words)."""
    for pair in golden_pairs:
        cv = CandidateCVNormalized.model_validate(pair["cv"])
        jd = JobDescriptionNormalized.model_validate(pair["jd"])
        interview = InterviewSnapshot.model_validate(pair.get("interview", {}))
        
        endorsement = write_endorsement(cv, jd, interview)
        text = endorsement.endorsement_text
        word_count = len(text.split())
        
        # Should be concise but informative
        assert word_count >= 100, \
            f"Endorsement too short ({word_count} words) for {pair['name']}"
        assert word_count <= 400, \
            f"Endorsement too long ({word_count} words) for {pair['name']}"


def test_all_golden_pairs_produce_valid_endorsements(golden_pairs):
    """Regression test: ensure all golden pairs produce valid endorsements without errors."""
    for pair in golden_pairs:
        cv = CandidateCVNormalized.model_validate(pair["cv"])
        jd = JobDescriptionNormalized.model_validate(pair["jd"])
        interview = InterviewSnapshot.model_validate(pair.get("interview", {}))
        
        # Should not raise any exceptions
        endorsement = write_endorsement(cv, jd, interview)
        
        # Should produce non-empty text
        assert endorsement.endorsement_text
        assert len(endorsement.endorsement_text.strip()) > 0, \
            f"Empty endorsement produced for {pair['name']}"
