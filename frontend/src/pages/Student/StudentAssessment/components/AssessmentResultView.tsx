import { Badge, Button } from '@/components/ui';
import type { AssessmentResultResponse } from '@/lib/api/types';
import {
  getReadinessTierBadgeVariant,
  formatDimensionLabel,
  getSeverityBadgeVariant,
} from '../utils';

interface AssessmentResultViewProps {
  projectId: string;
  result: AssessmentResultResponse;
}

export function AssessmentResultView({ projectId, result }: AssessmentResultViewProps) {
  const readinessTierVariant = getReadinessTierBadgeVariant(result.readiness_tier);
  const dimensionalScores: [string, number][] = Object.entries(result.dimension_scores || {});

  return (
    <div className="gf-assessment-result" id="assessment-result-view">
      {/* Hero Card */}
      <div className="gf-assessment-result__hero">
        <div className="gf-assessment-result__hero-top">
          <div>
            <span className="gf-assessment-intro__eyebrow">Stage 2 Result</span>
            <h2 className="gf-assessment-result__hero-title">Project Understanding & Readiness</h2>
          </div>
          <div className="gf-assessment-result__score-badge-wrap">
            <div className="gf-assessment-result__score-circle" aria-label={`Overall score ${result.overall_score} out of 100`}>
              <span className="gf-assessment-result__score-val">{result.overall_score}</span>
              <span className="gf-assessment-result__score-denom">/ 100</span>
            </div>
            <Badge variant={readinessTierVariant} dot>
              {result.readiness_tier.replace('_', ' ')}
            </Badge>
          </div>
        </div>

        {/* Project Understanding Summary */}
        <p className="gf-assessment-intro__desc">
          {result.summary}
        </p>

        {/* Enriched Project Understanding Grid */}
        <div className="gf-understanding-grid" role="region" aria-label="Enriched Project Understanding">
          <div className="gf-understanding-item">
            <span className="gf-understanding-item__label">Skill Level</span>
            <span className="gf-understanding-item__value">{result.skill_level || 'INTERMEDIATE'}</span>
          </div>

          <div className="gf-understanding-item">
            <span className="gf-understanding-item__label">Project Complexity</span>
            <span className="gf-understanding-item__value">{result.project_complexity || 'MODERATE'}</span>
          </div>

          <div className="gf-understanding-item">
            <span className="gf-understanding-item__label">Alignment</span>
            <span className="gf-understanding-item__value">{result.alignment || 'ALIGNED'}</span>
          </div>

          <div className="gf-understanding-item">
            <span className="gf-understanding-item__label">Technical Confidence</span>
            <span className="gf-understanding-item__value">{result.technical_confidence || 'HIGH'}</span>
          </div>

          <div className="gf-understanding-item">
            <span className="gf-understanding-item__label">Learning Depth</span>
            <span className="gf-understanding-item__value">{result.learning_depth || 'FOUNDATIONAL'}</span>
          </div>

          <div className="gf-understanding-item">
            <span className="gf-understanding-item__label">Recommended Focus</span>
            <span className="gf-understanding-item__value">{result.recommended_focus || 'Core Architecture'}</span>
          </div>
        </div>
      </div>

      {/* Dimensional Scores */}
      {dimensionalScores.length > 0 && (
        <div className="gf-dimensions-card">
          <h3 className="gf-card-section-title">Dimensional Readiness Breakdown</h3>
          <div className="gf-dimensions-list">
            {dimensionalScores.map(([dimKey, score]) => (
              <div key={dimKey} className="gf-dimension-item">
                <div className="gf-dimension-item__top">
                  <span className="gf-dimension-item__name">{formatDimensionLabel(dimKey)}</span>
                  <span className="gf-dimension-item__val">{score} / 100</span>
                </div>
                <div
                  className="gf-dimension-item__track"
                  role="progressbar"
                  aria-valuenow={score}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${formatDimensionLabel(dimKey)} score`}
                >
                  <div className="gf-dimension-item__fill" style={{ width: `${score}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Identified Technical Gaps */}
      {result.identified_gaps && result.identified_gaps.length > 0 && (
        <div className="gf-gaps-card">
          <h3 className="gf-card-section-title">Identified Technical Gaps</h3>
          <div className="gf-gaps-list">
            {result.identified_gaps.map((gap, idx) => (
              <div key={idx} className="gf-gap-item">
                <div className="gf-gap-item__badge-wrap">
                  <Badge variant={getSeverityBadgeVariant(gap.severity)}>
                    {gap.severity}
                  </Badge>
                </div>
                <div className="gf-gap-item__content">
                  <h4 className="gf-gap-item__title">{gap.area}</h4>
                  <p className="gf-gap-item__desc">{gap.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actionable Recommendations */}
      {result.recommendations && result.recommendations.length > 0 && (
        <div className="gf-recommendations-card">
          <h3 className="gf-card-section-title">Architectural Recommendations</h3>
          <ul className="gf-recommendations-list">
            {result.recommendations.map((rec, idx) => {
              const text = typeof rec === 'string' ? rec : `${rec.phase ? `${rec.phase}: ` : ''}${rec.action}`;
              return (
                <li key={idx} className="gf-recommendation-item">
                  <svg
                    className="gf-recommendation-icon"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <polyline points="9 11 12 14 22 4" />
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                  </svg>
                  <span>{text}</span>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {/* Next Stage Transition Notice */}
      <div className="gf-next-stage-card">
        <div>
          <span className="gf-assessment-intro__eyebrow">Next Phase in Development</span>
          <h3 className="gf-card-section-title" style={{ marginTop: '0.25rem' }}>
            Stage 3: Blueprint Generation
          </h3>
          <p className="gf-assessment-intro__desc" style={{ marginTop: '0.5rem' }}>
            Your assessment results have been authoritatively recorded and locked into your project
            state. Stage 3 (Blueprint Generation) will formulate your comprehensive architectural
            blueprint, data models, API specifications, and task breakdown based on these verified
            parameters.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
          <Button
            as="link"
            to={`/student/projects/${projectId}/blueprint`}
            variant="primary"
            size="lg"
            id="generate-blueprint-btn"
          >
            Generate Project Blueprint
          </Button>
          <Button
            as="link"
            to={`/student/projects/${projectId}/profile`}
            variant="secondary"
            size="lg"
            id="assessment-return-profile-btn"
          >
            Return to Project Profile
          </Button>
        </div>
      </div>
    </div>
  );
}
