import { useRef } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import { EditorToolbar } from './EditorToolbar';
import { SpeakerNotesEditor } from './SpeakerNotesEditor';
import type { EditorSlide } from '../../../types/editor.types';

interface SlideEditorProps {
  slide: EditorSlide | null;
  onChange: (updates: Partial<EditorSlide>) => void;
}

export function SlideEditor({ slide, onChange }: SlideEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleInsert = (before: string, after: string, defaultText = '') => {
    const textarea = textareaRef.current;
    if (!textarea || !slide) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const value = textarea.value;
    const selectedText = value.substring(start, end) || defaultText;

    const newValue = value.substring(0, start) + before + selectedText + after + value.substring(end);
    const newCursorPos = start + before.length + selectedText.length;

    onChange({ content: newValue });

    // Set cursor position after React updates
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  if (!slide) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <p className="text-lg font-medium">No slide selected</p>
          <p className="text-sm mt-2">Select a slide from the left or create a new one</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <EditorToolbar textareaRef={textareaRef} onInsert={handleInsert} />

      <div className="flex-1 overflow-auto p-4">
        <TextareaAutosize
          ref={textareaRef}
          value={slide.content}
          onChange={(e) => onChange({ content: e.target.value })}
          placeholder="# Slide Title

Start typing your slide content here...

You can use markdown:
- **bold**, _italic_
- # headers
- bullet points
- [links](url)
- ![images](url)
- ```code blocks```"
          minRows={10}
          className="w-full px-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 resize-none text-gray-900 dark:text-gray-100 font-mono text-sm leading-relaxed"
        />

        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          {slide.content.length} characters
        </div>
      </div>

      <SpeakerNotesEditor
        notes={slide.notes}
        onChange={(notes) => onChange({ notes })}
      />
    </div>
  );
}
