import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../../../test/utils";
import EnrollmentActions from "../EnrollmentActions";
import type { CourseDetail } from "../../../types/courses.types";
import type { UseEnrollmentReturn } from "../../../hooks/useEnrollment";

const baseCourse: CourseDetail = {
  id: 1,
  title: "Test Course",
  outline: null,
  language: null,
  country: null,
  subject: null,
  visibility: "public",
  start_date: null,
  end_date: null,
  duration_time: 0,
  allow_join_requests: true,
  is_active: true,
  member_count: 2,
  user_role: null,
  user_status: null,
  members: [],
  modules: [],
};

const baseEnrollment: UseEnrollmentReturn = {
  status: null,
  role: null,
  isLoading: false,
  isLastTeacher: false,
  enroll: vi.fn(),
  leave: vi.fn(),
  cancelRequest: vi.fn(),
};

describe("EnrollmentActions", () => {
  describe("Not Enrolled", () => {
    it("renders Join Course button for public course", () => {
      renderWithProviders(
        <EnrollmentActions
          course={{ ...baseCourse, visibility: "public" }}
          enrollment={{ ...baseEnrollment }}
        />
      );
      expect(
        screen.getByRole("button", { name: /join course/i })
      ).toBeInTheDocument();
    });

    it("renders Request to Join button for restricted course with join requests", () => {
      renderWithProviders(
        <EnrollmentActions
          course={{
            ...baseCourse,
            visibility: "restricted",
            allow_join_requests: true,
          }}
          enrollment={{ ...baseEnrollment }}
        />
      );
      expect(
        screen.getByRole("button", { name: /request to join/i })
      ).toBeInTheDocument();
    });

    it("renders Enrollment Closed for restricted course without join requests", () => {
      renderWithProviders(
        <EnrollmentActions
          course={{
            ...baseCourse,
            visibility: "restricted",
            allow_join_requests: false,
          }}
          enrollment={{ ...baseEnrollment }}
        />
      );
      expect(screen.getByText(/enrollment closed/i)).toBeInTheDocument();
    });

    it("renders nothing for private course", () => {
      const { container } = renderWithProviders(
        <EnrollmentActions
          course={{ ...baseCourse, visibility: "private" }}
          enrollment={{ ...baseEnrollment }}
        />
      );
      expect(container.innerHTML).toBe("");
    });

    it("calls enroll when Join Course is clicked", async () => {
      const user = userEvent.setup();
      const mockEnroll = vi.fn();
      renderWithProviders(
        <EnrollmentActions
          course={{ ...baseCourse, visibility: "public" }}
          enrollment={{ ...baseEnrollment, enroll: mockEnroll }}
        />
      );

      await user.click(
        screen.getByRole("button", { name: /join course/i })
      );
      expect(mockEnroll).toHaveBeenCalledTimes(1);
    });

    it("disables button when loading", () => {
      renderWithProviders(
        <EnrollmentActions
          course={{ ...baseCourse, visibility: "public" }}
          enrollment={{ ...baseEnrollment, isLoading: true }}
        />
      );
      expect(
        screen.getByRole("button", { name: /joining/i })
      ).toBeDisabled();
    });
  });

  describe("Pending", () => {
    it("renders pending banner with cancel button", () => {
      renderWithProviders(
        <EnrollmentActions
          course={baseCourse}
          enrollment={{
            ...baseEnrollment,
            status: "pending",
            role: "student",
          }}
        />
      );
      expect(screen.getByText(/pending approval/i)).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /cancel request/i })
      ).toBeInTheDocument();
    });

    it("calls cancelRequest when Cancel Request is clicked", async () => {
      const user = userEvent.setup();
      const mockCancel = vi.fn();
      renderWithProviders(
        <EnrollmentActions
          course={baseCourse}
          enrollment={{
            ...baseEnrollment,
            status: "pending",
            role: "student",
            cancelRequest: mockCancel,
          }}
        />
      );

      await user.click(
        screen.getByRole("button", { name: /cancel request/i })
      );
      expect(mockCancel).toHaveBeenCalledTimes(1);
    });
  });

  describe("Invited", () => {
    it("renders invitation banner with disabled accept/decline buttons", () => {
      renderWithProviders(
        <EnrollmentActions
          course={baseCourse}
          enrollment={{
            ...baseEnrollment,
            status: "invited",
            role: "student",
          }}
        />
      );
      expect(screen.getByText(/invited to join/i)).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /accept/i })
      ).toBeDisabled();
      expect(
        screen.getByRole("button", { name: /decline/i })
      ).toBeDisabled();
    });
  });

  describe("Enrolled", () => {
    it("renders leave button for enrolled non-teacher", () => {
      renderWithProviders(
        <EnrollmentActions
          course={baseCourse}
          enrollment={{
            ...baseEnrollment,
            status: "enrolled",
            role: "student",
          }}
        />
      );
      expect(
        screen.getByRole("button", { name: /leave course/i })
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /leave course/i })
      ).toBeEnabled();
    });

    it("renders disabled leave button for last teacher", () => {
      renderWithProviders(
        <EnrollmentActions
          course={baseCourse}
          enrollment={{
            ...baseEnrollment,
            status: "enrolled",
            role: "teacher",
            isLastTeacher: true,
          }}
        />
      );
      expect(
        screen.getByRole("button", { name: /leave course/i })
      ).toBeDisabled();
    });

    it("shows leave confirmation modal on click", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <EnrollmentActions
          course={baseCourse}
          enrollment={{
            ...baseEnrollment,
            status: "enrolled",
            role: "student",
          }}
        />
      );

      await user.click(
        screen.getByRole("button", { name: /leave course/i })
      );

      // Confirmation modal should appear
      expect(
        screen.getByText(/are you sure you want to leave/i)
      ).toBeInTheDocument();
    });

    it("calls leave on confirm", async () => {
      const user = userEvent.setup();
      const mockLeave = vi.fn();
      renderWithProviders(
        <EnrollmentActions
          course={baseCourse}
          enrollment={{
            ...baseEnrollment,
            status: "enrolled",
            role: "student",
            leave: mockLeave,
          }}
        />
      );

      await user.click(
        screen.getByRole("button", { name: /leave course/i })
      );

      // Click confirm in modal
      const confirmButtons = screen.getAllByRole("button", {
        name: /leave course/i,
      });
      // The confirm button in the modal (second one)
      await user.click(confirmButtons[confirmButtons.length - 1]);

      expect(mockLeave).toHaveBeenCalledTimes(1);
    });

    it("renders nothing for enrolled teacher (not last)", () => {
      const { container } = renderWithProviders(
        <EnrollmentActions
          course={baseCourse}
          enrollment={{
            ...baseEnrollment,
            status: "enrolled",
            role: "teacher",
            isLastTeacher: false,
          }}
        />
      );
      // Teacher with other teachers — no leave button rendered
      expect(container.innerHTML).toBe("");
    });
  });
});
