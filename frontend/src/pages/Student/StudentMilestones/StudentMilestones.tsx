import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getMilestones, createMilestone } from '@/lib/api';
import type { MilestoneResponse, MilestoneStatus, MilestoneCreatePayload } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentMilestones.css';

export function StudentMilestones() {
  const { projectId } = useParams<{ projectId: string }>();
  const {
    project,
    isLoading: isProjectLoading,
    error: projectError,
    refetch: refetchProject,
  } = useProjectWorkspace(projectId);

  const [milestones, setMilestones] = useState<MilestoneResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newDesc, setNewDesc] = useState<string>('');
  const [newGate, setNewGate] = useState<string>('');
  const [newTargetDate, setNewTargetDate] = useState<string>('');

  const fetchMilestones = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getMilestones(projectId);
      setMilestones(data);
    } catch (err: any) {
      setError(err?.message || 'Unable to load project milestones.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchMilestones();
  }, [fetchMilestones]);

  const handleCreateMilestone = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;
    if (!newTitle.trim()) {
      setModalError('Milestone title is required.');
      return;
    }

    setIsSubmitting(true);
    setModalError(null);

    const payload: MilestoneCreatePayload = {
      title: newTitle.trim(),
      description: newDesc.trim(),
      gate_code: newGate.trim() || undefined,
      target_date: newTargetDate ? new Date(newTargetDate).toISOString() : null,
      deliverables: newDesc.trim() ? [newDesc.trim()] : [],
    };

    try {
      const created = await createMilestone(projectId, payload);
      setMilestones((prev) => [...prev, created]);
      setIsModalOpen(false);
      setNewTitle('');
      setNewDesc('');
      setNewGate('');
      setNewTargetDate('');
    } catch (err: any) {
      setModalError(err?.message || 'Failed to create milestone.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getMilestoneStatusBadge = (status: MilestoneStatus): { label: string; variant: 'neutral' | 'accent' | 'warning' | 'danger' | 'success' } => {
    switch (status) {
      case 'COMPLETED':
        return { label: 'Completed', variant: 'success' };
      case 'IN_PROGRESS':
        return { label: 'In Progress', variant: 'accent' };
      case 'AT_RISK':
        return { label: 'At Risk', variant: 'danger' };
      case 'UPCOMING':
      default:
        return { label: 'Upcoming', variant: 'neutral' };
    }
  };

  if (isProjectLoading) {
    return (
      <div className="gf-milestones-page">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', gap: '1rem' }}>
          <LoadingSpinner size="lg" label="Loading project milestones..." />
          <p style={{ color: 'var(--gf-color-text-secondary)', margin: 0, fontSize: '0.875rem' }}>Loading project milestones...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-milestones-page">
        <div style={{ maxWidth: '640px', margin: '3rem auto', padding: '0 1rem' }}>
          <InlineErrorState
            error={projectError || 'Project workspace not found.'}
            onRetry={refetchProject}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="gf-milestones-page" id="student-milestones-view">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <main className="gf-milestones-container">
        <div className="gf-milestones-header-row">
          <div className="gf-milestones-title-group">
            <h2>Execution Milestones & Quality Gates</h2>
            <p>Track phase completion, verification deliverables, and incremental project maturity.</p>
          </div>

          <Button
            as="button"
            variant="primary"
            id="create-milestone-btn"
            onClick={() => setIsModalOpen(true)}
          >
            + New Milestone
          </Button>
        </div>

        {error && (
          <div style={{ marginBottom: '1.5rem' }}>
            <InlineErrorState
              error={error}
              onRetry={fetchMilestones}
            />
          </div>
        )}

        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem 0', gap: '0.75rem' }}>
            <LoadingSpinner size="md" label="Loading milestone registry..." />
            <span style={{ color: 'var(--gf-color-text-secondary)', fontSize: '0.875rem' }}>Loading milestone registry...</span>
          </div>
        ) : milestones.length === 0 ? (
          <EmptyState
            icon="🎯"
            title="No milestones defined"
            description="Milestones represent stage gates and major deliverables. Create your first milestone to track high-level progress."
            action={
              <Button as="button" variant="primary" onClick={() => setIsModalOpen(true)}>
                Add First Milestone
              </Button>
            }
          />
        ) : (
          <div className="gf-milestones-timeline" role="list">
            {milestones.map((m) => {
              const statusMeta = getMilestoneStatusBadge(m.status);
              return (
                <div
                  key={m.id}
                  className="gf-milestone-card"
                  id={`milestone-card-${m.gate_code || m.id}`}
                  role="listitem"
                >
                  <div className="gf-milestone-card__top">
                    <div className="gf-milestone-card__gate-title">
                      <span className="gf-milestone-gate-badge">{m.gate_code || 'M'}</span>
                      <Link
                        to={`/student/projects/${projectId}/milestones/${m.id}`}
                        className="gf-milestone-card__heading"
                        id={`milestone-link-${m.id}`}
                      >
                        {m.title}
                      </Link>
                    </div>

                    <Badge variant={statusMeta.variant}>
                      {statusMeta.label}
                    </Badge>
                  </div>

                  {m.description && (
                    <p className="gf-milestone-card__desc">{m.description}</p>
                  )}

                  {/* Progress Bar */}
                  <div className="gf-milestone-progress-section">
                    <div className="gf-milestone-progress-labels">
                      <span>Gate Completion</span>
                      <span>{m.progress_percent}%</span>
                    </div>
                    <div className="gf-milestone-progress-track">
                      <div
                        className="gf-milestone-progress-fill"
                        style={{ width: `${m.progress_percent}%` }}
                      />
                    </div>
                  </div>

                  {/* Deliverables */}
                  {m.deliverables && m.deliverables.length > 0 && (
                    <div>
                      <div className="gf-milestone-deliverables-title">Key Deliverables</div>
                      <ul className="gf-milestone-deliverables-list">
                        {m.deliverables.map((deliv, idx) => (
                          <li key={idx} className="gf-milestone-deliverable-item">
                            📦 {deliv}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="gf-milestone-card__footer">
                    <span>
                      Tasks: <strong>{m.completed_task_count} / {m.task_count}</strong> completed
                    </span>
                    <Link
                      to={`/student/projects/${projectId}/milestones/${m.id}`}
                      style={{ color: '#0284c7', fontWeight: 600, textDecoration: 'none' }}
                    >
                      Manage Milestone Details →
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Create Milestone Modal */}
      {isModalOpen && (
        <div className="gf-modal-backdrop" role="dialog" aria-modal="true">
          <div className="gf-modal-card">
            <div className="gf-modal-header">
              <h2 className="gf-modal-title">Create Milestone Gate</h2>
              <button
                type="button"
                className="gf-modal-close-btn"
                onClick={() => setIsModalOpen(false)}
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateMilestone}>
              <div className="gf-modal-body">
                {modalError && (
                  <div style={{ padding: '0.75rem', background: '#fef2f2', color: '#b91c1c', borderRadius: '6px', fontSize: '0.875rem' }}>
                    {modalError}
                  </div>
                )}

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-milestone-title">
                    Milestone Title *
                  </label>
                  <input
                    type="text"
                    id="new-milestone-title"
                    className="gf-form-input"
                    placeholder="e.g. Core Domain Engine & Verification"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    required
                    autoFocus
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div className="gf-form-group">
                    <label className="gf-form-label" htmlFor="new-milestone-gate">
                      Gate Code
                    </label>
                    <input
                      type="text"
                      id="new-milestone-gate"
                      className="gf-form-input"
                      placeholder="e.g. M1, M2"
                      value={newGate}
                      onChange={(e) => setNewGate(e.target.value)}
                    />
                  </div>

                  <div className="gf-form-group">
                    <label className="gf-form-label" htmlFor="new-milestone-date">
                      Target Completion Date
                    </label>
                    <input
                      type="date"
                      id="new-milestone-date"
                      className="gf-form-input"
                      value={newTargetDate}
                      onChange={(e) => setNewTargetDate(e.target.value)}
                    />
                  </div>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-milestone-desc">
                    Deliverables & Gate Scope
                  </label>
                  <textarea
                    id="new-milestone-desc"
                    className="gf-form-textarea"
                    placeholder="List expected deliverables and verification criteria..."
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                  />
                </div>
              </div>

              <div className="gf-modal-footer">
                <Button
                  as="button"
                  variant="secondary"
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  as="button"
                  variant="primary"
                  type="submit"
                  id="submit-milestone-btn"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Creating...' : 'Create Milestone'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
