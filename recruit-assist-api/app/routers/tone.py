from __future__ import annotations
from fastapi import APIRouter
from app.models import ToneProfile

router = APIRouter(prefix="/tone", tags=["tone"])
_TONE = ToneProfile()  # replace with persistent storage later

@router.get("/profile", response_model=ToneProfile)
async def get_tone() -> ToneProfile:
    return _TONE

@router.post("/profile", response_model=ToneProfile)
async def set_tone(profile: ToneProfile) -> ToneProfile:
    global _TONE
    _TONE = profile
    return _TONE
