import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getAdminMentor } from '@/lib/api/client';
import type { AdminMentorDetail } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorDetail.css';

/**
 * AD03 — Mentor Detail
 *
 * Detailed governance inspection for a specific platform mentor, including
 * supervised cohorts and student roster.
 */
export function MentorDetail() {
  const { mentorId } = useParams<{ mentorId: string }>();
  const [mentor, setMentor] = useState<AdminMentorDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadMentor() {
      if (!mentorId) return;
      try {
        setLoading(true);
        setError(null);
        const data = await getAdminMentor(mentorId);
        if (mounted) {
          setMentor(data);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to retrieve mentor details.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }
    loadMentor();
    return () => {
      mounted = false;
    };
  }, [mentorId]);

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        return <Badge variant="success">Active Account</Badge>;
      case 'SUSPENDED':
        return <Badge variant="danger">Suspended</Badge>;
      case 'INACTIVE':
        return <Badge variant="neutral">Inactive</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  return (
    <div className="gf-mentor-detail">
      <div className="gf-mentor-detail__breadcrumb">
        <Link to="/admin/mentors" className="gf-mentor-detail__back-link">
          ← Back to Mentor Directory
        </Link>
      </div>

      {loading ? (
        <div className="gf-mentor-detail__skeleton-container">
          <Skeleton height="80px" />
          <Skeleton height="200px" />
          <Skeleton height="200px" />
        </div>
      ) : error || !mentor ? (
        <div className="gf-mentor-detail__alert" role="alert">
          <span>{error || 'Mentor not found.'}</span>
          <Button as="link" to="/admin/mentors" variant="secondary" size="sm">
            Return to Directory
          </Button>
        </div>
      ) : (
        <>
          <PageHeader
            eyebrow="MENTOR GOVERNANCE RECORD"
            title={mentor.full_name}
            description={`${mentor.designation || 'Mentor'} ${
              mentor.organization ? `at ${mentor.organization}` : ''
            } • ${mentor.email}`}
            actions={
              <div className="gf-mentor-detail__header-status">
                {getStatusBadge(mentor.status)}
              </div>
            }
          />

          <div className="gf-mentor-detail__grid">
            {/* Mentor Overview Card */}
            <Card className="gf-mentor-detail__card">
              <CardHeader>
                <CardTitle>Professional Profile &amp; Governance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="gf-mentor-detail__info-list">
                  <div className="gf-mentor-detail__info-row">
                    <span className="gf-mentor-detail__label">User Identity ID</span>
                    <code className="gf-mentor-detail__code">{mentor.id}</code>
                  </div>
                  {mentor.mentor_id && (
                    <div className="gf-mentor-detail__info-row">
                      <span className="gf-mentor-detail__label">Mentor System ID</span>
                      <code className="gf-mentor-detail__code">{mentor.mentor_id}</code>
                    </div>
                  )}
                  <div className="gf-mentor-detail__info-row">
                    <span className="gf-mentor-detail__label">Specialization</span>
                    <span>{mentor.specialization || 'Not specified'}</span>
                  </div>
                  <div className="gf-mentor-detail__info-row">
                    <span className="gf-mentor-detail__label">Accepting Students</span>
                    <span>
                      {mentor.is_accepting_students ? (
                        <Badge variant="success">Accepting</Badge>
                      ) : (
                        <Badge variant="neutral">Not Accepting</Badge>
                      )}
                      {mentor.max_students ? ` (Max: ${mentor.max_students})` : ''}
                    </span>
                  </div>
                  <div className="gf-mentor-detail__info-row">
                    <span className="gf-mentor-detail__label">Registration Date</span>
                    <span>
                      {mentor.created_at ? new Date(mentor.created_at).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                  <div className="gf-mentor-detail__info-row">
                    <span className="gf-mentor-detail__label">Last Login</span>
                    <span>
                      {mentor.last_login_at
                        ? new Date(mentor.last_login_at).toLocaleString()
                        : 'No session recorded'}
                    </span>
                  </div>
                  {mentor.bio && (
                    <div className="gf-mentor-detail__bio-block">
                      <span className="gf-mentor-detail__label">Bio</span>
                      <p className="gf-mentor-detail__bio-text">{mentor.bio}</p>
                    </div>
                  )}
                  {mentor.skills && mentor.skills.length > 0 && (
                    <div className="gf-mentor-detail__skills-block">
                      <span className="gf-mentor-detail__label">Technical Skills</span>
                      <div className="gf-mentor-detail__skills-tags">
                        {mentor.skills.map((skill, idx) => (
                          <span key={idx} className="gf-mentor-detail__skill-tag">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Supervised Cohorts Card */}
            <Card className="gf-mentor-detail__card">
              <CardHeader>
                <div className="gf-mentor-detail__card-header-inner">
                  <CardTitle>Supervised Cohorts ({mentor.groups.length})</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                {mentor.groups.length === 0 ? (
                  <EmptyState
                    title="No cohorts created"
                    description="This mentor has not created or been assigned any cohorts yet."
                  />
                ) : (
                  <div className="gf-mentor-detail__table-responsive">
                    <table className="gf-mentor-detail__table">
                      <thead>
                        <tr>
                          <th scope="col">Cohort Name</th>
                          <th scope="col">Join Code</th>
                          <th scope="col">Status</th>
                          <th scope="col">Students</th>
                          <th scope="col">Projects</th>
                        </tr>
                      </thead>
                      <tbody>
                        {mentor.groups.map((grp) => (
                          <tr key={grp.id}>
                            <td className="gf-mentor-detail__cohort-name">{grp.name}</td>
                            <td>
                              <code className="gf-mentor-detail__code">{grp.join_code}</code>
                            </td>
                            <td>
                              <Badge variant={grp.status === 'ACTIVE' ? 'success' : 'neutral'}>
                                {grp.status}
                              </Badge>
                            </td>
                            <td>{grp.student_count}</td>
                            <td>{grp.project_count}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Supervised Students Roster */}
          <section className="gf-mentor-detail__students-section">
            <Card>
              <CardHeader>
                <CardTitle>Supervised Students Roster ({mentor.supervised_students.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {mentor.supervised_students.length === 0 ? (
                  <EmptyState
                    title="No students assigned"
                    description="There are currently no students enrolled in cohorts supervised by this mentor."
                  />
                ) : (
                  <div className="gf-mentor-detail__table-responsive">
                    <table className="gf-mentor-detail__table">
                      <thead>
                        <tr>
                          <th scope="col">Student</th>
                          <th scope="col">Cohort</th>
                          <th scope="col">Active Projects</th>
                          <th scope="col" className="gf-mentor-detail__th-actions">Governance</th>
                        </tr>
                      </thead>
                      <tbody>
                        {mentor.supervised_students.map((st) => (
                          <tr key={st.id}>
                            <td>
                              <div className="gf-mentor-detail__user-meta">
                                <span className="gf-mentor-detail__user-name">{st.full_name}</span>
                                <span className="gf-mentor-detail__user-email">{st.email}</span>
                              </div>
                            </td>
                            <td>{st.group_name}</td>
                            <td>
                              <span className="gf-mentor-detail__stat-pill">
                                {st.active_projects_count} active
                              </span>
                            </td>
                            <td className="gf-mentor-detail__cell-actions">
                              <Link
                                to={`/admin/students/${st.id}`}
                                className="gf-mentor-detail__action-link"
                              >
                                View Student →
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </section>
        </>
      )}
    </div>
  );
}
