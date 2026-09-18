import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getRisks, createRisk } from '@/lib/api';
import type { RiskResponse, RiskSeverity, RiskCreatePayload } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentRisks.css';

export function StudentRisks() {
  const { projectId } = useParams<{ projectId: string }>();
  const {
    project,
    isLoading: isProjectLoading,
    error: projectError,
    refetch: refetchProject,
  } = useProjectWorkspace(projectId);

  const [risks, setRisks] = useState<RiskResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newDesc, setNewDesc] = useState<string>('');
  const [newSeverity, setNewSeverity] = useState<RiskSeverity>('MEDIUM');
  const [newProb, setNewProb] = useState<'LOW' | 'MEDIUM' | 'HIGH'>('MEDIUM');
  const [newImpact, setNewImpact] = useState<'LOW' | 'MEDIUM' | 'HIGH'>('MEDIUM');
  const [newMitigation, setNewMitigation] = useState<string>('');
  const [newOwner, setNewOwner] = useState<string>('Student');

  const fetchRisks = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getRisks(projectId);
      setRisks(data);
    } catch (err: any) {
      setError(err?.message || 'Unable to load project risks.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchRisks();
  }, [fetchRisks]);

  const handleCreateRisk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;
    if (!newTitle.trim()) {
      setModalError('Risk title is required.');
      return;
    }

    setIsSubmitting(true);
    setModalError(null);

    const payload: RiskCreatePayload = {
      title: newTitle.trim(),
      description: newDesc.trim(),
      severity: newSeverity,
      probability: newProb,
      impact: newImpact,
      mitigation: newMitigation.trim(),
      owner: newOwner.trim() || 'Student',
    };

    try {
      const created = await createRisk(projectId, payload);
      setRisks((prev) => [...prev, created]);
      setIsModalOpen(false);
      setNewTitle('');
      setNewDesc('');
      setNewSeverity('MEDIUM');
      setNewMitigation('');
    } catch (err: any) {
      setModalError(err?.message || 'Failed to create risk.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredRisks = useMemo(() => {
    return risks.filter((r) => {
      if (statusFilter !== 'ALL' && r.status !== statusFilter) return false;
      if (severityFilter !== 'ALL' && r.severity !== severityFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        if (
          !r.title.toLowerCase().includes(q) &&
          !r.risk_code.toLowerCase().includes(q) &&
          !r.mitigation.toLowerCase().includes(q) &&
          !r.description.toLowerCase().includes(q)
        ) {
          return false;
        }
      }
      return true;
    });
  }, [risks, statusFilter, severityFilter, searchQuery]);

  const stats = useMemo(() => {
    return {
      total: risks.length,
      open: risks.filter((r) => r.status === 'OPEN').length,
      mitigating: risks.filter((r) => r.status === 'MITIGATING').length,
      resolved: risks.filter((r) => r.status === 'RESOLVED').length,
      highCritical: risks.filter((r) => r.severity === 'HIGH' || r.severity === 'CRITICAL').length,
    };
  }, [risks]);

  const getSeverityBadgeVariant = (severity: RiskSeverity): 'neutral' | 'accent' | 'warning' | 'danger' => {
    switch (severity) {
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

  if (isProjectLoading) {
    return (
      <div className="gf-risks-page">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', gap: '1rem' }}>
          <LoadingSpinner size="lg" label="Loading project risks..." />
          <p style={{ color: 'var(--gf-color-text-secondary)', margin: 0, fontSize: '0.875rem' }}>Loading project risks...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-risks-page">
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
    <div className="gf-risks-page" id="student-risks-view">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <main className="gf-risks-container">
        {/* Stats Summary */}
        <div className="gf-risks-stats">
          <div className="gf-risks-stat-card">
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>TOTAL RISKS</span>
            <span style={{ fontSize: '1.75rem', fontWeight: 700, color: '#0f172a' }}>{stats.total}</span>
          </div>
          <div className="gf-risks-stat-card">
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>OPEN RISKS</span>
            <span style={{ fontSize: '1.75rem', fontWeight: 700, color: '#ef4444' }}>{stats.open}</span>
          </div>
          <div className="gf-risks-stat-card">
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>MITIGATING</span>
            <span style={{ fontSize: '1.75rem', fontWeight: 700, color: '#0284c7' }}>{stats.mitigating}</span>
          </div>
          <div className="gf-risks-stat-card">
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>HIGH / CRITICAL</span>
            <span style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f59e0b' }}>{stats.highCritical}</span>
          </div>
          <div className="gf-risks-stat-card">
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>RESOLVED</span>
            <span style={{ fontSize: '1.75rem', fontWeight: 700, color: '#10b981' }}>{stats.resolved}</span>
          </div>
        </div>

        {/* Controls Bar */}
        <div className="gf-risks-controls">
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', flex: 1 }}>
            <input
              type="text"
              id="risks-search-input"
              placeholder="Search risks & mitigations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="gf-form-input"
              style={{ minWidth: '220px', maxWidth: '340px' }}
            />

            <select
              id="risks-status-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="gf-form-select"
            >
              <option value="ALL">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="MITIGATING">Mitigating</option>
              <option value="RESOLVED">Resolved</option>
              <option value="ACCEPTED">Accepted</option>
            </select>

            <select
              id="risks-severity-filter"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="gf-form-select"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <Button
            as="button"
            variant="primary"
            id="create-risk-btn"
            onClick={() => setIsModalOpen(true)}
          >
            + New Risk
          </Button>
        </div>

        {/* Alerts */}
        {error && (
          <div style={{ marginBottom: '1.5rem' }}>
            <InlineErrorState
              error={error}
              onRetry={fetchRisks}
            />
          </div>
        )}

        {/* Risk Cards */}
        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem 0', gap: '0.75rem' }}>
            <LoadingSpinner size="md" label="Refreshing risk registry..." />
            <span style={{ color: 'var(--gf-color-text-secondary)', fontSize: '0.875rem' }}>Refreshing risk registry...</span>
          </div>
        ) : filteredRisks.length === 0 ? (
          <EmptyState
            icon="🛡️"
            title="No risks identified"
            description="Proactive risk management helps anticipate technical hurdles early. Create your first risk item to document mitigation strategies."
            action={
              <Button as="button" variant="primary" onClick={() => setIsModalOpen(true)}>
                Record First Risk
              </Button>
            }
          />
        ) : (
          <div className="gf-risks-grid" role="list">
            {filteredRisks.map((risk) => (
              <div
                key={risk.id}
                className="gf-risk-card"
                id={`risk-card-${risk.risk_code}`}
                role="listitem"
              >
                <div className="gf-risk-card__top">
                  <span className="gf-risk-card__code">{risk.risk_code}</span>
                  <div className="gf-risk-card__badges">
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

                <Link
                  to={`/student/projects/${projectId}/risks/${risk.id}`}
                  className="gf-risk-card__title"
                  id={`risk-link-${risk.id}`}
                >
                  {risk.title}
                </Link>

                {risk.description && (
                  <p className="gf-risk-card__desc">{risk.description}</p>
                )}

                {risk.mitigation && (
                  <div className="gf-risk-card__mitigation">
                    <strong>Mitigation:</strong> {risk.mitigation}
                  </div>
                )}

                <div className="gf-risk-card__footer">
                  <span>Owner: {risk.owner || 'Student'}</span>
                  <Link
                    to={`/student/projects/${projectId}/risks/${risk.id}`}
                    style={{ color: '#0284c7', fontWeight: 600, textDecoration: 'none' }}
                  >
                    View Details →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Risk Modal */}
      {isModalOpen && (
        <div className="gf-modal-backdrop" role="dialog" aria-modal="true">
          <div className="gf-modal-card">
            <div className="gf-modal-header">
              <h2 className="gf-modal-title">Record Technical Risk</h2>
              <button
                type="button"
                className="gf-modal-close-btn"
                onClick={() => setIsModalOpen(false)}
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateRisk}>
              <div className="gf-modal-body">
                {modalError && (
                  <div style={{ padding: '0.75rem', background: '#fef2f2', color: '#b91c1c', borderRadius: '6px', fontSize: '0.875rem' }}>
                    {modalError}
                  </div>
                )}

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-risk-title">
                    Risk Title *
                  </label>
                  <input
                    type="text"
                    id="new-risk-title"
                    className="gf-form-input"
                    placeholder="e.g. Rate limiting on external AI LLM API"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    required
                    autoFocus
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-risk-desc">
                    Description & Failure Mode
                  </label>
                  <textarea
                    id="new-risk-desc"
                    className="gf-form-textarea"
                    placeholder="Explain what triggers this risk and potential system impact..."
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
                  <div className="gf-form-group">
                    <label className="gf-form-label" htmlFor="new-risk-severity">
                      Severity
                    </label>
                    <select
                      id="new-risk-severity"
                      className="gf-form-select"
                      value={newSeverity}
                      onChange={(e) => setNewSeverity(e.target.value as RiskSeverity)}
                    >
                      <option value="LOW">Low</option>
                      <option value="MEDIUM">Medium</option>
                      <option value="HIGH">High</option>
                      <option value="CRITICAL">Critical</option>
                    </select>
                  </div>

                  <div className="gf-form-group">
                    <label className="gf-form-label" htmlFor="new-risk-prob">
                      Probability
                    </label>
                    <select
                      id="new-risk-prob"
                      className="gf-form-select"
                      value={newProb}
                      onChange={(e) => setNewProb(e.target.value as any)}
                    >
                      <option value="LOW">Low</option>
                      <option value="MEDIUM">Medium</option>
                      <option value="HIGH">High</option>
                    </select>
                  </div>

                  <div className="gf-form-group">
                    <label className="gf-form-label" htmlFor="new-risk-impact">
                      Impact
                    </label>
                    <select
                      id="new-risk-impact"
                      className="gf-form-select"
                      value={newImpact}
                      onChange={(e) => setNewImpact(e.target.value as any)}
                    >
                      <option value="LOW">Low</option>
                      <option value="MEDIUM">Medium</option>
                      <option value="HIGH">High</option>
                    </select>
                  </div>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-risk-owner">
                    Risk Owner
                  </label>
                  <input
                    type="text"
                    id="new-risk-owner"
                    className="gf-form-input"
                    value={newOwner}
                    onChange={(e) => setNewOwner(e.target.value)}
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-risk-mitigation">
                    Mitigation Strategy
                  </label>
                  <textarea
                    id="new-risk-mitigation"
                    className="gf-form-textarea"
                    placeholder="Define fallback behavior, caching, or monitoring..."
                    value={newMitigation}
                    onChange={(e) => setNewMitigation(e.target.value)}
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
                  id="submit-risk-btn"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Recording...' : 'Record Risk'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
