import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import "./spellbook.css";
import App from "./App.jsx";
import "./i18n";

// Apply saved theme immediately on page load
const savedTheme = localStorage.getItem("theme");
if (savedTheme === "dark") {
  document.documentElement.classList.add("dark");
} else if (savedTheme === "light") {
  document.documentElement.classList.remove("dark");
} else {
  // No saved preference, use system preference
  if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.documentElement.classList.add("dark");
  }
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
