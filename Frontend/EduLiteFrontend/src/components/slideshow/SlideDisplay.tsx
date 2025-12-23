import React from "react";
import type { SlideDisplayProps } from "./types";

/**
 * SlideDisplay Component
 *
 * Renders a single slide's HTML content in the presentation viewer.
 * Shows loading state for slides that haven't been fetched yet.
 */
const SlideDisplay: React.FC<SlideDisplayProps> = ({
  slide,
  isLoading,
  slideNumber,
  totalSlides,
}) => {
  if (isLoading || !slide) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        {/* Loading spinner */}
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mb-6"></div>
        <p className="text-xl text-gray-300 font-light">
          Loading slide {slideNumber} of {totalSlides}...
        </p>
      </div>
    );
  }

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="w-full max-w-6xl px-16 text-center space-y-12">
        {/* Slide Title (if present) */}
        {slide.title && (
          <h1 className="text-7xl font-bold text-gray-900 dark:text-white mb-16">
            {slide.title}
          </h1>
        )}

        {/* Slide Content */}
        <div
          className="text-gray-900 dark:text-white text-5xl leading-relaxed prose-headings:text-gray-900 dark:prose-headings:text-white prose-p:text-gray-900 dark:prose-p:text-white prose-li:text-gray-900 dark:prose-li:text-white"
          style={{
            fontSize: '3rem',
            lineHeight: '1.8'
          }}
          dangerouslySetInnerHTML={{ __html: slide.rendered_content }}
        />
      </div>

      {/* Slide Number Indicator */}
      <div className="absolute bottom-24 left-1/2 -translate-x-1/2">
        <span className="text-xl text-gray-500 dark:text-gray-400">
          {slideNumber} / {totalSlides}
        </span>
      </div>
    </div>
  );
};

export default SlideDisplay;
