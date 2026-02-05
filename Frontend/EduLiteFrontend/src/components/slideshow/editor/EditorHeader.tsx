import { useNavigate } from 'react-router-dom';
import { HiArrowLeft, HiEye, HiSave } from 'react-icons/hi';
import { SaveStatusIndicator } from './SaveStatusIndicator';
import type { SaveStatus } from '../../../types/editor.types';

interface EditorHeaderProps {
  slideshowId: number | 'new';
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

  return (
    <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm">
      <div className="flex items-center justify-between px-4 py-3 gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <button
            type="button"
            onClick={() => navigate(slideshowId === 'new' ? '/slideshows/me' : `/slideshows/${slideshowId}`)}
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
            className="flex-1 text-lg font-semibold bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1 min-w-0"
          />
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onSaveClick}
            disabled={!isDirty}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <HiSave className="w-5 h-5" />
            Save
          </button>

          <SaveStatusIndicator status={saveStatus} lastSaved={lastSaved} error={saveError} />

          <button
            type="button"
            onClick={onPresentClick}
            disabled={!canPresent}
            className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer rounded-lg font-medium transition-colors flex items-center gap-2"
            title={!canPresent ? 'Add slides to present' : 'Present slideshow'}
          >
            <HiEye className="w-5 h-5" />
            Present
          </button>
        </div>
      </div>
    </div>
  );
}
