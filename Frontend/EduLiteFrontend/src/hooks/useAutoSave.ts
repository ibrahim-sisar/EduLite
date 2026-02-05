import { useState, useEffect, useRef } from 'react';
import { useDebounce } from './useDebounce';
import { getSafeErrorMessage } from '../utils/errorUtils';

interface AutoSaveResult {
  isSaving: boolean;
  lastSaved: Date | null;
  error: string | null;
  saveNow: () => Promise<void>;
}

interface AutoSaveOptions {
  delay: number;
  enabled: boolean;
  isOnline: boolean;
}

/**
 * Hook for auto-saving data with debouncing
 * @param data - The data to auto-save
 * @param onSave - Async function to call when saving
 * @param options - Configuration options
 * @returns Save status and manual save trigger
 */
export function useAutoSave<T>(
  data: T,
  onSave: (data: T) => Promise<void>,
  options: AutoSaveOptions
): AutoSaveResult {
  const debouncedData = useDebounce(data, options.delay);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const previousDataRef = useRef<T>(data);
  const isInitialMount = useRef(true);

  const save = async (dataToSave: T) => {
    if (!options.enabled || !options.isOnline) {
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      await onSave(dataToSave);
      setLastSaved(new Date());
      previousDataRef.current = dataToSave;
    } catch (err) {
      const errorMessage = getSafeErrorMessage(err);
      setError(errorMessage);
      console.error('Auto-save error:', err);
    } finally {
      setIsSaving(false);
    }
  };

  // Auto-save effect
  useEffect(() => {
    // Skip on initial mount
    if (isInitialMount.current) {
      isInitialMount.current = false;
      previousDataRef.current = debouncedData;
      return;
    }

    // Skip if data hasn't changed
    if (previousDataRef.current === debouncedData) {
      return;
    }

    save(debouncedData);
  }, [debouncedData, options.enabled, options.isOnline]);

  // Manual save function
  const saveNow = async () => {
    await save(data);
  };

  return { isSaving, lastSaved, error, saveNow };
}
