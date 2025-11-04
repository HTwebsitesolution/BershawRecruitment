import React, { useEffect, useState } from "react";
import { getActiveComposer, insertTextIntoComposer } from "../lib/linkedinComposer";

type Suggestion = { id: string; label: string; text: string };

function generateHypotheticalNotes(candidate: {
  firstName: string;
  hook?: string;
  role?: string;
  skill?: string;
}) : Suggestion[] {
  const fn = candidate.firstName || "there";
  const role = candidate.role || "role";
  const skill = candidate.skill || "experience";
  const hook = candidate.hook || "recent work";

  return [
    {
      id: "s1",
      label: "Short intro + CV ask",
      text: `Hi ${fn} — saw your ${hook}. If you're exploring options, could you send me your CV? I'll share a JD that looks aligned.`
    },
    {
      id: "s2",
      label: "Role-led pitch",
      text: `Hi ${fn}, I'm filling a ${role} that lines up with your ${skill}. If you're open, send over your CV and I'll forward the JD for a quick look.`
    },
    {
      id: "s3",
      label: "Salary-transparency variant",
      text: `Hi ${fn}. I help candidates land roles they actually enjoy. If you're curious, share your CV and I'll reply with JD + salary band up front.`
    }
  ];
}

/**
 * Extract candidate information from LinkedIn page.
 * This is a basic implementation - can be enhanced based on actual LinkedIn DOM structure.
 */
function extractCandidateInfo(): { first_name: string; role_title: string; location: string; work_mode: string } {
  // Try to extract first name from profile page
  // LinkedIn profile pages typically have the name in h1.text-heading-xlarge or similar
  const nameElement = document.querySelector("h1.text-heading-xlarge, h1.break-words, .ph5 h1");
  const fullName = nameElement?.textContent?.trim() || "";
  const first_name = fullName.split(" ")[0] || "there";

  // Try to extract role/title from profile header
  const roleElement = document.querySelector(".text-body-medium.break-words, .ph5 .text-body-medium");
  const role_title = roleElement?.textContent?.trim() || "Software Engineer";

  // Try to extract location
  const locationElement = document.querySelector(".text-body-small.inline.t-black--light, .pv-text-details__left-panel .text-body-small");
  const location = locationElement?.textContent?.trim() || "UK";

  // Default to hybrid work mode (can be enhanced to detect from job postings)
  const work_mode = "hybrid";

  return { first_name, role_title, location, work_mode };
}

/**
 * Check if we're in a conversation thread (vs initial connection).
 * Looks for existing messages in the thread.
 */
function isInThread(): boolean {
  // Check if there are message bubbles in the conversation
  const messageBubbles = document.querySelectorAll(".msg-s-message-list__message, .msg-s-event-listitem, [data-test-id='message-item']");
  return messageBubbles.length > 0;
}

/**
 * Extract the last message from the candidate in the thread.
 */
function getLastCandidateMessage(): string {
  // Look for the last message bubble that's not from us (could check sender attribute)
  // This is a simplified version - LinkedIn's DOM structure may vary
  const messages = document.querySelectorAll(".msg-s-message-list__message, .msg-s-event-listitem");
  if (messages.length === 0) return "";

  const lastMessage = messages[messages.length - 1];
  const messageText = lastMessage.querySelector(".msg-s-message-list__message-body, .msg-s-text-bubble__content")?.textContent?.trim() || "";
  return messageText;
}

const API_BASE_URL = "http://localhost:8000";

export default function DraftButton() {
  const [open, setOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Pre-load with fallback suggestions using extracted candidate info
    const candidateInfo = extractCandidateInfo();
    setSuggestions(generateHypotheticalNotes({
      firstName: candidateInfo.first_name,
      hook: "recent work",
      role: candidateInfo.role_title,
      skill: "experience"
    }));
  }, []);

  // IMPORTANT: All text insertion is user-initiated via button clicks only.
  // This ensures compliance with LinkedIn's policies - we never auto-insert text.
  const insert = (text: string) => {
    const el = getActiveComposer();
    if (!el) {
      alert("Composer not found. Click into a LinkedIn message box and try again.");
      return;
    }
    const success = insertTextIntoComposer(el, text);
    if (!success) {
      alert("Failed to insert text. Please try again.");
    }
    setOpen(false);
  };

  const refresh = async () => {
    setLoading(true);
    setError(null);

    try {
      const candidateInfo = extractCandidateInfo();
      const inThread = isInThread();

      if (inThread) {
        // We're in a conversation thread - use reply routing
        const lastMessage = getLastCandidateMessage();
        
        if (lastMessage) {
          const res = await fetch(`${API_BASE_URL}/outreach/route-reply`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              first_name: candidateInfo.first_name,
              message_text: lastMessage,
              jd_link_available: true
            })
          });

          if (!res.ok) {
            throw new Error(`API error: ${res.status}`);
          }

          const data = await res.json();
          setSuggestions([{
            id: "r1",
            label: `Auto-reply (${data.intent})`,
            text: data.reply
          }]);
        } else {
          // In thread but no message found - fallback to after-accept message
          const res = await fetch(`${API_BASE_URL}/outreach/draft/after-accept`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              first_name: candidateInfo.first_name
            })
          });

          if (!res.ok) {
            throw new Error(`API error: ${res.status}`);
          }

          const data = await res.json();
          setSuggestions([{
            id: "f1",
            label: "Follow-up",
            text: data.text
          }]);
        }
      } else {
        // Initial connection - generate connection note
        const res = await fetch(`${API_BASE_URL}/outreach/draft/connect`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            first_name: candidateInfo.first_name,
            role_title: candidateInfo.role_title,
            location: candidateInfo.location,
            work_mode: candidateInfo.work_mode
          })
        });

        if (!res.ok) {
          throw new Error(`API error: ${res.status}`);
        }

        const data = await res.json();
        setSuggestions([{
          id: "s1",
          label: "Your voice",
          text: data.text
        }]);
      }
    } catch (err) {
      console.error("Error fetching drafts:", err);
      setError("Failed to fetch from backend. Using fallback suggestions.");
      // Fallback to hypothetical notes on error
      setSuggestions(generateHypotheticalNotes({
        firstName: extractCandidateInfo().first_name,
        hook: "recent project",
        role: extractCandidateInfo().role_title,
        skill: "experience"
      }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="li-assist-root">
      <div className="li-assist-launcher">
        <button className="li-assist-btn" onClick={() => setOpen(v => !v)}>
          ✨ Drafts
        </button>
      </div>

      {open && (
        <div className="li-assist-panel">
          <h4>Insert a personalised note</h4>
          {error && <div style={{ color: "red", fontSize: "12px", marginBottom: 8 }}>{error}</div>}
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <button 
              className="li-assist-insert" 
              onClick={refresh}
              disabled={loading}
            >
              {loading ? "Loading..." : "Refresh"}
            </button>
          </div>
          {suggestions.map(s => (
            <div key={s.id} className="li-assist-suggestion">
              <div>{s.text}</div>
              <button className="li-assist-insert" onClick={() => insert(s.text)}>Insert</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


