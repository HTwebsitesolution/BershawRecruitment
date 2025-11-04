from __future__ import annotations
from app.services.llm import get_openai
from app.settings import settings
from app.models import ToneProfile

SYSTEM = """Write ultra-concise LinkedIn messages in Jean's voice for Bershaw.
Style markers: Warm, succinct, professional; 1-sentence client value prop; direct ask for CV; UK spelling; no emojis.
Do not invent details not provided. Output plain text only."""

def draft_connect_llm(tp: ToneProfile, *, first_name: str, role_title: str, location: str, work_mode: str) -> str:
    """Generate a personalized initial connection note using LLM while maintaining tone profile style."""
    client = get_openai()
    user = (
        f"Compose an initial connection note.\n"
        f"first_name={first_name}\n"
        f"company={tp.company}\n"
        f"role_title={role_title}\n"
        f"location={location}\n"
        f"work_mode={work_mode}\n"
        f'Must include the phrase "Are you currently exploring?" and a clear request for the CV.'
    )
    r = client.chat.completions.create(
        model=settings.openai_model_short,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}
        ],
        temperature=0.7,  # Slightly higher for natural language, but still controlled
        max_tokens=300,  # Enough for a concise LinkedIn message
    )
    return r.choices[0].message.content.strip()
