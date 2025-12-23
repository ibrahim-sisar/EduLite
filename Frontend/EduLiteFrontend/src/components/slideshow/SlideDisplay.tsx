import React from "react";
import type { SlideDisplayProps } from "./types";

/**
 * SlideDisplay Component
 *
 * Renders a single slide's HTML content in the presentation viewer.
 * Shows loading state for slides that haven't been fetched yet.
 *
 * The rendered_content is pre-rendered HTML from the backend (Spellbook),
 * so it's safe to use dangerouslySetInnerHTML.
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
        <p className="text-xl text-gray-300 dark:text-gray-400 font-light">
          Loading slide {slideNumber} of {totalSlides}...
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Slide Title (if present) */}
      {slide.title && (
        <div className="mb-6 px-8">
          <h1 className="text-4xl md:text-5xl font-light text-gray-100 dark:text-white text-center tracking-tight">
            {slide.title}
          </h1>
        </div>
      )}

      {/* Slide Content */}
      <div className="flex-1 overflow-auto px-8 py-4">
        <div
          className="prose prose-lg prose-invert max-w-none
                     prose-headings:text-gray-100 prose-headings:font-light
                     prose-p:text-gray-200 prose-p:leading-relaxed
                     prose-li:text-gray-200
                     prose-strong:text-gray-100 prose-strong:font-semibold
                     prose-code:text-blue-300 prose-code:bg-gray-800/50 prose-code:px-2 prose-code:py-1 prose-code:rounded
                     prose-pre:bg-gray-800/80 prose-pre:border prose-pre:border-gray-700
                     prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
                     prose-img:rounded-lg prose-img:shadow-xl
                     prose-blockquote:border-l-blue-500 prose-blockquote:text-gray-300"
          dangerouslySetInnerHTML={{ __html: slide.rendered_content }}
        />
      </div>

      {/* Slide Number Indicator */}
      <div className="mt-auto pt-4 text-center">
        <span className="text-sm text-gray-400 dark:text-gray-500 font-light">
          Slide {slideNumber} of {totalSlides}
        </span>
      </div>
    </div>
  );
};

export default SlideDisplay;
