import { useState } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import { HiChevronDown, HiChevronUp } from 'react-icons/hi';

interface SpeakerNotesEditorProps {
  notes: string;
  onChange: (notes: string) => void;
}

export function SpeakerNotesEditor({ notes, onChange }: SpeakerNotesEditorProps) {
  const [isExpanded, setIsExpanded] = useState(!!notes);

  return (
    <div className="border-t border-gray-200 dark:border-gray-700">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900/50 hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-colors text-left"
      >
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Speaker Notes
        </span>
        {isExpanded ? (
          <HiChevronUp className="w-5 h-5 text-gray-500" />
        ) : (
          <HiChevronDown className="w-5 h-5 text-gray-500" />
        )}
      </button>

      {isExpanded && (
        <div className="p-3">
          <TextareaAutosize
            value={notes}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Add speaker notes here... (only visible to you during presentation)"
            minRows={3}
            maxRows={10}
            className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 resize-none text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
          />
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            These notes will only be visible to you when presenting (press N during presentation)
          </p>
        </div>
      )}
    </div>
  );
}
