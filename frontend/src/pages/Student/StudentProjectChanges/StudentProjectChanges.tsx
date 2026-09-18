import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import {
  getProjectChanges,
  analyzeProjectChange,
  getBlueprintVersions,
} from '@/lib/api';
import type {
  ProjectChangeResponse,
  ProjectChangeAnalyzePayload,
  BlueprintVersionResponse,
} from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import './StudentProjectChanges.css';

export function StudentProjectChanges() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { project, isLoading: isProjectLoading, error: projectError } = useProjectWorkspace(projectId);

  const [changes, setChanges] = useState<ProjectChangeResponse[]>([]);
  const [versions, setVersions] = useState<BlueprintVersionResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Propose Change Modal
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [changeTitle, setChangeTitle] = useState<string>('');
  const [changeDescription, setChangeDescription] = useState<string>('');
  const [changeType, setChangeType] = useState<string>('TECH_STACK');

  const fetchData = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const [changesData, versionsData] = await Promise.all([
        getProjectChanges(projectId),
        getBlueprintVersions(projectId),
      ]);
      setChanges(changesData);
      setVersions(versionsData);
    } catch (err: any) {
      setError(err?.message || 'Failed to load project changes and versions.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  const handleProposeChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;

    if (!changeTitle.trim() || !changeDescription.trim()) {
      setModalError('Change title and detailed description are required.');
      return;
    }

    setIsSubmitting(true);
    setModalError(null);

    const payload: ProjectChangeAnalyzePayload = {
      change_title: changeTitle.trim(),
      change_description: changeDescription.trim(),
      change_type: changeType,
    };

    try {
      const created = await analyzeProjectChange(projectId, payload);
      setIsModalOpen(false);
      // Navigate to S33 detail screen
      navigate(`/student/projects/${projectId}/changes/${created.id}`);
    } catch (err: any) {
      setModalError(err?.message || 'Failed to analyze project change.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'CONFIRMED':
      case 'COMPLETED':
        return <Badge variant="success">{status}</Badge>;
      case 'ANALYZED':
        return <Badge variant="accent">Impact Analyzed</Badge>;
      case 'REJECTED':
        return <Badge variant="danger">Rejected</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk?.toUpperCase()) {
      case 'HIGH':
        return <Badge variant="danger">High Risk</Badge>;
      case 'MEDIUM':
        return <Badge variant="warning">Medium Risk</Badge>;
      default:
        return <Badge variant="success">Low Risk</Badge>;
    }
  };

  if (isProjectLoading || (isLoading && changes.length === 0 && versions.length === 0)) {
    return (
      <div className="gf-changes-page">
        <div className="gf-changes-page__loading" role="status">
          <div className="gf-changes-page__spinner" />
          <p>Loading project changes & blueprint versions...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-changes-page">
        <div className="gf-changes-page__error" role="alert">
          <h2>Error Loading Project</h2>
          <p>{(typeof projectError === 'string' ? projectError : projectError?.message) || 'Project not found.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-changes-page" id="student-project-changes-screen">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <div className="gf-changes-page__container">
        <header className="gf-changes-page__header">
          <div className="gf-changes-page__header-text">
            <h2 className="gf-changes-page__title">Project Change & Blueprint Evolution</h2>
            <p className="gf-changes-page__subtitle">
              Formal impact analysis and non-destructive regeneration workflow. Operational tasks and history are strictly preserved.
            </p>
          </div>
          <div className="gf-changes-page__actions">
            <Button
              variant="primary"
              onClick={() => setIsModalOpen(true)}
              id="propose-change-btn"
            >
              + Propose Project Change
            </Button>
          </div>
        </header>

        {error && (
          <div className="gf-changes-page__alert gf-changes-page__alert--danger" role="alert">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Change Requests Section */}
        <div className="gf-changes-section">
          <h3 className="gf-changes-section__title">Active Change Requests ({changes.length})</h3>

          {changes.length > 0 ? (
            <div className="gf-changes-list" id="project-changes-list">
              {changes.map((chg) => (
                <div key={chg.id} className="gf-change-card" id={`change-card-${chg.id}`}>
                  <div className="gf-change-card__header">
                    <div className="gf-change-card__badges">
                      {getStatusBadge(chg.status)}
                      <Badge variant="neutral">{chg.change_type}</Badge>
                      {chg.impact_analysis?.estimated_risk && (
                        getRiskBadge(chg.impact_analysis.estimated_risk)
                      )}
                      <span className="gf-change-card__version-tag">
                        v{chg.source_blueprint_version_number}
                        {chg.resulting_blueprint_version_number && ` → v${chg.resulting_blueprint_version_number}`}
                      </span>
                    </div>
                    <time className="gf-change-card__time">
                      {chg.created_at ? new Date(chg.created_at).toLocaleDateString() : ''}
                    </time>
                  </div>

                  <h4 className="gf-change-card__title">{chg.change_title}</h4>
                  <p className="gf-change-card__desc">{chg.change_description}</p>

                  {chg.impact_analysis && (
                    <div className="gf-change-card__impact-preview">
                      <div className="gf-change-card__impact-row">
                        <span className="gf-change-card__impact-label">Affected Sections:</span>
                        <span className="gf-change-card__impact-val">
                          {chg.impact_analysis.affected_sections?.join(', ') || 'None'}
                        </span>
                      </div>
                      <div className="gf-change-card__impact-row">
                        <span className="gf-change-card__impact-label">Affected Tasks:</span>
                        <span className="gf-change-card__impact-val">
                          {chg.impact_analysis.affected_tasks_count} tasks (preserved without deletion)
                        </span>
                      </div>
                    </div>
                  )}

                  <div className="gf-change-card__footer">
                    <Link
                      to={`/student/projects/${projectId}/changes/${chg.id}`}
                      className="gf-change-card__detail-link"
                      id={`view-impact-link-${chg.id}`}
                    >
                      View Impact Analysis & Review ➔
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No project change requests"
              description="Propose changes to scope, architecture, or tech stack when you need to evolve your blueprint with full impact analysis."
            />
          )}
        </div>

        {/* Blueprint Version History Section */}
        <div className="gf-changes-section gf-changes-section--versions">
          <h3 className="gf-changes-section__title">Archived Blueprint Versions ({versions.length})</h3>
          <p className="gf-changes-section__subtitle">
            Immutable snapshot log maintained in <code>project_blueprint_versions</code>. Every regeneration archives the prior blueprint.
          </p>

          {versions.length > 0 ? (
            <div className="gf-versions-table-wrapper" id="blueprint-versions-table">
              <table className="gf-versions-table">
                <thead>
                  <tr>
                    <th>Version</th>
                    <th>Status</th>
                    <th>QA Score</th>
                    <th>Change Summary</th>
                    <th>Archived Date</th>
                  </tr>
                </thead>
                <tbody>
                  {versions.map((ver) => (
                    <tr key={ver.id}>
                      <td>
                        <strong>Version {ver.version_number}</strong>
                      </td>
                      <td>
                        <Badge variant={ver.status === 'APPROVED' ? 'success' : 'neutral'}>
                          {ver.status}
                        </Badge>
                      </td>
                      <td>
                        {ver.qa_score !== null ? (
                          <span className="gf-qa-score-pill">{ver.qa_score}%</span>
                        ) : (
                          '—'
                        )}
                      </td>
                      <td>{ver.change_summary || 'Initial approved blueprint version'}</td>
                      <td>{ver.created_at ? new Date(ver.created_at).toLocaleString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="gf-versions-none">No historical versions archived yet.</p>
          )}
        </div>
      </div>

      {/* Propose Change Modal */}
      {isModalOpen && (
        <div className="gf-modal-overlay" role="dialog" aria-modal="true" id="propose-change-modal">
          <div className="gf-modal-card">
            <div className="gf-modal-header">
              <h3>Propose Project Change</h3>
              <button
                type="button"
                className="gf-modal-close"
                onClick={() => setIsModalOpen(false)}
              >
                ✕
              </button>
            </div>

            {modalError && (
              <div className="gf-changes-page__alert gf-changes-page__alert--danger" role="alert">
                <span>⚠️</span> {modalError}
              </div>
            )}

            <form onSubmit={handleProposeChange} className="gf-change-modal-form">
              <div className="gf-form-group">
                <label htmlFor="chg-title">Change Title</label>
                <input
                  id="chg-title"
                  type="text"
                  required
                  placeholder="e.g., Migrate database from SQLite to PostgreSQL with Prisma ORM"
                  value={changeTitle}
                  onChange={(e) => setChangeTitle(e.target.value)}
                  className="gf-input"
                />
              </div>

              <div className="gf-form-group">
                <label htmlFor="chg-type">Change Type</label>
                <select
                  id="chg-type"
                  value={changeType}
                  onChange={(e) => setChangeType(e.target.value)}
                  className="gf-select"
                >
                  <option value="TECH_STACK">Tech Stack / Library Migration</option>
                  <option value="SCOPE">Scope Expansion / Reduction</option>
                  <option value="ARCHITECTURE">Architecture & Integration Redesign</option>
                  <option value="SCHEDULE">Delivery Timeline / Milestone Schedule</option>
                </select>
              </div>

              <div className="gf-form-group">
                <label htmlFor="chg-desc">Detailed Description & Motivation</label>
                <textarea
                  id="chg-desc"
                  rows={5}
                  required
                  placeholder="Describe why this change is necessary, what will be replaced, and any anticipated trade-offs..."
                  value={changeDescription}
                  onChange={(e) => setChangeDescription(e.target.value)}
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
                  id="submit-propose-change-btn"
                >
                  {isSubmitting ? 'Analyzing Impact...' : 'Analyze Impact & Continue'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
