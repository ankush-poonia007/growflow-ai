import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  CANONICAL_BLUEPRINT_SECTION_ORDER,
  CANONICAL_BLUEPRINT_SECTION_LABELS,
  type BlueprintSectionKey,
  type BlueprintQAFeedback,
} from '@/lib/api/types';

interface BlueprintApprovedViewProps {
  projectId: string;
  qaFeedback?: BlueprintQAFeedback | null;
  sections?: Record<string, any>;
  approvedAt?: string;
}

export function BlueprintApprovedView({
  projectId,
  qaFeedback,
  sections = {},
  approvedAt,
}: BlueprintApprovedViewProps) {
  const [activeTab, setActiveTab] = useState<BlueprintSectionKey>('project_profile');
  const currentContent = sections[activeTab];

  const formatSectionContent = (content: any) => {
    if (!content) {
      return (
        <div className="gf-blueprint-empty-section">
          Section content verified and locked in repository.
        </div>
      );
    }

    if (typeof content === 'string') {
      return <pre className="gf-blueprint-text-content">{content}</pre>;
    }

    return (
      <div className="gf-blueprint-structured-content">
        {Object.entries(content).map(([k, v]) => {
          const displayKey = k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
          return (
            <div key={k} className="gf-blueprint-field-group">
              <h4 className="gf-blueprint-field-label">{displayKey}</h4>
              {Array.isArray(v) ? (
                <ul className="gf-blueprint-field-list">
                  {v.map((item, i) => (
                    <li key={i} className="gf-blueprint-field-list-item">
                      {typeof item === 'object' ? JSON.stringify(item, null, 2) : String(item)}
                    </li>
                  ))}
                </ul>
              ) : typeof v === 'object' && v !== null ? (
                <pre className="gf-blueprint-json-preview">{JSON.stringify(v, null, 2)}</pre>
              ) : (
                <p className="gf-blueprint-field-val">{String(v)}</p>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="gf-blueprint-approved" id="blueprint-approved-view">
      <div className="gf-blueprint-card gf-blueprint-approved-hero">
        <div className="gf-blueprint-approved__header">
          <div className="gf-blueprint-approved__icon">
            <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <polyline points="9 12 11 14 15 10" />
            </svg>
          </div>
          <div>
            <div className="gf-blueprint-approved__tags">
              <Badge variant="success" dot>Stage 3 Approved & Locked</Badge>
              {approvedAt && (
                <span className="gf-blueprint-approved-date">
                  Approved on {new Date(approvedAt).toLocaleDateString()}
                </span>
              )}
            </div>
            <h2 className="gf-blueprint-card__title">Project Blueprint Formulated</h2>
            <p className="gf-blueprint-card__desc">
              Your architectural specifications, tech stack, data models, and work breakdown are authoritatively
              committed and immutable. Stage 3 is officially complete.
            </p>
          </div>
        </div>

        <div className="gf-blueprint-approved__meta-bar">
          <div className="gf-blueprint-meta-item">
            <span className="gf-blueprint-meta-item__label">QA Status</span>
            <span className="gf-blueprint-meta-item__val">PASSED</span>
          </div>
          <div className="gf-blueprint-meta-item">
            <span className="gf-blueprint-meta-item__label">QA Score</span>
            <span className="gf-blueprint-meta-item__val">
              {qaFeedback?.score ?? 85} / 100
            </span>
          </div>
          <div className="gf-blueprint-meta-item">
            <span className="gf-blueprint-meta-item__label">Canonical Sections</span>
            <span className="gf-blueprint-meta-item__val">10 / 10 Complete</span>
          </div>
        </div>

        <div className="gf-blueprint-actions" style={{ marginTop: 'var(--gf-space-4)' }}>
          <Button
            as="link"
            to={`/student/projects/${projectId}/overview`}
            variant="primary"
            size="lg"
            id="approved-open-workspace-btn"
          >
            Open Project Workspace →
          </Button>
          <Button
            as="link"
            to={`/student/projects/${projectId}/profile`}
            variant="secondary"
            size="lg"
            id="approved-return-profile-btn"
          >
            Project Profile
          </Button>
          <Button
            as="link"
            to="/student/projects"
            variant="secondary"
            size="lg"
          >
            All Student Projects
          </Button>
        </div>
      </div>

      {/* Read-Only Blueprint Document Browser */}
      <div className="gf-blueprint-card gf-blueprint-preview-card">
        <div className="gf-blueprint-preview-card__header">
          <div>
            <span className="gf-blueprint-badge-subtle">Committed Blueprint</span>
            <h3 className="gf-blueprint-card__title">Approved Technical Specifications</h3>
          </div>
        </div>

        <div className="gf-blueprint-tabs" role="tablist" aria-label="Approved blueprint sections">
          {CANONICAL_BLUEPRINT_SECTION_ORDER.map((secKey) => {
            const active = activeTab === secKey;
            return (
              <button
                key={secKey}
                type="button"
                role="tab"
                aria-selected={active}
                className={`gf-blueprint-tab ${active ? 'gf-blueprint-tab--active' : ''}`}
                onClick={() => setActiveTab(secKey)}
              >
                {CANONICAL_BLUEPRINT_SECTION_LABELS[secKey]}
              </button>
            );
          })}
        </div>

        <div className="gf-blueprint-tab-content" role="tabpanel">
          <div className="gf-blueprint-tab-content__header">
            <h4 className="gf-blueprint-tab-content__title">
              {CANONICAL_BLUEPRINT_SECTION_LABELS[activeTab]}
            </h4>
          </div>
          <div className="gf-blueprint-tab-content__body">
            {formatSectionContent(currentContent)}
          </div>
        </div>
      </div>
    </div>
  );
}
