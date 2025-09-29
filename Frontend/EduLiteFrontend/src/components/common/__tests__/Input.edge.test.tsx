import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { renderWithProviders, screen, waitFor } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import Input from '../Input';

describe('Input Component - Edge Cases & Security', () => {
  describe('XSS Security Tests', () => {
    it('escapes HTML in error messages', () => {
      const xssAttempt = '<script>alert("XSS")</script>';
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          error={xssAttempt}
        />
      );

      // Error text should be escaped, not executed
      const errorElement = screen.getByText(/<script>alert\("XSS"\)<\/script>/i);
      expect(errorElement).toBeInTheDocument();
      expect(errorElement.innerHTML).not.toContain('<script');
    });

    it('escapes HTML entities in error messages', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          error="<img src=x onerror=alert(1)>"
        />
      );

      const errorElement = screen.getByText(/<img src=x onerror=alert\(1\)>/i);
      expect(errorElement).toBeInTheDocument();
      // Should be text content, not actual HTML
      expect(errorElement.querySelector('img')).toBeNull();
    });

    it('escapes HTML in label text', () => {
      renderWithProviders(
        <Input
          name="test"
          label="<script>alert('xss')</script>"
          value=""
          onChange={() => {}}
        />
      );

      const label = screen.getByText(/<script>alert\('xss'\)<\/script>/i);
      expect(label).toBeInTheDocument();
    });

    it('handles malicious placeholder text safely', () => {
      renderWithProviders(
        <Input
          name="test"
          placeholder="<img src=x onerror=alert(1)>"
          value=""
          onChange={() => {}}
        />
      );

      const input = screen.getByPlaceholderText(/<img src=x onerror=alert\(1\)>/i);
      expect(input).toBeInTheDocument();
      expect(input.placeholder).toBe('<img src=x onerror=alert(1)>');
    });
  });

  describe('Value Edge Cases', () => {
    it('handles empty string value', () => {
      renderWithProviders(
        <Input name="test" value="" onChange={() => {}} />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveValue('');
    });

    it('handles very long text value (10k characters)', () => {
      const longValue = 'a'.repeat(10000);
      renderWithProviders(
        <Input name="test" value={longValue} onChange={() => {}} />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveValue(longValue);
      expect((input as HTMLInputElement).value.length).toBe(10000);
    });

    it('handles Unicode and emoji values', () => {
      const unicodeValue = '🔥💯✨🎉 Hello 世界 مرحبا';
      renderWithProviders(
        <Input name="test" value={unicodeValue} onChange={() => {}} />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveValue(unicodeValue);
    });

    it('handles special characters', () => {
      const specialChars = '!@#$%^&*()_+-={}[]|\\:";\'<>?,./`~';
      renderWithProviders(
        <Input name="test" value={specialChars} onChange={() => {}} />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveValue(specialChars);
    });

    it('handles newlines and tabs in value', () => {
      const multilineValue = 'Line 1\nLine 2\tTabbed';
      renderWithProviders(
        <Input name="test" value={multilineValue} onChange={() => {}} />
      );
      const input = screen.getByRole('textbox');
      // Browser <input> elements strip newlines - this is expected behavior
      expect(input).toHaveValue('Line 1Line 2\tTabbed');
    });

    it('handles null-like string values', () => {
      renderWithProviders(
        <Input name="test" value="null" onChange={() => {}} />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveValue('null');
    });
  });

  describe('Rapid Typing Performance', () => {
    it('handles rapid typing without dropping characters', async () => {
      const handleChange = vi.fn();
      const user = userEvent.setup({ delay: null }); // No delay for fast typing

      const TestComponent = () => {
        const [value, setValue] = React.useState('');
        return (
          <Input
            name="test"
            value={value}
            onChange={(e) => {
              handleChange(e);
              setValue(e.target.value);
            }}
          />
        );
      };

      renderWithProviders(<TestComponent />);
      const input = screen.getByRole('textbox');

      // Type rapidly
      await user.type(input, 'RapidTyping123!');

      // Final value should be correct (most important)
      expect(input).toHaveValue('RapidTyping123!');
      // React may batch some onChange calls, so we check it was called at least once
      // and not more than the character count
      expect(handleChange.mock.calls.length).toBeGreaterThan(0);
      expect(handleChange.mock.calls.length).toBeLessThanOrEqual(16);
    });

    it('handles 100+ character rapid input', async () => {
      const longText = 'a'.repeat(100);
      const user = userEvent.setup({ delay: null });

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

      renderWithProviders(<TestComponent />);
      const input = screen.getByRole('textbox');

      await user.type(input, longText);

      expect((input as HTMLInputElement).value.length).toBe(100);
    });
  });

  describe('Paste Operations', () => {
    it('handles paste with large text', async () => {
      const largeText = 'Lorem ipsum '.repeat(1000); // ~12,000 characters
      const user = userEvent.setup();

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

      renderWithProviders(<TestComponent />);
      const input = screen.getByRole('textbox');

      await user.click(input);
      await user.paste(largeText);

      expect(input).toHaveValue(largeText);
    });

    it('handles paste with special characters', async () => {
      const specialText = '<script>alert("xss")</script>\n\ttab\n©™®';
      const user = userEvent.setup();

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

      renderWithProviders(<TestComponent />);
      const input = screen.getByRole('textbox');

      await user.click(input);
      await user.paste(specialText);

      // Browser <input> elements strip newlines - expect normalized value
      expect(input).toHaveValue('<script>alert("xss")</script>\ttab©™®');
    });

    it('handles paste into input with existing value', async () => {
      const user = userEvent.setup();

      const TestComponent = () => {
        const [value, setValue] = React.useState('existing');
        return (
          <Input
            name="test"
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
        );
      };

      renderWithProviders(<TestComponent />);
      const input = screen.getByRole('textbox');

      // Select all and paste over
      await user.click(input);
      await user.keyboard('{Control>}a{/Control}');
      await user.paste('pasted');

      expect(input).toHaveValue('pasted');
    });
  });

  describe('ClassName Border-Red Logic Bug (Line 101)', () => {
    it('handles className with border-red correctly', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          className="border-red-600"
        />
      );

      const container = document.querySelector('.border-red-600');
      expect(container).toBeInTheDocument();
    });

    it('error prop takes precedence over className border', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          className="border-blue-500"
          error="Error message"
        />
      );

      const input = screen.getByRole('textbox');
      // Error styling should apply
      expect(input).toHaveClass('border-red-500/50');
    });

    it('handles both error and className with border-red', () => {
      renderWithProviders(
        <Input
          name="test"
          value=""
          onChange={() => {}}
          className="border-red-900"
          error="Error"
        />
      );

      const input = screen.getByRole('textbox');
      // Error border should win
      expect(input).toHaveClass('border-red-500/50');
    });
  });

  describe('Focus Management Edge Cases', () => {
    it('handles rapid focus and blur', async () => {
      const ref = React.createRef<HTMLInputElement>();

      renderWithProviders(
        <Input ref={ref} name="test" value="" onChange={() => {}} />
      );

      // Rapidly focus and blur
      ref.current?.focus();
      ref.current?.blur();
      ref.current?.focus();
      ref.current?.blur();
      ref.current?.focus();

      await waitFor(() => {
        expect(ref.current).toHaveFocus();
      });
    });

    it('can focus input programmatically twice', () => {
      const ref = React.createRef<HTMLInputElement>();

      renderWithProviders(
        <Input ref={ref} name="test" value="" onChange={() => {}} />
      );

      ref.current?.focus();
      expect(ref.current).toHaveFocus();

      ref.current?.blur();
      expect(ref.current).not.toHaveFocus();

      ref.current?.focus();
      expect(ref.current).toHaveFocus();
    });

    it('disabled input cannot be focused programmatically', () => {
      const ref = React.createRef<HTMLInputElement>();

      renderWithProviders(
        <Input ref={ref} name="test" value="" onChange={() => {}} disabled />
      );

      ref.current?.focus();
      expect(ref.current).not.toHaveFocus();
    });
  });

  describe('Error State Edge Cases', () => {
    it('handles error message changing dynamically', async () => {
      const TestComponent = () => {
        const [error, setError] = React.useState('First error');
        return (
          <>
            <Input name="test" value="" onChange={() => {}} error={error} />
            <button onClick={() => setError('Second error')}>Change Error</button>
          </>
        );
      };

      const user = userEvent.setup();
      renderWithProviders(<TestComponent />);

      expect(screen.getByText('First error')).toBeInTheDocument();

      const button = screen.getByText('Change Error');
      await user.click(button);

      expect(screen.getByText('Second error')).toBeInTheDocument();
      expect(screen.queryByText('First error')).not.toBeInTheDocument();
    });

    it('handles error being removed', async () => {
      const TestComponent = () => {
        const [error, setError] = React.useState<string | undefined>('Has error');
        return (
          <>
            <Input name="test" value="" onChange={() => {}} error={error} />
            <button onClick={() => setError(undefined)}>Clear Error</button>
          </>
        );
      };

      const user = userEvent.setup();
      renderWithProviders(<TestComponent />);

      expect(screen.getByText('Has error')).toBeInTheDocument();

      const button = screen.getByText('Clear Error');
      await user.click(button);

      expect(screen.queryByText('Has error')).not.toBeInTheDocument();
    });

    it('handles empty string error (should not render)', () => {
      renderWithProviders(
        <Input name="test" value="" onChange={() => {}} error="" />
      );

      // Empty error should not render the error paragraph
      const input = screen.getByRole('textbox');
      const errorElements = document.querySelectorAll('.text-red-600');

      // Only label should have red color if error prop exists, but empty error shouldn't render <p>
      const errorParagraphs = Array.from(errorElements).filter(el => el.tagName === 'P');
      expect(errorParagraphs.length).toBe(0);
    });

    it('handles very long error message', () => {
      const longError = 'Error: ' + 'a'.repeat(500);
      renderWithProviders(
        <Input name="test" value="" onChange={() => {}} error={longError} />
      );

      expect(screen.getByText(new RegExp(longError))).toBeInTheDocument();
    });
  });

  describe('onChange Edge Cases', () => {

    it('handles async onChange', async () => {
      const asyncOnChange = vi.fn(async () => {
        await new Promise(resolve => setTimeout(resolve, 10));
      });
      const user = userEvent.setup();

      renderWithProviders(
        <Input name="test" value="" onChange={asyncOnChange} />
      );
      const input = screen.getByRole('textbox');

      await user.type(input, 'test');
      expect(asyncOnChange).toHaveBeenCalled();
    });
  });

  describe('Required Field Edge Cases', () => {
    it('can transition from required to optional', async () => {
      const TestComponent = () => {
        const [required, setRequired] = React.useState(true);
        return (
          <>
            <Input
              name="test"
              label="Field"
              value=""
              onChange={() => {}}
              required={required}
            />
            <button onClick={() => setRequired(false)}>Make Optional</button>
          </>
        );
      };

      const user = userEvent.setup();
      renderWithProviders(<TestComponent />);

      expect(screen.getByText('*')).toBeInTheDocument();

      const button = screen.getByText('Make Optional');
      await user.click(button);

      expect(screen.queryByText('*')).not.toBeInTheDocument();
    });
  });

  describe('Disabled State Transitions', () => {
    it('can transition from enabled to disabled while preserving value', async () => {
      const TestComponent = () => {
        const [disabled, setDisabled] = React.useState(false);
        const [value, setValue] = React.useState('test value');
        return (
          <>
            <Input
              name="test"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              disabled={disabled}
            />
            <button onClick={() => setDisabled(true)}>Disable</button>
          </>
        );
      };

      const user = userEvent.setup();
      renderWithProviders(<TestComponent />);

      const input = screen.getByRole('textbox');
      expect(input).not.toBeDisabled();
      expect(input).toHaveValue('test value');

      const button = screen.getByText('Disable');
      await user.click(button);

      expect(input).toBeDisabled();
      expect(input).toHaveValue('test value'); // Value preserved
    });
  });

  describe('Compact Mode Edge Cases', () => {
    it('transitions between compact and normal spacing', async () => {
      const TestComponent = () => {
        const [compact, setCompact] = React.useState(false);
        return (
          <>
            <Input
              name="test"
              label="Test"
              value=""
              onChange={() => {}}
              compact={compact}
            />
            <button onClick={() => setCompact(!compact)}>Toggle Compact</button>
          </>
        );
      };

      const user = userEvent.setup();
      const { container } = renderWithProviders(<TestComponent />);

      let wrapper = container.firstChild;
      expect(wrapper).toHaveClass('mb-6');

      const button = screen.getByText('Toggle Compact');
      await user.click(button);

      wrapper = container.firstChild;
      expect(wrapper).toHaveClass('mb-3');
    });
  });

  describe('Input Type Edge Cases', () => {
    it('handles switching input types', async () => {
      const TestComponent = () => {
        const [type, setType] = React.useState('text');
        return (
          <>
            <Input name="test" type={type} value="" onChange={() => {}} />
            <button onClick={() => setType('password')}>To Password</button>
          </>
        );
      };

      const user = userEvent.setup();
      renderWithProviders(<TestComponent />);

      const input = document.querySelector('input[name="test"]');
      expect(input).toHaveAttribute('type', 'text');

      const button = screen.getByText('To Password');
      await user.click(button);

      expect(input).toHaveAttribute('type', 'password');
    });
  });
});
