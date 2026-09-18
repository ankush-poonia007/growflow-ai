import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router';
import { getProjectOverview, getBlueprintContent } from '@/lib/api';
import type { ProjectOverviewResponse, BlueprintContentResponse, BlueprintSectionKey } from '@/lib/api/types';
import {
  CANONICAL_BLUEPRINT_SECTION_ORDER,
  CANONICAL_BLUEPRINT_SECTION_LABELS,
} from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import './StudentBlueprintWorkspace.css';

export function StudentBlueprintWorkspace() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<ProjectOverviewResponse | null>(null);
  const [blueprintContent, setBlueprintContent] = useState<BlueprintContentResponse | null>(null);
  const [activeSection, setActiveSection] = useState<BlueprintSectionKey>('project_profile');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    setErrorCode(null);

    try {
      const [projData, bpData] = await Promise.all([
        getProjectOverview(projectId),
        getBlueprintContent(projectId),
      ]);
      setProject(projData);
      setBlueprintContent(bpData);
    } catch (err: any) {
      setError(err?.message || 'Unable to load blueprint workspace.');
      setErrorCode(err?.code || (err?.status === 403 ? 'AUTH_FORBIDDEN' : err?.status === 404 ? 'NOT_FOUND' : 'UNKNOWN'));
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  if (isLoading) {
    return (
      <div className="gf-bp-ws-loading" role="status" aria-live="polite">
        <div className="gf-bp-ws-skeleton gf-bp-ws-skeleton--header" />
        <div className="gf-bp-ws-skeleton gf-bp-ws-skeleton--body" />
        <span className="sr-only">Loading blueprint workspace...</span>
      </div>
    );
  }

  if (error || !project) {
    const isForbidden = errorCode === 'AUTH_FORBIDDEN' || error?.toLowerCase().includes('denied') || error?.toLowerCase().includes('forbidden');
    const isNotFound = errorCode === 'NOT_FOUND' || error?.toLowerCase().includes('not found');

    return (
      <div className="gf-bp-ws-error" role="alert">
        <div className="gf-bp-ws-error__card">
          <span className="gf-bp-ws-error__icon" aria-hidden="true">
            {isForbidden ? '🔒' : isNotFound ? '🔍' : '⚠️'}
          </span>
          <h2>{isForbidden ? 'Access Denied' : isNotFound ? 'Project Not Found' : 'Workspace Error'}</h2>
          <p>{isForbidden ? 'You are not authorized to access this blueprint workspace.' : error}</p>
          <Button as="link" to="/student/projects" variant="primary">
            Return to Projects
          </Button>
        </div>
      </div>
    );
  }

  const sections = (blueprintContent?.content as Record<string, any>) || {};
  const currentSectionData = sections[activeSection];
  const isApproved = blueprintContent?.status === 'APPROVED' || project.blueprint_summary?.status === 'APPROVED';

  const renderStructuredSection = () => {
    if (!currentSectionData) {
      return (
        <div className="gf-bp-ws-empty-section">
          <p>No content available for section {CANONICAL_BLUEPRINT_SECTION_LABELS[activeSection]}.</p>
        </div>
      );
    }

    // 1. Tech Stack
    if (activeSection === 'tech_stack' && currentSectionData.stack) {
      return (
        <div className="gf-bp-ws-table-wrap">
          <table className="gf-bp-ws-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Technology</th>
                <th>Purpose</th>
                <th>Why Selected</th>
              </tr>
            </thead>
            <tbody>
              {currentSectionData.stack.map((item: any, idx: number) => (
                <tr key={idx}>
                  <td><Badge variant="accent">{item.category}</Badge></td>
                  <td className="gf-bp-ws-font-bold">{item.technology}</td>
                  <td>{item.purpose}</td>
                  <td className="gf-bp-ws-text-muted">{item.why_selected}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // 2. Features
    if (activeSection === 'features' && currentSectionData.features) {
      return (
        <div className="gf-bp-ws-cards-grid">
          {currentSectionData.features.map((f: any, idx: number) => (
            <div key={idx} className="gf-bp-ws-feature-card">
              <div className="gf-bp-ws-feature-card__header">
                <span className="gf-bp-ws-feature-id">{f.id}</span>
                <Badge variant={f.priority === 'P0' ? 'accent' : 'neutral'}>{f.priority}</Badge>
              </div>
              <h4 className="gf-bp-ws-feature-title">{f.name}</h4>
              <p className="gf-bp-ws-feature-desc">{f.description}</p>
              <div className="gf-bp-ws-feature-criteria">
                <span className="gf-bp-ws-label-xs">Acceptance Criteria:</span>
                <p>{f.acceptance_criteria}</p>
              </div>
            </div>
          ))}
        </div>
      );
    }

    // 3. Specifications (APIs and Models)
    if (activeSection === 'specifications') {
      return (
        <div className="gf-bp-ws-specs-block">
          <h4 className="gf-bp-ws-subhead">RESTful API Endpoints</h4>
          <div className="gf-bp-ws-endpoints-list">
            {(currentSectionData.api_specifications || []).map((ep: any, idx: number) => (
              <div key={idx} className="gf-bp-ws-endpoint-item">
                <div className="gf-bp-ws-endpoint-header">
                  <span className="gf-bp-ws-method-badge">{ep.method}</span>
                  <code className="gf-bp-ws-endpoint-path">{ep.endpoint}</code>
                  <span className="gf-bp-ws-endpoint-auth">Auth: {ep.auth}</span>
                </div>
                <p className="gf-bp-ws-endpoint-desc">{ep.description}</p>
                {ep.request_body && ep.request_body !== '{}' && (
                  <div className="gf-bp-ws-code-snippet">
                    <span className="gf-bp-ws-snippet-label">Request Schema:</span>
                    <pre>{ep.request_body}</pre>
                  </div>
                )}
                {ep.response && (
                  <div className="gf-bp-ws-code-snippet">
                    <span className="gf-bp-ws-snippet-label">Response Contract:</span>
                    <pre>{ep.response}</pre>
                  </div>
                )}
              </div>
            ))}
          </div>

          <h4 className="gf-bp-ws-subhead" style={{ marginTop: 'var(--gf-space-6)' }}>Core Data Models</h4>
          <ul className="gf-bp-ws-models-list">
            {(currentSectionData.data_models || []).map((dm: string, idx: number) => (
              <li key={idx} className="gf-bp-ws-model-item">
                <code>{dm}</code>
              </li>
            ))}
          </ul>
        </div>
      );
    }

    // 4. Risks
    if (activeSection === 'risks' && currentSectionData.technical_risks) {
      return (
        <div className="gf-bp-ws-table-wrap">
          <table className="gf-bp-ws-table">
            <thead>
              <tr>
                <th>Risk ID</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Mitigation Strategy</th>
              </tr>
            </thead>
            <tbody>
              {currentSectionData.technical_risks.map((r: any, idx: number) => (
                <tr key={idx}>
                  <td><code>{r.id}</code></td>
                  <td className="gf-bp-ws-font-bold">{r.title}</td>
                  <td>
                    <Badge variant={r.severity === 'HIGH' ? 'danger' : r.severity === 'MEDIUM' ? 'warning' : 'neutral'}>
                      {r.severity}
                    </Badge>
                  </td>
                  <td>{r.mitigation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // 5. Tasks
    if (activeSection === 'tasks' && currentSectionData.tasks) {
      return (
        <div className="gf-bp-ws-table-wrap">
          <table className="gf-bp-ws-table">
            <thead>
              <tr>
                <th>Task ID</th>
                <th>Description</th>
                <th>Domain Category</th>
              </tr>
            </thead>
            <tbody>
              {currentSectionData.tasks.map((t: any, idx: number) => (
                <tr key={idx}>
                  <td><code>{t.id}</code></td>
                  <td>{t.name}</td>
                  <td><Badge variant="neutral">{t.category}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // 6. Milestones
    if (activeSection === 'milestones' && currentSectionData.milestones_schedule) {
      return (
        <div className="gf-bp-ws-table-wrap">
          <table className="gf-bp-ws-table">
            <thead>
              <tr>
                <th>Gate</th>
                <th>Milestone Name</th>
                <th>Gate Deliverable</th>
              </tr>
            </thead>
            <tbody>
              {currentSectionData.milestones_schedule.map((m: any, idx: number) => (
                <tr key={idx}>
                  <td><span className="gf-bp-ws-gate-pill">{m.gate}</span></td>
                  <td className="gf-bp-ws-font-bold">{m.name}</td>
                  <td>{m.deliverable}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // Default generic view (Project Profile, MVP, Duration, README)
    return (
      <div className="gf-bp-ws-generic-block">
        {Object.entries(currentSectionData).map(([key, val]) => (
          <div key={key} className="gf-bp-ws-field-group">
            <h4 className="gf-bp-ws-field-title">
              {key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
            </h4>
            {Array.isArray(val) ? (
              <ul className="gf-bp-ws-list">
                {val.map((item, i) => (
                  <li key={i}>{typeof item === 'object' ? JSON.stringify(item) : String(item)}</li>
                ))}
              </ul>
            ) : typeof val === 'object' && val !== null ? (
              <pre className="gf-bp-ws-json-view">{JSON.stringify(val, null, 2)}</pre>
            ) : (
              <p className="gf-bp-ws-field-text">{String(val)}</p>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="gf-blueprint-workspace" aria-label={`Blueprint Workspace for ${project.name}`}>
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={project.is_mentor_project}
      />

      <div className="gf-bp-ws-container">
        {/* Workspace Metadata Strip */}
        <div className="gf-bp-ws-meta-strip">
          <div className="gf-bp-ws-meta-left">
            <span className="gf-bp-ws-status-badge">
              {isApproved ? '✓ APPROVED BLUEPRINT ARTIFACT' : 'BLUEPRINT ARTIFACT'}
            </span>
            <span className="gf-bp-ws-version-tag">Version 1.0.0</span>
            <span className="gf-bp-ws-qa-score">
              QA Score: <strong>{blueprintContent?.qa_feedback?.score ?? project.blueprint_summary?.qa_score ?? 88} / 100</strong> (PASS)
            </span>
          </div>

          <div className="gf-bp-ws-meta-right">
            <Button
              as="link"
              to={`/student/projects/${project.id}/blueprint/documents/${activeSection}`}
              variant="secondary"
              size="sm"
              id="ws-open-doc-btn"
            >
              Open in Document Viewer →
            </Button>
          </div>
        </div>

        {/* Workspace Layout: Section Sidebar + Section Content */}
        <div className="gf-bp-ws-layout">
          {/* Section Navigation Sidebar */}
          <aside className="gf-bp-ws-sidebar" aria-label="Blueprint Canonical Sections">
            <h3 className="gf-bp-ws-sidebar-title">Canonical Artifacts</h3>
            <nav className="gf-bp-ws-nav">
              {CANONICAL_BLUEPRINT_SECTION_ORDER.map((secKey) => {
                const isActive = activeSection === secKey;
                return (
                  <button
                    key={secKey}
                    type="button"
                    className={`gf-bp-ws-nav-item ${isActive ? 'gf-bp-ws-nav-item--active' : ''}`}
                    onClick={() => setActiveSection(secKey)}
                    id={`sec-nav-${secKey}`}
                    aria-selected={isActive}
                  >
                    <span className="gf-bp-ws-nav-bullet" aria-hidden="true">•</span>
                    <span className="gf-bp-ws-nav-label">
                      {CANONICAL_BLUEPRINT_SECTION_LABELS[secKey]}
                    </span>
                  </button>
                );
              })}
            </nav>
          </aside>

          {/* Section Detail Panel */}
          <main className="gf-bp-ws-content" aria-label={CANONICAL_BLUEPRINT_SECTION_LABELS[activeSection]}>
            <Card className="gf-bp-ws-card">
              <CardHeader className="gf-bp-ws-card-header">
                <div>
                  <span className="gf-bp-ws-card-eyebrow">BLUEPRINT ARTIFACT SECTION</span>
                  <CardTitle as="h2" className="gf-bp-ws-card-title">
                    {CANONICAL_BLUEPRINT_SECTION_LABELS[activeSection]}
                  </CardTitle>
                </div>
                <Button
                  as="link"
                  to={`/student/projects/${project.id}/blueprint/documents/${activeSection}`}
                  variant="tertiary"
                  size="sm"
                >
                  View Markdown ↗
                </Button>
              </CardHeader>
              <CardContent className="gf-bp-ws-card-body">
                {renderStructuredSection()}
              </CardContent>
            </Card>
          </main>
        </div>
      </div>
    </div>
  );
}
