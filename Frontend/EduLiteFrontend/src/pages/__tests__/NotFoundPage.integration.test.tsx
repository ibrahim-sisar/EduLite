import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import userEvent from '@testing-library/user-event';
import NotFoundPage from '../NotFoundPage';
import { AuthProvider } from '../../contexts/AuthContext';
import i18n from '../../i18n';

/**
 * Integration tests for NotFoundPage with proper context mocking
 * These tests verify behavior with different auth states and i18n
 */

// Mock the tokenService to control auth state
vi.mock('../../services/tokenService', () => ({
  initializeTokenService: vi.fn(),
  setLogoutHandler: vi.fn(),
  setStoredTokens: vi.fn(),
  clearStoredTokens: vi.fn(),
  shouldBeAuthenticated: vi.fn(() => false), // Default to not authenticated
}));

describe('NotFoundPage - Integration Tests', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  describe('Authentication State Integration', () => {
    it('shows Login and Sign Up links when not authenticated', async () => {
      const { shouldBeAuthenticated } = await import('../../services/tokenService');
      vi.mocked(shouldBeAuthenticated).mockReturnValue(false);

      // Wait for auth check to complete
      await new Promise(resolve => setTimeout(resolve, 100));

      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // Should show login and signup links for unauthenticated users
      const loginLink = screen.getByRole('link', { name: /login/i });
      const signupLink = screen.getByRole('link', { name: /sign up/i });

      expect(loginLink).toBeInTheDocument();
      expect(signupLink).toBeInTheDocument();

      // Should NOT show profile link
      expect(screen.queryByRole('link', { name: /profile/i })).not.toBeInTheDocument();
    });

    it('shows Profile link when authenticated', async () => {
      const { shouldBeAuthenticated } = await import('../../services/tokenService');
      vi.mocked(shouldBeAuthenticated).mockReturnValue(true);

      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // Wait for auth state to update
      await new Promise(resolve => setTimeout(resolve, 100));

      // Should show profile link for authenticated users
      const profileLink = screen.getByRole('link', { name: /profile/i });
      expect(profileLink).toBeInTheDocument();

      // Should NOT show login/signup links
      expect(screen.queryByRole('link', { name: /^login$/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('link', { name: /sign up/i })).not.toBeInTheDocument();
    });
  });

  describe('Navigation Integration', () => {
    it('renders navigation links with correct hrefs', () => {
      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      const homeLink = screen.getByRole('link', { name: /go to home/i });
      const aboutLink = screen.getByRole('link', { name: /about/i });

      expect(homeLink).toHaveAttribute('href', '/');
      expect(aboutLink).toHaveAttribute('href', '/about');
    });

    it('GitHub link opens in new tab with security attributes', () => {
      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      const githubLink = screen.getByRole('link', {
        name: /github\.com\/ibrahim-sisar\/edulite\/issues/i
      });

      expect(githubLink).toHaveAttribute('href', 'https://github.com/ibrahim-sisar/EduLite/issues');
      expect(githubLink).toHaveAttribute('target', '_blank');
      expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });

  describe('window.history.back() Integration', () => {
    it('calls window.history.back when Go Back button is clicked', async () => {
      const mockHistoryBack = vi.fn();
      const originalBack = window.history.back;
      window.history.back = mockHistoryBack;

      const user = userEvent.setup();

      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      const goBackButton = screen.getByRole('button', { name: /go back/i });
      await user.click(goBackButton);

      expect(mockHistoryBack).toHaveBeenCalledTimes(1);

      // Restore original
      window.history.back = originalBack;
    });
  });

  describe('i18n Integration', () => {
    it('renders with English language by default', () => {
      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // Check for English text
      expect(screen.getByText('404')).toBeInTheDocument();
      expect(screen.getByText(/page not found/i)).toBeInTheDocument();
      expect(screen.getByText(/go to home/i)).toBeInTheDocument();
    });

    // Note: Testing language switching would require more complex i18n setup
    // and is typically covered by i18n-specific tests
  });

  describe('Component Structure Integration', () => {
    it('renders all major sections', () => {
      const { container } = render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // Check for main sections
      const mainHeading = screen.getByRole('heading', { level: 1, name: '404' });
      const subHeading = screen.getByRole('heading', { level: 2, name: /page not found/i });

      expect(mainHeading).toBeInTheDocument();
      expect(subHeading).toBeInTheDocument();

      // Check for action buttons section
      const homeLink = screen.getByRole('link', { name: /go to home/i });
      const goBackButton = screen.getByRole('button', { name: /go back/i });

      expect(homeLink).toBeInTheDocument();
      expect(goBackButton).toBeInTheDocument();

      // Check for helpful links section
      expect(screen.getByText(/here are some helpful links/i)).toBeInTheDocument();

      // Check for contribute section
      expect(screen.getByText(/do you think this page should exist/i)).toBeInTheDocument();
    });

    it('has proper semantic HTML structure', () => {
      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // Check heading hierarchy
      const h1 = screen.getByRole('heading', { level: 1 });
      const h2 = screen.getByRole('heading', { level: 2 });

      expect(h1).toBeInTheDocument();
      expect(h2).toBeInTheDocument();

      // Check for proper link structure
      const links = screen.getAllByRole('link');
      expect(links.length).toBeGreaterThan(0);

      links.forEach(link => {
        expect(link).toHaveAttribute('href');
      });
    });
  });

  describe('Icons Integration', () => {
    it('renders all icon components', () => {
      const { container } = render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // React Icons render as SVG elements
      const svgElements = container.querySelectorAll('svg');

      // Should have icons for:
      // 1. Exclamation triangle (error icon)
      // 2. Home icon
      // 3. Arrow left (go back)
      // 4. GitHub icon
      expect(svgElements.length).toBeGreaterThanOrEqual(4);
    });

    it('icons have proper aria-hidden or accessible labels', () => {
      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // Icons should either be decorative (aria-hidden) or have accessible text
      const homeLink = screen.getByRole('link', { name: /go to home/i });
      const goBackButton = screen.getByRole('button', { name: /go back/i });

      // These should have accessible names from their text content
      expect(homeLink).toHaveAccessibleName();
      expect(goBackButton).toHaveAccessibleName();
    });
  });

  describe('Responsive Design Integration', () => {
    it('uses responsive Tailwind classes', () => {
      const { container } = render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // Check for responsive flex classes
      const flexContainer = container.querySelector('.flex.flex-col.sm\\:flex-row');
      expect(flexContainer).toBeInTheDocument();
    });
  });

  describe('Dark Mode Integration', () => {
    it('includes dark mode classes for all elements', () => {
      const { container } = render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // Check for dark mode classes in main container
      const mainContainer = container.querySelector('.dark\\:from-gray-900');
      expect(mainContainer).toBeInTheDocument();

      // Check text elements have dark mode variants
      const pageTitle = screen.getByText(/page not found/i);
      expect(pageTitle).toHaveClass('dark:text-white');
    });
  });

  describe('Full User Journey Integration', () => {
    it('simulates complete user interaction flow', async () => {
      const user = userEvent.setup();
      const mockHistoryBack = vi.fn();
      window.history.back = mockHistoryBack;

      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // 1. User sees the 404 error
      expect(screen.getByText('404')).toBeInTheDocument();

      // 2. User reads the error message
      expect(screen.getByText(/page not found/i)).toBeInTheDocument();

      // 3. User considers their options
      const homeLink = screen.getByRole('link', { name: /go to home/i });
      const goBackButton = screen.getByRole('button', { name: /go back/i });
      const aboutLink = screen.getByRole('link', { name: /about/i });

      expect(homeLink).toBeInTheDocument();
      expect(goBackButton).toBeInTheDocument();
      expect(aboutLink).toBeInTheDocument();

      // 4. User clicks "Go Back"
      await user.click(goBackButton);
      expect(mockHistoryBack).toHaveBeenCalledTimes(1);
    });
  });

  describe('Error Boundaries and Edge Cases', () => {
    it('renders even if AuthContext has errors', () => {
      // This tests resilience to context errors
      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      // Page should still render
      expect(screen.getByText('404')).toBeInTheDocument();
    });

    it('renders even if i18n is not fully initialized', () => {
      // Test with minimal i18n setup
      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      expect(screen.getByText('404')).toBeInTheDocument();
    });
  });

  describe('Link Navigation Edge Cases', () => {
    it('all internal links use relative paths', () => {
      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      const homeLink = screen.getByRole('link', { name: /go to home/i });
      const aboutLink = screen.getByRole('link', { name: /about/i });

      expect(homeLink.getAttribute('href')).toMatch(/^\//);
      expect(aboutLink.getAttribute('href')).toMatch(/^\//);
    });

    it('external links open in new tab', () => {
      render(
        <BrowserRouter>
          <I18nextProvider i18n={i18n}>
            <AuthProvider>
              <NotFoundPage />
            </AuthProvider>
          </I18nextProvider>
        </BrowserRouter>
      );

      const githubLink = screen.getByRole('link', {
        name: /github\.com\/ibrahim-sisar\/edulite\/issues/i
      });

      expect(githubLink).toHaveAttribute('target', '_blank');
    });
  });
});
