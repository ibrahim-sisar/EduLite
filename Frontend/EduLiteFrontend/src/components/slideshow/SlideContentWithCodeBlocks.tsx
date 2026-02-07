import React, { useMemo, useRef, useEffect } from "react";
import type { CodeBlockData } from "../../utils/slideContent";
import CodeBlock from "./CodeBlock";

interface SlideContentWithCodeBlocksProps {
  processedHtml: string;
  codeBlocks: CodeBlockData[];
  isDarkMode: boolean;
}

/**
 * Renders HTML content with code blocks replaced by syntax-highlighted CodeBlock components.
 * Also handles accordion interactivity for Spellbook accordion widgets.
 */
const SlideContentWithCodeBlocks: React.FC<SlideContentWithCodeBlocksProps> = ({
  processedHtml,
  codeBlocks,
  isDarkMode,
}) => {
  const contentContainerRef = useRef<HTMLDivElement>(null);
  const accordionStatesRef = useRef<Map<number, boolean>>(new Map());

  // Add accordion functionality and remove inline onclick handlers
  useEffect(() => {
    if (!contentContainerRef.current) return;

    const container = contentContainerRef.current;

    // Remove inline onclick attributes and apply correct state
    const accordionButtons = container.querySelectorAll(".sb-accordion-toggle");
    accordionButtons.forEach((button, index) => {
      button.removeAttribute("onclick");

      // Use saved state if user has toggled, otherwise respect the server-rendered default
      const savedState = accordionStatesRef.current.get(index);
      const isExpanded =
        savedState ?? button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", isExpanded ? "true" : "false");
      const content = button.nextElementSibling;
      if (content && content.classList.contains("sb-accordion-content")) {
        content.setAttribute("aria-hidden", isExpanded ? "false" : "true");
      }
    });

    const handleAccordionClick = (e: Event) => {
      const target = e.target as HTMLElement;
      const button = target.closest(".sb-accordion-toggle");

      if (button) {
        e.preventDefault();
        e.stopPropagation();

        const isExpanded = button.getAttribute("aria-expanded") === "true";
        const newState = !isExpanded;

        button.setAttribute("aria-expanded", newState ? "true" : "false");

        const content = button.nextElementSibling;
        if (content && content.classList.contains("sb-accordion-content")) {
          content.setAttribute("aria-hidden", newState ? "false" : "true");
        }

        // Save the state
        const allButtons = Array.from(
          container.querySelectorAll(".sb-accordion-toggle"),
        );
        const index = allButtons.indexOf(button as Element);
        if (index !== -1) {
          accordionStatesRef.current.set(index, newState);
        }
      }
    };

    container.addEventListener("click", handleAccordionClick);

    return () => {
      container.removeEventListener("click", handleAccordionClick);
    };
  }, [processedHtml, isDarkMode]);

  // Split HTML by code block placeholders and render parts with code blocks
  const parts = useMemo(() => {
    const result: React.ReactNode[] = [];

    // Create a map of code blocks by ID for quick lookup
    const codeBlockMap = new Map(codeBlocks.map((cb) => [cb.id, cb]));

    // Split by placeholder divs
    const placeholderRegex =
      /<div[^>]*data-code-block-id="([^"]+)"[^>]*><\/div>/g;
    let lastIndex = 0;
    let match;

    while ((match = placeholderRegex.exec(processedHtml)) !== null) {
      const [fullMatch, codeBlockId] = match;
      const matchIndex = match.index;

      // Add HTML before this code block
      if (matchIndex > lastIndex) {
        const htmlPart = processedHtml.substring(lastIndex, matchIndex);
        result.push(
          <div
            key={`html-${lastIndex}`}
            dangerouslySetInnerHTML={{ __html: htmlPart }}
          />,
        );
      }

      // Add the code block component
      const codeBlockData = codeBlockMap.get(codeBlockId);
      if (codeBlockData) {
        result.push(
          <CodeBlock
            key={codeBlockId}
            code={codeBlockData.code}
            language={codeBlockData.language}
            isDarkMode={isDarkMode}
          />,
        );
      }

      lastIndex = matchIndex + fullMatch.length;
    }

    // Add remaining HTML after last code block
    if (lastIndex < processedHtml.length) {
      const htmlPart = processedHtml.substring(lastIndex);
      result.push(
        <div
          key={`html-${lastIndex}`}
          dangerouslySetInnerHTML={{ __html: htmlPart }}
        />,
      );
    }

    return result;
  }, [processedHtml, codeBlocks, isDarkMode]);

  return <div ref={contentContainerRef}>{parts}</div>;
};

export default SlideContentWithCodeBlocks;
