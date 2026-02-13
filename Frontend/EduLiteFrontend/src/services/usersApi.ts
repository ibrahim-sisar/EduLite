import axios from "axios";
import { getSafeErrorMessage } from "../utils/errorUtils";
import type {
  UserSearchParams,
  UserSearchPaginatedResponse,
} from "../types/users.types";

const API_BASE_URL = "http://localhost:8000/api";

/**
 * Search for users by username, first name, or last name.
 * Privacy settings are respected — some fields may be absent.
 *
 * @param params - Search parameters (q required, min 2 chars)
 * @returns Paginated list of matching users
 */
export const searchUsers = async (
  params: UserSearchParams,
): Promise<UserSearchPaginatedResponse> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/users/search/`, {
      params,
      timeout: 10000,
    });
    return response.data;
  } catch (error) {
    throw new Error(getSafeErrorMessage(error, "Failed to search users"));
  }
};
