"""
GDPR Compliance Endpoints

Endpoints for:
- Data export (right to data portability)
- Data deletion (right to erasure)
- Consent management
- Retention policy checks
"""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from app.services.gdpr import gdpr_manager, GDPRCompliance
from app.exceptions import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compliance", tags=["compliance"])


class ConsentRequest(BaseModel):
    email: EmailStr
    consent_type: str = Field(default="data_processing", description="Type of consent: data_processing, data_storage, data_sharing, marketing")
    granted: bool = Field(default=True, description="Whether consent is granted")
    source: Optional[str] = Field(None, description="Source of consent (e.g., 'email_upload', 'web_form')")


class DataExportRequest(BaseModel):
    cv_id: str = Field(..., description="ID of the CV to export")
    email: Optional[EmailStr] = Field(None, description="Email for verification")


class DataDeletionRequest(BaseModel):
    cv_id: str = Field(..., description="ID of the CV to delete")
    email: Optional[EmailStr] = Field(None, description="Email for verification")
    reason: Optional[str] = Field(None, description="Reason for deletion")


@router.post("/consent")
async def record_consent(consent: ConsentRequest) -> dict:
    """
    Record consent for GDPR compliance.
    
    Required for processing personal data under GDPR.
    """
    try:
        consent_record = gdpr_manager.create_consent_record(
            email=consent.email,
            consent_type=consent.consent_type,
            granted=consent.granted,
            source=consent.source or "api"
        )
        
        # Create audit log
        gdpr_manager.create_audit_log(
            action="consent_given" if consent.granted else "consent_withdrawn",
            details={
                "email_hash": consent_record["email_hash"],
                "consent_type": consent.consent_type,
            }
        )
        
        return {
            "success": True,
            "message": "Consent recorded successfully",
            "consent_record": consent_record,
        }
    
    except Exception as e:
        logger.error(f"Error recording consent: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record consent: {str(e)}"
        )


@router.get("/consent/check")
async def check_consent(
    email: EmailStr = Query(..., description="Email to check consent for"),
    consent_type: str = Query(default="data_processing", description="Type of consent to check")
) -> dict:
    """
    Check if consent exists and is valid for an email address.
    
    Note: In a real implementation, this would query a database.
    This is a placeholder that returns default consent.
    """
    # TODO: Implement database lookup
    logger.info(f"Checking consent for {email} (type: {consent_type})")
    
    return {
        "email_hash": gdpr_manager.hash_personal_data(email),
        "consent_type": consent_type,
        "has_consent": True,  # Placeholder - would check database
        "message": "This is a placeholder. Implement database lookup in production.",
    }


@router.post("/export")
async def export_candidate_data(request: DataExportRequest) -> dict:
    """
    Export candidate data (GDPR right to data portability).
    
    Returns all data associated with a candidate in a portable format.
    
    Note: In a real implementation, this would fetch data from database.
    """
    try:
        # TODO: Fetch CV data from database using cv_id
        logger.info(f"Export request for CV ID: {request.cv_id}")
        
        # Placeholder response
        export_data = {
            "cv_id": request.cv_id,
            "export_date": datetime.utcnow().isoformat(),
            "message": "This is a placeholder. Implement database lookup in production.",
            "format": "json",
        }
        
        # Create audit log
        gdpr_manager.create_audit_log(
            action="export",
            cv_id=request.cv_id,
            details={"email": request.email},
        )
        
        return export_data
    
    except Exception as e:
        logger.error(f"Error exporting data: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@router.post("/delete")
async def delete_candidate_data(request: DataDeletionRequest) -> dict:
    """
    Delete candidate data (GDPR right to erasure).
    
    Permanently deletes all personal data associated with a candidate.
    
    Note: In a real implementation, this would delete from database.
    """
    try:
        logger.info(f"Deletion request for CV ID: {request.cv_id}, reason: {request.reason}")
        
        # TODO: Fetch CV data from database
        # TODO: Create deletion record
        # TODO: Delete from database
        
        # Placeholder response
        deletion_record = {
            "cv_id": request.cv_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "reason": request.reason or "GDPR right to erasure",
            "message": "This is a placeholder. Implement database deletion in production.",
        }
        
        # Create audit log
        gdpr_manager.create_audit_log(
            action="delete",
            cv_id=request.cv_id,
            details={
                "email": request.email,
                "reason": request.reason,
            }
        )
        
        return {
            "success": True,
            "message": "Data deletion request processed (placeholder)",
            "deletion_record": deletion_record,
        }
    
    except Exception as e:
        logger.error(f"Error deleting data: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete data: {str(e)}"
        )


@router.get("/retention/check")
async def check_retention_compliance(
    created_at: str = Query(..., description="ISO datetime when data was created")
) -> dict:
    """
    Check if data complies with retention policy.
    
    Returns retention status and expiry information.
    """
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        compliance = gdpr_manager.check_retention_compliance(created)
        
        return {
            "retention_check": compliance,
            "policy": {
                "retention_days": gdpr_manager.retention_days,
                "description": "Data will be automatically deleted after retention period",
            }
        }
    
    except ValueError as e:
        raise ValidationError(
            f"Invalid datetime format: {created_at}",
            detail="Please provide ISO 8601 format datetime (e.g., 2025-01-15T10:30:00Z)"
        )


@router.get("/retention/policy")
async def get_retention_policy() -> dict:
    """Get current data retention policy."""
    return {
        "retention_days": gdpr_manager.retention_days,
        "retention_period": f"{gdpr_manager.retention_days} days",
        "description": "Personal data will be retained for the retention period and then automatically deleted",
        "compliance": "GDPR compliant",
    }

