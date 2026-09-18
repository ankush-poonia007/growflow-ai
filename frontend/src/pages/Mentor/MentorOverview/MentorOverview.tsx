import { useState, useEffect, useCallback } from 'react';
import { getMentorOverview } from '@/lib/api/client';
import type { MentorOverviewResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './MentorOverview.css';

export function MentorOverview() {
  const [data, setData] = useState<MentorOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadOverview = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getMentorOverview();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load mentor overview data.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  return (
    <div className="gf-mentor-overview">
      <PageHeader
        eyebrow="SUPERVISE WORKPLACE"
        title="Mentor Overview"
        description="Supervise student cohorts, track group health, and intervene on at-risk projects."
        actions={
          <Button as="link" to="/mentor/groups/new" variant="primary">
            + Create Group
          </Button>
        }
      />

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadOverview} />
        </div>
      )}

      {/* Stats Overview */}
      <section className="gf-mentor-overview__stats" aria-label="Supervisor Metrics">
        {loading ? (
          <>
            <Skeleton height="100px" />
            <Skeleton height="100px" />
            <Skeleton height="100px" />
            <Skeleton height="100px" />
          </>
        ) : (
          <>
            <StatTile
              label="Supervised Groups"
              value={data?.total_groups ?? 0}
              subtext="Active student cohorts"
            />
            <StatTile
              label="Enrolled Students"
              value={data?.total_students ?? 0}
              subtext="Across all groups"
            />
            <StatTile
              label="Supervised Projects"
              value={data?.total_projects ?? 0}
              subtext="Linked student projects"
            />
            <StatTile
              label="At-Risk Alerts"
              value={data?.at_risk_projects ?? 0}
              subtext={data?.at_risk_projects ? 'Requiring supervisor triage' : 'All projects healthy'}
              tone={data && data.at_risk_projects > 0 ? 'warning' : 'success'}
            />
          </>
        )}
      </section>

      {/* Groups Section */}
      <section className="gf-mentor-overview__groups-section" aria-labelledby="groups-heading">
        <div className="gf-mentor-overview__section-header">
          <div>
            <h2 id="groups-heading" className="gf-mentor-overview__section-title">
              Supervised Cohorts
            </h2>
            <p className="gf-mentor-overview__section-desc">
              Cohorts currently under your supervision. Click any group to access its workspace.
            </p>
          </div>
          {data && data.groups.length > 0 && (
            <Button as="link" to="/mentor/groups" variant="secondary" size="sm">
              View All Groups &rarr;
            </Button>
          )}
        </div>

        {loading ? (
          <div className="gf-mentor-overview__loading-grid">
            <Skeleton height="140px" />
            <Skeleton height="140px" />
          </div>
        ) : !data || data.groups.length === 0 ? (
          <EmptyState
            title="No Supervised Groups Yet"
            description="Create your first student cohort to generate an enrollment join code. Students use the code to link their project instances to your supervisor dashboard."
            action={
              <Button as="link" to="/mentor/groups/new" variant="primary">
                Create First Group
              </Button>
            }
          />
        ) : (
          <div className="gf-mentor-overview__grid">
            {data.groups.map((grp) => (
              <Card key={grp.id} className="gf-mentor-overview__group-card">
                <div className="gf-mentor-overview__card-top">
                  <div className="gf-mentor-overview__card-heading">
                    <h3 className="gf-mentor-overview__group-name">{grp.name}</h3>
                    <Badge variant={grp.status === 'ACTIVE' ? 'success' : 'neutral'}>
                      {grp.status}
                    </Badge>
                  </div>
                  <div className="gf-mentor-overview__join-code-badge" title="Enrollment Join Code">
                    <span className="gf-mentor-overview__join-code-label">CODE:</span>
                    <code className="gf-mentor-overview__join-code-val">{grp.join_code}</code>
                  </div>
                </div>

                <div className="gf-mentor-overview__card-metrics">
                  <div className="gf-mentor-overview__metric-col">
                    <span className="gf-mentor-overview__metric-num">{grp.student_count}</span>
                    <span className="gf-mentor-overview__metric-lbl">Students</span>
                  </div>
                  <div className="gf-mentor-overview__metric-col">
                    <span className="gf-mentor-overview__metric-num">{grp.project_count}</span>
                    <span className="gf-mentor-overview__metric-lbl">Projects</span>
                  </div>
                  <div className="gf-mentor-overview__metric-col">
                    <span
                      className={`gf-mentor-overview__metric-num ${
                        grp.at_risk_count > 0 ? 'gf-mentor-overview__metric-num--risk' : ''
                      }`}
                    >
                      {grp.at_risk_count}
                    </span>
                    <span className="gf-mentor-overview__metric-lbl">At Risk</span>
                  </div>
                </div>

                <div className="gf-mentor-overview__card-footer">
                  <Button
                    as="link"
                    to={`/mentor/groups/${grp.id}`}
                    variant="secondary"
                    size="sm"
                    className="gf-mentor-overview__card-btn"
                  >
                    Open Workspace &rarr;
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
