import { describe, it, expect, beforeEach, afterEach } from "vitest";
import axios from "axios";
import MockAdapter from "axios-mock-adapter";
import {
  listCourses,
  getCourseDetail,
  createCourse,
  updateCourse,
  deleteCourse,
  enrollInCourse,
  leaveCourse,
  listCourseModules,
  createCourseModule,
  getCourseModule,
  updateCourseModule,
  deleteCourseModule,
  listCourseMembers,
  inviteCourseMember,
  updateCourseMembership,
  removeCourseMember,
} from "../coursesApi";
import type {
  CourseDetail,
  CourseMembership,
  CourseModule,
} from "../../types/courses.types";

describe("coursesApi", () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  // --- Course CRUD ---

  describe("listCourses", () => {
    it("should fetch paginated courses", async () => {
      const mockResponse = {
        count: 2,
        next: null,
        previous: null,
        total_pages: 1,
        current_page: 1,
        page_size: 20,
        results: [
          { id: 1, title: "Course 1", member_count: 5 },
          { id: 2, title: "Course 2", member_count: 3 },
        ],
      };

      mock.onGet("http://localhost:8000/api/courses/").reply(200, mockResponse);

      const result = await listCourses();
      expect(result).toEqual(mockResponse);
      expect(result.results).toHaveLength(2);
    });

    it("should apply filter parameters", async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        total_pages: 1,
        current_page: 1,
        page_size: 20,
        results: [{ id: 1, title: "Public Course", visibility: "public" }],
      };

      mock
        .onGet("http://localhost:8000/api/courses/", {
          params: { visibility: "public", subject: "math" },
        })
        .reply(200, mockResponse);

      const result = await listCourses({
        visibility: "public",
        subject: "math",
      });
      expect(result.results).toHaveLength(1);
    });

    it("should filter user's own courses with mine param", async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        total_pages: 1,
        current_page: 1,
        page_size: 20,
        results: [{ id: 1, title: "My Course" }],
      };

      mock
        .onGet("http://localhost:8000/api/courses/", {
          params: { mine: true },
        })
        .reply(200, mockResponse);

      const result = await listCourses({ mine: true });
      expect(result.results).toHaveLength(1);
    });

    it("should handle errors", async () => {
      mock
        .onGet("http://localhost:8000/api/courses/")
        .reply(500, { detail: "Server error" });

      await expect(listCourses()).rejects.toThrow();
    });
  });

  describe("getCourseDetail", () => {
    it("should fetch course with members and modules", async () => {
      const mockCourse: CourseDetail = {
        id: 1,
        title: "Test Course",
        outline: "Course outline",
        language: "en",
        country: "US",
        subject: "cs",
        visibility: "public",
        start_date: "2024-09-01T08:00:00Z",
        end_date: "2024-12-15T20:00:00Z",
        duration_time: 152640,
        allow_join_requests: true,
        is_active: true,
        member_count: 2,
        user_role: "teacher",
        user_status: "enrolled",
        members: [
          {
            id: 1,
            user: 1,
            user_name: "teacher1",
            course: 1,
            course_title: "Test Course",
            role: "teacher",
            status: "enrolled",
          },
        ],
        modules: [
          {
            id: 1,
            course: 1,
            title: "Week 1",
            order: 0,
            course_title: "Test Course",
            content_type: "chat.chatroom",
            object_id: 1,
          },
        ],
      };

      mock.onGet("http://localhost:8000/api/courses/1/").reply(200, mockCourse);

      const result = await getCourseDetail(1);
      expect(result).toEqual(mockCourse);
      expect(result.members).toHaveLength(1);
      expect(result.modules).toHaveLength(1);
      expect(result.user_role).toBe("teacher");
    });

    it("should handle 404", async () => {
      mock
        .onGet("http://localhost:8000/api/courses/999/")
        .reply(404, { detail: "Not found" });

      await expect(getCourseDetail(999)).rejects.toThrow();
    });
  });

  describe("createCourse", () => {
    it("should create a new course", async () => {
      const createData = {
        title: "New Course",
        outline: "Course outline",
        visibility: "public" as const,
        language: "en",
      };

      const mockResponse = {
        id: 1,
        ...createData,
        country: null,
        subject: null,
        start_date: null,
        end_date: null,
        duration_time: 0,
        allow_join_requests: true,
        is_active: true,
      };

      mock
        .onPost("http://localhost:8000/api/courses/")
        .reply(201, mockResponse);

      const result = await createCourse(createData);
      expect(result.id).toBe(1);
      expect(result.title).toBe("New Course");
    });

    it("should handle validation errors", async () => {
      mock.onPost("http://localhost:8000/api/courses/").reply(400, {
        title: ["This field may not be blank."],
      });

      await expect(createCourse({ title: "" })).rejects.toThrow();
    });
  });

  describe("updateCourse", () => {
    it("should partially update a course", async () => {
      const mockResponse = {
        id: 1,
        title: "Updated Title",
        outline: null,
        language: null,
        country: null,
        subject: null,
        visibility: "public",
        start_date: null,
        end_date: null,
        duration_time: 0,
        allow_join_requests: true,
        is_active: true,
      };

      mock
        .onPatch("http://localhost:8000/api/courses/1/")
        .reply(200, mockResponse);

      const result = await updateCourse(1, { title: "Updated Title" });
      expect(result.title).toBe("Updated Title");
    });

    it("should handle 403 for non-teachers", async () => {
      mock
        .onPatch("http://localhost:8000/api/courses/1/")
        .reply(403, { detail: "Only teachers can update courses." });

      await expect(updateCourse(1, { title: "Updated" })).rejects.toThrow();
    });
  });

  describe("deleteCourse", () => {
    it("should delete a course", async () => {
      mock.onDelete("http://localhost:8000/api/courses/1/").reply(204);

      await expect(deleteCourse(1)).resolves.not.toThrow();
    });

    it("should handle errors", async () => {
      mock
        .onDelete("http://localhost:8000/api/courses/1/")
        .reply(403, { detail: "Permission denied" });

      await expect(deleteCourse(1)).rejects.toThrow();
    });
  });

  // --- Enrollment ---

  describe("enrollInCourse", () => {
    it("should enroll in a public course", async () => {
      const mockMembership: CourseMembership = {
        id: 1,
        user: 2,
        user_name: "student1",
        course: 1,
        course_title: "Test Course",
        role: "student",
        status: "enrolled",
      };

      mock
        .onPost("http://localhost:8000/api/courses/1/enroll/")
        .reply(201, mockMembership);

      const result = await enrollInCourse(1);
      expect(result.status).toBe("enrolled");
      expect(result.role).toBe("student");
    });

    it("should return pending for restricted courses", async () => {
      const mockMembership: CourseMembership = {
        id: 1,
        user: 2,
        user_name: "student1",
        course: 1,
        course_title: "Restricted Course",
        role: "student",
        status: "pending",
      };

      mock
        .onPost("http://localhost:8000/api/courses/1/enroll/")
        .reply(201, mockMembership);

      const result = await enrollInCourse(1);
      expect(result.status).toBe("pending");
    });

    it("should handle 409 when already enrolled", async () => {
      mock
        .onPost("http://localhost:8000/api/courses/1/enroll/")
        .reply(409, { detail: "You are already a member of this course." });

      await expect(enrollInCourse(1)).rejects.toThrow();
    });
  });

  describe("leaveCourse", () => {
    it("should leave a course", async () => {
      mock.onDelete("http://localhost:8000/api/courses/1/enroll/").reply(204);

      await expect(leaveCourse(1)).resolves.not.toThrow();
    });

    it("should handle 409 when last teacher", async () => {
      mock.onDelete("http://localhost:8000/api/courses/1/enroll/").reply(409, {
        detail: "Cannot leave as the last teacher in the course.",
      });

      await expect(leaveCourse(1)).rejects.toThrow();
    });
  });

  // --- Course Modules ---

  describe("listCourseModules", () => {
    it("should fetch modules as a plain array", async () => {
      const mockModules: CourseModule[] = [
        {
          id: 1,
          course: 1,
          title: "Week 1",
          order: 0,
          course_title: "Test Course",
          content_type: "chat.chatroom",
          object_id: 1,
        },
        {
          id: 2,
          course: 1,
          title: "Week 2",
          order: 1,
          course_title: "Test Course",
          content_type: "chat.chatroom",
          object_id: 2,
        },
      ];

      mock
        .onGet("http://localhost:8000/api/courses/1/modules/")
        .reply(200, mockModules);

      const result = await listCourseModules(1);
      expect(result).toHaveLength(2);
      expect(result[0].title).toBe("Week 1");
    });

    it("should handle errors", async () => {
      mock
        .onGet("http://localhost:8000/api/courses/1/modules/")
        .reply(403, { detail: "Not a course member." });

      await expect(listCourseModules(1)).rejects.toThrow();
    });
  });

  describe("createCourseModule", () => {
    it("should create a module", async () => {
      const createData = {
        title: "Week 1",
        order: 0,
        content_type: "chat.chatroom",
        object_id: 1,
      };

      const mockResponse: CourseModule = {
        id: 1,
        course: 1,
        course_title: "Test Course",
        ...createData,
      };

      mock
        .onPost("http://localhost:8000/api/courses/1/modules/")
        .reply(201, mockResponse);

      const result = await createCourseModule(1, createData);
      expect(result.id).toBe(1);
      expect(result.title).toBe("Week 1");
    });
  });

  describe("getCourseModule", () => {
    it("should fetch a single module", async () => {
      const mockModule: CourseModule = {
        id: 1,
        course: 1,
        title: "Week 1",
        order: 0,
        course_title: "Test Course",
        content_type: "chat.chatroom",
        object_id: 1,
      };

      mock
        .onGet("http://localhost:8000/api/courses/1/modules/1/")
        .reply(200, mockModule);

      const result = await getCourseModule(1, 1);
      expect(result).toEqual(mockModule);
    });
  });

  describe("updateCourseModule", () => {
    it("should partially update a module", async () => {
      const mockResponse: CourseModule = {
        id: 1,
        course: 1,
        title: "Updated Week 1",
        order: 0,
        course_title: "Test Course",
        content_type: "chat.chatroom",
        object_id: 1,
      };

      mock
        .onPatch("http://localhost:8000/api/courses/1/modules/1/")
        .reply(200, mockResponse);

      const result = await updateCourseModule(1, 1, {
        title: "Updated Week 1",
      });
      expect(result.title).toBe("Updated Week 1");
    });
  });

  describe("deleteCourseModule", () => {
    it("should delete a module", async () => {
      mock
        .onDelete("http://localhost:8000/api/courses/1/modules/1/")
        .reply(204);

      await expect(deleteCourseModule(1, 1)).resolves.not.toThrow();
    });
  });

  // --- Course Members ---

  describe("listCourseMembers", () => {
    it("should fetch paginated members", async () => {
      const mockResponse = {
        count: 2,
        next: null,
        previous: null,
        total_pages: 1,
        current_page: 1,
        page_size: 20,
        results: [
          {
            id: 1,
            user: 1,
            user_name: "teacher1",
            course: 1,
            course_title: "Test Course",
            role: "teacher",
            status: "enrolled",
          },
          {
            id: 2,
            user: 2,
            user_name: "student1",
            course: 1,
            course_title: "Test Course",
            role: "student",
            status: "enrolled",
          },
        ],
      };

      mock
        .onGet("http://localhost:8000/api/courses/1/members/")
        .reply(200, mockResponse);

      const result = await listCourseMembers(1);
      expect(result.results).toHaveLength(2);
      expect(result.total_pages).toBe(1);
    });
  });

  describe("inviteCourseMember", () => {
    it("should invite a user as student", async () => {
      const mockMembership: CourseMembership = {
        id: 3,
        user: 5,
        user_name: "newstudent",
        course: 1,
        course_title: "Test Course",
        role: "student",
        status: "invited",
      };

      mock
        .onPost("http://localhost:8000/api/courses/1/members/")
        .reply(201, mockMembership);

      const result = await inviteCourseMember(1, { user: 5 });
      expect(result.status).toBe("invited");
      expect(result.role).toBe("student");
    });

    it("should invite with a specific role", async () => {
      const mockMembership: CourseMembership = {
        id: 3,
        user: 5,
        user_name: "newassistant",
        course: 1,
        course_title: "Test Course",
        role: "assistant",
        status: "invited",
      };

      mock
        .onPost("http://localhost:8000/api/courses/1/members/")
        .reply(201, mockMembership);

      const result = await inviteCourseMember(1, {
        user: 5,
        role: "assistant",
      });
      expect(result.role).toBe("assistant");
    });

    it("should handle 409 when user already a member", async () => {
      mock
        .onPost("http://localhost:8000/api/courses/1/members/")
        .reply(409, { detail: "User is already a member of this course." });

      await expect(inviteCourseMember(1, { user: 5 })).rejects.toThrow();
    });
  });

  describe("updateCourseMembership", () => {
    it("should approve a pending membership", async () => {
      const mockMembership: CourseMembership = {
        id: 2,
        user: 3,
        user_name: "student1",
        course: 1,
        course_title: "Test Course",
        role: "student",
        status: "enrolled",
      };

      mock
        .onPatch("http://localhost:8000/api/courses/1/members/2/")
        .reply(200, mockMembership);

      const result = await updateCourseMembership(1, 2, {
        status: "enrolled",
      });
      expect(result.status).toBe("enrolled");
    });

    it("should change a member's role", async () => {
      const mockMembership: CourseMembership = {
        id: 2,
        user: 3,
        user_name: "student1",
        course: 1,
        course_title: "Test Course",
        role: "assistant",
        status: "enrolled",
      };

      mock
        .onPatch("http://localhost:8000/api/courses/1/members/2/")
        .reply(200, mockMembership);

      const result = await updateCourseMembership(1, 2, {
        role: "assistant",
      });
      expect(result.role).toBe("assistant");
    });
  });

  describe("removeCourseMember", () => {
    it("should remove a member", async () => {
      mock
        .onDelete("http://localhost:8000/api/courses/1/members/2/")
        .reply(204);

      await expect(removeCourseMember(1, 2)).resolves.not.toThrow();
    });

    it("should handle 409 when removing last teacher", async () => {
      mock
        .onDelete("http://localhost:8000/api/courses/1/members/1/")
        .reply(409, {
          detail: "Cannot remove the last teacher in the course.",
        });

      await expect(removeCourseMember(1, 1)).rejects.toThrow();
    });
  });
});
