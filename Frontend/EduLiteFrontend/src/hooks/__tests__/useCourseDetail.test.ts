import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useCourseDetail } from "../useCourseDetail";
import * as coursesApi from "../../services/coursesApi";
import type { CourseDetail } from "../../types/courses.types";

vi.mock("../../services/coursesApi");

describe("useCourseDetail", () => {
  const mockCourse: CourseDetail = {
    id: 1,
    title: "Test Course",
    outline: "Course outline",
    language: "en",
    country: "US",
    subject: "cs",
    visibility: "public",
    start_date: "2024-09-01T08:00:00Z",
    end_date: "2024-12-15T20:00:00Z",
    duration_time: 152640,
    allow_join_requests: true,
    is_active: true,
    member_count: 2,
    user_role: "teacher",
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
    ],
    modules: [
      {
        id: 1,
        course: 1,
        title: "Week 1",
        order: 0,
        course_title: "Test Course",
        content_type: "chat.chatroom",
        object_id: 1,
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
    vi.mocked(coursesApi.getCourseDetail).mockImplementation(
      () => new Promise(() => {}),
    );

    const { result } = renderHook(() => useCourseDetail(1));

    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
    expect(result.current.course).toBeNull();
  });

  it("should fetch course detail on mount", async () => {
    vi.mocked(coursesApi.getCourseDetail).mockResolvedValue(mockCourse);

    const { result } = renderHook(() => useCourseDetail(1));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.course).toEqual(mockCourse);
    expect(result.current.course?.members).toHaveLength(1);
    expect(result.current.course?.modules).toHaveLength(1);
    expect(result.current.course?.user_role).toBe("teacher");
  });

  it("should call getCourseDetail with correct id", async () => {
    vi.mocked(coursesApi.getCourseDetail).mockResolvedValue(mockCourse);

    renderHook(() => useCourseDetail(42));

    await waitFor(() => {
      expect(coursesApi.getCourseDetail).toHaveBeenCalledWith(42);
    });
  });

  it("should handle errors", async () => {
    vi.mocked(coursesApi.getCourseDetail).mockRejectedValue(
      new Error("Not found"),
    );

    const { result } = renderHook(() => useCourseDetail(999));

    await waitFor(() => {
      expect(result.current.error).toBe("Not found");
      expect(result.current.loading).toBe(false);
      expect(result.current.course).toBeNull();
    });
  });

  it("should refetch when refetch is called", async () => {
    vi.mocked(coursesApi.getCourseDetail).mockResolvedValue(mockCourse);

    const { result } = renderHook(() => useCourseDetail(1));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const updatedCourse = { ...mockCourse, title: "Updated Course" };
    vi.mocked(coursesApi.getCourseDetail).mockResolvedValue(updatedCourse);

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.course?.title).toBe("Updated Course");
    });
  });

  it("should reload when id changes", async () => {
    const course2: CourseDetail = {
      ...mockCourse,
      id: 2,
      title: "Course 2",
    };

    vi.mocked(coursesApi.getCourseDetail)
      .mockResolvedValueOnce(mockCourse)
      .mockResolvedValueOnce(course2);

    const { result, rerender } = renderHook(
      ({ id }) => useCourseDetail(id),
      { initialProps: { id: 1 } },
    );

    await waitFor(() => {
      expect(result.current.course?.title).toBe("Test Course");
    });

    rerender({ id: 2 });

    await waitFor(() => {
      expect(result.current.course?.title).toBe("Course 2");
    });
  });
});
