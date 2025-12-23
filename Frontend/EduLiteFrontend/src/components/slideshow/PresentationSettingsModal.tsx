import React from 'react';
import { useTranslation } from 'react-i18next';
import { HiX } from 'react-icons/hi';
import DarkModeToggle from '../DarkModeToggle';

interface PresentationSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Settings modal for presentation mode
 * Currently contains dark/light mode toggle
 */
const PresentationSettingsModal: React.FC<PresentationSettingsModalProps> = ({
  isOpen,
  onClose,
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
        <div className="p-6">
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
        </div>
      </div>
    </div>
  );
};

export default PresentationSettingsModal;
