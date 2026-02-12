import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useEnrollment } from "../useEnrollment";
import * as coursesApi from "../../services/coursesApi";
import type { CourseDetail, CourseMembership } from "../../types/courses.types";

vi.mock("../../services/coursesApi");
vi.mock("react-hot-toast", () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

const baseCourse: CourseDetail = {
  id: 1,
  title: "Test Course",
  outline: null,
  language: null,
  country: null,
  subject: null,
  visibility: "public",
  start_date: null,
  end_date: null,
  duration_time: 0,
  allow_join_requests: true,
  is_active: true,
  member_count: 2,
  user_role: "teacher",
  user_status: "enrolled",
  members: [
    {
      id: 1,
      user: 1,
      user_name: "teacher1",
      course: 1,
      course_title: "Test Course",
      role: "teacher",
      status: "enrolled",
    },
    {
      id: 2,
      user: 2,
      user_name: "student1",
      course: 1,
      course_title: "Test Course",
      role: "student",
      status: "enrolled",
    },
  ],
  modules: [],
};

describe("useEnrollment", () => {
  const mockRefetch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("status and role derivation", () => {
    it("returns null status and role when course is null", () => {
      const { result } = renderHook(() => useEnrollment(1, null, mockRefetch));
      expect(result.current.status).toBeNull();
      expect(result.current.role).toBeNull();
    });

    it("returns enrolled status for enrolled teacher", () => {
      const { result } = renderHook(() =>
        useEnrollment(1, baseCourse, mockRefetch),
      );
      expect(result.current.status).toBe("enrolled");
      expect(result.current.role).toBe("teacher");
    });

    it("returns pending status for pending student", () => {
      const course: CourseDetail = {
        ...baseCourse,
        user_role: "student",
        user_status: "pending",
      };
      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );
      expect(result.current.status).toBe("pending");
      expect(result.current.role).toBe("student");
    });

    it("returns invited status for invited user", () => {
      const course: CourseDetail = {
        ...baseCourse,
        user_role: "student",
        user_status: "invited",
      };
      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );
      expect(result.current.status).toBe("invited");
      expect(result.current.role).toBe("student");
    });

    it("returns null status for non-member", () => {
      const course: CourseDetail = {
        ...baseCourse,
        user_role: null,
        user_status: null,
      };
      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );
      expect(result.current.status).toBeNull();
      expect(result.current.role).toBeNull();
    });
  });

  describe("isLastTeacher", () => {
    it("returns true when user is the only enrolled teacher", () => {
      const course: CourseDetail = {
        ...baseCourse,
        members: [{ ...baseCourse.members[0] }, { ...baseCourse.members[1] }],
      };
      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );
      expect(result.current.isLastTeacher).toBe(true);
    });

    it("returns false when there are multiple enrolled teachers", () => {
      const course: CourseDetail = {
        ...baseCourse,
        members: [
          { ...baseCourse.members[0] },
          {
            id: 3,
            user: 3,
            user_name: "teacher2",
            course: 1,
            course_title: "Test Course",
            role: "teacher",
            status: "enrolled",
          },
        ],
      };
      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );
      expect(result.current.isLastTeacher).toBe(false);
    });

    it("returns false for non-teacher roles", () => {
      const course: CourseDetail = {
        ...baseCourse,
        user_role: "student",
        user_status: "enrolled",
      };
      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );
      expect(result.current.isLastTeacher).toBe(false);
    });
  });

  describe("enroll", () => {
    it("calls enrollInCourse and refetch on success", async () => {
      const course: CourseDetail = {
        ...baseCourse,
        user_role: null,
        user_status: null,
      };
      vi.mocked(coursesApi.enrollInCourse).mockResolvedValue({
        id: 3,
        user: 5,
        user_name: "newuser",
        course: 1,
        course_title: "Test Course",
        role: "student",
        status: "enrolled",
      });

      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );

      await act(async () => {
        await result.current.enroll();
      });

      expect(coursesApi.enrollInCourse).toHaveBeenCalledWith(1);
      expect(mockRefetch).toHaveBeenCalled();
    });

    it("shows error toast on failure", async () => {
      const toast = await import("react-hot-toast");
      const course: CourseDetail = {
        ...baseCourse,
        user_role: null,
        user_status: null,
      };
      vi.mocked(coursesApi.enrollInCourse).mockRejectedValue(
        new Error("Failed"),
      );

      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );

      await act(async () => {
        await result.current.enroll();
      });

      expect(toast.default.error).toHaveBeenCalled();
      expect(mockRefetch).not.toHaveBeenCalled();
    });
  });

  describe("leave", () => {
    it("calls leaveCourse and refetch on success", async () => {
      vi.mocked(coursesApi.leaveCourse).mockResolvedValue();

      const { result } = renderHook(() =>
        useEnrollment(1, baseCourse, mockRefetch),
      );

      await act(async () => {
        await result.current.leave();
      });

      expect(coursesApi.leaveCourse).toHaveBeenCalledWith(1);
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  describe("cancelRequest", () => {
    it("calls leaveCourse and refetch on success", async () => {
      const course: CourseDetail = {
        ...baseCourse,
        user_role: "student",
        user_status: "pending",
      };
      vi.mocked(coursesApi.leaveCourse).mockResolvedValue();

      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );

      await act(async () => {
        await result.current.cancelRequest();
      });

      expect(coursesApi.leaveCourse).toHaveBeenCalledWith(1);
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  describe("loading state", () => {
    it("sets isLoading during enroll", async () => {
      const course: CourseDetail = {
        ...baseCourse,
        user_role: null,
        user_status: null,
      };
      let resolveEnroll: (
        value: CourseMembership | PromiseLike<CourseMembership>,
      ) => void;
      vi.mocked(coursesApi.enrollInCourse).mockImplementation(
        () =>
          new Promise((resolve) => {
            resolveEnroll = resolve;
          }),
      );

      const { result } = renderHook(() =>
        useEnrollment(1, course, mockRefetch),
      );

      expect(result.current.isLoading).toBe(false);

      let enrollPromise: Promise<void>;
      act(() => {
        enrollPromise = result.current.enroll();
      });

      expect(result.current.isLoading).toBe(true);

      await act(async () => {
        resolveEnroll!({
          id: 3,
          user: 5,
          user_name: "newuser",
          course: 1,
          course_title: "Test Course",
          role: "student",
          status: "enrolled",
        });
        await enrollPromise!;
      });

      expect(result.current.isLoading).toBe(false);
    });
  });
});
