import { useState, useEffect, useCallback } from "react";
import { getCourseDetail } from "../services/coursesApi";
import type { CourseDetail } from "../types/courses.types";

export interface UseCourseDetailReturn {
  course: CourseDetail | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Hook for fetching full course details including members, modules, and user role.
 * Fetches on mount and whenever the id changes.
 * Aborts in-flight requests on unmount.
 *
 * @param id - Course ID
 */
export function useCourseDetail(id: number): UseCourseDetailReturn {
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fetchKey, setFetchKey] = useState(0);

  const refetch = useCallback(() => {
    setFetchKey((prev) => prev + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    const fetchCourse = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getCourseDetail(id);
        if (!cancelled) {
          setCourse(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load course"
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchCourse();

    return () => {
      cancelled = true;
    };
  }, [id, fetchKey]);

  return { course, loading, error, refetch };
}
