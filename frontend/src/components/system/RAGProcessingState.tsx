import { Button } from '@/components/ui/Button';
import './SystemStates.css';

export type RAGProcessingStage =
  | 'QUEUED'
  | 'PROCESSING'
  | 'INDEXING'
  | 'READY'
  | 'FAILED'
  | string;

export interface RAGProcessingStateProps {
  stage: RAGProcessingStage;
  documentName?: string;
  chunkCount?: number;
  embeddingStatus?: string;
  failureReason?: string;
  onRetry?: () => void;
  className?: string;
}

const STAGES = ['QUEUED', 'PROCESSING', 'INDEXING', 'READY'];

/**
 * SYS10 — RAG / Document Processing State Component.
 *
 * Requirements:
 * - Represents documented lifecycle: QUEUED → PROCESSING → INDEXING → READY / FAILED
 * - Shows current processing stage with visual stepper
 * - Shows chunk count only when authoritatively available (never fabricated)
 * - Shows embedding / vector indexing status when available
 * - Suppresses raw embeddings, vectors, and credentials
 * - Displays safe failure summary with optional retry on FAILED
 */
export function RAGProcessingState({
  stage,
  documentName,
  chunkCount,
  embeddingStatus,
  failureReason,
  onRetry,
  className = '',
}: RAGProcessingStateProps) {
  const normalizedStage = stage?.toUpperCase() || 'QUEUED';
  const isFailed = normalizedStage === 'FAILED';
  const isReady = normalizedStage === 'READY';

  const currentStepIndex = isFailed
    ? 3
    : Math.max(0, STAGES.indexOf(normalizedStage));

  return (
    <div
      className={`gf-system-card ${className}`.trim()}
      role="status"
      aria-live="polite"
    >
      <span
        className={`gf-system-badge ${
          isFailed
            ? 'gf-system-badge--danger'
            : isReady
            ? 'gf-system-badge--success'
            : 'gf-system-badge--ai'
        }`}
      >
        {isFailed
          ? 'RAG Pipeline Failed'
          : isReady
          ? 'RAG Knowledge Ready'
          : `Processing Stage: ${normalizedStage}`}
      </span>

      <h2 className="gf-system-title">
        {documentName
          ? `Document Ingestion: ${documentName}`
          : 'Document Intelligence & Vector Ingestion'}
      </h2>

      {/* Stepper Pipeline */}
      <div className="gf-system-stepper" aria-label="Processing Lifecycle Stages">
        {STAGES.map((s, idx) => {
          const isStepFailed = isFailed && idx === 3;
          const isCompleted = !isFailed && idx < currentStepIndex;
          const isActive = !isFailed && idx === currentStepIndex;

          const stepClass = isStepFailed
            ? 'gf-system-step--failed'
            : isCompleted
            ? 'gf-system-step--completed'
            : isActive
            ? 'gf-system-step--active'
            : '';

          const label = isStepFailed ? 'FAILED' : s;

          return (
            <div key={s} className={`gf-system-step ${stepClass}`.trim()}>
              <div className="gf-system-step-indicator">
                {isCompleted ? '✓' : isStepFailed ? '✕' : idx + 1}
              </div>
              <span className="gf-system-step-label">{label}</span>
            </div>
          );
        })}
      </div>

      {/* Metadata Disclosure */}
      {(chunkCount !== undefined || embeddingStatus) && (
        <div className="gf-system-meta">
          {chunkCount !== undefined && (
            <div className="gf-system-meta-row">
              <span className="gf-system-meta-label">Extracted Chunks:</span>
              <span className="gf-system-meta-value">{chunkCount}</span>
            </div>
          )}
          {embeddingStatus && (
            <div className="gf-system-meta-row">
              <span className="gf-system-meta-label">Embedding Status:</span>
              <span className="gf-system-meta-value">{embeddingStatus}</span>
            </div>
          )}
        </div>
      )}

      {/* Failure Details & Actions */}
      {isFailed && (
        <>
          {failureReason && (
            <div className="gf-system-note" style={{ borderColor: 'rgba(166, 83, 77, 0.3)' }}>
              <strong>Failure Cause:</strong> {failureReason}
            </div>
          )}
          {onRetry && (
            <div className="gf-system-actions">
              <Button variant="primary" onClick={onRetry}>
                Retry Ingestion
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
