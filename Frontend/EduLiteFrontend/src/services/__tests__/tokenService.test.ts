import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import toast from 'react-hot-toast';
import {
  getStoredTokens,
  setStoredTokens,
  clearStoredTokens,
  isTokenExpired,
  refreshAccessToken,
  getValidAccessToken,
  setLogoutHandler,
  setupAxiosInterceptors,
  shouldBeAuthenticated,
  initializeTokenService,
} from '../tokenService';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

/**
 * JWT Token Generator Utility
 * Creates valid/expired JWT tokens for testing
 */
const createJWT = (expiresInSeconds: number): string => {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(
    JSON.stringify({
      exp: Math.floor(Date.now() / 1000) + expiresInSeconds,
      user_id: 1,
      username: 'testuser',
    })
  );
  return `${header}.${payload}.fake-signature`;
};

describe('tokenService - Storage Functions', () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  describe('getStoredTokens', () => {
    it('returns null tokens when storage is empty', () => {
      const tokens = getStoredTokens();
      expect(tokens).toEqual({ access: null, refresh: null });
    });

    it('returns tokens from storage', () => {
      setStoredTokens('access-token', 'refresh-token');

      const tokens = getStoredTokens();
      expect(tokens).toEqual({
        access: 'access-token',
        refresh: 'refresh-token',
      });
    });
  });

  describe('setStoredTokens', () => {
    it('stores tokens in storage', () => {
      setStoredTokens('new-access', 'new-refresh');

      // Verify tokens are retrievable
      const tokens = getStoredTokens();
      expect(tokens.access).toBe('new-access');
      expect(tokens.refresh).toBe('new-refresh');
    });

    it('overwrites existing tokens', () => {
      setStoredTokens('old-access', 'old-refresh');
      setStoredTokens('new-access', 'new-refresh');

      const tokens = getStoredTokens();
      expect(tokens.access).toBe('new-access');
      expect(tokens.refresh).toBe('new-refresh');
    });
  });

  describe('clearStoredTokens', () => {
    it('removes tokens from storage', () => {
      setStoredTokens('access-token', 'refresh-token');
      clearStoredTokens();

      const tokens = getStoredTokens();
      expect(tokens.access).toBeNull();
      expect(tokens.refresh).toBeNull();
    });

    it('does not throw error when storage is already empty', () => {
      expect(() => clearStoredTokens()).not.toThrow();
    });
  });
});

describe('tokenService - Token Validation', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('isTokenExpired', () => {
    it('returns true for empty string token', () => {
      expect(isTokenExpired('')).toBe(true);
    });

    it('returns true for null/undefined token', () => {
      expect(isTokenExpired(null as any)).toBe(true);
      expect(isTokenExpired(undefined as any)).toBe(true);
    });

    it('returns true for malformed JWT (no dots)', () => {
      expect(isTokenExpired('malformed-token')).toBe(true);
    });

    it('returns true for JWT with invalid base64 payload', () => {
      expect(isTokenExpired('header.!!!invalid!!!.signature')).toBe(true);
    });

    it('returns false for valid non-expired token', () => {
      const validToken = createJWT(3600); // Expires in 1 hour
      expect(isTokenExpired(validToken)).toBe(false);
    });

    it('returns true for expired token', () => {
      const expiredToken = createJWT(-3600); // Expired 1 hour ago
      expect(isTokenExpired(expiredToken)).toBe(true);
    });

    it('returns true for token expiring within buffer time (30 seconds)', () => {
      // Token expires in 20 seconds (within 30-second buffer)
      const aboutToExpireToken = createJWT(20);
      expect(isTokenExpired(aboutToExpireToken)).toBe(true);
    });

    it('returns false for token expiring after buffer time', () => {
      // Token expires in 60 seconds (beyond 30-second buffer)
      const validToken = createJWT(60);
      expect(isTokenExpired(validToken)).toBe(false);
    });

    it('handles token with missing exp field', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256' }));
      const payload = btoa(JSON.stringify({ user_id: 1 })); // No exp
      const tokenWithoutExp = `${header}.${payload}.signature`;

      // Missing exp means undefined < number = false, so token appears valid
      // This is a quirk of the implementation - treats missing exp as "never expires"
      expect(isTokenExpired(tokenWithoutExp)).toBe(false);
    });
  });

  describe('shouldBeAuthenticated', () => {
    it('returns false when no tokens in storage', () => {
      expect(shouldBeAuthenticated()).toBe(false);
    });

    it('returns false when only access token exists', () => {
      setStoredTokens(createJWT(3600), 'temp');
      clearStoredTokens();
      localStorage.setItem('access', createJWT(3600));
      expect(shouldBeAuthenticated()).toBe(false);
    });

    it('returns false when only refresh token exists', () => {
      localStorage.setItem('refresh', createJWT(3600));
      expect(shouldBeAuthenticated()).toBe(false);
    });

    it('returns true when both tokens exist and refresh is valid', () => {
      setStoredTokens(createJWT(3600), createJWT(3600));
      expect(shouldBeAuthenticated()).toBe(true);
    });

    it('returns false and clears tokens when refresh token is expired', () => {
      setStoredTokens(createJWT(3600), createJWT(-3600)); // Expired refresh

      expect(shouldBeAuthenticated()).toBe(false);

      const tokens = getStoredTokens();
      expect(tokens.access).toBeNull();
      expect(tokens.refresh).toBeNull();
    });

    it('returns true even if access token is expired (as long as refresh is valid)', () => {
      setStoredTokens(createJWT(-100), createJWT(3600)); // Expired access, valid refresh

      expect(shouldBeAuthenticated()).toBe(true);
    });
  });
});

describe('tokenService - Token Refresh', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('refreshAccessToken', () => {
    it('throws error when no refresh token in storage', async () => {
      await expect(refreshAccessToken()).rejects.toThrow(/refresh token|Failed to refresh/i);
    });

    it('throws error when refresh token is expired', async () => {
      setStoredTokens('access', createJWT(-3600)); // Expired refresh

      await expect(refreshAccessToken()).rejects.toThrow('Refresh token expired');
    });

    it('successfully refreshes access token', async () => {
      const refreshToken = createJWT(3600);
      const newAccessToken = createJWT(3600);
      setStoredTokens('old-access', refreshToken);

      mockedAxios.post.mockResolvedValueOnce({
        data: { access: newAccessToken },
      });

      const result = await refreshAccessToken();

      expect(result).toBe(newAccessToken);
      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/token/refresh/'),
        { refresh: refreshToken },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 10000,
        }
      );

      // Verify new token was stored
      const tokens = getStoredTokens();
      expect(tokens.access).toBe(newAccessToken);
    });

    it('clears tokens on 401 response', async () => {
      setStoredTokens(createJWT(3600), createJWT(3600));

      mockedAxios.post.mockRejectedValueOnce({
        response: { status: 401 },
      });

      await expect(refreshAccessToken()).rejects.toThrow('Refresh token expired or invalid');

      const tokens = getStoredTokens();
      expect(tokens.access).toBeNull();
      expect(tokens.refresh).toBeNull();
    });

    it('clears tokens on network error', async () => {
      setStoredTokens(createJWT(3600), createJWT(3600));

      mockedAxios.post.mockRejectedValueOnce(new Error('Network error'));

      await expect(refreshAccessToken()).rejects.toThrow('Failed to refresh access token');

      const tokens = getStoredTokens();
      expect(tokens.access).toBeNull();
      expect(tokens.refresh).toBeNull();
    });
  });

  describe('getValidAccessToken', () => {
    it('throws error when no tokens exist', async () => {
      await expect(getValidAccessToken()).rejects.toThrow('No authentication tokens available');
    });

    it('returns access token directly when not expired', async () => {
      const validAccessToken = createJWT(3600);
      setStoredTokens(validAccessToken, createJWT(3600));

      const result = await getValidAccessToken();

      expect(result).toBe(validAccessToken);
      expect(mockedAxios.post).not.toHaveBeenCalled(); // No refresh needed
    });

    it('refreshes and returns new token when access token is expired', async () => {
      const expiredAccessToken = createJWT(-100);
      const newAccessToken = createJWT(3600);
      setStoredTokens(expiredAccessToken, createJWT(3600));

      mockedAxios.post.mockResolvedValueOnce({
        data: { access: newAccessToken },
      });

      const result = await getValidAccessToken();

      expect(result).toBe(newAccessToken);
      expect(mockedAxios.post).toHaveBeenCalledTimes(1);
    });

    it('queues concurrent requests during refresh', async () => {
      const expiredAccessToken = createJWT(-100);
      const newAccessToken = createJWT(3600);
      setStoredTokens(expiredAccessToken, createJWT(3600));

      // Simulate slow refresh
      mockedAxios.post.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ data: { access: newAccessToken } }), 100)
          )
      );

      // Make 3 concurrent requests
      const promises = [getValidAccessToken(), getValidAccessToken(), getValidAccessToken()];

      const results = await Promise.all(promises);

      // All should receive the same new token
      expect(results).toEqual([newAccessToken, newAccessToken, newAccessToken]);
      // But refresh should only happen once
      expect(mockedAxios.post).toHaveBeenCalledTimes(1);
    });

    it('propagates error to queued requests when refresh fails', async () => {
      const expiredAccessToken = createJWT(-100);
      setStoredTokens(expiredAccessToken, createJWT(3600));

      mockedAxios.post.mockRejectedValueOnce(new Error('Refresh failed'));

      const promises = [getValidAccessToken(), getValidAccessToken(), getValidAccessToken()];

      await expect(Promise.all(promises)).rejects.toThrow(/failed|refresh/i);
    });
  });
});

describe('tokenService - Setup & Handlers', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('setLogoutHandler', () => {
    it('registers logout handler callback', () => {
      const logoutHandler = vi.fn();
      setLogoutHandler(logoutHandler);

      // We can't directly test the handler is set, but we'll test it via interceptor tests
      expect(logoutHandler).toBeDefined();
    });
  });

  describe('initializeTokenService', () => {
    it('sets up axios interceptors', () => {
      const interceptorsSpy = vi.spyOn(axios.interceptors.request, 'use');

      initializeTokenService();

      expect(interceptorsSpy).toHaveBeenCalled();
    });
  });
});

describe('tokenService - Axios Interceptors', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();

    // Mock axios interceptors
    mockedAxios.interceptors = {
      request: { use: vi.fn(), eject: vi.fn() },
      response: { use: vi.fn(), eject: vi.fn() },
    } as any;
  });

  describe('Request Interceptor', () => {
    it('adds Authorization header to requests with valid token', async () => {
      const validAccessToken = createJWT(3600);
      setStoredTokens(validAccessToken, createJWT(3600));

      setupAxiosInterceptors();

      // Get the request interceptor callback
      const requestInterceptor = (mockedAxios.interceptors.request.use as any).mock.calls[0][0];

      const config = {
        url: '/api/profile/',
        headers: {},
      };

      const result = await requestInterceptor(config);

      expect(result.headers.Authorization).toBe(`Bearer ${validAccessToken}`);
    });

    it('skips token injection for /token/ endpoints', async () => {
      setupAxiosInterceptors();

      const requestInterceptor = (mockedAxios.interceptors.request.use as any).mock.calls[0][0];

      const config = {
        url: '/api/token/refresh/',
        headers: {},
      };

      const result = await requestInterceptor(config);

      expect(result.headers.Authorization).toBeUndefined();
    });

    it('skips token injection for /register/ endpoints', async () => {
      setupAxiosInterceptors();

      const requestInterceptor = (mockedAxios.interceptors.request.use as any).mock.calls[0][0];

      const config = {
        url: '/api/register/',
        headers: {},
      };

      const result = await requestInterceptor(config);

      expect(result.headers.Authorization).toBeUndefined();
    });

    it('does not block request when token retrieval fails', async () => {
      // Ensure no tokens exist by clearing and not setting any
      clearStoredTokens();

      setupAxiosInterceptors();

      const requestInterceptor = (mockedAxios.interceptors.request.use as any).mock.calls[0][0];

      const config = {
        url: '/api/profile/',
        headers: {},
      };

      const result = await requestInterceptor(config);

      // Request should still proceed without token
      expect(result).toBeDefined();
      expect(result.headers.Authorization).toBeUndefined();
    });
  });

  describe('Response Interceptor', () => {
    it('returns response directly on success', async () => {
      setupAxiosInterceptors();

      const responseInterceptor = (mockedAxios.interceptors.response.use as any).mock.calls[0][0];

      const response = {
        data: { message: 'success' },
        status: 200,
      };

      const result = await responseInterceptor(response);

      expect(result).toBe(response);
    });

    it('does not retry auth endpoints on 401', async () => {
      setupAxiosInterceptors();

      const errorInterceptor = (mockedAxios.interceptors.response.use as any).mock.calls[0][1];

      const error = {
        response: { status: 401 },
        config: { url: '/api/token/refresh/' },
      };

      await expect(errorInterceptor(error)).rejects.toEqual(error);
      expect(mockedAxios.post).not.toHaveBeenCalled();
    });

    it('retries request with new token on 401 after successful refresh', async () => {
      const expiredAccessToken = createJWT(-100);
      const newAccessToken = createJWT(3600);
      setStoredTokens(expiredAccessToken, createJWT(3600));

      mockedAxios.post.mockResolvedValueOnce({
        data: { access: newAccessToken },
      });

      mockedAxios.mockResolvedValueOnce({
        data: { message: 'success after retry' },
      });

      setupAxiosInterceptors();

      const errorInterceptor = (mockedAxios.interceptors.response.use as any).mock.calls[0][1];

      const error = {
        response: { status: 401 },
        config: {
          url: '/api/profile/',
          headers: {},
          _retry: false,
        },
      };

      const result = await errorInterceptor(error);

      expect(error.config.headers.Authorization).toBe(`Bearer ${newAccessToken}`);
      expect(mockedAxios).toHaveBeenCalledWith(error.config);
    });

    it('calls logout handler when refresh fails on 401', async () => {
      const logoutHandler = vi.fn();
      setLogoutHandler(logoutHandler);

      setStoredTokens(createJWT(-100), createJWT(3600));

      mockedAxios.post.mockRejectedValueOnce(new Error('Refresh failed'));

      setupAxiosInterceptors();

      const errorInterceptor = (mockedAxios.interceptors.response.use as any).mock.calls[0][1];

      const error = {
        response: { status: 401 },
        config: {
          url: '/api/profile/',
          headers: {},
        },
      };

      await expect(errorInterceptor(error)).rejects.toThrow();

      // Wait for async operations
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(logoutHandler).toHaveBeenCalledTimes(1);
      expect(toast.error).toHaveBeenCalledWith('Session expired. Please log in again.');
    });

    it('does not show multiple logout toasts for concurrent failures', async () => {
      const logoutHandler = vi.fn();
      setLogoutHandler(logoutHandler);

      setStoredTokens(createJWT(-100), createJWT(3600));

      mockedAxios.post.mockRejectedValue(new Error('Refresh failed'));

      setupAxiosInterceptors();

      const errorInterceptor = (mockedAxios.interceptors.response.use as any).mock.calls[0][1];

      const errors = [
        {
          response: { status: 401 },
          config: { url: '/api/profile/', headers: {} },
        },
        {
          response: { status: 401 },
          config: { url: '/api/courses/', headers: {} },
        },
        {
          response: { status: 401 },
          config: { url: '/api/assignments/', headers: {} },
        },
      ];

      await Promise.allSettled(errors.map((error) => errorInterceptor(error)));

      // Wait for async operations
      await new Promise(resolve => setTimeout(resolve, 50));

      // Should only show toast once despite 3 failed requests
      expect(toast.error).toHaveBeenCalledTimes(1);
      expect(logoutHandler).toHaveBeenCalledTimes(1);
    });
  });
});
