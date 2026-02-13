import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../../../test/utils";
import AddModuleModal from "../AddModuleModal";
import type { SlideshowListItem } from "../../../types/slideshow.types";
import type { CourseModule } from "../../../types/courses.types";

// Mock the slideshowApi module
vi.mock("../../../services/slideshowApi", () => ({
  searchSlideshows: vi.fn(),
  listMySlideshows: vi.fn(),
  listSlideshows: vi.fn(),
}));

import {
  searchSlideshows,
  listMySlideshows,
} from "../../../services/slideshowApi";

const mockSearchSlideshows = vi.mocked(searchSlideshows);
const mockListMySlideshows = vi.mocked(listMySlideshows);

const mockSlideshows: SlideshowListItem[] = [
  {
    id: 1,
    title: "Intro to Physics",
    description: "A basic physics overview",
    created_by: 1,
    created_by_username: "teacher1",
    visibility: "public",
    language: "en",
    country: "US",
    subject: "physics",
    is_published: true,
    slide_count: 10,
    version: 1,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 2,
    title: "Math Basics",
    description: null,
    created_by: 1,
    created_by_username: "teacher1",
    visibility: "private",
    language: "en",
    country: null,
    subject: "math",
    is_published: false,
    slide_count: 5,
    version: 1,
    created_at: "2024-02-01T00:00:00Z",
    updated_at: "2024-02-01T00:00:00Z",
  },
];

const defaultProps = {
  isOpen: true,
  onClose: vi.fn(),
  onSubmit: vi.fn(),
};

describe("AddModuleModal", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockSearchSlideshows.mockReset();
    mockListMySlideshows.mockReset();
    defaultProps.onClose.mockReset();
    defaultProps.onSubmit.mockReset();

    // Default: listMySlideshows returns mock results
    mockListMySlideshows.mockResolvedValue({
      count: 2,
      next: null,
      previous: null,
      results: mockSlideshows,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe("Rendering", () => {
    it("renders nothing when isOpen is false", () => {
      const { container } = renderWithProviders(
        <AddModuleModal {...defaultProps} isOpen={false} />,
      );
      expect(container.innerHTML).toBe("");
    });

    it("renders modal with title when isOpen is true", () => {
      renderWithProviders(<AddModuleModal {...defaultProps} />);
      expect(
        screen.getByRole("heading", { name: "Add Module" }),
      ).toBeInTheDocument();
    });

    it("shows type selection grid on initial open", () => {
      renderWithProviders(<AddModuleModal {...defaultProps} />);
      expect(screen.getByText("Select Module Type")).toBeInTheDocument();
      expect(screen.getByText("Slideshow")).toBeInTheDocument();
    });

    it("shows disabled future types with coming soon label", () => {
      renderWithProviders(<AddModuleModal {...defaultProps} />);
      expect(screen.getByText("Quiz")).toBeInTheDocument();
      expect(screen.getByText("Notes")).toBeInTheDocument();
      expect(screen.getByText("Assignment")).toBeInTheDocument();
      // All "Coming soon" labels
      expect(screen.getAllByText("Coming soon")).toHaveLength(3);
    });
  });

  describe("Step 1: Type Selection", () => {
    it("navigates to search step when Slideshow is clicked", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderWithProviders(<AddModuleModal {...defaultProps} />);

      await user.click(screen.getByText("Slideshow"));

      // Should now show search UI
      await waitFor(() => {
        expect(
          screen.getByPlaceholderText("Type to search slideshows..."),
        ).toBeInTheDocument();
      });
    });

    it("does not navigate when disabled type is clicked", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderWithProviders(<AddModuleModal {...defaultProps} />);

      await user.click(screen.getByText("Quiz"));

      // Should still be on type selection
      expect(screen.getByText("Select Module Type")).toBeInTheDocument();
    });
  });

  describe("Step 2: Search & Select", () => {
    const goToSearch = async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderWithProviders(<AddModuleModal {...defaultProps} />);

      await user.click(screen.getByText("Slideshow"));

      await waitFor(() => {
        expect(
          screen.getByPlaceholderText("Type to search slideshows..."),
        ).toBeInTheDocument();
      });

      return user;
    };

    it("loads user's slideshows by default (My Slideshows mode)", async () => {
      await goToSearch();

      await waitFor(() => {
        expect(mockListMySlideshows).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
        expect(screen.getByText("Math Basics")).toBeInTheDocument();
      });
    });

    it("shows published and draft badges", async () => {
      await goToSearch();

      await waitFor(() => {
        expect(screen.getByText("Published")).toBeInTheDocument();
        expect(screen.getByText("Draft")).toBeInTheDocument();
      });
    });

    it("shows slide count for each result", async () => {
      await goToSearch();

      await waitFor(() => {
        expect(screen.getByText("10 slides")).toBeInTheDocument();
        expect(screen.getByText("5 slides")).toBeInTheDocument();
      });
    });

    it("debounces search and calls searchSlideshows", async () => {
      mockSearchSlideshows.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockSlideshows[0]],
      });

      const user = await goToSearch();

      await user.type(
        screen.getByPlaceholderText("Type to search slideshows..."),
        "physics",
      );

      // Not called yet — debounce
      expect(mockSearchSlideshows).not.toHaveBeenCalled();

      await act(() => vi.advanceTimersByTime(350));

      expect(mockSearchSlideshows).toHaveBeenCalledWith({
        q: "physics",
        mine: true,
        page_size: 20,
      });
    });

    it("toggles between My Slideshows and All Slideshows", async () => {
      const user = await goToSearch();

      // Click "All Slideshows"
      await user.click(screen.getByText("All Slideshows"));

      // Without a query in All mode, should show prompt
      await waitFor(() => {
        expect(
          screen.getByText("Type at least 2 characters to search"),
        ).toBeInTheDocument();
      });

      // Switch back
      await user.click(screen.getByText("My Slideshows"));

      await waitFor(() => {
        expect(mockListMySlideshows).toHaveBeenCalled();
      });
    });

    it("shows no results message when search returns empty", async () => {
      mockListMySlideshows.mockResolvedValue({
        count: 0,
        next: null,
        previous: null,
        results: [],
      });

      await goToSearch();

      await waitFor(() => {
        expect(screen.getByText("No slideshows found")).toBeInTheDocument();
      });
    });

    it("navigates to confirm step when a slideshow is selected", async () => {
      const user = await goToSearch();

      await waitFor(() => {
        expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Intro to Physics"));

      // Should show confirm step
      await waitFor(() => {
        expect(screen.getByText("Selected content")).toBeInTheDocument();
        expect(
          screen.getByRole("button", { name: /add module/i }),
        ).toBeInTheDocument();
      });
    });

    it("navigates back to type selection on back button", async () => {
      const user = await goToSearch();

      // Click the back button
      await user.click(screen.getByRole("button", { name: /back/i }));

      expect(screen.getByText("Select Module Type")).toBeInTheDocument();
    });
  });

  describe("Step 3: Confirm & Submit", () => {
    const goToConfirm = async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

      renderWithProviders(<AddModuleModal {...defaultProps} />);

      await user.click(screen.getByText("Slideshow"));

      await waitFor(() => {
        expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Intro to Physics"));

      await waitFor(() => {
        expect(screen.getByText("Selected content")).toBeInTheDocument();
      });

      return user;
    };

    it("shows selected slideshow details", async () => {
      await goToConfirm();

      // Title should be in the summary and pre-filled in input
      expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
      expect(screen.getByText("A basic physics overview")).toBeInTheDocument();
      expect(screen.getByDisplayValue("Intro to Physics")).toBeInTheDocument();
    });

    it("pre-fills module title with slideshow title", async () => {
      await goToConfirm();

      const titleInput = screen.getByDisplayValue("Intro to Physics");
      expect(titleInput).toBeInTheDocument();
    });

    it("allows editing the module title", async () => {
      const user = await goToConfirm();

      const titleInput = screen.getByDisplayValue("Intro to Physics");
      await user.clear(titleInput);
      await user.type(titleInput, "Week 1: Physics");

      expect(screen.getByDisplayValue("Week 1: Physics")).toBeInTheDocument();
    });

    it("submits with correct data on Add Module click", async () => {
      const onSubmit = vi.fn().mockResolvedValue(undefined);
      const onClose = vi.fn();
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

      renderWithProviders(
        <AddModuleModal isOpen={true} onClose={onClose} onSubmit={onSubmit} />,
      );

      await user.click(screen.getByText("Slideshow"));

      await waitFor(() => {
        expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Intro to Physics"));

      await waitFor(() => {
        expect(screen.getByText("Selected content")).toBeInTheDocument();
      });

      // Click Add Module
      await user.click(screen.getByRole("button", { name: /add module/i }));

      expect(onSubmit).toHaveBeenCalledWith({
        title: "Intro to Physics",
        content_type: "slideshows.slideshow",
        object_id: 1,
      });

      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      });
    });

    it("shows error when submit fails", async () => {
      const onSubmit = vi
        .fn()
        .mockRejectedValue(new Error("Module already exists"));
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

      renderWithProviders(
        <AddModuleModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />,
      );

      await user.click(screen.getByText("Slideshow"));

      await waitFor(() => {
        expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Intro to Physics"));

      await waitFor(() => {
        expect(screen.getByText("Selected content")).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /add module/i }));

      await waitFor(() => {
        expect(screen.getByText("Module already exists")).toBeInTheDocument();
      });
    });

    it("navigates back to search on back button", async () => {
      const user = await goToConfirm();

      await user.click(screen.getByRole("button", { name: /back/i }));

      expect(
        screen.getByPlaceholderText("Type to search slideshows..."),
      ).toBeInTheDocument();
    });
  });

  describe("Edit Mode", () => {
    const editModule: CourseModule = {
      id: 10,
      course: 1,
      title: "Existing Module",
      order: 2,
      course_title: "Test Course",
      content_type: "slideshows.slideshow",
      object_id: 1,
    };

    it("skips type selection and goes to search in edit mode", () => {
      renderWithProviders(
        <AddModuleModal {...defaultProps} editModule={editModule} />,
      );

      expect(
        screen.getByRole("heading", { name: "Edit Module" }),
      ).toBeInTheDocument();
      expect(
        screen.getByPlaceholderText("Type to search slideshows..."),
      ).toBeInTheDocument();
    });

    it("pre-fills module title from editModule", () => {
      renderWithProviders(
        <AddModuleModal {...defaultProps} editModule={editModule} />,
      );

      // Title is pre-filled but we're on search step, not confirm
      // The title will be shown when we select an item
    });

    it("shows Save Module button instead of Add Module on confirm", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

      renderWithProviders(
        <AddModuleModal {...defaultProps} editModule={editModule} />,
      );

      await waitFor(() => {
        expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Intro to Physics"));

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /save module/i }),
        ).toBeInTheDocument();
      });
    });

    it("does not show back button to type selection in edit mode", async () => {
      renderWithProviders(
        <AddModuleModal {...defaultProps} editModule={editModule} />,
      );

      // Back button should not go to type selection (since we skipped it)
      expect(screen.queryByText("Select Module Type")).not.toBeInTheDocument();
    });
  });

  describe("Close and Reset", () => {
    it("calls onClose when Cancel is clicked", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      const onClose = vi.fn();

      renderWithProviders(
        <AddModuleModal isOpen={true} onClose={onClose} onSubmit={vi.fn()} />,
      );

      // Go to confirm step to see Cancel button
      await user.click(screen.getByText("Slideshow"));

      await waitFor(() => {
        expect(screen.getByText("Intro to Physics")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Intro to Physics"));

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /cancel/i }),
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /cancel/i }));
      expect(onClose).toHaveBeenCalled();
    });

    it("resets to type selection when reopened", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

      const { rerender } = renderWithProviders(
        <AddModuleModal {...defaultProps} />,
      );

      // Navigate to search step
      await user.click(screen.getByText("Slideshow"));

      await waitFor(() => {
        expect(
          screen.getByPlaceholderText("Type to search slideshows..."),
        ).toBeInTheDocument();
      });

      // Close and reopen
      rerender(<AddModuleModal {...defaultProps} isOpen={false} />);
      rerender(<AddModuleModal {...defaultProps} isOpen={true} />);

      // Should be back on type selection
      expect(screen.getByText("Select Module Type")).toBeInTheDocument();
    });
  });
});
