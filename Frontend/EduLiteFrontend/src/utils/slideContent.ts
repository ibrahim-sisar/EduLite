export interface CodeBlockData {
  id: string;
  code: string;
  language: string;
}

/**
 * Calculate content length from HTML string (strips tags)
 */
export const getContentLength = (html: string): number => {
  const tmp = document.createElement("div");
  tmp.innerHTML = html;
  return tmp.textContent?.length || 0;
};

/**
 * Determine font size class based on content length.
 * @param prefix - "slide" for presentation view, "preview" for editor preview
 */
export const getFontSizeClass = (
  contentLength: number,
  prefix: "slide" | "preview" = "slide",
): string => {
  const thresholds = [
    [100, "xl"],
    [300, "lg"],
    [600, "md"],
    [1000, "sm"],
  ] as const;

  for (const [max, size] of thresholds) {
    if (contentLength < max) return `${prefix}-text-${size}`;
  }
  return `${prefix}-text-xs`;
};

/**
 * Extract code blocks from HTML and replace them with placeholder divs.
 * Returns the processed HTML and an array of extracted code block data.
 */
export const extractCodeBlocks = (
  html: string,
): { processedHtml: string; codeBlocks: CodeBlockData[] } => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");
  const codeBlocks: CodeBlockData[] = [];

  const preElements = doc.querySelectorAll("pre");

  preElements.forEach((pre, index) => {
    const codeElement = pre.querySelector("code");
    if (codeElement) {
      const codeText = codeElement.textContent || "";

      const className = codeElement.className || "";
      const languageMatch = className.match(/language-(\w+)/);
      const language = languageMatch ? languageMatch[1] : "text";

      const id = `code-block-${index}`;

      codeBlocks.push({ id, code: codeText, language });

      const placeholder = doc.createElement("div");
      placeholder.setAttribute("data-code-block-id", id);
      placeholder.className = "code-block-placeholder";
      pre.replaceWith(placeholder);
    }
  });

  return { processedHtml: doc.body.innerHTML, codeBlocks };
};
