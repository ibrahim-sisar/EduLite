import React, { useMemo, useRef, useEffect, useState } from "react";
import { HiChevronDown } from "react-icons/hi2";
import type { SlideDisplayProps } from "./types";
import CodeBlock from "./CodeBlock";

/**
 * Calculate content length from HTML string (strips tags)
 */
const getContentLength = (html: string): number => {
  const tmp = document.createElement("div");
  tmp.innerHTML = html;
  return tmp.textContent?.length || 0;
};

/**
 * Determine font size class based on content length
 */
const getFontSizeClass = (contentLength: number): string => {
  if (contentLength < 100) return "slide-text-xl"; // Very short: 2.5rem (40px)
  if (contentLength < 300) return "slide-text-lg"; // Short: 2rem (32px)
  if (contentLength < 600) return "slide-text-md"; // Medium: 1.5rem (24px)
  if (contentLength < 1000) return "slide-text-sm"; // Long: 1.25rem (20px)
  return "slide-text-xs"; // Very long: 1.1rem (17.6px)
};

/**
 * Extract code blocks from HTML and return structured data
 */
interface CodeBlockData {
  id: string;
  code: string;
  language: string;
}

const extractCodeBlocks = (
  html: string,
): { processedHtml: string; codeBlocks: CodeBlockData[] } => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");
  const codeBlocks: CodeBlockData[] = [];

  // Find all <pre><code> blocks
  const preElements = doc.querySelectorAll("pre");

  preElements.forEach((pre, index) => {
    const codeElement = pre.querySelector("code");
    if (codeElement) {
      const codeText = codeElement.textContent || "";

      // Extract language from class (e.g., "language-javascript")
      const className = codeElement.className || "";
      const languageMatch = className.match(/language-(\w+)/);
      const language = languageMatch ? languageMatch[1] : "text";

      // Create unique ID for this code block
      const id = `code-block-${index}`;

      codeBlocks.push({
        id,
        code: codeText,
        language,
      });

      // Replace the <pre> element with a placeholder div
      const placeholder = doc.createElement("div");
      placeholder.setAttribute("data-code-block-id", id);
      placeholder.className = "code-block-placeholder";
      pre.replaceWith(placeholder);
    }
  });

  return {
    processedHtml: doc.body.innerHTML,
    codeBlocks,
  };
};

/**
 * Component to render HTML content with injected CodeBlock components
 */
interface SlideContentWithCodeBlocksProps {
  processedHtml: string;
  codeBlocks: CodeBlockData[];
  isDarkMode: boolean;
}

const SlideContentWithCodeBlocks: React.FC<SlideContentWithCodeBlocksProps> = ({
  processedHtml,
  codeBlocks,
  isDarkMode,
}) => {
  const contentContainerRef = useRef<HTMLDivElement>(null);
  const accordionStatesRef = useRef<Map<number, boolean>>(new Map());

  // Add accordion functionality and remove inline onclick handlers
  useEffect(() => {
    if (!contentContainerRef.current) return;

    const container = contentContainerRef.current;

    // Remove inline onclick attributes from accordion buttons and restore state
    const accordionButtons = container.querySelectorAll(".sb-accordion-toggle");
    accordionButtons.forEach((button, index) => {
      button.removeAttribute("onclick");

      // Restore previous state if it exists
      const savedState = accordionStatesRef.current.get(index);
      if (savedState !== undefined) {
        button.setAttribute("aria-expanded", savedState ? "true" : "false");
        const content = button.nextElementSibling;
        if (content && content.classList.contains("sb-accordion-content")) {
          content.setAttribute("aria-hidden", savedState ? "false" : "true");
        }
      }
    });

    const handleAccordionClick = (e: Event) => {
      const target = e.target as HTMLElement;
      const button = target.closest(".sb-accordion-toggle");

      if (button) {
        e.preventDefault();
        e.stopPropagation();

        const isExpanded = button.getAttribute("aria-expanded") === "true";
        const newState = !isExpanded;

        button.setAttribute("aria-expanded", newState ? "true" : "false");

        const content = button.nextElementSibling;
        if (content && content.classList.contains("sb-accordion-content")) {
          content.setAttribute("aria-hidden", newState ? "false" : "true");
        }

        // Save the state
        const allButtons = Array.from(
          container.querySelectorAll(".sb-accordion-toggle"),
        );
        const index = allButtons.indexOf(button as Element);
        if (index !== -1) {
          accordionStatesRef.current.set(index, newState);
        }
      }
    };

    container.addEventListener("click", handleAccordionClick);

    return () => {
      container.removeEventListener("click", handleAccordionClick);
    };
  }, [processedHtml, isDarkMode]); // Re-run when theme changes

  // Split HTML by code block placeholders and render parts with code blocks
  const parts = useMemo(() => {
    const result: React.ReactNode[] = [];
    let currentHtml = processedHtml;

    // Create a map of code blocks by ID for quick lookup
    const codeBlockMap = new Map(codeBlocks.map((cb) => [cb.id, cb]));

    // Split by placeholder divs
    const placeholderRegex =
      /<div[^>]*data-code-block-id="([^"]+)"[^>]*><\/div>/g;
    let lastIndex = 0;
    let match;

    while ((match = placeholderRegex.exec(currentHtml)) !== null) {
      const [fullMatch, codeBlockId] = match;
      const matchIndex = match.index;

      // Add HTML before this code block
      if (matchIndex > lastIndex) {
        const htmlPart = currentHtml.substring(lastIndex, matchIndex);
        result.push(
          <div
            key={`html-${lastIndex}`}
            dangerouslySetInnerHTML={{ __html: htmlPart }}
          />,
        );
      }

      // Add the code block component
      const codeBlockData = codeBlockMap.get(codeBlockId);
      if (codeBlockData) {
        result.push(
          <CodeBlock
            key={codeBlockId}
            code={codeBlockData.code}
            language={codeBlockData.language}
            isDarkMode={isDarkMode}
          />,
        );
      }

      lastIndex = matchIndex + fullMatch.length;
    }

    // Add remaining HTML after last code block
    if (lastIndex < currentHtml.length) {
      const htmlPart = currentHtml.substring(lastIndex);
      result.push(
        <div
          key={`html-${lastIndex}`}
          dangerouslySetInnerHTML={{ __html: htmlPart }}
        />,
      );
    }

    return result;
  }, [processedHtml, codeBlocks, isDarkMode]);

  return <div ref={contentContainerRef}>{parts}</div>;
};

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
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Detect dark mode
  useEffect(() => {
    const checkDarkMode = () => {
      setIsDarkMode(document.documentElement.classList.contains("dark"));
    };

    checkDarkMode();

    // Watch for dark mode changes
    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
  }, []);

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
      const scrollThreshold = 200; // Hide hint after scrolling 200px

      // Calculate distance from bottom
      const distanceFromBottom = scrollHeight - scrollPosition - clientHeight;

      // Only hide if scrolled down AND very close to bottom (within 20px)
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
        {/* Loading spinner */}
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
        {/* Slide Content */}
        <div className="text-gray-900 dark:text-white slide-content prose-headings:text-gray-900 dark:prose-headings:text-white prose-p:text-gray-900 dark:prose-p:text-white prose-li:text-gray-900 dark:prose-li:text-white">
          <SlideContentWithCodeBlocks
            processedHtml={processedHtml}
            codeBlocks={codeBlocks}
            isDarkMode={isDarkMode}
          />
        </div>
      </div>

      {/* Scroll Hint - Shows when content overflows */}
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
