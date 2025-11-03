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

