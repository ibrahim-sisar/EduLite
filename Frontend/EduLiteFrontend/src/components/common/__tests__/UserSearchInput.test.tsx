import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../../../test/utils";
import UserSearchInput from "../UserSearchInput";
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
    email: "john@example.com",
    first_name: "John",
    last_name: "Doe",
    profile_id: 10,
  },
  {
    id: 2,
    username: "jane_doe",
    full_name: "Jane Doe",
    profile_id: 11,
  },
  {
    id: 3,
    username: "private_user",
    profile_id: 12,
  },
];

const defaultProps = {
  onSelect: vi.fn(),
  selectedUser: null,
  onClear: vi.fn(),
};

describe("UserSearchInput", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockSearchUsers.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe("Rendering", () => {
    it("renders search input with placeholder", () => {
      renderWithProviders(<UserSearchInput {...defaultProps} />);
      expect(
        screen.getByPlaceholderText("Type a username or name..."),
      ).toBeInTheDocument();
    });

    it("renders label when provided", () => {
      renderWithProviders(
        <UserSearchInput {...defaultProps} label="Find a user" />,
      );
      expect(screen.getByText("Find a user")).toBeInTheDocument();
    });

    it("renders selected user pill when selectedUser prop is set", () => {
      renderWithProviders(
        <UserSearchInput
          {...defaultProps}
          selectedUser={mockResults[0]}
        />,
      );
      expect(screen.getByText("john_doe")).toBeInTheDocument();
      expect(screen.getByText("John Doe")).toBeInTheDocument();
      // Search input should not be visible
      expect(
        screen.queryByPlaceholderText("Type a username or name..."),
      ).not.toBeInTheDocument();
    });

    it("renders disabled state correctly", () => {
      renderWithProviders(
        <UserSearchInput {...defaultProps} disabled={true} />,
      );
      expect(
        screen.getByPlaceholderText("Type a username or name..."),
      ).toBeDisabled();
    });

    it("renders external error message", () => {
      renderWithProviders(
        <UserSearchInput {...defaultProps} error="Something went wrong" />,
      );
      expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    });
  });

  describe("Search Behavior", () => {
    it("does not search when query is less than 2 characters", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "a",
      );
      await act(() => vi.advanceTimersByTime(400));

      expect(mockSearchUsers).not.toHaveBeenCalled();
    });

    it("shows min chars hint when typing 1 character", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "a",
      );

      expect(
        screen.getByText("Type at least 2 characters to search"),
      ).toBeInTheDocument();
    });

    it("debounces search input by 300ms", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockResults[0]],
      });

      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "john",
      );

      // Not called yet — debounce hasn't fired
      expect(mockSearchUsers).not.toHaveBeenCalled();

      // Advance past debounce
      await act(() => vi.advanceTimersByTime(350));

      expect(mockSearchUsers).toHaveBeenCalledWith({
        q: "john",
        page_size: 8,
      });
    });

    it("displays search results in dropdown", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 3,
        next: null,
        previous: null,
        results: mockResults,
      });

      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "doe",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByText("john_doe")).toBeInTheDocument();
        expect(screen.getByText("jane_doe")).toBeInTheDocument();
        expect(screen.getByText("private_user")).toBeInTheDocument();
      });
    });

    it("shows no results message when search returns empty", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 0,
        next: null,
        previous: null,
        results: [],
      });

      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "nonexistent",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByText("No users found")).toBeInTheDocument();
      });
    });

    it("shows error message on API failure", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockRejectedValue(new Error("Network error"));

      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "test",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByText("Network error")).toBeInTheDocument();
      });
    });

    it("only shows username for privacy-hidden users", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockResults[2]], // private_user with no full_name
      });

      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "private",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByText("private_user")).toBeInTheDocument();
      });

      // Ensure no "undefined" or empty full_name text
      const listbox = screen.getByRole("listbox");
      expect(listbox.textContent).not.toContain("undefined");
    });
  });

  describe("Selection", () => {
    it("calls onSelect when clicking a result", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      const onSelect = vi.fn();
      mockSearchUsers.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockResults[0]],
      });

      renderWithProviders(
        <UserSearchInput {...defaultProps} onSelect={onSelect} />,
      );

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "john",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByText("john_doe")).toBeInTheDocument();
      });

      await user.click(screen.getByText("john_doe"));
      expect(onSelect).toHaveBeenCalledWith(mockResults[0]);
    });

    it("closes dropdown after selection", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 2,
        next: null,
        previous: null,
        results: [mockResults[0], mockResults[1]],
      });

      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "doe",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByRole("listbox")).toBeInTheDocument();
      });

      await user.click(screen.getByText("john_doe"));
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    });

    it("calls onClear when clicking clear button on pill", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      const onClear = vi.fn();

      renderWithProviders(
        <UserSearchInput
          {...defaultProps}
          selectedUser={mockResults[0]}
          onClear={onClear}
        />,
      );

      await user.click(
        screen.getByRole("button", { name: /clear selection/i }),
      );
      expect(onClear).toHaveBeenCalledTimes(1);
    });
  });

  describe("Keyboard Navigation", () => {
    const setupWithResults = async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 3,
        next: null,
        previous: null,
        results: mockResults,
      });

      renderWithProviders(<UserSearchInput {...defaultProps} />);
      const input = screen.getByPlaceholderText("Type a username or name...");

      await user.type(input, "doe");
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByRole("listbox")).toBeInTheDocument();
      });

      return { user, input };
    };

    it("highlights first result on ArrowDown", async () => {
      const { user, input } = await setupWithResults();

      await user.type(input, "{ArrowDown}");

      const firstOption = screen.getByText("john_doe").closest("[role='option']");
      expect(firstOption).toHaveAttribute("aria-selected", "true");
    });

    it("wraps to first item when ArrowDown at end", async () => {
      const { user, input } = await setupWithResults();

      // Navigate to end
      await user.type(input, "{ArrowDown}{ArrowDown}{ArrowDown}");
      // One more should wrap to first
      await user.type(input, "{ArrowDown}");

      const firstOption = screen.getByText("john_doe").closest("[role='option']");
      expect(firstOption).toHaveAttribute("aria-selected", "true");
    });

    it("wraps to last item when ArrowUp at beginning", async () => {
      const { user, input } = await setupWithResults();

      await user.type(input, "{ArrowUp}");

      const lastOption = screen.getByText("private_user").closest("[role='option']");
      expect(lastOption).toHaveAttribute("aria-selected", "true");
    });

    it("selects highlighted result on Enter", async () => {
      const onSelect = vi.fn();
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 3,
        next: null,
        previous: null,
        results: mockResults,
      });

      renderWithProviders(
        <UserSearchInput {...defaultProps} onSelect={onSelect} />,
      );
      const input = screen.getByPlaceholderText("Type a username or name...");

      await user.type(input, "doe");
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByRole("listbox")).toBeInTheDocument();
      });

      await user.type(input, "{ArrowDown}{Enter}");
      expect(onSelect).toHaveBeenCalledWith(mockResults[0]);
    });

    it("closes dropdown on Escape", async () => {
      const { user, input } = await setupWithResults();

      await user.type(input, "{Escape}");

      expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    });
  });

  describe("Click Outside", () => {
    it("closes dropdown when clicking outside the component", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockResults[0]],
      });

      renderWithProviders(
        <div>
          <UserSearchInput {...defaultProps} />
          <button>Outside</button>
        </div>,
      );

      await user.type(
        screen.getByPlaceholderText("Type a username or name..."),
        "john",
      );
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByRole("listbox")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Outside"));
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("has combobox role on input", () => {
      renderWithProviders(<UserSearchInput {...defaultProps} />);
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    it("has aria-expanded matching dropdown state", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockResults[0]],
      });

      renderWithProviders(<UserSearchInput {...defaultProps} />);
      const combobox = screen.getByRole("combobox");

      expect(combobox).toHaveAttribute("aria-expanded", "false");

      await user.type(combobox, "john");
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(combobox).toHaveAttribute("aria-expanded", "true");
      });
    });

    it("has listbox role on dropdown", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [mockResults[0]],
      });

      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(screen.getByRole("combobox"), "john");
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getByRole("listbox")).toBeInTheDocument();
      });
    });

    it("has option role on each result item", async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      mockSearchUsers.mockResolvedValue({
        count: 2,
        next: null,
        previous: null,
        results: [mockResults[0], mockResults[1]],
      });

      renderWithProviders(<UserSearchInput {...defaultProps} />);

      await user.type(screen.getByRole("combobox"), "doe");
      await act(() => vi.advanceTimersByTime(350));

      await waitFor(() => {
        expect(screen.getAllByRole("option")).toHaveLength(2);
      });
    });
  });
});
