import { useState, useEffect, useCallback, RefObject } from "react";

export interface UsePresentationModeOptions {
  /** Ref to the container element for fullscreen */
  containerRef: RefObject<HTMLElement | null>;
  /** Whether notes panel is open (affects bottom bar hover threshold) */
  showNotes?: boolean;
  /** Whether settings modal is open (keeps top bar visible) */
  settingsOpen?: boolean;
  /** Whether help modal is open (keeps top bar visible) */
  helpOpen?: boolean;
}

export interface UsePresentationModeReturn {
  /** Whether currently in fullscreen mode */
  isFullscreen: boolean;
  /** Toggle fullscreen on/off */
  toggleFullscreen: () => Promise<void>;
  /** Whether top bar should be visible */
  shouldShowTopBar: boolean;
  /** Whether bottom bar should be visible */
  shouldShowBottomBar: boolean;
  /** Whether top bar auto-hide is enabled */
  autoHideTopBar: boolean;
  /** Set top bar auto-hide setting */
  setAutoHideTopBar: (value: boolean) => void;
  /** Whether bottom bar auto-hide is enabled */
  autoHideBottomBar: boolean;
  /** Set bottom bar auto-hide setting */
  setAutoHideBottomBar: (value: boolean) => void;
}

const STORAGE_KEY_TOP = "slideshow-auto-hide-top";
const STORAGE_KEY_BOTTOM = "slideshow-auto-hide-bottom";

/**
 * Hook for managing presentation mode features including fullscreen
 * and auto-hiding UI bars.
 *
 * @example
 * ```tsx
 * const containerRef = useRef<HTMLDivElement>(null);
 * const {
 *   isFullscreen,
 *   toggleFullscreen,
 *   shouldShowTopBar,
 *   shouldShowBottomBar,
 *   autoHideTopBar,
 *   setAutoHideTopBar,
 *   autoHideBottomBar,
 *   setAutoHideBottomBar,
 * } = usePresentationMode({ containerRef, showNotes });
 * ```
 */
export function usePresentationMode({
  containerRef,
  showNotes = false,
  settingsOpen = false,
  helpOpen = false,
}: UsePresentationModeOptions): UsePresentationModeReturn {
  // Fullscreen state
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  // Auto-hide settings (persisted to localStorage)
  const [autoHideTopBar, setAutoHideTopBarState] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_TOP);
      return saved !== null ? JSON.parse(saved) : true;
    } catch {
      return true;
    }
  });

  const [autoHideBottomBar, setAutoHideBottomBarState] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_BOTTOM);
      return saved !== null ? JSON.parse(saved) : true;
    } catch {
      return true;
    }
  });

  // Hover state for auto-hide
  const [isTopBarHovered, setIsTopBarHovered] = useState<boolean>(false);
  const [isBottomBarHovered, setIsBottomBarHovered] = useState<boolean>(false);

  // Persist auto-hide settings
  const setAutoHideTopBar = useCallback((value: boolean) => {
    setAutoHideTopBarState(value);
    try {
      localStorage.setItem(STORAGE_KEY_TOP, JSON.stringify(value));
    } catch {
      // localStorage may be unavailable
    }
  }, []);

  const setAutoHideBottomBar = useCallback((value: boolean) => {
    setAutoHideBottomBarState(value);
    try {
      localStorage.setItem(STORAGE_KEY_BOTTOM, JSON.stringify(value));
    } catch {
      // localStorage may be unavailable
    }
  }, []);

  // Track mouse position for auto-hide
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const baseThreshold = 100; // pixels from edge to trigger show

      // Top bar
      if (autoHideTopBar) {
        setIsTopBarHovered(e.clientY < baseThreshold);
      } else {
        setIsTopBarHovered(true);
      }

      // Bottom bar - adjust threshold based on notes being open
      if (autoHideBottomBar) {
        // When notes are open, extend threshold to cover:
        // - Notes content: max-h-80 (320px) + padding/borders (~20px)
        // - Toggle button: ~48px
        // - Progress bar: ~50px
        // Total: ~440px, use 450px to be safe
        const bottomThreshold = showNotes ? 450 : baseThreshold;
        setIsBottomBarHovered(e.clientY > window.innerHeight - bottomThreshold);
      } else {
        setIsBottomBarHovered(true);
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [autoHideTopBar, autoHideBottomBar, showNotes]);

  // Toggle fullscreen
  const toggleFullscreen = useCallback(async () => {
    if (!containerRef.current) return;

    try {
      if (!document.fullscreenElement) {
        await containerRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (err) {
      console.error("Fullscreen error:", err);
      throw err; // Let caller handle the error (e.g., show toast)
    }
  }, [containerRef]);

  // Listen for fullscreen changes (e.g., user presses Esc)
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  // Compute whether bars should be visible
  const shouldShowTopBar = !autoHideTopBar || isTopBarHovered || settingsOpen || helpOpen;
  const shouldShowBottomBar = !autoHideBottomBar || isBottomBarHovered;

  return {
    isFullscreen,
    toggleFullscreen,
    shouldShowTopBar,
    shouldShowBottomBar,
    autoHideTopBar,
    setAutoHideTopBar,
    autoHideBottomBar,
    setAutoHideBottomBar,
  };
}
