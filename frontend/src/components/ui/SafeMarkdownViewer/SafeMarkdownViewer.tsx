import React, { useMemo } from 'react';
import './SafeMarkdownViewer.css';

interface SafeMarkdownViewerProps {
  content: string;
  className?: string;
}

/**
 * Sanitizes a URL to prevent javascript: or data: XSS vectors.
 */
function sanitizeUrl(rawUrl: string): string {
  const trimmed = rawUrl.trim();
  if (/^(https?:\/\/|mailto:|\/|#)/i.test(trimmed)) {
    return trimmed;
  }
  return '#';
}

/**
 * Parses inline formatting: **bold**, *italic*, `code`, and [text](url).
 */
function renderInlineFormatted(text: string): React.ReactNode[] {
  const tokens: React.ReactNode[] = [];
  // Tokenize regex matching bold, code, link, italic
  const regex = /(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|\*[^*]+\*)/g;
  const parts = text.split(regex);

  parts.forEach((part, index) => {
    if (!part) return;

    if (part.startsWith('**') && part.endsWith('**')) {
      tokens.push(<strong key={index}>{part.slice(2, -2)}</strong>);
    } else if (part.startsWith('`') && part.endsWith('`')) {
      tokens.push(<code key={index} className="gf-markdown-inline-code">{part.slice(1, -1)}</code>);
    } else if (part.startsWith('[') && part.includes('](') && part.endsWith(')')) {
      const linkMatch = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (linkMatch) {
        const linkText = linkMatch[1] || '';
        const linkUrl = sanitizeUrl(linkMatch[2] || '');
        tokens.push(
          <a
            key={index}
            href={linkUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="gf-markdown-link"
          >
            {linkText}
          </a>
        );
      } else {
        tokens.push(part);
      }
    } else if (part.startsWith('*') && part.endsWith('*')) {
      tokens.push(<em key={index}>{part.slice(1, -1)}</em>);
    } else {
      tokens.push(part);
    }
  });

  return tokens;
}

/**
 * Safe, zero-dependency Markdown viewer.
 * Converts markdown text into semantic React elements with secure table scrolling.
 */
export function SafeMarkdownViewer({ content, className = '' }: SafeMarkdownViewerProps) {
  const renderedElements = useMemo(() => {
    if (!content) {
      return [<p key="empty" className="gf-markdown-empty">No content available.</p>];
    }

    const lines = content.split(/\r?\n/);
    const elements: React.ReactNode[] = [];
    let i = 0;

    while (i < lines.length) {
      const line = lines[i] ?? '';
      const trimmed = line.trim();

      // 1. Empty lines
      if (!trimmed) {
        i++;
        continue;
      }

      // 2. Fenced Code Blocks (```lang ... ```)
      if (trimmed.startsWith('```')) {
        const lang = trimmed.slice(3).trim();
        const codeLines: string[] = [];
        i++;
        while (i < lines.length && !(lines[i] ?? '').trim().startsWith('```')) {
          codeLines.push(lines[i] ?? '');
          i++;
        }
        if (i < lines.length) i++; // skip closing ```
        elements.push(
          <div key={`code-${i}`} className="gf-markdown-code-wrapper">
            {lang && <div className="gf-markdown-code-lang">{lang}</div>}
            <pre className="gf-markdown-code-block">
              <code>{codeLines.join('\n')}</code>
            </pre>
          </div>
        );
        continue;
      }

      // 3. Headings
      if (trimmed.startsWith('# ')) {
        elements.push(<h1 key={`h1-${i}`} className="gf-markdown-h1">{renderInlineFormatted(trimmed.slice(2))}</h1>);
        i++;
        continue;
      }
      if (trimmed.startsWith('## ')) {
        elements.push(<h2 key={`h2-${i}`} className="gf-markdown-h2">{renderInlineFormatted(trimmed.slice(3))}</h2>);
        i++;
        continue;
      }
      if (trimmed.startsWith('### ')) {
        elements.push(<h3 key={`h3-${i}`} className="gf-markdown-h3">{renderInlineFormatted(trimmed.slice(4))}</h3>);
        i++;
        continue;
      }
      if (trimmed.startsWith('#### ')) {
        elements.push(<h4 key={`h4-${i}`} className="gf-markdown-h4">{renderInlineFormatted(trimmed.slice(5))}</h4>);
        i++;
        continue;
      }

      // 4. Horizontal Dividers
      if (trimmed === '---' || trimmed === '***') {
        elements.push(<hr key={`hr-${i}`} className="gf-markdown-divider" />);
        i++;
        continue;
      }

      // 5. Blockquotes
      if (trimmed.startsWith('> ')) {
        elements.push(
          <blockquote key={`quote-${i}`} className="gf-markdown-blockquote">
            {renderInlineFormatted(trimmed.slice(2))}
          </blockquote>
        );
        i++;
        continue;
      }

      // 6. Tables (| col | col |)
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        const tableLines: string[] = [];
        while (i < lines.length && (lines[i] ?? '').trim().startsWith('|') && (lines[i] ?? '').trim().endsWith('|')) {
          tableLines.push((lines[i] ?? '').trim());
          i++;
        }

        if (tableLines.length >= 2) {
          const headerCells = (tableLines[0] ?? '').slice(1, -1).split('|').map((c) => c.trim());
          // Check if line 1 is separator | :--- | :--- |
          const isSeparator = /^\|?[\s:-|]+\|?$/.test(tableLines[1] ?? '');
          const dataRows = isSeparator ? tableLines.slice(2) : tableLines.slice(1);

          elements.push(
            <div key={`table-${i}`} className="gf-markdown-table-wrapper">
              <table className="gf-markdown-table">
                <thead>
                  <tr>
                    {headerCells.map((headerText, thIdx) => (
                      <th key={thIdx} className="gf-markdown-th">
                        {renderInlineFormatted(headerText)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dataRows.map((rowLine, rowIdx) => {
                    const cells = rowLine.slice(1, -1).split('|').map((c) => c.trim());
                    return (
                      <tr key={rowIdx} className="gf-markdown-tr">
                        {cells.map((cellText, cellIdx) => (
                          <td key={cellIdx} className="gf-markdown-td">
                            {renderInlineFormatted(cellText)}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          );
          continue;
        }
      }

      // 7. Unordered Lists (- or *)
      if (/^[-*]\s+/.test(trimmed)) {
        const listItems: string[] = [];
        while (i < lines.length && /^[-*]\s+/.test((lines[i] ?? '').trim())) {
          listItems.push((lines[i] ?? '').trim().replace(/^[-*]\s+/, ''));
          i++;
        }
        elements.push(
          <ul key={`ul-${i}`} className="gf-markdown-ul">
            {listItems.map((item, liIdx) => (
              <li key={liIdx} className="gf-markdown-li">
                {renderInlineFormatted(item)}
              </li>
            ))}
          </ul>
        );
        continue;
      }

      // 8. Ordered Lists (1. 2.)
      if (/^\d+\.\s+/.test(trimmed)) {
        const listItems: string[] = [];
        while (i < lines.length && /^\d+\.\s+/.test((lines[i] ?? '').trim())) {
          listItems.push((lines[i] ?? '').trim().replace(/^\d+\.\s+/, ''));
          i++;
        }
        elements.push(
          <ol key={`ol-${i}`} className="gf-markdown-ol">
            {listItems.map((item, liIdx) => (
              <li key={liIdx} className="gf-markdown-li">
                {renderInlineFormatted(item)}
              </li>
            ))}
          </ol>
        );
        continue;
      }

      // 9. Regular Paragraph
      elements.push(
        <p key={`p-${i}`} className="gf-markdown-p">
          {renderInlineFormatted(trimmed)}
        </p>
      );
      i++;
    }

    return elements;
  }, [content]);

  return (
    <div className={`gf-markdown-viewer ${className}`}>
      {renderedElements}
    </div>
  );
}
