import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  EditorHeader,
  SlideList,
  SlideEditor,
  SlidePreview,
} from '../components/slideshow/editor';
import { useOnlineStatus } from '../hooks/useOnlineStatus';
import { useEditorDraft } from '../hooks/useEditorDraft';
import { useUnsavedChanges } from '../hooks/useUnsavedChanges';
import {
  getSlideshowDetail,
  createSlideshow,
  updateSlideshow,
} from '../services/slideshowApi';
import type { EditorSlide, EditorDraft, SaveStatus } from '../types/editor.types';

export default function SlideshowEditorPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNewSlideshow = id === 'new';
  const slideshowId = isNewSlideshow ? 'new' : parseInt(id!, 10);

  const isOnline = useOnlineStatus();
  const { loadDraft, saveDraft, clearDraft } = useEditorDraft(slideshowId);

  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [visibility, setVisibility] = useState<'public' | 'unlisted' | 'private'>('private');
  const [subject, setSubject] = useState<string | null>(null);
  const [language, setLanguage] = useState<string | null>(null);
  const [isPublished, setIsPublished] = useState(false);
  const [slides, setSlides] = useState<EditorSlide[]>([]);
  const [selectedSlideId, setSelectedSlideId] = useState<string | null>(null);
  const [version, setVersion] = useState<number | undefined>(undefined);

  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [showPreview] = useState(true);

  // Warn about unsaved changes
  useUnsavedChanges(isDirty, 'You have unsaved changes. Are you sure you want to leave?');

  // Load slideshow or draft on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        // Try loading from localStorage draft first
        const draft = loadDraft();

        if (draft) {
          // Load from draft
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
          toast.success('Loaded draft from local storage', { id: 'draft-loaded' });
        } else if (!isNewSlideshow) {
          // Load from server
          const slideshow = await getSlideshowDetail(slideshowId as number);
          setTitle(slideshow.title);
          setDescription(slideshow.description || '');
          setVisibility(slideshow.visibility);
          setSubject(slideshow.subject);
          setLanguage(slideshow.language);
          setIsPublished(slideshow.is_published);
          setVersion(slideshow.version);

          // Convert slides to editor format
          const editorSlides: EditorSlide[] = slideshow.slides.map((slide, index) => ({
            id: slide.id,
            tempId: crypto.randomUUID(),
            order: slide.order ?? index,
            content: 'content' in slide ? slide.content : '',
            notes: 'notes' in slide ? (slide.notes || '') : '',
            rendered_content: slide.rendered_content,
          }));

          setSlides(editorSlides);
          if (editorSlides.length > 0) {
            setSelectedSlideId(editorSlides[0].tempId);
          }
        } else {
          // New slideshow - start with one empty slide
          const newSlide: EditorSlide = {
            tempId: crypto.randomUUID(),
            order: 0,
            content: '# Welcome\n\nStart creating your slideshow!',
            notes: '',
          };
          setSlides([newSlide]);
          setSelectedSlideId(newSlide.tempId);
        }
      } catch (error: any) {
        toast.error(error.message || 'Failed to load slideshow');
        navigate('/slideshows/me');
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
      toast.error('Please enter a title before saving');
      return;
    }

    try {
      setSaveStatus('saving');
      setSaveError(null);

      if (isNewSlideshow) {
        // Create new slideshow
        const created = await createSlideshow({
          title,
          description: description || null,
          visibility,
          subject,
          language,
          is_published: isPublished,
          slides: slides.map((slide) => ({
            order: slide.order,
            content: slide.content,
            notes: slide.notes || null,
          })),
        });

        toast.success('Slideshow created!');
        clearDraft();
        navigate(`/slideshows/${created.id}/edit`, { replace: true });
      } else {
        // Update existing slideshow
        const updated = await updateSlideshow(slideshowId as number, {
          title,
          description: description || null,
          visibility,
          subject,
          language,
          is_published: isPublished,
          version: version!,
          slides: slides.map((slide) => ({
            order: slide.order,
            content: slide.content,
            notes: slide.notes || null,
          })),
        });

        setVersion(updated.version);
        setIsDirty(false);
        setSaveStatus('saved');
        setLastSaved(new Date());
        toast.success('Slideshow saved!');
        clearDraft();
      }
    } catch (error: any) {
      setSaveStatus('error');
      setSaveError(error.message);
      toast.error(error.message || 'Failed to save');
    }
  };

  const handleAddSlide = () => {
    const newSlide: EditorSlide = {
      tempId: crypto.randomUUID(),
      order: slides.length,
      content: '',
      notes: '',
    };
    setSlides([...slides, newSlide]);
    setSelectedSlideId(newSlide.tempId);
    setIsDirty(true);
  };

  const handleDeleteSlide = (tempId: string) => {
    if (slides.length === 1) {
      toast.error('Cannot delete the last slide');
      return;
    }

    const index = slides.findIndex((s) => s.tempId === tempId);
    const newSlides = slides.filter((s) => s.tempId !== tempId).map((slide, i) => ({
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
    toast.success('Slide deleted');
  };

  const handleDuplicateSlide = (tempId: string) => {
    const slide = slides.find((s) => s.tempId === tempId);
    if (!slide) return;

    const index = slides.findIndex((s) => s.tempId === tempId);
    const newSlide: EditorSlide = {
      tempId: crypto.randomUUID(),
      order: index + 1,
      content: slide.content,
      notes: slide.notes,
    };

    const newSlides = [
      ...slides.slice(0, index + 1),
      newSlide,
      ...slides.slice(index + 1),
    ].map((s, i) => ({ ...s, order: i }));

    setSlides(newSlides);
    setSelectedSlideId(newSlide.tempId);
    setIsDirty(true);
    toast.success('Slide duplicated');
  };

  const handleSlideChange = (tempId: string, updates: Partial<EditorSlide>) => {
    setSlides(slides.map((s) => (s.tempId === tempId ? { ...s, ...updates } : s)));
    setIsDirty(true);
  };

  const handleReorderSlides = (reordered: EditorSlide[]) => {
    setSlides(reordered);
    setIsDirty(true);
  };

  const handlePresent = () => {
    if (isNewSlideshow || !slideshowId) {
      toast.error('Please save the slideshow before presenting');
      return;
    }
    navigate(`/slideshows/${slideshowId}/present`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading editor...</p>
        </div>
      </div>
    );
  }

  const selectedSlide = slides.find((s) => s.tempId === selectedSlideId) || null;

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      <EditorHeader
        slideshowId={slideshowId}
        title={title}
        onTitleChange={setTitle}
        isPublished={isPublished}
        onPublishToggle={() => setIsPublished(!isPublished)}
        onPresentClick={handlePresent}
        onSaveClick={handleSave}
        saveStatus={isOnline ? saveStatus : 'offline'}
        lastSaved={lastSaved}
        saveError={saveError}
        isDirty={isDirty}
        canPresent={slides.length > 0 && !isNewSlideshow}
      />

      <div className="flex-1 flex overflow-hidden">
        <div className="w-64 border-r border-gray-200 dark:border-gray-700">
          <SlideList
            slides={slides}
            selectedId={selectedSlideId}
            onSelect={setSelectedSlideId}
            onAdd={handleAddSlide}
            onDelete={handleDeleteSlide}
            onReorder={handleReorderSlides}
            onDuplicate={handleDuplicateSlide}
          />
        </div>

        <div className={showPreview ? 'flex-1' : 'flex-[2]'}>
          <SlideEditor
            slide={selectedSlide}
            onChange={(updates) => selectedSlideId && handleSlideChange(selectedSlideId, updates)}
          />
        </div>

        {showPreview && (
          <div className="flex-1">
            <SlidePreview slide={selectedSlide} isVisible={showPreview} />
          </div>
        )}
      </div>

      {!isOnline && (
        <div className="fixed bottom-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg">
          You're offline. Changes will be saved locally.
        </div>
      )}
    </div>
  );
}
