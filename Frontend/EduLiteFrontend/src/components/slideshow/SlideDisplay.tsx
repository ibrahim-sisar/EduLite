import React, { useMemo, useRef, useEffect, useState } from "react";
import { HiChevronDown } from "react-icons/hi2";
import type { SlideDisplayProps } from "./types";
import SlideContentWithCodeBlocks from "./SlideContentWithCodeBlocks";
import { useDarkMode } from "../../hooks/useDarkMode";
import {
  getContentLength,
  getFontSizeClass,
  extractCodeBlocks,
} from "../../utils/slideContent";

/**
 * SlideDisplay Component
 *
 * Renders a single slide's HTML content in the presentation viewer.
 * Shows loading state for slides that haven't been fetched yet.
 * Auto-scales font size based on content length.
 * Detects overflow and enables scrolling with visual indicators.
 */
const SlideDisplay: React.FC<SlideDisplayProps> = ({
  slide,
  isLoading,
  slideNumber,
  totalSlides,
}) => {
  const contentRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isOverflowing, setIsOverflowing] = useState(false);
  const [showScrollHint, setShowScrollHint] = useState(true);
  const isDarkMode = useDarkMode();

  // Extract code blocks and process HTML
  const { processedHtml, codeBlocks } = useMemo(() => {
    if (!slide) return { processedHtml: "", codeBlocks: [] };
    return extractCodeBlocks(slide.rendered_content);
  }, [slide]);

  // Calculate content length and determine font size class
  const fontSizeClass = useMemo(() => {
    if (!slide) return "slide-text-lg";
    const contentLength = getContentLength(slide.rendered_content);
    return getFontSizeClass(contentLength);
  }, [slide]);

  // Check for overflow and reset scroll position when slide changes
  useEffect(() => {
    if (!contentRef.current || !containerRef.current) return;

    // Reset scroll to top
    if (containerRef.current) {
      containerRef.current.scrollTop = 0;
      setShowScrollHint(true);
    }

    // Check if content overflows container
    const checkOverflow = () => {
      if (contentRef.current && containerRef.current) {
        const isContentOverflowing =
          contentRef.current.scrollHeight > containerRef.current.clientHeight;
        setIsOverflowing(isContentOverflowing);
      }
    };

    // Check immediately and after a short delay (for content to render)
    checkOverflow();
    const timer = setTimeout(checkOverflow, 100);

    return () => clearTimeout(timer);
  }, [slide, fontSizeClass]);

  // Hide scroll hint when user scrolls
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const scrollPosition = container.scrollTop;
      const scrollHeight = container.scrollHeight;
      const clientHeight = container.clientHeight;
      const scrollThreshold = 200;

      const distanceFromBottom = scrollHeight - scrollPosition - clientHeight;

      if (scrollPosition > scrollThreshold && distanceFromBottom < 20) {
        setShowScrollHint(false);
      } else if (scrollPosition < scrollThreshold) {
        setShowScrollHint(true);
      }
    };

    container.addEventListener("scroll", handleScroll);
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  if (isLoading || !slide) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mb-6"></div>
        <p className="text-xl text-gray-300 dark:text-gray-400 font-light">
          Loading slide {slideNumber} of {totalSlides}...
        </p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`absolute inset-0 ${
        isOverflowing
          ? "overflow-y-auto flex justify-center py-8"
          : "overflow-hidden flex items-center justify-center py-8"
      }`}
    >
      <div
        ref={contentRef}
        className={`w-full max-w-6xl px-16 my-auto text-center ${fontSizeClass}`}
      >
        <div className="text-gray-900 dark:text-white slide-content prose-headings:text-gray-900 dark:prose-headings:text-white prose-p:text-gray-900 dark:prose-p:text-white prose-li:text-gray-900 dark:prose-li:text-white">
          <SlideContentWithCodeBlocks
            processedHtml={processedHtml}
            codeBlocks={codeBlocks}
            isDarkMode={isDarkMode}
          />
        </div>
      </div>

      {isOverflowing && showScrollHint && (
        <button
          onClick={() => {
            if (containerRef.current) {
              containerRef.current.scrollTo({
                top: containerRef.current.scrollHeight,
                behavior: "smooth",
              });
            }
          }}
          className="fixed bottom-8 right-8 z-[60] p-2 rounded-full bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors cursor-pointer shadow-lg"
          aria-label="Scroll to bottom"
        >
          <HiChevronDown className="w-6 h-6 text-gray-700 dark:text-gray-300" />
        </button>
      )}
    </div>
  );
};

export default SlideDisplay;
