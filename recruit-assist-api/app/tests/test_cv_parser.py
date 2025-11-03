from app.services.cv_parser import parse_cv_bytes_to_normalized

def test_parse_cv_bytes_to_normalized_returns_minimal_structure():
    data = b"%PDF-1.4 fake content"
    out = parse_cv_bytes_to_normalized(data, filename="jane_doe.pdf")
    assert out.candidate.full_name.lower().startswith("jane")
    assert out.experience, "Should include at least one experience item"
    assert any(s.name.lower() == "node.js" for s in out.skills)


