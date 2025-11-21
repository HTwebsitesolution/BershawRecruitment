# Bershaw Recruitment Platform - Workflow Summary
**Quick Reference Guide**

---

## 🎯 The Complete Flow (At a Glance)

```
1. JOB SETUP
   ↓ AI Normalizes JD
   
2. LINKEDIN SOURCING
   ↓ AI Generates Messages
   ↓ Candidate Responds
   
3. CV PROCESSING
   ↓ AI Parses CV
   ↓ Auto-Match to Jobs
   
4. AI INTERVIEWER ⭐
   ↓ AI Conducts Interview
   ↓ AI Extracts Insights
   
5. ENDORSEMENT
   ↓ AI Generates Recommendation
   
6. DECISION
   ↓ Recruiter Reviews & Hires
```

---

## 🤖 AI Interviewer/Messenger - The Game Changer

### What It Does
- **Conducts automated interviews** with candidates - **AI Personnel is the interviewer**
- **Asks intelligent questions** based on job requirements - **AI asks all questions, no human present**
- **Adapts in real-time** to candidate responses - **AI decides what to ask next**
- **Extracts insights** from conversations
- **Provides recommendations** to recruiters

**Important**: The AI Personnel **fully conducts** the interview. The candidate interacts directly with the AI, not a human interviewer. The recruiter only reviews the results afterward.

### How It Works
1. Recruiter schedules AI interview
2. Candidate receives link and joins
3. **AI Interviewer (GPT-4o) conducts 30-90 minute interview** ⭐
   - **AI Personnel asks all questions**
   - **Candidate responds directly to AI**
   - **No human interviewer present**
   - AI adapts questions based on responses
4. AI analyzes transcript and extracts insights
5. AI provides recommendation: Proceed / Hold / Reject
6. Recruiter reviews transcript and AI insights, then makes final decision

### Key Benefits
- ✅ **70% time savings** - No manual interview scheduling
- ✅ **Consistent process** - Every candidate gets same quality
- ✅ **Deep insights** - AI extracts what humans might miss
- ✅ **24/7 availability** - Candidates interview on their schedule
- ✅ **Unbiased assessment** - AI focuses on skills and fit

---

## 📋 5 Main Workflow Phases

### Phase 1: Job Setup & Sourcing
- Create job posting → AI normalizes requirements
- LinkedIn outreach → AI generates personalized messages
- Candidate replies → AI routes and responds

### Phase 2: CV Processing & Matching
- CV uploaded → AI parses and extracts data
- Auto-match to jobs → AI scores candidates
- Recruiter reviews top matches

### Phase 3: AI Interviewer ⭐
- Schedule AI interview → AI generates questions
- **AI conducts interview** → Real-time conversation
- AI analyzes transcript → Extracts insights
- Auto-update profile with interview data

### Phase 4: Endorsement
- AI generates endorsement → Evidence-based recommendation
- Recruiter reviews → Full candidate picture

### Phase 5: Decision
- Recruiter makes final decision
- Update status → Hired / Rejected / Hold

---

## 🔑 Key API Endpoints

| Phase | Endpoint | Purpose |
|-------|----------|---------|
| **Job Setup** | `POST /normalize/jd` | Normalize job description |
| **LinkedIn** | `POST /outreach/draft/connect` | Generate connection message |
| **CV Processing** | `POST /ingest/cv` | Parse and save CV |
| **Matching** | `POST /matching/match` | Score candidate against job |
| **AI Interview** | `POST /scheduling/ai-interview` | **Schedule AI interview** ⭐ |
| **Interview Results** | `GET /scheduling/ai-interview/{id}/transcript` | **Get AI insights** ⭐ |
| **Endorsement** | `POST /endorsement/generate` | Generate recommendation |

---

## 🎬 Real-World Example

**Hiring a Senior Backend Engineer:**

1. **Day 1**: Create job → AI extracts: Node.js, AWS, 5+ years
2. **Day 2-5**: LinkedIn outreach → AI messages → Candidate responds
3. **Day 6**: CV uploaded → AI parses → Auto-match: 87% score
4. **Day 7**: **AI Interview** → 45min conversation → AI recommends: Proceed
5. **Day 8**: AI endorsement → Recruiter reviews → **Hired!**

**Total Time**: 8 days (vs. 3-4 weeks traditional)

---

## 🆚 vs. Competitors

| Feature | Bershaw | Alfa AI | Traditional |
|---------|---------|---------|-------------|
| **AI Interviewer** | ✅ Adaptive, real-time | ⚠️ Pre-recorded | ❌ Manual only |
| **Evidence-Based** | ✅ Transparent | ⚠️ Generic | ❌ Subjective |
| **LinkedIn Integration** | ✅ Chrome extension | ✅ Yes | ❌ No |
| **End-to-End** | ✅ Fully automated | ⚠️ Partial | ❌ Manual |
| **GDPR Compliance** | ✅ Built-in | ⚠️ Basic | ⚠️ Varies |

---

## 📊 Automation Level

- **Fully Automated**: CV parsing, matching, AI interview, insights extraction
- **Semi-Automated**: Message drafting (review before send), interview scheduling
- **Manual**: Final hiring decision, offer negotiation

**Result**: Recruiters focus on high-value decisions, not repetitive tasks.

---

## 🎯 The AI Interviewer Advantage

The **AI Interviewer/Messenger** is what sets Bershaw apart:

1. **Intelligent Conversations** - Not just Q&A, but adaptive dialogue
2. **Deep Analysis** - Extracts insights humans might miss
3. **Consistency** - Every candidate gets same quality interview
4. **Speed** - Interviews happen 24/7, no scheduling delays
5. **Scalability** - Handle 100+ interviews simultaneously

**Bottom Line**: The AI Interviewer transforms recruitment from a time-intensive manual process into an efficient, data-driven pipeline.

---

For detailed workflow, see **[COMPLETE_WORKFLOW.md](./COMPLETE_WORKFLOW.md)**

