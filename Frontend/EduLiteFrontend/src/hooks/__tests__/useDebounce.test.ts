import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useDebounce } from "../useDebounce";

describe("useDebounce", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("should return initial value immediately", () => {
    const { result } = renderHook(() => useDebounce("hello", 500));

    expect(result.current).toBe("hello");
  });

  it("should debounce value changes", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "initial", delay: 500 } },
    );

    expect(result.current).toBe("initial");

    // Change value
    rerender({ value: "updated", delay: 500 });

    // Value should NOT update immediately
    expect(result.current).toBe("initial");

    // Fast-forward time by 499ms (still within delay)
    act(() => {
      vi.advanceTimersByTime(499);
    });
    expect(result.current).toBe("initial");

    // Fast-forward by 1ms more (total 500ms)
    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current).toBe("updated");
  });

  it("should cancel previous timer on rapid changes", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "v1", delay: 500 } },
    );

    // Change to v2
    rerender({ value: "v2", delay: 500 });
    act(() => {
      vi.advanceTimersByTime(200);
    });

    // Change to v3 before v2 timer completes
    rerender({ value: "v3", delay: 500 });
    act(() => {
      vi.advanceTimersByTime(200);
    });

    // Change to v4 before v3 timer completes
    rerender({ value: "v4", delay: 500 });

    // After 500ms from v4, should show v4 (v2 and v3 timers were cancelled)
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(result.current).toBe("v4");
  });

  it("should handle delay of 0", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "initial", delay: 0 } },
    );

    rerender({ value: "updated", delay: 0 });

    // With 0 delay, should update on next tick
    act(() => {
      vi.advanceTimersByTime(0);
    });
    expect(result.current).toBe("updated");
  });

  it("should handle different data types", () => {
    // Test with number
    const { result: numberResult, rerender: numberRerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 42, delay: 100 } },
    );

    numberRerender({ value: 99, delay: 100 });
    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(numberResult.current).toBe(99);

    // Test with object
    const { result: objectResult, rerender: objectRerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: { foo: "bar" }, delay: 100 } },
    );

    const newObj = { foo: "baz" };
    objectRerender({ value: newObj, delay: 100 });
    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(objectResult.current).toEqual(newObj);

    // Test with array
    const { result: arrayResult, rerender: arrayRerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: [1, 2, 3], delay: 100 } },
    );

    const newArray = [4, 5, 6];
    arrayRerender({ value: newArray, delay: 100 });
    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(arrayResult.current).toEqual(newArray);
  });

  it("should handle delay changes", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "test", delay: 500 } },
    );

    // Change delay
    rerender({ value: "test", delay: 1000 });

    // Change value with new delay
    rerender({ value: "updated", delay: 1000 });

    // After 500ms, should NOT update (new delay is 1000ms)
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(result.current).toBe("test");

    // After 1000ms total, should update
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(result.current).toBe("updated");
  });

  it("should cleanup timer on unmount", () => {
    const { rerender, unmount } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "initial", delay: 500 } },
    );

    rerender({ value: "updated", delay: 500 });

    // Unmount before timer fires
    unmount();

    // Timer should be cleaned up, advancing time should not cause issues
    expect(() => vi.advanceTimersByTime(500)).not.toThrow();
  });

  describe("Real-world scenarios", () => {
    it("should debounce search input (typing simulation)", () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 300),
        { initialProps: { value: "" } },
      );

      // User types "hello" character by character
      const chars = ["h", "he", "hel", "hell", "hello"];

      chars.forEach((char) => {
        rerender({ value: char });
        // Wait 50ms between keystrokes (realistic typing speed)
        act(() => {
          vi.advanceTimersByTime(50);
        });
      });

      // Value should still be empty (no individual keystroke completed the 300ms delay)
      expect(result.current).toBe("");

      // Wait remaining time to complete delay (300ms from last keystroke)
      act(() => {
        vi.advanceTimersByTime(250);
      });

      // Now should show final value
      expect(result.current).toBe("hello");
    });

    it("should debounce slide content changes", () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 2000),
        { initialProps: { value: "# Title" } },
      );

      // User edits markdown
      act(() => {
        rerender({ value: "# Title\n\n" });
        vi.advanceTimersByTime(500);

        rerender({ value: "# Title\n\nParagraph 1" });
        vi.advanceTimersByTime(500);

        rerender({ value: "# Title\n\nParagraph 1\n\nParagraph 2" });
      });

      // After 1000ms (500 + 500), still showing initial
      expect(result.current).toBe("# Title");

      // Wait 2000ms from last change
      act(() => {
        vi.advanceTimersByTime(2000);
      });

      // Should show final content
      expect(result.current).toBe("# Title\n\nParagraph 1\n\nParagraph 2");
    });

    it("should handle pause in typing (debounce fires mid-session)", () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 500),
        { initialProps: { value: "" } },
      );

      // Type "hello"
      rerender({ value: "hello" });

      // Wait for debounce to fire
      act(() => {
        vi.advanceTimersByTime(500);
      });
      expect(result.current).toBe("hello");

      // User pauses, then continues typing
      act(() => {
        vi.advanceTimersByTime(1000); // Pause for 1 second
      });

      rerender({ value: "hello world" });

      // Still showing 'hello'
      expect(result.current).toBe("hello");

      // Wait for new debounce
      act(() => {
        vi.advanceTimersByTime(500);
      });
      expect(result.current).toBe("hello world");
    });
  });

  describe("Edge cases", () => {
    it("should handle null and undefined", () => {
      const { result: nullResult, rerender: nullRerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: null as string | null, delay: 100 } },
      );

      nullRerender({ value: "not null", delay: 100 });
      act(() => {
        vi.advanceTimersByTime(100);
      });
      expect(nullResult.current).toBe("not null");

      const { result: undefinedResult, rerender: undefinedRerender } =
        renderHook(({ value, delay }) => useDebounce(value, delay), {
          initialProps: { value: undefined as string | undefined, delay: 100 },
        });

      undefinedRerender({ value: "defined", delay: 100 });
      act(() => {
        vi.advanceTimersByTime(100);
      });
      expect(undefinedResult.current).toBe("defined");
    });

    it("should handle boolean values", () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: false, delay: 100 } },
      );

      rerender({ value: true, delay: 100 });
      act(() => {
        vi.advanceTimersByTime(100);
      });
      expect(result.current).toBe(true);
    });

    it("should handle same value updates", () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: "same", delay: 100 } },
      );

      // Update with same value
      rerender({ value: "same", delay: 100 });
      act(() => {
        vi.advanceTimersByTime(100);
      });

      // Should still work normally
      expect(result.current).toBe("same");
    });
  });
});
