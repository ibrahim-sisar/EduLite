import React, { useState, useEffect, useCallback, useRef } from "react";
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
import { getSlideshowDetail, getSlide } from "../../services/slideshowApi";
import type { Slide, SlideViewOnly } from "../../types/slideshow.types";
import type { SlideshowViewerProps } from "./types";
import SlideDisplay from "./SlideDisplay";
import SlideProgress from "./SlideProgress";
import SpeakerNotes from "./SpeakerNotes";
import PresentationSettingsModal from "./PresentationSettingsModal";
import PresentationHelpModal from "./PresentationHelpModal";

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
 * SlideshowViewer Component
 *
 * Main presentation viewer with:
 * - Progressive loading (first 3 slides immediate, rest in background)
 * - Keyboard navigation (arrows, space, escape, N for notes)
 * - Fullscreen support (optional)
 * - Offline capability (loads ALL slides, works without network)
 * - Speaker notes panel
 */
const SlideshowViewer: React.FC<SlideshowViewerProps> = ({
  slideshowId,
  initialSlide = 0,
  showNotes: showNotesInitial = false,
  onExit,
  allowFullscreen = false,
}) => {
  // State management
  const [currentIndex, setCurrentIndex] = useState<number>(initialSlide);
  const [slides, setSlides] = useState<Map<number, Slide | SlideViewOnly>>(new Map());
  const [showNotes, setShowNotes] = useState<boolean>(showNotesInitial);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [slideCount, setSlideCount] = useState<number>(0);
  const [slideshowTitle, setSlideshowTitle] = useState<string>("");
  const [createdByUsername, setCreatedByUsername] = useState<string>("");
  const [subject, setSubject] = useState<string | null>(null);
  const [remainingSlideIds, setRemainingSlideIds] = useState<number[]>([]);
  const [settingsOpen, setSettingsOpen] = useState<boolean>(false);
  const [helpOpen, setHelpOpen] = useState<boolean>(false);

  // Auto-hide settings (default to true)
  const [autoHideTopBar, setAutoHideTopBar] = useState<boolean>(() => {
    const saved = localStorage.getItem('slideshow-auto-hide-top');
    return saved !== null ? JSON.parse(saved) : true;
  });
  const [autoHideBottomBar, setAutoHideBottomBar] = useState<boolean>(() => {
    const saved = localStorage.getItem('slideshow-auto-hide-bottom');
    return saved !== null ? JSON.parse(saved) : true;
  });

  // Hover state for auto-hide
  const [isTopBarHovered, setIsTopBarHovered] = useState<boolean>(false);
  const [isBottomBarHovered, setIsBottomBarHovered] = useState<boolean>(false);

  const containerRef = useRef<HTMLDivElement>(null);

  // Get current slide
  const currentSlide = slides.get(currentIndex) || null;
  const currentSlideNotes: string | null =
    currentSlide && "notes" in currentSlide
      ? (currentSlide.notes as string | null)
      : null;

  // Get readable subject name
  const getSubjectName = (code: string | null): string | null => {
    if (!code) return null;
    return SUBJECTS[code] || code;
  };

  const subjectName = getSubjectName(subject);

  // Save auto-hide settings to localStorage
  useEffect(() => {
    localStorage.setItem('slideshow-auto-hide-top', JSON.stringify(autoHideTopBar));
  }, [autoHideTopBar]);

  useEffect(() => {
    localStorage.setItem('slideshow-auto-hide-bottom', JSON.stringify(autoHideBottomBar));
  }, [autoHideBottomBar]);

  // Track mouse position for auto-hide
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const baseThreshold = 100; // pixels from edge to trigger show

      // Top bar
      if (autoHideTopBar) {
        setIsTopBarHovered(e.clientY < baseThreshold);
      } else {
        setIsTopBarHovered(true);
      }

      // Bottom bar - adjust threshold based on notes being open
      if (autoHideBottomBar) {
        // When notes are open, extend threshold to cover:
        // - Notes content: max-h-80 (320px) + padding/borders (~20px)
        // - Toggle button: ~48px
        // - Progress bar: ~50px
        // Total: ~440px, use 450px to be safe
        const bottomThreshold = showNotes ? 450 : baseThreshold;
        setIsBottomBarHovered(e.clientY > window.innerHeight - bottomThreshold);
      } else {
        setIsBottomBarHovered(true);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [autoHideTopBar, autoHideBottomBar, showNotes]);

  // Determine if bars should be visible
  const shouldShowTopBar = !autoHideTopBar || isTopBarHovered || settingsOpen || helpOpen;
  const shouldShowBottomBar = !autoHideBottomBar || isBottomBarHovered;

  /**
   * Initial load: Fetch first 3 slides immediately
   */
  useEffect(() => {
    const loadInitialSlides = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Fetch first 3 slides
        const data = await getSlideshowDetail(slideshowId, 3);

        // Store slideshow metadata
        setSlideCount(data.slide_count);
        setSlideshowTitle(data.title);
        setCreatedByUsername(data.created_by_username);
        setSubject(data.subject);
        setRemainingSlideIds(data.remaining_slide_ids);

        // Store initial slides in Map (indexed by order)
        const initialSlides = new Map<number, Slide | SlideViewOnly>();
        data.slides.forEach((slide) => {
          initialSlides.set(slide.order, slide);
        });
        setSlides(initialSlides);

        setIsLoading(false);
      } catch (err) {
        console.error("Failed to load slideshow:", err);
        setError(err instanceof Error ? err.message : "Failed to load slideshow");
        setIsLoading(false);
        toast.error("Failed to load slideshow");
      }
    };

    loadInitialSlides();
  }, [slideshowId]);

  /**
   * Background loading: Fetch remaining slides progressively
   */
  useEffect(() => {
    if (remainingSlideIds.length === 0) return;

    const loadRemainingSlides = async () => {
      // Load remaining slides in parallel (batch of 5 at a time)
      const batchSize = 5;
      const idsToLoad = [...remainingSlideIds];

      for (let i = 0; i < idsToLoad.length; i += batchSize) {
        const batch = idsToLoad.slice(i, i + batchSize);

        // Fetch batch in parallel
        const promises = batch.map((slideId) =>
          getSlide(slideshowId, slideId)
            .then((slide) => ({ slideId, slide, error: null }))
            .catch((error) => ({ slideId, slide: null, error }))
        );

        const results = await Promise.all(promises);

        // Store fetched slides
        setSlides((prev) => {
          const newMap = new Map(prev);
          results.forEach(({ slide }) => {
            if (slide) {
              newMap.set(slide.order, slide);
            }
          });
          return newMap;
        });
      }
    };

    loadRemainingSlides();
  }, [remainingSlideIds, slideshowId]);

  /**
   * Navigation functions
   */
  const goToNextSlide = useCallback(() => {
    setCurrentIndex((prev) => Math.min(prev + 1, slideCount - 1));
  }, [slideCount]);

  const goToPreviousSlide = useCallback(() => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  }, []);

  const goToSlide = useCallback((index: number) => {
    setCurrentIndex(Math.max(0, Math.min(index, slideCount - 1)));
  }, [slideCount]);

  const toggleNotes = useCallback(() => {
    setShowNotes((prev) => !prev);
  }, []);

  const handleEdit = useCallback(() => {
    // TODO: Navigate to editor when implemented
    // navigate(`/slideshows/${slideshowId}/edit`);
    toast("Editor coming soon!", {
      icon: "✏️",
      duration: 3000,
    });
  }, [slideshowId]);

  /**
   * Fullscreen handling
   */
  const toggleFullscreen = useCallback(async () => {
    if (!containerRef.current) return;

    try {
      if (!document.fullscreenElement) {
        await containerRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (err) {
      console.error("Fullscreen error:", err);
      toast.error("Failed to toggle fullscreen");
    }
  }, []);

  // Listen for fullscreen changes (e.g., user presses Esc)
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  /**
   * Keyboard navigation
   */
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case "ArrowRight":
        case " ":
          e.preventDefault();
          goToNextSlide();
          break;
        case "ArrowLeft":
        case "Backspace":
          e.preventDefault();
          goToPreviousSlide();
          break;
        case "Escape":
          e.preventDefault();
          if (document.fullscreenElement) {
            document.exitFullscreen();
          } else {
            onExit?.();
          }
          break;
        case "n":
        case "N":
          e.preventDefault();
          toggleNotes();
          break;
        case "Home":
          e.preventDefault();
          goToSlide(0);
          break;
        case "End":
          e.preventDefault();
          goToSlide(slideCount - 1);
          break;
        case "f":
        case "F":
          if (allowFullscreen) {
            e.preventDefault();
            toggleFullscreen();
          }
          break;
        default:
          // Number keys (1-9) for quick jump
          if (e.key >= "1" && e.key <= "9") {
            const slideNum = parseInt(e.key, 10) - 1;
            if (slideNum < slideCount) {
              e.preventDefault();
              goToSlide(slideNum);
            }
          }
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    goToNextSlide,
    goToPreviousSlide,
    goToSlide,
    toggleNotes,
    toggleFullscreen,
    onExit,
    slideCount,
    allowFullscreen,
  ]);

  /**
   * Error state
   */
  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-red-900/20 border border-red-500/50 rounded-2xl p-8 max-w-md text-center">
          <h2 className="text-2xl font-light text-red-400 mb-4">Error Loading Slideshow</h2>
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
          <p className="text-xl text-gray-300 font-light">Loading presentation...</p>
        </div>
      </div>
    );
  }

  /**
   * Main viewer UI
   */
  const loadedSlides = Array.from({ length: slideCount }, (_, i) => slides.has(i));
  const isCurrentSlideLoading = !slides.has(currentIndex);

  return (
    <div
      ref={containerRef}
      className="min-h-screen bg-white dark:bg-black flex flex-col"
    >
      {/* Header / Controls */}
      <div className={`fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-white/90 dark:bg-black/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700/30 transition-transform duration-300 ${
        shouldShowTopBar ? 'translate-y-0' : '-translate-y-full'
      }`}>
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
            {slideshowTitle}
          </a>
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            {createdByUsername && (
              <a
                href={`/profile/${createdByUsername}`}
                className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer"
                onClick={(e) => {
                  e.preventDefault();
                  window.location.href = `/profile/${createdByUsername}`;
                }}
              >
                by {createdByUsername}
              </a>
            )}
            {subjectName && subject && (
              <>
                {createdByUsername && <span>•</span>}
                <a
                  href={`/slideshows/public?subject=${subject}`}
                  className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer"
                  onClick={(e) => {
                    e.preventDefault();
                    window.location.href = `/slideshows/public?subject=${subject}`;
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
          {/* Edit Button (Always show, TODO: check ownership on backend when editor exists) */}
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
              onClick={toggleFullscreen}
              className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer"
              aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
              title={isFullscreen ? "Exit fullscreen (F)" : "Enter fullscreen (F)"}
            >
              {isFullscreen ? (
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
          marginTop: !autoHideTopBar ? '5rem' : '0',
          marginBottom: !autoHideBottomBar ? (showNotes ? '28rem' : 'calc(3.5rem - 8px)') : '0'
        }}
      >
        <div className="w-full h-full">
          {/* Slide Display */}
          <SlideDisplay
            slide={currentSlide}
            isLoading={isCurrentSlideLoading}
            slideNumber={currentIndex + 1}
            totalSlides={slideCount}
          />
        </div>

        {/* Navigation Arrows (always visible on desktop) */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 hidden md:block">
          <button
            onClick={goToPreviousSlide}
            disabled={currentIndex === 0}
            className="p-4 rounded-full bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-700 backdrop-blur-lg text-gray-900 dark:text-gray-100 hover:text-gray-900 dark:hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shadow-lg"
            aria-label="Previous slide"
          >
            <HiArrowLeft className="w-6 h-6" />
          </button>
        </div>

        <div className="absolute right-4 top-1/2 -translate-y-1/2 hidden md:block">
          <button
            onClick={goToNextSlide}
            disabled={currentIndex === slideCount - 1}
            className="p-4 rounded-full bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-700 backdrop-blur-lg text-gray-900 dark:text-gray-100 hover:text-gray-900 dark:hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shadow-lg"
            aria-label="Next slide"
          >
            <HiArrowRight className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Bottom Bar Container (Speaker Notes + Progress) */}
      <div className={`fixed bottom-0 left-0 right-0 z-50 transition-transform duration-300 ${
        shouldShowBottomBar ? 'translate-y-0' : 'translate-y-full'
      }`}>
        {/* Speaker Notes Panel */}
        <SpeakerNotes
          notes={currentSlideNotes}
          isVisible={showNotes}
          onToggle={toggleNotes}
        />

        {/* Progress Bar */}
        <SlideProgress
          currentIndex={currentIndex}
          totalSlides={slideCount}
          loadedSlides={loadedSlides}
          onSlideClick={goToSlide}
        />
      </div>

      {/* Settings Modal */}
      <PresentationSettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        autoHideTopBar={autoHideTopBar}
        autoHideBottomBar={autoHideBottomBar}
        onAutoHideTopBarChange={setAutoHideTopBar}
        onAutoHideBottomBarChange={setAutoHideBottomBar}
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
