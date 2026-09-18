import type { ProjectRecentActivity } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { getHealthDisplay, formatDateTime } from '../utils';

interface RecentChangesProps {
  activity?: ProjectRecentActivity | null;
}

export function RecentChanges({ activity }: RecentChangesProps) {
  const phaseTransition = activity?.latest_phase_transition;
  const healthTransition = activity?.latest_health_transition;
  const hasChanges = Boolean(phaseTransition || healthTransition);

  return (
    <Card as="section" className="gf-dashboard__recent-changes" variant="bordered">
      <CardHeader>
        <span className="gf-dashboard__section-eyebrow">AUDIT RECORD</span>
        <CardTitle as="h3" className="gf-dashboard__section-title">
          Recent Project Transitions
        </CardTitle>
      </CardHeader>

      <CardContent>
        {!hasChanges ? (
          <div className="gf-dashboard__recent-empty">
            <p className="gf-dashboard__recent-empty-title">No recent project changes</p>
            <p className="gf-dashboard__recent-empty-desc">
              State transitions and recorded health changes for this project will appear here when
              committed.
            </p>
          </div>
        ) : (
          <div className="gf-dashboard__transition-list">
            {phaseTransition && (
              <div className="gf-dashboard__transition-item">
                <div className="gf-dashboard__transition-top">
                  <span className="gf-dashboard__transition-type">Phase Transition</span>
                  <span className="gf-dashboard__transition-time">
                    {formatDateTime(phaseTransition.changed_at)}
                  </span>
                </div>
                <div className="gf-dashboard__transition-flow">
                  <Badge variant="neutral">{phaseTransition.previous_phase}</Badge>
                  <span className="gf-dashboard__transition-arrow" aria-hidden="true">→</span>
                  <Badge variant="accent">{phaseTransition.new_phase}</Badge>
                </div>
                {phaseTransition.reason && (
                  <p className="gf-dashboard__transition-reason">
                    Reason: {phaseTransition.reason}
                  </p>
                )}
              </div>
            )}

            {healthTransition && (
              <div className="gf-dashboard__transition-item">
                <div className="gf-dashboard__transition-top">
                  <span className="gf-dashboard__transition-type">Health Transition</span>
                  <span className="gf-dashboard__transition-time">
                    {formatDateTime(healthTransition.changed_at)}
                  </span>
                </div>
                <div className="gf-dashboard__transition-flow">
                  <Badge variant={getHealthDisplay(healthTransition.previous_health).variant}>
                    {getHealthDisplay(healthTransition.previous_health).label}
                  </Badge>
                  <span className="gf-dashboard__transition-arrow" aria-hidden="true">→</span>
                  <Badge variant={getHealthDisplay(healthTransition.new_health).variant} dot>
                    {getHealthDisplay(healthTransition.new_health).label}
                  </Badge>
                </div>
                {healthTransition.reason && (
                  <p className="gf-dashboard__transition-reason">
                    Reason: {healthTransition.reason}
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
