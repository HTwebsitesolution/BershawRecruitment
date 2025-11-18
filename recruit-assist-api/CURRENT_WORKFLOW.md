# Current Recruitment Workflow

## Overview

This document describes the **current workflow** of the Bershaw Recruitment Platform and identifies **gaps** where automation could be improved.

---

## Current Workflow (What We Have)

### 1. **Job Posting Setup**
```
Recruiter → Normalize JD → Save to Database
POST /normalize/jd?save_to_db=true
```
- Recruiter provides free-text job description
- System normalizes it into structured data
- Job posting saved to `job_postings` table

### 2. **LinkedIn Outreach** (Chrome Extension)

#### **Step 2a: Initial Connection**
```
Recruiter → LinkedIn Extension → Draft Connection Message
POST /outreach/draft/connect
```
- Recruiter browses LinkedIn profiles
- Chrome extension generates personalized connection message
- Uses tone profile (Jean from Bershaw)
- Message inserted into LinkedIn composer
- **Recruiter manually sends the message**

#### **Step 2b: After Connection Accepted**
```
Candidate accepts connection → Recruiter → Extension → Draft Follow-up
POST /outreach/draft/after-accept
```
- When candidate accepts connection
- Extension generates follow-up message
- Asks for CV, salary expectations, notice period
- **Recruiter manually sends the message**

#### **Step 2c: Route Replies**
```
Candidate replies → Recruiter → Extension → Classify & Generate Response
POST /outreach/route-reply
```
- Extension classifies reply intent:
  - `positive_reply` - Interested
  - `request_jd` - Wants job details
  - `cv_attached` - Sent CV
  - `decline` - Not interested
  - `unknown` - Unclear intent
- Generates appropriate response
- **Recruiter manually reviews and sends**

### 3. **CV Processing** (Manual or Email)

#### **Option A: Direct Upload**
```
Recruiter → Upload CV → Parse & Save
POST /ingest/cv?save_to_db=true&consent_granted=true
```
- Recruiter uploads CV file
- System parses and extracts structured data
- Saves to `candidates` table

#### **Option B: Email Processing**
```
Candidate emails CV → Email webhook → Parse & Save
POST /email/process
```
- Candidate sends CV via email
- Email webhook receives attachment
- System parses CV automatically
- Saves to database

### 4. **Candidate Matching** (Automatic)
```
System → Match Candidate to Job → Create Profile
POST /matching/match?create_profile=true
```
- System calculates match score (0.0 to 1.0)
- Creates `candidate_profile` record
- Stores match score and breakdown

### 5. **Review Candidates** (Manual)
```
Recruiter → View Matched Candidates
GET /matching/jobs/{job_id}/candidates/top?top_n=10&min_score=0.7
```
- Recruiter reviews top candidates
- Sorted by match score
- Can filter by minimum score

### 6. **Interview** (Manual - No Automation)

#### **Current State:**
- **NO automated call booking**
- **NO AI interviewer integration**
- **Manual interview scheduling** (outside system)

#### **What We Have:**
```
Recruiter → Manually Schedule Call → After Interview → Update Profile
PATCH /profiles/{profile_id}/interview
```
- Recruiter schedules call manually (phone, calendar, etc.)
- After interview, recruiter manually updates profile:
  - Interview date
  - Interview notes
  - Interview transcript (if available)
  - Interview insights (motivation, risks, etc.)

### 7. **Endorsement Generation** (Manual Trigger)
```
Recruiter → Generate Endorsement → Update Profile
POST /endorsement/generate?use_llm=true
PATCH /profiles/{profile_id}/endorsement
```
- Recruiter triggers endorsement generation
- System uses CV, JD, and interview data
- Generates endorsement text
- Recruiter updates profile with endorsement

### 8. **Status Management** (Manual)
```
Recruiter → Update Profile Status
PATCH /profiles/{profile_id}
```
- Recruiter updates status:
  - `active` → `shortlisted` → `hired`
  - Or `rejected` / `archived`

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT WORKFLOW                         │
└─────────────────────────────────────────────────────────────┘

1. Job Posting
   └─> Normalize JD → Save to DB

2. LinkedIn Outreach (Chrome Extension)
   ├─> Draft connection message (manual send)
   ├─> Draft follow-up after accept (manual send)
   └─> Route replies → Generate response (manual send)

3. CV Processing
   ├─> Direct upload (manual)
   └─> Email webhook (automatic)

4. Matching
   └─> Automatic match scoring → Create profile

5. Review
   └─> Recruiter reviews matches (manual)

6. Interview ⚠️ MANUAL - NO AUTOMATION
   ├─> ❌ NO automated call booking
   ├─> ❌ NO AI interviewer
   └─> ✅ Manual interview → Update profile

7. Endorsement
   └─> Generate → Update profile (manual trigger)

8. Status
   └─> Update status (manual)
```

---

## What's Missing (Gaps)

### ❌ **Automated Call Booking**

**Current State:** Manual scheduling outside the system

**What's Needed:**
- Calendar integration (Google Calendar, Outlook)
- Automated scheduling links (Calendly, etc.)
- Send booking link to candidate
- Track booking status
- Reminder notifications

**Potential Implementation:**
```python
POST /profiles/{profile_id}/schedule-call
{
  "preferred_times": [...],
  "duration_minutes": 30,
  "calendar_provider": "google"
}
```

### ❌ **AI Interviewer Integration**

**Current State:** Manual interviews only

**What's Needed:**
- AI interviewer service integration
- Automated interview scheduling
- Interview transcript capture
- Real-time interview insights
- Automatic profile updates

**Potential Implementation:**
```python
POST /profiles/{profile_id}/schedule-ai-interview
{
  "interview_type": "technical" | "cultural" | "general",
  "duration_minutes": 45,
  "questions": [...]  # Optional custom questions
}

# After interview
GET /profiles/{profile_id}/interview-results
# Returns: transcript, insights, recommendation
```

### ❌ **Automated Reply Sending**

**Current State:** Extension generates messages, but recruiter must manually send

**What's Needed:**
- LinkedIn API integration (with proper permissions)
- Automated message sending (with approval workflow)
- Reply handling automation
- Follow-up scheduling

**Note:** LinkedIn's API restrictions may limit full automation.

### ❌ **Workflow Automation**

**Current State:** Each step requires manual intervention

**What's Needed:**
- Automated workflow triggers
- Status-based actions
- Notification system
- Task management

**Example Workflow:**
```
Match score > 0.8 → Auto-shortlist → Auto-send interview invite
CV received → Auto-match → Auto-notify recruiter
Interview completed → Auto-generate endorsement → Auto-update status
```

---

## Ideal Workflow (Future State)

### **Fully Automated Pipeline:**

```
1. Job Posting
   └─> Normalize JD → Save to DB

2. LinkedIn Outreach (Automated)
   ├─> Auto-draft connection message
   ├─> Auto-send (with approval)
   ├─> Auto-route replies
   └─> Auto-send responses

3. CV Processing (Automated)
   └─> Email webhook → Parse → Save → Match

4. Matching (Automated)
   └─> Auto-match → Auto-create profile

5. Review (Semi-Automated)
   └─> Auto-shortlist high scores → Notify recruiter

6. Interview (Automated) ⭐ NEW
   ├─> Auto-send booking link
   ├─> Auto-schedule AI interview
   ├─> AI interviewer conducts interview
   ├─> Auto-capture transcript
   └─> Auto-extract insights

7. Endorsement (Automated)
   └─> Auto-generate after interview → Auto-update profile

8. Status (Automated)
   └─> Auto-update based on interview results
```

---

## Current vs. Ideal Comparison

| Step | Current | Ideal |
|------|---------|-------|
| **LinkedIn Outreach** | Manual send | Auto-send (with approval) |
| **CV Processing** | Manual upload or email | Fully automated |
| **Matching** | ✅ Automatic | ✅ Automatic |
| **Call Booking** | ❌ Manual | ✅ Automated scheduling |
| **Interview** | ❌ Manual | ✅ AI interviewer |
| **Endorsement** | Manual trigger | ✅ Auto-generate |
| **Status Updates** | Manual | ✅ Auto-update |

---

## Integration Points Needed

### 1. **Calendar Integration**
- Google Calendar API
- Outlook Calendar API
- Calendly API
- Send booking links
- Track availability

### 2. **AI Interviewer Service**
- Third-party AI interviewer (e.g., HireVue, MyInterview)
- Or build custom AI interviewer
- Video/audio interview platform
- Transcript extraction
- Insight generation

### 3. **LinkedIn API** (Limited)
- LinkedIn API for messaging (requires approval)
- Connection management
- Profile data extraction
- **Note:** LinkedIn has strict automation policies

### 4. **Notification System**
- Email notifications
- Slack/Teams integration
- SMS notifications
- In-app notifications

### 5. **Workflow Engine**
- Trigger-based automation
- Conditional logic
- Task scheduling
- Status transitions

---

## Recommendations

### **Short-Term (Quick Wins)**

1. **Add Interview Booking Endpoint**
   - Integrate with Calendly or similar
   - Generate booking links
   - Track booking status

2. **Automate Endorsement Generation**
   - Auto-generate after interview data is added
   - Background job processing

3. **Add Notification System**
   - Email notifications for new matches
   - Slack integration for status updates

### **Medium-Term (Significant Value)**

1. **AI Interviewer Integration**
   - Partner with AI interviewer service
   - Or build custom solution
   - Automated interview scheduling
   - Transcript capture

2. **Workflow Automation**
   - Trigger-based actions
   - Auto-status updates
   - Conditional workflows

### **Long-Term (Full Automation)**

1. **LinkedIn Automation** (with proper permissions)
   - Automated message sending
   - Reply handling
   - Connection management

2. **Complete Pipeline Automation**
   - End-to-end automation
   - Minimal manual intervention
   - AI-driven decisions

---

## Current API Endpoints for Workflow

### **LinkedIn Outreach**
- `POST /outreach/draft/connect` - Draft connection message
- `POST /outreach/draft/after-accept` - Draft follow-up
- `POST /outreach/route-reply` - Classify and respond

### **CV Processing**
- `POST /ingest/cv` - Upload and parse CV
- `POST /email/process` - Process email attachments

### **Matching**
- `POST /matching/match` - Match candidate to job
- `GET /matching/jobs/{id}/candidates` - Get matches

### **Interview** (Manual)
- `PATCH /profiles/{id}/interview` - Update interview data

### **Endorsement**
- `POST /endorsement/generate` - Generate endorsement
- `PATCH /profiles/{id}/endorsement` - Update endorsement

### **Status**
- `PATCH /profiles/{id}` - Update profile status

---

## Summary

**Current State:**
- ✅ LinkedIn Outreach Assistant (drafts messages, routes replies)
- ✅ CV parsing and matching (automatic)
- ✅ Profile management (manual updates)
- ❌ **NO automated call booking**
- ❌ **NO AI interviewer integration**
- ❌ **NO automated message sending**

**Key Gap:**
The system currently **drafts messages** but requires **manual sending**. There's **no automated interview booking or AI interviewer** - interviews are conducted manually and data is entered afterward.

**Next Steps:**
1. Add interview booking integration (Calendly/calendar APIs)
2. Integrate AI interviewer service
3. Add workflow automation
4. Consider LinkedIn API integration (with proper permissions)

---

**Last Updated:** January 2025  
**Status:** Current workflow documented, gaps identified

