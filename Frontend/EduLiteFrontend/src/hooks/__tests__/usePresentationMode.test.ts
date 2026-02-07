import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { usePresentationMode } from "../usePresentationMode";

describe("usePresentationMode", () => {
  let mockContainerRef: { current: HTMLDivElement | null };

  beforeEach(() => {
    // Create a mock container element
    mockContainerRef = { current: document.createElement("div") };

    // Clear localStorage
    localStorage.clear();

    // Reset fullscreen state
    Object.defineProperty(document, "fullscreenElement", {
      value: null,
      configurable: true,
      writable: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe("auto-hide settings initialization", () => {
    it("should default to auto-hide enabled for both bars", () => {
      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      expect(result.current.autoHideTopBar).toBe(true);
      expect(result.current.autoHideBottomBar).toBe(true);
    });

    it("should load saved settings from localStorage", () => {
      localStorage.setItem("slideshow-auto-hide-top", "false");
      localStorage.setItem("slideshow-auto-hide-bottom", "false");

      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      expect(result.current.autoHideTopBar).toBe(false);
      expect(result.current.autoHideBottomBar).toBe(false);
    });

    it("should handle corrupted localStorage gracefully", () => {
      localStorage.setItem("slideshow-auto-hide-top", "not-valid-json{");

      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      // Should fall back to default
      expect(result.current.autoHideTopBar).toBe(true);
    });
  });

  describe("setAutoHideTopBar", () => {
    it("should update state and persist to localStorage", () => {
      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      act(() => {
        result.current.setAutoHideTopBar(false);
      });

      expect(result.current.autoHideTopBar).toBe(false);
      expect(localStorage.getItem("slideshow-auto-hide-top")).toBe("false");
    });
  });

  describe("setAutoHideBottomBar", () => {
    it("should update state and persist to localStorage", () => {
      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      act(() => {
        result.current.setAutoHideBottomBar(false);
      });

      expect(result.current.autoHideBottomBar).toBe(false);
      expect(localStorage.getItem("slideshow-auto-hide-bottom")).toBe("false");
    });
  });

  describe("shouldShowTopBar", () => {
    it("should always show when autoHideTopBar is false", () => {
      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      act(() => {
        result.current.setAutoHideTopBar(false);
      });

      expect(result.current.shouldShowTopBar).toBe(true);
    });

    it("should show when settingsOpen is true", () => {
      const { result } = renderHook(() =>
        usePresentationMode({
          containerRef: mockContainerRef,
          settingsOpen: true,
        }),
      );

      expect(result.current.shouldShowTopBar).toBe(true);
    });

    it("should show when helpOpen is true", () => {
      const { result } = renderHook(() =>
        usePresentationMode({
          containerRef: mockContainerRef,
          helpOpen: true,
        }),
      );

      expect(result.current.shouldShowTopBar).toBe(true);
    });
  });

  describe("shouldShowBottomBar", () => {
    it("should always show when autoHideBottomBar is false", () => {
      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      act(() => {
        result.current.setAutoHideBottomBar(false);
      });

      expect(result.current.shouldShowBottomBar).toBe(true);
    });
  });

  describe("mouse hover tracking", () => {
    it("should show top bar when mouse is near top edge", () => {
      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      // Simulate mouse move near top
      act(() => {
        const event = new MouseEvent("mousemove", {
          clientY: 50, // Within 100px threshold
          bubbles: true,
        });
        window.dispatchEvent(event);
      });

      expect(result.current.shouldShowTopBar).toBe(true);
    });

    it("should hide top bar when mouse is away from top edge", () => {
      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      // Simulate mouse move away from top
      act(() => {
        const event = new MouseEvent("mousemove", {
          clientY: 500, // Beyond 100px threshold
          bubbles: true,
        });
        window.dispatchEvent(event);
      });

      expect(result.current.shouldShowTopBar).toBe(false);
    });

    it("should show bottom bar when mouse is near bottom edge", () => {
      // Mock window.innerHeight
      Object.defineProperty(window, "innerHeight", {
        value: 800,
        configurable: true,
      });

      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      // Simulate mouse move near bottom
      act(() => {
        const event = new MouseEvent("mousemove", {
          clientY: 750, // Within 100px of bottom (800 - 100 = 700)
          bubbles: true,
        });
        window.dispatchEvent(event);
      });

      expect(result.current.shouldShowBottomBar).toBe(true);
    });
  });

  describe("fullscreen", () => {
    it("should start not in fullscreen", () => {
      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      expect(result.current.isFullscreen).toBe(false);
    });

    it("should toggle fullscreen on", async () => {
      const requestFullscreenMock = vi.fn().mockResolvedValue(undefined);
      mockContainerRef.current!.requestFullscreen = requestFullscreenMock;

      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      await act(async () => {
        await result.current.toggleFullscreen();
      });

      expect(requestFullscreenMock).toHaveBeenCalled();
      expect(result.current.isFullscreen).toBe(true);
    });

    it("should toggle fullscreen off", async () => {
      // Start in fullscreen
      Object.defineProperty(document, "fullscreenElement", {
        value: mockContainerRef.current,
        configurable: true,
      });

      const exitFullscreenMock = vi.fn().mockResolvedValue(undefined);
      document.exitFullscreen = exitFullscreenMock;

      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      await act(async () => {
        await result.current.toggleFullscreen();
      });

      expect(exitFullscreenMock).toHaveBeenCalled();
      expect(result.current.isFullscreen).toBe(false);
    });

    it("should handle fullscreen errors", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});
      const requestFullscreenMock = vi
        .fn()
        .mockRejectedValue(new Error("Fullscreen denied"));
      mockContainerRef.current!.requestFullscreen = requestFullscreenMock;

      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      await expect(
        act(async () => {
          await result.current.toggleFullscreen();
        }),
      ).rejects.toThrow("Fullscreen denied");

      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });

    it("should do nothing when containerRef is null", async () => {
      const nullRef = { current: null };

      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: nullRef }),
      );

      // Should not throw
      await act(async () => {
        await result.current.toggleFullscreen();
      });

      expect(result.current.isFullscreen).toBe(false);
    });

    it("should update isFullscreen on fullscreenchange event", () => {
      const { result } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      expect(result.current.isFullscreen).toBe(false);

      // Simulate entering fullscreen
      act(() => {
        Object.defineProperty(document, "fullscreenElement", {
          value: mockContainerRef.current,
          configurable: true,
        });
        document.dispatchEvent(new Event("fullscreenchange"));
      });

      expect(result.current.isFullscreen).toBe(true);

      // Simulate exiting fullscreen
      act(() => {
        Object.defineProperty(document, "fullscreenElement", {
          value: null,
          configurable: true,
        });
        document.dispatchEvent(new Event("fullscreenchange"));
      });

      expect(result.current.isFullscreen).toBe(false);
    });
  });

  describe("cleanup", () => {
    it("should remove mousemove listener on unmount", () => {
      const removeEventListenerSpy = vi.spyOn(window, "removeEventListener");

      const { unmount } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "mousemove",
        expect.any(Function),
      );

      removeEventListenerSpy.mockRestore();
    });

    it("should remove fullscreenchange listener on unmount", () => {
      const removeEventListenerSpy = vi.spyOn(document, "removeEventListener");

      const { unmount } = renderHook(() =>
        usePresentationMode({ containerRef: mockContainerRef }),
      );

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "fullscreenchange",
        expect.any(Function),
      );

      removeEventListenerSpy.mockRestore();
    });
  });
});
