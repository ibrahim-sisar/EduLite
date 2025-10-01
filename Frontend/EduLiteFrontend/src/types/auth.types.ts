// Authentication-related TypeScript type definitions

/**
 * Form data for user login
 */
export interface LoginFormData {
  username: string;
  password: string;
}

/**
 * Form data for user signup/registration
 */
export interface SignupFormData {
  username: string;
  email: string;
  password: string;
  password2: string;
}

/**
 * Validation errors for form fields
 * Keys correspond to form field names
 */
export interface ValidationErrors {
  username?: string;
  email?: string;
  password?: string;
  password2?: string;
}

/**
 * Response from registration API endpoint
 */
export interface RegisterResponse {
  message: string;
  user: {
    id: number;
    username: string;
    email: string;
  };
}

/**
 * Response from login/token API endpoint
 */
export interface LoginResponse {
  access: string;
  refresh: string;
}

/**
 * Django REST Framework error response structure
 * Can contain field-specific errors or non_field_errors
 */
export interface BackendErrorResponse {
  username?: string | string[];
  email?: string | string[];
  password?: string | string[];
  password2?: string | string[];
  non_field_errors?: string | string[];
  detail?: string;
}
