import axios from "axios";
import { getSafeErrorMessage } from "../utils/errorUtils";
import type {
  CourseListItem,
  CourseDetail,
  Course,
  CourseCreateRequest,
  CourseUpdateRequest,
  CourseModule,
  CourseModuleCreateRequest,
  CourseModuleUpdateRequest,
  CourseMembership,
  CourseMemberInviteRequest,
  CourseMembershipUpdateRequest,
  CourseListParams,
  CoursePaginatedResponse,
} from "../types/courses.types";

const API_BASE_URL = "http://localhost:8000/api";

// Note: Authorization headers are handled automatically by axios interceptors in tokenService.ts

// --- Course CRUD ---

/**
 * List courses visible to the current user
 * Public courses + courses the user is enrolled in
 *
 * @param params - Optional filter parameters (visibility, subject, language, country, mine, pagination)
 * @returns Paginated list of courses
 */
export const listCourses = async (
  params?: CourseListParams
): Promise<CoursePaginatedResponse<CourseListItem>> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/courses/`, {
      params,
      timeout: 10000,
    });
    return response.data;
  } catch (error) {
    throw new Error(getSafeErrorMessage(error, "Failed to load courses"));
  }
};

/**
 * Get full details of a course including members, modules, and the user's role
 *
 * @param id - Course ID
 * @returns Course detail with nested members and modules
 */
export const getCourseDetail = async (id: number): Promise<CourseDetail> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/courses/${id}/`, {
      timeout: 10000,
    });
    return response.data;
  } catch (error) {
    throw new Error(getSafeErrorMessage(error, "Failed to load course"));
  }
};

/**
 * Create a new course
 * The creator is automatically added as a teacher
 *
 * @param data - Course creation data
 * @returns Created course
 */
export const createCourse = async (
  data: CourseCreateRequest
): Promise<Course> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/courses/`, data, {
      timeout: 15000,
    });
    return response.data;
  } catch (error) {
    throw new Error(getSafeErrorMessage(error, "Failed to create course"));
  }
};

/**
 * Partially update a course
 * Only course teachers can update
 *
 * @param id - Course ID
 * @param data - Partial update data
 * @returns Updated course
 */
export const updateCourse = async (
  id: number,
  data: CourseUpdateRequest
): Promise<Course> => {
  try {
    const response = await axios.patch(
      `${API_BASE_URL}/courses/${id}/`,
      data,
      { timeout: 15000 }
    );
    return response.data;
  } catch (error) {
    throw new Error(getSafeErrorMessage(error, "Failed to update course"));
  }
};

/**
 * Delete a course (teacher only)
 *
 * @param id - Course ID
 */
export const deleteCourse = async (id: number): Promise<void> => {
  try {
    await axios.delete(`${API_BASE_URL}/courses/${id}/`, {
      timeout: 10000,
    });
  } catch (error) {
    throw new Error(getSafeErrorMessage(error, "Failed to delete course"));
  }
};

// --- Enrollment ---

/**
 * Join a course as a student
 * - Public courses: immediately enrolled
 * - Restricted with join requests: pending approval
 * - Private / restricted without join requests: denied (403)
 *
 * @param id - Course ID
 * @returns Created membership
 */
export const enrollInCourse = async (
  id: number
): Promise<CourseMembership> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/courses/${id}/enroll/`,
      {},
      { timeout: 10000 }
    );
    return response.data;
  } catch (error) {
    throw new Error(getSafeErrorMessage(error, "Failed to enroll in course"));
  }
};

/**
 * Leave a course
 * The last teacher cannot leave (returns 409)
 *
 * @param id - Course ID
 */
export const leaveCourse = async (id: number): Promise<void> => {
  try {
    await axios.delete(`${API_BASE_URL}/courses/${id}/enroll/`, {
      timeout: 10000,
    });
  } catch (error) {
    throw new Error(getSafeErrorMessage(error, "Failed to leave course"));
  }
};

// --- Course Modules ---

/**
 * List all modules for a course, ordered by the order field
 * Returns a plain array (not paginated)
 *
 * @param courseId - Course ID
 * @returns Array of course modules
 */
export const listCourseModules = async (
  courseId: number
): Promise<CourseModule[]> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/courses/${courseId}/modules/`,
      { timeout: 10000 }
    );
    return response.data;
  } catch (error) {
    throw new Error(
      getSafeErrorMessage(error, "Failed to load course modules")
    );
  }
};

/**
 * Create a new module in a course (teacher only)
 * The course is set from the URL
 *
 * @param courseId - Course ID
 * @param data - Module creation data
 * @returns Created module
 */
export const createCourseModule = async (
  courseId: number,
  data: CourseModuleCreateRequest
): Promise<CourseModule> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/courses/${courseId}/modules/`,
      data,
      { timeout: 15000 }
    );
    return response.data;
  } catch (error) {
    throw new Error(
      getSafeErrorMessage(error, "Failed to create course module")
    );
  }
};

/**
 * Get details of a single course module
 *
 * @param courseId - Course ID
 * @param moduleId - Module ID
 * @returns Module details
 */
export const getCourseModule = async (
  courseId: number,
  moduleId: number
): Promise<CourseModule> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/courses/${courseId}/modules/${moduleId}/`,
      { timeout: 10000 }
    );
    return response.data;
  } catch (error) {
    throw new Error(
      getSafeErrorMessage(error, "Failed to load course module")
    );
  }
};

/**
 * Partially update a course module (teacher only)
 *
 * @param courseId - Course ID
 * @param moduleId - Module ID
 * @param data - Partial update data
 * @returns Updated module
 */
export const updateCourseModule = async (
  courseId: number,
  moduleId: number,
  data: CourseModuleUpdateRequest
): Promise<CourseModule> => {
  try {
    const response = await axios.patch(
      `${API_BASE_URL}/courses/${courseId}/modules/${moduleId}/`,
      data,
      { timeout: 15000 }
    );
    return response.data;
  } catch (error) {
    throw new Error(
      getSafeErrorMessage(error, "Failed to update course module")
    );
  }
};

/**
 * Delete a course module (teacher only)
 *
 * @param courseId - Course ID
 * @param moduleId - Module ID
 */
export const deleteCourseModule = async (
  courseId: number,
  moduleId: number
): Promise<void> => {
  try {
    await axios.delete(
      `${API_BASE_URL}/courses/${courseId}/modules/${moduleId}/`,
      { timeout: 10000 }
    );
  } catch (error) {
    throw new Error(
      getSafeErrorMessage(error, "Failed to delete course module")
    );
  }
};

// --- Course Members ---

/**
 * List members of a course (paginated)
 *
 * @param courseId - Course ID
 * @returns Paginated list of memberships
 */
export const listCourseMembers = async (
  courseId: number
): Promise<CoursePaginatedResponse<CourseMembership>> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/courses/${courseId}/members/`,
      { timeout: 10000 }
    );
    return response.data;
  } catch (error) {
    throw new Error(
      getSafeErrorMessage(error, "Failed to load course members")
    );
  }
};

/**
 * Invite a user to a course (teacher only)
 * Creates a membership with status "invited"
 *
 * @param courseId - Course ID
 * @param data - Invite data (user ID and optional role)
 * @returns Created membership
 */
export const inviteCourseMember = async (
  courseId: number,
  data: CourseMemberInviteRequest
): Promise<CourseMembership> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/courses/${courseId}/members/`,
      data,
      { timeout: 15000 }
    );
    return response.data;
  } catch (error) {
    throw new Error(
      getSafeErrorMessage(error, "Failed to invite course member")
    );
  }
};

/**
 * Update a course membership (teacher only)
 * Can approve (set status to "enrolled"), deny, or change role
 *
 * @param courseId - Course ID
 * @param membershipId - Membership ID
 * @param data - Update data (status and/or role)
 * @returns Updated membership
 */
export const updateCourseMembership = async (
  courseId: number,
  membershipId: number,
  data: CourseMembershipUpdateRequest
): Promise<CourseMembership> => {
  try {
    const response = await axios.patch(
      `${API_BASE_URL}/courses/${courseId}/members/${membershipId}/`,
      data,
      { timeout: 15000 }
    );
    return response.data;
  } catch (error) {
    throw new Error(
      getSafeErrorMessage(error, "Failed to update course membership")
    );
  }
};

/**
 * Remove a member from a course (teacher only)
 * Cannot remove the last teacher (returns 409)
 *
 * @param courseId - Course ID
 * @param membershipId - Membership ID
 */
export const removeCourseMember = async (
  courseId: number,
  membershipId: number
): Promise<void> => {
  try {
    await axios.delete(
      `${API_BASE_URL}/courses/${courseId}/members/${membershipId}/`,
      { timeout: 10000 }
    );
  } catch (error) {
    throw new Error(
      getSafeErrorMessage(error, "Failed to remove course member")
    );
  }
};
