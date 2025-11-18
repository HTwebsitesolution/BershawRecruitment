"""
Email Processing Endpoints

Handles CV processing from email attachments for 20 CVs/day workflow.
"""

from __future__ import annotations
import logging
import email
import base64
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, EmailStr, Field
from app.services.cv_parser_llm import parse_cv_bytes_to_normalized_llm
from app.services.cv_parser import parse_cv_bytes_to_normalized
from app.exceptions import ParseError, FileError, ValidationError
from app.models import CandidateCVNormalized

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["email"])


class EmailAttachment(BaseModel):
    filename: str = Field(..., description="Attachment filename")
    content_type: str = Field(..., description="MIME type (e.g., application/pdf)")
    content_base64: str = Field(..., description="Base64-encoded file content")
    size_bytes: Optional[int] = Field(None, description="File size in bytes")


class EmailProcessingRequest(BaseModel):
    from_email: EmailStr = Field(..., description="Sender email address")
    subject: Optional[str] = Field(None, description="Email subject")
    attachments: List[EmailAttachment] = Field(..., description="Email attachments (CVs)")
    use_llm: bool = Field(False, description="Use LLM-based extraction")
    max_files: int = Field(10, ge=1, le=20, description="Maximum number of files to process per request (max 20 for daily limit)")


class CVProcessingResult(BaseModel):
    filename: str
    success: bool
    cv_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class EmailProcessingResponse(BaseModel):
    processed_count: int
    successful: int
    failed: int
    results: List[CVProcessingResult]


@router.post("/process", response_model=EmailProcessingResponse)
async def process_email_cvs(
    request: EmailProcessingRequest = Body(...)
) -> EmailProcessingResponse:
    """
    Process CVs from email attachments.
    
    **Workflow:**
    - Accepts email with attachments (PDF/DOCX)
    - Processes up to 20 CVs per request (daily limit)
    - Returns normalized CV data for each attachment
    - Handles errors gracefully (continues processing if one fails)
    
    **Use Cases:**
    - Email webhook integration (e.g., SendGrid, Mailgun)
    - Direct email processing API
    - Batch CV processing
    
    **Rate Limits:**
    - Maximum 20 CVs per request
    - Designed for ~20 CVs/day workflow
    """
    try:
        # Validate attachment count
        if len(request.attachments) > request.max_files:
            raise ValidationError(
                f"Too many attachments: {len(request.attachments)} (max: {request.max_files})",
                detail=f"Please process at most {request.max_files} CVs per request"
            )
        
        if len(request.attachments) == 0:
            raise ValidationError(
                "No attachments provided",
                detail="Please provide at least one CV attachment"
            )
        
        logger.info(f"Processing email from {request.from_email} with {len(request.attachments)} attachments")
        
        results = []
        
        for attachment in request.attachments:
            try:
                # Decode base64 content
                try:
                    file_bytes = base64.b64decode(attachment.content_base64)
                except Exception as e:
                    logger.error(f"Failed to decode base64 for {attachment.filename}: {e}")
                    results.append(CVProcessingResult(
                        filename=attachment.filename,
                        success=False,
                        error=f"Failed to decode base64 content: {str(e)}"
                    ))
                    continue
                
                # Validate file size (10MB limit per file)
                MAX_FILE_SIZE = 10 * 1024 * 1024
                if len(file_bytes) > MAX_FILE_SIZE:
                    logger.warning(f"File {attachment.filename} too large: {len(file_bytes)} bytes")
                    results.append(CVProcessingResult(
                        filename=attachment.filename,
                        success=False,
                        error=f"File too large: {len(file_bytes) / 1024 / 1024:.2f}MB (max: 10MB)"
                    ))
                    continue
                
                # Validate file extension
                allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
                file_ext = '.' + attachment.filename.lower().split('.')[-1] if '.' in attachment.filename else ''
                if file_ext not in allowed_extensions:
                    logger.warning(f"Unsupported file type: {attachment.filename}")
                    results.append(CVProcessingResult(
                        filename=attachment.filename,
                        success=False,
                        error=f"Unsupported file type: {file_ext} (allowed: {', '.join(allowed_extensions)})"
                    ))
                    continue
                
                # Parse CV
                try:
                    if request.use_llm:
                        logger.info(f"Parsing {attachment.filename} with LLM (from email: {request.from_email})")
                        cv = parse_cv_bytes_to_normalized_llm(file_bytes, filename=attachment.filename)
                    else:
                        logger.info(f"Parsing {attachment.filename} with stub parser (from email: {request.from_email})")
                        cv = parse_cv_bytes_to_normalized(file_bytes, filename=attachment.filename)
                    
                    # Convert to dict for response
                    cv_data = cv.model_dump(exclude_none=True)
                    
                    results.append(CVProcessingResult(
                        filename=attachment.filename,
                        success=True,
                        cv_data=cv_data
                    ))
                    
                except Exception as e:
                    logger.error(f"Error parsing CV {attachment.filename}: {e}", exc_info=e)
                    results.append(CVProcessingResult(
                        filename=attachment.filename,
                        success=False,
                        error=f"Failed to parse CV: {str(e)}"
                    ))
            
            except Exception as e:
                logger.error(f"Unexpected error processing {attachment.filename}: {e}", exc_info=e)
                results.append(CVProcessingResult(
                    filename=attachment.filename,
                    success=False,
                    error=f"Unexpected error: {str(e)}"
                ))
        
        # Create audit log for email processing
        logger.info(
            f"Email processing complete: {request.from_email}, "
            f"{sum(1 for r in results if r.success)}/{len(results)} successful"
        )
        
        return EmailProcessingResponse(
            processed_count=len(results),
            successful=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
            results=results
        )
    
    except (ValidationError, FileError, ParseError) as e:
        raise
    
    except Exception as e:
        logger.error(f"Error processing email: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process email: {str(e)}"
        )


@router.post("/webhook")
async def email_webhook(
    payload: Dict[str, Any] = Body(...)
) -> dict:
    """
    Generic webhook endpoint for email providers (SendGrid, Mailgun, etc.).
    
    This endpoint accepts webhook payloads from email providers and extracts
    CV attachments for processing.
    
    **Supported Providers:**
    - SendGrid (inbound parse webhook)
    - Mailgun (route webhook)
    - Generic (parse manually)
    
    **Note:** Implement provider-specific parsing in production.
    """
    try:
        logger.info(f"Received email webhook: {payload.get('from', 'unknown')}")
        
        # TODO: Implement provider-specific parsing
        # - SendGrid: payload['from'], payload['attachments']
        # - Mailgun: payload['message-url'], download attachments
        # - Generic: parse email message manually
        
        return {
            "success": True,
            "message": "Webhook received (placeholder - implement provider-specific parsing)",
            "provider": "generic",
            "note": "This is a placeholder. Implement provider-specific parsing in production.",
        }
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )

