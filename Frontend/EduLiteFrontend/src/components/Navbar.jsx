import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { HiBell, HiMenuAlt2 } from "react-icons/hi";
import { FaUserCircle } from "react-icons/fa";
import DarkModeToggle from "./DarkModeToggle";
import LanguageSwitcher from "./LanguageSwitcher";
import logo from "../assets/EdTech_Logo.webp";
import SidebarMenu from "./Sidebar";

export default function Navbar({ isLoggedIn, onLogout }) {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const isActiveRoute = (path) =>
    path === "/" ? location.pathname === "/" : location.pathname.startsWith(path);

  return (
    <>
      <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/20 dark:border-gray-700/20 fixed top-0 left-0 w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between py-4 lg:grid lg:grid-cols-3">
            {/* Left Section - Logo + Name */}
            <div className="flex items-center gap-3 lg:justify-start">
              <div className="relative group">
                <img
                  src={logo}
                  alt="EduLite Logo"
                  className="h-8 w-8 sm:h-9 sm:w-9 rounded-lg"
                />
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-300"></div>
              </div>
              <Link
                to="/"
                className="text-lg sm:text-xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent hover:from-blue-700 hover:to-purple-700 transition-all duration-300"
              >
                EduLite
              </Link>
            </div>

            {/* Center Section - Links (Desktop only) */}
            <div className="hidden lg:flex items-center justify-center gap-2">
              {[
                { to: "/", label: t("nav.home") },
                { to: "/about", label: t("nav.about") },
                { to: "/conversations", label: t("nav.conversations") },
                { to: "/chapters", label: t("nav.chapters") },
              ].map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`relative px-4 py-2 rounded-full font-medium transition-all duration-300 ${
                    isActiveRoute(link.to)
                      ? "text-white bg-blue-600 shadow-lg shadow-blue-600/25"
                      : "text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>

            {/* Right Section - Actions */}
            <div className="flex items-center gap-1 sm:gap-2 lg:justify-end">
              <div className="hidden lg:flex items-center gap-1">
                <Link
                  to="/notifications"
                  title={t("notifications")}
                  className="relative p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200 group"
                >
                  <HiBell className="text-xl text-gray-600 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                </Link>
                {isLoggedIn ? (
                  <button
                    onClick={onLogout}
                    className="px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-all duration-200"
                  >
                    {t("nav.logout")}
                  </button>
                ) : (
                  <Link
                    to="/login"
                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-all duration-200"
                  >
                    {t("nav.login")}
                  </Link>
                )}
              </div>

              <div className="flex items-center gap-0.5 sm:gap-1 bg-gray-100/50 dark:bg-gray-800/50 rounded-full p-0.5 sm:p-1 backdrop-blur-sm">
                <div className="p-1.5 sm:p-2 rounded-full hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200">
                  <LanguageSwitcher />
                </div>
                <div className="p-1.5 sm:p-2 rounded-full hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200">
                  <DarkModeToggle />
                </div>
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-1.5 sm:p-2 rounded-full hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200 group"
                  title={t("menu")}
                >
                  <HiMenuAlt2 className="text-lg sm:text-xl text-gray-700 dark:text-gray-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>


      <SidebarMenu open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
    </>
  );
}
