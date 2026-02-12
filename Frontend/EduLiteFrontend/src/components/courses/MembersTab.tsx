import { useState } from "react";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import {
  HiPlus,
  HiCheck,
  HiXMark,
  HiTrash,
  HiUserGroup,
} from "react-icons/hi2";
import * as coursesApi from "../../services/coursesApi";
import type {
  CourseMembership,
  CourseRole,
  CoursePaginatedResponse,
} from "../../types/courses.types";
import HardLoadSelect from "../common/HardLoadSelect";
import ConfirmationModal from "../common/ConfirmationModal";
import InviteMemberModal from "./InviteMemberModal";

interface MembersTabProps {
  courseId: number;
  members: CoursePaginatedResponse<CourseMembership> | null;
  loading: boolean;
  error: string | null;
  isTeacher: boolean;
  refetch: () => void;
}

const ROLE_CHOICES: Array<[string, string]> = [
  ["student", "Student"],
  ["assistant", "Assistant"],
  ["teacher", "Teacher"],
];

const MembersTab: React.FC<MembersTabProps> = ({
  courseId,
  members,
  loading,
  error,
  isTeacher,
  refetch,
}) => {
  const { t } = useTranslation();
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [removeMember, setRemoveMember] = useState<CourseMembership | null>(
    null,
  );
  const [changingRole, setChangingRole] = useState<number | null>(null);

  const getRoleBadgeClasses = (role: CourseRole) => {
    switch (role) {
      case "teacher":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300";
      case "assistant":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300";
      case "student":
        return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300";
    }
  };

  const getStatusBadgeClasses = (status: string) => {
    switch (status) {
      case "enrolled":
        return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300";
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300";
      case "invited":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300";
    }
  };

  const handleInvite = async (userId: number, role: CourseRole) => {
    await coursesApi.inviteCourseMember(courseId, { user: userId, role });
    toast.success(t("course.detail.inviteModal.success"));
    refetch();
  };

  const handleApprove = async (member: CourseMembership) => {
    try {
      await coursesApi.updateCourseMembership(courseId, member.id, {
        status: "enrolled",
      });
      toast.success(t("course.detail.members.approveSuccess"));
      refetch();
    } catch {
      toast.error(t("course.detail.members.approveError"));
    }
  };

  const handleDeny = async (member: CourseMembership) => {
    try {
      await coursesApi.updateCourseMembership(courseId, member.id, {
        status: "denied",
      });
      toast.success(t("course.detail.members.denySuccess"));
      refetch();
    } catch {
      toast.error(t("course.detail.members.denyError"));
    }
  };

  const handleRoleChange = async (
    member: CourseMembership,
    newRole: CourseRole,
  ) => {
    setChangingRole(member.id);
    try {
      await coursesApi.updateCourseMembership(courseId, member.id, {
        role: newRole,
      });
      toast.success(t("course.detail.members.roleChangeSuccess"));
      refetch();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "";
      if (msg.toLowerCase().includes("last teacher")) {
        toast.error(t("course.detail.members.lastTeacherError"));
      } else {
        toast.error(t("course.detail.members.roleChangeError"));
      }
    } finally {
      setChangingRole(null);
    }
  };

  const handleRemove = async () => {
    if (!removeMember) return;
    try {
      await coursesApi.removeCourseMember(courseId, removeMember.id);
      toast.success(t("course.detail.members.removeSuccess"));
      refetch();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "";
      if (msg.toLowerCase().includes("last teacher")) {
        toast.error(t("course.detail.members.lastTeacherError"));
      } else {
        toast.error(t("course.detail.members.removeError"));
      }
    } finally {
      setRemoveMember(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">{error}</p>
        <button
          onClick={refetch}
          className="mt-2 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium cursor-pointer"
        >
          {t("course.detail.retryButton")}
        </button>
      </div>
    );
  }

  const memberList = members?.results ?? [];

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {t("course.detail.members.title")}
        </h3>
        {isTeacher && (
          <button
            onClick={() => setShowInviteModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all text-sm cursor-pointer"
          >
            <HiPlus className="w-4 h-4" />
            {t("course.detail.members.inviteButton")}
          </button>
        )}
      </div>

      {/* Empty state */}
      {memberList.length === 0 ? (
        <div className="text-center py-12">
          <HiUserGroup className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
          <p className="text-gray-500 dark:text-gray-400">
            {t("course.detail.members.emptyState")}
          </p>
        </div>
      ) : (
        <>
          {/* Desktop table */}
          <div className="hidden lg:block overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200/50 dark:border-gray-700/30">
                  <th className="text-start py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                    {t("course.detail.members.username")}
                  </th>
                  <th className="text-start py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                    {t("course.detail.members.role")}
                  </th>
                  <th className="text-start py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                    {t("course.detail.members.status")}
                  </th>
                  {isTeacher && (
                    <th className="text-end py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">
                      {t("course.detail.members.actions")}
                    </th>
                  )}
                </tr>
              </thead>
              <tbody>
                {memberList.map((member) => (
                  <tr
                    key={member.id}
                    className="border-b border-gray-100/50 dark:border-gray-700/20 hover:bg-gray-50/50 dark:hover:bg-gray-700/20 transition-colors"
                  >
                    <td className="py-3 px-4">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {member.user_name}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {isTeacher && member.status === "enrolled" ? (
                        <HardLoadSelect
                          name={`role-${member.id}`}
                          value={member.role}
                          onChange={(e) =>
                            handleRoleChange(
                              member,
                              e.target.value as CourseRole,
                            )
                          }
                          choices={ROLE_CHOICES}
                          showLabel={false}
                          disabled={changingRole === member.id}
                          className="!py-1 !px-2 text-sm max-w-[140px]"
                        />
                      ) : (
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeClasses(member.role)}`}
                        >
                          {t(`course.detail.role.${member.role}`)}
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeClasses(member.status)}`}
                      >
                        {t(
                          `course.detail.members.status${member.status.charAt(0).toUpperCase() + member.status.slice(1)}`,
                        )}
                      </span>
                    </td>
                    {isTeacher && (
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-end gap-2">
                          {member.status === "pending" && (
                            <>
                              <button
                                onClick={() => handleApprove(member)}
                                className="p-1.5 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors cursor-pointer"
                                aria-label={t("course.detail.members.approve")}
                                title={t("course.detail.members.approve")}
                              >
                                <HiCheck className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDeny(member)}
                                className="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors cursor-pointer"
                                aria-label={t("course.detail.members.deny")}
                                title={t("course.detail.members.deny")}
                              >
                                <HiXMark className="w-4 h-4" />
                              </button>
                            </>
                          )}
                          <button
                            onClick={() => setRemoveMember(member)}
                            className="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors cursor-pointer"
                            aria-label={t("course.detail.members.remove")}
                            title={t("course.detail.members.remove")}
                          >
                            <HiTrash className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile cards */}
          <div className="lg:hidden space-y-3">
            {memberList.map((member) => (
              <div
                key={member.id}
                className="p-4 bg-white/60 dark:bg-gray-700/30 rounded-xl border border-gray-200/30 dark:border-gray-600/20"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 dark:text-white">
                    {member.user_name}
                  </span>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeClasses(member.status)}`}
                  >
                    {t(
                      `course.detail.members.status${member.status.charAt(0).toUpperCase() + member.status.slice(1)}`,
                    )}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  {isTeacher && member.status === "enrolled" ? (
                    <HardLoadSelect
                      name={`role-mobile-${member.id}`}
                      value={member.role}
                      onChange={(e) =>
                        handleRoleChange(member, e.target.value as CourseRole)
                      }
                      choices={ROLE_CHOICES}
                      showLabel={false}
                      disabled={changingRole === member.id}
                      className="!py-1 !px-2 text-sm max-w-[140px]"
                    />
                  ) : (
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeClasses(member.role)}`}
                    >
                      {t(`course.detail.role.${member.role}`)}
                    </span>
                  )}

                  {isTeacher && (
                    <div className="flex items-center gap-2">
                      {member.status === "pending" && (
                        <>
                          <button
                            onClick={() => handleApprove(member)}
                            className="p-1.5 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors cursor-pointer"
                            aria-label={t("course.detail.members.approve")}
                          >
                            <HiCheck className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeny(member)}
                            className="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors cursor-pointer"
                            aria-label={t("course.detail.members.deny")}
                          >
                            <HiXMark className="w-4 h-4" />
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => setRemoveMember(member)}
                        className="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors cursor-pointer"
                        aria-label={t("course.detail.members.remove")}
                      >
                        <HiTrash className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Invite Modal */}
      <InviteMemberModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        onSubmit={handleInvite}
      />

      {/* Remove Confirmation */}
      <ConfirmationModal
        isOpen={!!removeMember}
        onClose={() => setRemoveMember(null)}
        onConfirm={handleRemove}
        title={t("course.detail.members.removeConfirmTitle")}
        message={t("course.detail.members.removeConfirmMessage", {
          name: removeMember?.user_name,
        })}
        confirmText={t("course.detail.members.remove")}
        cancelText={t("common.cancel")}
        confirmButtonClass="bg-red-600 hover:bg-red-700 text-white"
      />
    </div>
  );
};

export default MembersTab;
