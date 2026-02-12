import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useCourses } from "../useCourses";
import * as coursesApi from "../../services/coursesApi";
import type { CoursePaginatedResponse, CourseListItem } from "../../types/courses.types";

vi.mock("../../services/coursesApi");

describe("useCourses", () => {
  const mockResponse: CoursePaginatedResponse<CourseListItem> = {
    count: 2,
    next: null,
    previous: null,
    total_pages: 1,
    current_page: 1,
    page_size: 20,
    results: [
      {
        id: 1,
        title: "Course 1",
        outline: "Outline 1",
        visibility: "public",
        subject: "cs",
        language: "en",
        country: "US",
        is_active: true,
        member_count: 5,
        start_date: "2024-09-01T08:00:00Z",
        end_date: "2024-12-15T20:00:00Z",
      },
      {
        id: 2,
        title: "Course 2",
        outline: null,
        visibility: "private",
        subject: null,
        language: null,
        country: null,
        is_active: true,
        member_count: 3,
        start_date: null,
        end_date: null,
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
    vi.mocked(coursesApi.listCourses).mockImplementation(
      () => new Promise(() => {}),
    );

    const { result } = renderHook(() => useCourses());

    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
    expect(result.current.courses).toBeNull();
  });

  it("should fetch courses on mount", async () => {
    vi.mocked(coursesApi.listCourses).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useCourses());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.courses).toEqual(mockResponse);
    expect(result.current.courses?.results).toHaveLength(2);
    expect(result.current.error).toBeNull();
  });

  it("should pass params to listCourses", async () => {
    vi.mocked(coursesApi.listCourses).mockResolvedValue(mockResponse);

    const params = { visibility: "public" as const, subject: "math" };
    renderHook(() => useCourses(params));

    await waitFor(() => {
      expect(coursesApi.listCourses).toHaveBeenCalledWith(params);
    });
  });

  it("should handle errors", async () => {
    vi.mocked(coursesApi.listCourses).mockRejectedValue(
      new Error("Network error"),
    );

    const { result } = renderHook(() => useCourses());

    await waitFor(() => {
      expect(result.current.error).toBe("Network error");
      expect(result.current.loading).toBe(false);
      expect(result.current.courses).toBeNull();
    });
  });

  it("should handle non-Error rejections", async () => {
    vi.mocked(coursesApi.listCourses).mockRejectedValue("String error");

    const { result } = renderHook(() => useCourses());

    await waitFor(() => {
      expect(result.current.error).toBe("Failed to load courses");
    });
  });

  it("should refetch when refetch is called", async () => {
    vi.mocked(coursesApi.listCourses).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useCourses());

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
          title: "Course 3",
          outline: null,
          visibility: "public" as const,
          subject: null,
          language: null,
          country: null,
          is_active: true,
          member_count: 1,
          start_date: null,
          end_date: null,
        },
      ],
    };
    vi.mocked(coursesApi.listCourses).mockResolvedValue(updatedResponse);

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.courses?.results).toHaveLength(3);
    });
  });
});
