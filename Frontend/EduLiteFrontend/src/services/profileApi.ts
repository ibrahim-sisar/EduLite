import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

// API Response Types - exactly what backend returns
interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string; // ISO date string
}

interface UserProfile {
  url: string;
  user: number;
  user_url: string;
  bio: string | null;
  occupation: string | null;
  country: string | null;
  preferred_language: string | null;
  secondary_language: string | null;
  picture: string | null; // URL or null for profile picture
  website_url: string | null;
  friends: number[];
}

interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

// Combined user data for profile page
interface ProfileData {
  user: User;
  profile: UserProfile;
}

// Request types
interface ProfileUpdateRequest {
  bio?: string;
  occupation?: string;
  country?: string;
  preferred_language?: string;
  secondary_language?: string;
  website_url?: string;
}

// Get auth headers with stored token
const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem("access");
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  };
};

// Get auth headers for file upload (multipart/form-data)
const getFileUploadHeaders = (): Record<string, string> => {
  const token = localStorage.getItem("access");
  return {
    "Authorization": `Bearer ${token}`,
  };
};

// Get current user profile
export const getUserProfile = async (): Promise<UserProfile> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/users/me/profile/`, {
      headers: getAuthHeaders(),
      timeout: 10000,
    });
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error("Authentication required. Please log in again.");
    }
    throw new Error(error.response?.data?.detail || "Failed to fetch profile");
  }
};

// Update user profile
export const updateUserProfile = async (profileData: ProfileUpdateRequest): Promise<UserProfile> => {
  try {
    const response = await axios.patch(
      `${API_BASE_URL}/users/me/profile/`,
      profileData,
      {
        headers: getAuthHeaders(),
        timeout: 10000,
      }
    );
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error("Authentication required. Please log in again.");
    }
    if (error.response?.status === 400) {
      throw new Error(error.response?.data?.detail || "Invalid profile data");
    }
    throw new Error(error.response?.data?.detail || "Failed to update profile");
  }
};

// Upload profile picture
export const uploadProfilePicture = async (file: File): Promise<UserProfile> => {
  try {
    const formData = new FormData();
    formData.append("picture", file);

    const response = await axios.patch(
      `${API_BASE_URL}/users/me/profile/`,
      formData,
      {
        headers: getFileUploadHeaders(),
        timeout: 30000, // Longer timeout for file uploads
      }
    );
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error("Authentication required. Please log in again.");
    }
    if (error.response?.status === 400) {
      const message = error.response?.data?.picture?.[0] ||
                     error.response?.data?.detail ||
                     "Invalid file. Please use JPG, PNG, or WEBP format.";
      throw new Error(message);
    }
    throw new Error("Failed to upload profile picture");
  }
};

// Get user basic info (username, email)
export const getUserInfo = async (): Promise<User> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/users/me/`, {
      headers: getAuthHeaders(),
      timeout: 10000,
    });
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error("Authentication required. Please log in again.");
    }
    throw new Error(error.response?.data?.detail || "Failed to fetch user info");
  }
};

// Delete profile picture
export const deleteProfilePicture = async (): Promise<UserProfile> => {
  try {
    const response = await axios.patch(
      `${API_BASE_URL}/users/me/profile/`,
      { picture: null },
      {
        headers: getAuthHeaders(),
        timeout: 10000,
      }
    );
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error("Authentication required. Please log in again.");
    }
    throw new Error(error.response?.data?.detail || "Failed to remove profile picture");
  }
};

// Export types for use in components
export type { User, UserProfile, ProfileData, ProfileUpdateRequest };
