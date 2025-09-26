import React, { useEffect, useRef } from 'react';
import { HiExclamationTriangle } from 'react-icons/hi2';

interface UnsavedChangesModalProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  message?: string;
  confirmText?: string;
  cancelText?: string;
}

/**
 * Reusable modal component for warning about unsaved changes
 * Follows the established glass-morphism design system
 */
const UnsavedChangesModal: React.FC<UnsavedChangesModalProps> = ({
  isOpen,
  onConfirm,
  onCancel,
  message = "You have unsaved changes. Are you sure you want to leave?",
  confirmText = "Leave Without Saving",
  cancelText = "Stay on Page"
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const cancelButtonRef = useRef<HTMLButtonElement>(null);

  // Focus management
  useEffect(() => {
    if (isOpen && cancelButtonRef.current) {
      cancelButtonRef.current.focus();
    }
  }, [isOpen]);

  // Keyboard handling
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        onCancel();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCancel]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onCancel();
        }
      }}
    >
      {/* Backdrop with blur */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />

      {/* Modal */}
      <div
        ref={modalRef}
        className="relative w-full max-w-md transform transition-all duration-300 ease-out scale-100 opacity-100"
      >
        <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-900/20 dark:shadow-black/40 p-8">
          {/* Icon and Title */}
          <div className="flex flex-col items-center text-center mb-6">
            <div className="w-16 h-16 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center mb-4">
              <HiExclamationTriangle className="text-3xl text-amber-600 dark:text-amber-400" />
            </div>

            <h2 className="text-2xl font-light text-gray-900 dark:text-white mb-2 tracking-tight">
              Unsaved Changes
            </h2>

            <p className="text-gray-600 dark:text-gray-300 font-light leading-relaxed">
              {message}
            </p>
          </div>

          {/* Buttons */}
          <div className="flex flex-col-reverse sm:flex-row gap-3">
            {/* Stay Button (Primary Action) */}
            <button
              ref={cancelButtonRef}
              onClick={onCancel}
              className="cursor-pointer flex-1 px-6 py-3 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white font-medium rounded-2xl transition-all duration-200 hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50 focus:scale-[1.02]"
            >
              {cancelText}
            </button>

            {/* Leave Button (Destructive Action) */}
            <button
              onClick={onConfirm}
              className="cursor-pointer flex-1 px-6 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-2xl transition-all duration-200 hover:scale-[1.02] hover:border-red-300 dark:hover:border-red-600 hover:text-red-600 dark:hover:text-red-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 dark:focus:ring-red-400/50 focus:scale-[1.02]"
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnsavedChangesModal;
