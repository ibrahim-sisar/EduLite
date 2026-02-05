import { HiCheckCircle, HiClock, HiExclamationCircle, HiWifi } from 'react-icons/hi';
import type { SaveStatus } from '../../../types/editor.types';

interface SaveStatusIndicatorProps {
  status: SaveStatus;
  lastSaved: Date | null;
  error: string | null;
}

export function SaveStatusIndicator({
  status,
  lastSaved,
  error,
}: SaveStatusIndicatorProps) {
  const getStatusDisplay = () => {
    switch (status) {
      case 'saving':
        return {
          icon: <HiClock className="w-4 h-4 animate-spin" />,
          text: 'Saving...',
          className: 'bg-blue-500/20 text-blue-600 dark:text-blue-400 border-blue-500/30',
        };
      case 'saved':
        return {
          icon: <HiCheckCircle className="w-4 h-4" />,
          text: lastSaved
            ? `Saved ${formatTimeSince(lastSaved)}`
            : 'Saved',
          className: 'bg-green-500/20 text-green-600 dark:text-green-400 border-green-500/30',
        };
      case 'error':
        return {
          icon: <HiExclamationCircle className="w-4 h-4" />,
          text: error || 'Save failed',
          className: 'bg-red-500/20 text-red-600 dark:text-red-400 border-red-500/30',
        };
      case 'offline':
        return {
          icon: <HiWifi className="w-4 h-4 opacity-50" />,
          text: 'Offline - changes saved locally',
          className: 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400 border-yellow-500/30',
        };
      default:
        return null;
    }
  };

  const display = getStatusDisplay();
  if (!display) return null;

  return (
    <div
      className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium ${display.className}`}
    >
      {display.icon}
      <span>{display.text}</span>
    </div>
  );
}

function formatTimeSince(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);

  if (seconds < 10) return 'just now';
  if (seconds < 60) return `${seconds}s ago`;

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  return 'recently';
}
