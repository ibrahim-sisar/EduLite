import { RefObject, useState, useEffect, useRef } from "react";
import {
  HiCode,
  HiLink,
  HiPhotograph,
  HiPuzzle,
  HiChevronDown,
} from "react-icons/hi";
import { HiRectangleGroup } from "react-icons/hi2";

interface EditorToolbarProps {
  textareaRef: RefObject<HTMLTextAreaElement | null>;
  onInsert: (before: string, after: string, defaultText?: string) => void;
}

export function EditorToolbar({ textareaRef, onInsert }: EditorToolbarProps) {
  const [showSpellblocks, setShowSpellblocks] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Spellblock insert handlers
  const handleInsertCard = () => {
    onInsert(
      '\n{~ card title="Card Title" footer="Optional Footer" ~}\n',
      "\n{~~}\n",
      "Your content here",
    );
    setShowSpellblocks(false);
  };

  const handleInsertAccordion = () => {
    onInsert(
      '\n{~ accordion title="Accordion Title" open=false ~}\n',
      "\n{~~}\n",
      "Your content here",
    );
    setShowSpellblocks(false);
  };

  // Close dropdown on click outside
  useEffect(() => {
    if (!showSpellblocks) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setShowSpellblocks(false);
      }
    };

    // Use timeout to avoid immediate close from the button click
    const timeoutId = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 0);

    return () => {
      clearTimeout(timeoutId);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [showSpellblocks]);

  // Close dropdown on Escape
  useEffect(() => {
    if (!showSpellblocks) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setShowSpellblocks(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [showSpellblocks]);

  const handleBold = () => onInsert("**", "**", "bold text");
  const handleItalic = () => onInsert("_", "_", "italic text");
  const handleH1 = () => insertAtLineStart("# ");
  const handleH2 = () => insertAtLineStart("## ");
  const handleH3 = () => insertAtLineStart("### ");
  const handleBulletList = () => insertListAtLineStart("- ", "unordered");
  const handleNumberedList = () => insertListAtLineStart("1. ", "ordered");
  const handleLink = () => onInsert("[", "](url)", "link text");
  const handleImage = () => onInsert("![", "](url)", "alt text");
  const handleCodeBlock = () => onInsert("\n```\n", "\n```\n", "code here");

  const insertAtLineStart = (text: string) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const value = textarea.value;

    // Find the start of the current line
    const lineStart = value.lastIndexOf("\n", start - 1) + 1;

    // Insert text at line start
    const before = value.substring(0, lineStart);
    const after = value.substring(lineStart);
    const newValue = before + text + after;

    textarea.value = newValue;
    textarea.selectionStart = textarea.selectionEnd = lineStart + text.length;
    textarea.focus();

    // Trigger change event
    const event = new Event("input", { bubbles: true });
    textarea.dispatchEvent(event);
  };

  // List patterns
  const UNORDERED_LIST_REGEX = /^(\s*)([-*+])\s/;
  const ORDERED_LIST_REGEX = /^(\s*)(\d+)\.\s/;

  const insertListAtLineStart = (
    text: string,
    listType: "ordered" | "unordered",
  ) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const value = textarea.value;

    // Find the current line
    const lineStart = value.lastIndexOf("\n", start - 1) + 1;
    const lineEnd = value.indexOf("\n", start);
    const currentLine = value.substring(
      lineStart,
      lineEnd === -1 ? value.length : lineEnd,
    );

    // Check if we're already in a list
    const unorderedMatch = currentLine.match(UNORDERED_LIST_REGEX);
    const orderedMatch = currentLine.match(ORDERED_LIST_REGEX);

    const currentListType = unorderedMatch
      ? "unordered"
      : orderedMatch
        ? "ordered"
        : null;

    // If we're in a different list type, nest it (add indent)
    if (currentListType && currentListType !== listType) {
      // Get current indentation
      const currentIndent = unorderedMatch
        ? unorderedMatch[1]
        : orderedMatch
          ? orderedMatch[1]
          : "";
      const newIndent = currentIndent + "  "; // Add 2 spaces for nesting

      // Insert nested list on new line
      const insertion = `\n${newIndent}${text}`;
      const newValue =
        value.substring(0, start) + insertion + value.substring(start);

      textarea.value = newValue;
      textarea.selectionStart = textarea.selectionEnd =
        start + insertion.length;
      textarea.focus();

      const event = new Event("input", { bubbles: true });
      textarea.dispatchEvent(event);
      return;
    }

    // Otherwise, just insert at line start as normal
    const before = value.substring(0, lineStart);
    const after = value.substring(lineStart);
    const newValue = before + text + after;

    textarea.value = newValue;
    textarea.selectionStart = textarea.selectionEnd = lineStart + text.length;
    textarea.focus();

    const event = new Event("input", { bubbles: true });
    textarea.dispatchEvent(event);
  };

  const buttons = [
    { icon: "B", label: "Bold (Ctrl+B)", onClick: handleBold, isText: true },
    {
      icon: "I",
      label: "Italic (Ctrl+I)",
      onClick: handleItalic,
      isText: true,
    },
    { icon: "H1", label: "Heading 1", onClick: handleH1, isText: true },
    { icon: "H2", label: "Heading 2", onClick: handleH2, isText: true },
    { icon: "H3", label: "Heading 3", onClick: handleH3, isText: true },
    {
      icon: "•",
      label: "Bullet List",
      onClick: handleBulletList,
      isText: true,
    },
    {
      icon: "1.",
      label: "Numbered List",
      onClick: handleNumberedList,
      isText: true,
    },
    { icon: HiLink, label: "Link", onClick: handleLink },
    { icon: HiPhotograph, label: "Image", onClick: handleImage },
    { icon: HiCode, label: "Code Block", onClick: handleCodeBlock },
  ];

  return (
    <div className="flex flex-wrap items-center justify-center gap-1 py-3 px-2 border-b border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-900/50">
      {buttons.map((button, index) => {
        const Icon = button.icon;
        const isText = button.isText;

        return (
          <button
            key={index}
            type="button"
            onClick={button.onClick}
            title={button.label}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white cursor-pointer"
          >
            {isText ? (
              <span className="text-sm font-semibold">{String(Icon)}</span>
            ) : (
              // @ts-ignore - Icon is a component here
              <Icon className="w-5 h-5" />
            )}
          </button>
        );
      })}

      {/* Spellblocks Dropdown */}
      <div ref={dropdownRef} className="relative">
        <button
          type="button"
          onClick={() => setShowSpellblocks(!showSpellblocks)}
          title="Spellblocks"
          className={`p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white cursor-pointer flex items-center gap-1 ${
            showSpellblocks ? "bg-gray-100 dark:bg-gray-800" : ""
          }`}
        >
          <HiPuzzle className="w-5 h-5" />
          <HiChevronDown
            className={`w-3 h-3 transition-transform ${showSpellblocks ? "rotate-180" : ""}`}
          />
        </button>

        {showSpellblocks && (
          <div className="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 min-w-[160px] z-50">
            <button
              type="button"
              onClick={handleInsertCard}
              className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer flex items-center gap-2"
            >
              <HiRectangleGroup className="w-4 h-4" />
              Card
            </button>
            <button
              type="button"
              onClick={handleInsertAccordion}
              className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer flex items-center gap-2"
            >
              <HiChevronDown className="w-4 h-4" />
              Accordion
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
