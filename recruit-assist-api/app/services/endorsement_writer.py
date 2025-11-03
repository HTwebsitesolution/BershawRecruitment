from __future__ import annotations
from typing import List, Tuple, Optional
from app.models import CandidateCVNormalized, JobDescriptionNormalized, InterviewSnapshot, EndorsementOut

def _check(requirement: str, cv: CandidateCVNormalized) -> Tuple[str, str]:
    """Return tuple (mark, evidence) where mark in {'✔','△','✖'} and short evidence."""
    req_lower = requirement.lower()
    evidence = ""

    # Naive signal: skills + technologies strings
    skill_hits = [s.name for s in cv.skills if s.name and s.name.lower() in req_lower]
    tech_hits = []
    for exp in cv.experience:
        for t in (exp.technologies or []):
            if t.lower() in req_lower:
                tech_hits.append(t)

    if skill_hits or tech_hits:
        evidence = f"{', '.join(skill_hits + tech_hits)}"
        return "✔", evidence

    # partial: if any token overlaps
    tokens = [w for w in req_lower.replace("(", " ").replace(")", " ").replace("/", " ").split() if len(w) > 2]
    skill_token_hits = [s.name for s in cv.skills if any(tok in s.name.lower() for tok in tokens)]
    if skill_token_hits:
        evidence = f"{', '.join(skill_token_hits)}"
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

def write_endorsement(
    cv: CandidateCVNormalized,
    jd: JobDescriptionNormalized,
    interview: InterviewSnapshot
) -> EndorsementOut:
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
    for req in jd.requirements.must_haves[:4]:
        mark, ev = _check(req.name, cv)
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

    # Simple recommendation rule (you will replace with scoring later)
    marks = [l.split(":")[1].strip().split(" ")[0] for l in lines]  # crude parse
    proceed_score = marks.count("✔") - marks.count("✖")
    recommendation = "Proceed" if proceed_score >= 2 else ("Hold" if proceed_score == 1 else "Reject")

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
