import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate, useBlocker, Link } from "react-router-dom";
import toast from "react-hot-toast";
import {
  HiPlay,
  HiPencil,
  HiTrash,
  HiArrowLeft,
  HiCalendar,
  HiUser,
  HiGlobeAlt,
  HiEye,
  HiEyeSlash,
  HiLockClosed,
  HiBookOpen,
  HiLanguage,
  HiRectangleStack,
} from "react-icons/hi2";
import { FaSave } from "react-icons/fa";
import { getSlideshowDetail, updateSlideshow } from "../services/slideshowApi";
import type { SlideshowDetail } from "../types/slideshow.types";
import { useUnsavedChanges, useFormDirtyState } from "../hooks/useUnsavedChanges";
import UnsavedChangesModal from "../components/common/UnsavedChangesModal";
import LazySelect from "../components/common/LazySelect";

// Subject name mappings (same as in SlideshowListPage)
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

interface FormData {
  title: string;
  description: string;
  visibility: string;
  subject: string;
  language: string;
}

const SlideshowDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [slideshow, setSlideshow] = useState<SlideshowDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [visibilityMenuOpen, setVisibilityMenuOpen] = useState(false);
  const [showNavigationModal, setShowNavigationModal] = useState(false);
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set());

  // Form data tracking for unsaved changes
  const [originalFormData, setOriginalFormData] = useState<FormData | null>(null);
  const [formData, setFormData] = useState<FormData>({
    title: "",
    description: "",
    visibility: "private",
    subject: "",
    language: "",
  });

  // Refs
  const blockerRef = useRef<any>(null);

  // Track form dirty state
  const isDirty = useFormDirtyState(formData, originalFormData);

  // Add browser warning for unsaved changes
  useUnsavedChanges(isDirty, "You have unsaved changes that will be lost.");

  // Block navigation when there are unsaved changes
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && currentLocation.pathname !== nextLocation.pathname
  );

  // Store blocker reference for modal callbacks
  blockerRef.current = blocker;

  // Handle blocked navigation with custom modal
  useEffect(() => {
    if (blocker.state === 'blocked') {
      setShowNavigationModal(true);
    }
  }, [blocker]);

  // Modal callbacks for navigation
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

  useEffect(() => {
    if (!id || isNaN(Number(id))) {
      toast.error("Invalid slideshow ID");
      navigate("/slideshows", { replace: true });
      return;
    }

    const fetchSlideshow = async () => {
      setLoading(true);
      try {
        const data = await getSlideshowDetail(Number(id));
        setSlideshow(data);

        // Initialize form data with loaded slideshow
        const initialFormData = {
          title: data.title,
          description: data.description || "",
          visibility: data.visibility,
          subject: data.subject || "",
          language: data.language || "",
        };
        setFormData(initialFormData);
        setOriginalFormData(initialFormData);
      } catch (error) {
        console.error("Failed to fetch slideshow:", error);
        toast.error("Failed to load slideshow");
        navigate("/slideshows", { replace: true });
      } finally {
        setLoading(false);
      }
    };

    fetchSlideshow();
  }, [id, navigate]);

  const handlePresent = () => {
    if (!slideshow) return;
    if (slideshow.slide_count === 0) {
      toast.error("This slideshow has no slides yet", {
        icon: "🚧",
      });
      return;
    }
    navigate(`/slideshows/${id}/present`);
  };

  const handleEdit = () => {
    toast("Editor coming soon!", {
      icon: "🚧",
      duration: 3000,
    });
  };

  const handleDelete = () => {
    toast("Delete functionality coming soon!", {
      icon: "🚧",
      duration: 3000,
    });
  };

  // Handle field blur to track touched fields
  const handleBlur = (field: keyof FormData) => {
    setTouchedFields(prev => new Set(prev).add(field));
  };

  // Handle form field changes
  const handleFieldChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Handle visibility change (marks as dirty, doesn't auto-save)
  const handleVisibilityChange = (newVisibility: string) => {
    handleFieldChange("visibility", newVisibility);
    setVisibilityMenuOpen(false);
  };

  // Handle form submission (Save Changes)
  const handleSaveChanges = async () => {
    if (!slideshow) return;

    setSaving(true);
    try {
      const updatedSlideshow = await updateSlideshow(slideshow.id, {
        title: formData.title,
        description: formData.description || null,
        visibility: formData.visibility as any,
        subject: formData.subject || null,
        language: formData.language || null,
        version: slideshow.version,
      });

      setSlideshow(updatedSlideshow);

      // Reset original form data to match saved data
      const newOriginalData = {
        title: updatedSlideshow.title,
        description: updatedSlideshow.description || "",
        visibility: updatedSlideshow.visibility,
        subject: updatedSlideshow.subject || "",
        language: updatedSlideshow.language || "",
      };
      setFormData(newOriginalData);
      setOriginalFormData(newOriginalData);

      // Clear touched fields after successful save
      setTouchedFields(new Set());

      toast.success("Slideshow updated successfully!");
    } catch (error: any) {
      console.error("Failed to update slideshow:", error);
      toast.error(error.message || "Failed to update slideshow");
    } finally {
      setSaving(false);
    }
  };

  const getSubjectName = (code: string | null) => {
    if (!code) return null;
    return SUBJECTS[code] || code;
  };

  const getLanguageName = (code: string | null) => {
    if (!code) return null;
    return LANGUAGES[code] || code;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const getVisibilityIcon = (visibility: string) => {
    switch (visibility) {
      case "public":
        return <HiGlobeAlt className="w-5 h-5" />;
      case "unlisted":
        return <HiEyeSlash className="w-5 h-5" />;
      case "private":
        return <HiLockClosed className="w-5 h-5" />;
      default:
        return <HiEye className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!slideshow) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <Link
          to="/slideshows"
          className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors mb-6"
        >
          <HiArrowLeft className="w-5 h-5" />
          <span>Back to Slideshows</span>
        </Link>

        {/* Main Card */}
        <div className="bg-white/80 dark:bg-gray-800/40 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/30 rounded-3xl shadow-2xl shadow-gray-200/20 dark:shadow-gray-900/20 overflow-hidden">
          {/* Header - Editable Title and Description */}
          <div className="p-8 border-b border-gray-200/50 dark:border-gray-700/30">
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleFieldChange("title", e.target.value)}
              onBlur={() => handleBlur("title")}
              className={`text-4xl font-light text-gray-900 dark:text-white mb-4 bg-transparent border-b-2 ${
                touchedFields.has('title') && formData.title !== originalFormData?.title
                  ? 'border-red-300 dark:border-red-500/50'
                  : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600'
              } focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none w-full transition-colors cursor-text`}
              placeholder="Slideshow Title"
            />
            <textarea
              value={formData.description}
              onChange={(e) => handleFieldChange("description", e.target.value)}
              onBlur={() => handleBlur("description")}
              className={`text-lg text-gray-600 dark:text-gray-400 leading-relaxed bg-transparent border ${
                touchedFields.has('description') && formData.description !== originalFormData?.description
                  ? 'border-red-300 dark:border-red-500/50'
                  : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600'
              } focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none w-full rounded-lg p-2 min-h-[60px] resize-y transition-colors cursor-text`}
              placeholder="Add a description..."
            />
          </div>

          {/* Metadata */}
          <div className="p-8 border-b border-gray-200/50 dark:border-gray-700/30">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Author */}
              <div className="flex items-center gap-3">
                <HiUser className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Created by
                  </div>
                  <Link
                    to={`/profile/${slideshow.created_by_username}`}
                    className="font-medium text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                  >
                    {slideshow.created_by_username}
                  </Link>
                </div>
              </div>

              {/* Subject - Searchable Dropdown */}
              <div className="col-span-1 md:col-span-2">
                <LazySelect
                  label="Subject"
                  name="subject"
                  value={formData.subject}
                  onChange={(e) => handleFieldChange("subject", e.target.value)}
                  onBlur={() => handleBlur("subject")}
                  placeholder="Select a subject..."
                  choiceType="subjects"
                  searchable={true}
                  className={
                    touchedFields.has('subject') && formData.subject !== originalFormData?.subject
                      ? 'border-red-300 dark:border-red-500/50'
                      : ''
                  }
                />
              </div>

              {/* Language - Searchable Dropdown */}
              <div className="col-span-1 md:col-span-2">
                <LazySelect
                  label="Language"
                  name="language"
                  value={formData.language}
                  onChange={(e) => handleFieldChange("language", e.target.value)}
                  onBlur={() => handleBlur("language")}
                  placeholder="Select a language..."
                  choiceType="languages"
                  searchable={true}
                  className={
                    touchedFields.has('language') && formData.language !== originalFormData?.language
                      ? 'border-red-300 dark:border-red-500/50'
                      : ''
                  }
                />
              </div>

              {/* Visibility */}
              <div className="flex items-center gap-3 relative">
                <div className="text-gray-400">
                  {getVisibilityIcon(formData.visibility)}
                </div>
                <div className="flex-1">
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Visibility
                  </div>
                  <button
                    onClick={() => setVisibilityMenuOpen(!visibilityMenuOpen)}
                    onBlur={() => handleBlur("visibility")}
                    className={`font-medium capitalize hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer flex items-center gap-1 px-2 py-1 -mx-2 -my-1 rounded border-2 ${
                      touchedFields.has('visibility') && formData.visibility !== originalFormData?.visibility
                        ? 'border-red-300 dark:border-red-500/50 text-gray-900 dark:text-white'
                        : 'border-transparent text-gray-900 dark:text-white'
                    }`}
                  >
                    {formData.visibility}
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {/* Dropdown Menu */}
                  {visibilityMenuOpen && (
                    <>
                      <div
                        className="fixed inset-0 z-10"
                        onClick={() => setVisibilityMenuOpen(false)}
                      />
                      <div className="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-20 min-w-[160px]">
                        <button
                          onClick={() => handleVisibilityChange('public')}
                          className="w-full px-4 py-2 text-left text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors cursor-pointer"
                        >
                          <HiGlobeAlt className="w-4 h-4" />
                          <span>Public</span>
                        </button>
                        <button
                          onClick={() => handleVisibilityChange('unlisted')}
                          className="w-full px-4 py-2 text-left text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors cursor-pointer"
                        >
                          <HiEyeSlash className="w-4 h-4" />
                          <span>Unlisted</span>
                        </button>
                        <button
                          onClick={() => handleVisibilityChange('private')}
                          className="w-full px-4 py-2 text-left text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors cursor-pointer rounded-b-lg"
                        >
                          <HiLockClosed className="w-4 h-4" />
                          <span>Private</span>
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Slide Count */}
              <div className="flex items-center gap-3">
                <HiRectangleStack className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Slides
                  </div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {slideshow.slide_count} {slideshow.slide_count === 1 ? 'slide' : 'slides'}
                  </div>
                </div>
              </div>

              {/* Created Date */}
              <div className="flex items-center gap-3">
                <HiCalendar className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Created
                  </div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {formatDate(slideshow.created_at)}
                  </div>
                </div>
              </div>

              {/* Updated Date */}
              <div className="flex items-center gap-3">
                <HiCalendar className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Last updated
                  </div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {formatDate(slideshow.updated_at)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Save Changes Banner - Shows when there are unsaved changes */}
          {isDirty && (
            <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></div>
                  <p className="text-amber-800 dark:text-amber-200 font-medium">
                    You have unsaved changes
                  </p>
                </div>
                <button
                  onClick={handleSaveChanges}
                  disabled={saving}
                  className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <FaSave className="w-4 h-4" />
                      <span>Save Changes</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="p-8 bg-gray-50/50 dark:bg-gray-900/20">
            <div className="flex flex-wrap gap-4">
              <button
                onClick={handlePresent}
                disabled={slideshow.slide_count === 0}
                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
              >
                <HiPlay className="w-5 h-5" />
                Present
              </button>

              <button
                onClick={handleEdit}
                className="inline-flex items-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg font-medium transition-all duration-200 cursor-pointer"
              >
                <HiPencil className="w-5 h-5" />
                Edit
              </button>

              <button
                onClick={handleDelete}
                className="inline-flex items-center gap-2 px-6 py-3 border-2 border-gray-300 dark:border-gray-600 hover:border-red-500 dark:hover:border-red-400 text-gray-700 dark:text-gray-200 hover:text-red-600 dark:hover:text-red-400 rounded-lg font-medium transition-all duration-200 cursor-pointer"
              >
                <HiTrash className="w-5 h-5" />
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Unsaved Changes Modal */}
      <UnsavedChangesModal
        isOpen={showNavigationModal}
        onConfirm={handleConfirmNavigation}
        onCancel={handleCancelNavigation}
        message="You have unsaved changes. Are you sure you want to leave?"
      />
    </div>
  );
};

export default SlideshowDetailPage;
