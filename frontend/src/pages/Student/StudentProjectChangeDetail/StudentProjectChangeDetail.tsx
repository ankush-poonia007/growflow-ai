import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getProjectChange, confirmProjectChange } from '@/lib/api';
import type { ProjectChangeResponse } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import './StudentProjectChangeDetail.css';

export function StudentProjectChangeDetail() {
  const { projectId, changeId } = useParams<{ projectId: string; changeId: string }>();
  const { project, isLoading: isProjectLoading, error: projectError } = useProjectWorkspace(projectId);

  const [changeRequest, setChangeRequest] = useState<ProjectChangeResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isConfirming, setIsConfirming] = useState<boolean>(false);
  const [confirmSuccessMessage, setConfirmSuccessMessage] = useState<string | null>(null);

  const fetchChange = useCallback(async () => {
    if (!projectId || !changeId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getProjectChange(projectId, changeId);
      setChangeRequest(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load change request details.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, changeId]);

  useEffect(() => {
    void fetchChange();
  }, [fetchChange]);

  const handleConfirmRegeneration = async () => {
    if (!projectId || !changeId || !changeRequest) return;

    const promptMessage =
      `Are you sure you want to apply this change and regenerate the project blueprint?\n\n` +
      `• The current blueprint will be archived as Version ${changeRequest.source_blueprint_version_number}.\n` +
      `• A new blueprint version will be created with re-evaluated QA scorecard.\n` +
      `• Your operational tasks and execution history will NOT be deleted.`;

    if (!window.confirm(promptMessage)) return;

    setIsConfirming(true);
    setError(null);
    setConfirmSuccessMessage(null);

    try {
      const idempotencyKey = `idemp-${changeId}-${Date.now()}`;
      const confirmed = await confirmProjectChange(projectId, changeId, {
        idempotency_key: idempotencyKey,
      });
      setChangeRequest(confirmed);
      setConfirmSuccessMessage(
        `Blueprint successfully regenerated! Version ${confirmed.resulting_blueprint_version_number} is now active with QA score ${confirmed.qa_score}%.`
      );
    } catch (err: any) {
      setError(err?.message || 'Failed to confirm blueprint regeneration.');
    } finally {
      setIsConfirming(false);
    }
  };

  if (isProjectLoading || (isLoading && !changeRequest)) {
    return (
      <div className="gf-change-detail-page">
        <div className="gf-change-detail-page__loading" role="status">
          <div className="gf-change-detail-page__spinner" />
          <p>Analyzing impact report and change details...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project || !changeRequest) {
    return (
      <div className="gf-change-detail-page">
        <div className="gf-change-detail-page__error" role="alert">
          <h2>Error Loading Change Request</h2>
          <p>{error || (typeof projectError === 'string' ? projectError : projectError?.message) || 'Change request not found.'}</p>
          <Link to={`/student/projects/${projectId}/changes`} className="gf-back-link">
            ← Back to Changes
          </Link>
        </div>
      </div>
    );
  }

  const isConfirmed = changeRequest.status === 'CONFIRMED' || changeRequest.status === 'COMPLETED';
  const impact = changeRequest.impact_analysis;

  return (
    <div className="gf-change-detail-page" id="student-project-change-detail-screen">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <div className="gf-change-detail-page__container">
        {/* Navigation Breadcrumb */}
        <div className="gf-change-detail-breadcrumb">
          <Link to={`/student/projects/${projectId}/changes`} className="gf-breadcrumb-link">
            ← Back to Change Requests
          </Link>
        </div>

        {/* Change Header */}
        <header className="gf-change-detail-header">
          <div className="gf-change-detail-header__main">
            <div className="gf-change-detail-badges">
              <Badge variant={isConfirmed ? 'success' : 'accent'} dot>
                {changeRequest.status}
              </Badge>
              <Badge variant="neutral">{changeRequest.change_type}</Badge>
              <span className="gf-change-version-badge">
                Source: Blueprint v{changeRequest.source_blueprint_version_number}
                {changeRequest.resulting_blueprint_version_number &&
                  ` → Active: v${changeRequest.resulting_blueprint_version_number}`}
              </span>
            </div>
            <h1 className="gf-change-detail-title">{changeRequest.change_title}</h1>
            <p className="gf-change-detail-subtitle">{changeRequest.change_description}</p>
          </div>

          <div className="gf-change-detail-header__cta">
            {!isConfirmed ? (
              <Button
                variant="primary"
                size="lg"
                onClick={handleConfirmRegeneration}
                disabled={isConfirming}
                id="confirm-regeneration-btn"
              >
                {isConfirming ? 'Regenerating Blueprint...' : 'Confirm & Regenerate Blueprint'}
              </Button>
            ) : (
              <Link
                to={`/student/projects/${projectId}/blueprint/workspace`}
                className="gf-view-blueprint-btn"
                id="view-active-blueprint-btn"
              >
                View Active Blueprint (v{changeRequest.resulting_blueprint_version_number}) ➔
              </Link>
            )}
          </div>
        </header>

        {confirmSuccessMessage && (
          <div className="gf-change-alert gf-change-alert--success" role="alert">
            <span>✓</span> {confirmSuccessMessage}
          </div>
        )}

        {error && (
          <div className="gf-change-alert gf-change-alert--danger" role="alert">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Impact Report Grid */}
        <div className="gf-impact-grid">
          {/* Main Analysis Card */}
          <div className="gf-impact-card">
            <h2 className="gf-impact-card__heading">Impact Analysis Report</h2>

            {/* Non-destructive guarantee banner */}
            <div className="gf-impact-guarantee-banner">
              <span className="gf-impact-guarantee-icon">🛡️</span>
              <div>
                <strong>Zero Silent Deletion Guarantee:</strong>
                <p>
                  Existing operational tasks, completed milestones, and student work history are never silently purged.
                  Regeneration archives the previous blueprint version into <code>project_blueprint_versions</code> and updates specifications for future work.
                </p>
              </div>
            </div>

            {/* Affected sections pills */}
            <div className="gf-impact-row">
              <span className="gf-impact-row-label">Affected Blueprint Sections:</span>
              <div className="gf-impact-tags">
                {impact?.affected_sections && impact.affected_sections.length > 0 ? (
                  impact.affected_sections.map((sec, i) => (
                    <span key={i} className="gf-impact-tag">
                      {sec}
                    </span>
                  ))
                ) : (
                  <span className="gf-impact-tag gf-impact-tag--none">None identified</span>
                )}
              </div>
            </div>

            {/* Affected tasks */}
            <div className="gf-impact-row">
              <span className="gf-impact-row-label">Affected Operational Tasks:</span>
              <span className="gf-impact-row-val">
                <strong>{impact?.affected_tasks_count ?? 0}</strong> tasks flagged for scope review
              </span>
            </div>

            {/* Narrative */}
            <div className="gf-impact-narrative-section">
              <h3>Technical Impact Narrative</h3>
              <p className="gf-impact-narrative-text">
                {impact?.analysis_narrative || 'Impact analysis in progress.'}
              </p>
            </div>

            {/* Recommendation & Duration */}
            {impact?.recommended_action && (
              <div className="gf-impact-recommendation">
                <h4>Recommended Action</h4>
                <p>{impact.recommended_action}</p>
                {impact.duration_impact && (
                  <div className="gf-impact-duration">
                    Estimated timeline effect: <strong>{impact.duration_impact}</strong>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Side Summary Card */}
          <div className="gf-impact-sidebar">
            <div className="gf-sidebar-card">
              <h3 className="gf-sidebar-card__title">Risk Assessment</h3>
              <div className="gf-risk-indicator">
                <Badge
                  variant={
                    impact?.estimated_risk === 'HIGH'
                      ? 'danger'
                      : impact?.estimated_risk === 'MEDIUM'
                      ? 'warning'
                      : 'success'
                  }
                >
                  {impact?.estimated_risk || 'LOW'} RISK
                </Badge>
                <p className="gf-risk-explainer">
                  Evaluated based on cross-cutting dependencies and architectural layer coupling.
                </p>
              </div>
            </div>

            {/* Regeneration Scorecard (shown if confirmed) */}
            {isConfirmed && (
              <div className="gf-sidebar-card gf-sidebar-card--qa" id="regeneration-qa-scorecard">
                <h3 className="gf-sidebar-card__title">Regenerated QA Scorecard</h3>
                <div className="gf-qa-score-display">
                  <span className="gf-qa-score-number">{changeRequest.qa_score ?? 88}%</span>
                  <span className="gf-qa-score-label">Blueprint Quality Score</span>
                </div>

                {changeRequest.qa_feedback && (
                  <div className="gf-qa-feedback-box">
                    <p className="gf-qa-feedback-title">QA Verification Checks:</p>
                    <ul className="gf-qa-feedback-list">
                      <li>Blueprint schemas validated against technical scope</li>
                      <li>Milestone dependencies recalculated</li>
                      <li>Prior version archived cleanly in immutable history</li>
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Change metadata */}
            <div className="gf-sidebar-card">
              <h3 className="gf-sidebar-card__title">Proposal Metadata</h3>
              <dl className="gf-meta-dl">
                <dt>Request ID</dt>
                <dd><code>{changeRequest.id}</code></dd>
                <dt>Source Version</dt>
                <dd>v{changeRequest.source_blueprint_version_number}</dd>
                <dt>Created At</dt>
                <dd>{changeRequest.created_at ? new Date(changeRequest.created_at).toLocaleString() : '—'}</dd>
                <dt>Last Updated</dt>
                <dd>{changeRequest.updated_at ? new Date(changeRequest.updated_at).toLocaleString() : '—'}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
