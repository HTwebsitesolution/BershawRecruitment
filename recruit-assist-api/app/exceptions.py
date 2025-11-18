from __future__ import annotations
from typing import Optional, Any
from fastapi import HTTPException, status


class RecruitAssistException(Exception):
    """Base exception for Recruit Assist API."""
    def __init__(self, message: str, detail: Optional[str] = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class ParseError(RecruitAssistException):
    """Raised when CV or JD parsing fails."""
    pass


class ValidationError(RecruitAssistException):
    """Raised when data validation fails."""
    pass


class LLMError(RecruitAssistException):
    """Raised when LLM API calls fail."""
    pass


class FileError(RecruitAssistException):
    """Raised when file operations fail."""
    pass


def raise_http_exception(
    status_code: int,
    message: str,
    detail: Optional[str] = None,
    error_type: Optional[str] = None
) -> HTTPException:
    """
    Create a standardized HTTPException with consistent error format.
    """
    error_body: dict[str, Any] = {
        "error": {
            "message": message,
            "type": error_type or "generic_error"
        }
    }
    
    if detail:
        error_body["error"]["detail"] = detail
    
    return HTTPException(status_code=status_code, detail=error_body)


def handle_parse_error(error: ParseError) -> HTTPException:
    """Convert ParseError to HTTPException."""
    return raise_http_exception(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Failed to parse document",
        detail=error.message,
        error_type="parse_error"
    )


def handle_validation_error(error: ValidationError) -> HTTPException:
    """Convert ValidationError to HTTPException."""
    return raise_http_exception(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation failed",
        detail=error.message,
        error_type="validation_error"
    )


def handle_llm_error(error: LLMError) -> HTTPException:
    """Convert LLMError to HTTPException."""
    return raise_http_exception(
        status_code=status.HTTP_502_BAD_GATEWAY,
        message="LLM service error",
        detail=error.message,
        error_type="llm_error"
    )


def handle_file_error(error: FileError) -> HTTPException:
    """Convert FileError to HTTPException."""
    return raise_http_exception(
        status_code=status.HTTP_400_BAD_REQUEST,
        message="File operation failed",
        detail=error.message,
        error_type="file_error"
    )

