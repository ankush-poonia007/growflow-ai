import { Button } from '@/components/ui/Button';
import {
  CANONICAL_BLUEPRINT_SECTION_LABELS,
  type BlueprintSectionKey,
  type BlueprintJobSummary,
} from '@/lib/api/types';

interface BlueprintFailureViewProps {
  activeJob?: BlueprintJobSummary | null;
  errorMessage?: string | null;
  completedSections?: BlueprintSectionKey[];
  failedSections?: BlueprintSectionKey[];
  onRetry: (targetSections?: BlueprintSectionKey[]) => void;
  isRetrying: boolean;
}

export function BlueprintFailureView({
  activeJob,
  errorMessage,
  completedSections = [],
  failedSections = [],
  onRetry,
  isRetrying,
}: BlueprintFailureViewProps) {
  const effectiveFailed =
    failedSections.length > 0
      ? failedSections
      : activeJob?.failed_sections && activeJob.failed_sections.length > 0
      ? activeJob.failed_sections
      : (['specifications'] as BlueprintSectionKey[]);

  const message =
    errorMessage ||
    activeJob?.error_message ||
    'Synthesis was interrupted or encountered a schema validation error during generation.';

  return (
    <div className="gf-blueprint-failure">
      <div className="gf-blueprint-card gf-blueprint-failure-card">
        <div className="gf-blueprint-failure__top">
          <div className="gf-blueprint-failure__icon-wrap">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="32"
              height="32"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <div>
            <span className="gf-blueprint-badge-error">Synthesis Halted • S13 Recovery</span>
            <h2 className="gf-blueprint-card__title">Synthesis Interrupted</h2>
            <p className="gf-blueprint-failure__message">{message}</p>
          </div>
        </div>

        {/* State Preservation Guarantee */}
        <div className="gf-blueprint-preservation-banner">
          <div className="gf-blueprint-preservation-icon">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <div className="gf-blueprint-preservation-text">
            <strong>State Preservation Active:</strong> {completedSections.length} completed section(s)
            have been safely persisted to your database and will NOT be overwritten during targeted recovery.
          </div>
        </div>

        {/* Affected Sections */}
        <div className="gf-blueprint-affected-sections">
          <h3 className="gf-blueprint-subheading">Affected Sections Requiring Recovery:</h3>
          <div className="gf-blueprint-failed-chips">
            {effectiveFailed.map((sec) => (
              <span key={sec} className="gf-blueprint-chip gf-blueprint-chip--error">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="15" y1="9" x2="9" y2="15" />
                  <line x1="9" y1="9" x2="15" y2="15" />
                </svg>
                {CANONICAL_BLUEPRINT_SECTION_LABELS[sec] || sec}
              </span>
            ))}
          </div>
        </div>

        {/* Action Controls */}
        <div className="gf-blueprint-actions">
          <Button
            as="button"
            variant="primary"
            size="lg"
            onClick={() => onRetry(effectiveFailed)}
            disabled={isRetrying}
            id="retry-failed-sections-btn"
          >
            {isRetrying ? 'Retrying Affected Sections...' : 'Retry Affected Sections'}
          </Button>

          <Button
            as="button"
            variant="secondary"
            size="lg"
            onClick={() => onRetry()}
            disabled={isRetrying}
            id="restart-full-blueprint-btn"
          >
            Re-synthesize Entire Blueprint
          </Button>
        </div>
      </div>
    </div>
  );
}
