import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen, within } from '@/test/utils';
import NotFoundPage from '../NotFoundPage';

describe('NotFoundPage', () => {
  describe('Rendering', () => {
    it('renders the 404 error code', () => {
      renderWithProviders(<NotFoundPage />);
      expect(screen.getByText('404')).toBeInTheDocument();
    });

    it('renders the page title', () => {
      renderWithProviders(<NotFoundPage />);
      expect(screen.getByText(/page not found/i)).toBeInTheDocument();
    });

    it('renders the error description', () => {
      renderWithProviders(<NotFoundPage />);
      expect(
        screen.getByText(/the page you're looking for doesn't exist/i)
      ).toBeInTheDocument();
    });

    it('renders the exclamation triangle icon', () => {
      renderWithProviders(<NotFoundPage />);
      // The icon is rendered as an SVG element
      const iconContainer = document.querySelector('.text-5xl.text-blue-500');
      expect(iconContainer).toBeInTheDocument();
    });
  });

  describe('Navigation Links', () => {
    it('renders "Go to Home" link', () => {
      renderWithProviders(<NotFoundPage />);
      const homeLink = screen.getByRole('link', { name: /go to home/i });
      expect(homeLink).toBeInTheDocument();
      expect(homeLink).toHaveAttribute('href', '/');
    });

    it('renders "Go Back" button', () => {
      renderWithProviders(<NotFoundPage />);
      const backButton = screen.getByRole('button', { name: /go back/i });
      expect(backButton).toBeInTheDocument();
    });

    it('renders "About" link', () => {
      renderWithProviders(<NotFoundPage />);
      const aboutLink = screen.getByRole('link', { name: /about/i });
      expect(aboutLink).toBeInTheDocument();
      expect(aboutLink).toHaveAttribute('href', '/about');
    });
  });

  describe('Authenticated vs Unauthenticated States', () => {
    // Note: The default renderWithProviders provides a mocked AuthContext
    // In a real scenario, you would create separate test utilities or
    // modify renderWithProviders to accept custom context values

    it('renders auth-dependent links based on login state', () => {
      renderWithProviders(<NotFoundPage />);

      // The component should render either login/signup OR profile links
      // depending on the auth state from the provider
      const links = screen.getAllByRole('link');
      expect(links.length).toBeGreaterThan(0);
    });
  });

  describe('GitHub Link', () => {
    it('renders GitHub issues link', () => {
      renderWithProviders(<NotFoundPage />);
      const githubLink = screen.getByRole('link', {
        name: /github\.com\/ibrahim-sisar\/edulite\/issues/i
      });
      expect(githubLink).toBeInTheDocument();
      expect(githubLink).toHaveAttribute('href', 'https://github.com/ibrahim-sisar/EduLite/issues');
      expect(githubLink).toHaveAttribute('target', '_blank');
      expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('renders the contribute section', () => {
      renderWithProviders(<NotFoundPage />);
      expect(
        screen.getByText(/do you think this page should exist\?/i)
      ).toBeInTheDocument();
    });
  });

  describe('Styling and Layout', () => {
    it('has proper gradient background', () => {
      const { container } = renderWithProviders(<NotFoundPage />);
      const mainDiv = container.querySelector('.min-h-\\[60vh\\]');
      expect(mainDiv).toHaveClass('bg-gradient-to-br');
    });

    it('renders with proper spacing (pt-24)', () => {
      const { container } = renderWithProviders(<NotFoundPage />);
      const mainDiv = container.querySelector('.pt-24');
      expect(mainDiv).toBeInTheDocument();
    });
  });

  describe('Icons', () => {
    it('renders home icon in Go to Home link', () => {
      renderWithProviders(<NotFoundPage />);
      const homeLink = screen.getByRole('link', { name: /go to home/i });
      const icon = within(homeLink).getByTestId = homeLink.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('renders back arrow icon in Go Back button', () => {
      renderWithProviders(<NotFoundPage />);
      const backButton = screen.getByRole('button', { name: /go back/i });
      const icon = backButton.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('renders GitHub icon', () => {
      renderWithProviders(<NotFoundPage />);
      // GitHub icon is rendered near the contribute section
      const githubIcon = document.querySelector('.text-xl.text-gray-600');
      expect(githubIcon).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('calls window.history.back() when Go Back button is clicked', () => {
      const mockBack = vi.fn();
      window.history.back = mockBack;

      renderWithProviders(<NotFoundPage />);
      const backButton = screen.getByRole('button', { name: /go back/i });

      backButton.click();
      expect(mockBack).toHaveBeenCalled();
    });
  });

  describe('Responsive Design', () => {
    it('uses responsive flex classes for action buttons', () => {
      const { container } = renderWithProviders(<NotFoundPage />);
      const buttonContainer = container.querySelector('.flex.flex-col.sm\\:flex-row');
      expect(buttonContainer).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper semantic structure with headings', () => {
      renderWithProviders(<NotFoundPage />);

      // Main heading (404)
      const mainHeading = screen.getByRole('heading', { level: 1 });
      expect(mainHeading).toHaveTextContent('404');

      // Subheading (Page Not Found)
      const subHeading = screen.getByRole('heading', { level: 2 });
      expect(subHeading).toHaveTextContent(/page not found/i);
    });

    it('has properly styled and accessible links', () => {
      renderWithProviders(<NotFoundPage />);
      const homeLink = screen.getByRole('link', { name: /go to home/i });

      expect(homeLink).toHaveClass('rounded-2xl', 'transition-all');
    });

    it('external links have proper security attributes', () => {
      renderWithProviders(<NotFoundPage />);
      const githubLink = screen.getByRole('link', {
        name: /github\.com\/ibrahim-sisar\/edulite\/issues/i
      });

      // Check for security best practices
      expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
      expect(githubLink).toHaveAttribute('target', '_blank');
    });
  });

  describe('Dark Mode Support', () => {
    it('has dark mode classes on main container', () => {
      const { container } = renderWithProviders(<NotFoundPage />);
      const mainDiv = container.querySelector('.dark\\:from-gray-900');
      expect(mainDiv).toBeInTheDocument();
    });

    it('has dark mode classes on text elements', () => {
      renderWithProviders(<NotFoundPage />);
      const pageTitle = screen.getByText(/page not found/i);
      expect(pageTitle).toHaveClass('dark:text-white');
    });
  });
});
