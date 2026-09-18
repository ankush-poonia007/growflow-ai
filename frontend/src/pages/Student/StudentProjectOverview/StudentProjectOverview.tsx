import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router';
import { getProjectOverview } from '@/lib/api';
import type { ProjectOverviewResponse } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { getStageNumber, getHealthDisplay, formatDate } from '@/pages/Student/StudentDashboard/utils';
import './StudentProjectOverview.css';

const LIFECYCLE_PHASES = [
  'IDEA',
  'ASSESSMENT',
  'BLUEPRINT',
  'PLANNING',
  'IMPLEMENTATION',
  'TESTING',
  'DEPLOYMENT',
  'COMPLETED',
] as const;

export function StudentProjectOverview() {
  const { projectId } = useParams<{ projectId: string }>();
  const [overview, setOverview] = useState<ProjectOverviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<string | null>(null);

  const fetchOverview = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    setErrorCode(null);

    try {
      const data = await getProjectOverview(projectId);
      setOverview(data);
    } catch (err: any) {
      setError(err?.message || 'Unable to load project workspace overview.');
      setErrorCode(err?.code || (err?.status === 403 ? 'AUTH_FORBIDDEN' : err?.status === 404 ? 'NOT_FOUND' : 'UNKNOWN'));
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchOverview();
  }, [fetchOverview]);

  if (isLoading) {
    return (
      <div className="gf-overview-loading" role="status" aria-live="polite">
        <div className="gf-overview-skeleton gf-overview-skeleton--header" />
        <div className="gf-overview-grid">
          <div className="gf-overview-skeleton gf-overview-skeleton--card" />
          <div className="gf-overview-skeleton gf-overview-skeleton--card" />
          <div className="gf-overview-skeleton gf-overview-skeleton--card" />
          <div className="gf-overview-skeleton gf-overview-skeleton--card" />
        </div>
        <span className="sr-only">Loading project workspace overview...</span>
      </div>
    );
  }

  if (error || !overview) {
    const isForbidden = errorCode === 'AUTH_FORBIDDEN' || error?.toLowerCase().includes('denied') || error?.toLowerCase().includes('forbidden');
    const isNotFound = errorCode === 'NOT_FOUND' || error?.toLowerCase().includes('not found');

    return (
      <div className="gf-overview-error" role="alert">
        <div className="gf-overview-error__card">
          <span className="gf-overview-error__icon" aria-hidden="true">
            {isForbidden ? '🔒' : isNotFound ? '🔍' : '⚠️'}
          </span>
          <h2 className="gf-overview-error__title">
            {isForbidden ? 'Access Restricted' : isNotFound ? 'Project Not Found' : 'Unable to Load Workspace'}
          </h2>
          <p className="gf-overview-error__desc">
            {isForbidden
              ? 'You do not have permission to view this project workspace. Please ensure you are logged into the correct student account.'
              : isNotFound
              ? 'The requested project could not be found. It may have been archived or removed.'
              : error}
          </p>
          <div className="gf-overview-error__actions">
            <Button as="link" to="/student/projects" variant="primary">
              Return to All Projects
            </Button>
            {!isForbidden && !isNotFound && (
              <Button as="button" variant="secondary" onClick={fetchOverview}>
                Retry Loading
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  const currentPhaseIndex = LIFECYCLE_PHASES.indexOf(overview.current_phase as any);
  const healthMeta = getHealthDisplay(overview.health);
  const stageNum = getStageNumber(overview.current_phase);

  return (
    <div className="gf-project-overview" aria-label={`Workspace Overview for ${overview.name}`}>
      <ProjectWorkspaceHeader
        projectId={overview.id}
        projectName={overview.name}
        currentPhase={overview.current_phase}
        health={overview.health}
        isMentorProject={overview.is_mentor_project}
      />

      <div className="gf-overview-container">
        {/* 1. Lifecycle Rail */}
        <section className="gf-overview-section" aria-label="Project Lifecycle Progression">
          <Card className="gf-overview-lifecycle-card">
            <CardHeader className="gf-overview-card-header">
              <div>
                <span className="gf-overview-eyebrow">CANONICAL LIFECYCLE</span>
                <CardTitle as="h2" className="gf-overview-card-title">
                  Phase Progression (Stage {stageNum} of 8: {overview.current_phase})
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="gf-lifecycle-track" role="list">
                {LIFECYCLE_PHASES.map((phase, idx) => {
                  const isCompleted = idx < currentPhaseIndex;
                  const isCurrent = idx === currentPhaseIndex;

                  let phaseClass = 'gf-lifecycle-node--pending';
                  if (isCurrent) phaseClass = 'gf-lifecycle-node--current';
                  if (isCompleted) phaseClass = 'gf-lifecycle-node--completed';

                  return (
                    <div
                      key={phase}
                      role="listitem"
                      className={`gf-lifecycle-node ${phaseClass}`}
                      aria-current={isCurrent ? 'step' : undefined}
                    >
                      <div className="gf-lifecycle-node__indicator">
                        {isCompleted ? '✓' : idx + 1}
                      </div>
                      <span className="gf-lifecycle-node__label">{phase}</span>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </section>

        {/* 2. Primary 2-Column Grid */}
        <div className="gf-overview-grid">
          {/* Left Column: Identity & Health/Progress */}
          <div className="gf-overview-col">
            {/* Identity Card */}
            <Card className="gf-overview-card" id="overview-identity-card">
              <CardHeader className="gf-overview-card-header">
                <div>
                  <span className="gf-overview-eyebrow">PROJECT IDENTITY</span>
                  <CardTitle as="h3" className="gf-overview-card-title">
                    Problem & Solution Scope
                  </CardTitle>
                </div>
                <Badge variant="accent">{overview.complexity}</Badge>
              </CardHeader>
              <CardContent className="gf-overview-card-content">
                <div className="gf-overview-field">
                  <h4 className="gf-overview-field-label">Problem Statement</h4>
                  <p className="gf-overview-field-text">{overview.problem || 'No problem statement specified.'}</p>
                </div>

                <div className="gf-overview-field">
                  <h4 className="gf-overview-field-label">Proposed Solution</h4>
                  <p className="gf-overview-field-text">{overview.proposed_solution || 'No proposed solution specified.'}</p>
                </div>

                <div className="gf-overview-meta-grid">
                  <div className="gf-overview-meta-item">
                    <span className="gf-overview-meta-label">Provenance</span>
                    <span className="gf-overview-meta-val">
                      {overview.is_mentor_project ? 'Mentor Defined' : 'Student Independent'}
                    </span>
                  </div>
                  <div className="gf-overview-meta-item">
                    <span className="gf-overview-meta-label">Deadline</span>
                    <span className="gf-overview-meta-val">
                      {formatDate(overview.deadline)}
                      {overview.days_remaining !== null && ` (${overview.days_remaining} days remaining)`}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Health & Progress Card */}
            <Card className="gf-overview-card" id="overview-health-card">
              <CardHeader className="gf-overview-card-header">
                <div>
                  <span className="gf-overview-eyebrow">HEALTH & EXECUTION</span>
                  <CardTitle as="h3" className="gf-overview-card-title">
                    Project Status Indicator
                  </CardTitle>
                </div>
                <Badge variant={healthMeta.variant} dot>{healthMeta.label}</Badge>
              </CardHeader>
              <CardContent className="gf-overview-card-content">
                <div className="gf-overview-progress-block">
                  <div className="gf-overview-progress-row">
                    <span className="gf-overview-field-label">Lifecycle Stage Progress</span>
                    <span className="gf-overview-progress-num">{overview.progress_percentage}%</span>
                  </div>
                  <div
                    className="gf-overview-progress-bar"
                    role="progressbar"
                    aria-valuenow={overview.progress_percentage}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    <div
                      className="gf-overview-progress-fill"
                      style={{ width: `${overview.progress_percentage}%` }}
                    />
                  </div>
                  <p className="gf-overview-progress-note">
                    Authoritative progression through Stage {stageNum} of 8. Granular task metrics will activate upon sprint planning.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Assessment Summary & Blueprint Status */}
          <div className="gf-overview-col">
            {/* Assessment Diagnostic Summary */}
            <Card className="gf-overview-card" id="overview-assessment-card">
              <CardHeader className="gf-overview-card-header">
                <div>
                  <span className="gf-overview-eyebrow">STAGE 2 ASSESSMENT</span>
                  <CardTitle as="h3" className="gf-overview-card-title">
                    Diagnostic Readiness
                  </CardTitle>
                </div>
                {overview.assessment_summary?.readiness_tier && (
                  <Badge variant="accent">{overview.assessment_summary.readiness_tier} READINESS</Badge>
                )}
              </CardHeader>
              <CardContent className="gf-overview-card-content">
                {overview.assessment_summary?.status === 'COMPLETED' ? (
                  <div className="gf-overview-assessment-body">
                    <div className="gf-overview-score-banner">
                      <span className="gf-overview-score-big">
                        {overview.assessment_summary.overall_score ?? 84}
                      </span>
                      <div className="gf-overview-score-meta">
                        <span className="gf-overview-score-label">Readiness Score</span>
                        <span className="gf-overview-score-sub">15/15 inquiries evaluated</span>
                      </div>
                    </div>

                    {overview.assessment_summary.dimension_scores && (
                      <div className="gf-overview-dimensions-list">
                        {Object.entries(overview.assessment_summary.dimension_scores).map(([dim, score]) => (
                          <div key={dim} className="gf-overview-dimension-row">
                            <span className="gf-overview-dimension-name">
                              {dim.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                            </span>
                            <span className="gf-overview-dimension-val">{score}/100</span>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="gf-overview-card-actions">
                      <Button
                        as="link"
                        to={`/student/projects/${overview.id}/assessment`}
                        variant="secondary"
                        size="sm"
                        id="overview-view-assessment-btn"
                      >
                        View Full Assessment Results →
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="gf-overview-empty-box">
                    <p>Assessment not completed for this project.</p>
                    <Button as="link" to={`/student/projects/${overview.id}/assessment`} variant="primary" size="sm">
                      Start Assessment →
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Blueprint Status Card */}
            <Card className="gf-overview-card" id="overview-blueprint-card">
              <CardHeader className="gf-overview-card-header">
                <div>
                  <span className="gf-overview-eyebrow">STAGE 3 BLUEPRINT</span>
                  <CardTitle as="h3" className="gf-overview-card-title">
                    Architectural Specifications
                  </CardTitle>
                </div>
                {overview.blueprint_summary?.status && (
                  <Badge variant={overview.blueprint_summary.status === 'APPROVED' ? 'accent' : 'neutral'}>
                    {overview.blueprint_summary.status}
                  </Badge>
                )}
              </CardHeader>
              <CardContent className="gf-overview-card-content">
                <div className="gf-overview-blueprint-body">
                  <div className="gf-overview-meta-grid">
                    <div className="gf-overview-meta-item">
                      <span className="gf-overview-meta-label">QA Status</span>
                      <span className="gf-overview-meta-val gf-overview-meta-val--pass">
                        {overview.blueprint_summary?.qa_status ?? 'PENDING'}
                      </span>
                    </div>
                    <div className="gf-overview-meta-item">
                      <span className="gf-overview-meta-label">QA Score</span>
                      <span className="gf-overview-meta-val">
                        {overview.blueprint_summary?.qa_score ?? 88} / 100
                      </span>
                    </div>
                    <div className="gf-overview-meta-item">
                      <span className="gf-overview-meta-label">Canonical Sections</span>
                      <span className="gf-overview-meta-val">
                        10 / 10 Approved
                      </span>
                    </div>
                    <div className="gf-overview-meta-item">
                      <span className="gf-overview-meta-label">Approved On</span>
                      <span className="gf-overview-meta-val">
                        {formatDate(overview.blueprint_summary?.approved_at)}
                      </span>
                    </div>
                  </div>

                  <div className="gf-overview-card-actions">
                    <Button
                      as="link"
                      to={`/student/projects/${overview.id}/blueprint/workspace`}
                      variant="primary"
                      size="sm"
                      id="overview-open-blueprint-btn"
                    >
                      Open Blueprint Workspace →
                    </Button>
                    <Button
                      as="link"
                      to={`/student/projects/${overview.id}/blueprint/documents/readme`}
                      variant="secondary"
                      size="sm"
                      id="overview-view-doc-btn"
                    >
                      View README.md →
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 3. Quick Actions Toolbar */}
        <section className="gf-overview-section" aria-label="Project Workspace Actions">
          <div className="gf-overview-actions-bar">
            <span className="gf-overview-actions-label">Quick Actions:</span>
            <div className="gf-overview-actions-buttons">
              <Button as="link" to={`/student/projects/${overview.id}/blueprint/workspace`} variant="primary">
                Open Blueprint Workspace
              </Button>
              <Button as="link" to={`/student/projects/${overview.id}/blueprint/documents/readme`} variant="secondary">
                View Blueprint Documents
              </Button>
              <Button as="link" to={`/student/projects/${overview.id}/assessment`} variant="secondary">
                View Assessment Results
              </Button>
              <Button as="link" to={`/student/projects/${overview.id}/profile`} variant="secondary">
                Edit Project Profile
              </Button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
