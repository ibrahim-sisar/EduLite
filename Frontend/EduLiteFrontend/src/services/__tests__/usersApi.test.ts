import { describe, it, expect, beforeEach, afterEach } from "vitest";
import axios from "axios";
import MockAdapter from "axios-mock-adapter";
import { searchUsers } from "../usersApi";

describe("usersApi", () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  describe("searchUsers", () => {
    it("should search users with query parameter", async () => {
      const mockResponse = {
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            username: "john_doe",
            email: "john@example.com",
            first_name: "John",
            last_name: "Doe",
            full_name: "John Doe",
            profile_id: 10,
          },
          {
            id: 2,
            username: "johnny",
            full_name: "Johnny Smith",
            profile_id: 11,
          },
        ],
      };

      mock
        .onGet("http://localhost:8000/api/users/search/", {
          params: { q: "john" },
        })
        .reply(200, mockResponse);

      const result = await searchUsers({ q: "john" });
      expect(result).toEqual(mockResponse);
      expect(result.results).toHaveLength(2);
    });

    it("should pass pagination parameters", async () => {
      const mockResponse = {
        count: 10,
        next: "http://localhost:8000/api/users/search/?q=test&page=3",
        previous: "http://localhost:8000/api/users/search/?q=test&page=1",
        results: [
          { id: 5, username: "tester5", profile_id: 50 },
        ],
      };

      mock
        .onGet("http://localhost:8000/api/users/search/", {
          params: { q: "test", page: 2, page_size: 5 },
        })
        .reply(200, mockResponse);

      const result = await searchUsers({ q: "test", page: 2, page_size: 5 });
      expect(result.count).toBe(10);
      expect(result.next).toContain("page=3");
      expect(result.previous).toContain("page=1");
    });

    it("should handle empty results", async () => {
      const mockResponse = {
        count: 0,
        next: null,
        previous: null,
        results: [],
      };

      mock
        .onGet("http://localhost:8000/api/users/search/")
        .reply(200, mockResponse);

      const result = await searchUsers({ q: "nonexistent" });
      expect(result.count).toBe(0);
      expect(result.results).toHaveLength(0);
    });

    it("should handle results with privacy-hidden fields", async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [
          {
            id: 3,
            username: "private_user",
            profile_id: 30,
          },
        ],
      };

      mock
        .onGet("http://localhost:8000/api/users/search/")
        .reply(200, mockResponse);

      const result = await searchUsers({ q: "private" });
      expect(result.results[0].username).toBe("private_user");
      expect(result.results[0].email).toBeUndefined();
      expect(result.results[0].full_name).toBeUndefined();
    });

    it("should handle 400 for short query", async () => {
      mock
        .onGet("http://localhost:8000/api/users/search/")
        .reply(400, { q: ["Search query must be at least 2 characters."] });

      await expect(searchUsers({ q: "a" })).rejects.toThrow();
    });

    it("should handle 500 server errors", async () => {
      mock
        .onGet("http://localhost:8000/api/users/search/")
        .reply(500, { detail: "Internal server error" });

      await expect(searchUsers({ q: "test" })).rejects.toThrow();
    });

    it("should handle network errors", async () => {
      mock
        .onGet("http://localhost:8000/api/users/search/")
        .networkError();

      await expect(searchUsers({ q: "test" })).rejects.toThrow();
    });
  });
});
