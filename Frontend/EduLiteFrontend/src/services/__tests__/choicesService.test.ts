import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { choicesService, Choice } from '../choicesService';

// Mock data
const mockOccupations: Choice[] = [
  { value: 'engineer', label: 'Engineer' },
  { value: 'teacher', label: 'Teacher' },
  { value: 'doctor', label: 'Doctor' },
];

const mockCountries: Choice[] = [
  { value: 'us', label: 'United States' },
  { value: 'uk', label: 'United Kingdom' },
  { value: 'ca', label: 'Canada' },
];

const mockLanguages: Choice[] = [
  { value: 'en', label: 'English' },
  { value: 'ar', label: 'Arabic' },
  { value: 'es', label: 'Spanish' },
];

const mockSubjects: Choice[] = [
  { value: 'math', label: 'Mathematics' },
  { value: 'cs', label: 'Computer Science' },
  { value: 'physics', label: 'Physics' },
];

// Mock fetch globally
global.fetch = vi.fn();

describe('choicesService - Caching Strategy', () => {
  beforeEach(() => {
    localStorage.clear();
    choicesService.clearCache();
    vi.clearAllMocks();
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Memory Cache', () => {
    it('returns data from memory cache on subsequent calls', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockOccupations),
      } as unknown as Response);

      // First call - fetches from network
      const result1 = await choicesService.getChoices('occupations');
      expect(result1).toEqual(mockOccupations);
      expect(fetch).toHaveBeenCalledTimes(1);

      // Second call - should use memory cache (no additional fetch)
      const result2 = await choicesService.getChoices('occupations');
      expect(result2).toEqual(mockOccupations);
      expect(fetch).toHaveBeenCalledTimes(1); // Still just 1 call
    });

    it('memory cache persists across different choice types', async () => {
      vi.mocked(fetch)
        .mockResolvedValueOnce({
          ok: true,
          headers: { get: () => 'application/json' },
          text: async () => JSON.stringify(mockOccupations),
        } as unknown as Response)
        .mockResolvedValueOnce({
          ok: true,
          headers: { get: () => 'application/json' },
          text: async () => JSON.stringify(mockCountries),
        } as unknown as Response);

      await choicesService.getChoices('occupations');
      await choicesService.getChoices('countries');

      // Both should be cached in memory
      expect(fetch).toHaveBeenCalledTimes(2);

      // Retrieve again - should use memory cache
      await choicesService.getChoices('occupations');
      await choicesService.getChoices('countries');
      expect(fetch).toHaveBeenCalledTimes(2); // No additional fetches
    });
  });

  describe('localStorage Cache', () => {
    it('returns data from localStorage when memory cache is cold', async () => {
      // Pre-populate localStorage
      localStorage.setItem(
        'edulite_choices_occupations_v1.0',
        JSON.stringify(mockOccupations)
      );

      // Should load from localStorage without fetching
      const result = await choicesService.getChoices('occupations');
      expect(result).toEqual(mockOccupations);
      expect(fetch).not.toHaveBeenCalled();
    });

    it('stores fetched data in localStorage for future use', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockCountries),
      } as unknown as Response);

      await choicesService.getChoices('countries');

      // Check localStorage was updated
      const cached = localStorage.getItem('edulite_choices_countries_v1.0');
      expect(cached).toBe(JSON.stringify(mockCountries));
    });

    it('handles corrupted localStorage data gracefully', async () => {
      // Store invalid JSON
      localStorage.setItem('edulite_choices_languages_v1.0', 'invalid-json{{{');

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockLanguages),
      } as unknown as Response);

      // Should remove corrupted cache and fetch fresh
      const result = await choicesService.getChoices('languages');
      expect(result).toEqual(mockLanguages);
      expect(console.warn).toHaveBeenCalledWith(
        expect.stringContaining('Failed to parse cached'),
        expect.anything()
      );
      expect(localStorage.getItem('edulite_choices_languages_v1.0')).toBe(
        JSON.stringify(mockLanguages)
      );
    });
  });

  describe('Network Fetch', () => {
    it('fetches from network when no cache exists', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockOccupations),
      } as unknown as Response);

      const result = await choicesService.getChoices('occupations');

      expect(fetch).toHaveBeenCalledWith(
        '/project_choices_data/occupations.json',
        { cache: 'force-cache' }
      );
      expect(result).toEqual(mockOccupations);
    });

    it('uses force-cache for browser caching', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockCountries),
      } as unknown as Response);

      await choicesService.getChoices('countries');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('countries.json'),
        expect.objectContaining({ cache: 'force-cache' })
      );
    });
  });
});

describe('choicesService - Fetch & Retry Logic', () => {
  beforeEach(() => {
    localStorage.clear();
    choicesService.clearCache();
    vi.clearAllMocks();
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('successfully fetches JSON on first attempt', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify(mockOccupations),
    } as unknown as Response);

    const result = await choicesService.getChoices('occupations');

    expect(result).toEqual(mockOccupations);
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('retries when receiving HTML instead of JSON', async () => {
    // First attempt: HTML response
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'text/html' },
        text: async () => '<html>404 page</html>',
      } as unknown as Response)
      // Second attempt: JSON response
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockCountries),
      } as unknown as Response);

    const result = await choicesService.getChoices('countries');

    expect(result).toEqual(mockCountries);
    expect(fetch).toHaveBeenCalledTimes(2);
    expect(console.warn).toHaveBeenCalledWith(
      expect.stringContaining('[Attempt 1/3] Got HTML instead of JSON')
    );
  });

  it('exhausts retries and returns empty array after 3 HTML responses', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      headers: { get: () => 'text/html' },
      text: async () => '<html>404</html>',
    } as unknown as Response);

    const result = await choicesService.getChoices('languages');

    expect(result).toEqual([]);
    expect(fetch).toHaveBeenCalledTimes(3); // Max retries
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('Final attempt'),
      expect.anything()
    );
  });

  it('handles non-OK HTTP status', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      headers: { get: () => 'application/json' },
      text: async () => 'Not found',
    } as unknown as Response);

    const result = await choicesService.getChoices('occupations');

    expect(result).toEqual([]);
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('Failed to fetch'),
      expect.anything()
    );
  });

  it('handles network errors gracefully', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

    const result = await choicesService.getChoices('countries');

    expect(result).toEqual([]);
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('Error loading'),
      expect.any(Error)
    );
  });

  it('waits 150ms between retries', async () => {
    vi.useFakeTimers();

    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'text/html' },
        text: async () => '<html>404</html>',
      } as unknown as Response)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockLanguages),
      } as unknown as Response);

    const promise = choicesService.getChoices('languages');

    // Fast-forward time
    await vi.advanceTimersByTimeAsync(150);

    const result = await promise;

    expect(result).toEqual(mockLanguages);
    expect(fetch).toHaveBeenCalledTimes(2);

    vi.useRealTimers();
  });
});

describe('choicesService - Data Validation', () => {
  beforeEach(() => {
    localStorage.clear();
    choicesService.clearCache();
    vi.clearAllMocks();
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('validates data structure has value and label fields', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify([
        { value: 'test1', label: 'Test 1' },
        { value: 'test2', label: 'Test 2' },
      ]),
    } as unknown as Response);

    const result = await choicesService.getChoices('occupations');

    expect(result).toHaveLength(2);
    expect(result[0]).toHaveProperty('value');
    expect(result[0]).toHaveProperty('label');
  });

  it('rejects invalid data structure (missing value)', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify([
        { label: 'Test 1' }, // Missing value
        { value: 'test2', label: 'Test 2' },
      ]),
    } as unknown as Response);

    const result = await choicesService.getChoices('countries');

    expect(result).toEqual([]);
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('Error loading'),
      expect.anything()
    );
  });

  it('rejects invalid data structure (missing label)', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify([
        { value: 'test1' }, // Missing label
        { value: 'test2', label: 'Test 2' },
      ]),
    } as unknown as Response);

    const result = await choicesService.getChoices('languages');

    expect(result).toEqual([]);
  });

  it('rejects non-array data', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify({ error: 'Not an array' }),
    } as unknown as Response);

    const result = await choicesService.getChoices('occupations');

    expect(result).toEqual([]);
  });

  it('handles malformed JSON', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => '{invalid json{{',
    } as unknown as Response);

    const result = await choicesService.getChoices('countries');

    expect(result).toEqual([]);
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('JSON parsing failed'),
      expect.anything()
    );
  });

  it('warns about suspiciously short responses', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => '[]',
    } as unknown as Response);

    const result = await choicesService.getChoices('languages');

    expect(result).toEqual([]);
    expect(console.warn).toHaveBeenCalledWith(
      expect.stringContaining('Suspiciously short response'),
      '[]'
    );
  });
});

describe('choicesService - Convenience Methods', () => {
  beforeEach(() => {
    localStorage.clear();
    choicesService.clearCache();
    vi.clearAllMocks();
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('getOccupationChoices() fetches occupations', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify(mockOccupations),
    } as unknown as Response);

    const result = await choicesService.getOccupationChoices();

    expect(result).toEqual(mockOccupations);
    expect(fetch).toHaveBeenCalledWith(
      '/project_choices_data/occupations.json',
      expect.anything()
    );
  });

  it('getCountryChoices() fetches countries', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify(mockCountries),
    } as unknown as Response);

    const result = await choicesService.getCountryChoices();

    expect(result).toEqual(mockCountries);
    expect(fetch).toHaveBeenCalledWith(
      '/project_choices_data/countries.json',
      expect.anything()
    );
  });

  it('getLanguageChoices() fetches languages', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify(mockLanguages),
    } as unknown as Response);

    const result = await choicesService.getLanguageChoices();

    expect(result).toEqual(mockLanguages);
    expect(fetch).toHaveBeenCalledWith(
      '/project_choices_data/languages.json',
      expect.anything()
    );
  });
});

describe('choicesService - Cache Management', () => {
  beforeEach(() => {
    localStorage.clear();
    choicesService.clearCache();
    vi.clearAllMocks();
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('clearCache(type) clears specific choice type', async () => {
    // Populate caches
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockOccupations),
      } as unknown as Response)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockCountries),
      } as unknown as Response);

    await choicesService.getChoices('occupations');
    await choicesService.getChoices('countries');

    expect(fetch).toHaveBeenCalledTimes(2);

    // Clear only occupations
    choicesService.clearCache('occupations');

    // Mock new fetch for occupations
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify(mockOccupations),
    } as unknown as Response);

    // Occupations should fetch again, countries should use cache
    await choicesService.getChoices('occupations');
    await choicesService.getChoices('countries');

    expect(fetch).toHaveBeenCalledTimes(3); // Only 1 new fetch for occupations
  });

  it('clearCache() with no argument clears all caches', async () => {
    // Populate multiple caches
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockOccupations),
      } as unknown as Response)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockCountries),
      } as unknown as Response)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockLanguages),
      } as unknown as Response);

    await choicesService.getChoices('occupations');
    await choicesService.getChoices('countries');
    await choicesService.getChoices('languages');

    expect(fetch).toHaveBeenCalledTimes(3);

    // Clear all caches
    choicesService.clearCache();

    // Mock fresh fetches
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockOccupations),
      } as unknown as Response)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockCountries),
      } as unknown as Response);

    // All should fetch again
    await choicesService.getChoices('occupations');
    await choicesService.getChoices('countries');

    expect(fetch).toHaveBeenCalledTimes(5); // 3 initial + 2 new
  });

  it('clearCache removes from both memory and localStorage', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify(mockOccupations),
    } as unknown as Response);

    await choicesService.getChoices('occupations');

    // Verify both caches exist
    expect(localStorage.getItem('edulite_choices_occupations_v1.0')).toBeTruthy();

    choicesService.clearCache('occupations');

    // Verify both caches cleared
    expect(localStorage.getItem('edulite_choices_occupations_v1.0')).toBeNull();
  });
});

describe('choicesService - Offline Support', () => {
  beforeEach(() => {
    localStorage.clear();
    choicesService.clearCache();
    vi.clearAllMocks();
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('hasOfflineChoices() returns true when data is cached', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify(mockOccupations),
    } as unknown as Response);

    await choicesService.getChoices('occupations');

    expect(choicesService.hasOfflineChoices('occupations')).toBe(true);
  });

  it('hasOfflineChoices() returns false when no cache exists', () => {
    expect(choicesService.hasOfflineChoices('countries')).toBe(false);
  });

  it('hasOfflineChoices() checks localStorage when memory cache empty', () => {
    // Pre-populate localStorage
    localStorage.setItem(
      'edulite_choices_languages_v1.0',
      JSON.stringify(mockLanguages)
    );

    // Memory cache is cold, but localStorage has data
    expect(choicesService.hasOfflineChoices('languages')).toBe(true);
  });

  it('preloadAllChoices() loads all four choice types', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockOccupations),
      } as unknown as Response)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockCountries),
      } as unknown as Response)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockLanguages),
      } as unknown as Response)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockSubjects),
      } as unknown as Response);

    await choicesService.preloadAllChoices();

    expect(fetch).toHaveBeenCalledTimes(4); // Now includes subjects
    expect(choicesService.hasOfflineChoices('occupations')).toBe(true);
    expect(choicesService.hasOfflineChoices('countries')).toBe(true);
    expect(choicesService.hasOfflineChoices('languages')).toBe(true);
    expect(choicesService.hasOfflineChoices('subjects')).toBe(true);
  });

  it('preloadAllChoices() continues despite partial failures', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockOccupations),
      } as unknown as Response)
      .mockRejectedValueOnce(new Error('Network error')) // Countries fail
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockLanguages),
      } as unknown as Response)
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(mockSubjects),
      } as unknown as Response);

    await choicesService.preloadAllChoices();

    // Should have attempted all 4 (occupations, countries, languages, subjects)
    expect(fetch).toHaveBeenCalledTimes(4);

    // Success caches should exist, failed one should not
    expect(choicesService.hasOfflineChoices('occupations')).toBe(true);
    expect(choicesService.hasOfflineChoices('countries')).toBe(false);
    expect(choicesService.hasOfflineChoices('languages')).toBe(true);

    // Note: Individual getChoices() calls catch their own errors and return []
    // so Promise.all doesn't actually reject, and outer try-catch doesn't fire
    // The failed request was logged by getChoices()'s internal error handler
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('Error loading countries'),
      expect.any(Error)
    );
  });
});

describe('choicesService - Edge Cases', () => {
  beforeEach(() => {
    localStorage.clear();
    choicesService.clearCache();
    vi.clearAllMocks();
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('handles concurrent requests for same choice type', async () => {
    // Current implementation doesn't deduplicate concurrent requests
    // Each racing request tries to fetch independently
    // First one to complete populates the cache
    // Others may fail to fetch (race lost) and return empty array

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify(mockOccupations),
    } as unknown as Response);

    // Make 3 concurrent requests
    const promises = [
      choicesService.getChoices('occupations'),
      choicesService.getChoices('occupations'),
      choicesService.getChoices('occupations'),
    ];

    const results = await Promise.all(promises);

    // At least one should succeed and get cached data
    const successfulResults = results.filter(r => r.length > 0);
    expect(successfulResults.length).toBeGreaterThan(0);
    expect(successfulResults[0]).toEqual(mockOccupations);

    // After concurrent requests, cache should exist
    expect(choicesService.hasOfflineChoices('occupations')).toBe(true);
  });

  it('handles empty array response as valid data', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      text: async () => JSON.stringify([]),
    } as unknown as Response);

    const result = await choicesService.getChoices('countries');

    // Empty array is technically valid, but triggers warning
    expect(result).toEqual([]);
    expect(console.warn).toHaveBeenCalledWith(
      expect.stringContaining('Suspiciously short'),
      expect.anything()
    );
  });

  it('respects cache versioning', () => {
    // Old version cache
    localStorage.setItem(
      'edulite_choices_occupations_v0.9',
      JSON.stringify(mockOccupations)
    );

    // Should not use old version
    expect(choicesService.hasOfflineChoices('occupations')).toBe(false);
  });
});
