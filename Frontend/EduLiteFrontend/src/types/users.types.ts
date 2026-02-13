/**
 * A single user result from the search API.
 * Mirrors backend UserSearchSerializer.
 * Fields may be absent due to privacy settings.
 */
export interface UserSearchResult {
  id: number;
  username: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  profile_id: number;
}

/**
 * Query parameters for the user search endpoint.
 */
export interface UserSearchParams {
  q: string;
  page?: number;
  page_size?: number;
}

/**
 * Paginated response from the user search endpoint.
 * Uses standard DRF PageNumberPagination (count, next, previous, results).
 */
export interface UserSearchPaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: UserSearchResult[];
}
