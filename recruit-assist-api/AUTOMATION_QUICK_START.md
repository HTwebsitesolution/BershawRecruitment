# Automation Features - Quick Start Guide

## ✅ What's Been Built

All three missing automation features have been implemented:

1. ✅ **Automated Call Booking** - Calendar integration
2. ✅ **AI Interviewer Integration** - Automated interview scheduling
3. ✅ **LinkedIn API Automation** - Automated messaging (ready, needs LinkedIn approval)

---

## 🚀 Quick Start

### 1. Automated Call Booking (5 minutes)

**Easiest Option: Calendly (Free)**

```bash
# 1. Create free Calendly account at https://calendly.com
# 2. Create "Interview" event type (30 minutes)
# 3. Get your username from your Calendly URL
# 4. Add to .env:
CALENDLY_USERNAME=your-calendly-username

# 5. Test it:
POST /scheduling/book
{
  "profile_id": "uuid",
  "provider": "calendly",
  "duration_minutes": 30
}

# Returns booking link - send to candidate!
```

**That's it!** Booking links work immediately.

---

### 2. AI Interviewer (Works Now!)

**No Setup Required - Custom Interviewer Works Immediately**

```bash
# Schedule AI interview
POST /scheduling/ai-interview
{
  "profile_id": "uuid",
  "interview_type": "technical",  # general, technical, cultural
  "provider": "custom",  # Works immediately!
  "duration_minutes": 45
}

# Returns interview link
# After interview, fetch transcript:
POST /scheduling/ai-interview/{interview_id}/transcript?profile_id={profile_id}
```

**Status:** ✅ Works right now - no configuration needed!

---

### 3. LinkedIn Automation (Ready, Needs Approval)

**Current State:**
- ✅ Extension drafts messages (works now)
- ✅ Extension routes replies (works now)
- ✅ API endpoints ready for automation
- ⚠️ Requires LinkedIn API approval (can take days/weeks)

**Use Extension Now:**
- Extension drafts messages automatically
- Recruiter manually sends (works immediately)

**Enable Automation Later:**
```bash
# 1. Apply for LinkedIn API access
# 2. Get approved (may take time)
# 3. Add to .env:
LINKEDIN_API_KEY=your_client_id
LINKEDIN_API_SECRET=your_client_secret

# 4. Then automation works:
POST /linkedin/message/send
{
  "recipient_urn": "urn:li:person:abc123",
  "message_text": "Automated message"
}
```

---

## 📋 Complete Workflow Example

### Automated End-to-End Flow

```bash
# 1. Match candidate to job
POST /matching/match
→ Creates profile with match score

# 2. High match score? Auto-create booking link
POST /scheduling/book
{
  "profile_id": "{profile_id}",
  "provider": "calendly"
}
→ Returns booking_link

# 3. Send booking link to candidate
# (via email or LinkedIn - manual for now)

# 4. When booking confirmed, schedule AI interview
POST /scheduling/ai-interview
{
  "profile_id": "{profile_id}",
  "interview_type": "technical",
  "provider": "custom"
}
→ Returns interview_link

# 5. Send interview link to candidate
# (via email or LinkedIn)

# 6. After interview, fetch transcript automatically
POST /scheduling/ai-interview/{interview_id}/transcript?profile_id={profile_id}
→ Transcript saved to profile
→ Insights extracted automatically

# 7. Auto-generate endorsement
POST /endorsement/generate
→ Uses CV, JD, and interview transcript

# 8. Update profile with endorsement
PATCH /profiles/{profile_id}/endorsement
{
  "endorsement_text": "...",
  "endorsement_recommendation": "Proceed"
}

# 9. Update status
PATCH /profiles/{profile_id}
{
  "status": "shortlisted"
}
```

---

## 🔧 Setup Instructions

### Minimal Setup (5 minutes)

**1. Calendly (Free Account)**
```bash
# In .env file:
CALENDLY_USERNAME=your-username

# No API key needed for basic booking links!
```

**2. Test Booking**
```bash
curl -X POST "http://localhost:8000/scheduling/book" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "your-profile-id",
    "provider": "calendly"
  }'
```

**3. Test AI Interviewer**
```bash
curl -X POST "http://localhost:8000/scheduling/ai-interview" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "your-profile-id",
    "interview_type": "technical",
    "provider": "custom"
  }'
```

**Done!** Both features work immediately.

---

## 📊 Feature Status

| Feature | Implementation | Setup Required | Status |
|---------|----------------|----------------|--------|
| **Calendar Booking** | ✅ Complete | Calendly username (free) | ✅ Ready |
| **AI Interviewer** | ✅ Complete | None | ✅ Ready |
| **LinkedIn Automation** | ✅ Complete | LinkedIn API approval | ⚠️ Pending approval |

---

## 🎯 What You Can Do Right Now

1. ✅ **Generate booking links** (with Calendly username)
2. ✅ **Schedule AI interviews** (custom interviewer works immediately)
3. ✅ **Draft LinkedIn messages** (extension works now)
4. ✅ **Route LinkedIn replies** (extension works now)
5. ⏭️ **Send LinkedIn messages automatically** (requires API approval)

---

## 📚 Full Documentation

- **[AUTOMATION_INTEGRATION_GUIDE.md](./AUTOMATION_INTEGRATION_GUIDE.md)** - Detailed setup for all providers
- **[AUTOMATION_IMPLEMENTATION.md](./AUTOMATION_IMPLEMENTATION.md)** - Implementation details
- **[CURRENT_WORKFLOW.md](./CURRENT_WORKFLOW.md)** - Current workflow documentation

---

**Next Step:** Test the features with a Calendly account setup!

