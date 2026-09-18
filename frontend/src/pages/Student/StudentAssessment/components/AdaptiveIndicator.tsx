interface AdaptiveIndicatorProps {
  contextBadge?: string;
}

export function AdaptiveIndicator({ contextBadge }: AdaptiveIndicatorProps) {
  return (
    <div className="gf-adaptive-indicator" role="status">
      <div className="gf-adaptive-indicator__icon" aria-hidden="true">
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
          <path d="M5 3v4" />
          <path d="M19 17v4" />
          <path d="M3 5h4" />
          <path d="M17 19h4" />
        </svg>
      </div>
      <div className="gf-adaptive-indicator__text">
        <strong>Project-Specific Question</strong>
        <span>
          {contextBadge
            ? `Context: ${contextBadge}. This question adapts to your project's technical specifications and earlier responses.`
            : 'This question adapts sequentially based on your project definition, complexity, and earlier architectural choices.'}
        </span>
      </div>
    </div>
  );
}
