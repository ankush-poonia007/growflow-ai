import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { getMentorInstanceBlueprint } from '@/lib/api/client';
import type { MentorBlueprintInspectionResponse } from '@/lib/api/types';
import { MentorInstanceHeader } from '@/components/navigation/MentorInstanceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorInstanceBlueprint.css';

const CANONICAL_SECTIONS = [
  { key: 'project_profile', label: '1. Project Profile' },
  { key: 'tech_stack', label: '2. Tech Stack' },
  { key: 'features', label: '3. Features' },
  { key: 'specifications', label: '4. Specifications' },
  { key: 'mvp', label: '5. MVP Scope' },
  { key: 'duration', label: '6. Duration & Timeline' },
  { key: 'risks', label: '7. Risks' },
  { key: 'tasks', label: '8. Tasks Breakdown' },
  { key: 'milestones', label: '9. Milestones Schedule' },
  { key: 'readme', label: '10. README' },
];

export const MentorInstanceBlueprint: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [data, setData] = useState<MentorBlueprintInspectionResponse | null>(null);
  const [selectedSection, setSelectedSection] = useState<string>('project_profile');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadBlueprint() {
      if (!projectId) return;
      try {
        setLoading(true);
        setError(null);
        const res = await getMentorInstanceBlueprint(projectId);
        if (mounted) {
          setData(res);
        }
      } catch (err: unknown) {
        if (mounted) {
          setError(
            err instanceof Error ? err.message : 'Failed to retrieve blueprint or access is denied.'
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadBlueprint();
    return () => {
      mounted = false;
    };
  }, [projectId]);

  if (loading) {
    return (
      <div className="gf-mentor-blueprint-page" id="mentor-blueprint-loading">
        <Skeleton width="100%" height="160px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '1.5rem' }}>
          <Skeleton width="100%" height="400px" style={{ borderRadius: '12px' }} />
          <Skeleton width="100%" height="400px" style={{ borderRadius: '12px' }} />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="gf-mentor-blueprint-page" id="mentor-blueprint-error">
        <div className="gf-mentor-blueprint-error-card" role="alert">
          <h3>Blueprint Supervision Restricted</h3>
          <p>{error || 'Blueprint not found or access denied.'}</p>
          <Button as="link" to="/mentor/project-instances" variant="secondary">
            Return to Project Instances
          </Button>
        </div>
      </div>
    );
  }

  const { project, blueprint, content } = data;
  const activeSectionData = content[selectedSection];

  const renderSectionContent = (key: string, sectionData: any) => {
    if (!sectionData || (typeof sectionData === 'object' && Object.keys(sectionData).length === 0)) {
      return (
        <div className="gf-mentor-blueprint__empty-section" id="blueprint-section-empty">
          <p>No content generated yet for this section.</p>
        </div>
      );
    }

    if (key === 'readme' && sectionData.markdown) {
      return (
        <div className="gf-mentor-blueprint__markdown-preview">
          <pre>{sectionData.markdown}</pre>
        </div>
      );
    }

    return (
      <div className="gf-mentor-blueprint__json-display">
        <pre>{JSON.stringify(sectionData, null, 2)}</pre>
      </div>
    );
  };

  return (
    <div className="gf-mentor-blueprint-page" id="mentor-blueprint-container">
      <MentorInstanceHeader project={project} activeTab="blueprint" />

      {/* Blueprint Top Overview & Scorecard */}
      <div className="gf-mentor-blueprint__status-card" id="blueprint-status-card">
        <div className="gf-mentor-blueprint__status-header">
          <div>
            <span className="gf-mentor-blueprint__eyebrow">CANONICAL BLUEPRINT INSPECTION</span>
            <h2 className="gf-mentor-blueprint__heading">System Architecture Blueprint</h2>
          </div>
          <div className="gf-mentor-blueprint__badges">
            <span className="gf-mentor-blueprint__status-badge">
              Status: <strong>{blueprint.status}</strong>
            </span>
            {blueprint.qa_score !== undefined && blueprint.qa_score !== null && (
              <Badge variant={blueprint.qa_score >= 80 ? 'success' : 'warning'}>
                QA Score: {blueprint.qa_score}/100
              </Badge>
            )}
            <Badge variant="neutral">Progress: {blueprint.progress_percent}%</Badge>
          </div>
        </div>

        {blueprint.qa_feedback && (
          <div className="gf-mentor-blueprint__qa-feedback" id="blueprint-qa-feedback">
            <div className="gf-mentor-blueprint__qa-summary">
              <strong>Evaluation Summary:</strong> {blueprint.qa_feedback.summary}
            </div>
            {blueprint.qa_feedback.recommendations && blueprint.qa_feedback.recommendations.length > 0 && (
              <div className="gf-mentor-blueprint__qa-recommendations">
                <strong>Recommendations:</strong>
                <ul>
                  {blueprint.qa_feedback.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Inspection Layout: Section Navigation + Content */}
      <div className="gf-mentor-blueprint__layout">
        <aside className="gf-mentor-blueprint__sidebar" aria-label="Blueprint Sections">
          <div className="gf-mentor-blueprint__sidebar-title">10 Canonical Sections</div>
          <nav className="gf-mentor-blueprint__section-list">
            {CANONICAL_SECTIONS.map((sec) => (
              <button
                key={sec.key}
                type="button"
                id={`blueprint-nav-${sec.key}`}
                className={`gf-mentor-blueprint__section-btn ${
                  selectedSection === sec.key ? 'gf-mentor-blueprint__section-btn--active' : ''
                }`}
                onClick={() => setSelectedSection(sec.key)}
              >
                <span>{sec.label}</span>
                {content[sec.key] ? (
                  <span className="gf-mentor-blueprint__dot-ready" title="Populated" />
                ) : (
                  <span className="gf-mentor-blueprint__dot-empty" title="Pending" />
                )}
              </button>
            ))}
          </nav>
        </aside>

        <main className="gf-mentor-blueprint__content-panel" id="blueprint-content-panel">
          <div className="gf-mentor-blueprint__content-header">
            <h3 className="gf-mentor-blueprint__content-title">
              {CANONICAL_SECTIONS.find((s) => s.key === selectedSection)?.label || selectedSection}
            </h3>
            <span className="gf-mentor-blueprint__read-only-pill">Read-Only View</span>
          </div>

          <div className="gf-mentor-blueprint__section-body">
            {renderSectionContent(selectedSection, activeSectionData)}
          </div>
        </main>
      </div>
    </div>
  );
};
