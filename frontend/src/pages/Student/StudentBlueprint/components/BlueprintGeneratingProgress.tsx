import {
  CANONICAL_BLUEPRINT_SECTION_LABELS,
  type BlueprintSectionKey,
  type BlueprintGenerationProgress,
  type BlueprintStatusResponse,
} from '@/lib/api/types';
import { Button } from '@/components/ui/Button';

export interface BlueprintGeneratingProgressProps {
  progress?: BlueprintGenerationProgress;
  status?: BlueprintStatusResponse | null;
  currentStep?: string | null;
  progressPercent?: number | null;
  regenerationAttempt?: number | null;
  regenerationTarget?: string | null;
  qaScore?: number | null;
  qaStatus?: string | null;
  onCancelRequest?: () => void;
  isCancelling?: boolean;
}

export function BlueprintGeneratingProgress({
  progress: directProgress,
  status,
  currentStep: directCurrentStep,
  progressPercent: directProgressPercent,
  regenerationAttempt: directRegenAttempt,
  regenerationTarget: directRegenTarget,
  qaScore: directQaScore,
  qaStatus: directQaStatus,
  onCancelRequest,
  isCancelling = false,
}: BlueprintGeneratingProgressProps) {
  const progress = directProgress || status?.generation_progress;
  const completed = progress?.completed_sections || [];
  const total = progress?.total_sections || 10;
  const inProgress = progress?.in_progress_section;
  const failed = progress?.failed_sections || [];

  const completedCount = completed.length;

  const effectiveCurrentStep = directCurrentStep ?? status?.current_step ?? null;
  const effectiveProgressPercent = directProgressPercent ?? status?.progress_percent ?? null;
  const effectiveRegenAttempt = directRegenAttempt ?? status?.regeneration_attempt ?? 0;
  const effectiveRegenTarget = directRegenTarget ?? status?.regeneration_target ?? null;
  const effectiveQaScore = directQaScore ?? status?.qa_score ?? null;
  const effectiveQaStatus = directQaStatus ?? status?.qa_status ?? null;

  // Prefer backend progress_percent if provided, otherwise fallback to completedCount / total * 100
  const percent =
    effectiveProgressPercent != null
      ? Math.min(100, Math.max(0, Math.round(effectiveProgressPercent)))
      : Math.min(100, Math.round((completedCount / total) * 100));

  const isStepActive = (key: BlueprintSectionKey) => {
    if (inProgress === key) return true;
    if (!effectiveCurrentStep) return false;
    if (effectiveCurrentStep === key) return true;
    if (key === 'tech_stack' && (effectiveCurrentStep === 'technology' || effectiveCurrentStep === 'tech_stack')) return true;
    if (key === 'features' && effectiveCurrentStep === 'features') return true;
    if (key === 'mvp' && effectiveCurrentStep === 'mvp') return true;
    if (key === 'specifications' && (effectiveCurrentStep === 'specification' || effectiveCurrentStep === 'specifications')) return true;
    if (key === 'duration' && (effectiveCurrentStep === 'timeline' || effectiveCurrentStep === 'duration')) return true;
    if (key === 'risks' && (effectiveCurrentStep === 'risk' || effectiveCurrentStep === 'risks')) return true;
    if (key === 'tasks' && (effectiveCurrentStep === 'task' || effectiveCurrentStep === 'tasks')) return true;
    if (key === 'milestones' && (effectiveCurrentStep === 'milestone' || effectiveCurrentStep === 'milestones')) return true;
    if (key === 'project_profile' && (effectiveCurrentStep === 'idea' || effectiveCurrentStep === 'scope' || effectiveCurrentStep === 'project_profile')) return true;
    return false;
  };

  const getSectionState = (key: BlueprintSectionKey) => {
    if (completed.includes(key)) return 'COMPLETED';
    if (failed.includes(key)) return 'FAILED';
    if (isStepActive(key)) return 'IN_PROGRESS';
    return 'PENDING';
  };

  const getQAState = () => {
    const normalized = effectiveQaStatus?.toUpperCase();
    if (normalized === 'PASSED' || normalized === 'PASS') return 'COMPLETED';
    if (normalized === 'FAILED' || normalized === 'FAIL') return 'FAILED';
    if (effectiveCurrentStep === 'qa_judge') return 'IN_PROGRESS';
    if (completed.length === 10) return 'IN_PROGRESS';
    return 'PENDING';
  };

  const qaState = getQAState();

  const targetLabel = effectiveRegenTarget
    ? CANONICAL_BLUEPRINT_SECTION_LABELS[effectiveRegenTarget as BlueprintSectionKey] ||
      (effectiveRegenTarget === 'timeline' ? 'Timeline & Sprint Duration' : effectiveRegenTarget)
    : 'the affected section';

  // Parallel group keys
  const parallelKeys: { key: BlueprintSectionKey; title: string; subtitle: string }[] = [
    { key: 'tech_stack', title: 'Technology', subtitle: 'Tech Stack & Architecture' },
    { key: 'features', title: 'Features', subtitle: 'Core Features & Modules' },
    { key: 'mvp', title: 'MVP', subtitle: 'MVP Scope & Validation' },
  ];

  const isParallelActive =
    parallelKeys.some((p) => isStepActive(p.key)) ||
    effectiveCurrentStep === 'technology' ||
    effectiveCurrentStep === 'features' ||
    effectiveCurrentStep === 'mvp';

  const isParallelCompleted = parallelKeys.every((p) => completed.includes(p.key));

  return (
    <div className="gf-blueprint-generating">
      {/* Targeted Refinement Notice */}
      {effectiveRegenAttempt > 0 && (
        <div
          className="gf-blueprint-refinement-banner"
          role="alert"
          data-testid="targeted-refinement-notice"
        >
          <div className="gf-blueprint-refinement-banner__icon">
            <svg
              viewBox="0 0 24 24"
              width="22"
              height="22"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
          </div>
          <div className="gf-blueprint-refinement-banner__content">
            <strong>Targeted Refinement in Progress</strong> (Attempt {effectiveRegenAttempt} of 2)
            <p style={{ margin: '4px 0 0', fontSize: '0.875rem' }}>
              The QA Judge identified opportunities to strengthen the {targetLabel}. Upstream sections remain preserved while this section is being refined.
            </p>
          </div>
        </div>
      )}

      <div className="gf-blueprint-card gf-blueprint-progress-card">
        <div className="gf-blueprint-progress-card__top">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span className="gf-blueprint-badge-subtle">Autonomous Synthesis Active</span>
              {isParallelActive && (
                <span className="gf-blueprint-parallel-badge">Parallel Synthesis</span>
              )}
            </div>
            <h2 className="gf-blueprint-card__title">Generating Architectural Blueprint</h2>
            <p className="gf-blueprint-card__desc">
              Synthesizing domain architecture, technical requirements, and work breakdown. Core architectural sections synthesize in parallel and all outputs are validated against schema invariants.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {onCancelRequest && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onCancelRequest}
                disabled={isCancelling}
                id="cancel-blueprint-generation-btn"
              >
                {isCancelling ? 'Cancelling...' : 'Cancel Generation'}
              </Button>
            )}

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
        </div>

        {/* Linear Progress Track */}
        <div className="gf-blueprint-progress-bar-wrap">
          <div
            className="gf-blueprint-progress-bar-fill"
            style={{ width: `${percent}%` }}
          />
        </div>

        {/* Live announcer for screen readers */}
        <div className="gf-blueprint-sr-only" aria-live="polite">
          {isParallelActive && 'Core architecture parallel synthesis in progress.'}
          {effectiveCurrentStep === 'qa_judge' && 'Architectural QA and schema validation in progress.'}
          {effectiveRegenAttempt > 0 && `Targeted refinement in progress for ${targetLabel}.`}
        </div>

        {/* Section Status Breakdown */}
        <div className="gf-blueprint-checklist" role="region" aria-label="Blueprint Sections Status">
          {/* Step 1: Project Profile */}
          {(() => {
            const state = getSectionState('project_profile');
            return (
              <div
                key="project_profile"
                className={`gf-blueprint-checklist-item gf-blueprint-checklist-item--${state.toLowerCase()}`}
              >
                <div className="gf-blueprint-checklist-item__left">
                  <span className="gf-blueprint-checklist-num">1</span>
                  <div className="gf-blueprint-checklist-item__icon-state">
                    {state === 'COMPLETED' && (
                      <svg className="gf-blueprint-check-icon" viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2.5" fill="none" aria-label="Completed">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    )}
                    {state === 'IN_PROGRESS' && <span className="gf-blueprint-spinner-dot" aria-label="Synthesizing..." />}
                    {state === 'FAILED' && (
                      <svg className="gf-blueprint-fail-icon" viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none" aria-label="Failed">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="15" y1="9" x2="9" y2="15" />
                        <line x1="9" y1="9" x2="15" y2="15" />
                      </svg>
                    )}
                    {state === 'PENDING' && <span className="gf-blueprint-pending-dot" aria-label="Pending" />}
                  </div>
                  <span className="gf-blueprint-checklist-label">{CANONICAL_BLUEPRINT_SECTION_LABELS.project_profile}</span>
                </div>

                <div className="gf-blueprint-checklist-item__badge">
                  {state === 'COMPLETED' && <span className="gf-checklist-badge gf-checklist-badge--success">Synthesized</span>}
                  {state === 'IN_PROGRESS' && <span className="gf-checklist-badge gf-checklist-badge--active">Synthesizing...</span>}
                  {state === 'FAILED' && <span className="gf-checklist-badge gf-checklist-badge--error">Failed</span>}
                  {state === 'PENDING' && <span className="gf-checklist-badge gf-checklist-badge--muted">Queued</span>}
                </div>
              </div>
            );
          })()}

          {/* Parallel Synthesis Group: Technology, Features, MVP */}
          <div
            className="gf-blueprint-checklist-item gf-blueprint-checklist-item--parallel"
            data-testid="parallel-synthesis-group"
          >
            <div className="gf-blueprint-parallel-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="gf-blueprint-checklist-num">2</span>
                <span className="gf-blueprint-checklist-label" style={{ fontWeight: 600 }}>
                  Core Architecture & Scope
                </span>
                <span className="gf-blueprint-parallel-badge">Parallel Synthesis</span>
              </div>
              <div>
                {isParallelCompleted ? (
                  <span className="gf-checklist-badge gf-checklist-badge--success">Completed</span>
                ) : isParallelActive ? (
                  <span className="gf-checklist-badge gf-checklist-badge--active">Synthesizing...</span>
                ) : (
                  <span className="gf-checklist-badge gf-checklist-badge--muted">Queued</span>
                )}
              </div>
            </div>

            <div className="gf-blueprint-parallel-subgrid">
              {parallelKeys.map((item) => {
                const subState = getSectionState(item.key);
                return (
                  <div key={item.key} className="gf-blueprint-parallel-subitem">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div className="gf-blueprint-checklist-item__icon-state">
                        {subState === 'COMPLETED' && (
                          <svg className="gf-blueprint-check-icon" viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2.5" fill="none" aria-label="Completed">
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                        )}
                        {subState === 'IN_PROGRESS' && <span className="gf-blueprint-spinner-dot" aria-label="Synthesizing..." />}
                        {subState === 'FAILED' && (
                          <svg className="gf-blueprint-fail-icon" viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none" aria-label="Failed">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="15" y1="9" x2="9" y2="15" />
                            <line x1="9" y1="9" x2="15" y2="15" />
                          </svg>
                        )}
                        {subState === 'PENDING' && <span className="gf-blueprint-pending-dot" aria-label="Pending" />}
                      </div>
                      <div>
                        <strong>{item.title}</strong>
                        <div style={{ fontSize: '11px', color: 'var(--gf-color-text-secondary)' }}>
                          {item.subtitle}
                        </div>
                      </div>
                    </div>

                    <div>
                      {subState === 'COMPLETED' && <span className="gf-checklist-badge gf-checklist-badge--success">Synthesized</span>}
                      {subState === 'IN_PROGRESS' && <span className="gf-checklist-badge gf-checklist-badge--active">Synthesizing...</span>}
                      {subState === 'FAILED' && <span className="gf-checklist-badge gf-checklist-badge--error">Failed</span>}
                      {subState === 'PENDING' && <span className="gf-checklist-badge gf-checklist-badge--muted">Queued</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sequential Downstream Sections: Specifications through Readme */}
          {(
            [
              'specifications',
              'duration',
              'risks',
              'tasks',
              'milestones',
              'readme',
            ] as BlueprintSectionKey[]
          ).map((sectionKey, index) => {
            const state = getSectionState(sectionKey);
            const label = CANONICAL_BLUEPRINT_SECTION_LABELS[sectionKey];
            const displayNum = index + 3; // After Step 1 (profile) and Step 2 (parallel group)

            return (
              <div
                key={sectionKey}
                className={`gf-blueprint-checklist-item gf-blueprint-checklist-item--${state.toLowerCase()}`}
              >
                <div className="gf-blueprint-checklist-item__left">
                  <span className="gf-blueprint-checklist-num">{displayNum}</span>
                  <div className="gf-blueprint-checklist-item__icon-state">
                    {state === 'COMPLETED' && (
                      <svg className="gf-blueprint-check-icon" viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2.5" fill="none" aria-label="Completed">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    )}
                    {state === 'IN_PROGRESS' && <span className="gf-blueprint-spinner-dot" aria-label="Synthesizing..." />}
                    {state === 'FAILED' && (
                      <svg className="gf-blueprint-fail-icon" viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none" aria-label="Failed">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="15" y1="9" x2="9" y2="15" />
                        <line x1="9" y1="9" x2="15" y2="15" />
                      </svg>
                    )}
                    {state === 'PENDING' && <span className="gf-blueprint-pending-dot" aria-label="Pending" />}
                  </div>
                  <span className="gf-blueprint-checklist-label">{label}</span>
                </div>

                <div className="gf-blueprint-checklist-item__badge">
                  {state === 'COMPLETED' && <span className="gf-checklist-badge gf-checklist-badge--success">Synthesized</span>}
                  {state === 'IN_PROGRESS' && <span className="gf-checklist-badge gf-checklist-badge--active">Synthesizing...</span>}
                  {state === 'FAILED' && <span className="gf-checklist-badge gf-checklist-badge--error">Failed</span>}
                  {state === 'PENDING' && <span className="gf-checklist-badge gf-checklist-badge--muted">Queued</span>}
                </div>
              </div>
            );
          })}

          {/* QA / Judge Step */}
          <div
            key="qa_judge"
            className={`gf-blueprint-checklist-item gf-blueprint-checklist-item--${qaState.toLowerCase()}`}
            data-testid="qa-judge-step"
          >
            <div className="gf-blueprint-checklist-item__left">
              <span className="gf-blueprint-checklist-num">9</span>
              <div className="gf-blueprint-checklist-item__icon-state">
                {qaState === 'COMPLETED' && (
                  <svg className="gf-blueprint-check-icon" viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2.5" fill="none" aria-label="Completed">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                )}
                {qaState === 'IN_PROGRESS' && <span className="gf-blueprint-spinner-dot" aria-label="Evaluating..." />}
                {qaState === 'FAILED' && (
                  <svg className="gf-blueprint-fail-icon" viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none" aria-label="Failed">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="15" y1="9" x2="9" y2="15" />
                    <line x1="9" y1="9" x2="15" y2="15" />
                  </svg>
                )}
                {qaState === 'PENDING' && <span className="gf-blueprint-pending-dot" aria-label="Pending" />}
              </div>
              <span className="gf-blueprint-checklist-label">
                Architectural QA & Schema Validation
                {effectiveQaScore != null && (
                  <span style={{ marginLeft: '8px', fontSize: '12px', color: 'var(--gf-color-accent)', fontWeight: 600 }}>
                    (Score: {effectiveQaScore}/100)
                  </span>
                )}
              </span>
            </div>

            <div className="gf-blueprint-checklist-item__badge">
              {qaState === 'COMPLETED' && <span className="gf-checklist-badge gf-checklist-badge--success">Passed</span>}
              {qaState === 'IN_PROGRESS' && <span className="gf-checklist-badge gf-checklist-badge--active">Evaluating...</span>}
              {qaState === 'FAILED' && <span className="gf-checklist-badge gf-checklist-badge--error">Failed</span>}
              {qaState === 'PENDING' && <span className="gf-checklist-badge gf-checklist-badge--muted">Queued</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
