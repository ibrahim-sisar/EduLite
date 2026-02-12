import { useState } from "react";
import { useTranslation } from "react-i18next";
import HardLoadSelect from "../common/HardLoadSelect";
import type { CourseRole } from "../../types/courses.types";

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
  const [userId, setUserId] = useState("");
  const [role, setRole] = useState<CourseRole>("student");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const parsed = parseInt(userId, 10);
    if (isNaN(parsed) || parsed <= 0) {
      setError("Please enter a valid user ID");
      return;
    }

    setSending(true);
    setError("");
    try {
      await onSubmit(parsed, role);
      setUserId("");
      setRole("student");
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to invite");
    } finally {
      setSending(false);
    }
  };

  const handleClose = () => {
    if (!sending) {
      setUserId("");
      setRole("student");
      setError("");
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md p-6 border border-gray-200/50 dark:border-gray-700/30">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {t("course.detail.inviteModal.title")}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* User ID */}
          <div>
            <label
              htmlFor="invite-user-id"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              {t("course.detail.inviteModal.userIdLabel")}
            </label>
            <input
              id="invite-user-id"
              type="number"
              min="1"
              value={userId}
              onChange={(e) => {
                setUserId(e.target.value);
                setError("");
              }}
              placeholder={t("course.detail.inviteModal.userIdPlaceholder")}
              disabled={sending}
              className="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm text-gray-700 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 disabled:opacity-60"
            />
          </div>

          {/* Role */}
          <HardLoadSelect
            label={t("course.detail.inviteModal.roleLabel")}
            name="invite-role"
            value={role}
            onChange={(e) => setRole(e.target.value as CourseRole)}
            choices={ROLE_CHOICES}
            disabled={sending}
          />

          {/* Error */}
          {error && <p className="text-red-500 text-sm">{error}</p>}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              disabled={sending}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50 cursor-pointer"
            >
              {t("common.cancel")}
            </button>
            <button
              type="submit"
              disabled={sending || !userId}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
            >
              {sending
                ? t("course.detail.inviteModal.sending")
                : t("course.detail.inviteModal.submitButton")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InviteMemberModal;
