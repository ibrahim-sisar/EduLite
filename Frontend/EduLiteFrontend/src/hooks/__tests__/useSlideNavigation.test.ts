import { describe, it, expect } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useSlideNavigation } from "../useSlideNavigation";

describe("useSlideNavigation", () => {
  describe("initialization", () => {
    it("should start at initialSlide when provided", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 2 })
      );

      expect(result.current.currentIndex).toBe(2);
    });

    it("should default to slide 0 when no initialSlide provided", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5 })
      );

      expect(result.current.currentIndex).toBe(0);
    });

    it("should clamp initialSlide to valid range (too high)", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 10 })
      );

      expect(result.current.currentIndex).toBe(4); // Last valid index
    });

    it("should clamp initialSlide to valid range (negative)", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: -5 })
      );

      expect(result.current.currentIndex).toBe(0);
    });

    it("should handle zero slides", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 0 })
      );

      expect(result.current.currentIndex).toBe(0);
      expect(result.current.isFirst).toBe(true);
      expect(result.current.isLast).toBe(true);
    });
  });

  describe("next()", () => {
    it("should navigate to next slide", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 0 })
      );

      act(() => {
        result.current.next();
      });

      expect(result.current.currentIndex).toBe(1);
    });

    it("should not go past last slide", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 4 })
      );

      act(() => {
        result.current.next();
      });

      expect(result.current.currentIndex).toBe(4);
    });

    it("should navigate multiple times", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 0 })
      );

      act(() => {
        result.current.next();
        result.current.next();
        result.current.next();
      });

      expect(result.current.currentIndex).toBe(3);
    });
  });

  describe("prev()", () => {
    it("should navigate to previous slide", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 3 })
      );

      act(() => {
        result.current.prev();
      });

      expect(result.current.currentIndex).toBe(2);
    });

    it("should not go before first slide", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 0 })
      );

      act(() => {
        result.current.prev();
      });

      expect(result.current.currentIndex).toBe(0);
    });

    it("should navigate multiple times", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 4 })
      );

      act(() => {
        result.current.prev();
        result.current.prev();
      });

      expect(result.current.currentIndex).toBe(2);
    });
  });

  describe("goToSlide()", () => {
    it("should navigate to specific slide", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 0 })
      );

      act(() => {
        result.current.goToSlide(3);
      });

      expect(result.current.currentIndex).toBe(3);
    });

    it("should clamp to last slide when index too high", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 0 })
      );

      act(() => {
        result.current.goToSlide(100);
      });

      expect(result.current.currentIndex).toBe(4);
    });

    it("should clamp to first slide when index negative", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 2 })
      );

      act(() => {
        result.current.goToSlide(-10);
      });

      expect(result.current.currentIndex).toBe(0);
    });

    it("should handle zero slideCount gracefully", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 0 })
      );

      act(() => {
        result.current.goToSlide(5);
      });

      expect(result.current.currentIndex).toBe(0);
    });
  });

  describe("isFirst and isLast", () => {
    it("should be isFirst when at index 0", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 0 })
      );

      expect(result.current.isFirst).toBe(true);
      expect(result.current.isLast).toBe(false);
    });

    it("should be isLast when at last index", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 5, initialSlide: 4 })
      );

      expect(result.current.isFirst).toBe(false);
      expect(result.current.isLast).toBe(true);
    });

    it("should be both isFirst and isLast with single slide", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 1, initialSlide: 0 })
      );

      expect(result.current.isFirst).toBe(true);
      expect(result.current.isLast).toBe(true);
    });

    it("should update after navigation", () => {
      const { result } = renderHook(() =>
        useSlideNavigation({ slideCount: 3, initialSlide: 0 })
      );

      expect(result.current.isFirst).toBe(true);

      act(() => {
        result.current.next();
      });

      expect(result.current.isFirst).toBe(false);
      expect(result.current.isLast).toBe(false);

      act(() => {
        result.current.next();
      });

      expect(result.current.isLast).toBe(true);
    });
  });

  describe("slideCount changes", () => {
    it("should respect new slideCount for bounds", () => {
      const { result, rerender } = renderHook(
        ({ slideCount }) => useSlideNavigation({ slideCount, initialSlide: 0 }),
        { initialProps: { slideCount: 10 } }
      );

      act(() => {
        result.current.goToSlide(8);
      });

      expect(result.current.currentIndex).toBe(8);

      // Reduce slide count - goToSlide should now respect new bounds
      rerender({ slideCount: 5 });

      // Try to navigate beyond new bounds
      act(() => {
        result.current.goToSlide(10);
      });

      expect(result.current.currentIndex).toBe(4); // Clamped to new max
    });
  });
});
