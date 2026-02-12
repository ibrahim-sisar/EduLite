import { useState, useEffect, useCallback } from "react";
import { listCourseModules } from "../services/coursesApi";
import type { CourseModule } from "../types/courses.types";

export interface UseCourseModulesReturn {
  modules: CourseModule[] | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Hook for fetching course modules.
 * Returns a plain array (modules endpoint is not paginated).
 * Fetches on mount and whenever courseId changes.
 * Aborts in-flight requests on unmount.
 *
 * @param courseId - Course ID
 */
export function useCourseModules(courseId: number): UseCourseModulesReturn {
  const [modules, setModules] = useState<CourseModule[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fetchKey, setFetchKey] = useState(0);

  const refetch = useCallback(() => {
    setFetchKey((prev) => prev + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    const fetchModules = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await listCourseModules(courseId);
        if (!cancelled) {
          setModules(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load course modules"
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchModules();

    return () => {
      cancelled = true;
    };
  }, [courseId, fetchKey]);

  return { modules, loading, error, refetch };
}
