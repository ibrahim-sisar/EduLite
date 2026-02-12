import { useState, useMemo, useCallback } from "react";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import * as coursesApi from "../services/coursesApi";
import type {
  CourseDetail,
  CourseRole,
  CourseMembershipStatus,
} from "../types/courses.types";

export interface UseEnrollmentReturn {
  /** User's membership status, or null if not enrolled */
  status: CourseMembershipStatus | null;
  /** User's role in the course, or null if not enrolled */
  role: CourseRole | null;
  /** Whether an enrollment action is in progress */
  isLoading: boolean;
  /** Whether the current user is the only teacher in the course */
  isLastTeacher: boolean;
  /** Join the course (public = instant, restricted = pending) */
  enroll: () => Promise<void>;
  /** Leave the course */
  leave: () => Promise<void>;
  /** Cancel a pending join request */
  cancelRequest: () => Promise<void>;
}

/**
 * Hook that encapsulates enrollment state and actions for a course.
 *
 * Derives status/role from the course detail response and provides
 * action methods that call the API and trigger a refetch on success.
 */
export function useEnrollment(
  courseId: number,
  course: CourseDetail | null,
  refetch: () => void
): UseEnrollmentReturn {
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);

  const status = course?.user_status ?? null;
  const role = course?.user_role ?? null;

  const isLastTeacher = useMemo(() => {
    if (!course || role !== "teacher") return false;
    const enrolledTeachers = course.members.filter(
      (m) => m.role === "teacher" && m.status === "enrolled"
    );
    return enrolledTeachers.length <= 1;
  }, [course, role]);

  const enroll = useCallback(async () => {
    setIsLoading(true);
    try {
      const membership = await coursesApi.enrollInCourse(courseId);
      if (membership.status === "pending") {
        toast.success(t("course.enrollment.joinPending"));
      } else {
        toast.success(t("course.enrollment.joinSuccess"));
      }
      refetch();
    } catch {
      toast.error(t("course.enrollment.networkError"));
    } finally {
      setIsLoading(false);
    }
  }, [courseId, refetch, t]);

  const leave = useCallback(async () => {
    setIsLoading(true);
    try {
      await coursesApi.leaveCourse(courseId);
      toast.success(t("course.enrollment.leaveSuccess"));
      refetch();
    } catch {
      toast.error(t("course.enrollment.networkError"));
    } finally {
      setIsLoading(false);
    }
  }, [courseId, refetch, t]);

  const cancelRequest = useCallback(async () => {
    setIsLoading(true);
    try {
      await coursesApi.leaveCourse(courseId);
      toast.success(t("course.enrollment.cancelRequestSuccess"));
      refetch();
    } catch {
      toast.error(t("course.enrollment.networkError"));
    } finally {
      setIsLoading(false);
    }
  }, [courseId, refetch, t]);

  return {
    status,
    role,
    isLoading,
    isLastTeacher,
    enroll,
    leave,
    cancelRequest,
  };
}
