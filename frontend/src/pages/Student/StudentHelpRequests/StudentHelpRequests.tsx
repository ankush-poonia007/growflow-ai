import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getHelpRequests, createHelpRequest } from '@/lib/api';
import type { HelpRequestResponse, HelpRequestCreatePayload } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import './StudentHelpRequests.css';

export function StudentHelpRequests() {
  const { projectId } = useParams<{ projectId: string }>();
  const { project, isLoading: isProjectLoading, error: projectError } = useProjectWorkspace(projectId);

  const [requests, setRequests] = useState<HelpRequestResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'OPEN' | 'RESOLVED'>('ALL');
  const [selectedRequest, setSelectedRequest] = useState<HelpRequestResponse | null>(null);

  // New request modal
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [subject, setSubject] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [category, setCategory] = useState<string>('TECHNICAL');
  const [priority, setPriority] = useState<string>('MEDIUM');

  const fetchRequests = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getHelpRequests(projectId);
      setRequests(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load mentor help requests.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchRequests();
  }, [fetchRequests]);

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;

    if (!subject.trim() || !description.trim()) {
      setModalError('Subject and description are required.');
      return;
    }

    setIsSubmitting(true);
    setModalError(null);

    const payload: HelpRequestCreatePayload = {
      subject: subject.trim(),
      description: description.trim(),
      category,
      priority,
    };

    try {
      const created = await createHelpRequest(projectId, payload);
      setRequests((prev) => [created, ...prev]);
      setIsModalOpen(false);
      setSubject('');
      setDescription('');
      setCategory('TECHNICAL');
      setPriority('MEDIUM');
      setSelectedRequest(created);
    } catch (err: any) {
      setModalError(err?.message || 'Failed to submit help request.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredRequests = useMemo(() => {
    if (statusFilter === 'ALL') return requests;
    if (statusFilter === 'OPEN') return requests.filter((r) => r.status === 'OPEN' || r.status === 'IN_REVIEW');
    return requests.filter((r) => r.status === 'RESOLVED');
  }, [requests, statusFilter]);

  const getPriorityBadgeVariant = (p: string): 'danger' | 'warning' | 'info' | 'neutral' => {
    switch (p?.toUpperCase()) {
      case 'URGENT':
        return 'danger';
      case 'HIGH':
        return 'warning';
      case 'MEDIUM':
        return 'info';
      default:
        return 'neutral';
    }
  };

  const getStatusBadgeVariant = (s: string): 'success' | 'accent' | 'info' | 'neutral' => {
    switch (s?.toUpperCase()) {
      case 'RESOLVED':
        return 'success';
      case 'IN_REVIEW':
        return 'accent';
      default:
        return 'info';
    }
  };

  if (isProjectLoading || (isLoading && requests.length === 0)) {
    return (
      <div className="gf-help-page">
        <div className="gf-help-page__loading" role="status">
          <div className="gf-help-page__spinner" />
          <p>Loading help requests...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-help-page">
        <div className="gf-help-page__error" role="alert">
          <h2>Error Loading Project</h2>
          <p>{(typeof projectError === 'string' ? projectError : projectError?.message) || 'Project not found.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-help-page" id="student-help-requests-screen">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <div className="gf-help-page__container">
        <header className="gf-help-page__header">
          <div className="gf-help-page__header-text">
            <h2 className="gf-help-page__title">Mentor Help Requests</h2>
            <p className="gf-help-page__subtitle">
              Escalate blockers, technical architecture questions, or code reviews to faculty mentors.
            </p>
          </div>
          <div className="gf-help-page__actions">
            <Button
              variant="primary"
              onClick={() => setIsModalOpen(true)}
              id="new-help-request-btn"
            >
              + Request Help
            </Button>
          </div>
        </header>

        {error && (
          <div className="gf-help-page__alert gf-help-page__alert--danger" role="alert">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Filter bar */}
        <div className="gf-help-filter-bar">
          <div className="gf-help-filter-tabs">
            {(['ALL', 'OPEN', 'RESOLVED'] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                className={`gf-help-tab-btn ${statusFilter === tab ? 'gf-help-tab-btn--active' : ''}`}
                onClick={() => setStatusFilter(tab)}
              >
                {tab === 'ALL' ? `All Requests (${requests.length})` : tab === 'OPEN' ? 'Open & In Review' : 'Resolved'}
              </button>
            ))}
          </div>
        </div>

        {/* Master-detail split view */}
        <div className="gf-help-layout">
          {/* Requests list */}
          <div className="gf-help-list" id="help-requests-list">
            {filteredRequests.length > 0 ? (
              filteredRequests.map((req) => (
                <div
                  key={req.id}
                  className={`gf-help-card ${selectedRequest?.id === req.id ? 'gf-help-card--active' : ''}`}
                  onClick={() => setSelectedRequest(req)}
                >
                  <div className="gf-help-card__top">
                    <div className="gf-help-card__badges">
                      <Badge variant={getStatusBadgeVariant(req.status)} dot>
                        {req.status}
                      </Badge>
                      <Badge variant={getPriorityBadgeVariant(req.priority)}>
                        {req.priority}
                      </Badge>
                      <span className="gf-help-card__category">{req.category}</span>
                    </div>
                    <time className="gf-help-card__time">
                      {req.created_at ? new Date(req.created_at).toLocaleDateString() : ''}
                    </time>
                  </div>

                  <h3 className="gf-help-card__subject">{req.subject}</h3>
                  <p className="gf-help-card__snippet">{req.description}</p>

                  {req.mentor_response && (
                    <div className="gf-help-card__response-indicator">
                      <span>💬 Mentor replied</span>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <EmptyState
                title="No help requests found"
                description={
                  statusFilter === 'ALL'
                    ? "You haven't submitted any help requests for this project yet."
                    : `No requests with status '${statusFilter}'.`
                }
              />
            )}
          </div>

          {/* Request detail panel */}
          <div className="gf-help-detail-panel" id="help-request-detail-panel">
            {selectedRequest ? (
              <div className="gf-help-detail-content">
                <div className="gf-help-detail-header">
                  <div className="gf-help-detail-badges">
                    <Badge variant={getStatusBadgeVariant(selectedRequest.status)} dot>
                      {selectedRequest.status}
                    </Badge>
                    <Badge variant={getPriorityBadgeVariant(selectedRequest.priority)}>
                      {selectedRequest.priority} Priority
                    </Badge>
                    <Badge variant="neutral">{selectedRequest.category}</Badge>
                  </div>
                  <span className="gf-help-detail-date">
                    Created {selectedRequest.created_at ? new Date(selectedRequest.created_at).toLocaleString() : ''}
                  </span>
                </div>

                <h2 className="gf-help-detail-title">{selectedRequest.subject}</h2>

                <div className="gf-help-detail-section">
                  <h4>Your Request Details</h4>
                  <p className="gf-help-detail-description">{selectedRequest.description}</p>
                </div>

                <div className="gf-help-detail-section gf-help-detail-section--mentor">
                  <h4>Faculty Mentor Response</h4>
                  {selectedRequest.mentor_response ? (
                    <div className="gf-help-mentor-box">
                      <p className="gf-help-mentor-text">{selectedRequest.mentor_response}</p>
                      {selectedRequest.resolved_at && (
                        <div className="gf-help-mentor-meta">
                          Resolved on {new Date(selectedRequest.resolved_at).toLocaleString()}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="gf-help-mentor-pending">
                      <span className="gf-help-clock-icon">⏳</span>
                      <p>
                        Your request is queued for faculty mentor review. Responses will appear here once submitted.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="gf-help-detail-placeholder">
                <p>Select a request from the list to view full details and mentor correspondence.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Request Modal */}
      {isModalOpen && (
        <div className="gf-modal-overlay" role="dialog" aria-modal="true" id="new-help-request-modal">
          <div className="gf-modal-card">
            <div className="gf-modal-header">
              <h3>Submit Help Request</h3>
              <button
                type="button"
                className="gf-modal-close"
                onClick={() => setIsModalOpen(false)}
              >
                ✕
              </button>
            </div>

            {modalError && (
              <div className="gf-help-page__alert gf-help-page__alert--danger" role="alert">
                <span>⚠️</span> {modalError}
              </div>
            )}

            <form onSubmit={handleCreateRequest} className="gf-help-modal-form">
              <div className="gf-form-group">
                <label htmlFor="req-subject">Subject</label>
                <input
                  id="req-subject"
                  type="text"
                  required
                  placeholder="e.g., Blocked on OAuth token validation in Gateway"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="gf-input"
                />
              </div>

              <div className="gf-form-row">
                <div className="gf-form-group">
                  <label htmlFor="req-category">Category</label>
                  <select
                    id="req-category"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="gf-select"
                  >
                    <option value="TECHNICAL">Technical Problem</option>
                    <option value="ARCHITECTURE">Architecture Design</option>
                    <option value="BLOCKED">Critical Blocker</option>
                    <option value="REVIEW">Code / Spec Review</option>
                    <option value="GENERAL">General Guidance</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label htmlFor="req-priority">Priority</label>
                  <select
                    id="req-priority"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="gf-select"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent (Blocked)</option>
                  </select>
                </div>
              </div>

              <div className="gf-form-group">
                <label htmlFor="req-desc">Detailed Description</label>
                <textarea
                  id="req-desc"
                  rows={5}
                  required
                  placeholder="Explain what you have tried, relevant logs/errors, and the specific guidance requested..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="gf-textarea"
                />
              </div>

              <div className="gf-modal-actions">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setIsModalOpen(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={isSubmitting}
                  id="submit-help-request-btn"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Request'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
