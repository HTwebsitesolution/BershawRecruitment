// Utility to find and write to the currently focused LinkedIn composer.
// Works for connection notes, InMail, and messaging threads that use contenteditable divs.

export function getActiveComposer(): HTMLElement | null {
  // Prioritise focused contenteditable
  const focused = document.activeElement as HTMLElement | null;
  if (focused && focused.getAttribute("contenteditable") === "true") return focused;

  // Common LinkedIn composer selectors (may evolve; we keep it resilient)
  const selectors = [
    'div[contenteditable="true"][role="textbox"]',
    "div.msg-form__contenteditable",
    "div.share-box__contenteditable",
    "div.editor-content[contenteditable='true']"
  ];

  for (const sel of selectors) {
    const el = document.querySelector(sel) as HTMLElement | null;
    if (el) return el;
  }
  return null;
}

export function insertTextIntoComposer(el: HTMLElement, text: string) {
  // Prefer inserting plain text to avoid LinkedIn sanitisation issues.
  el.focus();

  // Try execCommand for broad support on contenteditable
  const success = document.execCommand("insertText", false, text);
  if (!success) {
    // Fallback: mutate textContent (may overwrite existing; so append)
    const current = el.textContent || "";
    el.textContent = current ? current + "\n" + text : text;
  }

  // Dispatch input event so LinkedIn picks up changes
  el.dispatchEvent(new InputEvent("input", { bubbles: true }));
}


