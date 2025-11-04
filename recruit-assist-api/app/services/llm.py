from __future__ import annotations
from openai import OpenAI
from app.settings import settings

def get_openai() -> OpenAI:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    return OpenAI(api_key=settings.openai_api_key)
