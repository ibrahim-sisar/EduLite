import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useSlideLoader } from "../useSlideLoader";
import * as slideshowApi from "../../services/slideshowApi";
import type { SlideshowDetail, Slide } from "../../types/slideshow.types";

// Mock the slideshowApi
vi.mock("../../services/slideshowApi");

// Mock react-hot-toast
vi.mock("react-hot-toast", () => ({
  default: {
    error: vi.fn(),
  },
}));

describe("useSlideLoader", () => {
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
    slide_count: 5,
    slides: [
      {
        id: 1,
        order: 0,
        content: "# Slide 1",
        rendered_content: "<h1>Slide 1</h1>",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
      {
        id: 2,
        order: 1,
        content: "# Slide 2",
        rendered_content: "<h1>Slide 2</h1>",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
      {
        id: 3,
        order: 2,
        content: "# Slide 3",
        rendered_content: "<h1>Slide 3</h1>",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
    ],
    remaining_slide_ids: [4, 5],
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  };

  const mockSlide4: Slide = {
    id: 4,
    order: 3,
    content: "# Slide 4",
    rendered_content: "<h1>Slide 4</h1>",
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  };

  const mockSlide5: Slide = {
    id: 5,
    order: 4,
    content: "# Slide 5",
    rendered_content: "<h1>Slide 5</h1>",
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  };

  beforeEach(() => {
    vi.resetAllMocks();
    // Default mock for getSlide to prevent unhandled rejections during background loading
    vi.mocked(slideshowApi.getSlide).mockResolvedValue({
      id: 99,
      order: 99,
      content: "# Default",
      rendered_content: "<h1>Default</h1>",
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("initial loading", () => {
    it("should start in loading state", () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockImplementation(
        () => new Promise(() => {}), // Never resolves
      );

      const { result } = renderHook(() => useSlideLoader(1));

      expect(result.current.isLoading).toBe(true);
      expect(result.current.error).toBeNull();
    });

    it("should call getSlideshowDetail with correct parameters", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );

      renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(slideshowApi.getSlideshowDetail).toHaveBeenCalledWith(1, 3);
      });
    });

    it("should set slideCount after loading", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.slideCount).toBe(5);
      });
    });

    it("should set metadata after loading", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.metadata).toEqual({
          title: "Test Slideshow",
          author: "testuser",
          subject: "cs",
        });
      });
    });

    it("should populate initial slides", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        // Check that initial 3 slides are present (background loading may add more)
        expect(result.current.slides.size).toBeGreaterThanOrEqual(3);
        expect(result.current.slides.get(0)?.rendered_content).toBe(
          "<h1>Slide 1</h1>",
        );
        expect(result.current.slides.get(1)?.rendered_content).toBe(
          "<h1>Slide 2</h1>",
        );
        expect(result.current.slides.get(2)?.rendered_content).toBe(
          "<h1>Slide 3</h1>",
        );
      });
    });

    it("should set isLoading to false after initial load", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });
  });

  describe("error handling", () => {
    it("should set error when API call fails", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockRejectedValue(
        new Error("Network error"),
      );

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.error).toBe("Network error");
        expect(result.current.isLoading).toBe(false);
      });
    });

    it("should handle non-Error rejections", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockRejectedValue(
        "String error",
      );

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.error).toBe("Failed to load slideshow");
      });
    });
  });

  describe("progressive loading", () => {
    it("should load remaining slides in background", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );
      vi.mocked(slideshowApi.getSlide)
        .mockResolvedValueOnce(mockSlide4)
        .mockResolvedValueOnce(mockSlide5);

      const { result } = renderHook(() => useSlideLoader(1));

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Wait for background loading
      await waitFor(() => {
        expect(result.current.slides.size).toBe(5);
      });

      expect(result.current.slides.get(3)?.rendered_content).toBe(
        "<h1>Slide 4</h1>",
      );
      expect(result.current.slides.get(4)?.rendered_content).toBe(
        "<h1>Slide 5</h1>",
      );
    });

    it("should not call getSlide when no remaining slides", async () => {
      const noRemainingSlides = {
        ...mockSlideshowDetail,
        remaining_slide_ids: [],
      };
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        noRemainingSlides,
      );

      renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(slideshowApi.getSlideshowDetail).toHaveBeenCalled();
      });

      // Give time for any potential getSlide calls
      await new Promise((resolve) => setTimeout(resolve, 50));

      expect(slideshowApi.getSlide).not.toHaveBeenCalled();
    });

    it("should handle partial failures in background loading gracefully", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );
      vi.mocked(slideshowApi.getSlide)
        .mockResolvedValueOnce(mockSlide4)
        .mockRejectedValueOnce(new Error("Failed to load slide 5"));

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Wait for background loading
      await waitFor(() => {
        expect(result.current.slides.size).toBe(4); // 3 initial + 1 successful background
      });

      expect(result.current.slides.has(3)).toBe(true);
      expect(result.current.slides.has(4)).toBe(false); // Failed to load
    });
  });

  describe("isSlideLoaded", () => {
    it("should return true for loaded slides", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.isSlideLoaded(0)).toBe(true);
      expect(result.current.isSlideLoaded(1)).toBe(true);
      expect(result.current.isSlideLoaded(2)).toBe(true);
    });

    it("should return false for unloaded slides", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Before background loading completes
      expect(result.current.isSlideLoaded(3)).toBe(false);
      expect(result.current.isSlideLoaded(4)).toBe(false);
    });
  });

  describe("getLoadedSlides", () => {
    it("should return array of loaded status", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const loadedSlides = result.current.getLoadedSlides();

      expect(loadedSlides).toHaveLength(5);
      expect(loadedSlides[0]).toBe(true);
      expect(loadedSlides[1]).toBe(true);
      expect(loadedSlides[2]).toBe(true);
      expect(loadedSlides[3]).toBe(false);
      expect(loadedSlides[4]).toBe(false);
    });

    it("should update as slides load", async () => {
      vi.mocked(slideshowApi.getSlideshowDetail).mockResolvedValue(
        mockSlideshowDetail,
      );
      vi.mocked(slideshowApi.getSlide)
        .mockResolvedValueOnce(mockSlide4)
        .mockResolvedValueOnce(mockSlide5);

      const { result } = renderHook(() => useSlideLoader(1));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await waitFor(() => {
        const loadedSlides = result.current.getLoadedSlides();
        expect(loadedSlides.every((loaded) => loaded)).toBe(true);
      });
    });
  });

  describe("slideshowId changes", () => {
    it("should reload when slideshowId changes", async () => {
      const slideshow2: SlideshowDetail = {
        ...mockSlideshowDetail,
        id: 2,
        title: "Slideshow 2",
        slide_count: 2,
        slides: [
          {
            id: 10,
            order: 0,
            content: "# New Slide 1",
            rendered_content: "<h1>New Slide 1</h1>",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
          {
            id: 11,
            order: 1,
            content: "# New Slide 2",
            rendered_content: "<h1>New Slide 2</h1>",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
        ],
        remaining_slide_ids: [],
      };

      vi.mocked(slideshowApi.getSlideshowDetail)
        .mockResolvedValueOnce(mockSlideshowDetail)
        .mockResolvedValueOnce(slideshow2);

      const { result, rerender } = renderHook(({ id }) => useSlideLoader(id), {
        initialProps: { id: 1 },
      });

      await waitFor(() => {
        expect(result.current.metadata.title).toBe("Test Slideshow");
      });

      rerender({ id: 2 });

      await waitFor(() => {
        expect(result.current.metadata.title).toBe("Slideshow 2");
        expect(result.current.slideCount).toBe(2);
      });
    });
  });
});
