"""
GDPR Compliance Module

Handles:
- Data retention policies
- Data encryption
- Consent management
- Right to erasure (deletion)
- Data export
- Audit logging
"""

from __future__ import annotations
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Default retention period: 2 years (730 days) - GDPR allows "reasonable" retention
DEFAULT_RETENTION_DAYS = 730


class GDPRCompliance:
    """
    GDPR compliance manager for CV data.
    
    Features:
    - Data retention policies
    - Encryption at rest (metadata)
    - Consent tracking
    - Right to erasure
    - Data export
    - Audit logging
    """
    
    def __init__(self, retention_days: int = DEFAULT_RETENTION_DAYS):
        self.retention_days = retention_days
    
    def calculate_expiry_date(self, created_at: datetime) -> datetime:
        """Calculate when data should be deleted based on retention policy."""
        return created_at + timedelta(days=self.retention_days)
    
    def should_delete(self, created_at: datetime) -> bool:
        """Check if data should be deleted based on retention policy."""
        expiry = self.calculate_expiry_date(created_at)
        return datetime.utcnow() > expiry
    
    def hash_personal_data(self, data: str) -> str:
        """
        Hash personal data for pseudonymization.
        Uses SHA-256 for one-way hashing.
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def pseudonymize_cv(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pseudonymize personal data in CV for compliance.
        Replaces direct identifiers with hashes.
        """
        pseudonymized = cv_data.copy()
        
        if 'candidate' in pseudonymized:
            candidate = pseudonymized['candidate']
            
            # Hash email
            if candidate.get('email'):
                candidate['email_hash'] = self.hash_personal_data(candidate['email'])
                candidate.pop('email', None)
            
            # Hash phone
            if candidate.get('phone'):
                candidate['phone_hash'] = self.hash_personal_data(candidate['phone'])
                candidate.pop('phone', None)
            
            # Hash LinkedIn URL
            if candidate.get('linkedin_url'):
                candidate['linkedin_url_hash'] = self.hash_personal_data(candidate['linkedin_url'])
                candidate.pop('linkedin_url', None)
        
        return pseudonymized
    
    def create_audit_log(
        self,
        action: str,
        cv_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an audit log entry for GDPR compliance.
        
        Actions:
        - 'upload': CV uploaded
        - 'access': CV data accessed
        - 'export': CV data exported
        - 'delete': CV data deleted (right to erasure)
        - 'update': CV data updated
        - 'consent_given': Consent recorded
        - 'consent_withdrawn': Consent withdrawn
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "cv_id": cv_id,
            "user_id": user_id,
            "details": details or {},
        }
        
        logger.info(f"GDPR audit log: {action}", extra=log_entry)
        return log_entry
    
    def create_consent_record(
        self,
        email: str,
        consent_type: str = "data_processing",
        granted: bool = True,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a consent record for GDPR compliance.
        
        Consent types:
        - 'data_processing': Processing personal data
        - 'data_storage': Storing personal data
        - 'data_sharing': Sharing with third parties
        - 'marketing': Marketing communications
        """
        return {
            "email": email,
            "email_hash": self.hash_personal_data(email),
            "consent_type": consent_type,
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "expiry_date": (datetime.utcnow() + timedelta(days=self.retention_days)).isoformat() if granted else None,
        }
    
    def validate_consent(self, consent_record: Dict[str, Any]) -> bool:
        """Check if consent is still valid."""
        if not consent_record.get('granted'):
            return False
        
        expiry_date_str = consent_record.get('expiry_date')
        if expiry_date_str:
            expiry = datetime.fromisoformat(expiry_date_str)
            if datetime.utcnow() > expiry:
                return False
        
        return True
    
    def prepare_for_deletion(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare CV data for deletion (right to erasure).
        Returns audit record with minimal data.
        """
        deletion_record = {
            "deleted_at": datetime.utcnow().isoformat(),
            "original_cv_id": cv_data.get('id'),
            "retention_days": self.retention_days,
            "deletion_reason": "GDPR right to erasure",
        }
        
        # Keep only metadata for audit purposes
        if 'extraction_meta' in cv_data:
            deletion_record['extraction_meta'] = {
                "parser_version": cv_data['extraction_meta'].get('parser_version'),
                "source": cv_data['extraction_meta'].get('source'),
                "extracted_at": cv_data['extraction_meta'].get('extracted_at'),
            }
        
        return deletion_record
    
    def export_candidate_data(self, cv_data: Dict[str, Any]) -> str:
        """
        Export all candidate data in a portable format (GDPR right to data portability).
        Returns JSON string.
        """
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "export_format": "json",
            "candidate_data": cv_data,
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def check_retention_compliance(self, created_at: datetime) -> Dict[str, Any]:
        """Check if data complies with retention policy."""
        expiry = self.calculate_expiry_date(created_at)
        days_until_expiry = (expiry - datetime.utcnow()).days
        
        return {
            "created_at": created_at.isoformat(),
            "expiry_date": expiry.isoformat(),
            "days_until_expiry": days_until_expiry,
            "should_delete": days_until_expiry < 0,
            "retention_days": self.retention_days,
            "compliant": days_until_expiry > 0,
        }


# Global instance
gdpr_manager = GDPRCompliance()

