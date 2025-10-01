import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderWithProviders, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import toast from 'react-hot-toast';
import SignupPage from '../SignupPage';
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
  };
});

describe('SignupPage', () => {
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
    it('renders the signup form', () => {
      renderWithProviders(<SignupPage />);

      expect(screen.getByRole('heading', { name: /join edulite/i })).toBeInTheDocument();
      expect(screen.getByText(/create your account to start learning/i)).toBeInTheDocument();
    });

    it('renders all form fields', () => {
      renderWithProviders(<SignupPage />);

      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password(?!\s)/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    });

    it('renders submit button', () => {
      renderWithProviders(<SignupPage />);

      const submitButton = screen.getByRole('button', { name: /create account/i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveAttribute('type', 'submit');
    });

    it('renders link to login page', () => {
      renderWithProviders(<SignupPage />);

      const loginLink = screen.getByRole('link', { name: /sign in/i });
      expect(loginLink).toBeInTheDocument();
      expect(loginLink).toHaveAttribute('href', '/login');
    });
  });

  describe('Form Input Handling', () => {
    it('updates username field when user types', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SignupPage />);

      const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;
      await user.type(usernameInput, 'newuser');

      expect(usernameInput.value).toBe('newuser');
    });

    it('updates email field when user types', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SignupPage />);

      const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
      await user.type(emailInput, 'test@example.com');

      expect(emailInput.value).toBe('test@example.com');
    });

    it('updates password fields when user types', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SignupPage />);

      const passwordInput = screen.getByLabelText(/^password(?!\s)/i) as HTMLInputElement;
      const confirmInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;

      await user.type(passwordInput, 'password123');
      await user.type(confirmInput, 'password123');

      expect(passwordInput.value).toBe('password123');
      expect(confirmInput.value).toBe('password123');
    });
  });

  describe('Client-Side Validation', () => {
    it('shows error when username is empty', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      });
    });

    it('shows error when email is empty', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      });
    });

    it('shows error for invalid email format', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'invalid-email');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
      });
    });

    it('shows error when password is too short', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'short');
      await user.type(screen.getByLabelText(/confirm password/i), 'short');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      });
    });

    it('shows error when passwords do not match', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'different123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
      });
    });

    it('clears field error when user starts typing', async () => {
      const user = userEvent.setup();
      renderWithProviders(<SignupPage />);

      // Trigger validation error
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      });

      // Start typing in username field
      await user.type(screen.getByLabelText(/username/i), 't');

      // Error should be cleared
      await waitFor(() => {
        expect(screen.queryByText(/username is required/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Successful Registration', () => {
    it('calls registration API with correct data', async () => {
      const user = userEvent.setup();
      const mockRegisterResponse = { data: { message: 'Success' } };
      const mockLoginResponse = {
        data: { access: 'access-token', refresh: 'refresh-token' }
      };

      vi.mocked(axios.post)
        .mockResolvedValueOnce(mockRegisterResponse)
        .mockResolvedValueOnce(mockLoginResponse);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'newuser');
      await user.type(screen.getByLabelText(/email/i), 'new@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(axios.post).toHaveBeenCalledWith(
          `${API_BASE_URL}/register/`,
          {
            username: 'newuser',
            email: 'new@example.com',
            password: 'password123',
            password2: 'password123'
          },
          {
            headers: { 'Content-Type': 'application/json' },
            timeout: 10000,
          }
        );
      });
    });

    it('shows success toast after registration', async () => {
      const user = userEvent.setup();
      const mockRegisterResponse = { data: { message: 'Success' } };
      const mockLoginResponse = {
        data: { access: 'access-token', refresh: 'refresh-token' }
      };

      vi.mocked(axios.post)
        .mockResolvedValueOnce(mockRegisterResponse)
        .mockResolvedValueOnce(mockLoginResponse);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'newuser');
      await user.type(screen.getByLabelText(/email/i), 'new@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(toast.success).toHaveBeenCalledWith('Account created successfully! 🎉');
      });
    });

    it('automatically logs in user after successful registration', async () => {
      const user = userEvent.setup();
      const mockRegisterResponse = { data: { message: 'Success' } };
      const mockLoginResponse = {
        data: { access: 'access-token-123', refresh: 'refresh-token-456' }
      };

      vi.mocked(axios.post)
        .mockResolvedValueOnce(mockRegisterResponse)
        .mockResolvedValueOnce(mockLoginResponse);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'newuser');
      await user.type(screen.getByLabelText(/email/i), 'new@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('access-token-123', 'refresh-token-456');
      });
    });

    it('shows welcome toast after auto-login', async () => {
      const user = userEvent.setup();
      const mockRegisterResponse = { data: { message: 'Success' } };
      const mockLoginResponse = {
        data: { access: 'access-token', refresh: 'refresh-token' }
      };

      vi.mocked(axios.post)
        .mockResolvedValueOnce(mockRegisterResponse)
        .mockResolvedValueOnce(mockLoginResponse);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'newuser');
      await user.type(screen.getByLabelText(/email/i), 'new@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(toast.success).toHaveBeenCalledWith('Welcome to EduLite! 🚀');
      });
    });
  });

  describe('Error Handling - Backend Validation', () => {
    it('maps backend username error to form field', async () => {
      const user = userEvent.setup();
      const mockError = {
        response: {
          status: 400,
          data: {
            username: ['A user with that username already exists.']
          }
        }
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'existinguser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/a user with that username already exists/i)).toBeInTheDocument();
      });
    });

    it('maps backend email error to form field', async () => {
      const user = userEvent.setup();
      const mockError = {
        response: {
          status: 400,
          data: {
            email: ['Enter a valid email address.']
          }
        }
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'invalid@email');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/enter a valid email address/i)).toBeInTheDocument();
      });
    });

    it('handles network timeout error', async () => {
      const user = userEvent.setup();
      const mockError = {
        code: 'ECONNABORTED'
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Request timeout. Is your backend running?');
      });
    });

    it('handles connection failure', async () => {
      const user = userEvent.setup();
      const mockError = {
        response: undefined
      };

      vi.mocked(axios.post).mockRejectedValueOnce(mockError);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith(
          'Cannot connect to server. Is your backend running on port 8000?'
        );
      });
    });
  });

  describe('Auto-Login Failure Handling', () => {
    it('redirects to login page if auto-login fails', async () => {
      const user = userEvent.setup();
      const mockRegisterResponse = { data: { message: 'Success' } };
      const mockLoginError = {
        response: { status: 401 }
      };

      vi.mocked(axios.post)
        .mockResolvedValueOnce(mockRegisterResponse)
        .mockRejectedValueOnce(mockLoginError);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'newuser');
      await user.type(screen.getByLabelText(/email/i), 'new@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(toast.success).toHaveBeenCalledWith('Please log in with your new account');
      });
    });
  });

  describe('Loading State', () => {
    it('shows loading state during registration', async () => {
      const user = userEvent.setup();

      let resolveRegistration: (value: any) => void;
      const registrationPromise = new Promise((resolve) => {
        resolveRegistration = resolve;
      });

      vi.mocked(axios.post).mockReturnValueOnce(registrationPromise as any);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      expect(screen.getByText(/creating account/i)).toBeInTheDocument();

      const submitButton = screen.getByRole('button', { name: /creating account/i });
      expect(submitButton).toBeDisabled();

      resolveRegistration!({ data: { message: 'Success' } });
    });

    it('disables form inputs during registration', async () => {
      const user = userEvent.setup();

      let resolveRegistration: (value: any) => void;
      const registrationPromise = new Promise((resolve) => {
        resolveRegistration = resolve;
      });

      vi.mocked(axios.post).mockReturnValueOnce(registrationPromise as any);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      expect(screen.getByLabelText(/username/i)).toBeDisabled();
      expect(screen.getByLabelText(/email/i)).toBeDisabled();

      resolveRegistration!({ data: { message: 'Success' } });
    });
  });

  describe('Environment Variables', () => {
    it('uses API_BASE_URL from tokenService', async () => {
      const user = userEvent.setup();
      const mockResponse = { data: { message: 'Success' } };

      vi.mocked(axios.post).mockResolvedValueOnce(mockResponse);

      renderWithProviders(<SignupPage />);

      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password(?!\s)/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        const callArgs = vi.mocked(axios.post).mock.calls[0];
        expect(callArgs[0]).toBe(`${API_BASE_URL}/register/`);
      });
    });
  });

  describe('Styling and Layout', () => {
    it('has proper gradient background', () => {
      const { container } = renderWithProviders(<SignupPage />);
      const mainDiv = container.querySelector('.min-h-screen');
      expect(mainDiv).toHaveClass('bg-gradient-to-br');
    });

    it('has glass-morphism styling', () => {
      const { container } = renderWithProviders(<SignupPage />);
      const glassDiv = container.querySelector('.backdrop-blur-xl');
      expect(glassDiv).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper form structure', () => {
      renderWithProviders(<SignupPage />);

      const form = document.querySelector('form');
      expect(form).toBeInTheDocument();
    });

    it('has accessible labels for all inputs', () => {
      renderWithProviders(<SignupPage />);

      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password(?!\s)/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    });

    it('has proper heading hierarchy', () => {
      renderWithProviders(<SignupPage />);

      const heading = screen.getByRole('heading', { name: /join edulite/i });
      expect(heading).toBeInTheDocument();
    });

    it('all required fields have required attribute', () => {
      renderWithProviders(<SignupPage />);

      expect(screen.getByLabelText(/username/i)).toBeRequired();
      expect(screen.getByLabelText(/email/i)).toBeRequired();
      expect(screen.getByLabelText(/^password(?!\s)/i)).toBeRequired();
      expect(screen.getByLabelText(/confirm password/i)).toBeRequired();
    });
  });

  describe('Dark Mode Support', () => {
    it('has dark mode classes', () => {
      const { container } = renderWithProviders(<SignupPage />);
      const darkModeElement = container.querySelector('.dark\\:from-gray-900');
      expect(darkModeElement).toBeInTheDocument();
    });
  });
});
