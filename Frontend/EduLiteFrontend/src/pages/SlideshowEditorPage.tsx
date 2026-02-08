import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { HiXMark } from "react-icons/hi2";
import { HiViewList, HiPencilAlt, HiEye } from "react-icons/hi";
import {
  EditorHeader,
  SlideList,
  SlideEditor,
  SlidePreview,
} from "../components/slideshow/editor";
import { useOnlineStatus } from "../hooks/useOnlineStatus";
import { useEditorDraft } from "../hooks/useEditorDraft";
import { useUnsavedChanges } from "../hooks/useUnsavedChanges";

import {
  getSlideshowDetail,
  createSlideshow,
  updateSlideshow,
} from "../services/slideshowApi";
import type {
  EditorSlide,
  EditorDraft,
  SaveStatus,
} from "../types/editor.types";

export default function SlideshowEditorPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNewSlideshow = !id || id === "new";
  const slideshowId = isNewSlideshow ? "new" : parseInt(id, 10);

  const isOnline = useOnlineStatus();
  const { loadDraft, saveDraft, clearDraft } = useEditorDraft(slideshowId);

  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [visibility, setVisibility] = useState<
    "public" | "unlisted" | "private"
  >("private");
  const [subject, setSubject] = useState<string | null>(null);
  const [language, setLanguage] = useState<string | null>(null);
  const [isPublished, setIsPublished] = useState(false);
  const [slides, setSlides] = useState<EditorSlide[]>([]);
  const [selectedSlideId, setSelectedSlideId] = useState<string | null>(null);
  const [version, setVersion] = useState<number | undefined>(undefined);

  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [showPreview] = useState(true);
  const [mobilePanel, setMobilePanel] = useState<
    "slides" | "editor" | "preview"
  >("editor");
  const [showPresentModal, setShowPresentModal] = useState(false);

  // Warn about unsaved changes
  useUnsavedChanges(
    isDirty,
    "You have unsaved changes. Are you sure you want to leave?",
  );

  // Helper to load slideshow data from server into state
  const loadFromServer = async (slideshowIdNum: number) => {
    const slideshow = await getSlideshowDetail(slideshowIdNum);
    setTitle(slideshow.title);
    setDescription(slideshow.description || "");
    setVisibility(slideshow.visibility);
    setSubject(slideshow.subject);
    setLanguage(slideshow.language);
    setIsPublished(slideshow.is_published);
    setVersion(slideshow.version);

    // Convert slides to editor format
    const editorSlides: EditorSlide[] = slideshow.slides.map(
      (slide, index) => ({
        id: slide.id,
        tempId: crypto.randomUUID(),
        order: slide.order ?? index,
        content: "content" in slide ? slide.content : "",
        rendered_content: slide.rendered_content,
      }),
    );

    setSlides(editorSlides);
    if (editorSlides.length > 0) {
      setSelectedSlideId(editorSlides[0].tempId);
    }

    return slideshow;
  };

  // Load slideshow or draft on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        // Try loading from localStorage draft first
        const draft = loadDraft();

        if (draft && !isNewSlideshow) {
          // Draft exists for an existing slideshow - check if it's stale
          try {
            const serverData = await getSlideshowDetail(slideshowId as number);
            if (serverData.version > (draft.version || 0)) {
              // Draft is stale, discard it and use server data
              clearDraft();
              toast("Draft was outdated, loaded latest from server", {
                id: "draft-stale",
                icon: "ℹ️",
              });
              await loadFromServer(slideshowId as number);
            } else {
              // Draft is current, use it
              setTitle(draft.data.title);
              setDescription(draft.data.description);
              setVisibility(draft.data.visibility);
              setSubject(draft.data.subject);
              setLanguage(draft.data.language);
              setIsPublished(draft.data.is_published);
              setSlides(draft.data.slides);
              setVersion(draft.version);
              if (draft.data.slides.length > 0) {
                setSelectedSlideId(draft.data.slides[0].tempId);
              }
              setIsDirty(true);
              toast.success("Loaded draft from local storage", {
                id: "draft-loaded",
              });
            }
          } catch {
            // Server fetch failed, use draft anyway (might be offline)
            setTitle(draft.data.title);
            setDescription(draft.data.description);
            setVisibility(draft.data.visibility);
            setSubject(draft.data.subject);
            setLanguage(draft.data.language);
            setIsPublished(draft.data.is_published);
            setSlides(draft.data.slides);
            setVersion(draft.version);
            if (draft.data.slides.length > 0) {
              setSelectedSlideId(draft.data.slides[0].tempId);
            }
            setIsDirty(true);
            toast.success("Loaded draft from local storage", {
              id: "draft-loaded",
            });
          }
        } else if (draft && isNewSlideshow) {
          // Draft for a new slideshow - just load it
          setTitle(draft.data.title);
          setDescription(draft.data.description);
          setVisibility(draft.data.visibility);
          setSubject(draft.data.subject);
          setLanguage(draft.data.language);
          setIsPublished(draft.data.is_published);
          setSlides(draft.data.slides);
          setVersion(draft.version);
          if (draft.data.slides.length > 0) {
            setSelectedSlideId(draft.data.slides[0].tempId);
          }
          setIsDirty(true);
          toast.success("Loaded draft from local storage", {
            id: "draft-loaded",
          });
        } else if (!isNewSlideshow) {
          // Load from server
          await loadFromServer(slideshowId as number);
        } else {
          // New slideshow - start with one empty slide
          const newSlide: EditorSlide = {
            tempId: crypto.randomUUID(),
            order: 0,
            content: "# Welcome\n\nStart creating your slideshow!",
          };
          setSlides([newSlide]);
          setSelectedSlideId(newSlide.tempId);
        }
      } catch (error: any) {
        toast.error(error.message || "Failed to load slideshow");
        navigate("/slideshows/me");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Auto-save to localStorage on any change
  useEffect(() => {
    if (loading) return;

    const draft: EditorDraft = {
      slideshowId,
      lastSaved: lastSaved?.toISOString() || new Date().toISOString(),
      lastModified: new Date().toISOString(),
      version,
      data: {
        title,
        description,
        visibility,
        subject,
        language,
        country: null,
        is_published: isPublished,
        slides,
      },
    };

    saveDraft(draft);
  }, [title, description, visibility, subject, language, isPublished, slides]);

  const handleSave = async () => {
    if (!title.trim()) {
      toast.error("Please enter a title before saving");
      return;
    }

    try {
      setSaveStatus("saving");
      setSaveError(null);

      if (isNewSlideshow) {
        // Create new slideshow
        // Filter out slides with empty content
        const validSlides = slides.filter(
          (slide) => slide.content.trim() !== "",
        );

        if (validSlides.length === 0) {
          toast.error("Please add at least one slide with content");
          setSaveStatus("error");
          return;
        }

        const created = await createSlideshow({
          title,
          description: description || null,
          visibility,
          subject,
          language,
          is_published: isPublished,
          slides: validSlides.map((slide, index) => ({
            order: index, // Re-index after filtering
            content: slide.content,
          })),
        });

        toast.success("Slideshow created!");
        clearDraft();
        navigate(`/slideshows/${created.id}/edit`, { replace: true });
      } else {
        // Update existing slideshow
        // Filter out slides with empty content
        const validSlides = slides.filter(
          (slide) => slide.content.trim() !== "",
        );

        if (validSlides.length === 0) {
          toast.error("Please add at least one slide with content");
          setSaveStatus("error");
          return;
        }

        const updated = await updateSlideshow(slideshowId as number, {
          title,
          description: description || null,
          visibility,
          subject,
          language,
          is_published: isPublished,
          version: version!,
          slides: validSlides.map((slide, index) => ({
            order: index, // Re-index after filtering
            content: slide.content,
          })),
        });

        // Update version
        setVersion(updated.version);

        // Update slides with the backend response to get proper IDs and rendered_content
        const updatedSlides: EditorSlide[] = updated.slides.map(
          (slide, index) => {
            // Preserve tempId by matching position (order is preserved through save)
            const existingSlide = validSlides[index];
            return {
              id: slide.id,
              tempId: existingSlide?.tempId || crypto.randomUUID(),
              order: slide.order ?? index,
              content: "content" in slide ? slide.content : "",
              rendered_content: slide.rendered_content,
            };
          },
        );
        setSlides(updatedSlides);

        // If we filtered out any slides, update the selected slide if needed
        if (
          selectedSlideId &&
          !updatedSlides.find((s) => s.tempId === selectedSlideId)
        ) {
          setSelectedSlideId(updatedSlides[0]?.tempId || null);
        }

        setIsDirty(false);
        setSaveStatus("saved");
        setLastSaved(new Date());
        toast.success("Slideshow saved!");
        clearDraft();
      }
    } catch (error: any) {
      // Check for version conflict error
      const errorData = error.response?.data;
      if (errorData?.error?.includes("version_conflict")) {
        setSaveStatus("error");
        setSaveError("Version conflict");
        const reload = window.confirm(
          "This slideshow was modified elsewhere.\n\n" +
            "Would you like to reload with the latest version?\n" +
            "(Your unsaved changes will be lost)",
        );
        if (reload) {
          clearDraft();
          window.location.reload();
        }
        return;
      }

      setSaveStatus("error");
      setSaveError(error.message);
      toast.error(error.message || "Failed to save");
    }
  };

  const handleAddSlide = () => {
    const newSlide: EditorSlide = {
      tempId: crypto.randomUUID(),
      order: slides.length,
      content: "",
    };
    setSlides([...slides, newSlide]);
    setSelectedSlideId(newSlide.tempId);
    setIsDirty(true);
  };

  const handleDeleteSlide = (tempId: string) => {
    if (slides.length === 1) {
      toast.error("Cannot delete the last slide");
      return;
    }

    const index = slides.findIndex((s) => s.tempId === tempId);
    const newSlides = slides
      .filter((s) => s.tempId !== tempId)
      .map((slide, i) => ({
        ...slide,
        order: i,
      }));

    setSlides(newSlides);

    // Select adjacent slide
    if (selectedSlideId === tempId) {
      const newIndex = Math.min(index, newSlides.length - 1);
      setSelectedSlideId(newSlides[newIndex]?.tempId || null);
    }

    setIsDirty(true);
    toast.success("Slide deleted");
  };

  const handleDuplicateSlide = (tempId: string) => {
    const slide = slides.find((s) => s.tempId === tempId);
    if (!slide) return;

    const index = slides.findIndex((s) => s.tempId === tempId);
    const newSlide: EditorSlide = {
      tempId: crypto.randomUUID(),
      order: index + 1,
      content: slide.content,
    };

    const newSlides = [
      ...slides.slice(0, index + 1),
      newSlide,
      ...slides.slice(index + 1),
    ].map((s, i) => ({ ...s, order: i }));

    setSlides(newSlides);
    setSelectedSlideId(newSlide.tempId);
    setIsDirty(true);
    toast.success("Slide duplicated");
  };

  const handleSlideChange = (tempId: string, updates: Partial<EditorSlide>) => {
    setSlides(
      slides.map((s) => (s.tempId === tempId ? { ...s, ...updates } : s)),
    );
    setIsDirty(true);
  };

  const handleReorderSlides = (reordered: EditorSlide[]) => {
    setSlides(reordered);
    setIsDirty(true);
  };

  const handlePresent = () => {
    if (isNewSlideshow || !slideshowId) {
      toast.error("Please save the slideshow before presenting");
      return;
    }

    // Show modal if there are unsaved changes
    if (isDirty) {
      setShowPresentModal(true);
      return;
    }

    navigate(`/slideshows/${slideshowId}/present`);
  };

  const handleSaveAndPresent = async () => {
    setShowPresentModal(false);
    await handleSave();
    // Only navigate if save was successful (no errors)
    if (saveStatus !== "error") {
      navigate(`/slideshows/${slideshowId}/present`);
    }
  };

  const handlePresentWithoutSaving = () => {
    setShowPresentModal(false);
    navigate(`/slideshows/${slideshowId}/present`);
  };

  // Handle keyboard shortcuts for present modal
  useEffect(() => {
    if (!showPresentModal) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleSaveAndPresent();
      }
      if (e.key === "Escape") {
        e.preventDefault();
        setShowPresentModal(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [showPresentModal]);

  // Navigation handlers for slides
  const currentSlideIndex = slides.findIndex(
    (s) => s.tempId === selectedSlideId,
  );

  const handlePrevSlide = useCallback(() => {
    if (currentSlideIndex > 0) {
      setSelectedSlideId(slides[currentSlideIndex - 1].tempId);
    }
  }, [currentSlideIndex, slides]);

  const handleNextSlide = useCallback(() => {
    if (currentSlideIndex < slides.length - 1) {
      setSelectedSlideId(slides[currentSlideIndex + 1].tempId);
    }
  }, [currentSlideIndex, slides]);

  // Arrow key navigation for editor (when not in text input)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if typing in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      if (e.key === "ArrowLeft") {
        e.preventDefault();
        handlePrevSlide();
      }
      if (e.key === "ArrowRight") {
        e.preventDefault();
        handleNextSlide();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handlePrevSlide, handleNextSlide]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Loading editor...
          </p>
        </div>
      </div>
    );
  }

  const selectedSlide =
    slides.find((s) => s.tempId === selectedSlideId) || null;

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 pt-16">
      <EditorHeader
        slideshowId={slideshowId}
        title={title}
        onTitleChange={setTitle}
        onPresentClick={handlePresent}
        onSaveClick={handleSave}
        saveStatus={isOnline ? saveStatus : "offline"}
        lastSaved={lastSaved}
        saveError={saveError}
        isDirty={isDirty}
        canPresent={slides.length > 0 && !isNewSlideshow}
      />

      {/* Mobile Panel Tabs */}
      <div className="flex md:hidden border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <button
          onClick={() => setMobilePanel("slides")}
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-sm font-medium transition-colors cursor-pointer ${
            mobilePanel === "slides"
              ? "text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400"
              : "text-gray-500 dark:text-gray-400"
          }`}
        >
          <HiViewList className="w-4 h-4" />
          Slides
        </button>
        <button
          onClick={() => setMobilePanel("editor")}
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-sm font-medium transition-colors cursor-pointer ${
            mobilePanel === "editor"
              ? "text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400"
              : "text-gray-500 dark:text-gray-400"
          }`}
        >
          <HiPencilAlt className="w-4 h-4" />
          Editor
        </button>
        <button
          onClick={() => setMobilePanel("preview")}
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-sm font-medium transition-colors cursor-pointer ${
            mobilePanel === "preview"
              ? "text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400"
              : "text-gray-500 dark:text-gray-400"
          }`}
        >
          <HiEye className="w-4 h-4" />
          Preview
        </button>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div
          className={`w-full md:w-64 border-r border-gray-200 dark:border-gray-700 ${mobilePanel === "slides" ? "block" : "hidden"} md:block`}
        >
          <SlideList
            slides={slides}
            selectedId={selectedSlideId}
            onSelect={(id) => {
              setSelectedSlideId(id);
              setMobilePanel("editor");
            }}
            onAdd={handleAddSlide}
            onDelete={handleDeleteSlide}
            onReorder={handleReorderSlides}
            onDuplicate={handleDuplicateSlide}
          />
        </div>

        <div
          className={`w-full ${showPreview ? "md:flex-1" : "md:flex-[2]"} ${mobilePanel === "editor" ? "block" : "hidden"} md:block`}
        >
          <SlideEditor
            slide={selectedSlide}
            onChange={(updates) =>
              selectedSlideId && handleSlideChange(selectedSlideId, updates)
            }
          />
        </div>

        {showPreview && (
          <div
            className={`w-full md:flex-1 ${mobilePanel === "preview" ? "block" : "hidden"} md:block`}
          >
            <SlidePreview
              slide={selectedSlide}
              isVisible={showPreview}
              currentIndex={currentSlideIndex}
              totalSlides={slides.length}
              onPrev={handlePrevSlide}
              onNext={handleNextSlide}
            />
          </div>
        )}
      </div>

      {!isOnline && (
        <div className="fixed bottom-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg">
          You're offline. Changes will be saved locally.
        </div>
      )}

      {/* Present with unsaved changes modal */}
      {showPresentModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
          onClick={() => setShowPresentModal(false)}
        >
          <div
            className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Unsaved Changes
              </h2>
              <button
                onClick={() => setShowPresentModal(false)}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
              >
                <HiXMark className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>

            <div className="px-6 py-4">
              <p className="text-gray-700 dark:text-gray-300">
                You have unsaved changes. These changes will not appear in the
                presentation.
              </p>
            </div>

            <div className="px-6 py-4 bg-gray-50 dark:bg-gray-900/50 flex justify-end gap-3">
              <button
                onClick={handlePresentWithoutSaving}
                className="px-4 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg font-medium transition-colors cursor-pointer"
              >
                Don't Save
              </button>
              <button
                onClick={handleSaveAndPresent}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors cursor-pointer"
              >
                Save & Present
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
