import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";
import { HiUserPlus } from "react-icons/hi2";
import type { CourseRole } from "../../types/courses.types";
import type { UserSearchResult } from "../../types/users.types";
import UserSearchInput from "../common/UserSearchInput";
import HardLoadSelect from "../common/HardLoadSelect";

interface InviteMemberModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (userId: number, role: CourseRole) => Promise<void>;
}

const ROLE_CHOICES: Array<[string, string]> = [
  ["student", "Student"],
  ["assistant", "Assistant"],
  ["teacher", "Teacher"],
];

const InviteMemberModal: React.FC<InviteMemberModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const { t } = useTranslation();
  const [selectedUser, setSelectedUser] = useState<UserSearchResult | null>(
    null,
  );
  const [selectedRole, setSelectedRole] = useState<CourseRole>("student");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setSelectedUser(null);
      setSelectedRole("student");
      setIsSubmitting(false);
      setSubmitError(null);
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    if (!selectedUser) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await onSubmit(selectedUser.id, selectedRole);
      onClose();
    } catch (err) {
      setSubmitError(
        err instanceof Error
          ? err.message
          : t("course.detail.inviteModal.error"),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBackdropKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape" && !isSubmitting) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onKeyDown={handleBackdropKeyDown}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={!isSubmitting ? onClose : undefined}
      />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-sm sm:max-w-md p-6 sm:p-8 border border-gray-200/50 dark:border-gray-700/30 max-h-[90vh] overflow-y-auto">
        {/* Close button */}
        <button
          type="button"
          onClick={onClose}
          disabled={isSubmitting}
          className="absolute top-4 end-4 p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 cursor-pointer"
          aria-label={t("common.close")}
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Header */}
        <div className="text-center mb-6">
          <HiUserPlus className="w-12 h-12 text-blue-400 dark:text-blue-500 mx-auto mb-3 opacity-70" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {t("course.detail.inviteModal.title")}
          </h2>
        </div>

        {/* User search */}
        <div className="space-y-4">
          <UserSearchInput
            onSelect={setSelectedUser}
            selectedUser={selectedUser}
            onClear={() => setSelectedUser(null)}
            label={t("course.detail.inviteModal.searchLabel")}
            placeholder={t("course.detail.inviteModal.searchPlaceholder")}
            disabled={isSubmitting}
          />

          {/* Role selector */}
          <HardLoadSelect
            label={t("course.detail.inviteModal.roleLabel")}
            name="invite-role"
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value as CourseRole)}
            choices={ROLE_CHOICES}
            disabled={isSubmitting}
          />

          {/* Submit error */}
          {submitError && (
            <p className="text-sm text-red-500 text-center">{submitError}</p>
          )}

          {/* Action buttons */}
          <div className="flex flex-col-reverse sm:flex-row gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 px-4 py-2.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-medium transition-colors disabled:opacity-50 cursor-pointer"
            >
              {t("course.detail.inviteModal.cancel")}
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!selectedUser || isSubmitting}
              className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2"
            >
              {isSubmitting && (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              )}
              {isSubmitting
                ? t("course.detail.inviteModal.sending")
                : t("course.detail.inviteModal.submitButton")}
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
};

export default InviteMemberModal;
