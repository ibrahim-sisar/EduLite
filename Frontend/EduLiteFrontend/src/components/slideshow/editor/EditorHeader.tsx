import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { HiArrowLeft, HiEye, HiSave } from "react-icons/hi";
import { HiXMark } from "react-icons/hi2";
import { BsKeyboard } from "react-icons/bs";
import { SaveStatusIndicator } from "./SaveStatusIndicator";
import type { SaveStatus } from "../../../types/editor.types";

interface EditorHeaderProps {
  slideshowId: number | "new";
  title: string;
  onTitleChange: (title: string) => void;
  onPresentClick: () => void;
  onSaveClick: () => void;
  saveStatus: SaveStatus;
  lastSaved: Date | null;
  saveError: string | null;
  isDirty: boolean;
  canPresent: boolean;
}

export function EditorHeader({
  slideshowId,
  title,
  onTitleChange,
  onPresentClick,
  onSaveClick,
  saveStatus,
  lastSaved,
  saveError,
  isDirty,
  canPresent,
}: EditorHeaderProps) {
  const navigate = useNavigate();
  const [showShortcuts, setShowShortcuts] = useState(false);

  return (
    <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm">
      <div className="flex items-center justify-between px-4 py-3 gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <button
            type="button"
            onClick={() =>
              navigate(
                slideshowId === "new"
                  ? "/slideshows/me"
                  : `/slideshows/${slideshowId}`,
              )
            }
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
            title="Back"
          >
            <HiArrowLeft className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>

          <input
            type="text"
            value={title}
            onChange={(e) => onTitleChange(e.target.value)}
            placeholder="Untitled Slideshow"
            className="flex-1 text-base sm:text-lg font-semibold bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1 min-w-0"
          />
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <button
            type="button"
            onClick={onSaveClick}
            disabled={!isDirty}
            className="px-3 sm:px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <HiSave className="w-5 h-5" />
            <span className="hidden sm:inline">Save</span>
          </button>

          <button
            type="button"
            onClick={() => setShowShortcuts(true)}
            className="hidden sm:block p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
            title="Keyboard shortcuts"
          >
            <BsKeyboard className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>

          <div className="hidden sm:block">
            <SaveStatusIndicator
              status={saveStatus}
              lastSaved={lastSaved}
              error={saveError}
            />
          </div>

          <button
            type="button"
            onClick={onPresentClick}
            disabled={!canPresent}
            className="px-3 sm:px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer rounded-lg font-medium transition-colors flex items-center gap-2"
            title={!canPresent ? "Add slides to present" : "Present slideshow"}
          >
            <HiEye className="w-5 h-5" />
            <span className="hidden sm:inline">Present</span>
          </button>
        </div>
      </div>

      {/* Keyboard Shortcuts Modal */}
      {showShortcuts && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
          onClick={() => setShowShortcuts(false)}
        >
          <div
            className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Keyboard Shortcuts
              </h2>
              <button
                onClick={() => setShowShortcuts(false)}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
              >
                <HiXMark className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>

            <div className="px-6 py-4 space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                  Navigation
                </h3>
                <div className="space-y-2">
                  <ShortcutRow keys={["←"]} description="Previous slide" />
                  <ShortcutRow keys={["→"]} description="Next slide" />
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                  Preview
                </h3>
                <div className="space-y-2">
                  <ShortcutRow
                    keys={["E"]}
                    description="Toggle expanded preview"
                  />
                  <ShortcutRow
                    keys={["Esc"]}
                    description="Close expanded preview"
                  />
                </div>
              </div>
            </div>

            <div className="px-6 py-3 bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400">
              Arrow keys only work when not focused in a text field
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ShortcutRow({
  keys,
  description,
}: {
  keys: string[];
  description: string;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-700 dark:text-gray-300">
        {description}
      </span>
      <div className="flex items-center gap-1">
        {keys.map((key, i) => (
          <kbd
            key={i}
            className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded border border-gray-300 dark:border-gray-600"
          >
            {key}
          </kbd>
        ))}
      </div>
    </div>
  );
}
