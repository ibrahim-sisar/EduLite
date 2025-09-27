import axios, { InternalAxiosRequestConfig, AxiosResponse } from "axios";
import toast from "react-hot-toast";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
const TOKEN_REFRESH_BUFFER = Number(import.meta.env.VITE_TOKEN_REFRESH_BUFFER) || 30;
const USE_SESSION_STORAGE = import.meta.env.VITE_USE_SESSION_STORAGE === 'true';

// Token storage keys
const ACCESS_TOKEN_KEY = "access";
const REFRESH_TOKEN_KEY = "refresh";

// Token refresh state to prevent concurrent refresh attempts
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

// Flags to prevent multiple logout notifications
let hasShownSessionExpiredMessage = false;
let logoutInProgress = false;

// Process queued requests after token refresh
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else if (token) {
      resolve(token);
    }
  });

  failedQueue = [];
};

// Select storage mechanism based on configuration
const getStorage = () => {
  return USE_SESSION_STORAGE ? sessionStorage : localStorage;
};

// JWT token utilities with configurable storage
export const getStoredTokens = (): { access: string | null; refresh: string | null } => {
  const storage = getStorage();
  return {
    access: storage.getItem(ACCESS_TOKEN_KEY),
    refresh: storage.getItem(REFRESH_TOKEN_KEY),
  };
};

export const setStoredTokens = (access: string, refresh: string): void => {
  const storage = getStorage();
  storage.setItem(ACCESS_TOKEN_KEY, access);
  storage.setItem(REFRESH_TOKEN_KEY, refresh);
  // Reset the session expired flag when new tokens are set
  hasShownSessionExpiredMessage = false;
  logoutInProgress = false;
};

export const clearStoredTokens = (): void => {
  const storage = getStorage();
  storage.removeItem(ACCESS_TOKEN_KEY);
  storage.removeItem(REFRESH_TOKEN_KEY);
};

// Check if a JWT token is expired
export const isTokenExpired = (token: string): boolean => {
  if (!token) return true;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);

    // Check if token expires in the next buffer time (proactive refresh)
    return payload.exp < (currentTime + TOKEN_REFRESH_BUFFER);
  } catch (error) {
    // Silent fail - token is considered expired if we can't parse it
    return true;
  }
};

// Refresh access token using refresh token
export const refreshAccessToken = async (): Promise<string> => {
  const { refresh } = getStoredTokens();

  if (!refresh) {
    throw new Error("No refresh token available");
  }

  if (isTokenExpired(refresh)) {
    throw new Error("Refresh token expired");
  }

  try {
    const response = await axios.post(
      `${API_BASE_URL}/token/refresh/`,
      { refresh },
      {
        headers: {
          "Content-Type": "application/json",
        },
        timeout: 10000,
      }
    );

    const { access } = response.data;

    // Update stored access token
    const storage = getStorage();
    storage.setItem(ACCESS_TOKEN_KEY, access);

    return access;
  } catch (error: any) {
    // Clear tokens if refresh fails
    clearStoredTokens();

    if (error.response?.status === 401) {
      throw new Error("Refresh token expired or invalid");
    }

    throw new Error("Failed to refresh access token");
  }
};

// Get a valid access token (refresh if necessary)
export const getValidAccessToken = async (): Promise<string> => {
  const { access, refresh } = getStoredTokens();

  if (!access || !refresh) {
    throw new Error("No authentication tokens available");
  }

  // If access token is still valid, return it
  if (!isTokenExpired(access)) {
    return access;
  }

  // If refresh is already in progress, queue this request
  if (isRefreshing) {
    return new Promise<string>((resolve, reject) => {
      failedQueue.push({ resolve, reject });
    });
  }

  // Start refresh process
  isRefreshing = true;

  try {
    const newAccessToken = await refreshAccessToken();
    processQueue(null, newAccessToken);
    isRefreshing = false;
    return newAccessToken;
  } catch (error) {
    processQueue(error, null);
    isRefreshing = false;
    throw error;
  }
};

// Logout handler - to be set by AuthContext
let onLogoutHandler: (() => void) | null = null;

export const setLogoutHandler = (handler: () => void): void => {
  onLogoutHandler = handler;
};

// Setup Axios interceptors for automatic token management
export const setupAxiosInterceptors = (): void => {
  // Request interceptor: Add authorization header with valid token
  axios.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      // Skip token injection for auth endpoints
      if (config.url?.includes('/token/') || config.url?.includes('/register/')) {
        return config;
      }

      try {
        const token = await getValidAccessToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (error) {
        // Don't block the request, let it fail naturally
      }

      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor: Handle 401 responses with token refresh
  axios.interceptors.response.use(
    (response: AxiosResponse) => {
      return response;
    },
    async (error) => {
      const originalRequest = error.config;

      // Skip retry for auth endpoints
      if (originalRequest.url?.includes('/token/') || originalRequest.url?.includes('/register/')) {
        return Promise.reject(error);
      }

      // Handle 401 Unauthorized responses
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          // Try to refresh token
          const newAccessToken = await getValidAccessToken();

          // Update the original request with new token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

          // Retry the original request
          return axios(originalRequest);
        } catch (refreshError) {
          // Only show logout message once to prevent spam
          if (onLogoutHandler && !logoutInProgress) {
            logoutInProgress = true;

            if (!hasShownSessionExpiredMessage) {
              hasShownSessionExpiredMessage = true;
              toast.error("Session expired. Please log in again.");
            }

            onLogoutHandler();

            // Reset flags after a delay to allow for new sessions
            setTimeout(() => {
              hasShownSessionExpiredMessage = false;
              logoutInProgress = false;
            }, 3000);
          }

          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );
};

// Check if user should be authenticated based on stored tokens
export const shouldBeAuthenticated = (): boolean => {
  const { access, refresh } = getStoredTokens();

  if (!access || !refresh) {
    return false;
  }

  // If refresh token is expired, user should not be authenticated
  if (isTokenExpired(refresh)) {
    clearStoredTokens();
    return false;
  }

  return true;
};

// Initialize token service (call this in app startup)
export const initializeTokenService = (): void => {
  setupAxiosInterceptors();

  // Reset flags on initialization
  hasShownSessionExpiredMessage = false;
  logoutInProgress = false;
};
