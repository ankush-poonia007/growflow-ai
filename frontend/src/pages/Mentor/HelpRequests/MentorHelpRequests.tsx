import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { getMentorHelpRequests, respondMentorHelpRequest, getMentorGroups } from '@/lib/api/client';
import type { MentorHelpRequestSummary, GroupResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorHelpRequests.css';

export function MentorHelpRequests() {
  const [requests, setRequests] = useState<MentorHelpRequestSummary[]>([]);
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'OPEN' | 'IN_PROGRESS' | 'RESOLVED'>('ALL');
  const [selectedGroupId, setSelectedGroupId] = useState<string>('ALL');

  // Response modal state
  const [activeRequest, setActiveRequest] = useState<MentorHelpRequestSummary | null>(null);
  const [responseText, setResponseText] = useState<string>('');
  const [targetStatus, setTargetStatus] = useState<'RESOLVED' | 'IN_PROGRESS'>('RESOLVED');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [modalError, setModalError] = useState<string | null>(null);

  const fetchGroups = useCallback(async () => {
    try {
      const data = await getMentorGroups();
      setGroups(data || []);
    } catch {
      // ignore groups fetch failure
    }
  }, []);

  const fetchRequests = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: { status?: string; group_id?: string } = {};
      if (statusFilter !== 'ALL') params.status = statusFilter;
      if (selectedGroupId !== 'ALL') params.group_id = selectedGroupId;
      const data = await getMentorHelpRequests(params);
      setRequests(data || []);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve help requests.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter, selectedGroupId]);

  useEffect(() => {
    void fetchGroups();
  }, [fetchGroups]);

  useEffect(() => {
    void fetchRequests();
  }, [fetchRequests]);

  const handleOpenResponseModal = (req: MentorHelpRequestSummary) => {
    setActiveRequest(req);
    setResponseText(req.mentor_response || '');
    setTargetStatus(req.status === 'IN_PROGRESS' ? 'IN_PROGRESS' : 'RESOLVED');
    setModalError(null);
  };

  const handleCloseModal = () => {
    setActiveRequest(null);
    setResponseText('');
    setModalError(null);
  };

  const handleSubmitResponse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeRequest) return;
    const cleanResponse = responseText.trim();
    if (!cleanResponse) {
      setModalError('Please enter a response message.');
      return;
    }

    setIsSubmitting(true);
    setModalError(null);

    try {
      const updated = await respondMentorHelpRequest(activeRequest.id, {
        mentor_response: cleanResponse,
        status: targetStatus,
      });

      // Update in local state
      setRequests((prev) =>
        prev.map((r) => (r.id === updated.id ? { ...r, ...updated } : r))
      );
      handleCloseModal();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to record response.';
      setModalError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getPriorityBadgeVariant = (priority: string): 'danger' | 'warning' | 'info' | 'neutral' => {
    switch (priority?.toUpperCase()) {
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

  const getStatusBadgeVariant = (status: string): 'success' | 'accent' | 'info' | 'neutral' => {
    switch (status?.toUpperCase()) {
      case 'RESOLVED':
        return 'success';
      case 'IN_PROGRESS':
        return 'accent';
      case 'OPEN':
      default:
        return 'info';
    }
  };

  const openCount = useMemo(() => {
    return requests.filter((r) => r.status === 'OPEN').length;
  }, [requests]);

  return (
    <div className="gf-mentor-help-page" id="mentor-help-requests-screen">
      <PageHeader
        title="Student Help Requests Inbox"
        description="Review questions, blockers, and assistance requests from students in your supervised cohorts."
      />

      {error && (
        <div className="gf-mentor-help-page__error" role="alert" id="help-requests-error">
          <p>⚠️ {error}</p>
          <Button variant="secondary" size="sm" onClick={() => void fetchRequests()}>
            Retry
          </Button>
        </div>
      )}

      {/* Filter and controls bar */}
      <div className="gf-mentor-help-filters" id="help-requests-filters">
        <div className="gf-mentor-help-filters__tabs">
          {(['ALL', 'OPEN', 'IN_PROGRESS', 'RESOLVED'] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              id={`filter-tab-${tab.toLowerCase()}`}
              className={`gf-mentor-help-tab ${statusFilter === tab ? 'gf-mentor-help-tab--active' : ''}`}
              onClick={() => setStatusFilter(tab)}
            >
              {tab.replace('_', ' ')}
              {tab === 'OPEN' && openCount > 0 && (
                <span className="gf-mentor-help-tab__badge">{openCount}</span>
              )}
            </button>
          ))}
        </div>

        {groups.length > 0 && (
          <div className="gf-mentor-help-filters__group-select">
            <label htmlFor="group-filter-select" className="gf-mentor-help-label">
              Cohort:
            </label>
            <select
              id="group-filter-select"
              value={selectedGroupId}
              onChange={(e) => setSelectedGroupId(e.target.value)}
              className="gf-mentor-help-select"
            >
              <option value="ALL">All Supervised Cohorts</option>
              {groups.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {isLoading && requests.length === 0 ? (
        <div className="gf-mentor-help-page__loading" id="help-requests-loading">
          <Skeleton height="120px" style={{ borderRadius: '12px', marginBottom: '1rem' }} />
          <Skeleton height="120px" style={{ borderRadius: '12px', marginBottom: '1rem' }} />
          <Skeleton height="120px" style={{ borderRadius: '12px', marginBottom: '1rem' }} />
        </div>
      ) : requests.length === 0 ? (
        <div className="gf-mentor-help-page__empty" id="help-requests-empty">
          <EmptyState
            title="No help requests found"
            description="There are currently no student requests matching your active filter criteria."
          />
        </div>
      ) : (
        <div className="gf-mentor-help-list" id="help-requests-list">
          {requests.map((req) => (
            <div key={req.id} className="gf-mentor-help-card" id={`help-request-${req.id}`}>
              <div className="gf-mentor-help-card__header">
                <div className="gf-mentor-help-card__badges">
                  <Badge variant={getPriorityBadgeVariant(req.priority)}>
                    {req.priority}
                  </Badge>
                  <Badge variant={getStatusBadgeVariant(req.status)}>
                    {req.status}
                  </Badge>
                  <span className="gf-mentor-help-card__category">{req.category}</span>
                </div>
                <span className="gf-mentor-help-card__date">
                  {req.created_at ? new Date(req.created_at).toLocaleDateString() : ''}
                </span>
              </div>

              <h3 className="gf-mentor-help-card__subject">{req.subject}</h3>
              <p className="gf-mentor-help-card__description">{req.description}</p>

              <div className="gf-mentor-help-card__context">
                <span className="gf-mentor-help-card__student">
                  Student: <strong>{req.student_name}</strong> ({req.student_email})
                </span>
                <span className="gf-mentor-help-card__divider">•</span>
                <span className="gf-mentor-help-card__project">
                  Project: <strong>{req.project_name}</strong>
                </span>
                {req.group_name && (
                  <>
                    <span className="gf-mentor-help-card__divider">•</span>
                    <span className="gf-mentor-help-card__group">
                      Cohort: <strong>{req.group_name}</strong>
                    </span>
                  </>
                )}
              </div>

              {req.mentor_response && (
                <div className="gf-mentor-help-card__response-preview">
                  <strong>Your Response:</strong> {req.mentor_response}
                </div>
              )}

              <div className="gf-mentor-help-card__actions">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleOpenResponseModal(req)}
                  id={`respond-btn-${req.id}`}
                >
                  {req.status === 'RESOLVED' ? 'Update Response' : 'Respond to Request'}
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Response Modal Dialog */}
      {activeRequest && (
        <div className="gf-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="response-modal-title">
          <div className="gf-modal-card gf-modal-card--lg">
            <div className="gf-modal-header">
              <h2 id="response-modal-title" className="gf-modal-title">
                Respond to Help Request
              </h2>
              <button
                type="button"
                className="gf-modal-close"
                onClick={handleCloseModal}
                aria-label="Close dialog"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmitResponse} className="gf-modal-form" id="help-response-form">
              <div className="gf-modal-context-box">
                <p><strong>Student:</strong> {activeRequest.student_name} ({activeRequest.student_email})</p>
                <p><strong>Project:</strong> {activeRequest.project_name}</p>
                <p><strong>Subject:</strong> {activeRequest.subject}</p>
                <div className="gf-modal-context-desc">
                  <strong>Description:</strong>
                  <p>{activeRequest.description}</p>
                </div>
              </div>

              {modalError && (
                <div className="gf-modal-error" role="alert" id="response-modal-error">
                  <span>⚠️</span> {modalError}
                </div>
              )}

              <div className="gf-modal-field">
                <label htmlFor="mentor-response-input" className="gf-modal-label">
                  Mentor Guidance & Resolution <span className="gf-modal-required">*</span>
                </label>
                <textarea
                  id="mentor-response-input"
                  className="gf-modal-textarea"
                  rows={5}
                  value={responseText}
                  onChange={(e) => setResponseText(e.target.value)}
                  placeholder="Provide technical guidance, architectural suggestions, or code review feedback..."
                  disabled={isSubmitting}
                  autoFocus
                />
              </div>

              <div className="gf-modal-field">
                <label htmlFor="target-status-select" className="gf-modal-label">
                  Lifecycle Status
                </label>
                <select
                  id="target-status-select"
                  className="gf-modal-select"
                  value={targetStatus}
                  onChange={(e) => setTargetStatus(e.target.value as 'RESOLVED' | 'IN_PROGRESS')}
                  disabled={isSubmitting}
                >
                  <option value="RESOLVED">Resolved (Closes request)</option>
                  <option value="IN_PROGRESS">In Progress (Investigation ongoing)</option>
                </select>
                <small className="gf-modal-hint">
                  Setting to Resolved marks the request as completed for the student.
                </small>
              </div>

              <div className="gf-modal-actions">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleCloseModal}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={isSubmitting || !responseText.trim()}
                  id="submit-response-btn"
                >
                  {isSubmitting ? 'Submitting...' : 'Save & Send Response'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
