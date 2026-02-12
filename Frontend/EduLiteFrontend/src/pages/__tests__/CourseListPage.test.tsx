import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/test/utils";
import userEvent from "@testing-library/user-event";
import toast from "react-hot-toast";
import CourseListPage from "../CourseListPage";
import * as coursesApi from "../../services/coursesApi";
import type {
  CoursePaginatedResponse,
  CourseListItem,
} from "../../types/courses.types";

// Mock dependencies
vi.mock("../../services/coursesApi");
vi.mock("react-hot-toast");
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockNavigate = vi.fn();

const mockCourse1: CourseListItem = {
  id: 1,
  title: "Introduction to Physics",
  outline: "Learn the fundamentals of physics",
  visibility: "public",
  subject: "physics",
  language: "en",
  country: "US",
  is_active: true,
  member_count: 25,
  is_member: true,
  user_role: "teacher",
  user_status: "enrolled",
  start_date: "2024-09-01T08:00:00Z",
  end_date: "2024-12-15T20:00:00Z",
};

const mockCourse2: CourseListItem = {
  id: 2,
  title: "Advanced Mathematics",
  outline: null,
  visibility: "private",
  subject: "math",
  language: "ar",
  country: "PS",
  is_active: true,
  member_count: 10,
  is_member: true,
  user_role: "student",
  user_status: "enrolled",
  start_date: null,
  end_date: null,
};

const mockCourse3: CourseListItem = {
  id: 3,
  title: "Computer Science 101",
  outline: "Intro to CS",
  visibility: "restricted",
  subject: "cs",
  language: "en",
  country: "CA",
  is_active: false,
  member_count: 0,
  is_member: false,
  user_role: null,
  user_status: null,
  start_date: "2025-01-15T08:00:00Z",
  end_date: null,
};

const mockPaginatedResponse: CoursePaginatedResponse<CourseListItem> = {
  count: 3,
  next: null,
  previous: null,
  total_pages: 1,
  current_page: 1,
  page_size: 20,
  results: [mockCourse1, mockCourse2, mockCourse3],
};

const mockEmptyResponse: CoursePaginatedResponse<CourseListItem> = {
  count: 0,
  next: null,
  previous: null,
  total_pages: 1,
  current_page: 1,
  page_size: 20,
  results: [],
};

const mockMultiPageResponse: CoursePaginatedResponse<CourseListItem> = {
  count: 45,
  next: "http://localhost:8000/api/courses/?page=2",
  previous: null,
  total_pages: 3,
  current_page: 1,
  page_size: 20,
  results: [mockCourse1, mockCourse2, mockCourse3],
};

describe("CourseListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Rendering", () => {
    it("renders loading state initially", () => {
      vi.mocked(coursesApi.listCourses).mockImplementation(
        () => new Promise(() => {}),
      );

      renderWithProviders(<CourseListPage view="me" />);

      expect(screen.getByText(/loading courses/i)).toBeInTheDocument();
    });

    it("renders My Courses view with title and subtitle", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      expect(screen.getByText("My Courses")).toBeInTheDocument();
      expect(
        screen.getByText(/manage and access your enrolled courses/i),
      ).toBeInTheDocument();
    });

    it("renders Public Courses view with title and subtitle", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      expect(screen.getByText("Public Courses")).toBeInTheDocument();
      expect(
        screen.getByText(/discover and enroll in public courses/i),
      ).toBeInTheDocument();
    });

    it("renders Create Course button", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      expect(screen.getByText(/create course/i)).toBeInTheDocument();
    });

    it("renders course data in table rows", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        // Titles appear in both desktop table and mobile cards
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      expect(
        screen.getAllByText("Advanced Mathematics").length,
      ).toBeGreaterThan(0);
      expect(
        screen.getAllByText("Computer Science 101").length,
      ).toBeGreaterThan(0);
      // Subject lookup
      expect(screen.getAllByText("Physics").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Mathematics").length).toBeGreaterThan(0);
    });

    it("renders visibility badges", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      expect(screen.getAllByText("Public").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Private").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Restricted").length).toBeGreaterThan(0);
    });

    it("renders member counts", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      expect(screen.getAllByText(/25 member/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/10 member/).length).toBeGreaterThan(0);
    });

    it("dims inactive courses with opacity", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      const { container } = renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Computer Science 101").length,
        ).toBeGreaterThan(0);
      });

      // mockCourse3 is_active: false, should have opacity-50
      const rows = container.querySelectorAll("tbody tr");
      const inactiveRow = Array.from(rows).find((row) =>
        row.textContent?.includes("Computer Science 101"),
      );
      expect(inactiveRow).toHaveClass("opacity-50");
    });
  });

  describe("Empty States", () => {
    it("shows My Courses empty state with browse CTA", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(mockEmptyResponse);

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      expect(screen.getByText("No courses yet")).toBeInTheDocument();
      expect(
        screen.getByText(/you're not enrolled in any courses yet/i),
      ).toBeInTheDocument();
      // Should show "View Public" CTA button
      expect(screen.getAllByText(/view public/i).length).toBeGreaterThan(0);
    });

    it("shows Public Courses empty state without browse CTA", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(mockEmptyResponse);

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      expect(screen.getByText("No courses yet")).toBeInTheDocument();
      expect(
        screen.getByText(/no public courses available/i),
      ).toBeInTheDocument();
    });
  });

  describe("Error State", () => {
    it("shows error message when API call fails", async () => {
      vi.mocked(coursesApi.listCourses).mockRejectedValue(
        new Error("Network error"),
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      expect(screen.getByText(/failed to load courses/i)).toBeInTheDocument();
    });
  });

  describe("View Toggle", () => {
    it("shows toggle to switch to Public from My Courses view", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      // The toggle button in the header (not the empty state CTA)
      const toggleButton = screen.getByRole("button", {
        name: /view public/i,
      });
      expect(toggleButton).toBeInTheDocument();
    });

    it("shows toggle to switch to Mine from Public view", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      const toggleButton = screen.getByRole("button", {
        name: /view mine/i,
      });
      expect(toggleButton).toBeInTheDocument();
    });

    it("navigates to /courses/public when toggle clicked from me view", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /view public/i }));

      expect(mockNavigate).toHaveBeenCalledWith("/courses/public");
    });

    it("navigates to /courses/me when toggle clicked from public view", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /view mine/i }));

      expect(mockNavigate).toHaveBeenCalledWith("/courses/me");
    });

    it("saves current view to localStorage", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(localStorage.getItem("courseView")).toBe("public");
      });
    });

    it("redirects from /courses to saved view in localStorage", () => {
      localStorage.setItem("courseView", "public");
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage />);

      expect(mockNavigate).toHaveBeenCalledWith("/courses/public", {
        replace: true,
      });
    });

    it("redirects to /courses/me by default when no localStorage", () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage />);

      expect(mockNavigate).toHaveBeenCalledWith("/courses/me", {
        replace: true,
      });
    });
  });

  describe("API Params", () => {
    it("passes mine=true for My Courses view", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(coursesApi.listCourses).toHaveBeenCalledWith(
          expect.objectContaining({ mine: true }),
        );
      });
    });

    it("passes visibility=public for Public Courses view", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(coursesApi.listCourses).toHaveBeenCalledWith(
          expect.objectContaining({ visibility: "public" }),
        );
      });
    });

    it("includes page and page_size in params", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(coursesApi.listCourses).toHaveBeenCalledWith(
          expect.objectContaining({ page: 1, page_size: 20 }),
        );
      });
    });
  });

  describe("Pagination", () => {
    it("shows pagination when multiple pages exist", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockMultiPageResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      expect(screen.getByText(/page 1 of 3/i)).toBeInTheDocument();
      expect(screen.getByText(/showing 1-20 of 45/i)).toBeInTheDocument();
    });

    it("does not show pagination for single page", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      expect(screen.queryByText(/page 1 of 1/i)).not.toBeInTheDocument();
    });

    it("disables previous button on first page", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockMultiPageResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      const prevButton = screen.getByLabelText("Previous page");
      expect(prevButton).toBeDisabled();
    });

    it("enables next button when more pages exist", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockMultiPageResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      const nextButton = screen.getByLabelText("Next page");
      expect(nextButton).not.toBeDisabled();
    });

    it("advances to next page when next button clicked", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockMultiPageResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      await user.click(screen.getByLabelText("Next page"));

      await waitFor(() => {
        expect(coursesApi.listCourses).toHaveBeenCalledWith(
          expect.objectContaining({ page: 2 }),
        );
      });
    });
  });

  describe("Navigation", () => {
    it("navigates to course detail when row is clicked", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      await user.click(screen.getAllByText("Introduction to Physics")[0]);

      expect(mockNavigate).toHaveBeenCalledWith("/courses/1");
    });

    it("navigates to create page when Create Course is clicked", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      await user.click(screen.getByText(/create course/i));

      expect(mockNavigate).toHaveBeenCalledWith("/courses/new");
    });
  });

  describe("Filters", () => {
    it("shows filter panel when filter button is clicked", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      // Filter labels should not be visible initially
      expect(
        screen.queryByText("Subject", { selector: "label" }),
      ).not.toBeInTheDocument();

      // Click the filter button — find the button with no text content (icon-only)
      const actionsButtons = screen.getAllByRole("button");
      const filterBtn = actionsButtons.find(
        (btn) => !btn.textContent?.trim() || btn.textContent?.trim() === "",
      );
      if (filterBtn) {
        await user.click(filterBtn);
      }

      // Now filter labels should be visible
      await waitFor(() => {
        expect(
          screen.getByText("Subject", { selector: "label" }),
        ).toBeInTheDocument();
      });
    });

    it("shows visibility filter only in My Courses view", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      // Render with "me" view
      const { unmount } = renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      // Open filters
      const buttons = screen.getAllByRole("button");
      const filterBtn = buttons.find(
        (btn) => !btn.textContent?.trim() || btn.textContent?.trim() === "",
      );
      if (filterBtn) await user.click(filterBtn);

      await waitFor(() => {
        expect(
          screen.getByText("Visibility", { selector: "label" }),
        ).toBeInTheDocument();
      });

      unmount();

      // Render with "public" view
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );
      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(screen.queryByText(/loading courses/i)).not.toBeInTheDocument();
      });

      // Open filters
      const buttons2 = screen.getAllByRole("button");
      const filterBtn2 = buttons2.find(
        (btn) => !btn.textContent?.trim() || btn.textContent?.trim() === "",
      );
      if (filterBtn2) await user.click(filterBtn2);

      await waitFor(() => {
        expect(
          screen.getByText("Subject", { selector: "label" }),
        ).toBeInTheDocument();
      });

      // Visibility filter should NOT be present in public view
      expect(
        screen.queryByText("Visibility", { selector: "label" }),
      ).not.toBeInTheDocument();
    });
  });

  describe("Enroll Action", () => {
    it("calls enrollInCourse and shows success toast", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );
      vi.mocked(coursesApi.enrollInCourse).mockResolvedValue({
        id: 100,
        user: 1,
        user_name: "testuser",
        course: 3,
        course_title: "Computer Science 101",
        role: "student",
        status: "enrolled",
      });

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Computer Science 101").length,
        ).toBeGreaterThan(0);
      });

      // Click dots menu on non-member course (mockCourse3, is_member: false)
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[2]);

      // Click Enroll
      await waitFor(() => {
        expect(screen.getByText(/^enroll$/i)).toBeInTheDocument();
      });
      await user.click(screen.getByText(/^enroll$/i));

      await waitFor(() => {
        expect(coursesApi.enrollInCourse).toHaveBeenCalledWith(3);
        expect(toast.success).toHaveBeenCalledWith(
          expect.stringContaining("enrolled"),
        );
      });
    });

    it("shows pending toast for restricted course enrollment", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );
      vi.mocked(coursesApi.enrollInCourse).mockResolvedValue({
        id: 100,
        user: 1,
        user_name: "testuser",
        course: 3,
        course_title: "Computer Science 101",
        role: "student",
        status: "pending",
      });

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Computer Science 101").length,
        ).toBeGreaterThan(0);
      });

      // Click dots menu on non-member course (mockCourse3, is_member: false)
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[2]);

      await waitFor(() => {
        expect(screen.getByText(/^enroll$/i)).toBeInTheDocument();
      });
      await user.click(screen.getByText(/^enroll$/i));

      await waitFor(() => {
        expect(toast.success).toHaveBeenCalledWith(
          expect.stringContaining("awaiting"),
        );
      });
    });

    it("shows error toast when enrollment fails", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );
      vi.mocked(coursesApi.enrollInCourse).mockRejectedValue(
        new Error("Already enrolled"),
      );

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Computer Science 101").length,
        ).toBeGreaterThan(0);
      });

      // Click dots menu on non-member course (mockCourse3, is_member: false)
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[2]);

      await waitFor(() => {
        expect(screen.getByText(/^enroll$/i)).toBeInTheDocument();
      });
      await user.click(screen.getByText(/^enroll$/i));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalled();
      });
    });
  });

  describe("Leave Action", () => {
    it("shows confirmation modal before leaving", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      // Click dots menu
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[0]);

      // Click Leave
      await waitFor(() => {
        expect(screen.getByText(/leave course/i)).toBeInTheDocument();
      });
      await user.click(screen.getByText(/leave course/i));

      // Confirmation modal should appear
      await waitFor(() => {
        expect(
          screen.getByText(/are you sure you want to leave/i),
        ).toBeInTheDocument();
      });
    });

    it("calls leaveCourse when confirmed", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );
      vi.mocked(coursesApi.leaveCourse).mockResolvedValue(undefined);

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      // Open context menu
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/leave course/i)).toBeInTheDocument();
      });
      await user.click(screen.getByText(/leave course/i));

      // Click confirm in modal
      await waitFor(() => {
        expect(
          screen.getByText(/are you sure you want to leave/i),
        ).toBeInTheDocument();
      });

      const leaveButton = screen.getByRole("button", { name: /^leave$/i });
      await user.click(leaveButton);

      await waitFor(() => {
        expect(coursesApi.leaveCourse).toHaveBeenCalledWith(1);
        expect(toast.success).toHaveBeenCalled();
      });
    });

    it("does not call leaveCourse when cancelled", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      // Open context menu and click Leave
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/leave course/i)).toBeInTheDocument();
      });
      await user.click(screen.getByText(/leave course/i));

      // Click Cancel in modal
      await waitFor(() => {
        expect(
          screen.getByText(/are you sure you want to leave/i),
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /cancel/i }));

      expect(coursesApi.leaveCourse).not.toHaveBeenCalled();
    });

    it("shows error toast when leave fails", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );
      vi.mocked(coursesApi.leaveCourse).mockRejectedValue(
        new Error("Last teacher cannot leave"),
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/leave course/i)).toBeInTheDocument();
      });
      await user.click(screen.getByText(/leave course/i));

      await waitFor(() => {
        expect(
          screen.getByText(/are you sure you want to leave/i),
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /^leave$/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalled();
      });
    });
  });

  describe("Context Menu", () => {
    it("shows View Details option in context menu", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/view details/i)).toBeInTheDocument();
      });
    });

    it("shows Enroll option for non-member course", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Computer Science 101").length,
        ).toBeGreaterThan(0);
      });

      // Click dots on non-member course (mockCourse3, is_member: false)
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[2]);

      await waitFor(() => {
        expect(screen.getByText(/^enroll$/i)).toBeInTheDocument();
      });
    });

    it("shows Leave option for member course", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      // Click dots on member course (mockCourse1, is_member: true)
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/leave course/i)).toBeInTheDocument();
      });
    });

    it("does not show Enroll for member course", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      // Click dots on member course (mockCourse1, is_member: true)
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/view details/i)).toBeInTheDocument();
      });

      expect(screen.queryByText(/^enroll$/i)).not.toBeInTheDocument();
    });

    it("does not show Leave for non-member course", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="public" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Computer Science 101").length,
        ).toBeGreaterThan(0);
      });

      // Click dots on non-member course (mockCourse3, is_member: false)
      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[2]);

      await waitFor(() => {
        expect(screen.getByText(/^enroll$/i)).toBeInTheDocument();
      });

      expect(screen.queryByText(/leave course/i)).not.toBeInTheDocument();
    });

    it("navigates to detail page on View Details click", async () => {
      const user = userEvent.setup();
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      const dotsButtons = screen.getAllByLabelText(/actions/i);
      await user.click(dotsButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/view details/i)).toBeInTheDocument();
      });
      await user.click(screen.getByText(/view details/i));

      expect(mockNavigate).toHaveBeenCalledWith("/courses/1");
    });
  });

  describe("Styling and Layout", () => {
    it("has gradient background", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      const { container } = renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      const mainDiv = container.querySelector(".min-h-screen");
      expect(mainDiv).toHaveClass("bg-gradient-to-br");
    });

    it("has glass-morphism card styling", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      const { container } = renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      const glassCard = container.querySelector(".backdrop-blur-xl");
      expect(glassCard).toBeInTheDocument();
    });

    it("has dark mode classes", async () => {
      vi.mocked(coursesApi.listCourses).mockResolvedValue(
        mockPaginatedResponse,
      );

      const { container } = renderWithProviders(<CourseListPage view="me" />);

      await waitFor(() => {
        expect(
          screen.getAllByText("Introduction to Physics").length,
        ).toBeGreaterThan(0);
      });

      const darkElement = container.querySelector(".dark\\:from-gray-900");
      expect(darkElement).toBeInTheDocument();
    });
  });
});
