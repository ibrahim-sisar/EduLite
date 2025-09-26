import { useEffect, useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

/**
 * Custom hook to detect and warn about unsaved changes
 * Works with standard BrowserRouter
 * Provides browser-level (beforeunload) protection and React Router navigation interception
 */
export const useUnsavedChanges = (isDirty: boolean, message?: string) => {
  const [showModal, setShowModal] = useState(false);
  const [pendingPath, setPendingPath] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

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

  // Intercept link clicks for navigation
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      // Check if it's a link click that would cause navigation
      const target = e.target as HTMLElement;
      const link = target.closest('a');

      if (!link) return;

      const href = link.getAttribute('href');

      // Check if it's an internal navigation link
      if (href && href.startsWith('/') && isDirty) {
        // Check if we're navigating to a different path
        if (href !== location.pathname) {
          e.preventDefault();
          setPendingPath(href);
          setShowModal(true);
        }
      }
    };

    // Add click listener to intercept navigation
    document.addEventListener('click', handleClick);

    return () => {
      document.removeEventListener('click', handleClick);
    };
  }, [isDirty, location.pathname]);

  // Note: Programmatic navigation (like logout button) needs to be handled
  // separately in the component by checking isDirty before calling navigate

  // Confirm navigation (user clicked "Leave" in modal)
  const confirmNavigation = useCallback(() => {
    setShowModal(false);
    if (pendingPath) {
      const path = pendingPath;
      setPendingPath(null);
      // Navigate after a small delay to ensure state cleanup
      setTimeout(() => {
        navigate(path);
      }, 0);
    }
  }, [pendingPath, navigate]);

  // Cancel navigation (user clicked "Stay" in modal)
  const cancelNavigation = useCallback(() => {
    setPendingPath(null);
    setShowModal(false);
  }, []);

  return {
    showModal,
    confirmNavigation,
    cancelNavigation,
    message: defaultMessage
  };
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
    if (!originalData) {
      setIsDirty(false);
      return;
    }

    // Deep comparison of form data
    const hasChanges = Object.keys(currentData).some(key => {
      const current = currentData[key];
      const original = originalData[key];

      // Handle null/undefined/empty string as equivalent
      if (!current && !original) return false;

      // Check if values are different
      return current !== original;
    });

    setIsDirty(hasChanges);
  }, [currentData, originalData]);

  return isDirty;
};
