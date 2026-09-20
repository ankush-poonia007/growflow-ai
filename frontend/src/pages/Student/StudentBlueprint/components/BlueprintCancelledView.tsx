import { Button } from '@/components/ui/Button';

export interface BlueprintCancelledViewProps {
  projectId: string;
  onStartNewGeneration: () => void;
  isStarting?: boolean;
}

export function BlueprintCancelledView({
  projectId,
  onStartNewGeneration,
  isStarting = false,
}: BlueprintCancelledViewProps) {
  return (
    <div className="gf-blueprint-cancelled" data-testid="blueprint-cancelled-view">
      <div className="gf-blueprint-card gf-blueprint-cancelled-card">
        <div className="gf-blueprint-cancelled__top">
          <div className="gf-blueprint-cancelled__icon-wrap">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="32"
              height="32"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
            </svg>
          </div>
          <div>
            <span className="gf-blueprint-badge-muted">Generation Stopped • Cancelled</span>
            <h2 className="gf-blueprint-card__title">Blueprint Generation Cancelled</h2>
            <p className="gf-blueprint-cancelled__message">
              The blueprint synthesis run was stopped by user request. Any uncommitted sections from this run were discarded. If a previously approved blueprint exists for this project, it remains intact.
            </p>
          </div>
        </div>

        <div className="gf-blueprint-actions">
          <Button
            as="button"
            variant="primary"
            size="lg"
            onClick={onStartNewGeneration}
            disabled={isStarting}
            id="start-new-generation-btn"
          >
            {isStarting ? 'Initiating Synthesis...' : 'Start New Generation'}
          </Button>

          <Button
            as="link"
            variant="secondary"
            size="lg"
            to={`/student/projects/${projectId}`}
            id="return-to-project-btn"
          >
            Return to Project
          </Button>
        </div>
      </div>
    </div>
  );
}
