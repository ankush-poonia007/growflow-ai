import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getRisk, updateRisk, deleteRisk } from '@/lib/api';
import type { RiskResponse, RiskSeverity, RiskStatus } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentRiskDetail.css';

export function StudentRiskDetail() {
  const { projectId, riskId } = useParams<{ projectId: string; riskId: string }>();
  const navigate = useNavigate();
  const {
    project,
    isLoading: isProjectLoading,
    error: projectError,
    refetch: refetchProject,
  } = useProjectWorkspace(projectId);

  const [risk, setRisk] = useState<RiskResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
    };
  }, []);

  // Form Fields
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [severity, setSeverity] = useState<RiskSeverity>('MEDIUM');
  const [probability, setProbability] = useState<'LOW' | 'MEDIUM' | 'HIGH'>('MEDIUM');
  const [impact, setImpact] = useState<'LOW' | 'MEDIUM' | 'HIGH'>('MEDIUM');
  const [status, setStatus] = useState<RiskStatus>('OPEN');
  const [mitigation, setMitigation] = useState<string>('');
  const [owner, setOwner] = useState<string>('Student');
  const [reviewDate, setReviewDate] = useState<string>('');

  const fetchRisk = useCallback(async () => {
    if (!projectId || !riskId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getRisk(projectId, riskId);
      setRisk(data);
      setTitle(data.title);
      setDescription(data.description || '');
      setSeverity(data.severity);
      setProbability(data.probability);
      setImpact(data.impact);
      setStatus(data.status);
      setMitigation(data.mitigation || '');
      setOwner(data.owner || 'Student');
      setReviewDate(data.review_date ? data.review_date.slice(0, 10) : '');
    } catch (err: any) {
      setError(err?.message || 'Unable to load risk details.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, riskId]);

  useEffect(() => {
    void fetchRisk();
  }, [fetchRisk]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !riskId) return;
    if (!title.trim()) {
      setError('Risk title is required.');
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const updated = await updateRisk(projectId, riskId, {
        title: title.trim(),
        description: description.trim(),
        severity,
        probability,
        impact,
        status,
        mitigation: mitigation.trim(),
        owner: owner.trim() || 'Student',
        review_date: reviewDate ? new Date(reviewDate).toISOString() : null,
      });
      setRisk(updated);
      setSuccessMsg('Risk updated successfully.');
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
      feedbackTimerRef.current = setTimeout(() => {
        setSuccessMsg(null);
        feedbackTimerRef.current = null;
      }, 3000);
    } catch (err: any) {
      setError(err?.message || 'Failed to update risk.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!projectId || !riskId) return;
    if (!window.confirm('Are you sure you want to remove this risk from the register?')) {
      return;
    }

    setIsDeleting(true);
    try {
      await deleteRisk(projectId, riskId);
      navigate(`/student/projects/${projectId}/risks`);
    } catch (err: any) {
      setError(err?.message || 'Failed to delete risk.');
      setIsDeleting(false);
    }
  };

  const getSeverityBadgeVariant = (s: RiskSeverity): 'neutral' | 'accent' | 'warning' | 'danger' => {
    switch (s) {
      case 'CRITICAL':
        return 'danger';
      case 'HIGH':
        return 'warning';
      case 'MEDIUM':
        return 'accent';
      case 'LOW':
      default:
        return 'neutral';
    }
  };

  const handleRetry = useCallback(() => {
    void refetchProject();
    void fetchRisk();
  }, [refetchProject, fetchRisk]);

  if (isProjectLoading || isLoading) {
    return (
      <div className="gf-risk-detail-page">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', gap: '1rem' }}>
          <LoadingSpinner size="lg" label="Loading risk details..." />
          <p style={{ color: 'var(--gf-color-text-secondary)', margin: 0, fontSize: '0.875rem' }}>Loading risk details...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project || !risk) {
    return (
      <div className="gf-risk-detail-page">
        <div style={{ maxWidth: '640px', margin: '3rem auto', padding: '0 1rem' }}>
          <InlineErrorState
            error={projectError || error || 'Risk or project not found.'}
            onRetry={handleRetry}
            action={
              <Button as="link" to={`/student/projects/${projectId}/risks`} variant="secondary" size="sm">
                Back to Risk Register
              </Button>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="gf-risk-detail-page" id="student-risk-detail-view">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <main className="gf-risk-detail-container">
        {/* Top Header Card */}
        <div className="gf-risk-detail-header-card">
          <div>
            <Link
              to={`/student/projects/${projectId}/risks`}
              style={{ color: '#64748b', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500 }}
              id="back-to-risks-btn"
            >
              ← Back to Risk Register
            </Link>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.5rem' }}>
              <span className="gf-risk-card__code">{risk.risk_code}</span>
              <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700, color: '#0f172a' }}>
                {risk.title}
              </h1>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <Badge variant={getSeverityBadgeVariant(risk.severity)}>
              {risk.severity} Severity
            </Badge>
            <Badge
              variant={
                risk.status === 'RESOLVED'
                  ? 'success'
                  : risk.status === 'MITIGATING'
                  ? 'accent'
                  : risk.status === 'OPEN'
                  ? 'danger'
                  : 'neutral'
              }
            >
              {risk.status}
            </Badge>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div style={{ marginBottom: '1.5rem' }}>
            <InlineErrorState error={error} onRetry={fetchRisk} />
          </div>
        )}
        {successMsg && (
          <div style={{ padding: '1rem', background: '#f0fdf4', color: '#16a34a', borderRadius: '8px', marginBottom: '1.5rem' }}>
            {successMsg}
          </div>
        )}

        <form onSubmit={handleSave}>
          <div className="gf-risk-detail-grid">
            {/* Left: Definition & Mitigation */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="gf-risk-detail-card">
                <h3>Risk Description & Impact</h3>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="r-title-input">
                    Risk Title *
                  </label>
                  <input
                    type="text"
                    id="r-title-input"
                    className="gf-form-input"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="r-desc-input">
                    Failure Mode & Trigger
                  </label>
                  <textarea
                    id="r-desc-input"
                    className="gf-form-textarea"
                    style={{ minHeight: '120px' }}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Document root cause, trigger conditions, and technical impact..."
                  />
                </div>
              </div>

              <div className="gf-risk-detail-card">
                <h3>Mitigation Strategy & Contingency</h3>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="r-mitigation-input">
                    Planned Mitigation Actions
                  </label>
                  <textarea
                    id="r-mitigation-input"
                    className="gf-form-textarea"
                    style={{ minHeight: '140px' }}
                    value={mitigation}
                    onChange={(e) => setMitigation(e.target.value)}
                    placeholder="Document preventive actions, graceful fallbacks, and recovery steps..."
                  />
                </div>
              </div>
            </div>

            {/* Right: Risk Classification & Actions */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="gf-risk-detail-card">
                <h3>Risk Assessment</h3>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="r-status-select">
                    Current Status
                  </label>
                  <select
                    id="r-status-select"
                    className="gf-form-select"
                    value={status}
                    onChange={(e) => setStatus(e.target.value as RiskStatus)}
                  >
                    <option value="OPEN">Open</option>
                    <option value="MITIGATING">Mitigating</option>
                    <option value="RESOLVED">Resolved</option>
                    <option value="ACCEPTED">Accepted</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="r-severity-select">
                    Severity
                  </label>
                  <select
                    id="r-severity-select"
                    className="gf-form-select"
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value as RiskSeverity)}
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="r-prob-select">
                    Probability
                  </label>
                  <select
                    id="r-prob-select"
                    className="gf-form-select"
                    value={probability}
                    onChange={(e) => setProbability(e.target.value as any)}
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="r-impact-select">
                    Impact
                  </label>
                  <select
                    id="r-impact-select"
                    className="gf-form-select"
                    value={impact}
                    onChange={(e) => setImpact(e.target.value as any)}
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="r-owner-input">
                    Assigned Owner
                  </label>
                  <input
                    type="text"
                    id="r-owner-input"
                    className="gf-form-input"
                    value={owner}
                    onChange={(e) => setOwner(e.target.value)}
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="r-review-input">
                    Review Date
                  </label>
                  <input
                    type="date"
                    id="r-review-input"
                    className="gf-form-input"
                    value={reviewDate}
                    onChange={(e) => setReviewDate(e.target.value)}
                  />
                </div>
              </div>

              <div className="gf-risk-detail-card">
                <h3>Actions</h3>
                <Button
                  as="button"
                  variant="primary"
                  type="submit"
                  id="save-risk-btn"
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save Risk Changes'}
                </Button>

                <Button
                  as="button"
                  variant="secondary"
                  type="button"
                  id="delete-risk-btn"
                  onClick={handleDelete}
                  disabled={isDeleting}
                  style={{ color: '#ef4444', borderColor: '#fca5a5' }}
                >
                  {isDeleting ? 'Removing...' : 'Delete Risk'}
                </Button>
              </div>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
}
