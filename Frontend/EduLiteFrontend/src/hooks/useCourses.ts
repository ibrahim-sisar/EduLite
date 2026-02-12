import { useState, useEffect, useCallback } from "react";
import { listCourses } from "../services/coursesApi";
import type {
  CourseListItem,
  CourseListParams,
  CoursePaginatedResponse,
} from "../types/courses.types";

export interface UseCoursesReturn {
  courses: CoursePaginatedResponse<CourseListItem> | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Hook for fetching a paginated list of courses.
 * Fetches on mount and whenever params change.
 * Aborts in-flight requests on unmount.
 *
 * @param params - Optional filter/pagination parameters
 */
export function useCourses(params?: CourseListParams): UseCoursesReturn {
  const [courses, setCourses] =
    useState<CoursePaginatedResponse<CourseListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fetchKey, setFetchKey] = useState(0);

  const refetch = useCallback(() => {
    setFetchKey((prev) => prev + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    const fetchCourses = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await listCourses(params);
        if (!cancelled) {
          setCourses(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load courses"
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchCourses();

    return () => {
      cancelled = true;
    };
  }, [
    params?.visibility,
    params?.subject,
    params?.language,
    params?.country,
    params?.mine,
    params?.page,
    params?.page_size,
    fetchKey,
  ]);

  return { courses, loading, error, refetch };
}
