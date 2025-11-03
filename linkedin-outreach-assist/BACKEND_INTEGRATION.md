# Backend Integration Guide

## Overview

This document outlines how to wire the LinkedIn Outreach Assist extension into your backend API.

## Replacing Hypothetical Notes Generation

### Current Implementation
The extension currently uses `generateHypotheticalNotes()` in `src/ui/DraftButton.tsx` to generate placeholder drafts.

### Backend Integration

Replace the `refresh()` function in `src/ui/DraftButton.tsx` with a `fetch()` call to your API endpoint.

**API Endpoint:** `POST /api/outreach/draft`

**Request Body:**
```json
{
  "candidate_context": {
    "firstName": "string",
    "hook": "string",
    "role": "string",
    "skill": "string",
    "profile_url": "string"
  },
  "tone_profile_id": "string"
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "id": "string",
      "label": "string",
      "text": "string"
    }
  ]
}
```

### Example Implementation

```typescript
const refresh = async () => {
  try {
    // Extract candidate context from LinkedIn page
    const candidateContext = extractCandidateContext(); // Implement this
    
    const response = await fetch('https://your-api.com/api/outreach/draft', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getAuthToken()}` // Implement auth
      },
      body: JSON.stringify({
        candidate_context: candidateContext,
        tone_profile_id: 'default' // Or retrieve from storage
      })
    });
    
    if (!response.ok) throw new Error('Failed to fetch drafts');
    
    const data = await response.json();
    setSuggestions(data.suggestions);
  } catch (error) {
    console.error('Error fetching drafts:', error);
    // Fallback to hypothetical notes
    setSuggestions(generateHypotheticalNotes({ firstName: "there" }));
  }
};
```

## Endorsement Generation

Use the endorsement prompt (`prompts/endorsement_prompt.txt`) server-side to generate client-ready summaries after parsing CV + interview data.

**Flow:**
1. Parse CV using `CandidateCVNormalized` schema
2. Parse interview transcript/extract interview data
3. Parse job description using `JobDescriptionNormalized` schema
4. Use endorsement prompt with LLM to generate summary
5. Return structured endorsement

**API Endpoint:** `POST /api/endorsement/generate`

**Request Body:**
```json
{
  "candidate_cv": { /* CandidateCVNormalized JSON */ },
  "job_description": { /* JobDescriptionNormalized JSON */ },
  "interview": {
    "notice_period_weeks": 4,
    "target_comp": { "base_min": 85000, "base_max": 92000, "currency": "GBP", "period": "year" },
    "motivation": "string",
    "location_prefs": "string",
    "transcript_text": "string"
  }
}
```

**Response:**
```json
{
  "endorsement": "string", // Plain text endorsement following the prompt format
  "generated_at": "2025-11-03T20:00:00Z"
}
```

## Authentication

Implement secure token storage and retrieval:

```typescript
// Store token securely (consider using chrome.storage.local)
async function getAuthToken(): Promise<string> {
  const result = await chrome.storage.local.get(['authToken']);
  return result.authToken || '';
}

async function setAuthToken(token: string): Promise<void> {
  await chrome.storage.local.set({ authToken: token });
}
```

## Error Handling

Always implement fallback to hypothetical notes if API call fails:
- Network errors
- Authentication errors
- Rate limiting
- Invalid responses

