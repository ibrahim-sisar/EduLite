import { useEffect, useState } from 'react';

/**
 * Simple hook to add browser warning for unsaved changes
 * Shows browser's native warning when trying to close/refresh tab
 */
export const useUnsavedChanges = (isDirty: boolean, message?: string) => {
  const defaultMessage = message || "You have unsaved changes. Are you sure you want to leave?";

  // Browser-level protection (tab close, refresh, etc.)
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        // Modern browsers require returnValue to be set
        e.returnValue = defaultMessage;
        return defaultMessage;
      }
    };

    if (isDirty) {
      window.addEventListener('beforeunload', handleBeforeUnload);
    }

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isDirty, defaultMessage]);
};

/**
 * Helper hook to track form changes
 * Compares current form data with original data to detect changes
 */
export const useFormDirtyState = <T extends Record<string, any>>(
  currentData: T,
  originalData: T | null
): boolean => {
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    if (!originalData || Object.keys(originalData).length === 0) {
      setIsDirty(false);
      return;
    }

    // Deep comparison of form data
    const hasChanges = Object.keys(currentData).some(key => {
      const current = currentData[key];
      const original = originalData[key];

      // Handle null/undefined/empty string as equivalent
      if ((!current || current === '') && (!original || original === '')) {
        return false;
      }

      // Check if values are different
      return current !== original;
    });

    setIsDirty(hasChanges);
  }, [currentData, originalData]);

  return isDirty;
};
