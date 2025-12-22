import React from "react";
import { HiChevronDown, HiChevronUp } from "react-icons/hi2";
import type { SpeakerNotesProps } from "./types";

/**
 * SpeakerNotes Component
 *
 * Displays speaker notes for the current slide in a collapsible panel.
 * Can be toggled via the UI button or keyboard shortcut (N).
 */
const SpeakerNotes: React.FC<SpeakerNotesProps> = ({
  notes,
  isVisible,
  onToggle,
}) => {
  // Don't render anything if there are no notes
  if (!notes || notes.trim() === "") {
    return null;
  }

  return (
    <div
      className={`
        transition-all duration-300 ease-in-out
        ${isVisible ? "max-h-96" : "max-h-12"}
        overflow-hidden
      `}
    >
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-6 py-3 bg-gray-800/80 dark:bg-gray-900/80 backdrop-blur-lg border-t border-gray-700/30 hover:bg-gray-800/90 dark:hover:bg-gray-900/90 transition-colors cursor-pointer"
        aria-label={isVisible ? "Hide speaker notes" : "Show speaker notes"}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-300">
            Speaker Notes
          </span>
          <kbd className="hidden sm:inline-block px-2 py-1 text-xs font-mono bg-gray-700/50 text-gray-400 rounded border border-gray-600/50">
            N
          </kbd>
        </div>
        {isVisible ? (
          <HiChevronDown className="w-5 h-5 text-gray-400" />
        ) : (
          <HiChevronUp className="w-5 h-5 text-gray-400" />
        )}
      </button>

      {/* Notes Content */}
      {isVisible && (
        <div className="px-6 py-4 bg-gray-800/60 dark:bg-gray-900/60 backdrop-blur-lg border-t border-gray-700/20 overflow-y-auto max-h-80">
          <div className="prose prose-sm prose-invert max-w-none">
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
              {notes}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpeakerNotes;
