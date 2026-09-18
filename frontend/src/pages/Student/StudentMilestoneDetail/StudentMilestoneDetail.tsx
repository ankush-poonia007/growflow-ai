import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getMilestone, updateMilestone } from '@/lib/api';
import type { MilestoneResponse, MilestoneStatus } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentMilestoneDetail.css';

export function StudentMilestoneDetail() {
  const { projectId, milestoneId } = useParams<{ projectId: string; milestoneId: string }>();
  const {
    project,
    isLoading: isProjectLoading,
    error: projectError,
    refetch: refetchProject,
  } = useProjectWorkspace(projectId);

  const [milestone, setMilestone] = useState<MilestoneResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
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
  const [gateCode, setGateCode] = useState<string>('');
  const [status, setStatus] = useState<MilestoneStatus>('UPCOMING');
  const [targetDate, setTargetDate] = useState<string>('');
  const [deliverables, setDeliverables] = useState<string[]>([]);
  const [newDeliverable, setNewDeliverable] = useState<string>('');

  const fetchMilestone = useCallback(async () => {
    if (!projectId || !milestoneId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getMilestone(projectId, milestoneId);
      setMilestone(data);
      setTitle(data.title);
      setDescription(data.description || '');
      setGateCode(data.gate_code || '');
      setStatus(data.status);
      setTargetDate(data.target_date ? data.target_date.slice(0, 10) : '');
      setDeliverables(data.deliverables || []);
    } catch (err: any) {
      setError(err?.message || 'Unable to load milestone details.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, milestoneId]);

  useEffect(() => {
    void fetchMilestone();
  }, [fetchMilestone]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !milestoneId) return;
    if (!title.trim()) {
      setError('Milestone title is required.');
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const updated = await updateMilestone(projectId, milestoneId, {
        title: title.trim(),
        description: description.trim(),
        gate_code: gateCode.trim(),
        status,
        target_date: targetDate ? new Date(targetDate).toISOString() : null,
        deliverables,
      });
      setMilestone(updated);
      setSuccessMsg('Milestone updated successfully.');
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
      feedbackTimerRef.current = setTimeout(() => {
        setSuccessMsg(null);
        feedbackTimerRef.current = null;
      }, 3000);
    } catch (err: any) {
      setError(err?.message || 'Failed to update milestone.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddDeliverable = () => {
    if (!newDeliverable.trim()) return;
    setDeliverables((prev) => [...prev, newDeliverable.trim()]);
    setNewDeliverable('');
  };

  const handleRemoveDeliverable = (index: number) => {
    setDeliverables((prev) => prev.filter((_, i) => i !== index));
  };

  const handleRetry = useCallback(() => {
    void refetchProject();
    void fetchMilestone();
  }, [refetchProject, fetchMilestone]);

  if (isProjectLoading || isLoading) {
    return (
      <div className="gf-milestone-detail-page">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', gap: '1rem' }}>
          <LoadingSpinner size="lg" label="Loading milestone details..." />
          <p style={{ color: 'var(--gf-color-text-secondary)', margin: 0, fontSize: '0.875rem' }}>Loading milestone details...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project || !milestone) {
    return (
      <div className="gf-milestone-detail-page">
        <div style={{ maxWidth: '640px', margin: '3rem auto', padding: '0 1rem' }}>
          <InlineErrorState
            error={projectError || error || 'Milestone or project not found.'}
            onRetry={handleRetry}
            action={
              <Button as="link" to={`/student/projects/${projectId}/milestones`} variant="secondary" size="sm">
                Back to Milestones
              </Button>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="gf-milestone-detail-page" id="student-milestone-detail-view">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <main className="gf-milestone-detail-container">
        {/* Top Header Card */}
        <div className="gf-milestone-detail-header-card">
          <div>
            <Link
              to={`/student/projects/${projectId}/milestones`}
              style={{ color: '#64748b', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500 }}
              id="back-to-milestones-btn"
            >
              ← Back to All Milestones
            </Link>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.5rem' }}>
              <span className="gf-milestone-gate-badge">{milestone.gate_code || 'M'}</span>
              <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700, color: '#0f172a' }}>
                {milestone.title}
              </h1>
            </div>
          </div>

          <Badge
            variant={
              milestone.status === 'COMPLETED'
                ? 'success'
                : milestone.status === 'IN_PROGRESS'
                ? 'accent'
                : milestone.status === 'AT_RISK'
                ? 'danger'
                : 'neutral'
            }
          >
            {milestone.status}
          </Badge>
        </div>

        {/* Alerts */}
        {error && (
          <div style={{ marginBottom: '1.5rem' }}>
            <InlineErrorState error={error} onRetry={fetchMilestone} />
          </div>
        )}
        {successMsg && (
          <div style={{ padding: '1rem', background: '#f0fdf4', color: '#16a34a', borderRadius: '8px', marginBottom: '1.5rem' }}>
            {successMsg}
          </div>
        )}

        <form onSubmit={handleSave}>
          <div className="gf-milestone-detail-grid">
            {/* Left: Definition & Attached Tasks */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="gf-milestone-detail-card">
                <h3>Milestone Definition</h3>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="m-title-input">
                    Milestone Title *
                  </label>
                  <input
                    type="text"
                    id="m-title-input"
                    className="gf-form-input"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="m-desc-input">
                    Scope & Objective
                  </label>
                  <textarea
                    id="m-desc-input"
                    className="gf-form-textarea"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe verification gates and major outcomes..."
                  />
                </div>
              </div>

              {/* Deliverables Manager */}
              <div className="gf-milestone-detail-card">
                <h3>Verification Deliverables</h3>
                {deliverables.length === 0 ? (
                  <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
                    No deliverables recorded for this milestone gate.
                  </p>
                ) : (
                  <ul className="gf-checklist">
                    {deliverables.map((d, idx) => (
                      <li key={idx} className="gf-checklist-item">
                        <span>📦 {d}</span>
                        <button
                          type="button"
                          className="gf-checklist-remove-btn"
                          onClick={() => handleRemoveDeliverable(idx)}
                          aria-label="Remove deliverable"
                        >
                          ✕
                        </button>
                      </li>
                    ))}
                  </ul>
                )}

                <div className="gf-checklist-add">
                  <input
                    type="text"
                    className="gf-form-input"
                    style={{ flex: 1 }}
                    placeholder="Add deliverable artifact..."
                    value={newDeliverable}
                    onChange={(e) => setNewDeliverable(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddDeliverable();
                      }
                    }}
                  />
                  <Button as="button" variant="secondary" type="button" onClick={handleAddDeliverable}>
                    Add
                  </Button>
                </div>
              </div>

              {/* Attached Tasks */}
              <div className="gf-milestone-detail-card">
                <h3>Assigned Operational Tasks ({milestone.tasks.length})</h3>
                {milestone.tasks.length === 0 ? (
                  <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
                    No tasks currently linked to this milestone gate.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {milestone.tasks.map((t) => (
                      <div
                        key={t.id}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '0.75rem',
                          background: '#f8fafc',
                          border: '1px solid #e2e8f0',
                          borderRadius: '8px',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span className="gf-task-card__code">{t.task_code}</span>
                          <Link
                            to={`/student/projects/${projectId}/tasks/${t.id}`}
                            style={{ fontWeight: 600, color: '#0284c7', textDecoration: 'none' }}
                          >
                            {t.title}
                          </Link>
                        </div>
                        <Badge
                          variant={
                            t.status === 'COMPLETED'
                              ? 'success'
                              : t.status === 'BLOCKED'
                              ? 'danger'
                              : t.status === 'IN_PROGRESS'
                              ? 'accent'
                              : 'neutral'
                          }
                        >
                          {t.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right: State & Actions */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="gf-milestone-detail-card">
                <h3>Milestone Status & Progress</h3>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="m-gate-input">
                    Gate Code
                  </label>
                  <input
                    type="text"
                    id="m-gate-input"
                    className="gf-form-input"
                    value={gateCode}
                    onChange={(e) => setGateCode(e.target.value)}
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="m-status-select">
                    Gate Status
                  </label>
                  <select
                    id="m-status-select"
                    className="gf-form-select"
                    value={status}
                    onChange={(e) => setStatus(e.target.value as MilestoneStatus)}
                  >
                    <option value="UPCOMING">Upcoming</option>
                    <option value="IN_PROGRESS">In Progress</option>
                    <option value="COMPLETED">Completed</option>
                    <option value="AT_RISK">At Risk</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="m-target-date-input">
                    Target Completion Date
                  </label>
                  <input
                    type="date"
                    id="m-target-date-input"
                    className="gf-form-input"
                    value={targetDate}
                    onChange={(e) => setTargetDate(e.target.value)}
                  />
                </div>

                {/* Progress bar */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>
                    <span>Completion Rate</span>
                    <span>{milestone.progress_percent}%</span>
                  </div>
                  <div className="gf-milestone-progress-track">
                    <div
                      className="gf-milestone-progress-fill"
                      style={{ width: `${milestone.progress_percent}%` }}
                    />
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                    {milestone.completed_task_count} of {milestone.task_count} tasks completed
                  </div>
                </div>
              </div>

              <div className="gf-milestone-detail-card">
                <h3>Actions</h3>
                <Button
                  as="button"
                  variant="primary"
                  type="submit"
                  id="save-milestone-btn"
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save Milestone Changes'}
                </Button>
              </div>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
}
