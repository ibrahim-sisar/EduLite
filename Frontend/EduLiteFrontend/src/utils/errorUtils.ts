import { AxiosError } from "axios";
import toast from "react-hot-toast";

/**
 * Toast deduplication - prevents showing the same error multiple times
 * Tracks recently shown toasts and prevents duplicates within a time window
 */
const recentToasts = new Map<string, number>();
const TOAST_DEDUP_WINDOW = 3000; // 3 seconds

/**
 * Cleans up old toast entries from the deduplication map
 */
const cleanupOldToasts = () => {
  const now = Date.now();
  for (const [message, timestamp] of recentToasts.entries()) {
    if (now - timestamp > TOAST_DEDUP_WINDOW) {
      recentToasts.delete(message);
    }
  }
};

/**
 * Checks if a toast with this message was recently shown
 */
const wasRecentlyShown = (message: string): boolean => {
  cleanupOldToasts();
  const now = Date.now();
  const lastShown = recentToasts.get(message);

  if (lastShown && now - lastShown < TOAST_DEDUP_WINDOW) {
    return true;
  }

  recentToasts.set(message, now);
  return false;
};

/**
 * Sanitizes error messages to prevent leaking internal system details
 *
 * This function takes backend error messages and returns user-friendly messages
 * that don't expose internal API details, database schemas, or stack traces.
 *
 * @param error - The error object (typically from axios)
 * @param fallbackMessage - Generic message to show if we can't determine the issue
 * @returns A safe, user-friendly error message
 */
export const sanitizeErrorMessage = (
  error: any,
  fallbackMessage: string = "An error occurred. Please try again."
): string => {
  // Handle network errors
  if (!error.response) {
    return "Unable to connect to the server. Please check your internet connection.";
  }

  const status = error.response?.status;

  // Handle specific HTTP status codes with generic messages
  switch (status) {
    case 401:
      return "You have been automatically logged out. Please log in again.";

    case 403:
      return "You don't have permission to perform this action.";

    case 404:
      return "The requested resource was not found.";

    case 409:
      return "This item has been modified by someone else. Please refresh and try again.";

    case 429:
      return "Too many requests. Please wait a moment and try again.";

    case 500:
    case 502:
    case 503:
    case 504:
      return "Server error. Please try again later.";

    default:
      // For other errors, use the fallback message
      return fallbackMessage;
  }
};

/**
 * Checks if an error is an authentication/authorization error
 * that should trigger an automatic logout
 */
export const isAuthError = (error: any): boolean => {
  return error.response?.status === 401;
};

/**
 * Extracts a safe error message from an axios error
 * Only allows whitelisted, user-friendly error types
 */
export const getSafeErrorMessage = (
  error: any,
  fallbackMessage: string = "An error occurred. Please try again."
): string => {
  if (error instanceof AxiosError) {
    return sanitizeErrorMessage(error, fallbackMessage);
  }

  // For non-axios errors, just use the fallback
  return fallbackMessage;
};

/**
 * Shows an error toast with deduplication
 * Prevents showing the same error message multiple times in rapid succession
 *
 * @param message - The error message to display
 * @param options - Optional toast options
 */
export const showErrorToast = (message: string, options?: any) => {
  // Don't show if this message was recently shown
  if (wasRecentlyShown(message)) {
    console.log(`[Toast Dedup] Skipped duplicate toast: "${message}"`);
    return;
  }

  toast.error(message, options);
};

/**
 * Shows a safe error toast from an error object
 * Combines error sanitization with toast deduplication
 *
 * @param error - The error object
 * @param fallbackMessage - Fallback message if error can't be parsed
 * @param options - Optional toast options
 */
export const showSafeErrorToast = (
  error: any,
  fallbackMessage: string = "An error occurred. Please try again.",
  options?: any
) => {
  const message = getSafeErrorMessage(error, fallbackMessage);
  showErrorToast(message, options);
};
