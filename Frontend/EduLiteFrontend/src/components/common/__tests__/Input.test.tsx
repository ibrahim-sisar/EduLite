import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { renderWithProviders, screen } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import Input from '../Input';

describe('Input Component', () => {
  describe('Rendering', () => {
    it('renders input field', () => {
      renderWithProviders(
        <Input
          name="test-input"
          value=""
          onChange={() => {}}
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toBeInTheDocument();
    });

    it('renders with label', () => {
      renderWithProviders(
        <Input
          name="email"
          label="Email Address"
          value=""
          onChange={() => {}}
        />
      );
      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByText(/email address/i)).toBeInTheDocument();
    });

    it('renders without label', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).not.toHaveAccessibleName();
    });

    it('renders with placeholder', () => {
      renderWithProviders(
        <Input
          name="test"
          placeholder="Enter text here"
          value=""
          onChange={() => {}}
        />
      );
      expect(screen.getByPlaceholderText(/enter text here/i)).toBeInTheDocument();
    });
  });

  describe('Input Types', () => {
    it('renders text input by default', () => {
      renderWithProviders(
        <Input
          name="text"
          value=""
          onChange={() => {}}
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('type', 'text');
    });

    it('renders email input', () => {
      renderWithProviders(
        <Input
          name="email"
          type="email"
          value=""
          onChange={() => {}}
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('type', 'email');
    });

    it('renders password input', () => {
      renderWithProviders(
        <Input
          name="password"
          type="password"
          value=""
          onChange={() => {}}
        />
      );
      // Password inputs don't have a standard role, query by name attribute
      const input = document.querySelector('input[name="password"]');
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'password');
    });

    it('renders search input', () => {
      renderWithProviders(
        <Input
          name="search"
          type="search"
          value=""
          onChange={() => {}}
        />
      );
      const input = screen.getByRole('searchbox');
      expect(input).toHaveAttribute('type', 'search');
    });
  });

  describe('Value and Change Handler', () => {
    it('displays the provided value', () => {
      renderWithProviders(
        <Input
          name="test"
          value="Hello World"
          onChange={() => {}}
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveValue('Hello World');
    });

    it('calls onChange when user types', async () => {
      const handleChange = vi.fn();
      const user = userEvent.setup();

      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={handleChange}
        />
      );
      const input = screen.getByRole('textbox');

      await user.type(input, 'Hello');

      expect(handleChange).toHaveBeenCalled();
      expect(handleChange).toHaveBeenCalledTimes(5); // Once per character
    });

    it('updates value on user input', async () => {
      const TestComponent = () => {
        const [value, setValue] = React.useState('');
        return (
          <Input
            name="test"
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
        );
      };

      const user = userEvent.setup();
      renderWithProviders(<TestComponent />);
      const input = screen.getByRole('textbox');

      await user.type(input, 'Testing');

      expect(input).toHaveValue('Testing');
    });
  });

  describe('Required Field', () => {
    it('renders required indicator when required prop is true', () => {
      renderWithProviders(
        <Input
          name="required-field"
          label="Required Field"
          value=""
          onChange={() => {}}
          required
        />
      );
      // Check for asterisk (*)
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('has required attribute when required prop is true', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          required
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toBeRequired();
    });

    it('does not show asterisk when required is false', () => {
      renderWithProviders(
        <Input
          name="optional-field"
          label="Optional Field"
          value=""
          onChange={() => {}}
        />
      );
      expect(screen.queryByText('*')).not.toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    it('displays error message when error prop is provided', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          error="This field is required"
        />
      );
      expect(screen.getByText(/this field is required/i)).toBeInTheDocument();
    });

    it('applies error styling when error exists', () => {
      renderWithProviders(
        <Input
          name="test"
          label="Test"
          value=""
          onChange={() => {}}
          error="Error message"
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('border-red-500/50');
    });

    it('applies error styling to label when error exists', () => {
      renderWithProviders(
        <Input
          name="test"
          label="Test Label"
          value=""
          onChange={() => {}}
          error="Error message"
        />
      );
      const label = screen.getByText(/test label/i);
      expect(label).toHaveClass('text-red-600');
    });

    it('does not display error message when error prop is not provided', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
        />
      );
      // Error messages should not be in the document
      const errorElements = document.querySelectorAll('.text-red-600');
      expect(errorElements.length).toBe(0);
    });
  });

  describe('Disabled State', () => {
    it('renders disabled input correctly', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          disabled
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toBeDisabled();
    });

    it('applies disabled styling', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          disabled
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('opacity-60', 'cursor-not-allowed');
    });

    it('does not call onChange when disabled', async () => {
      const handleChange = vi.fn();
      const user = userEvent.setup();

      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={handleChange}
          disabled
        />
      );
      const input = screen.getByRole('textbox');

      await user.type(input, 'test');

      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Compact Mode', () => {
    it('applies compact spacing when compact prop is true', () => {
      const { container } = renderWithProviders(
        <Input
          name="test"
          label="Compact"
          value=""
          onChange={() => {}}
          compact
        />
      );
      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('mb-3');
    });

    it('applies normal spacing when compact prop is false', () => {
      const { container } = renderWithProviders(
        <Input
          name="test"
          label="Normal"
          value=""
          onChange={() => {}}
        />
      );
      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('mb-6');
    });
  });

  describe('Accessibility', () => {
    it('associates label with input using htmlFor and id', () => {
      renderWithProviders(
        <Input
          name="accessible-input"
          label="Accessible Input"
          value=""
          onChange={() => {}}
        />
      );
      const input = screen.getByLabelText(/accessible input/i);
      expect(input).toHaveAttribute('id', 'accessible-input');
    });

    it('has proper name attribute', () => {
      renderWithProviders(
        <Input
          name="test-name"
          value=""
          onChange={() => {}}
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('name', 'test-name');
    });
  });

  describe('Forward Ref', () => {
    it('forwards ref to input element', () => {
      const ref = { current: null };

      renderWithProviders(
        <Input
          ref={ref}
          name="ref-test"
          value=""
          onChange={() => {}}
        />
      );

      expect(ref.current).toBeInstanceOf(HTMLInputElement);
      expect(ref.current?.name).toBe('ref-test');
    });

    it('allows focus via ref', () => {
      const ref = { current: null };

      renderWithProviders(
        <Input
          ref={ref}
          name="focus-test"
          value=""
          onChange={() => {}}
        />
      );

      ref.current?.focus();
      expect(ref.current).toHaveFocus();
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const { container } = renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          className="custom-wrapper-class"
        />
      );
      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('custom-wrapper-class');
    });
  });

  describe('HTML Input Attributes', () => {
    it('accepts and applies additional HTML input attributes', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          autoComplete="email"
          data-testid="custom-input"
        />
      );
      const input = screen.getByTestId('custom-input');
      expect(input).toHaveAttribute('autocomplete', 'email');
    });
  });
});
