import React from "react";
import { createRoot } from "react-dom/client";
import DraftButton from "./ui/DraftButton";
// Vite inline import gives raw CSS as string so we can inject into Shadow DOM
// @ts-ignore - vite query param typing
import panelCss from "./ui/panel.css?inline";

// Mount into a Shadow DOM to avoid CSS collisions with LinkedIn
const mount = () => {
  if (document.getElementById("li-assist-shadow-host")) return;

  const host = document.createElement("div");
  host.id = "li-assist-shadow-host";
  document.documentElement.appendChild(host);

  const shadow = host.attachShadow({ mode: "open" });
  const app = document.createElement("div");
  shadow.appendChild(app);

  // Inject CSS (panel.css is imported by DraftButton but we also add base resets if needed)
  const style = document.createElement("style");
  style.textContent = panelCss;
  shadow.appendChild(style);

  const root = createRoot(app);
  root.render(<DraftButton />);
};

const readyStates = ["interactive", "complete"];
if (readyStates.includes(document.readyState)) {
  mount();
} else {
  document.addEventListener("DOMContentLoaded", mount);
}


