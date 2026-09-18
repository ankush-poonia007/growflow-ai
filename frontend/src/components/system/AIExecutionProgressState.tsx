import './SystemStates.css';

export interface AIExecutionProgressStateProps {
  status?: 'QUEUED' | 'RUNNING' | string;
  currentStage?: string;
  progress?: number | { current: number; total: number };
  independentExecution?: boolean;
  executionId?: string;
  className?: string;
}

/**
 * SYS09 — AI Execution In Progress System State Component.
 *
 * Requirements:
 * - Represents QUEUED and RUNNING pipeline states
 * - Displays authoritative progress only when explicitly supplied (never fabricates numbers)
 * - Uses calm indeterminate indicator when progress percentage is unmetered
 * - Explicitly communicates that background execution continues independently and leaving
 *   the page does not destroy the execution
 */
export function AIExecutionProgressState({
  status = 'RUNNING',
  currentStage,
  progress,
  independentExecution = true,
  executionId,
  className = '',
}: AIExecutionProgressStateProps) {
  const isQueued = status?.toUpperCase() === 'QUEUED';
  const badgeLabel = isQueued ? 'Pipeline Queued' : 'Execution in Progress';
  const title = isQueued ? 'AI Execution Queued' : 'AI Execution in Progress';

  const hasPercentage = typeof progress === 'number';
  const hasSteps = progress && typeof progress === 'object';

  return (
    <div
      className={`gf-system-card ${className}`.trim()}
      role="status"
      aria-live="polite"
    >
      <span className="gf-system-badge gf-system-badge--ai">
        {badgeLabel}
      </span>

      <h2 className="gf-system-title">{title}</h2>

      {currentStage && (
        <p className="gf-system-desc">{currentStage}</p>
      )}

      {/* Progress Presentation */}
      <div className="gf-system-progress-wrapper">
        <div className="gf-system-progress-track">
          {hasPercentage ? (
            <div
              className="gf-system-progress-fill"
              style={{ width: `${Math.min(Math.max(progress as number, 0), 100)}%` }}
            />
          ) : hasSteps ? (
            <div
              className="gf-system-progress-fill"
              style={{
                width: `${Math.min(
                  Math.max(((progress as { current: number; total: number }).current / (progress as { current: number; total: number }).total) * 100, 0),
                  100,
                )}%`,
              }}
            />
          ) : (
            <div className="gf-system-progress-indeterminate" />
          )}
        </div>

        {hasPercentage && (
          <div className="gf-system-meta-row" style={{ marginTop: '6px', justifyContent: 'flex-end' }}>
            <span className="gf-system-meta-value">{Math.round(progress as number)}%</span>
          </div>
        )}

        {hasSteps && (
          <div className="gf-system-meta-row" style={{ marginTop: '6px', justifyContent: 'flex-end' }}>
            <span className="gf-system-meta-value">
              Step {(progress as { current: number; total: number }).current} of{' '}
              {(progress as { current: number; total: number }).total}
            </span>
          </div>
        )}
      </div>

      {executionId && (
        <div className="gf-system-meta">
          <div className="gf-system-meta-row">
            <span className="gf-system-meta-label">Execution ID:</span>
            <code className="gf-system-code">{executionId}</code>
          </div>
        </div>
      )}

      {independentExecution && (
        <div className="gf-system-note">
          <strong>Background Execution Active:</strong> This workflow runs asynchronously in the
          background. You can safely navigate to other views or close this tab without
          interrupting progress.
        </div>
      )}
    </div>
  );
}
