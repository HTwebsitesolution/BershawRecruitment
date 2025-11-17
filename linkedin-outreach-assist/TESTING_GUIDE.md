# Chrome Extension Testing Guide

## Prerequisites

1. **Backend API running** - The extension requires your FastAPI backend to be running
2. **Chrome browser** - For loading the extension
3. **LinkedIn account** - For testing on actual LinkedIn pages

## Step 1: Verify Backend is Running

### Start the Backend API

```bash
cd "C:\Bershaw Recruitment\recruit-assist-api"
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Test Backend Endpoints

Open a new terminal and test the endpoints:

**Test 1: Health Check**
```bash
curl http://localhost:8000/healthz
```
Expected: `{"ok": true}`

**Test 2: Tone Profile**
```bash
curl http://localhost:8000/tone/profile
```
Expected: JSON with tone profile (persona_name, templates, etc.)

**Test 3: Outreach Draft (Connection Note)**
```bash
curl -X POST http://localhost:8000/outreach/draft/connect -H "Content-Type: application/json" -d "{\"first_name\":\"Peter\",\"role_title\":\"Country Manager\",\"location\":\"Davao\",\"work_mode\":\"hybrid\"}"
```
Expected: `{"text": "Hi Peter, I'm Jean from Bershaw. I'm recruiting..."}`

**Test 4: Outreach Draft (After Accept)**
```bash
curl -X POST http://localhost:8000/outreach/draft/after-accept -H "Content-Type: application/json" -d "{\"first_name\":\"Peter\"}"
```
Expected: `{"text": "Sure, Peter. Please see the attached JD..."}`

**Test 5: Reply Routing**
```bash
curl -X POST http://localhost:8000/outreach/route-reply -H "Content-Type: application/json" -d "{\"first_name\":\"Peter\",\"message_text\":\"Yes, I'm interested!\",\"jd_link_available\":true}"
```
Expected: `{"intent": "positive_reply", "reply": "Sure, Peter..."}`

If all tests pass, your backend is ready! ✅

## Step 2: Build the Extension (if needed)

```bash
cd "C:\Bershaw Recruitment\linkedin-outreach-assist"
npm install  # Only needed first time
npm run build
```

You should see:
```
✓ built in XXXms
```

Check that `dist/contentScript.js` exists and has content.

## Step 3: Load Extension in Chrome

1. **Open Chrome Extensions Page**
   - Open Chrome
   - Go to `chrome://extensions/`
   - Or: Menu (⋮) → Extensions → Manage Extensions

2. **Enable Developer Mode**
   - Toggle "Developer mode" switch in the top-right corner

3. **Load Unpacked Extension**
   - Click "Load unpacked" button
   - Navigate to: `C:\Bershaw Recruitment\linkedin-outreach-assist`
   - Click "Select Folder"

4. **Verify Extension Loaded**
   - You should see "LinkedIn Outreach Assist" in the extensions list
   - Status should be "Enabled"
   - ID should be shown (like: `abc123def456...`)

## Step 4: Test on LinkedIn

### Test 1: Initial Connection Note

1. **Go to LinkedIn**
   - Visit `https://www.linkedin.com`
   - Log in to your account

2. **Find a Profile**
   - Search for someone or go to any LinkedIn profile
   - Example: Visit `https://www.linkedin.com/in/[someone]`

3. **Start a Connection**
   - Click "Connect" or "Message" button
   - This opens the message composer

4. **Use the Extension**
   - Look for the **"✨ Drafts"** button (bottom-right corner)
   - Click it to open the panel
   - Click **"Refresh"** button
   - Wait for the backend API call (may take 1-2 seconds)
   - You should see a suggestion labeled "Your voice"
   - Click **"Insert"** on the suggestion
   - The text should appear in the LinkedIn composer

5. **Verify**
   - ✅ Text appears in composer
   - ✅ Text matches your tone profile
   - ✅ Includes candidate's first name
   - ✅ Includes role and location info

### Test 2: Reply Routing (In Conversation Thread)

1. **Open an Existing Conversation**
   - Go to LinkedIn Messages
   - Open a conversation thread that has messages

2. **Click into the Composer**
   - Click in the message box at the bottom

3. **Use the Extension**
   - Click **"✨ Drafts"** button
   - Click **"Refresh"**
   - Extension should detect it's in a thread
   - Should call `/outreach/route-reply` endpoint
   - Should show appropriate reply based on last message

4. **Verify**
   - ✅ Detects thread context
   - ✅ Shows intent classification (positive_reply, cv_attached, etc.)
   - ✅ Generates appropriate follow-up message

## Step 5: Debugging

### Check Browser Console

1. **Open Developer Tools**
   - Press `F12` or right-click → Inspect
   - Go to "Console" tab

2. **Look for Extension Logs**
   - Messages prefixed with `[LinkedIn Outreach Assist]`
   - Should see: "Found composer via..." messages
   - Should see: "Successfully inserted text..." on success

3. **Check for Errors**
   - Red errors indicate problems
   - Common issues:
     - `Failed to fetch` → Backend not running
     - `CORS error` → Backend CORS not configured correctly
     - `Composer not found` → LinkedIn DOM changed (selectors need update)

### Check Network Requests

1. **Open Network Tab**
   - In Developer Tools, go to "Network" tab
   - Filter by "Fetch/XHR"

2. **Trigger Extension**
   - Click "Refresh" in the extension panel

3. **Verify API Calls**
   - Should see requests to `http://localhost:8000/outreach/...`
   - Check request payload (JSON in Request tab)
   - Check response (JSON in Response tab)
   - Status should be `200 OK`

### Common Issues & Solutions

#### Issue: Extension button doesn't appear
**Solution:**
- Check that extension is enabled in `chrome://extensions/`
- Refresh the LinkedIn page (F5)
- Check console for errors
- Verify `dist/contentScript.js` exists and is loaded

#### Issue: "Failed to fetch from backend"
**Solution:**
- Verify backend is running: `curl http://localhost:8000/healthz`
- Check CORS is enabled in `app/main.py`
- Verify `manifest.json` has `http://localhost:8000/*` in host_permissions
- Check browser console for CORS errors

#### Issue: "Composer not found"
**Solution:**
- Make sure you clicked INTO the message box first
- Try clicking "Connect" or "Message" button again
- LinkedIn DOM may have changed - check `linkedinComposer.ts` selectors
- Check console logs for which selectors were tried

#### Issue: Text doesn't insert
**Solution:**
- Make sure composer is focused (click in it first)
- Check console for insertion errors
- Verify `insertTextIntoComposer` is being called
- Try manually typing in the box first, then use extension

#### Issue: Wrong candidate info extracted
**Solution:**
- Check `extractCandidateInfo()` function in `DraftButton.tsx`
- LinkedIn selectors may have changed
- Check console for what values are being extracted
- May need to update DOM selectors

## Step 6: Test Different Scenarios

### Scenario 1: Profile Page (Initial Connection)
- ✅ Extension appears
- ✅ Extracts name, role, location correctly
- ✅ Generates connection note
- ✅ Inserts text successfully

### Scenario 2: Message Thread (Reply)
- ✅ Detects thread context
- ✅ Extracts last message
- ✅ Routes to correct intent
- ✅ Generates appropriate reply

### Scenario 3: Different LinkedIn Pages
- Test on profile pages
- Test in messaging interface
- Test on job posting pages (if relevant)

### Scenario 4: Error Handling
- ✅ Backend offline → Shows fallback suggestions
- ✅ Invalid API response → Shows error message
- ✅ Composer not found → Shows alert message

## Step 7: Test LLM Features (Optional)

If you want to test LLM-based generation:

1. **Make sure `.env` has your OpenAI API key**
   ```bash
   cd recruit-assist-api
   # Verify .env file has OPENAI_API_KEY=sk-...
   ```

2. **Test LLM Connection Note**
   - Use the extension on a profile
   - The default template mode should work
   - (LLM mode would need to be added as a toggle in the extension UI)

3. **Test LLM Endorsement**
   ```bash
   curl -X POST "http://localhost:8000/endorsement/generate?use_llm=true" \
     -H "Content-Type: application/json" \
     -d @test-endorsement-payload.json
   ```

## Verification Checklist

- [ ] Backend API running and responding
- [ ] Extension loaded in Chrome
- [ ] Extension button appears on LinkedIn
- [ ] Candidate info extracted correctly
- [ ] API calls successful (check Network tab)
- [ ] Connection notes generated correctly
- [ ] Text inserts into composer
- [ ] Reply routing works in threads
- [ ] Error handling works (backend offline)
- [ ] Console shows helpful logs
- [ ] No CORS errors
- [ ] Tone profile used correctly

## Next Steps

Once testing is complete:
1. Fix any issues found
2. Rebuild extension: `npm run build`
3. Reload extension in Chrome (click refresh icon on extension card)
4. Test again

## Support

If you encounter issues:
1. Check browser console for errors
2. Check backend logs for API errors
3. Verify all prerequisites are met
4. Review the troubleshooting section above

