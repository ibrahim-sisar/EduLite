import { useState, useEffect } from "react";

/**
 * Hook that tracks whether dark mode is active by observing
 * the "dark" class on the document element.
 */
export function useDarkMode(): boolean {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const check = () =>
      setIsDarkMode(document.documentElement.classList.contains("dark"));
    check();
    const observer = new MutationObserver(check);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });
    return () => observer.disconnect();
  }, []);

  return isDarkMode;
}
