import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/test/utils";
import userEvent from "@testing-library/user-event";
import SlideshowViewer from "../SlideshowViewer";
import * as slideshowApi from "../../../services/slideshowApi";
import type { SlideshowDetail } from "../../../types/slideshow.types";

// Mock the slideshowApi
vi.mock("../../../services/slideshowApi");

describe("SlideshowViewer Component", () => {
  const mockSlideshowDetail: SlideshowDetail = {
    id: 1,
    title: "Test Slideshow",
    description: "Test description",
    created_by: 1,
    created_by_username: "testuser",
    visibility: "public",
    language: "en",
    country: "US",
    subject: "cs",
    is_published: true,
    version: 1,
    slide_count: 3,
    slides: [
      {
        id: 1,
        order: 0,
        content: "# Slide 1\n\nWelcome to the presentation",
        rendered_content: "<h1>Slide 1</h1><p>Welcome to the presentation</p>",
        notes: "Notes for slide 1",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
      {
        id: 2,
        order: 1,
        content: "# Slide 2\n\nMiddle slide content",
        rendered_content: "<h1>Slide 2</h1><p>Middle slide content</p>",
        notes: null,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
      {
        id: 3,
        order: 2,
        content: "# Slide 3\n\nThank you for watching",
        rendered_content: "<h1>Slide 3</h1><p>Thank you for watching</p>",
        notes: "Notes for slide 3",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
    ],
    remaining_slide_ids: [],
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  };

  beforeEach(() => {
    vi.resetAllMocks();
    // Mock successful API call
    vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
      mockSlideshowDetail,
    );
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("Initial Loading", () => {
    it("shows loading state initially", () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} />);
      expect(screen.getByText(/loading presentation/i)).toBeInTheDocument();
    });

    it("calls getSlideshowDetail with correct parameters", async () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      await waitFor(() => {
        expect(slideshowApi.getSlideshowDetail).toHaveBeenCalledWith(1, 3);
      });
    });

    it("displays slideshow title after loading", async () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      expect(await screen.findByText("Test Slideshow")).toBeInTheDocument();
    });

    it("displays first slide after loading", async () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      expect(await screen.findByText("Slide 1")).toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("shows error message when API call fails", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockRejectedValue(
        new Error("Failed to load slideshow"),
      );

      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      expect(
        await screen.findByText(/error loading slideshow/i),
      ).toBeInTheDocument();
    });

    it("shows go back button on error when onExit is provided", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockRejectedValue(
        new Error("Failed to load"),
      );

      const handleExit = vi.fn();
      renderWithProviders(
        <SlideshowViewer slideshowId={1} onExit={handleExit} />,
      );

      expect(
        await screen.findByRole("button", { name: /go back/i }),
      ).toBeInTheDocument();
    });
  });

  describe("Navigation", () => {
    it("navigates to next slide with arrow button", async () => {
      const user = userEvent.setup({ delay: null });
      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      expect(await screen.findByText("Slide 1")).toBeInTheDocument();

      const nextButton = screen.getByLabelText(/next slide/i);
      await user.click(nextButton);

      expect(screen.getByText("Slide 2")).toBeInTheDocument();
    });

    it("navigates to previous slide with arrow button", async () => {
      const user = userEvent.setup({ delay: null });
      renderWithProviders(<SlideshowViewer slideshowId={1} initialSlide={1} />);

      expect(await screen.findByText("Slide 2")).toBeInTheDocument();

      const prevButton = screen.getByLabelText(/previous slide/i);
      await user.click(prevButton);

      expect(screen.getByText("Slide 1")).toBeInTheDocument();
    });

    it("starts at specified initialSlide", async () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} initialSlide={2} />);

      expect(await screen.findByText("Slide 3")).toBeInTheDocument();
    });
  });

  describe("Exit Functionality", () => {
    it("shows exit button when onExit is provided", async () => {
      const handleExit = vi.fn();
      renderWithProviders(
        <SlideshowViewer slideshowId={1} onExit={handleExit} />,
      );

      expect(
        await screen.findByLabelText(/exit presentation/i),
      ).toBeInTheDocument();
    });

    it("calls onExit when exit button is clicked", async () => {
      const handleExit = vi.fn();
      const user = userEvent.setup({ delay: null });
      renderWithProviders(
        <SlideshowViewer slideshowId={1} onExit={handleExit} />,
      );

      expect(await screen.findByText("Test Slideshow")).toBeInTheDocument();

      const exitButton = screen.getByLabelText(/exit presentation/i);
      await user.click(exitButton);

      expect(handleExit).toHaveBeenCalledTimes(1);
    });

    it("does not show exit button when onExit is not provided", async () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      expect(await screen.findByText("Test Slideshow")).toBeInTheDocument();

      expect(
        screen.queryByLabelText(/exit presentation/i),
      ).not.toBeInTheDocument();
    });
  });

  describe("Fullscreen", () => {
    it("shows fullscreen button when allowFullscreen is true", async () => {
      renderWithProviders(
        <SlideshowViewer slideshowId={1} allowFullscreen={true} />,
      );

      expect(
        await screen.findByLabelText(/enter fullscreen/i),
      ).toBeInTheDocument();
    });

    it("does not show fullscreen button when allowFullscreen is false", async () => {
      renderWithProviders(
        <SlideshowViewer slideshowId={1} allowFullscreen={false} />,
      );

      expect(await screen.findByText("Test Slideshow")).toBeInTheDocument();

      expect(
        screen.queryByLabelText(/enter fullscreen/i),
      ).not.toBeInTheDocument();
    });

    it("does not show fullscreen button by default", async () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      expect(await screen.findByText("Test Slideshow")).toBeInTheDocument();

      expect(
        screen.queryByLabelText(/enter fullscreen/i),
      ).not.toBeInTheDocument();
    });
  });

  describe("Speaker Notes", () => {
    it("shows speaker notes when showNotes is true", async () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} showNotes={true} />);

      expect(await screen.findByText("Notes for slide 1")).toBeInTheDocument();
    });

    it("hides speaker notes by default", async () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      expect(await screen.findByText("Slide 1")).toBeInTheDocument();

      expect(screen.queryByText("Notes for slide 1")).not.toBeInTheDocument();
    });
  });

  describe("Progress Indicator", () => {
    it("shows progress indicator with current slide", async () => {
      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      expect(await screen.findByText("1 / 3")).toBeInTheDocument();
    });

    it("updates progress when navigating", async () => {
      const user = userEvent.setup({ delay: null });
      renderWithProviders(<SlideshowViewer slideshowId={1} />);

      expect(await screen.findByText("1 / 3")).toBeInTheDocument();

      const nextButton = screen.getByLabelText(/next slide/i);
      await user.click(nextButton);

      expect(screen.getByText("2 / 3")).toBeInTheDocument();
    });
  });
});
