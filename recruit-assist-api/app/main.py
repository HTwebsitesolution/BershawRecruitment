from __future__ import annotations
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from app.routers import ingest, normalize, endorsement, tone, outreach, compliance, email, candidates, jobs, matching, profiles, interview_scheduling, linkedin_automation
from app.exceptions import (
    RecruitAssistException, ParseError, ValidationError, LLMError, FileError,
    handle_parse_error, handle_validation_error, handle_llm_error, handle_file_error
)

# Configure logging for intent classification review
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Recruit Assist API",
        version="0.1.0",
        description="Skeleton API for CV ingest, JD normalization, and endorsement generation."
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(RecruitAssistException)
    async def recruit_assist_exception_handler(request: Request, exc: RecruitAssistException):
        """Handle custom RecruitAssist exceptions."""
        logger.error(f"RecruitAssist exception: {exc.message}", exc_info=exc)
        
        if isinstance(exc, ParseError):
            http_exc = handle_parse_error(exc)
        elif isinstance(exc, ValidationError):
            http_exc = handle_validation_error(exc)
        elif isinstance(exc, LLMError):
            http_exc = handle_llm_error(exc)
        elif isinstance(exc, FileError):
            http_exc = handle_file_error(exc)
        else:
            from app.exceptions import raise_http_exception
            http_exc = raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Internal server error",
                detail=exc.message,
                error_type="internal_error"
            )
        
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle FastAPI request validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "message": "Request validation failed",
                    "type": "validation_error",
                    "detail": exc.errors(),
                }
            }
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: PydanticValidationError):
        """Handle Pydantic model validation errors."""
        logger.warning(f"Pydantic validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "message": "Data validation failed",
                    "type": "validation_error",
                    "detail": exc.errors(),
                }
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "message": "Internal server error",
                    "type": "internal_error",
                    "detail": "An unexpected error occurred. Please try again later.",
                }
            }
        )

    app.include_router(ingest.router)
    app.include_router(normalize.router)
    app.include_router(endorsement.router)
    app.include_router(tone.router)
    app.include_router(outreach.router)
    app.include_router(compliance.router)
    app.include_router(email.router)
    app.include_router(candidates.router)
    app.include_router(jobs.router)
    app.include_router(matching.router)
    app.include_router(profiles.router)
    app.include_router(interview_scheduling.router)
    app.include_router(linkedin_automation.router)

    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Recruit Assist API",
            "version": "0.1.0",
            "description": "AI-powered recruiting platform API for CV parsing, JD normalization, and endorsement generation.",
            "docs": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json"
            },
            "endpoints": {
                "health": "/healthz",
                "ingest": {
                    "cv_upload": "POST /ingest/cv?use_llm=true"
                },
                "normalize": {
                    "jd": "POST /normalize/jd?use_llm=true"
                },
                "endorsement": {
                    "generate": "POST /endorsement/generate?use_llm=true"
                },
                "outreach": {
                    "draft_connect": "POST /outreach/draft/connect?mode=llm",
                    "draft_after_accept": "POST /outreach/draft/after-accept",
                    "route_reply": "POST /outreach/route-reply"
                },
                "tone": {
                    "get": "GET /tone",
                    "update": "POST /tone"
                },
                "compliance": {
                    "consent": "POST /compliance/consent",
                    "check_consent": "GET /compliance/consent/check",
                    "export": "POST /compliance/export",
                    "delete": "POST /compliance/delete",
                    "retention_check": "GET /compliance/retention/check",
                    "retention_policy": "GET /compliance/retention/policy"
                },
                "email": {
                    "process": "POST /email/process",
                    "webhook": "POST /email/webhook"
                },
                "candidates": {
                    "list": "GET /candidates/",
                    "get": "GET /candidates/{id}",
                    "update": "PATCH /candidates/{id}",
                    "delete": "DELETE /candidates/{id}"
                },
                "jobs": {
                    "create": "POST /jobs/",
                    "list": "GET /jobs/",
                    "get": "GET /jobs/{id}",
                    "update": "PATCH /jobs/{id}",
                    "delete": "DELETE /jobs/{id}"
                },
                "matching": {
                    "match": "POST /matching/match",
                    "job_candidates": "GET /matching/jobs/{id}/candidates",
                    "candidate_jobs": "GET /matching/candidates/{id}/jobs",
                    "top_candidates": "GET /matching/jobs/{id}/candidates/top",
                    "recommended_jobs": "GET /matching/candidates/{id}/jobs/recommended"
                },
                "profiles": {
                    "create": "POST /profiles/",
                    "list": "GET /profiles/?candidate_id={id} or ?job_id={id}",
                    "get": "GET /profiles/{id}",
                    "update": "PATCH /profiles/{id}",
                    "update_endorsement": "PATCH /profiles/{id}/endorsement",
                    "update_interview": "PATCH /profiles/{id}/interview",
                    "update_match": "PATCH /profiles/{id}/match",
                    "delete": "DELETE /profiles/{id}",
                    "candidate_profiles": "GET /profiles/candidates/{id}/profiles",
                    "job_profiles": "GET /profiles/jobs/{id}/profiles"
                },
                "scheduling": {
                    "create_booking": "POST /scheduling/book",
                    "schedule_ai_interview": "POST /scheduling/ai-interview",
                    "fetch_transcript": "POST /scheduling/ai-interview/{id}/transcript",
                    "booking_status": "GET /scheduling/booking/{id}/status",
                    "cancel_booking": "POST /scheduling/booking/{id}/cancel"
                },
                "linkedin": {
                    "send_connection": "POST /linkedin/connection/send",
                    "send_message": "POST /linkedin/message/send",
                    "webhook": "POST /linkedin/webhook",
                    "message_status": "GET /linkedin/message/{id}/status",
                    "extract_profile": "GET /linkedin/profile/{url}"
                }
            },
            "status": "running",
            "gdpr_compliance": {
                "data_retention_days": 730,
                "right_to_erasure": True,
                "right_to_data_portability": True,
                "consent_management": True
            }
        }

    @app.get("/healthz")
    async def health():
        """Health check endpoint."""
        from app.database import check_db_connection
        
        db_status = check_db_connection()
        
        return {
            "ok": True,
            "database": "connected" if db_status else "disconnected",
            "status": "healthy" if db_status else "degraded"
        }

    return app

app = create_app()

