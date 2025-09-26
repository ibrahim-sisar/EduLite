import { useTranslation } from "react-i18next";
import { HiOutlineTranslate } from "react-icons/hi";

export default function LanguageSwitcher({ onClick } = {}) {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === "en" ? "ar" : "en";
    i18n.changeLanguage(newLang);
    document.dir = newLang === "ar" ? "rtl" : "ltr";
  };

  // If onClick is provided from parent, use it; otherwise use internal handler
  const handleClick = onClick || toggleLanguage;

  return (
    <button
      onClick={handleClick}
      className="p-1.5 sm:p-2 rounded-full hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200 cursor-pointer group"
      aria-label="Toggle language"
    >
      <HiOutlineTranslate className="text-lg text-gray-600 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-200" />
    </button>
  );
}
