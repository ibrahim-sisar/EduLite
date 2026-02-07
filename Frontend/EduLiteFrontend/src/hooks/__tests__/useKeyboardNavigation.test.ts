import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { useKeyboardNavigation } from "../useKeyboardNavigation";

describe("useKeyboardNavigation", () => {
  const mockCallbacks = {
    onNext: vi.fn(),
    onPrev: vi.fn(),
    onGoToSlide: vi.fn(),
    onToggleFullscreen: vi.fn(),
    onExit: vi.fn(),
  };

  const fireKeyDown = (key: string) => {
    const event = new KeyboardEvent("keydown", { key, bubbles: true });
    vi.spyOn(event, "preventDefault");
    window.dispatchEvent(event);
    return event;
  };

  beforeEach(() => {
    vi.resetAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("next slide navigation", () => {
    it("should call onNext when ArrowRight is pressed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown("ArrowRight");

      expect(mockCallbacks.onNext).toHaveBeenCalledTimes(1);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    it("should call onNext when Space is pressed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown(" ");

      expect(mockCallbacks.onNext).toHaveBeenCalledTimes(1);
      expect(event.preventDefault).toHaveBeenCalled();
    });
  });

  describe("previous slide navigation", () => {
    it("should call onPrev when ArrowLeft is pressed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown("ArrowLeft");

      expect(mockCallbacks.onPrev).toHaveBeenCalledTimes(1);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    it("should call onPrev when Backspace is pressed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown("Backspace");

      expect(mockCallbacks.onPrev).toHaveBeenCalledTimes(1);
      expect(event.preventDefault).toHaveBeenCalled();
    });
  });

  describe("first/last slide navigation", () => {
    it("should call onGoToSlide(0) when Home is pressed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown("Home");

      expect(mockCallbacks.onGoToSlide).toHaveBeenCalledWith(0);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    it("should call onGoToSlide(slideCount - 1) when End is pressed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown("End");

      expect(mockCallbacks.onGoToSlide).toHaveBeenCalledWith(9);
      expect(event.preventDefault).toHaveBeenCalled();
    });
  });

  describe("number key navigation", () => {
    it("should navigate to slide 0 when 1 is pressed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown("1");

      expect(mockCallbacks.onGoToSlide).toHaveBeenCalledWith(0);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    it("should navigate to slide 4 when 5 is pressed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown("5");

      expect(mockCallbacks.onGoToSlide).toHaveBeenCalledWith(4);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    it("should navigate to slide 8 when 9 is pressed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown("9");

      expect(mockCallbacks.onGoToSlide).toHaveBeenCalledWith(8);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    it("should not navigate when number exceeds slideCount", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 3,
        }),
      );

      fireKeyDown("5");

      expect(mockCallbacks.onGoToSlide).not.toHaveBeenCalled();
    });
  });

  describe("fullscreen toggle", () => {
    it("should call onToggleFullscreen when f is pressed and allowed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
          allowFullscreen: true,
        }),
      );

      const event = fireKeyDown("f");

      expect(mockCallbacks.onToggleFullscreen).toHaveBeenCalledTimes(1);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    it("should call onToggleFullscreen when F is pressed and allowed", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
          allowFullscreen: true,
        }),
      );

      const event = fireKeyDown("F");

      expect(mockCallbacks.onToggleFullscreen).toHaveBeenCalledTimes(1);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    it("should not call onToggleFullscreen when allowFullscreen is false", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
          allowFullscreen: false,
        }),
      );

      fireKeyDown("f");

      expect(mockCallbacks.onToggleFullscreen).not.toHaveBeenCalled();
    });

    it("should not call onToggleFullscreen when not provided", () => {
      renderHook(() =>
        useKeyboardNavigation({
          onNext: mockCallbacks.onNext,
          onPrev: mockCallbacks.onPrev,
          onGoToSlide: mockCallbacks.onGoToSlide,
          slideCount: 10,
          allowFullscreen: true,
        }),
      );

      fireKeyDown("f");

      // Should not throw, just silently do nothing
      expect(mockCallbacks.onToggleFullscreen).not.toHaveBeenCalled();
    });
  });

  describe("escape key", () => {
    it("should call onExit when Escape is pressed and not in fullscreen", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      const event = fireKeyDown("Escape");

      expect(mockCallbacks.onExit).toHaveBeenCalledTimes(1);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    it("should exit fullscreen when Escape is pressed in fullscreen mode", () => {
      // Mock fullscreen state
      const exitFullscreenMock = vi.fn();
      Object.defineProperty(document, "fullscreenElement", {
        value: document.createElement("div"),
        configurable: true,
      });
      document.exitFullscreen = exitFullscreenMock;

      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      fireKeyDown("Escape");

      expect(exitFullscreenMock).toHaveBeenCalled();
      expect(mockCallbacks.onExit).not.toHaveBeenCalled();

      // Restore
      Object.defineProperty(document, "fullscreenElement", {
        value: null,
        configurable: true,
      });
    });
  });

  describe("enabled flag", () => {
    it("should not respond to keys when disabled", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
          enabled: false,
        }),
      );

      fireKeyDown("ArrowRight");
      fireKeyDown("ArrowLeft");

      expect(mockCallbacks.onNext).not.toHaveBeenCalled();
      expect(mockCallbacks.onPrev).not.toHaveBeenCalled();
    });

    it("should respond to keys when enabled", () => {
      renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
          enabled: true,
        }),
      );

      fireKeyDown("ArrowRight");

      expect(mockCallbacks.onNext).toHaveBeenCalledTimes(1);
    });
  });

  describe("cleanup", () => {
    it("should remove event listener on unmount", () => {
      const removeEventListenerSpy = vi.spyOn(window, "removeEventListener");

      const { unmount } = renderHook(() =>
        useKeyboardNavigation({
          ...mockCallbacks,
          slideCount: 10,
        }),
      );

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith(
        "keydown",
        expect.any(Function),
      );

      removeEventListenerSpy.mockRestore();
    });
  });
});
