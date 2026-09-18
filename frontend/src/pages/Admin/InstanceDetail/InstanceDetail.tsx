import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getAdminInstanceDetail } from '@/lib/api/client';
import type { AdminProjectInstanceDetail } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './InstanceDetail.css';

/**
 * AD10 Canonical Detail — Project Instance Governance Detail
 *
 * Single canonical Admin project-instance detail view at /admin/instances/:projectId.
 * Inspects execution health, student ownership, supervisor context,
 * profile metadata, and historical lifecycle/health transitions.
 */
export function InstanceDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const [instance, setInstance] = useState<AdminProjectInstanceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInstance = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getAdminInstanceDetail(projectId);
      setInstance(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve project instance details.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInstance();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  const getHealthBadge = (health?: string | null) => {
    switch (health?.toUpperCase()) {
      case 'HEALTHY':
        return <Badge variant="success">Healthy</Badge>;
      case 'WARNING':
      case 'NEEDS_ATTENTION':
        return <Badge variant="warning">Warning</Badge>;
      case 'CRITICAL':
      case 'AT_RISK':
        return <Badge variant="danger">Critical</Badge>;
      default:
        return <Badge variant="neutral">{health ?? 'UNKNOWN'}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="gf-inst-detail">
        <Skeleton height="32px" width="180px" className="gf-mb-3" />
        <Skeleton height="80px" className="gf-mb-4" />
        <div className="gf-inst-detail__grid">
          <Skeleton height="200px" />
          <Skeleton height="200px" />
        </div>
      </div>
    );
  }

  if (error || !instance) {
    return (
      <div className="gf-inst-detail">
        <Link to="/admin/instances" className="gf-inst-detail__back-link">
          &larr; Back to Instances Monitoring
        </Link>
        <EmptyState
          title="Project instance not found"
          description={error || 'The requested student project instance does not exist or has been removed.'}
        />
        <div className="gf-inst-detail__error-actions">
          <Button variant="secondary" onClick={fetchInstance}>
            Retry
          </Button>
          <Button as="link" to="/admin/instances" variant="tertiary">
            Back to Instances
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-inst-detail">
      <div className="gf-inst-detail__nav">
        <div className="gf-inst-detail__back-links">
          <Link to="/admin/instances" className="gf-inst-detail__back-link">
            &larr; Back to Instances Monitoring
          </Link>
          <span className="gf-inst-detail__nav-divider">•</span>
          <Link to="/admin/projects" className="gf-inst-detail__back-link">
            Projects Directory
          </Link>
        </div>
        <span className="gf-inst-detail__mode-badge">Governance Read-Only Mode</span>
      </div>

      <PageHeader
        eyebrow="RESOURCE GOVERNANCE • INSTANCE INSPECTION"
        title={instance.name}
        description="Inspect student project instance progression, lifecycle audit trails, and supervisor context."
        actions={
          <div className="gf-inst-detail__header-badges">
            <span className="gf-inst-detail__phase-pill">
              {instance.current_phase.replace(/_/g, ' ')}
            </span>
            {getHealthBadge(instance.health)}
            <Badge variant={instance.status === 'ACTIVE' ? 'success' : 'neutral'}>
              {instance.status}
            </Badge>
            <Badge variant="neutral">{instance.complexity}</Badge>
            {instance.definition_name && (
              <span className="gf-inst-detail__def-badge">
                Template: {instance.definition_name} {instance.version_number ? `v${instance.version_number}` : ''}
              </span>
            )}
          </div>
        }
      />

      {/* Top Cards: Context & Health/Progress */}
      <div className="gf-inst-detail__grid">
        {/* Ownership Context Card */}
        <Card className="gf-inst-detail__card">
          <CardHeader>
            <CardTitle>Ownership & Supervision Context</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-inst-detail__context-list">
              <div className="gf-inst-detail__context-item">
                <span className="gf-inst-detail__context-label">Student Owner:</span>
                <Link
                  to={`/admin/students/${instance.student_id}`}
                  className="gf-inst-detail__context-link"
                >
                  {instance.student_name}
                </Link>
                <span className="gf-inst-detail__context-email">({instance.student_email})</span>
              </div>

              <div className="gf-inst-detail__context-item">
                <span className="gf-inst-detail__context-label">Supervising Mentor:</span>
                {instance.mentor_id ? (
                  <Link
                    to={`/admin/mentors/${instance.mentor_id}`}
                    className="gf-inst-detail__context-link"
                  >
                    {instance.mentor_name}
                  </Link>
                ) : (
                  <span className="gf-inst-detail__muted">Independent (No supervisor)</span>
                )}
              </div>

              <div className="gf-inst-detail__context-item">
                <span className="gf-inst-detail__context-label">Assigned Cohort:</span>
                {instance.group_id ? (
                  <Link
                    to={`/admin/groups/${instance.group_id}`}
                    className="gf-inst-detail__context-link"
                  >
                    {instance.group_name}
                  </Link>
                ) : (
                  <span className="gf-inst-detail__muted">None</span>
                )}
              </div>

              <div className="gf-inst-detail__context-item">
                <span className="gf-inst-detail__context-label">Created / Updated:</span>
                <span className="gf-inst-detail__context-val">
                  {new Date(instance.created_at).toLocaleDateString()} /{' '}
                  {new Date(instance.updated_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Execution & Progress Card */}
        <Card className="gf-inst-detail__card">
          <CardHeader>
            <CardTitle>Execution Progression</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-inst-detail__progress-section">
              <div className="gf-inst-detail__progress-header">
                <span className="gf-inst-detail__progress-lbl">Overall Milestone Progress</span>
                <span className="gf-inst-detail__progress-pct">{instance.progress_percentage}%</span>
              </div>
              <div className="gf-inst-detail__bar-container">
                <div
                  className="gf-inst-detail__bar-fill"
                  style={{ width: `${Math.min(100, Math.max(0, instance.progress_percentage))}%` }}
                />
              </div>

              <div className="gf-inst-detail__dates-grid">
                <div>
                  <span className="gf-inst-detail__date-label">Started:</span>
                  <span className="gf-inst-detail__date-value">
                    {instance.started_at ? new Date(instance.started_at).toLocaleDateString() : 'Pending'}
                  </span>
                </div>
                <div>
                  <span className="gf-inst-detail__date-label">Target Deadline:</span>
                  <span className="gf-inst-detail__date-value">
                    {instance.deadline ? new Date(instance.deadline).toLocaleDateString() : 'None set'}
                  </span>
                </div>
                <div>
                  <span className="gf-inst-detail__date-label">Completed:</span>
                  <span className="gf-inst-detail__date-value">
                    {instance.completed_at ? new Date(instance.completed_at).toLocaleDateString() : 'In Progress'}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Problem & Solution Card */}
      {(instance.problem || instance.proposed_solution) && (
        <Card className="gf-inst-detail__card">
          <CardHeader>
            <CardTitle>Problem Statement & Proposed Solution</CardTitle>
          </CardHeader>
          <CardContent>
            {instance.problem && (
              <div className="gf-inst-detail__content-block">
                <strong>Problem Statement:</strong>
                <p>{instance.problem}</p>
              </div>
            )}
            {instance.proposed_solution && (
              <div className="gf-inst-detail__content-block gf-mt-3">
                <strong>Proposed Solution:</strong>
                <p>{instance.proposed_solution}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Profile Metadata */}
      {(instance.profile_objective || instance.profile_goals || instance.profile_scope) && (
        <Card className="gf-inst-detail__card">
          <CardHeader>
            <CardTitle>Project Profile & Architectural Scope</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-inst-detail__profile-grid">
              {instance.profile_objective && (
                <div>
                  <strong>Objective:</strong>
                  <p>{instance.profile_objective}</p>
                </div>
              )}
              {instance.profile_goals && (
                <div>
                  <strong>Goals:</strong>
                  <p>{instance.profile_goals}</p>
                </div>
              )}
              {instance.profile_scope && (
                <div>
                  <strong>Scope:</strong>
                  <p>{instance.profile_scope}</p>
                </div>
              )}
              {instance.profile_expected_outcome && (
                <div>
                  <strong>Expected Outcome:</strong>
                  <p>{instance.profile_expected_outcome}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Transition History Audit Logs */}
      <div className="gf-inst-detail__history-grid">
        {/* Phase Transition History */}
        <Card className="gf-inst-detail__card">
          <CardHeader>
            <CardTitle>Phase Transitions ({(instance.phase_history ?? []).length})</CardTitle>
          </CardHeader>
          <CardContent>
            {(instance.phase_history ?? []).length === 0 ? (
              <p className="gf-inst-detail__muted">No phase transitions recorded yet.</p>
            ) : (
              <div className="gf-inst-detail__history-list">
                {(instance.phase_history ?? []).map((h) => (
                  <div key={h.id} className="gf-inst-detail__history-item">
                    <div className="gf-inst-detail__history-title">
                      <span className="gf-inst-detail__hist-pill">{h.previous_phase}</span>
                      <span className="gf-inst-detail__hist-arrow">&rarr;</span>
                      <span className="gf-inst-detail__hist-pill gf-inst-detail__hist-pill--active">
                        {h.new_phase}
                      </span>
                    </div>
                    {h.reason && <p className="gf-inst-detail__hist-reason">{h.reason}</p>}
                    <span className="gf-inst-detail__hist-date">
                      {new Date(h.changed_at).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Health Transition History */}
        <Card className="gf-inst-detail__card">
          <CardHeader>
            <CardTitle>Health Transitions ({(instance.health_history ?? []).length})</CardTitle>
          </CardHeader>
          <CardContent>
            {(instance.health_history ?? []).length === 0 ? (
              <p className="gf-inst-detail__muted">No health changes recorded yet.</p>
            ) : (
              <div className="gf-inst-detail__history-list">
                {(instance.health_history ?? []).map((h) => (
                  <div key={h.id} className="gf-inst-detail__history-item">
                    <div className="gf-inst-detail__history-title">
                      {getHealthBadge(h.previous_health)}
                      <span className="gf-inst-detail__hist-arrow">&rarr;</span>
                      {getHealthBadge(h.new_health)}
                    </div>
                    {h.reason && <p className="gf-inst-detail__hist-reason">{h.reason}</p>}
                    <span className="gf-inst-detail__hist-date">
                      {new Date(h.changed_at).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
