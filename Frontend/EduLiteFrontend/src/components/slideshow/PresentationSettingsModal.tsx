import React from 'react';
import { useTranslation } from 'react-i18next';
import { HiX } from 'react-icons/hi';
import DarkModeToggle from '../DarkModeToggle';

interface PresentationSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  autoHideTopBar: boolean;
  autoHideBottomBar: boolean;
  onAutoHideTopBarChange: (value: boolean) => void;
  onAutoHideBottomBarChange: (value: boolean) => void;
}

/**
 * Settings modal for presentation mode
 * Currently contains dark/light mode toggle
 */
const PresentationSettingsModal: React.FC<PresentationSettingsModalProps> = ({
  isOpen,
  onClose,
  autoHideTopBar,
  autoHideBottomBar,
  onAutoHideTopBarChange,
  onAutoHideBottomBarChange,
}) => {
  const { t } = useTranslation();

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full animate-scale-fade"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {t('slideshow.settings.title')}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors cursor-pointer"
            aria-label={t('common.close')}
          >
            <HiX className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Theme Toggle */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-medium text-gray-900 dark:text-white">
                {t('slideshow.settings.theme')}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {t('slideshow.settings.themeDescription')}
              </p>
            </div>
            <DarkModeToggle />
          </div>

          {/* Auto-hide Top Bar */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-medium text-gray-900 dark:text-white">
                Auto-hide Top Bar
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Hide the top bar until you hover near the top of the screen
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={autoHideTopBar}
                onChange={(e) => onAutoHideTopBarChange(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* Auto-hide Bottom Bar */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-medium text-gray-900 dark:text-white">
                Auto-hide Bottom Bar
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Hide the bottom bar and notes until you hover near the bottom
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={autoHideBottomBar}
                onChange={(e) => onAutoHideBottomBarChange(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PresentationSettingsModal;
