import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useCourseModules } from "../useCourseModules";
import * as coursesApi from "../../services/coursesApi";
import type { CourseModule } from "../../types/courses.types";

vi.mock("../../services/coursesApi");

describe("useCourseModules", () => {
  const mockModules: CourseModule[] = [
    {
      id: 1,
      course: 1,
      title: "Week 1: Introduction",
      order: 0,
      course_title: "Test Course",
      content_type: "chat.chatroom",
      object_id: 1,
    },
    {
      id: 2,
      course: 1,
      title: "Week 2: Fundamentals",
      order: 1,
      course_title: "Test Course",
      content_type: "chat.chatroom",
      object_id: 2,
    },
  ];

  beforeEach(() => {
    vi.resetAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should start in loading state", () => {
    vi.mocked(coursesApi.listCourseModules).mockImplementation(
      () => new Promise(() => {}),
    );

    const { result } = renderHook(() => useCourseModules(1));

    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
    expect(result.current.modules).toBeNull();
  });

  it("should fetch modules on mount", async () => {
    vi.mocked(coursesApi.listCourseModules).mockResolvedValue(mockModules);

    const { result } = renderHook(() => useCourseModules(1));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.modules).toEqual(mockModules);
    expect(result.current.modules).toHaveLength(2);
    expect(result.current.modules?.[0].title).toBe("Week 1: Introduction");
  });

  it("should call listCourseModules with correct courseId", async () => {
    vi.mocked(coursesApi.listCourseModules).mockResolvedValue(mockModules);

    renderHook(() => useCourseModules(42));

    await waitFor(() => {
      expect(coursesApi.listCourseModules).toHaveBeenCalledWith(42);
    });
  });

  it("should handle errors", async () => {
    vi.mocked(coursesApi.listCourseModules).mockRejectedValue(
      new Error("Not a course member"),
    );

    const { result } = renderHook(() => useCourseModules(1));

    await waitFor(() => {
      expect(result.current.error).toBe("Not a course member");
      expect(result.current.loading).toBe(false);
      expect(result.current.modules).toBeNull();
    });
  });

  it("should handle non-Error rejections", async () => {
    vi.mocked(coursesApi.listCourseModules).mockRejectedValue("String error");

    const { result } = renderHook(() => useCourseModules(1));

    await waitFor(() => {
      expect(result.current.error).toBe("Failed to load course modules");
    });
  });

  it("should refetch when refetch is called", async () => {
    vi.mocked(coursesApi.listCourseModules).mockResolvedValue(mockModules);

    const { result } = renderHook(() => useCourseModules(1));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const updatedModules = [
      ...mockModules,
      {
        id: 3,
        course: 1,
        title: "Week 3: Advanced",
        order: 2,
        course_title: "Test Course",
        content_type: "chat.chatroom",
        object_id: 3,
      },
    ];
    vi.mocked(coursesApi.listCourseModules).mockResolvedValue(updatedModules);

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.modules).toHaveLength(3);
    });
  });

  it("should reload when courseId changes", async () => {
    const course2Modules: CourseModule[] = [
      {
        id: 10,
        course: 2,
        title: "Module A",
        order: 0,
        course_title: "Course 2",
        content_type: "chat.chatroom",
        object_id: 5,
      },
    ];

    vi.mocked(coursesApi.listCourseModules)
      .mockResolvedValueOnce(mockModules)
      .mockResolvedValueOnce(course2Modules);

    const { result, rerender } = renderHook(
      ({ courseId }) => useCourseModules(courseId),
      { initialProps: { courseId: 1 } },
    );

    await waitFor(() => {
      expect(result.current.modules).toHaveLength(2);
    });

    rerender({ courseId: 2 });

    await waitFor(() => {
      expect(result.current.modules).toHaveLength(1);
      expect(result.current.modules?.[0].title).toBe("Module A");
    });
  });
});
