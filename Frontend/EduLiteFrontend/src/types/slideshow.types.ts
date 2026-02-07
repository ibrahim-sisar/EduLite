// Slideshow-related TypeScript type definitions

/**
 * Visibility options for slideshows
 * - public: Discoverable and viewable by anyone (if published)
 * - unlisted: Not discoverable, but viewable with direct link (if published)
 * - private: Only the owner can view
 */
export type SlideshowVisibility = "public" | "unlisted" | "private";

/**
 * Individual slide within a slideshow
 * Full version with all fields (for owners)
 */
export interface Slide {
  id: number;
  order: number;
  content: string; // Raw markdown (owner only)
  rendered_content: string; // HTML rendered from markdown
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

/**
 * Slide view for non-owners
 * Does not include raw content or speaker notes
 */
export interface SlideViewOnly {
  id: number;
  order: number;
  rendered_content: string; // HTML rendered from markdown
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

/**
 * Lightweight slideshow for list views
 * Does not include nested slides - only metadata
 */
export interface SlideshowListItem {
  id: number;
  title: string;
  description: string | null;
  created_by: number;
  created_by_username: string;
  visibility: SlideshowVisibility;
  language: string | null; // Language code like 'en', 'ar', 'es'
  country: string | null; // Country code like 'US', 'PS', 'AF'
  subject: string | null; // Subject code like 'cs', 'math', 'science'
  is_published: boolean;
  slide_count: number;
  version: number;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

/**
 * Full slideshow detail with nested slides
 * Supports progressive loading via 'initial' parameter
 */
export interface SlideshowDetail {
  id: number;
  title: string;
  description: string | null;
  created_by: number;
  created_by_username: string;
  visibility: SlideshowVisibility;
  language: string | null;
  country: string | null;
  subject: string | null;
  is_published: boolean;
  version: number;
  slide_count: number;
  slides: Slide[] | SlideViewOnly[]; // Depends on ownership
  remaining_slide_ids: number[]; // IDs of slides not yet loaded (for progressive loading)
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

/**
 * Request payload for creating a new slideshow
 * Slides are optional - can be added later
 */
export interface SlideshowCreateRequest {
  title: string;
  description?: string | null;
  visibility?: SlideshowVisibility;
  language?: string | null;
  country?: string | null;
  subject?: string | null;
  is_published?: boolean;
  slides?: SlideCreateData[];
}

/**
 * Slide data for creation (nested within slideshow)
 */
export interface SlideCreateData {
  order?: number; // Auto-assigned if not provided
  content: string; // Raw markdown
}

/**
 * Request payload for updating a slideshow
 * Must include version number for conflict detection
 */
export interface SlideshowUpdateRequest {
  title?: string;
  description?: string | null;
  visibility?: SlideshowVisibility;
  language?: string | null;
  country?: string | null;
  subject?: string | null;
  is_published?: boolean;
  version: number; // Required for conflict detection
  slides?: SlideCreateData[]; // Optional - if provided, replaces all existing slides
}

/**
 * Query parameters for filtering slideshow list
 */
export interface SlideshowListParams {
  mine?: boolean; // If true, only return current user's slideshows
  visibility?: SlideshowVisibility; // Filter by visibility
  subject?: string; // Filter by subject code
  language?: string; // Filter by language code
  country?: string; // Filter by country code
  search?: string; // Search in title/description
  page?: number; // Page number for pagination
  page_size?: number; // Results per page
}

/**
 * Paginated response wrapper (Django REST Framework format)
 */
export interface PaginatedResponse<T> {
  count: number; // Total number of results
  next: string | null; // URL to next page
  previous: string | null; // URL to previous page
  results: T[]; // Array of results
}

/**
 * Version conflict error response (HTTP 409)
 * Returned when client tries to update with stale version
 */
export interface VersionConflictError {
  error: "version_conflict";
  message: string;
  server_version: number;
  client_version: number;
}

/**
 * Generic backend error response structure
 */
export interface SlideshowErrorResponse {
  detail?: string;
  error?: string;
  message?: string;
  // Field-specific errors
  title?: string | string[];
  description?: string | string[];
  visibility?: string | string[];
  slides?: string | string[];
  non_field_errors?: string | string[];
}
