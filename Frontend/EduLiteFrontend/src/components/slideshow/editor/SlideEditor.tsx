import { useRef, useCallback } from "react";
import TextareaAutosize from "react-textarea-autosize";
import { EditorToolbar } from "./EditorToolbar";
import type { EditorSlide } from "../../../types/editor.types";

// Regex patterns for list detection
const UNORDERED_LIST_REGEX = /^(\s*)([-*+])\s/;
const ORDERED_LIST_REGEX = /^(\s*)(\d+)\.\s/;

interface SlideEditorProps {
  slide: EditorSlide | null;
  onChange: (updates: Partial<EditorSlide>) => void;
}

export function SlideEditor({ slide, onChange }: SlideEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleInsert = (before: string, after: string, defaultText = "") => {
    const textarea = textareaRef.current;
    if (!textarea || !slide) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const value = textarea.value;
    const selectedText = value.substring(start, end) || defaultText;

    const newValue =
      value.substring(0, start) +
      before +
      selectedText +
      after +
      value.substring(end);
    const newCursorPos = start + before.length + selectedText.length;

    onChange({ content: newValue });

    // Set cursor position after React updates
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  // Handle Enter key for list continuation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key !== "Enter" || !slide) return;

      const textarea = e.currentTarget;
      const value = textarea.value;
      const cursorPos = textarea.selectionStart;

      // Find the current line
      const lineStart = value.lastIndexOf("\n", cursorPos - 1) + 1;
      const lineEnd = value.indexOf("\n", cursorPos);
      const currentLine = value.substring(
        lineStart,
        lineEnd === -1 ? value.length : lineEnd,
      );

      // Check for unordered list
      const unorderedMatch = currentLine.match(UNORDERED_LIST_REGEX);
      if (unorderedMatch) {
        const [fullMatch, indent, bullet] = unorderedMatch;
        const lineContent = currentLine.substring(fullMatch.length);

        // If the line is empty (just the bullet), remove it and don't continue the list
        if (lineContent.trim() === "") {
          e.preventDefault();
          const newValue =
            value.substring(0, lineStart) +
            "\n" +
            value.substring(lineEnd === -1 ? value.length : lineEnd + 1);
          onChange({ content: newValue });
          setTimeout(() => {
            textarea.setSelectionRange(lineStart + 1, lineStart + 1);
          }, 0);
          return;
        }

        // Continue the list
        e.preventDefault();
        const insertion = `\n${indent}${bullet} `;
        const newValue =
          value.substring(0, cursorPos) +
          insertion +
          value.substring(cursorPos);
        onChange({ content: newValue });
        setTimeout(() => {
          const newPos = cursorPos + insertion.length;
          textarea.setSelectionRange(newPos, newPos);
        }, 0);
        return;
      }

      // Check for ordered list
      const orderedMatch = currentLine.match(ORDERED_LIST_REGEX);
      if (orderedMatch) {
        const [fullMatch, indent, num] = orderedMatch;
        const lineContent = currentLine.substring(fullMatch.length);

        // If the line is empty (just the number), remove it and don't continue the list
        if (lineContent.trim() === "") {
          e.preventDefault();
          const newValue =
            value.substring(0, lineStart) +
            "\n" +
            value.substring(lineEnd === -1 ? value.length : lineEnd + 1);
          onChange({ content: newValue });
          setTimeout(() => {
            textarea.setSelectionRange(lineStart + 1, lineStart + 1);
          }, 0);
          return;
        }

        // Continue the list with incremented number
        e.preventDefault();
        const nextNum = parseInt(num, 10) + 1;
        const insertion = `\n${indent}${nextNum}. `;
        const newValue =
          value.substring(0, cursorPos) +
          insertion +
          value.substring(cursorPos);
        onChange({ content: newValue });
        setTimeout(() => {
          const newPos = cursorPos + insertion.length;
          textarea.setSelectionRange(newPos, newPos);
        }, 0);
        return;
      }
    },
    [slide, onChange],
  );

  if (!slide) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <p className="text-lg font-medium">No slide selected</p>
          <p className="text-sm mt-2">
            Select a slide from the left or create a new one
          </p>
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
          onKeyDown={handleKeyDown}
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
    </div>
  );
}
