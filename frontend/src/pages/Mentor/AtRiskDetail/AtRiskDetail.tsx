import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getMentorAtRiskProject } from '@/lib/api/client';
import type { MentorProjectInstanceDetail } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Skeleton } from '@/components/ui/Skeleton';
import './AtRiskDetail.css';

export function AtRiskDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<MentorProjectInstanceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadAtRiskDetail() {
      if (!projectId) return;
      try {
        setLoading(true);
        setError(null);
        const data = await getMentorAtRiskProject(projectId);
        if (mounted) {
          setProject(data);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg =
            err instanceof Error
              ? err.message
              : 'Failed to retrieve at-risk project details or access was denied.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadAtRiskDetail();
    return () => {
      mounted = false;
    };
  }, [projectId]);

  if (loading) {
    return (
      <div className="gf-at-risk-detail" id="at-risk-detail-loading">
        <Skeleton width="180px" height="24px" />
        <Skeleton width="100%" height="80px" style={{ borderRadius: '12px' }} />
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
          <Skeleton width="100%" height="300px" style={{ borderRadius: '14px' }} />
          <Skeleton width="100%" height="300px" style={{ borderRadius: '14px' }} />
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="gf-at-risk-detail" id="at-risk-detail-error-container">
        <div className="gf-at-risk-detail__nav">
          <Link to="/mentor/at-risk">← Back to At-Risk Directory</Link>
        </div>
        <div className="gf-at-risk-detail__error" role="alert" id="at-risk-detail-error">
          <h3>At-Risk Record Not Accessible</h3>
          <p>
            {error ||
              'This project is not currently marked as at-risk (WARNING or CRITICAL), does not exist, or is not in your cohorts.'}
          </p>
          <Button as="link" to="/mentor/at-risk" variant="secondary">
            Return to At-Risk Directory
          </Button>
        </div>
      </div>
    );
  }

  const isCritical = project.health === 'CRITICAL';

  return (
    <div className="gf-at-risk-detail" id="at-risk-detail-container">
      <div className="gf-at-risk-detail__nav">
        <Link to="/mentor/at-risk">Global At-Risk Directory</Link>
        <span>/</span>
        <span>{project.name}</span>
      </div>

      <PageHeader
        eyebrow="SUPERVISE AT-RISK TRIAGE (READ-ONLY)"
        title={`At-Risk Inspection: ${project.name}`}
        description={`Detailed risk assessment for ${project.student_name}'s project instance.`}
        actions={
          <Button
            as="link"
            to={`/mentor/project-instances/${project.id}`}
            variant="secondary"
            id="view-full-instance-btn"
          >
            Open Full Project Instance View →
          </Button>
        }
      />

      <div
        className={`gf-at-risk-detail__banner ${
          isCritical
            ? 'gf-at-risk-detail__banner--critical'
            : 'gf-at-risk-detail__banner--warning'
        }`}
        id="risk-level-banner"
      >
        <span className="gf-at-risk-detail__banner-icon">
          {isCritical ? '🚨' : '⚠️'}
        </span>
        <div className="gf-at-risk-detail__banner-body">
          <h3 className="gf-at-risk-detail__banner-title">
            Standing: {project.health} ({project.progress_percentage}% Progress)
          </h3>
          <p className="gf-at-risk-detail__banner-desc">
            {isCritical
              ? 'Critical project standing requires urgent mentor intervention. Verify student milestone obstacles or technical bottlenecks.'
              : 'Warning project standing indicates progression lag or unresolved risks. Schedule cohort check-in.'}
          </p>
        </div>
      </div>

      <div className="gf-at-risk-detail__grid">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="gf-at-risk-detail__card">
            <h3 className="gf-at-risk-detail__heading">Project Description & Scope</h3>

            <div className="gf-at-risk-detail__item">
              <span className="gf-at-risk-detail__label">Problem Statement</span>
              <div className="gf-at-risk-detail__val" id="at-risk-problem">
                {project.problem || 'No problem statement recorded.'}
              </div>
            </div>

            <div className="gf-at-risk-detail__item">
              <span className="gf-at-risk-detail__label">Proposed Solution</span>
              <div className="gf-at-risk-detail__val" id="at-risk-solution">
                {project.proposed_solution || 'No proposed solution recorded.'}
              </div>
            </div>
          </div>

          {project.source_definition_name && (
            <div className="gf-at-risk-detail__card">
              <h3 className="gf-at-risk-detail__heading">Source Definition & Version Snapshot</h3>
              <div
                style={{
                  background: 'rgba(99, 102, 241, 0.08)',
                  padding: '1rem',
                  borderRadius: '8px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: '0.5rem',
                  }}
                >
                  <strong>{project.source_definition_name}</strong>
                  <Badge variant="accent">
                    Pinned v{project.source_definition_version_number ?? 1}
                  </Badge>
                </div>
                {project.source_definition_version_summary && (
                  <p style={{ fontSize: '0.875rem', color: 'var(--gf-text-secondary)', margin: 0 }}>
                    {project.source_definition_version_summary}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="gf-at-risk-detail__card">
            <h3 className="gf-at-risk-detail__heading">Student Contact & Information</h3>
            <div className="gf-at-risk-detail__item">
              <span className="gf-at-risk-detail__label">Student</span>
              <Link
                to={`/mentor/students/${project.student_id}`}
                style={{
                  color: 'var(--gf-accent-primary)',
                  fontWeight: 600,
                  textDecoration: 'none',
                }}
                id="at-risk-student-link"
              >
                {project.student_name}
              </Link>
              <span style={{ fontSize: '0.8125rem', color: 'var(--gf-text-secondary)' }}>
                {project.student_email}
              </span>
            </div>

            {project.student_bio && (
              <div className="gf-at-risk-detail__item">
                <span className="gf-at-risk-detail__label">Bio</span>
                <span style={{ fontSize: '0.875rem', color: 'var(--gf-text-secondary)' }}>
                  {project.student_bio}
                </span>
              </div>
            )}

            {project.student_skills && project.student_skills.length > 0 && (
              <div className="gf-at-risk-detail__item">
                <span className="gf-at-risk-detail__label">Skills</span>
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

          <div className="gf-at-risk-detail__card">
            <h3 className="gf-at-risk-detail__heading">Operational Context</h3>
            <div className="gf-at-risk-detail__item">
              <span className="gf-at-risk-detail__label">Cohort</span>
              <span style={{ fontSize: '0.875rem' }}>{project.group_name || 'Individual'}</span>
            </div>
            <div className="gf-at-risk-detail__item">
              <span className="gf-at-risk-detail__label">Current Phase</span>
              <Badge variant="neutral">{project.current_phase}</Badge>
            </div>
            {project.deadline && (
              <div className="gf-at-risk-detail__item">
                <span className="gf-at-risk-detail__label">Deadline</span>
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
export default AtRiskDetail;
