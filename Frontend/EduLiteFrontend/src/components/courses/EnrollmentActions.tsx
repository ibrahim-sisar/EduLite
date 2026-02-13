import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  HiArrowRightOnRectangle,
  HiArrowLeftOnRectangle,
  HiXMark,
  HiClock,
  HiEnvelope,
  HiLockClosed,
} from "react-icons/hi2";
import ConfirmationModal from "../common/ConfirmationModal";
import type { CourseDetail } from "../../types/courses.types";
import type { UseEnrollmentReturn } from "../../hooks/useEnrollment";

interface EnrollmentActionsProps {
  course: CourseDetail;
  enrollment: UseEnrollmentReturn;
  className?: string;
}

/**
 * Renders the correct enrollment UI based on the user's membership state.
 * Handles: not enrolled, pending, invited, enrolled (student/teacher).
 */
export default function EnrollmentActions({
  course,
  enrollment,
  className = "",
}: EnrollmentActionsProps) {
  const { t } = useTranslation();
  const [showLeaveModal, setShowLeaveModal] = useState(false);

  const {
    status,
    role,
    isLoading,
    isLastTeacher,
    enroll,
    leave,
    cancelRequest,
  } = enrollment;

  const handleLeaveConfirm = async () => {
    await leave();
    setShowLeaveModal(false);
  };

  // --- Not enrolled ---
  if (status === null) {
    // Public course: "Join Course" button
    if (course.visibility === "public") {
      return (
        <div className={className}>
          <button
            onClick={enroll}
            disabled={isLoading}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer w-full sm:w-auto"
          >
            <HiArrowRightOnRectangle className="w-5 h-5" />
            {isLoading
              ? t("course.enrollment.joining")
              : t("course.enrollment.joinButton")}
          </button>
        </div>
      );
    }

    // Restricted + allow join requests: "Request to Join" button
    if (course.visibility === "restricted" && course.allow_join_requests) {
      return (
        <div className={className}>
          <button
            onClick={enroll}
            disabled={isLoading}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer w-full sm:w-auto"
          >
            <HiArrowRightOnRectangle className="w-5 h-5" />
            {isLoading
              ? t("course.enrollment.joining")
              : t("course.enrollment.requestJoinButton")}
          </button>
        </div>
      );
    }

    // Restricted + no join requests: "Enrollment Closed"
    if (course.visibility === "restricted") {
      return (
        <div className={className}>
          <span className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 rounded-lg font-medium">
            <HiLockClosed className="w-5 h-5" />
            {t("course.enrollment.enrollmentClosed")}
          </span>
        </div>
      );
    }

    // Private: no UI (user shouldn't see private courses they're not in)
    return null;
  }

  // --- Pending ---
  if (status === "pending") {
    return (
      <div className={className}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/40 rounded-lg">
          <div className="flex items-center gap-2 flex-1">
            <HiClock className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 animate-pulse" />
            <p className="text-amber-800 dark:text-amber-200 text-sm font-medium">
              {t("course.enrollment.pendingBanner")}
            </p>
          </div>
          <button
            onClick={cancelRequest}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm border border-amber-300 dark:border-amber-700 text-amber-700 dark:text-amber-300 hover:bg-amber-100 dark:hover:bg-amber-900/40 rounded-lg font-medium transition-colors disabled:opacity-50 cursor-pointer"
          >
            <HiXMark className="w-4 h-4" />
            {t("course.enrollment.cancelRequest")}
          </button>
        </div>
      </div>
    );
  }

  // --- Invited ---
  if (status === "invited") {
    return (
      <div className={className}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800/40 rounded-lg">
          <div className="flex items-center gap-2 flex-1">
            <HiEnvelope className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
            <p className="text-blue-800 dark:text-blue-200 text-sm font-medium">
              {t("course.enrollment.invitedBanner", {
                role: role || "student",
              })}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              disabled
              title={t("course.enrollment.inviteComingSoon")}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-green-600 text-white rounded-lg font-medium opacity-50 cursor-not-allowed"
            >
              {t("course.enrollment.acceptInvite")}
            </button>
            <button
              disabled
              title={t("course.enrollment.inviteComingSoon")}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 rounded-lg font-medium opacity-50 cursor-not-allowed"
            >
              {t("course.enrollment.declineInvite")}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- Enrolled ---
  if (status === "enrolled") {
    // Teacher who is the last teacher: disabled leave
    if (role === "teacher" && isLastTeacher) {
      return (
        <div className={className}>
          <button
            disabled
            title={t("course.enrollment.lastTeacherTooltip")}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-400 dark:text-gray-500 rounded-lg font-medium opacity-50 cursor-not-allowed w-full sm:w-auto"
          >
            <HiArrowLeftOnRectangle className="w-5 h-5" />
            {t("course.enrollment.leaveButton")}
          </button>
        </div>
      );
    }

    // Non-teacher or teacher with other teachers: leave button
    if (role !== "teacher") {
      return (
        <div className={className}>
          <button
            onClick={() => setShowLeaveModal(true)}
            disabled={isLoading}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 hover:border-red-500 dark:hover:border-red-400 text-gray-700 dark:text-gray-200 hover:text-red-600 dark:hover:text-red-400 rounded-lg font-medium transition-all disabled:opacity-50 cursor-pointer w-full sm:w-auto"
          >
            <HiArrowLeftOnRectangle className="w-5 h-5" />
            {t("course.enrollment.leaveButton")}
          </button>

          <ConfirmationModal
            isOpen={showLeaveModal}
            onClose={() => setShowLeaveModal(false)}
            onConfirm={handleLeaveConfirm}
            title={t("course.enrollment.leaveConfirmTitle")}
            message={t("course.enrollment.leaveConfirmMessage", {
              title: course.title,
            })}
            confirmText={t("course.enrollment.leaveButton")}
            cancelText={t("common.cancel")}
            confirmButtonClass="bg-red-600 hover:bg-red-700 text-white"
          />
        </div>
      );
    }
  }

  return null;
}
