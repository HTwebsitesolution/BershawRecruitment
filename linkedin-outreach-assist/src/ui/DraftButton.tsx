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
      text: `${fn}, I'm filling a ${role} that lines up with your ${skill}. If you're open, send over your CV and I'll forward the JD for a quick look.`
    },
    {
      id: "s3",
      label: "Salary-transparency variant",
      text: `Hi ${fn}. I help candidates land roles they actually enjoy. If you're curious, share your CV and I'll reply with JD + salary band up front.`
    }
  ];
}

export default function DraftButton() {
  const [open, setOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  useEffect(() => {
    // Basic heuristic: pre-load suggestions with empty candidate context.
    setSuggestions(generateHypotheticalNotes({ firstName: "there" }));
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

  const refresh = () => {
    // TODO: replace with call to your backend for truly personalised drafts.
    setSuggestions(generateHypotheticalNotes({
      firstName: "there",
      hook: "recent project",
      role: "Senior Backend Engineer",
      skill: "Node.js/TypeScript"
    }));
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
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <button className="li-assist-insert" onClick={refresh}>Refresh</button>
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


