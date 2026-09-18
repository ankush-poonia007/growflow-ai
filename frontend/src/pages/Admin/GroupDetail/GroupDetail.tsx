import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getAdminGroup } from '@/lib/api/client';
import type { AdminGroupDetail as AdminGroupDetailType } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './GroupDetail.css';

/**
 * AD07 — Group Detail
 *
 * Comprehensive governance inspection of a single platform cohort,
 * establishing the Group -> Mentor -> Students -> Projects relationship hierarchy.
 */
export function GroupDetail() {
  const { groupId } = useParams<{ groupId: string }>();
  const [group, setGroup] = useState<AdminGroupDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchGroup = async () => {
    if (!groupId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getAdminGroup(groupId);
      setGroup(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve cohort details.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroup();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupId]);

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
      <div className="gf-group-detail">
        <Skeleton height="32px" width="180px" className="gf-mb-3" />
        <Skeleton height="80px" className="gf-mb-4" />
        <div className="gf-group-detail__grid">
          <Skeleton height="180px" />
          <Skeleton height="180px" />
        </div>
      </div>
    );
  }

  if (error || !group) {
    return (
      <div className="gf-group-detail">
        <Link to="/admin/groups" className="gf-group-detail__back-link">
          &larr; Back to Groups Directory
        </Link>
        <EmptyState
          title="Cohort not found"
          description={error || 'The requested cohort could not be found or has been removed.'}
        />
        <div className="gf-group-detail__error-actions">
          <Button variant="secondary" onClick={fetchGroup}>
            Retry
          </Button>
          <Button as="link" to="/admin/groups" variant="tertiary">
            Back to Groups
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-group-detail">
      <div className="gf-group-detail__nav">
        <Link to="/admin/groups" className="gf-group-detail__back-link">
          &larr; Back to Groups Directory
        </Link>
        <span className="gf-group-detail__mode-badge">Governance Read-Only Mode</span>
      </div>

      <PageHeader
        eyebrow="RESOURCE GOVERNANCE • COHORT INSPECTION"
        title={group.name}
        description="Inspect cohort membership, supervising mentor, and student project execution state."
        actions={
          <div className="gf-group-detail__header-badges">
            <code className="gf-group-detail__join-code" title="Unique Join Code">
              Code: {group.join_code}
            </code>
            <Badge variant={group.status === 'ACTIVE' ? 'success' : 'neutral'}>
              {group.status}
            </Badge>
            <span className="gf-group-detail__created-info">
              Created on {new Date(group.created_at).toLocaleDateString()}
            </span>
          </div>
        }
      />

      {/* Top Cards: Mentor Overview & Cohort Metrics */}
      <div className="gf-group-detail__grid">
        {/* Mentor Card */}
        <Card className="gf-group-detail__card">
          <CardHeader>
            <CardTitle>Supervising Mentor</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-group-detail__mentor-info">
              <div className="gf-group-detail__mentor-avatar">
                {group.mentor_name.charAt(0).toUpperCase()}
              </div>
              <div className="gf-group-detail__mentor-meta">
                <Link
                  to={`/admin/mentors/${group.mentor_id}`}
                  className="gf-group-detail__mentor-link"
                >
                  {group.mentor_name}
                </Link>
                <span className="gf-group-detail__mentor-email">{group.mentor_email}</span>
                {group.mentor_specialization && (
                  <span className="gf-group-detail__specialization-tag">
                    {group.mentor_specialization}
                  </span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Aggregate Metrics Card */}
        <Card className="gf-group-detail__card">
          <CardHeader>
            <CardTitle>Cohort Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-group-detail__metrics-grid">
              <div className="gf-group-detail__metric">
                <span className="gf-group-detail__metric-val">{group.student_count}</span>
                <span className="gf-group-detail__metric-lbl">Enrolled Students</span>
              </div>
              <div className="gf-group-detail__metric">
                <span className="gf-group-detail__metric-val">{group.project_count}</span>
                <span className="gf-group-detail__metric-lbl">Total Projects</span>
              </div>
              <div className="gf-group-detail__metric">
                <span className="gf-group-detail__metric-val gf-group-detail__metric-val--active">
                  {group.active_project_count}
                </span>
                <span className="gf-group-detail__metric-lbl">Active Projects</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Enrolled Students Table */}
      <Card className="gf-group-detail__section-card">
        <CardHeader>
          <CardTitle>Enrolled Students ({(group.members ?? []).length})</CardTitle>
        </CardHeader>
        <CardContent>
          {(group.members ?? []).length === 0 ? (
            <EmptyState
              title="No students enrolled"
              description="No students have joined this cohort yet."
            />
          ) : (
            <div className="gf-group-detail__table-responsive">
              <table className="gf-group-detail__table">
                <thead>
                  <tr>
                    <th scope="col">Student Name</th>
                    <th scope="col">Email</th>
                    <th scope="col">Status</th>
                    <th scope="col">Joined Date</th>
                    <th scope="col"><span className="gf-sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody>
                  {(group.members ?? []).map((member) => (
                    <tr key={member.id}>
                      <td>
                        <Link
                          to={`/admin/students/${member.student_id}`}
                          className="gf-group-detail__item-link"
                        >
                          {member.full_name}
                        </Link>
                      </td>
                      <td>{member.email}</td>
                      <td>
                        <Badge variant={member.status === 'ACTIVE' ? 'success' : 'neutral'}>
                          {member.status}
                        </Badge>
                      </td>
                      <td>{new Date(member.joined_at).toLocaleDateString()}</td>
                      <td className="gf-group-detail__action-cell">
                        <Button
                          as="link"
                          to={`/admin/students/${member.student_id}`}
                          variant="secondary"
                          size="sm"
                        >
                          Inspect Student
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Associated Project Instances Table */}
      <Card className="gf-group-detail__section-card">
        <CardHeader>
          <CardTitle>Cohort Projects ({(group.projects ?? []).length})</CardTitle>
        </CardHeader>
        <CardContent>
          {(group.projects ?? []).length === 0 ? (
            <EmptyState
              title="No associated projects"
              description="Students in this cohort have not initialized any project instances yet."
            />
          ) : (
            <div className="gf-group-detail__table-responsive">
              <table className="gf-group-detail__table">
                <thead>
                  <tr>
                    <th scope="col">Project Title</th>
                    <th scope="col">Student Owner</th>
                    <th scope="col">Current Phase</th>
                    <th scope="col">Health</th>
                    <th scope="col">Progress</th>
                    <th scope="col">Status</th>
                    <th scope="col"><span className="gf-sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody>
                  {group.projects.map((proj) => (
                    <tr key={proj.id}>
                      <td>
                        <Link
                          to={`/admin/instances/${proj.id}`}
                          className="gf-group-detail__item-link"
                        >
                          {proj.name}
                        </Link>
                      </td>
                      <td>
                        <Link
                          to={`/admin/students/${proj.student_id}`}
                          className="gf-group-detail__sub-link"
                        >
                          {proj.student_name}
                        </Link>
                      </td>
                      <td>
                        <span className="gf-group-detail__phase-pill">
                          {proj.current_phase.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td>{getHealthBadge(proj.health)}</td>
                      <td>
                        <div className="gf-group-detail__progress-wrap">
                          <div
                            className="gf-group-detail__progress-bar"
                            style={{ width: `${Math.min(100, Math.max(0, proj.progress_percentage))}%` }}
                          />
                          <span className="gf-group-detail__progress-val">{proj.progress_percentage}%</span>
                        </div>
                      </td>
                      <td>
                        <Badge variant={proj.status === 'ACTIVE' ? 'success' : 'neutral'}>
                          {proj.status}
                        </Badge>
                      </td>
                      <td className="gf-group-detail__action-cell">
                        <Button
                          as="link"
                          to={`/admin/instances/${proj.id}`}
                          variant="secondary"
                          size="sm"
                        >
                          Inspect Instance
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
