import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import i18n from "../../i18n";
import { AuthProvider } from "../../contexts/AuthContext";
import toast from "react-hot-toast";
import CourseDetailPage from "../CourseDetailPage";
import * as coursesApi from "../../services/coursesApi";
import type {
  CourseDetail,
  CourseMembership,
  CourseModule,
  CoursePaginatedResponse,
} from "../../types/courses.types";

// Mock dependencies
vi.mock("../../services/coursesApi");
vi.mock("react-hot-toast");

const mockNavigate = vi.fn();

// useBlocker requires a data router — use createMemoryRouter
const renderWithDataRouter = () => {
  const router = createMemoryRouter(
    [
      {
        path: "/courses/:id",
        element: <CourseDetailPage />,
      },
      {
        path: "/courses",
        element: <div>Course List</div>,
      },
    ],
    { initialEntries: ["/courses/1"] },
  );

  // Spy on navigate
  const originalNavigate = router.navigate.bind(router);
  router.navigate = vi.fn((...args: unknown[]) => {
    mockNavigate(...args);
    return originalNavigate(...(args as Parameters<typeof originalNavigate>));
  }) as typeof router.navigate;

  return render(
    <I18nextProvider i18n={i18n}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </I18nextProvider>,
  );
};

// --- Mock Data ---

const mockMember1: CourseMembership = {
  id: 10,
  user: 1,
  user_name: "teacher_user",
  course: 1,
  course_title: "Intro to Physics",
  role: "teacher",
  status: "enrolled",
};

const mockMember2: CourseMembership = {
  id: 11,
  user: 2,
  user_name: "student_user",
  course: 1,
  course_title: "Intro to Physics",
  role: "student",
  status: "enrolled",
};

const mockMember3: CourseMembership = {
  id: 12,
  user: 3,
  user_name: "pending_user",
  course: 1,
  course_title: "Intro to Physics",
  role: "student",
  status: "pending",
};

const mockModule1: CourseModule = {
  id: 20,
  course: 1,
  title: "Getting Started",
  order: 1,
  course_title: "Intro to Physics",
  content_type: "chat.chatroom",
  object_id: 5,
};

const mockModule2: CourseModule = {
  id: 21,
  course: 1,
  title: "",
  order: 2,
  course_title: "Intro to Physics",
  content_type: "slideshows.slideshow",
  object_id: 10,
};

const mockCourseDetail: CourseDetail = {
  id: 1,
  title: "Intro to Physics",
  outline: "Learn the basics of physics",
  language: "en",
  country: "US",
  subject: "physics",
  visibility: "public",
  start_date: "2024-09-01T08:00:00Z",
  end_date: "2024-12-15T20:00:00Z",
  duration_time: 2520,
  allow_join_requests: true,
  is_active: true,
  member_count: 25,
  user_role: "teacher",
  user_status: "enrolled" as const,
  members: [mockMember1, mockMember2, mockMember3],
  modules: [mockModule1, mockModule2],
};

const mockCourseAsStudent: CourseDetail = {
  ...mockCourseDetail,
  user_role: "student",
  user_status: "enrolled",
};

const mockCourseNotEnrolled: CourseDetail = {
  ...mockCourseDetail,
  user_role: null,
  user_status: null,
};

const mockMembersResponse: CoursePaginatedResponse<CourseMembership> = {
  count: 3,
  next: null,
  previous: null,
  total_pages: 1,
  current_page: 1,
  page_size: 20,
  results: [mockMember1, mockMember2, mockMember3],
};

const mockModulesArray: CourseModule[] = [mockModule1, mockModule2];

// --- Helpers ---

const setupMocks = (course: CourseDetail = mockCourseDetail) => {
  vi.mocked(coursesApi.getCourseDetail).mockResolvedValue(course);
  vi.mocked(coursesApi.listCourseMembers).mockResolvedValue(
    mockMembersResponse,
  );
  vi.mocked(coursesApi.listCourseModules).mockResolvedValue(mockModulesArray);
};

const waitForPageLoad = async () => {
  await waitFor(() => {
    expect(screen.queryByText(/loading course/i)).not.toBeInTheDocument();
  });
};

describe("CourseDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ===== RENDERING =====
  describe("Rendering", () => {
    it("shows loading state initially", () => {
      vi.mocked(coursesApi.getCourseDetail).mockImplementation(
        () => new Promise(() => {}),
      );
      vi.mocked(coursesApi.listCourseMembers).mockImplementation(
        () => new Promise(() => {}),
      );
      vi.mocked(coursesApi.listCourseModules).mockImplementation(
        () => new Promise(() => {}),
      );

      renderWithDataRouter();
      expect(screen.getByText(/loading course/i)).toBeInTheDocument();
    });

    it("renders course title and outline", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
      expect(
        screen.getByText("Learn the basics of physics"),
      ).toBeInTheDocument();
    });

    it("renders user role badge for teacher", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      // "Teacher" appears in role badge and in member HardLoadSelect options
      const teacherTexts = screen.getAllByText("Teacher");
      expect(teacherTexts.length).toBeGreaterThan(0);
      // The first one is the header role badge
      expect(teacherTexts[0].closest("span")).toHaveClass("rounded-full");
    });

    it("renders user role badge for student", async () => {
      setupMocks(mockCourseAsStudent);
      renderWithDataRouter();
      await waitForPageLoad();

      // "Student" appears in role badge and in member list badges
      const studentTexts = screen.getAllByText("Student");
      expect(studentTexts.length).toBeGreaterThan(0);
      // The first one is the header role badge
      expect(studentTexts[0].closest("span")).toHaveClass("rounded-full");
    });

    it("renders Not Enrolled badge for non-members", async () => {
      setupMocks(mockCourseNotEnrolled);
      renderWithDataRouter();
      await waitForPageLoad();

      expect(screen.getByText("Not Enrolled")).toBeInTheDocument();
    });

    it("renders metadata fields (subject, language, dates)", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      expect(screen.getByText("Physics")).toBeInTheDocument();
      expect(screen.getByText("English")).toBeInTheDocument();
      expect(screen.getByText("Active")).toBeInTheDocument();
    });

    it("renders member count", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      expect(screen.getAllByText(/25 member/i).length).toBeGreaterThan(0);
    });

    it("renders back to courses link", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      expect(screen.getByText("Back to Courses")).toBeInTheDocument();
    });
  });

  // ===== ERROR STATE =====
  describe("Error State", () => {
    it("shows error when API fails", async () => {
      vi.mocked(coursesApi.getCourseDetail).mockRejectedValue(
        new Error("Not found"),
      );
      vi.mocked(coursesApi.listCourseMembers).mockRejectedValue(
        new Error("fail"),
      );
      vi.mocked(coursesApi.listCourseModules).mockRejectedValue(
        new Error("fail"),
      );

      renderWithDataRouter();
      await waitForPageLoad();

      expect(screen.getByText(/not found/i)).toBeInTheDocument();
      expect(screen.getByText("Retry")).toBeInTheDocument();
    });
  });

  // ===== ENROLLMENT ACTIONS =====
  describe("Enrollment Actions", () => {
    it("shows Join Course button for non-members on public course", async () => {
      setupMocks(mockCourseNotEnrolled);
      renderWithDataRouter();
      await waitForPageLoad();

      expect(
        screen.getByRole("button", { name: /join course/i }),
      ).toBeInTheDocument();
    });

    it("shows Request to Join for restricted courses", async () => {
      setupMocks({
        ...mockCourseNotEnrolled,
        visibility: "restricted",
        allow_join_requests: true,
      });
      renderWithDataRouter();
      await waitForPageLoad();

      expect(
        screen.getByRole("button", { name: /request to join/i }),
      ).toBeInTheDocument();
    });

    it("hides join button for private courses", async () => {
      setupMocks({
        ...mockCourseNotEnrolled,
        visibility: "private",
      });
      renderWithDataRouter();
      await waitForPageLoad();

      expect(
        screen.queryByRole("button", { name: /join course/i }),
      ).not.toBeInTheDocument();
    });

    it("calls enrollInCourse on join click and shows toast", async () => {
      const user = userEvent.setup();
      setupMocks(mockCourseNotEnrolled);
      vi.mocked(coursesApi.enrollInCourse).mockResolvedValue({
        ...mockMember2,
        status: "enrolled",
      });

      renderWithDataRouter();
      await waitForPageLoad();

      await user.click(screen.getByRole("button", { name: /join course/i }));

      await waitFor(() => {
        expect(coursesApi.enrollInCourse).toHaveBeenCalledWith(1);
        expect(toast.success).toHaveBeenCalled();
      });
    });

    it("shows Leave Course button for enrolled students", async () => {
      setupMocks(mockCourseAsStudent);
      renderWithDataRouter();
      await waitForPageLoad();

      expect(
        screen.getByRole("button", { name: /leave course/i }),
      ).toBeInTheDocument();
    });

    it("shows confirmation modal when Leave is clicked", async () => {
      const user = userEvent.setup();
      setupMocks(mockCourseAsStudent);
      renderWithDataRouter();
      await waitForPageLoad();

      await user.click(screen.getByRole("button", { name: /leave course/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/are you sure you want to leave/i),
        ).toBeInTheDocument();
      });
    });
  });

  // ===== TEACHER ACTIONS =====
  describe("Teacher Actions", () => {
    it("shows Edit and Delete buttons for teachers", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      expect(
        screen.getByRole("button", { name: /edit course/i }),
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /delete course/i }),
      ).toBeInTheDocument();
    });

    it("hides Edit and Delete for non-teachers", async () => {
      setupMocks(mockCourseAsStudent);
      renderWithDataRouter();
      await waitForPageLoad();

      expect(
        screen.queryByRole("button", { name: /edit course/i }),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: /delete course/i }),
      ).not.toBeInTheDocument();
    });

    it("enters edit mode when Edit Course is clicked", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      await user.click(screen.getByRole("button", { name: /edit course/i }));

      // Should see Cancel button and editable title input
      expect(
        screen.getByRole("button", { name: /cancel/i }),
      ).toBeInTheDocument();
      expect(screen.getByDisplayValue("Intro to Physics")).toBeInTheDocument();
    });

    it("shows delete confirmation modal", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      await user.click(screen.getByRole("button", { name: /delete course/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/are you sure you want to delete/i),
        ).toBeInTheDocument();
      });
    });

    it("calls deleteCourse and navigates on confirm", async () => {
      const user = userEvent.setup();
      setupMocks();
      vi.mocked(coursesApi.deleteCourse).mockResolvedValue(undefined);

      renderWithDataRouter();
      await waitForPageLoad();

      await user.click(screen.getByRole("button", { name: /delete course/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/are you sure you want to delete/i),
        ).toBeInTheDocument();
      });

      // Click the confirm button in the modal
      const confirmButtons = screen.getAllByRole("button", {
        name: /delete course/i,
      });
      // The modal confirm button is the last one
      await user.click(confirmButtons[confirmButtons.length - 1]);

      await waitFor(() => {
        expect(coursesApi.deleteCourse).toHaveBeenCalledWith(1);
        expect(toast.success).toHaveBeenCalled();
        expect(mockNavigate).toHaveBeenCalledWith(
          "/courses",
          expect.anything(),
        );
      });
    });
  });

  // ===== METADATA EDITING =====
  describe("Metadata Editing", () => {
    it("shows save banner when fields are changed", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      await user.click(screen.getByRole("button", { name: /edit course/i }));

      // Modify the title
      const titleInput = screen.getByDisplayValue("Intro to Physics");
      await user.clear(titleInput);
      await user.type(titleInput, "Advanced Physics");

      // Click somewhere else to trigger blur
      await user.tab();

      await waitFor(() => {
        expect(
          screen.getByText("You have unsaved changes"),
        ).toBeInTheDocument();
      });
    });

    it("calls updateCourse on save", async () => {
      const user = userEvent.setup();
      setupMocks();
      vi.mocked(coursesApi.updateCourse).mockResolvedValue({
        ...mockCourseDetail,
        title: "Advanced Physics",
      });

      renderWithDataRouter();
      await waitForPageLoad();

      await user.click(screen.getByRole("button", { name: /edit course/i }));

      const titleInput = screen.getByDisplayValue("Intro to Physics");
      await user.clear(titleInput);
      await user.type(titleInput, "Advanced Physics");
      await user.tab();

      await waitFor(() => {
        expect(
          screen.getByText("You have unsaved changes"),
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /save changes/i }));

      await waitFor(() => {
        expect(coursesApi.updateCourse).toHaveBeenCalledWith(
          1,
          expect.objectContaining({ title: "Advanced Physics" }),
        );
        expect(toast.success).toHaveBeenCalled();
      });
    });

    it("resets form on cancel", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      await user.click(screen.getByRole("button", { name: /edit course/i }));

      const titleInput = screen.getByDisplayValue("Intro to Physics");
      await user.clear(titleInput);
      await user.type(titleInput, "Changed Title");

      // Click cancel in the actions area (not the save banner)
      const cancelButtons = screen.getAllByRole("button", {
        name: /cancel/i,
      });
      await user.click(cancelButtons[0]);

      // Confirmation modal should appear — click discard
      await user.click(
        screen.getByRole("button", { name: /discard changes/i }),
      );

      // Should exit edit mode, title goes back to original
      expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
      expect(
        screen.queryByDisplayValue("Changed Title"),
      ).not.toBeInTheDocument();
    });
  });

  // ===== TAB NAVIGATION =====
  describe("Tab Navigation", () => {
    it("shows Members tab by default", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      // Members tab should be active and show member content
      expect(screen.getByText("Course Members")).toBeInTheDocument();
    });

    it("switches to Modules tab on click", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      // Click the Modules tab
      const modulesTabButtons = screen.getAllByText("Modules");
      // The tab button (not the header)
      await user.click(modulesTabButtons[0]);

      await waitFor(() => {
        expect(screen.getByText("Course Modules")).toBeInTheDocument();
      });
    });
  });

  // ===== MEMBERS TAB =====
  describe("Members Tab", () => {
    it("renders member list with names and badges", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      expect(screen.getAllByText("teacher_user").length).toBeGreaterThan(0);
      expect(screen.getAllByText("student_user").length).toBeGreaterThan(0);
      expect(screen.getAllByText("pending_user").length).toBeGreaterThan(0);
    });

    it("shows Invite Member button for teachers", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      expect(
        screen.getByRole("button", { name: /invite member/i }),
      ).toBeInTheDocument();
    });

    it("hides Invite Member button for non-teachers", async () => {
      setupMocks(mockCourseAsStudent);
      renderWithDataRouter();
      await waitForPageLoad();

      expect(
        screen.queryByRole("button", { name: /invite member/i }),
      ).not.toBeInTheDocument();
    });

    it("shows Approve/Deny buttons for pending members", async () => {
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      // Should have approve and deny buttons for the pending member
      expect(screen.getAllByLabelText(/approve/i).length).toBeGreaterThan(0);
      expect(screen.getAllByLabelText(/deny/i).length).toBeGreaterThan(0);
    });

    it("opens invite modal when Invite Member is clicked", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      await user.click(screen.getByRole("button", { name: /invite member/i }));

      await waitFor(() => {
        // Modal heading is an h2, distinct from the button text
        expect(
          screen.getByRole("heading", { name: "Invite Member" }),
        ).toBeInTheDocument();
        // Modal shows search input and Send Invite button
        expect(
          screen.getByPlaceholderText("Type a username or name..."),
        ).toBeInTheDocument();
        expect(
          screen.getByRole("button", { name: /send invite/i }),
        ).toBeInTheDocument();
      });
    });
  });

  // ===== MODULES TAB =====
  describe("Modules Tab", () => {
    it("renders module list with titles", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      // Switch to modules tab
      const modulesTabButtons = screen.getAllByText("Modules");
      await user.click(modulesTabButtons[0]);

      await waitFor(() => {
        expect(screen.getByText("Getting Started")).toBeInTheDocument();
      });

      // Module 2 has no title — should show "Module 2"
      expect(screen.getByText("Module 2")).toBeInTheDocument();
    });

    it("renders content type labels", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      const modulesTabButtons = screen.getAllByText("Modules");
      await user.click(modulesTabButtons[0]);

      await waitFor(() => {
        expect(screen.getByText("Chatroom")).toBeInTheDocument();
      });
      expect(screen.getByText("Slideshow")).toBeInTheDocument();
    });

    it("shows Add Module button for teachers", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      const modulesTabButtons = screen.getAllByText("Modules");
      await user.click(modulesTabButtons[0]);

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /add module/i }),
        ).toBeInTheDocument();
      });
    });

    it("shows reorder, edit, delete buttons for teachers", async () => {
      const user = userEvent.setup();
      setupMocks();
      renderWithDataRouter();
      await waitForPageLoad();

      const modulesTabButtons = screen.getAllByText("Modules");
      await user.click(modulesTabButtons[0]);

      await waitFor(() => {
        expect(screen.getAllByLabelText(/move up/i).length).toBeGreaterThan(0);
      });

      expect(screen.getAllByLabelText(/move down/i).length).toBeGreaterThan(0);
      expect(screen.getAllByLabelText(/edit/i).length).toBeGreaterThan(0);
      expect(screen.getAllByLabelText(/delete/i).length).toBeGreaterThan(0);
    });

    it("hides teacher actions for non-teachers", async () => {
      const user = userEvent.setup();
      setupMocks(mockCourseAsStudent);
      renderWithDataRouter();
      await waitForPageLoad();

      const modulesTabButtons = screen.getAllByText("Modules");
      await user.click(modulesTabButtons[0]);

      await waitFor(() => {
        expect(screen.getByText("Getting Started")).toBeInTheDocument();
      });

      expect(
        screen.queryByRole("button", { name: /add module/i }),
      ).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/edit/i)).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/delete/i)).not.toBeInTheDocument();
    });
  });

  // ===== STYLING =====
  describe("Styling", () => {
    it("has gradient background", async () => {
      setupMocks();
      const { container } = renderWithDataRouter();
      await waitForPageLoad();

      const mainDiv = container.querySelector(".min-h-screen");
      expect(mainDiv).toHaveClass("bg-gradient-to-br");
    });

    it("has glass-morphism card styling", async () => {
      setupMocks();
      const { container } = renderWithDataRouter();
      await waitForPageLoad();

      const glassCard = container.querySelector(".backdrop-blur-xl");
      expect(glassCard).toBeInTheDocument();
    });

    it("has dark mode classes", async () => {
      setupMocks();
      const { container } = renderWithDataRouter();
      await waitForPageLoad();

      const darkElement = container.querySelector(".dark\\:from-gray-900");
      expect(darkElement).toBeInTheDocument();
    });
  });
});
