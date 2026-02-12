import { useState, useEffect, useCallback } from "react";
import { listCourseMembers } from "../services/coursesApi";
import type {
  CourseMembership,
  CoursePaginatedResponse,
} from "../types/courses.types";

export interface UseCourseMembersReturn {
  members: CoursePaginatedResponse<CourseMembership> | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Hook for fetching a paginated list of course members.
 * Fetches on mount and whenever courseId changes.
 * Aborts in-flight requests on unmount.
 *
 * @param courseId - Course ID
 */
export function useCourseMembers(courseId: number): UseCourseMembersReturn {
  const [members, setMembers] =
    useState<CoursePaginatedResponse<CourseMembership> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fetchKey, setFetchKey] = useState(0);

  const refetch = useCallback(() => {
    setFetchKey((prev) => prev + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    const fetchMembers = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await listCourseMembers(courseId);
        if (!cancelled) {
          setMembers(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load course members"
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchMembers();

    return () => {
      cancelled = true;
    };
  }, [courseId, fetchKey]);

  return { members, loading, error, refetch };
}
