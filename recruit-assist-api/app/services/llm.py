from __future__ import annotations
from openai import OpenAI
from openai import APITimeoutError, APIError
from app.settings import settings
from app.exceptions import LLMError

def get_openai() -> OpenAI:
    """
    Get configured OpenAI client with timeout settings.
    
    Raises:
        RuntimeError: If OPENAI_API_KEY is not configured
    """
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    return OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout,
        max_retries=2
    )


def handle_llm_timeout_error(error: Exception, operation: str = "LLM operation") -> LLMError:
    """
    Convert timeout errors to LLMError with helpful messages.
    
    Args:
        error: The timeout or API error
        operation: Description of the operation that timed out
    
    Returns:
        LLMError with appropriate message
    """
    if isinstance(error, APITimeoutError):
        return LLMError(
            f"{operation} timed out after {settings.openai_timeout} seconds",
            detail="The LLM API call exceeded the timeout limit. Please try again with a simpler request or increase OPENAI_TIMEOUT."
        )
    elif isinstance(error, APIError):
        return LLMError(
            f"{operation} failed: {str(error)}",
            detail="The LLM API returned an error. Please check your API key and try again."
        )
    else:
        return LLMError(
            f"{operation} failed: {str(error)}",
            detail="An unexpected error occurred during LLM API call."
        )
