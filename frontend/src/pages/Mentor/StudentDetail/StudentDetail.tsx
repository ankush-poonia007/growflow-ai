import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getMentorStudent } from '@/lib/api/client';
import type { MentorStudentDetail } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './StudentDetail.css';

export function StudentDetail() {
  const { studentId } = useParams<{ studentId: string }>();
  const [student, setStudent] = useState<MentorStudentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadStudent() {
      if (!studentId) return;
      try {
        setLoading(true);
        setError(null);
        const data = await getMentorStudent(studentId);
        if (mounted) {
          setStudent(data);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg =
            err instanceof Error
              ? err.message
              : 'Failed to retrieve student profile or access was denied.';
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

  if (loading) {
    return (
      <div className="gf-student-detail" id="student-detail-loading">
        <Skeleton width="180px" height="24px" />
        <div style={{ display: 'flex', gap: '1.5rem', background: 'var(--gf-color-surface, #FFFFFF)', border: '1px solid var(--gf-color-border-subtle, #E5E5DF)', padding: '1.5rem', borderRadius: '14px' }}>
          <Skeleton width="72px" height="72px" variant="circle" />
          <div style={{ flex: 1 }}>
            <Skeleton width="40%" height="28px" />
            <div style={{ height: '8px' }} />
            <Skeleton width="25%" height="16px" />
            <div style={{ height: '12px' }} />
            <Skeleton width="70%" height="16px" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !student) {
    return (
      <div className="gf-student-detail" id="student-detail-error-container">
        <div className="gf-student-detail__nav">
          <Link to="/mentor/students" id="back-to-students-from-error">← Back to Supervised Students</Link>
        </div>
        <div className="gf-student-detail__error" role="alert" id="student-detail-error">
          <h3>Supervision Access Restriction</h3>
          <p>{error || 'Student not found or not in your supervised cohorts.'}</p>
          <Button as="link" to="/mentor/students" variant="secondary">
            Return to Students Directory
          </Button>
        </div>
      </div>
    );
  }

  const initials = student.full_name
    ? student.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2)
    : student.email.substring(0, 2).toUpperCase();

  const getHealthBadge = (health: string) => {
    switch (health) {
      case 'CRITICAL':
        return <Badge variant="danger">CRITICAL</Badge>;
      case 'WARNING':
        return <Badge variant="warning">WARNING</Badge>;
      case 'HEALTHY':
      default:
        return <Badge variant="success">HEALTHY</Badge>;
    }
  };

  return (
    <div className="gf-student-detail" id="student-detail-container">
      <div className="gf-student-detail__nav">
        <Link to="/mentor/students" id="student-detail-back-link">← Supervised Students</Link>
        <span>/</span>
        <span>{student.full_name}</span>
      </div>

      <PageHeader
        eyebrow="STUDENT PROFILE (READ-ONLY)"
        title={student.full_name}
        description={`Supervised student enrolled across ${student.group_count} cohort(s).`}
        actions={
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button
              as="link"
              to={`/mentor/students/${student.id || student.student_id || studentId}/activity`}
              variant="tertiary"
              id="view-student-activity-btn"
            >
              Activity Trail
            </Button>
            <Button
              as="link"
              to={`/mentor/students/${student.id || student.student_id || studentId}/projects`}
              variant="secondary"
              id="view-all-student-projects-btn"
            >
              View Projects Directory ({student.project_count})
            </Button>
          </div>
        }
      />

      <div className="gf-student-detail__profile-card" id="student-profile-card">
        <div className="gf-student-detail__avatar-large">
          {student.avatar_url ? (
            <img src={student.avatar_url} alt={student.full_name} />
          ) : (
            <span>{initials}</span>
          )}
        </div>
        <div className="gf-student-detail__profile-body">
          <div className="gf-student-detail__name-row">
            <h2 className="gf-student-detail__name">{student.full_name}</h2>
            {student.at_risk_project_count > 0 ? (
              <Badge variant="danger">{student.at_risk_project_count} Project(s) At Risk</Badge>
            ) : (
              <Badge variant="success">Good Standing</Badge>
            )}
          </div>
          <span className="gf-student-detail__email">{student.email}</span>
          {student.bio && <p className="gf-student-detail__bio">{student.bio}</p>}

          {student.skills && student.skills.length > 0 && (
            <div className="gf-student-detail__skills" id="student-skills-list">
              {student.skills.map((skill, idx) => (
                <Badge key={idx} variant="accent">
                  {skill}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="gf-student-detail__section">
        <div className="gf-student-detail__section-title">
          <span>Assigned Cohorts & Groups</span>
        </div>
        {student.groups.length === 0 ? (
          <p style={{ color: 'var(--gf-text-secondary)', fontSize: '0.875rem' }}>
            No cohort records found.
          </p>
        ) : (
          <div className="gf-student-detail__cohort-list">
            {student.groups.map((grp) => (
              <div key={grp.id} className="gf-student-detail__cohort-chip">
                <span>📁</span>
                <strong>{grp.name}</strong>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="gf-student-detail__section">
        <div className="gf-student-detail__section-title">
          <span>Supervised Project Instances ({student.projects.length})</span>
          <Link
            to={`/mentor/students/${student.id}/projects`}
            style={{ fontSize: '0.875rem', color: 'var(--gf-accent-primary)' }}
          >
            View dedicated projects view →
          </Link>
        </div>

        {student.projects.length === 0 ? (
          <EmptyState
            title="No project instances"
            description="This student has not created or been assigned any project instances yet."
          />
        ) : (
          <div className="gf-student-detail__projects-list" id="student-projects-list">
            {student.projects.map((proj) => (
              <Link
                key={proj.id}
                to={`/mentor/project-instances/${proj.id}`}
                className="gf-student-project-item"
                id={`project-item-${proj.id}`}
              >
                <div className="gf-student-project-item__info">
                  <span className="gf-student-project-item__title">{proj.name}</span>
                  <div className="gf-student-project-item__meta">
                    <span>Phase: <strong>{proj.current_phase}</strong></span>
                    {proj.source_definition_name && (
                      <span>
                        Template: {proj.source_definition_name} (v{proj.source_definition_version_number ?? 1})
                      </span>
                    )}
                    {proj.group_name && <span>Cohort: {proj.group_name}</span>}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  {getHealthBadge(proj.health)}
                  <div className="gf-student-project-item__progress">
                    <span className="gf-student-project-item__progress-label">
                      {proj.progress_percentage}%
                    </span>
                    <div className="gf-student-project-item__bar-track">
                      <div
                        className="gf-student-project-item__bar-fill"
                        style={{ width: `${proj.progress_percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
export default StudentDetail;
