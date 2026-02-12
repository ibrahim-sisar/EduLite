// Courses-related TypeScript type definitions

/**
 * Course visibility setting
 * - public: Discoverable and joinable by anyone
 * - restricted: Discoverable but requires approval or invite to join
 * - private: Only visible to members, join by invite only
 */
export type CourseVisibility = "public" | "restricted" | "private";

/**
 * Role a user can have within a course
 */
export type CourseRole = "teacher" | "student" | "assistant";

/**
 * Status of a user's membership in a course
 * - pending: Awaiting teacher approval (restricted courses)
 * - enrolled: Active member
 * - invited: Invited by a teacher, not yet accepted
 */
export type CourseMembershipStatus = "pending" | "enrolled" | "invited";

/**
 * Full course object matching CourseSerializer
 */
export interface Course {
  id: number;
  title: string;
  outline: string | null;
  language: string | null;
  country: string | null;
  subject: string | null;
  visibility: CourseVisibility;
  start_date: string | null; // ISO date string
  end_date: string | null; // ISO date string
  duration_time: number; // Duration in minutes, calculated from start/end
  allow_join_requests: boolean;
  is_active: boolean;
}

/**
 * Lightweight course for list views
 * Matches CourseListSerializer — no nested members/modules
 */
export interface CourseListItem {
  id: number;
  title: string;
  outline: string | null;
  visibility: CourseVisibility;
  subject: string | null;
  language: string | null;
  country: string | null;
  is_active: boolean;
  member_count: number;
  start_date: string | null; // ISO date string
  end_date: string | null; // ISO date string
}

/**
 * Course module matching CourseModuleSerializer
 * content_type is serialized as "app_label.model" string
 */
export interface CourseModule {
  id: number;
  course: number;
  title: string;
  order: number;
  course_title: string;
  content_type: string; // Format: "app_label.model" (e.g. "chat.chatroom")
  object_id: number;
}

/**
 * Course membership matching CourseMembershipSerializer
 */
export interface CourseMembership {
  id: number;
  user: number;
  user_name: string;
  course: number;
  course_title: string;
  role: CourseRole;
  status: CourseMembershipStatus;
}

/**
 * Full course detail with nested members, modules, and user role
 * Matches CourseDetailSerializer
 */
export interface CourseDetail {
  id: number;
  title: string;
  outline: string | null;
  language: string | null;
  country: string | null;
  subject: string | null;
  visibility: CourseVisibility;
  start_date: string | null; // ISO date string
  end_date: string | null; // ISO date string
  duration_time: number;
  allow_join_requests: boolean;
  is_active: boolean;
  member_count: number;
  user_role: CourseRole | null; // null if not a member
  members: CourseMembership[];
  modules: CourseModule[];
}

/**
 * Request payload for creating a course
 */
export interface CourseCreateRequest {
  title: string;
  outline?: string | null;
  language?: string | null;
  country?: string | null;
  subject?: string | null;
  visibility?: CourseVisibility;
  start_date?: string | null;
  end_date?: string | null;
  allow_join_requests?: boolean;
}

/**
 * Request payload for updating a course (partial)
 */
export interface CourseUpdateRequest {
  title?: string;
  outline?: string | null;
  language?: string | null;
  country?: string | null;
  subject?: string | null;
  visibility?: CourseVisibility;
  start_date?: string | null;
  end_date?: string | null;
  allow_join_requests?: boolean;
}

/**
 * Request payload for creating a course module
 */
export interface CourseModuleCreateRequest {
  title?: string;
  order?: number;
  content_type: string; // Format: "app_label.model"
  object_id: number;
}

/**
 * Request payload for updating a course module (partial)
 */
export interface CourseModuleUpdateRequest {
  title?: string;
  order?: number;
  content_type?: string;
  object_id?: number;
}

/**
 * Request payload for inviting a user to a course
 */
export interface CourseMemberInviteRequest {
  user: number;
  role?: CourseRole;
}

/**
 * Request payload for updating a course membership
 */
export interface CourseMembershipUpdateRequest {
  status?: "enrolled" | "denied";
  role?: CourseRole;
}

/**
 * Query parameters for filtering the course list
 */
export interface CourseListParams {
  visibility?: CourseVisibility;
  subject?: string;
  language?: string;
  country?: string;
  mine?: boolean;
  page?: number;
  page_size?: number;
}

/**
 * Paginated response from courses endpoints
 * Includes total_pages, current_page, page_size beyond standard DRF fields
 */
export interface CoursePaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  total_pages: number;
  current_page: number;
  page_size: number;
  results: T[];
}
