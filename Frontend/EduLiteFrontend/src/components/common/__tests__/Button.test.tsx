import { describe, it, expect, vi } from "vitest";
import { renderWithProviders, screen } from "@/test/utils";
import userEvent from "@testing-library/user-event";
import Button from "../Button";

describe("Button Component", () => {
  describe("Rendering", () => {
    it("renders with children text", () => {
      renderWithProviders(<Button>Click me</Button>);
      expect(
        screen.getByRole("button", { name: /click me/i }),
      ).toBeInTheDocument();
    });

    it("renders with default primary type", () => {
      renderWithProviders(<Button>Primary Button</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("bg-blue-600");
    });

    it("renders with custom className", () => {
      renderWithProviders(<Button className="custom-class">Button</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("custom-class");
    });
  });

  describe("Type Variants", () => {
    it("renders primary variant correctly", () => {
      renderWithProviders(<Button type="primary">Primary</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("bg-blue-600", "text-white");
    });

    it("renders secondary variant correctly", () => {
      renderWithProviders(<Button type="secondary">Secondary</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass(
        "bg-white",
        "text-blue-700",
        "border",
        "border-blue-600",
      );
    });

    it("renders danger variant correctly", () => {
      renderWithProviders(<Button type="danger">Delete</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("bg-red-600", "text-white");
    });
  });

  describe("Size Variants", () => {
    it("renders small size correctly", () => {
      renderWithProviders(<Button size="sm">Small</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("px-3", "py-1.5", "text-sm");
    });

    it("renders medium size correctly (default)", () => {
      renderWithProviders(<Button size="md">Medium</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("px-4", "py-2", "text-base");
    });

    it("renders large size correctly", () => {
      renderWithProviders(<Button size="lg">Large</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("px-6", "py-3", "text-lg");
    });
  });

  describe("Width Variants", () => {
    it("renders auto width (default)", () => {
      renderWithProviders(<Button>Auto Width</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("w-auto");
    });

    it("renders full width", () => {
      renderWithProviders(<Button width="full">Full Width</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("w-full");
    });

    it("renders half width", () => {
      renderWithProviders(<Button width="half">Half Width</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("w-1/2");
    });

    it("renders one-third width", () => {
      renderWithProviders(<Button width="one-third">One Third</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("w-1/3");
    });
  });

  describe("Disabled State", () => {
    it("renders disabled button correctly", () => {
      renderWithProviders(<Button disabled>Disabled</Button>);
      const button = screen.getByRole("button");
      expect(button).toBeDisabled();
      expect(button).toHaveClass(
        "disabled:opacity-50",
        "disabled:cursor-not-allowed",
      );
      expect(button).toHaveAttribute("aria-disabled", "true");
    });

    it("does not call onClick when disabled", async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup({ delay: null });

      renderWithProviders(
        <Button disabled onClick={handleClick}>
          Disabled
        </Button>,
      );
      const button = screen.getByRole("button");

      await user.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe("Click Handler", () => {
    it("calls onClick when button is clicked", async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup({ delay: null });

      renderWithProviders(<Button onClick={handleClick}>Click Me</Button>);
      const button = screen.getByRole("button");

      await user.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it("calls onClick multiple times", async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup({ delay: null });

      renderWithProviders(<Button onClick={handleClick}>Click Me</Button>);
      const button = screen.getByRole("button");

      await user.click(button);
      await user.click(button);
      await user.click(button);

      expect(handleClick).toHaveBeenCalledTimes(3);
    });
  });

  describe("Accessibility", () => {
    it("has button role", () => {
      renderWithProviders(<Button>Button</Button>);
      expect(screen.getByRole("button")).toBeInTheDocument();
    });

    it("has proper type attribute", () => {
      renderWithProviders(<Button>Button</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("type", "button");
    });

    it("supports aria-label", () => {
      renderWithProviders(<Button aria-label="Close modal">×</Button>);
      const button = screen.getByRole("button", { name: /close modal/i });
      expect(button).toBeInTheDocument();
    });

    it("has focus styles", () => {
      renderWithProviders(<Button>Focus Me</Button>);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("focus:outline-none", "focus-visible:ring-2");
    });
  });

  describe("Keyboard Navigation", () => {
    it("can be focused with keyboard", async () => {
      const user = userEvent.setup({ delay: null });

      renderWithProviders(<Button>Keyboard Button</Button>);
      const button = screen.getByRole("button");

      await user.tab();
      expect(button).toHaveFocus();
    });

    it("can be activated with Enter key", async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup({ delay: null });

      renderWithProviders(<Button onClick={handleClick}>Press Enter</Button>);
      const button = screen.getByRole("button");

      button.focus();
      await user.keyboard("{Enter}");

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it("can be activated with Space key", async () => {
      const handleClick = vi.fn();
      const user = userEvent.setup({ delay: null });

      renderWithProviders(<Button onClick={handleClick}>Press Space</Button>);
      const button = screen.getByRole("button");

      button.focus();
      await user.keyboard(" ");

      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  describe("Forward Ref", () => {
    it("forwards ref to button element", () => {
      const ref = { current: null };

      renderWithProviders(<Button ref={ref}>Button with Ref</Button>);

      expect(ref.current).toBeInstanceOf(HTMLButtonElement);
      expect((ref.current as unknown as HTMLButtonElement)?.textContent).toBe(
        "Button with Ref",
      );
    });
  });

  describe("HTML Button Attributes", () => {
    it("accepts and applies additional HTML button attributes", () => {
      renderWithProviders(
        <Button data-testid="custom-button" title="Custom title">
          Button
        </Button>,
      );

      const button = screen.getByTestId("custom-button");
      expect(button).toHaveAttribute("title", "Custom title");
    });
  });
});
