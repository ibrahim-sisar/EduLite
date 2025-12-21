import axios, { AxiosError } from "axios";
import type {
  SlideshowListItem,
  SlideshowDetail,
  SlideshowCreateRequest,
  SlideshowUpdateRequest,
  SlideshowListParams,
  PaginatedResponse,
  VersionConflictError,
  Slide,
  SlideViewOnly,
  SlideshowErrorResponse,
} from "../types/slideshow.types";

const API_BASE_URL = "http://localhost:8000/api";

// Note: Authorization headers are handled automatically by axios interceptors in tokenService.ts

/**
 * List all visible slideshows
 * Returns paginated results with current user's own slideshows + published public ones
 *
 * @param params - Optional filter parameters (visibility, subject, language, country, mine, pagination)
 * @returns Paginated list of slideshows
 */
export const listSlideshows = async (
  params?: SlideshowListParams
): Promise<PaginatedResponse<SlideshowListItem>> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/slideshows/`, {
      params,
      timeout: 10000,
    });
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      throw new Error(
        error.response?.data?.detail || "Failed to fetch slideshows"
      );
    }
    throw error;
  }
};

/**
 * Get only the current user's slideshows
 * Convenience function that sets mine=true
 *
 * @param params - Optional additional filter parameters
 * @returns Paginated list of user's slideshows
 */
export const listMySlideshows = async (
  params?: Omit<SlideshowListParams, "mine">
): Promise<PaginatedResponse<SlideshowListItem>> => {
  return listSlideshows({ ...params, mine: true });
};

/**
 * Get detailed slideshow information
 * Supports progressive loading via initialSlideCount parameter
 *
 * @param id - Slideshow ID
 * @param initialSlideCount - Optional: load only first N slides, get remaining IDs for background fetching
 * @returns Full slideshow detail with slides
 */
export const getSlideshowDetail = async (
  id: number,
  initialSlideCount?: number
): Promise<SlideshowDetail> => {
  try {
    const params = initialSlideCount ? { initial: initialSlideCount } : {};
    const response = await axios.get(`${API_BASE_URL}/slideshows/${id}/`, {
      params,
      timeout: 10000,
    });
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      if (error.response?.status === 404) {
        throw new Error("Slideshow not found");
      }
      if (error.response?.status === 403) {
        throw new Error("You don't have permission to view this slideshow");
      }
      throw new Error(
        error.response?.data?.detail || "Failed to fetch slideshow"
      );
    }
    throw error;
  }
};

/**
 * Get a single slide by ID
 * Used for progressive loading - fetch individual slides in background
 *
 * @param slideshowId - Slideshow ID
 * @param slideId - Slide ID
 * @returns Single slide data
 */
export const getSlide = async (
  slideshowId: number,
  slideId: number
): Promise<Slide | SlideViewOnly> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/slideshows/${slideshowId}/slides/${slideId}/`,
      {
        timeout: 10000,
      }
    );
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      if (error.response?.status === 404) {
        throw new Error("Slide not found");
      }
      throw new Error(error.response?.data?.detail || "Failed to fetch slide");
    }
    throw error;
  }
};

/**
 * Create a new slideshow
 * Can optionally include nested slides in the creation request
 *
 * @param data - Slideshow creation data
 * @returns Created slideshow detail
 */
export const createSlideshow = async (
  data: SlideshowCreateRequest
): Promise<SlideshowDetail> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/slideshows/`, data, {
      timeout: 15000, // Longer timeout for creation with nested slides
    });
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      if (error.response?.status === 400) {
        const errorData = error.response?.data as SlideshowErrorResponse;
        // Handle field-specific errors
        if (errorData?.title) {
          throw new Error(`Title: ${Array.isArray(errorData.title) ? errorData.title[0] : errorData.title}`);
        }
        if (errorData?.slides) {
          throw new Error(`Slides: ${Array.isArray(errorData.slides) ? errorData.slides[0] : errorData.slides}`);
        }
        throw new Error(errorData?.detail || "Invalid slideshow data");
      }
      throw new Error(
        error.response?.data?.detail || "Failed to create slideshow"
      );
    }
    throw error;
  }
};

/**
 * Update an existing slideshow
 * Must include version number - server returns 409 if version conflicts
 *
 * @param id - Slideshow ID
 * @param data - Update data including version number
 * @returns Updated slideshow detail
 * @throws VersionConflictError if version is stale (HTTP 409)
 */
export const updateSlideshow = async (
  id: number,
  data: SlideshowUpdateRequest
): Promise<SlideshowDetail> => {
  try {
    const response = await axios.patch(
      `${API_BASE_URL}/slideshows/${id}/`,
      data,
      {
        timeout: 15000,
      }
    );
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      if (error.response?.status === 409) {
        // Version conflict - throw the conflict details
        const conflictData = error.response?.data as VersionConflictError;
        throw {
          isVersionConflict: true,
          ...conflictData,
        } as VersionConflictError & { isVersionConflict: true };
      }
      if (error.response?.status === 400) {
        const errorData = error.response?.data as SlideshowErrorResponse;
        // Check if this is a version conflict disguised as 400
        if (errorData?.error === "version_conflict") {
          throw {
            isVersionConflict: true,
            ...errorData,
          } as VersionConflictError & { isVersionConflict: true };
        }
        throw new Error(errorData?.detail || "Invalid update data");
      }
      if (error.response?.status === 403) {
        throw new Error("You don't have permission to update this slideshow");
      }
      if (error.response?.status === 404) {
        throw new Error("Slideshow not found");
      }
      throw new Error(
        error.response?.data?.detail || "Failed to update slideshow"
      );
    }
    throw error;
  }
};

/**
 * Delete a slideshow (owner only)
 *
 * @param id - Slideshow ID
 */
export const deleteSlideshow = async (id: number): Promise<void> => {
  try {
    await axios.delete(`${API_BASE_URL}/slideshows/${id}/`, {
      timeout: 10000,
    });
  } catch (error) {
    if (error instanceof AxiosError) {
      if (error.response?.status === 403) {
        throw new Error("You don't have permission to delete this slideshow");
      }
      if (error.response?.status === 404) {
        throw new Error("Slideshow not found");
      }
      throw new Error(
        error.response?.data?.detail || "Failed to delete slideshow"
      );
    }
    throw error;
  }
};

/**
 * Type guard to check if an error is a version conflict
 *
 * @param error - Any error object
 * @returns True if error is a version conflict
 */
export const isVersionConflictError = (
  error: any
): error is VersionConflictError & { isVersionConflict: true } => {
  return (
    error?.isVersionConflict === true ||
    (error?.error === "version_conflict" &&
      typeof error?.server_version === "number" &&
      typeof error?.client_version === "number")
  );
};

/**
 * Extract version conflict details from error
 * Returns null if not a version conflict
 *
 * @param error - Error object from API call
 * @returns Conflict details or null
 */
export const getVersionConflictDetails = (
  error: any
): VersionConflictError | null => {
  if (isVersionConflictError(error)) {
    return {
      error: "version_conflict",
      message: error.message || "Slideshow was modified since you loaded it",
      server_version: error.server_version,
      client_version: error.client_version,
    };
  }
  return null;
};

// Export types for use in components
export type {
  SlideshowListItem,
  SlideshowDetail,
  SlideshowCreateRequest,
  SlideshowUpdateRequest,
  SlideshowListParams,
  PaginatedResponse,
  VersionConflictError,
  Slide,
  SlideViewOnly,
};
