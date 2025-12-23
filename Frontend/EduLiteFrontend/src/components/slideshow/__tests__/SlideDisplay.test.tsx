import { describe, it, expect } from 'vitest';
import { renderWithProviders, screen } from '@/test/utils';
import SlideDisplay from '../SlideDisplay';
import type { Slide } from '../../../types/slideshow.types';

describe('SlideDisplay Component', () => {
  const mockSlide: Slide = {
    id: 1,
    order: 0,
    title: 'Test Slide',
    content: '# Test Content',
    rendered_content: '<h1>Test Content</h1><p>This is a test slide.</p>',
    notes: 'Test notes',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  describe('Rendering', () => {
    it('renders loading state when isLoading is true', () => {
      renderWithProviders(
        <SlideDisplay
          slide={null}
          isLoading={true}
          slideNumber={1}
          totalSlides={10}
        />
      );

      expect(screen.getByText(/loading slide 1 of 10/i)).toBeInTheDocument();
    });

    it('renders loading state when slide is null', () => {
      renderWithProviders(
        <SlideDisplay
          slide={null}
          isLoading={false}
          slideNumber={1}
          totalSlides={10}
        />
      );

      expect(screen.getByText(/loading slide 1 of 10/i)).toBeInTheDocument();
    });

    it('renders slide title when present', () => {
      renderWithProviders(
        <SlideDisplay
          slide={mockSlide}
          isLoading={false}
          slideNumber={1}
          totalSlides={10}
        />
      );

      expect(screen.getByText('Test Slide')).toBeInTheDocument();
    });

    it('renders slide content HTML', () => {
      const { container } = renderWithProviders(
        <SlideDisplay
          slide={mockSlide}
          isLoading={false}
          slideNumber={1}
          totalSlides={10}
        />
      );

      const contentDiv = container.querySelector('.prose');
      expect(contentDiv?.innerHTML).toContain('<h1>Test Content</h1>');
    });

    it('renders slide number indicator', () => {
      renderWithProviders(
        <SlideDisplay
          slide={mockSlide}
          isLoading={false}
          slideNumber={3}
          totalSlides={10}
        />
      );

      expect(screen.getByText(/slide 3 of 10/i)).toBeInTheDocument();
    });

    it('does not render title when slide has no title', () => {
      const slideWithoutTitle = { ...mockSlide, title: null };
      renderWithProviders(
        <SlideDisplay
          slide={slideWithoutTitle}
          isLoading={false}
          slideNumber={1}
          totalSlides={10}
        />
      );

      // The title heading (with specific text) should not be in the document
      // Note: rendered_content may still have h1 tags, but the slide title shouldn't render
      expect(screen.queryByText('Test Slide')).not.toBeInTheDocument();
    });
  });

  describe('Loading Spinner', () => {
    it('shows loading spinner when loading', () => {
      const { container } = renderWithProviders(
        <SlideDisplay
          slide={null}
          isLoading={true}
          slideNumber={1}
          totalSlides={10}
        />
      );

      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });
  });
});
