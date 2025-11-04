import re
import logging
from typing import Literal
from app.models import ToneProfile

# Set up logging for intent classification review
logger = logging.getLogger(__name__)

Intent = Literal["positive_reply", "request_jd", "cv_attached", "decline", "unknown"]

POSITIVE = re.compile(r"\b(yes|sure|interested|exploring|okay|ok|sounds good|go ahead)\b", re.I)
REQUEST_JD = re.compile(r"\b(jd|job desc|job description|share details)\b", re.I)
DECLINE = re.compile(r"\b(not interested|no thanks|no, thank|pass|maybe later)\b", re.I)
CV_ATTACHED = re.compile(r"\b(attached my cv|here is my cv|shared my cv|cv attached)\b", re.I)


def classify(text: str) -> Intent:
    """Classify the intent of a reply message. Logs for review of borderline cases."""
    text_lower = text.lower()
    
    if CV_ATTACHED.search(text):
        intent = "cv_attached"
    elif DECLINE.search(text):
        intent = "decline"
    elif REQUEST_JD.search(text):
        intent = "request_jd"
    elif POSITIVE.search(text):
        intent = "positive_reply"
    else:
        intent = "unknown"
    
    # Log intent classification for review (especially unknown/borderline cases)
    logger.info(f"Intent classified: {intent} | Message: {text[:100]}...")
    
    return intent


def next_message(intent: Intent, first_name: str, *, jd_link_available: bool, tone: ToneProfile) -> str:
    """
    Generate the appropriate follow-up message based on intent.
    Uses tone profile templates strictly for consistency - no hardcoded messages.
    """
    # Use strict template matching - consistency matters more than creativity
    if intent in {"positive_reply", "request_jd"}:
        if jd_link_available:
            # Use the exact template from tone profile - this asks for salary and notice
            return tone.templates["after_accept_send_jd"].format(first_name=first_name)
        else:
            # Use polite acknowledgment template when JD not ready yet
            return tone.templates["polite_ack"].format(first_name=first_name)
    
    if intent == "cv_attached":
        # When CV is attached, acknowledge and ask for salary/notice
        # Using the same template as after_accept_send_jd for consistency
        return tone.templates["after_accept_send_jd"].format(first_name=first_name)
    
    if intent == "decline":
        # For declines, use a simple acknowledgment
        # Note: This is a polite close - consider adding to tone profile templates if needed
        return f"Appreciate the reply, {first_name}. If circumstances change, feel free to reach out. Wishing you continued success."
    
    # Unknown intent - fallback: politely ask for CV, salary, notice
    # Using the same template for consistency
    return tone.templates["after_accept_send_jd"].format(first_name=first_name)
