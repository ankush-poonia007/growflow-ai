import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { CANONICAL_LIFECYCLE_STAGES, getStageNumber } from '../utils';

interface LifecycleTrackProps {
  currentPhase: string;
}

export function LifecycleTrack({ currentPhase }: LifecycleTrackProps) {
  const currentStage = getStageNumber(currentPhase);

  return (
    <Card as="section" className="gf-dashboard__lifecycle-card" variant="bordered">
      <CardHeader>
        <div className="gf-dashboard__section-header-row">
          <div>
            <span className="gf-dashboard__section-eyebrow">LIFECYCLE POSITION</span>
            <CardTitle as="h3" className="gf-dashboard__section-title">
              Stage {currentStage} of 8 — {currentPhase}
            </CardTitle>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <ol className="gf-lifecycle-track" aria-label="Project lifecycle progression">
          {CANONICAL_LIFECYCLE_STAGES.map((item) => {
            const isCompleted = item.stage < currentStage;
            const isCurrent = item.stage === currentStage;

            let statusClass = 'gf-lifecycle-track__item--upcoming';
            let statusLabel = 'Upcoming';
            if (isCompleted) {
              statusClass = 'gf-lifecycle-track__item--completed';
              statusLabel = 'Completed';
            } else if (isCurrent) {
              statusClass = 'gf-lifecycle-track__item--current';
              statusLabel = 'Current Phase';
            }

            return (
              <li
                key={item.phase}
                className={`gf-lifecycle-track__item ${statusClass}`}
                aria-current={isCurrent ? 'step' : undefined}
              >
                <div className="gf-lifecycle-track__node-indicator">
                  <span className="gf-lifecycle-track__node-number">{item.stage}</span>
                </div>
                <div className="gf-lifecycle-track__label-group">
                  <span className="gf-lifecycle-track__label">{item.label}</span>
                  <span className="gf-lifecycle-track__status-sr sr-only">({statusLabel})</span>
                </div>
              </li>
            );
          })}
        </ol>

        <p className="gf-dashboard__lifecycle-note">
          Canonical lifecycle sequence defines execution gates from initial concept definition
          through final verification.
        </p>
      </CardContent>
    </Card>
  );
}
