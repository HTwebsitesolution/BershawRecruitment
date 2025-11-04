from __future__ import annotations
from typing import Literal
from app.models import ToneProfile
from app.services.llm import get_openai
from app.settings import settings


def connection_note(tp: ToneProfile, *, first_name: str, role_title: str, location: str, work_mode: str) -> str:
    """Generate an initial connection note using the tone profile template."""
    return tp.templates["initial_connect"].format(
        first_name=first_name, company=tp.company, role_title=role_title, location=location, work_mode=work_mode
    )


def followup_after_accept(tp: ToneProfile, *, first_name: str) -> str:
    """Generate a follow-up message after connection acceptance using the tone profile template."""
    return tp.templates["after_accept_send_jd"].format(first_name=first_name)


def polite_ack(tp: ToneProfile, *, first_name: str) -> str:
    """Generate a polite acknowledgment message using the tone profile template."""
    return tp.templates["polite_ack"].format(first_name=first_name)


def connection_note_llm(
    tp: ToneProfile,
    *,
    first_name: str,
    role_title: str,
    location: str,
    work_mode: str,
    message_type: Literal["initial_connect", "after_accept_send_jd"] = "initial_connect"
) -> str:
    """
    Generate a personalized connection note using LLM while enforcing tone profile style markers.
    Falls back to template-based generation if LLM is not configured.
    """
    # Try to get OpenAI client, fallback to template-based if not configured
    try:
        openai_client = get_openai()
    except RuntimeError:
        # API key not configured, use template-based fallback
        if message_type == "initial_connect":
            return connection_note(tp, first_name=first_name, role_title=role_title, location=location, work_mode=work_mode)
        elif message_type == "after_accept_send_jd":
            return followup_after_accept(tp, first_name=first_name)
        else:
            raise ValueError(f"Unknown message_type: {message_type}")

    try:
        # Construct style markers string
        style_markers_str = "; ".join(tp.style_markers)
        
        # Build the prompt
        system_prompt = (
            "Write ultra-concise LinkedIn messages in Jean's voice for Bershaw.\n"
            f"Follow style markers: {style_markers_str}.\n"
            "Never invent details; use variables provided."
        )
        
        user_prompt = f"""ToneProfile:
- persona_name: {tp.persona_name}
- company: {tp.company}
- style_markers: {style_markers_str}

MessageType: {message_type}

Variables:
- first_name: {first_name}
- role_title: {role_title}
- location: {location}
- work_mode: {work_mode}

Write the message in plain text (no greeting duplication, no hashtags)."""

        # Call OpenAI API using short model for fast/cheap drafting
        response = openai_client.chat.completions.create(
            model=settings.openai_model_short,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,  # Slightly higher for natural language, but still controlled
            max_tokens=300,  # Enough for a concise LinkedIn message
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # If LLM call fails, fallback to template-based
        print(f"Warning: LLM outreach generation failed: {e}. Falling back to template-based.")
        if message_type == "initial_connect":
            return connection_note(tp, first_name=first_name, role_title=role_title, location=location, work_mode=work_mode)
        elif message_type == "after_accept_send_jd":
            return followup_after_accept(tp, first_name=first_name)
        else:
            raise ValueError(f"Unknown message_type: {message_type}")
