import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../../../test/utils";
import InviteMemberModal from "../InviteMemberModal";
import type { UserSearchResult } from "../../../types/users.types";

// Mock the usersApi module
vi.mock("../../../services/usersApi", () => ({
  searchUsers: vi.fn(),
}));

import { searchUsers } from "../../../services/usersApi";

const mockSearchUsers = vi.mocked(searchUsers);

const mockResults: UserSearchResult[] = [
  {
    id: 1,
    username: "john_doe",
    full_name: "John Doe",
    profile_id: 10,
  },
  {
    id: 2,
    username: "jane_doe",
    full_name: "Jane Doe",
    profile_id: 11,
  },
];

const defaultProps = {
  isOpen: true,
  onClose: vi.fn(),
  onSubmit: vi.fn(),
};

describe("InviteMemberModal", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockSearchUsers.mockReset();
    defaultProps.onClose.mockReset();
    defaultProps.onSubmit.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe("Rendering", () => {
    it("renders nothing when isOpen is false", () => {
      const { container } = renderWithProviders(
        <InviteMemberModal {...defaultProps} isOpen={false} />,
      );
      expect(container.innerHTML).toBe("");
    });

    it("renders modal with title when isOpen is true", () => {
      renderWithProviders(<InviteMemberModal {...defaultProps} />);
      expect(screen.getByText("Invite Member")).toBeInTheDocument();
    });

    it("renders search input and role selector", () => {
      renderWithProviders(<InviteMemberModal {...defaultProps} />);
      expect(
        screen.getByPlaceholderText("Type a username or name..."),
      ).toBeInTheDocument();
      expect(screen.getByText("Role")).toBeInTheDocument();
    });

    it("renders Send Invite button disabled initially", () => {
      renderWithProviders(<InviteMemberModal {...defaultProps} />);
      expect(
        screen.getByRole("button", { name: /send invite/i }),
      ).toBeDisabled();
    });

    it("renders Cancel button", () => {
      renderWithProviders(<InviteMemberModal {...defaultProps} />);
      expect(
        screen.getByRole("button", { name: /cancel/i }),
      ).toBeInTheDocument();
    });
  });

  describe("Full Invite Flow", () => {
    it("search -> select user -> pick role -> submit succeeds", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      const onSubmit = vi.fn().mockResolvedValue(undefined);
      const onClose = vi.fn();

      mockSearchUsers.mockResolvedValue({
        count: 2,
        next: null,
        previous: null,
        results: mockResults,
      });

      renderWithProviders(
        <InviteMemberModal
          isOpen={true}
          onClose={onClose}
          onSubmit={onSubmit}
        />,
      );

      // 1. Type username and wait for search
      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "doe",
      );
      await act(() => vi.advanceTimersByTime(350));

      // 2. Click a result
      await waitFor(() => {
        expect(screen.getByText("john_doe")).toBeInTheDocument();
      });
      await user.click(screen.getByText("john_doe"));

      // 3. Change role to assistant
      const roleSelect = document.querySelector(
        'select[name="invite-role"]',
      ) as HTMLSelectElement;
      await user.selectOptions(roleSelect, "assistant");

      // 4. Click Send Invite
      const submitButton = screen.getByRole("button", { name: /send invite/i });
      expect(submitButton).toBeEnabled();
      await user.click(submitButton);

      // 5. Verify onSubmit called with correct args
      expect(onSubmit).toHaveBeenCalledWith(1, "assistant");
      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      });
    });

    it("shows error when submit fails", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      const onSubmit = vi
        .fn()
        .mockRejectedValue(new Error("User is already a member"));

      mockSearchUsers.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockResults[0]],
      });

      renderWithProviders(
        <InviteMemberModal
          isOpen={true}
          onClose={vi.fn()}
          onSubmit={onSubmit}
        />,
      );

      // Search and select
      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "john",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByText("john_doe")).toBeInTheDocument();
      });
      await user.click(screen.getByText("john_doe"));

      // Submit
      await user.click(screen.getByRole("button", { name: /send invite/i }));

      // Error should be shown
      await waitFor(() => {
        expect(
          screen.getByText("User is already a member"),
        ).toBeInTheDocument();
      });
    });

    it("shows sending text on button while submitting", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      let resolveSubmit: () => void;
      const onSubmit = vi.fn().mockReturnValue(
        new Promise<void>((resolve) => {
          resolveSubmit = resolve;
        }),
      );

      mockSearchUsers.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockResults[0]],
      });

      renderWithProviders(
        <InviteMemberModal
          isOpen={true}
          onClose={vi.fn()}
          onSubmit={onSubmit}
        />,
      );

      // Search and select
      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "john",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByText("john_doe")).toBeInTheDocument();
      });
      await user.click(screen.getByText("john_doe"));

      // Submit
      await user.click(screen.getByRole("button", { name: /send invite/i }));

      // Should show "Sending..."
      expect(screen.getByText("Sending...")).toBeInTheDocument();

      // Resolve the submit
      await act(async () => {
        resolveSubmit!();
      });
    });
  });

  describe("Close and Reset", () => {
    it("calls onClose when clicking Cancel", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      const onClose = vi.fn();

      renderWithProviders(
        <InviteMemberModal
          isOpen={true}
          onClose={onClose}
          onSubmit={vi.fn()}
        />,
      );

      await user.click(screen.getByRole("button", { name: /cancel/i }));
      expect(onClose).toHaveBeenCalled();
    });

    it("calls onClose when clicking close button", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      const onClose = vi.fn();

      renderWithProviders(
        <InviteMemberModal
          isOpen={true}
          onClose={onClose}
          onSubmit={vi.fn()}
        />,
      );

      await user.click(screen.getByRole("button", { name: /close/i }));
      expect(onClose).toHaveBeenCalled();
    });

    it("resets state when reopened", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

      mockSearchUsers.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockResults[0]],
      });

      const { rerender } = renderWithProviders(
        <InviteMemberModal {...defaultProps} />,
      );

      // Search and select a user
      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "john",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByText("john_doe")).toBeInTheDocument();
      });
      await user.click(screen.getByText("john_doe"));

      // Verify user is selected (pill visible)
      expect(screen.getByText("john_doe")).toBeInTheDocument();

      // Close modal
      rerender(<InviteMemberModal {...defaultProps} isOpen={false} />);

      // Reopen modal
      rerender(<InviteMemberModal {...defaultProps} isOpen={true} />);

      // Should be back to empty search input
      expect(
        screen.getByPlaceholderText("Type a username or name..."),
      ).toBeInTheDocument();
      // Send Invite should be disabled again
      expect(
        screen.getByRole("button", { name: /send invite/i }),
      ).toBeDisabled();
    });
  });

  describe("Role Selection", () => {
    it("defaults to student role", () => {
      renderWithProviders(<InviteMemberModal {...defaultProps} />);
      const roleSelect = document.querySelector(
        'select[name="invite-role"]',
      ) as HTMLSelectElement;
      expect(roleSelect).toHaveValue("student");
    });

    it("allows changing role to assistant", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderWithProviders(<InviteMemberModal {...defaultProps} />);

      const roleSelect = document.querySelector(
        'select[name="invite-role"]',
      ) as HTMLSelectElement;
      await user.selectOptions(roleSelect, "assistant");
      expect(roleSelect).toHaveValue("assistant");
    });

    it("allows changing role to teacher", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderWithProviders(<InviteMemberModal {...defaultProps} />);

      const roleSelect = document.querySelector(
        'select[name="invite-role"]',
      ) as HTMLSelectElement;
      await user.selectOptions(roleSelect, "teacher");
      expect(roleSelect).toHaveValue("teacher");
    });
  });
});
