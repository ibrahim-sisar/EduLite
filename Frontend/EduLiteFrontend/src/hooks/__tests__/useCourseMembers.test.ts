import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useCourseMembers } from "../useCourseMembers";
import * as coursesApi from "../../services/coursesApi";
import type { CoursePaginatedResponse, CourseMembership } from "../../types/courses.types";

vi.mock("../../services/coursesApi");

describe("useCourseMembers", () => {
  const mockResponse: CoursePaginatedResponse<CourseMembership> = {
    count: 2,
    next: null,
    previous: null,
    total_pages: 1,
    current_page: 1,
    page_size: 20,
    results: [
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
  };

  beforeEach(() => {
    vi.resetAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should start in loading state", () => {
    vi.mocked(coursesApi.listCourseMembers).mockImplementation(
      () => new Promise(() => {}),
    );

    const { result } = renderHook(() => useCourseMembers(1));

    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
    expect(result.current.members).toBeNull();
  });

  it("should fetch members on mount", async () => {
    vi.mocked(coursesApi.listCourseMembers).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useCourseMembers(1));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.members).toEqual(mockResponse);
    expect(result.current.members?.results).toHaveLength(2);
  });

  it("should call listCourseMembers with correct courseId", async () => {
    vi.mocked(coursesApi.listCourseMembers).mockResolvedValue(mockResponse);

    renderHook(() => useCourseMembers(42));

    await waitFor(() => {
      expect(coursesApi.listCourseMembers).toHaveBeenCalledWith(42);
    });
  });

  it("should handle errors", async () => {
    vi.mocked(coursesApi.listCourseMembers).mockRejectedValue(
      new Error("Permission denied"),
    );

    const { result } = renderHook(() => useCourseMembers(1));

    await waitFor(() => {
      expect(result.current.error).toBe("Permission denied");
      expect(result.current.loading).toBe(false);
      expect(result.current.members).toBeNull();
    });
  });

  it("should refetch when refetch is called", async () => {
    vi.mocked(coursesApi.listCourseMembers).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useCourseMembers(1));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const updatedResponse = {
      ...mockResponse,
      count: 3,
      results: [
        ...mockResponse.results,
        {
          id: 3,
          user: 3,
          user_name: "student2",
          course: 1,
          course_title: "Test Course",
          role: "student" as const,
          status: "enrolled" as const,
        },
      ],
    };
    vi.mocked(coursesApi.listCourseMembers).mockResolvedValue(updatedResponse);

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.members?.results).toHaveLength(3);
    });
  });

  it("should reload when courseId changes", async () => {
    const course2Response: CoursePaginatedResponse<CourseMembership> = {
      ...mockResponse,
      count: 1,
      results: [
        {
          id: 5,
          user: 10,
          user_name: "other_teacher",
          course: 2,
          course_title: "Course 2",
          role: "teacher",
          status: "enrolled",
        },
      ],
    };

    vi.mocked(coursesApi.listCourseMembers)
      .mockResolvedValueOnce(mockResponse)
      .mockResolvedValueOnce(course2Response);

    const { result, rerender } = renderHook(
      ({ courseId }) => useCourseMembers(courseId),
      { initialProps: { courseId: 1 } },
    );

    await waitFor(() => {
      expect(result.current.members?.results).toHaveLength(2);
    });

    rerender({ courseId: 2 });

    await waitFor(() => {
      expect(result.current.members?.results).toHaveLength(1);
      expect(result.current.members?.results[0].user_name).toBe("other_teacher");
    });
  });
});
