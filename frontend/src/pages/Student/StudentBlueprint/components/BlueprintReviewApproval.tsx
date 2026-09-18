import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  CANONICAL_BLUEPRINT_SECTION_ORDER,
  CANONICAL_BLUEPRINT_SECTION_LABELS,
  type BlueprintSectionKey,
  type BlueprintQAFeedback,
} from '@/lib/api/types';

interface BlueprintReviewApprovalProps {
  qaFeedback?: BlueprintQAFeedback | null;
  sections?: Record<string, any>;
  onApprove: () => void;
  onRetry: (sections?: BlueprintSectionKey[]) => void;
  isApproving: boolean;
  isRetrying: boolean;
}

export function BlueprintReviewApproval({
  qaFeedback,
  sections = {},
  onApprove,
  onRetry,
  isApproving,
  isRetrying,
}: BlueprintReviewApprovalProps) {
  const [activeTab, setActiveTab] = useState<BlueprintSectionKey>('project_profile');

  const qaPassed = qaFeedback?.status === 'PASSED' || (qaFeedback?.status as string) === 'PASS';
  const score = qaFeedback?.score ?? null;
  const criteria: Record<string, number> = (qaFeedback?.evaluated_criteria as Record<string, number>) || (qaFeedback as any)?.rubric || {};
  const hasCriteria = Object.keys(criteria).length > 0;

  const strengths = qaFeedback?.strengths || [];
  const recommendations = qaFeedback?.recommendations || [];

  const currentContent = sections[activeTab];

  const formatSectionContent = (content: any) => {
    if (!content) {
      return (
        <div className="gf-blueprint-empty-section">
          Section content currently being verified or awaiting preview generation.
        </div>
      );
    }

    if (typeof content === 'string') {
      return (
        <pre className="gf-blueprint-text-content">{content}</pre>
      );
    }

    return (
      <div className="gf-blueprint-structured-content">
        {Object.entries(content).map(([k, v]) => {
          const formattedKey = k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
          return (
            <div key={k} className="gf-blueprint-structured-block">
              <span className="gf-blueprint-structured-label">{formattedKey}</span>
              <div className="gf-blueprint-structured-val">
                {typeof v === 'object' ? JSON.stringify(v, null, 2) : String(v)}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="gf-blueprint-review" id="blueprint-review-view">
      {/* S14 QA Judge Scorecard */}
      <div className="gf-blueprint-card gf-blueprint-qa-card">
        <div className="gf-blueprint-qa__top">
          <div className="gf-blueprint-qa__header-text">
            <span className="gf-blueprint-badge-subtle">Stage 3 QA Evaluation</span>
            <h2 className="gf-blueprint-card__title">Autonomous Judge & QA Scorecard</h2>
            <p className="gf-blueprint-card__desc">
              Your synthesized blueprint has been evaluated across completeness, technical feasibility,
              and schema compliance by the GrowFlow QA engine.
            </p>
          </div>

          <div className="gf-blueprint-qa__score-wrap">
            <div
              className="gf-blueprint-qa__score-circle"
              aria-label={`QA Score ${score !== null ? score : 'N/A'} out of 100`}
            >
              <span className="gf-blueprint-qa__score-num">{score !== null ? score : '—'}</span>
              <span className="gf-blueprint-qa__score-denom">/ 100</span>
            </div>
            <Badge variant={qaPassed ? 'success' : 'danger'} dot>
              {qaPassed ? 'QA STATUS: PASS' : 'QA STATUS: FAIL'}
            </Badge>
          </div>
        </div>

        {/* Criteria Breakdown */}
        {hasCriteria ? (
          <div className="gf-blueprint-rubric-grid">
            {Object.entries(criteria).map(([crit, rawVal]) => {
              const numVal = typeof rawVal === 'number' ? rawVal : Number(rawVal) || 0;
              const label = crit.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
              return (
                <div key={crit} className="gf-blueprint-rubric-item">
                  <div className="gf-blueprint-rubric-top">
                    <span className="gf-blueprint-rubric-label">{label}</span>
                    <span className="gf-blueprint-rubric-score">{numVal} / 100</span>
                  </div>
                  <div
                    className="gf-blueprint-rubric-track"
                    role="progressbar"
                    aria-valuenow={numVal}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    <div
                      className="gf-blueprint-rubric-fill"
                      style={{
                        width: `${numVal}%`,
                        backgroundColor: numVal >= 75 ? 'var(--gf-color-accent)' : 'var(--gf-color-error)',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="gf-blueprint-empty-section" style={{ margin: 'var(--gf-space-3) 0' }}>
            No evaluated criteria scores recorded for this evaluation.
          </div>
        )}

        {/* Strengths & Recommendations */}
        <div className="gf-blueprint-feedback-columns">
          <div className="gf-blueprint-feedback-col">
            <h4 className="gf-blueprint-feedback-title">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Evaluated Strengths
            </h4>
            {strengths.length > 0 ? (
              <ul className="gf-blueprint-feedback-list">
                {strengths.map((str, i) => (
                  <li key={i}>{str}</li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: 'var(--gf-font-size-sm)', color: 'var(--gf-color-text-muted)', margin: 'var(--gf-space-2) 0' }}>
                No explicit strengths documented.
              </p>
            )}
          </div>

          <div className="gf-blueprint-feedback-col">
            <h4 className="gf-blueprint-feedback-title">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
              Architectural Recommendations
            </h4>
            {recommendations.length > 0 ? (
              <ul className="gf-blueprint-feedback-list">
                {recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: 'var(--gf-font-size-sm)', color: 'var(--gf-color-text-muted)', margin: 'var(--gf-space-2) 0' }}>
                No recommendations recorded.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* 10-Section Document Preview */}
      <div className="gf-blueprint-card gf-blueprint-preview-card">
        <div className="gf-blueprint-preview-card__header">
          <div>
            <span className="gf-blueprint-badge-subtle">Specification Preview</span>
            <h3 className="gf-blueprint-card__title">10 Canonical Blueprint Sections</h3>
          </div>
        </div>

        {/* Section Tabs */}
        <div className="gf-blueprint-tabs" role="tablist" aria-label="Blueprint sections">
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

        {/* Active Tab Section Display */}
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

      {/* Authoritative Approval Section */}
      <div className="gf-blueprint-card gf-blueprint-approval-card">
        <div className="gf-blueprint-approval__inner">
          <div className="gf-blueprint-approval__text">
            <span className="gf-blueprint-badge-subtle">Authoritative Gate Decision</span>
            <h3 className="gf-blueprint-card__title">
              {qaPassed ? 'Approve & Lock Stage 3 Blueprint' : 'QA Revisions Required'}
            </h3>
            <p className="gf-blueprint-card__desc">
              {qaPassed
                ? 'Your blueprint has satisfied all QA standards and schema requirements. Approving this document locks the architectural specifications and marks Stage 3 as complete.'
                : 'The autonomous QA evaluation identified criteria requiring adjustment before stage approval. You may re-synthesize affected sections.'}
            </p>
          </div>

          <div className="gf-blueprint-approval__actions">
            {qaPassed ? (
              <Button
                as="button"
                variant="primary"
                size="lg"
                onClick={onApprove}
                disabled={isApproving}
                id="approve-blueprint-btn"
              >
                {isApproving ? 'Locking Stage 3...' : 'Approve Blueprint & Advance Stage'}
              </Button>
            ) : (
              <Button
                as="button"
                variant="primary"
                size="lg"
                onClick={() => onRetry()}
                disabled={isRetrying}
                id="retry-blueprint-qa-btn"
              >
                {isRetrying ? 'Re-synthesizing...' : 'Re-synthesize With Judge Feedback'}
              </Button>
            )}

            <Button
              as="button"
              variant="secondary"
              size="lg"
              onClick={() => onRetry()}
              disabled={isRetrying || isApproving}
            >
              Re-generate Blueprint
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
