import { useState, useEffect, useMemo, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import {
  HiAcademicCap,
  HiPlus,
  HiChevronLeft,
  HiChevronRight,
  HiDotsVertical,
  HiEye,
  HiLogout,
  HiLogin,
  HiGlobeAlt,
  HiUser,
  HiFilter,
  HiX,
  HiChevronDown,
  HiCheck,
} from "react-icons/hi";
import { useCourses } from "../hooks/useCourses";
import { enrollInCourse, leaveCourse } from "../services/coursesApi";
import type {
  CourseListItem,
  CourseListParams,
  CourseVisibility,
} from "../types/courses.types";
import ContextMenu, {
  type ContextMenuItem,
} from "../components/common/ContextMenu";
import ConfirmationModal from "../components/common/ConfirmationModal";
import LazySelect from "../components/common/LazySelect";

// Lookup maps for readable names (same as SlideshowListPage)
const SUBJECTS: Record<string, string> = {
  math: "Mathematics",
  physics: "Physics",
  chemistry: "Chemistry",
  biology: "Biology",
  cs: "Computer Science",
  it: "Information Technology",
  engineering: "Engineering",
  datasci: "Data Science",
  ai: "Artificial Intelligence",
  envsci: "Environmental Science",
  astronomy: "Astronomy",
  stats: "Statistics",
  robotics: "Robotics",
  electronics: "Electronics",
  psych: "Psychology",
  sociology: "Sociology",
  polisci: "Political Science",
  economics: "Economics",
  anthropology: "Anthropology",
  intlrel: "International Relations",
  criminology: "Criminology",
  history: "History",
  philosophy: "Philosophy",
  literature: "Literature",
  linguistics: "Linguistics",
  religion: "Religious Studies",
  cultural: "Cultural Studies",
  classics: "Classics",
  visualart: "Visual Arts",
  music: "Music",
  performing: "Performing Arts",
  architecture: "Architecture",
  design: "Graphic Design",
  film: "Film & Media Studies",
  photo: "Photography",
  fashion: "Fashion Design",
  business: "Business Administration",
  accounting: "Accounting",
  finance: "Finance",
  marketing: "Marketing",
  hrm: "Human Resource Management",
  entrepreneurship: "Entrepreneurship",
  project: "Project Management",
  supplychain: "Supply Chain Management",
  education: "Education",
  earlyedu: "Early Childhood Education",
  specialedu: "Special Education",
  english: "English Language",
  foreignlang: "Foreign Languages",
  translation: "Translation Studies",
  tesol: "TESOL / ESL",
  law: "Law",
  legal: "Legal Studies",
  constitutional: "Constitutional Law",
  publicpolicy: "Public Policy",
  politicaltheory: "Political Theory",
  medicine: "Medicine",
  nursing: "Nursing",
  pharmacy: "Pharmacy",
  publichealth: "Public Health",
  nutrition: "Nutrition",
  veterinary: "Veterinary Science",
  dentistry: "Dentistry",
  biomed: "Biomedical Science",
  physicaltherapy: "Physical Therapy",
};

const LANGUAGES: Record<string, string> = {
  en: "English",
  fr: "French",
  es: "Spanish",
  ar: "Arabic",
};

const VISIBILITY_LABELS: Record<CourseVisibility, string> = {
  public: "Public",
  restricted: "Restricted",
  private: "Private",
};

interface CourseListPageProps {
  view?: "me" | "public";
}

const CourseListPage: React.FC<CourseListPageProps> = ({ view: propView }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const currentView: "me" | "public" = propView || "me";

  // Filter state
  const [filterSubject, setFilterSubject] = useState("");
  const [filterLanguage, setFilterLanguage] = useState("");
  const [filterCountry, setFilterCountry] = useState("");
  const [filterVisibility, setFilterVisibility] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [visibilityDropdownOpen, setVisibilityDropdownOpen] = useState(false);
  const visibilityDropdownRef = useRef<HTMLDivElement>(null);
  const pageSize = 20;

  const visibilityOptions = [
    { value: "", label: t("course.list.filterVisibility") },
    { value: "public", label: t("course.list.visibilityPublic") },
    { value: "restricted", label: t("course.list.visibilityRestricted") },
    { value: "private", label: t("course.list.visibilityPrivate") },
  ];

  // Close visibility dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        visibilityDropdownRef.current &&
        !visibilityDropdownRef.current.contains(event.target as Node)
      ) {
        setVisibilityDropdownOpen(false);
      }
    };
    if (visibilityDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () =>
        document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [visibilityDropdownOpen]);

  // Build params for the hook
  const params = useMemo<CourseListParams>(() => {
    const p: CourseListParams = {
      page: currentPage,
      page_size: pageSize,
    };
    if (currentView === "me") {
      p.mine = true;
      if (filterVisibility) p.visibility = filterVisibility as CourseVisibility;
    } else {
      p.visibility = "public";
    }
    if (filterSubject) p.subject = filterSubject;
    if (filterLanguage) p.language = filterLanguage;
    if (filterCountry) p.country = filterCountry;
    return p;
  }, [
    currentView,
    currentPage,
    filterSubject,
    filterLanguage,
    filterCountry,
    filterVisibility,
  ]);

  const { courses, loading, error, refetch } = useCourses(params);

  // Context menu state
  const [contextMenuOpen, setContextMenuOpen] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({
    x: 0,
    y: 0,
  });
  const [selectedCourse, setSelectedCourse] = useState<CourseListItem | null>(
    null,
  );

  // Leave confirmation modal state
  const [leaveModalOpen, setLeaveModalOpen] = useState(false);
  const [courseToLeave, setCourseToLeave] = useState<CourseListItem | null>(
    null,
  );

  // Redirect from /courses to /courses/me or /courses/public based on localStorage
  useEffect(() => {
    if (!propView) {
      const stored = localStorage.getItem("courseView");
      const targetView = stored === "public" ? "public" : "me";
      navigate(`/courses/${targetView}`, { replace: true });
    }
  }, [propView, navigate]);

  // Save current view to localStorage
  useEffect(() => {
    if (currentView) {
      localStorage.setItem("courseView", currentView);
    }
  }, [currentView]);

  // Reset page when filters or view change
  useEffect(() => {
    setCurrentPage(1);
  }, [
    currentView,
    filterSubject,
    filterLanguage,
    filterCountry,
    filterVisibility,
  ]);

  const hasActiveFilters =
    filterSubject || filterLanguage || filterCountry || filterVisibility;

  const clearFilters = () => {
    setFilterSubject("");
    setFilterLanguage("");
    setFilterCountry("");
    setFilterVisibility("");
  };

  const handleFilterChange = (
    setter: React.Dispatch<React.SetStateAction<string>>,
  ) => {
    return (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
      setter(e.target.value);
    };
  };

  const handleCourseClick = (course: CourseListItem) => {
    navigate(`/courses/${course.id}`);
  };

  const handleCreateClick = () => {
    navigate("/courses/new");
  };

  const handleContextMenu = (e: React.MouseEvent, course: CourseListItem) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedCourse(course);
    setContextMenuPosition({ x: e.clientX, y: e.clientY });
    setContextMenuOpen(true);
  };

  const handleDotsClick = (e: React.MouseEvent, course: CourseListItem) => {
    e.stopPropagation();
    const rect = (e.target as HTMLElement).getBoundingClientRect();
    setSelectedCourse(course);
    setContextMenuPosition({ x: rect.right - 180, y: rect.bottom + 4 });
    setContextMenuOpen(true);
  };

  const handleViewClick = () => {
    if (!selectedCourse) return;
    navigate(`/courses/${selectedCourse.id}`);
    setContextMenuOpen(false);
  };

  const handleEnrollClick = async () => {
    if (!selectedCourse) return;
    setContextMenuOpen(false);

    try {
      const membership = await enrollInCourse(selectedCourse.id);
      if (membership.status === "pending") {
        toast.success(t("course.contextMenu.enrollPending"));
      } else {
        toast.success(t("course.contextMenu.enrollSuccess"));
      }
      refetch();
    } catch {
      toast.error(t("course.contextMenu.enrollError"));
    }
  };

  const handleLeaveClick = () => {
    if (!selectedCourse) return;
    setCourseToLeave(selectedCourse);
    setLeaveModalOpen(true);
    setContextMenuOpen(false);
  };

  const handleConfirmLeave = async () => {
    if (!courseToLeave) return;

    try {
      await leaveCourse(courseToLeave.id);
      toast.success(t("course.contextMenu.leaveSuccess"));
      refetch();
    } catch {
      toast.error(t("course.contextMenu.leaveError"));
    } finally {
      setLeaveModalOpen(false);
      setCourseToLeave(null);
    }
  };

  const contextMenuItems: ContextMenuItem[] = [
    {
      id: "view",
      label: t("course.contextMenu.view"),
      icon: <HiEye />,
      onClick: handleViewClick,
    },
    ...(currentView === "public"
      ? [
          {
            id: "enroll",
            label: t("course.contextMenu.enroll"),
            icon: <HiLogin />,
            onClick: handleEnrollClick,
          },
        ]
      : []),
    ...(currentView === "me"
      ? [
          {
            id: "separator" as const,
            separator: true as const,
          },
          {
            id: "leave",
            label: t("course.contextMenu.leave"),
            icon: <HiLogout />,
            onClick: handleLeaveClick,
            danger: true,
          },
        ]
      : []),
  ];

  const getSubjectName = (code: string | null) => {
    if (!code) return "-";
    return SUBJECTS[code] || code;
  };

  const getLanguageName = (code: string | null) => {
    if (!code) return "-";
    return LANGUAGES[code] || code;
  };

  const getVisibilityLabel = (visibility: CourseVisibility) => {
    return VISIBILITY_LABELS[visibility] || visibility;
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return t("course.list.notStarted");
    return new Date(dateString).toLocaleDateString();
  };

  const courseList = courses?.results || [];
  const totalPages = courses?.total_pages || 1;
  const totalCount = courses?.count || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl shadow-lg">
              <HiAcademicCap className="text-2xl text-white" />
            </div>
            <h1 className="text-4xl font-light text-gray-900 dark:text-white tracking-tight">
              {currentView === "me"
                ? t("course.list.myTitle")
                : t("course.list.publicTitle")}
            </h1>
            {/* Toggle Button */}
            <button
              onClick={() => {
                const newView = currentView === "me" ? "public" : "me";
                navigate(`/courses/${newView}`);
              }}
              className="ms-4 text-sm text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer inline-flex items-center gap-1.5 opacity-70 hover:opacity-100"
            >
              {currentView === "me" ? (
                <>
                  <HiGlobeAlt className="text-base" />
                  <span>{t("course.list.viewPublic")}</span>
                </>
              ) : (
                <>
                  <HiUser className="text-base" />
                  <span>{t("course.list.viewMine")}</span>
                </>
              )}
            </button>
          </div>
          <p className="text-lg text-gray-500 dark:text-gray-400 font-light ms-16">
            {currentView === "me"
              ? t("course.list.mySubtitle")
              : t("course.list.publicSubtitle")}
          </p>
        </div>

        {/* Actions Bar */}
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <button
            onClick={handleCreateClick}
            className="inline-flex items-center gap-2 px-6 py-2.5 border-2 border-gray-300 dark:border-gray-600 hover:border-green-500 dark:hover:border-green-400 text-gray-700 dark:text-gray-200 hover:text-green-600 dark:hover:text-green-400 rounded-lg font-medium transition-all duration-200 hover:bg-green-50/50 dark:hover:bg-green-900/10 cursor-pointer"
          >
            <HiPlus className="text-lg" />
            {t("course.list.createButton")}
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center gap-2 px-4 py-2.5 border-2 rounded-lg font-medium transition-all duration-200 cursor-pointer ${
              showFilters || hasActiveFilters
                ? "border-blue-500 dark:border-blue-400 text-blue-600 dark:text-blue-400 bg-blue-50/50 dark:bg-blue-900/10"
                : "border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:border-blue-500 dark:hover:border-blue-400"
            }`}
          >
            <HiFilter className="text-lg" />
            {hasActiveFilters && (
              <span className="w-2 h-2 bg-blue-500 rounded-full" />
            )}
          </button>
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="inline-flex items-center gap-1 px-3 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors cursor-pointer"
            >
              <HiX className="text-base" />
              {t("course.list.clearFilters")}
            </button>
          )}
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mb-6 bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-2xl p-4 sm:p-6 relative z-10">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <LazySelect
                label={t("course.list.filterSubject")}
                name="subject"
                value={filterSubject}
                onChange={handleFilterChange(setFilterSubject)}
                choiceType="subjects"
                placeholder={t("course.list.filterSubject")}
                searchable
              />
              <LazySelect
                label={t("course.list.filterLanguage")}
                name="language"
                value={filterLanguage}
                onChange={handleFilterChange(setFilterLanguage)}
                choiceType="languages"
                placeholder={t("course.list.filterLanguage")}
                searchable
              />
              <LazySelect
                label={t("course.list.filterCountry")}
                name="country"
                value={filterCountry}
                onChange={handleFilterChange(setFilterCountry)}
                choiceType="countries"
                placeholder={t("course.list.filterCountry")}
                searchable
              />
              {currentView === "me" && (
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {t("course.list.filterVisibility")}
                  </label>
                  <div className="relative" ref={visibilityDropdownRef}>
                    <button
                      type="button"
                      onClick={() =>
                        setVisibilityDropdownOpen(!visibilityDropdownOpen)
                      }
                      className="w-full px-4 py-3 pr-10 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400 transition-all duration-200 cursor-pointer hover:border-gray-400 dark:hover:border-gray-500 font-medium text-left"
                    >
                      <span
                        className={
                          filterVisibility
                            ? ""
                            : "text-gray-500 dark:text-gray-400"
                        }
                      >
                        {visibilityOptions.find(
                          (o) => o.value === filterVisibility,
                        )?.label || t("course.list.filterVisibility")}
                      </span>
                      <HiChevronDown
                        className={`absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 transition-transform duration-200 ${
                          visibilityDropdownOpen ? "rotate-180" : ""
                        }`}
                      />
                    </button>
                    {visibilityDropdownOpen && (
                      <div className="absolute z-50 mt-2 w-full">
                        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-600 overflow-hidden">
                          {visibilityOptions.map((option) => (
                            <button
                              key={option.value}
                              type="button"
                              onClick={() => {
                                setFilterVisibility(option.value);
                                setVisibilityDropdownOpen(false);
                              }}
                              className={`w-full px-4 py-3 text-left flex items-center justify-between transition-colors duration-150 text-gray-700 dark:text-gray-200 cursor-pointer ${
                                filterVisibility === option.value
                                  ? "bg-blue-500 text-white hover:bg-blue-600"
                                  : "hover:bg-gray-50 dark:hover:bg-gray-700/50"
                              }`}
                            >
                              <span className="font-medium">
                                {option.label}
                              </span>
                              {filterVisibility === option.value && (
                                <HiCheck className="text-white text-lg" />
                              )}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-2xl p-6 text-center mb-6">
            <p className="text-red-600 dark:text-red-400">
              {t("course.list.errorLoading")}
            </p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400 font-light">
              {t("course.list.loading")}
            </p>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && courseList.length === 0 && (
          <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 p-12 text-center">
            <div className="flex justify-center mb-6">
              <div className="p-6 bg-gray-100 dark:bg-gray-800 rounded-full">
                <HiAcademicCap className="text-6xl text-gray-400" />
              </div>
            </div>
            <h2 className="text-2xl font-light text-gray-900 dark:text-white mb-3">
              {t("course.list.emptyTitle")}
            </h2>
            <p className="text-gray-500 dark:text-gray-400 font-light mb-6">
              {currentView === "me"
                ? t("course.list.myEmptyMessage")
                : t("course.list.publicEmptyMessage")}
            </p>
            {currentView === "me" && (
              <button
                onClick={() => navigate("/courses/public")}
                className="inline-flex items-center gap-2 px-6 py-2.5 border-2 border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg font-medium transition-all duration-200 hover:bg-blue-50/50 dark:hover:bg-blue-900/10 cursor-pointer"
              >
                <HiGlobeAlt className="text-lg" />
                {t("course.list.viewPublic")}
              </button>
            )}
          </div>
        )}

        {/* Course List */}
        {!loading && !error && courseList.length > 0 && (
          <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 overflow-hidden">
            {/* Desktop Table */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200/50 dark:border-gray-700/30">
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("course.list.titleColumn")}
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("course.list.subjectColumn")}
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("course.list.languageColumn")}
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("course.list.visibilityColumn")}
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("course.list.membersColumn")}
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("course.list.startDateColumn")}
                    </th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {/* Actions column */}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {courseList.map((course, index) => (
                    <tr
                      key={course.id}
                      onClick={() => handleCourseClick(course)}
                      onContextMenu={(e) => handleContextMenu(e, course)}
                      className={`cursor-pointer transition-all duration-200 hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-purple-50/50 dark:hover:from-blue-900/20 dark:hover:to-purple-900/20 ${
                        !course.is_active ? "opacity-50" : ""
                      } ${
                        index !== courseList.length - 1
                          ? "border-b border-gray-200/30 dark:border-gray-700/20"
                          : ""
                      }`}
                    >
                      <td className="px-6 py-4">
                        <div className="flex flex-col">
                          <span className="font-medium text-gray-900 dark:text-white">
                            {course.title}
                          </span>
                          {course.outline && (
                            <span className="text-sm text-gray-500 dark:text-gray-400 line-clamp-1 mt-1">
                              {course.outline}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-700 dark:text-gray-300">
                        {getSubjectName(course.subject)}
                      </td>
                      <td className="px-6 py-4 text-gray-700 dark:text-gray-300">
                        {getLanguageName(course.language)}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-2 py-0.5 text-xs font-medium rounded-full border ${
                            course.visibility === "public"
                              ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 border-green-300 dark:border-green-700/50"
                              : course.visibility === "restricted"
                                ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700/50"
                                : "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 border-red-300 dark:border-red-700/50"
                          }`}
                        >
                          {getVisibilityLabel(course.visibility)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-700 dark:text-gray-300">
                        {t("course.list.memberCount", {
                          count: course.member_count,
                        })}
                      </td>
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400 text-sm">
                        {formatDate(course.start_date)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={(e) => handleDotsClick(e, course)}
                          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 cursor-pointer"
                          aria-label={t("course.contextMenu.actions")}
                        >
                          <HiDotsVertical className="text-xl text-gray-600 dark:text-gray-300" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile Card Layout */}
            <div className="md:hidden divide-y divide-gray-200/30 dark:divide-gray-700/20">
              {courseList.map((course) => (
                <div
                  key={course.id}
                  onClick={() => handleCourseClick(course)}
                  onContextMenu={(e) => handleContextMenu(e, course)}
                  className={`p-4 cursor-pointer transition-all duration-200 hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-purple-50/50 dark:hover:from-blue-900/20 dark:hover:to-purple-900/20 ${
                    !course.is_active ? "opacity-50" : ""
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 dark:text-white truncate">
                        {course.title}
                      </h3>
                      {course.outline && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mt-1">
                          {course.outline}
                        </p>
                      )}
                      <div className="flex flex-wrap items-center gap-2 mt-2">
                        <span
                          className={`px-2 py-0.5 text-xs font-medium rounded-full border ${
                            course.visibility === "public"
                              ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 border-green-300 dark:border-green-700/50"
                              : course.visibility === "restricted"
                                ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700/50"
                                : "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 border-red-300 dark:border-red-700/50"
                          }`}
                        >
                          {getVisibilityLabel(course.visibility)}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {getSubjectName(course.subject)}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {t("course.list.memberCount", {
                            count: course.member_count,
                          })}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleDotsClick(e, course)}
                      className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 cursor-pointer flex-shrink-0"
                      aria-label={t("course.contextMenu.actions")}
                    >
                      <HiDotsVertical className="text-xl text-gray-600 dark:text-gray-300" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200/50 dark:border-gray-700/30 flex items-center justify-between">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {t("course.list.showing", {
                    start: (currentPage - 1) * pageSize + 1,
                    end: Math.min(currentPage * pageSize, totalCount),
                    total: totalCount,
                  })}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                    aria-label="Previous page"
                  >
                    <HiChevronLeft className="text-xl text-gray-600 dark:text-gray-300" />
                  </button>
                  <span className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                    {t("course.list.pageOf", {
                      current: currentPage,
                      total: totalPages,
                    })}
                  </span>
                  <button
                    onClick={() =>
                      setCurrentPage((p) => Math.min(totalPages, p + 1))
                    }
                    disabled={currentPage === totalPages}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                    aria-label="Next page"
                  >
                    <HiChevronRight className="text-xl text-gray-600 dark:text-gray-300" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Context Menu */}
      <ContextMenu
        isOpen={contextMenuOpen}
        onClose={() => {
          setContextMenuOpen(false);
          setSelectedCourse(null);
        }}
        position={contextMenuPosition}
        items={contextMenuItems}
      />

      {/* Leave Confirmation Modal */}
      {courseToLeave && (
        <ConfirmationModal
          isOpen={leaveModalOpen}
          onClose={() => {
            setLeaveModalOpen(false);
            setCourseToLeave(null);
          }}
          onConfirm={handleConfirmLeave}
          title={t("course.contextMenu.leaveConfirmTitle")}
          message={t("course.contextMenu.leaveConfirmMessage", {
            title: courseToLeave.title,
          })}
          confirmText={t("course.contextMenu.leaveConfirmButton")}
          cancelText={t("common.cancel")}
          confirmButtonClass="bg-red-600 hover:bg-red-700 text-white"
        />
      )}
    </div>
  );
};

export default CourseListPage;
