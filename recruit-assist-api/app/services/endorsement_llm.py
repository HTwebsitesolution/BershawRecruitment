from __future__ import annotations
from pathlib import Path
from app.services.llm import get_openai
from app.settings import settings
from app.models import CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot, EndorsementOut

# Get the path to the prompts directory (at root level, one level up from recruit-assist-api)
_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "endorsement_prompt.txt"

ENDORSEMENT_SYSTEM = """You are a recruitment assistant that produces concise, audit-friendly candidate endorsements for clients. Be accurate over confident. Do not invent salary, notice, or locations—if not provided, write "Unknown". Always ground each Fit bullet in evidence snippets from CV or interview transcript. Keep to ~160–220 words, use UK spelling, and the structure specified by the user."""


def _load_prompt_template() -> str:
    """Load the endorsement prompt template from prompts/endorsement_prompt.txt"""
    try:
        with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback prompt if file not found (shouldn't happen in production)
        return """Follow this exact OUTPUT FORMAT (plain text):
Candidate: {Full Name} — {City, Country or 'Unknown'}
Background: {2–4 lines from CV+interview with tangible impact}
Motivation: {one paragraph from interview, else 'Unknown'}
Compensation: {Current → Target}
Notice: {N weeks or 'Unknown'}
Location: {policy/prefs; relocation?}
Fit vs JD:
- {Must-have #1}: {✔/△/✖} — {1-line reason} (evidence: "snippet")
- {Must-have #2}: ...
- {Nice-to-have #1}: ...
Risks/Unknowns: {comma-separated or 'None material'}
Recommendation: {Proceed / Hold / Reject} — {1 reason}"""


def generate_endorsement_llm(
    cv: CandidateCVNormalized,
    jd: JobDescriptionNormalized,
    interview: InterviewSnapshot
) -> EndorsementOut:
    """Generate endorsement using LLM with few-shot prompt template."""
    client = get_openai()

    # Load the full prompt template (includes few-shot examples)
    prompt_template = _load_prompt_template()

    # Convert models to JSON for LLM input
    cv_json = cv.model_dump_json(indent=2, exclude_none=True)
    jd_json = jd.model_dump_json(indent=2, exclude_none=True)
    interview_json = interview.model_dump_json(indent=2, exclude_none=True)

    # Construct the full user prompt with the template and input data
    user_prompt = f"""{prompt_template}

INPUT DATA:

CandidateCVNormalized JSON:
```json
{cv_json}
```

JobDescriptionNormalized JSON:
```json
{jd_json}
```

Interview JSON:
```json
{interview_json}
```

Generate the endorsement following the format and rules above:"""

    # Call OpenAI API using chat completions
    resp = client.chat.completions.create(
        model=settings.openai_model_long,
        messages=[
            {"role": "system", "content": ENDORSEMENT_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,  # Lower temperature for more consistent, factual output
        max_tokens=800,  # Sufficient for ~160-220 word endorsement
    )
    
    # Extract the text from the response
    text = resp.choices[0].message.content.strip()
    return EndorsementOut(endorsement_text=text)
