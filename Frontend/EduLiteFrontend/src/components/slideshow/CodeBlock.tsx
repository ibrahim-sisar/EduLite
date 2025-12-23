import React, { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus, vs } from "react-syntax-highlighter/dist/esm/styles/prism";
import { HiClipboard, HiCheck } from "react-icons/hi2";

interface CodeBlockProps {
  code: string;
  language?: string;
  isDarkMode?: boolean;
}

/**
 * CodeBlock Component
 *
 * Renders code with:
 * - Syntax highlighting
 * - Language label
 * - Copy button
 * - Horizontal scroll for long lines
 */
const CodeBlock: React.FC<CodeBlockProps> = ({ code, language = "text", isDarkMode = false }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code:", err);
    }
  };

  // Normalize language name for display
  const displayLanguage = language.toLowerCase();

  // Map common language aliases to proper names
  const languageMap: Record<string, string> = {
    js: "javascript",
    ts: "typescript",
    py: "python",
    rb: "ruby",
    sh: "bash",
    yml: "yaml",
    md: "markdown",
  };

  const normalizedLanguage = languageMap[displayLanguage] || displayLanguage;

  return (
    <div className="code-block-wrapper relative group my-6">
      {/* Header with language label and copy button */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-200 dark:bg-gray-800 border-b border-gray-300 dark:border-gray-700 rounded-t-lg">
        <span className="text-xs font-mono font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
          {normalizedLanguage}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white bg-gray-300/50 dark:bg-gray-700/50 hover:bg-gray-300 dark:hover:bg-gray-700 rounded transition-all duration-200 cursor-pointer"
          aria-label="Copy code"
          title="Copy code"
        >
          {copied ? (
            <>
              <HiCheck className="w-4 h-4 text-green-400" />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <HiClipboard className="w-4 h-4" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code content with syntax highlighting */}
      <div className="code-block-content relative overflow-auto rounded-b-lg max-h-[32rem]">
        <SyntaxHighlighter
          language={normalizedLanguage}
          style={isDarkMode ? vscDarkPlus : vs}
          customStyle={{
            margin: 0,
            borderRadius: 0,
            background: isDarkMode ? "#1e1e1e" : "#f5f5f5",
            fontSize: "0.9rem",
            lineHeight: "1.5",
            padding: "1.25rem",
          }}
          showLineNumbers={true}
          wrapLines={false}
          wrapLongLines={false}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
};

export default CodeBlock;
