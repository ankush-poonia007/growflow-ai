import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getAdminStudent } from '@/lib/api/client';
import type { AdminStudentDetail } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './StudentDetail.css';

/**
 * AD05 — Student Detail
 *
 * Comprehensive governance record for an enrolled student, including
 * academic affiliations, skill inventory, enrolled cohorts, and project instances.
 */
export function StudentDetail() {
  const { studentId } = useParams<{ studentId: string }>();
  const [student, setStudent] = useState<AdminStudentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadStudent() {
      if (!studentId) return;
      try {
        setLoading(true);
        setError(null);
        const data = await getAdminStudent(studentId);
        if (mounted) {
          setStudent(data);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to retrieve student details.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }
    loadStudent();
    return () => {
      mounted = false;
    };
  }, [studentId]);

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

  const getHealthBadge = (health: string) => {
    switch (health.toUpperCase()) {
      case 'HEALTHY':
        return <Badge variant="success">Healthy</Badge>;
      case 'WARNING':
        return <Badge variant="warning">Warning</Badge>;
      case 'CRITICAL':
        return <Badge variant="danger">Critical Risk</Badge>;
      default:
        return <Badge variant="neutral">{health}</Badge>;
    }
  };

  return (
    <div className="gf-student-detail">
      <div className="gf-student-detail__breadcrumb">
        <Link to="/admin/students" className="gf-student-detail__back-link">
          ← Back to Student Directory
        </Link>
      </div>

      {loading ? (
        <div className="gf-student-detail__skeleton-container">
          <Skeleton height="80px" />
          <Skeleton height="200px" />
          <Skeleton height="200px" />
        </div>
      ) : error || !student ? (
        <div className="gf-student-detail__alert" role="alert">
          <span>{error || 'Student not found.'}</span>
          <Button as="link" to="/admin/students" variant="secondary" size="sm">
            Return to Directory
          </Button>
        </div>
      ) : (
        <>
          <PageHeader
            eyebrow="STUDENT GOVERNANCE RECORD"
            title={student.full_name}
            description={`${student.primary_track || 'Student'} • ${
              student.college || 'No college listed'
            } • ${student.email}`}
            actions={
              <div className="gf-student-detail__header-status">
                {getStatusBadge(student.status)}
              </div>
            }
          />

          <div className="gf-student-detail__grid">
            {/* Student Profile & Academic Info */}
            <Card className="gf-student-detail__card">
              <CardHeader>
                <CardTitle>Academic &amp; Profile Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="gf-student-detail__info-list">
                  <div className="gf-student-detail__info-row">
                    <span className="gf-student-detail__label">User Identity ID</span>
                    <code className="gf-student-detail__code">{student.id}</code>
                  </div>
                  {student.student_id && (
                    <div className="gf-student-detail__info-row">
                      <span className="gf-student-detail__label">Student Roll/ID</span>
                      <code className="gf-student-detail__code">{student.student_id}</code>
                    </div>
                  )}
                  <div className="gf-student-detail__info-row">
                    <span className="gf-student-detail__label">Institution</span>
                    <span>{student.college || 'Not specified'}</span>
                  </div>
                  <div className="gf-student-detail__info-row">
                    <span className="gf-student-detail__label">Branch &amp; Specialization</span>
                    <span>{student.branch || 'Not specified'}</span>
                  </div>
                  <div className="gf-student-detail__info-row">
                    <span className="gf-student-detail__label">Year of Study</span>
                    <span>{student.year_of_study ? `Year ${student.year_of_study}` : 'N/A'}</span>
                  </div>
                  <div className="gf-student-detail__info-row">
                    <span className="gf-student-detail__label">Primary Track</span>
                    <span>{student.primary_track || 'General Track'}</span>
                  </div>
                  <div className="gf-student-detail__info-row">
                    <span className="gf-student-detail__label">Enrollment Date</span>
                    <span>
                      {student.created_at ? new Date(student.created_at).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                  <div className="gf-student-detail__info-row">
                    <span className="gf-student-detail__label">Last Login</span>
                    <span>
                      {student.last_login_at
                        ? new Date(student.last_login_at).toLocaleString()
                        : 'No session recorded'}
                    </span>
                  </div>
                  {student.bio && (
                    <div className="gf-student-detail__bio-block">
                      <span className="gf-student-detail__label">Bio</span>
                      <p className="gf-student-detail__bio-text">{student.bio}</p>
                    </div>
                  )}
                  {student.technologies && student.technologies.length > 0 && (
                    <div className="gf-student-detail__skills-block">
                      <span className="gf-student-detail__label">Verified Skills Inventory</span>
                      <div className="gf-student-detail__skills-grid">
                        {student.technologies.map((t) => (
                          <div key={t.technology_id} className="gf-student-detail__skill-pill">
                            <span className="gf-student-detail__skill-name">{t.technology_name}</span>
                            <span className="gf-student-detail__skill-score">{t.proficiency_level}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Enrolled Cohorts Card */}
            <Card className="gf-student-detail__card">
              <CardHeader>
                <CardTitle>Enrolled Cohorts ({student.groups.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {student.groups.length === 0 ? (
                  <EmptyState
                    title="No cohort enrollments"
                    description="This student has not joined any mentorship cohorts yet."
                  />
                ) : (
                  <div className="gf-student-detail__table-responsive">
                    <table className="gf-student-detail__table">
                      <thead>
                        <tr>
                          <th scope="col">Cohort</th>
                          <th scope="col">Supervisor</th>
                          <th scope="col">Status</th>
                          <th scope="col">Enrolled On</th>
                        </tr>
                      </thead>
                      <tbody>
                        {student.groups.map((grp) => (
                          <tr key={grp.group_id}>
                            <td className="gf-student-detail__cohort-name">{grp.group_name}</td>
                            <td>{grp.mentor_name}</td>
                            <td>
                              <Badge variant={grp.status === 'ACTIVE' ? 'success' : 'neutral'}>
                                {grp.status}
                              </Badge>
                            </td>
                            <td>
                              {grp.joined_at
                                ? new Date(grp.joined_at).toLocaleDateString()
                                : 'N/A'}
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

          {/* Project Instances Section */}
          <section className="gf-student-detail__projects-section">
            <Card>
              <CardHeader>
                <CardTitle>Project Instances ({student.projects.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {student.projects.length === 0 ? (
                  <EmptyState
                    title="No project instances"
                    description="This student has not initialized any project instances yet."
                  />
                ) : (
                  <div className="gf-student-detail__table-responsive">
                    <table className="gf-student-detail__table">
                      <thead>
                        <tr>
                          <th scope="col">Project Name</th>
                          <th scope="col">Current Phase</th>
                          <th scope="col">Health</th>
                          <th scope="col">Progress</th>
                          <th scope="col">Created Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {student.projects.map((proj) => (
                          <tr key={proj.id}>
                            <td className="gf-student-detail__project-title">{proj.name}</td>
                            <td>
                              <span className="gf-student-detail__phase-pill">
                                {proj.current_phase.replace(/_/g, ' ')}
                              </span>
                            </td>
                            <td>{getHealthBadge(proj.health)}</td>
                            <td>
                              <div className="gf-student-detail__progress-container">
                                <div
                                  className="gf-student-detail__progress-bar"
                                  style={{ width: `${Math.min(100, Math.max(0, proj.progress_percentage))}%` }}
                                />
                                <span className="gf-student-detail__progress-text">
                                  {proj.progress_percentage}%
                                </span>
                              </div>
                            </td>
                            <td>
                              {proj.created_at
                                ? new Date(proj.created_at).toLocaleDateString()
                                : 'N/A'}
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
