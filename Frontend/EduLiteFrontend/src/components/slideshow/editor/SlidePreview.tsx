import { useState, useEffect, useMemo } from 'react';
import { usePreviewCache } from '../../../hooks/usePreviewCache';
import { previewMarkdown } from '../../../services/slideshowApi';
import toast from 'react-hot-toast';
import type { EditorSlide } from '../../../types/editor.types';

interface SlidePreviewProps {
  slide: EditorSlide | null;
  isVisible: boolean;
}

/**
 * Calculate content length from HTML string (strips tags)
 */
const getContentLength = (html: string): number => {
  const tmp = document.createElement("div");
  tmp.innerHTML = html;
  return tmp.textContent?.length || 0;
};

/**
 * Determine font size class based on content length - PREVIEW VERSION
 */
const getPreviewFontSizeClass = (contentLength: number): string => {
  if (contentLength < 100) return "preview-text-xl";
  if (contentLength < 300) return "preview-text-lg";
  if (contentLength < 600) return "preview-text-md";
  if (contentLength < 1000) return "preview-text-sm";
  return "preview-text-xs";
};

export function SlidePreview({ slide, isVisible }: SlidePreviewProps) {
  const [renderedContent, setRenderedContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const { getCache, setCache } = usePreviewCache(slide?.tempId || 'unknown');

  // Dark mode detection
  useEffect(() => {
    const checkDarkMode = () => {
      setIsDarkMode(document.documentElement.classList.contains('dark'));
    };
    checkDarkMode();
    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });
    return () => observer.disconnect();
  }, []);

  // SINGLE EFFECT - handles slide changes AND content changes
  useEffect(() => {
    // No slide or not visible = clear and bail
    if (!slide || !isVisible || !slide.content) {
      setRenderedContent('');
      setIsLoading(false);
      return;
    }

    // Check cache FIRST - instant return, no loading state
    const cached = getCache(slide.content);
    if (cached) {
      setRenderedContent(cached);
      setIsLoading(false);
      return;
    }

    // Not cached - debounce the fetch to avoid rate limiting
    const controller = new AbortController();
    setIsLoading(true);

    // Wait 500ms before fetching to batch rapid slide switches
    const timeoutId = setTimeout(() => {
      const fetchPreview = async () => {
        try {
          const rendered = await previewMarkdown(slide.content, controller.signal);
          // Only update if this request wasn't aborted
          if (!controller.signal.aborted) {
            setRenderedContent(rendered);
            setCache(slide.content, rendered);
            setIsLoading(false);
          }
        } catch (err: any) {
          // Ignore abort errors - that's expected behavior
          if (err.name === 'AbortError' || controller.signal.aborted) {
            return;
          }
          console.error('Preview fetch error:', err);
          if (!controller.signal.aborted) {
            // Handle rate limiting specifically
            if (err.response?.status === 429) {
              toast.error('Too many preview requests - please wait a moment');
            } else {
              toast.error('Preview unavailable');
            }
            setIsLoading(false);
          }
        }
      };

      fetchPreview();
    }, 500);

    // CLEANUP: Cancel timeout and abort request if slide changes or component unmounts
    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [slide?.tempId, slide?.content, isVisible, getCache, setCache]);

  // Calculate preview font size class based on content length
  const fontSizeClass = useMemo(() => {
    if (!renderedContent) return "preview-text-lg";
    const contentLength = getContentLength(renderedContent);
    return getPreviewFontSizeClass(contentLength);
  }, [renderedContent]);

  if (!isVisible || !slide) {
    return null;
  }

  return (
    <div className="h-full flex flex-col border-l border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-5 flex items-center justify-center">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Preview</h3>
      </div>

      {/* Preview area - fills remaining space */}
      <div className="flex-1 flex items-center justify-center px-4 overflow-auto relative">
        <div className="w-full h-full max-w-6xl">
          {/* Preview container matching presentation aspect ratio */}
          <div className={`w-full h-full rounded-lg shadow-xl overflow-auto ${
            isDarkMode ? 'bg-gray-900' : 'bg-white'
          }`}>
            {/* Content - matches SlideDisplay structure with preview classes */}
            <div className="h-full overflow-y-auto flex items-center justify-center p-12">
              <div className={`w-full text-center ${fontSizeClass}`}>
                <div className="text-gray-900 dark:text-white slide-content prose-headings:text-gray-900 dark:prose-headings:text-white prose-p:text-gray-900 dark:prose-p:text-white prose-li:text-gray-900 dark:prose-li:text-white">
                  {renderedContent ? (
                    <div dangerouslySetInnerHTML={{ __html: renderedContent }} />
                  ) : (
                    <div className={`text-center py-20 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                      <p>Preview will appear here</p>
                      <p className="text-sm mt-2">Start typing to see your slide</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading spinner overlay */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20 dark:bg-black/40 backdrop-blur-sm">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 flex flex-col items-center gap-3">
              <div className="w-12 h-12 border-4 border-blue-200 dark:border-blue-900 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Rendering preview...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
