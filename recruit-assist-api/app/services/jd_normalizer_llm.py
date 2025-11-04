from __future__ import annotations
import json
from typing import Optional
from app.services.llm import get_openai
from app.settings import settings
from app.models import JobDescriptionNormalized
from app.services.jd_normalizer import normalize_jd

JD_NORMALIZER_SYSTEM = """You are a recruitment assistant that extracts structured job description data from free-form text.
Extract the following information accurately:
- Job title (required)
- Client/company name (required)
- Department (if mentioned)
- Location policy: "onsite", "hybrid", or "remote" (infer from text if not explicit)
- Primary location (city, region, country)
- Salary band (min, max, currency, period: "year" or "month")
- Visa sponsorship availability: "available", "not_available", or "case_by_case"
- Clearance requirements (if mentioned)
- Hiring urgency: "asap", "this_quarter", or "next_quarter"
- Must-have requirements (list of skills/qualifications with weights 0.1-1.0)
- Nice-to-have requirements (list of skills/qualifications)
- Minimum years of experience (if specified)
- Education requirements (if specified)
- Interview process stages (if described)
- Role notes (any additional context)

Be accurate and conservative. If information is not provided in the text, use null for optional fields.
For location_policy, infer from phrases like "remote", "work from home", "hybrid", "2-3 days in office", etc.
For salary, extract numeric values and currency. If only one figure is given, use it as both min and max.
For requirements, identify key skills, technologies, and qualifications. Assign weights based on emphasis in the text.
Output valid JSON matching the JobDescriptionNormalized schema."""


def normalize_jd_llm(
    text: Optional[str] = None,
    *,
    title: Optional[str] = None,
    client: Optional[str] = None,
    location_policy: Optional[str] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    currency: Optional[str] = "GBP",
) -> JobDescriptionNormalized:
    """
    Normalize job description using LLM extraction from free-text JD.
    
    If structured hints (title, client, etc.) are provided, they take precedence.
    The LLM extracts missing information from the text field.
    
    Falls back to rule-based normalization if OpenAI API key is not configured.
    """
    # Try to get OpenAI client, fallback to rule-based if not configured
    try:
        client_openai = get_openai()
    except RuntimeError:
        # API key not configured, use rule-based fallback
        return normalize_jd(
            text=text,
            title=title,
            client=client,
            location_policy=location_policy,
            city=city,
            country=country,
            salary_min=salary_min,
            salary_max=salary_max,
            currency=currency
        )

    # Build the user prompt
    user_prompt_parts = []
    
    if text:
        user_prompt_parts.append(f"Free-text job description:\n{text}\n")
    
    # Include any structured hints as overrides
    hints = []
    if title:
        hints.append(f"Title (override): {title}")
    if client:
        hints.append(f"Client/Company (override): {client}")
    if location_policy:
        hints.append(f"Location Policy (override): {location_policy}")
    if city:
        hints.append(f"City (override): {city}")
    if country:
        hints.append(f"Country (override): {country}")
    if salary_min is not None or salary_max is not None:
        salary_str = f"Salary: {salary_min or 'N/A'} - {salary_max or 'N/A'} {currency}"
        hints.append(salary_str)
    
    if hints:
        user_prompt_parts.append("\nStructured hints (use these values if provided):\n" + "\n".join(hints))
    
    user_prompt_parts.append(
        "\nExtract and return a valid JSON object matching this structure:\n"
        '{\n'
        '  "job": {\n'
        '    "title": "string (required)",\n'
        '    "client": "string (required)",\n'
        '    "department": "string or null",\n'
        '    "location_policy": "onsite" | "hybrid" | "remote",\n'
        '    "onsite_days_per_week": number (0-5) or null,\n'
        '    "primary_location": {"city": "string or null", "region": "string or null", "country": "string or null"} or null,\n'
        '    "salary_band": {"min": number or null, "max": number or null, "currency": "string (3 chars)", "period": "year" | "month"} or null,\n'
        '    "visa_sponsorship": "available" | "not_available" | "case_by_case" or null,\n'
        '    "clearance_required": "string or null",\n'
        '    "hiring_urgency": "asap" | "this_quarter" | "next_quarter" or null\n'
        '  },\n'
        '  "requirements": {\n'
        '    "must_haves": [{"name": "string", "weight": number (0.1-1.0), "evidence_hint": "string or null"}],\n'
        '    "nice_to_haves": [{"name": "string", "weight": number (0.1-1.0), "evidence_hint": "string or null"}],\n'
        '    "years_experience_min": number or null,\n'
        '    "education_required": "string or null"\n'
        '  },\n'
        '  "interview_process": [{"stage_name": "string", "duration_minutes": number or null, "participants": ["string"] or null, "assessment_focus": "string or null"}] or null,\n'
        '  "role_notes": "string or null"\n'
        '}\n'
        "\nReturn only valid JSON, no markdown formatting or explanation."
    )
    
    user_prompt = "\n".join(user_prompt_parts)

    try:
        # Use JSON mode for structured output (available in GPT-4o and newer models)
        resp = client_openai.chat.completions.create(
            model=settings.openai_model_long,  # Use long model for better extraction quality
            messages=[
                {"role": "system", "content": JD_NORMALIZER_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},  # Force JSON output
            temperature=0.1,  # Low temperature for consistent, factual extraction
            max_tokens=2000,  # Enough for structured JD data
        )
        
        # Extract JSON from response
        content = resp.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Parse JSON
        jd_data = json.loads(content)
        
        # Validate and create Pydantic model
        return JobDescriptionNormalized.model_validate(jd_data)
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, fallback to rule-based normalization
        print(f"Warning: LLM returned invalid JSON: {e}. Falling back to rule-based normalization.")
        return normalize_jd(
            text=text,
            title=title,
            client=client,
            location_policy=location_policy,
            city=city,
            country=country,
            salary_min=salary_min,
            salary_max=salary_max,
            currency=currency
        )
    except Exception as e:
        # If LLM call fails, fallback to rule-based normalization
        print(f"Warning: JD normalization LLM call failed: {e}. Falling back to rule-based normalization.")
        return normalize_jd(
            text=text,
            title=title,
            client=client,
            location_policy=location_policy,
            city=city,
            country=country,
            salary_min=salary_min,
            salary_max=salary_max,
            currency=currency
        )
