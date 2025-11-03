// Utility to find and write to the currently focused LinkedIn composer.
// Works for connection notes, InMail, and messaging threads that use contenteditable divs.

const LOG_PREFIX = "[LinkedIn Outreach Assist]";
const LOG_ENABLED = true; // Set to false in production to disable logging

function log(message: string, data?: unknown): void {
  if (!LOG_ENABLED) return;
  
  // Log to console (content scripts can't easily send messages to background)
  // In production, consider using chrome.storage.local to persist logs
  console.log(`${LOG_PREFIX} ${message}`, data || "");
  
  // Optional: Store logs in chrome.storage for debugging
  if (typeof chrome !== "undefined" && chrome.storage) {
    chrome.storage.local.get(["loa_logs"], (result) => {
      const logs = result.loa_logs || [];
      logs.push({
        timestamp: new Date().toISOString(),
        message: `${LOG_PREFIX} ${message}`,
        data
      });
      // Keep only last 100 logs
      const recentLogs = logs.slice(-100);
      chrome.storage.local.set({ loa_logs: recentLogs }).catch(() => {
        // Ignore storage errors
      });
    });
  }
}

export function getActiveComposer(): HTMLElement | null {
  // Prioritise focused contenteditable
  const focused = document.activeElement as HTMLElement | null;
  if (focused && focused.getAttribute("contenteditable") === "true") {
    log("Found composer via focused element", { tagName: focused.tagName });
    return focused;
  }

  // Common LinkedIn composer selectors (may evolve; we keep it resilient)
  const selectors = [
    'div[contenteditable="true"][role="textbox"]',
    "div.msg-form__contenteditable",
    "div.share-box__contenteditable",
    "div.editor-content[contenteditable='true']",
    // Additional fallback selectors
    "div[contenteditable='true'][data-placeholder]",
    "div.ql-editor[contenteditable='true']", // Quill editor
    "div[aria-label*='message'][contenteditable='true']"
  ];

  for (const sel of selectors) {
    const el = document.querySelector(sel) as HTMLElement | null;
    if (el && el.isConnected && el.offsetParent !== null) {
      log("Found composer via selector", { selector: sel, tagName: el.tagName });
      return el;
    }
  }

  log("Composer not found - tried all selectors", {
    selectors,
    activeElement: focused?.tagName,
    url: window.location.href
  });
  return null;
}

export function insertTextIntoComposer(el: HTMLElement, text: string): boolean {
  // Prefer inserting plain text to avoid LinkedIn sanitisation issues.
  // NOTE: This function is ONLY called from user-initiated button clicks (DraftButton.tsx)
  // to comply with LinkedIn's policies.
  
  try {
    el.focus();

    // Try execCommand for broad support on contenteditable
    const success = document.execCommand("insertText", false, text);
    if (!success) {
      // Fallback: mutate textContent (may overwrite existing; so append)
      const current = el.textContent || "";
      el.textContent = current ? current + "\n" + text : text;
      log("Used fallback textContent insertion", { 
        execCommandFailed: true,
        textLength: text.length 
      });
    } else {
      log("Successfully inserted text via execCommand", { textLength: text.length });
    }

    // Dispatch input event so LinkedIn picks up changes
    el.dispatchEvent(new InputEvent("input", { bubbles: true }));
    return true;
  } catch (error) {
    log("Error inserting text into composer", { error: String(error) });
    return false;
  }
}


