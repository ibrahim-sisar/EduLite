import React, { useState } from "react";
import { FaExclamationTriangle, FaTimes } from "react-icons/fa";

interface DeleteAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isDeleting: boolean;
}

const DeleteAccountModal: React.FC<DeleteAccountModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  isDeleting
}) => {
  const [confirmText, setConfirmText] = useState("");

  if (!isOpen) return null;

  const canDelete = confirmText === "DELETE";

  const handleConfirm = () => {
    if (canDelete) {
      onConfirm();
    }
  };

  const handleClose = () => {
    setConfirmText("");
    onClose();
  };

  return (
    <>
      {/* Modal with backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-opacity"
        onClick={handleClose}
      >
        <div
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6 relative animate-scale-up"
          onClick={(e) => e.stopPropagation()}>
          {/* Close button */}
          <button
            onClick={handleClose}
            disabled={isDeleting}
            className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition disabled:opacity-50"
          >
            <FaTimes className="text-xl" />
          </button>

          {/* Warning icon and title */}
          <div className="flex items-center gap-3 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
              <FaExclamationTriangle className="text-red-600 dark:text-red-400 text-xl" />
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
              Delete Account
            </h2>
          </div>

          {/* Warning message */}
          <div className="space-y-4 mb-6">
            <p className="text-gray-700 dark:text-gray-300">
              This action is <span className="font-semibold text-red-600 dark:text-red-400">permanent and irreversible</span>.
            </p>

            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-sm text-red-800 dark:text-red-300 font-medium mb-2">
                Deleting your account will:
              </p>
              <ul className="text-sm text-red-700 dark:text-red-400 space-y-1 ml-4">
                <li>• Remove all your personal data</li>
                <li>• Delete all your notes and files</li>
                <li>• Remove you from all courses</li>
                <li>• Cancel any active subscriptions</li>
                <li>• This action cannot be undone</li>
              </ul>
            </div>

            <p className="text-gray-700 dark:text-gray-300">
              To confirm, please type <span className="font-mono font-semibold text-red-600 dark:text-red-400">DELETE</span> below:
            </p>
          </div>

          {/* Confirmation input */}
          <input
            type="text"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder="Type DELETE to confirm"
            disabled={isDeleting}
            className="w-full px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
          />

          {/* Action buttons */}
          <div className="flex gap-3 mt-6">
            <button
              onClick={handleClose}
              disabled={isDeleting}
              className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-lg transition disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={!canDelete || isDeleting}
              className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isDeleting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Deleting...</span>
                </>
              ) : (
                "Delete Account"
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default DeleteAccountModal;
