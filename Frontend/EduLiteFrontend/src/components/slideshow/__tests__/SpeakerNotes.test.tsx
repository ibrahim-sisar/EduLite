import { describe, it, expect, vi } from "vitest";
import { renderWithProviders, screen } from "@/test/utils";
import userEvent from "@testing-library/user-event";
import SpeakerNotes from "../SpeakerNotes";

describe("SpeakerNotes Component", () => {
  describe("Rendering", () => {
    it("renders nothing when notes are null", () => {
      const { container } = renderWithProviders(
        <SpeakerNotes notes={null} isVisible={true} onToggle={vi.fn()} />,
      );

      expect(container.firstChild).toBeNull();
    });

    it("renders nothing when notes are empty string", () => {
      const { container } = renderWithProviders(
        <SpeakerNotes notes="" isVisible={true} onToggle={vi.fn()} />,
      );

      expect(container.firstChild).toBeNull();
    });

    it("renders nothing when notes are only whitespace", () => {
      const { container } = renderWithProviders(
        <SpeakerNotes notes="   " isVisible={true} onToggle={vi.fn()} />,
      );

      expect(container.firstChild).toBeNull();
    });

    it("renders toggle button when notes exist", () => {
      renderWithProviders(
        <SpeakerNotes
          notes="Test notes"
          isVisible={false}
          onToggle={vi.fn()}
        />,
      );

      expect(
        screen.getByRole("button", { name: /speaker notes/i }),
      ).toBeInTheDocument();
    });

    it("shows notes content when visible", () => {
      renderWithProviders(
        <SpeakerNotes
          notes="These are my speaker notes"
          isVisible={true}
          onToggle={vi.fn()}
        />,
      );

      expect(
        screen.getByText("These are my speaker notes"),
      ).toBeInTheDocument();
    });

    it("hides notes content when not visible", () => {
      renderWithProviders(
        <SpeakerNotes
          notes="These are my speaker notes"
          isVisible={false}
          onToggle={vi.fn()}
        />,
      );

      expect(
        screen.queryByText("These are my speaker notes"),
      ).not.toBeInTheDocument();
    });
  });

  describe("Toggle Functionality", () => {
    it("calls onToggle when button is clicked", async () => {
      const handleToggle = vi.fn();
      const user = userEvent.setup({ delay: null });

      renderWithProviders(
        <SpeakerNotes
          notes="Test notes"
          isVisible={false}
          onToggle={handleToggle}
        />,
      );

      const toggleButton = screen.getByRole("button");
      await user.click(toggleButton);

      expect(handleToggle).toHaveBeenCalledTimes(1);
    });

    it("calls onToggle multiple times", async () => {
      const handleToggle = vi.fn();
      const user = userEvent.setup({ delay: null });

      renderWithProviders(
        <SpeakerNotes
          notes="Test notes"
          isVisible={false}
          onToggle={handleToggle}
        />,
      );

      const toggleButton = screen.getByRole("button");
      await user.click(toggleButton);
      await user.click(toggleButton);

      expect(handleToggle).toHaveBeenCalledTimes(2);
    });
  });

  describe("UI Elements", () => {
    it('shows "Speaker Notes" label', () => {
      renderWithProviders(
        <SpeakerNotes
          notes="Test notes"
          isVisible={false}
          onToggle={vi.fn()}
        />,
      );

      expect(screen.getByText("Speaker Notes")).toBeInTheDocument();
    });

    it("shows keyboard shortcut hint (N)", () => {
      renderWithProviders(
        <SpeakerNotes
          notes="Test notes"
          isVisible={false}
          onToggle={vi.fn()}
        />,
      );

      expect(screen.getByText("N")).toBeInTheDocument();
    });

    it("shows chevron down icon when visible", () => {
      const { container } = renderWithProviders(
        <SpeakerNotes notes="Test notes" isVisible={true} onToggle={vi.fn()} />,
      );

      // HiChevronDown is rendered when visible
      const svg = container.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });

    it("shows chevron up icon when hidden", () => {
      const { container } = renderWithProviders(
        <SpeakerNotes
          notes="Test notes"
          isVisible={false}
          onToggle={vi.fn()}
        />,
      );

      // HiChevronUp is rendered when hidden
      const svg = container.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("has accessible aria-label when hidden", () => {
      renderWithProviders(
        <SpeakerNotes
          notes="Test notes"
          isVisible={false}
          onToggle={vi.fn()}
        />,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("aria-label", "Show speaker notes");
    });

    it("has accessible aria-label when visible", () => {
      renderWithProviders(
        <SpeakerNotes notes="Test notes" isVisible={true} onToggle={vi.fn()} />,
      );

      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("aria-label", "Hide speaker notes");
    });
  });

  describe("Content Formatting", () => {
    it("preserves whitespace and line breaks", () => {
      const notesWithLineBreaks = "Line 1\nLine 2\nLine 3";
      renderWithProviders(
        <SpeakerNotes
          notes={notesWithLineBreaks}
          isVisible={true}
          onToggle={vi.fn()}
        />,
      );

      const notesElement = screen.getByText(/Line 1/);
      expect(notesElement).toHaveClass("whitespace-pre-wrap");
    });
  });
});
