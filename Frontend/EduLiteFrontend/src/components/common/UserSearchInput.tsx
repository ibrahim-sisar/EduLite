import { useState, useEffect, useRef, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { HiMagnifyingGlass, HiXMark } from "react-icons/hi2";
import { useDebounce } from "../../hooks/useDebounce";
import { searchUsers } from "../../services/usersApi";
import type { UserSearchResult } from "../../types/users.types";

interface UserSearchInputProps {
  onSelect: (user: UserSearchResult) => void;
  selectedUser: UserSearchResult | null;
  onClear: () => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  label?: string;
}

const UserSearchInput: React.FC<UserSearchInputProps> = ({
  onSelect,
  selectedUser,
  onClear,
  placeholder,
  disabled = false,
  error,
  label,
}) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 300);
  const [results, setResults] = useState<UserSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState(-1);

  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  // Fetch results when debounced query changes
  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setResults([]);
      setIsOpen(false);
      setSearchError(null);
      return;
    }

    let cancelled = false;

    const fetchResults = async () => {
      setIsLoading(true);
      setSearchError(null);
      try {
        const data = await searchUsers({ q: debouncedQuery, page_size: 8 });
        if (!cancelled) {
          setResults(data.results);
          setIsOpen(true);
          setActiveIndex(-1);
        }
      } catch (err) {
        if (!cancelled) {
          setSearchError(
            err instanceof Error
              ? err.message
              : t("course.detail.inviteModal.searchError"),
          );
          setResults([]);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchResults();
    return () => {
      cancelled = true;
    };
  }, [debouncedQuery, t]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
        setActiveIndex(-1);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Scroll active item into view
  useEffect(() => {
    if (activeIndex >= 0 && listRef.current) {
      const activeItem = listRef.current.children[activeIndex] as HTMLElement;
      activeItem?.scrollIntoView?.({ block: "nearest" });
    }
  }, [activeIndex]);

  const handleSelect = useCallback(
    (user: UserSearchResult) => {
      onSelect(user);
      setQuery("");
      setResults([]);
      setIsOpen(false);
      setActiveIndex(-1);
    },
    [onSelect],
  );

  const handleClear = useCallback(() => {
    onClear();
    setQuery("");
    setResults([]);
    setSearchError(null);
    // Focus input after clearing
    setTimeout(() => inputRef.current?.focus(), 0);
  }, [onClear]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || results.length === 0) {
      if (e.key === "Escape") {
        e.stopPropagation();
        (e.target as HTMLInputElement).blur();
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActiveIndex((prev) => (prev >= results.length - 1 ? 0 : prev + 1));
        break;
      case "ArrowUp":
        e.preventDefault();
        setActiveIndex((prev) => (prev <= 0 ? results.length - 1 : prev - 1));
        break;
      case "Enter":
        e.preventDefault();
        if (activeIndex >= 0 && activeIndex < results.length) {
          handleSelect(results[activeIndex]);
        }
        break;
      case "Escape":
        e.preventDefault();
        e.stopPropagation();
        setIsOpen(false);
        setActiveIndex(-1);
        break;
      case "Tab":
        setIsOpen(false);
        setActiveIndex(-1);
        break;
    }
  };

  const resolvedLabel = label || t("course.detail.inviteModal.searchLabel");
  const resolvedPlaceholder =
    placeholder || t("course.detail.inviteModal.searchPlaceholder");

  return (
    <div className="space-y-1">
      {resolvedLabel && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {resolvedLabel}
        </label>
      )}

      <div ref={wrapperRef} className="relative">
        {selectedUser ? (
          // Selected user pill
          <div className="flex items-center gap-2 px-3 py-2.5 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700/50 rounded-xl">
            <div className="flex-1 min-w-0">
              <span className="text-sm font-medium text-blue-800 dark:text-blue-200 truncate block">
                {selectedUser.username}
              </span>
              {selectedUser.full_name && (
                <span className="text-xs text-blue-600 dark:text-blue-300/70 truncate block">
                  {selectedUser.full_name}
                </span>
              )}
            </div>
            <button
              type="button"
              onClick={handleClear}
              disabled={disabled}
              className="p-1 text-blue-400 hover:text-blue-600 dark:text-blue-300 dark:hover:text-blue-100 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800/50 transition-colors disabled:opacity-50 cursor-pointer"
              aria-label={t("course.detail.inviteModal.clearSelection")}
            >
              <HiXMark className="w-4 h-4" />
            </button>
          </div>
        ) : (
          // Search input
          <>
            <div className="relative">
              <HiMagnifyingGlass className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              <input
                ref={inputRef}
                type="search"
                role="combobox"
                aria-expanded={isOpen}
                aria-controls="user-search-listbox"
                aria-activedescendant={
                  activeIndex >= 0
                    ? `user-search-option-${results[activeIndex]?.id}`
                    : undefined
                }
                aria-autocomplete="list"
                aria-label={resolvedLabel}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => {
                  if (results.length > 0 && query.length >= 2) {
                    setIsOpen(true);
                  }
                }}
                placeholder={resolvedPlaceholder}
                disabled={disabled}
                className="w-full ps-9 pe-9 py-2.5 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm text-gray-700 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed"
              />
              {isLoading && (
                <div className="absolute end-3 top-1/2 -translate-y-1/2">
                  <div
                    className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"
                    role="status"
                    aria-label="Loading"
                  />
                </div>
              )}
            </div>

            {/* Dropdown */}
            {isOpen && results.length > 0 && (
              <ul
                id="user-search-listbox"
                ref={listRef}
                role="listbox"
                aria-label={t("course.detail.inviteModal.searchResults")}
                className="absolute z-10 mt-1 w-full max-h-60 overflow-y-auto bg-white dark:bg-gray-800 border border-gray-200/50 dark:border-gray-700/30 rounded-xl shadow-lg"
              >
                {results.map((user, index) => (
                  <li
                    key={user.id}
                    id={`user-search-option-${user.id}`}
                    role="option"
                    aria-selected={index === activeIndex}
                    onClick={() => handleSelect(user)}
                    onMouseEnter={() => setActiveIndex(index)}
                    className={`px-4 py-3 cursor-pointer transition-colors ${
                      index === activeIndex
                        ? "bg-blue-50 dark:bg-blue-900/20"
                        : "hover:bg-gray-50 dark:hover:bg-gray-700/50"
                    }`}
                  >
                    <span className="text-sm font-medium text-gray-900 dark:text-white truncate block">
                      {user.username}
                    </span>
                    {user.full_name && (
                      <span className="text-xs text-gray-500 dark:text-gray-400 truncate block">
                        {user.full_name}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            )}

            {/* No results */}
            {isOpen &&
              !isLoading &&
              debouncedQuery.length >= 2 &&
              results.length === 0 &&
              !searchError && (
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {t("course.detail.inviteModal.noResults")}
                </p>
              )}

            {/* Min chars hint */}
            {query.length > 0 && query.length < 2 && !isLoading && (
              <p className="mt-1 text-sm text-gray-400 dark:text-gray-500">
                {t("course.detail.inviteModal.searchMinChars")}
              </p>
            )}
          </>
        )}

        {/* Error messages */}
        {(searchError || error) && (
          <p className="mt-1 text-sm text-red-500">{searchError || error}</p>
        )}
      </div>
    </div>
  );
};

export default UserSearchInput;
