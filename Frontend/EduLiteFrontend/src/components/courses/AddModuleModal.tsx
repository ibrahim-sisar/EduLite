import { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import {
  HiArrowLeft,
  HiMagnifyingGlass,
  HiPresentationChartBar,
  HiDocumentText,
  HiClipboardDocumentList,
  HiAcademicCap,
  HiCheck,
} from "react-icons/hi2";
import { useDebounce } from "../../hooks/useDebounce";
import {
  searchSlideshows,
  listMySlideshows,
} from "../../services/slideshowApi";
import type { SlideshowListItem } from "../../types/slideshow.types";
import type { CourseModule } from "../../types/courses.types";

interface AddModuleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title?: string;
    content_type: string;
    object_id: number;
    order?: number;
  }) => Promise<void>;
  editModule?: CourseModule | null;
  existingModules?: CourseModule[];
}

type Step = "type" | "search" | "confirm";

const MODULE_TYPES = [
  {
    key: "slideshow",
    contentType: "slideshows.slideshow",
    icon: HiPresentationChartBar,
    enabled: true,
  },
  {
    key: "quiz",
    contentType: "",
    icon: HiClipboardDocumentList,
    enabled: false,
  },
  {
    key: "notes",
    contentType: "",
    icon: HiDocumentText,
    enabled: false,
  },
  {
    key: "assignment",
    contentType: "",
    icon: HiAcademicCap,
    enabled: false,
  },
] as const;

const AddModuleModal: React.FC<AddModuleModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  editModule,
  existingModules = [],
}) => {
  const { t } = useTranslation();
  const isEditMode = !!editModule;

  // Step management
  const [step, setStep] = useState<Step>("type");
  const [selectedType, setSelectedType] = useState<string>("");

  // Search state
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 300);
  const [mineOnly, setMineOnly] = useState(true);
  const [results, setResults] = useState<SlideshowListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Selection state
  const [selectedItem, setSelectedItem] = useState<SlideshowListItem | null>(
    null,
  );
  const [moduleTitle, setModuleTitle] = useState("");

  // Submit state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);

  // Build a set of already-used object IDs for the current content type
  const existingObjectIds = new Set(
    existingModules
      .filter(
        (m) => m.content_type === (selectedType || "slideshows.slideshow"),
      )
      .map((m) => m.object_id),
  );

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      if (isEditMode) {
        // Edit mode: skip to search with type pre-set
        setSelectedType(editModule.content_type);
        setStep("search");
        setModuleTitle(editModule.title || "");
      } else {
        setStep("type");
        setSelectedType("");
        setModuleTitle("");
      }
      setQuery("");
      setResults([]);
      setSelectedItem(null);
      setIsSubmitting(false);
      setSubmitError(null);
      setSearchError(null);
      setMineOnly(true);
    }
  }, [isOpen, isEditMode, editModule]);

  // Fetch results when debounced query or mineOnly changes
  useEffect(() => {
    if (!isOpen || step !== "search") return;

    // If no query and "My Slideshows" mode, list all user's slideshows
    if (debouncedQuery.length === 0 && mineOnly) {
      let cancelled = false;
      const fetchMine = async () => {
        setIsLoading(true);
        setSearchError(null);
        try {
          const data = await listMySlideshows({ page_size: 20 });
          if (!cancelled) {
            setResults(data.results);
          }
        } catch (err) {
          if (!cancelled) {
            setSearchError(
              err instanceof Error ? err.message : "Failed to load slideshows",
            );
            setResults([]);
          }
        } finally {
          if (!cancelled) setIsLoading(false);
        }
      };
      fetchMine();
      return () => {
        cancelled = true;
      };
    }

    // If no query and "All Slideshows" mode, clear results
    if (debouncedQuery.length === 0 && !mineOnly) {
      setResults([]);
      return;
    }

    // If query too short, clear
    if (debouncedQuery.length < 2) {
      setResults([]);
      return;
    }

    // Search with query
    let cancelled = false;
    const fetchResults = async () => {
      setIsLoading(true);
      setSearchError(null);
      try {
        const params: { q: string; mine?: boolean; page_size: number } = {
          q: debouncedQuery,
          page_size: 20,
        };
        if (mineOnly) params.mine = true;
        const data = await searchSlideshows(params);
        if (!cancelled) {
          setResults(data.results);
        }
      } catch (err) {
        if (!cancelled) {
          setSearchError(
            err instanceof Error ? err.message : "Failed to search slideshows",
          );
          setResults([]);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };
    fetchResults();
    return () => {
      cancelled = true;
    };
  }, [debouncedQuery, mineOnly, isOpen, step]);

  // Focus search input when entering search step
  useEffect(() => {
    if (step === "search") {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [step]);

  const handleTypeSelect = (contentType: string) => {
    setSelectedType(contentType);
    setStep("search");
  };

  const handleItemSelect = (item: SlideshowListItem) => {
    setSelectedItem(item);
    if (!moduleTitle) {
      setModuleTitle(item.title);
    }
    setStep("confirm");
  };

  const handleSubmit = async () => {
    if (!selectedItem || !selectedType) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await onSubmit({
        title: moduleTitle || undefined,
        content_type: selectedType,
        object_id: selectedItem.id,
      });
      onClose();
    } catch (err) {
      setSubmitError(
        err instanceof Error
          ? err.message
          : t("course.detail.modules.addError"),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBack = () => {
    if (step === "confirm") {
      setSelectedItem(null);
      setStep("search");
    } else if (step === "search" && !isEditMode) {
      setSelectedType("");
      setQuery("");
      setResults([]);
      setStep("type");
    }
  };

  const handleBackdropKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape" && !isSubmitting) {
      onClose();
    }
  };

  if (!isOpen) return null;

  const modalTitle = isEditMode
    ? t("course.detail.addModuleModal.editTitle")
    : t("course.detail.addModuleModal.title");

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onKeyDown={handleBackdropKeyDown}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={!isSubmitting ? onClose : undefined}
      />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-sm sm:max-w-lg p-6 sm:p-8 border border-gray-200/50 dark:border-gray-700/30 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          {step !== "type" && (
            <button
              type="button"
              onClick={handleBack}
              disabled={isSubmitting}
              className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 cursor-pointer"
              aria-label={t("course.detail.addModuleModal.back")}
            >
              <HiArrowLeft className="w-5 h-5 rtl:rotate-180" />
            </button>
          )}
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {modalTitle}
          </h2>
        </div>

        {/* Step 1: Type Selection */}
        {step === "type" && (
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              {t("course.detail.addModuleModal.selectType")}
            </p>
            <div className="grid grid-cols-2 gap-3">
              {MODULE_TYPES.map((type) => {
                const Icon = type.icon;
                return (
                  <button
                    key={type.key}
                    type="button"
                    onClick={() =>
                      type.enabled && handleTypeSelect(type.contentType)
                    }
                    disabled={!type.enabled}
                    className={`flex flex-col items-center gap-2 p-4 rounded-xl border transition-all ${
                      type.enabled
                        ? "border-gray-200 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 cursor-pointer"
                        : "border-gray-100 dark:border-gray-700 opacity-50 cursor-not-allowed"
                    }`}
                  >
                    <Icon
                      className={`w-8 h-8 ${
                        type.enabled
                          ? "text-blue-500 dark:text-blue-400"
                          : "text-gray-300 dark:text-gray-600"
                      }`}
                    />
                    <span
                      className={`text-sm font-medium ${
                        type.enabled
                          ? "text-gray-900 dark:text-white"
                          : "text-gray-400 dark:text-gray-500"
                      }`}
                    >
                      {t(`course.detail.addModuleModal.${type.key}`)}
                    </span>
                    {!type.enabled && (
                      <span className="text-xs text-gray-400 dark:text-gray-500">
                        {t("course.detail.addModuleModal.comingSoonType")}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 2: Search & Select */}
        {step === "search" && (
          <div>
            {/* Mine/All toggle */}
            <div className="flex gap-2 mb-4">
              <button
                type="button"
                onClick={() => setMineOnly(true)}
                className={`flex-1 px-3 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                  mineOnly
                    ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                    : "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600"
                }`}
              >
                {t("course.detail.addModuleModal.mySlideshows")}
              </button>
              <button
                type="button"
                onClick={() => {
                  setMineOnly(false);
                  if (!query) inputRef.current?.focus();
                }}
                className={`flex-1 px-3 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                  !mineOnly
                    ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                    : "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600"
                }`}
              >
                {t("course.detail.addModuleModal.allSlideshows")}
              </button>
            </div>

            {/* Search input */}
            <div className="relative mb-4">
              <HiMagnifyingGlass className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              <input
                ref={inputRef}
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t(
                  "course.detail.addModuleModal.searchPlaceholder",
                )}
                aria-label={t("course.detail.addModuleModal.searchLabel")}
                className="w-full ps-9 pe-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm text-gray-700 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 transition-all duration-200"
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

            {/* Min chars hint */}
            {query.length > 0 && query.length < 2 && !mineOnly && (
              <p className="text-sm text-gray-400 dark:text-gray-500 mb-4">
                {t("course.detail.addModuleModal.searchMinChars")}
              </p>
            )}

            {/* Results */}
            {!isLoading && results.length > 0 && (
              <ul
                className="space-y-2 max-h-64 overflow-y-auto"
                role="listbox"
                aria-label={t("course.detail.addModuleModal.searchLabel")}
              >
                {results.map((item) => {
                  const isAlreadyAdded = existingObjectIds.has(item.id);
                  return (
                    <li
                      key={item.id}
                      role="option"
                      aria-selected={false}
                      aria-disabled={isAlreadyAdded}
                      onClick={() => !isAlreadyAdded && handleItemSelect(item)}
                      className={`flex items-start gap-3 p-3 rounded-xl border transition-colors ${
                        isAlreadyAdded
                          ? "border-gray-200/50 dark:border-gray-700/30 opacity-50 cursor-not-allowed"
                          : "border-gray-200/50 dark:border-gray-700/30 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-600 cursor-pointer"
                      }`}
                    >
                      <HiPresentationChartBar className="w-5 h-5 text-blue-500 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {item.title}
                        </p>
                        {item.description && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mt-0.5">
                            {item.description}
                          </p>
                        )}
                        <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                          <span
                            className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                              item.is_published
                                ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
                                : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300"
                            }`}
                          >
                            {item.is_published
                              ? t("course.detail.addModuleModal.published")
                              : t("course.detail.addModuleModal.draft")}
                          </span>
                          <span className="text-xs text-gray-400 dark:text-gray-500">
                            {t("course.detail.addModuleModal.slides", {
                              count: item.slide_count,
                            })}
                          </span>
                          {item.visibility !== "public" && (
                            <span className="text-xs text-gray-400 dark:text-gray-500 capitalize">
                              {item.visibility}
                            </span>
                          )}
                          {isAlreadyAdded && (
                            <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                              {t("course.detail.addModuleModal.alreadyAdded")}
                            </span>
                          )}
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}

            {/* Create slideshow link below results */}
            {!isLoading && results.length > 0 && mineOnly && (
              <div className="mt-3 text-center">
                <Link
                  to="/slideshows/new"
                  className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline transition-colors"
                >
                  {t("course.detail.addModuleModal.createSlideshow")}
                </Link>
              </div>
            )}

            {/* No results */}
            {!isLoading &&
              results.length === 0 &&
              (debouncedQuery.length >= 2 ||
                (mineOnly && debouncedQuery.length === 0)) &&
              !searchError && (
                <div className="text-center py-8">
                  <HiPresentationChartBar className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {t("course.detail.addModuleModal.noResults")}
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    {t("course.detail.addModuleModal.noResultsHint")}
                  </p>
                  {mineOnly && (
                    <Link
                      to="/slideshows/new"
                      className="inline-block mt-3 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline transition-colors"
                    >
                      {t("course.detail.addModuleModal.createSlideshow")}
                    </Link>
                  )}
                </div>
              )}

            {/* Search error */}
            {searchError && (
              <p className="text-sm text-red-500 text-center py-4">
                {searchError}
              </p>
            )}

            {/* Prompt to search when "All" mode with no query */}
            {!mineOnly && query.length === 0 && !isLoading && (
              <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-8">
                {t("course.detail.addModuleModal.searchMinChars")}
              </p>
            )}
          </div>
        )}

        {/* Step 3: Confirm & Submit */}
        {step === "confirm" && selectedItem && (
          <div className="space-y-4">
            {/* Selected content summary */}
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                {t("course.detail.addModuleModal.selectedContent")}
              </p>
              <div className="flex items-start gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-700/50">
                <HiCheck className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-blue-800 dark:text-blue-200 truncate">
                    {selectedItem.title}
                  </p>
                  {selectedItem.description && (
                    <p className="text-xs text-blue-600 dark:text-blue-300/70 line-clamp-2 mt-0.5">
                      {selectedItem.description}
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-1.5">
                    <span
                      className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${
                        selectedItem.is_published
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
                          : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300"
                      }`}
                    >
                      {selectedItem.is_published
                        ? t("course.detail.addModuleModal.published")
                        : t("course.detail.addModuleModal.draft")}
                    </span>
                    <span className="text-xs text-blue-500 dark:text-blue-400">
                      {t("course.detail.addModuleModal.slides", {
                        count: selectedItem.slide_count,
                      })}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Module title input */}
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {t("course.detail.addModuleModal.titleLabel")}
              </label>
              <input
                type="text"
                value={moduleTitle}
                onChange={(e) => setModuleTitle(e.target.value)}
                placeholder={t("course.detail.addModuleModal.titlePlaceholder")}
                disabled={isSubmitting}
                className="w-full px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm text-gray-700 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed"
              />
            </div>

            {/* Submit error */}
            {submitError && (
              <p className="text-sm text-red-500 text-center">{submitError}</p>
            )}

            {/* Action buttons */}
            <div className="flex flex-col-reverse sm:flex-row gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-medium transition-colors disabled:opacity-50 cursor-pointer"
              >
                {t("course.detail.addModuleModal.cancel")}
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2"
              >
                {isSubmitting && (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                )}
                {isSubmitting
                  ? isEditMode
                    ? t("course.detail.addModuleModal.saving")
                    : t("course.detail.addModuleModal.adding")
                  : isEditMode
                    ? t("course.detail.addModuleModal.editSubmitButton")
                    : t("course.detail.addModuleModal.submitButton")}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
};

export default AddModuleModal;
