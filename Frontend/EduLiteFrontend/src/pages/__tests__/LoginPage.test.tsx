import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderWithProviders, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import toast from 'react-hot-toast';
import LoginPage from '../LoginPage';
import * as AuthContext from '../../contexts/AuthContext';
import { API_BASE_URL } from '../../services/tokenService';

// Mock dependencies
vi.mock('axios');
vi.mock('react-hot-toast');
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useLocation: () => ({ state: null }),
  };
});

describe('LoginPage', () => {
  const mockLogin = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock AuthContext
    vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
      login: mockLogin,
      logout: vi.fn(),
      isLoggedIn: false,
      loading: false,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('renders the login form', () => {
      renderWithProviders(<LoginPage />);

      expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument();
      expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();
    });

    it('renders username input field', () => {
      renderWithProviders(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      expect(usernameInput).toBeInTheDocument();
      expect(usernameInput).toHaveAttribute('type', 'text');
      expect(usernameInput).toHaveAttribute('name', 'username');
    });

    it('renders password input field', () => {
      renderWithProviders(<LoginPage />);

      const passwordInput = screen.getByLabelText(/^password(?!\s)/i);
      expect(passwordInput).toBeInTheDocument();
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(passwordInput).toHaveAttribute('name', 'password');
    });

    it('renders submit button', () => {
      renderWithProviders(<LoginPage />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveAttribute('type', 'submit');
    });

    it('renders link to signup page', () => {
      renderWithProviders(<LoginPage />);

      const signupLink = screen.getByRole('link', { name: /sign up/i });
      expect(signupLink).toBeInTheDocument();
      expect(signupLink).toHaveAttribute('href', '/signup');
    });
  });

  describe('Form Input Handling', () => {
    it('updates username field when user types', async () => {
      const user = userEvent.setup();
      renderWithProviders(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;
      await user.type(usernameInput, 'testuser');

      expect(usernameInput.value).toBe('testuser');
    });

    it('updates password field when user types', async () => {
      const user = userEvent.setup();
      renderWithProviders(<LoginPage />);

      const passwordInput = screen.getByLabelText(/^password(?!\s)/i) as HTMLInputElement;
      await user.type(passwordInput, 'password123');

      expect(passwordInput.value).toBe('password123');
    });
  });

  describe('Form Validation', () => {
    it('requires username field', () => {
      renderWithProviders(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      expect(usernameInput).toBeRequired();
    });

    it('requires password field', () => {
      renderWithProviders(<LoginPage />);

      const passwordInput = screen.getByLabelText(/^password(?!\s)/i);
      expect(passwordInput).toBeRequired();
    });
  });

  describe('Successful Login', () => {
    it('calls API with correct credentials on submit', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        data: { access: 'access-token', refresh: 'refresh-token' }
      };

      vi.mocked(axios.post).mockResolvedValueOnce(mockResponse);

      renderWithProviders(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/^password(?!\s)/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(axios.post).toHaveBeenCalledWith(
          `${API_BASE_URL}/token/`,
          { username: 'testuser', password: 'password123' },
          {
            headers: { 'Content-Type': 'application/json' },
            timeout: 10000,
          }
        );
      });
    });

    it('calls login from AuthContext with tokens', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        data: { access: 'access-token-123', refresh: 'refresh-token-456' }
      };

      vi.mocked(axios.post).mockResolvedValueOnce(mockResponse);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('access-token-123', 'refresh-token-456');
      });
    });

    it('shows success toast on successful login', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        data: { access: 'access-token', refresh: 'refresh-token' }
      };

      vi.mocked(axios.post).mockResolvedValueOnce(mockResponse);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(toast.success).toHaveBeenCalledWith('Login successful 🎉');
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message for 401 unauthorized', async () => {
      const user = userEvent.setup();
      const mockError = {
        response: { status: 401 }
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'wronguser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'wrongpass');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });

    it('displays error message for 400 bad request', async () => {
      const user = userEvent.setup();
      const mockError = {
        response: { status: 400 }
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'pass');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(/bad request/i)).toBeInTheDocument();
      });
    });

    it('displays error message for network timeout', async () => {
      const user = userEvent.setup();
      const mockError = {
        code: 'ECONNABORTED'
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(/request timeout/i)).toBeInTheDocument();
      });
    });

    it('displays error message for connection failure', async () => {
      const user = userEvent.setup();
      const mockError = {
        response: undefined
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(/cannot connect to server/i)).toBeInTheDocument();
      });
    });

    it('displays backend detail error message if provided', async () => {
      const user = userEvent.setup();
      const mockError = {
        response: {
          status: 500,
          data: { detail: 'Custom backend error message' }
        },
        message: 'Network Error'
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(/custom backend error message/i)).toBeInTheDocument();
      });
    });

    it('shows error toast on login failure', async () => {
      const user = userEvent.setup();
      const mockError = {
        response: { status: 401 }
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'wrongpass');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Login failed!');
      });
    });
  });

  describe('Loading State', () => {
    it('shows loading state during login', async () => {
      const user = userEvent.setup();

      // Create a promise that we control
      let resolveLogin: (value: any) => void;
      const loginPromise = new Promise((resolve) => {
        resolveLogin = resolve;
      });

      vi.mocked(axios.post).mockReturnValueOnce(loginPromise as any);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      // Should show loading text
      expect(screen.getByText(/signing in/i)).toBeInTheDocument();

      // Button should be disabled
      const submitButton = screen.getByRole('button', { name: /signing in/i });
      expect(submitButton).toBeDisabled();

      // Resolve the promise
      resolveLogin!({ data: { access: 'token', refresh: 'token' } });
    });

    it('disables form inputs during login', async () => {
      const user = userEvent.setup();

      let resolveLogin: (value: any) => void;
      const loginPromise = new Promise((resolve) => {
        resolveLogin = resolve;
      });

      vi.mocked(axios.post).mockReturnValueOnce(loginPromise as any);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      expect(screen.getByLabelText(/username/i)).toBeDisabled();
      expect(screen.getByLabelText(/^password(?!\s)/i)).toBeDisabled();

      resolveLogin!({ data: { access: 'token', refresh: 'token' } });
    });
  });

  describe('Environment Variables', () => {
    it('uses API_BASE_URL from tokenService', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        data: { access: 'token', refresh: 'token' }
      };

      vi.mocked(axios.post).mockResolvedValueOnce(mockResponse);

      renderWithProviders(<LoginPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(axios.post).toHaveBeenCalledWith(
          expect.stringContaining('/token/'),
          expect.any(Object),
          expect.any(Object)
        );

        // Verify it's using the tokenService URL pattern
        const callArgs = vi.mocked(axios.post).mock.calls[0];
        expect(callArgs[0]).toBe(`${API_BASE_URL}/token/`);
      });
    });
  });

  describe('Styling and Layout', () => {
    it('has proper gradient background', () => {
      const { container } = renderWithProviders(<LoginPage />);
      const mainDiv = container.querySelector('.min-h-screen');
      expect(mainDiv).toHaveClass('bg-gradient-to-br');
    });

    it('has glass-morphism styling', () => {
      const { container } = renderWithProviders(<LoginPage />);
      const glassDiv = container.querySelector('.backdrop-blur-xl');
      expect(glassDiv).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper form structure', () => {
      renderWithProviders(<LoginPage />);

      const form = document.querySelector('form');
      expect(form).toBeInTheDocument();
    });

    it('has accessible labels for inputs', () => {
      renderWithProviders(<LoginPage />);

      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password(?!\s)/i)).toBeInTheDocument();
    });

    it('has proper heading hierarchy', () => {
      renderWithProviders(<LoginPage />);

      const heading = screen.getByRole('heading', { name: /welcome back/i });
      expect(heading).toBeInTheDocument();
    });
  });

  describe('Dark Mode Support', () => {
    it('has dark mode classes', () => {
      const { container } = renderWithProviders(<LoginPage />);
      const darkModeElement = container.querySelector('.dark\\:from-gray-900');
      expect(darkModeElement).toBeInTheDocument();
    });
  });
});
