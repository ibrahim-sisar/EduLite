import { RefObject } from 'react';
import {
  HiCode,
  HiLink,
  HiPhotograph,
} from 'react-icons/hi';

interface EditorToolbarProps {
  textareaRef: RefObject<HTMLTextAreaElement | null>;
  onInsert: (before: string, after: string, defaultText?: string) => void;
}

export function EditorToolbar({ textareaRef, onInsert }: EditorToolbarProps) {
  const handleBold = () => onInsert('**', '**', 'bold text');
  const handleItalic = () => onInsert('_', '_', 'italic text');
  const handleH1 = () => insertAtLineStart('# ');
  const handleH2 = () => insertAtLineStart('## ');
  const handleH3 = () => insertAtLineStart('### ');
  const handleBulletList = () => insertAtLineStart('- ');
  const handleNumberedList = () => insertAtLineStart('1. ');
  const handleLink = () => onInsert('[', '](url)', 'link text');
  const handleImage = () => onInsert('![', '](url)', 'alt text');
  const handleCodeBlock = () => onInsert('\n```\n', '\n```\n', 'code here');

  const insertAtLineStart = (text: string) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const value = textarea.value;

    // Find the start of the current line
    const lineStart = value.lastIndexOf('\n', start - 1) + 1;

    // Insert text at line start
    const before = value.substring(0, lineStart);
    const after = value.substring(lineStart);
    const newValue = before + text + after;

    textarea.value = newValue;
    textarea.selectionStart = textarea.selectionEnd = lineStart + text.length;
    textarea.focus();

    // Trigger change event
    const event = new Event('input', { bubbles: true });
    textarea.dispatchEvent(event);
  };

  const buttons = [
    { icon: 'B', label: 'Bold (Ctrl+B)', onClick: handleBold, isText: true },
    { icon: 'I', label: 'Italic (Ctrl+I)', onClick: handleItalic, isText: true },
    { icon: 'H1', label: 'Heading 1', onClick: handleH1, isText: true },
    { icon: 'H2', label: 'Heading 2', onClick: handleH2, isText: true },
    { icon: 'H3', label: 'Heading 3', onClick: handleH3, isText: true },
    { icon: '•', label: 'Bullet List', onClick: handleBulletList, isText: true },
    { icon: '1.', label: 'Numbered List', onClick: handleNumberedList, isText: true },
    { icon: HiLink, label: 'Link', onClick: handleLink },
    { icon: HiPhotograph, label: 'Image', onClick: handleImage },
    { icon: HiCode, label: 'Code Block', onClick: handleCodeBlock },
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
    </div>
  );
}
