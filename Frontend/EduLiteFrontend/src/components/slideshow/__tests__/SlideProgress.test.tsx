import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import SlideProgress from '../SlideProgress';

describe('SlideProgress Component', () => {
  describe('Small Slide Deck (≤20 slides)', () => {
    it('renders individual dots for each slide', () => {
      const loadedSlides = [true, true, true, false, false];
      renderWithProviders(
        <SlideProgress
          currentIndex={0}
          totalSlides={5}
          loadedSlides={loadedSlides}
          onSlideClick={vi.fn()}
        />
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons).toHaveLength(5);
    });

    it('highlights current slide', () => {
      const loadedSlides = [true, true, true];
      renderWithProviders(
        <SlideProgress
          currentIndex={1}
          totalSlides={3}
          loadedSlides={loadedSlides}
          onSlideClick={vi.fn()}
        />
      );

      const currentButton = screen.getByLabelText('Go to slide 2');
      expect(currentButton).toHaveClass('bg-blue-500');
    });

    it('calls onSlideClick when dot is clicked', async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup();
      const loadedSlides = [true, true, true];

      renderWithProviders(
        <SlideProgress
          currentIndex={0}
          totalSlides={3}
          loadedSlides={loadedSlides}
          onSlideClick={handleClick}
        />
      );

      const thirdSlide = screen.getByLabelText('Go to slide 3');
      await user.click(thirdSlide);

      expect(handleClick).toHaveBeenCalledWith(2);
    });

    it('shows text indicator with current/total', () => {
      const loadedSlides = [true, true, true];
      renderWithProviders(
        <SlideProgress
          currentIndex={2}
          totalSlides={3}
          loadedSlides={loadedSlides}
          onSlideClick={vi.fn()}
        />
      );

      expect(screen.getByText('3 / 3')).toBeInTheDocument();
    });

    it('shows loading indicator for unloaded slides', () => {
      const loadedSlides = [true, false, true];
      const { container } = renderWithProviders(
        <SlideProgress
          currentIndex={0}
          totalSlides={3}
          loadedSlides={loadedSlides}
          onSlideClick={vi.fn()}
        />
      );

      // Should have loading animation on unloaded slide
      const loadingIndicators = container.querySelectorAll('.animate-spin');
      expect(loadingIndicators.length).toBeGreaterThan(0);
    });
  });

  describe('Large Slide Deck (>20 slides)', () => {
    it('renders condensed view with progress bar', () => {
      const loadedSlides = Array(25).fill(true);
      const { container } = renderWithProviders(
        <SlideProgress
          currentIndex={10}
          totalSlides={25}
          loadedSlides={loadedSlides}
          onSlideClick={vi.fn()}
        />
      );

      // Should have a progress bar instead of individual dots
      const progressBar = container.querySelector('.bg-blue-500');
      expect(progressBar).toBeInTheDocument();
    });

    it('shows text indicator in condensed view', () => {
      const loadedSlides = Array(25).fill(true);
      renderWithProviders(
        <SlideProgress
          currentIndex={15}
          totalSlides={25}
          loadedSlides={loadedSlides}
          onSlideClick={vi.fn()}
        />
      );

      expect(screen.getByText('16 / 25')).toBeInTheDocument();
    });

    it('calculates progress bar width correctly', () => {
      const loadedSlides = Array(25).fill(true);
      const { container } = renderWithProviders(
        <SlideProgress
          currentIndex={12}
          totalSlides={25}
          loadedSlides={loadedSlides}
          onSlideClick={vi.fn()}
        />
      );

      const progressBar = container.querySelector('.bg-blue-500');
      // 13/25 = 52%
      expect(progressBar).toHaveStyle({ width: '52%' });
    });
  });

  describe('Accessibility', () => {
    it('has aria-label on slide buttons', () => {
      const loadedSlides = [true, true, true];
      renderWithProviders(
        <SlideProgress
          currentIndex={0}
          totalSlides={3}
          loadedSlides={loadedSlides}
          onSlideClick={vi.fn()}
        />
      );

      expect(screen.getByLabelText('Go to slide 1')).toBeInTheDocument();
      expect(screen.getByLabelText('Go to slide 2')).toBeInTheDocument();
      expect(screen.getByLabelText('Go to slide 3')).toBeInTheDocument();
    });

    it('shows loading status in title attribute', () => {
      const loadedSlides = [true, false, true];
      renderWithProviders(
        <SlideProgress
          currentIndex={0}
          totalSlides={3}
          loadedSlides={loadedSlides}
          onSlideClick={vi.fn()}
        />
      );

      const unloadedSlide = screen.getByLabelText('Go to slide 2');
      expect(unloadedSlide).toHaveAttribute('title', 'Slide 2 (loading...)');
    });
  });
});
