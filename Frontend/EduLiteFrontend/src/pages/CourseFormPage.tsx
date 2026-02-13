import React, { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate, useParams, useBlocker } from "react-router-dom";
import { FaArrowLeft, FaSave, FaPlus } from "react-icons/fa";
import toast from "react-hot-toast";
import { useTranslation } from "react-i18next";
import Input from "../components/common/Input";
import LazySelect from "../components/common/LazySelect";
import UnsavedChangesModal from "../components/common/UnsavedChangesModal";
import {
  useUnsavedChanges,
  useFormDirtyState,
} from "../hooks/useUnsavedChanges";
import { useCourseDraft, type CourseFormData } from "../hooks/useCourseDraft";
import {
  createCourse,
  getCourseDetail,
  updateCourse,
} from "../services/coursesApi";
import type { CourseVisibility } from "../types/courses.types";

const DEFAULT_FORM_DATA: CourseFormData = {
  title: "",
  outline: "",
  subject: "",
  language: "",
  country: "",
  visibility: "public",
  start_date: "",
  end_date: "",
  allow_join_requests: true,
};

const CourseFormPage: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const isNewCourse = !id;
  const courseId = isNewCourse ? ("new" as const) : parseInt(id, 10);

  // Draft hook
  const { loadDraft, saveDraft, clearDraft } = useCourseDraft(courseId);

  // Form state
  const [formData, setFormData] = useState<CourseFormData>(DEFAULT_FORM_DATA);
  const [originalFormData, setOriginalFormData] =
    useState<CourseFormData | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(!isNewCourse);
  const [saving, setSaving] = useState(false);
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set());
  const [showNavigationModal, setShowNavigationModal] = useState(false);

  // Refs
  const blockerRef = useRef<ReturnType<typeof useBlocker> | null>(null);
  const initialized = useRef(false);

  // Dirty state
  const isDirty = useFormDirtyState(formData, originalFormData);
  useUnsavedChanges(isDirty, t("course.form.unsavedChanges"));

  // Block navigation when dirty
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && currentLocation.pathname !== nextLocation.pathname,
  );
  blockerRef.current = blocker;

  useEffect(() => {
    if (blocker.state === "blocked") {
      setShowNavigationModal(true);
    }
  }, [blocker]);

  const handleConfirmNavigation = () => {
    setShowNavigationModal(false);
    if (blockerRef.current?.proceed) {
      blockerRef.current.proceed();
    }
  };

  const handleCancelNavigation = () => {
    setShowNavigationModal(false);
    if (blockerRef.current?.reset) {
      blockerRef.current.reset();
    }
  };

  // Helper to check if draft differs from server data
  const draftDiffersFromServer = useCallback(
    (draft: CourseFormData, server: CourseFormData): boolean => {
      const keys = Object.keys(server) as (keyof CourseFormData)[];
      return keys.some((key) => {
        const draftVal = draft[key];
        const serverVal = server[key];
        if (draftVal === serverVal) return false;
        if (!draftVal && !serverVal) return false;
        return true;
      });
    },
    [],
  );

  // Format relative time for draft recovery toast
  const formatTimeAgo = useCallback(
    (isoString: string): string => {
      const diff = Date.now() - new Date(isoString).getTime();
      const minutes = Math.floor(diff / 60000);
      if (minutes < 1) return t("course.form.justNow");
      if (minutes < 60) return t("course.form.minutesAgo", { count: minutes });
      const hours = Math.floor(minutes / 60);
      if (hours < 24) return t("course.form.hoursAgo", { count: hours });
      const days = Math.floor(hours / 24);
      return t("course.form.daysAgo", { count: days });
    },
    [t],
  );

  // Initialize form data
  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const initialize = async () => {
      if (isNewCourse) {
        // Create mode: check for draft
        const draft = loadDraft();
        if (draft) {
          setFormData(draft.data);
          setOriginalFormData(DEFAULT_FORM_DATA);
          toast.success(
            t("course.form.draftRecovered", {
              time: formatTimeAgo(draft.lastModified),
            }),
            { id: "draft-loaded" },
          );
        } else {
          setFormData(DEFAULT_FORM_DATA);
          setOriginalFormData(DEFAULT_FORM_DATA);
        }
        return;
      }

      // Edit mode: fetch course, then check draft
      setLoading(true);
      try {
        const course = await getCourseDetail(courseId as number);

        // Permission check
        if (course.user_role !== "teacher") {
          toast.error(t("course.form.notTeacher"));
          navigate(`/courses/${courseId}`, { replace: true });
          return;
        }

        const serverData: CourseFormData = {
          title: course.title,
          outline: course.outline || "",
          subject: course.subject || "",
          language: course.language || "",
          country: course.country || "",
          visibility: course.visibility,
          start_date: course.start_date ? course.start_date.split("T")[0] : "",
          end_date: course.end_date ? course.end_date.split("T")[0] : "",
          allow_join_requests: course.allow_join_requests,
        };

        setOriginalFormData(serverData);

        // Check for draft
        const draft = loadDraft();
        if (draft && draftDiffersFromServer(draft.data, serverData)) {
          setFormData(draft.data);
          toast.success(
            t("course.form.draftRecovered", {
              time: formatTimeAgo(draft.lastModified),
            }),
            { id: "draft-loaded" },
          );
        } else {
          if (draft) clearDraft();
          setFormData(serverData);
        }
      } catch (error) {
        console.error("Failed to load course:", error);
        toast.error(t("course.form.loadError"));
        navigate("/courses", { replace: true });
      } finally {
        setLoading(false);
      }
    };

    initialize();
  }, [
    isNewCourse,
    courseId,
    loadDraft,
    clearDraft,
    draftDiffersFromServer,
    formatTimeAgo,
    navigate,
    t,
  ]);

  // Auto-save draft to localStorage
  useEffect(() => {
    if (loading || !initialized.current) return;
    saveDraft({
      courseId,
      lastSaved: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      data: formData,
    });
  }, [formData, loading, courseId, saveDraft]);

  // Handlers
  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleFieldChange = (
    field: keyof CourseFormData,
    value: string | boolean,
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
  };

  const handleBlur = (
    e: React.FocusEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLButtonElement
    >,
  ) => {
    const { name } = e.target;
    setTouchedFields((prev) => new Set(prev).add(name));
  };

  const isFieldDirty = (field: keyof CourseFormData): boolean => {
    if (isNewCourse || !originalFormData) return false;
    return (
      touchedFields.has(field) && formData[field] !== originalFormData[field]
    );
  };

  const dirtyClass = (field: keyof CourseFormData): string => {
    return isFieldDirty(field) ? "border-red-300 dark:border-red-500/50" : "";
  };

  // Validation
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = t("course.form.titleRequired");
    }

    if (formData.outline && formData.outline.length > 1000) {
      newErrors.outline = t("course.form.outlineTooLong");
    }

    if (formData.start_date && formData.end_date) {
      if (formData.start_date > formData.end_date) {
        newErrors.end_date = t("course.form.endDateBeforeStart");
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error(t("course.form.fixErrors"));
      return;
    }

    setSaving(true);

    try {
      const buildPayload = () => ({
        title: formData.title,
        outline: formData.outline || null,
        subject: formData.subject || null,
        language: formData.language || null,
        country: formData.country || null,
        visibility: formData.visibility as CourseVisibility,
        start_date: formData.start_date
          ? `${formData.start_date}T00:00:00Z`
          : null,
        end_date: formData.end_date ? `${formData.end_date}T00:00:00Z` : null,
        allow_join_requests: formData.allow_join_requests,
      });

      if (isNewCourse) {
        const newCourse = await createCourse(buildPayload());
        clearDraft();
        // Reset dirty state before navigating so useBlocker doesn't fire
        setOriginalFormData(formData);
        toast.success(t("course.form.createSuccess"));
        navigate(`/courses/${newCourse.id}`, { replace: true });
      } else {
        await updateCourse(courseId as number, buildPayload());
        clearDraft();
        setOriginalFormData(formData);
        setTouchedFields(new Set());
        toast.success(t("course.form.updateSuccess"));
      }
    } catch (error) {
      toast.error(
        error instanceof Error
          ? error.message
          : t(
              isNewCourse
                ? "course.form.createError"
                : "course.form.updateError",
            ),
      );
    } finally {
      setSaving(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4 pt-24">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400 font-light">
            {t("course.form.loading")}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4 pt-24">
      <div className="w-full max-w-3xl mx-auto">
        {/* Back button */}
        <button
          onClick={() =>
            navigate(isNewCourse ? "/courses" : `/courses/${courseId}`)
          }
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors mb-6 cursor-pointer"
        >
          <FaArrowLeft className="text-sm" />
          <span className="font-medium">
            {t(
              isNewCourse
                ? "course.form.backToCourses"
                : "course.form.backToCourse",
            )}
          </span>
        </button>

        {/* Glass-morphism container */}
        <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-light text-gray-900 dark:text-white mb-2 tracking-tight">
              {t(
                isNewCourse
                  ? "course.form.createTitle"
                  : "course.form.editTitle",
              )}
            </h2>
            <p className="text-gray-500 dark:text-gray-400 font-light">
              {t("course.form.subtitle")}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Info Section */}
            <div className="space-y-4">
              <Input
                label={t("course.form.titleLabel")}
                name="title"
                type="text"
                value={formData.title}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder={t("course.form.titlePlaceholder")}
                disabled={saving}
                error={errors.title}
                required
                className={dirtyClass("title")}
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t("course.form.outlineLabel")}
                </label>
                <textarea
                  name="outline"
                  value={formData.outline}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  placeholder={t("course.form.outlinePlaceholder")}
                  disabled={saving}
                  className={`w-full px-4 py-3 bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border ${
                    isFieldDirty("outline")
                      ? "border-red-300 dark:border-red-500/50"
                      : "border-gray-200/50 dark:border-gray-700/30"
                  } rounded-2xl shadow-lg shadow-gray-200/20 dark:shadow-gray-900/20 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-400/50 focus:shadow-xl focus:shadow-blue-500/30 dark:focus:shadow-blue-400/30 focus:scale-[1.02] transition-all duration-300 ease-out font-light resize-none`}
                  rows={4}
                  maxLength={1000}
                />
                {errors.outline && (
                  <p className="text-red-500 text-sm mt-1">{errors.outline}</p>
                )}
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {t("course.form.outlineCharCount", {
                    count: formData.outline.length,
                  })}
                </p>
              </div>
            </div>

            {/* Classification Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <LazySelect
                label={t("course.form.subjectLabel")}
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder={t("course.form.selectPlaceholder")}
                disabled={saving}
                error={errors.subject}
                choiceType="subjects"
                className={dirtyClass("subject")}
              />

              <LazySelect
                label={t("course.form.languageLabel")}
                name="language"
                value={formData.language}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder={t("course.form.selectPlaceholder")}
                disabled={saving}
                error={errors.language}
                choiceType="languages"
                className={dirtyClass("language")}
              />

              <LazySelect
                label={t("course.form.countryLabel")}
                name="country"
                value={formData.country}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder={t("course.form.selectPlaceholder")}
                disabled={saving}
                error={errors.country}
                choiceType="countries"
                searchable
                className={dirtyClass("country")}
              />
            </div>

            {/* Visibility Section */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                {t("course.form.visibilityLabel")}
              </label>
              <div className="space-y-2">
                {(
                  [
                    ["public", "visibilityPublicDesc"],
                    ["restricted", "visibilityRestrictedDesc"],
                    ["private", "visibilityPrivateDesc"],
                  ] as const
                ).map(([value, descKey]) => (
                  <label
                    key={value}
                    className={`flex items-start gap-3 p-3 rounded-xl cursor-pointer transition-all duration-200 ${
                      formData.visibility === value
                        ? "bg-blue-500/10 border border-blue-500/30 dark:border-blue-400/30"
                        : "bg-gray-50/50 dark:bg-gray-900/30 border border-transparent hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="visibility"
                      value={value}
                      checked={formData.visibility === value}
                      onChange={(e) =>
                        handleFieldChange("visibility", e.target.value)
                      }
                      disabled={saving}
                      className="mt-1 accent-blue-500"
                    />
                    <div>
                      <span className="font-medium text-gray-900 dark:text-white capitalize">
                        {t(
                          `course.form.visibility${value.charAt(0).toUpperCase() + value.slice(1)}`,
                        )}
                      </span>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {t(`course.form.${descKey}`)}
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Allow Join Requests — only for restricted visibility */}
            {formData.visibility === "restricted" && (
              <label className="flex items-center gap-3 p-3 rounded-xl bg-gray-50/50 dark:bg-gray-900/30 cursor-pointer">
                <input
                  type="checkbox"
                  name="allow_join_requests"
                  checked={formData.allow_join_requests}
                  onChange={(e) =>
                    handleFieldChange("allow_join_requests", e.target.checked)
                  }
                  disabled={saving}
                  className="w-4 h-4 accent-blue-500 rounded"
                />
                <div>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {t("course.form.allowJoinRequestsLabel")}
                  </span>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {t("course.form.allowJoinRequestsDesc")}
                  </p>
                </div>
              </label>
            )}

            {/* Schedule Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label={t("course.form.startDateLabel")}
                name="start_date"
                type="date"
                value={formData.start_date}
                onChange={handleChange}
                onBlur={handleBlur}
                disabled={saving}
                error={errors.start_date}
                className={dirtyClass("start_date")}
              />

              <Input
                label={t("course.form.endDateLabel")}
                name="end_date"
                type="date"
                value={formData.end_date}
                onChange={handleChange}
                onBlur={handleBlur}
                disabled={saving}
                error={errors.end_date}
                className={dirtyClass("end_date")}
              />
            </div>

            {/* Submit Button */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={saving || (!isNewCourse && !isDirty)}
                className="w-full flex items-center justify-center gap-3 px-6 py-3 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 dark:bg-blue-500/10 dark:hover:bg-blue-500/20 transition-all duration-200 group cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 dark:border-blue-400"></div>
                    <span className="font-medium text-blue-600 dark:text-blue-400">
                      {t(
                        isNewCourse
                          ? "course.form.creating"
                          : "course.form.saving",
                      )}
                    </span>
                  </>
                ) : (
                  <>
                    {isNewCourse ? (
                      <FaPlus className="text-lg text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300" />
                    ) : (
                      <FaSave className="text-lg text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300" />
                    )}
                    <span className="font-medium text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300">
                      {t(
                        isNewCourse
                          ? "course.form.createButton"
                          : "course.form.saveButton",
                      )}
                    </span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Unsaved Changes Modal */}
      <UnsavedChangesModal
        isOpen={showNavigationModal}
        onConfirm={handleConfirmNavigation}
        onCancel={handleCancelNavigation}
        message={t("course.form.unsavedChangesMessage")}
      />
    </div>
  );
};

export default CourseFormPage;
