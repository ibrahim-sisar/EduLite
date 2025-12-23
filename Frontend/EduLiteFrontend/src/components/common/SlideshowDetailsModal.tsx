import React from 'react';
import { useTranslation } from 'react-i18next';
import { HiX, HiPencil } from 'react-icons/hi';

interface SlideshowDetailsModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback when modal should close */
  onClose: () => void;
  /** Slideshow data to display */
  slideshow: {
    id: number;
    title: string;
    subject: string;
    language: string;
    visibility: string;
    slide_count: number;
    created_at: string;
    updated_at: string;
  };
  /** Callback when "Open in Editor" is clicked */
  onOpenEditor: () => void;
}

/**
 * Modal component to display detailed information about a slideshow.
 * Includes an "Open in Editor" button for quick access.
 */
const SlideshowDetailsModal: React.FC<SlideshowDetailsModalProps> = ({
  isOpen,
  onClose,
  slideshow,
  onOpenEditor,
}) => {
  const { t } = useTranslation();

  if (!isOpen) return null;

  // Format dates for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto animate-scale-fade"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {t('slideshow.details.title')}
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
        <div className="p-6 space-y-4">
          {/* Slideshow Title */}
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('slideshow.details.slideshowTitle')}
            </dt>
            <dd className="mt-1 text-base text-gray-900 dark:text-white">
              {slideshow.title}
            </dd>
          </div>

          {/* Subject */}
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('slideshow.details.subject')}
            </dt>
            <dd className="mt-1 text-base text-gray-900 dark:text-white">
              {slideshow.subject}
            </dd>
          </div>

          {/* Language */}
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('slideshow.details.language')}
            </dt>
            <dd className="mt-1 text-base text-gray-900 dark:text-white">
              {slideshow.language}
            </dd>
          </div>

          {/* Visibility */}
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('slideshow.details.visibility')}
            </dt>
            <dd className="mt-1 text-base text-gray-900 dark:text-white capitalize">
              {slideshow.visibility}
            </dd>
          </div>

          {/* Slide Count */}
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('slideshow.details.slideCount')}
            </dt>
            <dd className="mt-1 text-base text-gray-900 dark:text-white">
              {slideshow.slide_count}
            </dd>
          </div>

          {/* Created Date */}
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('slideshow.details.created')}
            </dt>
            <dd className="mt-1 text-base text-gray-900 dark:text-white">
              {formatDate(slideshow.created_at)}
            </dd>
          </div>

          {/* Updated Date */}
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('slideshow.details.updated')}
            </dt>
            <dd className="mt-1 text-base text-gray-900 dark:text-white">
              {formatDate(slideshow.updated_at)}
            </dd>
          </div>
        </div>

        {/* Footer with Actions */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="px-5 py-2.5 rounded-lg font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors duration-200 focus:outline-none cursor-pointer"
          >
            {t('common.close')}
          </button>
          <button
            onClick={() => {
              onOpenEditor();
              onClose();
            }}
            className="px-5 py-2.5 rounded-lg font-medium text-white bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 inline-flex items-center gap-2 cursor-pointer"
          >
            <HiPencil className="text-lg" />
            {t('slideshow.details.openEditor')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SlideshowDetailsModal;
