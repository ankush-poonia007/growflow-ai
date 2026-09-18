import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getMentorProjectInstance } from '@/lib/api/client';
import type { MentorProjectInstanceDetail } from '@/lib/api/types';
import { MentorInstanceHeader } from '@/components/navigation/MentorInstanceHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Skeleton } from '@/components/ui/Skeleton';
import './ProjectInstanceDetail.css';

export function ProjectInstanceDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<MentorProjectInstanceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadDetail() {
      if (!projectId) return;
      try {
        setLoading(true);
        setError(null);
        const data = await getMentorProjectInstance(projectId);
        if (mounted) {
          setProject(data);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg =
            err instanceof Error
              ? err.message
              : 'Failed to retrieve project instance details or access was denied.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadDetail();
    return () => {
      mounted = false;
    };
  }, [projectId]);

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
      <div className="gf-project-instance-detail" id="project-detail-loading">
        <Skeleton width="180px" height="24px" />
        <Skeleton width="60%" height="36px" />
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
          <Skeleton width="100%" height="300px" style={{ borderRadius: '14px' }} />
          <Skeleton width="100%" height="300px" style={{ borderRadius: '14px' }} />
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="gf-project-instance-detail" id="project-detail-error-container">
        <div className="gf-project-instance-detail__nav">
          <Link to="/mentor/project-instances">← Back to Monitored Projects</Link>
        </div>
        <div className="gf-project-instance-detail__error" role="alert" id="project-detail-error">
          <h3>Supervision Access Restriction</h3>
          <p>{error || 'Project instance not found or does not belong to your supervised cohorts.'}</p>
          <Button as="link" to="/mentor/project-instances" variant="secondary">
            Return to Project Instances
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-project-instance-detail" id="project-instance-detail-container">
      <MentorInstanceHeader project={project} activeTab="overview" />

      <div className="gf-project-instance-detail__header-card">
        <div className="gf-project-instance-detail__title-row">
          <h2 className="gf-project-instance-detail__title">{project.name}</h2>
          <div className="gf-project-instance-detail__badge-row">
            {getHealthBadge(project.health)}
            <Badge variant="neutral">Phase: {project.current_phase}</Badge>
            <Badge variant="neutral">Complexity: {project.complexity}</Badge>
            <Badge variant="neutral">Status: {project.status}</Badge>
          </div>
        </div>

        <div className="gf-project-instance-detail__progress-section">
          <div className="gf-project-instance-detail__progress-label">
            <span>Overall Progress Completion</span>
            <strong>{project.progress_percentage}%</strong>
          </div>
          <div className="gf-project-instance-detail__bar-track">
            <div
              className="gf-project-instance-detail__bar-fill"
              style={{ width: `${project.progress_percentage}%` }}
            />
          </div>
        </div>
      </div>

      <div className="gf-project-instance-detail__grid">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="gf-project-instance-detail__card">
            <h3 className="gf-project-instance-detail__section-heading">Project Problem & Scope</h3>

            <div className="gf-project-instance-detail__text-block">
              <span className="gf-project-instance-detail__label">Problem Statement</span>
              <div className="gf-project-instance-detail__content" id="detail-problem-statement">
                {project.problem || 'No problem statement recorded.'}
              </div>
            </div>

            <div className="gf-project-instance-detail__text-block">
              <span className="gf-project-instance-detail__label">Proposed Solution</span>
              <div className="gf-project-instance-detail__content" id="detail-proposed-solution">
                {project.proposed_solution || 'No proposed solution recorded.'}
              </div>
            </div>
          </div>

          {project.source_definition_name && (
            <div className="gf-project-instance-detail__card" id="detail-pinned-version-card">
              <h3 className="gf-project-instance-detail__section-heading">
                Pinned Project Definition & Version
              </h3>
              <div className="gf-project-instance-detail__pinned-box">
                <div className="gf-project-instance-detail__pinned-header">
                  <strong style={{ color: 'var(--gf-text-primary)' }}>
                    {project.source_definition_name}
                  </strong>
                  <Badge variant="accent">
                    Pinned v{project.source_definition_version_number ?? 1}
                  </Badge>
                </div>
                {project.source_definition_version_summary ? (
                  <p
                    style={{
                      fontSize: '0.875rem',
                      color: 'var(--gf-text-secondary)',
                      margin: 0,
                    }}
                  >
                    {project.source_definition_version_summary}
                  </p>
                ) : (
                  <p
                    style={{
                      fontSize: '0.8125rem',
                      color: 'var(--gf-text-secondary)',
                      margin: 0,
                    }}
                  >
                    Version snapshot pinned to this instance at time of assignment.
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="gf-project-instance-detail__card">
            <h3 className="gf-project-instance-detail__section-heading">Student Ownership</h3>
            <div className="gf-project-instance-detail__text-block">
              <span className="gf-project-instance-detail__label">Student</span>
              <Link
                to={`/mentor/students/${project.student_id}`}
                style={{
                  color: 'var(--gf-accent-primary)',
                  fontWeight: 600,
                  textDecoration: 'none',
                }}
                id="student-link-from-detail"
              >
                {project.student_name}
              </Link>
              <span style={{ fontSize: '0.8125rem', color: 'var(--gf-text-secondary)' }}>
                {project.student_email}
              </span>
            </div>

            {project.student_bio && (
              <div className="gf-project-instance-detail__text-block">
                <span className="gf-project-instance-detail__label">Student Bio</span>
                <p style={{ fontSize: '0.875rem', color: 'var(--gf-text-secondary)', margin: 0 }}>
                  {project.student_bio}
                </p>
              </div>
            )}

            {project.student_skills && project.student_skills.length > 0 && (
              <div className="gf-project-instance-detail__text-block">
                <span className="gf-project-instance-detail__label">Skills</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginTop: '0.25rem' }}>
                  {project.student_skills.map((s, idx) => (
                    <Badge key={idx} variant="neutral">
                      {s}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            <div style={{ marginTop: '0.5rem' }}>
              <Button
                as="link"
                to={`/mentor/students/${project.student_id}`}
                variant="secondary"
                size="sm"
                style={{ width: '100%' }}
              >
                View Student Profile →
              </Button>
            </div>
          </div>

          <div className="gf-project-instance-detail__card">
            <h3 className="gf-project-instance-detail__section-heading">Cohort & Timestamps</h3>
            <div className="gf-project-instance-detail__text-block">
              <span className="gf-project-instance-detail__label">Cohort</span>
              <span style={{ fontSize: '0.875rem' }}>{project.group_name || 'Individual (No Cohort)'}</span>
            </div>

            <div className="gf-project-instance-detail__text-block">
              <span className="gf-project-instance-detail__label">Created At</span>
              <span style={{ fontSize: '0.875rem' }}>
                {new Date(project.created_at).toLocaleDateString()}
              </span>
            </div>

            {project.deadline && (
              <div className="gf-project-instance-detail__text-block">
                <span className="gf-project-instance-detail__label">Deadline</span>
                <span style={{ fontSize: '0.875rem' }}>
                  {new Date(project.deadline).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
export default ProjectInstanceDetail;
