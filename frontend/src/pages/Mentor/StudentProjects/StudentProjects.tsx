import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getMentorStudentProjects, getMentorStudent } from '@/lib/api/client';
import type { MentorProjectInstanceSummary, MentorStudentDetail } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './StudentProjects.css';

export function StudentProjects() {
  const { studentId } = useParams<{ studentId: string }>();
  const [projects, setProjects] = useState<MentorProjectInstanceSummary[]>([]);
  const [student, setStudent] = useState<MentorStudentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadStudentProjects() {
      if (!studentId) return;
      try {
        setLoading(true);
        setError(null);
        const [projectsData, studentData] = await Promise.all([
          getMentorStudentProjects(studentId),
          getMentorStudent(studentId),
        ]);
        if (mounted) {
          setProjects(projectsData);
          setStudent(studentData);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg =
            err instanceof Error
              ? err.message
              : 'Failed to retrieve student projects or access was denied.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadStudentProjects();
    return () => {
      mounted = false;
    };
  }, [studentId]);

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

  if (loading) {
    return (
      <div className="gf-student-projects" id="student-projects-loading">
        <Skeleton width="200px" height="24px" />
        <Skeleton width="50%" height="36px" />
        <div className="gf-student-projects__grid">
          {[1, 2, 3].map((i) => (
            <div key={i} className="gf-student-project-card">
              <Skeleton width="70%" height="24px" />
              <Skeleton width="100%" height="40px" />
              <Skeleton width="100%" height="36px" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !student) {
    return (
      <div className="gf-student-projects" id="student-projects-error-container">
        <div className="gf-student-projects__nav">
          <Link to="/mentor/students">← Back to Supervised Students</Link>
        </div>
        <div className="gf-student-projects__error" role="alert" id="student-projects-error">
          <h3>Access Restriction</h3>
          <p>{error || 'Student not found or not in your supervised cohorts.'}</p>
          <Button as="link" to="/mentor/students" variant="secondary">
            Return to Students Directory
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-student-projects" id="student-projects-container">
      <div className="gf-student-projects__nav">
        <Link to="/mentor/students">Supervised Students</Link>
        <span>/</span>
        <Link to={`/mentor/students/${student.id || student.student_id || studentId}`}>{student.full_name}</Link>
        <span>/</span>
        <span>Projects</span>
      </div>

      <PageHeader
        eyebrow="STUDENT PROJECTS (READ-ONLY)"
        title={`${student.full_name}'s Projects`}
        description={`Active and completed project instances for ${student.email}. Read-only supervision view.`}
        actions={
          <Button
            as="link"
            to={`/mentor/students/${student.id || student.student_id || studentId}`}
            variant="secondary"
            id="back-to-student-profile-btn"
          >
            ← View Student Profile
          </Button>
        }
      />

      {projects.length === 0 ? (
        <EmptyState
          title="No projects assigned"
          description="This student has no registered project instances in your cohorts."
        />
      ) : (
        <div className="gf-student-projects__grid" id="student-projects-grid">
          {projects.map((proj) => (
            <div
              key={proj.id}
              className="gf-student-project-card"
              id={`student-project-card-${proj.id}`}
            >
              <div className="gf-student-project-card__header">
                <span className="gf-student-project-card__title">{proj.name}</span>
                {getHealthBadge(proj.health)}
              </div>

              {proj.source_definition_name && (
                <div className="gf-student-project-card__template">
                  Template: <strong>{proj.source_definition_name}</strong> (v
                  {proj.source_definition_version_number ?? 1})
                </div>
              )}

              <div className="gf-student-project-card__meta">
                <span>Phase: <strong>{proj.current_phase}</strong></span>
                <span>Status: <strong>{proj.status}</strong></span>
                {proj.group_name && <span>Cohort: {proj.group_name}</span>}
                {proj.deadline && (
                  <span>Due: {new Date(proj.deadline).toLocaleDateString()}</span>
                )}
              </div>

              <div className="gf-student-project-card__progress-block">
                <div className="gf-student-project-card__progress-label">
                  <span>Progress</span>
                  <strong>{proj.progress_percentage}%</strong>
                </div>
                <div className="gf-student-project-card__progress-bar">
                  <div
                    className="gf-student-project-card__progress-fill"
                    style={{ width: `${proj.progress_percentage}%` }}
                  />
                </div>
              </div>

              <div style={{ marginTop: 'auto', paddingTop: '0.5rem' }}>
                <Button
                  as="link"
                  to={`/mentor/project-instances/${proj.id}`}
                  variant="secondary"
                  size="sm"
                  id={`inspect-project-${proj.id}`}
                  style={{ width: '100%', textAlign: 'center' }}
                >
                  Inspect Project Instance →
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
export default StudentProjects;
