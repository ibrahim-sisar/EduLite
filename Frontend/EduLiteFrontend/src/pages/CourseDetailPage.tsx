import { useEffect, useState, useRef, useMemo } from "react";
import {
  useParams,
  useNavigate,
  useBlocker,
  useSearchParams,
  Link,
} from "react-router-dom";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import { FaSave } from "react-icons/fa";
import {
  HiArrowLeft,
  HiPencil,
  HiTrash,
  HiUserGroup,
  HiGlobeAlt,
  HiLockClosed,
  HiShieldCheck,
  HiCalendar,
  HiAcademicCap,
  HiLanguage,
  HiMapPin,
  HiBookOpen,
  HiArrowRightOnRectangle,
  HiArrowLeftOnRectangle,
  HiXMark,
} from "react-icons/hi2";
import {
  useUnsavedChanges,
  useFormDirtyState,
} from "../hooks/useUnsavedChanges";
import { useCourseDetail } from "../hooks/useCourseDetail";
import { useCourseMembers } from "../hooks/useCourseMembers";
import { useCourseModules } from "../hooks/useCourseModules";
import * as coursesApi from "../services/coursesApi";
import { getStoredTokens } from "../services/tokenService";
import type { CourseVisibility, CourseRole } from "../types/courses.types";
import UnsavedChangesModal from "../components/common/UnsavedChangesModal";
import ConfirmationModal from "../components/common/ConfirmationModal";
import LazySelect from "../components/common/LazySelect";
import HardLoadSelect from "../components/common/HardLoadSelect";
import MembersTab from "../components/courses/MembersTab";
import ModulesTab from "../components/courses/ModulesTab";

interface CourseFormData {
  title: string;
  outline: string;
  subject: string;
  language: string;
  country: string;
  visibility: CourseVisibility;
  start_date: string;
  end_date: string;
  allow_join_requests: boolean;
}

const VISIBILITY_CHOICES: Array<[string, string]> = [
  ["public", "Public"],
  ["restricted", "Restricted"],
  ["private", "Private"],
];

const VISIBILITY_ICONS: Record<string, React.ReactNode> = {
  public: <HiGlobeAlt className="w-5 h-5" />,
  restricted: <HiShieldCheck className="w-5 h-5" />,
  private: <HiLockClosed className="w-5 h-5" />,
};

// Lookup maps for human-readable labels
const SUBJECTS: Record<string, string> = {
  math: "Mathematics",
  physics: "Physics",
  chemistry: "Chemistry",
  biology: "Biology",
  cs: "Computer Science",
  literature: "Literature",
  history: "History",
  geography: "Geography",
  art: "Art",
  music: "Music",
  pe: "Physical Education",
  economics: "Economics",
  philosophy: "Philosophy",
  psychology: "Psychology",
  engineering: "Engineering",
  medicine: "Medicine",
  law: "Law",
  business: "Business",
  other: "Other",
};

const LANGUAGES: Record<string, string> = {
  en: "English",
  ar: "Arabic",
  fr: "French",
  es: "Spanish",
  de: "German",
  zh: "Chinese",
  ja: "Japanese",
  ko: "Korean",
  pt: "Portuguese",
  ru: "Russian",
  hi: "Hindi",
  tr: "Turkish",
};

const CourseDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  const courseId = Number(id);
  const activeTab = searchParams.get("tab") || "members";

  // Data hooks
  const {
    course,
    loading,
    error,
    refetch: refetchCourse,
  } = useCourseDetail(courseId);
  const {
    members,
    loading: membersLoading,
    error: membersError,
    refetch: refetchMembers,
  } = useCourseMembers(courseId);
  const {
    modules,
    loading: modulesLoading,
    error: modulesError,
    refetch: refetchModules,
  } = useCourseModules(courseId);

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set());

  // Form data
  const [originalFormData, setOriginalFormData] =
    useState<CourseFormData | null>(null);
  const [formData, setFormData] = useState<CourseFormData>({
    title: "",
    outline: "",
    subject: "",
    language: "",
    country: "",
    visibility: "public",
    start_date: "",
    end_date: "",
    allow_join_requests: true,
  });

  // Modal state
  const [showNavigationModal, setShowNavigationModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [joining, setJoining] = useState(false);
  const [, setLeaving] = useState(false);

  // Refs
  const blockerRef = useRef<ReturnType<typeof useBlocker> | null>(null);

  // Dirty state tracking
  const isDirty = useFormDirtyState(formData, originalFormData);
  useUnsavedChanges(isDirty && isEditing, t("course.detail.unsavedChanges"));

  // Block navigation when editing with unsaved changes
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty &&
      isEditing &&
      currentLocation.pathname !== nextLocation.pathname,
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

  // Redirect on invalid ID
  useEffect(() => {
    if (!id || isNaN(courseId)) {
      toast.error(t("course.detail.notFound"));
      navigate("/courses", { replace: true });
    }
  }, [id, courseId, navigate, t]);

  // Initialize form data when course loads
  useEffect(() => {
    if (course) {
      const data: CourseFormData = {
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
      setFormData(data);
      setOriginalFormData(data);
    }
  }, [course]);

  // Derived state
  const isTeacher = course?.user_role === "teacher";
  const isMember = course?.user_role !== null;
  const userRole = course?.user_role;

  const currentUserId = useMemo(() => {
    try {
      const { access } = getStoredTokens();
      if (!access) return null;
      const payload = JSON.parse(atob(access.split(".")[1]));
      return payload.user_id as number;
    } catch {
      return null;
    }
  }, []);

  // Handlers
  const handleFieldChange = (
    field: keyof CourseFormData,
    value: string | boolean,
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleBlur = (field: keyof CourseFormData) => {
    setTouchedFields((prev) => new Set(prev).add(field));
  };

  const handleStartEditing = () => {
    setIsEditing(true);
    setTouchedFields(new Set());
  };

  const handleCancelEditing = () => {
    if (originalFormData) {
      setFormData(originalFormData);
    }
    setTouchedFields(new Set());
    setIsEditing(false);
  };

  const handleSave = async () => {
    if (!course) return;
    setSaving(true);
    try {
      await coursesApi.updateCourse(course.id, {
        title: formData.title,
        outline: formData.outline || null,
        subject: formData.subject || null,
        language: formData.language || null,
        country: formData.country || null,
        visibility: formData.visibility,
        start_date: formData.start_date
          ? `${formData.start_date}T00:00:00Z`
          : null,
        end_date: formData.end_date ? `${formData.end_date}T00:00:00Z` : null,
        allow_join_requests: formData.allow_join_requests,
      });
      toast.success(t("course.detail.saveSuccess"));
      setTouchedFields(new Set());
      setIsEditing(false);
      refetchCourse();
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : t("course.detail.saveError"),
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!course) return;
    setDeleting(true);
    try {
      await coursesApi.deleteCourse(course.id);
      toast.success(t("course.detail.deleteSuccess"));
      navigate("/courses");
    } catch {
      toast.error(t("course.detail.deleteError"));
    } finally {
      setDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const handleJoin = async () => {
    if (!course) return;
    setJoining(true);
    try {
      const membership = await coursesApi.enrollInCourse(course.id);
      if (membership.status === "pending") {
        toast.success(t("course.detail.joinPending"));
      } else {
        toast.success(t("course.detail.joinSuccess"));
      }
      refetchCourse();
      refetchMembers();
    } catch {
      toast.error(t("course.detail.joinError"));
    } finally {
      setJoining(false);
    }
  };

  const handleLeave = async () => {
    if (!course) return;
    setLeaving(true);
    try {
      await coursesApi.leaveCourse(course.id);
      toast.success(t("course.detail.leaveSuccess"));
      refetchCourse();
      refetchMembers();
    } catch {
      toast.error(t("course.detail.leaveError"));
    } finally {
      setLeaving(false);
      setShowLeaveModal(false);
    }
  };

  const setTab = (tab: string) => {
    setSearchParams({ tab });
  };

  const getRoleBadgeClasses = (role: CourseRole | null | undefined) => {
    switch (role) {
      case "teacher":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300";
      case "assistant":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300";
      case "student":
        return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300";
    }
  };

  const getFieldBorderClass = (field: keyof CourseFormData) => {
    if (
      touchedFields.has(field) &&
      formData[field] !== originalFormData?.[field]
    ) {
      return "border-red-300 dark:border-red-500/50";
    }
    return "border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500";
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return t("course.detail.notSet");
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-500 dark:text-gray-400">
                {t("course.detail.loading")}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !course) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center py-20">
          <p className="text-red-500 text-lg mb-4">
            {error || t("course.detail.notFound")}
          </p>
          <button
            onClick={refetchCourse}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all cursor-pointer"
          >
            {t("course.detail.retryButton")}
          </button>
        </div>
      </div>
    );
  }

  // Determine join button visibility
  const canJoin =
    !isMember &&
    (course.visibility === "public" ||
      (course.visibility === "restricted" && course.allow_join_requests));

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <Link
          to="/courses"
          className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors mb-6"
        >
          <HiArrowLeft className="w-5 h-5" />
          <span>{t("course.detail.backToCourses")}</span>
        </Link>

        {/* Main Card */}
        <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 overflow-hidden">
          {/* ===== HEADER SECTION ===== */}
          <div className="p-8 border-b border-gray-200/50 dark:border-gray-700/30">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div className="flex-1">
                {/* Title */}
                {isEditing ? (
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => handleFieldChange("title", e.target.value)}
                    onBlur={() => handleBlur("title")}
                    className={`text-3xl font-light text-gray-900 dark:text-white mb-2 bg-transparent border-b-2 ${getFieldBorderClass("title")} focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none w-full transition-colors`}
                    placeholder="Course Title"
                  />
                ) : (
                  <h1 className="text-3xl font-light text-gray-900 dark:text-white mb-2">
                    {course.title}
                  </h1>
                )}

                {/* Outline */}
                {isEditing ? (
                  <textarea
                    value={formData.outline}
                    onChange={(e) =>
                      handleFieldChange("outline", e.target.value)
                    }
                    onBlur={() => handleBlur("outline")}
                    className={`text-lg text-gray-600 dark:text-gray-400 leading-relaxed bg-transparent border ${getFieldBorderClass("outline")} focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none w-full rounded-lg p-2 min-h-[60px] resize-y transition-colors`}
                    placeholder="Course outline..."
                  />
                ) : (
                  <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
                    {course.outline || t("course.detail.outline")}
                  </p>
                )}
              </div>

              {/* Role Badge */}
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium flex-shrink-0 ${getRoleBadgeClasses(userRole)}`}
              >
                {t(`course.detail.role.${userRole || "notEnrolled"}`)}
              </span>
            </div>
          </div>

          {/* ===== METADATA SECTION ===== */}
          <div className="p-8 border-b border-gray-200/50 dark:border-gray-700/30">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Subject */}
              {isEditing ? (
                <div className="col-span-1 md:col-span-2">
                  <LazySelect
                    label={t("course.detail.subject")}
                    name="subject"
                    value={formData.subject}
                    onChange={(e) =>
                      handleFieldChange("subject", e.target.value)
                    }
                    onBlur={() => handleBlur("subject")}
                    placeholder="Select a subject..."
                    choiceType="subjects"
                    searchable={true}
                    className={
                      touchedFields.has("subject") &&
                      formData.subject !== originalFormData?.subject
                        ? "border-red-300 dark:border-red-500/50"
                        : ""
                    }
                  />
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <HiAcademicCap className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {t("course.detail.subject")}
                    </div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {SUBJECTS[course.subject || ""] ||
                        course.subject ||
                        t("course.detail.notSet")}
                    </div>
                  </div>
                </div>
              )}

              {/* Language */}
              {isEditing ? (
                <div className="col-span-1 md:col-span-2">
                  <LazySelect
                    label={t("course.detail.language")}
                    name="language"
                    value={formData.language}
                    onChange={(e) =>
                      handleFieldChange("language", e.target.value)
                    }
                    onBlur={() => handleBlur("language")}
                    placeholder="Select a language..."
                    choiceType="languages"
                    searchable={true}
                    className={
                      touchedFields.has("language") &&
                      formData.language !== originalFormData?.language
                        ? "border-red-300 dark:border-red-500/50"
                        : ""
                    }
                  />
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <HiLanguage className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {t("course.detail.language")}
                    </div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {LANGUAGES[course.language || ""] ||
                        course.language ||
                        t("course.detail.notSet")}
                    </div>
                  </div>
                </div>
              )}

              {/* Country */}
              {isEditing ? (
                <div className="col-span-1 md:col-span-2">
                  <LazySelect
                    label={t("course.detail.country")}
                    name="country"
                    value={formData.country}
                    onChange={(e) =>
                      handleFieldChange("country", e.target.value)
                    }
                    onBlur={() => handleBlur("country")}
                    placeholder="Select a country..."
                    choiceType="countries"
                    searchable={true}
                    className={
                      touchedFields.has("country") &&
                      formData.country !== originalFormData?.country
                        ? "border-red-300 dark:border-red-500/50"
                        : ""
                    }
                  />
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <HiMapPin className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {t("course.detail.country")}
                    </div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {course.country || t("course.detail.notSet")}
                    </div>
                  </div>
                </div>
              )}

              {/* Visibility */}
              {isEditing ? (
                <HardLoadSelect
                  label={t("course.detail.visibility")}
                  name="visibility"
                  value={formData.visibility}
                  onChange={(e) =>
                    handleFieldChange("visibility", e.target.value)
                  }
                  onBlur={() => handleBlur("visibility")}
                  choices={VISIBILITY_CHOICES}
                  hasChanged={
                    formData.visibility !== originalFormData?.visibility
                  }
                  isTouched={touchedFields.has("visibility")}
                />
              ) : (
                <div className="flex items-center gap-3">
                  <div className="text-gray-400">
                    {VISIBILITY_ICONS[course.visibility]}
                  </div>
                  <div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {t("course.detail.visibility")}
                    </div>
                    <div className="font-medium text-gray-900 dark:text-white capitalize">
                      {course.visibility}
                    </div>
                  </div>
                </div>
              )}

              {/* Member Count */}
              <div className="flex items-center gap-3">
                <HiUserGroup className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {t("course.detail.tabs.members")}
                  </div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {t("course.detail.memberCount", {
                      count: course.member_count,
                    })}
                  </div>
                </div>
              </div>

              {/* Start Date */}
              {isEditing ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t("course.detail.startDate")}
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) =>
                      handleFieldChange("start_date", e.target.value)
                    }
                    onBlur={() => handleBlur("start_date")}
                    className={`w-full px-4 py-3 bg-white dark:bg-gray-800 border ${getFieldBorderClass("start_date")} rounded-xl shadow-sm text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer [&::-webkit-calendar-picker-indicator]:cursor-pointer`}
                  />
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <HiCalendar className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {t("course.detail.startDate")}
                    </div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {formatDate(course.start_date)}
                    </div>
                  </div>
                </div>
              )}

              {/* End Date */}
              {isEditing ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t("course.detail.endDate")}
                  </label>
                  {formData.end_date ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="date"
                        value={formData.end_date}
                        onChange={(e) =>
                          handleFieldChange("end_date", e.target.value)
                        }
                        onBlur={() => handleBlur("end_date")}
                        className={`flex-1 px-4 py-3 bg-white dark:bg-gray-800 border ${getFieldBorderClass("end_date")} rounded-xl shadow-sm text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer [&::-webkit-calendar-picker-indicator]:cursor-pointer`}
                      />
                      <button
                        type="button"
                        onClick={() => handleFieldChange("end_date", "")}
                        title={t("course.detail.noEndDate")}
                        className="p-3 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors cursor-pointer"
                      >
                        <HiXMark className="w-5 h-5" />
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() =>
                        handleFieldChange(
                          "end_date",
                          new Date().toISOString().split("T")[0],
                        )
                      }
                      className={`w-full flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-800 border ${getFieldBorderClass("end_date")} rounded-xl shadow-sm transition-all cursor-pointer hover:border-gray-400 dark:hover:border-gray-500`}
                    >
                      <span className="text-gray-400 dark:text-gray-500 italic">
                        {t("course.detail.noEndDate")}
                      </span>
                      <span className="inline-flex items-center gap-1 text-sm text-blue-600 dark:text-blue-400 font-medium">
                        <HiCalendar className="w-4 h-4" />
                        {t("course.detail.setEndDate")}
                      </span>
                    </button>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <HiCalendar className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {t("course.detail.endDate")}
                    </div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {formatDate(course.end_date)}
                    </div>
                  </div>
                </div>
              )}

              {/* Active Status */}
              <div className="flex items-center gap-3">
                <HiBookOpen className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Status
                  </div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {course.is_active
                      ? t("course.detail.active")
                      : t("course.detail.inactive")}
                  </div>
                </div>
              </div>

              {/* Allow Join Requests (edit mode only) */}
              {isEditing && (
                <div className="flex items-center gap-3 col-span-1 md:col-span-2">
                  <button
                    type="button"
                    role="switch"
                    aria-checked={formData.allow_join_requests}
                    onClick={() =>
                      handleFieldChange(
                        "allow_join_requests",
                        !formData.allow_join_requests,
                      )
                    }
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 cursor-pointer ${
                      formData.allow_join_requests
                        ? "bg-blue-600"
                        : "bg-gray-300 dark:bg-gray-600"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200 ${
                        formData.allow_join_requests
                          ? "translate-x-6"
                          : "translate-x-1"
                      }`}
                    />
                  </button>
                  <span
                    className="text-gray-700 dark:text-gray-300 font-medium cursor-pointer"
                    onClick={() =>
                      handleFieldChange(
                        "allow_join_requests",
                        !formData.allow_join_requests,
                      )
                    }
                  >
                    {t("course.detail.allowJoinRequests")}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* ===== SAVE CHANGES BANNER ===== */}
          {isEditing && isDirty && (
            <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></div>
                  <p className="text-amber-800 dark:text-amber-200 font-medium">
                    {t("course.detail.unsavedChanges")}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleCancelEditing}
                    className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors font-medium cursor-pointer"
                  >
                    {t("course.detail.cancelButton")}
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {saving ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>{t("course.detail.saving")}</span>
                      </>
                    ) : (
                      <>
                        <FaSave className="w-4 h-4" />
                        <span>{t("course.detail.saveButton")}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ===== ACTION BUTTONS ===== */}
          <div className="p-8 border-b border-gray-200/50 dark:border-gray-700/30 bg-gray-50/50 dark:bg-gray-900/20">
            <div className="flex flex-wrap gap-4">
              {/* Teacher actions */}
              {isTeacher && !isEditing && (
                <>
                  <button
                    onClick={handleStartEditing}
                    className="inline-flex items-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg font-medium transition-all cursor-pointer"
                  >
                    <HiPencil className="w-5 h-5" />
                    {t("course.detail.editButton")}
                  </button>
                  <button
                    onClick={() => setShowDeleteModal(true)}
                    className="inline-flex items-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 hover:border-red-500 dark:hover:border-red-400 text-gray-700 dark:text-gray-200 hover:text-red-600 dark:hover:text-red-400 rounded-lg font-medium transition-all cursor-pointer"
                  >
                    <HiTrash className="w-5 h-5" />
                    {t("course.detail.deleteButton")}
                  </button>
                </>
              )}

              {isEditing && (
                <button
                  onClick={handleCancelEditing}
                  className="inline-flex items-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-all hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                >
                  {t("course.detail.cancelButton")}
                </button>
              )}

              {/* Join button */}
              {canJoin && (
                <button
                  onClick={handleJoin}
                  disabled={joining}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <HiArrowRightOnRectangle className="w-5 h-5" />
                  {course.visibility === "restricted"
                    ? t("course.detail.requestJoinButton")
                    : t("course.detail.joinButton")}
                </button>
              )}

              {/* Leave button (non-teacher members) */}
              {isMember && !isTeacher && !isEditing && (
                <button
                  onClick={() => setShowLeaveModal(true)}
                  className="inline-flex items-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 hover:border-red-500 dark:hover:border-red-400 text-gray-700 dark:text-gray-200 hover:text-red-600 dark:hover:text-red-400 rounded-lg font-medium transition-all cursor-pointer"
                >
                  <HiArrowLeftOnRectangle className="w-5 h-5" />
                  {t("course.detail.leaveButton")}
                </button>
              )}
            </div>
          </div>

          {/* ===== TAB NAVIGATION ===== */}
          <div className="border-b border-gray-200/50 dark:border-gray-700/30">
            <div className="flex">
              <button
                onClick={() => setTab("members")}
                className={`flex-1 sm:flex-none px-6 py-4 text-sm font-medium transition-colors border-b-2 cursor-pointer ${
                  activeTab === "members"
                    ? "border-blue-500 text-blue-600 dark:text-blue-400"
                    : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                }`}
              >
                <span className="inline-flex items-center gap-2">
                  <HiUserGroup className="w-4 h-4" />
                  {t("course.detail.tabs.members")}
                </span>
              </button>
              <button
                onClick={() => setTab("modules")}
                className={`flex-1 sm:flex-none px-6 py-4 text-sm font-medium transition-colors border-b-2 cursor-pointer ${
                  activeTab === "modules"
                    ? "border-blue-500 text-blue-600 dark:text-blue-400"
                    : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                }`}
              >
                <span className="inline-flex items-center gap-2">
                  <HiBookOpen className="w-4 h-4" />
                  {t("course.detail.tabs.modules")}
                </span>
              </button>
            </div>
          </div>

          {/* ===== TAB CONTENT ===== */}
          <div className="p-8">
            {activeTab === "members" ? (
              <MembersTab
                courseId={course.id}
                members={members}
                loading={membersLoading}
                error={membersError}
                isTeacher={isTeacher}
                currentUserId={currentUserId}
                refetch={refetchMembers}
              />
            ) : (
              <ModulesTab
                courseId={course.id}
                modules={modules}
                loading={modulesLoading}
                error={modulesError}
                isTeacher={isTeacher}
                refetch={refetchModules}
              />
            )}
          </div>
        </div>
      </div>

      {/* ===== MODALS ===== */}
      <UnsavedChangesModal
        isOpen={showNavigationModal}
        onConfirm={handleConfirmNavigation}
        onCancel={handleCancelNavigation}
        message={t("course.detail.unsavedChanges")}
      />

      <ConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDelete}
        title={t("course.detail.deleteConfirmTitle")}
        message={t("course.detail.deleteConfirmMessage", {
          title: course.title,
        })}
        confirmText={
          deleting
            ? t("course.detail.deleting")
            : t("course.detail.deleteButton")
        }
        cancelText={t("common.cancel")}
        confirmButtonClass="bg-red-600 hover:bg-red-700 text-white"
      />

      <ConfirmationModal
        isOpen={showLeaveModal}
        onClose={() => setShowLeaveModal(false)}
        onConfirm={handleLeave}
        title={t("course.detail.leaveConfirmTitle")}
        message={t("course.detail.leaveConfirmMessage", {
          title: course.title,
        })}
        confirmText={t("course.detail.leaveButton")}
        cancelText={t("common.cancel")}
        confirmButtonClass="bg-red-600 hover:bg-red-700 text-white"
      />
    </div>
  );
};

export default CourseDetailPage;
