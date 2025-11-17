from __future__ import annotations
from typing import List, Tuple, Optional
from pathlib import Path
from app.models import CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot, EndorsementOut
from app.services.llm import get_openai
from app.settings import settings

# Get the path to the prompts directory (at root level, one level up from recruit-assist-api)
_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "endorsement_prompt.txt"


def _load_prompt_template() -> str:
    """Load the endorsement prompt template from prompts/endorsement_prompt.txt"""
    try:
        with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback prompt if file not found (shouldn't happen in production)
        return "Generate a concise candidate endorsement based on the CV, JD, and interview data provided."


def _check(requirement: str, cv: CandidateCVNormalized) -> Tuple[str, str]:
    """Return tuple (mark, evidence) where mark in {'✔','△','✖'} and short evidence."""
    req_lower = requirement.lower()
    evidence = ""

    # Naive signal: skills + technologies strings (bidirectional matching)
    skill_hits = [s.name for s in cv.skills if s.name and (s.name.lower() in req_lower or req_lower in s.name.lower())]
    tech_hits = []
    for exp in cv.experience:
        for t in (exp.technologies or []):
            if t.lower() in req_lower or req_lower in t.lower():
                tech_hits.append(t)

    if skill_hits or tech_hits:
        evidence = f"{', '.join(skill_hits + tech_hits)}"
        return "✔", evidence

    # partial: if any token overlaps (bidirectional)
    tokens = [w for w in req_lower.replace("(", " ").replace(")", " ").replace("/", " ").replace("&", " ").split() if len(w) > 2]
    skill_token_hits = [s.name for s in cv.skills if any(tok in s.name.lower() or s.name.lower() in tok for tok in tokens)]
    tech_token_hits = []
    for exp in cv.experience:
        for t in (exp.technologies or []):
            if any(tok in t.lower() or t.lower() in tok for tok in tokens):
                tech_token_hits.append(t)
    
    if skill_token_hits or tech_token_hits:
        evidence = f"{', '.join(skill_token_hits + tech_token_hits)}"
        return "△", evidence

    return "✖", ""


def _one_line_background(cv: CandidateCVNormalized) -> str:
    years = ""  # In this stub we don't compute years; keep concise
    exp = cv.experience[0] if cv.experience else None
    techs = ", ".join((exp.technologies or [])[:4]) if exp else ""
    impact = ""
    if exp and exp.achievements:
        impact = f"; {exp.achievements[0]}"
    return f"{exp.title if exp else 'Professional'}; {techs}{impact}".strip("; ")


def _fmt_currency(val: Optional[float], cur: Optional[str]) -> str:
    if val is None or not cur:
        return "Unknown"
    symbol = "£" if cur.upper() == "GBP" else cur.upper() + " "
    return f"{symbol}{int(val):,}"


def _write_endorsement_rule_based(
    cv: CandidateCVNormalized,
    jd: JobDescriptionNormalized,
    interview: InterviewSnapshot
) -> EndorsementOut:
    """Fallback rule-based endorsement writer (original implementation)"""
    name = cv.candidate.full_name
    loc = cv.candidate.location.city + ", " + cv.candidate.location.country if cv.candidate.location and cv.candidate.location.city and cv.candidate.location.country else "Unknown"
    background = _one_line_background(cv)

    motivation = interview.motivation or "Unknown"
    current_comp = _fmt_currency(cv.candidate.current_compensation.base_amount if cv.candidate.current_compensation else None,
                                 cv.candidate.current_compensation.currency if cv.candidate.current_compensation else None)
    target = interview.target_comp or cv.candidate.target_compensation
    target_txt = (
        f"{_fmt_currency(target.base_min, target.currency)}–{_fmt_currency(target.base_max, target.currency)}"
        if target and target.base_min and target.base_max else "Unknown"
    )
    notice = str(interview.notice_period_weeks) + " weeks" if interview.notice_period_weeks is not None else (str(cv.candidate.notice_period_weeks) + " weeks" if cv.candidate.notice_period_weeks is not None else "Unknown")
    loc_pref = interview.location_prefs or (cv.candidate.location.remote_preference if cv.candidate.location and cv.candidate.location.remote_preference else "Unknown")

    # Fit checks
    lines: List[str] = []
    must_have_marks: List[str] = []
    for req in jd.requirements.must_haves[:4]:
        mark, ev = _check(req.name, cv)
        must_have_marks.append(mark)
        ev_txt = f' (evidence: "{ev}")' if ev else ""
        lines.append(f"- {req.name}: {mark} — {('meets' if mark=='✔' else 'partial' if mark=='△' else 'missing')}{ev_txt}")
    for req in jd.requirements.nice_to_haves[:2]:
        mark, ev = _check(req.name, cv)
        ev_txt = f' (evidence: "{ev}")' if ev else ""
        lines.append(f"- {req.name}: {mark} — {('meets' if mark=='✔' else 'partial' if mark=='△' else 'missing')}{ev_txt}")

    risks = interview.risks or []
    if target_txt == "Unknown":
        risks.append("Target compensation unknown")
    if notice == "Unknown":
        risks.append("Notice period unknown")
    risks_txt = ", ".join(risks) if risks else "None material"

    # Simple recommendation rule: Proceed if all must-haves are met (✔ or △), otherwise use scoring
    # Count only must-have marks for recommendation (nice-to-haves are optional)
    # Treat △ (partial matches) as acceptable for must-haves
    all_must_haves_acceptable = len(must_have_marks) > 0 and all(m in ("✔", "△") for m in must_have_marks)
    if all_must_haves_acceptable:
        recommendation = "Proceed"
    else:
        # Use scoring for partial matches - only count must-haves for scoring
        # Count ✔ as +1, △ as +0.5, ✖ as -1
        must_have_score = must_have_marks.count("✔") + (must_have_marks.count("△") * 0.5) - must_have_marks.count("✖")
        # If most must-haves are met, proceed; if some are met, hold; if few/none, reject
        if must_have_score >= len(must_have_marks) * 0.6:  # 60% of must-haves met (allowing △ as partial)
            recommendation = "Proceed"
        elif must_have_score >= 0.5:
            recommendation = "Hold"
        else:
            recommendation = "Reject"

    out = (
        f"Candidate: {name} — {loc}\n"
        f"Background: {background}\n"
        f"Motivation: {motivation}\n"
        f"Compensation: {current_comp} → {target_txt}\n"
        f"Notice: {notice}\n"
        f"Location: {loc_pref}\n"
        f"Fit vs JD:\n" + "\n".join(lines) + "\n"
        f"Risks/Unknowns: {risks_txt}\n"
        f"Recommendation: {recommendation} — based on evidence above"
    )
    return EndorsementOut(endorsement_text=out)


def write_endorsement(
    cv: CandidateCVNormalized,
    jd: JobDescriptionNormalized,
    interview: InterviewSnapshot
) -> EndorsementOut:
    """
    Generate endorsement using LLM if configured, otherwise fallback to rule-based.
    """
    # Try to get OpenAI client, fallback to rule-based if not configured
    try:
        openai_client = get_openai()
    except RuntimeError:
        # API key not configured, use rule-based fallback
        return _write_endorsement_rule_based(cv, jd, interview)

    try:
        # Load prompt template
        prompt_template = _load_prompt_template()
        
        # Convert models to JSON for LLM input
        cv_json = cv.model_dump_json(indent=2, exclude_none=True)
        jd_json = jd.model_dump_json(indent=2, exclude_none=True)
        interview_json = interview.model_dump_json(indent=2, exclude_none=True)
        
        # Construct the full prompt with inputs
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

        # Call OpenAI API using long model for higher quality endorsements
        response = openai_client.chat.completions.create(
            model=settings.openai_model_long,
            messages=[
                {"role": "system", "content": "You are a recruitment assistant that produces concise, audit-friendly candidate endorsements."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent, factual output
            max_tokens=800,  # Sufficient for ~200 word endorsement
        )
        
        endorsement_text = response.choices[0].message.content.strip()
        return EndorsementOut(endorsement_text=endorsement_text)
        
    except Exception as e:
        # If LLM call fails, fallback to rule-based
        # In production, you might want to log this error
        print(f"Warning: LLM endorsement generation failed: {e}. Falling back to rule-based.")
        return _write_endorsement_rule_based(cv, jd, interview)
