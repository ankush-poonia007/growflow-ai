import { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { getMentorGroup, getGroupProjects } from '@/lib/api/client';
import type { GroupResponse, ProjectResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './GroupAtRisk.css';

export function GroupAtRisk() {
  const { groupId } = useParams<{ groupId: string }>();
  const [group, setGroup] = useState<GroupResponse | null>(null);
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!groupId) return;
    let mounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [gRes, pRes] = await Promise.all([
          getMentorGroup(groupId!),
          getGroupProjects(groupId!),
        ]);
        if (mounted) {
          setGroup(gRes);
          setProjects(pRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to load triage data.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadData();
    return () => {
      mounted = false;
    };
  }, [groupId]);

  const atRiskProjects = projects.filter(
    (p) => p.health === 'WARNING' || p.health === 'CRITICAL' || p.health === 'AT_RISK'
  );

  return (
    <div className="gf-group-at-risk">
      <PageHeader
        eyebrow="SUPERVISOR TRIAGE"
        title="At-Risk Projects"
        description={`Student projects in ${group ? group.name : 'this group'} requiring immediate supervisor attention.`}
        breadcrumbs={[
          { label: 'Groups', to: '/mentor/groups' },
          {
            label: group?.name || 'Cohort',
            to: groupId ? `/mentor/groups/${groupId}` : undefined,
          },
          { label: 'At-Risk' },
        ]}
      />

      {error && (
        <div className="gf-group-at-risk__error" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="gf-group-at-risk__loading">
          <Skeleton height="140px" />
          <Skeleton height="140px" />
        </div>
      ) : atRiskProjects.length === 0 ? (
        <EmptyState
          title="All Projects Healthy"
          description="None of the projects in this cohort are currently marked as At Risk or Critical. Great progress!"
          action={
            <Button
              as="link"
              to={`/mentor/groups/${groupId}/projects`}
              variant="secondary"
            >
              View All Projects &rarr;
            </Button>
          }
        />
      ) : (
        <div className="gf-group-at-risk__list" role="feed" aria-label="At-risk projects list">
          <div className="gf-group-at-risk__banner">
            <span className="gf-group-at-risk__banner-count">{atRiskProjects.length}</span>
            <span>
              {atRiskProjects.length === 1 ? 'project requires' : 'projects require'}{' '}
              mentor review or intervention to restore healthy progress.
            </span>
          </div>

          {atRiskProjects.map((p) => (
            <Card key={p.id} className="gf-group-at-risk__card">
              <div className="gf-group-at-risk__card-header">
                <div className="gf-group-at-risk__title-group">
                  <h3 className="gf-group-at-risk__project-name">{p.name}</h3>
                  <div className="gf-group-at-risk__badge-row">
                    <Badge variant={p.health === 'CRITICAL' ? 'danger' : 'warning'}>
                      {p.health}
                    </Badge>
                    <Badge variant="neutral">{p.current_phase}</Badge>
                  </div>
                </div>
              </div>

              {p.problem && (
                <div className="gf-group-at-risk__section">
                  <span className="gf-group-at-risk__section-label">Problem Definition:</span>
                  <p className="gf-group-at-risk__section-text">{p.problem}</p>
                </div>
              )}

              {p.proposed_solution && (
                <div className="gf-group-at-risk__section">
                  <span className="gf-group-at-risk__section-label">Proposed Solution:</span>
                  <p className="gf-group-at-risk__section-text">{p.proposed_solution}</p>
                </div>
              )}

              <div className="gf-group-at-risk__progress">
                <div className="gf-group-at-risk__progress-header">
                  <span>Current Progress</span>
                  <span>{p.progress_percentage}%</span>
                </div>
                <div className="gf-group-at-risk__progress-bar">
                  <div
                    className="gf-group-at-risk__progress-fill"
                    style={{ width: `${Math.min(100, p.progress_percentage)}%` }}
                  />
                </div>
              </div>

              <div className="gf-group-at-risk__card-footer">
                <span className="gf-group-at-risk__footer-meta">
                  Status: {p.status} &bull; Complexity: {p.complexity || 'INTERMEDIATE'}
                </span>
                {p.updated_at && (
                  <span className="gf-group-at-risk__footer-meta">
                    Last activity: {new Date(p.updated_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
