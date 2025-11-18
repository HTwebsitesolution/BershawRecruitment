# GDPR Compliance Implementation

This document outlines the GDPR compliance features implemented in the Recruit Assist API.

## Overview

The API includes comprehensive GDPR compliance features to handle personal data (CVs) in accordance with GDPR requirements:

- **Data Retention**: Automatic deletion after retention period (default: 730 days / 2 years)
- **Right to Erasure**: Endpoint to delete personal data on request
- **Right to Data Portability**: Export all candidate data in portable format
- **Consent Management**: Track and validate consent for data processing
- **Audit Logging**: Log all data access and modifications for compliance
- **Data Encryption**: Hash personal identifiers for pseudonymization

## Features

### 1. Data Retention Policy

**Default**: 730 days (2 years)

Personal data is automatically deleted after the retention period. The retention policy can be checked and configured.

**Endpoint**: `GET /compliance/retention/policy`

```json
{
  "retention_days": 730,
  "retention_period": "730 days",
  "description": "Personal data will be retained for the retention period and then automatically deleted",
  "compliance": "GDPR compliant"
}
```

**Check Compliance**: `GET /compliance/retention/check?created_at=2025-01-15T10:30:00Z`

### 2. Right to Erasure (Data Deletion)

Candidates have the right to request deletion of their personal data.

**Endpoint**: `POST /compliance/delete`

```json
{
  "cv_id": "cv_123",
  "email": "candidate@example.com",
  "reason": "GDPR right to erasure"
}
```

**Response**:
- Creates audit log entry
- Marks data for deletion
- Returns deletion record

### 3. Right to Data Portability

Candidates can request all their personal data in a portable format.

**Endpoint**: `POST /compliance/export`

```json
{
  "cv_id": "cv_123",
  "email": "candidate@example.com"
}
```

**Response**: JSON export of all candidate data

### 4. Consent Management

Track and validate consent for data processing.

**Record Consent**: `POST /compliance/consent`

```json
{
  "email": "candidate@example.com",
  "consent_type": "data_processing",
  "granted": true,
  "source": "email_upload"
}
```

**Check Consent**: `GET /compliance/consent/check?email=candidate@example.com&consent_type=data_processing`

**Consent Types**:
- `data_processing`: Processing personal data
- `data_storage`: Storing personal data
- `data_sharing`: Sharing with third parties
- `marketing`: Marketing communications

### 5. Audit Logging

All data access and modifications are logged for compliance.

**Logged Actions**:
- `upload`: CV uploaded
- `access`: CV data accessed
- `export`: CV data exported
- `delete`: CV data deleted
- `update`: CV data updated
- `consent_given`: Consent recorded
- `consent_withdrawn`: Consent withdrawn

### 6. Data Pseudonymization

Personal identifiers (email, phone, LinkedIn URL) can be hashed for pseudonymization.

**Method**: SHA-256 one-way hashing

**Use Cases**:
- Analytics without exposing personal data
- Compliance with "data minimization" principle
- Testing with realistic but anonymized data

## Implementation Details

### GDPR Service (`app/services/gdpr.py`)

The `GDPRCompliance` class provides:

- Retention policy management
- Consent tracking
- Data pseudonymization
- Audit logging
- Export/deletion utilities

### Compliance Endpoints (`app/routers/compliance.py`)

All compliance endpoints are under `/compliance`:

- `POST /compliance/consent` - Record consent
- `GET /compliance/consent/check` - Check consent status
- `POST /compliance/export` - Export candidate data
- `POST /compliance/delete` - Delete candidate data
- `GET /compliance/retention/check` - Check retention compliance
- `GET /compliance/retention/policy` - Get retention policy

## Data Retention Workflow

1. **Data Upload**: CV uploaded, creation date recorded
2. **Retention Period**: Default 730 days (configurable)
3. **Expiry Check**: System checks if data should be deleted
4. **Automatic Deletion**: Data deleted after retention period
5. **Audit Log**: Deletion logged for compliance

## Consent Workflow

1. **Consent Collection**: Consent recorded when CV uploaded
2. **Consent Storage**: Stored with timestamp and source
3. **Consent Validation**: Checked before processing data
4. **Consent Withdrawal**: Can be withdrawn at any time
5. **Data Deletion**: If consent withdrawn, data can be deleted

## Security Considerations

### Encryption at Rest

- Personal data should be encrypted in database
- File storage should use encrypted volumes
- API keys and secrets in environment variables

### Encryption in Transit

- HTTPS/TLS required for all API calls
- Email attachments should be encrypted
- Webhook payloads should use signed requests

### Access Control

- Authentication required for all endpoints
- Role-based access control (RBAC)
- Audit logs for all data access

## Production Checklist

- [ ] Implement database storage for CVs and consent records
- [ ] Add encryption at rest for stored CVs
- [ ] Set up automated retention policy enforcement (cron job)
- [ ] Implement authentication and authorization
- [ ] Set up audit log storage and retention
- [ ] Configure HTTPS/TLS for all endpoints
- [ ] Add rate limiting to prevent abuse
- [ ] Set up monitoring and alerting
- [ ] Create privacy policy and terms of service
- [ ] Document data processing activities (Article 30 record)

## Compliance Notes

### GDPR Articles Covered

- **Article 6 (Lawfulness)**: Consent management
- **Article 7 (Conditions for consent)**: Consent validation
- **Article 13 (Information to be provided)**: Privacy policy required
- **Article 15 (Right of access)**: Data export endpoint
- **Article 17 (Right to erasure)**: Data deletion endpoint
- **Article 20 (Right to data portability)**: Data export endpoint
- **Article 25 (Data protection by design)**: Built-in compliance features
- **Article 30 (Records of processing activities)**: Audit logging
- **Article 32 (Security of processing)**: Encryption and access control

### Best Practices

1. **Minimize Data**: Only collect necessary data
2. **Pseudonymize**: Hash personal identifiers when possible
3. **Retention**: Delete data after retention period
4. **Consent**: Track and validate consent
5. **Transparency**: Provide clear privacy policy
6. **Security**: Encrypt data at rest and in transit
7. **Audit**: Log all data access and modifications

## Testing

To test GDPR compliance features:

```bash
# Check retention policy
curl http://localhost:8000/compliance/retention/policy

# Record consent
curl -X POST http://localhost:8000/compliance/consent \
  -H "Content-Type: application/json" \
  -d '{"email": "candidate@example.com", "consent_type": "data_processing", "granted": true}'

# Export data
curl -X POST http://localhost:8000/compliance/export \
  -H "Content-Type: application/json" \
  -d '{"cv_id": "cv_123", "email": "candidate@example.com"}'

# Delete data
curl -X POST http://localhost:8000/compliance/delete \
  -H "Content-Type: application/json" \
  -d '{"cv_id": "cv_123", "email": "candidate@example.com", "reason": "GDPR request"}'
```

## References

- [GDPR Official Text](https://gdpr-info.eu/)
- [ICO GDPR Guide](https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/)
- [GDPR Checklist](https://gdpr.eu/checklist/)

