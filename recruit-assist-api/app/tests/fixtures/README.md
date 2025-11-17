# Golden Test Data

This directory contains golden test data for regression testing of the endorsement writer.

## File Structure

- `golden_cv_jd_pairs.json` - Collection of CV/JD pairs with expected outcomes

## Golden Test Data Format

Each entry in `golden_cv_jd_pairs.json` contains:

```json
{
  "name": "test_case_name",
  "description": "What this test case validates",
  "cv": { /* CandidateCVNormalized JSON */ },
  "jd": { /* JobDescriptionNormalized JSON */ },
  "interview": { /* InterviewSnapshot JSON */ },
  "expected_recommendation": "Proceed|Hold|Reject",
  "expected_min_checkmarks": 3,
  "expected_max_xmarks": 0,
  "expected_risks": ["List of expected risk factors"]
}
```

## Test Cases

### 1. `perfect_match_backend_engineer`
- **Purpose**: Strong candidate with all must-haves met
- **Expected**: Proceed recommendation with ≥3 checkmarks

### 2. `borderline_many_partial_matches`
- **Purpose**: Candidate with many partial matches (△) but few perfect matches (✔)
- **Expected**: Hold recommendation, ≥2 triangles

### 3. `weak_match_reject_candidate`
- **Purpose**: Candidate missing critical must-haves
- **Expected**: Reject recommendation, ≥2 X marks

### 4. `strong_but_long_notice`
- **Purpose**: Perfect candidate but long notice period vs urgent hiring
- **Expected**: Hold recommendation, risks should mention notice period

### 5. `salary_out_of_range`
- **Purpose**: Good candidate but salary expectations above budget
- **Expected**: Hold recommendation, risks should mention salary

### 6. `minimal_experience_below_threshold`
- **Purpose**: Good skills but years of experience below minimum
- **Expected**: Hold recommendation, risks should mention experience

## Usage

Tests load this data automatically:

```python
from app.tests.test_golden_endorsements import golden_pairs

def test_my_feature(golden_pairs):
    pair = next((p for p in golden_pairs if p["name"] == "perfect_match_backend_engineer"), None)
    # Use pair["cv"], pair["jd"], pair["interview"]
```

## Adding New Test Cases

1. Add a new entry to `golden_cv_jd_pairs.json`
2. Ensure CV/JD/interview data validates against their schemas
3. Add expected outcomes (recommendation, checkmarks, risks)
4. Add a corresponding test in `test_golden_endorsements.py` or `test_borderline_cases.py`

## Regression Testing

These golden pairs serve as regression tests:
- If endorsement format changes, update the expected values
- If recommendation logic changes, verify impacts on all golden pairs
- Use `pytest app/tests/test_golden_endorsements.py -v` to run all golden tests



