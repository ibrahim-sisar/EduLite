import React from "react";
import { useTranslation } from "react-i18next";
import { HiX } from "react-icons/hi";

interface PresentationHelpModalProps {
  isOpen: boolean;
  onClose: () => void;
  allowFullscreen: boolean;
}

/**
 * Help modal showing keyboard shortcuts for presentation mode
 */
const PresentationHelpModal: React.FC<PresentationHelpModalProps> = ({
  isOpen,
  onClose,
  allowFullscreen,
}) => {
  const { t } = useTranslation();

  if (!isOpen) return null;

  const shortcuts = [
    { key: "→ or Space", action: t("slideshow.viewer.shortcuts.space") },
    {
      key: "← or Backspace",
      action: t("slideshow.viewer.shortcuts.backspace"),
    },
    { key: "Escape", action: t("slideshow.viewer.shortcuts.escape") },
    { key: "Home", action: t("slideshow.viewer.shortcuts.home") },
    { key: "End", action: t("slideshow.viewer.shortcuts.end") },
    { key: "1-9", action: t("slideshow.viewer.shortcuts.numbers") },
  ];

  if (allowFullscreen) {
    shortcuts.push({ key: "F", action: t("slideshow.viewer.shortcuts.f") });
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto animate-scale-fade"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {t("slideshow.help.title")}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors cursor-pointer"
            aria-label={t("common.close")}
          >
            <HiX className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <h3 className="text-base font-medium text-gray-900 dark:text-white mb-4">
            {t("slideshow.help.keyboardShortcuts")}
          </h3>

          <div className="space-y-3">
            {shortcuts.map((shortcut, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
              >
                <span className="text-sm text-gray-900 dark:text-white">
                  {shortcut.action}
                </span>
                <kbd className="px-3 py-1.5 text-xs font-semibold text-gray-800 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded shadow-sm">
                  {shortcut.key}
                </kbd>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/30">
          <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
            {t("slideshow.help.footer")}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PresentationHelpModal;
