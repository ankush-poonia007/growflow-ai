import { Button } from '@/components/ui/Button';
import {
  CANONICAL_BLUEPRINT_SECTION_ORDER,
  CANONICAL_BLUEPRINT_SECTION_LABELS,
} from '@/lib/api/types';

interface BlueprintNotStartedProps {
  onStartGeneration: () => void;
  isStarting: boolean;
  assessmentScore?: number;
}

export function BlueprintNotStarted({
  onStartGeneration,
  isStarting,
  assessmentScore,
}: BlueprintNotStartedProps) {
  return (
    <div className="gf-blueprint-not-started">
      <div className="gf-blueprint-card gf-blueprint-hero-card">
        <div className="gf-blueprint-hero-card__header">
          <div>
            <span className="gf-blueprint-badge-subtle">Ready for Synthesis</span>
            <h2 className="gf-blueprint-card__title">Architectural Blueprint Synthesis</h2>
          </div>
          {typeof assessmentScore === 'number' && (
            <div className="gf-blueprint-hero-card__badge-score">
              <span className="gf-blueprint-score-label">Assessment Calibrated</span>
              <span className="gf-blueprint-score-num">{assessmentScore} / 100</span>
            </div>
          )}
        </div>

        <p className="gf-blueprint-card__desc">
          GrowFlow's synthesis engine will sequentially formulate a production-grade blueprint for your project.
          Each section is deterministically validated against industry best practices and evaluated by an autonomous QA Judge
          before unlocking Stage 3 approval.
        </p>

        <div className="gf-blueprint-sections-preview">
          <h3 className="gf-blueprint-subheading">10 Canonical Blueprint Sections:</h3>
          <div className="gf-blueprint-sections-grid">
            {CANONICAL_BLUEPRINT_SECTION_ORDER.map((sectionKey, index) => (
              <div key={sectionKey} className="gf-blueprint-section-preview-item">
                <span className="gf-blueprint-section-number">{index + 1}</span>
                <span className="gf-blueprint-section-name">
                  {CANONICAL_BLUEPRINT_SECTION_LABELS[sectionKey]}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="gf-blueprint-actions">
          <Button
            as="button"
            variant="primary"
            size="lg"
            onClick={onStartGeneration}
            disabled={isStarting}
            id="start-blueprint-btn"
          >
            {isStarting ? 'Initiating Synthesis Engine...' : 'Generate Project Blueprint'}
          </Button>
          <span className="gf-blueprint-engine-notice">
            Zero hallucinations • Strict Pydantic schemas • Automated QA review
          </span>
        </div>
      </div>
    </div>
  );
}
