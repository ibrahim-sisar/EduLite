import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import Button from '../Button';

describe('Button Component - Edge Cases & Security', () => {
  describe('Invalid Props - Fallback Behavior', () => {
    it('falls back to primary type when given invalid type', () => {
      // @ts-expect-error - Testing invalid prop value
      renderWithProviders(<Button type="invalid-type">Button</Button>);
      const button = screen.getByRole('button');
      // Should fall back to primary styles
      expect(button).toHaveClass('bg-blue-600', 'text-white');
    });

    it('falls back to medium size when given invalid size', () => {
      // @ts-expect-error - Testing invalid prop value
      renderWithProviders(<Button size="invalid-size">Button</Button>);
      const button = screen.getByRole('button');
      // Should fall back to medium size
      expect(button).toHaveClass('px-4', 'py-2', 'text-base');
    });

    it('falls back to auto width when given invalid width', () => {
      // @ts-expect-error - Testing invalid prop value
      renderWithProviders(<Button width="invalid-width">Button</Button>);
      const button = screen.getByRole('button');
      // Should fall back to auto width
      expect(button).toHaveClass('w-auto');
    });
  });

  describe('Children Edge Cases', () => {
    it('renders with empty string children', () => {
      renderWithProviders(<Button>{''}</Button>);
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button.textContent).toBe('');
    });

    it('renders with null children', () => {
      renderWithProviders(<Button>{null}</Button>);
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button.textContent).toBe('');
    });

    it('renders with undefined children', () => {
      renderWithProviders(<Button>{undefined}</Button>);
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button.textContent).toBe('');
    });

    it('renders with number as children', () => {
      renderWithProviders(<Button>{0}</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('0');
    });

    it('renders with React fragment children', () => {
      renderWithProviders(
        <Button>
          <>
            <span>Part 1</span>
            <span>Part 2</span>
          </>
        </Button>
      );
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Part 1Part 2');
    });

    it('renders with JSX element children', () => {
      renderWithProviders(
        <Button>
          <span data-testid="icon">🔥</span>
          <span>Text</span>
        </Button>
      );
      const button = screen.getByRole('button');
      expect(button).toContainElement(screen.getByTestId('icon'));
      expect(button).toHaveTextContent('🔥Text');
    });
  });

  describe('ClassName Handling', () => {
    it('applies custom className alongside default classes', () => {
      renderWithProviders(<Button className="custom-class">Button</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
      expect(button).toHaveClass('cursor-pointer'); // Still has base classes
    });

    it('handles empty string className', () => {
      renderWithProviders(<Button className="">Button</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('cursor-pointer'); // Base classes still applied
    });

    it('handles multiple space-separated classes in className', () => {
      renderWithProviders(<Button className="class1 class2 class3">Button</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('class1', 'class2', 'class3');
    });

    it('does not break with special characters in className', () => {
      renderWithProviders(<Button className="bg-[#ff0000]">Button</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-[#ff0000]');
    });
  });

  describe('Async onClick Handlers', () => {
    it('handles async onClick function', async () => {
      const asyncClick = vi.fn(async () => {
        await new Promise(resolve => setTimeout(resolve, 10));
        return 'done';
      });
      const user = userEvent.setup();

      renderWithProviders(<Button onClick={asyncClick}>Async Button</Button>);
      const button = screen.getByRole('button');

      await user.click(button);

      expect(asyncClick).toHaveBeenCalledTimes(1);
    });


    it('handles onClick with Promise rejection', async () => {
      const rejectClick = vi.fn(async () => {
        throw new Error('Promise rejected');
      });
      const user = userEvent.setup();

      renderWithProviders(<Button onClick={rejectClick}>Reject Button</Button>);
      const button = screen.getByRole('button');

      await user.click(button);
      expect(rejectClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('Rapid Clicking - Race Conditions', () => {
    it('calls onClick for each rapid click', async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup();

      renderWithProviders(<Button onClick={handleClick}>Rapid Click</Button>);
      const button = screen.getByRole('button');

      // Rapid fire 10 clicks
      await user.tripleClick(button);
      await user.tripleClick(button);
      await user.click(button);

      // Should have been called multiple times
      expect(handleClick.mock.calls.length).toBeGreaterThan(5);
    });

    it('disabled button prevents all rapid clicks', async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup();

      renderWithProviders(<Button disabled onClick={handleClick}>Disabled</Button>);
      const button = screen.getByRole('button');

      // Try rapid clicking disabled button
      await user.tripleClick(button);
      await user.tripleClick(button);

      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Event Object Handling', () => {
    it('passes event object to onClick handler', async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup();

      renderWithProviders(<Button onClick={handleClick}>Event Test</Button>);
      const button = screen.getByRole('button');

      await user.click(button);

      expect(handleClick).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'click',
          target: expect.any(Object),
        })
      );
    });

    it('event.preventDefault() can be called in onClick', async () => {
      const handleClick = vi.fn((e) => {
        e.preventDefault();
      });
      const user = userEvent.setup();

      renderWithProviders(<Button onClick={handleClick}>Prevent Default</Button>);
      const button = screen.getByRole('button');

      await user.click(button);

      expect(handleClick).toHaveBeenCalled();
      // Should not throw error when preventDefault is called
    });
  });

  describe('Button State Transitions', () => {
    it('can transition from enabled to disabled', async () => {
      const TestComponent = () => {
        const [disabled, setDisabled] = React.useState(false);
        return (
          <>
            <Button disabled={disabled} onClick={() => {}}>Target Button</Button>
            <button onClick={() => setDisabled(true)}>Toggle</button>
          </>
        );
      };

      const user = userEvent.setup();
      renderWithProviders(<TestComponent />);

      const targetButton = screen.getByText('Target Button');
      expect(targetButton).not.toBeDisabled();

      await user.click(screen.getByText('Toggle'));

      expect(targetButton).toBeDisabled();
    });
  });

  describe('Ref Edge Cases', () => {
    it('handles ref being set to null', () => {
      const ref = { current: null };

      renderWithProviders(<Button ref={ref}>Button</Button>);

      expect(ref.current).toBeInstanceOf(HTMLButtonElement);

      // Manually set ref to null (simulating unmount)
      ref.current = null;
      expect(ref.current).toBeNull();
    });

    it('can access button methods via ref', () => {
      const ref = React.createRef<HTMLButtonElement>();

      renderWithProviders(<Button ref={ref}>Button</Button>);

      expect(ref.current?.click).toBeDefined();
      expect(ref.current?.focus).toBeDefined();
      expect(ref.current?.blur).toBeDefined();
    });

    it('programmatic click via ref triggers onClick', () => {
      const handleClick = vi.fn();
      const ref = React.createRef<HTMLButtonElement>();

      renderWithProviders(<Button ref={ref} onClick={handleClick}>Button</Button>);

      // Programmatically trigger click
      ref.current?.click();

      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('HTML Button Attributes Edge Cases', () => {
    it('accepts form attribute', () => {
      renderWithProviders(<Button form="my-form">Submit</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('form', 'my-form');
    });

    it('accepts formAction attribute', () => {
      renderWithProviders(<Button formAction="/submit">Submit</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('formaction', '/submit');
    });

    it('accepts data attributes', () => {
      renderWithProviders(
        <Button data-testid="btn" data-analytics="click-event">
          Button
        </Button>
      );
      const button = screen.getByTestId('btn');
      expect(button).toHaveAttribute('data-analytics', 'click-event');
    });

    it('handles tabIndex attribute', () => {
      renderWithProviders(<Button tabIndex={-1}>No Tab</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('tabindex', '-1');
    });
  });

  describe('Accessibility Edge Cases', () => {
    it('can have both aria-label and children', () => {
      renderWithProviders(<Button aria-label="Close dialog">X</Button>);
      const button = screen.getByRole('button', { name: /close dialog/i });
      expect(button).toHaveTextContent('X');
    });

    it('handles aria-describedby', () => {
      renderWithProviders(
        <>
          <Button aria-describedby="help-text">Submit</Button>
          <p id="help-text">This will submit the form</p>
        </>
      );
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-describedby', 'help-text');
    });

    it('handles role override', () => {
      renderWithProviders(<Button role="link">Link Button</Button>);
      // Still renders as button element, but with link role
      const element = screen.getByRole('link');
      expect(element.tagName).toBe('BUTTON');
    });
  });
});

// Need to import React for useState in tests
import React from 'react';
