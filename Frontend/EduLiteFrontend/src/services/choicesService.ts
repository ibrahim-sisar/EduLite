// Lightweight choices service with smart caching for weak internet areas
// Only loads choices when needed, caches in memory + localStorage for offline access

export interface Choice {
  value: string;
  label: string;
}

export type ChoiceType = 'occupations' | 'countries' | 'languages';

class ChoicesService {
  private memoryCache = new Map<ChoiceType, Choice[]>();
  private readonly CACHE_PREFIX = 'edulite_choices_';
  private readonly CACHE_VERSION = '1.0'; // Increment to invalidate old cache

  /**
   * Get choices for a specific type with intelligent caching
   * 1. Check memory cache (instant)
   * 2. Check localStorage (still instant)
   * 3. Fetch from static file (only once per choice type)
   */
  async getChoices(type: ChoiceType): Promise<Choice[]> {
    try {
      // 1. Check memory cache first (fastest)
      if (this.memoryCache.has(type)) {
        return this.memoryCache.get(type)!;
      }

      // 2. Check localStorage cache (still instant)
      const cacheKey = `${this.CACHE_PREFIX}${type}_v${this.CACHE_VERSION}`;
      const cachedData = localStorage.getItem(cacheKey);

      if (cachedData) {
        try {
          const parsed = JSON.parse(cachedData);
          this.memoryCache.set(type, parsed);
          return parsed;
        } catch (error) {
          console.warn(`Failed to parse cached ${type} choices:`, error);
          localStorage.removeItem(cacheKey);
        }
      }

      // 3. Fetch from static file (network request)
      const response = await fetch(`/project_choices_data/${type}.json`, {
        cache: 'force-cache', // Use browser cache for better performance
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch ${type} choices: ${response.status}`);
      }

      const data: Choice[] = await response.json();

      // Validate data structure
      if (!Array.isArray(data) || data.some(item => !item.value || !item.label)) {
        throw new Error(`Invalid ${type} choices data structure`);
      }

      // Cache for future use
      this.memoryCache.set(type, data);
      localStorage.setItem(cacheKey, JSON.stringify(data));

      return data;

    } catch (error) {
      console.error(`Error loading ${type} choices:`, error);

      // Return empty array as fallback - component can handle gracefully
      return [];
    }
  }

  /**
   * Convenience methods for specific choice types
   */
  async getOccupationChoices(): Promise<Choice[]> {
    return this.getChoices('occupations');
  }

  async getCountryChoices(): Promise<Choice[]> {
    return this.getChoices('countries');
  }

  async getLanguageChoices(): Promise<Choice[]> {
    return this.getChoices('languages');
  }

  /**
   * Clear cache for a specific choice type (useful for development)
   */
  clearCache(type?: ChoiceType): void {
    if (type) {
      this.memoryCache.delete(type);
      const cacheKey = `${this.CACHE_PREFIX}${type}_v${this.CACHE_VERSION}`;
      localStorage.removeItem(cacheKey);
    } else {
      // Clear all caches
      this.memoryCache.clear();
      Object.keys(localStorage)
        .filter(key => key.startsWith(this.CACHE_PREFIX))
        .forEach(key => localStorage.removeItem(key));
    }
  }

  /**
   * Preload all choice types (useful for good connections)
   * This is optional - the service works fine with lazy loading
   */
  async preloadAllChoices(): Promise<void> {
    try {
      await Promise.all([
        this.getChoices('occupations'),
        this.getChoices('countries'),
        this.getChoices('languages')
      ]);
    } catch (error) {
      console.warn('Failed to preload some choices:', error);
      // Non-critical error - choices will load on demand
    }
  }

  /**
   * Check if choices are available offline (in cache)
   */
  hasOfflineChoices(type: ChoiceType): boolean {
    if (this.memoryCache.has(type)) return true;

    const cacheKey = `${this.CACHE_PREFIX}${type}_v${this.CACHE_VERSION}`;
    return localStorage.getItem(cacheKey) !== null;
  }
}

// Export singleton instance
export const choicesService = new ChoicesService();

// Export for easier importing
export default choicesService;
