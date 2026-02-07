import { useState, useEffect, useMemo, useRef } from "react";
import {
  HiArrowsPointingOut,
  HiArrowLeft,
  HiArrowRight,
  HiXMark,
} from "react-icons/hi2";
import { usePreviewCache } from "../../../hooks/usePreviewCache";
import { useDarkMode } from "../../../hooks/useDarkMode";
import { previewMarkdown } from "../../../services/slideshowApi";
import toast from "react-hot-toast";
import type { EditorSlide } from "../../../types/editor.types";
import SlideContentWithCodeBlocks from "../SlideContentWithCodeBlocks";
import {
  getContentLength,
  getFontSizeClass,
  extractCodeBlocks,
} from "../../../utils/slideContent";

interface SlidePreviewProps {
  slide: EditorSlide | null;
  isVisible: boolean;
  currentIndex?: number;
  totalSlides?: number;
  onPrev?: () => void;
  onNext?: () => void;
}

export function SlidePreview({
  slide,
  isVisible,
  currentIndex = 0,
  totalSlides = 1,
  onPrev,
  onNext,
}: SlidePreviewProps) {
  const [renderedContent, setRenderedContent] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const isDarkMode = useDarkMode();

  const contentRef = useRef<HTMLDivElement>(null);
  const slideContainerRef = useRef<HTMLDivElement>(null);

  const { getCache, setCache } = usePreviewCache(slide?.tempId || "unknown");

  // SINGLE EFFECT - handles slide changes AND content changes
  useEffect(() => {
    // No slide or not visible = clear and bail
    if (!slide || !isVisible || !slide.content) {
      setRenderedContent("");
      setIsLoading(false);
      return;
    }

    // Check cache FIRST - instant return, no loading state
    const cached = getCache(slide.content);
    if (cached) {
      setRenderedContent(cached);
      setIsLoading(false);
      return;
    }

    // Not cached - debounce the fetch to avoid rate limiting
    const controller = new AbortController();
    setIsLoading(true);

    // Wait 500ms before fetching to batch rapid slide switches
    const timeoutId = setTimeout(() => {
      const fetchPreview = async () => {
        try {
          const rendered = await previewMarkdown(
            slide.content,
            controller.signal,
          );
          // Only update if this request wasn't aborted
          if (!controller.signal.aborted) {
            setRenderedContent(rendered);
            setCache(slide.content, rendered);
            setIsLoading(false);
          }
        } catch (err: any) {
          // Ignore abort errors - that's expected behavior
          if (err.name === "AbortError" || controller.signal.aborted) {
            return;
          }
          console.error("Preview fetch error:", err);
          if (!controller.signal.aborted) {
            if (err.response?.status === 429) {
              toast.error("Too many preview requests - please wait a moment");
            } else {
              toast.error("Preview unavailable");
            }
            setIsLoading(false);
          }
        }
      };

      fetchPreview();
    }, 500);

    // CLEANUP: Cancel timeout and abort request if slide changes or component unmounts
    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [slide?.tempId, slide?.content, isVisible, getCache, setCache]);

  // Extract code blocks and process HTML
  const { processedHtml, codeBlocks } = useMemo(() => {
    if (!renderedContent) return { processedHtml: "", codeBlocks: [] };
    return extractCodeBlocks(renderedContent);
  }, [renderedContent]);

  // Calculate preview font size class based on content length
  const fontSizeClass = useMemo(() => {
    if (!renderedContent) return "preview-text-lg";
    const contentLength = getContentLength(renderedContent);
    return getFontSizeClass(contentLength, "preview");
  }, [renderedContent]);

  // Keyboard shortcuts for expand/collapse
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if typing in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      if (e.key === "Escape" && isExpanded) {
        e.preventDefault();
        setIsExpanded(false);
      }
      if ((e.key === "e" || e.key === "E") && isVisible) {
        e.preventDefault();
        setIsExpanded((prev) => !prev);
      }
      // Arrow key navigation in expanded view
      if (isExpanded) {
        if (e.key === "ArrowLeft" && onPrev) {
          e.preventDefault();
          onPrev();
        }
        if (e.key === "ArrowRight" && onNext) {
          e.preventDefault();
          onNext();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isExpanded, isVisible, onPrev, onNext]);

  // Lock body scroll when expanded
  useEffect(() => {
    if (!isExpanded) return;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, [isExpanded]);

  if (!isVisible || !slide) {
    return null;
  }

  return (
    <div className="h-full flex flex-col border-l border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between">
        <div className="w-8" /> {/* Spacer for centering */}
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">
          Preview
        </h3>
        <button
          onClick={() => setIsExpanded(true)}
          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
          title="Expand preview (E)"
        >
          <HiArrowsPointingOut className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        </button>
      </div>

      {/* Preview area - fills remaining space */}
      <div
        className={`flex-1 overflow-hidden relative ${
          isDarkMode ? "bg-gray-900" : "bg-white"
        }`}
      >
        {/* Scrollable content container */}
        <div
          ref={slideContainerRef}
          className="absolute inset-0 overflow-y-auto"
        >
          <div ref={contentRef} className="flex items-start justify-center p-8">
            <div className={`w-full max-w-4xl text-center ${fontSizeClass}`}>
              <div className="text-gray-900 dark:text-white slide-content prose-headings:text-gray-900 dark:prose-headings:text-white prose-p:text-gray-900 dark:prose-p:text-white prose-li:text-gray-900 dark:prose-li:text-white">
                {renderedContent ? (
                  <SlideContentWithCodeBlocks
                    processedHtml={processedHtml}
                    codeBlocks={codeBlocks}
                    isDarkMode={isDarkMode}
                  />
                ) : (
                  <div
                    className={`text-center py-12 ${isDarkMode ? "text-gray-400" : "text-gray-500"}`}
                  >
                    <p className="text-lg">Preview will appear here</p>
                    <p className="text-sm mt-2 opacity-75">
                      Start typing to see your slide
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Loading spinner overlay */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20 dark:bg-black/40 backdrop-blur-sm z-20">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 flex flex-col items-center gap-3">
              <div className="w-12 h-12 border-4 border-blue-200 dark:border-blue-900 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Rendering preview...
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Expanded fullscreen preview */}
      {isExpanded && (
        <div
          className={`fixed inset-0 z-50 flex justify-center overflow-auto py-8 ${isDarkMode ? "bg-black" : "bg-white"}`}
        >
          {/* Floating hint and slide counter */}
          <div
            className={`fixed top-4 left-4 flex items-center gap-4 text-sm z-10 ${isDarkMode ? "text-white/60" : "text-gray-500"}`}
          >
            <span>
              Press{" "}
              <kbd
                className={`px-2 py-0.5 rounded ${isDarkMode ? "bg-white/10 text-white/80" : "bg-gray-200 text-gray-700"}`}
              >
                Esc
              </kbd>{" "}
              or{" "}
              <kbd
                className={`px-2 py-0.5 rounded ${isDarkMode ? "bg-white/10 text-white/80" : "bg-gray-200 text-gray-700"}`}
              >
                E
              </kbd>{" "}
              to close
            </span>
            <span
              className={`font-medium ${isDarkMode ? "text-white/80" : "text-gray-700"}`}
            >
              {currentIndex + 1} / {totalSlides}
            </span>
          </div>

          {/* Close button */}
          <button
            onClick={() => setIsExpanded(false)}
            className={`fixed top-4 right-4 p-2 rounded-lg transition-colors cursor-pointer z-10 ${isDarkMode ? "hover:bg-white/10" : "hover:bg-gray-200"}`}
            title="Close (Esc/E)"
          >
            <HiXMark
              className={`w-6 h-6 ${isDarkMode ? "text-white" : "text-gray-700"}`}
            />
          </button>

          {/* Full presentation-style slide display */}
          <div className="w-full max-w-6xl px-16 my-auto text-center slide-text-lg">
            <div
              className={`slide-content ${isDarkMode ? "text-white prose-headings:text-white prose-p:text-white prose-li:text-white" : "text-gray-900 prose-headings:text-gray-900 prose-p:text-gray-900 prose-li:text-gray-900"}`}
            >
              {renderedContent ? (
                <SlideContentWithCodeBlocks
                  processedHtml={processedHtml}
                  codeBlocks={codeBlocks}
                  isDarkMode={isDarkMode}
                />
              ) : (
                <div
                  className={`text-center py-12 ${isDarkMode ? "text-gray-400" : "text-gray-500"}`}
                >
                  <p className="text-lg">No content to preview</p>
                </div>
              )}
            </div>
          </div>

          {/* Navigation Arrows */}
          {onPrev && (
            <div className="fixed left-4 top-1/2 -translate-y-1/2 pointer-events-none z-10">
              <button
                onClick={onPrev}
                onWheel={(e) => {
                  const expandedContainer = e.currentTarget.closest(
                    '[class*="overflow-auto"]',
                  );
                  if (expandedContainer)
                    expandedContainer.scrollTop += e.deltaY;
                }}
                disabled={currentIndex === 0}
                className={`p-4 rounded-full backdrop-blur-lg transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shadow-lg pointer-events-auto ${isDarkMode ? "bg-gray-800/90 hover:bg-gray-700 text-gray-100 hover:text-white" : "bg-white/90 hover:bg-white text-gray-900"}`}
                aria-label="Previous slide"
                title="Previous slide (←)"
              >
                <HiArrowLeft className="w-6 h-6" />
              </button>
            </div>
          )}

          {onNext && (
            <div className="fixed right-4 top-1/2 -translate-y-1/2 pointer-events-none z-10">
              <button
                onClick={onNext}
                onWheel={(e) => {
                  const expandedContainer = e.currentTarget.closest(
                    '[class*="overflow-auto"]',
                  );
                  if (expandedContainer)
                    expandedContainer.scrollTop += e.deltaY;
                }}
                disabled={currentIndex === totalSlides - 1}
                className={`p-4 rounded-full backdrop-blur-lg transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shadow-lg pointer-events-auto ${isDarkMode ? "bg-gray-800/90 hover:bg-gray-700 text-gray-100 hover:text-white" : "bg-white/90 hover:bg-white text-gray-900"}`}
                aria-label="Next slide"
                title="Next slide (→)"
              >
                <HiArrowRight className="w-6 h-6" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
