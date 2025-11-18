# Automation Integration Guide

This guide explains how to set up and integrate the automated features:
- Calendar integration (booking links)
- AI interviewer integration
- LinkedIn API automation

---

## 1. Automated Call Booking

### Overview

The system can automatically generate booking links for interview scheduling using multiple calendar providers.

### Supported Providers

- **Calendly** (Recommended) - Easy setup, professional booking experience
- **Google Calendar** - Direct calendar integration
- **Outlook Calendar** - Microsoft 365 integration
- **Manual** - Custom booking system

### Setup

#### Calendly Setup

1. **Create Calendly Account**
   - Sign up at https://calendly.com
   - Create an "Interview" event type (30-45 minutes)
   - Get your Calendly username

2. **Get API Key** (Optional, for advanced features)
   - Go to Calendly Integrations → API
   - Generate API key
   - Add to `.env`:
     ```bash
     CALENDLY_API_KEY=your_api_key_here
     CALENDLY_USERNAME=your-calendly-username
     CALENDLY_EVENT_TYPE=interview
     ```

3. **Test Booking**
   ```bash
   POST /scheduling/book
   {
     "profile_id": "uuid",
     "duration_minutes": 30,
     "provider": "calendly"
   }
   ```

#### Google Calendar Setup

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com
   - Create new project
   - Enable Google Calendar API

2. **Create Service Account**
   - Create service account
   - Generate JSON key
   - Share calendar with service account email

3. **Configure Settings**
   ```bash
   GOOGLE_CALENDAR_API_KEY=your_api_key_here
   GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
   ```

#### Outlook Calendar Setup

1. **Create Azure App Registration**
   - Go to https://portal.azure.com
   - Create app registration
   - Add Calendar.ReadWrite permission

2. **Get Client Credentials**
   ```bash
   MICROSOFT_GRAPH_CLIENT_ID=your_client_id
   MICROSOFT_GRAPH_CLIENT_SECRET=your_client_secret
   ```

### Usage

```bash
# Create booking link
POST /scheduling/book
{
  "profile_id": "uuid",
  "duration_minutes": 30,
  "provider": "calendly",
  "timezone": "Europe/London"
}

# Response
{
  "booking_link": "https://calendly.com/...",
  "booking_id": "calendly_...",
  "provider": "calendly",
  "duration_minutes": 30,
  "expires_at": "2025-02-15T10:00:00Z",
  "status": "pending"
}

# Check booking status
GET /scheduling/booking/{booking_id}/status?provider=calendly

# Cancel booking
POST /scheduling/booking/{booking_id}/cancel?provider=calendly
```

---

## 2. AI Interviewer Integration

### Overview

The system can schedule and manage AI-powered interviews with automatic transcript capture.

### Supported Providers

- **Custom OpenAI-based** (Default) - Built-in custom interviewer
- **HireVue** - Commercial AI interviewer service
- **MyInterview** - Commercial AI interviewer service

### Setup

#### Custom OpenAI Interviewer (Default - No Setup Required)

The system includes a custom OpenAI-based interviewer that works out of the box.

#### HireVue Setup

1. **Sign Up for HireVue**
   - Visit https://www.hirevue.com
   - Create account and subscribe
   - Get API credentials

2. **Configure Settings**
   ```bash
   HIREVUE_API_KEY=your_api_key
   HIREVUE_API_SECRET=your_api_secret
   ```

3. **Test Integration**
   ```bash
   POST /scheduling/ai-interview
   {
     "profile_id": "uuid",
     "interview_type": "technical",
     "provider": "hirevue"
   }
   ```

#### MyInterview Setup

1. **Sign Up for MyInterview**
   - Visit https://www.myinterview.com
   - Create account
   - Get API key

2. **Configure Settings**
   ```bash
   MYINTERVIEW_API_KEY=your_api_key
   ```

### Usage

```bash
# Schedule AI interview
POST /scheduling/ai-interview
{
  "profile_id": "uuid",
  "interview_type": "technical",  # general, technical, cultural
  "duration_minutes": 45,
  "provider": "custom",  # custom, hirevue, myinterview
  "questions": []  # Optional custom questions
}

# Response
{
  "success": true,
  "interview_id": "custom_...",
  "interview_link": "https://bershaw-recruitment.com/interview?...",
  "provider": "custom",
  "interview_type": "technical",
  "duration_minutes": 45,
  "scheduled_at": "2025-01-15T10:00:00Z",
  "status": "scheduled",
  "questions": [...]
}

# Fetch transcript after interview
POST /scheduling/ai-interview/{interview_id}/transcript?profile_id={profile_id}

# Response
{
  "success": true,
  "interview_id": "...",
  "transcript": "Interview transcript text...",
  "insights": {...},
  "scores": {...},
  "recommendation": "Proceed",
  "profile_updated": true
}
```

### Interview Types

- **general** - General interview questions (motivation, background, etc.)
- **technical** - Technical skills assessment (based on job requirements)
- **cultural** - Cultural fit assessment (teamwork, values, etc.)

### Automatic Transcript Capture

After the interview is completed, call the transcript endpoint to:
1. Fetch transcript from provider
2. Extract insights automatically
3. Update profile with transcript and insights
4. Trigger endorsement generation (optional)

---

## 3. LinkedIn API Automation

### Overview

LinkedIn API integration for automated messaging and connection management.

**⚠️ Important:** LinkedIn has strict automation policies. Use with caution and ensure compliance.

### Setup

#### LinkedIn Developer Account

1. **Create LinkedIn App**
   - Go to https://www.linkedin.com/developers/apps
   - Create new app
   - Request access to Messaging API (requires approval)

2. **Get API Credentials**
   ```bash
   LINKEDIN_API_KEY=your_client_id
   LINKEDIN_API_SECRET=your_client_secret
   ```

3. **Configure OAuth Redirect**
   - Set redirect URL in LinkedIn app settings
   - Configure required scopes:
     - `w_member_social` - Send messages
     - `r_liteprofile` - Read profiles
     - `w_messages` - Send messages

4. **Approve API Access**
   - LinkedIn requires approval for Messaging API
   - May take several days
   - Submit use case and explanation

### Usage

#### Send Connection Request

```bash
POST /linkedin/connection/send
{
  "recipient_urn": "urn:li:person:abc123",
  "message": "Hi John, I'm reaching out about a Senior Engineer role...",
  "note": "Optional note"
}
```

#### Send Message

```bash
POST /linkedin/message/send
{
  "recipient_urn": "urn:li:person:abc123",
  "message_text": "Thank you for connecting! Here's the job description...",
  "subject": "Job Opportunity - Senior Engineer"
}
```

#### Track Message Status

```bash
GET /linkedin/message/{message_id}/status

# Response
{
  "success": true,
  "message_id": "...",
  "status": "read",  # sent, delivered, read, replied
  "sent_at": "2025-01-15T10:00:00Z",
  "read_at": "2025-01-15T10:05:00Z",
  "replied_at": null
}
```

#### Webhook for Incoming Messages

```bash
POST /linkedin/webhook
{
  "event_type": "MESSAGE_RECEIVED",
  "data": {
    "sender_urn": "urn:li:person:abc123",
    "message_text": "Yes, I'm interested!",
    "timestamp": "2025-01-15T10:00:00Z"
  }
}

# System automatically:
# 1. Classifies message intent
# 2. Generates response
# 3. Returns response for review/auto-send
```

### LinkedIn URN Format

LinkedIn URNs (Uniform Resource Names) identify members:
- Format: `urn:li:person:{id}`
- Example: `urn:li:person:abc123xyz`

**Note:** URNs are not public URLs. You need LinkedIn API access to convert profile URLs to URNs.

### Limitations & Best Practices

1. **Rate Limits**
   - LinkedIn has strict rate limits
   - Don't exceed message limits
   - Implement delays between messages

2. **Compliance**
   - Always obtain consent
   - Follow LinkedIn's User Agreement
   - Don't spam or send unsolicited messages

3. **Approval Required**
   - Messaging API requires LinkedIn approval
   - May not be available immediately
   - Have a clear use case ready

4. **Fallback Strategy**
   - Extension can draft messages for manual sending
   - Use automation only when approved
   - Always allow manual review before sending

---

## 4. Workflow Automation

### Automated Workflow Triggers

The system can automatically trigger actions based on events:

#### Example Workflows

**1. High Match Score → Auto-Shortlist**
```
When: Match score > 0.8
Action: 
  - Update profile status to "shortlisted"
  - Create booking link
  - Send booking link to candidate
```

**2. CV Received → Auto-Match**
```
When: CV uploaded/emailed
Action:
  - Parse CV
  - Match to all active jobs
  - Notify recruiter if match > 0.7
```

**3. Interview Completed → Auto-Generate Endorsement**
```
When: Interview transcript received
Action:
  - Extract insights
  - Generate endorsement
  - Update profile with endorsement
```

**4. Booking Confirmed → Schedule AI Interview**
```
When: Booking status = "confirmed"
Action:
  - Schedule AI interview
  - Send interview link to candidate
```

### Implementation

Workflow automation can be implemented using:

1. **Background Job Queue** (Celery + Redis)
   - Async task processing
   - Scheduled jobs
   - Event-driven triggers

2. **Webhook Integration**
   - External service webhooks
   - Calendar booking confirmations
   - Interview completion notifications

3. **Database Triggers** (PostgreSQL)
   - Trigger on status changes
   - Automated updates
   - Status transitions

---

## 5. Complete Automated Workflow

### End-to-End Automation Example

```
1. Job Posted
   └─> Normalize JD → Save to DB

2. Candidate Found (LinkedIn)
   └─> Send Connection Request (automated if approved)

3. Connection Accepted
   └─> Auto-send Follow-up Message (automated if approved)

4. Candidate Replies "Interested"
   └─> Auto-route Reply → Generate Response
   └─> Auto-send Response (with approval)

5. CV Received
   └─> Auto-parse → Auto-match → Create Profile

6. Match Score > 0.8
   └─> Auto-shortlist → Auto-create Booking Link
   └─> Auto-send Booking Link (via email/LinkedIn)

7. Booking Confirmed
   └─> Auto-schedule AI Interview
   └─> Auto-send Interview Link

8. Interview Completed
   └─> Auto-fetch Transcript
   └─> Auto-extract Insights
   └─> Auto-generate Endorsement
   └─> Auto-update Profile

9. Endorsement Generated
   └─> Auto-update Status → Notify Recruiter
```

---

## 6. Configuration Summary

### Required Environment Variables

```bash
# Calendar Integration
CALENDLY_API_KEY=your_calendly_api_key
CALENDLY_USERNAME=your-calendly-username
CALENDLY_EVENT_TYPE=interview

GOOGLE_CALENDAR_API_KEY=your_google_api_key
GOOGLE_CALENDAR_ID=your_calendar_id

MICROSOFT_GRAPH_CLIENT_ID=your_client_id
MICROSOFT_GRAPH_CLIENT_SECRET=your_client_secret

# AI Interviewer
HIREVUE_API_KEY=your_hirevue_api_key
HIREVUE_API_SECRET=your_hirevue_api_secret

MYINTERVIEW_API_KEY=your_myinterview_api_key

# LinkedIn API
LINKEDIN_API_KEY=your_linkedin_client_id
LINKEDIN_API_SECRET=your_linkedin_client_secret
```

### Minimal Setup (Quick Start)

For quick start, you can use:
- **Calendly** for booking (free tier available)
- **Custom AI Interviewer** (no setup required)
- **LinkedIn Extension** for message drafting (manual send)

This requires minimal configuration and works immediately.

---

## 7. Testing Automation

### Test Calendar Integration

```bash
# Create booking link
curl -X POST "http://localhost:8000/scheduling/book" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "uuid",
    "provider": "calendly",
    "duration_minutes": 30
  }'
```

### Test AI Interviewer

```bash
# Schedule interview
curl -X POST "http://localhost:8000/scheduling/ai-interview" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "uuid",
    "interview_type": "technical",
    "provider": "custom"
  }'
```

### Test LinkedIn API

```bash
# Send message (requires LinkedIn API access)
curl -X POST "http://localhost:8000/linkedin/message/send" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_urn": "urn:li:person:abc123",
    "message_text": "Test message"
  }'
```

---

## 8. Next Steps

1. **Choose Providers**
   - Select calendar provider (Calendly recommended)
   - Select AI interviewer (custom for now, upgrade later)
   - Consider LinkedIn API (requires approval)

2. **Configure Credentials**
   - Set up provider accounts
   - Add API keys to `.env`
   - Test integrations

3. **Implement Workflow Automation**
   - Set up background jobs
   - Configure webhooks
   - Test automated triggers

4. **Production Deployment**
   - Secure API keys
   - Set up monitoring
   - Implement rate limiting
   - Add error handling

---

## Troubleshooting

### Calendar Integration Issues

**Problem:** Booking links not generated
- Check API keys are set correctly
- Verify provider account is active
- Check provider API documentation

### AI Interviewer Issues

**Problem:** Interview not scheduled
- Check interview provider API status
- Verify API credentials
- Review error logs

### LinkedIn API Issues

**Problem:** Messages not sending
- Verify LinkedIn API access is approved
- Check rate limits
- Review LinkedIn API documentation
- Ensure proper OAuth flow

---

**Last Updated:** January 2025  
**Status:** Integration guides created, ready for setup

