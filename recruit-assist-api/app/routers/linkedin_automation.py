"""
LinkedIn Automation Endpoints

Endpoints for automated LinkedIn messaging and connection management.
Note: LinkedIn has strict automation policies - use with caution.
"""

from __future__ import annotations
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.linkedin_service import linkedin_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/linkedin", tags=["linkedin"])


class ConnectionRequest(BaseModel):
    """Schema for sending connection request."""
    recipient_urn: str = Field(..., description="LinkedIn member URN (e.g., urn:li:person:abc123)")
    message: str = Field(..., description="Connection message")
    note: Optional[str] = Field(None, description="Optional note")


class MessageRequest(BaseModel):
    """Schema for sending message."""
    recipient_urn: str = Field(..., description="LinkedIn member URN")
    message_text: str = Field(..., description="Message content")
    subject: Optional[str] = Field(None, description="Optional subject")


class WebhookPayload(BaseModel):
    """Schema for LinkedIn webhook payload."""
    event_type: str
    data: dict


@router.post("/connection/send")
async def send_connection_request(
    request: ConnectionRequest = Body(...),
    db: Session = Depends(get_db)
) -> dict:
    """
    Send a LinkedIn connection request.
    
    **Warning:** LinkedIn has strict automation policies. This endpoint
    should only be used with proper LinkedIn API access and permissions.
    
    **Requirements:**
    - LinkedIn API access approved
    - Valid API credentials
    - Recipient consent for connection
    
    **Returns:**
    - Request ID
    - Status
    - Timestamp
    """
    try:
        if not linkedin_service.linkedin_api_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LinkedIn API not enabled or configured. Please set up LinkedIn API credentials."
            )
        
        result = linkedin_service.send_connection_request(
            recipient_urn=request.recipient_urn,
            message=request.message,
            note=request.note
        )
        
        logger.info(f"Sent LinkedIn connection request to {request.recipient_urn}")
        
        return {
            "success": True,
            "request_id": result["request_id"],
            "status": result["status"],
            "sent_at": result["sent_at"]
        }
    
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Error sending connection request: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send connection request: {str(e)}"
        )


@router.post("/message/send")
async def send_message(
    request: MessageRequest = Body(...),
    db: Session = Depends(get_db)
) -> dict:
    """
    Send a LinkedIn message.
    
    **Warning:** LinkedIn has strict automation policies. This endpoint
    should only be used with proper LinkedIn API access and permissions.
    
    **Requirements:**
    - LinkedIn API access approved
    - Existing connection with recipient
    - Valid API credentials
    
    **Returns:**
    - Message ID
    - Status
    - Timestamp
    """
    try:
        if not linkedin_service.linkedin_api_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LinkedIn API not enabled or configured. Please set up LinkedIn API credentials."
            )
        
        result = linkedin_service.send_message(
            recipient_urn=request.recipient_urn,
            message_text=request.message_text,
            subject=request.subject
        )
        
        logger.info(f"Sent LinkedIn message to {request.recipient_urn}")
        
        return {
            "success": True,
            "message_id": result["message_id"],
            "status": result["status"],
            "sent_at": result["sent_at"]
        }
    
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Error sending message: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/webhook")
async def handle_linkedin_webhook(
    payload: WebhookPayload = Body(...),
    db: Session = Depends(get_db)
) -> dict:
    """
    Handle incoming LinkedIn webhook events.
    
    **Events:**
    - `MESSAGE_RECEIVED` - Incoming message
    - `CONNECTION_ACCEPTED` - Connection accepted
    - `MESSAGE_READ` - Message read receipt
    
    **Note:** Requires webhook configuration in LinkedIn developer portal.
    """
    try:
        result = linkedin_service.handle_webhook(payload.data)
        
        logger.info(f"Processed LinkedIn webhook: {payload.event_type}")
        
        return {
            "success": True,
            "event_type": payload.event_type,
            "result": result
        }
    
    except Exception as e:
        logger.error(f"Error handling LinkedIn webhook: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle webhook: {str(e)}"
        )


@router.get("/message/{message_id}/status")
async def get_message_status(
    message_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """Get the status of a sent message (sent, delivered, read, replied)."""
    try:
        if not linkedin_service.linkedin_api_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LinkedIn API not enabled or configured."
            )
        
        status_result = linkedin_service.track_message_status(message_id)
        
        return {
            "success": True,
            "message_id": message_id,
            "status": status_result["status"],
            "sent_at": status_result.get("sent_at"),
            "read_at": status_result.get("read_at"),
            "replied_at": status_result.get("replied_at")
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error getting message status: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get message status: {str(e)}"
        )


@router.get("/profile/{profile_url}")
async def extract_profile_data(
    profile_url: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Extract profile data from LinkedIn URL.
    
    **Note:** This requires either:
    - LinkedIn API access with member permissions
    - Web scraping (with candidate consent)
    
    **Returns:**
    - Profile data (name, headline, experience, etc.)
    """
    try:
        if not linkedin_service.linkedin_api_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LinkedIn API not enabled or configured."
            )
        
        profile_data = linkedin_service.get_profile_data(profile_url)
        
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not extract profile data. Ensure LinkedIn API is configured and profile URL is valid."
            )
        
        return {
            "success": True,
            "profile_url": profile_url,
            "profile_data": profile_data
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error extracting profile data: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract profile data: {str(e)}"
        )

