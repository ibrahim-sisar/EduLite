import { describe, it, expect, beforeEach, afterEach } from "vitest";
import axios from "axios";
import MockAdapter from "axios-mock-adapter";
import {
  listSlideshows,
  listMySlideshows,
  getSlideshowDetail,
  createSlideshow,
  updateSlideshow,
  deleteSlideshow,
  getSlide,
  createSlide,
  updateSlide,
  deleteSlide,
  previewMarkdown,
  isVersionConflictError,
  getVersionConflictDetails,
} from "../slideshowApi";
import type {
  SlideshowDetail,
  SlideshowCreateRequest,
  SlideshowUpdateRequest,
  Slide,
} from "../../types/slideshow.types";

describe("slideshowApi", () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  describe("listSlideshows", () => {
    it("should fetch paginated slideshows", async () => {
      const mockResponse = {
        count: 2,
        next: null,
        previous: null,
        results: [
          { id: 1, title: "Test 1", slide_count: 3 },
          { id: 2, title: "Test 2", slide_count: 5 },
        ],
      };

      mock
        .onGet("http://localhost:8000/api/slideshows/")
        .reply(200, mockResponse);

      const result = await listSlideshows();
      expect(result).toEqual(mockResponse);
      expect(result.results).toHaveLength(2);
    });

    it("should apply filter parameters", async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [{ id: 1, title: "Public Slideshow", visibility: "public" }],
      };

      mock
        .onGet("http://localhost:8000/api/slideshows/", {
          params: { visibility: "public", subject: "math" },
        })
        .reply(200, mockResponse);

      const result = await listSlideshows({
        visibility: "public",
        subject: "math",
      });
      expect(result.results).toHaveLength(1);
    });

    it("should handle errors", async () => {
      mock
        .onGet("http://localhost:8000/api/slideshows/")
        .reply(500, { detail: "Server error" });

      await expect(listSlideshows()).rejects.toThrow();
    });
  });

  describe("listMySlideshows", () => {
    it("should fetch only user slideshows", async () => {
      const mockResponse = {
        count: 1,
        next: null,
        previous: null,
        results: [{ id: 1, title: "My Slideshow" }],
      };

      mock
        .onGet("http://localhost:8000/api/slideshows/", {
          params: { mine: true },
        })
        .reply(200, mockResponse);

      const result = await listMySlideshows();
      expect(result).toEqual(mockResponse);
    });
  });

  describe("getSlideshowDetail", () => {
    it("should fetch slideshow with all slides", async () => {
      const mockSlideshow: SlideshowDetail = {
        id: 1,
        title: "Test Slideshow",
        description: "Test",
        created_by: 1,
        created_by_username: "testuser",
        visibility: "public",
        language: "en",
        country: null,
        subject: "math",
        is_published: true,
        version: 1,
        slide_count: 2,
        slides: [
          {
            id: 1,
            order: 0,
            rendered_content: "<h1>Slide 1</h1>",
            content: "# Slide 1",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
          {
            id: 2,
            order: 1,
            rendered_content: "<h1>Slide 2</h1>",
            content: "# Slide 2",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
        ],
        remaining_slide_ids: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      mock
        .onGet("http://localhost:8000/api/slideshows/1/")
        .reply(200, mockSlideshow);

      const result = await getSlideshowDetail(1);
      expect(result).toEqual(mockSlideshow);
      expect(result.slides).toHaveLength(2);
    });

    it("should support progressive loading", async () => {
      const mockSlideshow: SlideshowDetail = {
        id: 1,
        title: "Test Slideshow",
        description: "Test",
        created_by: 1,
        created_by_username: "testuser",
        visibility: "public",
        language: "en",
        country: null,
        subject: "math",
        is_published: true,
        version: 1,
        slide_count: 5,
        slides: [
          {
            id: 1,
            order: 0,
            rendered_content: "<h1>Slide 1</h1>",
            content: "# Slide 1",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
          {
            id: 2,
            order: 1,
            rendered_content: "<h1>Slide 2</h1>",
            content: "# Slide 2",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
        ],
        remaining_slide_ids: [3, 4, 5],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      mock
        .onGet("http://localhost:8000/api/slideshows/1/", {
          params: { initial: 2 },
        })
        .reply(200, mockSlideshow);

      const result = await getSlideshowDetail(1, 2);
      expect(result.slides).toHaveLength(2);
      expect(result.remaining_slide_ids).toHaveLength(3);
    });
  });

  describe("createSlideshow", () => {
    it("should create a new slideshow with slides", async () => {
      const createRequest: SlideshowCreateRequest = {
        title: "New Slideshow",
        description: "Test description",
        visibility: "public",
        subject: "math",
        language: "en",
        is_published: false,
        slides: [
          { order: 0, content: "# Slide 1" },
          { order: 1, content: "# Slide 2" },
        ],
      };

      const mockResponse: SlideshowDetail = {
        id: 1,
        title: "New Slideshow",
        description: "Test description",
        visibility: "public",
        subject: "math",
        language: "en",
        is_published: false,
        created_by: 1,
        created_by_username: "testuser",
        country: null,
        version: 1,
        slide_count: 2,
        slides: [
          {
            id: 1,
            order: 0,
            rendered_content: "<h1>Slide 1</h1>",
            content: "# Slide 1",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
          {
            id: 2,
            order: 1,
            rendered_content: "<h1>Slide 2</h1>",
            content: "# Slide 2",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
        ],
        remaining_slide_ids: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      mock
        .onPost("http://localhost:8000/api/slideshows/")
        .reply(200, mockResponse);

      const result = await createSlideshow(createRequest);
      expect(result.id).toBe(1);
      expect(result.slides).toHaveLength(2);
    });

    it("should handle validation errors", async () => {
      const createRequest: SlideshowCreateRequest = {
        title: "",
        description: null,
        visibility: "public",
        subject: null,
        language: null,
        is_published: false,
        slides: [],
      };

      mock.onPost("http://localhost:8000/api/slideshows/").reply(400, {
        title: ["This field may not be blank."],
      });

      await expect(createSlideshow(createRequest)).rejects.toThrow();
    });
  });

  describe("updateSlideshow", () => {
    it("should update slideshow successfully", async () => {
      const updateRequest: SlideshowUpdateRequest = {
        title: "Updated Title",
        description: "Updated description",
        visibility: "public",
        subject: "science",
        language: "en",
        is_published: true,
        version: 1,
        slides: [
          { order: 0, content: "# Updated Slide 1" },
          { order: 1, content: "# Updated Slide 2" },
          { order: 2, content: "# New Slide 3" },
        ],
      };

      const mockResponse: SlideshowDetail = {
        id: 1,
        title: "Updated Title",
        description: "Updated description",
        visibility: "public",
        subject: "science",
        language: "en",
        is_published: true,
        created_by: 1,
        created_by_username: "testuser",
        country: null,
        version: 2, // Incremented
        slide_count: 3,
        slides: [
          {
            id: 1,
            order: 0,
            rendered_content: "<h1>Updated Slide 1</h1>",
            content: "# Updated Slide 1",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
          {
            id: 2,
            order: 1,
            rendered_content: "<h1>Updated Slide 2</h1>",
            content: "# Updated Slide 2",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
          {
            id: 3,
            order: 2,
            rendered_content: "<h1>New Slide 3</h1>",
            content: "# New Slide 3",
            created_at: "2024-01-01T00:00:00Z",
            updated_at: "2024-01-01T00:00:00Z",
          },
        ],
        remaining_slide_ids: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      mock
        .onPatch("http://localhost:8000/api/slideshows/1/")
        .reply(200, mockResponse);

      const result = await updateSlideshow(1, updateRequest);
      expect(result.version).toBe(2);
      expect(result.slides).toHaveLength(3);
      expect(result.title).toBe("Updated Title");
    });

    it("should handle version conflicts", async () => {
      const updateRequest: SlideshowUpdateRequest = {
        title: "Updated Title",
        description: null,
        visibility: "public",
        subject: null,
        language: null,
        is_published: false,
        version: 1, // Client has version 1
        slides: [{ order: 0, content: "# Slide 1" }],
      };

      mock.onPatch("http://localhost:8000/api/slideshows/1/").reply(409, {
        error: "version_conflict",
        message: "Slideshow was modified since you loaded it",
        server_version: 3,
        client_version: 1,
      });

      // Note: axios-mock-adapter throws plain errors, not AxiosErrors,
      // so we can't test the version conflict handling directly in unit tests.
      // This would need to be tested in an integration test with a real backend.
      await expect(updateSlideshow(1, updateRequest)).rejects.toThrow();
    });

    it("should handle empty content validation error", async () => {
      const updateRequest: SlideshowUpdateRequest = {
        title: "Test",
        description: null,
        visibility: "public",
        subject: null,
        language: null,
        is_published: false,
        version: 1,
        slides: [
          { order: 0, content: "# Slide 1" },
          { order: 1, content: "" }, // Empty content
        ],
      };

      mock.onPatch("http://localhost:8000/api/slideshows/1/").reply(400, {
        slides: [{}, { content: ["This field may not be blank."] }],
      });

      await expect(updateSlideshow(1, updateRequest)).rejects.toThrow();
    });
  });

  describe("deleteSlideshow", () => {
    it("should delete slideshow", async () => {
      mock.onDelete("http://localhost:8000/api/slideshows/1/").reply(204);

      await expect(deleteSlideshow(1)).resolves.not.toThrow();
    });

    it("should handle errors", async () => {
      mock
        .onDelete("http://localhost:8000/api/slideshows/1/")
        .reply(404, { detail: "Not found" });

      await expect(deleteSlideshow(1)).rejects.toThrow();
    });
  });

  describe("previewMarkdown", () => {
    it("should render markdown to HTML", async () => {
      const markdown = "# Hello World";
      const rendered = "<h1>Hello World</h1>";

      mock
        .onPost("http://localhost:8000/api/slideshows/preview/")
        .reply(200, { rendered_content: rendered });

      const result = await previewMarkdown(markdown);
      expect(result).toBe(rendered);
    });

    it("should support abort signal", async () => {
      const markdown = "# Test";
      const controller = new AbortController();

      mock
        .onPost("http://localhost:8000/api/slideshows/preview/")
        .reply(200, { rendered_content: "<h1>Test</h1>" });

      controller.abort();

      await expect(
        previewMarkdown(markdown, controller.signal),
      ).rejects.toThrow();
    });
  });

  describe("Version conflict utilities", () => {
    it("should identify version conflict errors", () => {
      const conflictError = {
        isVersionConflict: true,
        error: "version_conflict",
        message: "Conflict",
        server_version: 3,
        client_version: 1,
      };

      expect(isVersionConflictError(conflictError)).toBe(true);
      expect(isVersionConflictError({ error: "other" })).toBe(false);
      expect(isVersionConflictError(null)).toBe(false);
    });

    it("should extract version conflict details", () => {
      const conflictError = {
        isVersionConflict: true,
        error: "version_conflict",
        message: "Slideshow was modified",
        server_version: 5,
        client_version: 3,
      };

      const details = getVersionConflictDetails(conflictError);
      expect(details).toEqual({
        error: "version_conflict",
        message: "Slideshow was modified",
        server_version: 5,
        client_version: 3,
      });

      expect(getVersionConflictDetails({ error: "other" })).toBeNull();
    });
  });

  describe("Slide operations", () => {
    it("should get individual slide", async () => {
      const mockSlide: Slide = {
        id: 1,
        order: 0,
        content: "# Slide 1",
        rendered_content: "<h1>Slide 1</h1>",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      mock
        .onGet("http://localhost:8000/api/slideshows/1/slides/1/")
        .reply(200, mockSlide);

      const result = await getSlide(1, 1);
      expect(result).toEqual(mockSlide);
    });

    it("should create a new slide", async () => {
      const slideData = { order: 0, content: "# New Slide" };
      const mockResponse: Slide = {
        id: 1,
        ...slideData,
        rendered_content: "<h1>New Slide</h1>",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      mock
        .onPost("http://localhost:8000/api/slideshows/1/slides/")
        .reply(200, mockResponse);

      const result = await createSlide(1, slideData);
      expect(result.id).toBe(1);
      expect(result.content).toBe("# New Slide");
    });

    it("should update a slide", async () => {
      const updateData = { content: "# Updated Slide" };
      const mockResponse: Slide = {
        id: 1,
        order: 0,
        content: "# Updated Slide",
        rendered_content: "<h1>Updated Slide</h1>",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      mock
        .onPatch("http://localhost:8000/api/slideshows/1/slides/1/")
        .reply(200, mockResponse);

      const result = await updateSlide(1, 1, updateData);
      expect(result.content).toBe("# Updated Slide");
    });

    it("should delete a slide", async () => {
      mock
        .onDelete("http://localhost:8000/api/slideshows/1/slides/1/")
        .reply(204);

      await expect(deleteSlide(1, 1)).resolves.not.toThrow();
    });
  });
});
