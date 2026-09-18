import { Button } from '@/components/ui/Button';
import './SystemStates.css';

export interface AIExecutionFailedStateProps {
  stage?: string;
  error?: string | Error | null;
  executionId?: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

/**
 * SYS08 — AI Execution Failed System State Component.
 *
 * Requirements:
 * - Reflects failed asynchronous AI execution state
 * - Shows failed stage and safe error summary
 * - Displays execution/reference ID only when authoritatively available (no fabricated IDs)
 * - Offers retry/recovery action only when caller explicitly supports it
 * - Suppresses raw stack traces or internal secrets
 */
export function AIExecutionFailedState({
  stage,
  error,
  executionId,
  onRetry,
  onDismiss,
  className = '',
}: AIExecutionFailedStateProps) {
  // Extract safe summary without leaking internal traces or credentials
  let safeSummary = 'The requested AI workflow could not be completed.';
  if (typeof error === 'string' && error.trim()) {
    safeSummary = error.trim();
  } else if (error instanceof Error && error.message) {
    safeSummary = error.message;
  }

  return (
    <div
      className={`gf-system-card ${className}`.trim()}
      role="alert"
      aria-live="polite"
    >
      <span className="gf-system-badge gf-system-badge--danger">
        Execution Failed
      </span>

      <h2 className="gf-system-title">AI Workflow Execution Failed</h2>
      <p className="gf-system-desc">{safeSummary}</p>

      {(stage || executionId) && (
        <div className="gf-system-meta">
          {stage && (
            <div className="gf-system-meta-row">
              <span className="gf-system-meta-label">Failed Stage:</span>
              <span className="gf-system-meta-value">{stage}</span>
            </div>
          )}
          {executionId && (
            <div className="gf-system-meta-row">
              <span className="gf-system-meta-label">Execution ID:</span>
              <code className="gf-system-code">{executionId}</code>
            </div>
          )}
        </div>
      )}

      {(onRetry || onDismiss) && (
        <div className="gf-system-actions">
          {onRetry && (
            <Button variant="primary" onClick={onRetry}>
              Retry Execution
            </Button>
          )}
          {onDismiss && (
            <Button variant="secondary" onClick={onDismiss}>
              Dismiss
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
