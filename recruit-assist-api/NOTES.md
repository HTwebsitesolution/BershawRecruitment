# Development Notes

## Current Implementation Status

### Stub Implementations

#### CV Parser (`app/services/cv_parser.py`)
- **Status**: Intentional stub with mock data generation
- **Function**: `parse_cv_bytes_to_normalized()`
- **Current**: Returns realistic mock candidate data based on filename
- **TODO**: Replace with real parser:
  - **PDF**: Use `pdfplumber`, `PyPDF2`, or `pdfminer.six`
  - **DOCX**: Use `python-docx`
  - **AI Extraction**: Use OpenAI/Anthropic for structured extraction
  - **Validation**: Add JSON Schema validation after parsing

#### Endorsement Writer (`app/services/endorsement_writer.py`)
- **Status**: Rule-based implementation
- **Function**: `write_endorsement()`
- **Current**: Uses rule-based matching with `_check()` function
- **TODO**: Swap in LLM call:
  - Load the endorsement prompt from `../prompts/endorsement_prompt.txt`
  - Call OpenAI/Anthropic API with structured data
  - Use the few-shot examples from the prompt template
  - Replace `write_endorsement()` text assembly with LLM-generated content

### Security & Production Readiness

#### CORS Configuration
- **Current**: `allow_origins=["*"]` (open to all)
- **Action Required**: Tighten CORS before production
  ```python
  allow_origins=[
      "https://yourdomain.com",
      "https://app.yourdomain.com"
  ]
  ```

#### Authentication
- **Current**: None
- **Action Required**: Add authentication before exposing outside localhost
  - JWT tokens for API access
  - API key authentication
  - OAuth2 for external clients
  - Rate limiting per API key/user

## Next Steps

### 1. Wire Chrome Extension to Backend

**Location**: `linkedin-outreach-assist/src/ui/DraftButton.tsx`

**Current**: Uses `generateHypotheticalNotes()` placeholder

**Action**: Update `refresh()` function to call backend:

```typescript
const refresh = async () => {
  try {
    // Extract candidate context from LinkedIn page
    const candidateContext = extractCandidateContext();
    
    const response = await fetch('http://localhost:8000/api/outreach/draft', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getAuthToken()}`
      },
      body: JSON.stringify({
        candidate_context: candidateContext,
        tone_profile_id: 'default'
      })
    });
    
    if (!response.ok) throw new Error('Failed to fetch drafts');
    
    const data = await response.json();
    setSuggestions(data.suggestions);
  } catch (error) {
    console.error('Error fetching drafts:', error);
    // Fallback to hypothetical notes
    setSuggestions(generateHypotheticalNotes({ firstName: "there" }));
  }
};
```

**Alternative**: Call `/endorsement/generate` after backend parses CV + JD:
- Upload CV via `/ingest/cv`
- Normalize JD via `/normalize/jd`
- Generate endorsement via `/endorsement/generate`
- Use endorsement text in outreach drafts

### 2. Replace CV Parser with Real Implementation

**File**: `app/services/cv_parser.py`

**Recommended Approach**:
1. **PDF Parsing**: Use `pdfplumber` or `pdfminer.six`
   ```python
   import pdfplumber
   from io import BytesIO
   
   with pdfplumber.open(BytesIO(data)) as pdf:
       text = "\n".join([page.extract_text() for page in pdf.pages])
   ```

2. **DOCX Parsing**: Use `python-docx`
   ```python
   from docx import Document
   from io import BytesIO
   
   doc = Document(BytesIO(data))
   text = "\n".join([para.text for para in doc.paragraphs])
   ```

3. **Structured Extraction**: Use LLM for extraction
   - Send extracted text to OpenAI/Anthropic
   - Use structured output with JSON Schema
   - Validate against `CandidateCVNormalized` schema

4. **Validation**: Always validate parsed output
   ```python
   from app.models import CandidateCVNormalized
   
   parsed_data = extract_from_text(text)
   validated = CandidateCVNormalized.model_validate(parsed_data)
   ```

### 3. Add Unit Tests for Endorsement Writer

**File**: `tests/test_endorsement_writer.py` (create this)

**Focus**: Test `_check()` function against golden CV/JD pairs

**Why**: Avoid silent regressions in requirement matching logic

**Example Test Structure**:
```python
import pytest
from app.services.endorsement_writer import _check
from app.models import CandidateCVNormalized, Skill, ExperienceItem

def test_check_nodejs_exact_match():
    """Test that Node.js requirement matches Node.js skill."""
    cv = CandidateCVNormalized(
        candidate=...,
        skills=[Skill(name="Node.js", category="tech", level="expert")],
        experience=[]
    )
    mark, evidence = _check("Node.js", cv)
    assert mark == "✔"
    assert "Node.js" in evidence

def test_check_partial_match():
    """Test that 'AWS ECS' matches 'AWS' skill."""
    cv = CandidateCVNormalized(
        candidate=...,
        skills=[Skill(name="AWS", category="tech", level="advanced")],
        experience=[]
    )
    mark, evidence = _check("AWS ECS/RDS", cv)
    assert mark == "△"  # Partial match via token overlap

def test_check_no_match():
    """Test that unrelated requirement returns ✖."""
    cv = CandidateCVNormalized(
        candidate=...,
        skills=[Skill(name="Python", category="tech", level="expert")],
        experience=[]
    )
    mark, evidence = _check("Kubernetes", cv)
    assert mark == "✖"
    assert evidence == ""
```

**Golden Test Data**:
- Create `tests/fixtures/golden_cv_jd_pairs.json`
- Include known CV/JD combinations with expected endorsement outputs
- Test against these pairs to catch regressions

### 4. Integration Testing

**End-to-End Flow**:
1. Upload CV via `/ingest/cv`
2. Normalize JD via `/normalize/jd`
3. Generate endorsement via `/endorsement/generate`
4. Verify output matches expected format

**Test with Real Data**:
- Use anonymized real CVs and JDs
- Verify schema validation works
- Check endorsement quality and format

### 5. Performance Optimization

**CV Parsing**:
- Cache parsed CVs by hash
- Support async parsing for large files
- Add timeout for LLM extraction

**Endorsement Generation**:
- Cache endorsements for same CV/JD pairs
- Support batch generation
- Add rate limiting per user

### 6. Error Handling

**Add comprehensive error handling**:
- File upload errors (size, format)
- Parsing failures (malformed PDF/DOCX)
- LLM API errors (rate limits, timeouts)
- Validation errors (schema mismatches)

**Return helpful error messages**:
```python
try:
    parsed = parse_cv_bytes_to_normalized(data)
except ParseError as e:
    raise HTTPException(
        status_code=422,
        detail=f"Failed to parse CV: {str(e)}. Please ensure the file is a valid PDF or DOCX."
    )
```

## Testing Checklist

- [ ] Unit tests for `_check()` function
- [ ] Unit tests for `_fmt_currency()` function
- [ ] Unit tests for `_one_line_background()` function
- [ ] Integration tests for `/ingest/cv` endpoint
- [ ] Integration tests for `/normalize/jd` endpoint
- [ ] Integration tests for `/endorsement/generate` endpoint
- [ ] Golden test data validation
- [ ] Error handling tests
- [ ] Schema validation tests
- [ ] Borderline case tests for endorsement recommendations
- [ ] Evidence mapping tests (must-haves → evidence)

## Accuracy Checks & Testing Best Practices

### Core Principles

#### 1. Assert Structure, Not Fantasy
- **Unknowns remain unknown**: If data is missing, tests should verify it's marked as "Unknown", not fabricated
- **No guessing**: Don't test for data that wasn't in the input
- **Preserve uncertainty**: If notice period is missing, it should stay missing, not be defaulted

**Example**:
```python
def test_unknown_fields_remain_unknown():
    """Test that missing data doesn't get invented."""
    cv = CandidateCVNormalized.model_validate({
        "candidate": {"full_name": "Alex Morgan"},  # No email, no notice
        "experience": [],
        "skills": [{"name": "Node.js"}]
    })
    assert cv.candidate.email is None
    assert cv.candidate.notice_period_weeks is None
    
    # Endorsement should show "Unknown" for missing data
    endorsement = write_endorsement(cv, jd, InterviewSnapshot())
    assert "Unknown" in endorsement.endorsement_text  # For notice/compensation
```

#### 2. Must-Haves Map to Evidence
- **Every must-have check requires evidence**: If a requirement is marked ✔, there must be evidence
- **Evidence must be traceable**: Evidence quotes should come from actual CV/interview data
- **No false positives**: Don't mark requirements as met without evidence

**Example**:
```python
def test_must_have_requires_evidence():
    """Test that ✔ marks require evidence from CV."""
    cv = CandidateCVNormalized.model_validate({
        "candidate": {"full_name": "Alex"},
        "experience": [{
            "title": "Engineer",
            "employer": "TechCo",
            "start_date": "2022-01",
            "technologies": ["Node.js", "TypeScript"]
        }],
        "skills": [{"name": "Node.js"}]
    })
    jd = JobDescriptionNormalized.model_validate({
        "job": {"title": "Engineer", "client": "Client", "location_policy": "hybrid"},
        "requirements": {
            "must_haves": [{"name": "Node.js & TypeScript"}],
            "nice_to_haves": []
        }
    })
    
    endorsement = write_endorsement(cv, jd, InterviewSnapshot())
    # If Node.js is marked ✔, there must be evidence
    assert "Node.js" in endorsement.endorsement_text
    # Evidence should reference actual CV data
    assert "Node.js" in endorsement.endorsement_text or "Node.js" in str(cv.skills)
```

#### 3. Golden CV/JD Pairs for Regression Prevention

**When you replace the parser with a real one**, add golden test data:

**File**: `app/tests/fixtures/golden_cv_jd_pairs.json`
```json
{
  "golden_pairs": [
    {
      "name": "backend_engineer_match",
      "cv_file": "fixtures/cv_alex_morgan.pdf",
      "jd_text": "Senior Backend Engineer with Node.js, AWS...",
      "expected_endorsement_checks": {
        "must_have_matches": ["Node.js & TypeScript", "AWS (Lambda/ECS/RDS)"],
        "must_have_misses": [],
        "recommendation": "Proceed"
      }
    }
  ]
}
```

**Test**:
```python
def test_golden_cv_jd_pair_regression():
    """Test against golden CV/JD pair to prevent regressions."""
    with open("app/tests/fixtures/golden_cv_jd_pairs.json") as f:
        golden_pairs = json.load(f)
    
    for pair in golden_pairs["golden_pairs"]:
        # Parse actual CV
        with open(pair["cv_file"], "rb") as cv_file:
            cv = parse_cv_bytes_to_normalized(cv_file.read())
        
        # Normalize JD
        jd = normalize_jd(text=pair["jd_text"])
        
        # Generate endorsement
        endorsement = write_endorsement(cv, jd, InterviewSnapshot())
        
        # Verify expectations
        expected = pair["expected_endorsement_checks"]
        for must_have in expected["must_have_matches"]:
            assert must_have in endorsement.endorsement_text
            assert "✔" in endorsement.endorsement_text or endorsement.endorsement_text.count(must_have) > 0
```

#### 4. Transparent Recommendation Rules

**Keep endorsement_writer's recommendation rule transparent** until you swap in your scoring model:

**Current rule** (in `endorsement_writer.py`):
```python
# Simple recommendation rule (you will replace with scoring later)
marks = [l.split(":")[1].strip().split(" ")[0] for l in lines]  # crude parse
proceed_score = marks.count("✔") - marks.count("✖")
recommendation = "Proceed" if proceed_score >= 2 else ("Hold" if proceed_score == 1 else "Reject")
```

**Add tests for borderline cases**:

```python
def test_recommendation_borderline_cases():
    """Test recommendation logic for edge cases."""
    
    # Case 1: Many △ vs few ✔
    # Should this be "Hold" or "Reject"?
    cv_many_partial = CandidateCVNormalized.model_validate({
        "candidate": {"full_name": "Test"},
        "experience": [],
        "skills": [{"name": "Python"}]  # Partial match for Node.js requirement
    })
    jd = JobDescriptionNormalized.model_validate({
        "job": {"title": "Engineer", "client": "Client", "location_policy": "hybrid"},
        "requirements": {
            "must_haves": [
                {"name": "Node.js"},  # Will be △
                {"name": "TypeScript"},  # Will be △
                {"name": "AWS"},  # Will be △
            ],
            "nice_to_haves": []
        }
    })
    
    endorsement = write_endorsement(cv_many_partial, jd, InterviewSnapshot())
    # Many △ should likely be "Hold" or "Reject", not "Proceed"
    assert endorsement.endorsement_text.count("△") >= 3
    # Recommendation should reflect this
    assert "Proceed" not in endorsement.endorsement_text or endorsement.endorsement_text.count("✔") >= 2
    
    # Case 2: Few ✔ but critical ones
    cv_few_strong = CandidateCVNormalized.model_validate({
        "candidate": {"full_name": "Test"},
        "experience": [{
            "title": "Engineer",
            "employer": "TechCo",
            "start_date": "2022-01",
            "technologies": ["Node.js", "TypeScript", "AWS"]
        }],
        "skills": [{"name": "Node.js"}, {"name": "TypeScript"}, {"name": "AWS"}]
    })
    jd_critical = JobDescriptionNormalized.model_validate({
        "job": {"title": "Engineer", "client": "Client", "location_policy": "hybrid"},
        "requirements": {
            "must_haves": [
                {"name": "Node.js & TypeScript", "weight": 0.5},  # High weight
                {"name": "AWS", "weight": 0.3},  # High weight
            ],
            "nice_to_haves": []
        }
    })
    
    endorsement2 = write_endorsement(cv_few_strong, jd_critical, InterviewSnapshot())
    # Few ✔ but critical should be "Proceed"
    assert endorsement2.endorsement_text.count("✔") >= 2
    assert "Proceed" in endorsement2.endorsement_text
```

#### 5. Test Structure Validation

**Test that outputs match the endorsement prompt format**:

```python
def test_endorsement_format_compliance():
    """Test that endorsement follows the prompt format exactly."""
    cv = _sample_cv()
    jd = _sample_jd()
    interview = InterviewSnapshot(notice_period_weeks=4)
    
    endorsement = write_endorsement(cv, jd, interview)
    text = endorsement.endorsement_text
    
    # Must have these sections
    assert text.startswith("Candidate:")
    assert "Background:" in text
    assert "Motivation:" in text
    assert "Compensation:" in text
    assert "Notice:" in text
    assert "Location:" in text
    assert "Fit vs JD:" in text
    assert "Risks/Unknowns:" in text
    assert "Recommendation:" in text
    
    # Must use correct symbols
    assert any(mark in text for mark in ["✔", "△", "✖"])
    
    # Evidence quotes should be present for ✔ marks
    if "✔" in text:
        assert 'evidence: "' in text or '"' in text
```

### Testing Workflow

1. **Before parser replacement**: Add golden CV/JD pairs
2. **After parser replacement**: Run golden pair tests to ensure no regressions
3. **Before LLM swap**: Document current recommendation rules
4. **After LLM swap**: Verify outputs still match format and evidence requirements
5. **Ongoing**: Add tests for each new edge case discovered

### Key Testing Rules

- ✅ **Unknowns stay unknown**: Never test for data that wasn't provided
- ✅ **Evidence required**: Every ✔ must have traceable evidence
- ✅ **Golden pairs**: Lock behavior with real CV/JD combinations
- ✅ **Transparent rules**: Document recommendation logic clearly
- ✅ **Edge cases**: Test borderline scenarios (many △, few ✔, critical requirements)
- ✅ **Format compliance**: Verify output matches endorsement prompt format

## Deployment Checklist

- [ ] Tighten CORS configuration
- [ ] Add authentication (JWT/API keys)
- [ ] Add rate limiting
- [ ] Add logging (structured logs)
- [ ] Add monitoring (health checks, metrics)
- [ ] Add database for storing parsed CVs/JDs
- [ ] Add caching layer (Redis)
- [ ] Set up CI/CD pipeline
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Security audit (dependencies, vulnerabilities)

