# Bershaw Recruitment Platform - Complete Workflow
**When Fully Built and Completed**

This document describes the complete end-to-end workflow of the Bershaw Recruitment Platform, including the AI Interviewer/Messenger (AI Personnel) feature.

---

## 🎯 Overview

The Bershaw Recruitment Platform automates the entire recruitment pipeline from job posting to candidate hiring, with AI-powered assistance at every stage. The system includes an **AI Interviewer/Messenger (AI Personnel)** that **fully conducts automated interviews** and provides intelligent insights.

### ⭐ Key Feature: AI Personnel Conducts Interviews

**The AI Personnel (powered by GPT-4o) fully conducts the interview session:**
- ✅ **AI asks all questions** - No human interviewer present
- ✅ **Candidate interacts directly with AI** - Real-time conversation
- ✅ **AI adapts questions** based on candidate responses
- ✅ **AI manages entire flow** - 30-90 minute sessions
- ✅ **Recruiter reviews results** after interview completes

This is **not** AI-assisted interviewing where a human asks questions. The **AI Personnel is the interviewer**.

---

## 🔄 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    BERSHAW RECRUITMENT PLATFORM - COMPLETE WORKFLOW                 │
└─────────────────────────────────────────────────────────────────────────────────────┘

PHASE 1: JOB SETUP & SOURCING
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 1. Job Posting Setup                                                                │
│    Recruiter → POST /normalize/jd?save_to_db=true                                   │
│    ├─> Free-text JD input                                                          │
│    ├─> AI Normalization (LLM) → Structured JSON                                    │
│    ├─> Save to job_postings table                                                  │
│    └─> Returns: Job ID, normalized requirements                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 2. LinkedIn Candidate Sourcing (Chrome Extension)                                  │
│    Recruiter browses LinkedIn → Extension activated                               │
│    ├─> Extract candidate info (name, role, location)                              │
│    ├─> POST /outreach/draft/connect (AI generates message)                        │
│    ├─> Personalized connection message inserted                                   │
│    └─> Recruiter reviews & sends (or auto-send with approval)                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 3. Connection Accepted → Follow-up                                                 │
│    Candidate accepts → Extension detects                                            │
│    ├─> POST /outreach/draft/after-accept                                           │
│    ├─> AI generates follow-up message                                              │
│    ├─> Asks for CV, salary expectations, notice period                            │
│    └─> Recruiter sends (or auto-send)                                             │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 4. Candidate Reply Handling (AI Messenger)                                         │
│    Candidate replies → Extension analyzes                                          │
│    ├─> POST /outreach/route-reply                                                  │
│    ├─> AI classifies intent: positive/request_jd/cv_attached/decline              │
│    ├─> AI generates contextual response                                           │
│    └─> Recruiter reviews & sends (or auto-send)                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘


PHASE 2: CV PROCESSING & MATCHING
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 5. CV Processing (Multiple Input Methods)                                           │
│    Option A: Direct Upload                                                         │
│    ├─> POST /ingest/cv?save_to_db=true&consent_granted=true                        │
│    ├─> AI Parsing (LLM) → Extract structured data                                 │
│    └─> Save to candidates table                                                   │
│                                                                                     │
│    Option B: Email Webhook                                                         │
│    ├─> Candidate emails CV → POST /email/process                                   │
│    ├─> Auto-parse attachment                                                       │
│    └─> Auto-save to database                                                      │
│                                                                                     │
│    Option C: LinkedIn Attachment                                                  │
│    ├─> Extension detects CV attachment in message                                 │
│    ├─> Auto-upload to /ingest/cv                                                  │
│    └─> Auto-process and save                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 6. Automatic Candidate Matching                                                    │
│    System automatically matches CV to all active jobs                              │
│    ├─> POST /matching/match?create_profile=true                                    │
│    ├─> Multi-factor scoring algorithm:                                            │
│    │   ├─> Skills match (must-haves: 35%, nice-to-haves: 10%)                     │
│    │   ├─> Experience match (20%)                                                 │
│    │   ├─> Location match (15%)                                                   │
│    │   ├─> Salary match (10%)                                                     │
│    │   └─> Right to work (10%)                                                    │
│    ├─> Match score: 0.0 to 1.0 (0% to 100%)                                      │
│    ├─> Create candidate_profile record                                            │
│    └─> Store match breakdown                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 7. Recruiter Review & Shortlisting                                                │
│    Recruiter → GET /matching/jobs/{id}/candidates/top?top_n=10&min_score=0.7     │
│    ├─> View top candidates sorted by match score                                  │
│    ├─> Review match breakdown (skills, experience, etc.)                         │
│    ├─> Filter by minimum score                                                    │
│    ├─> Review candidate profiles                                                  │
│    └─> Shortlist candidates (update status: active → shortlisted)                │
└─────────────────────────────────────────────────────────────────────────────────────┘


PHASE 3: AI INTERVIEWER & SCHEDULING
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 8. AI Interviewer Scheduling ⭐ KEY FEATURE                                       │
│    Recruiter → POST /scheduling/ai-interview                                       │
│    ├─> Input: profile_id, interview_type (general/technical/cultural)              │
│    ├─> AI generates interview questions based on JD requirements                  │
│    ├─> Select provider: custom (OpenAI) / HireVue / MyInterview                   │
│    ├─> System creates interview session                                           │
│    ├─> Returns: interview_link, interview_id                                      │
│    └─> Auto-send interview link to candidate via email/LinkedIn                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 9. Alternative: Calendar Booking (Human Interview)                                 │
│    Recruiter → POST /scheduling/book                                               │
│    ├─> Select calendar provider: Calendly / Google / Outlook                     │
│    ├─> Set duration, preferred times, timezone                                    │
│    ├─> System generates booking link                                              │
│    ├─> Auto-send booking link to candidate                                       │
│    └─> Track booking status                                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 10. AI Interviewer Session (AI Personnel) ⭐ CORE FEATURE                           │
│     Candidate clicks interview link → AI Interviewer interface                    │
│     ├─> AI Interviewer (GPT-4o) greets candidate                                  │
│     ├─> Conducts interview based on job requirements                               │
│     ├─> Asks contextual questions:                                               │
│     │   ├─> Technical: "Tell me about your experience with Node.js"              │
│     │   ├─> Behavioral: "Describe a challenging project you led"                 │
│     │   └─> Cultural: "What motivates you in your career?"                       │
│     ├─> Real-time conversation with AI                                            │
│     ├─> AI adapts questions based on responses                                    │
│     ├─> Captures full transcript                                                  │
│     ├─> AI analyzes responses in real-time                                        │
│     └─> Interview duration: 30-90 minutes (configurable)                          │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 11. AI Interview Analysis & Insights                                               │
│     Interview completes → AI processes transcript                                  │
│     ├─> POST /scheduling/ai-interview/{id}/transcript                             │
│     ├─> AI extracts insights:                                                    │
│     │   ├─> Technical competency assessment                                       │
│     │   ├─> Communication skills                                                  │
│     │   ├─> Cultural fit indicators                                               │
│     │   ├─> Motivation and interest level                                         │
│     │   ├─> Red flags or concerns                                                │
│     │   └─> Strengths and standout qualities                                      │
│     ├─> AI generates interview summary                                            │
│     ├─> AI provides recommendation: Proceed / Hold / Reject                      │
│     └─> Auto-update candidate_profile with interview data                        │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 12. Profile Update with Interview Data                                             │
│     System → PATCH /profiles/{id}/interview                                        │
│     ├─> interview_date: Auto-populated                                           │
│     ├─> interview_transcript: Full conversation                                 │
│     ├─> interview_data (JSON):                                                   │
│     │   ├─> notice_period_weeks                                                  │
│     │   ├─> target_compensation                                                   │
│     │   ├─> motivation                                                           │
│     │   ├─> location_preferences                                                 │
│     │   ├─> top_skills (mentioned in interview)                                 │
│     │   ├─> risks (concerns raised)                                             │
│     │   └─> ai_insights (AI-generated analysis)                                  │
│     └─> interview_notes: AI-generated summary                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘


PHASE 4: ENDORSEMENT & DECISION
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 13. AI Endorsement Generation                                                       │
│     System auto-triggers after interview (or manual trigger)                       │
│     ├─> POST /endorsement/generate?use_llm=true                                    │
│     ├─> Input: CV data + JD requirements + Interview data                         │
│     ├─> AI generates evidence-based endorsement:                                 │
│     │   ├─> Candidate background summary                                         │
│     │   ├─> Fit vs JD requirements (✔/△/✖ with evidence)                        │
│     │   ├─> Interview insights                                                    │
│     │   ├─> Compensation & notice period                                         │
│     │   ├─> Risks and unknowns                                                    │
│     │   └─> Recommendation: Proceed / Hold / Reject                              │
│     ├─> Fit score: 0.0 to 1.0                                                    │
│     └─> Auto-save to profile: PATCH /profiles/{id}/endorsement                   │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 14. Recruiter Review & Decision                                                    │
│     Recruiter reviews in dashboard:                                               │
│     ├─> View candidate profile with full history                                 │
│     ├─> Review match score & breakdown                                           │
│     ├─> Review AI interview transcript & insights                                │
│     ├─> Review AI-generated endorsement                                          │
│     ├─> Compare with other candidates                                            │
│     └─> Make decision:                                                           │
│         ├─> Proceed → Update status: shortlisted → hired                         │
│         ├─> Hold → Keep in pipeline, request more info                           │
│         └─> Reject → Update status: rejected → archived                         │
└─────────────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 15. Offer & Onboarding (Future Enhancement)                                        │
│     Candidate hired → System updates:                                              │
│     ├─> Update profile status: hired                                              │
│     ├─> Archive job posting (if filled)                                           │
│     ├─> Send offer letter (automated)                                            │
│     ├─> Track onboarding process                                                 │
│     └─> Update analytics & metrics                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Interviewer/Messenger (AI Personnel) - Detailed Flow

### What is the AI Interviewer?

The **AI Interviewer** (also called "AI Personnel" or "AI Messenger") is an intelligent virtual interviewer powered by GPT-4o that:

1. **Conducts automated interviews** with candidates via video/chat interface - **The AI acts as the interviewer, not just an assistant**
2. **Generates contextual questions** based on job requirements
3. **Adapts in real-time** to candidate responses - **AI asks follow-up questions and probes deeper**
4. **Extracts insights** from conversations
5. **Provides recommendations** to recruiters

**Key Point**: The AI Personnel **fully conducts** the interview session. There is no human interviewer present during the AI interview. The AI asks all questions, listens to responses, asks follow-ups, and manages the entire conversation flow.

### AI Interviewer Workflow (Step-by-Step)

#### **Step 1: Interview Scheduling**
```
Recruiter Action:
  → Selects candidate from shortlist
  → Clicks "Schedule AI Interview"
  → Chooses interview type: General / Technical / Cultural
  → Sets duration: 30-90 minutes
  → Selects provider: Custom (OpenAI) / HireVue / MyInterview

System Action:
  → POST /scheduling/ai-interview
  → AI generates interview questions based on:
     - Job requirements (must-haves, nice-to-haves)
     - Candidate CV (experience, skills)
     - Interview type selected
  → Creates interview session
  → Generates unique interview link
  → Sends email to candidate with link
  → Updates profile with interview_id
```

#### **Step 2: Candidate Joins Interview**
```
Candidate Action:
  → Receives email with interview link
  → Clicks link → Opens AI Interviewer interface
  → Sees welcome screen with job details
  → Clicks "Start Interview"

System Action:
  → Loads interview session
  → Initializes AI Interviewer (GPT-4o)
  → AI greets candidate with personalized message
  → AI explains interview format and duration
```

#### **Step 3: AI Interviewer Conducts Interview** ⭐ **AI Personnel is the Interviewer**
```
**The AI Personnel fully conducts the interview. No human interviewer is present.**

AI Interviewer Flow:
  
  Opening (AI Personnel):
    "Hi [Candidate Name], I'm the AI interviewer for the [Job Title] 
     role at [Client]. I'll be asking you questions about your experience 
     and fit for this position. This will take about 45 minutes. 
     Let's begin!"
     
  **The AI Personnel:**
  - Asks all questions (not a human)
  - Listens to and analyzes responses in real-time
  - Decides what to ask next based on candidate answers
  - Manages the entire conversation flow
  - Conducts the full 30-90 minute interview session

  Question 1 - Background (AI):
    "Tell me about yourself and your background in [relevant field]."
    
  Candidate Response:
    [Candidate provides background]
    
  AI Analysis (Real-time):
    - Extracts key skills mentioned
    - Identifies relevant experience
    - Notes any gaps vs requirements
    - Determines next question focus

  Question 2 - Technical (AI):
    "I see you have experience with [Skill from CV]. Can you walk me 
     through a specific project where you used [Skill] to solve a 
     challenging problem?"
    
  Candidate Response:
    [Candidate describes project]
    
  AI Follow-up (Adaptive):
    - Asks clarifying questions based on response
    - Digs deeper into technical details
    - Assesses depth of knowledge

  Question 3 - Behavioral (AI):
    "Describe a time when you had to work under pressure to meet 
     a tight deadline. How did you handle it?"
    
  [Continues with 5-10 questions total]
  
  Closing Questions (AI):
    - "What are your salary expectations?"
    - "What is your notice period?"
    - "What motivates you about this role?"
    - "Do you have any questions about the position?"
```

#### **Step 4: AI Interview Analysis**
```
After Interview Completes:

AI Processing:
  → Analyzes full transcript
  → Extracts key insights:
     * Technical competency score
     * Communication clarity
     * Problem-solving approach
     * Cultural fit indicators
     * Motivation level
     * Red flags or concerns
     * Standout strengths

AI Generates:
  → Interview summary (2-3 paragraphs)
  → Key insights (bullet points)
  → Recommendation: Proceed / Hold / Reject
  → Confidence score: 0.0 to 1.0

System Updates:
  → PATCH /profiles/{id}/interview
  → Stores transcript, insights, recommendation
  → Notifies recruiter: "Interview completed"
```

#### **Step 5: Recruiter Review**
```
Recruiter Dashboard:
  → Sees notification: "AI Interview completed for [Candidate]"
  → Opens candidate profile
  → Reviews:
     - Full interview transcript
     - AI-generated insights
     - AI recommendation
     - Extracted data (salary, notice period, etc.)
  → Makes final decision
```

---

## 📊 Complete Workflow with AI Components

### AI-Powered Features Throughout the Pipeline

| Stage | AI Feature | What It Does |
|-------|-----------|--------------|
| **Job Setup** | JD Normalizer (LLM) | Converts free-text JD to structured requirements |
| **LinkedIn Outreach** | Message Generator (LLM) | Personalizes connection messages and replies |
| **Reply Routing** | Intent Classifier (LLM) | Classifies candidate replies and generates responses |
| **CV Processing** | CV Parser (LLM) | Extracts structured data from PDF/DOCX CVs |
| **Matching** | Matching Algorithm | Scores candidates against job requirements |
| **Interview** | **AI Interviewer (GPT-4o)** | **Conducts automated interviews, extracts insights** |
| **Endorsement** | Endorsement Generator (LLM) | Creates evidence-based candidate endorsements |

---

## 🔄 Automated vs Manual Steps

### Fully Automated (No Human Intervention)
- ✅ CV parsing and extraction
- ✅ Candidate matching and scoring
- ✅ AI interview question generation
- ✅ AI interview transcript capture
- ✅ AI insight extraction
- ✅ Endorsement generation (can be auto-triggered)
- ✅ Database updates and profile creation

### Semi-Automated (Human Review/Approval)
- ⚠️ LinkedIn message sending (draft → review → send)
- ⚠️ Interview scheduling (AI generates link → recruiter sends)
- ⚠️ Shortlisting (AI scores → recruiter reviews)
- ⚠️ Final decision (AI recommends → recruiter decides)

### Manual (Human-Driven)
- 👤 Job posting creation
- 👤 LinkedIn candidate sourcing
- 👤 Final hiring decision
- 👤 Offer negotiation

---

## 🎯 Key Workflow Triggers

### Automatic Triggers
```
1. CV Uploaded → Auto-match to all jobs → Auto-create profiles
2. Match Score > 0.8 → Auto-notify recruiter → Auto-shortlist (optional)
3. Interview Completed → Auto-generate endorsement → Auto-update profile
4. Endorsement Generated → Auto-notify recruiter for review
5. Profile Status Changed → Auto-update analytics
```

### Manual Triggers
```
1. Recruiter clicks "Schedule AI Interview" → Interview scheduled
2. Recruiter clicks "Generate Endorsement" → Endorsement created
3. Recruiter updates status → Profile updated
4. Recruiter sends LinkedIn message → Message sent
```

---

## 📱 User Interfaces

### 1. **Recruiter Dashboard** (Web)
- View job postings and candidates
- Review match scores and AI insights
- Schedule AI interviews
- Review interview transcripts
- Generate and review endorsements
- Update candidate status
- Analytics and reporting

### 2. **LinkedIn Chrome Extension**
- Generate personalized messages
- Route candidate replies
- Extract candidate information
- Insert AI-generated messages

### 3. **AI Interviewer Interface** (Candidate-Facing)
- Welcome screen with job details
- Video/chat interface with AI
- Real-time conversation
- Question display and response input
- Interview progress indicator
- Thank you screen after completion

### 4. **Email Notifications**
- Interview invitation emails
- Booking confirmation emails
- Interview completion notifications
- Status update notifications

---

## 🔗 API Endpoints Used in Complete Workflow

### Phase 1: Job Setup & Sourcing
- `POST /normalize/jd?save_to_db=true` - Normalize job description
- `POST /outreach/draft/connect` - Generate connection message
- `POST /outreach/draft/after-accept` - Generate follow-up
- `POST /outreach/route-reply` - Classify and respond to replies

### Phase 2: CV Processing & Matching
- `POST /ingest/cv?save_to_db=true` - Upload and parse CV
- `POST /email/process` - Process email attachments
- `POST /matching/match?create_profile=true` - Match candidate to job
- `GET /matching/jobs/{id}/candidates/top` - Get top candidates

### Phase 3: AI Interviewer & Scheduling
- `POST /scheduling/ai-interview` - **Schedule AI interview** ⭐
- `POST /scheduling/book` - Create calendar booking
- `GET /scheduling/ai-interview/{id}/transcript` - **Get interview transcript** ⭐
- `PATCH /profiles/{id}/interview` - Update interview data

### Phase 4: Endorsement & Decision
- `POST /endorsement/generate?use_llm=true` - Generate endorsement
- `PATCH /profiles/{id}/endorsement` - Update endorsement
- `PATCH /profiles/{id}` - Update profile status

---

## 🎬 Example: Complete Candidate Journey

### Scenario: Hiring a Senior Backend Engineer

**Day 1: Job Setup**
1. Recruiter creates job posting: "Senior Backend Engineer - Node.js, AWS"
2. System normalizes JD → Extracts requirements, salary, location
3. Job saved to database with ID: `job_123`

**Day 2-5: LinkedIn Sourcing**
4. Recruiter browses LinkedIn, finds candidate "Alex Morgan"
5. Chrome extension extracts: name="Alex", role="Backend Engineer", location="London"
6. Extension calls API → AI generates personalized message
7. Recruiter reviews message, clicks send on LinkedIn
8. Alex accepts connection
9. Extension generates follow-up: "Hi Alex, could you send your CV?"
10. Recruiter sends follow-up
11. Alex replies: "Sure, here's my CV" (attaches PDF)
12. Extension detects attachment → Auto-uploads to `/ingest/cv`
13. System parses CV with AI → Extracts: Node.js expert, 6 years, AWS experience
14. System auto-matches to `job_123` → Match score: 0.87 (87%)
15. System creates candidate_profile with match breakdown
16. Recruiter sees notification: "New high-match candidate for Senior Backend Engineer"

**Day 6: Review & Shortlisting**
17. Recruiter reviews Alex's profile in dashboard
18. Sees match score: 87% (Skills: 95%, Experience: 90%, Location: 100%)
19. Reviews CV details and match breakdown
20. Recruiter shortlists Alex → Status: `active` → `shortlisted`

**Day 7: AI Interview**
21. Recruiter clicks "Schedule AI Interview" for Alex
22. Selects: Interview type="Technical", Duration=45min, Provider="Custom"
23. System generates interview questions based on JD requirements
24. System sends email to Alex: "You're invited to an AI interview"
25. Alex clicks link → Opens AI Interviewer interface
26. **AI Interviewer conducts interview:**
    - "Hi Alex, tell me about your Node.js experience"
    - "Can you describe a challenging AWS project?"
    - "What's your approach to system design?"
    - [8 more questions, 45 minutes total]
27. Interview completes → AI analyzes transcript
28. AI extracts insights:
    - Technical: Strong Node.js, good AWS knowledge
    - Communication: Clear and articulate
    - Motivation: High interest in role
    - Notice period: 4 weeks
    - Salary expectation: £90k
29. AI recommendation: **Proceed** (confidence: 0.92)
30. System auto-updates profile with interview data

**Day 8: Endorsement & Decision**
31. System auto-triggers endorsement generation
32. AI generates endorsement using CV + JD + Interview data
33. Endorsement includes:
    - Background summary
    - Fit ratings: Node.js ✔, AWS ✔, Experience ✔
    - Interview insights
    - Recommendation: **Proceed**
34. Recruiter reviews endorsement in dashboard
35. Recruiter sees full picture: CV match (87%) + AI interview (Proceed)
36. Recruiter makes decision: **Proceed to offer**
37. Status updated: `shortlisted` → `hired`
38. System archives job posting (position filled)

---

## 🚀 Competitive Advantages

### vs. Alfa AI and Other Platforms

1. **AI Interviewer with Real-Time Adaptation**
   - Not just pre-recorded questions
   - AI adapts based on candidate responses
   - Extracts deeper insights through conversation

2. **Evidence-Based Endorsements**
   - Every recommendation backed by CV + interview evidence
   - Transparent fit ratings (✔/△/✖)
   - Audit-friendly format

3. **Seamless LinkedIn Integration**
   - Chrome extension for direct outreach
   - AI-powered message personalization
   - Reply routing and classification

4. **End-to-End Automation**
   - From LinkedIn sourcing to AI interview to endorsement
   - Minimal manual intervention
   - AI handles repetitive tasks

5. **GDPR-First Design**
   - Built-in compliance from day one
   - Data retention and consent management
   - Right to erasure and data portability

---

## 📈 Metrics & Analytics

The platform tracks:
- **Time to fill** - From job posting to hire
- **Interview completion rate** - % of candidates who complete AI interviews
- **AI interview quality** - Recruiter satisfaction with AI insights
- **Match accuracy** - How well AI predictions match final decisions
- **Response rates** - LinkedIn message engagement
- **Pipeline velocity** - Candidates moving through stages

---

## 🎯 Summary

The Bershaw Recruitment Platform provides a **complete, AI-powered recruitment workflow**:

1. **Job Setup** → AI normalizes job descriptions
2. **LinkedIn Sourcing** → AI generates personalized messages
3. **CV Processing** → AI extracts structured data
4. **Matching** → AI scores candidates automatically
5. **AI Interviewer** → **AI conducts interviews and extracts insights** ⭐
6. **Endorsement** → AI generates evidence-based recommendations
7. **Decision** → Recruiter makes informed decision with AI support

The **AI Interviewer/Messenger** is the centerpiece that:
- Conducts intelligent, adaptive interviews
- Extracts deep insights from conversations
- Provides actionable recommendations
- Reduces recruiter time by 70%+
- Ensures consistent, unbiased interview process

**Result**: Faster hiring, better candidate fit, reduced recruiter workload.

---

**Last Updated:** January 2025  
**Status:** Complete workflow design (implementation 70% complete)

