import React, { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import {
  HiXMark,
  HiArrowLeft,
  HiArrowRight,
  HiArrowsPointingOut,
  HiArrowsPointingIn,
  HiPencil,
} from "react-icons/hi2";
import { HiCog, HiQuestionMarkCircle } from "react-icons/hi";
import type { Slide, SlideViewOnly } from "../../types/slideshow.types";
import type { SlideshowViewerProps } from "./types";
import SlideDisplay from "./SlideDisplay";
import SlideProgress from "./SlideProgress";
import PresentationSettingsModal from "./PresentationSettingsModal";
import PresentationHelpModal from "./PresentationHelpModal";

// Hooks
import { useSlideNavigation } from "../../hooks/useSlideNavigation";
import { useSlideLoader } from "../../hooks/useSlideLoader";
import { usePresentationMode } from "../../hooks/usePresentationMode";
import { useKeyboardNavigation } from "../../hooks/useKeyboardNavigation";

// Subject name mappings
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

/**
 * Get readable subject name from code
 */
const getSubjectName = (code: string | null): string | null => {
  if (!code) return null;
  return SUBJECTS[code] || code;
};

/**
 * SlideshowViewer Component
 *
 * Main presentation viewer with:
 * - Progressive loading (first 3 slides immediate, rest in background)
 * - Keyboard navigation (arrows, space, escape)
 * - Fullscreen support (optional)
 * - Offline capability (loads ALL slides, works without network)
 */
const SlideshowViewer: React.FC<SlideshowViewerProps> = ({
  slideshowId,
  initialSlide = 0,
  onExit,
  allowFullscreen = false,
}) => {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);

  // UI State (kept in component as they're simple toggles)
  const [settingsOpen, setSettingsOpen] = useState<boolean>(false);
  const [helpOpen, setHelpOpen] = useState<boolean>(false);

  // Custom hooks
  const { slides, slideCount, isLoading, error, metadata, getLoadedSlides } =
    useSlideLoader(slideshowId);

  const navigation = useSlideNavigation({
    slideCount,
    initialSlide,
  });

  const presentation = usePresentationMode({
    containerRef,
    settingsOpen,
    helpOpen,
  });

  // Handle fullscreen toggle with error toast
  const handleToggleFullscreen = useCallback(async () => {
    try {
      await presentation.toggleFullscreen();
    } catch {
      toast.error("Failed to toggle fullscreen");
    }
  }, [presentation]);

  // Keyboard navigation
  useKeyboardNavigation({
    onNext: navigation.next,
    onPrev: navigation.prev,
    onGoToSlide: navigation.goToSlide,
    onToggleFullscreen: handleToggleFullscreen,
    onExit,
    slideCount,
    allowFullscreen,
  });

  // Navigation handler for edit
  const handleEdit = useCallback(() => {
    navigate(`/slideshows/${slideshowId}/edit`);
  }, [slideshowId, navigate]);

  // Get current slide data
  const currentSlide: Slide | SlideViewOnly | null =
    slides.get(navigation.currentIndex) || null;
  const isCurrentSlideLoading = !slides.has(navigation.currentIndex);

  // Derived values
  const subjectName = getSubjectName(metadata.subject);
  const loadedSlides = getLoadedSlides();

  /**
   * Error state
   */
  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-red-900/20 border border-red-500/50 rounded-2xl p-8 max-w-md text-center">
          <h2 className="text-2xl font-light text-red-400 mb-4">
            Error Loading Slideshow
          </h2>
          <p className="text-gray-300 mb-6">{error}</p>
          {onExit && (
            <button
              onClick={onExit}
              className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors cursor-pointer"
            >
              Go Back
            </button>
          )}
        </div>
      </div>
    );
  }

  /**
   * Loading state
   */
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto mb-6"></div>
          <p className="text-xl text-gray-300 font-light">
            Loading presentation...
          </p>
        </div>
      </div>
    );
  }

  /**
   * Main viewer UI
   */
  return (
    <div
      ref={containerRef}
      className="min-h-screen bg-white dark:bg-black flex flex-col"
    >
      {/* Header / Controls */}
      <div
        className={`fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-white/90 dark:bg-black/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700/30 transition-transform duration-300 ${
          presentation.shouldShowTopBar ? "translate-y-0" : "-translate-y-full"
        }`}
      >
        {/* Title, Author, and Subject */}
        <div className="flex flex-col max-w-md">
          <a
            href={`/slideshows/${slideshowId}`}
            className="text-xl font-light text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors truncate cursor-pointer"
            onClick={(e) => {
              e.preventDefault();
              if (onExit) {
                onExit();
              } else {
                window.location.href = `/slideshows/${slideshowId}`;
              }
            }}
          >
            {metadata.title}
          </a>
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            {metadata.author && (
              <a
                href={`/profile/${metadata.author}`}
                className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer"
                onClick={(e) => {
                  e.preventDefault();
                  window.location.href = `/profile/${metadata.author}`;
                }}
              >
                by {metadata.author}
              </a>
            )}
            {subjectName && metadata.subject && (
              <>
                {metadata.author && <span>•</span>}
                <a
                  href={`/slideshows/public?subject=${metadata.subject}`}
                  className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer"
                  onClick={(e) => {
                    e.preventDefault();
                    window.location.href = `/slideshows/public?subject=${metadata.subject}`;
                  }}
                >
                  {subjectName}
                </a>
              </>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Edit Button */}
          <button
            onClick={handleEdit}
            className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-blue-500 dark:hover:bg-blue-600 text-gray-700 dark:text-gray-300 hover:text-white transition-colors cursor-pointer"
            aria-label="Edit slideshow"
            title="Edit slideshow"
          >
            <HiPencil className="w-5 h-5" />
          </button>

          {/* Settings Button */}
          <button
            onClick={() => setSettingsOpen(true)}
            className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer"
            aria-label="Settings"
            title="Settings"
          >
            <HiCog className="w-5 h-5" />
          </button>

          {/* Help Button */}
          <button
            onClick={() => setHelpOpen(true)}
            className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer"
            aria-label="Help"
            title="Help"
          >
            <HiQuestionMarkCircle className="w-5 h-5" />
          </button>

          {/* Fullscreen Toggle */}
          {allowFullscreen && (
            <button
              onClick={handleToggleFullscreen}
              className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer"
              aria-label={
                presentation.isFullscreen
                  ? "Exit fullscreen"
                  : "Enter fullscreen"
              }
              title={
                presentation.isFullscreen
                  ? "Exit fullscreen (F)"
                  : "Enter fullscreen (F)"
              }
            >
              {presentation.isFullscreen ? (
                <HiArrowsPointingIn className="w-5 h-5" />
              ) : (
                <HiArrowsPointingOut className="w-5 h-5" />
              )}
            </button>
          )}

          {/* Exit Button */}
          {onExit && (
            <button
              onClick={onExit}
              className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-red-600 dark:hover:bg-red-700 text-gray-700 dark:text-gray-300 hover:text-white transition-colors cursor-pointer"
              aria-label="Exit presentation"
              title="Exit (Esc)"
            >
              <HiXMark className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div
        className="flex-1 flex items-center justify-center overflow-hidden relative transition-all duration-300"
        style={{
          marginTop: !presentation.autoHideTopBar ? "5rem" : "0",
          marginBottom: !presentation.autoHideBottomBar
            ? "calc(3.5rem - 8px)"
            : "0",
        }}
      >
        <div className="w-full h-full">
          {/* Slide Display */}
          <SlideDisplay
            slide={currentSlide}
            isLoading={isCurrentSlideLoading}
            slideNumber={navigation.currentIndex + 1}
            totalSlides={slideCount}
          />
        </div>

        {/* Navigation Arrows (always visible on desktop) */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 hidden md:block pointer-events-none z-10">
          <button
            onClick={navigation.prev}
            onWheel={(e) => {
              const scrollable = containerRef.current?.querySelector(
                '[class*="overflow-y"]',
              );
              if (scrollable) scrollable.scrollTop += e.deltaY;
            }}
            disabled={navigation.isFirst}
            className="p-4 rounded-full bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-700 backdrop-blur-lg text-gray-900 dark:text-gray-100 hover:text-gray-900 dark:hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shadow-lg pointer-events-auto"
            aria-label="Previous slide"
          >
            <HiArrowLeft className="w-6 h-6" />
          </button>
        </div>

        <div className="absolute right-4 top-1/2 -translate-y-1/2 hidden md:block pointer-events-none z-10">
          <button
            onClick={navigation.next}
            onWheel={(e) => {
              const scrollable = containerRef.current?.querySelector(
                '[class*="overflow-y"]',
              );
              if (scrollable) scrollable.scrollTop += e.deltaY;
            }}
            disabled={navigation.isLast}
            className="p-4 rounded-full bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-700 backdrop-blur-lg text-gray-900 dark:text-gray-100 hover:text-gray-900 dark:hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shadow-lg pointer-events-auto"
            aria-label="Next slide"
          >
            <HiArrowRight className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Bottom Bar Container (Speaker Notes + Progress) */}
      <div
        className={`fixed bottom-0 left-0 right-0 z-50 transition-transform duration-300 ${
          presentation.shouldShowBottomBar
            ? "translate-y-0"
            : "translate-y-full"
        }`}
      >
        {/* Progress Bar */}
        <SlideProgress
          currentIndex={navigation.currentIndex}
          totalSlides={slideCount}
          loadedSlides={loadedSlides}
          onSlideClick={navigation.goToSlide}
        />
      </div>

      {/* Settings Modal */}
      <PresentationSettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        autoHideTopBar={presentation.autoHideTopBar}
        autoHideBottomBar={presentation.autoHideBottomBar}
        onAutoHideTopBarChange={presentation.setAutoHideTopBar}
        onAutoHideBottomBarChange={presentation.setAutoHideBottomBar}
      />

      {/* Help Modal */}
      <PresentationHelpModal
        isOpen={helpOpen}
        onClose={() => setHelpOpen(false)}
        allowFullscreen={allowFullscreen}
      />
    </div>
  );
};

export default SlideshowViewer;
