import { useEffect, useState } from "react";
import { HiOutlineMoon, HiOutlineSun } from "react-icons/hi";

export default function DarkModeToggle({ onClick } = {}) {
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage first, then fall back to system preference
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      return savedTheme === "dark";
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDark]);

  const toggleDarkMode = () => setIsDark(!isDark);

  // If onClick is provided from parent, use it; otherwise use internal handler
  const handleClick = onClick || toggleDarkMode;

  return (
    <button
      onClick={handleClick}
      className="p-1.5 sm:p-2 rounded-full hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200 cursor-pointer group"
      aria-label="Toggle dark mode"
    >
      {isDark ? (
        <HiOutlineSun className="text-lg text-gray-600 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-200" />
      ) : (
        <HiOutlineMoon className="text-lg text-gray-600 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-200" />
      )}
    </button>
  );
}
