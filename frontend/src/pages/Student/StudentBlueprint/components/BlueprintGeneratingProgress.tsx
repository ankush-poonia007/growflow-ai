import {
  CANONICAL_BLUEPRINT_SECTION_ORDER,
  CANONICAL_BLUEPRINT_SECTION_LABELS,
  type BlueprintSectionKey,
  type BlueprintGenerationProgress,
} from '@/lib/api/types';

interface BlueprintGeneratingProgressProps {
  progress?: BlueprintGenerationProgress;
}

export function BlueprintGeneratingProgress({
  progress,
}: BlueprintGeneratingProgressProps) {
  const completed = progress?.completed_sections || [];
  const total = progress?.total_sections || 10;
  const inProgress = progress?.in_progress_section;
  const failed = progress?.failed_sections || [];

  const completedCount = completed.length;
  const percent = Math.min(100, Math.round((completedCount / total) * 100));

  const getSectionState = (key: BlueprintSectionKey) => {
    if (completed.includes(key)) return 'COMPLETED';
    if (failed.includes(key)) return 'FAILED';
    if (inProgress === key) return 'IN_PROGRESS';
    return 'PENDING';
  };

  return (
    <div className="gf-blueprint-generating">
      <div className="gf-blueprint-card gf-blueprint-progress-card">
        <div className="gf-blueprint-progress-card__top">
          <div>
            <span className="gf-blueprint-badge-subtle">Autonomous Synthesis Active</span>
            <h2 className="gf-blueprint-card__title">Generating Architectural Blueprint</h2>
            <p className="gf-blueprint-card__desc">
              Synthesizing domain architecture, technical requirements, and work breakdown. Each section
              is generated sequentially and validated against schema invariants.
            </p>
          </div>

          <div className="gf-blueprint-progress-circle-wrap">
            <div
              className="gf-blueprint-progress-circle"
              role="progressbar"
              aria-valuenow={percent}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Blueprint generation progress"
            >
              <span className="gf-blueprint-progress-percent">{percent}%</span>
              <span className="gf-blueprint-progress-count">
                {completedCount} of {total}
              </span>
            </div>
          </div>
        </div>

        {/* Linear Progress Track */}
        <div className="gf-blueprint-progress-bar-wrap">
          <div
            className="gf-blueprint-progress-bar-fill"
            style={{ width: `${percent}%` }}
          />
        </div>

        {/* 10 Canonical Section Status Breakdown */}
        <div className="gf-blueprint-checklist" role="region" aria-label="Blueprint Sections Status">
          {CANONICAL_BLUEPRINT_SECTION_ORDER.map((sectionKey, idx) => {
            const state = getSectionState(sectionKey);
            const label = CANONICAL_BLUEPRINT_SECTION_LABELS[sectionKey];

            return (
              <div
                key={sectionKey}
                className={`gf-blueprint-checklist-item gf-blueprint-checklist-item--${state.toLowerCase()}`}
              >
                <div className="gf-blueprint-checklist-item__left">
                  <span className="gf-blueprint-checklist-num">{idx + 1}</span>
                  <div className="gf-blueprint-checklist-item__icon-state">
                    {state === 'COMPLETED' && (
                      <svg
                        className="gf-blueprint-check-icon"
                        viewBox="0 0 24 24"
                        width="18"
                        height="18"
                        stroke="currentColor"
                        strokeWidth="2.5"
                        fill="none"
                        aria-label="Completed"
                      >
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    )}
                    {state === 'IN_PROGRESS' && (
                      <span
                        className="gf-blueprint-spinner-dot"
                        aria-label="Synthesizing..."
                      />
                    )}
                    {state === 'FAILED' && (
                      <svg
                        className="gf-blueprint-fail-icon"
                        viewBox="0 0 24 24"
                        width="18"
                        height="18"
                        stroke="currentColor"
                        strokeWidth="2"
                        fill="none"
                        aria-label="Failed"
                      >
                        <circle cx="12" cy="12" r="10" />
                        <line x1="15" y1="9" x2="9" y2="15" />
                        <line x1="9" y1="9" x2="15" y2="15" />
                      </svg>
                    )}
                    {state === 'PENDING' && (
                      <span className="gf-blueprint-pending-dot" aria-label="Pending" />
                    )}
                  </div>
                  <span className="gf-blueprint-checklist-label">{label}</span>
                </div>

                <div className="gf-blueprint-checklist-item__badge">
                  {state === 'COMPLETED' && (
                    <span className="gf-checklist-badge gf-checklist-badge--success">Synthesized</span>
                  )}
                  {state === 'IN_PROGRESS' && (
                    <span className="gf-checklist-badge gf-checklist-badge--active">Synthesizing...</span>
                  )}
                  {state === 'FAILED' && (
                    <span className="gf-checklist-badge gf-checklist-badge--error">Failed</span>
                  )}
                  {state === 'PENDING' && (
                    <span className="gf-checklist-badge gf-checklist-badge--muted">Queued</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
