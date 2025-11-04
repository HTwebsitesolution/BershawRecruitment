from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.models import ToneProfile
from app.routers.tone import _TONE
from app.services.outreach_writer import connection_note, followup_after_accept
from app.services.outreach_llm import draft_connect_llm
from app.services.reply_router import classify, next_message

router = APIRouter(prefix="/outreach", tags=["outreach"])

class ConnectIn(BaseModel):
    first_name: str
    role_title: str
    location: str
    work_mode: str = "hybrid"

@router.post("/draft/connect")
async def draft_connect(payload: ConnectIn, mode: str = Query("template", enum=["template", "llm"])):
    tp: ToneProfile = _TONE
    if mode == "llm":
        return {"text": draft_connect_llm(tp, **payload.model_dump())}
    return {"text": connection_note(tp, **payload.model_dump())}


class FollowUpIn(BaseModel):
    first_name: str


@router.post("/draft/after-accept")
async def draft_after_accept(payload: FollowUpIn) -> dict:
    """Generate a follow-up message after connection acceptance."""
    tp: ToneProfile = _TONE
    return {"text": followup_after_accept(tp, **payload.model_dump())}


class RouteReplyIn(BaseModel):
    first_name: str
    message_text: str
    jd_link_available: bool = True


@router.post("/route-reply")
async def route_reply(payload: RouteReplyIn) -> dict:
    """Classify a reply message and generate the appropriate response."""
    intent = classify(payload.message_text)
    return {
        "intent": intent,
        "reply": next_message(intent, payload.first_name, jd_link_available=payload.jd_link_available, tone=_TONE)
    }
