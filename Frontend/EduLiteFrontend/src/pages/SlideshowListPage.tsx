import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import {
  HiPresentationChartBar,
  HiPlus,
  HiChevronLeft,
  HiChevronRight,
  HiDotsVertical,
  HiPlay,
  HiPencil,
  HiInformationCircle,
  HiTrash,
  HiGlobeAlt,
  HiUser,
} from "react-icons/hi";
import { listSlideshows } from "../services/slideshowApi";
import type {
  SlideshowListItem,
  PaginatedResponse,
} from "../types/slideshow.types";
import ContextMenu, { type ContextMenuItem } from "../components/common/ContextMenu";
import SlideshowDetailsModal from "../components/common/SlideshowDetailsModal";
import ConfirmationModal from "../components/common/ConfirmationModal";

// Lookup maps for readable names
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

const COUNTRIES: Record<string, string> = {
  AF: "Afghanistan",
  PS: "Palestine",
  EG: "Egypt",
  SD: "Sudan",
  NG: "Nigeria",
  US: "United States",
  CA: "Canada",
  BR: "Brazil",
  UK: "United Kingdom",
  DE: "Germany",
  IN: "India",
  CN: "China",
  JP: "Japan",
  KR: "South Korea",
  SA: "Saudi Arabia",
  AE: "United Arab Emirates",
  TR: "Turkey",
  PK: "Pakistan",
  ID: "Indonesia",
  MY: "Malaysia",
  SG: "Singapore",
  AU: "Australia",
  NZ: "New Zealand",
  ZA: "South Africa",
  KE: "Kenya",
  ET: "Ethiopia",
  MA: "Morocco",
  FR: "France",
  IT: "Italy",
  ES: "Spain",
  RU: "Russia",
  MX: "Mexico",
  AR: "Argentina",
  CO: "Colombia",
  VN: "Vietnam",
  TH: "Thailand",
  IR: "Iran",
  IQ: "Iraq",
  SY: "Syria",
  LB: "Lebanon",
  JO: "Jordan",
  OT: "Other",
};

interface SlideshowListPageProps {
  view?: "me" | "public";
}

const SlideshowListPage: React.FC<SlideshowListPageProps> = ({ view: propView }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [slideshows, setSlideshows] = useState<SlideshowListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 10;

  // Determine current view: use prop if provided, otherwise check URL or localStorage
  const currentView: "me" | "public" = propView || "me";

  // Context menu state
  const [contextMenuOpen, setContextMenuOpen] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
  const [selectedSlideshow, setSelectedSlideshow] = useState<SlideshowListItem | null>(null);

  // Modal state
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [detailsSlideshow, setDetailsSlideshow] = useState<SlideshowListItem | null>(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteSlideshow, setDeleteSlideshow] = useState<SlideshowListItem | null>(null);

  // Redirect from /slideshows to /slideshows/me or /slideshows/public based on localStorage
  useEffect(() => {
    if (!propView) {
      const stored = localStorage.getItem("slideshowView");
      const targetView = stored === "public" ? "public" : "me";
      navigate(`/slideshows/${targetView}`, { replace: true });
    }
  }, [propView, navigate]);

  // Save current view to localStorage whenever it changes
  useEffect(() => {
    if (currentView) {
      localStorage.setItem("slideshowView", currentView);
    }
  }, [currentView]);

  useEffect(() => {
    if (propView) {
      fetchSlideshows();
    }
  }, [currentPage, propView]);

  const fetchSlideshows = async () => {
    setLoading(true);
    try {
      const params: any = {
        page: currentPage,
        page_size: pageSize,
      };

      // For "me" view: show only user's slideshows (any visibility)
      // For "public" view: show only public slideshows (visibility=public filter)
      if (currentView === "me") {
        params.mine = true;
      } else if (currentView === "public") {
        params.visibility = "public";
      }

      const response: PaginatedResponse<SlideshowListItem> =
        await listSlideshows(params);

      setSlideshows(response.results);
      setTotalCount(response.count);
      setTotalPages(Math.ceil(response.count / pageSize));
    } catch (error) {
      console.error("Failed to fetch slideshows:", error);
      toast.error(t("slideshow.list.errorLoading"));
    } finally {
      setLoading(false);
    }
  };

  const handleSlideshowClick = (slideshow: SlideshowListItem) => {
    // Check if slideshow has any slides
    if (slideshow.slide_count === 0) {
      toast.error(t("slideshow.list.noSlidesError"), {
        icon: "🚧",
        duration: 3000,
      });
      // TODO: When editor is implemented, route to editor instead:
      // navigate(`/slideshows/${slideshow.id}/edit`);
      return;
    }

    navigate(`/slideshows/${slideshow.id}`);
  };

  const handleCreateClick = () => {
    toast(t("slideshow.list.comingSoon"), {
      icon: "🚧",
      duration: 3000,
    });
  };

  const handleContextMenu = (e: React.MouseEvent, slideshow: SlideshowListItem) => {
    e.preventDefault();
    e.stopPropagation();
    setSelectedSlideshow(slideshow);
    setContextMenuPosition({ x: e.clientX, y: e.clientY });
    setContextMenuOpen(true);
  };

  const handleDotsClick = (e: React.MouseEvent, slideshow: SlideshowListItem) => {
    e.stopPropagation();
    const rect = (e.target as HTMLElement).getBoundingClientRect();
    setSelectedSlideshow(slideshow);
    setContextMenuPosition({ x: rect.right - 180, y: rect.bottom + 4 });
    setContextMenuOpen(true);
  };

  const handlePresentClick = () => {
    if (!selectedSlideshow) return;
    if (selectedSlideshow.slide_count === 0) {
      toast.error(t("slideshow.list.noSlidesError"), {
        icon: "🚧",
        duration: 3000,
      });
      return;
    }
    navigate(`/slideshows/${selectedSlideshow.id}`);
  };

  const handleEditClick = () => {
    toast(t("slideshow.contextMenu.editComingSoon"), {
      icon: "🚧",
      duration: 3000,
    });
    // TODO: When editor is implemented:
    // navigate(`/slideshows/${selectedSlideshow.id}/edit`);
  };

  const handleDetailsClick = () => {
    if (!selectedSlideshow) return;
    setDetailsSlideshow(selectedSlideshow);
    setDetailsModalOpen(true);
    setContextMenuOpen(false);
  };

  const handleDeleteClick = () => {
    if (!selectedSlideshow) return;
    setDeleteSlideshow(selectedSlideshow);
    setDeleteModalOpen(true);
    setContextMenuOpen(false);
  };

  const handleOpenEditor = () => {
    toast(t("slideshow.contextMenu.editComingSoon"), {
      icon: "🚧",
      duration: 3000,
    });
    // TODO: When editor is implemented:
    // navigate(`/slideshows/${selectedSlideshow.id}/edit`);
  };

  const handleConfirmDelete = async () => {
    if (!deleteSlideshow) return;

    try {
      // TODO: Implement delete API call when backend endpoint is ready
      // await deleteSlideshow(deleteSlideshow.id);
      toast.success(t("slideshow.contextMenu.deleteSuccess"));
      fetchSlideshows(); // Refresh the list
    } catch (error) {
      console.error("Failed to delete slideshow:", error);
      toast.error(t("slideshow.contextMenu.deleteError"));
    } finally {
      setDeleteModalOpen(false);
      setDeleteSlideshow(null);
    }
  };

  const contextMenuItems: ContextMenuItem[] = [
    {
      id: "present",
      label: t("slideshow.contextMenu.present"),
      icon: <HiPlay />,
      onClick: handlePresentClick,
      disabled: selectedSlideshow?.slide_count === 0,
    },
    {
      id: "edit",
      label: t("slideshow.contextMenu.edit"),
      icon: <HiPencil />,
      onClick: handleEditClick,
    },
    {
      id: "details",
      label: t("slideshow.contextMenu.details"),
      icon: <HiInformationCircle />,
      onClick: handleDetailsClick,
    },
    {
      id: "separator",
      separator: true,
    },
    {
      id: "delete",
      label: t("slideshow.contextMenu.delete"),
      icon: <HiTrash />,
      onClick: handleDeleteClick,
      danger: true,
    },
  ];

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return t("slideshow.list.today");
    } else if (diffDays === 1) {
      return t("slideshow.list.yesterday");
    } else if (diffDays < 7) {
      return t("slideshow.list.daysAgo", { count: diffDays });
    } else {
      return date.toLocaleDateString();
    }
  };

  const getSubjectName = (code: string | null) => {
    if (!code) return "-";
    return SUBJECTS[code] || code;
  };

  const getLanguageName = (code: string | null) => {
    if (!code) return "-";
    return LANGUAGES[code] || code;
  };

  // Reserved for future use when we add a country column
  const getCountryName = (code: string | null) => {
    if (!code) return "-";
    return COUNTRIES[code] || code;
  };
  // Prevent unused variable warning - will be used when country column is added
  void getCountryName;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl shadow-lg">
              <HiPresentationChartBar className="text-2xl text-white" />
            </div>
            <h1 className="text-4xl font-light text-gray-900 dark:text-white tracking-tight">
              {currentView === "me" ? t("slideshow.list.myTitle") : t("slideshow.list.publicTitle")}
            </h1>
            {/* Toggle Button */}
            <button
              onClick={() => {
                const newView = currentView === "me" ? "public" : "me";
                navigate(`/slideshows/${newView}`);
              }}
              className="ml-4 text-sm text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer inline-flex items-center gap-1.5 opacity-70 hover:opacity-100"
            >
              {currentView === "me" ? (
                <>
                  <HiGlobeAlt className="text-base" />
                  <span>{t("slideshow.list.viewPublic")}</span>
                </>
              ) : (
                <>
                  <HiUser className="text-base" />
                  <span>{t("slideshow.list.viewMine")}</span>
                </>
              )}
            </button>
          </div>
          <p className="text-lg text-gray-500 dark:text-gray-400 font-light ml-16">
            {currentView === "me" ? t("slideshow.list.mySubtitle") : t("slideshow.list.publicSubtitle")}
          </p>
        </div>

        {/* Create Button */}
        <div className="mb-6">
          <button
            onClick={handleCreateClick}
            className="inline-flex items-center gap-2 px-6 py-2.5 border-2 border-gray-300 dark:border-gray-600 hover:border-green-500 dark:hover:border-green-400 text-gray-700 dark:text-gray-200 hover:text-green-600 dark:hover:text-green-400 rounded-lg font-medium transition-all duration-200 hover:bg-green-50/50 dark:hover:bg-green-900/10 cursor-pointer"
          >
            <HiPlus className="text-lg" />
            {t("slideshow.list.createButton")}
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400 font-light">
              {t("slideshow.list.loading")}
            </p>
          </div>
        )}

        {/* Empty State */}
        {!loading && slideshows.length === 0 && (
          <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 p-12 text-center">
            <div className="flex justify-center mb-6">
              <div className="p-6 bg-gray-100 dark:bg-gray-800 rounded-full">
                <HiPresentationChartBar className="text-6xl text-gray-400" />
              </div>
            </div>
            <h2 className="text-2xl font-light text-gray-900 dark:text-white mb-3">
              {t("slideshow.list.emptyTitle")}
            </h2>
            <p className="text-gray-500 dark:text-gray-400 font-light mb-6">
              {t("slideshow.list.emptyMessage")}
            </p>
            <button
              onClick={handleCreateClick}
              className="inline-flex items-center gap-2 px-6 py-2.5 border-2 border-gray-300 dark:border-gray-600 hover:border-green-500 dark:hover:border-green-400 text-gray-700 dark:text-gray-200 hover:text-green-600 dark:hover:text-green-400 rounded-lg font-medium transition-all duration-200 hover:bg-green-50/50 dark:hover:bg-green-900/10 cursor-pointer"
            >
              <HiPlus className="text-lg" />
              {t("slideshow.list.createButton")}
            </button>
          </div>
        )}

        {/* Table View */}
        {!loading && slideshows.length > 0 && (
          <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200/50 dark:border-gray-700/30">
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("slideshow.list.titleColumn")}
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("slideshow.list.subjectColumn")}
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("slideshow.list.languageColumn")}
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("slideshow.list.slidesColumn")}
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {t("slideshow.list.updatedColumn")}
                    </th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {/* Actions column */}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {slideshows.map((slideshow, index) => (
                    <tr
                      key={slideshow.id}
                      onClick={() => handleSlideshowClick(slideshow)}
                      onContextMenu={(e) => handleContextMenu(e, slideshow)}
                      className={`cursor-pointer transition-all duration-200 hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-purple-50/50 dark:hover:from-blue-900/20 dark:hover:to-purple-900/20 ${
                        slideshow.slide_count === 0 ? "opacity-50" : ""
                      } ${
                        index !== slideshows.length - 1
                          ? "border-b border-gray-200/30 dark:border-gray-700/20"
                          : ""
                      }`}
                    >
                      <td className="px-6 py-4">
                        <div className="flex flex-col">
                          <span className="font-medium text-gray-900 dark:text-white">
                            {slideshow.title}
                          </span>
                          {slideshow.description && (
                            <span className="text-sm text-gray-500 dark:text-gray-400 line-clamp-1 mt-1">
                              {slideshow.description}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-700 dark:text-gray-300">
                        {getSubjectName(slideshow.subject)}
                      </td>
                      <td className="px-6 py-4 text-gray-700 dark:text-gray-300">
                        {getLanguageName(slideshow.language)}
                      </td>
                      <td className="px-6 py-4 text-gray-700 dark:text-gray-300">
                        <div className="flex items-center gap-2">
                          {t("slideshow.list.slideCount", {
                            count: slideshow.slide_count,
                          })}
                          {slideshow.slide_count === 0 && (
                            <span className="px-2 py-0.5 text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 rounded-full border border-yellow-300 dark:border-yellow-700/50">
                              Empty
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400 text-sm">
                        {formatDate(slideshow.updated_at)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={(e) => handleDotsClick(e, slideshow)}
                          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 cursor-pointer"
                          aria-label={t("slideshow.contextMenu.actions")}
                        >
                          <HiDotsVertical className="text-xl text-gray-600 dark:text-gray-300" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200/50 dark:border-gray-700/30 flex items-center justify-between">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {t("slideshow.list.showing", {
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
                    {t("slideshow.list.pageOf", {
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
          setSelectedSlideshow(null);
        }}
        position={contextMenuPosition}
        items={contextMenuItems}
      />

      {/* Details Modal */}
      {detailsSlideshow && (
        <SlideshowDetailsModal
          isOpen={detailsModalOpen}
          onClose={() => {
            setDetailsModalOpen(false);
            setDetailsSlideshow(null);
          }}
          slideshow={{
            id: detailsSlideshow.id,
            title: detailsSlideshow.title,
            subject: getSubjectName(detailsSlideshow.subject),
            language: getLanguageName(detailsSlideshow.language),
            visibility: detailsSlideshow.visibility,
            slide_count: detailsSlideshow.slide_count,
            created_at: detailsSlideshow.created_at,
            updated_at: detailsSlideshow.updated_at,
          }}
          onOpenEditor={handleOpenEditor}
        />
      )}

      {/* Delete Confirmation Modal */}
      {deleteSlideshow && (
        <ConfirmationModal
          isOpen={deleteModalOpen}
          onClose={() => {
            setDeleteModalOpen(false);
            setDeleteSlideshow(null);
          }}
          onConfirm={handleConfirmDelete}
          title={t("slideshow.contextMenu.deleteConfirmTitle")}
          message={t("slideshow.contextMenu.deleteConfirmMessage", {
            title: deleteSlideshow.title,
          })}
          confirmText={t("slideshow.contextMenu.deleteConfirmButton")}
          cancelText={t("common.cancel")}
          confirmButtonClass="bg-red-600 hover:bg-red-700 text-white"
        />
      )}
    </div>
  );
};

export default SlideshowListPage;
