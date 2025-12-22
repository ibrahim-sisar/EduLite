import React from "react";
import type { SlideProgressProps } from "./types";

/**
 * SlideProgress Component
 *
 * Displays a progress indicator with clickable dots representing each slide.
 * Shows which slides are loaded vs. still loading.
 * Current slide is highlighted.
 */
const SlideProgress: React.FC<SlideProgressProps> = ({
  currentIndex,
  totalSlides,
  loadedSlides,
  onSlideClick,
}) => {
  // For large slide decks, show condensed view
  const showCondensed = totalSlides > 20;

  if (showCondensed) {
    // Show just the text indicator for large decks
    return (
      <div className="flex items-center justify-center gap-4 px-4 py-3 bg-gray-900/80 dark:bg-black/80 backdrop-blur-lg border-t border-gray-700/30">
        <div className="flex items-center gap-2">
          <div className="h-2 w-32 bg-gray-700/50 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-300 ease-out"
              style={{ width: `${((currentIndex + 1) / totalSlides) * 100}%` }}
            />
          </div>
          <span className="text-sm text-gray-300 font-light whitespace-nowrap">
            {currentIndex + 1} / {totalSlides}
          </span>
        </div>
      </div>
    );
  }

  // Show individual dots for smaller decks
  return (
    <div className="flex items-center justify-center gap-2 px-4 py-3 bg-gray-900/80 dark:bg-black/80 backdrop-blur-lg border-t border-gray-700/30">
      {/* Slide dots */}
      <div className="flex items-center gap-2 flex-wrap justify-center max-w-4xl">
        {Array.from({ length: totalSlides }, (_, index) => {
          const isCurrentSlide = index === currentIndex;
          const isLoaded = loadedSlides[index];

          return (
            <button
              key={index}
              onClick={() => onSlideClick(index)}
              className={`
                relative rounded-full transition-all duration-200 cursor-pointer
                ${isCurrentSlide ? "w-10 h-3" : "w-3 h-3"}
                ${
                  isCurrentSlide
                    ? "bg-blue-500"
                    : isLoaded
                    ? "bg-gray-500 hover:bg-gray-400"
                    : "bg-gray-700 hover:bg-gray-600"
                }
                ${isCurrentSlide ? "ring-2 ring-blue-400 ring-offset-2 ring-offset-gray-900" : ""}
              `}
              aria-label={`Go to slide ${index + 1}`}
              title={`Slide ${index + 1}${!isLoaded ? " (loading...)" : ""}`}
            >
              {/* Loading indicator for unloaded slides */}
              {!isLoaded && !isCurrentSlide && (
                <div className="absolute inset-0 rounded-full border-2 border-gray-600 border-t-transparent animate-spin" />
              )}
            </button>
          );
        })}
      </div>

      {/* Text indicator */}
      <span className="text-sm text-gray-400 dark:text-gray-500 font-light ml-2 whitespace-nowrap">
        {currentIndex + 1} / {totalSlides}
      </span>
    </div>
  );
};

export default SlideProgress;
